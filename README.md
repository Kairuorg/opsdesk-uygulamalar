# OpsDesk — Claude Code × Codex eğitim reposu

Antalya Havalimanı'nın dört günlük eğitimi için hazırlanmış **sentetik** bir görev ve olay yönetimi API'si. Gerçek havalimanı sistemi, gerçek Jira verisi ya da müşteri ağına erişim kullanılmaz.

## Ön koşullar
- Python 3.12 ya da üstü
- macOS, Linux ya da Windows; bağımlılıkları kurmak için internet erişimi (ya da önceden hazırlanmış wheel önbelleği)

## Kurulum
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m scripts.seed_demo
uvicorn app.main:app --reload
```

- `source .venv/bin/activate`: Windows PowerShell'de `.venv\Scripts\Activate.ps1`

API dokümantasyonu: http://127.0.0.1:8000/docs

Dene:
```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/incidents
curl 'http://127.0.0.1:8000/incidents?severity=critical'
```

**Öğretim notu:** OPS-101 uygulanana kadar son istek olayları *filtrelemeden* döndürür. Bu bilinçli bir tercihtir.

## Testler
```bash
pytest -q -m 'not ops101'
pytest -q -m ops101
pytest -q
```

- `pytest -q -m 'not ops101'`: başlangıç baseline'ı, GEÇMELİ
- `pytest -q -m ops101`: başlangıçta kabul testleri, KALMASI beklenir (4 test)
- `pytest -q`: OPS-101 uygulandıktan sonra hepsi GEÇMELİ

Kabul testleri xfail olarak **işaretlenmemiştir**; böylece katılımcılar kırmızıdan yeşile gerçek bir TDD döngüsü görür. Bu yüzden başlangıç reposunda `pytest -q`, uygulama tamamlanana kadar başarısız olur. Görev için `docs/OPS-101.md` dosyasını oku.

## Repo yapısı
- `app/`: FastAPI endpoint'leri, modeller, şemalar, veritabanı
- `scripts/seed_demo.py`: sentetik örnek veriyi yükler; tekrar çalıştırılınca kayıt eklemez
- `tests/test_api.py`: mevcut davranışı koruyan baseline testleri
- `tests/test_ops101.py`: başlangıçta bilerek kalan OPS-101 kabul testleri
- `docs/OPS-101.md`: user story ve kabul kriterleri
- `uygulamalar/`: dört günün öğleden sonra uygulamaları
- `CLAUDE.md`: Claude Code'a özel proje kuralları
- `AGENTS.md`: agent'lar için ortak yönergeler

## Bilinçli sınırlamalar
Kimlik doğrulama, RBAC, sayfalama, ağ yalıtımı, production migration'ları ve yayına alma sıkılaştırması yoktur. Production servisi olarak yayına alınmamalıdır. Kimlik doğrulama ve güvenli veri işleme ayrıca anlatılır; bu başlangıç API'si yalnızca yerel eğitim içindir.

## Sonraki günler
Eğitim dört gündür ve bu depo gün gün büyür: her günün başlangıç dosyaları o gün `main` dalına eklenir. 2–4. günlerin malzemeleri (MCP logları, kod inceleme skill'i, hook'lar, legacy modül, prompt injection senaryoları, iki agent'lı PR incelemesi) günü geldiğinde gelir. Düzenin tamamı `uygulamalar/README.md` dosyasındadır.
