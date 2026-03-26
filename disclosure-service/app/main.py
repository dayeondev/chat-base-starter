from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.routers import companies, disclosures
from app.database import engine, Base
from app.middleware import RequestIdMiddleware
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Disclosure Service API",
    description="Company and Disclosure Information Service",
    version="1.0.0"
)

# Add Request ID middleware (should be first)
app.add_middleware(RequestIdMiddleware)

# CORS handled by Gateway - no CORS middleware needed here

# Routers
app.include_router(companies.router, prefix="/api/companies", tags=["companies"])
app.include_router(disclosures.router, prefix="/api/disclosures", tags=["disclosures"])

# Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/")
def root():
    return {"service": "disclosure-service", "version": "1.0.0"}
