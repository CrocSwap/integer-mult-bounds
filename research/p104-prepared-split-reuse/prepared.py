"""Exact endpoints for the prepared P104 helper.

Adapted from Ali Romman's P104 local.py; retained native sources are unchanged.
Changes: one retired helper, arbitrary owned roles, two ordinary reconstructions,
and 758 total fields. Scratch-net with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from common import need

def add(dst, src, q):
    for k,v in tuple(src.items()):
        z=dst.get(k,Q(0))+q*v
        if z:dst[k]=z
        else:dst.pop(k,None)

def span(basis):
    out={0}
    for v in basis:
        need(type(v) is int and 0<v<512 and v not in out, 'Independent binary basis')
        out|={x^v for x in tuple(out)}
    return frozenset(out)

def replay(w):
    need(len(w['program']) < 26000, 'Fixed operation bound')
    need(w['fields'] == 758 and w['retired_public'] == [573]
         and w['independent_public'] == [r for r in range(750) if r != 573]
         and w['owned_roles'] == [573]+list(range(750,758)), 'Exact independent and owned interface')
    frames = [span(x) for x in w['frames']]
    rows = [{r:Q(1)} for r in range(758)]
    current = list(w['initial']) + [None]*8
    current[573] = None
    owned = set(w['owned_roles'])
    lifetimes = 0
    paid, scalar, live_owned, peak = Counter(), 0, set(), 0
    for e in w['program']:
        op, r = e[:2]
        need(0 <= r < 758, 'Role index')
        if op == 'MOVE':
            _, r, a, b, private = e
            need(current[r] == a and (r in live_owned) == private, 'Transport source and ownership')
            ascending = r < 750
            need(frames[a] < frames[b] if ascending else frames[b] < frames[a],
                 'Strict nested chronological transport')
            paid[abs(len(w['frames'][b])-len(w['frames'][a]))] += 1
            current[r] = b
        elif op == 'INIT':
            need(r in owned and r not in live_owned, 'Owned initialization')
            lifetimes += 1
            live_owned.add(r)
            peak = max(peak, len(live_owned))
            rows[r] = {}
            current[r] = e[2]
            scalar += 2
        elif op == 'CLEAR':
            need(r in live_owned and current[r] == e[2], 'Owned erasure at declared frame')
            rows[r] = {}
            current[r] = None
            live_owned.remove(r)
            scalar += 2
        else:
            q, f = Q(e[-2]), e[-1]
            need(q and current[r] == f, 'Scalar destination and coefficient')
            n, d = abs(q.numerator), q.denominator
            need(d & (d-1) == 0, 'Dyadic scalar coefficient')
            need(abs(q)+1 < 2**16, 'Fixed scalar growth bound')
            if op == 'SCALE':
                need(n & (n-1) == 0, 'Dyadic unit SCALE')
                rows[r] = {k:q*x for k,x in rows[r].items()}
                scalar += 2*(abs(n.bit_length()-d.bit_length()) + int(q < 0))
            else:
                s = e[2]
                need(s != r and 0 <= s < 758 and current[s] == f, 'Common scalar chart')
                if op == 'COPY':
                    need(r in live_owned and not rows[r], 'COPY into cleared owned field')
                    rows[r] = {k:q*x for k,x in rows[s].items()}
                else:
                    need(op == 'ADD', 'Scalar opcode')
                    add(rows[r], rows[s], q)
                scalar += 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)
    need(not live_owned and peak == 2 and all(current[r] == w['final'][r] for r in w['independent_public']), 'All public and owned exits')
    need(lifetimes == 11, 'Complete owned lifetime census')
    live = set(w['live'])
    for r,row in enumerate(rows):
        expected = {r:Q(1)} if r < 750 and r != 573 else {}
        if r-112 in live:
            expected[r-112] = Q(1)
        need(row == expected, 'All 758 public and owned rows')
    main = live | {r+112 for r in live}
    helpers = Counter(len(w['frames'][w['final'][r]])-len(w['frames'][w['initial'][r]]) for r in range(750) if r not in main and r != 573)
    need(len(live) == len(w['ports']) == 104 and len(main) == 208 and min(helpers) > 0, 'Independent productive inputs')
    return {'paid':dict(paid), 'helpers':dict(helpers), 'public_inputs':749, 'owned_lifetimes':lifetimes,
            'peak_owned_fields':peak, 'real_scalar_allowance':scalar, 'endpoint_coefficients':758*758}


def reverse_columns(w):
    """Check the transpose with dense dyadic rows and the reverse chronology."""
    n = 758
    rows = [[int(i == j) for j in range(n)] for i in range(n)]
    exponents = [0]*n
    for e in reversed(w['program']):
        op,r = e[:2]
        if op == 'MOVE':
            continue
        if op in ('INIT','CLEAR'):
            rows[r] = [0]*n
            exponents[r] = 0
            continue
        q = Q(e[-2])
        qe = q.denominator.bit_length()-1
        if op == 'SCALE':
            rows[r] = [q.numerator*x for x in rows[r]]
            exponents[r] += qe
        else:
            s = e[2]
            level = max(exponents[s], exponents[r]+qe)
            a, b = 1 << (level-exponents[s]), q.numerator << (level-exponents[r]-qe)
            rows[s] = [a*x+b*y for x,y in zip(rows[s],rows[r])]
            exponents[s] = level
            if op == 'COPY':
                rows[r] = [0]*n
                exponents[r] = 0
            r = s
        while exponents[r] and not any(x & 1 for x in rows[r]):
            rows[r] = [x//2 for x in rows[r]]
            exponents[r] -= 1
    for r,row in enumerate(rows):
        expected = [0]*n
        if r < 750 and r != 573:
            expected[r] = 1 << exponents[r]
        if r in w['live']:
            expected[r+112] = 1 << exponents[r]
        need(row == expected, 'Independent dense transpose columns')
    return {'columns':n, 'coefficients':n*n, 'arithmetic':'Dense integer rows with binary denominators; reverse chronology'}
