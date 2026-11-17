#!/usr/bin/env python3
"""Exact full-state certificates for the restored-spare fanout word."""
import hashlib
import itertools
import json
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def poly(terms):
    require(len(terms) <= 128, 'polynomial term capacity')
    require(all(len(w) <= 12 for w in terms), 'polynomial degree capacity')
    return tuple(sorted((w, c) for w, c in terms.items() if c))


def add(p, q):
    out = dict(p)
    for w, c in q:
        out[w] = out.get(w, 0) + c
    return poly(out)


def neg(p):
    return tuple((w, -c) for w, c in p)


def mul(p, q, commutative):
    require(len(p) * len(q) <= 16384, 'polynomial product capacity')
    out = {}
    for u, c in p:
        for v, d in q:
            w = ''.join(sorted(u + v)) if commutative else u + v
            out[w] = out.get(w, 0) + c * d
    return poly(out)


def word(a, b, s, t, beta, negative):
    prefix = ((2, 0, s), (2, 1, t), (0, 2, negative(a)),
              (1, 2, negative(b)))
    suffix = tuple((i, j, negative(c)) for i, j, c in reversed(prefix))
    return prefix + ((2, 3, beta),) + suffix


def inverse(gates, negative):
    return tuple((i, j, negative(c)) for i, j, c in reversed(gates))


def execute_poly(gates, commutative):
    require(len(gates) <= 18, 'word capacity')
    one = poly({'': 1})
    rows = [[one if i == j else () for j in range(4)] for i in range(4)]
    for i, j, c in gates:
        require(0 <= i < 3 and 0 <= j < 4 and i != j, 'gate indices')
        rows[i] = [add(x, mul(c, y, commutative))
                   for x, y in zip(rows[i], rows[j], strict=True)]
    return rows


def expected_poly(x, y, residual):
    one = poly({'': 1})
    out = [[one if i == j else () for j in range(4)] for i in range(4)]
    out[0][3], out[1][3], out[2][3] = x, y, residual
    return out


def symbolic_checks():
    a, b, s, t, z = (poly({c: 1}) for c in 'abstz')
    gates = word(a, b, s, t, z, neg)
    x, y = poly({'az': 1}), poly({'bz': 1})
    residual = poly({'z': 1, 'saz': -1, 'tbz': -1})
    require(execute_poly(gates, False) == expected_poly(x, y, residual),
            'free associative full-state identity')
    require(execute_poly(gates + inverse(gates, neg), False)
            == expected_poly((), (), ()), 'formal inverse endpoint')
    wrong = add(z, neg(add(mul(x, s, False), mul(y, t, False))))
    require(wrong != residual, 'ordered products discriminator')
    return {'free_associative_identities': 2, 'order_discriminators': 1}


def cohn_checks():
    one, u, v = (poly({w: 1}) for w in ('', 'u', 'v'))
    uv = mul(u, v, True)
    a, b = add(one, uv), mul(u, u, True)
    s, t = add(one, neg(uv)), mul(v, v, True)
    gates = word(a, b, s, t, one, neg)
    endpoint = expected_poly(a, b, ())
    require(add(mul(s, a, True), mul(t, b, True)) == one,
            'Cohn witness identity')
    require(execute_poly(gates, True) == endpoint, 'Cohn full dirty endpoint')
    require(execute_poly(inverse(gates, neg), True)
            == expected_poly(neg(a), neg(b), ()), 'Cohn literal inverse')
    require(all(c for _, _, c in gates), 'nonzero polynomial gate census')
    counts = tuple(sum(i == k and j != 3 for i, j, _ in gates)
                   for k in range(3))
    require(counts == (2, 2, 4), 'complete destination counts')
    for cut in range(9):
        shortened = gates[:cut] + gates[cut + 1:]
        require(execute_poly(shortened, True) != endpoint, 'omitted gate')
    require(100 + sum(counts) == 108, 'declared complete word price')
    return {'cohn_words': 2, 'cohn_gate_deletions': 9,
            'cohn_row_adds': sum(counts), 'cohn_source_insertions': 1,
            'cohn_destination_counts': counts, 'cohn_declared_word_price': 108}


def table_product(kind, x, y):
    if kind == 'Z4':
        return x * y % 4
    if kind == 'UT2F2':
        a, b, c = ((x >> i) & 1 for i in range(3))
        d, e, f = ((y >> i) & 1 for i in range(3))
        return (a * d) | ((a * e ^ b * f) << 1) | ((c * f) << 2)
    require(kind == 'M2F2', 'unknown finite ring')
    a, b, c, d = ((x >> i) & 1 for i in range(4))
    e, f, g, h = ((y >> i) & 1 for i in range(4))
    return ((a * e ^ b * g) | ((a * f ^ b * h) << 1)
            | ((c * e ^ d * g) << 2) | ((c * f ^ d * h) << 3))


def tables(kind):
    require(kind in ('Z4', 'UT2F2', 'M2F2'), 'unknown finite ring')
    size, one = {'Z4': (4, 1), 'UT2F2': (8, 5), 'M2F2': (16, 9)}[kind]
    plus = tuple(tuple((x + y) % 4 if kind == 'Z4' else x ^ y
                       for y in range(size)) for x in range(size))
    times = tuple(tuple(table_product(kind, x, y) for y in range(size))
                  for x in range(size))
    minus = tuple(next(y for y in range(size) if plus[x][y] == 0)
                  for x in range(size))
    for a, b, c in itertools.product(range(size), repeat=3):
        require(times[times[a][b]][c] == times[a][times[b][c]], 'associativity')
        require(times[a][plus[b][c]] == plus[times[a][b]][times[a][c]],
                'left distributivity')
        require(times[plus[a][b]][c] == plus[times[a][c]][times[b][c]],
                'right distributivity')
    for a in range(size):
        require(times[one][a] == a == times[a][one], 'ring identity')
    return plus, times, minus, one


def execute_finite(gates, ring):
    plus, times, _, one = ring
    size = len(plus)
    require(len(gates) <= 18, 'word capacity')
    rows = [[one if i == j else 0 for j in range(4)] for i in range(4)]
    for i, j, c in gates:
        require(0 <= i < 3 and 0 <= j < 4 and i != j, 'gate indices')
        require(0 <= c < size, 'finite coefficient domain')
        rows[i] = [plus[x][times[c][y]]
                   for x, y in zip(rows[i], rows[j], strict=True)]
    return rows


def check_tuple(values, ring):
    beta, a, b, s, t = values
    plus, times, minus, one = ring
    x, y = times[a][beta], times[b][beta]
    residual = plus[beta][minus[plus[times[s][x]][times[t][y]]]]
    gates = word(a, b, s, t, beta, minus.__getitem__)
    expected = [[one if i == j else 0 for j in range(4)] for i in range(4)]
    expected[0][3], expected[1][3], expected[2][3] = x, y, residual
    require(execute_finite(gates, ring) == expected, 'finite full-state identity')
    backwards = inverse(gates, minus.__getitem__)
    for i in range(3):
        expected[i][3] = minus[expected[i][3]]
    require(execute_finite(backwards, ring) == expected, 'finite inverse identity')
    witness = residual == 0 and beta != 0
    nondual = witness and plus[times[s][a]][times[t][b]] != one
    return witness, nondual


def exhaustive_substitutions(kind):
    ring = tables(kind)
    size = len(ring[0])
    count = witnesses = nondual = 0
    for values in itertools.product(range(size), repeat=5):
        good, weak = check_tuple(values, ring)
        count += 1
        witnesses += good
        nondual += weak
    require(count == size**5 and witnesses > 0, 'complete tuple domain')
    require(nondual > 0, 'annihilator-only witness domain')
    return {'ring': kind, 'tuples': count, 'nonzero_witnesses': witnesses,
            'witnesses_with_sa_plus_tb_not_one': nondual}


def matrix_witnesses():
    ring = tables('M2F2')
    plus, times, _, _ = ring
    count = nondual = 0
    for beta, a, b in itertools.product(range(16), repeat=3):
        if beta == 0:
            continue
        x, y = times[a][beta], times[b][beta]
        candidates = ((s, t) for s, t in itertools.product(range(16), repeat=2)
                      if plus[times[s][x]][times[t][y]] == beta)
        found = next(candidates, None)
        if found is not None:
            good, weak = check_tuple((beta, a, b, *found), ring)
            require(good, 'selected noncommutative witness')
            count += 1
            nondual += weak
    require(count > 0 and nondual > 0, 'matrix witness coverage')
    return {'ring': 'M2F2', 'selected_witnesses': count,
            'selected_witnesses_with_sa_plus_tb_not_one': nondual}


def controls():
    ring = tables('UT2F2')
    _, times, minus, one = ring
    require(times[1][2] == 2 and times[2][1] == 0,
            'literal E00 E01 differs from E01 E00')
    # This tuple does not satisfy the witness relation: spare must retain p.
    gates = word(one, one, 0, 0, one, minus.__getitem__)
    require(execute_finite(gates, ring)[2][3] == one, 'invalid witness residual')
    rejected = 0
    for gates in (((3, 0, one),), ((0, 0, one),), ((0, 4, one),),
                  ((0, 1, 8),), ((0, 1, -1),), ((0, 1, one),) * 19):
        try:
            execute_finite(gates, ring)
        except ValueError:
            rejected += 1
    require(rejected == 6, 'invalid gate controls')
    for terms in ({'x' * 13: 1}, {str(i): 1 for i in range(129)}):
        try:
            poly(terms)
        except ValueError:
            rejected += 1
    require(rejected == 8, 'polynomial capacity controls')
    return {'invalid_domain_controls': rejected, 'semantic_controls': 2}


def receipt(results):
    root = Path(__file__).resolve().parent
    names = ('README.md', 'PROOF.md', 'TASK.json', 'SOURCES.json',
             'VERIFY.json', 'verify.py')
    hashes = {}
    for name in names:
        with (root / name).open('rb') as stream:
            data = stream.read(262145)
        require(len(data) <= 262144, 'source file capacity')
        hashes[name] = hashlib.sha256(data).hexdigest()
    return {'status': 'PASS_PRINCIPAL_DEMAND_DIRTY_SPARE',
            'claim_type': 'scoped written proof and exact polynomial certificate',
            'python': sys.version.split()[0], 'results': results,
            'sha256': hashes, 'no_new_kappa': True}


def main():
    require(len(sys.argv) == 1, 'no command-line inputs supported')
    results = {'symbolic': symbolic_checks(), 'polynomial': cohn_checks(),
               'complete_substitutions': [exhaustive_substitutions('Z4'),
                                          exhaustive_substitutions('UT2F2')],
               'matrix_substitutions': matrix_witnesses(), 'controls': controls()}
    print(json.dumps(receipt(results), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
