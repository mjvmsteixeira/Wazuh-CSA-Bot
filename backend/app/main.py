"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agents, sca, analysis, reports
from app.config import settings
from app.utils.logger import logger

# Create FastAPI app
app = FastAPI(
    title="Wazuh SCA AI Analyst API",
    description="API for analyzing Wazuh SCA checks using AI",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents.router, prefix="/api")
app.include_router(sca.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(reports.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Wazuh SCA AI Analyst API",
        "version": "2.0.0",
        "docs": "/api/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting Wazuh SCA AI Analyst API")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"vLLM API: {settings.vllm_api_url}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down Wazuh SCA AI Analyst API")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.app_port,
        reload=settings.app_env == "development",
    )
