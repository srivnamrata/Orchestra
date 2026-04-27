"""
Canonical Firestore schemas have been consolidated into
backend/services/firestore_schemas.py.

This module re-exports everything from there so that existing imports in the
mcp_tools package continue to work without modification.
"""

from backend.services.firestore_schemas import (   # noqa: F401
    # Research / news content schemas
    ResearchArticle,
    CustomResearchSummary,
    NewsArticle,
    CustomNewsSummary,
    ResearchSource,
    ResearchCategory,
    NewsSource,
    NewsCategory,
    # MCP audit schemas
    AuditEvent,
    AccessLog,
    SystemConfig,
    # Registry / rules / helpers
    FIRESTORE_COLLECTION_DEFINITIONS,
    DATA_VALIDATION_RULES,
    TTL_POLICIES,
    get_collection_schema,
    validate_document,
)
