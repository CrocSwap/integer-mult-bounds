#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact replay of the four courier (funded-return) moves against #7613's word.

Standard library only. Written for this package; it imports no other package
and none of #7613's or #7612's code was run (their word and invoice are vendored as data).

1. The vendored #7613 word has SHA256 21725d0c...afce (word.json.gz of
   research/p104-contact902-1091-on7612 at #7613) and applying data/edits.json
   to it gives data/word.json.gz event for event.
2. Both words are replayed over the rationals from arbitrary inputs. Legality:
   every ADD/COPY/SCALE operand sits at the event's chart, every MOVE starts at
   the register's current chart, public MOVEs strictly ascend (span inclusion),
   owned MOVEs are nested and only on live owned fields, COPY writes a zero
   field, no SCALE by 0, no self-ADD, every owned field is cleared at the chart
   it sits in, and public fields end at `final`.
3. Header identical; all 1,569 rows and end charts equal #7613's; helpers end
   at identity, owned rows end empty; owned MOVEs, lifetimes and peak unchanged.
4. The content erased at all 74 owned CLEARs equals #7613's exactly (so the
   only premise is the inherited CLEAR #44 one: owned 1557 erases
   {451:-1, 1495:1}).
5. Courier structure. Four (S, D) pairs: transit register S drops a mid-chart
   (532 and 1250 drop 744, 226 drops 907, 7 drops 922) and courier D, present
   with S at chart a, stops at S's next chart b (1464 gains 746; 990 and 779
   already stop at 127 and 245). The encode shear at a and the inverse decode
   shear at b are located in the program and checked to be elementary shears
   (determinant 1) and exact inverses in reverse order, with the encode before
   the transit MOVE and the decode after it. The 226/990 move needs 226's MOVE
   260->719 slid earlier, to just after its last chart-260 op, so that courier
   990 is co-present at 719; replay legality and row equality cover the slide.
   Only the five registers 7, 226, 532, 1250, 1464 change their MOVE chains,
   endpoints kept. Exactly three new chart pairs appear, all strictly nested.
6. Coefficients: every literal coefficient and every replayed intermediate
   coefficient has a 5-smooth denominator (main's #7000 alphabet) with the
   common grid (odd denominator lcm 1125, 2-adic exponent, numerator bits)
   within #7613's. No non-dyadic event is added.
7. Census, complete invoice (17 native calls) and kappa are recomputed and
   compared with data/invoice-*.json; #7613's crossing is reproduced.
8. Controls: corrupted words and a tampered invoice must be rejected.
"""
import collections
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
BASE_SHA256 = '21725d0c4ab84bac4d53701624c44701122a977b445d8facfb2ee7c7eba1afce'
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
DROPPED = {532: 744, 1250: 744, 226: 907, 7: 922}
ADDED = {1464: 746}
# Encode shears (program order, at the common chart a) and decode shears (at S's next chart b); each is (target, source, coeff, chart).
SHEARS = {
    '532/1464': ([(532, 1464, '-2', 3)], [(532, 1464, '2', 746)]),
    '1250/1464': ([(1464, 1250, '-2', 3)], [(1464, 1250, '2', 746)]),
    '226/990': ([(990, 226, '-1', 719)], [(990, 226, '1', 127)]),
    '7/779': ([(779, 7, '1', 743)], [(779, 7, '-1', 245)]),
}


def literal_coeffs(program):
    return [Q(e[2]) for e in program if e[0] == 'SCALE'] + [Q(e[3]) for e in program if e[0] in ('ADD', 'COPY')]


def nondyadic(program):
    return sum(1 for q in literal_coeffs(program) if q.denominator & (q.denominator - 1))


def compare(B, RB, W):
    """Everything that must hold between #7613's word B and a candidate W, except the erased-content premise.
    Returns the candidate replay and the changed registers."""
    require(all(B[k] == W[k] for k in B if k != 'program') and B.keys() == W.keys(), 'header identical')
    R = replay(W)
    n = W['public']
    bad = [r for r in range(len(R['rows'])) if R['rows'][r] != RB['rows'][r]]
    require(not bad, 'all rows equal #7613 (first differing %s)' % bad[:3])
    require(R['cur'] == RB['cur'], 'all end charts equal #7613')
    M = mains(W)
    require(all(R['rows'][r] == {r: Q(1)} for r in range(n) if r not in M), 'helpers end at identity')
    require(all(not R['rows'][r] for r in range(n, len(R['rows']))), 'owned rows end empty')
    require(R['owned_moves'] == RB['owned_moves'], 'owned MOVE multiset unchanged')
    require(R['lifetimes'] == RB['lifetimes'] and R['peak'] == RB['peak'], 'owned lifetimes and peak unchanged')
    cb, cw = clears(B), clears(W)
    require(len(cb) == len(cw), 'same number of CLEARs')
    diff = [(i, x, y) for i, (x, y) in enumerate(zip(cb, cw)) if x != y]
    require(not diff, 'CLEAR content identical to #7613 (differs at %s)' % [d[0] for d in diff[:5]])
    changed = sorted(r for r in set(R['chains']) | set(RB['chains']) if R['chains'][r] != RB['chains'][r])
    require(changed == [7, 226, 532, 1250, 1464], 'only the five transit/courier registers change chains (got %s)' % changed[:12])
    for r in changed:
        old, new = RB['chains'][r], R['chains'][r]
        require(old[0][0] == new[0][0] and old[-1][1] == new[-1][1], 'register %d chain endpoints' % r)
        co = [old[0][0]] + [b for a, b in old]
        cn = [new[0][0]] + [b for a, b in new]
        if r in DROPPED:
            require(co.count(DROPPED[r]) == 1 and cn == [c for c in co if c != DROPPED[r]],
                    'transit %d drops exactly chart %d' % (r, DROPPED[r]))
        else:
            k = co.index(ADDED[r]) if ADDED[r] in co else None
            require(k is None and ADDED[r] in cn and [c for c in cn if c != ADDED[r]] == co,
                    'courier %d gains exactly the stop %d' % (r, ADDED[r]))
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


def main():
    base_raw = (DATA / 'base-7613-word.json.gz').read_bytes()
    require(hashlib.sha256(base_raw).hexdigest() == BASE_SHA256, 'vendored #7613 word bytes')
    B = json.loads(gzip.decompress(base_raw))
    W = load_gz(DATA / 'word.json.gz')
    E = json.loads((DATA / 'edits.json').read_text())
    require(apply_edits(B['program'], E) == W['program'], 'word = #7613 word + edit list')
    print('PASS word = #7613 word (%d events) + %d deletions, %d insertions = %d events'
          % (len(B['program']), len(E['delete']), sum(len(x[1]) for x in E['insert_before']), len(W['program'])))

    RB = replay(B)
    R, changed = compare(B, RB, W)
    dim = [len(f) for f in W['frames']]
    for r in changed:
        f = lambda ch: '->'.join([str(dim[ch[0][0]])] + [str(dim[b]) for a, b in ch])
        print('PASS register %d dims %s became %s' % (r, f(RB['chains'][r]), f(R['chains'][r])))
    spans = check_shears(W)
    print('PASS shears: encode/decode of the four courier pairs located, elementary, exact inverses in reverse order,'
          ' encode before and decode after the transit MOVE; 226/990 needs the MOVE 226 260->719 slid earlier, checked by replay legality')
    print('PASS exact replay: legal, all %d rows and end charts equal #7613, helpers identity, owned empty;'
          ' owned MOVEs (%d), lifetimes (%d) and peak (%d) unchanged'
          % (len(R['rows']), sum(R['owned_moves'].values()), sum(R['lifetimes'].values()), R['peak']))

    cl = clears(W)
    require(len(cl) == 74, 'all 74 CLEARs present')
    row44 = dict(cl[44][1])
    require(cl[44][0] == 1557 and row44 == {451: Q(-1), 1495: Q(1)}, 'CLEAR #44 (owned 1557) erases {451:-1, 1495:1}')
    print('PASS CLEAR content: all 74 CLEARs erase exactly #7613 content (CLEAR #44, owned 1557, erases {451:-1, 1495:1}: the inherited premise row, unchanged)')

    key = lambda W_, i: tuple(W_['frames'][i])
    pairs = lambda W_: {(key(W_, e[2]), key(W_, e[3])) for e in W_['program'] if e[0] == 'MOVE'}
    ipairs = lambda W_: {(e[2], e[3]) for e in W_['program'] if e[0] == 'MOVE'}
    newp = sorted(ipairs(W) - ipairs(B))
    require(newp == [(3, 746), (719, 127), (743, 245)], 'exactly three new chart pairs (got %s)' % newp)
    require(len(pairs(W) - pairs(B)) == 3, 'three new frame pairs')
    gaps = []
    for a, b in newp:
        require(span(W['frames'][a]) < span(W['frames'][b]) or span(W['frames'][b]) < span(W['frames'][a]), 'new pair nested')
        gaps.append(abs(dim[b] - dim[a]))
    require(gaps == [6, 3, 2], 'dimension gaps of the new pairs')
    for a, b in pairs(W):
        require(span(a) < span(b) or span(b) < span(a), 'every pair nested')
    print('PASS 3 new chart pairs %s, all strictly nested, dimension gaps %s' % (newp, gaps))
    ops = lambda P: collections.Counter(e[0] for e in P)
    d = ops(W['program']); d.subtract(ops(B['program']))
    require({k: v for k, v in d.items() if v} == {'ADD': 3, 'MOVE': -3}, 'event delta per native call: ADD +3, MOVE -3')
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
    require(nw == nb, 'no non-dyadic literal event is added')
    require(sw['max_den_exp'] <= sb['max_den_exp'] and sw['odd_den'] == sb['odd_den']
            and sw['max_num_bits'] <= sb['max_num_bits'], 'intermediate coefficient grid within #7613')
    print('PASS coefficients: 5-smooth denominators (main #7000 alphabet); non-dyadic literal events %d -> %d (none added);'
          ' grid within #7613 (2-adic exponent %d, odd denominator lcm %d, numerator bits %d)'
          % (nb, nw, sw['max_den_exp'], sw['odd_den'], sw['max_num_bits']))

    cb, cw = census(B, RB), census(W, R)
    require(cw['helpers'] == cb['helpers'] and cw['rises'] == cb['rises'], 'helper targets and owned rises unchanged')
    dpaid = collections.Counter({int(k): v for k, v in cw['paid'].items()})
    dpaid.subtract({int(k): v for k, v in cb['paid'].items()})
    dpaid = {k: v for k, v in sorted(dpaid.items()) if v}
    require(dpaid == {1: -2, 3: -2, 4: -1, 6: 2}, 'native paid delta {1:-2, 3:-2, 4:-1, 6:+2}')
    print('PASS native paid delta per call', dpaid)
    inv0 = json.loads((DATA / 'invoice-7613.json').read_text())
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
    require((paid0, paid1) == (110247, 110196), 'paid positions')
    print('PASS complete invoice: paid positions %d -> %d, productive %d, S = %d' % (paid0, paid1, sum(T.values()), S))

    k0, k1 = crossing(inv0['targets'], inv0['paid']), crossing(T, Pn)
    lo, hi = decimal.Decimal('0.0036530568656'), decimal.Decimal('0.0036530568657')
    require(lo <= k0 <= hi, '#7613 crossing reproduced')
    print('PASS kappa #7613 %s' % k0)
    print('PASS kappa new   %s (ratio over #7613 %s)' % (k1, +decimal.Context(prec=12).divide(k1, k0)))
    expected = json.loads((HERE / 'EXPECTED.json').read_text())
    require(str(k1)[:len(expected['kappa_prefix'])] == expected['kappa_prefix'], 'kappa digits as recorded')
    require(k1 > decimal.Decimal('0.00365455370060'), 'claim 0.00365455215235 is below the exact crossing')

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
    rejected('532 decode dropped', lambda P: P.pop(idx(['ADD', 532, 1464, '2', 746])))
    rejected('779 decode dropped', lambda P: P.pop(idx(['ADD', 779, 7, '-1', 245])))
    rejected('7 encode dropped', lambda P: P.pop(idx(['ADD', 779, 7, '1', 743])))
    mk = idx(['MOVE', 1464, 744, 746, False])
    rejected('courier 1464 skips its new stop 746', lambda P: P.__setitem__(mk, ['MOVE', 1464, 744, 916, False]))
    ms = idx(['MOVE', 532, 3, 746, False])
    rejected('transit MOVE 532 placed after its decode', lambda P: (P.pop(ms), P.insert(idx(['ADD', 532, 1464, '2', 746]) + 1, ['MOVE', 532, 3, 746, False])))
    rejected('ownership flag flipped on a transit MOVE', lambda P: P.__setitem__(ms, ['MOVE', 532, 3, 746, True]))
    m7 = idx(['MOVE', 7, 743, 245, False])
    rejected('MOVE 7 reversed', lambda P: P.__setitem__(m7, ['MOVE', 7, 245, 743, False]))
    rejected('MOVE 7 to a non-nested chart (128)', lambda P: P.__setitem__(m7, ['MOVE', 7, 743, 128, False]))
    rejected('encode retagged at the dropped chart 922', lambda P: P.__setitem__(idx(['ADD', 779, 7, '1', 743]), ['ADD', 779, 7, '1', 922]))
    bare = copy.deepcopy(B['program'])
    i7 = bare.index(['MOVE', 7, 743, 922, False]); j7 = bare.index(['MOVE', 7, 922, 245, False])
    Xb = copy.deepcopy(B); Xb['program'] = bare[:i7] + [['MOVE', 7, 743, 245, False]] + [e for e in bare[i7 + 1:j7]] + bare[j7 + 1:]
    try:
        compare(B, RB, Xb)
        raise SystemExit('control not rejected: bare hop deletion')
    except AssertionError as exc:
        print('PASS control rejected: bare hop deletion of 7 at 922 without a courier (%s)' % exc)
    bad = dict(Pn); bad['3'] -= 1
    require(json.loads((DATA / 'invoice-new.json').read_text()) != invoice_json(bad, T), 'tampered invoice differs')
    print('PASS control rejected: invoice with one rank-3 job removed differs from the recomputed one')
    print('PASS_FOUR_COURIERS_EXACT (conditional on the inherited CLEAR #44 premise)')


if __name__ == '__main__':
    sys.exit(main())
