"""Run the complete retained scalar checks with an explicit row engine.

Adapted from Ali Romman PR5827. David Arias, Cinna Davis and Gareth
Davidson retain the P104 word and checker credit. Apache-2.0.
New interface: Ali Romman with substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from rows import coefficient

def need(ok, why):
    if not ok:
        raise ValueError(why)

def span(basis):
    out = {0}
    for v in basis:
        need(type(v) is int and 0 < v < 512 and v not in out, 'Independent binary basis')
        out |= {x ^ v for x in tuple(out)}
    return frozenset(out)

def replay(w, Row, observe=None):
    public = w['public']
    owned = w.get('owned_fields', 8)
    need(type(owned) is int and 8 <= owned <= 29, 'Owned inventory bound')
    need(type(public) is int and 767 <= public <= 770, 'Public inventory bound')
    need(len(w['initial']) == len(w['final']) == public, 'Public boundary size')
    need(len(w['program']) < 26000, 'Fixed operation bound')
    frames = [span(x) for x in w['frames']]
    rows = [Row.unit(r) for r in range(public+owned)]
    current = list(w['initial']) + [None]*owned
    paid, scalar, live_owned, peak = Counter(), 0, set(), 0
    lifetimes = 0
    for e in w['program']:
        op, r = e[:2]
        need(0 <= r < public+owned, 'Role index')
        if op == 'MOVE':
            _, r, a, b, private = e
            need(current[r] == a and (r in live_owned) == private, 'Transport source and ownership')
            need(frames[b] < frames[a] if private else frames[a] < frames[b], 'Nested chronological transport')
            paid[abs(len(w['frames'][b])-len(w['frames'][a]))] += 1
            current[r] = b
        elif op == 'INIT':
            need(r >= public and r not in live_owned, 'Owned initialization')
            live_owned.add(r)
            lifetimes += 1
            peak = max(peak, len(live_owned))
            rows[r] = Row.zero()
            current[r] = e[2]
            scalar += 2
        elif op == 'CLEAR':
            need(r in live_owned and current[r] == e[2], 'Owned erasure at declared frame')
            rows[r] = Row.zero()
            current[r] = None
            live_owned.remove(r)
            scalar += 2
        else:
            q, f = coefficient(e[-2]), e[-1]
            need(q and current[r] == f, 'Scalar destination and coefficient')
            n, d = abs(q.numerator), q.denominator
            need(d & (d-1) == 0, 'Dyadic scalar coefficient')
            need(n+d < (2**16)*d, 'Fixed scalar growth bound')
            if op == 'SCALE':
                need(n & (n-1) == 0, 'Dyadic unit SCALE')
                rows[r] = rows[r].scale(q)
                scalar += 2*(abs(n.bit_length()-d.bit_length()) + int(q < 0))
            else:
                s = e[2]
                need(s != r and 0 <= s < public+owned and current[s] == f, 'Common scalar chart')
                if op == 'COPY':
                    need(r in live_owned and not rows[r], 'COPY into cleared owned field')
                    rows[r] = rows[s].scale(q)
                else:
                    need(op == 'ADD', 'Scalar opcode')
                    rows[r].add(rows[s], q)
                scalar += 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)
        if observe is not None:
            observe(e, rows)
    need(not live_owned and 0 < peak <= 13 and current[:public] == w['final'], 'All public and owned exits')
    live = set(w['live'])
    for r,row in enumerate(rows):
        expected = {r:Q(1)} if r < public else {}
        if r-112 in live:
            expected[r-112] = Q(1)
        need(row == expected, 'All public and owned rows')
    main = live | {r+112 for r in live}
    helpers = Counter(len(w['frames'][w['final'][r]])-len(w['frames'][w['initial'][r]]) for r in range(public) if r not in main)
    need(len(live) == len(w['ports']) == 104 and len(main) == 208 and min(helpers) > 0, 'Independent productive inputs')
    return {'paid':dict(paid), 'helpers':dict(helpers), 'public_inputs':public, 'owned_fields':owned, 'owned_lifetimes':lifetimes,
            'peak_owned_fields':peak, 'real_scalar_allowance':scalar, 'endpoint_coefficients':(public+owned)*(public+owned),
            'paid_rank_mass':sum(r*count for r,count in paid.items())}
