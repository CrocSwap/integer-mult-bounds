#!/usr/bin/env python3
"""The 15 query-only shears of the p16 controllers cannot be absorbed by their neighbours.

#4440 replaced selected full native calls by copied rank-one query shears; #4470
keeps 15 of them per port in its p16 complex controller, and the retained BIT
controller has the same 15.  Each costs one rank-one job per port.  Making them
free would be worth a raw ceiling near 0.0099 on both sides (see the companion
productive-lever-reprice package), so this package checks three ways to remove
them, in the replay model of query-thinned-controllers/controller.py.

1. Fusion with a neighbouring full call.  For every thin stage, the bridged
   shear block composed with the previous or next full native call on the same
   pair needs two independent query results per port: complex has both Q^1 and
   Q^-1 terms; BIT (Q^-1 = Q) has a Q-coefficient matrix of rank 2.  A full call
   D_s S(Q^e) has Laurent support {Q^0, Q^e} and Q-coefficient rank 1.
2. Lazy central frames.  With W = S_x(-Q) S_y(Q^-1) = signed_swap diag(Q^-1,Q)
   S_x(Q), a thin query can be traded for a change of the central frame parity
   of fields.  In the parity model (transport 1, ADD across parities 1, query
   free across parities and 1 otherwise, full calls need equal parities), each
   thin query sits in a window that starts at a full call on its own pair and
   contains only ADD and IDLE events; the windows are disjoint.  Hence every
   thin stage costs at least 1, the optimum is 15, and the controller already
   attains it.  (A CP-SAT run on the whole word found the same optimum.)
3. A two-query native word.  The per-port query lines are all distinct (112
   complex, 111 BIT), so in gather-type schemes (linear maps, rank-one queries,
   free scalars and routes) a second query needs one rank-one job per port, and a
   query riding on an existing one returns Q(f+u), which linearity cannot split.
   Merging the 112 rank-one jobs of a stage into 14 rank-8 jobs saves under one
   unit of moment at the current saving.

Controls: a window with an inserted SWAP is rejected by the window check; a
single full call is confirmed to have Q-coefficient rank 1; a duplicated query
line is detected.  Standard library only.  Prepared by Matarener with Claude
Code assistance.  Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import gzip
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KR = ROOT/'research/kappa-rebuild'
DEP = ROOT/'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime'
CONTROLLERS = {'complex': ROOT/'research/joint-helper-lattice/CONTROLLER.json',
               'bit': ROOT/'research/query-thinned-controllers/BIT-CONTROLLER.json'}


def need(ok, why):
    if not ok:
        raise SystemExit('FAIL: ' + why)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Laurent polynomials in (Q, D) as {(q_exp, d_exp): Fraction}; matrices act on column vectors.
def padd(a, b, c=1):
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, 0)+c*v
        if out[k] == 0:
            del out[k]
    return out


def pmul(a, b):
    out = {}
    for (q1, d1), v1 in a.items():
        for (q2, d2), v2 in b.items():
            k = (q1+q2, d1+d2)
            out[k] = out.get(k, 0)+v1*v2
            if out[k] == 0:
                del out[k]
    return out


def apply(rows, event, fields, with_d):
    """Left-multiply the row-polynomial matrix by one replay event (controller.py semantics)."""
    op = event[0]
    if op in ('LOCAL', 'QUERY_SHEAR'):
        _, stage, pair, backward = event
        x, y = 2*pair, 2*pair+1
        if backward:
            x, y = y, x
        term = {(1 if backward else -1, 0): Q(-1 if backward else 1)}
        ix, iy = fields.index(x), fields.index(y)
        rows[iy] = [padd(a, pmul(term, b)) for a, b in zip(rows[iy], rows[ix])]
        if op == 'LOCAL' and with_d:
            for role in (ix, iy):
                rows[role] = [pmul({(0, 1): Q(1)}, a) for a in rows[role]]
    elif op == 'ADD':
        _, dst, src, *c = event
        idst, isrc = fields.index(dst), fields.index(src)
        rows[idst] = [padd(a, b, c[0] if c else 1) for a, b in zip(rows[idst], rows[isrc])]
    elif op == 'IDLE':
        pass  # commuting D multipliers of other stages; they do not change Q-structure
    else:
        raise ValueError(op)
    return rows


def block(events, fields, with_d=True):
    n = len(fields)
    rows = [[{(0, 0): Q(1)} if i == j else {} for j in range(n)] for i in range(n)]
    for e in events:
        rows = apply(rows, e, fields, with_d)
    return rows


def coeff(rows, qexp):
    return [[sum(v for (q, d), v in e.items() if q == qexp) for e in row] for row in rows]


def coeff_poly(rows, qexp):
    return [[{d: v for (q, d), v in e.items() if q == qexp} for e in row] for row in rows]


def rank(rows):
    rows = [list(map(Q, r)) for r in rows]
    r = 0
    for c in range(len(rows[0]) if rows else 0):
        piv = next((i for i in range(r, len(rows)) if rows[i][c]), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i][c]:
                f = rows[i][c]/rows[r][c]
                rows[i] = [x-f*y for x, y in zip(rows[i], rows[r])]
        r += 1
    return r


def mod2_rank_generic(polys):
    """Rank over GF(2)(D) via a nonzero 2x2 minor (D-polynomials mod 2); returns 2 if one exists, else <= 1."""
    def pm(a, b):
        out = Counter()
        for i, x in a.items():
            for j, y in b.items():
                out[i+j] += x*y
        return {k: v % 2 for k, v in out.items() if v % 2}
    n = len(polys)
    for i in range(n):
        for j in range(i+1, n):
            for k in range(n):
                for l in range(k+1, n):
                    a, b = pm(polys[i][k], polys[j][l]), pm(polys[i][l], polys[j][k])
                    diff = Counter(a)
                    diff.update(b)
                    if any(v % 2 for v in diff.values()):
                        return 2
    return 1 if any(any(v % 2 for v in e.values()) for row in polys for e in row) else 0


def thin_windows(events):
    """For each QUERY_SHEAR: (index, pair, start index of the full call on the same pair, bridge span)."""
    out = []
    for i, e in enumerate(events):
        if e[0] != 'QUERY_SHEAR':
            continue
        pair = e[2]
        j = max(k for k in range(i) if events[k][0] == 'LOCAL' and events[k][2] == pair)
        out.append((i, pair, j))
    return out


def window_ok(events, i, j):
    return all(events[k][0] in ('ADD', 'IDLE') for k in range(j+1, i))


def fusion(kind, events):
    """Q-structure of thin block + previous and + next full call on the involved pairs."""
    results = []
    for i, pair, j in thin_windows(events):
        bridge = events[i-2:i] + [events[i]] + events[i+1:i+3]
        need([b[0] for b in bridge] == ['ADD', 'ADD', 'QUERY_SHEAR', 'ADD', 'ADD'], f'{kind}: bridged thin block at {i}')
        fields = sorted({2*pair, 2*pair+1, 2*pair+2, 2*pair+3})
        nxt = next(k for k in range(i+1, len(events)) if events[k][0] == 'LOCAL')
        need(events[nxt][2] == pair+1, f'{kind}: next full call is on pair {pair+1}')
        need(all(events[k][0] == 'ADD' for k in range(i+3, nxt)), f'{kind}: only bridge ADDs before next call')
        for label, word in (('previous', [events[j]] + bridge), ('next', bridge + [events[nxt]])):
            rows = block(word, fields)
            if kind == 'complex':
                r1, rm = rank(coeff(rows, 1)), rank(coeff(rows, -1))
                need(r1 >= 1 and rm >= 1, f'complex {label} fusion needs both Q and Q^-1 at {i}')
                results.append(dict(thin_event=i, fused_with=label, rank_Q=r1, rank_Q_inverse=rm))
            else:
                plus, minus = coeff_poly(rows, 1), coeff_poly(rows, -1)
                summed = [[padd(a, b) for a, b in zip(r, s)] for r, s in zip(plus, minus)]
                r2 = mod2_rank_generic(summed)
                need(r2 == 2, f'BIT {label} fusion has Q-coefficient rank 2 at {i}')
                results.append(dict(thin_event=i, fused_with=label, rank_Q_mod2=r2))
    # Control: one full call alone has support {Q^0, Q^e} and Q-coefficient rank 1.
    first = next(e for e in events if e[0] == 'LOCAL')
    rows = block([first], [0, 1])
    e = 1 if first[3] else -1
    need(rank(coeff(rows, e)) == 1 and not any(any(v for v in r) for r in coeff(rows, -e)),
         f'{kind}: a single full call has one query (control)')
    return results


def parity_floor(kind, events):
    windows = thin_windows(events)
    need(len(windows) == 15, f'{kind}: 15 thin queries')
    for i, pair, j in windows:
        need(window_ok(events, i, j), f'{kind}: window of thin event {i} has only ADD/IDLE')
    spans = sorted((j, i) for i, _, j in windows)
    need(all(a[1] < b[0] for a, b in zip(spans, spans[1:])), f'{kind}: windows are disjoint')
    bad = list(events)
    i, pair, j = windows[0]
    bad.insert(j+1, ['SWAP', 2*pair, 2*pair+1])
    i2, _, j2 = thin_windows(bad)[0]
    need(not window_ok(bad, i2, j2), f'{kind}: inserted SWAP breaks the window (control)')
    return dict(thin_queries=15, lower_bound=15, attained=15, windows=[[j, i] for i, _, j in windows])


def distinct_lines():
    phases = json.loads((DEP/'direct-decoder/sources/DATA-PHASES.json').read_text())
    qs = [r['q'] for r in phases['recipes']]
    need([r['port'] for r in phases['recipes']] == list(range(112)), 'complex recipes per port')
    need(len(qs) == 112 and len(set(qs)) == 112 and all(0 < q < 512 for q in qs),
         'complex: 112 distinct nonzero 9-bit query lines')
    mutated = qs[:]
    mutated[1] = mutated[0]
    need(len(set(mutated)) == 111, 'duplicate line detected (control)')
    word = json.loads(gzip.decompress((KR/'bit/sources/pr589-regenerated/WORD.json.gz').read_bytes()))
    lines = [tuple(Q(x) for x in q) for q in word['lines']]
    need(len(lines) == 111 and all(sum(x*x for x in q) == 4 for q in lines), 'BIT root lines')
    need(len({max(q, tuple(-x for x in q)) for q in lines}) == 111, 'BIT: 111 distinct port lines up to sign')
    return dict(complex_distinct_q=112, bit_distinct_lines=111)


def merge_saving():
    E = load(KR/'architecture/mixed_target_probe.py', 'tqs_probe')
    c = Q('0.00302015')
    lo, hi = E.h_interval(8, c)
    saving = (112-14*hi, 112-14*lo)
    need(0 < saving[0] and saving[1] < 1, 'merging 112 rank-one into 14 rank-eight saves under one unit')
    return [f'{float(saving[0]):.6f}', f'{float(saving[1]):.6f}']


def main():
    out = {'schema': 'thin-query-shear-floor/1', 'new_kappa': False}
    for kind, path in CONTROLLERS.items():
        w = json.loads(path.read_text())
        need(w['pairs'] == 16, f'{kind}: p16 controller')
        events = w['physical_events']
        fz = fusion(kind, events)
        out[kind] = {'fusion_blocks_checked': len(fz), 'fusion': fz, 'parity_floor': parity_floor(kind, events)}
        print(kind, len(fz), 'fusion blocks need two queries; parity floor 15 = 15', flush=True)
    out['query_lines'] = distinct_lines()
    out['rank_merge_saving_at_0.00302015'] = merge_saving()
    out['status'] = 'PASS_THIN_QUERY_SHEAR_FLOOR'
    (HERE/'RESULT.json').write_text(json.dumps(out, indent=2, sort_keys=True)+'\n', newline='\n')
    print(out['status'], flush=True)


if __name__ == '__main__':
    main()
