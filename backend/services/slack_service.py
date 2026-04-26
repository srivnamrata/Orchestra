"""
Slack Integration Service (Mock)
Provides channel and message data for the Orchestra platform.
"""

class SlackService:
    async def get_channel_summary(self, channel_name="#engineering-hq"):
        """Mock channel summary and recent messages"""
        return {
            "channel": channel_name,
            "topic": "API rate limits and deployment windows",
            "summaries": [
                {"text": "Discussed API rate limits for the new crawler", "type": "summarized", "ts": "1h ago"},
                {"text": "Confirmed deployment window for v1.2.0", "type": "decision", "ts": "3h ago"},
                {"text": "Need clarification on the auth flow for GitHub", "type": "action_item", "ts": "4h ago"}
            ]
        }

def create_slack_service():
    return SlackService()
