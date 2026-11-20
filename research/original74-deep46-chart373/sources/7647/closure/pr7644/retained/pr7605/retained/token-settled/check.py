#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact replay of the token-settled helper drops against #7546's word.

Standard library only. Written for this package; it imports no other package.

1. The vendored #7546 word has the SHA256 of expected/role902-WORD.json.gz
   at #7546 head 99438c43df7aac1e5dbcc43c1578fcd886c119ec, and applying the
   edit list data/edits.json to it gives data/word.json.gz event for event.
2. Both words are replayed over the rationals from arbitrary inputs (every
   public field starts as its own symbol, owned fields start at INIT as 0).
   Legality: every ADD/COPY/SCALE operand sits at the event's chart, every
   MOVE starts at the register's current chart, public MOVEs strictly ascend
   (span inclusion), owned MOVEs are nested and only on live owned fields,
   COPY writes a zero field, no SCALE by 0, no self-ADD, every owned field
   is cleared at the chart it sits in, and public fields end at `final`.
3. Header identical; all 1,569 rows and end charts equal #7546's; helpers end
   at identity, owned rows end empty; owned MOVEs, lifetimes and peak are
   unchanged, and the content erased at each owned CLEAR is identical.
4. Only the mains 100 and 134 change their MOVE chains, endpoint-preserving.
5. Census, complete invoice (17 native calls) and kappa are recomputed and
   compared with data/invoice-*.json; #7546's crossing is reproduced.
6. Controls: corrupted words and a tampered invoice must be rejected.
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
BASE_SHA256 = '6e03624b173b90356e96f845d05fc93153846b863734dc8163ab6c44c602cd32'
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


def compare(B, RB, W):
    """Everything that must hold between #7546's word B and a candidate W. Returns the candidate replay."""
    require(all(B[k] == W[k] for k in B if k != 'program') and B.keys() == W.keys(), 'header identical')
    R = replay(W)
    n = W['public']
    bad = [r for r in range(len(R['rows'])) if R['rows'][r] != RB['rows'][r]]
    require(not bad, 'all rows equal #7546 (first differing %s)' % bad[:3])
    require(R['cur'] == RB['cur'], 'all end charts equal #7546')
    M = mains(W)
    require(all(R['rows'][r] == {r: Q(1)} for r in range(n) if r not in M), 'helpers end at identity')
    require(all(not R['rows'][r] for r in range(n, len(R['rows']))), 'owned rows end empty')
    require(R['owned_moves'] == RB['owned_moves'], 'owned MOVE multiset unchanged')
    require(R['lifetimes'] == RB['lifetimes'] and R['peak'] == RB['peak'], 'owned lifetimes and peak unchanged')
    require(clears(W) == clears(B), 'content erased at every owned CLEAR identical')
    changed = sorted(r for r in set(R['chains']) | set(RB['chains']) if R['chains'][r] != RB['chains'][r])
    require(changed == [100, 134], 'only mains 100 and 134 change chains (got %s)' % changed[:5])
    require(all(r in M for r in changed), 'changed registers are mains')
    for r in changed:
        old, new = RB['chains'][r], R['chains'][r]
        require(old[0][0] == new[0][0] and old[-1][1] == new[-1][1], 'register %d chain endpoints' % r)
    return R, changed


def main():
    base_raw = (DATA / 'base-7546-word.json.gz').read_bytes()
    require(hashlib.sha256(base_raw).hexdigest() == BASE_SHA256, 'vendored #7546 word bytes')
    B = json.loads(gzip.decompress(base_raw))
    W = load_gz(DATA / 'word.json.gz')
    E = json.loads((DATA / 'edits.json').read_text())
    require(apply_edits(B['program'], E) == W['program'], 'word = #7546 word + edit list')
    print('PASS word = #7546 word (%d events) + %d deletions, %d insertions, %d appended events = %d events'
          % (len(B['program']), len(E['delete']), sum(len(x[1]) for x in E['insert_before']),
             len(E['append']), len(W['program'])))

    RB = replay(B)
    R, changed = compare(B, RB, W)
    dim = [len(f) for f in W['frames']]
    for r in changed:
        f = lambda ch: '->'.join([str(dim[ch[0][0]])] + [str(dim[b]) for a, b in ch])
        print('PASS main %d dims %s became %s' % (r, f(RB['chains'][r]), f(R['chains'][r])))
    print('PASS exact replay: legal, all %d rows and end charts equal #7546, helpers identity, owned empty;'
          ' owned MOVEs (%d), lifetimes (%d), peak (%d) and erased content (%d CLEARs) unchanged'
          % (len(R['rows']), sum(R['owned_moves'].values()), sum(R['lifetimes'].values()), R['peak'],
             len(clears(W))))

    key = lambda W_, i: tuple(W_['frames'][i])
    pairs = lambda W_: {(key(W_, e[2]), key(W_, e[3])) for e in W_['program'] if e[0] == 'MOVE'}
    new_pairs = sorted(pairs(W) - pairs(B))
    require(len(new_pairs) == 2, 'two new chart pairs')
    for a, b in new_pairs:
        require(span(a) < span(b), 'new pair nested')
    print('PASS new chart pairs (nested, checked physically by chart.py):',
          ', '.join('%d->%d' % (len(a), len(b)) for a, b in new_pairs))

    def nondyadic(P):
        c = 0
        for e in P:
            if e[0] in ('ADD', 'COPY', 'SCALE'):
                q = Q(e[2] if e[0] == 'SCALE' else e[3])
                c += q.denominator & (q.denominator - 1) != 0
        return c
    added = [e for x in E['insert_before'] for e in x[1]] + E['append']
    coeffs = sorted({e[3] for e in added if e[0] == 'ADD'}, key=Q)
    require(all(Q(c).denominator & (Q(c).denominator - 1) == 0 for c in coeffs), 'added coefficients dyadic')
    require(nondyadic(W['program']) == nondyadic(B['program']), 'odd-denominator event count unchanged')
    sb, sw = RB['stats'], R['stats']
    require(sw['max_den_exp'] <= sb['max_den_exp'] and sw['odd_den'] == sb['odd_den']
            and sw['max_num_bits'] <= sb['max_num_bits'], 'intermediate coefficient grid within #7546')
    print('PASS intermediate coefficients: 2-adic exponent %d (#7546 %d), odd denominator lcm %d (#7546 %d),'
          ' numerator bits %d (#7546 %d)' % (sw['max_den_exp'], sb['max_den_exp'], sw['odd_den'], sb['odd_den'],
                                           sw['max_num_bits'], sb['max_num_bits']))
    ops = lambda P: collections.Counter(e[0] for e in P)
    d = ops(W['program']); d.subtract(ops(B['program']))
    print('PASS event delta per native call', {k: v for k, v in sorted(d.items()) if v})

    cb, cw = census(B, RB), census(W, R)
    require(cw['helpers'] == cb['helpers'] and cw['rises'] == cb['rises'], 'helper targets and owned rises unchanged')
    dpaid = collections.Counter({int(k): v for k, v in cw['paid'].items()})
    dpaid.subtract({int(k): v for k, v in cb['paid'].items()})
    dpaid = {k: v for k, v in sorted(dpaid.items()) if v}
    require(dpaid == {1: -2, 2: -2, 3: 2}, 'native paid delta {1:-2, 2:-2, 3:+2}')
    print('PASS native paid delta per call', dpaid)
    inv0 = json.loads((DATA / 'invoice-7546.json').read_text())
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
    require((paid0, paid1) == (110468, 110434), 'paid positions')
    print('PASS complete invoice: paid positions %d -> %d, productive %d, S = %d' % (paid0, paid1, sum(T.values()), S))

    k0, k1 = crossing(inv0['targets'], inv0['paid']), crossing(T, Pn)
    lo, hi = decimal.Decimal('0.00364841129479084532481164992024'), decimal.Decimal('0.00364841129479084532481164992025')
    require(lo <= k0 <= hi, '#7546 published crossing reproduced')
    print('PASS kappa #7546 %s (inside the published #7546 enclosure [...992024, ...992025])' % k0)
    print('PASS kappa new   %s (ratio %s)' % (k1, +decimal.Context(prec=12).divide(k1, k0)))
    expected = json.loads((HERE / 'EXPECTED.json').read_text())
    require(str(k1)[:26] == expected['kappa_26'], 'kappa digits as recorded')

    def rejected(label, mutate, base=False):
        X = copy.deepcopy(B if base else W)
        mutate(X['program'])
        try:
            if base:
                R2 = replay(X)
                require(not [r for r in range(len(R2['rows'])) if R2['rows'][r] != RB['rows'][r]], 'rows equal')
            else:
                compare(B, RB, X)
        except AssertionError as exc:
            print('PASS control rejected: %s (%s)' % (label, exc))
            return
        raise AssertionError('control not rejected: ' + label)
    idx = lambda P, ev: P.index(ev)
    rejected('premix 134 += -11/2*1030 changed to -9/2',
             lambda P: P.__setitem__(idx(P, ['ADD', 134, 1030, '-11/2', 3]), ['ADD', 134, 1030, '-9/2', 3]))
    rejected('premix 166 += -2*550 changed to -1',
             lambda P: P.__setitem__(idx(P, ['ADD', 166, 550, '-2', 3]), ['ADD', 166, 550, '-1', 3]))
    rejected('correction 134 += 1/2*315 @789 deleted', lambda P: P.remove(['ADD', 134, 315, '1/2', 789]))
    rejected('premix 134 += -1/2*146 moved to chart 595',
             lambda P: P.__setitem__(idx(P, ['ADD', 134, 146, '-1/2', 3]), ['ADD', 134, 146, '-1/2', 595]))
    rejected('owned read 134 += -2*owned1503 deleted without the premixes',
             lambda P: P.remove(['ADD', 134, 1503, '-2', 595]), base=True)
    bad = dict(Pn); bad['3'] -= 1
    require(json.loads((DATA / 'invoice-new.json').read_text()) != invoice_json(bad, T), 'tampered invoice differs')
    print('PASS control rejected: invoice with one rank-3 job removed differs from the recomputed one')
    print('PASS_TOKEN_SETTLED_DROPS_EXACT')


if __name__ == '__main__':
    sys.exit(main())
