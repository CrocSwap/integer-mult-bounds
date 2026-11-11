"""Negative controls for the elimination reuse: every mutant of the final word must be rejected by PR #370's
independent all-column checker (code/bit/independent/checkword.py, run unchanged in a subprocess, as PR #370's
mutate.py does). The mutated gates are the inserted elimination gates listed in the reuse ledger written by regen.py.
usage: controls.py WORD.json.gz LEDGER.json PRICING_DIR
Prepared by eumemic with Anthropic Claude assistance; Apache-2.0."""
import copy
import gzip
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "..", "bit", "independent", "checkword.py")
word, ledger, pricing = sys.argv[1:4]
w = json.load(gzip.open(word, "rt"))
led = json.load(open(ledger))
v = w["v"]
elim = [(ph, i) for ph, i, kind in led["eliminations"] if kind == "helper"]
undo = [(ph, i) for ph, i, kind in led["eliminations"] if kind == "total"]
assert len(elim) == led["helpers"] and len(undo) == led["totals"]
for ph, i in elim + undo:     # each ledger entry is an elimination into a helper slot
    assert w[ph][i][1] >= 2 * v and w[ph][i][2]
lines = [frozenset(f) for f in w["frames"]]   # frames are closed: frame a lies inside frame b iff lines[a] <= lines[b]


def prev_frame(c, ph, i, r):
    """frame id of register r just before gate (ph, i) (its last earlier gate in D, A, ... or its start frame)"""
    f = c["start"][r]
    for p in ("D", "A", "B", "C"):
        for k, g in enumerate(c[p]):
            if (p, k) == (ph, i):
                return f
            if r == g[1] or r in g[2]:
                f = g[0]
    raise AssertionError("gate not found")


muts = []
c = copy.deepcopy(w); ph, i = elim[0]; del c[ph][i]
muts.append(("omit the first helper elimination gate (the reused slot keeps a leftover x-content)", c))
c = copy.deepcopy(w); ph, i = next((p, k) for p, k in elim if len(w[p][k][2]) >= 2); c[ph][i][2].pop()
muts.append(("omit one eliminator of a helper elimination with two or more eliminators", c))
c = copy.deepcopy(w); ph, i = undo[0]; c[ph][i][2].pop()
muts.append(("omit one x-line read of a retained-total undo gate", c))
c = copy.deepcopy(w)
for ph, i in elim:
    f, d, srcs = c[ph][i]
    low = prev_frame(c, ph, i, d)
    if lines[low] < lines[f] and any(not lines[prev_frame(c, ph, i, s)] <= lines[low] for s in srcs):
        c[ph][i][0] = low
        break
else:
    raise AssertionError("no elimination gate above its slot's own frame")
muts.append(("an elimination gate lowered to the reused slot's own frame (below an eliminator's frame)", c))
c = copy.deepcopy(w)
for ph, i in sorted(elim + undo, key=lambda z: (z[0], -z[1])):
    del c[ph][i]
muts.append(("reuse without elimination: all %d elimination and undo gates removed" % (len(elim) + len(undo)), c))
c = copy.deepcopy(w); ph, i = undo[0]; c[ph][i][0] = w["start"][v]
muts.append(("a retained-total undo gate moved from the full frame to frame 0", c))
tmpd = tempfile.mkdtemp()
for k, (name, c) in enumerate(muts):
    p = os.path.join(tmpd, "mut%d.json.gz" % k)
    with gzip.open(p, "wt") as fh:
        json.dump(c, fh)
    r = subprocess.run([sys.executable, "-I", "-B", CHECK, p, pricing], capture_output=True, text=True)
    assert r.returncode != 0, "mutant accepted: " + name
    print("   REJECTED %s :: %s" % (name, (r.stderr.strip().splitlines() or ["?"])[-1][:90]))
print("PASS all %d elimination-reuse negative controls rejected by PR #370's independent checker" % len(muts))
