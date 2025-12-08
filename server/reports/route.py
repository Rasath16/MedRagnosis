from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from ..auth.route import get_current_user 
from .vectorstore import load_vectorstore
import uuid
import os
from pathlib import Path
from typing import List
from ..config.db import reports_collection

router = APIRouter(prefix="/reports", tags=["reports"])

# Configuration (Must match vectorstore.py)
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploaded_reports")

@router.post("/upload")
async def upload_reports(
    user=Depends(get_current_user),
    files: List[UploadFile] = File(...)
):
    if user["role"] != "patient":
        raise HTTPException(status_code=403, detail="Only patients can upload reports")
    
    doc_id = str(uuid.uuid4())
    await load_vectorstore(files, uploaded=user["username"], doc_id=doc_id)
    return {"message": "Uploaded and indexed", "doc_id": doc_id}

@router.get("/view/{doc_id}")
async def view_report(
    doc_id: str,
    user=Depends(get_current_user)
):
    """
    Allows Doctors to download/view the original report for verification.
    """
    # 1. Find report metadata
    report = reports_collection.find_one({"doc_id": doc_id})
    if not report:
        raise HTTPException(status_code=404, detail="Report metadata not found")

    # 2. Access Control: Only Doctors or the Uploader can view
    if user["role"] != "doctor" and user["username"] != report["uploader"]:
        raise HTTPException(status_code=403, detail="Unauthorized to view this report")

    # 3. Construct File Path
    # Note: File naming convention must match vectorstore.py: {doc_id}_{filename}
    filename = report["filename"]
    file_path = Path(UPLOAD_DIR) / f"{doc_id}_{filename}"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on server")

    # 4. Return File
    return FileResponse(
        path=file_path, 
        filename=filename, 
        media_type='application/pdf'
    )