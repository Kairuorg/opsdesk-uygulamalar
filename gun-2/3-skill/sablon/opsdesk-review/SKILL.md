---
name: opsdesk-review
description: OpsDesk değişikliklerini proje kurallarına göre inceler. Kullanıcı "değişikliğimi incele", "diff'i incele", "PR'ı gözden geçir" ya da "review yap" dediğinde kullan. Test çalıştırma isteklerinde kullanma.
argument-hint: "[karşılaştırılacak ref]"
allowed-tools: Bash(git diff *), Bash(git status *), Bash(git log *)
---

# OpsDesk değişiklik incelemesi

Verilen argüman: `$ARGUMENTS`

1. İncelenecek farkı al. Argüman boş değilse `git diff <argüman>...HEAD`, boşsa `git diff HEAD` çalıştır. Fark boşsa "İncelenecek değişiklik yok" yaz ve dur.
2. [checklist.md](checklist.md) dosyasındaki her maddeyi sırayla kontrol et. Gerekirse değişen dosyaların tamamını oku.
3. Yalnızca kanıtlayabildiğin bulguları yaz. Üslup ve biçim önerisi yazma.
4. Hiçbir dosyayı değiştirme.

## Çıktı

Her bulgu tek satır:

`önem | dosya:satır | kanıt | öneri`

Önem dereceleri:

- `critical`: veri kaybı, güvenlik açığı ya da testlerin gevşetilmesi. Merge edilemez.
- `high`: kabul kriteri ya da proje kuralı ihlali. Merge edilmeden düzeltilmelidir.
- `medium`: mevcut sözleşmeyi ya da davranışı riske atan değişiklik. Merge öncesi karar gerekir.
- `low`: düzeltilmesi iyi olur; merge'i engellemez.

Bulgu yoksa `Bulgu yok` yaz ve kontrol ettiğin maddeleri listele.
