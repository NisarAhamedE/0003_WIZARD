import os
import shutil
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_optional_current_user
from app.crud.wizard_run import wizard_run_crud
from app.models.user import User
from app.config import settings

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/run/{run_id}", status_code=status.HTTP_201_CREATED)
async def upload_run_file(
    run_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """
    Upload a file for a specific wizard run.
    """
    # Verify run exists
    run = wizard_run_crud.get(db, run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard run not found"
        )

    # Check ownership/access
    # If run has a user_id, current_user must match
    if run.user_id:
        if not current_user or run.user_id != current_user.id:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to upload to this run"
            )

    # Create run-specific directory
    run_upload_dir = os.path.join(UPLOAD_DIR, str(run_id))
    os.makedirs(run_upload_dir, exist_ok=True)

    # Generate safe filename
    # In a real app, we might want to uuid the filename to prevent collisions/overwrites
    # For now, we'll keep original name but maybe prepend timestamp if needed
    # or just overwrite if same name is uploaded
    file_path = os.path.join(run_upload_dir, file.filename)

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
    file_url = f"/uploads/{run_id}/{file.filename}"

    return {"filename": file.filename, "url": file_url}
