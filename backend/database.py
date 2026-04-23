"""
AlloyDB/PostgreSQL Database Configuration and Models
Handles persistent storage for Tasks, Notes, and Calendar Events
"""

import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

# Database URL Configuration
# For AlloyDB: postgresql+pg8000://user:password@host:5432/database
# For local SQLite (development): sqlite:///./productivity.db
# For PostgreSQL: postgresql://user:password@localhost:5432/database
# On Cloud Run the working directory is read-only; use /tmp for SQLite.
# In production set DATABASE_URL to a real PostgreSQL/AlloyDB connection string.
_default_sqlite = "sqlite:////tmp/productivity.db"
DB_URL = os.getenv("DATABASE_URL", _default_sqlite)

# Create engine with appropriate settings
if "sqlite" in DB_URL:
    # SQLite configuration (for local development)
    engine = create_engine(
        DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
else:
    # PostgreSQL/AlloyDB configuration (for production)
    engine = create_engine(
        DB_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

logger.info(f"Database configured at: {DB_URL}")


# ============================================================================
# DATABASE MODELS
# ============================================================================

class Task(Base):
    """Task model for storing user tasks"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(32), unique=True, index=True)
    title = Column(String(255), index=True)
    description = Column(Text, nullable=True)
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    status = Column(String(20), default="open")  # open, in_progress, completed, cancelled
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    subtasks = Column(Integer, default=0)
    dependencies = Column(Text, nullable=True)  # JSON string of task IDs
    assigned_to = Column(String(255), nullable=True)
    custom_data = Column(Text, nullable=True)  # JSON for additional fields


class Note(Base):
    """Note model for storing user notes and knowledge base"""
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(String(32), unique=True, index=True)
    title = Column(String(255), index=True)
    content = Column(Text)
    category = Column(String(100), nullable=True, index=True)
    tags = Column(Text, nullable=True)  # Comma-separated or JSON
    is_pinned = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255), nullable=True)
    custom_data = Column(Text, nullable=True)  # JSON for additional fields


class CalendarEvent(Base):
    """Calendar Event model for storing scheduled events and meetings"""
    __tablename__ = "calendar_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(32), unique=True, index=True)
    title = Column(String(255), index=True)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime, index=True)
    location = Column(String(255), nullable=True)
    duration_minutes = Column(Integer, default=60)
    status = Column(String(20), default="scheduled")  # scheduled, in_progress, completed, cancelled
    attendees = Column(Text, nullable=True)  # JSON array of attendees
    organizer = Column(String(255), nullable=True)
    is_all_day = Column(Boolean, default=False)
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String(255), nullable=True)
    color = Column(String(10), nullable=True)  # For calendar display
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255), nullable=True)
    custom_data = Column(Text, nullable=True)  # JSON for additional fields


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """Initialize database - create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise


def get_db_session():
    """Get database session for dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# CRUD OPERATIONS - TASKS
# ============================================================================

def create_task_in_db(task_id: str, title: str, description: str = None, 
                     priority: str = "medium", due_date: datetime = None, 
                     subtasks: int = 0, dependencies: str = None):
    """Create a new task in the database"""
    db = SessionLocal()
    try:
        task = Task(
            task_id=task_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            subtasks=subtasks,
            dependencies=dependencies
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        logger.info(f"✅ Task created: {task_id}")
        return task
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creating task: {e}")
        raise
    finally:
        db.close()


def get_all_tasks(limit: int = 100, offset: int = 0, status: str = None):
    """Retrieve all tasks with optional filtering"""
    db = SessionLocal()
    try:
        query = db.query(Task)
        if status:
            query = query.filter(Task.status == status)
        tasks = query.order_by(Task.created_at.desc()).limit(limit).offset(offset).all()
        return tasks
    finally:
        db.close()


def get_task_by_id(task_id: str):
    """Retrieve a specific task by ID"""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.task_id == task_id).first()
        return task
    finally:
        db.close()


def update_task(task_id: str, **kwargs):
    """Update task fields"""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.task_id == task_id).first()
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            task.updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"✅ Task updated: {task_id}")
            return task
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error updating task: {e}")
        raise
    finally:
        db.close()


# ============================================================================
# CRUD OPERATIONS - NOTES
# ============================================================================

def create_note_in_db(note_id: str, title: str, content: str, 
                     category: str = None, tags: str = None):
    """Create a new note in the database"""
    db = SessionLocal()
    try:
        note = Note(
            note_id=note_id,
            title=title,
            content=content,
            category=category,
            tags=tags
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        logger.info(f"✅ Note created: {note_id}")
        return note
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creating note: {e}")
        raise
    finally:
        db.close()


def get_all_notes(limit: int = 100, offset: int = 0, category: str = None):
    """Retrieve all notes with optional filtering"""
    db = SessionLocal()
    try:
        query = db.query(Note).filter(Note.is_archived == False)
        if category:
            query = query.filter(Note.category == category)
        notes = query.order_by(Note.created_at.desc()).limit(limit).offset(offset).all()
        return notes
    finally:
        db.close()


def search_notes(search_query: str, limit: int = 50):
    """Search notes by title or content"""
    db = SessionLocal()
    try:
        notes = db.query(Note).filter(
            (Note.title.ilike(f"%{search_query}%") | 
             Note.content.ilike(f"%{search_query}%")) &
            (Note.is_archived == False)
        ).limit(limit).all()
        return notes
    finally:
        db.close()


def get_note_by_id(note_id: str):
    """Retrieve a specific note by ID"""
    db = SessionLocal()
    try:
        note = db.query(Note).filter(Note.note_id == note_id).first()
        return note
    finally:
        db.close()


def update_note(note_id: str, **kwargs):
    """Update note fields"""
    db = SessionLocal()
    try:
        note = db.query(Note).filter(Note.note_id == note_id).first()
        if note:
            for key, value in kwargs.items():
                if hasattr(note, key):
                    setattr(note, key, value)
            note.updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"✅ Note updated: {note_id}")
            return note
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error updating note: {e}")
        raise
    finally:
        db.close()


# ============================================================================
# CRUD OPERATIONS - CALENDAR EVENTS
# ============================================================================

def create_event_in_db(event_id: str, title: str, start_time: datetime, 
                      end_time: datetime, location: str = None, 
                      duration_minutes: int = 60, attendees: str = None,
                      description: str = None):
    """Create a new calendar event in the database"""
    db = SessionLocal()
    try:
        event = CalendarEvent(
            event_id=event_id,
            title=title,
            start_time=start_time,
            end_time=end_time,
            location=location,
            duration_minutes=duration_minutes,
            attendees=attendees,
            description=description
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        logger.info(f"✅ Calendar event created: {event_id}")
        return event
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creating calendar event: {e}")
        raise
    finally:
        db.close()


def get_all_events(limit: int = 100, offset: int = 0, upcoming_only: bool = False):
    """Retrieve all calendar events with optional filtering"""
    db = SessionLocal()
    try:
        query = db.query(CalendarEvent)
        if upcoming_only:
            query = query.filter(CalendarEvent.start_time >= datetime.utcnow())
        events = query.order_by(CalendarEvent.start_time.asc()).limit(limit).offset(offset).all()
        return events
    finally:
        db.close()


def get_event_by_id(event_id: str):
    """Retrieve a specific calendar event by ID"""
    db = SessionLocal()
    try:
        event = db.query(CalendarEvent).filter(CalendarEvent.event_id == event_id).first()
        return event
    finally:
        db.close()


def get_upcoming_events(days_ahead: int = 7):
    """Get upcoming events for the next N days"""
    db = SessionLocal()
    try:
        from datetime import timedelta
        now = datetime.utcnow()
        future = now + timedelta(days=days_ahead)
        events = db.query(CalendarEvent).filter(
            (CalendarEvent.start_time >= now) &
            (CalendarEvent.start_time <= future)
        ).order_by(CalendarEvent.start_time.asc()).all()
        return events
    finally:
        db.close()


def update_event(event_id: str, **kwargs):
    """Update calendar event fields"""
    db = SessionLocal()
    try:
        event = db.query(CalendarEvent).filter(CalendarEvent.event_id == event_id).first()
        if event:
            for key, value in kwargs.items():
                if hasattr(event, key):
                    setattr(event, key, value)
            event.updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"✅ Calendar event updated: {event_id}")
            return event
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error updating calendar event: {e}")
        raise
    finally:
        db.close()
