#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact replay of 20 swap-then-delete composites and one exact-zero-join fix on the #7637 word.

Standard library only. Written for this package; it imports no other package and runs no other author's code
(the #7637 word, its invoice and its column-test pair records are vendored as data).

Modes (each is a separate VERIFY command): core, certificates, controls, columns1..columns4; all runs every mode.

core
  1. Vendored #7637 word (data/base-7637-word.json.gz) and new word (data/word.json.gz): sha256 pinned.
  2. Header (initial, final, frames, hosted, ports, live, owned_fields) identical.
  3. Interior: every MOVE/INIT/CLEAR and every ADD/COPY/SCALE at a chart of dimension 1..8 of the new word equals #7637's
     interior with the deletions and insertions of data/edits.json (composites C1..C20 and the zero-join fix Z1), event for
     event and in order. Everything else (ADD/SCALE at the {0} chart and at V) is the re-derived joint hub.
  4. Both words replayed over the rationals from arbitrary inputs with full legality checks. All 1,569 rows and end charts
     equal #7637's; helpers end at identity; owned rows empty; owned MOVE multiset unchanged; owned lifetimes unchanged except
     one more (the Z1 split), peak 50, the same labels (52 of the 68 allocated). The new word has no exact-zero join (the base has two).
  5. Routes: exactly the 40 helpers h1,h2 of C1..C20 change chains, each from route_before to route_after; new MOVE pairs strictly nested.
  6. Coefficients 5-smooth; grid statistics printed.
  7. Complete invoice (17 native calls), S and kappa recomputed; #7637's crossing reproduced.
certificates  exact CLEAR certificates for all 234 CLEARs of the new word (#7620's verify_certificates rule), 2 rejecting controls.
controls      negative controls rejected; 2 positives accepted.
columns1..4   column tests on the census (sorted index mod 4): 512 forward + 512 adjoint exact Gaussian columns, signed Pauli
              action, absolute phase, exact ascent rank, wrong-phase rejection; rejecting controls.
"""
import collections
import multiprocessing
import copy
import decimal
import gzip
import hashlib
import json
import os
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / 'data'
BASE_SHA256 = 'd7eb204bb24b2e1b5a3e4ebc282d346a4706ddd738004929d1e9ac345085a79a'
WORD_SHA256 = 'de43ed04f58133eaef8f8d12a9dae1e6e8aa7f9721044200cc839673d86fd7c1'
CALLS = 17
NPARTS = 4
NCOMP = 20
CLAIM, ABOVE = '0.0037136318149', '0.0037136318150'
DELTA_PAID = {2: -16, 3: -5, 4: -16, 6: 14, 9: 3}
CTRL_MOVE, CTRL_RELABEL, CTRL_COEF, CTRL_FLAG, CTRL_RETAKE = ('C1', 'C10', 'C20'), ('C1', 'C7'), ('C2', 'C9'), 'C3', 'C5'



def require(cond, label):
    if not cond:
        raise AssertionError(label)


def load_gz(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def span(vectors):
    s = {0}
    for v in vectors:
        require(type(v) is int and 0 < v < 512 and v not in s, 'frame vectors independent in F2^9')
        s |= {x ^ v for x in s}
    return frozenset(s)


def mains(W):
    live = set(W['live'])
    return live | {r + 112 for r in live} | set(W['hosted']['X2']) | set(W['hosted']['Y2'])


def replay(W):
    """Exact replay; returns rows, end charts, MOVE chains and owned data. Raises on any illegality."""
    n, N = W['public'], W['public'] + W['owned_fields']
    sp = [span(f) for f in W['frames']]
    rows = [{r: Q(1)} if r < n else {} for r in range(N)]
    cur = list(W['initial']) + [None] * W['owned_fields']
    alive, chains, owned_moves = set(), collections.defaultdict(list), collections.Counter()
    lifetimes, peak = collections.Counter(), 0
    init_chart = {}
    stats = dict(max_den_exp=0, odd_den=1, max_num_bits=0, smooth=True)

    def note(q):
        d = q.denominator
        e = (d & -d).bit_length() - 1
        stats['max_den_exp'] = max(stats['max_den_exp'], e)
        odd = d >> e
        o = odd
        for p in (3, 5):
            while o % p == 0:
                o //= p
        if o != 1:
            stats['smooth'] = False
        if odd > 1 and stats['odd_den'] % odd:
            stats['odd_den'] = stats['odd_den'] * odd // __import__('math').gcd(stats['odd_den'], odd)
        stats['max_num_bits'] = max(stats['max_num_bits'], abs(q.numerator).bit_length())

    for i, e in enumerate(W['program']):
        op, r = e[0], e[1]
        require(type(r) is int and 0 <= r < N, '%d register index' % i)
        if op == 'MOVE':
            a, b, flag = e[2], e[3], e[4]
            require(type(flag) is bool and flag == (r >= n), '%d MOVE ownership flag' % i)
            require(cur[r] == a, '%d MOVE from the current chart' % i)
            if r >= n:
                require(r in alive, '%d owned MOVE on a live field' % i)
                require(sp[a] < sp[b] or sp[b] < sp[a], '%d owned MOVE nested' % i)
                owned_moves[(a, b)] += 1
            else:
                require(sp[a] < sp[b], '%d public MOVE strictly ascends' % i)
            cur[r] = b
            chains[r].append((a, b))
        elif op == 'INIT':
            require(r >= n and r not in alive and len(e) == 3, '%d INIT of a dead owned field' % i)
            alive.add(r); rows[r] = {}; cur[r] = e[2]; init_chart[r] = e[2]
            peak = max(peak, len(alive))
        elif op == 'CLEAR':
            require(r >= n and r in alive and cur[r] == e[2], '%d CLEAR at the current chart' % i)
            lifetimes[(r, init_chart.pop(r), e[2])] += 1
            alive.discard(r); rows[r] = {}; cur[r] = None
        elif op == 'SCALE':
            q = Q(e[2])
            require(q != 0, '%d SCALE by zero' % i)
            require(cur[r] == e[3] and (r < n or r in alive), '%d SCALE chart' % i)
            rows[r] = {k: v * q for k, v in rows[r].items()}
            for v in rows[r].values():
                note(v)
        elif op in ('ADD', 'COPY'):
            s, q, f = e[2], Q(e[3]), e[4]
            require(type(s) is int and 0 <= s < N and s != r, '%d operand' % i)
            require(q != 0, '%d zero coefficient' % i)
            require(cur[r] == f and cur[s] == f, '%d ADD/COPY operands at chart %d' % (i, f))
            for x in (r, s):
                require(x < n or x in alive, '%d owned field live' % i)
            if op == 'COPY':
                require(not rows[r], '%d COPY into a zero field' % i)
            R = rows[r]
            for k, v in rows[s].items():
                nv = R.get(k, 0) + q * v
                if nv:
                    R[k] = nv
                    note(nv)
                else:
                    R.pop(k, None)
        else:
            raise AssertionError('%d unknown op %r' % (i, op))
    require(not alive, 'every owned field cleared')
    require(cur[:n] == list(W['final']), 'public fields end at final charts')
    return dict(rows=rows, cur=cur, chains=chains, owned_moves=owned_moves,
                lifetimes=lifetimes, peak=peak, sp=sp, stats=stats)


def crossing(T, P, digits=40):
    """Root of F(C) = sum (T_r - P_r) r^(1-C) on [0.003, 0.0045] by bisection in 80-digit decimals."""
    D = decimal.Decimal
    with decimal.localcontext(decimal.Context(prec=digits + 40)) as ctx:
        ranks = sorted({int(r) for r in T} | {int(r) for r in P})
        terms = [(D(T.get(str(r), 0) - P.get(str(r), 0)) * r, D(r).ln()) for r in ranks]

        def F(C):
            return sum((c * (-C * l).exp() for c, l in terms), D(0))
        lo, hi = D('0.003'), D('0.0045')
        require(F(lo) > 0 > F(hi), 'crossing bracketed')
        for _ in range(160):
            mid = (lo + hi) / 2
            if F(mid) > 0:
                lo = mid
            else:
                hi = mid
    return decimal.Context(prec=digits).create_decimal(lo)


def invoice_json(P, T):
    return {'schema': 'integer-mult-recursive-invoice/v1',
            'contract': {'model': 'mixed-target-unnormalized-power-v1',
                         'rank_semantics': 'H_r costs r^(1-C); debit surrendered productive fields',
                         'ambient_rank': 145,
                         'boundary': 'complete signed #7113 caller application with 17 native calls'},
            'paid': {k: P[k] for k in sorted(P, key=int)},
            'targets': {k: T[k] for k in sorted(T, key=int)}}


def clears(W):
    """Row content erased at every owned CLEAR, in program order."""
    n = W['public']
    rows = [{r: Q(1)} if r < n else {} for r in range(n + W['owned_fields'])]
    out = []
    for e in W['program']:
        op, r = e[0], e[1]
        if op == 'INIT':
            rows[r] = {}
        elif op == 'CLEAR':
            out.append((r, tuple(sorted(rows[r].items()))))
            rows[r] = {}
        elif op == 'SCALE':
            rows[r] = {k: v * Q(e[2]) for k, v in rows[r].items()}
        elif op in ('ADD', 'COPY'):
            R = rows[r]
            for k, v in rows[e[2]].items():
                nv = R.get(k, 0) + Q(e[3]) * v
                if nv:
                    R[k] = nv
                else:
                    R.pop(k, None)
    return out



def literal_coeffs(program):
    return [Q(e[2]) for e in program if e[0] == 'SCALE'] + [Q(e[3]) for e in program if e[0] in ('ADD', 'COPY')]


def nondyadic(program):
    return sum(1 for q in literal_coeffs(program) if q.denominator & (q.denominator - 1))


# ---------------------------------------------------------------------------
# Column tests for every affected public chart pair (own implementation).
# A chart pair (a, b) is the operator F_a^dagger F_b of two nine-bit stabilizer
# frames (Gaussian-dyadic Clifford maps). For each pair this section (i) builds
# the circuit of F_a^dagger F_b directly from the frame definition, (ii) compiles
# it to the child recipe  monomial . Fourier^r . monomial  with r = dim b - dim a,
# (iii) requires the recipe and the direct circuit to agree in signed Pauli action
# and exact absolute phase, and (iv) compares all 512 forward and 512 adjoint
# Gaussian columns, then checks that a recipe with its absolute phase shifted is
# rejected. Gates: P (bit permutation), D (diagonal Z4 quadratic form),
# C (one Fourier line, (1+i)I/2 + (1-i)X/2), X (offset), phase (i^k).
# ---------------------------------------------------------------------------
NB = 9
FULL = 1 << NB


def par(x):
    return x.bit_count() & 1


def rank2(rows):
    piv = {}
    for x in rows:
        while x:
            b = x.bit_length() - 1
            if b not in piv:
                piv[b] = x
                break
            x ^= piv[b]
    return len(piv)


def tr(rows, n=NB):
    return tuple(sum(((rows[j] >> i) & 1) << j for j in range(n)) for i in range(n))


def mvec(rows, x):
    return sum(par(r & x) << i for i, r in enumerate(rows))


def minv(rows, n=NB):
    a = [r | (1 << (n + i)) for i, r in enumerate(rows)]
    for j in range(n):
        k = next(i for i in range(j, n) if a[i] >> j & 1)
        a[j], a[k] = a[k], a[j]
        for i in range(n):
            if i != j and a[i] >> j & 1:
                a[i] ^= a[j]
    require([r & ((1 << n) - 1) for r in a] == [1 << i for i in range(n)], 'binary inverse')
    return tuple(r >> n for r in a)


def extend(vecs, n=NB):
    out = []
    for x in list(vecs) + [1 << i for i in range(n)]:
        if rank2(out + [x]) > len(out):
            out.append(x)
    require(len(out) == n, 'basis extension')
    return tuple(out)


def qform(Qr, al, x):
    return (sum(al[i] for i in range(NB) if x >> i & 1)
            + 2 * sum(par((Qr[i] >> (i + 1)) & (x >> (i + 1))) for i in range(NB) if x >> i & 1)) % 4


def dagger(circ):
    out = []
    for g in reversed(circ):
        t = g[0]
        if t == 'P':
            out.append(('P', minv(g[1])))
        elif t == 'D':
            out.append(('D', g[1], tuple(-a % 4 for a in g[2])))
        elif t == 'C':
            out.append(('C', g[1], -g[2]))
        elif t == 'phase':
            out.append(('phase', -g[1] % 4))
        else:
            out.append(g)
    return tuple(out)


def fourier(r):
    return tuple(('C', 1 << i, 1) for i in range(r))


def frame_circuit(vecs):
    r = len(vecs)
    if r == 0:
        return ()
    if r == NB:
        return fourier(NB)
    G = tr(extend(vecs))
    gi = tr(minv(G))
    Qr = tuple((1 << i) ^ sum(par(a & b) << j for j, b in enumerate(gi)) for i, a in enumerate(gi))
    chart = (('P', G), ('D', Qr, tuple((row >> i) & 1 for i, row in enumerate(Qr))))
    return dagger(chart) + fourier(r) + chart


def tableau(circ):
    rows = [(1 << i, 0, 0) for i in range(NB)] + [(0, 1 << i, 0) for i in range(NB)]
    for g in circ:
        t = g[0]
        out = []
        it = tr(minv(g[1])) if t == 'P' else None
        for x, z, p in rows:
            if t == 'P':
                x, z = mvec(g[1], x), mvec(it, z)
            elif t == 'X':
                p += 2 * par(z & g[1])
            elif t == 'C':
                if par(z & g[1]):
                    x ^= g[1]
                    p += 3 * g[2]
            elif t == 'D':
                p += sum(g[2][i] for i in range(NB) if x >> i & 1)
                p += 2 * sum(par((g[1][i] >> (i + 1)) & (x >> (i + 1))) for i in range(NB) if x >> i & 1)
                z ^= mvec(g[1], x)
            else:
                require(t == 'phase', 'gate type')
            out.append((x, z, p % 4))
        rows = out
    return tuple(rows)


_ACT = {}


def dact(g):
    if g not in _ACT:
        _ACT[g] = tuple(qform(g[1], g[2], x) for x in range(FULL))
    return _ACT[g]


def rot(pr, k):
    a, b = pr
    return ((a, b), (-b, a), (-a, -b), (b, -a))[k % 4]


def column(circ, basis=0):
    """Exact Gaussian-dyadic column: ({address: (re, im)}, denominator exponent), value = num / 2^(den/2) ... ."""
    val, den = {basis: (1, 0)}, 0
    for g in circ:
        t = g[0]
        res = {}
        if t == 'C':
            d, s = g[1], g[2]
            for ad, (a, b) in val.items():
                for tg, pr in ((ad, (a - s * b, b + s * a)), (ad ^ d, (a + s * b, b - s * a))):
                    o = res.get(tg, (0, 0))
                    res[tg] = (o[0] + pr[0], o[1] + pr[1])
            den += 1
        else:
            for ad, pr in val.items():
                if t == 'P':
                    tg = mvec(g[1], ad)
                elif t == 'X':
                    tg = ad ^ g[1]
                elif t == 'D':
                    tg = ad
                    pr = rot(pr, dact(g)[ad])
                else:
                    require(t == 'phase', 'gate type')
                    tg = ad
                    pr = rot(pr, g[1])
                require(tg not in res, 'monomial map injective')
                res[tg] = pr
        val = {ad: pr for ad, pr in res.items() if pr != (0, 0)}
    while den and all((a | b) % 2 == 0 for a, b in val.values()):
        den -= 1
        val = {ad: (a // 2, b // 2) for ad, (a, b) in val.items()}
    return val, den


def monomial_circuit(rec):
    M, Qr, al = tuple(rec['matrix_rows']), tuple(rec['quadratic_rows']), tuple(rec['linear_Z4'])
    require(tr(Qr) == Qr and all(al[i] % 2 == (Qr[i] >> i) & 1 for i in range(NB)), 'diagonal form')
    minv(M)
    return (('D', Qr, al), ('P', M), ('X', rec['offset']), ('phase', rec['phase']))


def recipe_circuit(rec):
    if rec['rank'] == 0:
        return monomial_circuit(rec['left'])
    return monomial_circuit(rec['right']) + fourier(rec['rank']) + monomial_circuit(rec['left'])


# compiler: symplectic tableau algebra used to produce the recipe
def pmul(a, b):
    x, z, p = a
    y, w, q = b
    return x ^ y, z ^ w, (p + q + 2 * par(z & y)) % 4


def tapply(T, pa):
    x, z, ph = pa
    out = (0, 0, ph)
    for i in range(NB):
        if x >> i & 1:
            out = pmul(out, T[i])
    for i in range(NB):
        if z >> i & 1:
            out = pmul(out, T[NB + i])
    return out


def tcompose(A, B):
    return tuple(tapply(A, p) for p in B)


def tidentity():
    return tuple([(1 << i, 0, 0) for i in range(NB)] + [(0, 1 << i, 0) for i in range(NB)])


def tinverse(T):
    cols = [x | (z << NB) for x, z, p in T]
    ci = tr(minv(tr(cols, 2 * NB), 2 * NB), 2 * NB)
    out = []
    for j, w in enumerate(ci):
        x, z = w & (FULL - 1), w >> NB
        u, v, p = tapply(T, (x, z, 0))
        require((u, v) == tidentity()[j][:2], 'tableau inverse')
        out.append((x, z, -p % 4))
    return tuple(out)


class Op:
    def __init__(s, tab, circ):
        s.tab, s.circ = tab, tuple(circ)

    def then(s, o):
        return Op(tcompose(o.tab, s.tab), s.circ + o.circ)

    def dag(s):
        return Op(tinverse(s.tab), dagger(s.circ))


def op_perm(G):
    cols, gi = tr(G), minv(G)
    return Op(tuple([(a, 0, 0) for a in cols] + [(0, a, 0) for a in gi]), [('P', tuple(G))])


def op_diag(Qr, al=None):
    Qr = tuple(Qr)
    al = tuple(al) if al is not None else tuple((Qr[i] >> i) & 1 for i in range(NB))
    return Op(tuple([(1 << i, Qr[i], al[i]) for i in range(NB)] + [(0, 1 << i, 0) for i in range(NB)]), [('D', Qr, al)])


def op_c(q, s=1):
    return Op(tuple([(1 << i, 0, 0) for i in range(NB)]
                    + [(q if q >> i & 1 else 0, 1 << i, (3 * s) % 4 if q >> i & 1 else 0) for i in range(NB)]), [('C', q, s)])


def op_x(b):
    return Op(tuple([(1 << i, 0, 0) for i in range(NB)] + [(0, 1 << i, 2 * ((b >> i) & 1)) for i in range(NB)]), [('X', b)])


def op_id():
    return Op(tidentity(), [])


def op_four(axes):
    o = op_id()
    for i in axes:
        o = o.then(op_c(1 << i))
    return o


def op_had(axes):
    S = op_diag(tuple(1 << i if i in axes else 0 for i in range(NB)))
    return S.then(op_four(axes)).then(S)


def frame_op(vecs):
    r = len(vecs)
    if r == 0:
        return op_id()
    if r == NB:
        return op_four(range(NB))
    G = tr(extend(vecs))
    gi = tr(minv(G))
    Qr = tuple((1 << i) ^ sum(par(a & b) << j for j, b in enumerate(gi)) for i, a in enumerate(gi))
    K = op_perm(G).then(op_diag(Qr))
    return K.dag().then(op_four(range(r))).then(K)


def split_monomial(op):
    T = op.tab
    require(all(x == 0 and p % 2 == 0 for x, z, p in T[NB:]), 'monomial tableau')
    G = tr([x for x, z, p in T[:NB]])
    b = mvec(G, sum((p // 2) << i for i, (x, z, p) in enumerate(T[NB:])))
    cols = [mvec(tr(G), z) for x, z, p in T[:NB]]
    Qr = tr(cols)
    al = [(p - 2 * par(b & z)) % 4 for x, z, p in T[:NB]]
    out = op_diag(Qr, al).then(op_perm(G)).then(op_x(b))
    require(out.tab == T, 'monomial rebuilt')
    val, den = column(op.circ)
    require(den == 0 and all(v == (0, 0) for a, v in val.items() if a != b), 'monomial column')
    ph = [(1, 0), (0, 1), (-1, 0), (0, -1)].index(val[b])
    out = out.then(Op(tidentity(), [('phase', ph)]))
    return out, dict(matrix_rows=G, offset=b, quadratic_rows=Qr, linear_Z4=al, phase=ph)


def lower(op):
    Bc = [x for x, z, p in op.tab[NB:]]
    r = rank2(Bc)
    if not r:
        mon, rec = split_monomial(op)
        return dict(rank=0, left=rec, right=None)
    G = tr(extend(Bc))
    A = minv(G)
    PA = op_perm(A)
    part = op.then(PA)
    Bc = [x for x, z, p in part.tab[NB:]]
    Dc = [z for x, z, p in part.tab[NB:]]
    picks, sel = [], []
    for j, x in enumerate(Bc):
        if rank2(sel + [x]) > len(sel):
            picks.append(j)
            sel.append(x)
    require(len(picks) == r and all(x >> r == 0 for x in Bc), 'rank selection')
    Br = tr(sel, r)
    Bi = minv(Br, r)
    Dr = tr([Dc[j] & ((1 << r) - 1) for j in picks], r)
    Qs = tuple(sum(par(row & col) << j for j, col in enumerate(tr(Bi, r))) for row in Dr)
    DQ = op_diag(Qs + (0,) * (NB - r))
    V = part.then(DQ).then(op_had(range(r)))
    require(all(x == 0 for x, z, p in V.tab[NB:]), 'V monomial')
    Vm, _ = split_monomial(V)
    S = op_diag(tuple(1 << i if i < r else 0 for i in range(NB)))
    left = S.dag().then(DQ.dag()).then(PA.dag())
    right = Vm.then(S.dag()).then(op_x((1 << r) - 1))
    lm, lrec = split_monomial(left)
    rm, rrec = split_monomial(right)
    comp = rm.then(op_four(range(r))).then(lm)
    require(comp.tab == op.tab and column(comp.circ) == column(op.circ), 'recipe reproduces the pair operator')
    return dict(rank=r, left=lrec, right=rrec)


def pair_columns(frames, a, b, wrong_phase=True):
    """Full column test of the chart pair (a, b); returns its rank."""
    U, V = frames[a], frames[b]
    rec = lower(frame_op(U).dag().then(frame_op(V)))
    require(rec['rank'] == len(V) - len(U), 'exact public ascent rank of pair %s' % ((a, b),))
    expected = dagger(frame_circuit(U)) + frame_circuit(V)
    actual = recipe_circuit(rec)
    require(tableau(actual) == tableau(expected), 'signed Pauli action of pair %s' % ((a, b),))
    for x, y in ((actual, expected), (dagger(actual), dagger(expected))):
        for c in range(FULL):
            require(column(x, c) == column(y, c), 'Gaussian column %d of pair %s' % (c, (a, b)))
    if wrong_phase:
        bad = actual + (('phase', 1),)
        require(tableau(bad) == tableau(actual) and column(bad) != column(expected), 'wrong absolute phase rejected')
    return rec['rank']



# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Package-specific checks.
# ---------------------------------------------------------------------------
MODES = ('all', 'core', 'certificates', 'controls') + tuple('columns%d' % i for i in range(1, NPARTS + 1))
MODE = sys.argv[1] if len(sys.argv) > 1 else 'all'
require(MODE in MODES, 'mode is one of ' + ', '.join(MODES))
CALLER_EXTRA_PAID = {'1': 384, '8': 656, '9': 32, '16': 416, '24': 416, '32': 416, '40': 416, '48': 416, '56': 416, '64': 208}
CALLER_EXTRA_TARGETS = {'9': 416, '17': 416, '25': 416, '33': 416, '41': 416, '49': 416, '57': 416, '65': 416, '73': 208, '137': 208}


def load_words():
    base_raw = (DATA / 'base-7637-word.json.gz').read_bytes()
    require(hashlib.sha256(base_raw).hexdigest() == BASE_SHA256, 'vendored #7637 word bytes')
    word_raw = (DATA / 'word.json.gz').read_bytes()
    require(hashlib.sha256(word_raw).hexdigest() == WORD_SHA256, 'new word bytes')
    base = json.loads(gzip.decompress(base_raw))
    require(hashlib.sha256(gzip.decompress(base_raw)).hexdigest() == '8ab3d9dbe2e2e24202ac96c6122b010b3e7980912f935cc0cc2db2e9d85f83aa',
            "decompressed #7637 word has the candidate hash recorded in #7637's evidence")
    return base, json.loads(gzip.decompress(word_raw))


def interior_test(W):
    dim = [len(f) for f in W['frames']]

    def ok(e):
        if e[0] in ('ADD', 'COPY'):
            return 0 < dim[e[4]] < 9
        if e[0] == 'SCALE':
            return 0 < dim[e[3]] < 9
        return True
    return ok


def apply_interior(B, E):
    """#7637's interior subsequence with the listed deletions and insertions (inserts ordered by seq)."""
    ok, P = interior_test(B), B['program']
    dele, ins = {}, collections.defaultdict(list)
    allins = []
    for ed in E['edits']:
        for i, ev in ed['delete']:
            require(P[i] == ev and ok(ev) and i not in dele, '%s deletion %d matches an interior base event' % (ed['id'], i))
            dele[i] = ev
        allins.extend(ed['insert'])
    require(sorted(x['seq'] for x in allins) == list(range(len(allins))), 'insert sequence numbers')
    for x in sorted(allins, key=lambda x: x['seq']):
        require(ok(x['event']), 'insertion is interior')
        ins[x['before']].append(x['event'])
    keys, k, out = sorted(ins), 0, []
    for i, e in enumerate(P):
        if not ok(e):
            continue
        while k < len(keys) and keys[k] <= i:
            out.extend(ins[keys[k]])
            k += 1
        if i not in dele:
            out.append(e)
    for key in keys[k:]:
        out.extend(ins[key])
    return out, len(dele), sum(len(v) for v in ins.values())


def chain_route(RX, X, r):
    ch = RX['chains'].get(r, [])
    return [ch[0][0]] + [b for a, b in ch] if ch else [X['initial'][r]]


def routes_of(X):
    out = collections.defaultdict(list)
    for e in X['program']:
        if e[0] == 'MOVE' and e[1] < X['public']:
            out[e[1]].append((e[2], e[3]))
    return out


def move_pairs(X):
    return {(e[2], e[3]) for e in X['program'] if e[0] == 'MOVE'}


def public_move_pairs(X):
    return {(e[2], e[3]) for e in X['program'] if e[0] == 'MOVE' and e[1] < X['public']}


def native_counts(W):
    dim = [len(f) for f in W['frames']]
    paid = collections.Counter(abs(dim[e[3]] - dim[e[2]]) for e in W['program'] if e[0] == 'MOVE')
    M, n = mains(W), W['public']
    helpers = collections.Counter(dim[W['final'][r]] - dim[W['initial'][r]] for r in range(n) if r not in M)
    return paid, helpers


def diff(a, b):
    d = collections.Counter(b)
    d.subtract(a)
    return {k: v for k, v in sorted(d.items()) if v}


def zero_joins(W):
    """Exact-zero joins: an owned row that becomes exactly 0 after a non-INIT op and is written again (ADD from a nonzero
    operand) before its CLEAR. Returns [(field, event index where it became zero, event index of the refill)]."""
    n = W['public']
    rows = {r: {r: Q(1)} for r in range(n)}
    zero, joins = {}, []
    for t, e in enumerate(W['program']):
        op = e[0]
        if op == 'INIT':
            rows[e[1]] = {}
            zero.pop(e[1], None)
        elif op == 'CLEAR':
            rows.pop(e[1], None)
            zero.pop(e[1], None)
        elif op == 'ADD':
            x, y, q = e[1], e[2], Q(e[3])
            R = rows[x]
            if x in zero and any(rows[y].values()):
                joins.append((x, zero.pop(x), t))
            for k, v in rows[y].items():
                s = R.get(k, 0) + q * v
                if s:
                    R[k] = s
                else:
                    R.pop(k, None)
            if x >= n and not R:
                zero[x] = t
        elif op == 'SCALE':
            q = Q(e[2])
            rows[e[1]] = {k: q * v for k, v in rows[e[1]].items()}
            if q == 0 and e[1] >= n:
                zero[e[1]] = t
        elif op == 'COPY':
            rows[e[1]] = dict(rows[e[2]])
    return joins


def verify_certificates(W, certs):
    """#7620's verify_certificates rule at every CLEAR: erased row == sum of certificate coefficients times rows of live
    registers other than the cleared field, exactly. A zero row needs the empty certificate. Returns per-CLEAR sizes and failures."""
    n = W['public']
    rows = [{r: Q(1)} if r < n else {} for r in range(n + W['owned_fields'])]
    live, sizes, bad, seen = set(range(n)), [], [], 0
    for i, e in enumerate(W['program']):
        op, r = e[0], e[1]
        if op == 'INIT':
            live.add(r)
            rows[r] = {}
        elif op == 'CLEAR':
            seen += 1
            c = certs.get(str(i))
            okc = c is not None
            if okc:
                cert = {int(k): Q(v) for k, v in c.items()}
                okc = all(k in live and k != r for k in cert)
                s = {}
                for k, cf in cert.items():
                    for t, v in rows[k].items():
                        s[t] = s.get(t, 0) + cf * v
                okc = okc and {t: v for t, v in s.items() if v} == rows[r]
                sizes.append(len(cert))
            if not okc:
                bad.append(i)
            rows[r] = {}
            live.discard(r)
        elif op == 'SCALE':
            rows[r] = {k: v * Q(e[2]) for k, v in rows[r].items()}
        elif op != 'MOVE':
            R = rows[r]
            for k, v in rows[e[2]].items():
                nv = R.get(k, 0) + Q(e[3]) * v
                if nv:
                    R[k] = nv
                else:
                    R.pop(k, None)
    require(seen == len(certs), 'one certificate per CLEAR and no other')
    return sizes, bad


def certificates_section(B, W):
    certs = json.loads((DATA / 'clear-certificates.json').read_text())['clear_event_index']
    require(len(certs) == 234, '234 certificates')
    sizes, bad = verify_certificates(W, certs)
    require(not bad and len(sizes) == 234, 'every CLEAR certified (failures at %s)' % bad[:5])
    nz = sum(1 for s in sizes if s)
    cb, cw = clears(B), clears(W)
    same = sum(1 for a, b in zip(cb, cw) if a == b)
    print('PASS CLEAR certificates: all 234 CLEARs of the new word erase an exact combination of other live registers'
          ' (#7620 verify_certificates rule; %d nonzero rows, certificate sizes %d..%d; %d zero rows with the empty certificate);'
          ' %d of the base word\'s 233 CLEAR contents are unchanged in the new word, the rest change with the re-derived hub content'
          % (nz, min(s for s in sizes if s), max(sizes), 234 - nz, same))
    k = next(i for i, c in certs.items() if c)
    X = copy.deepcopy(certs)
    f0 = next(iter(X[k]))
    X[k][f0] = str(Q(X[k][f0]) + 1)
    require(int(k) in verify_certificates(W, X)[1], 'corrupted coefficient rejected')
    Y = copy.deepcopy(certs)
    r = W['program'][int(k)][1]
    Y[k][str(r)] = Y[k].pop(f0)
    require(int(k) in verify_certificates(W, Y)[1], 'cleared field as a term rejected')
    print('PASS certificate controls: corrupted coefficient (CLEAR at event %s) rejected; cleared field as a term rejected' % k)
    print('PASS_CERTIFICATES_ON_7637')


def changed_registers(B, W):
    rb, rw = routes_of(B), routes_of(W)
    return rb, rw, [r for r in range(W['public']) if rb[r] != rw[r]]


def census(B, W):
    """Column-test census. #7637 publishes no pair census, so the census is the set of chart pairs this word touches:
    every old- and new-route pair of the 40 changed helpers and every new MOVE pair; the 13 new pairs are among them."""
    rb, rw, changed = changed_registers(B, W)
    E = json.loads((DATA / 'edits.json').read_text())
    comps = [ed for ed in E['edits'] if 'h1' in ed]
    require(changed == sorted({r for ed in comps for r in (ed['h1'], ed['h2'])}) and len(changed) == 2 * NCOMP,
            'changed routes are exactly the 40 helpers of C1..C20')
    allp = {q for r in changed for q in rb[r] + rw[r]} | (move_pairs(W) - move_pairs(B))
    filep = {tuple(p) for p in json.loads((DATA / 'affected-pairs-new.json').read_text())}
    require(allp == filep and len(allp) == CENSUS_SIZE, 'census is %d pairs' % CENSUS_SIZE)
    require(move_pairs(W) - move_pairs(B) <= allp and len(move_pairs(W) - move_pairs(B)) == 13, 'all 13 new MOVE pairs are tested')
    return None, allp


CENSUS_SIZE = 223


def _pair_job(args):
    frames, a, b = args
    return (a, b, pair_columns(frames, a, b))


def columns_section(B, W, part):
    p0, allp = census(B, W)
    frames = [tuple(f) for f in W['frames']]
    mine = sorted(allp)[part::NPARTS]
    print('census: old and new route pairs of the 40 changed helpers plus the 13 new MOVE pairs = %d; part %d of %d tests %d pairs'
          % (len(allp), part + 1, NPARTS, len(mine)))
    jobs = [(frames, a, b) for a, b in mine]
    with multiprocessing.Pool(min(int(os.environ.get('CHECK_PROCS', '8')), multiprocessing.cpu_count())) as pool:
        done = pool.map(_pair_job, jobs, chunksize=4)
    require(len(done) == len(mine), 'all pairs of this part tested')
    print('PASS columns part %d: %d chart pairs x (512 forward + 512 adjoint) exact Gaussian columns = %d, signed Pauli action,'
          ' absolute phase, exact public ascent rank, wrong-phase rejection each' % (part + 1, len(done), len(done) * 1024))
    if part:
        return

    def col_rejected(label, mutate):
        try:
            mutate()
        except AssertionError as exc:
            print('PASS control rejected: %s (%s)' % (label, str(exc)[:70]))
            return
        raise AssertionError('control not rejected: ' + label)

    def non_nested():
        pair_columns(frames, 260, 128)
    require(not (span(frames[260]) < span(frames[128]) or span(frames[128]) < span(frames[260])), 'control pair is not nested')
    col_rejected('column test rejects the non-nested pair (260,128)', non_nested)
    exp_of = lambda a, b: dagger(frame_circuit(frames[a])) + frame_circuit(frames[b])
    newp = sorted(move_pairs(W) - move_pairs(B))
    for a, b in (newp[0], newp[-1]):
        def tampered_recipe(a=a, b=b):
            rec = lower(frame_op(frames[a]).dag().then(frame_op(frames[b])))
            rec['left']['offset'] ^= 1
            exp = exp_of(a, b)
            require(tableau(recipe_circuit(rec)) == tableau(exp) and column(recipe_circuit(rec), 0) == column(exp, 0), 'recipe column 0')
        col_rejected('column test rejects a (%d,%d) recipe with a shifted offset' % (a, b), tampered_recipe)

        def phase_only(a=a, b=b):
            rec = lower(frame_op(frames[a]).dag().then(frame_op(frames[b])))
            require(column(recipe_circuit(rec) + (('phase', 2),), 0) == column(exp_of(a, b), 0), 'recipe column 0 phase')
        col_rejected('column test rejects a (%d,%d) recipe with a global phase error' % (a, b), phase_only)


def run_controls(B, W):
    RB = replay(B)
    P0 = W['program']
    E = json.loads((DATA / 'edits.json').read_text())
    res = []

    def outcome(P, X0, initial=None):
        X = dict(X0)
        X['program'] = P
        if initial is not None:
            X['initial'] = initial
        try:
            R = replay(X)
        except AssertionError as ex:
            return 'illegal: ' + str(ex)
        if R['rows'] != RB['rows'] or R['cur'] != RB['cur']:
            return 'rows/end charts differ (%d rows)' % sum(a != b for a, b in zip(R['rows'], RB['rows']))
        return None

    def test(label, P, X0=W, expect_reject=True, initial=None):
        o = outcome(P, X0, initial)
        require((o is not None) == expect_reject, 'control %s: %s' % (label, 'ACCEPTED' if o is None else 'REJECTED ' + o))
        if expect_reject:
            res.append(1)
        print('PASS control %s: %s %s' % ('rejected' if expect_reject else 'accepted', label, '(%s)' % o[:80] if o else ''), flush=True)

    def ix(ev, P=P0):
        require(P.count(ev) == 1, 'control event present once: %r' % (ev,))
        return P.index(ev)

    def mod(f, base=P0):
        P = list(base)
        f(P)
        return P

    dim = [len(f) for f in W['frames']]
    ed = {e['id']: e for e in E['edits']}
    test('new word (positive)', P0, expect_reject=False)
    test('#7637 word itself (positive)', B['program'], B, expect_reject=False)

    def inserted_moves(cid):
        return [x['event'] for x in ed[cid]['insert'] if x['event'][0] == 'MOVE']
    for n, cid in enumerate(CTRL_MOVE, 1):
        mv = inserted_moves(cid)[0]
        test('%d %s inserted MOVE %s dropped' % (n, cid, mv), mod(lambda P, mv=mv: P.pop(ix(mv))))
    for n, cid in zip((4, 5), CTRL_RELABEL):
        pair = (ed[cid]['h1'], ed[cid]['h2'])
        adds = [x['event'] for x in ed[cid]['insert'] if x['event'][0] == 'ADD' and (x['event'][1] in pair or x['event'][2] in pair)]
        a = adds[-1]
        alt = list(a)
        j = 1 if a[1] in pair else 2
        alt[j] = pair[1] if a[j] == pair[0] else pair[0]
        test('%d %s inserted ADD %s with the swapped register undone %s' % (n, cid, a, alt), mod(lambda P, a=a, alt=alt: P.__setitem__(ix(a), alt)))
    for n, cid in zip((6, 7), CTRL_COEF):
        a = next(x['event'] for x in ed[cid]['insert'] if x['event'][0] == 'ADD')
        alt = list(a)
        alt[3] = str(-Q(a[3]))
        test('%d %s inserted ADD %s coefficient negated' % (n, cid, a), mod(lambda P, a=a, alt=alt: P.__setitem__(ix(a), alt)))
    mv = inserted_moves(CTRL_FLAG)[0]
    test('8 %s inserted MOVE with ownership flag True' % CTRL_FLAG, mod(lambda P: P.__setitem__(ix(mv), mv[:4] + [True])))
    v_add = next(i for i, e in enumerate(P0) if e[0] == 'ADD' and dim[e[4]] == 9)
    z_add = next(i for i, e in enumerate(P0) if e[0] == 'ADD' and dim[e[4]] == 0)
    test('9 first V-mix ADD coefficient doubled', mod(lambda P: P.__setitem__(v_add, P[v_add][:3] + [str(2 * Q(P[v_add][3]))] + P[v_add][4:])))
    test('10 first {0}-prefix ADD dropped', mod(lambda P: P.pop(z_add)))
    old_first = next(e for i, e in ed[CTRL_RETAKE]['delete'] if e[0] == 'MOVE' and e[2] == 3)
    mv = next(x['event'] for x in ed[CTRL_RETAKE]['insert'] if x['event'][0] == 'MOVE' and x['event'][2] == 3)
    test('11 %s stay re-taken: MOVE %s replaced by %s' % (CTRL_RETAKE, mv, old_first), mod(lambda P: P.__setitem__(ix(mv), old_first)))
    Bp = B['program']

    def bare(P):
        for i, ev in sorted(ed['C1']['delete'], reverse=True):
            require(P[i] == ev, 'C1 event in #7637')
            del P[i]
    test('12 C1 deletions applied to #7637 without the relabel and without hub re-settle', mod(bare, Bp), B)
    test('13 one C4 deletion alone applied to #7637', mod(lambda P: P.pop(ed['C4']['delete'][0][0]), Bp), B)
    test('14 last event of the new word dropped', P0[:-1])
    require(len(res) == 14, '14 negative controls rejected')
    # the zero-join fix: without Z1 the word is row-equal and legal, but the exact-zero join comes back
    z1 = ed['Z1']
    zev = [x['event'] for x in z1['insert']]
    require(len(zev) == 2 and zev[0][0] == 'CLEAR' and zev[1][0] == 'INIT' and zev[0][1:] == zev[1][1:], 'Z1 is one CLEAR+INIT at one chart')
    Pz = list(P0)
    cand = [i for i in range(len(P0) - 1) if P0[i] == zev[0] and P0[i + 1] == zev[1]]
    require(len(cand) == 1, 'the Z1 CLEAR+INIT pair occurs once')
    i = cand[0]
    del Pz[i:i + 2]
    require(outcome(Pz, W) is None, 'without Z1 the word is legal and row-equal')
    require(zero_joins({**W, 'program': Pz}) and not zero_joins(W), 'zero-join detector: present without Z1, absent with it')
    print('PASS control: removing the Z1 CLEAR+INIT leaves a legal row-equal word whose exact-zero join (field %d) the detector flags; the new word has none' % zev[0][1])
    print('PASS_CONTROLS_ON_7637: 14/14 negative controls rejected, 2 positives accepted, zero-join control passed')


def core(B, W):
    E = json.loads((DATA / 'edits.json').read_text())
    require(B.keys() == W.keys() and all(B[k] == W[k] for k in B if k != 'program'), 'header identical (initial, final, frames, hosted, ports, owned_fields)')
    print('PASS header: identical to #7637 (initial, final, frames, hosted, ports, live, owned_fields; entrance initial[457] = 281 as in #7637)')
    comps = [ed for ed in E['edits'] if 'h1' in ed]
    require(len(E['edits']) == NCOMP + 1 and len(comps) == NCOMP and E['edits'][-1]['id'] == 'Z1', '20 composites and the zero-join fix Z1')
    got, nd, ni = apply_interior(B, E)
    ok = interior_test(W)
    mine = [e for e in W['program'] if ok(e)]
    require(got == mine, 'interior of the new word = #7637 interior + edit list')
    hb = sum(1 for e in B['program'] if not ok(e))
    hw = sum(1 for e in W['program'] if not ok(e))
    print('PASS interior: %d interior events = #7637\'s %d - %d deleted + %d inserted (C1..C20 and Z1); hub events (ADD/SCALE at {0} and V)'
          ' %d -> %d; word %d -> %d events' % (len(mine), len(mine) - ni + nd, nd, ni, hb, hw, len(B['program']), len(W['program'])))
    RB, R = replay(B), replay(W)
    n = W['public']
    bad = [r for r in range(len(R['rows'])) if R['rows'][r] != RB['rows'][r]]
    require(not bad, 'all rows equal #7637 (first differing %s)' % bad[:3])
    require(R['cur'] == RB['cur'], 'all end charts equal #7637')
    M = mains(W)
    require(all(R['rows'][r] == {r: Q(1)} for r in range(n) if r not in M), 'helpers end at identity')
    require(all(not R['rows'][r] for r in range(n, len(R['rows']))), 'owned rows end empty')
    require(R['owned_moves'] == RB['owned_moves'], 'owned MOVE multiset unchanged')
    z1 = E['edits'][-1]
    zev = [x['event'] for x in z1['insert']]
    require(not z1['delete'] and len(zev) == 2 and zev[0][0] == 'CLEAR' and zev[1] == ['INIT'] + zev[0][1:], 'Z1 inserts one CLEAR and one INIT of the same field at the same chart')
    ltb, ltw = collections.Counter(RB['lifetimes']), collections.Counter(R['lifetimes'])
    require(sum(ltb.values()) == 233 and sum(ltw.values()) == 234, '233 lifetimes become 234')
    require(diff(ltb, ltw) == {(zev[0][1], zev[0][2], zev[0][2]): 1}, 'owned lifetimes unchanged except the Z1 split')
    require(R['peak'] == RB['peak'] == 50, 'owned peak 50')
    ownseq = lambda X: [e for e in X['program'] if e[0] in ('INIT', 'CLEAR') or (e[0] == 'MOVE' and e[1] >= n)]
    os_w = ownseq(W)
    j = os_w.index(zev[0])
    require(os_w[j + 1] == zev[1] and os_w[:j] + os_w[j + 2:] == ownseq(B), 'owned INIT/CLEAR/MOVE sequence = #7637\'s plus the Z1 pair')
    labels = {e[1] for e in W['program'] if e[0] == 'INIT'}
    require(labels == {e[1] for e in B['program'] if e[0] == 'INIT'} and len(labels) <= 68 == W['owned_fields'], 'same owned labels as #7637, within the 68 allocated')
    zb, zw = zero_joins(B), zero_joins(W)
    require(len(zb) == 2 and not zw, 'exact-zero joins: two in #7637, none in the new word')
    print('PASS exact replay: both words legal; all %d rows and end charts equal #7637, helpers identity, owned empty;'
          ' owned MOVEs (%d) unchanged; 233 -> 234 lifetimes (the Z1 split of field %d at chart %d), peak 50, %d of 68 labels used;'
          ' exact-zero joins %s in #7637 -> none' % (len(R['rows']), sum(R['owned_moves'].values()), zev[0][1], zev[0][2], len(labels), zb))
    changed = sorted(r for r in range(n) if chain_route(R, W, r) != chain_route(RB, B, r))
    require(changed == sorted({r for ed in comps for r in (ed['h1'], ed['h2'])}) and len(changed) == 2 * NCOMP, 'exactly the 40 helpers of C1..C20 change chains')
    for ed in comps:
        for r in (ed['h1'], ed['h2']):
            require(chain_route(RB, B, r) == ed['route_before'][str(r)] and chain_route(R, W, r) == ed['route_after'][str(r)],
                    '%s route of %d: %s -> %s' % (ed['id'], r, chain_route(RB, B, r), chain_route(R, W, r)))
        require(all(B['initial'][r] == 3 and B['final'][r] == 127 for r in (ed['h1'], ed['h2'])), '%s: both swapped registers are helpers born at chart 3 ending at V' % ed['id'])
        require(all(r not in M for r in (ed['h1'], ed['h2'])), '%s: both are helpers' % ed['id'])
    newp, gone = sorted(move_pairs(W) - move_pairs(B)), sorted(move_pairs(B) - move_pairs(W))
    for a, b in newp:
        require(R['sp'][a] < R['sp'][b], 'new pair %s strictly nested' % ((a, b),))
    print('PASS routes: exactly the 40 helpers of C1..C20 change chains, as listed; %d new MOVE pairs %s, all strictly nested; %d leave'
          % (len(newp), newp, len(gone)))
    sb, sw = RB['stats'], R['stats']
    require(sw['smooth'], 'replayed coefficients have 5-smooth denominators')
    for q in literal_coeffs(W['program']):
        o = q.denominator
        for p in (2, 3, 5):
            while o % p == 0:
                o //= p
        require(o == 1, 'literal coefficient has a 5-smooth denominator')
    print('PASS coefficients: 5-smooth; replayed grid #7637 (2-adic exponent %d, odd lcm %d, numerator bits %d) -> new (%d, %d, %d);'
          ' non-dyadic literal events %d -> %d' % (sb['max_den_exp'], sb['odd_den'], sb['max_num_bits'], sw['max_den_exp'], sw['odd_den'],
                                                  sw['max_num_bits'], nondyadic(B['program']), nondyadic(W['program'])))
    pb, hb_ = native_counts(B)
    pw, hw_ = native_counts(W)
    dP, dT = diff(pb, pw), diff(hb_, hw_)
    require(dP == DELTA_PAID and dT == {}, 'native deltas per call')
    print('PASS native per call: paid MOVE delta %s (20 fewer MOVEs); helper target delta %s' % (dP, dT))
    inv0 = json.loads((DATA / 'invoice-7637.json').read_text())
    P0 = {k: inv0['paid'][k] for k in sorted(inv0['paid'], key=int)}
    T0 = {k: inv0['targets'][k] for k in sorted(inv0['targets'], key=int)}
    require(inv0 == invoice_json(P0, T0), 'invoice-7637.json is #7637\'s invoice in the official schema')
    for k in sorted(set(P0) | set(str(x) for x in pb), key=int):
        require(P0.get(k, 0) == CALLS * pb.get(int(k), 0) + CALLER_EXTRA_PAID.get(k, 0), 'invoice-7637 paid rank %s = 17 x native + the caller constant' % k)
    for k in sorted(set(T0) | set(str(x) for x in hb_), key=int):
        require(T0.get(k, 0) == CALLS * hb_.get(int(k), 0) + CALLER_EXTRA_TARGETS.get(k, 0), 'invoice-7637 target rank %s = 17 x helper + the caller constant' % k)
    P, T = collections.Counter({int(k): v for k, v in P0.items()}), collections.Counter({int(k): v for k, v in T0.items()})
    for k, v in dP.items():
        P[k] += CALLS * v
    for k, v in dT.items():
        T[k] += CALLS * v
    require(min(P.values()) >= 0 and min(T.values()) >= 0, 'nonnegative counts')
    Pn = {str(k): v for k, v in sorted(P.items()) if v}
    Tn = {str(k): v for k, v in sorted(T.items()) if v}
    Sf = lambda T_, P_: sum(int(k) * v for k, v in T_.items()) - sum(int(k) * v for k, v in P_.items())
    require(Sf(T0, P0) == Sf(Tn, Pn) == 1424, 'rank surplus S 1424 unchanged')
    require(json.loads((DATA / 'invoice-new.json').read_text()) == invoice_json(Pn, Tn), 'invoice-new.json matches')
    require(json.loads((DATA / 'invoice-zero.json').read_text()) == invoice_json({}, {}), 'zero invoice')
    print('PASS complete invoice: paid positions %d -> %d, productive %d -> %d, S = 1424' % (sum(P0.values()), sum(Pn.values()), sum(T0.values()), sum(Tn.values())))
    k0, k1 = crossing(T0, P0), crossing(Tn, Pn)
    require(decimal.Decimal('0.00370007700378') <= k0 < decimal.Decimal('0.00370007700379'), '#7637 crossing reproduced')
    print('PASS kappa #7637 %s' % k0)
    print('PASS kappa new   %s (ratio over #7637 %s)' % (k1, +decimal.Context(prec=12).divide(k1, k0)))
    expected = json.loads((HERE / 'EXPECTED.json').read_text())
    require(str(k1)[:len(expected['kappa_prefix'])] == expected['kappa_prefix'], 'kappa digits as recorded')
    require(decimal.Decimal(CLAIM) < k1 < decimal.Decimal(ABOVE), 'claim %s is below the exact crossing' % CLAIM)
    print('PASS_CORE_ON_7637')


def main():
    B, W = load_words()
    if MODE in ('core', 'all'):
        core(B, W)
    if MODE in ('certificates', 'all'):
        certificates_section(B, W)
    if MODE in ('controls', 'all'):
        run_controls(B, W)
    for i in range(NPARTS):
        if MODE in ('columns%d' % (i + 1), 'all'):
            columns_section(B, W, i)
            print('PASS_COLUMNS_ON_7637_%d' % (i + 1))
    if MODE == 'all':
        print('PASS_SWAP_COMPOSITES_ON_7637_EXACT (conditional on the premises named in the README)')


if __name__ == '__main__':
    main()
