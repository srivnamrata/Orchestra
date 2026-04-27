import logging

from fastapi import APIRouter

from backend.api import state

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Guru"])


@router.post("/api/guru/audit")
async def guru_life_audit():
    """Param Mitra life audit — pulls real data from git, email, tasks, and books."""
    if not state.param_mitra:
        return {"status": "error", "message": "Guru agent not initialized"}

    from backend.database import get_all_tasks, get_all_books

    try:
        gh_data    = await state.github_service.get_recent_activity() if state.github_service else {}
        email_data = await state.email_service.get_unread_summaries() if state.email_service else {}
    except Exception:
        gh_data    = {}
        email_data = {}

    tasks = get_all_tasks(limit=20)
    books = get_all_books()

    done_tasks     = [t for t in tasks if t.status == "done"]
    open_tasks     = [t for t in tasks if t.status not in ("done", "cancelled")]
    efficiency_pct = int(len(done_tasks) / len(tasks) * 100) if tasks else 0

    prs       = gh_data.get("pull_requests", [])
    repos     = gh_data.get("repositories", [])
    git_summary = (
        f"{len(repos)} active repos. PRs: "
        + ", ".join(f"#{p['id']} '{p['title']}' [{p['status']}]" for p in prs[:3])
        if prs else "No recent commits found."
    )

    urgent_emails = email_data.get("urgent", [])
    email_summary = (
        f"{email_data.get('unread_count', 0)} unread emails. Urgent: "
        + "; ".join(f"'{e['subject']}' from {e['from']}" for e in urgent_emails[:3])
        if urgent_emails else "No urgent emails."
    )

    task_summary = (
        f"{len(open_tasks)} open tasks, {len(done_tasks)} completed. "
        f"Efficiency: {efficiency_pct}%. "
        + ("Overdue: " + ", ".join(f"'{t.title}'" for t in open_tasks[:3]) if open_tasks else "")
    )

    reading_list = ", ".join(
        f"'{b.title}' ({b.current_page}/{b.total_pages} pages)" for b in books[:5]
    ) if books else "No books in reading list."

    context = {
        "git_summary":   git_summary,
        "email_summary": email_summary,
        "task_status":   task_summary,
        "goals":         f"Reading: {reading_list}",
    }

    try:
        result = await state.param_mitra.generate_audit(context)
        return {"status": "success", "audit": result}
    except Exception as e:
        logger.error(f"Guru audit error: {e}")
        return {"status": "error", "message": str(e)}
