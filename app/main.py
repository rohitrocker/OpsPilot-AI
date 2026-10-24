
"""Main entry point for the OpsPilot AI API."""

from fastapi import FastAPI

from app.api.incidents import router as incidents_router


app = FastAPI(
    title="OpsPilot AI",
    description=(
        "An AI-powered incident diagnosis system "
        "for analyzing unusual system log records."
    ),
    version="0.1.0",
)

# Register incident-related endpoints.
app.include_router(incidents_router)


@app.get("/", tags=["General"])
def root() -> dict[str, str]:
    """Provide basic information about the API."""
    return {
        "application": "OpsPilot AI",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Check whether the API process is responding."""
    return {
        "status": "ok",
        "service": "opspilot-api",
    }
