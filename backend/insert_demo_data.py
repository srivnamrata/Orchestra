"""
Demo Data Insertion Script
Populates the database with sample tasks, notes, and calendar events for testing
Run this script once to seed the database with demo data

Usage:
    python insert_demo_data.py           # Insert demo data (skip if exists)
    python insert_demo_data.py --reset   # Clear and re-insert all demo data
    python insert_demo_data.py --help    # Show this help message
"""

import sys
from datetime import datetime, timedelta
import uuid
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import SessionLocal, Task, Note, CalendarEvent, init_db


def generate_id(prefix: str) -> str:
    """Generate a unique ID with a prefix"""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def insert_demo_tasks():
    """Insert demo tasks into the database"""
    db = SessionLocal()
    
    try:
        # Check if demo data already exists
        existing_count = db.query(Task).count()
        if existing_count > 0:
            print(f"⚠️  Database already contains {existing_count} tasks. Skipping task insertion.")
            return
        
        print("\n📝 Inserting Demo Tasks...")
        
        now = datetime.utcnow()
        
        # Task 1: Completed Task (past due date)
        task1 = Task(
            task_id=generate_id("task"),
            title="Write Database Schema Documentation",
            description="Document all database tables, relationships, and field definitions. Include examples and use cases.",
            priority="high",
            status="completed",
            due_date=now - timedelta(days=5),
            created_at=now - timedelta(days=10),
            completed_at=now - timedelta(days=2),
            assigned_to="Administrator",
            subtasks=3
        )
        
        # Task 2: In Progress Task (due soon)
        task2 = Task(
            task_id=generate_id("task"),
            title="Implement API Authentication Layer",
            description="Add JWT token-based authentication to all API endpoints. Include refresh token mechanism and rate limiting.",
            priority="critical",
            status="in_progress",
            due_date=now + timedelta(days=2),
            created_at=now - timedelta(days=7),
            assigned_to="Administrator",
            subtasks=5
        )
        
        # Task 3: Open Task (normal priority)
        task3 = Task(
            task_id=generate_id("task"),
            title="Optimize Database Query Performance",
            description="Review slow queries, add appropriate indexes, and implement caching for frequently accessed data.",
            priority="medium",
            status="open",
            due_date=now + timedelta(days=14),
            created_at=now - timedelta(days=3),
            assigned_to="Administrator",
            subtasks=4
        )
        
        # Task 4: Open Task (high priority)
        task4 = Task(
            task_id=generate_id("task"),
            title="Create Unit Tests for Core Agents",
            description="Write comprehensive unit tests for Critic, Vibe-Check, and Debate engine agents. Aim for 80%+ coverage.",
            priority="high",
            status="open",
            due_date=now + timedelta(days=7),
            created_at=now - timedelta(days=1),
            assigned_to="Administrator",
            subtasks=6
        )
        
        # Task 5: Completed Task (recent)
        task5 = Task(
            task_id=generate_id("task"),
            title="Set Up Development Environment",
            description="Configure Docker containers, install dependencies, and set up local database.",
            priority="high",
            status="completed",
            due_date=now - timedelta(days=1),
            created_at=now - timedelta(days=8),
            completed_at=now - timedelta(hours=2),
            assigned_to="Administrator",
            subtasks=2
        )
        
        # Task 6: Open Task (low priority)
        task6 = Task(
            task_id=generate_id("task"),
            title="Add Dark Mode Support",
            description="Implement dark mode toggle and color theme switching for the frontend UI.",
            priority="low",
            status="open",
            due_date=now + timedelta(days=30),
            created_at=now - timedelta(days=2),
            assigned_to="Administrator",
            subtasks=3
        )
        
        # Task 7: In Progress Task
        task7 = Task(
            task_id=generate_id("task"),
            title="Integrate Real-Time Notifications",
            description="Set up WebSocket connections for real-time activity feeds and event notifications.",
            priority="medium",
            status="in_progress",
            due_date=now + timedelta(days=10),
            created_at=now - timedelta(days=5),
            assigned_to="Administrator",
            subtasks=4
        )
        
        # Task 8: Open Task (blocked by other tasks)
        task8 = Task(
            task_id=generate_id("task"),
            title="Deploy to Production",
            description="Deploy latest version to production environment, configure monitoring and logging.",
            priority="critical",
            status="open",
            due_date=now + timedelta(days=21),
            created_at=now - timedelta(days=4),
            assigned_to="Administrator",
            dependencies=f"{task2.task_id},{task4.task_id}",
            subtasks=5
        )
        
        # Task 9: Completed Task
        task9 = Task(
            task_id=generate_id("task"),
            title="Review Code from Team",
            description="Code review for pull requests from the development team. Provide feedback and approve changes.",
            priority="medium",
            status="completed",
            due_date=now - timedelta(days=2),
            created_at=now - timedelta(days=5),
            completed_at=now - timedelta(days=1),
            assigned_to="Administrator",
            subtasks=0
        )
        
        # Task 10: Open Task (upcoming)
        task10 = Task(
            task_id=generate_id("task"),
            title="Update Project Documentation",
            description="Update README, API documentation, and deployment guides with latest information.",
            priority="medium",
            status="open",
            due_date=now + timedelta(days=20),
            created_at=now - timedelta(days=2),
            assigned_to="Administrator",
            subtasks=3
        )
        
        # Add all tasks to session
        tasks = [task1, task2, task3, task4, task5, task6, task7, task8, task9, task10]
        db.add_all(tasks)
        db.commit()
        
        print(f"✅ Inserted {len(tasks)} demo tasks:")
        for task in tasks:
            print(f"   • {task.title} ({task.status}) - {task.priority}")
        
        return tasks

    except Exception as e:
        db.rollback()
        print(f"❌ Error inserting tasks: {e}")
        raise
    finally:
        db.close()


def insert_demo_calendar_events():
    """Insert demo calendar events into the database"""
    db = SessionLocal()
    
    try:
        # Check if demo data already exists
        existing_count = db.query(CalendarEvent).count()
        if existing_count > 0:
            print(f"⚠️  Database already contains {existing_count} calendar events. Skipping events insertion.")
            return
        
        print("\n📅 Inserting Demo Calendar Events...")
        
        now = datetime.utcnow()
        
        # Event 1: Team Meeting (Today at 2 PM)
        event1 = CalendarEvent(
            event_id=generate_id("event"),
            title="Team Standup Meeting",
            description="Daily team standup to discuss progress, blockers, and plans for the day.",
            start_time=now.replace(hour=14, minute=0, second=0, microsecond=0),
            end_time=now.replace(hour=14, minute=30, second=0, microsecond=0),
            location="Conference Room A",
            duration_minutes=30,
            status="scheduled",
            attendees='["Administrator", "John", "Sarah", "Mike"]',
            organizer="Administrator",
            color="#4FACFE"
        )
        
        # Event 2: Project Review (Tomorrow)
        event2 = CalendarEvent(
            event_id=generate_id("event"),
            title="Project Status Review",
            description="Quarterly project review with stakeholders. Present progress, metrics, and upcoming deliverables.",
            start_time=now.replace(day=now.day+1, hour=10, minute=0, second=0, microsecond=0),
            end_time=now.replace(day=now.day+1, hour=11, minute=30, second=0, microsecond=0),
            location="Executive Boardroom",
            duration_minutes=90,
            status="scheduled",
            attendees='["Administrator", "Executive Team", "Project Leads"]',
            organizer="CTO",
            color="#00F2FE"
        )
        
        # Event 3: Code Review Session (3 days from now)
        event3 = CalendarEvent(
            event_id=generate_id("event"),
            title="Code Review - API Layer",
            description="In-depth code review session for the new API authentication layer.",
            start_time=now + timedelta(days=3, hours=3),
            end_time=now + timedelta(days=3, hours=4),
            location="Virtual - Zoom",
            duration_minutes=60,
            status="scheduled",
            attendees='["Administrator", "Backend Team"]',
            organizer="Lead Developer",
            color="#F59E0B"
        )
        
        # Event 4: All-Hands Meeting (Next week)
        event4 = CalendarEvent(
            event_id=generate_id("event"),
            title="Company All-Hands Meeting",
            description="Company-wide meeting to discuss strategy, updates, and Q&A session.",
            start_time=now + timedelta(days=7, hours=9),
            end_time=now + timedelta(days=7, hours=10, minutes=30),
            location="Main Auditorium / Virtual",
            duration_minutes=90,
            is_all_day=False,
            status="scheduled",
            attendees='["All Staff"]',
            organizer="CEO",
            color="#10B981"
        )
        
        # Event 5: Client Demo (5 days from now)
        event5 = CalendarEvent(
            event_id=generate_id("event"),
            title="Client Demo - New Features",
            description="Demonstration of newly completed features to key client stakeholders.",
            start_time=now + timedelta(days=5, hours=15),
            end_time=now + timedelta(days=5, hours=16, minutes=30),
            location="Virtual - Microsoft Teams",
            duration_minutes=90,
            status="scheduled",
            attendees='["Administrator", "Product Manager", "Client Team"]',
            organizer="Product Manager",
            color="#EC4899"
        )
        
        # Event 6: Training Session (2 days from now)
        event6 = CalendarEvent(
            event_id=generate_id("event"),
            title="API Development Training",
            description="Training session on new API frameworks and best practices for the development team.",
            start_time=now + timedelta(days=2, hours=13),
            end_time=now + timedelta(days=2, hours=15),
            location="Training Room B",
            duration_minutes=120,
            status="scheduled",
            attendees='["Development Team"]',
            organizer="Tech Lead",
            color="#8B5CF6"
        )
        
        # Event 7: One-on-One (Tomorrow afternoon)
        event7 = CalendarEvent(
            event_id=generate_id("event"),
            title="1:1 with Team Lead",
            description="Weekly one-on-one meeting to discuss personal development and blockers.",
            start_time=now.replace(day=now.day+1, hour=15, minute=0, second=0, microsecond=0),
            end_time=now.replace(day=now.day+1, hour=15, minute=45, second=0, microsecond=0),
            location="Lead's Office",
            duration_minutes=45,
            status="scheduled",
            attendees='["Administrator", "Team Lead"]',
            organizer="Team Lead",
            color="#06B6D4"
        )
        
        # Event 8: Completed Meeting (Past)
        event8 = CalendarEvent(
            event_id=generate_id("event"),
            title="Sprint Planning Meeting",
            description="Sprint planning for the upcoming 2-week development cycle.",
            start_time=now - timedelta(days=7, hours=2),
            end_time=now - timedelta(days=7, hours=1),
            location="Zoom",
            duration_minutes=60,
            status="completed",
            attendees='["Administrator", "Scrum Master", "Development Team"]',
            organizer="Scrum Master",
            color="#F87171"
        )
        
        # Event 9: Recurring Meeting (Weekly standup)
        event9 = CalendarEvent(
            event_id=generate_id("event"),
            title="Weekly Team Sync",
            description="Weekly synchronization meeting for team updates and collaboration.",
            start_time=now + timedelta(days=2, hours=10),
            end_time=now + timedelta(days=2, hours=11),
            location="Conference Room",
            duration_minutes=60,
            status="scheduled",
            is_recurring=True,
            recurrence_rule="FREQ=WEEKLY;BYDAY=WE",
            attendees='["Development Team"]',
            organizer="Administrator",
            color="#84CC16"
        )
        
        # Event 10: Lunch Break (Today)
        event10 = CalendarEvent(
            event_id=generate_id("event"),
            title="Lunch Break",
            description="Team lunch break - off-site at local restaurant.",
            start_time=now.replace(hour=12, minute=0, second=0, microsecond=0),
            end_time=now.replace(hour=13, minute=0, second=0, microsecond=0),
            location="Downtown Restaurant",
            duration_minutes=60,
            status="scheduled",
            attendees='["Team Members"]',
            organizer="Administrator",
            color="#FBBF24"
        )
        
        # Add all events to session
        events = [event1, event2, event3, event4, event5, event6, event7, event8, event9, event10]
        db.add_all(events)
        db.commit()
        
        print(f"✅ Inserted {len(events)} demo calendar events:")
        for event in events:
            print(f"   • {event.title} - {event.start_time.strftime('%Y-%m-%d %H:%M')} ({event.status})")
        
        return events

    except Exception as e:
        db.rollback()
        print(f"❌ Error inserting calendar events: {e}")
        raise
    finally:
        db.close()


def insert_demo_notes():
    """Insert demo notes into the database"""
    db = SessionLocal()
    
    try:
        # Check if demo data already exists
        existing_count = db.query(Note).count()
        if existing_count > 0:
            print(f"⚠️  Database already contains {existing_count} notes. Skipping notes insertion.")
            return
        
        print("\n📌 Inserting Demo Notes...")
        
        now = datetime.utcnow()
        
        # Note 1: API Design Notes
        note1 = Note(
            note_id=generate_id("note"),
            title="API Endpoint Design Patterns",
            content="""# RESTful API Design Best Practices

## Core Principles
- Use meaningful resource names
- Implement proper HTTP status codes
- Version your APIs
- Implement pagination for large datasets

## Examples
- GET /api/v1/tasks - Retrieve all tasks
- POST /api/v1/tasks - Create new task
- PUT /api/v1/tasks/{id} - Update task
- DELETE /api/v1/tasks/{id} - Delete task

## Authentication
- Use JWT tokens for stateless authentication
- Implement refresh token rotation
- Add rate limiting per API key""",
            category="Technical",
            tags="api,design,rest,best-practices",
            is_pinned=True,
            created_at=now - timedelta(days=5),
            created_by="Administrator"
        )
        
        # Note 2: Project Architecture
        note2 = Note(
            note_id=generate_id("note"),
            title="System Architecture Overview",
            content="""# Multi-Agent Productivity Assistant Architecture

## Components
1. **Frontend**: HTML5, CSS, JavaScript
2. **Backend**: FastAPI, SQLAlchemy
3. **Database**: PostgreSQL/AlloyDB
4. **Agents**: Critic, Vibe-Check, Debate Engine

## Data Flow
Frontend → API → Services → Database
         ← Response ←

## Key Features
- Real-time notifications via WebSockets
- Distributed task processing
- Knowledge graph for context understanding
- Multi-agent collaboration system""",
            category="Architecture",
            tags="system,architecture,design",
            is_pinned=True,
            created_at=now - timedelta(days=10),
            created_by="Administrator"
        )
        
        # Note 3: Development Checklist
        note3 = Note(
            note_id=generate_id("note"),
            title="Development Checklist - Sprint 5",
            content="""# Sprint 5 Development Checklist

## Frontend
- [x] Implement command palette
- [x] Add real-time search
- [ ] Implement dark mode
- [ ] Add export functionality

## Backend
- [x] Set up database models
- [x] Create API endpoints
- [ ] Add data validation
- [ ] Implement caching

## Testing
- [ ] Write unit tests (aim for 80% coverage)
- [ ] Integration testing
- [ ] Load testing for API endpoints
- [ ] E2E testing for critical flows

## Documentation
- [x] API documentation
- [x] Database schema docs
- [ ] Deployment guide
- [ ] User guide""",
            category="Planning",
            tags="checklist,sprint,development",
            is_pinned=False,
            created_at=now - timedelta(days=3),
            created_by="Administrator"
        )
        
        # Note 4: Meeting Notes
        note4 = Note(
            note_id=generate_id("note"),
            title="Team Standup Notes - April 8",
            content="""# Team Standup - April 8, 2026

## Attendees
- John (Frontend Dev)
- Sarah (Backend Dev)
- Mike (QA)
- Administrator (Tech Lead)

## Updates
**John**: Completed command palette implementation, working on dark mode
**Sarah**: Adding API caching layer, ~80% complete
**Mike**: Testing new features, found 2 minor bugs

## Blockers
- Sarah blocked on API specification clarification
- Waiting for design approval on dark mode colors

## Next Steps
1. Complete API caching
2. Deploy to staging environment
3. Start load testing
4. Plan next sprint features""",
            category="Meetings",
            tags="standup,meeting,team",
            is_pinned=False,
            created_at=now - timedelta(days=1),
            created_by="Administrator"
        )
        
        # Note 5: Quick Reference
        note5 = Note(
            note_id=generate_id("note"),
            title="Quick Command Reference",
            content="""# FlowAlchemy Command Palette Quick Reference

## Essential Shortcuts
| Command | Shortcut | Action |
|---------|----------|--------|
| Open Palette | Ctrl+K | Search and execute commands |
| New Task | Ctrl+N | Create new task |
| New Event | Ctrl+E | Schedule event |
| New Note | Ctrl+Alt+N | Write note |
| Critic Demo | Ctrl+Shift+C | Run analysis |
| Vibe Check | Ctrl+Shift+V | Check alignment |
| Debate | Ctrl+Shift+D | Start debate |

## Search Tips
- Type "task" to see task commands
- Type "create" for creation options
- Type "agent" for agent commands
- Search is case-insensitive""",
            category="Reference",
            tags="reference,shortcuts,guide",
            is_pinned=True,
            created_at=now - timedelta(days=2),
            created_by="Administrator"
        )
        
        # Add all notes to session
        notes = [note1, note2, note3, note4, note5]
        db.add_all(notes)
        db.commit()
        
        print(f"✅ Inserted {len(notes)} demo notes:")
        for note in notes:
            print(f"   • {note.title} ({note.category})" + (" [PINNED]" if note.is_pinned else ""))
        
        return notes

    except Exception as e:
        db.rollback()
        print(f"❌ Error inserting notes: {e}")
        raise
    finally:
        db.close()


def clear_all_data():
    """Clear all existing data from the database"""
    db = SessionLocal()
    
    try:
        # Count records before deletion
        task_count = db.query(Task).count()
        event_count = db.query(CalendarEvent).count()
        note_count = db.query(Note).count()
        
        # Delete all records
        db.query(Task).delete()
        db.query(CalendarEvent).delete()
        db.query(Note).delete()
        db.commit()
        
        print(f"✅ Cleared all existing data:")
        if task_count > 0:
            print(f"   • Deleted {task_count} tasks")
        if event_count > 0:
            print(f"   • Deleted {event_count} calendar events")
        if note_count > 0:
            print(f"   • Deleted {note_count} notes")
        
        return task_count, event_count, note_count
    
    except Exception as e:
        db.rollback()
        print(f"❌ Error clearing data: {e}")
        raise
    finally:
        db.close()


def main():
    """Main function to insert all demo data"""
    
    # Check for command line arguments
    reset_flag = "--reset" in sys.argv
    help_flag = "--help" in sys.argv or "-h" in sys.argv
    
    if help_flag:
        print(__doc__)
        return
    
    print("=" * 70)
    print("🚀 DEMO DATA INSERTION SCRIPT")
    print("=" * 70)
    
    try:
        # Initialize database tables
        print("\n🔧 Initializing database...")
        init_db()
        print("✅ Database tables created/verified")
        
        # Clear existing data if --reset flag is used
        if reset_flag:
            print("\n🗑️  Clearing existing data (--reset flag detected)...")
            clear_all_data()
        
        # Insert demo data
        tasks = insert_demo_tasks()
        events = insert_demo_calendar_events()
        notes = insert_demo_notes()
        
        # Check if any data was inserted
        if not tasks and not events and not notes:
            print("\n⚠️  No new demo data was inserted (database already contains data)")
            print("    Use: python insert_demo_data.py --reset")
            print("    to clear and re-insert all demo data")
        
        print("\n" + "=" * 70)
        print("✅ DEMO DATA INSERTION COMPLETE!")
        print("=" * 70)
        print("\n📊 Summary:")
        if tasks:
            print(f"   ✓ {len(tasks)} Demo Tasks (various states)")
        if events:
            print(f"   ✓ {len(events)} Calendar Events (meetings, training, etc.)")
        if notes:
            print(f"   ✓ {len(notes)} Demo Notes (documentation, checklists, etc.)")
        
        if not tasks and not events and not notes:
            print("   (No new data inserted - database already populated)")
        
        print("\n💡 You can now use the application with demo data!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
