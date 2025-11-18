from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID

from app.api.deps import get_db, get_current_admin_user
from app.models.user import User
from app.models.wizard import Wizard
from app.models.session import UserSession
from app.models.analytics import AnalyticsEvent

router = APIRouter()


@router.get("/dashboard")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get overall dashboard statistics."""
    # Total counts
    total_wizards = db.query(func.count(Wizard.id)).filter(Wizard.is_deleted == False).scalar()
    published_wizards = db.query(func.count(Wizard.id)).filter(
        Wizard.is_deleted == False,
        Wizard.is_published == True
    ).scalar()
    total_sessions = db.query(func.count(UserSession.id)).scalar()
    completed_sessions = db.query(func.count(UserSession.id)).filter(
        UserSession.status == "completed"
    ).scalar()
    total_users = db.query(func.count(User.id)).scalar()

    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    sessions_this_week = db.query(func.count(UserSession.id)).filter(
        UserSession.started_at >= week_ago
    ).scalar()

    # Completion rate
    completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0

    # Average session time for completed sessions
    avg_time = db.query(func.avg(UserSession.total_time_seconds)).filter(
        UserSession.status == "completed",
        UserSession.total_time_seconds.isnot(None)
    ).scalar()

    return {
        "total_wizards": total_wizards,
        "published_wizards": published_wizards,
        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
        "sessions_this_week": sessions_this_week,
        "completion_rate": round(completion_rate, 2),
        "average_session_time": int(avg_time) if avg_time else 0,
        "total_users": total_users
    }


@router.get("/wizards/performance")
def get_wizard_performance(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get performance metrics for each wizard."""
    wizards = db.query(Wizard).filter(Wizard.is_deleted == False).all()

    performance_data = []
    for wizard in wizards:
        sessions = db.query(UserSession).filter(UserSession.wizard_id == wizard.id).all()
        total = len(sessions)
        completed = sum(1 for s in sessions if s.status == "completed")
        abandoned = sum(1 for s in sessions if s.status == "abandoned")

        avg_time = 0
        if completed > 0:
            completed_sessions = [s for s in sessions if s.status == "completed" and s.total_time_seconds]
            if completed_sessions:
                avg_time = sum(s.total_time_seconds for s in completed_sessions) / len(completed_sessions)

        performance_data.append({
            "wizard_id": str(wizard.id),
            "wizard_name": wizard.name,
            "total_sessions": total,
            "completed_sessions": completed,
            "abandoned_sessions": abandoned,
            "completion_rate": round((completed / total * 100) if total > 0 else 0, 2),
            "average_time_seconds": int(avg_time)
        })

    # Sort by total sessions
    performance_data.sort(key=lambda x: x["total_sessions"], reverse=True)
    return performance_data[:limit]


@router.get("/sessions/timeline")
def get_sessions_timeline(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get session counts over time."""
    start_date = datetime.utcnow() - timedelta(days=days)

    sessions = db.query(
        func.date(UserSession.started_at).label('date'),
        func.count(UserSession.id).label('count'),
        func.sum(func.case((UserSession.status == "completed", 1), else_=0)).label('completed')
    ).filter(
        UserSession.started_at >= start_date
    ).group_by(
        func.date(UserSession.started_at)
    ).order_by(
        func.date(UserSession.started_at)
    ).all()

    return [
        {
            "date": str(session.date),
            "total": session.count,
            "completed": int(session.completed)
        }
        for session in sessions
    ]


@router.get("/sessions/recent")
def get_recent_sessions(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get most recent sessions."""
    sessions = db.query(UserSession).order_by(
        desc(UserSession.started_at)
    ).limit(limit).all()

    result = []
    for session in sessions:
        wizard = db.query(Wizard).filter(Wizard.id == session.wizard_id).first()
        user = db.query(User).filter(User.id == session.user_id).first() if session.user_id else None

        result.append({
            "id": str(session.id),
            "wizard_name": wizard.name if wizard else "Unknown",
            "user_name": user.username if user else "Anonymous",
            "status": session.status,
            "progress": float(session.progress_percentage),
            "started_at": session.started_at.isoformat()
        })

    return result
