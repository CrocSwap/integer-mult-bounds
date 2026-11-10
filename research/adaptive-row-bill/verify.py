"""Independent finite controls for the adaptive bill certificate.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as Q
from itertools import combinations, combinations_with_replacement, permutations, product
import json
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
api = run_path(str(ROOT/'bills.py'))
certify, check = api['certify'], api['check']


def require(ok, message):
    if not ok:
        raise ValueError(message)


def det(a):
    n = len(a)
    answer = Q(0)
    for perm in permutations(range(n)):
        value = Q((-1)**sum(perm[i] > perm[j] for i in range(n) for j in range(i+1, n)))
        for i, j in enumerate(perm):
            value *= a[i][j]
        answer += value
    return answer


def oracle(a):
    n = len(a)
    m = [[Q(i == j)-a[i][j] for j in range(n)] for i in range(n)]
    for k in range(1, n+1):
        for indices in combinations(range(n), k):
            if det([[m[i][j] for j in indices] for i in indices]) <= 0:
                return None
    denominator = det(m)
    return [det([[Q(1) if j == col else m[i][j] for j in range(n)]
                 for i in range(n)])/denominator for col in range(n)]


def problem(rows):
    return {'schema': 'adaptive-row-bill/v1',
            'rows': [[[str(x) for x in row] for row in menu] for menu in rows]}


counts = {'families': 0, 'safe': 0, 'unsafe': 0, 'policies': 0,
          'prefix_checks': 0, 'rejections': 0}


def examine(rows):
    p = problem(rows)
    saved = deepcopy(p)
    certificate = certify(p)
    require(check(p, certificate), 'Certificate rejected')
    totals = []
    for policy in product(*(range(len(menu)) for menu in rows)):
        totals.append(oracle([rows[i][a] for i, a in enumerate(policy)]))
        counts['policies'] += 1
    safe = all(t is not None for t in totals)
    require((certificate['status'] == 'safe') == safe, 'Independent principal-minor decision differs')
    if safe:
        u = list(map(Q, certificate['total']))
        q = Q(certificate['ratio'])
        expected = [max(t[i] for t in totals) for i in range(len(rows))]
        require(u == expected and u in totals, 'Independent Cramer total differs')
        value = [Q(0)]*len(rows)
        for depth in range(9):
            require(all(0 <= u[i]-value[i] <= q**depth*u[i] for i in range(len(rows))),
                    'Finite-depth tail bound failed')
            value = [1+max(sum(row[j]*value[j] for j in range(len(rows))) for row in menu)
                     for menu in rows]
            counts['prefix_checks'] += 1
    require(p == saved, 'Input changed')
    counts['families'] += 1
    counts[certificate['status']] += 1


grid = list(product([Q(0), Q(1, 2), Q(3, 2)], repeat=2))
menus = list(combinations_with_replacement(grid, 2))
for rows in product(menus, repeat=2):
    examine(rows)

binary = list(product([Q(0), Q(1, 2)], repeat=3))
for selected in product(binary, repeat=3):
    examine([[row, tuple(Q(1, 2)-x for x in row)] for row in selected])

p = json.loads((ROOT/'example.json').read_text())
c = certify(p)
require(c['total'] == ['5', '3'] and c['ratio'] == '4/5', 'Example differs')
examine([[[Q(x) for x in row] for row in menu] for menu in p['rows']])

bad = problem([[(0, 2), (0, 0)], [(0, 0), (2, 0)]])
require(certify(bad)['status'] == 'unsafe', 'Mixed-row fault was missed')
require(oracle([[Q(0), Q(2)], [Q(0), Q(0)]]) is not None
        and oracle([[Q(0), Q(0)], [Q(2), Q(0)]]) is not None, 'Whole-mode control failed')

for n in [1, 4, 16, 64]:
    rows = []
    for i in range(n):
        row = [Q(0)]*n
        if i+1 < n:
            row[i+1] = Q(1, 2)
        rows.append([[Q(0)]*n, row])
    result = certify(problem(rows))
    require(list(map(Q, result['total'])) == [2-Q(1, 2)**(n-i-1) for i in range(n)],
            'Chain total differs')


def rejects(function, *args):
    try:
        function(*args)
    except (ValueError, TypeError, ZeroDivisionError):
        counts['rejections'] += 1
        return
    raise ValueError('Invalid input or certificate accepted')


for key, value in [('total', ['4', '3']), ('ratio', '1/2'), ('policy', [0, 0]),
                   ('policy', [True, 0]), ('total', ['5']), ('status', 'unknown')]:
    fault = deepcopy(c)
    fault[key] = value
    rejects(check, p, fault)
unsafe = certify(bad)
for value in [['0', '0'], ['-1', '1'], ['1', '0'], ['1']]:
    fault = deepcopy(unsafe)
    fault['witness'] = value
    rejects(check, bad, fault)
for value in [{}, {'schema': 'adaptive-row-bill/v1', 'rows': []},
              problem([[[-1]]]), problem([[[1, 0]]]), problem([[[]]]),
              {'schema': 'adaptive-row-bill/v1', 'rows': [[[True]]]}]:
    rejects(certify, value)
rejects(certify, p, 1)
rejects(certify, p, 0)
print(json.dumps({'status': 'PASS_ADAPTIVE_ROW_BILL', **counts}, sort_keys=True))
