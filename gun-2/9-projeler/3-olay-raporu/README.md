# Proje 3 — Olay 1043: kök neden raporu

## Görev

Olay 1043 (bildirim kuyruğu birikmesi) hâlâ `investigating` durumunda. Kök nedenini bul ve kanıta dayalı bir olay raporu yaz: `raporlar/OLAY-1043.md`.

Raporu agent yazacak. Senin işin iki şey: agent'ın kanıtsız bir şey yazamayacağı bir düzen kurmak ve sonucu kendin doğrulamak.

## Kullandığın konular

| Konu | Bu projede |
|---|---|
| 6. MCP | İncelemeyi yalnızca `opsdesk` araçlarıyla yaparsın |
| 7. Plan modu | İncelemeyi plan modunda yürütürsün; bunun için araçların salt okunur işaretli olması gerekir |
| 2. Kural dosyaları | Rapor yazım kuralı yalnızca `raporlar/` altında çalışırken yüklenir |
| 4. Hook | Rapordaki her log kanıtının veritabanında gerçekten var olduğunu denetleyen bir hook |
| 5. Subagent | Log taramasını yalnızca MCP araçlarına erişen bir subagent yapar |
| 3. Skill | İnceleme yöntemini `olay-raporu` skill'ine yazarsın |
| 8. Oturum | Kanıtları koruyarak compact edersin |
| 1. Talimat dosyaları | `AGENTS.md`'ye raporların yerini ve yöntemini yazarsın |

## Raporun kabul kriterleri

1. Dosya `raporlar/OLAY-1043.md`. Başlıklar bu sırayla: `## Özet`, `## Zaman çizelgesi`, `## Kök neden`, `## Kanıt`, `## Elenen ihtimaller`, `## Açık sorular`.
2. Her iddianın yanında en az bir log kanıtı var, `log#<id>` biçiminde. Raporda en az 5 farklı log geçiyor ve hepsi veritabanında gerçekten var.
3. Zaman çizelgesi olayın açılışına göre yazılmış: `T+<dakika>`. 1043'e bağlı her belirti çizelgede. Açıklanamayan bir belirti varsa "Açık sorular"da.
4. İnceleme 1043'e bağlı kayıtlarla sınırlı kalmamış; başka servislerdeki ve başka olaylardaki kayıtlar da taranmış.
5. Gözlem ile çıkarım ayrı: çıkarım içeren her cümle "Çıkarım:" ile başlıyor.
6. En az iki ihtimal kanıtla elenmiş.

## Hazırlık

**Neden:** Raporun kanıtları bu log kayıtlarıdır. Veri yüklü değilse inceleme yanlış sonuca varır ve hook kanıtları bulamaz.

```bash
python -m scripts.seed_logs
```

Proje 2'yi yaptıysan bu projeyi onun dalından başlat; `trace_request` aracı işini kolaylaştırır.

**Görmen gereken:** `Log veri seti zaten var; kayit eklenmedi.` Claude Code'da `/mcp` içinde `opsdesk` bağlı.

## Adımlar

### 1. Araçları plan moduna hazırla (konu 6, 7)

**Neden:** İncelemeyi plan modunda yürütmek istiyorsun; orada agent hiçbir dosyayı değiştiremez. Ama plan modu yalnızca salt okunur araçları çalıştırır. Bir MCP aracı salt okunur olduğunu sunucunun ona verdiği işaretle bildirir; işaret yoksa plan modu aracı çalıştırmaz.

Plan moduna geç ve agent'tan `opsdesk` aracıyla olay 1043'ü getirmesini iste.

**Görmen gereken:** Proje 2'yi yapmadıysan çağrı reddediliyor: `Cannot call mcp__opsdesk__get_incident while in plan mode`.

Çağrı reddedildiyse plan modundan çık ve `mcp_server/opsdesk_mcp.py`'deki beş aracı işaretle:

```python
from mcp.types import ToolAnnotations

@mcp.tool(annotations=ToolAnnotations(read_only_hint=True))
```

Claude Code'u yeniden başlat ve aynı isteği plan modunda tekrarla.

**Görmen gereken:** Çağrı çalışıyor; olayın başlığı geliyor.

### 2. Rapor kuralını yaz (konu 2)

**Neden:** Rapor kuralları yalnızca rapor yazılırken gerekir. `CLAUDE.md`'ye yazılsaydı her işte bağlamı doldururdu; `paths:` alanı onları yalnızca `raporlar/` altında yükletir.

`.claude/rules/raporlar.md` dosyasını oluştur. Başında `paths: "raporlar/**"` bloğu olsun; altında en fazla altı satırlık rapor kuralı: kanıt biçimi (`log#<id>`), çıkarımın nasıl işaretleneceği, zaman biçimi, açıklanamayan belirtinin nereye yazılacağı.

**Görmen gereken:** Dosyanın en başında `---` ile açılan `paths:` bloğu.

### 3. Kanıt denetimini hook'a bağla (konu 4)

**Neden:** Agent'ın yazdığı bir log id'si uydurma olabilir ve rapor okuyana doğru görünür. Kural "kanıt göster" der; hook ise her kanıtı veritabanında arar ve bulamadığını agent'a geri gönderir.

`.claude/hooks/check_report.py` adında bir `PostToolUse` hook'u yazdır ve `Edit|Write` için `settings.json`'a bağla. Hook yalnızca `raporlar/` altındaki `.md` dosyalarına bakar ve şunları denetler:

- Altı başlık var ve istenen sırada.
- En az 5 farklı `log#<id>` geçiyor.
- Geçen her id veritabanında var. Veritabanını salt okunur aç: `sqlite3.connect("file:opsdesk.db?mode=ro", uri=True)`.

Sorun varsa sorunları `stderr`'e yazar ve `exit 2` ile çıkar.

Hook'u agent olmadan, içinde uydurma bir id geçen bir deneme raporuyla sına:

```bash
mkdir -p raporlar
printf '## Özet\nDeneme log#32 log#33 log#34 log#35 log#99999\n' > raporlar/deneme.md
echo '{"tool_name":"Write","tool_input":{"file_path":"raporlar/deneme.md"}}' | python .claude/hooks/check_report.py; echo $?
rm raporlar/deneme.md
```

**Görmen gereken:** Çıkış kodu `2`. Mesajda eksik başlıklar ve `log#99999`.

### 4. Log analistini kur (konu 5)

**Neden:** Log taraması uzun çıktı üretir; o çıktı subagent'ta kalır, ana konuşmaya yalnızca kanıt listesi döner. Araç listesi dar olduğu için subagent veritabanını başka bir yoldan okuyamaz.

`.claude/agents/log-analisti.md` adında bir subagent oluştur. `tools` alanında yalnızca `opsdesk` MCP araçları olsun:

```text
mcp__opsdesk__get_incident, mcp__opsdesk__search_logs, mcp__opsdesk__incident_timeline, mcp__opsdesk__error_summary
```

Proje 2'yi yaptıysan `mcp__opsdesk__trace_request` de eklenir. Gövdede çıktı sözleşmesi olsun: her bulgu tek satır (`log#<id> | zaman | servis | seviye | ne gösteriyor`), en fazla 15 satır, tahmin yok.

**Görmen gereken:** `/agents` listesinde `log-analisti`.

### 5. Yöntemi skill'e yaz (konu 3)

**Neden:** İnceleme yöntemi her seferinde prompt'a yazılırsa adımlar atlanır: olaya bağlı olmayan kayıtlar taranmaz, ihtimaller elenmez. Skill yöntemi sabitler ve doğal dilden tetiklenir.

`.claude/skills/olay-raporu/` altında iki dosya oluştur:

- `SKILL.md`: inceleme yöntemi.
- `sablon.md`: raporun altı başlıklı iskeleti. Zaman çizelgesi tablosunun ilk sütunu `T+dk` olsun; biçim böylece kurala bağlı kalmaz.

Açıklama (`description`) skill'in ne zaman tetikleneceğini söylesin: "olayı incele", "kök neden", "postmortem" gibi ifadeler ve bir "kod değişikliği isteklerinde kullanma" sınırı.

Yöntem en az şu adımları içersin:

1. Olayı ve ona bağlı kayıtları al; en erken belirtiyi bul.
2. Olaya bağlı olmayan kayıtları da tara: ilk belirtiden önceki ve belirtilerin sürdüğü zaman aralığını servis filtresi olmadan sorgula. Taramayı `log-analisti`'ne ver.
3. İstek kimlikleri (`correlation_id`) üzerinden başka servislerle ve olaylarla bağ ara.
4. En az iki ihtimali kanıtla ele.
5. Raporu `sablon.md`'ye göre `raporlar/OLAY-<id>.md` olarak yaz.

**Görmen gereken:** `/` yazınca listede `/olay-raporu`.

### 6. İncelet (konu 3, 5, 7)

**Neden:** İnceleme yalnızca okumaktır; plan modunda agent hiçbir dosyayı değiştiremez. Bulguları raporu yazdırmadan önce planda sorgularsın.

Plan modunda doğal dille iste: "Olay 1043'ü incele." Skill'i adıyla çağırma.

**Görmen gereken:** Agent `olay-raporu` skill'ini kendisi seçiyor ve taramayı `log-analisti`'ne veriyor; `Ctrl+O` ile gör. Plan, bir rapor taslağı.

Planı onaylamadan önce sorgula:

- "1043'e bağlı en erken kayıt hangisi? Raporda açıklandı mı?"
- "Hangi cümle gözlem, hangisi çıkarım?"
- "Başka bir olayla bağ kurduysan, bunu hangi iki log gösteriyor?"

### 7. Kanıtları koruyarak compact et (konu 8)

**Neden:** İnceleme uzun araç çıktıları üretir ve bağlamı doldurur. Odaklı bir compact kanıtı tutar, gürültüyü atar; odaksız bir compact kanıt id'lerini kaybettirebilir.

`/compact kanıt log id'lerini ve zaman çizelgesini koru` yaz. Ardından sor: "Elindeki kanıt log id'lerini listele."

**Görmen gereken:** Compact sonrası liste, öncekiyle aynı id'leri içeriyor.

### 8. Raporu yazdır (konu 2, 4)

**Neden:** Yola bağlı kural, eşleşen dosyaya dokunulunca yüklenir. Yeni bir dosyada bu an yazmanın kendisidir; ilk taslak kuralı görmeden yazılır. Bu yüzden yazdıktan sonra gözden geçirtirsin.

Planı onayla; agent raporu yazar ve hook çalışır.

Yazdıktan sonra agent'a sor: `.claude/rules/raporlar.md` bağlamında mı, ne zaman geldi? Ardından raporu bu kurala ve kabul kriterlerine göre gözden geçirt.

**Görmen gereken:**

- Rapor yazıldı. Hook bir eksik bulduysa agent mesajı okuyup raporu düzeltti.
- Kural ilk yazımdan sonra bağlama girdi.
- Gözden geçirmede kurala uymayan yerler düzeltildi; örneğin saat yerine `T+<dakika>`.

### 9. Kendin doğrula

**Neden:** Hook kanıtın var olduğunu denetler, söylediğini değil. Kaydın iddiayı gerçekten desteklediğine sen bakarsın.

Raporun dayandığı en önemli üç kanıtı kendin aç. Id'leri kendi raporundan al:

```bash
python -c "import sqlite3; c = sqlite3.connect('file:opsdesk.db?mode=ro', uri=True); print(*c.execute('SELECT id, timestamp, service, level, message, incident_id FROM application_logs WHERE id IN (<id1>, <id2>, <id3>)'), sep='\n')"
```

**Görmen gereken:** Üç kayıt da raporda onlar için söyleneni gösteriyor.

### 10. Ortak talimatı güncelle (konu 1)

**Neden:** Yöntemin ve raporların yeri `AGENTS.md`'de yazmazsa, bir sonraki inceleme yine sıfırdan başlar.

Kök `AGENTS.md`'ye bir satır ekle: olay raporları `raporlar/` altında durur, yöntem `olay-raporu` skill'indedir.

## Bitti mi?

- [ ] Rapor altı kabul kriterini karşılıyor.
- [ ] Hook uydurma bir log id'sini yakalıyor; elle sınadın.
- [ ] Agent skill'i doğal dilden seçti; tarama `log-analisti`'nde yapıldı.
- [ ] Plan modunda MCP çağrısı çalışıyor.
- [ ] Raporun üç kanıtını kendin doğruladın.
