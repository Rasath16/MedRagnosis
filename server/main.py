from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .auth.route import router as auth_router
from .reports.route import router as report_router
from .diagnosis.route import  router as diagnosis_router



app=FastAPI(title="MedRagnosis-RAG-Enhanced Medical Diagnosis Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(auth_router)
app.include_router(report_router)
app.include_router(diagnosis_router)