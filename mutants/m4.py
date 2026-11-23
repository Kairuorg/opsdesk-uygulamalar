"""OpsDesk eğitim API'si."""
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import ApplicationLog, Incident, Task
from app.schemas import IncidentCreate, IncidentRead, LogRead, TaskCreate, TaskRead


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="OpsDesk Training API", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks", response_model=list[TaskRead])
def list_tasks(db: Session = Depends(get_db)):
    return db.scalars(select(Task).order_by(Task.id)).all()


@app.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    item = Task(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


VALID_SEVERITIES = ("critical", "high", "medium", "low")


@app.get("/incidents", response_model=list[IncidentRead])
def list_incidents(severity: str | None = None, db: Session = Depends(get_db)):
    if severity is not None and severity not in VALID_SEVERITIES:
        raise HTTPException(status_code=422, detail="Invalid severity")
    stmt = select(Incident).order_by(Incident.id)
    if severity is not None:
        stmt = stmt.where(Incident.severity == severity)
    return db.scalars(stmt).all()


@app.get("/incidents/{incident_id}", response_model=IncidentRead)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@app.post("/incidents", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    item = Incident(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/logs", response_model=list[LogRead])
def list_logs(db: Session = Depends(get_db)):
    # Yerel demo endpoint'i; 2. gündeki MCP server salt okunur bir log sorgusunu sarmalayabilir.
    return db.scalars(select(ApplicationLog).order_by(ApplicationLog.id).limit(100)).all()
