import logging

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app import models  # noqa: F401
from app.database import Base, engine
from app.middleware import RequestIdMiddleware
from app.routers import chat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Career Chat Service API",
    description="Browser-facing chat relay between gateway and Aegra",
    version="1.0.0",
)

# Add Request ID middleware (should be first)
app.add_middleware(RequestIdMiddleware)

# CORS handled by Gateway - no CORS middleware needed here

# Routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

# Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/")
def root():
    return {"service": "chat-service", "version": "1.0.0"}
