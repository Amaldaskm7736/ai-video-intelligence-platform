from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db, Incident
from schemas import IncidentCreate, IncidentResponse
from typing import List, Optional

router = APIRouter(tags=["incidents"])

# Get all incidents with optional filters
@router.get("/", response_model=List[IncidentResponse])
def get_incidents(
    db: Session = Depends(get_db),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    object_class: Optional[str] = None,
    zone_name: Optional[str] = None,
    camera_id: Optional[int] = None
):
    query = db.query(Incident).order_by(desc(Incident.timestamp))

    if object_class:
        query = query.filter(Incident.object_class == object_class)
    if zone_name:
        query = query.filter(Incident.zone_name == zone_name)
    if camera_id:
        query = query.filter(Incident.camera_id == camera_id)

    return query.offset(offset).limit(limit).all()

# Get single incident
@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

# Create incident (called internally by AI processor)
@router.post("/", response_model=IncidentResponse)
def create_incident(incident: IncidentCreate, db: Session = Depends(get_db)):
    db_incident = Incident(**incident.dict())
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident

# Get incident statistics
@router.get("/stats/summary")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Incident).count()
    by_class = db.query(
        Incident.object_class,
        db.query(Incident).filter(
            Incident.object_class == Incident.object_class
        ).count()
    ).distinct().all()

    return {
        "total_incidents": total,
        "by_class": {row[0]: db.query(Incident).filter(
            Incident.object_class == row[0]).count()
            for row in by_class}
    }