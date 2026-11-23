# OpsDesk Eğitimi — Uygulama Rehberi

Bu klasör dört günlük **Agentic Software Engineering** eğitiminin uygulamalarını içerir.

Her uygulamadan önce kısa bir gösterim yapılır: eğitmen, uygulamada kullanılacak tekniği başka bir örnek üzerinde agent ile canlı yürütür.

**Hedef kitle.** Katılımcılar Claude Code ve Codex'i günlük işinde kullanan yazılımcılardır. Uygulamalar ve gösterimler araçların temel kullanımını anlatmaz. Konu, agent'la yapılan işin doğrulanması, ölçülmesi ve sınırlandırılmasıdır.

Tüm uygulamalar bu repodaki sentetik OpsDesk API'si üzerinde yapılır. Gerçek sistem, gerçek Jira, gerçek kimlik bilgisi kullanılmaz.

## Bir günün uygulamaları

Dört günde de aynı sıra izlenir.

| Sıra | Ne yapılır | Kim |
|---|---|---|
| 1 | **Gösterim 1.** Uygulama 1'in tekniği başka bir örnekte canlı yürütülür | Eğitmen gösterir, katılımcı izler ve sorar |
| 2 | **Uygulama 1.** Aşamalı, tek bir senaryo | Katılımcı yapar, takıldığında sorar |
| 3 | **Gösterim 2.** Uygulama 2'nin tekniği başka bir örnekte canlı yürütülür | Eğitmen gösterir, katılımcı izler ve sorar |
| 4 | **Uygulama 2.** Aşamalı, tek bir senaryo | Katılımcı yapar, takıldığında sorar |
| 5 | **Kapanış.** Teslimler ve iki üç ekran paylaşımı | Herkes |

Uygulamalar az ve uzundur: günde iki tane. Her uygulama, eğitimde anlatılan birkaç konuyu gerçek bir iş akışında birleştirir.

Her günün ayrıca bir **ek uygulaması** vardır. İki uygulama planlanandan erken biterse ya da bir katılımcı ikisini de bitirirse yapılır. Kendi başına tamamlanabilen bir geliştirme işidir.

Üç kural:

- **Gösterim ile uygulama kardeştir.** Teknik aynıdır, hedef farklıdır. Uygulama, gösterimde ekranda olanı kopyalayarak bitirilemez.
- **Her aşamanın gözle görülür bir kontrol noktası vardır:** komut çıktısı, oluşan dosya, test sonucu. "Oldu galiba" kabul edilmez.
- **Agent'ın söylediği doğrulanmadan kabul edilmez.** Kanıt, kaynak dosya ve gerçek komut çıktısıdır.

## Dört günlük harita

| Gün | Konular | Uygulama 1 | Uygulama 2 | Ek uygulama (süre kalırsa) | Dosya |
|---|---|---|---|---|---|
| 1 | Agentic coding temelleri, Claude Code mimarisi, Git ve görev tabanlı geliştirme | OPS-101: yeşil testler neyi kanıtlamaz? | Belirsiz istekten PR'a: olay atama (OPS-106) | OPS-102: tek prompt, sıfır müdahale | `gun-1/README.md` |
| 2 | Skills, Hooks, Subagents, MCP | Kod inceleme skill'i ve kalite kontrol hook'u | Log analiz MCP server'ı | OPS-104: kurulan araçlarla özellik geliştirme | `gun-2/README.md` |
| 3 | AI destekli kod kalitesi, agent güvenliği, otomasyon ve CI/CD | Legacy kodda hata düzeltme ve API testleri | Prompt injection değerlendirmesi ve quality gate | Güvenli refactoring | `gun-3/README.md` |
| 4 | Claude Code × Codex, multi-agent orchestration, cross-review, değerlendirme | İki agent'la geliştirme ve cross-review | Final: hatalı PR'ın karşılaştırmalı incelemesi | OPS-105: paralel handoff | `gun-4/README.md` |

Her günün dosyası o gün depoya eklenir.

## Uygulama dosyasının yapısı

Her gün dosyası aynı sırayla yazılmıştır:

| Bölüm | İçerik |
|---|---|
| **Günün sırası** | Gösterimler ve uygulamalar, sırasıyla |
| **Gösterimler** | Her uygulamadan önce canlı gösterilen örnek ve gösterilenler |
| **Uygulama** | Senaryo, çıktılar, aşamalar içinde sıralı adımlar, her aşamanın kontrol noktası |
| **Takılırsan** | Sık takılınan yerler ve bir sonraki adımı gösteren ipuçları |
| **Erken bitirenlere** | Bir uygulamayı erken bitirenler için aynı konuyu derinleştiren kısa görevler |
| **Ek uygulama** | İki uygulama da erken biterse yapılacak aşamalı geliştirme işi |
| **Başvuru** | Gösterimlerde kullanılan ve uygulamalarda başvurulacak kod ve komutlar |

## Takılınca: yardım protokolü

Eğitim online olduğu için takılan kişinin görünür olması gerekir. Sırayla:

1. Uygulamadaki **Takılırsan** maddelerine ve gün dosyasının sonundaki **Başvuru** bölümüne bak.
2. Hatayı agent'a ver: komutu, çıktıyı ve ne beklediğini yaz. Agent iyi bir hata ayıklama ortağıdır.
3. Beş dakikadır aynı yerdeysen sohbete 🆘 ile birlikte üç satır yaz:
   - Ne yapmaya çalışıyordum
   - Ne bekliyordum
   - Ne oldu (komut ve çıktı)
4. Yardımcı eğitmen ayrı odada ekran paylaşımıyla bakar. Cevabı söylemez, bir sonraki ipucunu verir.
5. Aynı soru üç kişiden gelirse eğitmen uygulamayı durdurur ve herkese açıklar.

Eğitmen her aşamanın sonunda durum yoklaması yapar: ✅ aşamayı bitirdim · ⏳ devam ediyorum · 🆘 takıldım.

Bir aşamada geride kalan, o aşamanın kontrol noktasını eğitmenle birlikte geçip bir sonrakine ilerler. Bir uygulamayı erken bitiren, o uygulamanın **Erken bitirenlere** maddelerine geçer. İki uygulamayı da bitiren günün ek uygulamasını yapar ya da takılan bir katılımcıya eşlik eder.

## Ortak kurallar

- Yalnızca sentetik veri. Gerçek sisteme, gerçek Jira'ya, kurum ağına bağlanılmaz.
- `.env` ve API anahtarları okunmaz, yazdırılmaz, repoya konmaz. Güvenlik uygulamalarında yalnızca sahte kanarya değerleri kullanılır.
- Herkes kendi dalında çalışır. Push ve PR, eğitmenin açıkladığı kurala göre yapılır.
- Bir testi geçirmek için test gevşetilmez.
- Sonuç bildirirken çalıştırılan komut ve görülen çıktı gösterilir.

## Dil

Dokümanlar, kod içindeki açıklamalar ve script'lerin ekrana yazdığı mesajlar Türkçedir. Script çıktılarında Türkçe karakter kullanılmaz; çıktıyı bir agent ya da başka bir program okuduğunda konsol kodlaması hata vermesin diye. Legacy modül (`app/legacy/`) eski kod görünümünü korumak için bütünüyle Türkçe karaktersiz yazılmıştır.

İngilizce kalanlar: kod adları (fonksiyon, alan, komut), API'nin döndürdüğü mesajlar, sentetik veri (olay başlıkları, log satırları), repo geçmişindeki commit mesajları ve yerleşik teknik terimler.

## Kurulum

- Her gün: Python 3.12 ya da üstü ve Claude Code 2.1 ya da üstü. Komutlar gün dosyasının **Başlangıç** bölümündedir.
- 2. günden itibaren `mcp` Python paketi: `python -m pip install "mcp[cli]"`
- 4. gün için kurulu ve giriş yapılmış Codex CLI

## Günlerin başlangıcı

Bu depo eğitimin uygulamaları içindir ve gün gün büyür: her günün başlangıç dosyaları o gün `main` dalına eklenir.

| Gün | `main` dalına eklenenler |
|---|---|
| 1 | OPS-101 çözülmemiş uygulama, bu rehber ve 1. günün uygulamaları |
| 2 | OPS-101 referans çözümü, log verisi script'i, 2. günün uygulamaları |
| 3 | 2. günün referans çözümleri, legacy modül, hata biletleri, injection senaryoları, 3. günün uygulamaları |
| 4 | Legacy hatalarının düzeltmesi ve referans testleri, 4. günün uygulamaları. Final uygulamasının PR'ı ayrı bir dalda gelir: `hatali-pr` |

1. gün depoyu klonla ve kendi dalını aç. Sonraki günlerde önce güncel `main` dalını al, sonra o günün dalını aç:

```bash
git switch main
git pull
git switch -c participant/<kimlik>/day<N>
```

Önceki günün dalında commit edilmemiş değişikliğin varsa önce onu commit et. `main` dalına commit atma; her gün kendi dalında çalış.
