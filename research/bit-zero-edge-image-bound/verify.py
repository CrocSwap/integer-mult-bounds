#!/usr/bin/env python3
"""Exact finite corroboration of the written all-width zero-edge proof.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
Standard library only; no Git, predecessor-code imports or network required.
Finite checks do not prove the all-width theorem by enumeration.
"""

import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent


class VerificationError(ValueError):
    """A proof-relevant fixture or replay obligation failed."""


def need(condition, message):
    if not condition:
        raise VerificationError(message)


def rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            lead = value.bit_length() - 1
            if lead in pivots:
                value ^= pivots[lead]
            else:
                pivots[lead] = value
                break
    return len(pivots)


def span(vectors):
    result = {0}
    for value in vectors:
        result |= {entry ^ value for entry in result}
    return result


def matrix(x, y, width):
    """Row-major bit packing, including the diagonal."""
    return sum(y << (width * row) for row in range(width) if x >> row & 1)


def diagonal_mask(width):
    return sum(1 << (row * width + row) for row in range(width))


def off_matrix(value, width):
    return value & ~diagonal_mask(width)


def pattern(x, y, width):
    return off_matrix(matrix(x, y, width), width)


def catalogue(width):
    """All binary rank-one idempotents, by their literal off-diagonal matrix."""
    result = {}
    for x in range(1, 1 << width):
        for y in range(1, 1 << width):
            if (x & y).bit_count() % 2:
                result.setdefault(pattern(x, y, width), []).append((x, y))
    return result


def source_integrity(directory):
    origins = json.loads((directory / 'ORIGINS.json').read_text())
    need(len(origins['files']) == 1, 'source inventory count')
    rows = []
    for entry in origins['files']:
        raw = (directory / entry['path']).read_bytes()
        sha256 = hashlib.sha256(raw).hexdigest()
        git_blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(sha256 == entry['sha256'], 'source SHA256 mismatch')
        need(git_blob == entry['git_blob'], 'source Git-blob mismatch')
        rows.append({'path': entry['path'], 'sha256': sha256, 'bytes': len(raw)})
    return rows


def check_fibers(catalogues):
    result = []
    for width, by_pattern in catalogues.items():
        total = sum(map(len, by_pattern.values()))
        need(total == ((1 << width) - 1) * (1 << (width - 1)), 'idempotent census')
        need(set(by_pattern.get(0, [])) == {(1 << i, 1 << i) for i in range(width)},
             'zero-pattern coordinate fiber')
        edges = 0
        for value, lifts in by_pattern.items():
            if value == 0:
                continue
            if value.bit_count() == 1:
                edges += 1
                position = value.bit_length() - 1
                a, b = divmod(position, width)
                need(a != b, 'edge is off diagonal')
                expected = {(1 << a, (1 << a) | (1 << b)),
                            ((1 << a) | (1 << b), 1 << b)}
                need(set(lifts) == expected, 'edge fiber has its exact two lifts')
            else:
                need(len(lifts) == 1, 'nonedge fiber is unique')
        need(edges == width * (width - 1), 'complete directed-edge count')
        result.append({'width': width, 'idempotents': total,
                       'realized_nonzero_patterns': len(by_pattern) - 1,
                       'edge_patterns': edges})
    return result


def check_fano():
    checked = 0
    for subset in itertools.combinations(range(1, 8), 5):
        triangles = [set(triple) for triple in itertools.combinations(subset, 3)
                     if triple[0] ^ triple[1] ^ triple[2] == 0]
        need(len(triangles) == 2, 'five-point set has two zero-sum triples')
        need(len(triangles[0] & triangles[1]) == 1, 'triple intersection is one point')
        need(triangles[0] | triangles[1] == set(subset), 'triple union is the five points')
        a, b = sorted(set(range(1, 8)) - set(subset))
        need(triangles[0] & triangles[1] == {a ^ b}, 'constructive Fano center')
        checked += 1
    need(checked == 21, 'all five-point subsets checked')
    cap = (1, 2, 4, 7)
    need(all(a ^ b ^ c != 0 for a, b, c in itertools.combinations(cap, 3)),
         'four-point cap has no zero-sum triple')
    return {'five_point_subsets': checked, 'four_point_cap': list(cap)}


def check_case(case, catalogues):
    width = case['width']
    basis = case['pattern_basis']
    need(1 <= width <= 7, 'fixture width in finite replay domain')
    need(all(isinstance(p, int) and 0 < p < (1 << (width * width)) for p in basis),
         'pattern-basis range')
    need(all(off_matrix(p, width) == p for p in basis), 'pattern basis is zero diagonal')
    need(rank(basis) == case['pattern_dimension'], 'declared pattern dimension')
    patterns = span(basis)
    need(len(patterns) == 1 << case['pattern_dimension'], 'pattern-space size')
    given = []
    for raw in case['pool']:
        need(len(raw) == 2, 'projector factor pair')
        x, y = raw
        need(0 < x < (1 << width) and 0 < y < (1 << width), 'projector factor range')
        need((x & y).bit_count() % 2 == 1, 'projector is idempotent')
        value = pattern(x, y, width)
        need(value != 0, 'projector is noncoordinate')
        need(value in patterns, 'projector pattern belongs to P')
        given.append((x, y))
    need(len(given) == len(set(given)), 'pool has no duplicates')
    complete = {lift for value in patterns - {0}
                for lift in catalogues[width].get(value, [])}
    need(set(given) == complete, 'pool is complete')
    image_dimension = rank(x for x, _ in complete)
    covector_dimension = rank(y for _, y in complete)
    need(image_dimension == case['joint_image_dimension'], 'declared joint-image dimension')
    need(image_dimension <= case.get('joint_image_bound', image_dimension),
         'claimed joint-image bound')
    edges = sum(value.bit_count() == 1 for value in patterns)
    need(edges == case['edge_count'], 'declared edge count')
    return {'width': width, 'pattern_dimension': case['pattern_dimension'],
            'edge_count': edges, 'pool_size': len(complete),
            'joint_image_dimension': image_dimension, 'covector_dimension': covector_dimension}


def require_noedge_theorem_scope(case):
    need(case['pattern_dimension'] <= 3, 'no-edge theorem pattern dimension at most three')
    need(case['edge_count'] == 0, 'no-edge theorem excludes matrix units')


def check_dependency_configuration(pairs, width):
    need(len(pairs) == 5, 'dependency configuration size')
    need(all(x and y for x, y in pairs), 'dependency factors are nonzero')
    need(rank(x for x, _ in pairs) == 5, 'dependency images are independent')
    for indices in ((0, 1, 2), (0, 3, 4)):
        value = 0
        for index in indices:
            value ^= matrix(*pairs[index], width)
        need(off_matrix(value, width) == 0, 'dependency sum is diagonal')
    x, y = pairs[0]
    need(x == y and x.bit_count() == 1, 'shared projector is coordinate')


def expect_rejection(label, action, reason, observed):
    try:
        action()
    except VerificationError as error:
        need(reason in str(error), label + ': rejected for the wrong reason: ' + str(error))
        observed.append({'control': label, 'rejection': str(error)})
    else:
        raise VerificationError(label + ': invalid input was accepted')


def check_controls(cases, catalogues):
    observed = []
    sharp = cases['zero_edge_sharp']
    forged = copy.deepcopy(sharp)
    forged['joint_image_bound'] = 3
    expect_rejection('false no-edge cap three', lambda: check_case(forged, catalogues),
                     'claimed joint-image bound', observed)
    omitted = copy.deepcopy(sharp)
    omitted['pool'].pop()
    expect_rejection('incomplete seven-projector pool', lambda: check_case(omitted, catalogues),
                     'pool is complete', observed)
    nonidempotent = copy.deepcopy(sharp)
    nonidempotent['pool'][0][0] ^= 1
    expect_rejection('nonidempotent factor mutation', lambda: check_case(nonidempotent, catalogues),
                     'projector is idempotent', observed)
    coordinate = copy.deepcopy(sharp)
    coordinate['pool'].append([1, 1])
    expect_rejection('coordinate-call admission', lambda: check_case(coordinate, catalogues),
                     'projector is noncoordinate', observed)
    expect_rejection('two-edge dimension-five scope witness',
                     lambda: require_noedge_theorem_scope(cases['two_edge_scope_control']),
                     'excludes matrix units', observed)
    expect_rejection('rank-four parity-code scope witness',
                     lambda: require_noedge_theorem_scope(cases['rank_four_scope_control']),
                     'dimension at most three', observed)
    coordinate_five = [(1 << i, 1 << i) for i in range(5)]
    check_dependency_configuration(coordinate_five, 6)
    # Labels u1,u2,u1+u2,u3,u1+u3 give both required sums E_00.
    dependent = [(1 | u, 1) for u in (6, 10, 12, 18, 20)]
    for indices in ((0, 1, 2), (0, 3, 4)):
        value = 0
        for index in indices:
            value ^= matrix(*dependent[index], 5)
        need(value == 1, 'dependent control really has both diagonal sums E_00')
    need(rank(x for x, _ in dependent) == 4, 'dependent control has image rank four')
    need(pattern(*dependent[0], 5) != 0, 'dependent control shared projector is noncoordinate')
    expect_rejection('dependent images invalidate intersection lemma',
                     lambda: check_dependency_configuration(dependent, 5),
                     'images are independent', observed)
    nondiagonal = coordinate_five.copy()
    nondiagonal[0] = (1, 33)
    expect_rejection('nondiagonal sums invalidate intersection lemma',
                     lambda: check_dependency_configuration(nondiagonal, 6),
                     'sum is diagonal', observed)
    # Run the actual hash checker on changed retained bytes outside this package.
    with tempfile.TemporaryDirectory(prefix='zero-edge-source-control-') as temporary:
        destination = Path(temporary)
        (destination / 'ORIGINS.json').write_bytes((HERE / 'ORIGINS.json').read_bytes())
        for entry in json.loads((HERE / 'ORIGINS.json').read_text())['files']:
            target = destination / entry['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((HERE / entry['path']).read_bytes() + b'\ncorrupted\n')
        expect_rejection('retained-source byte corruption', lambda: source_integrity(destination),
                         'source SHA256 mismatch', observed)
    return observed


EXPECTED_CENSUS = {
    3: {'generated_spaces': 202, 'zero_edge_spaces': 112,
        'image_dimension/pool_size': {'1/4': 1, '2/3': 53, '3/3': 48, '3/4': 7, '3/5': 3}},
    4: {'generated_spaces': 104657, 'zero_edge_spaces': 98997,
        'image_dimension/pool_size': {'1/4': 52, '2/3': 18012, '2/4': 1450,
                                    '2/5': 100, '3/3': 72676, '3/4': 5468,
                                    '3/5': 168, '4/4': 987, '4/5': 84}}
}


def check_census(width, by_pattern):
    """All 3-spaces generated by three realized nonedge patterns at this width.

    This does not enumerate arbitrary subspaces of the full off-diagonal
    ambient space. If the realized patterns span less than three dimensions,
    fiber uniqueness already bounds the image dimension by three.
    """
    lifts = {p: values[0] for p, values in by_pattern.items() if p.bit_count() > 1}
    need(all(len(by_pattern[p]) == 1 for p in lifts), 'census unique nonedge lifts')
    seen = set()
    histogram = {}
    for a, b, c in itertools.combinations(sorted(lifts), 3):
        if c == a ^ b:
            continue
        nonzero = tuple(sorted((a, b, c, a ^ b, a ^ c, b ^ c, a ^ b ^ c)))
        if nonzero in seen:
            continue
        seen.add(nonzero)
        if any(p.bit_count() == 1 for p in nonzero):
            continue
        pool = [lifts[p] for p in nonzero if p in lifts]
        dimension = rank(x for x, _ in pool)
        need(dimension <= 4, 'finite no-edge image bound')
        need(rank(y for _, y in pool) <= 4, 'finite transposed no-edge image bound')
        key = str(dimension) + '/' + str(len(pool))
        histogram[key] = histogram.get(key, 0) + 1
    result = {'generated_spaces': len(seen), 'zero_edge_spaces': sum(histogram.values()),
              'image_dimension/pool_size': dict(sorted(histogram.items()))}
    need(result == EXPECTED_CENSUS[width], 'frozen exact census at width ' + str(width))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json-output', type=Path,
                        help='write the completed deterministic report after every check passes')
    parser.add_argument('--integrity-only', action='store_true',
                        help='check retained provenance bytes only; not a mathematical replay')
    args = parser.parse_args()
    sources = source_integrity(HERE)
    if args.integrity_only:
        print('PASS_ZERO_EDGE_SOURCE_BYTES ' + json.dumps(sources, sort_keys=True))
        return
    catalogues = {width: catalogue(width) for width in range(1, 8)}
    cases = json.loads((HERE / 'WITNESSES.json').read_text())['cases']
    witnesses = {name: check_case(case, catalogues) for name, case in cases.items()}
    require_noedge_theorem_scope(cases['zero_edge_sharp'])
    report = {
        'claim': 'finite corroboration of written all-width no-edge image bound four; universal rank-three bound six',
        'all_width_proof': 'PROOF.md; not established by finite replay',
        'new_kappa': False,
        'sources': sources,
        'fibers': check_fibers(catalogues),
        'fano': check_fano(),
        'witnesses': witnesses,
        'census': {str(width): check_census(width, catalogues[width]) for width in (3, 4)},
        'negative_controls': check_controls(cases, catalogues),
    }
    need(json.loads((HERE / 'RESULT.json').read_text()) == report,
         'committed deterministic report matches the completed replay')
    payload = json.dumps(report, sort_keys=True, indent=2) + '\n'
    if args.json_output:
        args.json_output.write_text(payload)
    print('PASS_ZERO_EDGE_IMAGE_BOUND ' + json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (VerificationError, OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise SystemExit('FAIL_ZERO_EDGE_IMAGE_BOUND: ' + str(error)) from error
