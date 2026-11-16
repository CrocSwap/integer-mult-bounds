#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact replay of a courier move and a helper re-stop applied to #7620's word.

Standard library only. Written for this package; it imports no other package
and none of #7620's, #7617's or #7615's code was run (their word, invoice and
the pinned affected-pair census are vendored or copied as data).

1. The vendored #7620 word has compressed SHA256 2eb2cf1d...a81c (data/word.json.gz
   of research/p104-stationary-primal-dual at #7620) and applying data/edits.json
   gives data/word.json.gz event for event (the new word's hash is pinned too).
2. Both words are replayed over the rationals from arbitrary inputs. Legality:
   every ADD/COPY/SCALE operand sits at the event's chart, every MOVE starts at
   the register's current chart, public MOVEs strictly ascend (span inclusion),
   owned MOVEs are nested and only on live owned fields, COPY writes a zero
   field, no SCALE by 0, no self-ADD, every owned field is cleared at the chart
   it sits in, and public fields end at `final`.
3. Header identical; all 1,569 rows and end charts equal #7620's; helpers end
   at identity, owned rows end empty; owned MOVEs, all 167 lifetimes, peak 50
   and the 68 owned labels unchanged; event census pinned (77,194 -> 77,196).
4. The content erased at all 167 CLEARs (74 + 93 stationary) equals #7620's
   exactly, so the premises are exactly #7620's.
5. Structure. Only registers 226, 1445 and 1461 change their MOVE chains
   (endpoints kept). (a) Courier: transit 1445 drops chart 755 (3->755->757
   becomes 3->757); courier 1461, present with 1445 at chart 3, gains the
   stop 757 (3->755->924 becomes 3->755->757->924). The encode shears at chart
   3 and the inverse decode shears at 757 are located and checked as elementary
   shears (determinant 1), exact inverses in reverse order, encode before the
   transit MOVE and decode after it. (b) Re-stop: helper 226 goes
   3->86->260->906->127 instead of ...->719->127 (its dimensions 3,6,9 become
   3,7,9); its decode of courier 990 at chart 127 is unchanged and the encode
   ADD 990 -= 226 moves to chart 260. Exactly two new chart pairs, (3,757) and
   (260,906), appear, both strictly nested; (719,127) and (755,924) leave the
   MOVE pairs.
6. Coefficients: every literal and replayed coefficient has a 5-smooth
   denominator (main's #7000 alphabet) with the common grid equal to #7620's.
   Non-dyadic literal events 5,901 -> 5,903 (+2/3 and -2/3).
7. Census, complete invoice (17 native calls) and kappa are recomputed and
   compared with data/invoice-*.json; #7620's crossing is reproduced.
8. Affected-pair column tests (own implementation, section at the end): the 837
   chart pairs pinned by #7620's native runner (data/affected-pairs-7620.json),
   minus (719,127) (no longer a route of any changed register) plus the 10
   pairs on the new routes of the changed registers (846 in all) are tested:
   512 forward and 512 adjoint exact Gaussian columns, signed Pauli action,
   absolute phase, exact public ascent rank, and a wrong-phase rejection for
   each pair.
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
BASE_SHA256 = '2eb2cf1d29529c68a6cb1c0639de3065a805858d3492068e76b70c5a5e80a81c'
WORD_SHA256 = 'ff8cc4ac45dc89c6dfca54d1954b21edefe599c14d31b2ead7ceeafe3bed1ec8'
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


# Expected route changes (old chart sequence -> new), endpoints kept.
ROUTES = {
    226: ([3, 86, 260, 719, 127], [3, 86, 260, 906, 127]),
    1445: ([3, 755, 757, 923, 127], [3, 757, 923, 127]),
    1461: ([3, 755, 924, 127], [3, 755, 757, 924, 127]),
}
# Encode shears (program order, at the common chart a) and decode shears (at the transit's next chart b); each is (target, source, coeff, chart).
SHEARS = {
    '1445/1461': ([(1461, 1445, '-2', 3), (1445, 1461, '2/3', 3)], [(1445, 1461, '-2/3', 757), (1461, 1445, '2', 757)]),
    '226/990': ([(990, 226, '-1', 260)], [(990, 226, '1', 127)]),
}


def literal_coeffs(program):
    return [Q(e[2]) for e in program if e[0] == 'SCALE'] + [Q(e[3]) for e in program if e[0] in ('ADD', 'COPY')]


def nondyadic(program):
    return sum(1 for q in literal_coeffs(program) if q.denominator & (q.denominator - 1))


def compare(B, RB, W):
    """Everything that must hold between #7620's word B and a candidate W, except the erased-content premise.
    Returns the candidate replay and the changed registers."""
    require(all(B[k] == W[k] for k in B if k != 'program') and B.keys() == W.keys(), 'header identical')
    R = replay(W)
    n = W['public']
    bad = [r for r in range(len(R['rows'])) if R['rows'][r] != RB['rows'][r]]
    require(not bad, 'all rows equal #7620 (first differing %s)' % bad[:3])
    require(R['cur'] == RB['cur'], 'all end charts equal #7620')
    M = mains(W)
    require(all(R['rows'][r] == {r: Q(1)} for r in range(n) if r not in M), 'helpers end at identity')
    require(all(not R['rows'][r] for r in range(n, len(R['rows']))), 'owned rows end empty')
    require(R['owned_moves'] == RB['owned_moves'], 'owned MOVE multiset unchanged')
    require(R['lifetimes'] == RB['lifetimes'] and R['peak'] == RB['peak'], 'owned lifetimes and peak unchanged')
    cb, cw = clears(B), clears(W)
    require(len(cb) == len(cw), 'same number of CLEARs')
    diff = [(i, x, y) for i, (x, y) in enumerate(zip(cb, cw)) if x != y]
    require(not diff, 'CLEAR content identical to #7620 (differs at %s)' % [d[0] for d in diff[:5]])
    changed = sorted(r for r in set(R['chains']) | set(RB['chains']) if R['chains'][r] != RB['chains'][r])
    require(changed == sorted(ROUTES), 'only registers 226, 1445, 1461 change chains (got %s)' % changed[:12])
    for r in changed:
        old, new = RB['chains'][r], R['chains'][r]
        require(old[0][0] == new[0][0] and old[-1][1] == new[-1][1], 'register %d chain endpoints' % r)
        co = [old[0][0]] + [b for a, b in old]
        cn = [new[0][0]] + [b for a, b in new]
        require((co, cn) == ROUTES[r], 'register %d route %s -> %s as expected' % (r, co, cn))
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
    """Pinned #7620 census (837 pairs; affected versus #7481) adjusted for the changed routes of 226, 1445, 1461:
    (719,127) leaves (226 no longer visits 719); every old- or new-route pair of the three registers not pinned joins (10 pairs)."""
    pinned = {tuple(p) for p in json.loads((DATA / 'affected-pairs-7620.json').read_text())}
    require(len(pinned) == 837, 'pinned census has 837 pairs')
    routes = lambda X, r: [tuple(e[2:4]) for e in X['program'] if e[0] == 'MOVE' and e[1] == r]
    newr, oldr = set(), set()
    for r in ROUTES:
        newr |= set(routes(W, r))
        oldr |= set(routes(B, r))
    mp = lambda X: {tuple(e[2:4]) for e in X['program'] if e[0] == 'MOVE'}
    dropped = {(719, 127)}
    require(dropped <= pinned and not dropped & mp(W) and not dropped & newr, '(719,127) is pinned but no longer a MOVE pair of the new word')
    added = (newr | oldr) - pinned
    require(added == {(3, 755), (3, 757), (260, 906), (755, 757), (755, 924), (757, 923), (757, 924), (906, 127), (923, 127), (924, 127)},
            'the 10 added pairs are exactly the old- or new-route pairs of the changed registers outside the pinned census (got %s)' % sorted(added))
    require((newr | oldr) - added <= pinned, 'every other old- or new-route pair is pinned')
    allp = (pinned - dropped) | added
    require(len(allp) == 846, 'census has 846 pairs')
    return pinned, added, allp


def columns_section(B, W):
    ipairs = lambda W_: {(e[2], e[3]) for e in W_['program'] if e[0] == 'MOVE'}
    pinned, added, allp = affected_pairs(B, W)
    wp = ipairs(W)
    require(all(0 <= p[0] < len(W['frames']) and 0 <= p[1] < len(W['frames']) for p in allp), 'pair indices are charts')
    require(ipairs(W) - ipairs(B) <= allp, 'every new MOVE pair is tested')
    in_word = sum(1 for p in allp if p in wp)
    print('affected pairs: %d pinned by #7620 - 1 dropped (719,127) + %d on the old or new routes of the changed registers = %d (%d are MOVE pairs of the new word, the rest are the pinned #7481-comparator pairs)'
          % (len(pinned), len(added), len(allp), in_word))
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
        pair_columns(frames, 260, 128)
    require(not (span(frames[260]) < span(frames[128]) or span(frames[128]) < span(frames[260])), 'control pair is not nested')
    col_rejected('column test rejects the non-nested pair (260,128)', non_nested)
    exp_of = lambda a, b: dagger(frame_circuit(frames[a])) + frame_circuit(frames[b])
    for a, b in ((3, 757), (260, 906)):
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


def main():
    base_raw = (DATA / 'base-7620-word.json.gz').read_bytes()
    require(hashlib.sha256(base_raw).hexdigest() == BASE_SHA256, 'vendored #7620 word bytes')
    word_raw = (DATA / 'word.json.gz').read_bytes()
    require(hashlib.sha256(word_raw).hexdigest() == WORD_SHA256, 'new word bytes')
    B = json.loads(gzip.decompress(base_raw))
    W = load_gz(DATA / 'word.json.gz')
    E = json.loads((DATA / 'edits.json').read_text())
    require(apply_edits(B['program'], E) == W['program'], 'word = #7620 word + edit list')
    require(len(B['program']) == 77194 and len(W['program']) == 77196, 'event census 77,194 -> 77,196')
    print('PASS word = #7620 word (%d events) + %d deletions, %d insertions = %d events; word sha256 %s'
          % (len(B['program']), len(E['delete']), sum(len(x[1]) for x in E['insert_before']), len(W['program']), WORD_SHA256[:12]))

    RB = replay(B)
    R, changed = compare(B, RB, W)
    dim = [len(f) for f in W['frames']]
    for r in changed:
        f = lambda ch: '->'.join([str(dim[ch[0][0]])] + [str(dim[b]) for a, b in ch])
        print('PASS register %d dims %s became %s' % (r, f(RB['chains'][r]), f(R['chains'][r])))
    check_shears(W)
    print('PASS shears: encode/decode of the 1445/1461 courier and the 226/990 pair located, elementary, exact inverses in reverse order,'
          ' encode before and decode after the transit MOVE; the 226 re-stop and the earlier 990 encode are checked by replay legality')
    print('PASS exact replay: legal, all %d rows and end charts equal #7620, helpers identity, owned empty;'
          ' owned MOVEs (%d), lifetimes (%d), peak (%d) unchanged'
          % (len(R['rows']), sum(R['owned_moves'].values()), sum(R['lifetimes'].values()), R['peak']))
    require((sum(R['lifetimes'].values()), R['peak']) == (167, 50), 'census (167 lifetimes, peak 50)')
    owned_labels = {e[1] for e in W['program'] if e[0] == 'INIT'}
    require(len(owned_labels) == 68 and len(owned_labels) == W['owned_fields'], '68 owned labels')

    cl = clears(W)
    require(len(cl) == 167, 'all 167 CLEARs present')
    nz = sum(1 for _, c in cl if c)
    print('PASS CLEAR content: all 167 CLEARs (74 + 93 stationary) erase exactly #7620 content (%d nonzero, %d zero); no new premise' % (nz, 167 - nz))

    key = lambda W_, i: tuple(W_['frames'][i])
    pairs = lambda W_: {(key(W_, e[2]), key(W_, e[3])) for e in W_['program'] if e[0] == 'MOVE'}
    ipairs = lambda W_: {(e[2], e[3]) for e in W_['program'] if e[0] == 'MOVE'}
    newp = sorted(ipairs(W) - ipairs(B))
    require(newp == [(3, 757), (260, 906)], 'exactly two new chart pairs (got %s)' % newp)
    require(sorted(ipairs(B) - ipairs(W)) == [(719, 127), (755, 924)], 'pairs leaving: (719,127), (755,924)')
    require(len(pairs(W) - pairs(B)) == 2, 'two new frame pairs')
    for a, b in newp:
        require(span(W['frames'][a]) < span(W['frames'][b]), 'new pair %s strictly nested' % ((a, b),))
    require([(dim[a], dim[b]) for a, b in newp] == [(0, 6), (3, 7)], 'new pair dims 0->6 and 3->7')
    for pa, pb in pairs(W):
        require(span(pa) < span(pb) or span(pb) < span(pa), 'every pair nested')
    print('PASS new chart pairs %s, strictly nested, dims %s' % (newp, [(dim[a], dim[b]) for a, b in newp]))
    ops = lambda P: collections.Counter(e[0] for e in P)
    d = ops(W['program']); d.subtract(ops(B['program']))
    require({k: v for k, v in d.items() if v} == {'ADD': 2}, 'event delta per native call: ADD +2')
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
    require((nb, nw) == (5901, 5903), 'non-dyadic literal events 5901 -> 5903 (+2/3, -2/3)')
    require(sw['max_den_exp'] <= sb['max_den_exp'] and sw['odd_den'] == sb['odd_den']
            and sw['max_num_bits'] <= sb['max_num_bits'], 'intermediate coefficient grid within #7620')
    print('PASS coefficients: 5-smooth denominators (main #7000 alphabet); non-dyadic literal events %d -> %d;'
          ' grid equal to #7620 (2-adic exponent %d, odd denominator lcm %d, numerator bits %d)'
          % (nb, nw, sw['max_den_exp'], sw['odd_den'], sw['max_num_bits']))

    cb, cw = census(B, RB), census(W, R)
    require(cw['helpers'] == cb['helpers'] and cw['rises'] == cb['rises'], 'helper targets and owned rises unchanged')
    dpaid = collections.Counter({int(k): v for k, v in cw['paid'].items()})
    dpaid.subtract({int(k): v for k, v in cb['paid'].items()})
    dpaid = {k: v for k, v in sorted(dpaid.items()) if v}
    require(dpaid == {1: 1, 2: 1, 3: -3, 6: 1}, 'native paid delta {1:+1, 2:+1, 3:-3, 6:+1}')
    print('PASS native paid delta per call', dpaid)
    inv0 = json.loads((DATA / 'invoice-7620.json').read_text())
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
    require(json.loads((DATA / 'invoice-old.json').read_text()) == invoice_json(P0, T), 'invoice-old.json is #7620 invoice in the official schema')
    paid1 = sum(Pn.values())
    require((paid0, paid1) == (110145, 110145), 'paid positions 110145 unchanged')
    print('PASS complete invoice: paid positions %d -> %d, productive %d, S = %d' % (paid0, paid1, sum(T.values()), S))

    k0, k1 = crossing(T, P0), crossing(T, Pn)
    lo, hi = decimal.Decimal('0.0036611026181'), decimal.Decimal('0.0036611026182')
    require(lo <= k0 <= hi, '#7620 crossing reproduced')
    print('PASS kappa #7620 %s' % k0)
    print('PASS kappa new   %s (ratio over #7620 %s)' % (k1, +decimal.Context(prec=12).divide(k1, k0)))
    expected = json.loads((HERE / 'EXPECTED.json').read_text())
    require(str(k1)[:len(expected['kappa_prefix'])] == expected['kappa_prefix'], 'kappa digits as recorded')
    require(k1 > decimal.Decimal('0.0036614625547'), 'claim 0.0036614625547 is below the exact crossing')

    if MODE == 'columns':
        columns_section(B, W)
        print('PASS_COLUMNS_ON_7620')
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
            print('PASS control rejected: %s (%s)' % (label, str(exc)[:110]))
            return
        raise AssertionError('control not rejected: ' + label)
    P_ = W['program']
    idx = lambda ev: P_.index(ev)
    # courier 1445/1461
    e1 = idx(['ADD', 1461, 1445, '-2', 3])
    e2 = idx(['ADD', 1445, 1461, '2/3', 3])
    d1 = idx(['ADD', 1445, 1461, '-2/3', 757])
    d2 = idx(['ADD', 1461, 1445, '2', 757])
    rejected('1461/1445 encode coefficient -2 -> -1', lambda P: P.__setitem__(e1, ['ADD', 1461, 1445, '-1', 3]))
    rejected('1445/1461 encode coefficient 2/3 -> 1/3', lambda P: P.__setitem__(e2, ['ADD', 1445, 1461, '1/3', 3]))
    rejected('first encode dropped', lambda P: P.pop(e1))
    rejected('second encode dropped', lambda P: P.pop(e2))
    rejected('first decode dropped', lambda P: P.pop(d1))
    rejected('second decode dropped', lambda P: P.pop(d2))
    rejected('first decode sign flipped', lambda P: P.__setitem__(d1, ['ADD', 1445, 1461, '2/3', 757]))
    rejected('second decode sign flipped', lambda P: P.__setitem__(d2, ['ADD', 1461, 1445, '-2', 757]))
    ms = idx(['MOVE', 1445, 3, 757, False])
    rejected('transit MOVE 1445 placed after its decode', lambda P: (P.pop(ms), P.insert(d1, ['MOVE', 1445, 3, 757, False])))
    rejected('ownership flag flipped on the transit MOVE', lambda P: P.__setitem__(ms, ['MOVE', 1445, 3, 757, True]))
    rejected('transit MOVE 1445 kept at 755 (3->755)', lambda P: P.__setitem__(ms, ['MOVE', 1445, 3, 755, False]))
    m1461 = idx(['MOVE', 1461, 755, 757, False])
    rejected('courier 1461 MOVE 755->757 reversed', lambda P: P.__setitem__(m1461, ['MOVE', 1461, 757, 755, False]))
    rejected('courier 1461 MOVE to a non-nested chart (128)', lambda P: P.__setitem__(m1461, ['MOVE', 1461, 755, 128, False]))
    rejected('395 read left at the old coefficient 1/2', lambda P: P.__setitem__(idx(['ADD', 1461, 395, '-3/2', 755]), ['ADD', 1461, 395, '1/2', 755]))
    # helper 226 / courier 990
    g1 = idx(['ADD', 990, 226, '-1', 260])
    g2 = idx(['ADD', 990, 226, '1', 127])
    rejected('226/990 encode coefficient -1 -> -1/2', lambda P: P.__setitem__(g1, ['ADD', 990, 226, '-1/2', 260]))
    rejected('226/990 encode dropped', lambda P: P.pop(g1))
    rejected('226/990 decode dropped', lambda P: P.pop(g2))
    rejected('226/990 decode sign flipped', lambda P: P.__setitem__(g2, ['ADD', 990, 226, '-1', 127]))
    rejected('226/990 encode retagged at the old chart 719', lambda P: P.__setitem__(g1, ['ADD', 990, 226, '-1', 719]))
    m226 = idx(['MOVE', 226, 260, 906, False])
    rejected('226 MOVE 260->906 ownership flag flipped', lambda P: P.__setitem__(m226, ['MOVE', 226, 260, 906, True]))
    rejected('226 MOVE 906->127 reversed', lambda P: P.__setitem__(idx(['MOVE', 226, 906, 127, False]), ['MOVE', 226, 127, 906, False]))
    rejected('226 MOVE to a non-nested chart (128)', lambda P: P.__setitem__(idx(['MOVE', 226, 906, 127, False]), ['MOVE', 226, 906, 128, False]))
    rejected('226 re-stop MOVE placed after 473+=226 at 906', lambda P: (P.pop(m226), P.insert(idx(['ADD', 473, 226, '1', 906]) + 1, ['MOVE', 226, 260, 906, False])))
    rejected('MOVE 473 719->906 left at its old place', lambda P: (P.pop(idx(['MOVE', 473, 719, 906, False])), P.append(['MOVE', 473, 719, 906, False])))
    bad = dict(Pn); bad['3'] -= 1
    require(json.loads((DATA / 'invoice-new.json').read_text()) != invoice_json(bad, T), 'tampered invoice differs')
    print('PASS control rejected: invoice with one rank-3 job removed differs from the recomputed one')
    print('PASS_COURIER_RESTOP_ON_7620_EXACT (conditional on exactly #7620\'s premises)')


if __name__ == '__main__':
    main()
