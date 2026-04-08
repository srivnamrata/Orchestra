"""
Research Agent - Sub-agent for fetching and analyzing AI/ML research.
Connects the Orchestrator with the Research MCP server.
"""

import asyncio
from typing import Dict, Any
import logging
from backend.mcp_tools.mcp_client import call_tool, MCPServerType

logger = logging.getLogger(__name__)


class ResearchAgent:
    """
    Sub-agent specialized in deep research operations.
    Acts as a router between the Orchestrator step definitions and the Research MCP server.
    """
    
    def __init__(self, knowledge_graph=None):
        self.knowledge_graph = knowledge_graph
    
    async def execute(self, step: Dict[str, Any], previous_results: Dict) -> Dict[str, Any]:
        """
        Execute a research step by calling the designated MCP Tool.
        """
        step_type = step.get("type", "")
        inputs = step.get("inputs", {})
        
        logger.info(f"ResearchAgent executing step type: {step_type}")
        
        try:
            if step_type == "fetch_weekly_highlights":
                # Ensure we pick top 10 news specifically for data science, AI, GENAI, breakthroughs
                inputs.setdefault("max_articles", 10)
                inputs.setdefault("categories", [
                    "artificial_intelligence", 
                    "data_science", 
                    "machine_learning",
                    "robotics",
                    "deep_learning",
                    "nlp",
                    "computer_vision",
                    "reinforcement_learning"
                ])
                return await call_tool(MCPServerType.RESEARCH, "fetch_weekly_highlights", inputs)
            elif step_type == "search_articles":
                # Inject user's preferred topics if query is generic or missing
                if not inputs.get("query"):
                    inputs["query"] = "major breakthroughs in AI and GEN AI, Robotics, new research, algorithms, latest advancements etc."
                inputs.setdefault("limit", 10)
                return await call_tool(MCPServerType.RESEARCH, "search_articles", inputs)
            elif step_type == "get_article_summary":
                return await call_tool(MCPServerType.RESEARCH, "get_article_summary", inputs)
            elif step_type == "get_trending_topics":
                return await call_tool(MCPServerType.RESEARCH, "get_trending_topics", inputs)
            elif step_type == "generate_audio":
                return await call_tool(MCPServerType.RESEARCH, "generate_audio", inputs)
            elif step_type == "get_weekly_digest":
                return await call_tool(MCPServerType.RESEARCH, "get_weekly_digest", inputs)
            elif step_type == "create_custom_summary":
                # Ensure custom summaries have a strong AI/Data Science focus
                if "focus_areas" not in inputs:
                    inputs["focus_areas"] = [
                        "Data Science", "AI", "Major Breakthroughs", 
                        "New Algorithms", "GenAI", "Robotics", "Deep Learning",
                        "NLP", "Computer Vision", "Reinforcement Learning"
                    ]
                return await call_tool(MCPServerType.RESEARCH, "create_custom_summary", inputs)
            else:
                return {
                    "status": "error",
                    "message": f"unsupported_step_type: {step_type}"
                }
        except Exception as e:
            logger.error(f"Research agent error: {e}")
            return {"status": "error", "message": str(e)}
