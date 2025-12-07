from pydantic import BaseModel, Field
from typing import Optional, List
import time

class UserOut(BaseModel):
    username: str
    role: str

class ReportMeta(BaseModel):
    doc_id: str
    filename: str
    uploader: str
    uploaded_at: float
    num_chunks: int

class DiagnosisRecord(BaseModel):
    doc_id: str
    requester: str
    question: str
    answer: str
    sources: Optional[List] = []
    timestamp: float = Field(default_factory=lambda: time.time())
    
    verified_by: Optional[str] = None 
    verification_status: str = "pending"  
    doctor_note: Optional[str] = None

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    doc_id: str
    messages: List[ChatMessage]

# --- ADDED THIS CLASS ---
class VerificationRequest(BaseModel):
    record_id: str
    status: str
    note: str