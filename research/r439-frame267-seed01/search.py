"""Exact nonnegative row-subtraction DAG for one fixed integer transfer.

Ross Richardson, substantial OpenAI Codex assistance; Apache-2.0.
No search across frames, wires, integer transfers or general F2 circuits.
"""
import argparse
from collections import Counter
from functools import cache
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = ROOT / 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
REGS = [222, 351, 353, 369, 379, 486]
IDENTITY = tuple(tuple(int(i == j) for j in range(6)) for i in range(6))


def transfer(ops):
    rows = list(IDENTITY)
    for dst, src in ops:
        rows[dst] = tuple(x + y for x, y in zip(rows[dst], rows[src]))
    return tuple(rows)


def nominate(original):
    target = transfer(original)
    distances, choices = {}, {}
    edges = 0
    states = 0
    infinity = 999  # Strictly above the original 21-step witness.

    @cache
    def distance(rows):
        nonlocal edges, states
        states += 1
        if states > 1_000_000:
            raise ValueError('state budget exceeded; no optimum established')
        if rows == IDENTITY:
            distances[rows] = 0
            return 0
        best = infinity
        for dst in range(6):
            for src in range(6):
                if dst == src or rows[dst][dst] - rows[src][dst] < 1:
                    continue
                difference = tuple(x - y for x, y in zip(rows[dst], rows[src]))
                if min(difference) < 0:
                    continue
                previous = list(rows)
                previous[dst] = difference
                previous = tuple(previous)
                edges += 1
                length = 1 + distance(previous)
                if length < best:
                    best = length
                    choices[rows] = (dst, src, previous)
        distances[rows] = best
        return best

    minimum = distance(target)
    if minimum >= infinity:
        raise ValueError('no positive-addition factorization found')
    backward, current = [], target
    while current != IDENTITY:
        dst, src, current = choices[current]
        backward.append([dst, src])
    return {'replacement': list(reversed(backward)), 'minimum': minimum,
            'states': len(distances), 'edges': edges,
            'distance_histogram': {str(k): v for k, v in sorted(Counter(distances.values()).items())},
            'dead_end_distance': infinity}


def original_ops():
    word = json.loads(gzip.decompress(WORD.read_bytes()))
    segment = word['A'][615:636]
    if len(segment) != 21 or any(f != 267 or len(ss) != 1 for f, _, ss in segment):
        raise ValueError('source slice changed')
    return [[REGS.index(dst), REGS.index(ss[0])] for _, dst, ss in segment]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-witness', action='store_true')
    args = parser.parse_args()
    old = original_ops()
    result = {'phase': 'A', 'start': 615, 'stop': 636, 'frame': 267, 'quad': 1,
              'registers': REGS, 'assignment_seed': 1, 'original': old, **nominate(old)}
    path = HERE / 'WITNESS.json'
    if args.write_witness:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    elif result != json.loads(path.read_text()):
        raise ValueError('search witness mismatch')
    print(f"PASS_FRAME267_SEARCH states={result['states']} edges={result['edges']} minimum={result['minimum']}")


if __name__ == '__main__':
    main()
