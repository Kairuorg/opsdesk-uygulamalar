# 1. Gün — Uygulamalar: Agentic coding ve Claude Code

Yardım protokolü ve ortak kurallar: [../README.md](../README.md).

Bu uygulamalar Claude Code'u günlük işinde kullananlar için yazıldı; aracın temel kullanımı anlatılmaz. Bugünün konusu, agent'la yapılan işe ne kadar güvenilebileceğidir: agent'ın bir iddiası, yeşil testler ve "bitti" cümlesi neyi kanıtlar, neyi kanıtlamaz?

Bugün iki uzun uygulama var; her birinden önce eğitmen aynı tekniği başka bir iş üzerinde canlı gösterir. İlkinde küçük bir işi bitirecek, sonra testlerinin kaçırdığı hataları kanıtlayacaksın. İkincisinde elinde yalnızca tek cümlelik bir istek olacak: kabul kriterlerini, testleri ve birden çok dosyaya dokunan değişikliği sen yöneteceksin.

## Günün sırası

1. **Gösterim 1.1** — Yeşil ama yanlış: bir testin kanıtlamadığını kanıtlamak
2. **Uygulama 1.1** — OPS-101: yeşil testler neyi kanıtlamaz?
3. **Gösterim 1.2** — Tek cümlelik istekten kabul kriterlerine ve testlere
4. **Uygulama 1.2** — Belirsiz istekten PR'a: olay atama
5. Kapanış

İki uygulama da planlanandan erken biterse: **Ek Uygulama 1.3** — OPS-102: tek prompt, sıfır müdahale.

## Gösterimler

Her uygulamadan önce eğitmen kısa bir gösterim yapar. Uygulamada kullanacağın teknik, başka bir iş üzerinde Claude Code ile canlı yürütülür.

| Gösterim | Ne gösterilir |
|---|---|
| **1.1** — Yeşil ama yanlış | Mevcut bir testin neyi garanti etmediğini agent'a sordurma; testleri geçen ama yanlış bir uygulama yazdırma; onu yakalayan testin hatalı kodda kırmızı, doğru kodda yeşil olduğunu gösterme; hatalı uygulamayı patch olarak saklama |
| **1.2** — OPS-107: görev silme | Tek cümlelik istekten netleştirme soruları; kararlarla birlikte kabul kriteri dosyası; kriterlerden testler; baştan yeşil testlerin ayıklanması; plan |

Gösterimlerin akışı dosyanın sonundaki [Başvuru](#başvuru) bölümündedir.

## Başlangıç

Depoyu klonla ve kökünde:

```bash
claude --version
python -m pip install -e '.[dev]'
python -m scripts.seed_demo
git switch -c participant/<kimlik>/day1
git status --short
```

- `claude --version`: 2.1 veya üstü
- `git status --short`: boş olmalı

Dalını `main` üzerinden açmış olursun; `main` dalına commit atma.

---

## Uygulama 1.1 — OPS-101: yeşil testler neyi kanıtlamaz?

**Süre:** yaklaşık 60 dakika, öncesinde Gösterim 1.1
**Pekiştirdiği konular:** Repository keşfi ve agent iddialarının doğrulanması, kabul kriteri analizi, testlerle doğrulama ve testlerin yeterliliği, Git diff ve commit.
**Hikâye:** [docs/OPS-101.md](../../docs/OPS-101.md).

### Senaryo

OPS-101 küçük bir iş: olay listesine severity filtresi. Alıştığın yöntemle birkaç dakikada bitirirsin ve beş kabul testi yeşile döner. Bu uygulamanın konusu ondan sonrasıdır: yeşil testler ve agent'ın "bitti" demesi, işin doğru yapıldığını ne kadar kanıtlıyor?

Önce işi bitireceksin. Sonra agent'ın bir iddiasını deneyle sınayacak, bütün testleri geçtiği hâlde yanlış olan uygulamalar yazdıracak ve testlerini bunları yakalayacak hâle getireceksin. Son aşamada eğitmenin elindeki hatalı uygulamalar senin testlerine karşı çalıştırılır ve bir skor alırsın.

### Çıktılar

1. OPS-101 çözümü ve commit'i
2. Deney notu: agent'ın iddiası ve deneyin gösterdiği
3. `tests/test_ops101_extra.py` ve hatalı uygulama tablosu
4. Skor: eğitmenin hatalı uygulamalarından kaçını yakaladın

### Aşama 1 — Hızlı tur: OPS-101'i bitir (10 dk)

```bash
pytest -q -m 'not ops101'
pytest -q -m ops101
```

- `pytest -q -m 'not ops101'`: 7 passed
- `pytest -q -m ops101`: 4 failed, 1 passed

Hikâyeyi kendi yönteminle uygulat. Tek kısıt: `tests/test_ops101.py` değişmez. Bitince commit et. OPS-101'i bu depoda daha önce bitirdiysen o commit'ten devam et.

**Kontrol noktası:** `pytest -q` sonucu 12 passed. Değişiklik yalnızca uygulama kodunda ve commit edildi.

### Aşama 2 — Agent'ın iddiasını deneyle sına (10 dk)

1. Agent'a sor ve cevabını dayandığı `dosya:satır` ile not et:

   ```text
   Bu repoda pytest çalıştırmak yerelde bir veritabanı dosyası oluşturur ya da değiştirir mi?
   ```

2. Cevabı deneyle sına:

   macOS / Linux:

   ```bash
   OPSDESK_DATABASE_URL=sqlite:///./deneme.db pytest -q -m 'not ops101'
   ls deneme.db
   ```

   Windows PowerShell:

   ```powershell
   $env:OPSDESK_DATABASE_URL = "sqlite:///./deneme.db"; pytest -q -m "not ops101"
   Remove-Item Env:OPSDESK_DATABASE_URL; dir deneme.db
   ```

3. Dosya oluştu mu? Agent'ın cevabıyla uyuşuyor mu? Uyuşmuyorsa agent'ı hangi satır yanılttı; uyuşuyorsa doğru cevaba hangi dosyaları okuyarak ulaştı? Bitince `deneme.db` dosyasını sil.

**Kontrol noktası:** Üç satırlık deney notu: agent ne dedi, deney ne gösterdi, fark nereden geliyor. Bu nota ikinci uygulamada döneceksin.

### Aşama 3 — Yeşil ama yanlış (25 dk)

Kabul testleri hikâyenin her kriterini sınamıyor. Bunu söylemek yetmez; kanıtlayacaksın.

1. Hikâyenin yedi kriterini `tests/` altındaki testlerle eşleştir ve testlerin sınamadığı kısımları listele. `CLAUDE.md`'deki kodlama kurallarını da listeye kat.
2. Listendeki en az üç boşluk için agent'a **hatalı** bir uygulama yazdır: bir kriteri ya da proje kuralını çiğnesin, ama 12 testin hepsi yeşil kalsın. Her birinde 12 testin geçtiğini kendi gözünle gör, sonra hatalı uygulamayı sakla ve doğru koda dön:

   ```bash
   pytest -q
   git diff --output=hatali-1.patch app/
   git checkout -- app/
   ```

   - `pytest -q`: hatalı kodda 12 passed

3. Her hatalı uygulama için onu yakalayan bir test yazdır: `tests/test_ops101_extra.py`. Kabul testlerinin dosyasına dokunma. Testin işe yaradığını iki yönde göster:

   ```bash
   pytest -q tests/test_ops101_extra.py
   git apply hatali-1.patch
   pytest -q tests/test_ops101_extra.py
   git checkout -- app/
   ```

   - `pytest -q tests/test_ops101_extra.py`: doğru kodda yeşil
   - `pytest -q tests/test_ops101_extra.py`: hatalı kodda kırmızı

4. Tabloyu doldur:

   | # | Çiğnenen kriter ya da kural | 12 test geçti mi? | Yakalayan test |
   |---|---|---|---|
   | 1 | | | |
   | … | | | |

   API üzerinden yazılan hiçbir testle yakalayamadığın bir hatalı uygulama çıkarsa onu da tabloya yaz ve karar ver: bunu ne yakalar?

**Kontrol noktası:** En az üç hatalı uygulama var; her biri için "12 passed" çıktısını gördün ve onu kırmızıya döndüren bir testin var. Doğru kodda `pytest -q` tamamen yeşil. `git status --short` çıktısında `app/` yok.

### Aşama 4 — Eğitmenin hatalı uygulamaları (10 dk)

Eğitmen bu aşamada bir paket paylaşır. Paketi repo köküne aç: `mutants/` klasörü ve `tests/test_ops101_reference.py` dosyası gelir.

1. Kendi testlerini eğitmenin altı hatalı uygulamasına karşı çalıştır. Altısı da mevcut 12 testi geçer.

   ```bash
   python mutants/run_mutants.py tests/test_ops101_extra.py
   ```

   Script her hatalı uygulamayı sırayla `app/main.py` yerine koyar, testleri çalıştırır ve dosyayı eski hâline döndürür.
2. Kaçan her hatalı uygulamayı kendi kodunla karşılaştır. Neyi çiğniyor? Testlerin neden yakalamadı?

   ```bash
   git diff --no-index app/main.py mutants/m1.py
   ```

3. Kendi uygulamanı eğitmenin testleriyle sına:

   ```bash
   pytest -q tests/test_ops101_reference.py
   ```

**Kontrol noktası:** Skorun yazılı: altı hatalı uygulamadan kaçını yakaladın. Kaçan her biri için bir cümle: neden kaçtı, onu ne yakalardı? Kendi uygulaman referans testlerin beşini de geçiyor ya da geçmeyenin nedenini biliyorsun.

### Aşama 5 — Teslim (5 dk)

1. `tests/test_ops101_extra.py` dosyasını commit et (`test:`). `mutants/` klasörü, patch dosyaları ve referans test dosyası commit'e girmesin.
2. Şu cümleyi tamamla: "Testler yeşilken şunu hâlâ bilmiyordum: …"
3. Sohbete skorunla birlikte ✅ yaz.

### Takılırsan

- **Agent "dokunmaz" dedi ama dosya oluştu.** `app/main.py` içindeki `lifespan` fonksiyonuna ve `TestClient`'ın onu çalıştırıp çalıştırmadığına baktır.
- **Boşluk bulamıyorum.** `tests/conftest.py`'deki fixture verisine bak: her severity'den kaç kayıt var, hangi değer hiç sorgulanmıyor? 422 testi yanıtın gövdesine bakıyor mu? Hikâyenin "Kapsam dışı" listesindeki bir davranışı ekleyen uygulama testleri bozar mı?
- **Agent hatalı uygulama yazmak istemiyor.** Amacını söyle: testlerin yeterliliğini ölçüyorsun ve hatalı kod commit edilmeyecek.
- **Hatalı uygulama testleri bozdu.** O boşluk yokmuş; testler o hatayı zaten yakalıyor. Başka bir boşluk seç.
- **Yazdığım test hatalı uygulamada da yeşil.** Test o hatayı sınamıyor. Hatalı uygulamanın farklı cevap vereceği bir istek seç.
- **Sıralamayı kaldırdım ama sonuç yine id sırasıyla geliyor.** SQLite, sıralama verilmediğinde çoğunlukla ekleme sırasını döndürür. Sıralamayı kaldırtmak yerine açıkça başka bir sıra verdir. Tek kayıtla sıralama sınanabilir mi?
- **`git apply` hata veriyor.** Patch'i aldıktan sonra doğru kodu değiştirdiysen patch artık uymaz. Hatalı uygulamayı yeniden yazdır.
- **`run_mutants.py` başlamıyor.** Yazdığı mesajı oku: OPS-101 çözümün commit edilmiş ve testlerin kendi kodunda yeşil olmalı.
- **Bir hatalı uygulamayı hiçbir API testiyle yakalayamıyorum.** Olabilir: dışarıdan görünen davranışı aynıysa test onu göremez. O hatayı ne yakalar? Kararını yaz.

### Erken bitirenlere

- **İkinci deney.** Agent'a sor: "Veritabanında severity değeri geçersiz bir olay kaydı bulunsaydı `GET /incidents` ne döndürürdü? `GET /incidents?severity=critical` ne döndürürdü?" Cevabı not et, sonra dene: `OPSDESK_DATABASE_URL` ile ayrı bir veritabanı dosyası kullan, içine doğrudan SQL ile böyle bir kayıt ekle, uygulamayı çalıştır ve iki isteği gönder. Sonuç agent'ın cevabıyla uyuşuyor mu? Bu sonuç OPS-101 için ne anlama geliyor?
- **Yakalanamayanı yakala.** API testiyle yakalanamayan hatalı uygulama için başka türde bir kontrol tasarla ve dene.

---

## Uygulama 1.2 — Belirsiz istekten PR'a: olay atama

**Süre:** yaklaşık 60 dakika, öncesinde Gösterim 1.2
**Pekiştirdiği konular:** User story ve kabul kriterlerinin analizi, agent ile plan, birden çok dosyaya dokunan değişikliğin yönetimi, izinler ve insan onayı, testlerle ve çalışan uygulamayla doğrulama, commit iş akışı, PR incelemesi, proje talimatları.

### Senaryo

Operasyon ekibinden tek cümlelik bir istek geldi:

> "Bir olayın kimde olduğunu göremiyoruz. Olayları bir kişiye atayabilmek ve bir kişiye atanmış olayları listeleyebilmek istiyoruz."

Hazır hikâye, hazır kabul kriteri ve hazır test yok. İsteği netleştirecek, kriterleri ve testleri yazdıracak, veri modeline kadar inen bir değişikliği yönetecek ve PR'a hazır bir dal teslim edeceksin. Agent'ın ilk planı ya da ilk "bitti" demesi her zaman doğru olmayacak; kararları sen vereceksin.

Herkesin sonucu karşılaştırılabilsin diye API'nin dış çerçevesi sabittir:

| İş | İstek |
|---|---|
| Atama | `PUT /incidents/{incident_id}/assignee`, gövde `{"assignee": "<ad>"}` |
| Atamayı kaldırma | `DELETE /incidents/{incident_id}/assignee` |
| Kişiye göre listeleme | `GET /incidents?assignee=<ad>` |
| Görünürlük | Olay yanıtlarında `assignee` alanı bulunur; atanmamışsa `null` |

Geri kalan her kural senin kararındır.

### Çıktılar

1. `docs/OPS-106.md`: senin yazdırdığın kabul kriterleri
2. Testleriyle birlikte çalışan özellik
3. En az üç commit ve bir PR açıklaması
4. `CLAUDE.md`'ye eklenmiş bir kural

### Aşama 1 — İstekten kabul kriterlerine (10 dk)

1. Başlangıç noktanı işaretle: `git branch ops106-base`
2. Agent'a isteği ve çerçeveyi ver; çözüm değil, soru al. Her soru için mevcut koddaki benzer davranışa dayanan bir varsayılan (`dosya:satır`) önersin.
3. Soruları cevapla. Karar vermediğin soruda önerilen varsayılanı kabul ettiğini söyle.
4. Kriterleri `docs/OPS-101.md` biçiminde `docs/OPS-106.md` dosyasına yazdır ve commit et (`docs:`).

**Kontrol noktası:** En az sekiz kriter var ve en az üçü hata durumu. Her kriter bir istek ve beklenen yanıt içeriyor. "Mevcut endpoint'ler ve testler bozulmaz" kriteri ile bir "kapsam dışı" listesi var.

### Aşama 2 — Testler ve plan (10 dk)

1. Kriterlerden testleri yazdır: `tests/test_ops106.py`. Uygulama kodu değişmesin.
2. Testleri çalıştır. Hangileri kalıyor? Daha hiçbir şey yazılmadan geçen test var mı; varsa neyi sınıyor?
3. Uygulama planını iste. Her değişiklik için dosya, fonksiyon, gerekçe ve mevcut davranışa riski yazsın.
4. Planı oku: hangi dosyalara dokunuyor, mevcut testleri değiştiriyor mu, kriterlerinde olmayan bir şey ekliyor mu?
5. Testleri commit et (`test:`).

**Kontrol noktası:** Yeni davranışı sınayan testler kırmızı, mevcut 12 test yeşil. Plan dokunacağı dosyaları tek tek sayıyor ve kapsam dışı bir şey içermiyor.

### Aşama 3 — Uygulama (15 dk)

1. Testlerin sana sorulmadan çalışması için bir izin kuralı ekle. Dosya düzenlemelerini okuyarak onayla.
2. Planı uygulat. Agent plan dışına çıkarsa değişikliği geri al ve kısıtı yinele.
3. İşin ortasında context kullanımını bir kez ölç. Yer açman gerekirse kriterlerinin diskte durduğunu unutma.

**Kontrol noktası:** `git diff --stat ops106-base` beklenen dosyaları gösteriyor. `tests/test_api.py` ve `tests/test_ops101.py` değişmedi.

### Aşama 4 — Doğrulama: testler ve çalışan uygulama (10 dk)

1. Testleri çalıştır:

   ```bash
   pytest -q
   ```

2. Şimdi uygulamayı gerçekten çalıştır ve dene:

   ```bash
   uvicorn app.main:app
   curl -i http://127.0.0.1:8000/incidents
   ```

3. Ne gördün? Testler yeşilken bu nasıl oldu? Nedenini agent'a buldur ve 1.1'deki deney notunla karşılaştır.
4. Agent'tan çözüm seçeneklerini iste. Agent bir dosyayı silmek ya da yeni bir araç kurmak isterse izin penceresini dikkatle oku ve kararını ver: bu işlem bu repoda neden kabul edilebilir ya da edilemez? Gerçek bir sistemde aynı kararı verir miydin?
5. Çözümü uygula, uygulamayı yeniden çalıştır, atamayı ve listelemeyi `curl` ile dene.
6. Özelliği commit et (`feat:`).

**Kontrol noktası:** `curl` 200 dönüyor ve yanıtta `assignee` alanı var. Şu cümleyi tamamladın: "Testler bunu yakalamadı, çünkü …"

### Aşama 5 — İnceleme ve PR açıklaması (10 dk)

1. Temiz bir oturumda `git diff ops106-base...HEAD` değişikliğini kendi kriterlerine (`docs/OPS-106.md`) göre incelet. Şunlara ayrıca baktır: mevcut testler değişmiş mi, mevcut endpoint'lerin yanıtı değişmiş mi, kriterlerde olmayan bir şey eklenmiş mi. Bulgular önem, `dosya:satır` ve kanıtla gelsin; inceleyen oturum değişiklik yapmasın.
2. Her bulguyu sınıflandır: geçerli, yanlış alarm, kapsam dışı. Geçerli olanı düzelttir, testleri yeniden çalıştır.
3. PR açıklamasını agent'a yazdır ve kendin düzelt:

   ```markdown
   ## Ne değişti
   ## Neden
   ## Nasıl test edildi (komut ve çıktı)
   ## Bilinen riskler ve sınırlamalar
   ## Kapsam dışı bırakılanlar
   ```

**Kontrol noktası:** `git log --oneline ops106-base..HEAD` en az üç commit gösteriyor. PR açıklamasının "riskler" bölümü Aşama 4'te yaşadığın durumu ve gerçek bir sistemde ne gerekeceğini anlatıyor.

### Aşama 6 — Dersi kurala çevir (5 dk)

1. Bugün öğrendiğin bir dersi `CLAUDE.md`'ye tek satırlık, gözlemlenebilir bir kural olarak ekle. Kuralı sen seç; Aşama 4 iyi bir adaydır.
2. Yeni bir oturumda sına: kuralın tetiklenmesi gereken bir soru sor ve cevabın kuralı yansıtıp yansıtmadığına bak.
3. Commit et ve sohbete ✅ yaz.

**Kontrol noktası:** Yeni oturumdaki cevap eklediğin kuralı yansıtıyor.

### Takılırsan

- **Agent soru sormak yerine çözüme geçiyor.** "Henüz çözüm önerme, yalnızca soruları listele" kısıtını yinele; düzenleme yapamayacağı bir modda çalıştır.
- **Kriterler muğlak.** "Uygun şekilde işlenir" bir kriter değildir. Her kriter somut bir istek ve beklenen durum koduyla yanıt içermeli.
- **Bir test hiçbir şey yazılmadan geçiyor.** Var olmayan bir adres de 404 döndürür. Yalnızca durum kodunu sınayan "olay yoksa 404" testi bir şey kanıtlamaz; yanıtın gövdesini de sına.
- **Agent mevcut testleri değiştirdi.** Nedenini sor. Mevcut davranış bozulmadıysa değişikliğe gerek yoktur; geri aldır.
- **`curl` 500 döndü.** Uygulama hangi veritabanını kullanıyor, testler hangisini? O veritabanı dosyası ne zaman oluşturuldu? Hata mesajının ilk satırını agent'a ver.
- **Agent veritabanı dosyasını silmek istiyor.** İzin penceresi bunun için var. Dosyanın ne olduğunu, geri getirilip getirilemeyeceğini (`python -m scripts.seed_demo`) ve `CLAUDE.md`'nin yıkıcı işlemler için ne dediğini düşün; sonra karar ver.
- **Agent bir migration aracı kurmak istiyor.** Bu, kriterlerinde var mı? `README.md`'nin "Bilinçli sınırlamalar" bölümüne bak.
- **Konuşma çok uzadı.** Kriterlerin diskte, `docs/OPS-106.md` içinde. Yer aç ve agent'a o dosyayı yeniden okut.

### Erken bitirenlere

- Kriterlerinde yoksa şu kuralı ekle ve önce testini yazdır: çözülmüş (`resolved`) bir olaya atama yapılamaz, 409 döner.
- `scripts/seed_demo.py` içindeki örnek veriye atanmış bir olay ekle. Seed script'inin "veri varsa ekleme" davranışı bu değişikliği nasıl etkiler?

---

## Ek Uygulama 1.3 — OPS-102: tek prompt, sıfır müdahale

**Ne zaman:** İki uygulamayı da bitirdiysen ya da gün planlanandan erken ilerliyorsa.
**Süre:** yaklaşık 40 dakika
**Pekiştirdiği konular:** Günün bütün döngüsü; bu kez agent'ı adım adım yönlendirmek yerine çerçeveyi önceden kurup sonucu denetliyorsun.

### Senaryo

Küçük bir istek daha geldi. Bu kez agent'ın başında durmayacaksın: işi tek bir prompt'la baştan sona yaptıracak, araya girmeyecek ve bittiğinde sonucu denetleyeceksin. Araya girmek zorunda kalırsan bunu say; her müdahale, prompt'unda ya da ortamında eksik kalan bir şeyi gösterir.

**OPS-102 — Olayları duruma göre filtrele**

- `GET /incidents` opsiyonel `status` parametresi alır: `open`, `investigating`, `resolved`.
- `severity` ile birlikte verilirse iki koşul birden uygulanır.
- Geçersiz `status` değeri 422 döner.
- Parametre yoksa mevcut davranış korunur.

### Çıktılar

1. `ops102-prompt.md`: agent'a verdiğin tek prompt
2. İki commit: önce test, sonra özellik
3. Denetim notu: müdahale sayısı ve bulduğun kusurlar

### Aşama 1 — Çerçeveyi kur (10 dk)

1. İzinleri hazırla: agent test çalıştırırken ve commit atarken sana sormasın; mevcut test dosyalarını değiştiremesin.
2. Prompt'u `ops102-prompt.md` dosyasına yaz. İçinde şunlar olsun: hikâye; önce test, sonra uygulama sırası; iki commit; dokunulmayacak dosyalar; işin bittiğini gösteren komutlar ve beklenen çıktıları. Agent'ın sana soru sormasına gerek kalmasın.

**Kontrol noktası:** Prompt'u okuyan biri, sana soru sormadan işin ne zaman bittiğini söyleyebilir.

### Aşama 2 — Çalıştır, araya girme (10 dk)

Temiz bir oturumda prompt'u ver ve agent bitirene kadar yazma. İzin penceresi çıkarsa ya da agent soru sorarsa cevapla, ama her birini say.

**Kontrol noktası:** Agent işi bitirdiğini bildirdi. Müdahale sayın yazılı.

### Aşama 3 — Denetle (15 dk)

Agent'ın raporuna değil, depoya bak.

1. `git log --oneline -3`: iki commit var mı, sırası doğru mu?
2. `git diff --stat HEAD~2`: yalnızca `app/main.py` ve yeni test dosyası mı değişti? Mevcut test dosyalarına dokunuldu mu?
3. `pytest -q`
4. Testler özellik yazılmadan önce gerçekten kırmızı mıydı? Test commit'ine geç, testleri çalıştır ve geri dön:

   ```bash
   git switch --detach HEAD~1
   pytest -q tests/test_ops102.py
   git switch -
   ```

   Baştan yeşil geçen test var mı? Her testin beklediği sonucu `tests/conftest.py`'deki fixture verisiyle karşılaştır.

**Kontrol noktası:** Fixture'a göre `status=open` yalnızca 1042 ve 1043'ü, `severity=low&status=open` boş listeyi, `status=investigating` boş listeyi, geçersiz değer 422'yi bekler. Testlerin bunlardan hangilerini sınadığını ve hangi testin özellik yazılmadan da geçtiğini biliyorsun.

### Aşama 4 — Çerçeveyi düzelt (5 dk)

Bulduğun her kusur ve her müdahale için prompt'una ya da izinlerine ne eklerdin? `ops102-prompt.md` dosyasını güncelle.

**Kontrol noktası:** Prompt'a yaptığın her ekleme bir kusura ya da bir müdahaleye karşılık geliyor.

### Takılırsan

- **Agent sürekli izin soruyor.** Hangi komut için? İzin kuralın komutun yazılışıyla eşleşiyor mu? `pytest -q` ile `python -m pytest -q` ayrı komutlardır.
- **Mevcut test dosyalarını nasıl korurum?** İzin ayarlarında, belirli dosyaların düzenlenmesini yasaklayan kurallar yazılabilir. `/permissions` yüklü kuralları gösterir.
- **Bir test daha uygulama yazılmadan yeşil geçiyor.** O test yeni davranışı sınamıyor. Beklenen sonuç, `status` filtresi olmadan da aynı çıkan bir birleşim olabilir. Fixture'a bak.
- **Agent tek commit attı ya da sırayı karıştırdı.** Prompt'un sırayı ve her commit'in içeriğini açıkça söylüyor muydu?
- **İki filtre birlikte çalışmıyor.** Her filtre sorguya ayrı bir koşul olarak eklenir.

---

## Başvuru

Gösterimlerin akışı.

### Gösterim 1.1 — Yeşil ama yanlış

Hedef: `POST /tasks` endpoint'i ve onu sınayan `test_task_creation_and_list` testi.

1. Agent'a sorulur: bu test neyi garanti ediyor, neyi etmiyor? Garanti etmediği her şey için, testi geçmeye devam eden ama yanlış olan bir uygulama örneği istenir.
2. Örneklerden biri gerçekten yazdırılır. `pytest -q -m 'not ops101'` hâlâ yeşildir: yanlış ama yeşil.
3. Hatalı uygulama saklanır ve doğru koda dönülür: `git diff --output=hatali-1.patch app/`, ardından `git checkout -- app/`.
4. Hatayı yakalayan test yazdırılır ve iki yönde çalıştırılır: doğru kodda yeşil, patch uygulanınca kırmızı.
5. Yalnızca test commit edilir.

### Gösterim 1.2 — OPS-107

Gelen istek: "Yanlışlıkla açılan görevleri listeden kaldıramıyoruz. Görevleri silebilmek istiyoruz." API çerçevesi: `DELETE /tasks/{task_id}`.

1. İstek ve çerçeve verilir. Çözüm değil, soru istenir; her soru için mevcut koddan bir varsayılan önerilir.
2. Sorular cevaplanır. Karar verilmeyen soruda önerilen varsayılan kabul edilir.
3. Kriterler, verilen kararlarla birlikte `docs/OPS-107.md` dosyasına yazdırılır. Her kriterin somut bir istek ve beklenen yanıt içerip içermediğine bakılır.
4. Kriterlerden testler yazdırılır: `tests/test_ops107.py`. Testler çalıştırılır; her birinin neden kırmızı olduğu okunur ve baştan yeşil geçen test ayıklanır.
5. Uygulama planı istenir; planın dokunacağı dosyalar tek tek sayılır.
