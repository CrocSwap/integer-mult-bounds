"""Exact rational kernel-bijection replay on the pinned 6x6 source example.
No predecessor arithmetic imports or finite-census/minor calls.
@woklerx with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('nullity_sources', HERE / 'verify.py')
sources = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sources)
need = sources.need


def rref(rows, width):
    a = [list(map(Q, row)) for row in rows]
    need(all(len(row) == width for row in a), 'matrix width')
    pivots = []
    for col in range(width):
        k = len(pivots)
        pivot = next((i for i in range(k, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[k], a[pivot] = a[pivot], a[k]
        scale = a[k][col]
        a[k] = [x/scale for x in a[k]]
        for i in range(len(a)):
            if i != k:
                scale = a[i][col]
                a[i] = [x-scale*y for x, y in zip(a[i], a[k])]
        pivots.append(col)
    return a, pivots


def inverse(a):
    n = len(a)
    rows = [list(row) + [int(i == j) for j in range(n)] for i, row in enumerate(a)]
    reduced, pivots = rref(rows, 2*n)
    need(pivots == list(range(n)), 'invertible source matrix')
    return [row[n:] for row in reduced]


def multiply(a, x):
    return [sum(u*v for u,v in zip(row,x)) for row in a]


def kernel(rows, width):
    reduced, pivots = rref(rows, width)
    vectors = []
    for free in range(width):
        if free in pivots:
            continue
        v = [Q(0)]*width
        v[free] = Q(1)
        for r, pivot in enumerate(pivots):
            v[pivot] = -reduced[r][free]
        need(not any(multiply(rows, v)), 'kernel membership')
        vectors.append(v)
    need(len(vectors) + len(pivots) == width, 'rank-nullity coverage')
    return vectors, len(pivots)


def check_inverse(a, b):
    n = len(a)
    for left, right in ((a,b), (b,a)):
        need(all(sum(left[i][k]*right[k][j] for k in range(n)) == int(i == j)
                 for i in range(n) for j in range(n)), 'two-sided inverse')


def correspondence(a, b, i, j):
    n = len(a)
    need(len(set(i)) == len(i) and len(set(j)) == len(j)
         and all(type(k) is int and 0 <= k < n for k in i+j), 'index subsets')
    ic, jc = [k for k in range(n) if k not in i], [k for k in range(n) if k not in j]
    left = [[a[r][c] for c in j] for r in i]
    right = [[b[r][c] for c in ic] for r in jc]
    u, ra = kernel(left, len(j))
    v, rb = kernel(right, len(ic))
    need(len(u) == len(v), 'equal complementary nullities')
    mapped = []
    for matrix, undo, domain, codomain, basis in ((a,b,j,ic,u), (b,a,ic,j,v)):
        for vector in basis:
            x = [Q(0)]*n
            for k, value in zip(domain, vector):
                x[k] = value
            y = multiply(matrix, x)
            need(all(y[k] == 0 for k in range(n) if k not in codomain), 'image support')
            need(multiply(undo, y) == x, 'inverse kernel transport')
            mapped.append([str(z) for z in x+y])
    need(ra - rb == len(i)+len(j)-n, 'rank offset')
    return ra, rb, mapped


def run():
    sources.pins()
    raw, receipt = sources.source_matrix()
    a = [list(map(Q, row)) for row in raw]
    b = inverse(a)
    check_inverse(a,b)
    need([[str(x) for x in row] for row in b] == receipt['B'], 'source rational inverse receipt')
    subsets = [[k for k in range(6) if mask >> k & 1] for mask in range(64)]
    histogram = Counter()
    trace = sha256()
    pairs, transported = 0, 0
    for i in subsets:
        for j in subsets:
            ra, rb, maps = correspondence(a,b,i,j)
            histogram[(len(i),len(j),ra,rb)] += 1
            trace.update(sources.canonical([i,j,ra,rb,maps]).encode())
            pairs += 1
            transported += len(maps)
    need(pairs == 4096, 'all source subblocks including empty/full')
    a00 = len(rref([row[:2] for row in a[:2]], 2)[1])
    a11 = len(rref([row[2:] for row in a[2:]], 4)[1])
    b00 = len(rref([row[:2] for row in b[:2]], 2)[1])
    b11 = len(rref([row[2:] for row in b[2:]], 4)[1])
    need([a00,a11,b00,b11] == [2,4,2,4], 'actual mixed-rank local obligation')
    restrictions = []
    for label in range(3):
        for block in (1,2):
            ar = len(rref([row[2*label:2*label+2] for row in a[2*block:2*block+2]], 2)[1])
            br = len(rref([row[2*block:2*block+2] for row in b[2*label:2*label+2]], 2)[1])
            need(ar == br == 1, 'source regular-block restriction')
            restrictions.append([label,block,ar,br])
    return {'schema': 1, 'source_inverse': [[str(x) for x in row] for row in b],
            'all_source_block_pairs': pairs, 'transported_kernel_basis_vectors': transported,
            'complete_trace_sha256': trace.hexdigest(), 'source_block_ranks_A00_A11_B00_B11': [a00,a11,b00,b11],
            'regular_block_restrictions': restrictions,
            'rank_histogram': {','.join(map(str,k)): v for k,v in sorted(histogram.items())}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    actual = run()
    path = HERE / 'KERNEL-CERTIFICATE.json'
    if args.write:
        path.write_text(json.dumps(actual, indent=2) + '\n', encoding='utf-8')
    else:
        need(sources.canonical(actual) == sources.canonical(json.loads(path.read_text(encoding='utf-8'))), 'complete kernel receipt mismatch')
    print('PASS_COMPLEMENTARY_KERNEL_SOURCE block_pairs=4096 ranks=2,4,2,4 no_new_Fano_exclusion')
