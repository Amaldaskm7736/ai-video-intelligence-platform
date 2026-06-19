from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Camera schemas
class CameraBase(BaseModel):
    name: str
    stream_url: str
    location: str

class CameraCreate(CameraBase):
    pass

class CameraResponse(CameraBase):
    id: int
    active: int
    created_at: datetime

    class Config:
        from_attributes = True

# Incident schemas
class IncidentBase(BaseModel):
    camera_id: int
    object_class: str
    object_id: int
    zone_name: str
    confidence: float
    bbox: Optional[List[int]] = None

class IncidentCreate(IncidentBase):
    pass

class IncidentResponse(IncidentBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# Alert schema (for WebSocket messages)
class AlertMessage(BaseModel):
    type: str = "alert"
    object_id: int
    object_class: str
    zone_name: str
    confidence: float
    timestamp: str
    camera_id: int = 1