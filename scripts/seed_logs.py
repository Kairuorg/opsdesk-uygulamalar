"""2. günden itibaren kullanılan sentetik uygulama logu veri setini ekler.

`python -m scripts.seed_demo` komutundan sonra çalıştırılır. Tekrar çalıştırılabilir: veri seti
zaten varsa hiçbir şey yapmaz. Bütün kayıtlar sentetiktir; log mesajları bilerek İngilizcedir.
Zaman damgaları 1042 numaralı olayın açılışına göre hesaplanır; hikâye her kurulumda aynı kalır.
"""
import sys
from datetime import timedelta

from sqlalchemy import select, text

from app.database import SessionLocal
from app.models import ApplicationLog, Incident

MARKER = "cfg-r418"
WAVE_SIZE = 70          # ana dalgadaki timeout hatalarının sayısı
WAVE_STEP_SECONDS = 33


def build_rows(anchor):
    """(timestamp, service, level, message, correlation_id, incident_id) demetlerini döndürür."""
    rows = []

    def add(minutes, service, level, message, correlation_id, incident_id=None):
        rows.append((anchor + timedelta(minutes=minutes), service, level, message, correlation_id, incident_id))

    # Önceki gün: normal trafik. Gateway gecikmesi olağan koşulda birkaç yüz milisaniyedir.
    baseline = [(-1560, 412), (-1500, 655), (-1440, 498), (-1380, 731), (-1200, 920), (-960, 388),
                (-720, 547), (-480, 804), (-300, 463), (-180, 612), (-90, 695), (-45, 529)]
    for index, (minutes, latency) in enumerate(baseline, start=1):
        add(minutes, "payment-api", "INFO", f"Charge authorized in {latency} ms", f"req-6{index:04d}")
    add(-1505, "payment-api", "WARN", "Connection pool usage 85%", "pool-0001")
    add(-1495, "payment-api", "INFO", "Connection pool usage back to 40%", "pool-0001")
    for index in range(1, 11):
        add(-1500 + index * 137, "auth-service", "INFO", "Operator session refreshed", f"sess-{index:04d}")

    # 1042 numaralı olay açıldıktan kısa süre sonra.
    add(4, "payment-api", "INFO", "Charge authorized in 2890 ms", "req-69990")
    add(10, "metrics-collector", "WARN", "Metrics refresh lag 45 s", "met-0001", 1045)
    add(12, "payment-api", "WARN", "Connection pool usage 85%", "pool-0002")
    add(14, "payment-api", "INFO", "Connection pool usage back to 45%", "pool-0002")

    # Başka bir servisin kaydettiği, hiçbir olaya bağlanmamış bir yapılandırma değişikliği.
    add(21, "config-service", "INFO",
        "Applied revision r418 to payment-api: gateway.timeout_ms=300 (was 3000)", MARKER)
    add(22, "payment-api", "INFO", "Configuration reloaded (revision r418)", MARKER)

    # Ana dalga: yeni sınırdan yavaş kalan her ödeme isteği hata verir.
    wave_start = 24
    for index in range(WAVE_SIZE):
        minutes = wave_start + index * WAVE_STEP_SECONDS / 60
        request = f"req-7{index + 1:04d}"
        add(minutes, "payment-api", "ERROR", "Gateway timeout after 300 ms (POST /charge)", request, 1042)
        if index % 12 == 5:
            add(minutes + 0.2, "payment-api", "WARN", f"Retry scheduled for {request} (attempt 2)", request, 1042)
        if index % 9 == 4:
            fast = 240 + (index * 7) % 55
            add(minutes + 0.3, "payment-api", "INFO", f"Charge authorized in {fast} ms", f"req-8{index + 1:04d}")

    # Sonuç: başarısız ödemeler yeniden denenir ve bildirim kuyruğu birikir.
    lag_up = [(27, 180), (30, 260), (34, 340), (38, 430), (42, 520), (46, 610), (50, 700), (55, 790), (60, 860), (64, 900)]
    lag_down = [(70, 720), (76, 510), (82, 290), (88, 110)]
    for index, (minutes, lag) in enumerate(lag_up + lag_down, start=1):
        add(minutes, "notification-worker", "WARN", f"Queue lag {lag} s", f"queue-{index:04d}", 1043)
    for index, request_number in enumerate((12, 23, 34, 45, 56), start=1):
        add(30 + index * 6, "notification-worker", "ERROR",
            f"Dropped notification after 5 retries (req-7{request_number:04d})", f"req-7{request_number:04d}", 1043)
    add(92, "notification-worker", "INFO", "Queue drained", "queue-0015", 1043)

    # Aynı zaman aralığındaki ilgisiz hareketler.
    add(29, "dashboard-web", "INFO", "Deployed build 2026.11.3", "deploy-0441")
    add(31, "dashboard-web", "WARN", "Icon sprite offset mismatch on /dashboard", "deploy-0441", 1044)
    add(33, "dashboard-web", "INFO", "Static assets cache purged", "deploy-0441")
    add(50, "metrics-collector", "INFO", "Refresh interval restored", "met-0002", 1045)

    # Değişiklik geri alınır ve trafik düzelir.
    add(64, "config-service", "INFO",
        "Reverted revision r418 on payment-api: gateway.timeout_ms=3000 (was 300)", "cfg-r419")
    add(65, "payment-api", "INFO", "Configuration reloaded (revision r419)", "cfg-r419")
    recovery = [(66, 644), (69, 512), (73, 780), (77, 455), (81, 903), (85, 587), (89, 431), (93, 668), (97, 720), (101, 549)]
    for index, (minutes, latency) in enumerate(recovery, start=1):
        add(minutes, "payment-api", "INFO", f"Charge authorized in {latency} ms", f"req-9{index:04d}")

    return rows


def main():
    with SessionLocal.begin() as db:
        anchor = db.scalar(select(Incident.created_at).where(Incident.id == 1042))
        if anchor is None:
            print("1042 numarali olay yok. Once `python -m scripts.seed_demo` calistir.")
            return 1
        if db.scalar(select(ApplicationLog.id).where(ApplicationLog.correlation_id == MARKER).limit(1)) is not None:
            print("Log veri seti zaten var; kayit eklenmedi.")
            return 0
        anchor = anchor.replace(tzinfo=None)
        rows = sorted(build_rows(anchor), key=lambda row: row[0])
        db.add_all([
            ApplicationLog(timestamp=ts, service=service, level=level, message=message,
                           correlation_id=correlation_id, incident_id=incident_id)
            for ts, service, level, message, correlation_id, incident_id in rows
        ])
        # Eski bir içe aktarma aracının yazdığı kayıt: saniyenin kesirli kısmı yoktur.
        resolved_at = (anchor + timedelta(minutes=95)).strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            text("INSERT INTO application_logs (timestamp, service, level, message, correlation_id, incident_id) "
                 "VALUES (:ts, 'metrics-collector', 'INFO', 'Incident resolved: metrics refresh lag', 'met-0003', 1045)"),
            {"ts": resolved_at},
        )
        total = len(rows) + 1
    print(f"Log seed tamamlandi: {total} kayit eklendi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
