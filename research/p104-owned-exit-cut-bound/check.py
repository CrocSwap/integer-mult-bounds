#!/usr/bin/env python3
"""Exact checks for the owned-exit cut bound.  Python 3.12, standard library only.

Run:  python3 -I -B research/p104-owned-exit-cut-bound/check.py
Marker: PASS_P104_OWNED_EXIT_CUT_BOUND

Reads only two files next to this script: wB.json.gz (the native word of the 9|9 chain-nested root of #6833) and
certs.json (stored certificates).  Everything else is recomputed here in exact arithmetic.
"""
import collections
import gzip
import json
import os
import random
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
W_ = json.load(gzip.open(os.path.join(HERE, "wB.json.gz")))
CERTS = json.load(open(os.path.join(HERE, "certs.json")))


def par(x):
    return bin(x).count("1") & 1


def span(basis):
    s = {0}
    for v in basis:
        s |= {x ^ v for x in s}
    return frozenset(s)


def mask(S):
    m = 0
    for x in S:
        if x:
            m |= 1 << x
    return m


N = len(W_["initial"])
PORTS = W_["ports"]
SP = [span(b) for b in W_["frames"]]
SM = [mask(s) for s in SP]
DIM = [len(b) for b in W_["frames"]]
assert N == 772 and len(PORTS) == 104 and W_["public"] == N
PROG = W_["program"]


# ---------------------------------------------------------------- 1. the word obeys the frame law (replayed exactly)
def replay():
    """Checks H1-H4 on the program and returns the exact endpoint map T (sparse rows) and the owned lifetimes."""
    cur = {r: W_["initial"][r] for r in range(N)}
    val = {r: {r: Fr(1)} for r in range(N)}
    lives, cur_life = [], {}
    nmove_pub = nmove_own = nmove_own_up = 0
    for e in PROG:
        op = e[0]
        if op == "INIT":
            _, r, f = e
            assert r >= N and r not in cur
            cur[r] = f
            val[r] = {}
            lives.append([f])
            cur_life[r] = len(lives) - 1
        elif op == "CLEAR":
            _, r, f = e
            assert r >= N and cur[r] == f          # CLEAR may be dirty: no condition on the value
            del cur[r], val[r], cur_life[r]
        elif op == "MOVE":
            _, r, a, b = e[:4]
            assert cur[r] == a and a != b
            if r < N:                               # public: strictly up, nested
                assert SM[a] & ~SM[b] == 0 and SM[a] != SM[b]
                nmove_pub += 1
            else:                                   # owned: any direction allowed; counted as an event
                nmove_own += 1
                nmove_own_up += (SM[a] & ~SM[b] == 0)
                lives[cur_life[r]].append(b)
            cur[r] = b
        elif op in ("ADD", "COPY"):
            _, d, s, c, f = e
            assert cur[d] == f == cur[s] and d != s  # common frame
            c = Fr(c)
            if op == "COPY":
                assert d >= N and not val[d]        # into a zeroed owned register
            vd = val[d]
            for k, x in val[s].items():
                y = vd.get(k, 0) + c * x
                if y:
                    vd[k] = y
                else:
                    vd.pop(k, None)
        elif op == "SCALE":
            _, r, c, f = e
            c = Fr(c)
            assert cur[r] == f and c != 0
            val[r] = {k: c * x for k, x in val[r].items()}
        else:
            raise AssertionError(op)
    assert set(cur) == set(range(N)), "an owned register is live at exit"
    assert all(cur[r] == W_["final"][r] for r in range(N))
    return val, lives, nmove_pub, nmove_own, nmove_own_up


T, LIVES, NPUB, NOWN, NOWN_UP = replay()
print("frame law replayed: %d events, %d public MOVEs (all strictly ascending), %d owned MOVE events (%d ascending), "
      "%d owned lifetimes, no owned register live at exit" % (len(PROG), NPUB, NOWN, NOWN_UP, len(LIVES)))
assert NOWN == 24 and NOWN_UP == 0 and len(LIVES) == 47

# ---------------------------------------------------------------- 2. SPEC pins and the identity block T[Y_W, X_W] = I
X, Y = {}, {}
for p, q in enumerate(PORTS):
    assert par(q & q) == 1                          # odd weight
    xs = [W_["live"][p]]                           # X_p = live register p, Y_p = live register p + 112
    ys = [xs[0] + 112]
    perp = frozenset(v for v in range(512) if par(v & q) == 0)
    assert SP[W_["initial"][xs[0]]] == frozenset({0, q}) and SP[W_["final"][ys[0]]] == perp
    assert DIM[W_["initial"][ys[0]]] == 0
    X[p], Y[p] = xs[0], ys[0]
    assert T[Y[p]].get(Y[p]) == 1 and T[Y[p]].get(X[p]) == 1   # Y_p ends as y_p + x_p
    assert T[X[p]] == {X[p]: 1}                                 # X_p ends as x_p
assert len(set(X.values())) == 104 == len(set(Y.values()))
print("pins: X_p initial frame <q_p>, Y_p final frame q_p-perp, Y_p initial dim 0, T[Y_p,X_p] = 1 for all 104 ports")

# ---------------------------------------------------------------- 3. exits, cuts, cliques
PATHS = [[SM[f] for f in L] for L in LIVES]


def moves(paths):
    return [(a, b) for p in paths for a, b in zip(p, p[1:])]


def exits(mv, Q):
    return sum(1 for a, b in mv if a & Q and not b & Q)


def qmask(Q):
    m = 0
    for x in Q:
        m |= 1 << x
    return m


def A_of(W):
    return [x for x in range(1, 512) if all(par(x & q) for q in W)]


def is_clique(W):
    return all(par(a & b) for a in W for b in W)   # includes a = b: q.q = 1


def check_cert(W, Q):
    """Hypotheses of the corollary for (W,Q); returns |W|."""
    assert is_clique(W) and set(W) <= set(Q) and set(W) <= set(PORTS)
    assert all(par(x & q) for q in W for x in Q)    # Q inside A(W)
    return len(W)


BASE = moves(PATHS)
assert len(BASE) == 24
assert sum(abs(DIM[a] - DIM[b]) for p in LIVES for a, b in zip(p, p[1:])) == 56   # total owned dimension change

# the block of the corollary really is the identity: rows Y_W lie outside U_Q, columns X_W inside, T[Y_p,X_p'] = delta
cl = []
P = len(PORTS)
adj = [[par(a & b) if i != j else 0 for j, b in enumerate(PORTS)] for i, a in enumerate(PORTS)]   # simple graph


def bk(R, Pp, Xx):
    if not Pp and not Xx:
        cl.append(R)
        return
    piv = max(Pp + Xx, key=lambda u: sum(adj[u][v] for v in Pp))
    for v in [u for u in Pp if not adj[piv][u]]:
        bk(R + [v], [u for u in Pp if u != v and adj[v][u]], [u for u in Xx if adj[v][u]])
        Pp.remove(v)
        Xx.append(v)


sys.setrecursionlimit(10000)
bk([], list(range(P)), [])
sizes = sorted(collections.Counter(len(c) for c in cl).items())
print("maximal cliques of the port graph:", len(cl), sizes)
assert len(cl) == 1967 and sizes == [(4, 24), (5, 96), (6, 432), (7, 656), (8, 759)]

rng = random.Random(5)
tight = viol = 0
for Wi in cl:
    Wv = [PORTS[p] for p in Wi]
    for p in Wi:                                   # identity block T[Y_W, X_W] = I, endpoint frames as stated
        for p2 in Wi:
            assert T[Y[p]].get(X[p2], 0) == (1 if p == p2 else 0)
        assert SM[W_["initial"][X[p]]] & qmask(Wv) and not SM[W_["final"][Y[p]]] & qmask(Wv)
    A = [x for x in A_of(Wv) if x not in Wv]
    best = 10 ** 9
    for st in range(3):
        Q = set(Wv) | (set(A) if st == 1 else set())
        if st == 2:
            Q |= {x for x in A if rng.random() < .3}
        cur = exits(BASE, qmask(Q))
        check_cert(Wv, Q)
        best = min(best, cur)
        for _ in range(150):
            if not A:
                break
            x = rng.choice(A)
            Q2 = set(Q) ^ {x}
            if not set(Wv) <= Q2:
                continue
            e = exits(BASE, qmask(Q2))
            assert e >= len(Wv), "cut bound violated on wB"      # theorem
            if e <= cur:
                Q, cur = Q2, e
            best = min(best, cur)
    assert best >= len(Wv)
    tight += best == len(Wv)
print("wB: owned exits >= |W| on all 1967 maximal cliques (no violation); exits = |W| attained on %d / 1967" % tight)
assert tight == 1967

# ---------------------------------------------------------------- 4. one-unit end shortenings: stored certificates
def subspaces_between(A, B, d):
    da = len(A).bit_length() - 1
    db = len(B).bit_length() - 1
    if not da <= d <= db:
        return set()
    cur, k = {A}, da
    while k < d:
        nxt = set()
        for F in cur:
            for x in B:
                if x not in F:
                    nxt.add(frozenset(F | {y ^ x for y in F}))
        cur, k = nxt, k + 1
    return cur


FULL = frozenset(range(512))
POOL = [(CERTS["pool"][i]["W"], CERTS["pool"][i]["Q"]) for i in range(len(CERTS["pool"]))]
for W, Q in POOL:
    check_cert(W, Q)
stored = {(r["l"], r["end"], r["family"], F): c for r in CERTS["variants"] for F, c in r["cert"].items()}
used = set()
cnt = collections.Counter()
for (l, end, nF_core, nF_asc) in CERTS["records"]:
    fr = LIVES[l]
    ref = fr[1] if end == "top" else fr[-2]
    far = fr[0] if end == "top" else fr[-1]
    m = abs(DIM[far] - DIM[ref])
    dr = DIM[ref]
    if end == "top":
        core = subspaces_between(SP[ref], SP[far], DIM[far] - 1)
    else:
        core = subspaces_between(SP[far], SP[ref], DIM[far] + 1)
    core = {F for F in core if F != SP[far]}
    if m == 1:
        asc = set()
    elif end == "top":
        asc = subspaces_between(frozenset({0}), SP[ref], dr - m + 1) if dr - m + 1 >= 0 else set()
    else:
        asc = subspaces_between(SP[ref], FULL, dr + m - 1) if dr + m - 1 <= 9 else set()
    assert len(core) == nF_core and len(asc) == nF_asc, (l, end, len(core), len(asc))
    own = [p for k, p in enumerate(PATHS) if k != l]
    for fam, Fs in (("core", core), ("asc", asc)):
        for F in sorted(Fs, key=mask):
            if fam == "core" and m == 1:
                path = PATHS[l][1:] if end == "top" else PATHS[l][:-1]      # the hop is deleted
            elif end == "top":
                path = [mask(F)] + PATHS[l][1:]
            else:
                path = PATHS[l][:-1] + [mask(F)]
            ci = stored.pop((l, end, fam, "%x" % mask(F)))
            W, Q = POOL[ci]
            assert exits(moves(own + [path]), qmask(Q)) < len(W), (l, end, fam)   # fewer exits than the bound demands
            assert exits(BASE, qmask(Q)) == len(W)
            used.add(ci)
            cnt[fam] += 1
assert not stored
print("end shortenings of the 47 owned lifetimes (38 life/end records): core family %d variants, ascending-start family %d variants; "
      "every one carries a stored (W,Q) with exits < |W|; %d distinct certificates used" % (cnt["core"], cnt["asc"], len(used)))
assert cnt["core"] == 246 and cnt["asc"] == 547

# ---------------------------------------------------------------- 5. exact fuzz of the theorem on small frame models
import itertools


def subspaces(d):
    S = {frozenset({0})}
    for k in range(1, d + 1):
        for b in itertools.combinations(range(1, 2 ** d), k):
            S.add(span(b))
    return sorted(S, key=lambda s: (len(s), sorted(s)))


def rank(M):
    M = [r[:] for r in M if any(r)]
    rk = 0
    if not M:
        return 0
    for c in range(len(M[0])):
        p = next((i for i in range(rk, len(M)) if M[i][c] != 0), None)
        if p is None:
            continue
        M[rk], M[p] = M[p], M[rk]
        for i in range(len(M)):
            if i != rk and M[i][c] != 0:
                f = M[i][c] / M[rk][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[rk])]
        rk += 1
        if rk == len(M):
            break
    return rk


def run(seed, d, npub, steps, pubdown=False):
    R = random.Random(seed)
    FR = subspaces(d)
    up = lambda f: [g for g in FR if f < g]
    dn = lambda f: [g for g in FR if g < f]
    init = [R.choice(FR) for _ in range(npub)]
    val = {("p", u): [Fr(int(i == u)) for i in range(npub)] for u in range(npub)}
    fr = {("p", u): init[u] for u in range(npub)}
    owned, nid, ev = [], 0, []
    for _ in range(steps):
        k = R.random()
        regs = list(fr)
        if k < 0.2:                                  # public MOVE (up only, unless the control)
            x = ("p", R.randrange(npub))
            o = up(fr[x]) + (dn(fr[x]) if pubdown else [])
            if o:
                fr[x] = R.choice(o)
        elif k < 0.3 and len(owned) < 4:             # INIT owned (zero)
            nid += 1
            x = ("o", nid)
            owned.append(x)
            val[x] = [Fr(0)] * npub
            fr[x] = R.choice(FR)
        elif k < 0.5 and owned:                      # owned MOVE, either direction
            x = R.choice(owned)
            o = up(fr[x]) + dn(fr[x])
            if o:
                g = R.choice(o)
                ev.append((fr[x], g))
                fr[x] = g
        elif k < 0.55 and owned:                     # dirty CLEAR
            x = R.choice(owned)
            owned.remove(x)
            del fr[x], val[x]
        elif k < 0.6 and owned:                      # COPY into a zero owned register from a same-frame register
            z = [x for x in owned if all(v == 0 for v in val[x])]
            if z:
                x = R.choice(z)
                c = [y for y in fr if y != x and fr[y] == fr[x]]
                if c:
                    y = R.choice(c)
                    val[x] = [Fr(R.choice([1, -1, 2, Fr(1, 2)])) * v for v in val[y]]
        elif k < 0.65:                               # SCALE
            x = R.choice(regs)
            c = Fr(R.choice([-1, 2, Fr(1, 2), 3]))
            val[x] = [c * v for v in val[x]]
        else:                                        # ADD at a common frame
            byf = {}
            for x in regs:
                byf.setdefault(fr[x], []).append(x)
            pr = [v for v in byf.values() if len(v) > 1]
            if not pr:
                continue
            a, b = R.sample(R.choice(pr), 2)
            c = Fr(R.choice([1, -1, 2, -2, Fr(1, 2), 3]))
            val[a] = [x + c * y for x, y in zip(val[a], val[b])]
    for x in list(owned):                            # owned dead at exit
        del fr[x]
    pubs = [("p", u) for u in range(npub)]
    return init, [fr[x] for x in pubs], [val[x] for x in pubs], ev


def cutcheck(res, Qs):
    init, fin, Tm, ev = res
    npub = len(init)
    viol = tight = nz = 0
    for Q in Qs:
        hit = lambda f: any(x in f for x in Q)
        ex = sum(1 for a, b in ev if hit(a) and not hit(b))
        rows = [i for i in range(npub) if not hit(fin[i])]
        cols = [j for j in range(npub) if hit(init[j])]
        rk = rank([[Tm[i][j] for j in cols] for i in rows]) if rows and cols else 0
        viol += rk > ex
        tight += rk == ex and rk > 0
        nz += rk > 0
    return viol, tight, nz


def fuzz(d, nwords, ctrl=False):
    allQ = [[x for x in range(1, 2 ** d) if m >> (x - 1) & 1] for m in range(1, 2 ** (2 ** d - 1))] if d <= 3 else None
    V = Ti = Nz = 0
    R = random.Random(7)
    for s in range(nwords):
        res = run(s, d, R.randint(3, 6), R.randint(30, 90), pubdown=ctrl)
        Qs = allQ if allQ else [[x for x in range(1, 2 ** d) if R.random() < 0.35] or [1] for _ in range(300)]
        v, t, nz = cutcheck(res, Qs)
        V, Ti, Nz = V + v, Ti + t, Nz + nz
    return V, Ti, Nz


quick = "--quick" in sys.argv
n3, n4, nc = (300, 100, 100) if quick else (25000, 6000, 3000)
V3, T3, Z3 = fuzz(3, n3)
print("fuzz d=3 (all 127 cut sets Q), %d legal words: %d violations; %d nonzero-rank cuts, %d with rank = exits > 0" % (n3, V3, Z3, T3))
V4, T4, Z4 = fuzz(4, n4)
print("fuzz d=4 (300 random Q per word), %d legal words: %d violations; %d nonzero-rank cuts, %d tight" % (n4, V4, Z4, T4))
VC, TC, ZC = fuzz(3, nc, ctrl=True)
print("control, public MOVEs may descend (illegal), %d words: %d violations" % (nc, VC))
assert V3 == 0 and V4 == 0 and T3 > 0 and VC > 0
if not quick:
    assert (n3 + n4) == 31000
print("PASS_P104_OWNED_EXIT_CUT_BOUND")
