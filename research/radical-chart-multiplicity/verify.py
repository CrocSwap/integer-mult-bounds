"""Exact common-chart multiplicities. Ali Romman with OpenAI Codex. Apache-2.0."""
from collections import Counter
from itertools import combinations, product
import json


def require(ok, message):
    if not ok:
        raise ValueError(message)


def field(q):
    require(q in (2, 3, 4, 5), 'unsupported field')
    add = [[(a ^ b) if q == 4 else (a + b) % q for b in range(q)] for a in range(q)]
    mul = [[0] * q for _ in range(q)]
    for a, b in product(range(q), repeat=2):
        if q != 4:
            mul[a][b] = a * b % q
        else:
            x = ((a & 1) * (b & 1)) ^ (((a & 1) * (b >> 1)) << 1)
            x ^= (((a >> 1) * (b & 1)) << 1) ^ (((a >> 1) * (b >> 1)) * 3)
            mul[a][b] = x
    return add, mul


def projective(q, n):
    for pivot in range(n):
        for tail in product(range(q), repeat=n - pivot - 1):
            yield (0,) * pivot + (1,) + tail


def rref_spaces(q, n, r):
    for pivots in combinations(range(n), r):
        free = [(i, j) for i, p in enumerate(pivots) for j in range(p + 1, n) if j not in pivots]
        for values in product(range(q), repeat=len(free)):
            rows = [[int(j == p) for j in range(n)] for p in pivots]
            for (i, j), value in zip(free, values):
                rows[i][j] = value
            yield rows


def table(q):
    return {
        0: {0: 1},
        1: {0: q**3-q, 1: (q+1)**2},
        2: {0: q*q*(q-1)**2//2, 1: (q+1)**2*(q-1),
            2: q*q*(q+1)**2//2, q+1: 2*(q+1)},
        3: {q+1: q**3-q, 2*q+1: (q+1)**2},
        4: {(q+1)**2: 1},
    }


def predicted(q, d):
    answer = Counter()
    for s, histogram in table(q).items():
        weight = 1
        for i in range(4-s):
            weight *= q**d-q**i
        for k, count in histogram.items():
            answer[k] += count * weight
    return Counter({k: v for k, v in answer.items() if v})


def subspaces(q, add, mul):
    total = 0
    for s in range(5):
        actual = Counter()
        for rows in rref_spaces(q, 4, s):
            k = 0
            for coeff in projective(q, s):
                matrix = [0] * 4
                for c, row in zip(coeff, rows):
                    matrix = [add[x][mul[c][y]] for x, y in zip(matrix, row)]
                k += mul[matrix[0]][matrix[3]] == mul[matrix[1]][matrix[2]]
            actual[k] += 1
            total += 1
        require(actual == table(q)[s], ('subspace table', q, s, actual))
    return total


def target_masks(q, add, mul):
    charts = list(product(projective(q, 2), repeat=2))
    masks = []
    for a, b, c, d in product(range(q), repeat=4):
        mask = 0
        for i, (phi, v) in enumerate(charts):
            row0 = add[mul[a][v[0]]][mul[b][v[1]]]
            row1 = add[mul[c][v[0]]][mul[d][v[1]]]
            if add[mul[phi[0]][row0]][mul[phi[1]][row1]] == 0:
                mask |= 1 << i
        masks.append(mask)
    return masks


def main():
    target_total = space_total = 0
    fixture = None
    for q, max_d in ((2, 4), (3, 3), (4, 2), (5, 2)):
        add, mul = field(q)
        space_total += subspaces(q, add, mul)
        masks = target_masks(q, add, mul)
        for d in range(max_d + 1):
            actual = Counter()
            for selected in product(masks, repeat=d):
                common = (1 << ((q+1)**2)) - 1
                for mask in selected:
                    common &= mask
                actual[common.bit_count()] += 1
                target_total += 1
            require(actual == predicted(q, d), ('target histogram', q, d, actual))
            require(sum(actual.values()) == q**(4*d), 'total target count')
            if (q, d) == (3, 2):
                fixture = dict(sorted(actual.items()))
    require(predicted(2, 3)[0] == 1092, 'predecessor unreachable calibration')
    require(predicted(3, 2)[1] > 0, 'single-chart targets must occur')
    require(predicted(3, 2)[3] == 0, 'three-chart targets are forbidden')
    add, mul = field(4)
    require(add[add[mul[2][2]][2]][1] == 0, 'F4 must not be Z/4')
    a, b = target_masks(2, *field(2))[1:3]
    require((a & b).bit_count() < min(a.bit_count(), b.bit_count()), 'charts must be common')
    try:
        field(6)
    except ValueError:
        pass
    else:
        raise ValueError('unsupported field accepted')
    print(json.dumps(dict(status='PASS_RADICAL_CHART_MULTIPLICITY', target_tuples=target_total,
                         subspaces=space_total, q3_d2=fixture, controls=6, no_new_kappa=True), sort_keys=True))


if __name__ == '__main__':
    main()
