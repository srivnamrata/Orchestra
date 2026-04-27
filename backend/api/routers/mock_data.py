from datetime import datetime, timedelta

from fastapi import APIRouter

router = APIRouter(tags=["Mock Data"])


@router.get("/api/mock/tasks")
async def get_mock_tasks():
    return {
        "count": 5,
        "tasks": [
            {
                "task_id":     "task-001",
                "title":       "Review Q2 OKRs with team",
                "description": "Go through quarterly objectives and key results",
                "priority":    "high",
                "status":      "in_progress",
                "due_date":    "2026-04-15",
                "created_at":  "2026-04-01T09:00:00",
                "assigned_to": "you",
            },
            {
                "task_id":     "task-002",
                "title":       "Deploy latest features to production",
                "description": "Release new AI agent improvements",
                "priority":    "critical",
                "status":      "pending_review",
                "due_date":    "2026-04-10",
                "created_at":  "2026-04-05T10:30:00",
                "assigned_to": "engineering",
            },
            {
                "task_id":     "task-003",
                "title":       "Prepare presentation for stakeholders",
                "description": "Slides covering agent capabilities and metrics",
                "priority":    "medium",
                "status":      "open",
                "due_date":    "2026-04-20",
                "created_at":  "2026-04-06T14:00:00",
                "assigned_to": "you",
            },
            {
                "task_id":     "task-004",
                "title":       "Optimize database queries",
                "description": "Reduce query latency by 30%",
                "priority":    "high",
                "status":      "open",
                "due_date":    "2026-04-25",
                "created_at":  "2026-04-01T11:00:00",
                "assigned_to": "databases",
            },
            {
                "task_id":     "task-005",
                "title":       "Document API endpoints",
                "description": "Create comprehensive API documentation",
                "priority":    "medium",
                "status":      "completed",
                "due_date":    "2026-04-08",
                "created_at":  "2026-03-25T13:00:00",
                "assigned_to": "you",
            },
        ],
    }


@router.get("/api/mock/events")
async def get_mock_events():
    now = datetime.now()
    return {
        "count": 4,
        "events": [
            {
                "event_id":   "evt-001",
                "title":      "Team Standup",
                "location":   "Conference Room A",
                "start_time": (now + timedelta(hours=1)).isoformat(),
                "end_time":   (now + timedelta(hours=1, minutes=30)).isoformat(),
                "attendees":  8,
                "status":     "confirmed",
                "created_at": now.isoformat(),
            },
            {
                "event_id":   "evt-002",
                "title":      "1-on-1 with Manager",
                "location":   "Virtual - Zoom",
                "start_time": (now + timedelta(hours=3)).isoformat(),
                "end_time":   (now + timedelta(hours=3, minutes=30)).isoformat(),
                "attendees":  2,
                "status":     "confirmed",
                "created_at": now.isoformat(),
            },
            {
                "event_id":   "evt-003",
                "title":      "Project Planning Session",
                "location":   "Main Office - Open Space",
                "start_time": (now + timedelta(days=1, hours=10)).isoformat(),
                "end_time":   (now + timedelta(days=1, hours=11, minutes=30)).isoformat(),
                "attendees":  12,
                "status":     "confirmed",
                "created_at": now.isoformat(),
            },
            {
                "event_id":   "evt-004",
                "title":      "Stakeholder Review",
                "location":   "Board Room",
                "start_time": (now + timedelta(days=3)).isoformat(),
                "end_time":   (now + timedelta(days=3, hours=2)).isoformat(),
                "attendees":  6,
                "status":     "tentative",
                "created_at": now.isoformat(),
            },
        ],
    }
