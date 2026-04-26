"""
GitHub Integration Service (Mock)
Provides repository and pull request data for the Orchestra platform.
"""

class GitHubService:
    async def get_recent_activity(self):
        """Mock recent activity from GitHub"""
        return {
            "repositories": [
                {"name": "orchestra-core", "url": "https://github.com/org/orchestra-core", "stars": 124, "last_commit": "2h ago"},
                {"name": "orchestra-ui", "url": "https://github.com/org/orchestra-ui", "stars": 45, "last_commit": "5h ago"}
            ],
            "pull_requests": [
                {"id": 42, "title": "Integration with Vertex AI Gemini 1.5", "status": "APPROVED", "repo": "orchestra-core"},
                {"id": 108, "title": "Mobile responsive dashboard navigation", "status": "BLOCKED", "repo": "orchestra-ui"}
            ]
        }

def create_github_service():
    return GitHubService()
