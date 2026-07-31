from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints.health import router as health_router

app = FastAPI(
    title="Sketch2UI - Team Aarambh",
    version="1.0.0",
    description="Backend AI Engine for converting paper wireframe sketches into code."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    health_router,
    prefix="/api/v1",
    tags=["Health"]
)

@app.get("/", tags=["Root"])
def read_root():
    return {
        "status": "Online",
        "project": "Sketch2UI",
        "team": "Aarambh",
        "message": "Welcome to the Sketch2UI Backend Engine!",
        "members": ["Naina (Leader)", "Shikha", "Shalini"]
    }