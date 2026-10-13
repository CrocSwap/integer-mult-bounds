"""Apply moves.json to the base word (research/e8-bit-p111/data/bitE8mut-p111.json.gz) and write the tuned word.
usage: apply.py BASE.json.gz MOVES.json OUT.json.gz [--discover]
Checks: the base word's canonical content hash; each moved summand and its gate and frame; the exact replay of the result
(frames nested, every F2 column restored, targets y + x) and its local paid profile.  C is rebuilt as the literal reverse
of the z-destination gates of A then B at the full frame.  --discover also runs the generic searches of tune.py on the
base word (transports, Steinberg 3 -> 2, frame reassignment, on A and B, to a fixed point) and asserts that they find
exactly this word (same flat operation list, same frames).
Prepared with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0."""
import copy
import hashlib
import json
import sys
from pathlib import Path

import wlib

base_p, moves_p, out_p = sys.argv[1:4]
discover = "--discover" in sys.argv[4:]
mv = json.loads(Path(moves_p).read_text())
base = wlib.load(base_p)
h = hashlib.sha256(wlib.canon(base)).hexdigest()
assert h == mv["base_content_sha256"], "base word differs from the pinned one"
before = wlib.paid(base)
A = base["A"]
rm, ins = {}, {}
for m in mv["moves"]:
    f, d, ss = A[m["gate"]]
    assert d == m["dst"] and m["src"] in ss and f == m["from_frame"] and len(ss) > 1, m["name"]
    rm.setdefault(m["gate"], []).append(m["src"])
    ins.setdefault(m["before_gate"], []).append([m["to_frame"], m["dst"], [m["src"]]])
newA = []
for i, (f, d, ss) in enumerate(A):
    newA += [copy.deepcopy(g) for g in ins.get(i, [])]
    newA.append([f, d, [s for s in ss if s not in rm.get(i, [])]])
assert not [k for k in ins if k >= len(A)]
w = copy.deepcopy(base)
w["A"] = newA
w["C"] = wlib.rebuild_C(w)
after = wlib.paid(w)       # asserts nested frames and the exact F2 endpoint on all columns
assert sum(k * n for k, n in before.items()) == sum(k * n for k, n in after.items())
sha = wlib.save(w, out_p)
print("   %d moves; local paid profile %s -> %s; word sha256 %s" % (len(mv["moves"]), before, after, sha))
if discover:
    import tune
    Tn = tune.Tuner(base, a=0.001733)
    total = 0
    for _ in range(4):
        n = 0
        for ch in "TSF":
            for sec in "AB":
                V = Tn.view(sec)
                ap = (tune.transport_sweep(V, verbose=False) if ch == "T" else
                      tune.steinberg_sweep(V, verbose=False) if ch == "S" else
                      tune.transport_sweep(V, verbose=False, allow_move=False))
                n += len(ap)
        total += n
        if not n:
            break
    found = Tn.word()
    flat = lambda x, s: [(f, t, q) for f, t, qq in x[s] for q in qq]  # noqa: E731
    assert total == len(mv["moves"]), total
    assert flat(found, "A") == flat(w, "A") and flat(found, "B") == flat(w, "B") and found["frames"] == w["frames"]
    assert found["start"] == w["start"] and found["final"] == w["final"] and found["D"] == w["D"]
    print("   rediscovery: transports, Steinberg and frame passes on A and B find exactly these %d moves" % total)
