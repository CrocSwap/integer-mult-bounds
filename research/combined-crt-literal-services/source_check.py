"""Authenticate the compact exact-source closure, with a byte-mutation control."""
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import join

count = join.authenticate()
join.need(count == 14, "complete fourteen-file source closure")
rows = json.loads((HERE / "SOURCE-PINS.json").read_text())["files"]
row = rows[0]
data = bytearray((join.ROOT / row["path"]).read_bytes())
data[-1] ^= 1
join.need(sha256(data).hexdigest() != row["sha256"]
          and sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() != row["git_blob"],
          "source-byte mutation must change both identities")
print(json.dumps({"status": "PASS_COMBINED_CRT_SOURCE_CLOSURE",
                  "files": count, "bytes": sum((join.ROOT / r["path"]).stat().st_size for r in rows),
                  "mutation_rejected": True}, sort_keys=True))

