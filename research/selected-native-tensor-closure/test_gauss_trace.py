#!/usr/bin/env python3
"""Independent bounded oracles and rejecting controls for gauss_trace.py."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gauss_trace import Quadratic, adjoint, affine_solution, circuit_trace, equal, gauss_sum, require


def exhaustive_quadratics() -> int:
    count = 0
    for n in range(5):
        edges = list(combinations(range(n), 2))
        for linear in product(range(4), repeat=n):
            for mask in range(1 << len(edges)):
                q = Quadratic(list(linear), {edge for j, edge in enumerate(edges) if mask >> j & 1})
                real = imag = 0
                for x in range(1 << n):
                    v = (sum(linear[j]*((x >> j) & 1) for j in range(n))
                         +2*sum(((x >> a) & 1)*((x >> b) & 1) for a, b in q.pairs)) % 4
                    real += (1, 0, -1, 0)[v]
                    imag += (0, 1, 0, -1)[v]
                require(gauss_sum(q) == (real, imag), 'exhaustive quadratic sum')
                count += 1
    return count


def affine_and_substitution() -> dict[str, int]:
    rng = random.Random(7606030)
    systems = substitutions = 0
    for n in range(8):
        for _ in range(60):
            equations = [(rng.randrange(1 << n), rng.randrange(2)) for __ in range(rng.randrange(n+3))]
            expected = {x for x in range(1 << n)
                        if all((x & mask).bit_count() % 2 == rhs for mask, rhs in equations)}
            solved = affine_solution(n, equations)
            if solved is None:
                actual = set()
            else:
                forms, free = solved
                values = [sum((((mask & t).bit_count() % 2)^c) << j for j, (mask, c) in enumerate(forms))
                          for t in range(1 << free)]
                require(len(set(values)) == len(values), 'unique affine enumeration')
                actual = set(values)
            require(actual == expected, 'complete affine solution set')
            systems += 1
        for _ in range(60):
            q = Quadratic([rng.randrange(4) for __ in range(n)],
                          {pair for pair in combinations(range(n), 2) if rng.randrange(2)}, rng.randrange(4))
            free = rng.randrange(7)
            forms = [(rng.randrange(1 << free), rng.randrange(2)) for __ in range(n)]
            changed = q.substitute(forms, free)
            for t in range(1 << free):
                x = sum((((mask & t).bit_count() % 2)^c) << j for j, (mask, c) in enumerate(forms))
                require(changed.value(t) == q.value(x), 'complete affine quadratic substitution')
            substitutions += 1
    return {'affine_systems': systems, 'affine_substitutions': substitutions}


def dense_trace(n: int, circuit: tuple[tuple, ...]) -> tuple[Fraction, Fraction]:
    """Separate direct column propagation; only used at n<=4."""
    size = 1 << n
    total = [Fraction(0), Fraction(0)]
    for column in range(size):
        real = [Fraction(int(x == column)) for x in range(size)]
        imag = [Fraction(0) for _ in range(size)]
        for gate in circuit:
            kind = gate[0]
            ar, ai = [Fraction(0) for _ in range(size)], [Fraction(0) for _ in range(size)]
            if kind == 'C':
                q, sign = gate[1:]
                for x in range(size):
                    y = x ^ q
                    ar[x] = (real[x]-sign*imag[x]+real[y]+sign*imag[y])/2
                    ai[x] = (imag[x]+sign*real[x]+imag[y]-sign*real[y])/2
            else:
                for x in range(size):
                    y, power = x, 0
                    if kind == 'P':
                        y = sum(((row & x).bit_count() % 2) << j for j, row in enumerate(gate[1]))
                    elif kind == 'X':
                        y ^= gate[1]
                    elif kind == 'phase':
                        power = gate[1]
                    else:
                        require(kind == 'D', 'dense oracle gate')
                        power = sum(a for j, a in enumerate(gate[2]) if x >> j & 1)
                        power += 2*sum(1 for a in range(n) for b in range(a+1, n)
                                       if (x >> a & 1) and (x >> b & 1) and (gate[1][a] >> b & 1))
                    a, b = real[x], imag[x]
                    ar[y], ai[y] = ((a, b), (-b, a), (-a, -b), (b, -a))[power % 4]
            real, imag = ar, ai
        total[0] += real[column]
        total[1] += imag[column]
    return total[0], total[1]


def dense_circuits() -> int:
    rng = random.Random(7606546)
    count = 0
    for n in range(1, 5):
        for _ in range(30):
            gates = []
            for __ in range(1+rng.randrange(18)):
                kind = rng.randrange(5)
                if kind == 0:
                    gates.append(('C', rng.randrange(1, 1 << n), (-1, 1)[rng.randrange(2)]))
                elif kind == 1:
                    gates.append(('X', rng.randrange(1 << n)))
                elif kind == 2:
                    gates.append(('phase', rng.randrange(4)))
                elif kind == 3:
                    rows = [1 << j for j in range(n)]
                    for ___ in range(2*n):
                        a, b = rng.randrange(n), rng.randrange(n)
                        if a != b:
                            rows[a] ^= rows[b]
                    gates.append(('P', tuple(rows)))
                else:
                    linear = tuple(rng.randrange(4) for __ in range(n))
                    rows = [((a % 2) << j) for j, a in enumerate(linear)]
                    for a, b in combinations(range(n), 2):
                        if rng.randrange(2):
                            rows[a] ^= 1 << b
                            rows[b] ^= 1 << a
                    gates.append(('D', tuple(rows), linear))
            circuit = tuple(gates)
            got = circuit_trace(n, circuit)
            expected = dense_trace(n, circuit)
            require((Fraction(got[0], 1 << got[2]), Fraction(got[1], 1 << got[2])) == expected,
                    'Gauss trace equals separate dense-column oracle')
            equal(n, circuit+adjoint(circuit), (), 'literal inverse')
            count += 1
    require(circuit_trace(300, (('C', 1, 1),)) == (1 << 299, 1 << 299, 0),
            '300-axis symbolic Gaussian trace')
    return count


def rejecting_controls() -> int:
    attempts = [
        lambda: equal(1, (('phase', 1),), (), 'wrong global phase'),
        lambda: equal(1, (('D', (0,), (2,)),), (), 'input phase invisible on zero'),
        lambda: equal(1, (('C', 1, 1),), (('C', 1, -1),), 'wrong child direction'),
        lambda: equal(1, (('X', 1), ('D', (1,), (1,))), (('D', (1,), (1,)), ('X', 1)), 'wrong order'),
        lambda: circuit_trace(2, (('P', (1, 1)),)),
        lambda: circuit_trace(1, (('C', 1, 0),)),
        lambda: circuit_trace(2, (('D', (2, 0), (0, 0)),)),
        lambda: circuit_trace(1, (('scale', 2),)),
        lambda: equal(1, (), (('phase', 4),), 'expected phase before normalization'),
        lambda: equal(1, (), (('phase', 0, 'discarded'),), 'expected arity before adjoint'),
    ]
    for run in attempts:
        try:
            run()
        except ValueError:
            continue
        raise ValueError('trace negative control accepted')
    return len(attempts)


def main() -> None:
    result = {'all_quadratics_through_four_variables': exhaustive_quadratics(),
              **affine_and_substitution(), 'independent_dense_circuits': dense_circuits(),
              'rejecting_controls': rejecting_controls(), 'seed': [7606030, 7606546]}
    print('PASS_GAUSS_TRACE', json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
