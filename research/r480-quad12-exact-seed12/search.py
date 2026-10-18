"""Exact nonnegative row-subtraction DAG for one fixed integer transfer.

Adapted from Ross Richardson PR925 by Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
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
WORD = ROOT / 'research/e8-bit-p111-tuned/vendor/pr510/e8-r480-dead-totals/data/bitE8mut-r480.json.gz'
REGS = [307, 355, 415, 439, 494, 518]
IDENTITY = tuple(tuple(int(i == j) for j in range(6)) for i in range(6))


def transfer(ops):
    rows = list(IDENTITY)
    for dst, src in ops:
        rows[dst] = tuple(x + y for x, y in zip(rows[dst], rows[src]))
    return tuple(rows)


def nominate(original):
    target = transfer(original)
    distances, choices, path_counts = {}, {}, {}
    edges = 0
    states = 0
    infinity = 999  # Strictly above the original 23-step witness.

    @cache
    def distance(rows):
        nonlocal edges, states
        states += 1
        if states > 1_000_000:
            raise ValueError('state budget exceeded; no optimum established')
        if rows == IDENTITY:
            distances[rows] = 0
            path_counts[rows] = 1
            return 0
        best = infinity
        ways = 0
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
                    ways = path_counts[previous]
                elif length == best and best < infinity:
                    ways += path_counts[previous]
        distances[rows] = best
        path_counts[rows] = ways
        return best

    minimum = distance(target)
    if minimum >= infinity:
        raise ValueError('no positive-addition factorization found')
    programs = []

    def enumerate_shortest(rows, backward):
        if rows == IDENTITY:
            programs.append(list(reversed(backward)))
            return
        for dst in range(6):
            for src in range(6):
                if dst == src or rows[dst][dst] - rows[src][dst] < 1:
                    continue
                difference = tuple(x-y for x, y in zip(rows[dst], rows[src]))
                if min(difference) < 0:
                    continue
                previous = list(rows)
                previous[dst] = difference
                previous = tuple(previous)
                if distances[previous] + 1 == distances[rows]:
                    enumerate_shortest(previous, backward + [[dst, src]])

    if path_counts[target] > 100_000:
        raise ValueError('shortest-program enumeration budget exceeded')
    enumerate_shortest(target, [])
    if len(programs) != path_counts[target]:
        raise ValueError('enumeration does not match the independent DAG path count')
    backward, current = [], target
    while current != IDENTITY:
        dst, src, current = choices[current]
        backward.append([dst, src])
    return {'replacement': list(reversed(backward)), 'minimum': minimum,
            'states': len(distances), 'edges': edges,
            'shortest_programs': path_counts[target], 'programs': programs,
            'distance_histogram': {str(k): v for k, v in sorted(Counter(distances.values()).items())},
            'dead_end_distance': infinity}


def original_ops():
    word = json.loads(gzip.decompress(WORD.read_bytes()))
    segment = word['A'][849:872]
    if len(segment) != 23 or any(f != 314 or len(ss) != 1 for f, _, ss in segment):
        raise ValueError('source slice changed')
    return [[REGS.index(dst), REGS.index(ss[0])] for _, dst, ss in segment]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-witness', action='store_true')
    args = parser.parse_args()
    import runpy
    runpy.run_path(str(HERE / "common.py"))["check_sources"]()
    old = original_ops()
    result = {'phase': 'A', 'start': 849, 'stop': 872, 'frame': 314, 'quad': 12,
              'registers': REGS, 'assignment_seed': 12, 'original': old, **nominate(old)}
    census = {'format': 'r480-quad12-shortest-programs/1', 'minimum': result['minimum'],
              'programs': result.pop('programs')}
    path = HERE / 'WITNESS.json'
    census_path = HERE / 'MINIMUM-CENSUS.json'
    if args.write_witness:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
        census_path.write_text(json.dumps(census, separators=(',', ':')) + '\n')
    elif (result != json.loads(path.read_text()) or census != json.loads(census_path.read_text())):
        raise ValueError('search witness or complete census mismatch')
    print(f"PASS_R480_QUAD12_SEARCH states={result['states']} edges={result['edges']} minimum={result['minimum']} programs={result['shortest_programs']}")


if __name__ == '__main__':
    main()
