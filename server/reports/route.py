from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from ..auth.route import get_current_user 
from .vectorstore import load_vectorstore
import uuid
from typing import List
from ..config.db import reports_collection

router = APIRouter(prefix="/reports", tags=["reports"])

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