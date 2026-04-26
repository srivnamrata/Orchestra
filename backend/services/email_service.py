"""
Email (Gmail) Integration Service (Mock)
Provides unread message summaries for the Orchestra platform.
"""

class EmailService:
    async def get_unread_summaries(self):
        """Mock unread email summaries"""
        return {
            "unread_count": 12,
            "urgent": [
                {
                    "subject": "Client feedback regarding the Q1 report latency",
                    "from": "major-client@example.com",
                    "summary": "The client is reporting 2s+ latency on dashboard loads. Requires immediate investigation.",
                    "priority": "high"
                },
                {
                    "subject": "Security Alert: New login detected",
                    "from": "google-accounts@google.com",
                    "summary": "New login from San Francisco, CA. User confirmed it was them.",
                    "priority": "medium"
                }
            ]
        }

def create_email_service():
    return EmailService()
