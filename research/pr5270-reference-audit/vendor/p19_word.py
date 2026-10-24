#!/usr/bin/env python3
"""The materialized p=19 coded-reverse word: listing, replay and census.

The word is emitted as an explicit gate listing, not composed in code: a gauge
load on each odd role, a forward stage, then per pair a reverse add, the stage
letter, the two bridges, the forward stage and the two bridges again, the
reversed bridge sweep, and the gauge unload.  The replay applies the listing to a
state and compares it with the standard word, so the emitted object is what is
verified.

Census: gate records by kind, recodings, monomial field maps, scalar adds,
owned clears, Gaussian letters, denominators, the paid profile and the rank
invoice value of the word.
"""
import importlib.util, json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P, OWNERS, SIZE = 65537, 112, 512
H = {4: 28, 7: 7, 8: 47, 9: 326}
P_NEW = {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40}
P_OLD = {1: 2237, 2: 388, 3: 494, 4: 147, 5: 36, 8: 8}
MAPS, ADDS, CLEARS = 224, 896, 16          # per recoding: 112 K + 112 K^-1, 8 x (56 + 56) adds, 16 clears

def need(ok, why):
    if not ok: raise ValueError(why)

def engine():
    spec = importlib.util.spec_from_file_location('lift', HERE/'physical_gauge_lift.py')
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

PATTERN = 'I'*9 + 'T'*9

def gaussian_power(bank, axes, power=1):
    """R**power in one butterfly pass: the gate matrix has eigenvalues 1 and i, so its
    power has a=(1+i^power)/2, b=(1-i^power)/2."""
    ik = pow(256, power, P)
    a = (1+ik)*pow(2, -1, P) % P
    b = (1-ik)*pow(2, -1, P) % P
    out = [r[:] for r in bank]
    for bit in axes:
        step = 1 << bit
        for row in out:
            for st in range(0, SIZE, 2*step):
                for x in range(st, st+step):
                    u, v = row[x], row[x+step]
                    row[x] = (a*u+b*v) % P
                    row[x+step] = (b*u+a*v) % P
    return out

def idle_census(p, pat=PATTERN):
    """The formal controller's idle calls: (kind, pair, rank, retained)."""
    rows = []
    for stage in range(1, 2*p):
        if stage % 2 and stage <= 2*p-3:
            pair = (stage+1)//2
            rows.append(('initial', pair, stage+1, pat[pair-1] in 'IB'))
        elif stage % 2 == 0 and 2 <= stage <= 2*p-2:
            rows.append(('middle', stage//2, 1, True))
    for j in range(p-1):
        rows.append(('terminal', j, 2*p+1-(2*j+3), pat[j] in 'TB'))
    return rows

def pattern_of(p):
    return 'I'*((p-1)//2) + 'T'*(p-1-(p-1)//2)

def listing(p, letter='R'):
    pat = pattern_of(p)
    gates = []
    for r in range(1, 2*p, 2): gates.append(('GAUGE_LOAD', r, 'C^-1'))
    gates.append(('FORWARD', 0, 1, 'C^-1.Q^-1'))
    for j in range(p):
        gates.append(('REVERSE', 2*j, 2*j+1, 'Q.C'))
        gates.append(('LETTER', 2*j, 2*j+1, letter))
        if j < p-1 and pat[j] in 'IB':
            gates.append(('IDLE', 2*(j+1), 2*(j+1)+1, 2*j+2, 'initial'))
        if j < p-1:
            gates.append(('BRIDGE', 2*j, 2*j+2, 1)); gates.append(('BRIDGE', 2*j+1, 2*j+3, -1))
        gates.append(('FORWARD', 2*j, 2*j+1, 'C^-1.Q^-1'))
        if j < p-1:
            gates.append(('IDLE', 2*(j+1), 2*(j+1)+1, 1, 'middle'))
            gates.append(('BRIDGE', 2*j, 2*j+2, -1)); gates.append(('BRIDGE', 2*j+1, 2*j+3, 1))
    for j in range(p-1):
        if pat[j] in 'TB':
            gates.append(('IDLE', 2*j, 2*j+1, 2*p+1-(2*j+3), 'terminal'))
    for j in reversed(range(p-1)):
        gates.append(('BRIDGE', 2*j+2, 2*j, 1)); gates.append(('BRIDGE', 2*j+1, 2*j+3, -1))
    for r in range(1, 2*p, 2): gates.append(('GAUGE_UNLOAD', r, 'C'))
    for j in range(p): gates.append(('SWAP', 2*j, 2*j+1, -1))
    return gates

def standard(p, v0, letter, L):
    st = [r[:] for r in v0]
    Q, Dg, R = (lambda x, inv=False: L.gaussian(x, [0], inv)), \
               (lambda x, inv=False: L.gaussian(x, range(1, 9), inv)), \
               (lambda x, inv=False: L.gaussian(x, range(9), inv))
    let = {'R': R, 'D': Dg}[letter]
    st[1] = L.add(st[1], Q(st[0], True))
    for j in range(p):
        a, b = 2*j, 2*j+1
        st[a] = L.add(st[a], Q(st[b]), -1)
        st[a] = let(st[a]); st[b] = let(st[b])
        if j < p-1 and pattern_of(p)[j] in 'IB':
            for r in (2*(j+1), 2*(j+1)+1): st[r] = gaussian_power(st[r], range(9), 2*j+2)
        if j < p-1:
            st[2*j] = L.add(st[2*j], st[2*j+2], 1); st[2*j+1] = L.add(st[2*j+1], st[2*j+3], -1)
        st[b] = L.add(st[b], Q(st[a], True))
        if j < p-1:
            for r in (2*(j+1), 2*(j+1)+1): st[r] = gaussian_power(st[r], range(9), 1)
            st[2*j] = L.add(st[2*j], st[2*j+2], -1); st[2*j+1] = L.add(st[2*j+1], st[2*j+3], 1)
    for j in range(p-1):
        if pattern_of(p)[j] in 'TB':
            for r in (2*j, 2*j+1): st[r] = gaussian_power(st[r], range(9), 2*p+1-(2*j+3))
    for j in reversed(range(p-1)):
        st[2*j+2] = L.add(st[2*j+2], st[2*j], 1); st[2*j+1] = L.add(st[2*j+1], st[2*j+3], -1)
    for j in range(p):
        hold = st[2*j]
        st[2*j] = st[2*j+1]
        st[2*j+1] = [[(-v) % P for v in row] for row in hold]
    return st

def replay(p, gates, v0, L, C, Ci):
    Q = lambda x, inv=False: L.gaussian(x, [0], inv)
    let = {'R': (lambda x, inv=False: L.gaussian(x, range(9), inv)),
           'D': (lambda x, inv=False: L.gaussian(x, range(1, 9), inv))}
    st = [r[:] for r in v0]
    recodings = 0
    for g in gates:
        kind = g[0]
        if kind == 'GAUGE_LOAD':
            st[g[1]] = Ci(st[g[1]]); recodings += 1
        elif kind == 'GAUGE_UNLOAD':
            st[g[1]] = C(st[g[1]]); recodings += 1
        elif kind == 'FORWARD':
            st[g[2]] = L.add(st[g[2]], Ci(Q(st[g[1]], True))); recodings += 1
        elif kind == 'REVERSE':
            st[g[1]] = L.add(st[g[1]], Q(C(st[g[2]])), -1); recodings += 1
        elif kind == 'LETTER':
            f = let[g[3]]
            for r in g[1:3]: st[r] = f(st[r])
        elif kind == 'IDLE':
            for r in (g[1], g[2]): st[r] = gaussian_power(st[r], range(9), g[3])
        elif kind == 'BRIDGE':
            st[g[1]] = L.add(st[g[1]], st[g[2]], g[3])
        elif kind == 'SWAP':
            hold = st[g[1]]
            st[g[1]] = st[g[2]]
            st[g[2]] = [[(-v) % P for v in row] for row in hold]
        else:
            raise ValueError('unknown gate ' + kind)
    return st, recodings

def invoice(p, pat, thick, prof):
    full = frozenset(range(2*p+1)); T, D = Counter(), Counter()
    outs = [full, full]
    for i, ch in enumerate(pat, 1):
        outs += [frozenset(range(0, 2*i+1)) if ch == 'I' else frozenset(range(2*i, 2*p+1))]*2
    for s in outs: T[1+8*len(s & thick)] += 112
    for i, ch in enumerate(pat, 1):
        if ch == 'I': D[8*len(frozenset(range(0, 2*i)) & thick)] += 224
        else: D[8*len(frozenset(range(2*i+1, 2*p+1)) & thick)] += 224
    for j in range(1, p): D[8*len(frozenset([2*j]) & thick)] += 224
    for r, n in H.items(): T[r] += len(thick)*n
    for r, n in prof.items(): D[r] += len(thick)*n
    D[1] += 112*(2*p+1-len(thick))
    T.pop(0, None); D.pop(0, None)
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
    L = engine()
    receipt = json.loads((ROOT/'research/coded-native-caller/NORMALIZERS.json').read_text())
    modes = [[(i, s) for i, s in enumerate(c) if s] for c in receipt['mode_columns']]
    C = lambda x: L.physical_code(x, receipt['ports'], modes, False)
    Ci = lambda x: L.physical_code(x, receipt['ports'], modes, True)

    import random
    rng = random.Random(5)
    p = 2
    gates = listing(p)
    kinds = Counter(g[0] for g in gates)
    v0 = [[[rng.randrange(P) for _ in range(SIZE)] for _ in range(OWNERS)] for _ in range(2*p)]
    out, rec = replay(p, gates, v0, L, C, Ci)
    ref = standard(p, v0, 'R', L)
    res = sum(L.diff(out[r], ref[r]) for r in range(2*p))
    need(res == 0, 'p=2 replay')
    need(rec == 4*p+1, 'p=2 recodings')
    print('PASS p=2 listing replay: %d gate records %s, %d recodings, residual 0 of %d entries'
          % (len(gates), dict(kinds), rec, 2*p*OWNERS*SIZE))

    p = 19
    gates = listing(p)
    kinds = Counter(g[0] for g in gates)
    v0 = [[[rng.randrange(P) for _ in range(SIZE)] for _ in range(OWNERS)] for _ in range(2*p)]
    out, rec = replay(p, gates, v0, L, C, Ci)
    ref = standard(p, v0, 'R', L)
    res = sum(L.diff(out[r], ref[r]) for r in range(2*p))
    need(res == 0, 'p=19 replay')
    need(rec == 4*p+1, 'p=19 recodings')
    print('PASS p=19 listing replay: %d gate records %s, %d recodings, residual 0 of %d entries'
          % (len(gates), dict(kinds), rec, 2*p*OWNERS*SIZE))

    thick = frozenset(range(1, 2*p, 2))
    pat = 'I'*9+'T'*9
    r_new = root(*invoice(p, pat, thick, P_NEW))
    r_old = root(*invoice(p, pat, thick, P_OLD))
    need(abs(r_new-0.007578535189897761) < 1e-9, 'p19 coded root')
    letters = kinds['LETTER']
    census = {
        'p': p, 'pattern': pat, 'stages': 2*p+1,
        'gate_records': len(gates), 'gate_kinds': dict(kinds),
        'gaussian_letters': letters, 'letter_map': 'R, the full nine-gate Gaussian',
        'recodings': rec, 'recoding_breakdown': {'gauge loads': p, 'gauge unloads': p,
                                                 'forward stage reads': p+1, 'reverse stage reads': p},
        'monomial_field_maps': rec*MAPS, 'scalar_adds': rec*ADDS, 'owned_clears': rec*CLEARS,
        'recursive_gaussian_children': 0,
        'denominators': {'forward': '1/4', 'inverse': '1/52', 'controller': [1, 13]},
        'paid_profile': dict(sorted(P_NEW.items())), 'helper_profile': dict(sorted(H.items())),
        'productive_total': sum(invoice(p, pat, thick, P_NEW)[0].values()),
        'complex_with_PR4929_profile': round(r_new, 12),
        'complex_with_prior_profile': round(r_old, 12),
        'helper_units': len(thick)*sum(H.values()), 'helper_profile_inherited': dict(sorted(H.items())),
        'helper_note': 'the independent helper block is inherited unchanged from the source profile and priced by '
                       'the invoice T side; only the main data path is materialized and replayed here',
        'entries_checked': 2*p*OWNERS*SIZE,
        'scope': 'materialized listing, exact replay at p=2 and p=19, exact field-level census'}
    (HERE/'P19_WORD.json').write_text(json.dumps(census, indent=2, sort_keys=True)+'\n')
    print(json.dumps(census, sort_keys=True))

if __name__ == '__main__':
    main()
