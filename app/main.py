from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1. Initialize FastAPI Application
app = FastAPI(
    title="Sketch2UI - Team Aarambh",
    version="1.0.0",
    description="Backend AI Engine for converting paper wireframe sketches into code."
)

# 2. Configure CORS Middleware (Allows future Next.js frontend to communicate safely)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all connections during local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Root Welcome Endpoint
@app.get("/", tags=["Root"])
def read_root():
    return {
        "status": "Online",
        "project": "Sketch2UI",
        "team": "Aarambh",
        "message": "Welcome to the Sketch2UI Backend Engine!",
        "members": ["Naina (Leader)", "Shikha", "Shalini"]
    }