from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from app.models.session import UserSession, SessionResponse
from app.schemas.session import SessionCreate, SessionUpdate, SessionResponseCreate


class SessionCRUD:
    def get(self, db: Session, session_id: UUID) -> Optional[UserSession]:
        """Get session by ID with responses"""
        return db.query(UserSession).options(
            joinedload(UserSession.responses)
        ).filter(UserSession.id == session_id).first()

    def get_by_user(
        self,
        db: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[UserSession]:
        """Get user's sessions"""
        query = db.query(UserSession).filter(UserSession.user_id == user_id)

        if status:
            query = query.filter(UserSession.status == status)

        return query.order_by(UserSession.last_activity_at.desc()).offset(skip).limit(limit).all()

    def get_by_wizard(
        self,
        db: Session,
        wizard_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserSession]:
        """Get sessions for a wizard"""
        return db.query(UserSession).filter(
            UserSession.wizard_id == wizard_id
        ).order_by(UserSession.created_at.desc()).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: SessionCreate, user_id: Optional[UUID] = None) -> UserSession:
        """Create new session"""
        db_session = UserSession(
            wizard_id=obj_in.wizard_id,
            user_id=user_id,
            session_name=obj_in.session_name,
            metadata=obj_in.metadata,
            browser_info=obj_in.browser_info,
            status="in_progress"
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session

    def update(self, db: Session, db_obj: UserSession, obj_in: SessionUpdate) -> UserSession:
        """Update session"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field in update_data:
            setattr(db_obj, field, update_data[field])

        db_obj.last_activity_at = datetime.utcnow()
        db_obj.updated_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def add_response(
        self,
        db: Session,
        session: UserSession,
        response_in: SessionResponseCreate
    ) -> SessionResponse:
        """Add or update a response in the session"""
        # Check if response already exists
        existing = db.query(SessionResponse).filter(
            SessionResponse.session_id == session.id,
            SessionResponse.option_set_id == response_in.option_set_id
        ).first()

        if existing:
            # Update existing response
            existing.response_data = response_in.response_data
            existing.time_spent_seconds = response_in.time_spent_seconds
            existing.answered_at = datetime.utcnow()
            existing.updated_at = datetime.utcnow()
            db.add(existing)
            db_response = existing
        else:
            # Create new response
            db_response = SessionResponse(
                session_id=session.id,
                step_id=response_in.step_id,
                option_set_id=response_in.option_set_id,
                response_data=response_in.response_data,
                time_spent_seconds=response_in.time_spent_seconds
            )
            db.add(db_response)

        # Update session last activity
        session.last_activity_at = datetime.utcnow()
        db.add(session)

        db.commit()
        db.refresh(db_response)
        return db_response

    def complete_session(self, db: Session, session: UserSession) -> UserSession:
        """Mark session as completed"""
        session.status = "completed"
        session.completed_at = datetime.utcnow()

        # Calculate total time
        if session.started_at:
            total_time = (session.completed_at - session.started_at).total_seconds()
            session.total_time_seconds = int(total_time)

        # Calculate final progress
        session.progress_percentage = Decimal("100.00")

        session.updated_at = datetime.utcnow()
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def abandon_session(self, db: Session, session: UserSession) -> UserSession:
        """Mark session as abandoned"""
        session.status = "abandoned"
        session.updated_at = datetime.utcnow()
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def delete(self, db: Session, session: UserSession) -> None:
        """Physically delete session and all associated responses"""
        # Delete all responses first (due to foreign key constraints)
        db.query(SessionResponse).filter(SessionResponse.session_id == session.id).delete()
        # Delete the session
        db.delete(session)
        db.commit()

    def update_progress(self, db: Session, session: UserSession, progress: Decimal) -> UserSession:
        """Update session progress percentage"""
        session.progress_percentage = progress
        session.last_activity_at = datetime.utcnow()
        session.updated_at = datetime.utcnow()
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def count_by_user(self, db: Session, user_id: UUID, status: Optional[str] = None) -> int:
        """Count user's sessions"""
        query = db.query(UserSession).filter(UserSession.user_id == user_id)
        if status:
            query = query.filter(UserSession.status == status)
        return query.count()

    def count_by_wizard(self, db: Session, wizard_id: UUID) -> int:
        """Count wizard's sessions"""
        return db.query(UserSession).filter(UserSession.wizard_id == wizard_id).count()


session_crud = SessionCRUD()
