#!/usr/bin/env python3
"""Bounded positive-integer factor search, not an optimality proof.

Prepared for CubeJerry with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[2]
WORD = ROOT / 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
WORD_SHA256 = 'e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f'
SEED = 17
TRIALS = 12000


def matrix(ops, size):
    rows = [[int(i == j) for j in range(size)] for i in range(size)]
    for dst, src in ops:
        rows[dst] = [x + y for x, y in zip(rows[dst], rows[src])]
    return rows


def search():
    if hashlib.sha256(WORD.read_bytes()).hexdigest() != WORD_SHA256:
        raise ValueError('source word pin mismatch')
    word = json.loads(gzip.decompress(WORD.read_bytes()))
    block = word['B'][361:404]
    registers = sorted({r for _, dst, srcs in block for r in [dst, *srcs]})
    index = {r: i for i, r in enumerate(registers)}
    old = [(index[dst], index[src]) for frame, dst, srcs in block for src in srcs]
    size = len(registers)
    target = matrix(old, size)
    identity = matrix([], size)
    rng = random.Random(SEED)
    best = old
    best_score = (len(old), sum(map(sum, matrix(reversed(old), size))))
    successes = 0
    histogram = {}
    for trial in range(TRIALS):
        rows = [r[:] for r in target]
        undo = []
        while rows != identity:
            choices = []
            for dst, row in enumerate(rows):
                for src, donor in enumerate(rows):
                    if dst != src and all(x >= y for x, y in zip(row, donor)):
                        choices.append((sum(donor), dst, src))
            if not choices:
                break
            choices.sort(reverse=True)
            # Cycle greedy, mildly perturbed, and broad exploration policies.
            width = (1, 2, 4, 8, len(choices))[trial % 5]
            _, dst, src = choices[rng.randrange(min(width, len(choices)))]
            rows[dst] = [x - y for x, y in zip(rows[dst], rows[src])]
            undo.append((dst, src))
        if rows != identity:
            continue
        successes += 1
        ops = list(reversed(undo))
        histogram[len(ops)] = histogram.get(len(ops), 0) + 1
        score = (len(ops), sum(map(sum, matrix(reversed(ops), size))))
        if score < best_score:
            best, best_score = ops, score
            print('improved', trial, score, flush=True)
    return {
        'format': 'r439-block522-positive-factor-v1',
        'source_sha256': WORD_SHA256,
        'seed': SEED,
        'trials': TRIALS,
        'successful_identity_factorizations': successes,
        'gate_count_histogram': dict(sorted(histogram.items())),
        'frame': 522,
        'slice': [361, 404],
        'registers': registers,
        'baseline_additions': len(old),
        'candidate_additions': len(best),
        'reverse_matrix_entry_sum': best_score[1],
        'operations': [[registers[d], registers[s]] for d, s in best],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = search()
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print('PASS_R439_BLOCK522_SEARCH', result['candidate_additions'],
          result['successful_identity_factorizations'], '/', TRIALS)
