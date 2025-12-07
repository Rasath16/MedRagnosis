from fastapi import APIRouter, Depends, HTTPException
from ..auth.route import get_current_user 
from .query import chat_diagnosis_report
from ..config.db import reports_collection, diagnosis_collection
from ..models.db_models import ChatRequest
import time
from pydantic import BaseModel

router = APIRouter(prefix="/diagnosis", tags=["diagnosis"])

@router.post("/chat")
async def chat_diagnose(
    req: ChatRequest,
    user=Depends(get_current_user)
):
    """
    Conversational Endpoint.
    Expects JSON body: { "doc_id": "...", "messages": [{"role": "user", "content": "..."}] }
    """
    report = reports_collection.find_one({"doc_id": req.doc_id})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if user["role"] == "patient" and report["uploader"] != user["username"]:
        raise HTTPException(status_code=406, detail="You cannot access another user's report")
    
    if user["role"] == "patient":
        # Call the new chat logic
        res = await chat_diagnosis_report(user["username"], req.doc_id, req.messages)
        
        # Determine the latest question for logging
        latest_q = req.messages[-1].content if req.messages else "Unknown"

        # Persist this interaction
        diagnosis_collection.insert_one({
            "doc_id": req.doc_id,
            "requester": user["username"],
            "question": latest_q, 
            "answer": res.get("diagnosis"),
            "sources": res.get("sources", []),
            "timestamp": time.time(),
            "type": "chat"
        })
        return res
    
    if user["role"] in ("doctor", "admin"):
        raise HTTPException(status_code=407, detail="Doctors cannot access for diagnosis with this endpoint")
    
    raise HTTPException(status_code=408, detail="Unauthorized action")

@router.get("/by_patient_name")
async def get_patient_diagnosis(patient_name: str, user=Depends(get_current_user)):
    if user["role"] != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can access this endpoint")
        
    diagnosis_records = diagnosis_collection.find({"requester": patient_name})
    if not diagnosis_records:
        raise HTTPException(status_code=404, detail="No diagnosis found for this patient")
        
    # Convert cursor to a list of dictionaries, excluding the internal _id field
    records_list = []
    for record in diagnosis_records:
        record["_id"] = str(record["_id"]) 
        records_list.append(record)
        
    return records_list

class VerificationRequest(BaseModel):
    record_id: str
    status: str
    note: str

@router.post("/verify")
def verify_diagnosis(req: VerificationRequest, user=Depends(get_current_user)):
    if user["role"] != "doctor":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    from bson.objectid import ObjectId
    
    result = diagnosis_collection.update_one(
        {"_id": ObjectId(req.record_id)},
        {"$set": {
            "verified_by": user["username"],
            "verification_status": req.status,
            "doctor_note": req.note
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")
        
    return {"message": "Diagnosis updated successfully"}