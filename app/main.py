from fastapi import FastAPI
from .ingestion import router as ingestion_router
from .metrics import router as metrics_router
from .funnel import router as funnel_router
from .health import router as health_router
from .anomalies import router as anomalies_router
from .database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Store Intelligence API")

app.include_router(ingestion_router)
app.include_router(metrics_router)
app.include_router(funnel_router)
app.include_router(health_router)
app.include_router(anomalies_router)

@app.get("/")
def root():
    return {"message": "Store Intelligence API Running"}
