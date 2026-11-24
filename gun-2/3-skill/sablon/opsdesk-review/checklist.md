# OpsDesk inceleme kontrol listesi

Kaynak: `AGENTS.md`, `CLAUDE.md`, `docs/OPS-101.md`.

| # | Kural | Diff'te ihlal nasıl anlaşılır |
|---|---|---|
| 1 | Filtreleme ve sıralama SQL sorgusunda yapılır | Sorgu sonucu Python'da süzülüyor ya da sıralanıyor: liste üreteci, `for` ile eleme, `sorted` |
| 2 | Liste endpoint'leri id sırasıyla (artan) döner | `order_by` kaldırılmış ya da `desc()` ile ters çevrilmiş |
| 3 | Girdi doğrulaması tipli modellerle yapılır; geçersiz değer standart 422 gövdesiyle döner | Parametre `str` gibi serbest bir tipe çevrilmiş, doğrulama elle `if` ile yapılmış, `HTTPException(422, ...)` ile özel gövde dönüyor |
| 4 | Testler gevşetilmez ya da silinmez | `tests/` altında silinen test, zayıflatılan `assert`, eklenen `skip` ya da `xfail`; `tests/test_ops101.py` içinde herhangi bir değişiklik |
| 5 | Mevcut endpoint'lerin yanıt yapısı ve durum kodları korunur | Mevcut bir `response_model`, alan adı, durum kodu ya da hata gövdesi değişmiş |
