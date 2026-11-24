# Proje 1 — OPS-108: Olay durumunu güncelleme

## Görev

Olayların durumu bugün yalnızca veritabanına elle yazılarak değişiyor. `PATCH /incidents/{incident_id}` ile durum değiştirilebilsin. İzin verilmeyen geçişler reddedilsin, her değişiklik log tablosuna kaydedilsin.

Bilet: [OPS-108.md](OPS-108.md). Bilette bir soru açık; kararı sen vereceksin.

## Kullandığın konular

| Konu | Bu projede |
|---|---|
| 7. Plan modu | Bileti plan modunda planlatır, açık soruyu planda kapatırsın |
| 8. Oturum | Oturuma ad verir, kararı konuşmada değil dosyada tutarsın |
| 2. Kural dosyaları | Test kuralın yeni test dosyasıyla birlikte yüklenir |
| 4. Hook | "Testler geçmeden bitirme" kuralını bir `Stop` hook'una bağlarsın |
| 3. Skill | Değişikliği `/opsdesk-review` ile incelersin |
| 5. Subagent | `reviewer`'dan her kabul kriterinin kanıtını istersin |
| 6. MCP | Yazılan durum kaydını gerçek veride MCP ile görürsün |
| 1. Talimat dosyaları | `AGENTS.md`'yi işin sonuna göre güncellersin |

## Hazırlık

**Neden:** İş tanımları `docs/` altında durur (`AGENTS.md`). Agent bileti oradan okur, sen de kararı oraya yazarsın.

```bash
cp gun-2/9-projeler/1-durum-guncelleme/OPS-108.md docs/
pytest -q
```

**Görmen gereken:** `pytest -q` yeşil.

## Adımlar

### 1. Oturuma ad ver, planlat (konu 7, 8)

**Neden:** Yanlış anlaşılmayı yakalamanın en ucuz yeri, kod yazılmadan önceki plandır. Oturuma ad verirsen ara verdiğinde ya da terminal kapandığında bu işe kolayca dönersin.

`/rename ops-108` yaz. Plan moduna geç ve agent'tan `docs/OPS-108.md`'yi okuyup bir uygulama planı çıkarmasını iste: dokunulacak dosyalar, geçiş kurallarının nerede duracağı, yeni testler ve riskler.

**Görmen gereken:** Agent dosyaları okuyor ama değiştirmiyor. Biletteki açık soruyu ya kendisi soruyor ya da sen soruyorsun.

### 2. Planı sorgula, açık soruya karar ver

**Neden:** Açık soruyu agent'a bırakırsan, ekibin vermesi gereken bir karar fark edilmeden koda girer. Konuşmada verilen bir karar da compact sırasında kaybolabilir; biletteki karar kalır ve testler ona göre yazılır.

Planı onaylamadan önce en az şunları sor:

- "Gövdede `status` dışında bir alan gelirse ne oluyor? Bunu hangi satır reddediyor?"
- "Başarısız bir istekte log kaydı yazılmadığını hangi test gösterecek?"
- "Mevcut testlere ya da `tests/conftest.py`'ye dokunuyor musun?"

Açık soruya karar ver: olay zaten istenen durumdaysa yanıt ne olsun, log yazılsın mı? Kararı `docs/OPS-108.md`'deki tabloya yazdır.

**Görmen gereken:** Tabloda "Açık" yerine senin kararın. Plan bu karara göre güncellendi.

### 3. Önce testler (konu 2, 7)

**Neden:** Önce kırmızı görülmeyen bir test, özelliği gerçekten sınadığını kanıtlamaz. Kod yazılmadan da geçiyorsa hiçbir şeyi ölçmüyordur.

Planı onayla, ama agent'a önce yalnızca testleri yazdır: `tests/test_ops108.py`. Her kabul kriteri ve senin kararın için en az bir test olsun. Testleri çalıştır.

**Görmen gereken:**

- Testler kalıyor; endpoint henüz yok.
- `git diff tests/test_api.py tests/test_ops101.py tests/conftest.py` boş.
- Agent'a sorduğunda, `tests/` altında çalıştığı için `.claude/rules/testler.md`'nin bağlamında olduğunu söylüyor.

### 4. "Bitti"yi garantiye bağla (konu 4)

**Neden:** "Testler geçmeden bitti deme" bir kuraldır; agent ona uymayabilir. Hook ise agent ne derse desin çalışır. Kodun testlerden sonra değişip değişmediğine bakmak, yalnızca test yazılırken agent'ın durabilmesini sağlar; `stop_hook_active` kontrolü sonsuz döngüyü önler.

`.claude/hooks/stop_tests.py` adında bir `Stop` hook'u yazdır ve `settings.json`'a bağla. Kuralı şu:

- Girdideki `stop_hook_active` alanı `true` ise hemen `exit 0`.
- `app/` altındaki en son değişen `.py` dosyası, `tests/` altındakinden daha yeni değilse `exit 0`: kod en son testlerden önce değişmiş, yani test yazılıyor.
- Daha yeniyse `pytest -q` çalıştır. Testler kalırsa son satırları `stderr`'e yaz ve `exit 2`.

Hook'u agent olmadan sına:

```bash
echo '{"stop_hook_active": false}' | python .claude/hooks/stop_tests.py; echo $?
touch app/main.py
echo '{"stop_hook_active": false}' | python .claude/hooks/stop_tests.py; echo $?
touch tests/test_ops108.py
```

**Görmen gereken:** İlk çağrıda `0`: en son testler değişti. `touch app/main.py` kodu daha yeni gösterir; ikinci çağrıda `2` ve kalan testlerin listesi. Son satır testleri yeniden en yeni yapar.

### 5. Uygula (konu 7)

**Neden:** Plan onaylandı, testler hazır; her düzenlemeyi tek tek onaylamak artık yalnızca işi yavaşlatır. `accept edits` düzenlemeleri sorulmadan yaptırır, hook ise bitirmeden önce testlerin geçmesini sağlar.

`Shift+Tab` ile `accept edits` moduna geç ve özelliği yazdır.

**Görmen gereken:** `pytest -q` tamamen yeşil. Agent testler kırmızıyken bitirmeye çalıştıysa hook onu durdurdu ve agent devam etti; bunu ekranda gördün.

### 6. İncelet (konu 3, 5, 8)

**Neden:** Agent'ın kendi yazdığı koda "tamam" demesi kanıt değildir. Kontrol listesi bilinen hata türlerini, ayrı bağlamdaki `reviewer` ise yazanın kaçırdığını yakalar. Uzamış bir bağlam incelemenin kalitesini düşürür; önce ölç.

Önce `/context` ile bağlamın doluluğuna bak. Yarıyı geçtiyse odaklı bir compact yap: `/compact OPS-108 kararlarını ve test listesini koru`.

Sonra iki inceleme yaptır:

1. `/opsdesk-review` ile diff'i kontrol listesine göre.
2. `reviewer` subagent'ıyla bilete göre. Brief'te bileti ve diff'i ver. Her kabul kriteri için onu kanıtlayan testi `dosya:satır` olarak, tablo hâlinde istesin.

Kanıtı olmayan bir kriter ya da kapanmamış bir bulgu varsa düzelttir. İncelemeden genel bir kural çıktıysa onu kontrol listesine madde olarak ekle; örneğin "başarısız istek yan etki bırakmaz".

**Görmen gereken:** Kanıtsız kriter kalmadı; iki incelemenin bulguları kapandı.

### 7. Gerçek veride doğrula (konu 6)

**Neden:** Testler kendi küçük veritabanlarında çalışır. Kaydın gerçek veritabanına yazıldığını başka bir yoldan görmek ayrı bir kanıttır.

Uygulamayı demo veritabanıyla başlat:

```bash
uvicorn app.main:app --port 8000
```

Başka bir terminalde bir olayın durumunu değiştir ve log listesine bak:

```bash
curl -s -X PATCH localhost:8000/incidents/1044 -H 'Content-Type: application/json' -d '{"status": "investigating"}'
curl -s localhost:8000/logs | python -m json.tool | tail -12
```

Yeni kaydı `GET /logs` çıktısında ara. Bulamazsan nedenini `app/main.py`'deki `list_logs` fonksiyonunda bul. Sonra Claude Code'da MCP ile bak: olay 1044'ün zaman çizelgesini iste.

**Görmen gereken:** `GET /logs` yeni kaydı göstermiyor. MCP aracı gösteriyor: `Incident 1044 status open -> investigating`.

İşin bitince olayı aynı `curl` komutuyla `"open"` durumuna geri al ve uygulamayı `Ctrl+C` ile durdur.

### 8. Ortak talimatı güncelle (konu 1)

**Neden:** `AGENTS.md`'nin "Durum" bölümü güncel kalmazsa, bir sonraki oturumda agent OPS-108'in yapılmadığını sanır; konu 1'deki eskimiş talimat sorunu yeniden başlar.

`AGENTS.md`'nin "Durum" bölümüne OPS-108'i ekle. İşten kalıcı bir kural çıktıysa "Kurallar" bölümüne yaz; örneğin durum geçişlerinin tek bir tabloda tanımlandığı. Test sayısı gibi kolay eskiyen bilgi yazma.

## Bitti mi?

- [ ] Açık sorunun kararı `docs/OPS-108.md`'de yazılı ve bir testle sabit.
- [ ] `tests/test_ops108.py` her kabul kriterini kapsıyor; önce kırmızı, sonra yeşil gördün.
- [ ] `Stop` hook'u kod değişip testler kalırken `2` veriyor; elle sınadın.
- [ ] `/opsdesk-review` ve `reviewer` bulguları kapandı.
- [ ] Durum kaydını gerçek veride MCP ile gördün.
- [ ] `pytest -q` yeşil, mevcut test dosyaları değişmedi, `AGENTS.md` güncel.
