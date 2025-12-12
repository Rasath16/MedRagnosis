import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .auth.route import router as auth_router
from .reports.route import router as report_router
from .diagnosis.route import router as diagnosis_router

# 1. Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("MedRagnosis")

app = FastAPI(title="MedRagnosis-RAG-Enhanced Medical Diagnosis Engine")

# 2. Add Global Exception Handler 
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error. Please check server logs."},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 MedRagnosis Server Starting Up...")

app.include_router(auth_router)
app.include_router(report_router)
app.include_router(diagnosis_router)