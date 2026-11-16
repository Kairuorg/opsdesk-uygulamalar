"""Testler yalıtılmış, bellek içi bir SQLite veritabanı kullanır; demo veritabanına asla dokunmaz."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import ApplicationLog, Incident, Task


@pytest.fixture()
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add_all([
            Incident(id=1042, title="Critical timeout", severity="critical", status="open"),
            Incident(id=1043, title="Queue backlog", severity="high", status="open"),
            Incident(id=1044, title="Minor visual bug", severity="low", status="resolved"),
            Task(id=101, title="Test task", description="", status="todo", priority="medium"),
            ApplicationLog(service="demo-api", level="ERROR", message="Synthetic error", correlation_id="test-001"),
        ])
        db.commit()

    def override_db():
        with Session(engine) as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
