"""Freeze six exact continuations from the modular rank drops."""
from hashlib import sha256
from pathlib import Path
import json
import sys

PIN = "a3505dd0cfd3ee9e242f804e12e3c4705ea6548080d537f597cec355f358e92c"
root = Path(sys.argv[1])
raw = (root/"lead/RESULT.json").read_bytes()
if sha256(raw).hexdigest() != PIN:
    raise ValueError("changed modular support receipt")
d = json.loads(raw)
assert d["status"] == "EXHAUSTED" and d["counts"]["rank drop"] == 2134
rank_drops = [r for r in d["results"] if r["disposition"] == "rank drop"]


def priority(r):
    return (bool(r["owned"]), len(r["pivots"]) < 2,
            len(r["public"]) - len(r["pivots"]),
            r["exterior_rank"] - len(r["public"]),
            -len(r["pivots"]), -r["key"][0], r["key"][1])


selected, charts, clocks = [], set(), set()
for row in sorted(rank_drops, key=priority):
    t, c = row["key"]
    if c in charts or t in clocks:
        continue
    selected.append(row)
    charts.add(c)
    clocks.add(t)
    if len(selected) == 6:
        break
assert len(selected) == 6
used = {tuple(r["key"]) for r in selected}
print(json.dumps(dict(modular_sha256=PIN, exact_cap=6, exact_seconds_cap=35,
    ordered_score="no owned, >=2 pivots, fewest external roles, greatest nullity, most pivots, later cut, chart",
    diversification="one cut per chart and one chart per cut",
    selected=selected, unselected=[r["key"] for r in rank_drops if tuple(r["key"]) not in used]),
    indent=2, sort_keys=True))
