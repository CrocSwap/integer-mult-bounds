#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact replay of the hosted-main-902 drop against #7605's word.

Standard library only. Written for this package; it imports no other package.

1. The vendored #7605 word has the SHA256 of research/p104-timed-helper757/
   data/word.json.gz at #7605 head e1d2756eecf03e146338239fee81772a99ba8d4c,
   and applying data/edits.json to it gives data/word.json.gz event for event.
2. Both words are replayed over the rationals from arbitrary inputs (every
   public field starts as its own symbol, owned fields start at INIT as 0).
   Legality: every ADD/COPY/SCALE operand sits at the event's chart, every
   MOVE starts at the register's current chart, public MOVEs strictly ascend
   (span inclusion), owned MOVEs are nested and only on live owned fields,
   COPY writes a zero field, no SCALE by 0, no self-ADD, every owned field
   is cleared at the chart it sits in, and public fields end at `final`.
3. Header identical; all 1,569 rows and end charts equal #7605's; helpers end
   at identity, owned rows end empty; owned MOVEs, lifetimes and peak are
   unchanged.
4. THE PREMISE. The content erased at the 74 owned CLEARs is compared with
   #7605's. Exactly one differs: CLEAR #44 (owned field 1557, chart 595,
   event 42713 of the new word). #7605 erases {451:-1, 902:-3/2, 985:-3/2,
   1495:1}; the new word erases {451:-1, 1495:1}. The check prints both rows
   and requires that this is the only difference. This is what makes the
   claim conditional.
5. Only main 902 changes its MOVE chain (0->1->3 becomes 0->3), endpoints kept.
6. Census, complete invoice (17 native calls) and kappa are recomputed and
   compared with data/invoice-*.json; #7605's crossing is reproduced.
7. Controls: corrupted words and a tampered invoice must be rejected.
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
BASE_SHA256 = '37358c493d18ebc6be386aebb4c17529b38883674731f7009ef4e96a5313467d'
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
    stats = dict(max_den_exp=0, odd_den=1, max_num_bits=0)

    def note(q):
        d = q.denominator
        e = (d & -d).bit_length() - 1
        stats['max_den_exp'] = max(stats['max_den_exp'], e)
        odd = d >> e
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


PREMISE_BASE = (451, Q(-1)), (902, Q(-3, 2)), (985, Q(-3, 2)), (1495, Q(1))
PREMISE_NEW = (451, Q(-1)), (1495, Q(1))


def compare(B, RB, W):
    """Everything that must hold between #7605's word B and a candidate W, except the erased-content premise.
    Returns the candidate replay, the changed chains and the list of differing CLEARs (index, base, new)."""
    require(all(B[k] == W[k] for k in B if k != 'program') and B.keys() == W.keys(), 'header identical')
    R = replay(W)
    n = W['public']
    bad = [r for r in range(len(R['rows'])) if R['rows'][r] != RB['rows'][r]]
    require(not bad, 'all rows equal #7605 (first differing %s)' % bad[:3])
    require(R['cur'] == RB['cur'], 'all end charts equal #7605')
    M = mains(W)
    require(all(R['rows'][r] == {r: Q(1)} for r in range(n) if r not in M), 'helpers end at identity')
    require(all(not R['rows'][r] for r in range(n, len(R['rows']))), 'owned rows end empty')
    require(R['owned_moves'] == RB['owned_moves'], 'owned MOVE multiset unchanged')
    require(R['lifetimes'] == RB['lifetimes'] and R['peak'] == RB['peak'], 'owned lifetimes and peak unchanged')
    cb, cw = clears(B), clears(W)
    require(len(cb) == len(cw), 'same number of CLEARs')
    diff = [(i, x, y) for i, (x, y) in enumerate(zip(cb, cw)) if x != y]
    changed = sorted(r for r in set(R['chains']) | set(RB['chains']) if R['chains'][r] != RB['chains'][r])
    require(changed == [902], 'only main 902 changes its chain (got %s)' % changed[:5])
    require(all(r in M for r in changed), 'changed registers are mains')
    for r in changed:
        old, new = RB['chains'][r], R['chains'][r]
        require(old[0][0] == new[0][0] and old[-1][1] == new[-1][1], 'register %d chain endpoints' % r)
    return R, changed, diff


def main():
    base_raw = (DATA / 'base-7605-word.json.gz').read_bytes()
    require(hashlib.sha256(base_raw).hexdigest() == BASE_SHA256, 'vendored #7605 word bytes')
    B = json.loads(gzip.decompress(base_raw))
    W = load_gz(DATA / 'word.json.gz')
    E = json.loads((DATA / 'edits.json').read_text())
    require(apply_edits(B['program'], E) == W['program'], 'word = #7605 word + edit list')
    print('PASS word = #7605 word (%d events) + %d deletions, %d insertions = %d events'
          % (len(B['program']), len(E['delete']), sum(len(x[1]) for x in E['insert_before']), len(W['program'])))

    RB = replay(B)
    R, changed, diff = compare(B, RB, W)
    dim = [len(f) for f in W['frames']]
    for r in changed:
        f = lambda ch: '->'.join([str(dim[ch[0][0]])] + [str(dim[b]) for a, b in ch])
        print('PASS main %d dims %s became %s' % (r, f(RB['chains'][r]), f(R['chains'][r])))
    print('PASS exact replay: legal, all %d rows and end charts equal #7605, helpers identity, owned empty;'
          ' owned MOVEs (%d), lifetimes (%d) and peak (%d) unchanged'
          % (len(R['rows']), sum(R['owned_moves'].values()), sum(R['lifetimes'].values()), R['peak']))

    fmt = lambda row: '{' + ', '.join('%d:%s' % (k, v) for k, v in row) + '}'
    require(len(diff) == 1, 'exactly one CLEAR erases different content (got %d)' % len(diff))
    i, x, y = diff[0]
    require(i == 44 and x[0] == y[0] == 1557, 'the differing CLEAR is #44 on owned field 1557')
    require(x[1] == PREMISE_BASE and y[1] == PREMISE_NEW, 'erased rows as stated')
    print('PREMISE CLEAR #%d of %d (owned %d): #7605 erases %s, new word erases %s; the other %d CLEARs are identical'
          % (i, len(clears(B)), x[0], fmt(x[1]), fmt(y[1]), len(clears(B)) - 1))

    key = lambda W_, i: tuple(W_['frames'][i])
    pairs = lambda W_: {(key(W_, e[2]), key(W_, e[3])) for e in W_['program'] if e[0] == 'MOVE'}
    require(pairs(W) <= pairs(B), 'no new chart pair')
    print('PASS no new chart pair: every MOVE of the new word is a chart pair #7605 already uses')
    ops = lambda P: collections.Counter(e[0] for e in P)
    d = ops(W['program']); d.subtract(ops(B['program']))
    require({k: v for k, v in d.items() if v} == {'ADD': -4, 'MOVE': -1}, 'event delta -4 ADD, -1 MOVE')
    sb, sw = RB['stats'], R['stats']
    require(sw['max_den_exp'] <= sb['max_den_exp'] and sw['odd_den'] == sb['odd_den']
            and sw['max_num_bits'] <= sb['max_num_bits'], 'intermediate coefficient grid within #7605')
    print('PASS intermediate coefficients within #7605 (2-adic exponent %d, odd denominator lcm %d, numerator bits %d)'
          % (sw['max_den_exp'], sw['odd_den'], sw['max_num_bits']))
    print('PASS event delta per native call', {k: v for k, v in sorted(d.items()) if v})

    cb, cw = census(B, RB), census(W, R)
    require(cw['helpers'] == cb['helpers'] and cw['rises'] == cb['rises'], 'helper targets and owned rises unchanged')
    dpaid = collections.Counter({int(k): v for k, v in cw['paid'].items()})
    dpaid.subtract({int(k): v for k, v in cb['paid'].items()})
    dpaid = {k: v for k, v in sorted(dpaid.items()) if v}
    require(dpaid == {1: -1, 2: -1, 3: 1}, 'native paid delta {1:-1, 2:-1, 3:+1}')
    print('PASS native paid delta per call', dpaid)
    inv0 = json.loads((DATA / 'invoice-7605.json').read_text())
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
    require((paid0, paid1) == (110366, 110349), 'paid positions')
    print('PASS complete invoice: paid positions %d -> %d, productive %d, S = %d' % (paid0, paid1, sum(T.values()), S))

    k0, k1 = crossing(inv0['targets'], inv0['paid']), crossing(T, Pn)
    lo, hi = decimal.Decimal('0.0036504442446'), decimal.Decimal('0.0036504442448')
    require(lo <= k0 <= hi, '#7605 published crossing reproduced')
    print('PASS kappa #7605 %s (inside the published #7605 enclosure)' % k0)
    print('PASS kappa new   %s (ratio %s)' % (k1, +decimal.Context(prec=12).divide(k1, k0)))
    expected = json.loads((HERE / 'EXPECTED.json').read_text())
    require(str(k1)[:26] == expected['kappa_26'], 'kappa digits as recorded')

    def rejected(label, mutate):
        X = copy.deepcopy(W)
        mutate(X['program'])
        try:
            R2, _, diff2 = compare(B, RB, X)
            require(len(diff2) == 1 and diff2[0][0] == 44, 'only the premise CLEAR differs')
        except AssertionError as exc:
            print('PASS control rejected: %s (%s)' % (label, exc))
            return
        raise AssertionError('control not rejected: ' + label)
    P0 = W['program']
    i = P0.index(['MOVE', 902, 3, 618, False])
    rejected('re-add 1479 += -1/2*902 at chart 618 (operand absent)',
             lambda P: P.insert(i + 1, ['ADD', 1479, 902, '-1/2', 618]))
    rejected('1557 += 1*1495 coefficient changed to 2',
             lambda P: P.__setitem__(P.index(['ADD', 1557, 1495, '1', 595]), ['ADD', 1557, 1495, '2', 595]))
    rejected('3->618 MOVE replaced by 3->595 without 595->618',
             lambda P: P.__setitem__(i, ['MOVE', 902, 3, 595, False]))
    rejected('owned write at 595 after 902 has left',
             lambda P: P.insert(i + 1, ['ADD', 1532, 902, '2', 595]))
    rejected('descending public MOVE 902 618->3', lambda P: P.__setitem__(i, ['MOVE', 902, 618, 3, False]))

    def partial(P):  # the drop on #7605 with only the 1495 ADD removed
        P[:] = copy.deepcopy(B['program'])
        P.remove(['ADD', 1495, 902, '-3/2', 595])
    rejected('partial drop on #7605 (only 1495 += -3/2*902 deleted)', partial)
    bad = dict(Pn); bad['3'] -= 1
    require(json.loads((DATA / 'invoice-new.json').read_text()) != invoice_json(bad, T), 'tampered invoice differs')
    print('PASS control rejected: invoice with one rank-3 job removed differs from the recomputed one')
    print('PASS_DUAL_SCAN_DROP_902_EXACT (conditional on the CLEAR #44 premise)')


if __name__ == '__main__':
    sys.exit(main())
