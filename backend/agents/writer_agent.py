"""
Writer Agent - Specializes in drafting reports, emails, and documentation.
"""
import logging
from typing import Dict, Any
from backend.services.llm_utils import parse_llm_json

logger = logging.getLogger(__name__)

class WriterAgent:
    def __init__(self, llm_service):
        self.llm = llm_service

    async def execute(self, step: Dict[str, Any], previous_results: Dict) -> Dict[str, Any]:
        topic = step.get("params", {}).get("topic", "General Report")
        format_type = step.get("params", {}).get("format", "markdown")
        context = step.get("params", {}).get("context", "")

        prompt = f"""
        You are the Writer Agent in a multi-agent system.
        Topic: {topic}
        Format: {format_type}
        Context from previous steps: {context}

        Draft a high-quality document. Return the result in JSON format:
        {{
            "title": "Title of the document",
            "content": "The full body text...",
            "word_count": number
        }}
        """
        try:
            raw = await self.llm.call(prompt)
            result = parse_llm_json(raw)
            return {"status": "success", "data": result}
        except Exception as e:
            logger.error(f"Writer error: {e}")
            return {"status": "error", "message": str(e)}