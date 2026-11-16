#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact replay of 14 loan + stationary-snapshot instances applied to #7621's word.

Standard library only. Written for this package; it imports no other package and none of the other PRs' code was
run (their words, invoices and the pinned affected-pair census are vendored or copied as data).

Modes (each is a separate VERIFY command): core, controls, columns1, columns2, engine; all runs core, controls and both
column halves (not engine).

core
  1. The vendored #7621 word (data/base-7621-word.json.gz, sha256 ff8cc4ac...) plus data/edits.json gives data/word.json.gz
     event for event (77,196 -> 77,277 events; sha256 97391721...).
  2. Both words are replayed over the rationals from arbitrary inputs, with full legality checks. Header identical; all 1,569 rows
     and end charts equal #7621's; helpers end at identity, owned rows end empty; owned MOVEs (47), owned peak (50) and the 68
     owned labels unchanged.
  3. Owned data. All 167 old lifetimes survive; there are exactly 13 new lifetimes, each stationary (INIT chart = CLEAR chart,
     one write of coefficient 1, one read of coefficient 1, dirty CLEAR, no MOVE). Every old owned observation (operation,
     source-row and destination-row content at every owned-touching event) reappears identically and in order once the
     new lifetimes' own events are removed. The old 167 CLEAR contents are identical and in order; the word has 180 CLEARs.
  4. Certificates: each of the 13 new CLEARs erases a row that is an exact rational combination of other live registers' rows
     (the acceptance rule of #7620's verify_certificates: keys live, not the cleared field, exact sum), from data/clear-certificates.json.
  5. Structure: 14 instances (data/instances.json); in each, register r drops its interior stop X and a partner p gains the chart A
     that precedes X on r's route, immediately before X in p's route (side A); exactly these 28 registers change chains, endpoints kept;
     every new MOVE pair is strictly nested.
  6. Coefficients: 5-smooth denominators, grid unchanged, non-dyadic literal events 5,903 -> 5,903; event delta per native call
     ADD +55, INIT +13, CLEAR +13; native paid delta {1:+1, 2:+13, 3:-28, 4:+13, 5:+1}; S 1,424; paid positions 110,145.
  7. Census, complete invoice (17 native calls) and kappa recomputed; #7621's crossing reproduced.
controls   22 negative controls (rejected) and 2 positives (accepted).
columns1/2 affected-pair column tests on the 964-pair census (even / odd sorted index): 512 forward + 512 adjoint exact Gaussian
           columns, signed Pauli action, absolute phase, exact ascent rank, wrong-phase rejection; rejecting controls.
engine     reruns engine/run_on.py on #7621's word and requires the output word and instance log to equal data/word.json.gz
           and data/instances.json.
"""
import collections
import multiprocessing
import copy
import decimal
import gzip
import hashlib
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / 'data'
BASE_SHA256 = 'ff8cc4ac45dc89c6dfca54d1954b21edefe599c14d31b2ead7ceeafe3bed1ec8'
WORD_SHA256 = '97391721ab7d30f8dd84c8d3c29a3c3ed2df2d65ca55e7ff8329bd09877681d2'
CALLS = 17


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


def apply_edits(program, E):
    require(len(program) == E['base_events'], 'edit list base length')
    dele = {}
    for i, ev in E['delete']:
        require(program[i] == ev, 'deleted event %d matches' % i)
        dele[i] = ev
    ins = collections.defaultdict(list)
    for i, evs in E['insert_before']:
        ins[i].extend(evs)
    out = []
    for i, ev in enumerate(program):
        out.extend(ins.get(i, []))
        if i not in dele:
            out.append(ev)
    out.extend(ins.get(len(program), []))
    return out + E['append']


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


def census(W, R):
    """Per-native paid MOVE ranks and helper targets (the #7546 accounting)."""
    dim = [len(f) for f in W['frames']]
    paid = collections.Counter(abs(dim[e[3]] - dim[e[2]]) for e in W['program'] if e[0] == 'MOVE')
    M, n = mains(W), W['public']
    helpers = collections.Counter(dim[W['final'][r]] - dim[W['initial'][r]] for r in range(n) if r not in M)
    rises = collections.Counter(dim[e[3]] - dim[e[2]] for e in W['program']
                                if e[0] == 'MOVE' and e[1] >= n and dim[e[3]] > dim[e[2]])
    hist = lambda c: {str(k): v for k, v in sorted(c.items()) if v}
    return dict(events=len(W['program']), public=n, helpers=hist(helpers), paid=hist(paid),
                lifetimes=sum(R['lifetimes'].values()), owned_peak=R['peak'], rises=hist(rises))


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


MODE = sys.argv[1] if len(sys.argv) > 1 else 'all'


def load_gz(path):
    return json.loads(gzip.decompress(Path(path).read_bytes()))


def observations(W):
    """Per owned-touching event the observation (event, source row, destination row); plus per-lifetime records."""
    n = W['public']
    rows = [{r: Q(1)} if r < n else {} for r in range(n + W['owned_fields'])]
    out, lt, open_ = [], [], {}
    for i, e in enumerate(W['program']):
        op, r = e[0], e[1]
        if op == 'INIT':
            rows[r] = {}
            open_[r] = dict(init=i, chart=e[2], w=[], rd=[], mv=0, field=r)
            out.append((i, r, tuple(e)))
        elif op == 'CLEAR':
            x = open_.pop(r)
            x['clear'] = i
            x['content'] = dict(rows[r])
            lt.append(x)
            out.append((i, r, (tuple(e), tuple(sorted(rows[r].items())))))
            rows[r] = {}
        elif op == 'MOVE':
            if r >= n:
                open_[r]['mv'] += 1
                out.append((i, r, (tuple(e), tuple(sorted(rows[r].items())))))
        elif op == 'SCALE':
            if r >= n:
                open_[r]['w'].append(('SCALE', e[2]))
                out.append((i, r, (tuple(e), tuple(sorted(rows[r].items())))))
            rows[r] = {k: v * Q(e[2]) for k, v in rows[r].items()}
        else:
            s = e[2]
            if r >= n:
                open_[r]['w'].append((s, e[3]))
            if s >= n:
                open_[s]['rd'].append((r, e[3]))
            if r >= n or s >= n:
                out.append((i, r if r >= n else s, (tuple(e), tuple(sorted(rows[s].items())), tuple(sorted(rows[r].items())))))
            R = rows[r]
            for k, v in rows[s].items():
                nv = R.get(k, 0) + Q(e[3]) * v
                if nv:
                    R[k] = nv
                else:
                    R.pop(k, None)
    return out, lt


def new_lifetimes(ltb, ltw):
    """Lifetimes of W not matched by a lifetime of B on the same (field, chart), in order."""
    old = collections.Counter((x['field'], x['chart']) for x in ltb)
    used, new = collections.Counter(), []
    for x in ltw:
        k = (x['field'], x['chart'])
        if used[k] < old[k]:
            used[k] += 1
        else:
            new.append(x)
    return new


def ordered_subsequence(small, big):
    it = iter(big)
    return all(any(c == d for d in it) for c in small)


def compare(B, RB, W):
    """Everything that must hold between #7621's word B and a candidate W, except observations and certificates."""
    require(all(B[k] == W[k] for k in B if k != 'program') and B.keys() == W.keys(), 'header identical')
    R = replay(W)
    n = W['public']
    bad = [r for r in range(len(R['rows'])) if R['rows'][r] != RB['rows'][r]]
    require(not bad, 'all rows equal #7621 (first differing %s)' % bad[:3])
    require(R['cur'] == RB['cur'], 'all end charts equal #7621')
    M = mains(W)
    require(all(R['rows'][r] == {r: Q(1)} for r in range(n) if r not in M), 'helpers end at identity')
    require(all(not R['rows'][r] for r in range(n, len(R['rows']))), 'owned rows end empty')
    require(R['owned_moves'] == RB['owned_moves'], 'owned MOVE multiset unchanged')
    require(R['peak'] == RB['peak'], 'owned peak unchanged')
    lb, lw = RB['lifetimes'], R['lifetimes']
    require(all(lw[k] >= v for k, v in lb.items()), 'every old lifetime kept')
    new = lw - lb
    require(sum(new.values()) == sum(lw.values()) - sum(lb.values()) and all(k[1] == k[2] for k in new),
            'new lifetimes are stationary (INIT chart = CLEAR chart)')
    cb, cw = clears(B), clears(W)
    require(ordered_subsequence(cb, cw), 'old CLEAR contents identical and in order')
    return R, sum(new.values()), len(cb), len(cw)


def chain_routes(RX, r):
    ch = RX['chains'][r]
    return [ch[0][0]] + [b for a, b in ch]


def structure(B, RB, W, R, I):
    """The 14 instances: r drops X; p gains the chart A before X (side A). Exactly these 28 registers change."""
    changed = sorted(r for r in set(R['chains']) | set(RB['chains']) if R['chains'][r] != RB['chains'][r])
    want = set()
    for x in I:
        r, X, p = x['r'], x['X'], x['p']
        require(x['side'] == 'A', 'instance %s is side A' % ((r, X, p),))
        ro, rn, po, pn = chain_routes(RB, r), chain_routes(R, r), chain_routes(RB, p), chain_routes(R, p)
        require(ro.count(X) == 1 and 0 < ro.index(X) < len(ro) - 1, 'X is an interior stop of r')
        k = ro.index(X)
        require(rn == ro[:k] + ro[k + 1:], 'r %d drops X %d (route %s -> %s)' % (r, X, ro, rn))
        A = ro[k - 1]
        require(X in po and po.count(X) == 1, 'p visits X')
        j = po.index(X)
        require(pn == po[:j] + [A] + po[j:] and A not in po, 'p %d gains chart %d immediately before X (route %s -> %s)' % (p, A, po, pn))
        want |= {r, p}
    require(len(I) == 14 and len(want) == 28 and changed == sorted(want), 'exactly the 28 registers of the 14 instances change chains')
    mp = lambda X: {(e[2], e[3]) for e in X['program'] if e[0] == 'MOVE'}
    newp, gone = sorted(mp(W) - mp(B)), sorted(mp(B) - mp(W))
    require((len(newp), len(gone)) == (24, 14), 'MOVE pairs: 24 new, 14 leave (got %d, %d)' % (len(newp), len(gone)))
    for a, b in newp:
        require(R['sp'][a] < R['sp'][b], 'new pair %s strictly nested' % ((a, b),))
    return changed, newp, gone


def verify_certificates(W, certs, newidx):
    """Exact CLEAR certificates for the new CLEARs: erased row == sum of cert coefficients times live registers' rows."""
    n = W['public']
    require(set(certs) == {str(i) for i in newidx}, 'a certificate for every new CLEAR and no other')
    rows = [{r: Q(1)} if r < n else {} for r in range(n + W['owned_fields'])]
    live = set(range(n))
    sizes = []
    for i, e in enumerate(W['program']):
        op, r = e[0], e[1]
        if op == 'INIT':
            live.add(r)
            rows[r] = {}
        elif op == 'CLEAR':
            if str(i) in certs:
                cert = {int(k): Q(v) for k, v in certs[str(i)].items()}
                require(all(k in live and k != r for k in cert), 'certificate keys live and not the cleared field')
                s = {}
                for k, c in cert.items():
                    for t, v in rows[k].items():
                        s[t] = s.get(t, 0) + c * v
                require({t: v for t, v in s.items() if v} == rows[r] and rows[r], 'exact nonzero certificate for CLEAR %d' % i)
                sizes.append(len(cert))
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
    return sorted(sizes)


def routes_of(X):
    out = collections.defaultdict(list)
    for e in X['program']:
        if e[0] == 'MOVE' and e[1] < X['public']:
            out[e[1]].append((e[2], e[3]))
    return out


def affected_pairs(B, W):
    """#7621's 846-pair census (the 837 pairs pinned by #7620's runner, minus (719,127), plus 10) extended to the loan word:
    every old- or new-route pair of every register whose chain changed (28 registers) joins; none leaves."""
    pin = {tuple(p) for p in json.loads((DATA / 'affected-pairs-7620.json').read_text())}
    require(len(pin) == 837, 'pinned census has 837 pairs')
    ten = {(3, 755), (3, 757), (260, 906), (755, 757), (755, 924), (757, 923), (757, 924), (906, 127), (923, 127), (924, 127)}
    p846 = {tuple(p) for p in json.loads((DATA / 'affected-pairs-7621.json').read_text())}
    require(p846 == (pin - {(719, 127)}) | ten and len(p846) == 846, "#7621's census is 846 pairs: 837 - (719,127) + 10")
    rb, rw = routes_of(B), routes_of(W)
    changed = [r for r in range(W['public']) if rb[r] != rw[r]]
    add = {q for r in changed for q in rb[r] + rw[r]}
    allp = p846 | add
    filep = {tuple(p) for p in json.loads((DATA / 'affected-pairs-loan.json').read_text())}
    require(allp == filep and len(allp) == 964, 'loan census is 964 pairs (846 + 118)')
    require(len(allp - p846) == 118 and not p846 - allp, '118 pairs added, none dropped')
    mp = lambda X: {(e[2], e[3]) for e in X['program'] if e[0] == 'MOVE'}
    require(mp(W) - mp(B) <= allp, 'every new MOVE pair is tested')
    return p846, allp


MODE = sys.argv[1] if len(sys.argv) > 1 else 'all'
require(MODE in ('all', 'core', 'controls', 'columns1', 'columns2', 'engine'), 'mode is all, core, controls, columns1, columns2 or engine')


def _pair_job(args):
    frames, a, b = args
    return (a, b, pair_columns(frames, a, b))


def columns_section(B, W, part):
    p846, allp = affected_pairs(B, W)
    frames = [tuple(f) for f in W['frames']]
    ordered = sorted(allp)
    mine = ordered[part::2]
    print('affected pairs: 846 (#7621) + 118 = %d; half %d of 2 tests %d pairs' % (len(allp), part + 1, len(mine)))
    jobs = [(frames, a, b) for a, b in mine]
    with multiprocessing.Pool(min(8, multiprocessing.cpu_count())) as pool:
        done = pool.map(_pair_job, jobs, chunksize=4)
    require(len(done) == len(mine), 'all pairs of this half tested')
    print('PASS columns half %d: %d chart pairs x (512 forward + 512 adjoint) exact Gaussian columns = %d, signed Pauli action, absolute phase,'
          ' exact public ascent rank, wrong-phase rejection each' % (part + 1, len(done), len(done) * 1024))
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
    mp = lambda X: {(e[2], e[3]) for e in X['program'] if e[0] == 'MOVE'}
    newp = sorted(mp(W) - mp(B))
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


def load_words():
    base_raw = (DATA / 'base-7621-word.json.gz').read_bytes()
    require(hashlib.sha256(base_raw).hexdigest() == BASE_SHA256, 'vendored #7621 word bytes')
    word_raw = (DATA / 'word.json.gz').read_bytes()
    require(hashlib.sha256(word_raw).hexdigest() == WORD_SHA256, 'new word bytes')
    return json.loads(gzip.decompress(base_raw)), json.loads(gzip.decompress(word_raw))


def run_controls(B, W):
    RB = replay(B)
    cB = clears(B)
    P0 = W['program']
    res = []

    def outcome(P, X0):
        X = dict(X0)
        X['program'] = P
        try:
            R = replay(X)
        except AssertionError as ex:
            return 'illegal: ' + str(ex)
        if R['rows'] != RB['rows'] or R['cur'] != RB['cur']:
            return 'rows/end charts differ (%d rows)' % sum(a != b for a, b in zip(R['rows'], RB['rows']))
        if not ordered_subsequence(cB, clears(X)):
            return 'old CLEAR contents differ'
        return None

    def test(label, P, X0=W, expect_reject=True):
        o = outcome(P, X0)
        require((o is not None) == expect_reject, 'control %s: %s' % (label, 'ACCEPTED' if o is None else 'REJECTED ' + o))
        if expect_reject:
            res.append(1)
        print('PASS control %s: %s %s' % ('rejected' if expect_reject else 'accepted', label, '(%s)' % o[:80] if o else ''), flush=True)

    def ix(ev, P=P0):
        return P.index(ev)

    def mod(f, base=P0):
        P = copy.deepcopy(base)
        f(P)
        return P

    def setv(old, new):
        return lambda P: P.__setitem__(ix(old, P), new)

    def mvb(ev, before):
        return lambda P: (P.remove(ev), P.insert(ix(before, P), ev))
    # instance r=392 X=455 p=562 carrier c=1154 snapshot 1525
    INI = ['INIT', 1525, 455]
    SW = ['ADD', 1525, 394, '1', 455]
    MP1 = ['MOVE', 562, 3, 445, False]
    RD = ['ADD', 562, 392, '1', 445]
    SWP = ['ADD', 392, 562, '-1', 445]
    LOAN = ['ADD', 392, 1154, '1', 445]
    MP2 = ['MOVE', 562, 445, 455, False]
    MR = ['MOVE', 392, 445, 848, False]
    PICK = ['ADD', 562, 1525, '1', 455]
    CLR = ['CLEAR', 1525, 455]
    SET = ['ADD', 392, 1154, '-1', 848]
    # instance r=382 X=438 p=553 and r=348 X=399 p=528 (no snapshot: X-writes rerouted straight into p)
    W724 = ['ADD', 553, 724, '2', 438]
    W93 = ['ADD', 528, 93, '1', 399]
    W714 = ['ADD', 528, 714, '-2', 399]
    L348 = ['ADD', 348, 1110, '1', 390]
    S348 = ['ADD', 348, 1110, '-1', 837]
    for ev in (INI, SW, MP1, RD, SWP, LOAN, MP2, MR, PICK, CLR, SET, W724, W93, W714, L348, S348):
        require(P0.count(ev) == 1, 'control event present once: %r' % (ev,))
    test('hit word (positive)', P0, expect_reject=False)
    test('#7621 word itself (positive)', B['program'], B, expect_reject=False)
    test('1 loan 392+=1154 @445 dropped', mod(lambda P: P.remove(LOAN)))
    test('2 settle 392+=-1154 @848 dropped', mod(lambda P: P.remove(SET)))
    test('3 loan and settle both dropped', mod(lambda P: (P.remove(LOAN), P.remove(SET))))
    test('4 loan coefficient +1 -> -1', mod(setv(LOAN, ['ADD', 392, 1154, '-1', 445])))
    test('5 swap 392+=-562 coefficient -1 -> +1', mod(setv(SWP, ['ADD', 392, 562, '1', 445])))
    test('6 snapshot pickup 562+=1525 @455 dropped', mod(lambda P: P.remove(PICK)))
    test('7 snapshot write 1525+=394 @455 dropped', mod(lambda P: P.remove(SW)))
    test('8 snapshot CLEAR before pickup', mod(mvb(CLR, PICK)))
    test('9 snapshot never cleared', mod(lambda P: P.remove(CLR)))
    test('10 snapshot write before its INIT', mod(mvb(SW, INI)))
    test('11 MOVE 562 445->455 before 562+=392 @445', mod(mvb(MP2, RD)))
    test('12 settle before MOVE 392 445->848', mod(mvb(SET, MR)))
    test('13 snapshot pickup before 562 arrives at 455', mod(mvb(PICK, MP2)))
    test('14 snapshot INIT on chart 445 (wrong chart)', mod(lambda P: (setv(INI, ['INIT', 1525, 445])(P), setv(CLR, ['CLEAR', 1525, 445])(P))))
    test('15 inserted stop dropped: MOVE 562 3->455 direct, ops at 445 removed',
         mod(lambda P: (P.remove(MP2), P.remove(SWP), P.remove(LOAN), P.remove(RD), setv(MP1, ['MOVE', 562, 3, 455, False])(P))))
    test('16 MOVE 392 445->848 ownership flag True', mod(setv(MR, MR[:4] + [True])))
    test('17 p=553 X-write 2*724 @438 sent back to r=382 (old form)', mod(setv(W724, ['ADD', 382, 724, '2', 438])))
    test('18 p=528 X-write 93 @399 dropped', mod(lambda P: P.remove(W93)))
    test('19 p=528 X-write -2*714 coefficient -> +2', mod(setv(W714, ['ADD', 528, 714, '2', 399])))
    test('20 348 loan dropped', mod(lambda P: P.remove(L348)))
    test('21 348 settle coefficient -1 -> -2', mod(setv(S348, ['ADD', 348, 1110, '-2', 837])))
    Bp = B['program']
    test('22 bare stop drop on #7621: 392 goes 445->848 direct, no loan or snapshot',
         mod(lambda P: (P.remove(['MOVE', 392, 445, 455, False]),
                        P.__setitem__(ix(['MOVE', 392, 455, 848, False], P), ['MOVE', 392, 445, 848, False])), Bp), B)
    require(len(res) == 22, '22 negative controls rejected')
    print('PASS_CONTROLS_LOAN: 22/22 negative controls rejected, 2 positives accepted')


def run_engine(B, W):
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory(prefix='loan-engine-') as tmp:
        out = str(Path(tmp) / 'out')
        r = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'engine' / 'run_on.py'), str(DATA / 'base-7621-word.json.gz'), out],
                           capture_output=True, text=True, timeout=1800)
        require(r.returncode == 0, 'engine run exited 0: ' + r.stderr[-300:])
        print(r.stdout[-700:])
        new = load_gz(out + '_14.json.gz')
        require(new == W, 'engine output on #7621 equals data/word.json.gz (JSON-equal)')
        log = json.loads(Path(out + '_log.json').read_text())
        require(log == json.loads((DATA / 'instances.json').read_text()), 'engine instance log equals data/instances.json')
    print('PASS_ENGINE_REPRODUCES_HIT_LOAN_14: run_on.py on #7621 lands 14 instances; word JSON-equal, log equal')


def main():
    B, W = load_words()
    if MODE == 'engine':
        run_engine(B, W)
        return
    if MODE in ('columns1', 'columns2'):
        columns_section(B, W, 0 if MODE == 'columns1' else 1)
        print('PASS_COLUMNS_ON_7621_' + MODE[-1])
        return
    if MODE == 'controls':
        run_controls(B, W)
        return
    E = json.loads((DATA / 'edits.json').read_text())
    require(apply_edits(B['program'], E) == W['program'], 'word = #7621 word + edit list')
    require(len(B['program']) == 77196 and len(W['program']) == 77277, 'event census 77,196 -> 77,277')
    print('PASS word = #7621 word (%d events) + %d deletions, %d insertions = %d events; word sha256 %s'
          % (len(B['program']), len(E['delete']), sum(len(x[1]) for x in E['insert_before']), len(W['program']), WORD_SHA256[:12]))
    RB = replay(B)
    R, nnew, ncb, ncw = compare(B, RB, W)
    require((sum(RB['lifetimes'].values()), sum(R['lifetimes'].values()), RB['peak'], R['peak']) == (167, 180, 50, 50), 'lifetimes 167 -> 180, peak 50')
    require((ncb, ncw, nnew) == (167, 180, 13), 'CLEARs 167 -> 180 (74 + 106 stationary); 13 new')
    owned_labels = {e[1] for e in W['program'] if e[0] == 'INIT'}
    require(len(owned_labels) == 68 and len(owned_labels) == W['owned_fields'], '68 owned labels')
    print('PASS exact replay: legal, header identical, all %d rows and end charts equal #7621, helpers identity, owned empty;'
          ' owned MOVEs (%d) unchanged, peak %d, labels 68; lifetimes 167 -> 180 (13 new, all stationary)'
          % (len(R['rows']), sum(R['owned_moves'].values()), R['peak']))
    ob, ltb = observations(B)
    ow, ltw = observations(W)
    new = new_lifetimes(ltb, ltw)
    require(len(new) == 13, '13 new lifetimes')
    for x in new:
        require(x['init'] < x['clear'] and x['chart'] == W['program'][x['clear']][2] and x['mv'] == 0 and len(x['w']) == 1 and len(x['rd']) == 1
                and Q(x['w'][0][1]) == 1 and Q(x['rd'][0][1]) == 1 and x['content'], 'new lifetime at %d is stationary: INIT, one write, one read (coefficient 1), dirty CLEAR, no MOVE' % x['init'])
    excl = {i for x in new for i, f, o in ow if f == x['field'] and x['init'] <= i <= x['clear']}
    ow2 = [o for i, f, o in ow if i not in excl]
    require(ow2 == [o for i, f, o in ob], 'every old owned observation reappears identically and in order')
    print('PASS owned observations: all %d old observations identical and in order once the %d events of the 13 new lifetimes are removed'
          % (len(ob), len(excl)))
    certs = json.loads((DATA / 'clear-certificates.json').read_text())['clear_event_index']
    sizes = verify_certificates(W, certs, [x['clear'] for x in new])
    print('PASS CLEAR certificates: the 13 new CLEARs each erase an exact combination of %d..%d other live registers (#7620 verify_certificates rule)' % (sizes[0], sizes[-1]))
    nz = sum(1 for _, c in clears(W) if c)
    print('PASS CLEAR reading: %d CLEARs in all (74 + 106 stationary: 167 old identical to #7621 + 13 new), %d with nonzero content; premises = #7620\'s, now over 180 CLEARs' % (ncw, nz))

    I = json.loads((DATA / 'instances.json').read_text())
    changed, newp, gone = structure(B, RB, W, R, I)
    dim = [len(f) for f in W['frames']]
    print('PASS structure: 14 side-A instances; r drops X, p gains the chart before X; exactly the %d registers change chains; %d new MOVE pairs, all strictly nested, %d leave'
          % (len(changed), len(newp), len(gone)))
    ops = lambda P: collections.Counter(e[0] for e in P)
    d = ops(W['program'])
    d.subtract(ops(B['program']))
    require({k: v for k, v in d.items() if v} == {'ADD': 55, 'INIT': 13, 'CLEAR': 13}, 'event delta ADD +55, INIT +13, CLEAR +13')
    print('PASS event delta', {k: v for k, v in sorted(d.items()) if v})
    sb, sw = RB['stats'], R['stats']
    require(sw['smooth'] and sb['smooth'], 'replayed coefficients have 5-smooth denominators')
    for q in literal_coeffs(W['program']):
        o = q.denominator
        while o % 2 == 0: o //= 2
        while o % 3 == 0: o //= 3
        while o % 5 == 0: o //= 5
        require(o == 1, 'literal coefficient has a 5-smooth denominator')
    nb, nw = nondyadic(B['program']), nondyadic(W['program'])
    require((nb, nw) == (5903, 5903), 'non-dyadic literal events 5903 -> 5903')
    require(sw['max_den_exp'] <= sb['max_den_exp'] and sw['odd_den'] == sb['odd_den'] and sw['max_num_bits'] <= sb['max_num_bits'], 'grid within #7621')
    print('PASS coefficients: 5-smooth; non-dyadic literal events %d -> %d; grid equal to #7621 (2-adic exponent %d, odd denominator lcm %d, numerator bits %d)'
          % (nb, nw, sw['max_den_exp'], sw['odd_den'], sw['max_num_bits']))
    cb, cw = census(B, RB), census(W, R)
    require(cw['helpers'] == cb['helpers'] and cw['rises'] == cb['rises'], 'helper targets and owned rises unchanged')
    dpaid = collections.Counter({int(k): v for k, v in cw['paid'].items()})
    dpaid.subtract({int(k): v for k, v in cb['paid'].items()})
    dpaid = {k: v for k, v in sorted(dpaid.items()) if v}
    require(dpaid == {1: 1, 2: 13, 3: -28, 4: 13, 5: 1}, 'native paid delta {1:+1, 2:+13, 3:-28, 4:+13, 5:+1}')
    print('PASS native paid delta per call', dpaid)
    inv0 = json.loads((DATA / 'invoice-7621.json').read_text())
    P0 = {k: inv0['paid'][k] for k in sorted(inv0['paid'], key=int)}
    T = {k: inv0['targets'][k] for k in sorted(inv0['targets'], key=int)}
    P = collections.Counter({int(k): v for k, v in P0.items()})
    S0 = sum(int(k) * v for k, v in T.items()) - sum(int(k) * v for k, v in P0.items())
    paid0 = sum(P.values())
    for k, v in dpaid.items():
        P[k] += CALLS * v
    Pn = {str(k): v for k, v in sorted(P.items()) if v}
    S = sum(int(k) * v for k, v in T.items()) - sum(int(k) * v for k, v in Pn.items())
    require(S == S0 == 1424, 'rank surplus 1424 unchanged')
    require(json.loads((DATA / 'invoice-new.json').read_text()) == invoice_json(Pn, T), 'invoice-new.json matches')
    require(json.loads((DATA / 'invoice-zero.json').read_text()) == invoice_json({}, {}), 'zero invoice')
    require(inv0 == invoice_json(P0, T), 'invoice-7621.json is #7621 invoice in the official schema')
    paid1 = sum(Pn.values())
    require((paid0, paid1) == (110145, 110145), 'paid positions 110145 unchanged')
    print('PASS complete invoice: paid positions %d -> %d, productive %d, S = %d' % (paid0, paid1, sum(T.values()), S))
    k0, k1 = crossing(T, P0), crossing(T, Pn)
    require(decimal.Decimal('0.0036614625547') <= k0 <= decimal.Decimal('0.0036614625548'), '#7621 crossing reproduced')
    print('PASS kappa #7621 %s' % k0)
    print('PASS kappa new   %s (ratio over #7621 %s)' % (k1, +decimal.Context(prec=12).divide(k1, k0)))
    expected = json.loads((HERE / 'EXPECTED.json').read_text())
    require(str(k1)[:len(expected['kappa_prefix'])] == expected['kappa_prefix'], 'kappa digits as recorded')
    require(k1 > decimal.Decimal('0.0036624027915'), 'claim 0.0036624027915 is below the exact crossing')
    if MODE == 'core':
        print('PASS_CORE_LOAN_ON_7621')
        return
    run_controls(B, W)
    columns_section(B, W, 0)
    columns_section(B, W, 1)
    print('PASS_LOAN_SNAPSHOT_ON_7621_EXACT (conditional on exactly #7620\'s premises, 180 CLEARs)')


if __name__ == '__main__':
    main()
