from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import cameras, incidents, alerts

app = FastAPI(
    title="AI Video Intelligence Platform",
    description="Real-time AI surveillance and monitoring system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers without prefix so paths match exactly
app.include_router(cameras.router, prefix="/cameras", tags=["cameras"])
app.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
app.include_router(alerts.router)

@app.on_event("startup")
def startup_event():
    init_db()
    print("Database initialized!")
    print("AI Video Intelligence Platform running!")

@app.get("/")
def root():
    return {
        "message": "AI Video Intelligence Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}