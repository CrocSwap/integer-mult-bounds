"""Exact nonnegative row-subtraction DAG for the one claimed frame272 transfer.

This adaptation: GitHub @woklerx, substantial OpenAI Codex assistance.
Adapted from Ross Richardson's PR925 research/r439-frame267-seed01/search.py;
the predecessor also credits substantial OpenAI Codex assistance. Apache-2.0.
No search across frames, wires, integer transfers or general F2 circuits.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = ROOT / 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
REGS = [242, 294, 296, 302, 316, 501]
IDENTITY = tuple(tuple(int(i == j) for j in range(6)) for i in range(6))
STATE_LIMIT = 1_000_000
PR936_WORD = ROOT / 'research/r439-five-wire-prefix/candidate.json.gz'
PR936_SHA256 = '3a11fc4675cd708316f9b0d398e0c3b73d626de0f824c5ed9b9c96279cfef091'
PR936_OPS = [[0, 2], [0, 3], [0, 1], [0, 4], [5, 3], [3, 1],
             [1, 4], [2, 1], [5, 2], [4, 0], [4, 5], [4, 2],
             [4, 3], [1, 0], [1, 5], [2, 5], [2, 0], [3, 2]]


def transfer(ops):
    rows = list(IDENTITY)
    for dst, src in ops:
        rows[dst] = tuple(x + y for x, y in zip(rows[dst], rows[src]))
    return tuple(rows)


def overlap_reverse_bound(target):
    """Bind the stricter tie-break cap to Ross Richardson's exact PR936 word."""
    raw = PR936_WORD.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PR936_SHA256:
        raise ValueError('PR936 comparison word changed')
    word = json.loads(gzip.decompress(raw))
    segment = word['A'][695:713]
    if len(segment) != 18 or any(f != 272 or len(ss) != 1 for f, _, ss in segment):
        raise ValueError('PR936 comparison slice changed')
    actual = [[REGS.index(dst), REGS.index(ss[0])] for _, dst, ss in segment]
    if actual != PR936_OPS or transfer(actual) != target:
        raise ValueError('PR936 comparison transfer changed')
    return transfer(list(reversed(actual)))


def nominate(original):
    target = transfer(original)
    distances, choices = {}, {}
    edges = 0
    states = 0
    infinity = 999
    started = time.monotonic()

    def distance(rows):
        nonlocal edges, states
        if rows in distances:
            return distances[rows]
        states += 1
        if states > STATE_LIMIT:
            raise ValueError('state budget exceeded; no optimum established')
        if states % 100000 == 0:
            print(f'SEARCH_PROGRESS states={states} edges={edges} elapsed={time.monotonic()-started:.1f}s', flush=True)
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
    unconstrained_replacement = list(reversed(backward))
    reverse_bound = transfer(list(reversed(original)))
    guard_states = 0
    guard_prunes = 0
    failures = set()

    def guarded(rows, reverse_rows, remaining):
        nonlocal guard_states, guard_prunes
        key = (rows, reverse_rows, remaining)
        if key in failures:
            return None
        guard_states += 1
        if guard_states > STATE_LIMIT:
            raise ValueError('reverse guard state budget exceeded; no guarded optimum established')
        if rows == IDENTITY:
            return [] if remaining == 0 else None
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
                if distances[previous] > remaining - 1:
                    continue
                next_reverse = tuple(x + y for x, y in zip(reverse_rows[dst], reverse_rows[src]))
                if any(x > y for x, y in zip(next_reverse, reverse_bound[dst])):
                    guard_prunes += 1
                    continue
                next_reverse_rows = list(reverse_rows)
                next_reverse_rows[dst] = next_reverse
                suffix = guarded(previous, tuple(next_reverse_rows), remaining - 1)
                if suffix is not None:
                    return [[dst, src]] + suffix
        failures.add(key)
        return None

    attempts = []
    guarded_backward = None
    for length in range(minimum, len(original) + 1):
        before = guard_states
        before_prunes = guard_prunes
        guarded_backward = guarded(target, IDENTITY, length)
        attempts.append({'length': length, 'states': guard_states - before,
                         'prunes': guard_prunes - before_prunes,
                         'found': guarded_backward is not None})
        print(f'REVERSE_LENGTH {attempts[-1]}', flush=True)
        if guarded_backward is not None:
            break
    if guarded_backward is not None:
        backward = guarded_backward
    print(f'REVERSE_GUARD states={guard_states} prunes={guard_prunes} found={guarded_backward is not None}', flush=True)
    baseline_guard = {'states': guard_states, 'prunes': guard_prunes,
                      'found': guarded_backward is not None,
                      'minimum': len(backward) if guarded_backward is not None else None,
                      'attempts': attempts}
    # Baseline guarded minimality was proved above. Among words at that same
    # length, choose one satisfying the stricter existing PR936 reverse cap.
    # Reset the failed-state cache because its meaning depends on this cap.
    stricter_bound = overlap_reverse_bound(target)
    if any(a > b for row_a, row_b in zip(stricter_bound, reverse_bound)
           for a, b in zip(row_a, row_b)):
        raise ValueError('PR936 cap is not dominated by the baseline cap')
    reverse_bound = stricter_bound
    guard_states = guard_prunes = 0
    failures.clear()
    stronger_backward = guarded(target, IDENTITY, len(backward))
    if stronger_backward is None:
        raise ValueError('no PR936-dominated nominee at the baseline guarded minimum')
    backward = stronger_backward
    overlap_selection = {'pr': 936, 'word_sha256': PR936_SHA256,
                         'length': len(backward), 'states': guard_states,
                         'prunes': guard_prunes, 'found': True}
    print(f'OVERLAP_SELECTION {overlap_selection}', flush=True)
    return {'replacement': list(reversed(backward)),
            'unconstrained_replacement': unconstrained_replacement, 'minimum': minimum,
            'states': len(distances), 'edges': edges,
            'distance_histogram': {str(k): v for k, v in sorted(Counter(distances.values()).items())},
            'dead_end_distance': infinity,
            'reverse_guard': baseline_guard,
            'overlap_selection': overlap_selection}


def original_ops():
    word = json.loads(gzip.decompress(WORD.read_bytes()))
    segment = word['A'][725:748]
    if len(segment) != 23 or any(f != 272 or len(ss) != 1 for f, _, ss in segment):
        raise ValueError('source slice changed')
    if (word['A'][724][0] == 272 or word['A'][748][0] == 272):
        raise ValueError('source slice is not the complete frame')
    return [[REGS.index(dst), REGS.index(ss[0])] for _, dst, ss in segment]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-witness', action='store_true')
    args = parser.parse_args()
    old = original_ops()
    result = {'phase': 'A', 'start': 725, 'stop': 748, 'frame': 272,
              'registers': REGS, 'assignment_seed': 6, 'original': old, **nominate(old)}
    path = HERE / 'WITNESS.json'
    if args.write_witness:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    elif result != json.loads(path.read_text()):
        raise ValueError('search witness mismatch')
    print(f"PASS_FRAME272_SEARCH states={result['states']} edges={result['edges']} minimum={result['minimum']}")
    for label, ops in [('original', old), ('replacement', result['replacement'])]:
        print(label, 'forward', transfer(ops), 'reverse', transfer(list(reversed(ops))))


if __name__ == '__main__':
    main()
