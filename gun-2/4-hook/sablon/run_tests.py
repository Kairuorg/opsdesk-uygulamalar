"""Kalite kontrol hook'u: app/ altında bir .py dosyası değişince testleri çalıştırır."""
import json
import os
import subprocess
import sys
from pathlib import Path

event = json.load(sys.stdin)
root = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
raw = str(event.get("tool_input", {}).get("file_path", ""))
if not raw:
    sys.exit(0)

path = Path(raw)
if not path.is_absolute():
    path = root / path
try:
    relative = path.resolve().relative_to(root).as_posix()
except ValueError:
    sys.exit(0)  # proje dışındaki dosya
if not (relative.startswith("app/") and relative.endswith(".py")):
    sys.exit(0)

result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x"], cwd=root, capture_output=True, text=True)
if result.returncode != 0:
    tail = "\n".join((result.stdout + result.stderr).strip().splitlines()[-15:])
    print("Testler kaldi. Degisikligi duzelt:\n" + tail, file=sys.stderr)
    sys.exit(2)
sys.exit(0)
