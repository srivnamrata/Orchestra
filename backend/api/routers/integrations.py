import logging

from fastapi import APIRouter, HTTPException, Request

from backend.api import state

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/github/activity")
async def get_github_activity():
    try:
        return await state.github_service.get_recent_activity()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/slack/summary")
async def get_slack_summary():
    try:
        return await state.slack_service.get_channel_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/email/urgent")
async def get_email_urgent():
    try:
        return await state.email_service.get_unread_summaries()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/feedback")
async def submit_feedback(request: Request):
    data = await request.json()
    print(f"🎓 ACADEMY FEEDBACK: Agent={data.get('agent')} Type={data.get('type')}")
    return {"status": "success", "message": "Feedback captured for learning loop"}
