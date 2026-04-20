from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from .ingestion import router as ingestion_router
from .metrics import router as metrics_router
from .funnel import router as funnel_router
from .health import router as health_router
from .anomalies import router as anomalies_router
from .heatmap import router as heatmap_router
from .database import engine, Base
from .middleware import structured_logging_middleware
from .logger import logger

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Store Intelligence API")

# Register Middleware
@app.middleware("http")
async def add_logging(request: Request, call_next):
    return await structured_logging_middleware(request, call_next)

# Global 503 Handler (Production Readiness)
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=503,
        content={"error": "Service Temporarily Unavailable", "detail": "Database connection issue"}
    )

app.include_router(ingestion_router)
app.include_router(metrics_router)
app.include_router(funnel_router)
app.include_router(health_router)
app.include_router(anomalies_router)
app.include_router(heatmap_router)

@app.get("/")
def root():
    return {"message": "Store Intelligence API Running"}
