#!/usr/bin/env python3
"""Bounded nomination, not a lower-bound proof. Standard library only.

Prepared for the machine owner with substantial OpenAI Codex assistance.
New code: Apache-2.0. The source circuit is eumemic's PR543.
"""
import argparse
import gzip
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'research/e8-bit-r420/data/bitE8mut-r420.json.gz'
SOURCE_SHA256 = '9721a3819efd68307f66f00d84a952eb28eb7c3ad2ce79653ce295c98a764784'
BASE = '66849e1475c930fd7732b1a0067ffee7e1e95f60'
REGISTERS = [8, 13, 33, 39, 42, 47, 80, 85, 88, 94, 114, 119]


def transfer(ops, n):
    rows = [[int(i == j) for j in range(n)] for i in range(n)]
    for a, b in ops:
        rows[a] = [x + y for x, y in zip(rows[a], rows[b])]
    return rows


def nominate(seed, trials):
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError('source pin mismatch')
    word = json.loads(gzip.decompress(raw))
    gates = word['B'][559:597]
    if any(f != 551 or len(ss) != 1 for f, _, ss in gates):
        raise ValueError('source block shape')
    old = [(REGISTERS.index(d), REGISTERS.index(ss[0])) for _, d, ss in gates]
    n = len(REGISTERS)
    target, identity = transfer(old, n), transfer([], n)
    old_reverse = transfer(old[::-1], n)
    rng = random.Random(seed)
    best, best_ops = len(old), old
    successes = accepted = dead_ends = cutoff = 0
    trace, reverse_control = [], None
    for trial in range(trials):
        m = [row[:] for row in target]
        first, last = [], []
        mode = trial % 5
        while m != identity and len(first) + len(last) < best:
            columns = list(zip(*m))
            options = []
            for a in range(n):
                for b in range(n):
                    if a == b:
                        continue
                    if m[a][a] > m[b][a] and all(x >= y for x, y in zip(m[a], m[b])):
                        options.append((sum(m[b]), 0, a, b))
                    if m[b][b] > m[b][a] and all(x >= y for x, y in zip(columns[b], columns[a])):
                        options.append((sum(columns[a]), 1, a, b))
            if not options:
                dead_ends += 1
                break
            if mode == 0:
                high = max(q[0] for q in options)
                op = rng.choice([q for q in options if q[0] == high])
            else:
                op = max(options, key=lambda q: q[0] * rng.random() ** (mode / 2))
            _, side, a, b = op
            if side == 0:
                m[a] = [x - y for x, y in zip(m[a], m[b])]
                last.append((a, b))
            else:
                for row in m:
                    row[b] -= row[a]
                first.append((a, b))
        else:
            if m != identity:
                cutoff += 1
        if m != identity:
            continue
        successes += 1
        ops = first + last[::-1]
        if transfer(ops, n) != target:
            raise RuntimeError('factorization invariant failed')
        reverse = transfer(ops[::-1], n)
        if not all(x <= y for rx, ry in zip(reverse, old_reverse) for x, y in zip(rx, ry)):
            if reverse_control is None:
                reverse_control = {'trial': trial, 'operations': ops}
            continue
        accepted += 1
        if len(ops) < best:
            best, best_ops = len(ops), ops
            trace.append({'trial': trial, 'gates': best})
    if successes + dead_ends + cutoff != trials:
        raise RuntimeError('trial accounting failed')
    return {
        'format': 'r420-block9-positive-factorization-v1',
        'base_commit': BASE, 'source_sha256': SOURCE_SHA256,
        'block_index': 9, 'slice': [559, 597], 'frame': 551,
        'registers': REGISTERS, 'original_operations': old, 'operations': best_ops,
        'search': {
            'seed': seed, 'trials': trials, 'integer_factorizations': successes,
            'reverse_dominated_factorizations': accepted,
            'dead_ends': dead_ends, 'gate_budget_cutoffs': cutoff,
            'improvement_trace': trace,
            'stopping_rule': 'Fixed trial count; each trial stops at identity, no legal subtraction, or current best gate count.',
            'optimality_claim': False,
        },
        'reverse_domination_negative_control': reverse_control,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--seed', type=int, default=19)
    ap.add_argument('--trials', type=int, default=2000)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    if args.trials <= 0:
        ap.error('--trials must be positive')
    if args.output.exists():
        ap.error('output already exists')
    result = nominate(args.seed, args.trials)
    with args.output.open('x') as handle:
        json.dump(result, handle, indent=2)
        handle.write('\n')
    print(json.dumps(result['search'], sort_keys=True))
    print('NOMINATED_BLOCK9', len(result['original_operations']), '->', len(result['operations']))


if __name__ == '__main__':
    main()
