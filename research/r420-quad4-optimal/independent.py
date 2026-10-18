#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared for Chris Barber (@cbarber1) with OpenAI Codex assistance.
"""Independent packed-row breadth-first check of the monotone gate minimum.

No import of the constructor, matrix engine or optimal.py. Each base-4 row
encodes six entries from 0 through 3. Reverse BFS exhausts depths 0..10 before
reaching the identity at depth 11. This is not an independent human review.
"""
from pathlib import Path
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def breadth_first(target):
    n = len(target)
    width = max(x for row in target for x in row).bit_length()
    width = max(width, 1)
    mask = (1 << width) - 1
    encode = lambda row: sum(x << (width * j) for j, x in enumerate(row))
    goal = tuple(1 << (width * j) for j in range(n))
    start = tuple(encode(row) for row in target)
    front = {start}
    seen = {start}
    widths = []
    depth = 0
    while front:
        widths.append(len(front))
        if goal in front:
            return {'minimum_additions': depth, 'layer_widths': widths, 'states_through_minimum': len(seen)}
        nxt = set()
        for matrix in front:
            for d, a in enumerate(matrix):
                for s, b in enumerate(matrix):
                    if d == s:
                        continue
                    if any(((a >> (width*j)) & mask) < ((b >> (width*j)) & mask) for j in range(n)):
                        continue
                    c = a - b  # digitwise dominance above prevents borrowing
                    if ((c >> (width*d)) & mask) == 0:
                        continue
                    child = matrix[:d] + (c,) + matrix[d+1:]
                    if child not in seen:
                        seen.add(child)
                        nxt.add(child)
        front = nxt
        depth += 1
    return {'minimum_additions': None, 'layer_widths': widths, 'states_through_minimum': len(seen)}


def main():
    spec = json.loads((HERE/'CIRCUIT.json').read_text())
    relative = 'research/e8-bit-r420/data/bitE8mut-r420.json.gz'
    raw = (ROOT/relative).read_bytes()
    expected_hash = json.loads((HERE/'SOURCES.json').read_text())['files'][relative]['sha256']
    if hashlib.sha256(raw).hexdigest() != expected_hash:
        raise ValueError('source pin mismatch')
    word = json.loads(gzip.decompress(raw))
    regs = spec['registers']
    # Column-oriented integer replay, derived from the source word, not from
    # a matrix emitted by the primary checker.
    columns = []
    for j in range(6):
        values = [int(i == j) for i in range(6)]
        for f, d, sources in word['A'][690:709]:
            if f != 306 or len(sources) != 1:
                raise ValueError('unexpected source slice')
            values[regs.index(d)] += values[regs.index(sources[0])]
        columns.append(values)
    target = [list(row) for row in zip(*columns)]
    report = breadth_first(target)
    # Full Boolean truth table provides an independent concrete endpoint and
    # cleanup check for arbitrary six-register inputs, including dirty helpers.
    for bits in range(64):
        values = [(bits >> i) & 1 for i in range(6)]
        original = values[:]
        expected = [sum(target[i][j]*original[j] for j in range(6)) % 2 for i in range(6)]
        for d, s in spec['operations']:
            values[d] ^= values[s]
        if values != expected:
            raise ValueError('Boolean endpoint mismatch')
        for d, s in reversed(spec['operations']):
            values[d] ^= values[s]
        if values != original:
            raise ValueError('Boolean cleanup mismatch')
    if report['minimum_additions'] != 11:
        raise ValueError('unexpected minimum')
    report['truth_table_inputs'] = 64
    expected = json.loads((HERE/'INDEPENDENT.json').read_text())
    if report != expected:
        raise ValueError('independent receipt mismatch')
    print(json.dumps(report, sort_keys=True))
    print('PASS_INDEPENDENT_QUAD4_MINIMUM minimum=11 truth_table=64')


if __name__ == '__main__':
    main()
