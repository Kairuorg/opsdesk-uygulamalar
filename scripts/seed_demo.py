"""Yeni bir yerel SQLite veritabanını sentetik, hassas olmayan kayıtlarla doldurur."""
from sqlalchemy import select
from app.database import Base, SessionLocal, engine
from app.models import ApplicationLog, Incident, Task


def main():
    Base.metadata.create_all(engine)
    with SessionLocal.begin() as db:
        if db.scalar(select(Incident.id).limit(1)) is not None:
            print("Demo verisi zaten var; kayit eklenmedi.")  # çıktıda Türkçe karakter yok: konsol kodlaması hata vermesin
            return
        db.add_all([
            Incident(id=1042, title="Payment API timeout (synthetic)", severity="critical", status="open"),
            Incident(id=1043, title="Notification queue backlog (synthetic)", severity="high", status="investigating"),
            Incident(id=1044, title="Dashboard icon alignment (synthetic)", severity="low", status="open"),
            Incident(id=1045, title="Metrics refresh lag (synthetic)", severity="medium", status="resolved"),
            Task(id=101, title="Add incident severity filter", description="See docs/OPS-101.md", priority="high"),
            ApplicationLog(service="payment-api", level="ERROR", message="Synthetic timeout after 3000 ms", correlation_id="demo-req-101", incident_id=1042),
            ApplicationLog(service="notification-worker", level="WARN", message="Synthetic queue lag 120 s", correlation_id="demo-req-102", incident_id=1043),
        ])
    print("Seed tamamlandi: 4 olay, 1 gorev, 2 log.")


if __name__ == "__main__":
    main()
