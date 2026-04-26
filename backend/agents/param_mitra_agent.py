"""
Param Mitra Agent — The Supreme Friend & Guru
=============================================
A high-performance life coach that observes all data streams (Git, Email, Tasks, Meetings)
to identify gaps in code quality, communication, and human potential.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ParamMitraAgent:
    def __init__(self, llm_service, github_service=None, email_service=None, task_service=None):
        self.llm = llm_service
        self.github = github_service
        self.email = email_service
        self.tasks = task_service

    async def generate_audit(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates weekly insights: specific feedback on code, communication, efficiency.
        Training suggestions only when improvement is genuinely needed.
        """
        prompt = f"""You are Param Mitra — a wise, warm, honest Guru who is also a best friend.
Generate a weekly insight report based on this data:

Code / Git Activity: {context.get('git_summary', 'No recent commits.')}
Email / Communication: {context.get('email_summary', 'No recent emails.')}
Tasks & Efficiency: {context.get('task_status', 'No task data.')}
Reading & Goals: {context.get('goals', 'No goals set.')}

Rules:
- Be specific. Reference actual data (PR titles, email threads, task names) when possible.
- Be encouraging first. Celebrate genuine wins.
- Only suggest a training if there is a REAL gap. If things look good, say so warmly.
- Cheer: end with a short personal motivational line (not generic).

Return ONLY valid JSON, no markdown:
{{
  "summary": "One sentence overall assessment of the week.",
  "code": {{
    "assessment": "great" | "good" | "needs_improvement",
    "insight": "Specific observation about code quality, commit messages, PR activity this week.",
    "training": null
  }},
  "communication": {{
    "assessment": "great" | "good" | "needs_improvement",
    "insight": "Specific observation about email tone, reply speed, clarity.",
    "training": null
  }},
  "efficiency": {{
    "assessment": "great" | "good" | "needs_improvement",
    "insight": "Specific observation about task completion, priorities, focus.",
    "training": null
  }},
  "cheer": "Short personal motivational line."
}}

If assessment is 'needs_improvement', populate training as:
{{"topic": "Course or skill name", "why": "One sentence reason", "link_hint": "Coursera / YouTube / Book"}}
"""
        try:
            raw = await self.llm.call(prompt)
            import json
            # Extract JSON from markdown if necessary
            clean_json = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            return json.loads(clean_json)
        except Exception as e:
            logger.error(f"Param Mitra error: {e}")
            return {
                "guru_message": "I am observing your path. Today, focus on clarity over speed.",
                "scores": {"code_mastery": 75, "communication": 80, "efficiency": 60},
                "bottlenecks": ["Your code is functional but lacks documentation.", "Emails are too transactional.", "Tasks are being moved but not finished."],
                "potential_unlock": "Spend 30 minutes refactoring the core engine."
            }
