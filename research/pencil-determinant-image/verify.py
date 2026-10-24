#!/usr/bin/env python3
"""Exact bounded corroboration of the pencil determinant-image theorem."""
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return tuple(int(i == j) for i in range(n) for j in range(n))


def multiply(a, b, n, p):
    return tuple(sum(a[i*n+k] * b[k*n+j] for k in range(n)) % p
                 for i in range(n) for j in range(n))


def determinant(a, n, p):
    rows = [list(a[i*n:(i+1)*n]) for i in range(n)]
    answer = 1
    for col in range(n):
        pivot = next((i for i in range(col, n) if rows[i][col]), None)
        if pivot is None:
            return 0
        if pivot != col:
            rows[col], rows[pivot] = rows[pivot], rows[col]
            answer = -answer
        value = rows[col][col]
        answer = answer * value % p
        for row in range(col+1, n):
            factor = rows[row][col] * pow(value, -1, p) % p
            for j in range(col+1, n):
                rows[row][j] = (rows[row][j] - factor*rows[col][j]) % p
    return answer % p


def nullspace(rows, width, p):
    rows = [list(row) for row in rows]
    pivots = []
    for col in range(width):
        pivot = next((i for i in range(len(pivots), len(rows))
                      if rows[i][col]), None)
        if pivot is None:
            continue
        at = len(pivots)
        rows[at], rows[pivot] = rows[pivot], rows[at]
        scale = pow(rows[at][col], -1, p)
        rows[at] = [x*scale % p for x in rows[at]]
        for i in range(len(rows)):
            if i != at:
                factor = rows[i][col]
                rows[i] = [(x-factor*y) % p
                           for x, y in zip(rows[i], rows[at])]
        pivots.append(col)
    basis = []
    for free in (i for i in range(width) if i not in pivots):
        vector = [0]*width
        vector[free] = 1
        for i, col in enumerate(pivots):
            vector[col] = -rows[i][free] % p
        basis.append(tuple(vector))
    return basis


def centralizer_image(matrix, n, p):
    units = [tuple(int(k == i) for k in range(n*n)) for i in range(n*n)]
    differences = []
    for unit in units:
        left = multiply(matrix, unit, n, p)
        right = multiply(unit, matrix, n, p)
        differences.append(tuple((x-y) % p for x, y in zip(left, right)))
    equations = list(zip(*differences))
    basis = nullspace(equations, n*n, p)
    require(p**len(basis) <= 25000, 'centralizer enumeration exceeds bound')
    image = set()
    for coefficients in product(range(p), repeat=len(basis)):
        c = tuple(sum(a*v[j] for a, v in zip(coefficients, basis)) % p
                  for j in range(n*n))
        require(multiply(matrix, c, n, p) == multiply(c, matrix, n, p),
                'nullspace did not centralize')
        value = determinant(c, n, p)
        if value:
            image.add(value)
    return image, p**len(basis)


def block_diagonal(blocks):
    n = sum(size for size, _ in blocks)
    answer = [0]*(n*n)
    offset = 0
    for size, block in blocks:
        for i in range(size):
            for j in range(size):
                answer[(offset+i)*n+offset+j] = block[i*size+j]
        offset += size
    return tuple(answer)


def companion(coefficients, p):
    n = len(coefficients)-1
    require(coefficients[-1] == 1, 'companion polynomial must be monic')
    out = [0]*(n*n)
    for i in range(1, n):
        out[i*n+i-1] = 1
    for i in range(n):
        out[i*n+n-1] = -coefficients[i] % p
    return tuple(out)


def centralizer_fixtures():
    cases = []
    for p in (3, 5):
        j2 = companion((0, 0, 1), p)
        j3 = companion((0, 0, 0, 1), p)
        cases.extend([(p, 2, j2, 2, 'J2'),
                      (p, 2, identity(2), 1, 'scalar2'),
                      (p, 3, j3, 3, 'J3')])
    j2 = companion((0, 0, 1), 3)
    j3 = companion((0, 0, 0, 1), 3)
    cases.extend([
        (3, 3, block_diagonal([(2, j2), (1, (0,))]), 1, 'J2+J1'),
        (3, 4, block_diagonal([(2, j2), (2, j2)]), 2, 'J2+J2'),
        (3, 5, block_diagonal([(3, j3), (2, j2)]), 1, 'J3+J2'),
        (3, 2, companion((1, 0, 1), 3), 1, 'irreducible-degree2'),
        (3, 4, companion((1, 0, 2, 0, 1), 3), 2, 'irreducible-square')])
    results = []
    for p, n, matrix, exponent, name in cases:
        actual, count = centralizer_image(matrix, n, p)
        expected = {pow(x, exponent, p) for x in range(1, p)}
        require(actual == expected, f'centralizer determinant formula: {name}')
        results.append([p, name, n, count, sorted(actual)])
    return results


def matrix_tables(p):
    matrices = list(product(range(p), repeat=4))
    index = {a: i for i, a in enumerate(matrices)}
    table = [[index[multiply(a, b, 2, p)] for b in matrices] for a in matrices]
    determinants = [determinant(a, 2, p) for a in matrices]
    group = [i for i, d in enumerate(determinants) if d]
    transposes = [index[(a[0], a[2], a[1], a[3])] for a in matrices]
    one = index[identity(2)]
    inverses = {a: next(b for b in group if table[a][b] == one) for a in group}
    return matrices, index, table, determinants, group, transposes, one, inverses


def signature(a, p):
    scalar = a[0] if a[1] == a[2] == 0 and a[0] == a[3] else None
    return (a[0]+a[3]) % p, determinant(a, 2, p), scalar


def predicted_image(m, data, p, enlarge=False, omit_coset=False):
    matrices, index, table, dets, group, _, one, inverses = data
    matrix = matrices[m]
    trace, det, scalar = signature(matrix, p)
    exponent = 2 if scalar is None and (trace*trace-4*det) % p == 0 else 1
    hset = {pow(x, 1 if enlarge else exponent, p) for x in range(1, p)}
    image = set()
    for r in group:
        a, b, c, d = matrices[r]
        b0 = index[tuple((a*x+b*y) % p for x, y in zip(matrices[one], matrix))]
        if not dets[b0]:
            continue
        b1 = index[tuple((c*x+d*y) % p for x, y in zip(matrices[one], matrix))]
        transformed = table[b1][inverses[b0]]
        if signature(matrices[transformed], p) != signature(matrix, p):
            continue
        choices = [u for u in group if table[u][transformed] == table[m][u]]
        require(bool(choices), 'similarity signature failed to produce intertwiner')
        z = 1 if omit_coset else dets[choices[0]]
        for h in hset:
            first = z*h % p
            second = pow(dets[b0]*first % p, -1, p)
            image.add((first, second, dets[r]))
    return image


def literal_image(m, data, p):
    matrices, index, table, dets, group, transposes, one, _ = data
    image = set()
    stabilizers = 0
    for r in group:
        a, b, c, d = matrices[r]
        b0 = index[tuple((a*x+b*y) % p for x, y in zip(matrices[one], matrices[m]))]
        b1 = index[tuple((c*x+d*y) % p for x, y in zip(matrices[one], matrices[m]))]
        for left in group:
            first, second = table[left][b0], table[left][b1]
            for right in group:
                qt = transposes[right]
                if table[first][qt] == one and table[second][qt] == m:
                    image.add((dets[left], dets[right], dets[r]))
                    stabilizers += 1
    return image, stabilizers


def tensor_census(p):
    data = matrix_tables(p)
    matrices, index, _, _, group, _, _, _ = data
    histogram = {}
    stabilizer_total = 0
    exact_images = {}
    for m in range(len(matrices)):
        literal, count = literal_image(m, data, p)
        predicted = predicted_image(m, data, p)
        require(literal == predicted, f'literal tensor image mismatch: {p}, {m}')
        require(bool(literal), 'identity determinant triple disappeared')
        histogram[str(len(literal))] = histogram.get(str(len(literal)), 0)+1
        stabilizer_total += count
        exact_images[m] = sorted(literal)
    j = index[(0, 1, 0, 0)]
    if p == 3:
        actual = set(exact_images[j])
        require(actual == {(1, 1, 1), (2, 2, 2)}, 'first Jordan fixture')
        require(predicted_image(j, data, p, enlarge=True) != actual,
                'enlarged centralizer control did not reject')
        require(predicted_image(j, data, p, omit_coset=True) != actual,
                'omitted similarity determinant control did not reject')
    encoded = json.dumps(exact_images, sort_keys=True, separators=(',', ':')).encode()
    return {'field': p, 'matrices': len(matrices), 'group_size': len(group),
            'literal_triples': len(matrices)*len(group)**3,
            'stabilizers': stabilizer_total, 'image_size_histogram': histogram,
            'images_sha256': sha256(encoded).hexdigest()}


def main():
    results = {'centralizers': centralizer_fixtures(),
               'tensors': [tensor_census(p) for p in (2, 3)],
               'controls': ['enlarged-centralizer', 'omitted-similarity-coset']}
    root = Path(__file__).resolve().parent
    files = ('README.md', 'TASK.json', 'SOURCES.json', 'VERIFY.json', 'verify.py')
    receipt = {'schema_version': 1, 'results': results,
               'source_sha256': {name: sha256((root/name).read_bytes()).hexdigest()
                                 for name in files}}
    print('PASS_PENCIL_DETERMINANT_IMAGE fields=2,3 tensor_slices=97 controls=2')
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    main()
