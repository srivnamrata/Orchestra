import logging
import asyncio

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.api import state

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    return {
        "status":    "healthy",
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "services": {
            "orchestrator":    "ready",
            "critic_agent":    "running" if state.config and state.config.CRITIC_AGENT_ENABLED else "disabled",
            "knowledge_graph": "ready",
            "pubsub":          "connected",
            "research_agent":  "ready",
            "news_agent":      "ready",
            "task_agent":      "ready",
            "scheduler_agent": "ready",
            "database":        "connected",
        },
    }


@router.get("/api/info", tags=["Health"])
async def root_info():
    return {
        "service": "Multi-Agent Productivity Assistant",
        "version": "1.0.0",
        "status":  "operational",
        "features": [
            "🧠 Orchestrator Agent - Primary coordinator",
            "🔍 Critic Agent - Proactive goal anticipation & autonomous replanning",
            "🔐 Security & Strategy Auditor - Cross-agent vibe-checking",
            "🗣️ Multi-Agent Debate Engine - Team consensus & voting",
            "📊 Knowledge Graph - Semantic understanding",
            "🔄 Real-time Pub/Sub - Inter-agent communication",
            "🏆 Survival Fitness Function - Rank best team outcomes",
        ],
        "innovation_highlights": [
            "Autonomous agents that think strategically",
            "Trustworthy AI through peer-review",
            "Multi-dimensional safety checks before execution",
            "Team consensus via intelligent debate",
            "Transparency in every decision",
        ],
    }


@router.get("/api/agents/status", tags=["Agents"])
async def get_agents_status():
    cfg      = state.config
    env_name = "production" if cfg and "Production" in cfg.__class__.__name__ else "development"
    return {
        "status": "operational",
        "agents": {
            "orchestrator":    {"status": "ready",   "role": "Primary Coordinator"},
            "critic_agent":    {"status": "running", "role": "Workflow Auditor"},
            "auditor_agent":   {"status": "ready",   "role": "Security Check"},
            "research_agent":  {"status": "ready",   "role": "Research Data"},
            "news_agent":      {"status": "ready",   "role": "News Feed"},
            "task_agent":      {"status": "ready",   "role": "Task Manager"},
            "scheduler_agent": {"status": "ready",   "role": "Calendar Manager"},
            "knowledge_agent": {"status": "ready",   "role": "Context Builder"},
        },
        "system": {
            "firestore":   "connected" if cfg and cfg.USE_FIRESTORE else "disabled",
            "pubsub":      "connected" if cfg and not cfg.USE_MOCK_PUBSUB else "mock",
            "llm":         "vertex_ai" if cfg and not cfg.USE_MOCK_LLM else "mock",
            "environment": env_name,
        },
    }


@router.get("/api/debug/db", tags=["Health"])
async def debug_db():
    import os
    from backend.database import (
        CLOUD_SQL_CONNECTION_NAME, DATABASE_URL, DB_NAME, DB_USER, get_all_tasks, engine
    )
    db_url_display = str(engine.url)
    try:
        tasks     = get_all_tasks(limit=5)
        is_sqlite = "sqlite" in db_url_display
        return {
            "engine":                  db_url_display,
            "cloud_sql_connection":    CLOUD_SQL_CONNECTION_NAME or "not set",
            "database_url_env":        DATABASE_URL or "not set",
            "db_name":                 DB_NAME,
            "db_type":                 "sqlite" if is_sqlite else "postgresql",
            "db_file_exists":          os.path.exists("/tmp/productivity.db") if is_sqlite else "n/a",
            "task_count":              len(tasks),
            "last_5_tasks": [
                {"id": t.task_id, "title": t.title, "priority": t.priority,
                 "created_at": t.created_at.isoformat()}
                for t in tasks
            ],
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc(), "engine": db_url_display}


@router.post("/api/debug/test-write", tags=["Health"])
async def debug_test_write():
    import uuid
    import traceback
    from backend.database import create_task_in_db, get_task_by_id
    test_id = f"test-{uuid.uuid4().hex[:6]}"
    try:
        task    = create_task_in_db(
            task_id=test_id,
            title="[DEBUG] Test task",
            description="Written by /api/debug/test-write",
            priority="low",
            source="debug",
        )
        readback = get_task_by_id(test_id)
        return {
            "write":    "success",
            "task_id":  task.task_id,
            "title":    task.title,
            "readback": readback.title if readback else "NOT FOUND — write/read mismatch!",
        }
    except Exception as e:
        return {"write": "failed", "error": str(e), "traceback": traceback.format_exc()}


@router.get("/agent/reasoning/stream", tags=["Proactive Monitor"])
async def agent_reasoning_stream():
    return StreamingResponse(
        state.proactive_monitor.reasoning_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/agent/monitor/scan", tags=["Proactive Monitor"])
async def trigger_manual_scan():
    asyncio.create_task(state.proactive_monitor.run_scan())
    return {"status": "scan_started", "message": "Proactive scan triggered"}


@router.get("/agent/monitor/notifications", tags=["Proactive Monitor"])
async def get_notifications():
    pm = state.proactive_monitor
    return {
        "status":        "success",
        "count":         len(pm.notifications),
        "last_scan_at":  pm.last_scan_at,
        "scan_count":    pm.scan_count,
        "notifications": pm.notifications,
    }


@router.delete("/agent/monitor/notifications/{notif_id}", tags=["Proactive Monitor"])
async def dismiss_notification(notif_id: str):
    state.proactive_monitor.notifications = [
        n for n in state.proactive_monitor.notifications if n.get("id") != notif_id
    ]
    return {"status": "dismissed", "id": notif_id}


@router.get("/agent/monitor/status", tags=["Proactive Monitor"])
async def monitor_status():
    pm = state.proactive_monitor
    return {
        "running":                pm._running,
        "scan_count":             pm.scan_count,
        "last_scan_at":           pm.last_scan_at,
        "pending_notifications":  len(pm.notifications),
        "agents_used": [
            "ProactiveMonitorAgent", "CriticAgent", "AuditorAgent",
            "SchedulerAgent", "TaskAgent",
        ],
    }
