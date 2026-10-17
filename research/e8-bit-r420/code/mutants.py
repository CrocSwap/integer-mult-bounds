"""Mutation controls for xcheck.py (exact replay and interleaved-interface audit).  Every negative control must be
rejected: either the replay raises (frame legality or the exact F2 identity fails), or a hypothesis or conclusion of the
interleaved lemma fails.  The positive control must be accepted.
usage: mutants.py XCHECK_PY WORD.json.gz [--json OUT]

Negative controls (sites are found from the word's structure, not from producer code):
  1 target feeds a source: a cancelled pair x_k += y_t inserted before the target's d-single read of x_k (F2-neutral)
  2 target feeds a helper: a cancelled pair h += y_t inserted before the first target read of a helper h (F2-neutral)
  3 drop a cleanup gate (the literal inverse of the last phase-B source write)
  4 corrupt a phase-B source write: its source operand replaced by another source register of the same block frame,
    with the matching cleanup gate changed the same way (C stays the literal reverse; every source is restored)
  5 move a phase-B source write below the source's frame (to the destination source's own line)
  6 a target reads another target (a single read at frame 0 at the start of phase B, so V != I)
  7 corrupt the frame-0 preconditioner (drop one helper read from a D gate)
  8 move a phase-B source write before the target read of that register (the write order relative to the reads)
  9 move a cleanup gate off the full frame (to the frame of the gate it inverts)
Positive control:
  P a cancelled pair of target-to-target reads at frame 0 (y_t += y_u twice: V = I, allowed by the lemma)

Production path reuses exact Word.__init__/labels geometry across evaluate() calls when h/v/R/form/lines/frames
match (research/r420-geometry-cache/). full() and interface() always rerun on a fresh Word. Equivalence: same
check API and mutation receipts as the pairwise harness.
Prepared by eumemic with substantial Anthropic Claude assistance; production geometry cache by Wentao Li with
substantial AI assistance; Apache-2.0."""
import copy
from collections import OrderedDict
import gzip
import importlib.util
import json
import sys

sp = importlib.util.spec_from_file_location("xcheck", sys.argv[1])
X = importlib.util.module_from_spec(sp)
sp.loader.exec_module(X)
w0 = json.load(gzip.open(sys.argv[2], "rt"))
v = w0["v"]
is_y = lambda r: v <= r < 2 * v
is_z = lambda r: not is_y(r)
ZERO = next(k for k, f in enumerate(w0["frames"]) if not f)

# Complete data dependencies of Word.__init__ and labels(); see research/r420-geometry-cache/.
GEOMETRY_FIELDS = ("h", "v", "R", "form", "lines", "frames")


class GeometryCache:
    """Reuse validated geometry across mutation checks with identical geometry fields."""

    def __init__(self, capacity=2):
        if type(capacity) is not int or capacity < 1:
            raise ValueError("capacity must be a positive integer")
        self.capacity = capacity
        self._entries = OrderedDict()
        self.hits = 0
        self.misses = 0

    def check(self, word):
        key = json.dumps({field: word[field] for field in GEOMETRY_FIELDS},
                         sort_keys=True, separators=(",", ":"), allow_nan=False)
        if key in self._entries:
            self.hits += 1
            snapshot = self._entries.pop(key)
            self._entries[key] = snapshot
        else:
            self.misses += 1
            checked = X.Word(word)
            labels = checked.labels()  # Failures never populate the cache.
            snapshot = (
                checked.v, checked.R, checked.n, tuple(checked.lines),
                tuple(checked.fdim),
                tuple(tuple(tuple(row) for row in frame) for frame in checked.fperp),
                checked.FULL, checked.ZERO, tuple(labels.items()),
            )
            self._entries[key] = snapshot
            if len(self._entries) > self.capacity:
                self._entries.popitem(last=False)

        # Never return the cached mutable Word or share mutable derived data.
        obj = X.Word.__new__(X.Word)
        obj.w = word
        obj.v, obj.R, obj.n = snapshot[:3]
        obj.lines = list(snapshot[3])
        obj.fdim = list(snapshot[4])
        obj.fperp = [[list(row) for row in frame] for frame in snapshot[5]]
        obj.FULL, obj.ZERO = snapshot[6:8]
        obj._nest = {}
        labels = dict(snapshot[8])
        full = obj.full()
        hypotheses, conclusion, info = obj.interface()
        return obj, labels, full, hypotheses, conclusion, info


_geometry_cache = GeometryCache()


def zgates(w):
    return [("A", i) for i, g in enumerate(w["A"]) if is_z(g[1])] + [("B", i) for i, g in enumerate(w["B"]) if is_z(g[1])]


def mirror(w, sec, i):
    zg = zgates(w)
    return len(zg) - 1 - zg.index((sec, i))


def evaluate(w):
    try:
        # Production path caches geometry when argv[1] is a full xcheck module.
        # Historical drop-in adapters (research/r420-geometry-cache/cached_xcheck.py)
        # expose only check/Reject; call them directly.
        if hasattr(X, "Word") and hasattr(X, "check"):
            W, lab, fl, H, C, info = _geometry_cache.check(w)
        else:
            W, lab, fl, H, C, info = X.check(w)
    except X.Reject as e:
        return False, "replay: " + str(e)[:90]
    bad = [k for k, x in list(H.items()) + list(C.items()) if not x]
    return (not bad), ("interface: fails " + ",".join(bad)) if bad else "accepted"


def first_keeper_read(w):
    return next(j for j, g in enumerate(w["B"]) if is_y(g[1]) and any(s < v for s in g[2]))


def b_source_writes(w):
    return [i for i, g in enumerate(w["B"]) if g[1] < v and all(s < v for s in g[2]) and len(g[2]) == 1]


def m1(w):
    j = first_keeper_read(w)
    F, t, srcs = w["B"][j]
    xk = next(s for s in srcs if s < v)
    w["B"][j:j] = [[F, xk, [t]], [F, xk, [t]]]
    return "target feeds a source (cancelled pair, F2-neutral)"


def m2(w):
    j = next(j for j, g in enumerate(w["B"]) if is_y(g[1]) and any(s >= 2 * v for s in g[2]))
    F, t, srcs = w["B"][j]
    h = next(s for s in srcs if s >= 2 * v)
    w["B"][j:j] = [[F, h, [t]], [F, h, [t]]]
    return "target feeds a helper (cancelled pair, F2-neutral)"


def m3(w):
    last = max(i for i, g in enumerate(w["B"]) if g[1] < v)
    p = mirror(w, "B", last)
    assert p == 0
    w["C"].pop(p)
    return "drop a cleanup gate (inverse of the last phase-B source write)"


def m4(w):
    i = b_source_writes(w)[0]
    F, d, (s,) = w["B"][i]
    p = mirror(w, "B", i)
    lines = w["frames"][F]
    other = next(r for r in lines if r not in (d, s))
    w["B"][i] = [F, d, [other]]
    assert w["C"][p][1:] == [d, [s]]
    w["C"][p] = [w["C"][p][0], d, [other]]
    return "corrupt a phase-B source write (operand %d -> %d, cleanup changed alike)" % (s, other)


def m5(w):
    i = b_source_writes(w)[0]
    F, d, srcs = w["B"][i]
    w["B"][i] = [w["start"][d], d, srcs]
    return "phase-B source write moved down to the destination's own line frame"


def m6(w):
    w["B"].insert(0, [ZERO, v + 0, [v + 1]])
    return "a target reads another target (single read, V != I)"


def m7(w):
    g = next(g for g in w["D"] if len(g[2]) > 1)
    g[2].pop()
    return "frame-0 preconditioner corrupted (one helper read dropped)"


def m8(w):
    i = min(i for i, g in enumerate(w["B"]) if is_z(g[1]))
    d = w["B"][i][1]
    j = next(j for j, g in enumerate(w["B"]) if is_y(g[1]) and d in g[2])
    assert j < i
    g = w["B"].pop(i)
    w["B"].insert(j, g)
    return "phase-B source write moved before the target read of that register"


def m9(w):
    p = len(w["C"]) - 1
    zg = zgates(w)
    sec, i = zg[len(zg) - 1 - p]
    w["C"][p][0] = w[sec][i][0]
    return "cleanup gate moved off the full frame (to the frame of the gate it inverts)"


def pos(w):
    w["B"][0:0] = [[ZERO, v + 0, [v + 1]], [ZERO, v + 0, [v + 1]]]
    return "cancelled pair of target-to-target reads at frame 0 (V = I)"


ok0, msg0 = evaluate(w0)
assert ok0, ("the unmutated word must pass", msg0)
rows = []
allok = True
for f in (m1, m2, m3, m4, m5, m6, m7, m8, m9):
    w = copy.deepcopy(w0)
    name = f(w)
    acc, msg = evaluate(w)
    rows.append(dict(control=f.__name__, mutation=name, rejected=not acc, by=msg))
    allok &= not acc
    print("   %s  %s :: %s" % ("REJECTED " if not acc else "ACCEPTED!", name, msg))
w = copy.deepcopy(w0)
name = pos(w)
acc, msg = evaluate(w)
rows.append(dict(control="positive", mutation=name, rejected=not acc, by=msg))
allok &= acc
print("   %s  %s :: %s" % ("accepted " if acc else "REJECTED!", name, msg))
assert allok, "a mutation control did not behave as required"
print("PASS mutation controls: 9/9 negative controls rejected, 1/1 positive control accepted")
if "--json" in sys.argv:
    json.dump(dict(status="PASS_INTERLEAVED_INTERFACE_MUTATION_CONTROLS", controls=rows),
              open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
