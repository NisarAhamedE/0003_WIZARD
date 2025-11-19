from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

from app.api.deps import get_db, get_current_admin_user
from app.models.user import User
from app.models.wizard import Wizard
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
    total_users = db.query(func.count(User.id)).scalar()

    # Recent activity (last 7 days)
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    wizards_created_this_week = db.query(func.count(Wizard.id)).filter(
        Wizard.created_at >= week_ago,
        Wizard.is_deleted == False
    ).scalar()

    return {
        "total_wizards": total_wizards,
        "published_wizards": published_wizards,
        "wizards_created_this_week": wizards_created_this_week,
        "total_users": total_users
    }


@router.get("/wizards/performance")
def get_wizard_performance(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get wizard statistics."""
    wizards = db.query(Wizard).filter(Wizard.is_deleted == False).all()

    performance_data = []
    for wizard in wizards:
        performance_data.append({
            "wizard_id": str(wizard.id),
            "wizard_name": wizard.name,
            "is_published": wizard.is_published,
            "created_at": wizard.created_at.isoformat()
        })

    # Sort by created_at
    performance_data.sort(key=lambda x: x["created_at"], reverse=True)
    return performance_data[:limit]
