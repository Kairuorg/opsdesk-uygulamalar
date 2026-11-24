"""Koruma hook'u: OPS-101 kabul testlerinin düzenlenmesini engeller."""
import json
import sys

PROTECTED = "tests/test_ops101.py"

event = json.load(sys.stdin)
path = str(event.get("tool_input", {}).get("file_path", "")).replace("\\", "/")
if path.endswith(PROTECTED):
    print(
        f"ENGELLENDI: {PROTECTED} kabul testidir ve degistirilemez. "
        "Testi degil, uygulama kodunu duzelt.",
        file=sys.stderr,
    )
    sys.exit(2)  # 2 = engelle; stderr metni agent'a iletilir
sys.exit(0)
