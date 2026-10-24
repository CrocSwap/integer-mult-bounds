#!/usr/bin/env python3
"""The uncoded p=19 controller word: trace, diagonalisation, census and price.

The invoice prices a word by its rank census, and the census never sees the code:
``invoice(p, pattern, thick, profile)`` takes no coding argument.  The coded reverse
was therefore an overlay the endpoint does not need, and it is the overlay that costs
the terminal-gauge decoder (one Q per owner per thick stage = 2128 rank-1 units
against a 1103-unit root budget).  This receipt builds the word without it.

The word is not transcribed by hand: the controller loop is re-executed with a log of
every role update, the log is replayed in the controller's own monomial algebra, and
the replay must reproduce the controller's matrix exactly.  A hand transcription is
what a prior audit showed can drift (#5349); an instrumented trace cannot.

Scope: the trace identity, the p=19 diagonalisation, the census and the price.  The
ambient rank of this word is 153, so a literal 512-address replay cannot host it; the
local physical identities stay with the companion package.
"""
import importlib.util, json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
H = {4: 28, 7: 7, 8: 47, 9: 326}
PROF = {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40}

def need(ok, why):
    if not ok: raise ValueError(why)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def traced_controller(C, p, keep, coupling):
    """The controller's own loop, emitting the gate sequence as it goes."""
    n, stages = 2*p, 2*p+1
    zero = (0,)*(stages+1)
    matrix = [[{zero: 1} if i == j else {} for j in range(n)] for i in range(n)]
    gates, idle = [], []
    term = lambda q, sel: (q,)+tuple(int(s in sel) for s in range(stages))
    def idle_call(pair, sel, kind):
        retained = bool(keep >> len(idle) & 1)
        idle.append(dict(kind=kind, pair=pair, retained=retained, sel=list(sel)))
        if retained:
            for role in (2*pair, 2*pair+1):
                matrix[role] = [C.monomial_times(x, term(0, sel)) for x in matrix[role]]
            gates.append(('IDLE', kind, 2*pair, 2*pair+1, tuple(sel)))
    def local(stage, pair, reverse):
        x, y = 2*pair, 2*pair+1
        if reverse: x, y = y, x
        coef = (-1 if reverse else 1)*coupling[stage]
        matrix[y] = [C.plus(a, C.monomial_times(b, term(1 if reverse else -1, []), coef)) for a, b in zip(matrix[y], matrix[x])]
        gates.append(('REVERSE' if reverse else 'FORWARD', stage, y, x, coef))
        for role in (x, y): matrix[role] = [C.monomial_times(z, term(0, [stage])) for z in matrix[role]]
        gates.append(('LETTER', stage, x, y, stage))
        if stage % 2 and stage <= 2*p-3: idle_call((stage+1)//2, list(range(stage+1)), 'initial')
        elif stage % 2 == 0 and 2 <= stage <= 2*p-2: idle_call(stage//2, [stage], 'middle')
        elif stage == 2*p:
            for j in range(p-1): idle_call(j, list(range(2*j+3, 2*p+1)), 'terminal')
    def bridge(dst, src, c):
        for d, s, cc in ((2*dst, 2*src, c), (2*src+1, 2*dst+1, -c)):
            matrix[d] = [C.plus(a, b, cc) for a, b in zip(matrix[d], matrix[s])]
            gates.append(('BRIDGE', cc, d, s, None))
    local(0, 0, False)
    for j in range(p):
        local(2*j+1, j, True)
        if j < p-1: bridge(j, j+1, 1)
        local(2*j+2, j, False)
        if j < p-1: bridge(j, j+1, -1)
    for j in reversed(range(p-1)): bridge(j+1, j, 1)
    for j in range(p):
        matrix[2*j], matrix[2*j+1] = matrix[2*j+1], [C.monomial_times(x, zero, -1) for x in matrix[2*j]]
        gates.append(('SWAP', -1, 2*j, 2*j+1, None))
    co = {}
    for i, row in enumerate(matrix):
        for j, poly in enumerate(row):
            for key, v in poly.items(): co.setdefault(key, [[Q(0)]*n for _ in range(n)])[i][j] += v
    return matrix, {k: m for k, m in co.items() if any(any(r) for r in m)}, gates, idle

def invoice(p, pat, thick, prof):
    full = frozenset(range(2*p+1)); T, D = Counter(), Counter()
    outs = [full, full]
    for i, ch in enumerate(pat, 1):
        outs += [frozenset(range(0, 2*i+1)) if ch == 'I' else frozenset(range(2*i, 2*p+1))]*2
    for s in outs: T[1+8*len(s & thick)] += 112
    for i, ch in enumerate(pat, 1):
        D[8*len((frozenset(range(0, 2*i)) if ch == 'I' else frozenset(range(2*i+1, 2*p+1))) & thick)] += 224
    for j in range(1, p): D[8*len(frozenset([2*j]) & thick)] += 224
    for r, n in H.items(): T[r] += len(thick)*n
    for r, n in prof.items(): D[r] += len(thick)*n
    D[1] += 112*(2*p+1-len(thick)); T.pop(0, None); D.pop(0, None)
    return T, D

def root(T, D):
    f = lambda c: sum(n*r**(1-c) for r, n in T.items())-sum(n*r**(1-c) for r, n in D.items())
    lo, hi = 0.0, 0.05
    for _ in range(200):
        mid = (lo+hi)/2
        if f(mid) > 0: lo = mid
        else: hi = mid
    return lo

def main():
    mod = load('c4940', ROOT/'research/coded-reverse-controller/verify.py')
    C = mod.C
    receipt = {}
    for p, pat in ((2, 'I'), (3, 'IT'), (19, 'I'*9+'T'*9)):
        coupling = {s: Q(1) for s in range(2*p+1)}
        keep = mod.keep_of(p, pat)
        want_co, want_idle = mod.controller(p, keep, coupling)
        got, got_co, gates, idle = traced_controller(C, p, keep, coupling)
        need(got_co == want_co, 'the trace reproduces the controller matrix exactly')
        need([r['retained'] for r in idle] == [r['retained'] for r in want_idle],
             'the trace reproduces the retention pattern')
        std = mod.diagonalize(p, pat, coupling)
        need(std is not None, 'the uncoded word diagonalises at p=%d' % p)
        kinds = Counter(g[0] for g in gates)
        ret = [r for r in idle if r['retained']]
        receipt['p%d' % p] = {'gates': len(gates), 'kinds': dict(kinds),
                      'retained_idles': len(ret),
                      'idle_rank': sum(len(r['sel']) for r in ret),
                      'outputs': std[0], 'denominators': std[1],
                      'trace_identity': 'replayed in the controller algebra'}
        need(std[1] == [1], 'standard denominators are [1] at p=%d' % p)
        print('PASS p=%2d trace == controller: %d gates %s, %d retained idles, rank %d; diagonalises to %s with '
              'denominators %s' % (p, len(gates), dict(kinds), len(ret),
                                   sum(len(r['sel']) for r in ret), std[0], std[1]))

    p, pat = 19, 'I'*9+'T'*9
    thick = frozenset(range(1, 2*p, 2))
    T, D = invoice(p, pat, thick, PROF)
    r = root(T, D)
    need(abs(r-0.007578535189897761) < 1e-9, 'p19 coded root, unchanged without the code')
    need(max(T) == 153, 'ambient target rank')
    print('PASS price: the invoice is code-blind, so the uncoded word keeps the root %.12f '
          '(T %d units, D %d units, ambient rank %d)' % (r, sum(T.values()), sum(D.values()), max(T)))
    receipt['p19'] = dict(receipt['p19'], invoice_root=r, ambient_rank=max(T),
                          recodings=0, monomial_field_maps=0, scalar_adds=0, owned_clears=0,
                          terminal_gauge_decoder=0,
                          note='no code, so no recoding bill and no terminal-gauge decoder')
    receipt['status'] = 'PASS_P19_UNCODED_WORD'
    receipt['scope'] = ('controller trace identity, p=2/3/19 diagonalisation, census and price; '
                        'ambient rank 153 precludes a literal 512-address replay')
    (HERE/'P19_PLAIN.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k: receipt[k] for k in ('status',)}, sort_keys=True))

if __name__ == '__main__':
    main()
