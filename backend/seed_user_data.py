"""
Specialized Seeding Script for User: srivnamrata@gmail.com
Populates the database with 4 distinct projects to demonstrate Agentic AI features.
"""

import sys
import uuid
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import (
    init_db, create_user, create_task_in_db, 
    create_event_in_db, create_note_in_db,
    get_user_by_email, SessionLocal, User
)

def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

def seed():
    print("🚀 Initializing Orchestra Database Seeding...")
    init_db()
    
    email = "srivnamrata@gmail.com"
    password = "Atharv19@" # Note: In production this should be hashed
    
    db = SessionLocal()
    existing_user = db.query(User).filter(User.email == email).first()
    
    if not existing_user:
        print(f"👤 Creating user: {email}")
        user = create_user(email=email, name="Namrata Srivastava", password_hash=password)
    else:
        print(f"👤 User {email} already exists.")
        user = existing_user
    
    u_id = user.id
    now = datetime.utcnow()

    # --------------------------------------------------------------------------
    # PROJECT 1: AI INNOVATION SUMMIT (Event Orchestration)
    # Demonstrates: SchedulerAgent and TaskAgent collaboration.
    # --------------------------------------------------------------------------
    print("\n🏗️ Project 1: AI Innovation Summit")
    
    # Note for context
    create_note_in_db(
        generate_id("note"), "Summit Strategy", 
        "Objective: Launch the new Multi-Agent framework. Key speakers include CTO and Lead Data Scientist.",
        category="Strategy", tags="AI,Summit,Launch", user_id=u_id
    )
    
    # Tasks
    t1_id = generate_id("task")
    create_task_in_db(t1_id, "Finalize Speaker List", "Review and confirm all 10 speakers.", "high", now + timedelta(days=2), user_id=u_id)
    
    t2_id = generate_id("task")
    create_task_in_db(t2_id, "Design Summit Landing Page", "Need glassmorphism UI.", "medium", now + timedelta(days=5), user_id=u_id)
    
    # Event
    create_event_in_db(
        generate_id("event"), "Summit Kickoff Meeting", 
        now + timedelta(hours=4), now + timedelta(hours=5),
        location="Virtual - Zoom", description="Initial sync for summit logistics.", user_id=u_id
    )

    # --------------------------------------------------------------------------
    # PROJECT 2: INFRASTRUCTURE MIGRATION (The "Bottleneck" Demo)
    # Demonstrates: CriticAgent's ability to detect silent bottlenecks and suggest re-planning.
    # --------------------------------------------------------------------------
    print("🏗️ Project 2: Cloud Migration 2026")
    
    # A task that is overdue
    create_task_in_db(
        generate_id("task"), "Audit Legacy Database", "Identify all deprecated tables.", 
        "critical", now - timedelta(days=2), user_id=u_id
    )
    
    # A chain of dependencies that the Critic can optimize
    dep1 = generate_id("task")
    create_task_in_db(dep1, "Provision Staging Environment", "Setup GCP Cloud Run instances.", "high", now + timedelta(days=3), user_id=u_id)
    
    dep2 = generate_id("task")
    create_task_in_db(
        generate_id("task"), "Deploy Microservices", "Deploy all 12 services to staging.", 
        "high", now + timedelta(days=4), dependencies=dep1, user_id=u_id
    )
    
    # A conflict: Meeting scheduled before the dependency is likely to be finished
    create_event_in_db(
        generate_id("event"), "Migration Go-Live Review", 
        now + timedelta(days=1), now + timedelta(days=2),
        location="War Room", description="Reviewing deployment results (Warning: Tasks are still open!)", user_id=u_id
    )

    # --------------------------------------------------------------------------
    # PROJECT 3: AGENTIC RESEARCH R&D (The "Live Data" Demo)
    # Demonstrates: ResearchAgent and NewsAgent integration.
    # --------------------------------------------------------------------------
    print("🏗️ Project 3: Agentic Workflows R&D")
    
    create_note_in_db(
        generate_id("note"), "Research Direction: LLM Critics", 
        "Focusing on self-correcting loops in multi-agent systems. Check arXiv daily.",
        category="Research", tags="AI,Agents,Critic", user_id=u_id
    )
    
    create_task_in_db(
        generate_id("task"), "Synthesize ArXiv Findings", 
        "Read latest papers on 'Autonomous Re-planning'.", "medium", now + timedelta(days=7), user_id=u_id
    )

    # --------------------------------------------------------------------------
    # PROJECT 4: QUARTERLY PERFORMANCE REVIEW (Auditor & Vibe Check)
    # Demonstrates: AuditorAgent security checks and ParamMitra coaching.
    # --------------------------------------------------------------------------
    print("🏗️ Project 4: HR & Performance")
    
    # Security-sensitive task (for Auditor/Debate engine)
    create_task_in_db(
        generate_id("task"), "Export Employee Compensation Data", 
        "Export sensitive CSV for HR review. Ensure PII is masked.", 
        "critical", now + timedelta(days=1), user_id=u_id
    )
    
    # Event for Proactive Monitoring
    create_event_in_db(
        generate_id("event"), "1:1 with Engineering Director", 
        now + timedelta(days=2, hours=2), now + timedelta(days=2, hours=3),
        description="Discuss career growth and project bottlenecks.", user_id=u_id
    )

    db.close()
    print("\n" + "="*50)
    print("✅ DATABASE SEEDED SUCCESSFULLY")
    print(f"User: {email}")
    print("You can now explain functionality using:")
    print("1. Orchestration: The Summit project flow.")
    print("2. Critic/Monitor: The Cloud Migration bottleneck (Event vs Overdue Tasks).")
    print("3. Research/Knowledge: The R&D notes and synthesis tasks.")
    print("4. Security/Audit: The Compensation Export task (High risk).")
    print("="*50)

if __name__ == "__main__":
    seed()
