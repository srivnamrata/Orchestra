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


@router.get("/api/mock/bottlenecks")
async def get_mock_bottlenecks():
    return {
        "bottlenecks": [
            {
                "id": "bn-1",
                "source": "github",
                "icon_class": "fa-brands fa-github",
                "icon_color": "#e0e0e0",
                "title": "PR #42 — API rate limiter",
                "detail": "2 failing checks: <span style='color:var(--g-red); font-family:var(--font-mono); font-size:11px;'>unit-tests</span>, <span style='color:var(--g-red); font-family:var(--font-mono); font-size:11px;'>lint</span>",
                "action_text": "Review & unblock"
            },
            {
                "id": "bn-2",
                "source": "slack",
                "icon_class": "fa-brands fa-slack",
                "icon_color": "#e01e5a",
                "title": "@you in #backend",
                "detail": "Can you unblock the <span style='color:var(--g-amber); font-weight:600;'>deploy pipeline</span>?",
                "action_text": "Review & unblock"
            },
            {
                "id": "bn-3",
                "source": "email",
                "icon_class": "fa-solid fa-envelope",
                "icon_color": "#4285f4",
                "title": "Re: Product launch sign-off",
                "detail": "Awaiting approval — <span style='color:var(--g-red); font-weight:600;'>2 days overdue</span>",
                "action_text": "Review & reply"
            }
        ]
    }
