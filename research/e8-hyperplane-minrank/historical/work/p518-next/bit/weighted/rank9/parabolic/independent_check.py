"""Check the eight finite certificates with integer arithmetic."""
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
import hashlib
import json

BASE = Path(__file__).resolve().parent
source = BASE.parent / 'quick.json'
raw = source.read_bytes()
data = json.loads(raw)
roots = set()
for i in range(8):
    for j in range(i + 1, 8):
        for u, v in product((-2, 2), repeat=2):
            row = [0] * 8
            row[i], row[j] = u, v
            roots.add(tuple(row))
roots.update(row for row in product((-1, 1), repeat=8)
             if row.count(-1) % 2 == 0)
assert len(roots) == 240
simple = [(1,-1,-1,-1,-1,-1,-1,1), (2,2,0,0,0,0,0,0),
          (-2,2,0,0,0,0,0,0)]
for j in range(1, 6):
    row = [0] * 8
    row[j], row[j + 1] = -2, 2
    simple.append(tuple(row))
assert data['simple_roots'] == list(map(list, simple))
assert all(root in roots for root in simple)

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

# Invert the column matrix of the simple roots.
matrix = [[Fraction(simple[j][i]) for j in range(8)]
          + [Fraction(i == j) for j in range(8)] for i in range(8)]
for j in range(8):
    pivot = next(i for i in range(j, 8) if matrix[i][j])
    matrix[j], matrix[pivot] = matrix[pivot], matrix[j]
    scale = matrix[j][j]
    matrix[j] = [x / scale for x in matrix[j]]
    for i in range(8):
        if i != j:
            scale = matrix[i][j]
            matrix[i] = [x - scale * y for x, y in zip(matrix[i], matrix[j])]
inverse = [row[8:] for row in matrix]
for root in roots:
    coordinates = [dot(row, root) for row in inverse]
    assert all(x.denominator == 1 for x in coordinates)
    assert all(x >= 0 for x in coordinates) or all(x <= 0 for x in coordinates)
    for alpha in simple:
        inner = dot(root, alpha)
        assert inner % 4 == 0
        reflected = tuple(x - inner // 4 * y for x, y in zip(root, alpha))
        assert reflected in roots
assert all(dot(alpha, alpha) == 8 for alpha in simple)
cartan = [[dot(a, b) // 4 for b in simple] for a in simple]
assert [(i + 1, j + 1) for i, j in combinations(range(8), 2)
        if cartan[i][j] == -1] == [(1,3),(2,4),(3,4),(4,5),(5,6),(6,7),(7,8)]

pairs = [tuple(pair) for pair in data['pairs']]
assert len(pairs) == 5 and len(set(pairs)) == 5
assert len(set().union(*map(set, pairs))) == 4
counts = [42,28,22,14,16,23,37,63]
types = ['D7','A7','A6+A1','A4+A2+A1','A4+A3','D5+A2','E6+A1','E7']
items = []
assert len(data['parabolics']) == 8
for item in data['parabolics']:
    node = item['node']
    n = item['normal']
    assert [i + 1 for i, a in enumerate(simple) if dot(n, a)] == [node]
    inside = sum(dot(n, r) == 0 for r in roots) // 2
    assert inside == item['roots_in_hyperplane'] == counts[node - 1]
    rows = list(map(tuple, item['certificate']))
    assert len(rows) == 13
    assert len({min(r, tuple(-x for x in r)) for r in rows}) == 13
    assert all(r in roots and dot(r, n) != 0 for r in rows)
    anchors, witnesses = rows[:8], rows[8:]
    assert all(dot(a, b) != 0 for a, b in combinations(anchors, 2))
    for pair, witness in zip(pairs, witnesses):
        assert tuple(i for i, a in enumerate(anchors) if dot(a, witness) == 0) == pair
    checks = 0
    for (p, u), (q, v) in combinations(list(zip(pairs, witnesses)), 2):
        if set(p) & set(q):
            assert dot(u, v) != 0
            checks += 1
    assert checks == 8
    items.append({'node':node, 'type':types[node - 1], 'root_lines_inside':inside,
                  'certificate_lines':13, 'incident_zero_constraints':checks})
result = {'status':'PASS', 'input_sha256':hashlib.sha256(raw).hexdigest(),
          'integer_root_count':240, 'simple_basis_and_reflection_checks':True,
          'all_eight_certificates_checked':True, 'parabolics':items,
          'scope':'Finite certificates and simple roots. The universal theorem also uses the Weyl chamber and fitting rank arguments in PROOF.md.'}
(BASE / 'INDEPENDENT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
