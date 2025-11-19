import os
import shutil
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_optional_current_user
from app.crud.session import session_crud
from app.models.user import User
from app.config import settings

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/session/{session_id}", status_code=status.HTTP_201_CREATED)
async def upload_session_file(
    session_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """
    Upload a file for a specific session.
    """
    # Verify session exists
    session = session_crud.get(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Check ownership/access
    # If session has a user_id, current_user must match
    if session.user_id:
        if not current_user or session.user_id != current_user.id:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to upload to this session"
            )
    
    # Create session-specific directory
    session_upload_dir = os.path.join(UPLOAD_DIR, str(session_id))
    os.makedirs(session_upload_dir, exist_ok=True)

    # Generate safe filename
    # In a real app, we might want to uuid the filename to prevent collisions/overwrites
    # For now, we'll keep original name but maybe prepend timestamp if needed
    # or just overwrite if same name is uploaded
    file_path = os.path.join(session_upload_dir, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )
    finally:
        file.file.close()

    # Return the relative path or URL
    # Assuming we mount 'uploads' at /uploads
    file_url = f"/uploads/{session_id}/{file.filename}"
    
    return {"filename": file.filename, "url": file_url}
