"""
Coder Agent - Handles code analysis, refactoring, and logic generation.
"""
import logging
from typing import Dict, Any
from backend.services.llm_utils import parse_llm_json

logger = logging.getLogger(__name__)

class CoderAgent:
    def __init__(self, llm_service):
        self.llm = llm_service

    async def execute(self, step: Dict[str, Any], previous_results: Dict) -> Dict[str, Any]:
        objective = step.get("params", {}).get("objective", "Analyze code")
        code_snippet = step.get("params", {}).get("code", "")

        prompt = f"""
        You are the Coder Agent. 
        Objective: {objective}
        Target Code: {code_snippet}

        Analyze the code for bugs or efficiency improvements. Return JSON:
        {{
            "analysis": "Summary of findings",
            "suggested_fix": "Improved code or refactor",
            "complexity_impact": "low/medium/high"
        }}
        """
        try:
            raw = await self.llm.call(prompt)
            result = parse_llm_json(raw)
            return {"status": "success", "data": result}
        except Exception as e:
            logger.error(f"Coder error: {e}")
            return {"status": "error", "message": str(e)}