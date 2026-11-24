# Proje 2 — `trace_request`: isteğin izini süren MCP aracı

## Görev

Bir isteğin servisler arasındaki izini görmek için bugün logları elle aramak gerekiyor; `search_logs` aracında istek kimliği (`correlation_id`) filtresi yok. OpsDesk MCP sunucusuna, bir istek kimliğinin bütün kayıtlarını tek çağrıda getiren salt okunur bir araç ekle.

Aynı işte sunucudaki bütün araçları salt okunur olarak işaretle. İşaretsiz bir MCP aracını plan modu çalıştırmaz.

## Kullandığın konular

| Konu | Bu projede |
|---|---|
| 1. Talimat dosyaları | Kök `AGENTS.md`'ye sunucu kurallarının yerini gösteren bir satır |
| 2. Kural dosyaları | `mcp_server/` klasörüne özel talimat; yalnızca o klasörde çalışırken yüklenir |
| 4. Hook | Sunucuya veritabanına yazan kod girmesini engelleyen bir `PreToolUse` hook'u |
| 7. Plan modu | Sözleşmeyi plan modunda planlatırsın; işaretli araçlar plan modunda çalışır |
| 8. Oturum | Planı dosyaya yazdırıp temiz bir bağlamla uygulatırsın |
| 5. Subagent | `reviewer` aracı tasarım kurallarına göre inceler |
| 3. Skill | `opsdesk-review` kontrol listesine MCP araçları için bir madde |
| 6. MCP | Aracı ekler, sunucuya yeniden bağlanır ve kullanırsın |

## Araç sözleşmesi

**Ad:** `trace_request`

**Parametreler**

| Ad | Tip | Kural |
|---|---|---|
| `correlation_id` | metin | Zorunlu, 1–80 karakter. Tam eşleşme; joker karakter yok. |
| `limit` | tamsayı | 1–50, varsayılan 50. Sınır parametre şemasında da tanımlı. |

**Dönen değer** (sözlük)

| Alan | Anlamı |
|---|---|
| `correlation_id` | Aranan kimlik; baştaki ve sondaki boşluklar atılmış |
| `total_matches` | Eşleşen bütün kayıtların sayısı |
| `returned` | Dönen kayıt sayısı |
| `truncated` | `total_matches` dönen kayıt sayısından büyükse `true` |
| `services` | Eşleşen **bütün** kayıtlardaki servisler: alfabetik, tekrarsız |
| `incident_ids` | Eşleşen **bütün** kayıtlardaki olay id'leri: artan, tekrarsız, boş olanlar hariç |
| `records` | Kayıtlar, **en eski önce**. Her kayıtta `id`, `timestamp`, `service`, `level`, `message`, `incident_id` |
| `hint` | Yalnızca eşleşme yoksa: kimliğin `search_logs` çıktısındaki `correlation_id` alanından aynen kopyalanması gerektiğini söyleyen kısa bir cümle |

**Kurallar**

- Veritabanına yalnızca mevcut `_query` yardımcısıyla eriş; o bağlantı salt okunurdur. SQL parametreli olsun; kimlik SQL metnine eklenmesin.
- Kimlik boşsa ya da yalnızca boşluktan oluşuyorsa `ValueError` fırlat. Mesajda doğru bir örnek kimlik geçsin: `req-70012` gibi.
- Araç salt okunur olarak işaretlenir: `annotations=ToolAnnotations(read_only_hint=True)`. Sunucudaki diğer beş araç da aynı işareti alır.
- Mevcut araçların davranışı değişmez.
- Hata ve ipucu metinleri Türkçe karaktersiz yazılır.

**Örnek:** `trace_request("deploy-0441")` üç kayıt döndürür. Hepsi `dashboard-web` servisinden; biri olay 1044'e bağlı.

## Hazırlık

**Neden:** Araç eklemeden önce sunucunun bugünkü hâlinin çalıştığını gör. Sonra çıkan bir sorunun yeni araçtan geldiğini bilirsin.

```bash
pytest -q
```

Claude Code'da `/mcp` yaz.

**Görmen gereken:** `pytest -q` yeşil; `opsdesk` bağlı ve 5 aracı var.

## Adımlar

### 1. Sunucunun kurallarını klasörüne koy (konu 1, 2)

**Neden:** Bu kurallar yalnızca sunucu üzerinde çalışırken gerekir; kök dosyaya yazılsaydı her işte bağlamı doldururdu. Claude Code klasördeki `CLAUDE.md`'yi o klasördeki bir dosyaya dokununca yükler. Codex ise klasördeki `AGENTS.md`'yi yalnızca o klasörde başlatılırsa okur; kökteki yönlendirme satırı bu yüzden var.

`mcp_server/AGENTS.md` dosyasını oluştur: bu sunucuya araç eklerken uyulacak en fazla 10 satırlık kural. Kaynağın yukarıdaki sözleşme. Yanına tek satırlık bir `mcp_server/CLAUDE.md` koy: `@AGENTS.md`.

Kök `AGENTS.md`'ye bir yönlendirme satırı ekle: "MCP sunucusunda çalışırken `mcp_server/AGENTS.md`'yi oku."

**Görmen gereken:** `/clear` sonrası, hiçbir dosya okutmadan sorduğunda sunucu kuralları bağlamda **yok**. `mcp_server/opsdesk_mcp.py` okunduktan sonra **var**.

### 2. Salt okunurluğu garantiye bağla (konu 4)

**Neden:** "Salt okunur kal" bir kuraldır; agent ona uymayabilir ve sunucuya yazan tek bir satır eklerse veritabanı değişir. Hook her düzenlemede çalışır ve bunu engeller.

`.claude/hooks/guard_readonly.py` adında bir `PreToolUse` hook'u yazdır ve `Edit|Write` için `settings.json`'a bağla. Hook yalnızca `mcp_server/` altındaki `.py` dosyalarına bakar ve şu durumlarda `exit 2` ile engeller:

- Yazılan metinde (`Write` için `content`, `Edit` için `new_string`) büyük harfle `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER` ya da `CREATE` kelimesi, `executescript` ya da `.commit(` var.
- Bir `Edit` çağrısı `mode=ro` ifadesini siliyor: `old_string` içinde var, `new_string` içinde yok.

Hook'u agent olmadan, elle bir JSON vererek sına. En az üç durum dene: engellenen bir yazma, geçen bir düzenleme ve `mode=ro` silme.

**Görmen gereken:** Engellenen iki durumda çıkış kodu `2` ve anlaşılır bir mesaj, geçen durumda `0`.

### 3. Planlat (konu 7)

**Neden:** Sözleşmenin en kolay kaçan maddesi kırpmayla ilgili olanı: `services` yalnızca dönen kayıtlardan hesaplanırsa kırpılan kayıtlardaki servisler kaybolur. Bunu planda yakalamak koddan ucuzdur.

Plan moduna geç. Agent'tan bu dosyadaki sözleşmeyi ve sunucunun kodunu okuyup bir uygulama planı çıkarmasını iste: fonksiyonun imzası, sorgular, işaretler, testler ve dokunulmayacak yerler.

Planı onaylamadan önce sorgula. En az şu ikisini sor:

- "`services` ve `incident_ids` kırpılan kayıtları da sayıyor mu?"
- "Testler hangi veritabanını kullanıyor? Demo veritabanına dokunuyor mu?"

**Görmen gereken:** Plan, testler için geçici bir veritabanı kullanıyor. Örnek veriyi `scripts/seed_logs.py` içindeki `build_rows` ile üretebilir. `services` ve `incident_ids` bütün eşleşmelerden hesaplanıyor.

### 4. Planı dosyaya yaz, temiz bağlamla başla (konu 8)

**Neden:** Keşif konuşması bağlamda yer kaplar ve uygulamada dikkati dağıtır. Plan dosyada durursa uygulama temiz ve odaklı bir bağlamla başlar.

Planı onayla ve agent'a önce yalnızca planı `docs/PLAN-trace-request.md` dosyasına yazdır. Sonra `/clear` yaz ve yeni konuşmada planı o dosyadan uygulat.

**Görmen gereken:** `/context` yüzdesi `/clear` öncesine göre düşük. Agent planı dosyadan okuyarak başlıyor.

### 5. Önce testler, sonra kod (konu 2, 7)

**Neden:** Önce kırmızı görülmeyen bir test, aracı gerçekten sınadığını kanıtlamaz. Araç yokken de geçiyorsa hiçbir şeyi ölçmüyordur.

Agent'tan önce yalnızca testleri yazmasını iste: `tests/test_mcp_trace.py`, sözleşmenin her maddesi için en az bir test. Testleri çalıştır ve kaldıklarını gör. Sonra aracı yazdır.

**Görmen gereken:** Önce testler kalıyor, araç yazılınca geçiyor. `pytest -q` tamamen yeşil; mevcut test dosyalarında değişiklik yok.

### 6. İncelet (konu 3, 5)

**Neden:** Aracı yazan agent kendi tasarımındaki eksikleri kolay görmez. Ayrı bağlamdaki `reviewer` aracı sözleşmeye karşı inceler; kontrol listesine eklediğin madde bir sonraki MCP aracında da uygulanır.

`reviewer` subagent'ına aracı incelet. Brief'te sözleşmeyi ve `mcp_server/AGENTS.md`'deki kuralları ver. Her sözleşme maddesinin hangi testle kanıtlandığını tablo olarak istesin.

Ardından `opsdesk-review` skill'inin kontrol listesine (`.claude/skills/opsdesk-review/checklist.md`) MCP araçları için bir madde ekle: salt okunur bağlantı, parametreli SQL, satır sınırı, `truncated` alanı, salt okunur işareti.

**Görmen gereken:** Testi olmayan bir sözleşme maddesi kalmadı. Kontrol listesinde 6. madde var.

### 7. Bağlan ve kullan (konu 6, 7)

**Neden:** Yeni araç ancak sunucuya yeniden bağlanınca görünür. İşaretli araçlar plan modunda da çalışır. Bir istek kimliğinin izi, olaya bağlı kayıtların göstermediği bir bağı gösterebilir.

Claude Code'dan çıkıp yeniden aç ya da `/mcp` ekranında sunucuya yeniden bağlan. Plan moduna geç ve şunu iste: olay 1043'e bağlı ERROR kayıtlarından birinin istek kimliğini al ve `trace_request` ile izini sür.

**Görmen gereken:** `/mcp` 6 araç gösteriyor. Plan modunda çağrı reddedilmiyor. Sonuçta `incident_ids` alanına bak: ne görüyorsun?

İzin penceresi çıktı mı? Konu 6'da `mcp__opsdesk` için sunucu düzeyinde izin vermiştin; bu izin sonradan eklenen araçları da kapsar. Yazabilen bir araç eklenseydi o da sorulmadan çalışırdı. Bu izni araç araç vermeye geçip geçmeyeceğine karar ver.

## Bitti mi?

- [ ] `trace_request` sözleşmeye uyuyor; testleri önce kırmızı, sonra yeşil gördün.
- [ ] Altı araç da salt okunur işaretli; plan modunda MCP çağrısı çalışıyor.
- [ ] Hook, yazma SQL'ini ve `mode=ro` silmeyi engelliyor; elle sınadın.
- [ ] `mcp_server/` kuralları yalnızca o klasörde çalışırken yükleniyor.
- [ ] `reviewer`'ın bulguları kapandı; kontrol listesinde MCP maddesi var.
- [ ] `pytest -q` yeşil, mevcut testler değişmedi.
