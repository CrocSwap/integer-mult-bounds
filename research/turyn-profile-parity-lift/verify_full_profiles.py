#!/usr/bin/env python3
"""Independently enumerate all actual ports and verify full-profile upper fits.

No geometry producer is imported. This uses the checker's binary code span,
canonical sign enumeration, exact integers, and a complete fiber partition.
"""
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('independent_parity_checker', HERE/'verify.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def enumerate_ports(code):
    ports = set()
    for word in sorted(code):
        if word.bit_count() == 8:
            support = [i for i in range(24) if word >> i & 1]
            blocks = [[i for i in support if i//8 == k] for k in range(3)]
            if all(blocks):
                # First nonzero coordinate in each block is positive. Of
                # the five remaining signs, exactly an even number are minus.
                free = [i for block in blocks for i in block[1:]]
                for mask in range(1 << len(free)):
                    if mask.bit_count() % 2:
                        continue
                    row = [2 if i in support else 0 for i in range(24)]
                    for j, i in enumerate(free):
                        if mask >> j & 1:
                            row[i] = -2
                    ports.add(tuple(row))
        for exceptional in range(24):
            row = [1-2*((word >> i) & 1) for i in range(24)]
            row[exceptional] *= -3
            for start in (0, 8, 16):
                if row[start] < 0:
                    row[start:start+8] = [-x for x in row[start:start+8]]
            ports.add(tuple(row))
    ordered = sorted(ports)
    V.require(len(ordered) == 23040, 'Complete canonical port count')
    digest = hashlib.sha256(bytes(x % 256 for row in ordered for x in row)).hexdigest()
    reference = json.loads((V.ROOT/'research/leech-lattice/evidence/TURYN-GEOMETRY.json').read_text())
    V.require(digest == reference['integer_representatives_sha256'], 'Independent complete coordinate-array digest')
    return ordered, digest


def upper_bound(ports, certificate, code):
    V.require(certificate['selected_low_block'] == '(profile+1) mod 3', 'Declared low-block convention')
    roots = certificate['roots']
    labels = certificate['nine_bit_labels']
    V.require(len(roots) == len({tuple(r) for r in roots}) == 120, 'All 120 distinct low roots')
    V.require(roots == sorted(roots), 'Canonical root order')
    V.require(all(len(r) == 8 and all(type(x) is int for x in r) and
                  sum(x*x for x in r) == 8 and next(x for x in r if x) > 0 for r in roots),
              'Canonical exact norm-eight roots')
    V.require(len(labels) == 120 and all(type(x) is int and 0 <= x < 512 for x in labels),
              'Root labels have exactly nine binary coordinates')
    V.require(all(x.bit_count() % 2 == 1 for x in labels), 'Odd root-label diagonals')
    V.require(V.binary_rank(labels) == 9, 'Full-profile upper labels rank nine')
    root_dots = Counter()
    for i, a in enumerate(roots):
        for j, b in enumerate(roots[:i]):
            dot = sum(x*y for x, y in zip(a, b))
            V.require(dot in (-4, 0, 4), 'Distinct low-root pairing spectrum')
            root_dots[dot] += 1
            V.require((labels[i]&labels[j]).bit_count() % 2 == (1+dot//4) % 2,
                      'Every root-pair binary Gram entry')
    by_root = {tuple(root): label for root, label in zip(roots, labels)}
    fibers = [defaultdict(list) for _ in range(3)]
    for row in ports:
        norms = [sum(x*x for x in row[8*k:8*k+8]) for k in range(3)]
        V.require(sorted(norms) == [8, 8, 16], 'Complete-array profile norms')
        profile = norms.index(16)
        V.actual_port(row, profile, code)
        low = (profile+1) % 3
        root = tuple(row[8*low:8*low+8])
        V.require(root in by_root, 'Every actual port has a certified low-root label')
        fibers[profile][root].append(row)
    reports = []
    for profile in range(3):
        V.require(set(fibers[profile]) == set(by_root), 'Every low root is used in each profile')
        V.require(Counter(map(len, fibers[profile].values())) == {64: 120}, 'Complete 120-by-64 fiber partition')
        checks = 0
        for fiber in fibers[profile].values():
            for a, b in combinations(fiber, 2):
                V.require(not V.active(a, b), 'All distinct same-root ports are inactive')
                checks += 1
        reports.append({'profile': profile, 'ports': 7680, 'fibers': 120,
                        'ports_per_fiber': 64, 'same_fiber_inactive_pairs_checked': checks,
                        'all_unordered_port_pairs_covered': 7680*7679//2,
                        'explicit_label_rank': 9})
    return {'profiles': reports, 'root_pair_dots': {str(k): v for k, v in sorted(root_dots.items())},
            'distinct_root_pairs_checked': 120*119//2}


def bind_source_classes(ports, lower, control):
    groups = [defaultdict(list) for _ in range(3)]
    for i, row in enumerate(ports):
        profile = next(k for k in range(3) if sum(x*x for x in row[8*k:8*k+8]) == 16)
        key = tuple(x for k in range(3) if k != profile for x in row[8*k:8*k+8])
        groups[profile][key].append(i)
    classes = [groups[profile][key] for profile in range(3) for key in sorted(groups[profile])]
    V.require(len(classes) == 2880 and all(len(c) == 8 for c in classes), 'Independent full glue-class map')
    for record in lower['profiles']:
        V.require([list(ports[i]) for i in record['selected_ports']] == record['coordinates'],
                  'All twenty lower-certificate source indices bind exact coordinates')
        V.require(all(port in classes[source_class] for port, source_class in
                      zip(record['selected_ports'], record['classes'])),
                  'Each chosen port belongs to its declared quotient source class')
    V.require(list(ports[control['replacement_port']]) == control['replacement_coordinates'],
              'Same-class control source index binds exact replacement coordinates')
    V.require(control['replacement_port'] in classes[control['source_class']] and
              control['original_port'] in classes[control['source_class']],
              'Original and replacement port share the exact declared source class')
    return {'complete_classes': 2880, 'ports_per_class': 8, 'lower_witness_bindings': 60,
            'same_class_control_bound': True}


def run():
    V.source_check()
    code = V.turyn_code()
    ports, digest = enumerate_ports(code)
    certificate = V.load('FULL-PROFILE-UPPER.json')
    V.require(certificate['all_ports_sha256'] == digest, 'Full-profile source-array receipt')
    report = upper_bound(ports, certificate, code)
    # Match the lower certificates to literal entries of this independently
    # regenerated array. This additionally checks all recorded source IDs.
    lower = V.load('CERTIFICATE.json')
    bindings = bind_source_classes(ports, lower, V.load('SAME-CLASS-CONTROL.json'))
    V.run()
    return {'status': 'PASS_FULL_TURYN_PROFILES_BLOCK_RANK_9',
            'all_ports_sha256': digest, 'canonical_ports': len(ports), 'source_bindings': bindings, **report,
            'scope': 'Each individual complete 7680-port profile has minimum asymmetric d-block fitting rank exactly 9d over every characteristic-two field; no global additive lower bound.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    report = run()
    if args.write:
        args.write.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    else:
        V.require(report == V.load('FULL-PROFILE-EXPECTED.json'), 'Exact complete-profile receipt')
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
