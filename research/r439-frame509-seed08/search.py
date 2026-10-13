#!/usr/bin/env python3
"""Bounded whole-block positive factor search; Apache-2.0.

The bidirectional reduction method follows martin Rv's PR884 frame-521
search. This independently targets PR589 frame 509, beyond PR843's
single-hoist class. Prepared with substantial OpenAI Codex assistance.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
SOURCE_SHA = 'e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f'
BASE = 'bbc600db2fc15007b7c914f4f2b2ed55fa909c87'
FRAME = 509
SLICE = (283, 314)
SEED = 8
TRIALS = 12000


def matrix(ops, size):
    rows = [[int(i == j) for j in range(size)] for i in range(size)]
    for dst, src in ops:
        rows[dst] = [a + b for a, b in zip(rows[dst], rows[src])]
    return rows


def search():
    raw = (ROOT / SOURCE).read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise ValueError('source pin mismatch')
    word = json.loads(gzip.decompress(raw))
    block = word['B'][slice(*SLICE)]
    if len(block) != 31 or any(f != FRAME or len(ss) != 1 for f, _, ss in block):
        raise ValueError('source block mismatch')
    regs = sorted({r for _, dst, srcs in block for r in [dst, *srcs]})
    index = {r: i for i, r in enumerate(regs)}
    old = [(index[d], index[ss[0]]) for _, d, ss in block]
    size = len(regs)
    target, identity = matrix(old, size), matrix([], size)
    old_reverse = matrix(old[::-1], size)
    rng = random.Random(SEED)
    best = old
    trace = []
    completed = accepted = dead = cutoff = 0
    for trial in range(TRIALS):
        rows = [r[:] for r in target]
        prefix, suffix = [], []
        mode = trial % 7
        while rows != identity and len(prefix) + len(suffix) < len(best):
            cols = list(zip(*rows))
            choices = []
            for dst in range(size):
                for src in range(size):
                    if dst == src:
                        continue
                    if rows[dst][dst] > rows[src][dst] and all(
                            a >= b for a, b in zip(rows[dst], rows[src])):
                        choices.append((sum(rows[src]), 0, dst, src))
                    if rows[src][src] > rows[src][dst] and all(
                            a >= b for a, b in zip(cols[src], cols[dst])):
                        choices.append((sum(cols[dst]), 1, dst, src))
            if not choices:
                dead += 1
                break
            if mode == 0:
                high = max(c[0] for c in choices)
                chosen = rng.choice([c for c in choices if c[0] == high])
            else:
                chosen = max(choices, key=lambda c: c[0] * rng.random() ** (mode / 2))
            _, side, dst, src = chosen
            if side == 0:
                rows[dst] = [a - b for a, b in zip(rows[dst], rows[src])]
                suffix.append((dst, src))
            else:
                for row in rows:
                    row[src] -= row[dst]
                prefix.append((dst, src))
        else:
            if rows != identity:
                cutoff += 1
        if rows != identity:
            continue
        completed += 1
        ops = prefix + suffix[::-1]
        if matrix(ops, size) != target:
            raise ValueError('factor reconstruction failed')
        reverse = matrix(ops[::-1], size)
        if not all(a <= b for x, y in zip(reverse, old_reverse) for a, b in zip(x, y)):
            continue
        accepted += 1
        if len(ops) < len(best):
            best = ops
            trace.append({'trial': trial, 'additions': len(best)})
            print('improvement', trace[-1], flush=True)
    return {
        'format': 'r439-frame509-seed08/1', 'base_commit': BASE,
        'assignment_seed': SEED, 'source': SOURCE, 'source_sha256': SOURCE_SHA,
        'frame': FRAME, 'slice': list(SLICE), 'registers': regs,
        'baseline_additions': len(old), 'candidate_additions': len(best),
        'gates': [[FRAME, regs[d], [regs[s]]] for d, s in best],
        'search': {
            'method': 'bidirectional diagonal-preserving nonnegative integer subtraction',
            'seed': SEED, 'trials': TRIALS, 'identity_factorizations': completed,
            'reverse_dominated_factorizations': accepted,
            'dead_ends': dead, 'incumbent_cutoffs': cutoff,
            'improvement_trace': trace,
            'stopping_rule': 'Exactly 12000 trials; stop a trial at identity, no legal subtraction, or incumbent length.',
            'optimality_claim': False,
        },
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('output already exists')
    result = search()
    with args.output.open('x') as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write('\n')
    print('PASS_R439_FRAME509_SEARCH', result['baseline_additions'],
          '->', result['candidate_additions'], result['search'])
