"""Separate tuple-matrix check of the scalar reduction and nine-call endpoint.

Enumerates all 2^16 binary matrices rather than outer-product parameters.
No primary-checker import. Finite corroboration, not a proof of all rational words.
Prepared for Tuafo with substantial OpenAI assistance. Apache-2.0.
"""
import itertools
import json
from pathlib import Path


def need(ok, why):
    if not ok:
        raise ValueError(why)


def zero(n):
    return tuple(tuple(0 for _ in range(n)) for _ in range(n))


def identity(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def plus(a, b):
    return tuple(tuple(x ^ y for x, y in zip(r, s)) for r, s in zip(a, b))


def times(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(len(b))) % 2
                       for j in range(len(b))) for i in range(len(a)))


def dimension(a):
    rows = [list(r) for r in a]
    pivot = 0
    for j in range(len(rows[0]) if rows else 0):
        found = next((i for i in range(pivot, len(rows)) if rows[i][j]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        for i in range(pivot + 1, len(rows)):
            if rows[i][j]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
    return pivot


def submatrix(a, ids):
    return tuple(tuple(a[i][j] for j in ids) for i in ids)


def rank_one_projection(a):
    return dimension(a) == 1 and times(a, a) == a


def check_scalar():
    z = zero(4)
    p = tuple(tuple(int(i == j and i < 3) for j in range(4)) for i in range(4))
    axes = [tuple(tuple(int(i == j == k) for j in range(4)) for i in range(4)) for k in range(3)]
    alphabet = []
    for entries in itertools.product((0, 1), repeat=16):
        a = tuple(tuple(entries[4*i:4*i+4]) for i in range(4))
        nonzero = {row for row in a if any(row)}
        if len(nonzero) == 1 and sum(a[i][i] for i in range(4)) % 2:
            need(rank_one_projection(a), 'Alphabet membership')
            alphabet.append(a)
    need(len(alphabet) == 120, 'Complete binary matrix census')
    index = {a: i for i, a in enumerate(alphabet)}
    triples = 0
    for i, a in enumerate(alphabet):
        for j in range(i+1, len(alphabet)):
            b = alphabet[j]
            c = plus(p, plus(a, b))
            if c not in index or index[c] <= j:
                continue
            for x in (a, b, c):
                for y in (a, b, c):
                    need(times(x, y) == (x if x == y else z), 'Orthogonal decomposition')
            triples += 1
    need(triples == 28, 'Rank-three decomposition count')
    records = []
    checked = partitioned = 0
    for q in alphabet:
        first = next(row for row in q if any(row))
        u = sum(int(any(row)) << i for i, row in enumerate(q))
        v = sum(x << i for i, x in enumerate(first))
        pool = set()
        for bits in itertools.product((0, 1), repeat=4):
            a = z
            for enabled, b in zip(bits, axes+[q]):
                if enabled:
                    a = plus(a, b)
            if rank_one_projection(a):
                pool.add(a)
        checked += len(pool)
        if not any(q[3]):
            kind, ids = 'active_image', None
            for a in pool:
                need(not any(a[3]) and rank_one_projection(submatrix(a, [0,1,2])), 'Active restriction')
        elif all(q[i][3] == 0 for i in range(4)):
            kind, ids = 'dirty_common_kernel', None
            for a in pool:
                need(all(a[i][3] == 0 for i in range(4)), 'Common kernel')
                need(rank_one_projection(submatrix(a, [0,1,2])), 'Quotient projector')
        else:
            i = next(i for i in range(3) if q[i][i] == 0)
            if first[i] == 0:
                kind, ids = 'active_line', [i]
            else:
                kind, ids = 'active_hyperplane', [j for j in range(4) if j != i]
            rest = [j for j in range(4) if j not in ids]
            need(sorted([dimension(submatrix(p, ids)), dimension(submatrix(p, rest))]) == [1,2], 'Target partition')
            for a in pool:
                need(all(a[r][c] == 0 for r in rest for c in ids), 'Invariant subspace')
                b, c = submatrix(a, ids), submatrix(a, rest)
                need(times(b,b) == b and times(c,c) == c, 'Induced idempotents')
                need(sorted([dimension(b),dimension(c)]) == [0,1], 'Disjoint call partition')
                partitioned += 1
        records.append(dict(u=u, v=v, case=kind, rank_one_members=len(pool), invariant_coordinates=ids))
    receipt = json.loads(Path(__file__).with_name('CERTIFICATE.json').read_text(encoding='utf-8'))
    need(sorted(records, key=lambda r:(r['u'],r['v'])) == receipt['cases'], 'Exact case receipt comparison')
    need(checked == 489 and partitioned == 144, 'All member counts')
    altered = [dict(r) for r in receipt['cases']]
    altered[0]['rank_one_members'] += 1
    need(sorted(records, key=lambda r:(r['u'],r['v'])) != altered, 'Count corruption not detected')
    return dict(idempotents=120, decompositions=triples, span_members=checked, call_partitions=partitioned)


def formal_word(n, factors):
    origin = (0,)*9
    result = {origin: identity(n)}
    for address, projector in factors:
        new = {}
        for exponent, coefficient in result.items():
            for offset, local in ((origin,plus(identity(n),projector)), (address,projector)):
                key = tuple(x+y for x,y in zip(exponent,offset))
                new[key] = plus(new.get(key,zero(n)), times(coefficient,local))
        result = {k:v for k,v in new.items() if any(any(row) for row in v)}
    return result


def check_attainment():
    # This integer target has determinant25 and is not diagonal.
    target = (1,2,0, 0,1,3, 4,0,1)
    need(target[0]*(target[4]*target[8]-target[5]*target[7])-target[1]*(target[3]*target[8]-target[5]*target[6])+target[2]*(target[3]*target[7]-target[4]*target[6]) == 25, 'Invertible target')
    columns = [tuple(target[3*i+j] if j == k else 0 for i in range(3) for j in range(3)) for k in range(3)]
    for n in (3,4,7):
        # Involutory scalar basis change, mixing active and dirty coordinates.
        s = [list(r) for r in identity(n)]
        for j in range(1,n):
            s[0][j] = 1
        s = tuple(map(tuple,s))
        need(times(s,s) == identity(n), 'Conjugating basis')
        factors, p = [], zero(n)
        for active in range(3):
            e = tuple(tuple(int(i == j == active) for j in range(n)) for i in range(n))
            q = times(times(s,e),s)
            need(rank_one_projection(q), 'Paid projector')
            p = plus(p,q)
            factors.extend((a,q) for a in columns)
        expected = {(0,)*9:plus(identity(n),p), target:p}
        expected = {k:v for k,v in expected.items() if any(any(row) for row in v)}
        need(formal_word(n,factors) == expected, 'Full formal nine-call endpoint')
        need(formal_word(n,factors[:-1]) != expected, 'Omitted-call control')
    return dict(nine_call_register_counts=[3,4,7], exact_formal_non_diagonal_target=True, omitted_call_controls=3)


if __name__ == '__main__':
    print('PASS_INDEPENDENT_IDENTICAL_THREE_DIRTY ' + json.dumps(dict(scalar=check_scalar(), attainment=check_attainment()), sort_keys=True))
