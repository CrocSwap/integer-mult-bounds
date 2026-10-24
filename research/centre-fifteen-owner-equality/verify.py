"""Bounded exact corroboration of the fifteen-owner equality theorem."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
import sys

MAX_SIDE = 32


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(rows: tuple[int, ...], columns: int) -> tuple[int, ...]:
    require(type(columns) is int and 1 <= columns <= MAX_SIDE, 'column bound')
    require(1 <= len(rows) <= MAX_SIDE, 'row bound')
    require(all(type(r) is int and 0 <= r < 1 << columns for r in rows),
            'invalid row')
    return tuple(sum(1 << i for i, r in enumerate(rows) if r >> j & 1)
                 for j in range(columns))


def four_free(rows: tuple[int, ...]) -> bool:
    return all((a & b).bit_count() <= 1
               for a, b in itertools.combinations(rows, 2))


def cycles_by_intersections(rows: tuple[int, ...]) -> set[tuple[int, ...]]:
    require(four_free(rows), 'four-cycle present')
    cycles = set()
    for a, b, c in itertools.combinations(range(len(rows)), 3):
        x, y, z = rows[a] & rows[b], rows[b] & rows[c], rows[c] & rows[a]
        if x and y and z and len({x, y, z}) == 3:
            edges = tuple(sorted((a * MAX_SIDE + x.bit_length() - 1,
                                  b * MAX_SIDE + x.bit_length() - 1,
                                  b * MAX_SIDE + y.bit_length() - 1,
                                  c * MAX_SIDE + y.bit_length() - 1,
                                  c * MAX_SIDE + z.bit_length() - 1,
                                  a * MAX_SIDE + z.bit_length() - 1)))
            cycles.add(edges)
    return cycles


def cycles_by_walks(rows: tuple[int, ...], columns: int) -> set[tuple[int, ...]]:
    cols = validate(rows, columns)
    require(all(r.bit_count() <= 3 for r in rows + cols), 'walk degree bound')
    size = len(rows)
    adjacency = [tuple(size + j for j in range(columns) if r >> j & 1)
                 for r in rows]
    adjacency += [tuple(i for i in range(size) if r >> i & 1) for r in cols]
    cycles = set()
    for root in range(size):
        paths = [(root,)]
        for _ in range(5):
            paths = [path + (v,) for path in paths
                     for v in adjacency[path[-1]] if v not in path]
        for path in paths:
            if root not in adjacency[path[-1]]:
                continue
            edges = []
            for a, b in zip(path, path[1:] + (root,)):
                if a >= size:
                    a, b = b, a
                edges.append(a * MAX_SIDE + b - size)
            cycles.add(tuple(sorted(edges)))
    return cycles


def incidence_product(rows: tuple[int, ...], columns: int) -> list[list[int]]:
    # Literal matrix product, separate from the path/edge-set enumerators.
    common = [[sum((a >> j & 1) * (b >> j & 1) for j in range(columns))
               for b in rows] for a in rows]
    return [[sum(common[i][k] * (rows[k] >> j & 1)
                 for k in range(len(rows))) for j in range(columns)]
            for i in range(len(rows))]


def cycle_counts(cycles: set[tuple[int, ...]], size: int) -> tuple[list[int], list[int]]:
    left, right = [0] * size, [0] * size
    for cycle in cycles:
        for i in {e // MAX_SIDE for e in cycle}:
            left[i] += 1
        for j in {e % MAX_SIDE for e in cycle}:
            right[j] += 1
    return left, right


def check_defect(rows: tuple[int, ...]) -> dict[str, int]:
    cols = validate(rows, 15)
    require(len(rows) == 15 and all(r.bit_count() == 3 for r in rows + cols),
            'cubic fifteen-by-fifteen boundary')
    cycles = cycles_by_intersections(rows)
    require(cycles == cycles_by_walks(rows, 15), 'independent cycle disagreement')
    left, right = cycle_counts(cycles, 15)
    require(max(left + right) <= 1, 'six-cycle capacity exceeded')
    product = incidence_product(rows, 15)
    defect = [[product[i][j] - 4 * (rows[i] >> j & 1) - 1
               for j in range(15)] for i in range(15)]
    for i in range(15):
        require(sorted(x for x in defect[i] if x) == [-1, 1] * left[i],
                'row defect')
    for j in range(15):
        require(sorted(defect[i][j] for i in range(15) if defect[i][j])
                == [-1, 1] * right[j], 'column defect')
    for cycle in cycles:
        bset = {e // MAX_SIDE for e in cycle}
        dset = {e % MAX_SIDE for e in cycle}
        for i in bset:
            positive = [j for j in dset if not (rows[i] >> j & 1)]
            require(len(positive) == 1 and defect[i][positive[0]] == 1,
                    'opposite endpoint')
            require(all(defect[i][j] != -1 for j in dset), 'negative same-cycle')
    require(len(cycles) != 1, 'single six-cycle equality impossible')
    for i in range(15):
        for j in range(15):
            lhs = sum(defect[i][k] * (rows[j] >> k & 1) for k in range(15))
            rhs = sum((rows[i] >> k & 1) * defect[j][k] for k in range(15))
            require(lhs == rhs, 'defect symmetry')
    return {'six_cycles': len(cycles), 'active_vertices_per_part': sum(left)}


def doily() -> tuple[int, ...]:
    duads = list(itertools.combinations(range(6), 2))
    matchings = [t for t in itertools.combinations(range(15), 3)
                 if len({x for i in t for x in duads[i]}) == 6]
    require(len(matchings) == 15, 'matching construction')
    return tuple(sum(1 << j for j, block in enumerate(matchings) if i in block)
                 for i in range(15))


def path_profile(profile: tuple[int, ...]) -> list[int]:
    require(len(profile) == 12, 'twelve nonneighbors required')
    require(all(type(p) is int and 0 <= p <= 12 for p in profile),
            'invalid path count')
    require(sum(profile) == 12, 'twelve paths required')
    require(sum(p * (p - 1) // 2 for p in profile) <= 1, 'local cycle capacity')
    return sorted(p - 1 for p in profile if p != 1)


def profile_checks() -> dict[str, int]:
    accepted = 0
    doubled = 0
    for profile in itertools.product(range(3), repeat=12):
        if sum(profile) != 12 or sum(p == 2 for p in profile) > 1:
            continue
        excess = sum(p * (p - 1) // 2 for p in profile)
        values = path_profile(profile)
        require(values == ([-1, 1] if excess else []), 'local path defect')
        accepted += 1
        doubled += excess
    require((accepted, doubled) == (133, 132), 'local profile completeness')
    # A count >=3 would already give at least three six-cycles.
    require(all(p * (p - 1) // 2 > 1 for p in range(3, 13)), 'large count')
    bounds = [5 * k - k * k // 4 for k in range(4, 16)]
    require(min(bounds) == 16, 'noncubic degree exclusion')
    return {'profiles_visited': 3 ** 12, 'admitted_profiles': accepted,
            'nonzero_profiles': doubled, 'degree_cases': len(bounds)}


def switching_checks(base: tuple[int, ...]) -> dict[str, int | str]:
    edges = [(i, j) for i, r in enumerate(base) for j in range(15) if r >> j & 1]
    counts = {'switches': 0, 'four_free': 0, 'capacity_rejected': 0}
    digest = hashlib.sha256()
    for (a, x), (b, y) in itertools.combinations(edges, 2):
        if a == b or x == y or base[a] >> y & 1 or base[b] >> x & 1:
            continue
        rows = list(base)
        rows[a] ^= (1 << x) | (1 << y)
        rows[b] ^= (1 << x) | (1 << y)
        counts['switches'] += 1
        trial = tuple(rows)
        if not four_free(trial):
            continue
        counts['four_free'] += 1
        cycles = cycles_by_intersections(trial)
        require(cycles == cycles_by_walks(trial, 15), 'switched cycle mismatch')
        left, right = cycle_counts(cycles, 15)
        if max(left + right) > 1:
            counts['capacity_rejected'] += 1
        else:
            check_defect(trial)
        digest.update(json.dumps(sorted(cycles), separators=(',', ':')).encode())
    require(counts['switches'] == 720, 'switch-domain enumeration')
    counts['cycle_digest'] = digest.hexdigest()
    return counts


def controls(base: tuple[int, ...]) -> int:
    rejected = 0
    fixtures = [(base[:-1], 15), (base, 14), (base + (True,), 15),
                (base + (-1,), 15)]
    for rows, columns in fixtures:
        try:
            cols = validate(rows, columns)
            require(len(rows) == 15 and all(r.bit_count() == 3 for r in rows + cols),
                    'wrong equality boundary')
        except ValueError:
            rejected += 1
    require(rejected == len(fixtures), 'invalid boundary accepted')
    # This cubic fifteen-by-fifteen graph is C4-free but violates the cycle cap.
    cyclic = tuple(sum(1 << ((i + shift) % 15) for shift in (0, 1, 3))
                   for i in range(15))
    require(four_free(cyclic), 'cyclic capacity control must be C4-free')
    try:
        check_defect(cyclic)
    except ValueError as error:
        require(str(error) == 'six-cycle capacity exceeded', 'wrong control cause')
        rejected += 1
    else:
        raise ValueError('capacity violation accepted')
    malformed_profiles = [(2,) + (1,) * 11, (2, 2, 0, 0) + (1,) * 8,
                          (True,) + (1,) * 11, (1,) * 11]
    for profile in malformed_profiles:
        try:
            path_profile(profile)
        except ValueError:
            rejected += 1
        else:
            raise ValueError('malformed path profile accepted')
    return rejected


def main() -> None:
    require(len(sys.argv) == 1, 'this verifier accepts no arguments')
    base = doily()
    result = {'scope': 'scoped equality proof; finite corroboration only',
              'doily': check_defect(base), 'local_profiles': profile_checks(),
              'switching': switching_checks(base), 'controls': controls(base)}
    root = Path(__file__).resolve().parent
    names = ('README.md', 'PROOF.md', 'TASK.json', 'SOURCES.json',
             'VERIFY.json', 'verify.py')
    hashes = {}
    for name in names:
        path = root / name
        require(path.stat().st_size <= 262144, 'package file bound')
        hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    result['source_sha256'] = hashes
    print(json.dumps(result, sort_keys=True))
    print('PASS_CENTRE_FIFTEEN_OWNER_EQUALITY')


if __name__ == '__main__':
    main()
