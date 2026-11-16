"""Veritabanı oturum fabrikası. Varsayılan yerel SQLite eğitim içindir, production için değildir."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


def build_engine(url: str | None = None):
    target = url or os.getenv("OPSDESK_DATABASE_URL", "sqlite:///./opsdesk.db")
    opts = {"connect_args": {"check_same_thread": False}} if target.startswith("sqlite") else {}
    if target == "sqlite://":
        opts["poolclass"] = StaticPool
    return create_engine(target, **opts)


engine = build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    with SessionLocal() as session:
        yield session
