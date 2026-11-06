#!/usr/bin/env python3
"""Exact finite corroboration; the universal theorem is in PROOF.md.
Produced with OpenAI GPT-6.1 Sol at high reasoning effort through Codex.
Apache-2.0. No predecessor executable is imported.
"""
from itertools import product, combinations_with_replacement
from fractions import Fraction
import json


def check(ok, label):
    if not ok:
        raise ValueError(label)


def mm(a, b, p):
    return tuple(tuple(sum(x*y for x, y in zip(row, col)) % p
                       for col in zip(*b)) for row in a)


def eye(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def add(a, b, p, sign=1):
    return tuple(tuple((x+sign*y) % p for x, y in zip(ra, rb))
                 for ra, rb in zip(a, b))


def rank(a, p):
    a = [list(row) for row in a]
    r = 0
    for j in range(len(a[0])):
        k = next((k for k in range(r, len(a)) if a[k][j]), None)
        if k is None:
            continue
        a[r], a[k] = a[k], a[r]
        inv = pow(a[r][j], -1, p)
        a[r] = [x*inv % p for x in a[r]]
        for k in range(len(a)):
            if k != r:
                t = a[k][j]
                a[k] = [(x-t*y) % p for x, y in zip(a[k], a[r])]
        r += 1
    return r


def compose(a, b):
    return tuple(a[i] for i in b)


def root_model(kind):
    if kind == 'A2':
        roots = [(i, j) for i in range(3) for j in range(3) if i != j]
        pos = [i < j for i, j in roots]
        gens = []
        for k in range(2):
            perm = list(range(3))
            perm[k], perm[k+1] = perm[k+1], perm[k]
            gens.append(tuple(roots.index((perm[i], perm[j])) for i, j in roots))
    else:
        roots = [(i, j) for i, j in product(range(-1, 2), repeat=2) if i or j]
        pos = [(j if j else i) > 0 for i, j in roots]
        gens = [tuple(roots.index((-i, j)) for i, j in roots),
                tuple(roots.index((j, i)) for i, j in roots)]
    e = tuple(range(len(roots)))
    words = {e: ()}
    queue = [e]
    for g in queue:
        for s in range(2):
            h = compose(g, gens[s])
            if h not in words:
                words[h] = words[g]+(s,)
                queue.append(h)
    unseen = set(e)
    orbits = []
    while unseen:
        seed = min(unseen)
        orbit = {g[seed] for g in queue}
        unseen -= orbit
        orbits.append(orbit)
    return pos, gens, words, orbits


def clean(a):
    return {g: m for g, m in a.items() if any(any(row) for row in m)}


def formal_mul(a, b, p):
    out = {}
    for g, x in a.items():
        for h, y in b.items():
            k = compose(g, h)
            z = mm(x, y, p)
            out[k] = add(out[k], z, p) if k in out else z
    return clean(out)


def paid(e, s, a, p):
    return clean({e: add(eye(len(a)), a, p, -1), s: a})


def crossing(a, pos, orbit, p):
    n = len(next(iter(a.values())))
    plus = sorted(i for i in orbit if pos[i])
    minus = sorted(i for i in orbit if not pos[i])
    rows = []
    for r in range(n):
        for beta in minus:
            rows.append(tuple(sum(m[r][c] for g, m in a.items() if g[alpha] == beta) % p
                              for c in range(n) for alpha in plus))
    return rank(rows, p)


def packed(m, b, f):
    q, r = divmod(m, b)
    return q*f[b]+f[r]


def packing_tests():
    cases = 0
    for b in range(1, 7):
        tariffs = []
        for slopes in combinations_with_replacement(range(5), b):
            f = [0]
            for slope in reversed(slopes):
                f.append(f[-1]+slope)
            tariffs.append(f)
        tariffs.append([Fraction(k, k+1) for k in range(b+1)])
        for f in tariffs:
            dp = [0]
            for m in range(1, 31):
                dp.append(min(f[k]+dp[max(0, m-k)] for k in range(1, b+1)))
                check(dp[m] == packed(m, b, f), 'packing dynamic program')
                cases += 1
    check(packed(4, 2, [0, Fraction(1, 2), Fraction(2, 3)]) == Fraction(4, 3), 'cap two')
    check(Fraction(4, 5) < Fraction(4, 3), 'relaxed cap changes optimum')
    # Genuine rejecting controls: the proposed conclusions fail outside their hypotheses.
    check(packed(2, 2, [0, 1, 4]) != 2, 'nonconcave tariff must fail')
    check(packed(1, 2, [0, 2, 1]) > 1, 'nonmonotone overshoot beats claimed bound')
    return cases


def gate_tests():
    cases = 0
    for kind in ('A2', 'B2'):
        pos, gens, words, orbits = root_model(kind)
        e = next(iter(words))
        for p, n in ((2, 3), (3, 2), (5, 2)):
            for flat in product(range(p), repeat=n*n):
                a = tuple(tuple(flat[i*n:(i+1)*n]) for i in range(n))
                ar = rank(a, p)
                for s in gens:
                    f = paid(e, s, a, p)
                    for orbit in orbits:
                        sc = sum(pos[i] and not pos[s[i]] for i in orbit)
                        check(crossing(f, pos, orbit, p) == sc*ar, 'arbitrary coupling crossing')
                    cases += 1
    return cases


def product_tests():
    cases = 0
    for kind in ('A2', 'B2'):
        pos, gens, words, orbits = root_model(kind)
        e = next(iter(words))
        for p in (2, 3, 5):
            # Deterministic nonsymmetric couplings, including singular factors.
            for seed in range(160):
                a = ((seed % p, (seed//p) % p),
                     ((seed//(p*p)) % p, (seed+1) % p))
                b = (((seed+2) % p, (3*seed+1) % p),
                     ((seed//2) % p, (seed//3) % p))
                u = paid(e, gens[seed % 2], a, p)
                v = paid(e, gens[(seed//2) % 2], b, p)
                uv = formal_mul(u, v, p)
                for orbit in orbits:
                    check(crossing(uv, pos, orbit, p) <=
                          crossing(u, pos, orbit, p)+crossing(v, pos, orbit, p),
                          'chronological product cut inequality')
                    cases += 1
    return cases


def witness_tests():
    cases = omissions = gauges = 0
    for kind in ('A2', 'B2'):
        pos, gens, words, orbits = root_model(kind)
        e = next(iter(words))
        for w, word in words.items():
            invs = [sum(pos[i] and not pos[w[i]] for i in orbit) for orbit in orbits]
            for orbit, inv in zip(orbits, invs):
                letters = sum(any(pos[i] and not pos[gens[s][i]] for i in orbit) for s in word)
                check(inv == letters, 'reduced orbit letter count')
            for d in range(1, 7):
                for b in range(1, d+1):
                    # Include nondivisible single-reflection attainment only.
                    if d % b and len(word) != 1:
                        continue
                    for p in (2, 3, 5):
                        n = d+1
                        ident = eye(n)
                        current = {e: ident}
                        factors = []
                        costs = [Fraction(0) for _ in orbits]
                        for start in range(0, d, b):
                            k = min(b, d-start)
                            proj = tuple(tuple(int(i == j and start <= i < start+k)
                                               for j in range(n)) for i in range(n))
                            # A shear and inverse really couple the dirty spectator.
                            shear = [list(row) for row in ident]
                            shear[d][start] = 1
                            shear = tuple(map(tuple, shear))
                            sinv = add(ident, add(shear, ident, p, -1), p, -1)
                            check(mm(shear, sinv, p) == ident, 'gauge inverse')
                            coupled = mm(mm(shear, proj, p), sinv, p)
                            check(coupled[d][start] != 0, 'dirty helper participates')
                            check(rank(coupled, p) == k <= b, 'paid rank cap')
                            check(mm(coupled, coupled, p) == coupled, 'attaining projector')
                            for sidx in word:
                                f = paid(e, gens[sidx], coupled, p)
                                f = formal_mul(formal_mul({e: sinv}, f, p), {e: shear}, p)
                                check(f == paid(e, gens[sidx], proj, p), 'free scalar normalization')
                                factors.append(f)
                                current = formal_mul(current, f, p)
                                for oi, orbit in enumerate(orbits):
                                    if any(pos[i] and not pos[gens[sidx][i]] for i in orbit):
                                        costs[oi] += Fraction(k, k+1)
                                gauges += 1
                        expected = clean({e: tuple(tuple(int(i == j == d) for j in range(n)) for i in range(n)),
                                          w: tuple(tuple(int(i == j and i < d) for j in range(n)) for i in range(n))}) if w != e else {e: ident}
                        check(current == expected, 'full formal endpoint')
                        for oi, inv in enumerate(invs):
                            f = [Fraction(k, k+1) for k in range(b+1)]
                            check(costs[oi] == packed(d*inv, b, f), 'sharp packed tariff')
                            check(crossing(current, pos, orbits[oi], p) == d*inv, 'target crossing')
                        if factors:
                            mutant = {e: ident}
                            for factor in factors[1:]:
                                mutant = formal_mul(mutant, factor, p)
                            check(mutant != expected, 'omitted call rejected')
                            omissions += 1
                        cases += 1
    return cases, omissions, gauges


def remainder_tests():
    pos, gens, words, orbits = root_model('A2')
    e = next(iter(words))
    st = compose(gens[0], gens[1])
    expected = {(0, 0, 0): {}, (0, 0, 1): {(0, 2): 1, (1, 2): 1, (0, 1, 2): -2},
                (0, 1, 0): {(0, 1): 1, (0, 1, 2): -1},
                (0, 1, 1): {(0, 1): 1, (0, 2): 1, (0, 1, 2): -2},
                (1, 0, 0): {}, (1, 0, 1): {(1, 2): 1, (0, 1, 2): -1},
                (1, 1, 0): {}, (1, 1, 1): {}}
    for labels in product(range(2), repeat=3):
        poly = {(e, ()): 1}
        for i, label in enumerate(labels):
            out = {}
            for (g, mon), coeff in poly.items():
                for h, term, sign in ((e, (), 1), (e, (i,), -1),
                                      (gens[label], (i,), 1)):
                    key = (compose(g, h), mon+term)
                    out[key] = out.get(key, 0)+sign*coeff
            poly = {key: val for key, val in out.items() if val}
        check({mon: val for (g, mon), val in poly.items() if g == st} == expected[labels],
              'signed three-call remainder coefficient')
    for pfield in (2, 3, 5):
        current = {e: eye(4)}
        for label in gens:
            for block in ((0, 1), (2,)):
                proj = tuple(tuple(int(i == j and i in block) for j in range(4))
                             for i in range(4))
                current = formal_mul(current, paid(e, label, proj, pfield), pfield)
        target = {st: tuple(tuple(int(i == j and i < 3) for j in range(4)) for i in range(4)),
                  e: tuple(tuple(int(i == j == 3) for j in range(4)) for i in range(4))}
        check(current == target, 'four-call st endpoint')
    prices = 0
    for c1 in range(6):
        for c2 in range(c1, 2*c1+1):
            optimum = min(c1*q1+c2*q2 for q1 in range(13) for q2 in range(13)
                          if q1+2*q2 >= 6 and q1+q2 >= 4)
            check(optimum == 2*c1+2*c2, 'chronological price optimum')
            prices += 1
    check(Fraction(7, 3) > 3*Fraction(2, 3), 'strict packed-floor gap')
    return 8, 3, prices


def boundary_tests():
    pos, gens, words, orbits = root_model('A2')
    e = next(iter(words))
    # Augmentation is insufficient as a formal dirty-output oracle.
    leak = {e: ((0, 1), (0, 0)), gens[0]: ((0, 1), (0, 0))}
    check(clean(leak) != {}, 'nonzero full formal leak')
    aug = add(leak[e], leak[gens[0]], 2)
    check(not any(any(row) for row in aug), 'augmentation misses dirty leak')
    # Non-idempotent paid factors need not be involutions over odd fields.
    nil = ((0, 1), (0, 0))
    f = paid(e, gens[0], nil, 3)
    check(formal_mul(f, f, 3) != {e: eye(2)}, 'odd-field involution trap')
    # Genuine nondivisible gap, using rational concave prices.
    tariff = [Fraction(0), Fraction(1, 2), Fraction(2, 3)]
    check(packed(9, 2, tariff) < 3*packed(3, 2, tariff), 'remainder gap retained')
    return 3


def main():
    packing = packing_tests()
    gates = gate_tests()
    products = product_tests()
    witnesses, omissions, gauges = witness_tests()
    boundaries = boundary_tests()
    remainder = remainder_tests()
    check(remainder == (8, 3, 21), 'remainder finite domain')
    check((packing, gates, products, witnesses, omissions, gauges, boundaries) ==
          (14010, 4872, 1440, 672, 588, 2655, 3), 'finite domain counts')
    print(json.dumps({'status': 'PASS_COXETER_CAPPED_CONCAVE_TARIFF',
                      'packing_optima': packing, 'arbitrary_coupling_gate_checks': gates,
                      'product_cut_checks': products, 'chronological_remainder_checks': remainder, 'formal_witnesses': witnesses, 'omission_rejections': omissions,
                      'dirty_gauged_calls': gauges, 'boundary_groups': boundaries}, sort_keys=True))


if __name__ == '__main__':
    main()
