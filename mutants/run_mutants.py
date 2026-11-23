"""Uygulama 1.1: hatalı OPS-101 uygulamalarını senin testlerine karşı çalıştırır.

Kullanım (repo kökünden):

    python mutants/run_mutants.py tests/test_ops101_extra.py

Uygulama 1.1, Aşama 4'te kullanılır; Aşama 3 bitmeden bu klasörü açma.

Bu klasördeki her hatalı uygulama (m1.py, m2.py, ...) için app/main.py geçici olarak
değiştirilir, önce mevcut 12 test, sonra senin testlerin çalıştırılır ve app/main.py
eski hâline döndürülür. Testlerin hatalı uygulamada kırmızıya dönüyorsa o hatayı
yakalamış sayılırsın.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TARGET = ROOT / "app" / "main.py"
BACKUP = HERE / "main.py.yedek"
EXISTING_TESTS = ["tests/test_api.py", "tests/test_ops101.py"]


def tests_pass(paths):
    # Eski derlenmiş dosya kalmasın: art arda kopyalanan dosyalar aynı boyutta olabilir.
    for cached in (ROOT / "app" / "__pycache__").glob("main.*.pyc"):
        cached.unlink()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *paths],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def has_uncommitted_changes():
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--", "app/main.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return False
    return bool(result.stdout.strip())


def main(argv):
    # Çıktıda Türkçe karakter yok: konsol kodlaması hata vermesin.
    if not argv:
        print("Kullanim: python mutants/run_mutants.py <test dosyan> [baska test dosyalari]")
        return 2
    missing = [path for path in argv if not (ROOT / path).exists()]
    if missing:
        print("Bulunamadi: " + ", ".join(missing))
        return 2
    if BACKUP.exists():
        print("Onceki calistirmadan kalan yedek var: mutants/main.py.yedek")
        print("Once app/main.py dosyasini kontrol et (git diff app/main.py), sonra yedegi sil.")
        return 2
    if has_uncommitted_changes():
        print("app/main.py icinde commit edilmemis degisiklik var. Once OPS-101 cozumunu commit et.")
        return 2
    if not tests_pass(EXISTING_TESTS):
        print("Mevcut 12 test kendi uygulamanda gecmiyor. Once OPS-101'i bitir.")
        return 2
    if not tests_pass(argv):
        print("Senin testlerin kendi uygulamanda kirmizi. Testlerin dogru uygulamada yesil olmali.")
        return 2

    mutants = sorted(HERE.glob("m[0-9]*.py"))
    if not mutants:
        print("Bu klasorde hatali uygulama (m1.py, m2.py, ...) yok.")
        return 2

    rows = []
    shutil.copyfile(TARGET, BACKUP)
    try:
        for mutant in mutants:
            shutil.copyfile(mutant, TARGET)
            existing_pass = tests_pass(EXISTING_TESTS)
            caught = not tests_pass(argv)
            rows.append((mutant.stem, existing_pass, caught))
    finally:
        shutil.copyfile(BACKUP, TARGET)
        BACKUP.unlink()

    print("")
    print("%-18s %-16s %s" % ("Hatali uygulama", "Mevcut 12 test", "Senin testlerin"))
    for name, existing_pass, caught in rows:
        print("%-18s %-16s %s" % (
            name,
            "geciyor" if existing_pass else "KALIYOR",
            "YAKALADI" if caught else "kacti",
        ))
    caught_count = sum(1 for _, _, caught in rows if caught)
    print("")
    print("Skor: %d / %d hatali uygulama yakalandi." % (caught_count, len(rows)))
    escaped = [name for name, _, caught in rows if not caught]
    if escaped:
        print("Kacanlari incele, ornek:  git diff --no-index app/main.py mutants/%s.py" % escaped[0])
    print("app/main.py eski haline donduruldu.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
