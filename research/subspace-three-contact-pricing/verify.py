#!/usr/bin/env python3
"""Exact finite corroboration of the scoped three-contact pricing theorem."""
import argparse
import hashlib
import json
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_FILES = ('README.md', 'SOURCES.json', 'TASK.json', 'VERIFY.json', 'verify.py')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_package_file(name):
    path = ROOT / name
    require(path.stat().st_size <= 1024 * 1024, 'package file exceeds 1 MiB')
    return path.read_bytes()


def vector_add(a, b, q, n):
    result, place = 0, 1
    for _ in range(n):
        result += ((a % q + b % q) % q) * place
        a, b, place = a // q, b // q, place * q
    return result


def vector_scale(a, scalar, q, n):
    result, place = 0, 1
    for _ in range(n):
        result += ((a % q * scalar) % q) * place
        a, place = a // q, place * q
    return result


def members(mask, size):
    return tuple(v for v in range(size) if (mask >> v) & 1)


def enumerate_spaces(q, n):
    """All RREF bases, encoded independently as sets of actual vectors."""
    require(q in (2, 3) and 1 <= n <= (4 if q == 2 else 3), 'finite domain')
    masks = set()
    for rank in range(n + 1):
        for pivots in combinations(range(n), rank):
            free = tuple((i, j) for i, pivot in enumerate(pivots)
                         for j in range(pivot + 1, n) if j not in pivots)
            for entries in product(range(q), repeat=len(free)):
                rows = [q ** pivot for pivot in pivots]
                for (i, j), value in zip(free, entries):
                    rows[i] += value * q ** j
                mask = 0
                for coefficients in product(range(q), repeat=rank):
                    value = 0
                    for row, coefficient in zip(rows, coefficients):
                        value = vector_add(value, vector_scale(row, coefficient, q, n), q, n)
                    mask |= 1 << value
                require(mask.bit_count() == q ** rank, 'RREF independence')
                require(mask not in masks, 'distinct RREF bases must give distinct subspaces')
                masks.add(mask)
    return tuple(sorted(masks))


def geometry(q, n):
    spaces = enumerate_spaces(q, n)
    size = q ** n
    index = {mask: i for i, mask in enumerate(spaces)}
    dimension = {q ** d: d for d in range(n + 1)}
    dims = tuple(dimension[mask.bit_count()] for mask in spaces)
    vectors = tuple(members(mask, size) for mask in spaces)
    meets, joins, distances = [], [], []
    for i, left in enumerate(spaces):
        meet_row, join_row, distance_row = [], [], []
        for j, right in enumerate(spaces):
            meet = index[left & right]
            span = 0
            for a in vectors[i]:
                for b in vectors[j]:
                    span |= 1 << vector_add(a, b, q, n)
            meet_row.append(meet)
            join_row.append(index[span])
            distance_row.append(dims[i] + dims[j] - 2 * dims[meet])
        meets.append(tuple(meet_row))
        joins.append(tuple(join_row))
        distances.append(tuple(distance_row))
    return spaces, tuple(meets), tuple(joins), tuple(distances)


def median(a, b, c, meets, joins):
    return joins[joins[meets[a][b]][meets[b][c]]][meets[c][a]]


def branches(a, b, c, distances):
    ab, bc, ca = distances[a][b], distances[b][c], distances[c][a]
    require((ab + bc + ca) % 2 == 0, 'integer median radii')
    return ((ab + ca - bc) // 2, (ab + bc - ca) // 2, (bc + ca - ab) // 2)


def domination(actual, radii):
    """Return the median or one median-to-terminal segment dominated by actual."""
    depressed = tuple(i for i in range(3) if actual[i] < radii[i])
    require(len(depressed) <= 1, 'two depressed radii violate triangle inequality')
    if not depressed:
        return None
    i = depressed[0]
    delta = radii[i] - actual[i]
    point = tuple(actual[i] if j == i else radii[j] + delta for j in range(3))
    require(all(point[j] <= actual[j] for j in range(3)), 'segment domination')
    return i


def collect_domain(q, n):
    spaces, meets, joins, distances = geometry(q, n)
    signatures = set()
    triples = comparisons = segments = 0
    for a, b, c in combinations_with_replacement(range(len(spaces)), 3):
        contacts = (a, b, c)
        radii = branches(a, b, c, distances)
        m = median(a, b, c, meets, joins)
        require(tuple(distances[m][v] for v in contacts) == radii, 'median identity')
        attainable = set()
        for x in range(len(spaces)):
            actual = tuple(distances[x][v] for v in contacts)
            segments += domination(actual, radii) is not None
            attainable.add(actual)
            comparisons += 1
        candidates = tuple(tuple(distances[x][v] for v in contacts) for x in (a, b, c, m))
        signatures.add((candidates, tuple(sorted(attainable))))
        triples += 1
    report = {'q': q, 'n': n, 'spaces': len(spaces), 'unordered_contact_triples': triples,
              'all_frame_comparisons': comparisons, 'segment_cases': segments,
              'distinct_optimization_signatures': len(signatures)}
    return report, tuple(sorted(signatures)), (spaces, meets, joins, distances)


def tariffs(n):
    result = []
    for increasing in combinations_with_replacement(range(3), n):
        values = [0]
        for increment in reversed(increasing):
            values.append(values[-1] + increment)
        result.append(tuple(values))
    return tuple(result)


def validate_tariff(values, n):
    require(len(values) == n + 1 and all(type(v) is int and v >= 0 for v in values),
            'nonnegative integer tariff table')
    steps = tuple(values[i + 1] - values[i] for i in range(n))
    require(all(step >= 0 for step in steps), 'nondecreasing tariff')
    require(all(steps[i] >= steps[i + 1] for i in range(n - 1)), 'concave tariff')


def price(point, tables):
    return sum(tables[i][point[i]] for i in range(3))


def audit_prices(n, signatures):
    tables = tariffs(n)
    for table in tables:
        validate_tariff(table, n)
    checks = 0
    digest = hashlib.sha256()
    for family in product(tables, repeat=3):
        for candidates, attainable in signatures:
            predicted = min(price(point, family) for point in candidates)
            exhaustive = min(price(point, family) for point in attainable)
            require(predicted == exhaustive, 'four-frame optimum differs from exhaustive search')
            digest.update(f'{exhaustive},'.encode('ascii'))
            checks += 1
    return {'tariffs_per_contact': len(tables), 'independent_tariff_triples': len(tables) ** 3,
            'exact_optimum_comparisons': checks, 'optimum_transcript_sha256': digest.hexdigest()}


def audit_intervals(data):
    spaces, meets, joins, distances = data
    intervals = triples = comparisons = 0
    for low, low_mask in enumerate(spaces):
        for high, high_mask in enumerate(spaces):
            if low_mask & high_mask != low_mask:
                continue
            allowed = tuple(i for i, mask in enumerate(spaces)
                            if low_mask & mask == low_mask and mask & high_mask == mask)
            for a, b, c in combinations_with_replacement(allowed, 3):
                m = median(a, b, c, meets, joins)
                require(m in allowed, 'median left mandatory-subspace/cap interval')
                radii = branches(a, b, c, distances)
                require(tuple(distances[m][v] for v in (a, b, c)) == radii, 'interval radii')
                for x in allowed:
                    domination(tuple(distances[x][v] for v in (a, b, c)), radii)
                    comparisons += 1
                triples += 1
            intervals += 1
    return {'intervals': intervals, 'contact_triples': triples, 'frame_comparisons': comparisons}


def controls():
    rejected = []
    for label, table in [('decreasing', (0, 2, 1)), ('convex', (0, 1, 4)),
                         ('negative', (0, -1, 0)), ('wrong_length', (0, 1))]:
        try:
            validate_tariff(table, 2)
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError('invalid tariff accepted: ' + label)
    # Three different lines in F2^2: both terminals and a median can be essential.
    spaces, meets, joins, distances = geometry(2, 2)
    a, b, c = (spaces.index(mask) for mask in (3, 5, 9))
    m = median(a, b, c, meets, joins)
    points = tuple(tuple(distances[x][v] for v in (a, b, c)) for x in (a, b, c, m))
    mild = ((0, 3, 5),) * 3
    strong = ((0, 1, 1),) * 3
    require(price(points[3], mild) < min(price(p, mild) for p in points[:3]), 'median is essential')
    require(min(price(p, strong) for p in points[:3]) < price(points[3], strong), 'terminal is essential')
    weighted = ((0, 3, 6), (0, 1, 2), (0, 1, 2))
    weighted_prices = tuple(price(p, weighted) for p in points)
    require(weighted_prices == (4, 8, 8, 5), 'a specified terminal can be uniquely optimal')
    # Fixed-dimensional/Lagrangian frames exclude the zero median in this same fixture.
    require(all(spaces[m].bit_count() != spaces[v].bit_count() for v in (a, b, c)),
            'fixed-dimension restriction must not be silently imposed')
    # A concrete convex price is cheaper strictly between a median and a terminal.
    spaces4, meets4, joins4, distances4 = geometry(2, 4)
    contacts = tuple(spaces4.index(sum(1 << v for v in values)) for values in
                     ((0, 1, 2, 3), (0, 4, 8, 12), (0, 5, 10, 15)))
    middle = median(*contacts, meets4, joins4)
    convex = ((0, 5, 20, 45, 80), (0, 1, 4, 9, 16), (0, 1, 4, 9, 16))
    candidate_price = min(price(tuple(distances4[x][v] for v in contacts), convex)
                          for x in (*contacts, middle))
    witness = spaces4.index(3)
    witness_price = price(tuple(distances4[witness][v] for v in contacts), convex)
    require((witness_price, candidate_price) == (23, 28), 'convex counterexample')
    return {'rejected_tariffs': rejected, 'essential_median': 9, 'best_terminal_mild': 10,
            'essential_terminal': 2, 'median_strong': 3,
            'weighted_terminal_prices': list(weighted_prices),
            'convex_counterexample': {'witness_price': witness_price, 'four_candidate_price': candidate_price},
            'fixed_dimension_counterexample': 'three lines of F2^2 have no median within the lines'}


def result():
    reports = []
    interval_report = None
    for q, n in ((2, 2), (2, 3), (2, 4), (3, 2), (3, 3)):
        report, signatures, data = collect_domain(q, n)
        report.update(audit_prices(n, signatures))
        reports.append(report)
        if (q, n) == (2, 3):
            interval_report = audit_intervals(data)
    return {'schema_version': 1, 'claim_type': 'scoped proof with finite corroboration',
            'domains': reports, 'binary_dimension_three_intervals': interval_report,
            'controls': controls(), 'source_sha256': {
                name: hashlib.sha256(read_package_file(name)).hexdigest() for name in SOURCE_FILES}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true', help='emit a generated source-bound receipt to stdout')
    args = parser.parse_args()
    actual = result()
    if args.emit:
        print(json.dumps(actual, indent=2, sort_keys=True))
        return
    expected = json.loads(read_package_file('RESULT.json'))
    require(actual == expected, 'generated result or source hashes differ from RESULT.json')
    print('PASS_THREE_CONTACT_PRICING ' + json.dumps({
        'contact_triples': sum(d['unordered_contact_triples'] for d in actual['domains']),
        'frame_comparisons': sum(d['all_frame_comparisons'] for d in actual['domains']),
        'exact_optimum_comparisons': sum(d['exact_optimum_comparisons'] for d in actual['domains'])},
        sort_keys=True))


if __name__ == '__main__':
    main()
