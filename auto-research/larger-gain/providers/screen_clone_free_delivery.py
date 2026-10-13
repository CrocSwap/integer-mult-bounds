#!/usr/bin/env python3
"""Check necessary geometry for eliminating ordinary packet clones.

Reconstructs the exact SAME504 prefix through packet-sum formation, then
transforms all ordinary output contributions into the already chosen selected
output basis. A direct read is impossible if the packet's current frame is not
inside both output hyperplanes required by the later basis restoration.
Prepared with OpenAI Codex assistance. Apache-2.0; source notices retained.
"""
import argparse
from collections import defaultdict
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--constructor', type=Path, required=True)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    assert __debug__ and not args.out.exists()
    source = args.constructor.read_text()
    marker = 'consumers=defaultdict(list)\n'
    assert source.count(marker) == 1
    prefix = source.split(marker)[0]
    scope = {'__name__': 'same504_prefix'}
    old_argv = sys.argv
    try:
        sys.argv = [str(args.constructor), str(args.input), str(args.out)]
        exec(compile(prefix, str(args.constructor), 'exec'), scope)
    finally:
        sys.argv = old_argv
    pairs, packets = scope['pairs'], scope['Ms']
    current, ports = scope['cur'], scope['P']
    basis, hyper, inside = scope['basis'], scope['hyper'], scope['inside']
    rows = defaultdict(lambda: defaultdict(Q))
    for pair in pairs:
        if pair['selected']:
            continue
        for row_index, target in enumerate(pair['targets']):
            for col_index, key in enumerate(pair['keys']):
                register, alpha = packets[key]
                rows[target][register] += -Q(pair['matrix'][row_index][col_index], 2) * alpha
    upper = {}
    for pair in pairs:
        if not pair['selected']:
            continue
        target, partner = pair['targets']
        z = -Q(2 * pair['matrix'][1][0], pair['matrix'][0][0])
        left, right = rows[target].copy(), rows[partner].copy()
        rows[target] = {r: left.get(r, Q(0)) / 2 - right.get(r, Q(0)) / z
                        for r in set(left) | set(right)}
        rows[partner] = {r: left.get(r, Q(0)) / 2 + right.get(r, Q(0)) / z
                         for r in set(left) | set(right)}
        cap = basis(tuple(x for x in range(1, 512)
                          if not (x & ports[target]).bit_count() % 2
                          and not (x & ports[partner]).bit_count() % 2))
        upper[target] = upper[partner] = cap
    checks, consumers = [], defaultdict(set)
    for target, row in sorted(rows.items()):
        for register, coefficient in sorted(row.items()):
            if not coefficient:
                continue
            consumers[register].add(target)
            joined = basis(current[scope['v'] + target] + current[register])
            checks.append(dict(target=target - 8, packet_register=register - 16,
                               coefficient=str(coefficient), source_frame=current[register],
                               target_frame=current[scope['v'] + target],
                               minimum_join=joined, target_upper=upper[target],
                               individually_compatible=inside(joined, upper[target])))
    failures = [check for check in checks if not check['individually_compatible']]
    # A full tetrahedron Walsh basis has dense output columns. Every such
    # intermediate coordinate must therefore lie in all four final target
    # hyperplanes, regardless of how its own initial loads are rescheduled.
    physical = defaultdict(lambda: defaultdict(Q))
    for pair in pairs:
        if pair['selected']:
            continue
        for row_index, target in enumerate(pair['targets']):
            for col_index, key in enumerate(pair['keys']):
                register, alpha = packets[key]
                physical[target][register] += -Q(pair['matrix'][row_index][col_index], 2) * alpha
    walsh = [[1, 1, 1, 1], [1, -1, 1, -1], [1, 1, -1, -1], [1, -1, -1, 1]]
    walsh_checks = []
    for block, tetrahedra in sorted(scope['tetrads'].items()):
        for tetrahedron in tetrahedra:
            cap = basis(tuple(x for x in range(1, 512)
                              if all(not (x & ports[target]).bit_count() % 2 for target in tetrahedron)))
            used_packets = set().union(*(set(physical[target]) for target in tetrahedron))
            for coordinate, row in enumerate(walsh):
                for register in sorted(used_packets):
                    coefficient = sum(Q(sign, 4) * physical[target].get(register, Q(0))
                                      for sign, target in zip(row, tetrahedron))
                    if coefficient:
                        walsh_checks.append(dict(tetrahedron=[target - 8 for target in tetrahedron],
                                                 coordinate=coordinate, packet_register=register - 16,
                                                 coefficient=str(coefficient), source_frame=current[register],
                                                 required_upper=cap,
                                                 compatible=inside(current[register], cap)))
    record = dict(status='PASS_EXACT_NECESSARY_CLONE_FREE_DELIVERY_SCREEN',
                  source_constructor_sha256=hashlib.sha256(source.encode()).hexdigest(),
                  prefix_helper_count=len(current) - 240,
                  ordinary_packet_sums=len(packets),
                  direct_reads=len(checks), incompatible_reads=len(failures),
                  affected_packets=len({check['packet_register'] for check in failures}),
                  would_remove_helpers=112,
                  checks=checks,
                  walsh4=dict(direct_reads=len(walsh_checks),
                              incompatible_reads=sum(not check['compatible'] for check in walsh_checks),
                              required_upper_ranks=sorted({len(check['required_upper']) for check in walsh_checks}),
                              checks=walsh_checks,
                              scope='Full dense Walsh4 output coordinates with unchanged ordinary packet sums. '
                                    'A failing source-frame inclusion is independent of initial target levels '
                                    'and scheduling. Packet refactorization or sparse mixed output bases remain open.'),
                  scope='This tests clone-free direct ordinary reads before selected output-basis '
                        'restoration, with the original exact factory/packet sums and selected basis. '
                        'Each failing read violates a necessary final-frame inclusion independently '
                        'of read order. Other output bases, factory factorizations and partial reuse '
                        'are not ruled out.')
    (args.out / 'SCREEN.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({key: value for key, value in record.items() if key not in ('checks', 'walsh4')}, indent=2))
    print(json.dumps({key: value for key, value in record['walsh4'].items() if key != 'checks'}, indent=2))


if __name__ == '__main__':
    main()
