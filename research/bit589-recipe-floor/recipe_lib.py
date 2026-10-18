"""Shared code: scalar model of a nine-stage stage recipe, idle insertion, hosting windows, hosting programme and price.

A recipe is a list of stages; stage s carries (gap, pair, type): `gap` is None or one bridge (d, src, c) applied just
before the local, `type` is 'F' (forward local, side1 += side0) or 'R' (reverse local, side0 -= side1). Stage 0 has no
gap (a Levi before every local is a global basis change). Bridges after the last local are a free final Levi: they act
when every pair is already at level L-1 and touch no window. Idle children are inserted exactly when a level must rise
(before a local, before a bridge, and at the end in pair order), as in PR #463/#510 global_k.py; windows follow PR #442
hosting_core.windows (a bridge or local touching the pair closes its window).
Prepared by Ian Libânio with substantial AI assistance (Claude Opus 5.5, Anthropic, via Claude Code). Apache-2.0."""
import gzip, hashlib, importlib.util, json, math
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    # selected assembly input pin (research/community-frontier942-audit/ASSEMBLY.json input_sha256["engines/moment.py"])
    'research/e8-bit-carrier-skeleton/code/hub/e8-r740-replica32/code/engines/moment.py':
        '81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482',
    # PR #589 supplier record (local paid profile, c, frozen nine-stage remainder source)
    # (= the selected assembly input pin "package:inputs/PR589-EXPECTED.json")
    'research/e8-bit-p111-tuned/tune/EXPECTED.json': 'b9f0e5ca038abe837b0007c8fe006f366a6f02009244ac57705a8a200e2301f4',
    'research/e8-bit-p111-tuned/data/selection9-p111.json': '4ab1ed4529683cd184987f8bc3031fb7408b9cd22c25ab9cf541a8aaf896eaf1',
    'research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py':
        '6368196a393ac25bb2918880e4c4bd31ed733b762c27b6873ab391cbc0c5c3c8',
    'research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/hosting_k.py':
        '081c3b95b18d900d97ce82af64fb428f085b6adc6d8ca93ea920797dad7eb81e',
    'research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/idle-axis-hosting/hosting_core.py':
        'd8b90cd5d152df3c7c351230863d9e61816ad5e1f21d69bea1a86a5daad559a3',
}
H, M9, T = 8, 64, 32


def sha(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def load(rel, name):
    sp = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod); return mod


def moment_engine():
    rel = 'research/e8-bit-carrier-skeleton/code/hub/e8-r740-replica32/code/engines/moment.py'
    assert sha(rel) == PINS[rel], 'moment engine differs from the selected assembly pin'
    return load(rel, 'pinned_moment')


def check_pins():
    bad = {rel: sha(rel) for rel, want in PINS.items() if sha(rel) != want}
    assert not bad, ('pinned inputs differ', bad)
    return dict(PINS)


def official_hosting():
    """the vendored PR #510/#545 hosting_k (PR #442 programme with host_all / max_remainder), imported unchanged"""
    return load('research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/hosting_k.py',
                'official_hosting_k')


def pr589():
    e = json.loads((ROOT / 'research/e8-bit-p111-tuned/tune/EXPECTED.json').read_text())
    w = e['word']
    return dict(v=w['v'], R=w['R'], cst=w['decoder_constant'], local={int(r): n for r, n in w['local_histogram'].items()},
                c=Q(e['nine']['bit_lower']), profile={int(r): n for r, n in e['nine']['profile'].items()},
                rank_mass=w['legality']['rank_mass'])


def template_recipe(K):
    """recipe(K) of the vendored global_k.py, extracted by AST and executed alone (the module needs the parent tree)."""
    import ast
    rel = 'research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py'
    src = (ROOT / rel).read_text(); tree = ast.parse(src)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'recipe')
    ns = {}; exec(compile(ast.Module(body=[fn], type_ignores=[]), rel, 'exec'), ns)
    return ns['recipe'](K)


def from_template(events, K):
    """global_k recipe events -> (stages, final_bridges) in this module's format; asserts the template has one bridge per gap."""
    stages = []; pending = []; final = []
    for e in events:
        if e['kind'] == 'local':
            assert e['stage'] == len(stages) and len(pending) <= 1
            stages.append((pending[0] if pending else None, e['pair'], 'R' if e['reverse'] else 'F')); pending = []
        elif e['kind'] == 'bridge':
            pending.append((e['dst'], e['src'], e['coefficient']))
    final = pending
    assert stages[0][0] is None
    return stages, final


# ---------- scalar model (exact integers, row operations) ----------
def ident(K):
    return tuple(tuple(int(i == j) for j in range(2 * K)) for i in range(2 * K))


def addrow(P, i, j, c):
    P = list(P); P[i] = tuple(a + c * b for a, b in zip(P[i], P[j])); return tuple(P)


def local(P, K, p, ty):
    return addrow(P, K + p, p, 1) if ty == 'F' else addrow(P, p, K + p, -1)


def bridge(P, K, d, s, c):
    P = list(P)
    rd = tuple(a + c * b for a, b in zip(P[d], P[s])); rs = tuple(a - c * b for a, b in zip(P[K + s], P[K + d]))
    P[d] = rd; P[K + s] = rs; return tuple(P)


def exchange(P, K):
    P = list(P)
    for j in range(K):
        P[j], P[K + j] = P[K + j], tuple(-x for x in P[j])
    return tuple(P)


def antidiagonal(P, K):
    return all(P[i][j] == 0 for i in range(K) for j in range(K)) and \
        all(P[i][j] == 0 for i in range(K, 2 * K) for j in range(K, 2 * K))


def gap_bridges(g):
    """a gap is None, one bridge (d, src, c), or a list of bridges"""
    if g is None: return []
    return [tuple(g)] if isinstance(g[0], int) else [tuple(b) for b in g]


def product(stages, K, final=()):
    P = ident(K)
    for g, p, ty in stages:
        for b in gap_bridges(g): P = bridge(P, K, *b)
        P = local(P, K, p, ty)
    for g in final: P = bridge(P, K, *g)
    return P


def rank(rows):
    """exact integer rank (fraction-free elimination)"""
    A = [list(r) for r in rows]; n = len(A); m = len(A[0]); r = 0; prev = 1
    for c in range(m):
        piv = next((i for i in range(r, n) if A[i][c]), None)
        if piv is None: continue
        A[r], A[piv] = A[piv], A[r]
        for i in range(r + 1, n):
            A[i] = [(A[r][c] * A[i][j] - A[i][c] * A[r][j]) // prev for j in range(m)]
        prev = A[r][c]; r += 1
        if r == n: break
    return r


def invariants(P, K):
    """(mu, mu', nu, nu') of PROOF.md for the current product P"""
    P00 = [P[i][:K] for i in range(K)]; P01 = [P[i][K:] for i in range(K)]
    P10 = [P[i][:K] for i in range(K, 2 * K)]; P11 = [P[i][K:] for i in range(K, 2 * K)]
    return K - rank(P10), K - rank(P11), K - rank(P00), K - rank(P01)


# ---------- idle insertion and windows ----------
def schedule(stages, K):
    """events with idle children inserted when a level must rise; final idle in pair order (global_k's s == 2K branch)"""
    L = 2 * K + 1; lev = [-1] * K; out = []; idx = 0
    def adv(p, to):
        nonlocal idx
        if lev[p] < to:
            out.append(dict(kind='idle', pair=p, rank=7 * (to - lev[p]), idx=idx)); idx += 1; lev[p] = to
    for s, (g, p, ty) in enumerate(stages):
        for d, src, _ in gap_bridges(g):              # several bridges in one gap: synchronised one by one, in order
            t = max(lev[d], lev[src]); adv(d, t); adv(src, t)
            out.append(dict(kind='bridge', dst=d, src=src))
        assert lev[p] <= s - 1, 'a pair cannot be above the level its local needs'
        adv(p, s - 1); out.append(dict(kind='local', stage=s, pair=p)); lev[p] = s
    for p in range(K): adv(p, L - 1)
    return out


def windows(sched):
    """PR #442 hosting_core.windows, reimplemented: stages of other-pair locals strictly between the pair's last touch and
    the idle child"""
    last = {}; out = {}; locs = []
    for pos, e in enumerate(sched):
        k = e['kind']
        if k == 'local': locs.append((pos, e['stage'], e['pair'])); last[e['pair']] = pos
        elif k == 'bridge': last[e['dst']] = pos; last[e['src']] = pos
        else:
            p = e['pair']; lo = last.get(p, -1)
            out[e['idx']] = (p, e['rank'], frozenset(s for q, s, pp in locs if lo < q < pos and pp != p))
    return out


def structure_key(win):
    return tuple(sorted((r, tuple(sorted(st))) for (_, r, st) in win.values()))


# ---------- hosting programme and price ----------
def f(r, m=M9):
    return r * math.log(m / r) if r else 0.0


def host(win, L, copies, R, m=M9, maxrem=45, time_limit=120):
    """Exact integer programme, PR #442 objective with every residual hosted (0 banks, as PR #589) and every paid
    remainder <= maxrem (halving depth 2, row 18,355 < 20,161). Width 8 for every helper (PR #589 has entrance total 0).
    Returns (remainder Counter per replica, proxy cost) or None if infeasible."""
    import numpy as np
    from scipy.optimize import milp, LinearConstraint, Bounds
    var = []
    for i, (p, r, st) in win.items():
        for k in range(r // 8 + 1):
            if r - 8 * k <= maxrem: var.append(('y', i, k))
        for s in st: var.append(('z', i, s))
    if not var: return None
    n = len(var)
    c = np.array([f(win[v[1]][1] - 8 * v[2], m) if v[0] == 'y' else 0.0 for v in var])
    A = []; lo = []; hi = []
    for i in win:
        A.append([1.0 if v[0] == 'y' and v[1] == i else 0.0 for v in var]); lo.append(copies); hi.append(copies)
        A.append([float(v[2]) if v[0] == 'y' and v[1] == i else (-1.0 if v[0] == 'z' and v[1] == i else 0.0) for v in var])
        lo.append(0); hi.append(0)
    for s in range(L):
        A.append([1.0 if v[0] == 'z' and v[2] == s else 0.0 for v in var]); lo.append(R); hi.append(R)
    res = milp(c, constraints=LinearConstraint(np.array(A), lo, hi), integrality=np.ones(n),
               bounds=Bounds(np.zeros(n), np.full(n, np.inf)), options=dict(time_limit=time_limit))
    if res.x is None or res.status != 0: return None
    rem = Counter(); hosted = 0
    for v, x in zip(var, res.x):
        x = int(round(x))
        if v[0] == 'y' and x:
            hosted += v[2] * x
            if win[v[1]][1] - 8 * v[2]: rem[win[v[1]][1] - 8 * v[2]] += x
    assert hosted == L * R
    return rem, sum(f(r, m) * k for r, k in rem.items())


def global_profile(local_hist, rem, L, T=T):
    P = Counter({r: L * T * n for r, n in local_hist.items()})
    for r, n in rem.items(): P[r] += T * n
    return dict(sorted(P.items()))


def price(engine, P, K, L, v, cst, T=T):
    m = 1 + 7 * L; W = T * 2 * K * v
    mass = sum(r * n for r, n in P.items())
    assert m * W - mass == T * (2 * K * v - L * cst), 'rank-mass identity T(2Kv - L cst) fails'
    assert 2 * max(P) ** 2 < m ** 2, 'halving depth 2 fails'
    out = engine.certify(P, m, W, True)
    return Q(out['lower']), Q(out['upper'])
