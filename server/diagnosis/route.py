from fastapi import APIRouter, Depends, HTTPException
from ..auth.route import get_current_user 
from .query import chat_diagnosis_report, longitudinal_analysis 
from ..config.db import reports_collection, diagnosis_collection
from ..models.db_models import ChatRequest, VerificationRequest
import time
from typing import List
from bson.objectid import ObjectId

router = APIRouter(prefix="/diagnosis", tags=["diagnosis"])

@router.post("/chat")
async def chat_diagnose(
    req: ChatRequest,
    user=Depends(get_current_user)
):
    report = reports_collection.find_one({"doc_id": req.doc_id})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if user["role"] == "patient" and report["uploader"] != user["username"]:
        raise HTTPException(status_code=406, detail="You cannot access another user's report")
    
    if user["role"] == "patient":
        res = await chat_diagnosis_report(user["username"], req.doc_id, req.messages)
        latest_q = req.messages[-1].content if req.messages else "Unknown"

        diagnosis_collection.insert_one({
            "doc_id": req.doc_id,
            "requester": user["username"],
            "question": latest_q, 
            "answer": res.get("diagnosis"),
            "sources": res.get("sources", []),
            "timestamp": time.time(),
            "type": "chat",
            "verification_status": "pending",
            "doctor_note": None
        })
        return res
    
    raise HTTPException(status_code=403, detail="Unauthorized")

@router.post("/longitudinal")
async def longitudinal_diagnose(
    req: ChatRequest,
    user=Depends(get_current_user)
):
    if user["role"] != "patient":
        raise HTTPException(status_code=403, detail="Only patients can use this feature")

    question = req.messages[-1].content if req.messages else "Analyze trends"
    res = await longitudinal_analysis(user["username"], question)
    
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

@router.get("/pending")
def get_pending_reviews_endpoint(user=Depends(get_current_user)):
    if user["role"] != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can view pending items")
    
    cursor = diagnosis_collection.find({"verification_status": "pending"}).sort("timestamp", -1)
    
    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"]) 
        # Attach Filename for Doctor Context
        if doc.get("doc_id") and doc.get("doc_id") != "all-reports":
            report_meta = reports_collection.find_one({"doc_id": doc["doc_id"]})
            doc["filename"] = report_meta["filename"] if report_meta else "Unknown File"
        else:
             doc["filename"] = "Longitudinal Analysis (All Files)"
             
        results.append(doc)
    return results

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

@router.get("/my_history")
def get_my_history(user=Depends(get_current_user)):
    if user["role"] != "patient":
        raise HTTPException(status_code=403, detail="Only patients can view their own history")
        
    cursor = diagnosis_collection.find({"requester": user["username"]}).sort("timestamp", -1)
    
    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results

@router.get("/by_patient_name")
async def get_patient_diagnosis(patient_name: str, user=Depends(get_current_user)):
    if user["role"] != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can access this endpoint")
        
    diagnosis_records = diagnosis_collection.find({"requester": patient_name})
    records_list = []
    for record in diagnosis_records:
        record["_id"] = str(record["_id"]) 
        
        # Attach Filename
        if record.get("doc_id") and record.get("doc_id") != "all-reports":
            report_meta = reports_collection.find_one({"doc_id": record["doc_id"]})
            record["filename"] = report_meta["filename"] if report_meta else "Unknown File"
        else:
             record["filename"] = "Longitudinal Analysis (All Files)"

        records_list.append(record)
        
    return records_list