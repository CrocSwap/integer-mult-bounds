#!/usr/bin/env python3
"""Exact source-bound controls for the quotient prefix-rank consequence.
@CubeJerry; substantial OpenAI GPT-6 Astra Pro assistance. Apache-2.0.
The universal rank inequalities are proved in QUOTIENT-PREFIX-FLOOR.md.
"""
import argparse
import ast
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path


def need(ok, message):
    if not ok:
        raise ValueError(message)


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def mm(a, b):
    return [[sum(x*y for x, y in zip(r, c)) for c in zip(*b)] for r in a]


def outer(x, y):
    return [[a*b for b in y] for a in x]


def add(a, b, c=1):
    return [[x+c*y for x, y in zip(r, s)] for r, s in zip(a, b)]


def rank(matrix):
    a = [[Q(x) for x in row] for row in matrix]
    r = 0
    for c in range(len(a[0]) if a else 0):
        p = next((i for i in range(r, len(a)) if a[i][c]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        d = a[r][c]
        a[r] = [x/d for x in a[r]]
        for i in range(r+1, len(a)):
            d = a[i][c]
            if d:
                a[i] = [x-d*y for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def rejected(fn, message):
    try:
        fn()
    except ValueError:
        return
    raise ValueError('Negative control accepted: '+message)


def source_word(package):
    path = package/'retained'/'chain_root.py'
    data = path.read_bytes()
    need(hashlib.sha256(data).hexdigest() == '6f4046c804f27071d88ce05820c75baebe9cbf32533c4ba89285c413bfc8edaa', 'source SHA256')
    need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == 'ca1e0244f1329c153c1224b05bf0c0c5d5e2367b', 'source Git blob')
    names = {'fields', 'vector', 'thin_vectors', 'sites'}
    functions = [node for node in ast.parse(data).body if isinstance(node, ast.FunctionDef) and node.name in names]
    need({node.name for node in functions} == names, 'four pinned constructor functions')
    scope = {'Q': Q}
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(path), 'exec'), scope)
    source = scope['sites']([1]*9, [1]*9)
    need(len(source) == 21, 'source has eighteen full plus three thin factors')
    e = [Q(j == 19) for j in range(20)]
    u = [x-y for x, y in zip(source[9][0], e)]
    w = [x-y for x, y in zip(source[10][1], e)]
    v = [x-y for x, y in zip(u, source[10][0])]
    z = [x-y for x, y in zip(source[9][1], w)]
    p = add(outer(e, e), outer(v, z))
    need(mm(p, p) == p and rank(p) == 2, 'common idle projector')
    word = [(x, y) for x, y, *_ in source[:9]] + [(u, w)] + [(x, y) for x, y, *_ in source[12:]]
    need(len(word) == 19, 'shortened query count')
    return word, p


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    word, p = source_word(args.package)
    n = 18
    gram = [[sum(a*b for a, b in zip(y, x)) for x, _ in word] for _, y in word]
    need(gram == [[Q((i > j)-(i < j)) for j in range(19)] for i in range(19)], 'all 361 quotient Gram entries')
    basis = [list(row) for row in zip(*(x for x, _ in word[:18]))]
    need(rank(basis) == 18 and mm(p, basis) == [[0]*18 for _ in range(20)], 'basis spans the invariant complement')
    full = set(range(19)) - {9}
    even = list(range(2, 18, 2))
    need(len(full) == 18 and len(even) == 8 and set(even) <= full, 'eight even interior full sites')
    prefix, source_prefix = eye(18), eye(20)
    records, saved = [], {}
    for i, (sx, sy) in enumerate(word):
        x = [Q(i == j) for j in range(n)] if i < n else [Q((-1)**(j+1)) for j in range(n)]
        y = [Q((i > j)-(i < j)) for j in range(n)]
        need(mm(basis, [[a] for a in x]) == [[a] for a in sx], 'canonical column equals exact source quotient column')
        need(mm([sy], basis) == [y], 'canonical row equals exact restricted source row')
        need(any(sx) and any(sy) and sum(a*b for a, b in zip(sx, sy)) == 0, 'nonzero square-zero source query')
        prefix = add(prefix, outer(x, mm([y], prefix)[0]), -2)
        source_prefix = add(source_prefix, outer(sx, mm([sy], source_prefix)[0]), -2)
        need(mm(source_prefix, basis) == mm(basis, prefix), 'actual prefix transfers through quotient basis')
        if i in even:
            u = [Q((-1)**j if j < i else 0) for j in range(n)]
            v = [Q(j < i) for j in range(n)]
            px, yp = mm(prefix, [[a] for a in x]), mm([y], prefix)[0]
            need(px == [[a+2*b] for a, b in zip(x, u)], 'even prefix column formula')
            need(yp == [a-2*b for a, b in zip(y, v)], 'even prefix row formula')
            columns = [[a, b[0]] for a, b in zip(x, px)]
            rows = [y, yp]
            need(rank(columns) == rank(rows) == 2 and mm(rows, columns) == [[0, 0], [0, 0]], 'two zero-paired prefix closures')
            records.append({'position': i, 'source_site': ('L'+str(i)) if i < 9 else ('R'+str(i-10)),
                            'column_rank': 2, 'row_rank': 2, 'pairing_rank': 0, 'stage_rank_floor': 4})
            saved[i] = (x, y, [r[:] for r in prefix])
    need(prefix == [[-v for v in row] for row in eye(18)], 'quotient endpoint -I18')
    need(source_prefix == add([[ -v for v in row] for row in eye(20)], p, 2), 'ambient shortened endpoint -I20+2P')
    x, y, b = saved[2]
    w = [Q(j == 0) for j in range(n)]
    local = add(outer(x, x), outer(w, y))
    query = outer(x, y)
    need(rank(local) == 2 and mm(local, local) == local, 'rank-two omitted-prefix control')
    need(mm(local, query) == query and mm(query, local) == query, 'control supports query on both sides')
    commutator = add(mm(local, b), mm(b, local), -1)
    need(rank(commutator) > 0, 'support alone does not imply prefix compatibility')
    rejected(lambda: need(mm(local, b) == mm(b, local), 'prefix commutation'), 'omitted prefix')
    bound = 8*4 + 8*3 + 2*2
    need(bound == 60, 'rank60 arithmetic from eight even floors and known at-most-two rank-two supports')
    rejected(lambda: need(all(3 >= r['stage_rank_floor'] for r in records), 'uniform rank three'), 'uniform rank-three census')
    rejected(lambda: need(18*3 >= bound, 'balanced degree-three census'), '54-incidence census')
    result = {'status': 'PASS_QUOTIENT_PREFIX_RANK60', 'source_head': '51f54e3c31f2f3a3e056a483b3ed66ae916ad06a',
              'quotient': {'n': 18, 'queries': 19, 'full': 18, 'thin_position': 9},
              'even_full_positions': records, 'total_stage_rank_lower_bound': bound,
              'rank_two_stage_cap': {'value': 2, 'proof': 'QUOTIENT-SUPPORT-COROLLARY.md; not inferred from this finite replay'},
              'omitted_prefix_control': {'position': 2, 'supporting_idempotent_rank': 2, 'prefix_commutator_rank': rank(commutator)},
              'blocked_censuses': ['all eighteen stages rank three', 'eighteen outputs each of incidence degree three; total54'],
              'scope': 'Commuting supporting idempotents that commute with their actual prefixes; rank60 is necessary, not attained.',
              'new_kappa': False}
    print(json.dumps(result, indent=2))
    print(result['status'])


if __name__ == '__main__':
    main()
