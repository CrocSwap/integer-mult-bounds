#!/usr/bin/env python3
"""Construct full-mask fits for separated-port excess payloads. Standard library."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CERT = 'research/paired-plane-block-rank/predecessor/PR2484-CERTIFICATE.json'
MATCH = 'research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json'
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def inputs():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    raw = {}
    for entry in manifest['files']:
        if entry['usage'] != 'input':
            continue
        path = ROOT / entry['path']
        need(path.stat().st_size <= 16 * 1024 * 1024, 'input size')
        data = path.read_bytes()
        need(hashlib.sha256(data).hexdigest() == entry['sha256'], 'input hash')
        raw[entry['path']] = data
    source = json.loads(raw[CERT])
    matching = json.loads(raw[MATCH])['matching']
    with tarfile.open(fileobj=io.BytesIO(raw[ARCHIVE]), mode='r:gz') as archive:
        member = archive.getmember(MEMBER)
        need(member.isfile() and member.size <= 16 * 1024 * 1024, 'member size')
        with archive.extractfile(member) as stream:
            data = json.load(stream)
    labels = [row['q'] for row in data['recipes']]
    need(len(labels) == 112 and len(matching) == 56, 'source dimensions')
    owners = {port: plane for plane, pair in enumerate(matching) for port in pair}
    allowed = [[i != j and all((labels[a] & labels[b]).bit_count() % 2 == 0
               for a in matching[owners[i]] for b in matching[owners[j]])
               for j in range(112)] for i in range(112)]
    qports = [p for plane in source['clique22'] for p in matching[plane]]
    return source['rank49_supports'], qports, allowed


def construct(d, excess, supports, qports):
    need(type(d) is int and 1 <= d and d.bit_length() <= 4096, 'base width')
    need(len(excess) == 44 and all(type(e) is int and 0 <= e and
         e.bit_length() <= 4096 for e in excess), 'excess vector')
    dimensions = [d] * 112
    for port, value in zip(qports, excess):
        dimensions[port] += value
    capacities = [max(dimensions[p] for p in support) for support in supports]
    return dimensions, capacities


def expand(dimensions, capacities, supports):
    size = sum(dimensions)
    need(size <= 512, 'expanded size limit')
    offsets = [0]
    for width in dimensions:
        offsets.append(offsets[-1] + width)
    matrix = [[0] * size for _ in range(size)]
    groups = []
    for support, capacity in zip(supports, capacities):
        for coordinate in range(capacity):
            group = [offsets[p] + coordinate for p in support
                     if coordinate < dimensions[p]]
            need(bool(group), 'empty query')
            groups.append(group)
            for row in group:
                for column in group:
                    matrix[row][column] = 1
    return matrix, offsets, groups


def fits(matrix, dimensions, offsets, allowed):
    size = sum(dimensions)
    need(len(matrix) == size and all(len(row) == size for row in matrix), 'shape')
    for i in range(112):
        for j in range(112):
            if i != j and allowed[i][j]:
                continue
            for a in range(dimensions[i]):
                for b in range(dimensions[j]):
                    need(matrix[offsets[i]+a][offsets[j]+b] ==
                         int(i == j and a == b), 'ordered mask or identity')


def rank(matrix, prime):
    rows = [[value % prime for value in row] for row in matrix]
    height = len(rows)
    pivot = 0
    for column in range(len(rows[0])):
        candidates = [i for i in range(pivot, height) if rows[i][column]]
        if not candidates:
            continue
        index = candidates[0]
        rows[pivot], rows[index] = rows[index], rows[pivot]
        inverse = pow(rows[pivot][column], -1, prime)
        rows[pivot] = [(x * inverse) % prime for x in rows[pivot]]
        for i in range(pivot + 1, height):
            scalar = rows[i][column]
            if scalar:
                rows[i] = [(x - scalar*y) % prime
                           for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
        if pivot == height:
            break
    return pivot


def change_charts(matrix, dimensions, offsets):
    result = [row[:] for row in matrix]
    for port, width in enumerate(dimensions):
        if width < 2:
            continue
        a, b = offsets[port], offsets[port] + 1
        if port % 2:
            a, b = b, a
        result[a] = [x+y for x, y in zip(result[a], result[b])]
        for row in result:
            row[b] -= row[a]
    return result


def check_case(d, excess, supports, qports, allowed, charts=False):
    dimensions, capacities = construct(d, excess, supports, qports)
    expected = 49*d + sum(excess)
    need(sum(capacities) == expected, 'capacity formula')
    matrix, offsets, groups = expand(dimensions, capacities, supports)
    need(len(groups) == expected, 'query count')
    flattened = sorted(x for group in groups for x in group)
    need(flattened == list(range(sum(dimensions))), 'factor coordinates')
    if charts:
        matrix = change_charts(matrix, dimensions, offsets)
    fits(matrix, dimensions, offsets, allowed)
    observed = [rank(matrix, p) for p in (2, 3, 101)]
    need(observed == [expected]*3, 'literal matrix ranks')
    return {'d': d, 'excess': {str(i): e for i, e in enumerate(excess) if e},
            'size': sum(dimensions),
            'rank': expected, 'field_ranks': observed, 'charts': charts}


def rejects(operation):
    try:
        operation()
    except ValueError:
        return
    raise ValueError('negative control was accepted')


def controls(supports, qports, allowed):
    for d in (0, -1, True):
        rejects(lambda: construct(d, [1]*44, supports, qports))
    for excess in ([1]*43, [-1]+[0]*43, [True]+[0]*43):
        rejects(lambda: construct(1, excess, supports, qports))
    dims, caps = construct(1, [1]+[0]*43, supports, qports)
    matrix, offsets, groups = expand(dims, caps, supports)
    bad = [row[:] for row in matrix]
    bad[offsets[qports[0]]][offsets[qports[1]]] = 1
    rejects(lambda: fits(bad, dims, offsets, allowed))
    bad = [row[:] for row in matrix]
    bad[0][0] = 0
    rejects(lambda: fits(bad, dims, offsets, allowed))
    need(len(groups) != 49, 'unpaid extra coordinate control')
    rejects(lambda: expand([5]*112, [5]*49, supports))
    return 10


def receipt():
    supports, qports, allowed = inputs()
    cases = []
    for i in range(44):
        excess = [0]*44
        excess[i] = 1
        cases.append(check_case(1, excess, supports, qports, allowed))
    for d, excess in ((1, [1]*44), (2, [1]+[0]*43),
                      (2, [i % 3 for i in range(44)])):
        cases.append(check_case(d, excess, supports, qports, allowed))
        cases.append(check_case(d, excess, supports, qports, allowed, True))
    large = [2**(100+i)+i for i in range(44)]
    dims, caps = construct(2**200, large, supports, qports)
    need(sum(caps) == 49*2**200 + sum(large), 'large exact recipe')
    count = controls(supports, qports, allowed)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(HERE.iterdir()) if p.is_file() and
              p.name != 'RESULT.json'}
    return {'claim_type': 'scoped proof with finite corroboration',
            'cases': cases, 'matrix_cases': len(cases),
            'literal_field_rank_checks': 3*len(cases), 'controls': count,
            'large_recipe_rank': sum(caps), 'package_sha256': hashes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = receipt()
    canonical = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.emit:
        print(canonical, end='')
        return
    expected = json.loads((HERE / 'RESULT.json').read_text())
    need(canonical == json.dumps(expected, sort_keys=True, indent=2)+'\n',
         'receipt mismatch')
    print('PASS_FULL_MASK_SEPARATED_EXCESS matrices=50 field_ranks=150 controls=10')


if __name__ == '__main__':
    main()
