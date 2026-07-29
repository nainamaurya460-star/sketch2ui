from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import API Routers
from app.api.v1.endpoints.health import router as health_router

# Initialize FastAPI Application
app = FastAPI(
    title="Sketch2UI - Team Aarambh",
    version="1.0.0",
    description="Backend AI Engine for converting hand-drawn paper sketches into React + Tailwind UI."
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(health_router)

# Root Endpoint
@app.get("/", tags=["Root"])
def read_root():
    return {
        "status": "success",
        "project": "Sketch2UI",
        "version": "1.0.0",
        "team": "Aarambh",
        "message": "Sketch2UI Backend is running successfully."
    }
