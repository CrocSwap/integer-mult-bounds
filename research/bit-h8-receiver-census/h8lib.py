"""Shared helpers: build an h = 8 punctured L3 BIT word with PR555's generator, export its records, price it
under the p16 query-thinned BIT invoice, and run PR589's generic tuner passes.

All construction code is imported from main (research/e8-bit-p111, e8-bit-p111-tuned, e8-bit-carrier-skeleton);
nothing here changes it.  The invoice is rebuilt from research/query-thinned-controllers/BIT-CONTROLLER.json exactly as
research/bit-compact-productive-controller/price.py does, and the raw root is bracketed with that package's exact
outward-interval series (exact_series.py)."""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import copy, gzip, importlib.util, json, os, random, struct, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P111 = ROOT / "research/e8-bit-p111"
TUNED = ROOT / "research/e8-bit-p111-tuned/tune"
EXPORT = ROOT / "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
THIN = ROOT / "research/query-thinned-controllers/BIT-CONTROLLER.json"
SERIES = ROOT / "research/bit-compact-productive-controller/exact_series.py"
for p in (P111 / "code", TUNED):
    sys.path.insert(0, str(p))
import gen_p3  # noqa: E402
from geom import Geom  # noqa: E402
from planio import load_plan  # noqa: E402
from wordkit import save  # noqa: E402
import wlib  # noqa: E402

PLAN = P111 / "data/plan-l3.json"
SHIPPED = json.loads((P111 / "data/punct.json").read_text())
PR589_LOCAL = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}
COMPACT_LOCAL = {1: 1319, 2: 1342, 3: 78, 4: 39, 5: 102, 6: 10, 7: 18}
COMPACT_HELPERS = {4: 4, 8: 432}


def need(c, m):
    if not c:
        raise ValueError(m)


def _load(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


X = _load(SERIES, "h8_exact_series")
_G = _sol = None
_plans = {}


def build(P, seed, rcvsel=None, nodeopt=2000, node_seed=0):
    """gen_p3.make with retries on missing block carriers (as gen_p3's own __main__); returns the word or None."""
    global _G, _sol
    if _G is None:
        _G, _sol = Geom(), load_plan(str(PLAN))
    if seed not in _plans:
        _plans[seed] = gen_p3.plan_thirds(_G, _sol, random.Random(seed))
    pt = _plans[seed]
    if pt[0] == "failed":
        return None
    freeline, assign = pt
    gen_p3.NODEOPT[0] = nodeopt
    extras = {}
    for _ in range(20):
        try:
            res = gen_p3.build(_G, _sol, sorted(P), freeline, assign, extras=extras, node_seed=node_seed,
                               verbose=False, rcvsel=rcvsel)
        except AssertionError:
            return None
        if res[0] != "missing":
            return res[1]
        for B, ls in res[1].items():
            extras[B] = sorted(set(extras.get(B, [])) | set(ls))
    return None


def profile(word):
    """Local paid MOVE+COPY rank histogram of the exported records (export_records.py of PR #493)."""
    with tempfile.TemporaryDirectory() as d:
        wp = os.path.join(d, "w.json.gz")
        save(word, wp)
        subprocess.run([sys.executable, "-I", "-B", str(EXPORT), wp, os.path.join(d, "rec")], check=True,
                       stdout=subprocess.DEVNULL)
        raw = open(os.path.join(d, "rec", "249-records.bin"), "rb").read()
    h = Counter()
    for t in struct.iter_unpack("<6i", raw):
        if t[0] == 0 and t[4] > 0:
            h[t[4]] += 1
        elif t[0] == 2:
            h[t[5]] += 1
    return dict(sorted(h.items()))


def invoice(local, helpers):
    """p16 invoice with the local paid profile and helper target widths replaced, as #4760's price.invoice()."""
    row = json.loads(THIN.read_bytes())["invoice"]
    calls = row["thick_calls"]
    targets = Counter({int(k): v for k, v in row["targets"].items()})
    paid = Counter({int(k): v for k, v in row["paid"].items()})
    targets[8] -= calls * 439
    for k, n in helpers.items():
        targets[k] += calls * n
    for k, n in PR589_LOCAL.items():
        paid[k] -= calls * n
    for k, n in local.items():
        paid[k] += calls * n
    need(all(v >= 0 for v in targets.values()) and all(v >= 0 for v in paid.values()), "negative job count")
    return {k: v for k, v in sorted(targets.items()) if v}, {k: v for k, v in sorted(paid.items()) if v}


def raw_root(local, helpers=None, digits=15):
    """Bracket the raw crossing sum T r^(1-k) = sum P r^(1-k) on a 10^-digits grid; exact outward intervals."""
    T, P = invoice(local, helpers or {8: 439})

    def above(k):  # T moment strictly larger than P moment at t = 1 - k: k is below the root
        t = X.moment(T, 1 - k)
        p = X.moment(P, 1 - k)
        if t[0] > p[1]:
            return True
        if t[1] < p[0]:
            return False
        raise ValueError("interval too wide")

    def fgap(k):  # float guess only; the bracket below is decided by the exact intervals
        return sum(n * r ** (1 - k) for r, n in T.items()) - sum(n * r ** (1 - k) for r, n in P.items())

    a, b = 0.003, 0.004
    for _ in range(80):
        m = (a + b) / 2
        a, b = (m, b) if fgap(m) > 0 else (a, m)
    S = 10 ** digits
    lo = F(int(a * S), S)
    hi = lo + F(1, S)
    for _ in range(4):  # the float guess is within a grid step or two; anything else is an error
        if not above(lo):
            lo, hi = lo - F(1, S), lo
        elif above(hi):
            lo, hi = hi, hi + F(1, S)
        else:
            return lo, hi
    raise ValueError("float guess does not bracket the exact root")


def tune(base):
    """PR589's generic tuner passes (transports, Steinberg 3->2, frame reassignment, A and B) to a fixed point."""
    import tune as T
    Tn = T.Tuner(base, a=0.001733)
    moves = 0
    for _ in range(6):
        n = 0
        for ch in "TSF":
            for sec in "AB":
                V = Tn.view(sec)
                n += len(T.transport_sweep(V, verbose=False) if ch == "T" else
                         T.steinberg_sweep(V, verbose=False) if ch == "S" else
                         T.transport_sweep(V, verbose=False, allow_move=False))
        moves += n
        if not n:
            break
    w = Tn.word()
    w["C"] = wlib.rebuild_C(w)
    return w, moves


def apply_moves(base, moves):
    """apply.py of e8-bit-p111-tuned without its base-hash pin; every moved summand, gate and frame is still checked."""
    A = base["A"]
    rm, ins = {}, {}
    for m in moves:
        f, d, ss = A[m["gate"]]
        need(d == m["dst"] and m["src"] in ss and f == m["from_frame"] and len(ss) > 1, "move " + m["name"])
        rm.setdefault(m["gate"], []).append(m["src"])
        ins.setdefault(m["before_gate"], []).append([m["to_frame"], m["dst"], [m["src"]]])
    newA = []
    for i, (f, d, ss) in enumerate(A):
        newA += [copy.deepcopy(g) for g in ins.get(i, [])]
        newA.append([f, d, [s for s in ss if s not in rm.get(i, [])]])
    w = copy.deepcopy(base)
    w["A"] = newA
    w["C"] = wlib.rebuild_C(w)
    wlib.paid(w)  # nested frames and exact F2 endpoint on every column
    return w


def shipped(receivers=None):
    """PR555's frozen generator parameters, optionally with some receiver choices changed."""
    sel = {int(k): v for k, v in SHIPPED["receivers"].items()}
    sel.update(receivers or {})
    return sorted(SHIPPED["punctured"]), SHIPPED["thirds_seed"], sel, SHIPPED["nodeopt"]


def canon_gz(path):
    return json.loads(gzip.decompress(Path(path).read_bytes()))
