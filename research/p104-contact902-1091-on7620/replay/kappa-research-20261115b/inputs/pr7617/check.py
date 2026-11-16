#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact replay of two courier (funded-return) moves against #7616's word.

Standard library only. Written for this package; it imports no other package
and none of #7616's, #7615's or #7613's code was run (their word, invoice and
the pinned affected-pair list are vendored as data).

1. The vendored #7616 word has compressed SHA256 ed760a6d...2110 (data/word.json.gz
   of research/p104-w2-stationary-followup at #7616) and applying data/edits.json
   gives data/word.json.gz event for event (the new word's hash is pinned too).
2. Both words are replayed over the rationals from arbitrary inputs. Legality:
   every ADD/COPY/SCALE operand sits at the event's chart, every MOVE starts at
   the register's current chart, public MOVEs strictly ascend (span inclusion),
   owned MOVEs are nested and only on live owned fields, COPY writes a zero
   field, no SCALE by 0, no self-ADD, every owned field is cleared at the chart
   it sits in, and public fields end at `final`.
3. Header identical; all 1,569 rows and end charts equal #7616's; helpers end
   at identity, owned rows end empty; owned MOVEs, all 113 lifetimes, peak 50
   and the 68 owned labels unchanged; event census pinned (76,896 events).
4. The content erased at all 113 CLEARs (74 + 39 stationary) equals #7616's
   exactly, so the premises are exactly #7616's.
5. Courier structure. Two (S, D) pairs: transit S drops a mid-chart (532 drops
   744, 226 drops 907); courier D, present with S at chart a, stops at S's
   next chart b (1464 already stops at 746, 990 at 127). The encode shear at a
   and the inverse decode shear at b are located and checked as elementary
   shears (determinant 1), exact inverses, with the encode before the transit
   MOVE and the decode after it. The 226/990 move needs 226's MOVE 260->719
   slid earlier, to just after its last chart-260 op, so courier 990 is
   co-present at 719. Only registers 226 and 532 change chains, endpoints kept.
   Exactly one new chart pair (719,127) appears, strictly nested.
6. Coefficients: every literal and replayed coefficient has a 5-smooth
   denominator (main's #7000 alphabet) with the common grid within #7616's.
   No non-dyadic event is added.
7. Census, complete invoice (17 native calls) and kappa are recomputed and
   compared with data/invoice-*.json; #7616's crossing is reproduced.
8. Affected-pair column tests (own implementation, section at the end): the 442
   chart pairs pinned by #7616's native adapter (data/affected-pairs-7616.json)
   plus every pair on the routes of the registers whose route changed here
   (226, 532) are tested: 512 forward and 512 adjoint exact Gaussian columns,
   signed Pauli action, absolute phase, exact public ascent rank, and a
   wrong-phase rejection for each pair.
9. Controls: corrupted words and a tampered invoice must be rejected.
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
BASE_SHA256 = 'ed760a6d4efc06ffdc831acd99b1a4661b09eb3cd82e2942a4783f4af0e52110'
WORD_SHA256 = '8bc9799174f377239bc0bf18611c5bab1ffdf95613fb60e5db684efb6ffbed2a'
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


# DROPPED: chart a transit register S no longer visits; ADDED: stop a courier D gains (990 and 779 already stop at S's next chart).
DROPPED = {532: 744, 226: 907}
# Encode shears (program order, at the common chart a) and decode shears (at S's next chart b); each is (target, source, coeff, chart).
SHEARS = {
    '532/1464': ([(532, 1464, '-2', 3)], [(532, 1464, '2', 746)]),
    '226/990': ([(990, 226, '-1', 719)], [(990, 226, '1', 127)]),
}


def literal_coeffs(program):
    return [Q(e[2]) for e in program if e[0] == 'SCALE'] + [Q(e[3]) for e in program if e[0] in ('ADD', 'COPY')]


def nondyadic(program):
    return sum(1 for q in literal_coeffs(program) if q.denominator & (q.denominator - 1))


def compare(B, RB, W):
    """Everything that must hold between #7616's word B and a candidate W, except the erased-content premise.
    Returns the candidate replay and the changed registers."""
    require(all(B[k] == W[k] for k in B if k != 'program') and B.keys() == W.keys(), 'header identical')
    R = replay(W)
    n = W['public']
    bad = [r for r in range(len(R['rows'])) if R['rows'][r] != RB['rows'][r]]
    require(not bad, 'all rows equal #7616 (first differing %s)' % bad[:3])
    require(R['cur'] == RB['cur'], 'all end charts equal #7616')
    M = mains(W)
    require(all(R['rows'][r] == {r: Q(1)} for r in range(n) if r not in M), 'helpers end at identity')
    require(all(not R['rows'][r] for r in range(n, len(R['rows']))), 'owned rows end empty')
    require(R['owned_moves'] == RB['owned_moves'], 'owned MOVE multiset unchanged')
    require(R['lifetimes'] == RB['lifetimes'] and R['peak'] == RB['peak'], 'owned lifetimes and peak unchanged')
    cb, cw = clears(B), clears(W)
    require(len(cb) == len(cw), 'same number of CLEARs')
    diff = [(i, x, y) for i, (x, y) in enumerate(zip(cb, cw)) if x != y]
    require(not diff, 'CLEAR content identical to #7616 (differs at %s)' % [d[0] for d in diff[:5]])
    changed = sorted(r for r in set(R['chains']) | set(RB['chains']) if R['chains'][r] != RB['chains'][r])
    require(changed == [226, 532], 'only the two transit registers change chains (got %s)' % changed[:12])
    for r in changed:
        old, new = RB['chains'][r], R['chains'][r]
        require(old[0][0] == new[0][0] and old[-1][1] == new[-1][1], 'register %d chain endpoints' % r)
        co = [old[0][0]] + [b for a, b in old]
        cn = [new[0][0]] + [b for a, b in new]
        require(co.count(DROPPED[r]) == 1 and cn == [c for c in co if c != DROPPED[r]],
                'transit %d drops exactly chart %d' % (r, DROPPED[r]))
    return R, changed


def locate(program, tgt, src, c, ch, lo=0):
    ev = ['ADD', tgt, src, c, ch]
    for i in range(lo, len(program)):
        if program[i][:5] == ev:
            return i
    raise AssertionError('shear %r not found' % ev)


def check_shears(W):
    """Locate each encode/decode shear, check inverse-in-reverse-order, encode before the transit MOVE, decode after."""
    P = W['program']
    out = {}
    for name, (enc, dec) in SHEARS.items():
        S, Dc = int(name.split('/')[0]), int(name.split('/')[1])
        ie = [locate(P, *e) for e in enc]
        idc = [locate(P, *e) for e in dec]
        require(len(enc) == len(dec), name + ' equal numbers of shears')
        for (t, s, c, ch), (t2, s2, c2, ch2) in zip(enc, reversed(dec)):
            require((t, s) == (t2, s2) and Q(c) == -Q(c2), name + ' decode is the inverse shear in reverse order')
        require(ie == sorted(ie) and idc == sorted(idc) and max(ie) < min(idc), name + ' encode precedes decode')
        # the transit register S makes its move to the decode chart b after encoding and before decoding
        b = dec[0][3]
        mv = [i for i, e in enumerate(P) if e[0] == 'MOVE' and e[1] == S and e[3] == b]
        require(len(mv) >= 1 and any(max(ie) < i < min(idc) for i in mv), name + ' S moves to b between encode and decode')
        out[name] = (min(ie), max(idc))
    return out


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
require(MODE in ('all', 'core', 'columns'), 'mode is all, core or columns')


def _pair_job(args):
    frames, a, b = args
    return (a, b, pair_columns(frames, a, b))


def affected_pairs(B, W):
    """Pinned #7616 census (442 pairs) plus every pair on the old and new routes of the registers whose route changed."""
    pinned = {tuple(p) for p in json.loads((DATA / 'affected-pairs-7616.json').read_text())}
    require(len(pinned) == 442, 'pinned census has 442 pairs')
    routes = lambda X, r: [tuple(e[2:4]) for e in X['program'] if e[0] == 'MOVE' and e[1] == r]
    extra = set()
    for r in (226, 532):
        extra |= set(routes(B, r)) | set(routes(W, r))
    return pinned, extra - pinned, pinned | extra


def columns_section(B, W):
    ipairs = lambda W_: {(e[2], e[3]) for e in W_['program'] if e[0] == 'MOVE'}
    # affected-pair column tests (own implementation)
    pinned, extra, allp = affected_pairs(B, W)
    wp = ipairs(W)
    require(all(0 <= p[0] < len(W['frames']) and 0 <= p[1] < len(W['frames']) for p in allp), 'pair indices are charts')
    in_word = sum(1 for p in allp if p in wp)
    require((719, 127) in extra, 'new pair (719,127) is in the census')
    print('affected pairs: %d pinned by #7616 + %d from the changed routes (incl. (719,127)) = %d (%d are MOVE pairs of the new word, the rest are the pinned #7481-comparator pairs)'
          % (len(pinned), len(extra), len(allp), in_word))
    frames = [tuple(f) for f in W['frames']]
    jobs = [(frames, a, b) for a, b in sorted(allp)]
    with multiprocessing.Pool(min(8, multiprocessing.cpu_count())) as pool:
        done = pool.map(_pair_job, jobs, chunksize=4)
    require(len(done) == len(allp), 'all pairs tested')
    print('PASS columns: %d chart pairs x (512 forward + 512 adjoint) exact Gaussian columns = %d, signed Pauli action, absolute phase,'
          ' exact public ascent rank, wrong-phase rejection each'
          % (len(done), len(done) * 1024))

    def col_rejected(label, mutate):
        try:
            mutate()
        except AssertionError as exc:
            print('PASS control rejected: %s (%s)' % (label, str(exc)[:70]))
            return
        raise AssertionError('control not rejected: ' + label)

    def non_nested():
        pair_columns(frames, 719, 128)
    require(not (span(frames[719]) < span(frames[128]) or span(frames[128]) < span(frames[719])), 'control pair is not nested')
    col_rejected('column test rejects the non-nested pair (719,128)', non_nested)

    def tampered_recipe():
        rec = lower(frame_op(frames[719]).dag().then(frame_op(frames[127])))
        rec['left']['offset'] ^= 1
        exp = dagger(frame_circuit(frames[719])) + frame_circuit(frames[127])
        require(tableau(recipe_circuit(rec)) == tableau(exp) and column(recipe_circuit(rec), 0) == column(exp, 0), 'recipe column 0')
    col_rejected('column test rejects a (719,127) recipe with a shifted offset', tampered_recipe)

    def phase_only():
        rec = lower(frame_op(frames[719]).dag().then(frame_op(frames[127])))
        exp = dagger(frame_circuit(frames[719])) + frame_circuit(frames[127])
        require(column(recipe_circuit(rec) + (('phase', 2),), 0) == column(exp, 0), 'recipe column 0 phase')
    col_rejected('column test rejects a (719,127) recipe with a global phase error', phase_only)


def main():
    base_raw = (DATA / 'base-7616-word.json.gz').read_bytes()
    require(hashlib.sha256(base_raw).hexdigest() == BASE_SHA256, 'vendored #7616 word bytes')
    word_raw = (DATA / 'word.json.gz').read_bytes()
    require(hashlib.sha256(word_raw).hexdigest() == WORD_SHA256, 'new word bytes')
    B = json.loads(gzip.decompress(base_raw))
    W = load_gz(DATA / 'word.json.gz')
    E = json.loads((DATA / 'edits.json').read_text())
    require(apply_edits(B['program'], E) == W['program'], 'word = #7616 word + edit list')
    require(len(B['program']) == len(W['program']) == 76896, 'event census 76,896 on both words')
    print('PASS word = #7616 word (%d events) + %d deletions, %d insertions = %d events; word sha256 %s'
          % (len(B['program']), len(E['delete']), sum(len(x[1]) for x in E['insert_before']), len(W['program']), WORD_SHA256[:12]))

    RB = replay(B)
    R, changed = compare(B, RB, W)
    dim = [len(f) for f in W['frames']]
    for r in changed:
        f = lambda ch: '->'.join([str(dim[ch[0][0]])] + [str(dim[b]) for a, b in ch])
        print('PASS register %d dims %s became %s' % (r, f(RB['chains'][r]), f(R['chains'][r])))
    check_shears(W)
    print('PASS shears: encode/decode of the two courier pairs located, elementary, exact inverses in reverse order,'
          ' encode before and decode after the transit MOVE; 226/990 needs the MOVE 226 260->719 slid earlier, checked by replay legality')
    print('PASS exact replay: legal, all %d rows and end charts equal #7616, helpers identity, owned empty;'
          ' owned MOVEs (%d), lifetimes (%d), peak (%d) unchanged'
          % (len(R['rows']), sum(R['owned_moves'].values()), sum(R['lifetimes'].values()), R['peak']))
    require((sum(R['lifetimes'].values()), R['peak']) == (113, 50), 'census (113 lifetimes, peak 50)')
    owned_labels = {e[1] for e in W['program'] if e[0] == 'INIT'}
    require(len(owned_labels) == 68 and len(owned_labels) == W['owned_fields'], '68 owned labels')

    cl = clears(W)
    require(len(cl) == 113, 'all 113 CLEARs present')
    nz = sum(1 for _, c in cl if c)
    print('PASS CLEAR content: all 113 CLEARs (74 + 39 stationary) erase exactly #7616 content (%d nonzero, %d zero); no new premise' % (nz, 113 - nz))

    key = lambda W_, i: tuple(W_['frames'][i])
    pairs = lambda W_: {(key(W_, e[2]), key(W_, e[3])) for e in W_['program'] if e[0] == 'MOVE'}
    ipairs = lambda W_: {(e[2], e[3]) for e in W_['program'] if e[0] == 'MOVE'}
    newp = sorted(ipairs(W) - ipairs(B))
    require(newp == [(719, 127)], 'exactly one new chart pair (got %s)' % newp)
    require(len(pairs(W) - pairs(B)) == 1 and not (pairs(B) - pairs(W)), 'one new frame pair, none removed')
    a, b = newp[0]
    require(span(W['frames'][a]) < span(W['frames'][b]) and (dim[a], dim[b]) == (6, 9), 'new pair strictly nested, dims 6->9')
    for pa, pb in pairs(W):
        require(span(pa) < span(pb) or span(pb) < span(pa), 'every pair nested')
    print('PASS new chart pair %s, strictly nested, dims %d->%d' % (newp[0], dim[a], dim[b]))
    ops = lambda P: collections.Counter(e[0] for e in P)
    d = ops(W['program']); d.subtract(ops(B['program']))
    require({k: v for k, v in d.items() if v} == {'ADD': 2, 'MOVE': -2}, 'event delta per native call: ADD +2, MOVE -2')
    print('PASS event delta per native call', {k: v for k, v in sorted(d.items()) if v})

    sb, sw = RB['stats'], R['stats']
    require(sw['smooth'] and sb['smooth'], 'replayed coefficients have 5-smooth denominators')
    for q in literal_coeffs(W['program']):
        o = q.denominator
        while o % 2 == 0: o //= 2
        while o % 3 == 0: o //= 3
        while o % 5 == 0: o //= 5
        require(o == 1, 'literal coefficient has a 5-smooth denominator')
    nb, nw = nondyadic(B['program']), nondyadic(W['program'])
    require(nw == nb == 5901, 'no non-dyadic literal event is added (5901 both)')
    require(sw['max_den_exp'] <= sb['max_den_exp'] and sw['odd_den'] == sb['odd_den']
            and sw['max_num_bits'] <= sb['max_num_bits'], 'intermediate coefficient grid within #7616')
    print('PASS coefficients: 5-smooth denominators (main #7000 alphabet); non-dyadic literal events %d -> %d (none added);'
          ' grid within #7616 (2-adic exponent %d, odd denominator lcm %d, numerator bits %d)'
          % (nb, nw, sw['max_den_exp'], sw['odd_den'], sw['max_num_bits']))

    cb, cw = census(B, RB), census(W, R)
    require(cw['helpers'] == cb['helpers'] and cw['rises'] == cb['rises'], 'helper targets and owned rises unchanged')
    dpaid = collections.Counter({int(k): v for k, v in cw['paid'].items()})
    dpaid.subtract({int(k): v for k, v in cb['paid'].items()})
    dpaid = {k: v for k, v in sorted(dpaid.items()) if v}
    require(dpaid == {1: -1, 2: -1, 3: -1, 6: 1}, 'native paid delta {1:-1, 2:-1, 3:-1, 6:+1}')
    print('PASS native paid delta per call', dpaid)
    inv0 = json.loads((DATA / 'invoice-7616.json').read_text())
    P = collections.Counter({int(k): v for k, v in inv0['paid'].items()})
    T = dict(inv0['targets'])
    S0 = sum(int(k) * v for k, v in T.items()) - sum(int(k) * v for k, v in inv0['paid'].items())
    paid0 = sum(P.values())
    for k, v in dpaid.items():
        P[k] += CALLS * v
    Pn = {str(k): v for k, v in sorted(P.items()) if v}
    S = sum(int(k) * v for k, v in T.items()) - sum(int(k) * v for k, v in Pn.items())
    require(S == S0 == 1424, 'rank surplus 1424 unchanged')
    require(json.loads((DATA / 'invoice-new.json').read_text()) == invoice_json(Pn, T), 'invoice-new.json matches')
    require(json.loads((DATA / 'invoice-zero.json').read_text()) == invoice_json({}, {}), 'zero invoice')
    paid1 = sum(Pn.values())
    require((paid0, paid1) == (110213, 110179), 'paid positions')
    print('PASS complete invoice: paid positions %d -> %d, productive %d, S = %d' % (paid0, paid1, sum(T.values()), S))

    k0, k1 = crossing(inv0['targets'], inv0['paid']), crossing(T, Pn)
    lo, hi = decimal.Decimal('0.0036566283026'), decimal.Decimal('0.0036566283027')
    require(lo <= k0 <= hi, '#7616 crossing reproduced')
    print('PASS kappa #7616 %s' % k0)
    print('PASS kappa new   %s (ratio over #7616 %s)' % (k1, +decimal.Context(prec=12).divide(k1, k0)))
    expected = json.loads((HERE / 'EXPECTED.json').read_text())
    require(str(k1)[:len(expected['kappa_prefix'])] == expected['kappa_prefix'], 'kappa digits as recorded')
    require(k1 > decimal.Decimal('0.00365760025222'), 'claim 0.00365760025222 is below the exact crossing')

    if MODE == 'columns':
        columns_section(B, W)
        print('PASS_COLUMNS_ON_7616')
        return
    if MODE == 'all':
        columns_section(B, W)

    def rejected(label, mutate):
        X = copy.deepcopy(W)
        mutate(X['program'])
        try:
            compare(B, RB, X)
            check_shears(X)
        except AssertionError as exc:
            print('PASS control rejected: %s (%s)' % (label, exc))
            return
        raise AssertionError('control not rejected: ' + label)
    P0 = W['program']
    idx = lambda ev: P0.index(ev)
    rejected('226/990 encode coefficient -1 -> -1/2', lambda P: P.__setitem__(idx(['ADD', 990, 226, '-1', 719]), ['ADD', 990, 226, '-1/2', 719]))
    rejected('226/990 decode dropped', lambda P: P.pop(idx(['ADD', 990, 226, '1', 127])))
    rejected('226/990 decode sign flipped', lambda P: P.__setitem__(idx(['ADD', 990, 226, '1', 127]), ['ADD', 990, 226, '-1', 127]))
    rejected('226/990 encode dropped', lambda P: P.pop(idx(['ADD', 990, 226, '-1', 719])))
    m226 = idx(['MOVE', 226, 260, 719, False])
    rejected('226 MOVE 260->719 not slid (back at its old place)', lambda P: (P.pop(m226), P.insert(idx(['ADD', 473, 226, '1', 719]), ['MOVE', 226, 260, 719, False])))
    rejected('226 MOVE 719->127 ownership flag flipped', lambda P: P.__setitem__(idx(['MOVE', 226, 719, 127, False]), ['MOVE', 226, 719, 127, True]))
    e1 = idx(['ADD', 532, 1464, '-2', 3])
    rejected('532/1464 encode coefficient changed', lambda P: P.__setitem__(e1, ['ADD', 532, 1464, '-1', 3]))
    rejected('532/1464 encode dropped', lambda P: P.pop(e1))
    rejected('532 decode dropped', lambda P: P.pop(idx(['ADD', 532, 1464, '2', 746])))
    rejected('532 decode sign flipped', lambda P: P.__setitem__(idx(['ADD', 532, 1464, '2', 746]), ['ADD', 532, 1464, '-2', 746]))
    ms = idx(['MOVE', 532, 3, 746, False])
    rejected('transit MOVE 532 placed after its decode', lambda P: (P.pop(ms), P.insert(idx(['ADD', 532, 1464, '2', 746]) + 1, ['MOVE', 532, 3, 746, False])))
    rejected('ownership flag flipped on a transit MOVE', lambda P: P.__setitem__(ms, ['MOVE', 532, 3, 746, True]))
    m2 = idx(['MOVE', 226, 719, 127, False])
    rejected('MOVE 226 reversed', lambda P: P.__setitem__(m2, ['MOVE', 226, 127, 719, False]))
    rejected('MOVE 226 to a non-nested chart (128)', lambda P: P.__setitem__(m2, ['MOVE', 226, 719, 128, False]))
    rejected('encode retagged at the dropped chart 907', lambda P: P.__setitem__(idx(['ADD', 990, 226, '-1', 719]), ['ADD', 990, 226, '-1', 907]))
    rejected('no stop at 746 for 532 (MOVE 3->744 kept)', lambda P: P.__setitem__(ms, ['MOVE', 532, 3, 744, False]))
    bare = copy.deepcopy(B['program'])
    i7 = bare.index(['MOVE', 226, 719, 907, False]); j7 = bare.index(['MOVE', 226, 907, 127, False])
    Xb = copy.deepcopy(B); Xb['program'] = bare[:i7] + [['MOVE', 226, 719, 127, False]] + bare[i7 + 1:j7] + bare[j7 + 1:]
    try:
        compare(B, RB, Xb)
        raise SystemExit('control not rejected: bare hop deletion')
    except AssertionError as exc:
        print('PASS control rejected: bare hop deletion of 226 at 907 without a courier (%s)' % exc)
    bad = dict(Pn); bad['3'] -= 1
    require(json.loads((DATA / 'invoice-new.json').read_text()) != invoice_json(bad, T), 'tampered invoice differs')
    print('PASS control rejected: invoice with one rank-3 job removed differs from the recomputed one')
    print('PASS_TWO_COURIERS_ON_7616_EXACT (conditional on exactly #7616\'s premises)')

if __name__ == '__main__':
    main()
