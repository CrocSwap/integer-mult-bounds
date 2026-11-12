"""Independently count earlier carriers with a reverse first-contact walk."""
import gzip
import hashlib
import json
from pathlib import Path

base = Path(__file__).resolve().parents[1]
pins = {
    "lead/PRICE.json": "88ff264d2744dee9bc0bc9ecfe25fc4e53f30958c8c947d16e4df87c908e5c65",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/R137-RESULT.json": "a109deda97d3b4f5ceb52814a50186035ea44ac1bdaf47281f564dcc2da239db",
}

def load(name):
    raw = (base / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == pins[name]
    return json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)

price = load("lead/PRICE.json")
rows = load("inputs/R137-RESULT.json")["records"]
word = load("inputs/7334-WORD.json.gz")["program"]
def touch(e, h):
    return h in e[1:3] if e[0] in ("COPY", "ADD") else h == e[1]

eligible, counts = [], []
for row in rows:
    anchor, h = row["move_clock"], row["role"]
    next_use = row["first_clock"]
    assert touch(word[next_use], h) and next_use == anchor + 1
    moves = []
    for t in range(anchor-1, -1, -1):
        e = word[t]
        if touch(e, h):
            break
        if e[0] == "MOVE" and e[2:4] == [row["chart_from"], row["chart_to"]]:
            moves.append((t,e[1]))
    blocked = [(t,f) for t,f in moves if any(touch(e,f) for e in word[t+1:next_use])]
    eligible.extend([anchor,t,f] for t,f in moves if (t,f) not in blocked)
    counts.append([anchor,len(moves),len(blocked)])
assert len(word) == price["max_events"] and len(rows) == price["max_anchors"] and not eligible
print(json.dumps({"counts": sorted(counts), "eligible": eligible, "pins": pins}, sort_keys=True, indent=2))
