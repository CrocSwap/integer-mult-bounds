"""Check small equality cases of the affine-sector classification."""

from hashlib import sha256
from itertools import combinations, product
from math import prod
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[3]
SOURCE = LANES / 'portable-source-codes/correlated-access-20261015/ACCESS.md'
PIN = 'a5a91cdc4deed08aa15693aedbcc01f48186859f8902acdb864aa74fb6feba4d'


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def dot(a, b):
    return (a & b).bit_count() % 2


def subspaces(m, rank):
    for pivots in combinations(range(m), rank):
        entries = [(i, j) for i, p in enumerate(pivots)
                   for j in range(p + 1, m) if j not in pivots]
        for bits in range(1 << len(entries)):
            basis = [1 << p for p in pivots]
            for k, (i, j) in enumerate(entries):
                if bits & (1 << k):
                    basis[i] |= 1 << j
            yield tuple(basis)


def span(basis):
    result = [0]
    for v in basis:
        result += [w ^ v for w in result]
    need(len(result) == len(set(result)), 'Independent basis')
    return frozenset(result)


def cosets(m, subspace):
    remaining = set(range(1 << m))
    while remaining:
        a = min(remaining)
        block = frozenset(a ^ w for w in subspace)
        remaining.difference_update(block)
        yield a, block


def member(matrix, n, width):
    rows = [(matrix >> (i * width)) & ((1 << width) - 1) for i in range(n)]
    phases = set()
    for q in range(1 << n):
        if q.bit_count() % 2:
            total = 0
            for i, row in enumerate(rows):
                if q & (1 << i):
                    total ^= row
            phases.add(total.bit_count() % 4)
    return len(phases) == 1


def constant_cosets(width, subspace):
    return [(a, block) for a, block in cosets(width, subspace)
            if len({v.bit_count() % 4 for v in block}) == 1]


def sector(width, subspace, n=3):
    choices = constant_cosets(width, subspace)
    need(len(choices) == 1 + width % 2, 'One even or two odd constant cosets')
    result = set()
    for _, block in choices:
        for rows in product(block, repeat=n):
            result.add(sum(row << (i * width) for i, row in enumerate(rows)))
    return frozenset(result)


def row_codes(width):
    f = width // 2
    maxima, best = [], [-1] * 4
    checked_cosets = 0
    for rank in range(f + 1):
        for basis in subspaces(width, rank):
            if any(dot(a, b) for a in basis for b in basis):
                continue
            subspace = span(basis)
            good = constant_cosets(width, subspace)
            checked_cosets += (1 << width) // len(subspace)
            for a, _ in good:
                d = a.bit_count() % 4
                best[d] = max(best[d], rank)
            if rank == f:
                maxima.append(subspace)
                residues = {a.bit_count() % 4 for a, _ in good}
                expected = {f % 4} if width % 2 == 0 else {f % 4, (f + 1) % 4}
                need(residues == expected, 'Preferred residues from the Gauss sum')
    count = prod((1 << j) + 1 for j in range(1, f + (width % 2)))
    need(len(maxima) == count, 'Number of maximal self-orthogonal codes')
    actual_sectors = {sector(width, w) for w in maxima}
    need(len(actual_sectors) == count, 'Distinct codes give distinct maximal sectors')
    expected_dimension = 3 * f + width % 2
    for block in actual_sectors:
        need(len(block) == 1 << expected_dimension, 'Constructed sector dimension')
        need(all(member(x, 3, width) for x in block), 'All odd rows have one phase')
    preferred = {f % 4} if width % 2 == 0 else {f % 4, (f + 1) % 4}
    expected_best = [f if d in preferred else f - 1 for d in range(4)]
    if width == 1:
        expected_best = [0, 0, -1, -1]
    elif width == 2:
        expected_best = [0, 1, 0, -1]
    need(best == expected_best, 'Sharp fixed-residue dimensions')
    return {
        'width': width, 'maximal_codes': len(maxima),
        'constant_coset_dimension_by_residue': best,
        'all_self_orthogonal_code_cosets_checked': checked_cosets,
    }, actual_sectors


def affine_exhaustion(width, expected):
    n, m = 3, 3 * width
    dimension = n * (width // 2) + width % 2
    allowed = {x for x in range(1 << m) if member(x, n, width)}
    found, tested, directions = set(), 0, 0
    for basis in subspaces(m, dimension):
        directions += 1
        for _, block in cosets(m, span(basis)):
            tested += 1
            if block <= allowed:
                found.add(block)
    need(found == expected, 'Complete small affine equality classification')
    return {'n': n, 'width': width, 'directions': directions,
            'affine_sets_tested': tested, 'maximal_sectors_found': len(found)}


def main():
    need(sha256(SOURCE.read_bytes()).hexdigest() == PIN, 'Affine source pin')
    rows, sectors = [], {}
    for width in range(1, 7):
        result, blocks = row_codes(width)
        rows.append(result)
        sectors[width] = blocks
    exhaustive = [affine_exhaustion(width, sectors[width]) for width in [1, 2]]
    diagonal = frozenset(x | (x << 2) for x in range(4))
    need(all(member(x, 2, 2) for x in diagonal), 'The n=2 diagonal is a sector')
    need(len(diagonal) == 4, 'The n=2 diagonal attains the bound')
    need(len({x & 3 for x in diagonal}) == 4, 'The n=2 diagonal is not a rank-one row product')
    result = {
        'status': 'PASS_SMALL_MAXIMAL_AFFINE_SECTOR_CLASSIFICATION',
        'source_pin': PIN, 'producer_imported_or_executed': False,
        'row_code_cases': rows, 'complete_affine_searches': exhaustive,
        'n2_counterexample': {'width': 2, 'points': sorted(diagonal), 'row_projection_dimension': 2},
        'scope': 'Finite checks support the separate general proof. No stream or supplier claim.',
    }
    (HERE / 'CHECK.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(result['status'])
    print(json.dumps({'affine_sets_tested': sum(c['affine_sets_tested'] for c in exhaustive),
                      'maximal_row_codes': sum(c['maximal_codes'] for c in rows)}))


if __name__ == '__main__':
    main()
