import httpx
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from database import Incident

# This service connects the AI processor to the FastAPI backend
# It saves incidents to DB and broadcasts alerts via WebSocket

BACKEND_URL = "http://localhost:8000"

async def process_alert(alert: dict, db: Session = None):
    """Called when AI detects an intrusion"""
    
    # 1. Save incident to database
    if db:
        incident = Incident(
            camera_id=alert.get("camera_id", 1),
            object_class=alert.get("class"),
            object_id=alert.get("object_id"),
            zone_name=alert.get("zone"),
            confidence=alert.get("confidence", 0.0),
            bbox=alert.get("bbox")
        )
        db.add(incident)
        db.commit()

    # 2. Broadcast alert to all connected WebSocket clients
    alert_message = {
        "type": "alert",
        "object_id": alert.get("object_id"),
        "object_class": alert.get("class"),
        "zone_name": alert.get("zone"),
        "confidence": alert.get("confidence", 0.0),
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "camera_id": alert.get("camera_id", 1)
    }

    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{BACKEND_URL}/alerts/trigger",
                json=alert_message,
                timeout=2.0
            )
    except Exception as e:
        print(f"Could not broadcast alert: {e}")

def process_alert_sync(alert: dict, db: Session = None):
    """Synchronous wrapper for use in non-async contexts"""
    asyncio.run(process_alert(alert, db))