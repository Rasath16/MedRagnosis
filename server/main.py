import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError 
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

# 3. Add Validation Exception Handler 
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error = exc.errors()[0] 
    field = error.get("loc")[-1]
    msg = error.get("msg")
    clean_message = f"Validation Error ({field}): {msg}"
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": clean_message},
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