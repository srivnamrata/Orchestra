from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from backend.database import get_session, MetricRecord

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/")
def get_analytics(db: Session = Depends(get_session)):
    """Fetch dashboard analytics data (generates mock data if none exists)."""
    # Check if we have data
    count = db.query(MetricRecord).count()
    
    if count == 0:
        # Generate and insert mock analytics data
        now = datetime.utcnow()
        metrics = []
        
        # 1. Tasks Completed (last 12 weeks)
        for i in range(12):
            date = now - timedelta(weeks=11-i)
            # Upward trend roughly
            val = int(10 + i * 2 + random.randint(-5, 5))
            metrics.append(MetricRecord(metric_name="tasks_completed", value=max(5, val), timestamp=date, category="weekly"))
            
        # 2. Safety Score (last 30 days)
        for i in range(30):
            date = now - timedelta(days=29-i)
            # Staying around 95-100
            val = round(random.uniform(92.0, 100.0), 1)
            metrics.append(MetricRecord(metric_name="safety_score", value=val, timestamp=date, category="daily"))
            
        # 3. Time Saved (last 12 months)
        for i in range(12):
            date = now - timedelta(days=30 * (11-i))
            val = round(10 + i * 1.5 + random.uniform(-2, 3), 1)
            metrics.append(MetricRecord(metric_name="time_saved", value=max(5.0, val), timestamp=date, category="monthly"))
            
        db.add_all(metrics)
        db.commit()
    
    # Fetch and format data for charts
    tasks_data = db.query(MetricRecord).filter(MetricRecord.metric_name == "tasks_completed").order_by(MetricRecord.timestamp).all()
    safety_data = db.query(MetricRecord).filter(MetricRecord.metric_name == "safety_score").order_by(MetricRecord.timestamp).all()
    time_data = db.query(MetricRecord).filter(MetricRecord.metric_name == "time_saved").order_by(MetricRecord.timestamp).all()
    
    return {
        "tasks": {
            "labels": [m.timestamp.strftime("Week %U") for m in tasks_data],
            "data": [m.value for m in tasks_data]
        },
        "safety": {
            "labels": [m.timestamp.strftime("%b %d") for m in safety_data],
            "data": [m.value for m in safety_data]
        },
        "time": {
            "labels": [m.timestamp.strftime("%b %Y") for m in time_data],
            "data": [m.value for m in time_data]
        }
    }
