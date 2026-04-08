"""
News Agent - Sub-agent for fetching and analyzing news.
Connects the Orchestrator with the News MCP server.
"""

import asyncio
from typing import Dict, Any
import logging
from backend.mcp_tools.mcp_client import call_tool, MCPServerType

logger = logging.getLogger(__name__)


class NewsAgent:
    """
    Sub-agent specialized in news operations.
    Acts as a router between the Orchestrator step definitions and the News MCP server.
    """
    
    def __init__(self, knowledge_graph=None):
        self.knowledge_graph = knowledge_graph
    
    async def execute(self, step: Dict[str, Any], previous_results: Dict) -> Dict[str, Any]:
        """
        Execute a news step by calling the designated MCP Tool.
        """
        step_type = step.get("type", "")
        inputs = step.get("inputs", {})
        
        logger.info(f"NewsAgent executing step type: {step_type}")
        
        try:
            if step_type == "fetch_weekly_headlines":
                # Ensure we fetch top news specifically focusing on AI and tech breakthroughs
                inputs.setdefault("max_articles", 10)
                inputs.setdefault("categories", ["technology", "science", "business"])
                return await call_tool(MCPServerType.NEWS, "fetch_weekly_headlines", inputs)
            elif step_type == "get_news_summary":
                return await call_tool(MCPServerType.NEWS, "get_news_summary", inputs)
            elif step_type == "search_news":
                # Inject user's preferred topics if query is generic or missing
                if not inputs.get("query"):
                    inputs["query"] = "AI AND Data Science AND major breakthroughs AND Generative AI"
                inputs.setdefault("limit", 10)
                return await call_tool(MCPServerType.NEWS, "search_news", inputs)
            elif step_type == "generate_audio":
                return await call_tool(MCPServerType.NEWS, "generate_audio", inputs)
            elif step_type == "get_weekly_digest":
                return await call_tool(MCPServerType.NEWS, "get_weekly_digest", inputs)
            elif step_type == "create_custom_summary":
                # Ensure custom summaries have a strong AI/Data Science focus
                if "focus_areas" not in inputs:
                    inputs["focus_areas"] = [
                        "Data Science in News", "AI Industry Adoptions", "Major Technological Breakthroughs", 
                        "New Algorithm Deployments", "GenAI Trends"
                    ]
                return await call_tool(MCPServerType.NEWS, "create_custom_summary", inputs)
            elif step_type == "get_trending_topics":
                return await call_tool(MCPServerType.NEWS, "get_trending_topics", inputs)
            else:
                return {
                    "status": "error",
                    "message": f"unsupported_step_type: {step_type}"
                }
        except Exception as e:
            logger.error(f"News agent error: {e}")
            return {"status": "error", "message": str(e)}
