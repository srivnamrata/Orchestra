"""
Liaison Agent - The "Diplomat". Fixes communication tone and manages empathy.
"""
import logging
from typing import Dict, Any
from backend.services.llm_utils import parse_llm_json

logger = logging.getLogger(__name__)

class LiaisonAgent:
    def __init__(self, llm_service):
        self.llm = llm_service

    async def execute(self, step: Dict[str, Any], previous_results: Dict) -> Dict[str, Any]:
        original_text = step.get("params", {}).get("text", "")
        recipient = step.get("params", {}).get("recipient", "Team")

        prompt = f"""
        You are the Liaison Agent. Your goal is to ensure professional, warm, and clear communication.
        The following draft was flagged as potentially harsh or transactional:
        "{original_text}"

        Rewrite this for {recipient} to be more empathetic and effective. Return JSON:
        {{
            "original": "{original_text}",
            "revised": "Improved version",
            "tone_changes": ["Added greeting", "softened language"]
        }}
        """
        try:
            raw = await self.llm.call(prompt)
            return parse_llm_json(raw)
        except Exception as e:
            logger.error(f"Liaison error: {e}")
            return {"status": "error", "message": str(e)}