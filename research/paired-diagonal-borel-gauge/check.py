"""Certificate checker independent of the producer and its graph extraction."""
from fractions import Fraction


def need(ok, message):
    if not ok:
        raise ValueError(message)


def v2(x):
    x = Fraction(x)
    n, d, result = abs(x.numerator), x.denominator, 0
    need(n != 0, 'nonzero certificate entry')
    while n % 2 == 0:
        n //= 2
        result += 1
    while d % 2 == 0:
        d //= 2
        result -= 1
    return result


def check(m, matrices, certificate):
    need(type(m) is int and m > 0, 'certificate width')
    need(all(len(a) == 2*m and all(len(r) == 2*m for r in a) for a in matrices),
         'certificate matrix dimensions')
    if certificate.get('kind') == 'potential':
        need(set(certificate) == {'kind', 'weights'}, 'potential schema')
        a = certificate['weights']
        need(len(a) == m and all(type(x) is int for x in a), 'integer potential')
        for matrix in matrices:
            for i, row in enumerate(matrix):
                for j, raw in enumerate(row):
                    x = Fraction(raw)*Fraction(2)**(a[j % m]-a[i % m])
                    need(x.denominator % 2 == 1, 'potential leaves an even denominator')
        return 'integral-in-paired-gauge'
    need(certificate.get('kind') == 'negative-cycle' and
         set(certificate) == {'kind', 'edge_indices'}, 'cycle schema')
    # Reconstruct matrix-entry evidence in canonical traversal order, independently.
    evidence = []
    for matrix in matrices:
        for i, row in enumerate(matrix):
            for j, raw in enumerate(row):
                if Fraction(raw):
                    evidence.append((j % m, i % m, v2(raw)))
    ids = certificate['edge_indices']
    need(isinstance(ids, list) and 0 < len(ids) <= m and
         all(type(i) is int and 0 <= i < len(evidence) for i in ids), 'cycle indices')
    cycle = [evidence[i] for i in ids]
    need(all(cycle[k][1] == cycle[(k+1) % len(cycle)][0] for k in range(len(cycle))),
         'cycle does not close')
    need(sum(e[2] for e in cycle) < 0, 'cycle is not negative')
    return 'no-paired-diagonal-gauge'
