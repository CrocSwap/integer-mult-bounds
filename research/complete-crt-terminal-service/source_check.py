"""Authenticate public source closure and exercise the exact byte guard."""
from pathlib import Path
import json
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import integration

count = integration.authenticate()
rows = json.loads((HERE/"SOURCE-PINS.json").read_text())["files"]
data = (integration.ROOT/rows[0]["path"]).read_bytes()
try:
    integration.check_source_bytes(data+b"\n",rows[0])
except ValueError as exc:
    integration.need(str(exc) == "pinned source SHA-256","actual source-byte guard")
else:
    raise ValueError("source mutation accepted")
print(json.dumps({"status":"PASS_COMPLETE_CRT_SOURCE_CLOSURE","files":count,
                  "bytes":sum((integration.ROOT/r["path"]).stat().st_size for r in rows),
                  "mutation_rejected":True},sort_keys=True))
