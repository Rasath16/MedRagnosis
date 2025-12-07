from fastapi import APIRouter, Depends, HTTPException
from ..auth.route import get_current_user 
from .query import chat_diagnosis_report, longitudinal_analysis # Import longitudinal logic
from ..config.db import reports_collection, diagnosis_collection
from ..models.db_models import ChatRequest, VerificationRequest
import time
from typing import List
from bson.objectid import ObjectId

router = APIRouter(prefix="/diagnosis", tags=["diagnosis"])

# --- 1. Patient Chat Endpoint ---
@router.post("/chat")
async def chat_diagnose(
    req: ChatRequest,
    user=Depends(get_current_user)
):
    """
    Standard Chat with a specific report.
    """
    report = reports_collection.find_one({"doc_id": req.doc_id})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if user["role"] == "patient" and report["uploader"] != user["username"]:
        raise HTTPException(status_code=406, detail="You cannot access another user's report")
    
    if user["role"] == "patient":
        # Call RAG logic
        res = await chat_diagnosis_report(user["username"], req.doc_id, req.messages)
        
        latest_q = req.messages[-1].content if req.messages else "Unknown"

        # Save to DB with 'pending' status
        diagnosis_collection.insert_one({
            "doc_id": req.doc_id,
            "requester": user["username"],
            "question": latest_q, 
            "answer": res.get("diagnosis"),
            "sources": res.get("sources", []),
            "timestamp": time.time(),
            "type": "chat",
            "verification_status": "pending", # Default status
            "doctor_note": None
        })
        return res
    
    raise HTTPException(status_code=403, detail="Unauthorized")

# --- 2. Trends Analysis Endpoint (FIXED) ---
@router.post("/longitudinal")
async def longitudinal_diagnose(
    req: ChatRequest,
    user=Depends(get_current_user)
):
    """
    Analyzes trends across all user reports.
    """
    if user["role"] != "patient":
        raise HTTPException(status_code=403, detail="Only patients can use this feature")

    question = req.messages[-1].content if req.messages else "Analyze trends"

    # Call the existing longitudinal_analysis function
    res = await longitudinal_analysis(user["username"], question)
    
    # Save interaction so doctor can verify it
    diagnosis_collection.insert_one({
        "doc_id": "all-reports",
        "requester": user["username"],
        "question": question, 
        "answer": res.get("diagnosis"),
        "sources": [],
        "timestamp": time.time(),
        "type": "trend",
        "verification_status": "pending"
    })
    
    return res

# --- 3. Doctor: Get Pending Reviews (FIXED) ---
@router.get("/pending")
def get_pending_reviews_endpoint(user=Depends(get_current_user)):
    if user["role"] != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can view pending items")
    
    # Fetch all records where verification_status is 'pending'
    cursor = diagnosis_collection.find({"verification_status": "pending"}).sort("timestamp", -1)
    
    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"]) # Serialize ObjectId
        results.append(doc)
    return results

# --- 4. Doctor: Verify Diagnosis ---
@router.post("/verify")
def verify_diagnosis(req: VerificationRequest, user=Depends(get_current_user)):
    if user["role"] != "doctor":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
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

# --- 5. Patient: Get My History (NEW) ---
@router.get("/my_history")
def get_my_history(user=Depends(get_current_user)):
    """Allows patients to see their past diagnoses and doctor verification status."""
    if user["role"] != "patient":
        raise HTTPException(status_code=403, detail="Only patients can view their own history")
        
    cursor = diagnosis_collection.find({"requester": user["username"]}).sort("timestamp", -1)
    
    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results

# --- 6. Doctor: Search by Patient Name (Existing) ---
@router.get("/by_patient_name")
async def get_patient_diagnosis(patient_name: str, user=Depends(get_current_user)):
    if user["role"] != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can access this endpoint")
        
    diagnosis_records = diagnosis_collection.find({"requester": patient_name})
    records_list = []
    for record in diagnosis_records:
        record["_id"] = str(record["_id"]) 
        records_list.append(record)
        
    return records_list