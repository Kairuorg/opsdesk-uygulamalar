"""Açık API sözleşmeleri; ORM alanlarını gelişigüzel dışarı açma."""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Severity = Literal["critical", "high", "medium", "low"]
TaskStatus = Literal["todo", "in_progress", "done"]
IncidentStatus = Literal["open", "investigating", "resolved"]


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str = ""
    status: TaskStatus = "todo"
    priority: Severity = "medium"
    assignee: str | None = None


class TaskRead(TaskCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class IncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    severity: Severity
    status: IncidentStatus = "open"


class IncidentRead(IncidentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class LogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    timestamp: datetime
    service: str
    level: str
    message: str
    correlation_id: str
    incident_id: int | None
