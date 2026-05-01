"""
Firestore adapter for research and news agent content.

Ownership boundary
------------------
This adapter handles only the Firestore-native content collections defined in
services/firestore_schemas.py:
  - research_articles
  - custom_research_summaries
  - news_articles
  - custom_news_summaries

Tasks, Notes, and CalendarEvents are owned by database.py (SQLAlchemy).
Audit trail events are owned by mcp_tools/firestore_adapter.py.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from backend.services.firestore_schemas import (
    ResearchArticle,
    CustomResearchSummary,
    NewsArticle,
    CustomNewsSummary,
    FIRESTORE_COLLECTION_DEFINITIONS,
    DATA_VALIDATION_RULES,
    validate_document,
)

logger = logging.getLogger(__name__)


class FirestoreAdapter:
    """
    Firestore adapter for research/news content collections.
    Supports both a real Firestore client (production) and an in-memory mock
    (development / testing).
    """

    def __init__(self, project_id: str = None, use_mock: bool = True):
        self.project_id = project_id
        self.use_mock   = use_mock
        self._client    = None

        if not use_mock:
            try:
                from google.cloud import firestore as _fs
                self._client = _fs.AsyncClient(project=project_id)
                logger.info(f"Firestore client initialised (project={project_id})")
            except Exception as e:
                logger.warning(f"Firestore unavailable ({e}), falling back to mock")
                self.use_mock = True

        if self.use_mock:
            self._mock: Dict[str, Dict[str, Any]] = {
                collection: {}
                for collection in FIRESTORE_COLLECTION_DEFINITIONS
            }
            logger.info("FirestoreAdapter running in mock mode")

    # ── Generic CRUD ─────────────────────────────────────────────────────────

    async def create(self, collection: str, doc_id: str,
                     data: Dict[str, Any]) -> Dict[str, Any]:
        is_valid, errors = validate_document(collection, data)
        if not is_valid:
            raise ValueError(f"Validation failed for {collection}: {errors}")

        doc = {**data, "id": doc_id,
               "created_at": data.get("created_at") or datetime.utcnow().isoformat(),
               "updated_at": datetime.utcnow().isoformat()}

        if self.use_mock:
            self._mock.setdefault(collection, {})[doc_id] = doc
        else:
            await self._client.collection(collection).document(doc_id).set(doc)

        logger.debug(f"Created {collection}/{doc_id}")
        return doc

    async def read(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        if self.use_mock:
            return self._mock.get(collection, {}).get(doc_id)
        doc = await self._client.collection(collection).document(doc_id).get()
        return doc.to_dict() if doc.exists else None

    async def update(self, collection: str, doc_id: str,
                     data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        patch = {**data, "updated_at": datetime.utcnow().isoformat()}
        if self.use_mock:
            existing = self._mock.get(collection, {}).get(doc_id)
            if existing is None:
                return None
            existing.update(patch)
            return existing
        await self._client.collection(collection).document(doc_id).update(patch)
        return await self.read(collection, doc_id)

    async def delete(self, collection: str, doc_id: str) -> bool:
        if self.use_mock:
            return self._mock.get(collection, {}).pop(doc_id, None) is not None
        await self._client.collection(collection).document(doc_id).delete()
        return True

    async def query(self, collection: str, filters: List[tuple] = None,
                    order_by: str = None, limit: int = None) -> List[Dict[str, Any]]:
        if self.use_mock:
            results = list(self._mock.get(collection, {}).values())
            if filters:
                for field, op, val in filters:
                    results = [d for d in results if _match(d.get(field), op, val)]
            if order_by:
                results.sort(key=lambda d: d.get(order_by, ""))
            return results[:limit] if limit else results

        q = self._client.collection(collection)
        if filters:
            for field, op, val in filters:
                q = q.where(field, op, val)
        if order_by:
            q = q.order_by(order_by)
        if limit:
            q = q.limit(limit)
        return [d.to_dict() async for d in q.stream()]

    # ── Research Articles ─────────────────────────────────────────────────────

    async def save_research_article(self, article: ResearchArticle) -> Dict[str, Any]:
        return await self.create("research_articles", article.id, article.to_dict())

    async def get_research_article(self, article_id: str) -> Optional[Dict[str, Any]]:
        return await self.read("research_articles", article_id)

    async def query_research_articles(
        self, category: str = None, limit: int = 20
    ) -> List[Dict[str, Any]]:
        filters = [("category", "==", category)] if category else None
        return await self.query("research_articles", filters,
                                order_by="published_date", limit=limit)

    # ── News Articles ─────────────────────────────────────────────────────────

    async def save_news_article(self, article: NewsArticle) -> Dict[str, Any]:
        return await self.create("news_articles", article.id, article.to_dict())

    async def get_news_article(self, article_id: str) -> Optional[Dict[str, Any]]:
        return await self.read("news_articles", article_id)

    async def query_news_articles(
        self, category: str = None, limit: int = 20
    ) -> List[Dict[str, Any]]:
        filters = [("category", "==", category)] if category else None
        return await self.query("news_articles", filters,
                                order_by="published_date", limit=limit)

    # ── Custom Summaries ──────────────────────────────────────────────────────

    async def save_research_summary(
        self, summary: CustomResearchSummary
    ) -> Dict[str, Any]:
        return await self.create("custom_research_summaries",
                                 summary.id, summary.to_dict())

    async def save_news_summary(
        self, summary: CustomNewsSummary
    ) -> Dict[str, Any]:
        return await self.create("custom_news_summaries",
                                 summary.id, summary.to_dict())

    def get_health_status(self) -> Dict[str, Any]:
        return {
            "status":            "healthy",
            "mode":              "mock" if self.use_mock else "production",
            "project_id":        self.project_id,
            "collections":       list(FIRESTORE_COLLECTION_DEFINITIONS.keys()),
        }


# ── Filter helper for mock mode ───────────────────────────────────────────────

def _match(value: Any, op: str, target: Any) -> bool:
    try:
        if op == "==":            return value == target
        if op == "!=":            return value != target
        if op == "<":             return value < target
        if op == "<=":            return value <= target
        if op == ">":             return value > target
        if op == ">=":            return value >= target
        if op == "in":            return value in target
        if op == "array-contains": return isinstance(value, list) and target in value
    except TypeError:
        pass
    return False
