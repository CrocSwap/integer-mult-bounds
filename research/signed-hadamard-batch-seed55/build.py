#!/usr/bin/env python3
"""Bounded signed Hadamard connector construction; Apache-2.0.

Prepared with substantial OpenAI Codex assistance. No optimum is claimed.
"""
import argparse
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
H = [(1, 1, 1, 1), (1, -1, 1, -1), (1, 1, -1, -1), (1, -1, -1, 1)]
SEED = 55
TRIALS = 4000
B_LENGTHS = [1, 2, 3, 4]
A_LENGTHS = [2, 3, 4, 5]


def leaf_count(length):
    if length == 1:
        return 1
    cut = length//2
    return 2*leaf_count(cut)+2*leaf_count(length-cut)


def nominate():
    rng = random.Random(SEED)
    best = None
    best_score = None
    distinct = set()
    admitted = 0
    histogram = {}
    for trial in range(TRIALS):
        moves = [(j, sign) for j in range(4) for sign in (-1, 1)]
        rng.shuffle(moves)
        distinct.add(tuple(moves))
        state = [0]*4
        states = [tuple(state)]
        for j, sign in moves:
            state[j] += sign
            states.append(tuple(state))
        differences = {}
        for u, before in enumerate(states):
            for v, after in enumerate(states):
                delta = tuple(after[j]-before[j] for j in range(4))
                differences.setdefault(delta, (u, v))
        rows = []
        for target in H:
            if target in differences:
                rows.append([differences[target]])
                continue
            nominations = []
            for first, pair in differences.items():
                remainder = tuple(target[j]-first[j] for j in range(4))
                if remainder in differences:
                    nominations.append([pair, differences[remainder]])
            if not nominations:
                break
            rows.append(min(nominations))
        if len(rows) != 4:
            continue
        admitted += 1
        queries = 8+sum(2*len(row) for row in rows)
        histogram[queries] = histogram.get(queries, 0)+1
        cost = 2*sum(map(leaf_count, B_LENGTHS))
        cost += sum(2*len(row)*leaf_count(length) for row, length in zip(rows, A_LENGTHS))
        score = (cost, queries, moves, rows)
        if best_score is None or score < best_score:
            best_score = score
            best = (trial, moves, rows)
    if best is None:
        raise ValueError('no candidate in completed domain')
    trial, moves, rows = best
    taps = [[] for _ in range(9)]
    for i, pairs in enumerate(rows):
        for minus, plus in pairs:
            taps[minus].append(['A', i, -1])
            taps[plus].append(['A', i, 1])
    word = []
    for position in range(9):
        word.extend(sorted(taps[position]))
        if position < 8:
            j, sign = moves[position]
            word.append(['B', j, sign])
    return {
        'format': 'signed-hadamard-batch-seed55/1',
        'base_commit': 'bbc600db2fc15007b7c914f4f2b2ed55fa909c87',
        'assignment_seed': SEED, 'matrix': H,
        'B_lengths': B_LENGTHS, 'A_lengths': A_LENGTHS,
        'word': word, 'source_path': moves, 'readout_pairs': rows,
        'winning_trial': trial, 'leaf_calls': best_score[0],
        'query_calls': best_score[1],
        'search': {'trials': TRIALS, 'distinct_source_paths': len(distinct),
                   'admitted_trials': admitted, 'query_histogram': histogram,
                   'domain': 'one positive and one negative query for each of four sources; each output gets one or two signed differences of visited connector states',
                   'stopping_rule': 'Complete exactly 4000 seed-55 shuffled source paths; select minimum charged leaf cost, then query count and lexicographic word.',
                   'optimality_claim': False},
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with args.output.open('x') as stream:
        result = nominate()
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write('\n')
    print('BUILT_SIGNED_HADAMARD_BATCH queries=%d leaf_calls=%d' %
          (result['query_calls'], result['leaf_calls']))
