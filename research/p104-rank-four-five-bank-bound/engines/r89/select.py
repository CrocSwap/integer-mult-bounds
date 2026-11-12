"""Freeze six deterministic rational checks from the bounded modular ranking."""
from hashlib import sha256
import json
from pathlib import Path
import sys

PIN = "4b8f2963ae0ef7bd357c3129e8287f79c5c1fccca6375c41e35fa01c476cb2ae"

root = Path(sys.argv[1])
raw = (root / "lead/PAIR.json").read_bytes()
if sha256(raw).hexdigest() != PIN:
    raise ValueError("changed pair-priority receipt")
receipt = json.loads(raw)
assert receipt["cases"] == 1465 and not receipt["unvisited"]
records = receipt["results"]
selected, clocks, charts = [], set(), set()
for row in sorted(records, key=lambda r: (r["pair_class"] == 2, bool(r["owned"]),
        r["pair_class"], r["direct_terms"], len(r["public"]) - len(r["pivots"]), r["key"])):
    cut, chart = row["key"]
    if cut in clocks or chart in charts:
        continue
    selected.append(row)
    clocks.add(cut)
    charts.add(chart)
    if len(selected) == 6:
        break
assert len(selected) == 6 and not any(r["owned"] for r in selected)
used = {tuple(r["key"]) for r in selected}
print(json.dumps({"pair_sha256": PIN, "case_cap": 6, "seconds_cap": 35,
                  "selected": selected, "unselected": [r["key"] for r in records if tuple(r["key"]) not in used]},
                 indent=2, sort_keys=True))
