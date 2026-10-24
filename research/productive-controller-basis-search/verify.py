#!/usr/bin/env python3
"""Reproduce the complete finite search, then replay survivors symbolically."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

import algebra as A
import global_check

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for row in pins['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'Changed source input: ' + row['path'])


def controls():
    need(len(A.FULL) == 1680 and len(A.THIN) == 105, 'Complete gate inventories')
    for p, n in A.FULL:
        need(A.rank(p) == 2 and A.rank(n) == 1, 'Actual operator ranks')
        need(A.multiply_binary(p, p) == list(p), 'Projector idempotence')
        need(A.multiply_binary(n, n) == [0] * 4, 'Query nilpotence')
        need(A.multiply_binary(p, n) == A.multiply_binary(n, p) == list(n),
             'Full multiplier commutes with its query')
    ids = [A.elementary(0, 1), A.elementary(1, 0), A.elementary(0, 1),
           A.elementary(2, 3), A.elementary(3, 2), A.elementary(2, 3)]
    positive = A.literal(63, ids)
    positive_stats = A.stats(positive)
    need(positive_stats['central_query_on_every_output'] and
         positive_stats['coefficient_rank_sum'] == 4,
         'Two independent three-call controllers factor')
    broken = A.literal(63, ids[:2] + [ids[1]] + ids[3:])
    need(not A.stats(broken)['central_query_on_every_output'],
         'Wrong query orientation is rejected')
    # Four native calls plus one thin call: cancellation alone is insufficient.
    near = A.literal(27, [112, 0, 39, 832, 384])
    near_stats = A.stats(near)
    need(near_stats['central_query_on_every_output'] and
         near_stats['coefficient_rank_sum'] == 6,
         'A genuine all-Q controller still fails independent Fourier outputs')
    # Setting all D=1 hides this failure; preserve them as distinct variables.
    specialized = [[int(x.bit_count() % 2) for x in row] for row in near]
    need(A.rank([sum(x << j for j, x in enumerate(row)) for row in specialized]) == 4,
         'Collapsed-stage false positive is demonstrated')
    return {'positive_six_call_rank_sum': 4, 'wrong_query_rejected': True,
            'five_call_all_Q_rank_sum': 6, 'collapsed_stage_false_positive': True,
            'gate_relations_checked': 1680}


def check_numeric_transitions(executable):
    """Compare C++ updates with evaluation of distinct symbolic monomials."""
    def multiply(a, b):
        value = 0
        while b:
            if b & 1:
                value ^= a
            b >>= 1
            a <<= 1
            if a & 16:
                a ^= 19
        return value

    result = subprocess.run([str(executable), 'trace'], check=True,
                            capture_output=True, text=True, timeout=5)
    count = 0
    for line in result.stdout.splitlines():
        args = line.split()
        need(args[0] == 'TRACE' and len(args) == 15, 'Numeric trace format')
        mask, *values = map(int, args[1:])
        ids, expected = values[:5], values[5:]
        matrix = A.literal(mask, ids)
        even, odd = [0] * 4, [0] * 4
        for i, row in enumerate(matrix):
            for j, poly in enumerate(row):
                for g in range(poly.bit_length()):
                    if not poly >> g & 1:
                        continue
                    value = 1
                    for stage in range(5):
                        if g >> (stage + 1) & 1:
                            value = multiply(value, stage + 2)
                    (odd if g & 1 else even)[i] ^= value << (4*j)
        need(even + odd == expected, 'Independent polynomial/numeric transition check')
        count += 1
    need(count == 128, 'All numeric traces checked')
    return count


def run():
    authenticate()
    checked = controls()
    checked['global_proof_controls'] = global_check.check()
    compiler = shutil.which('g++') or shutil.which('clang++')
    need(compiler is not None, 'A C++17 compiler is required')
    cases, all_counts = {}, Counter()
    with tempfile.TemporaryDirectory(prefix='controller-basis-') as tmp:
        executable = Path(tmp) / 'search'
        subprocess.run([compiler, '-O2', '-std=c++17', str(HERE / 'search.cpp'),
                        '-o', str(executable)], check=True, capture_output=True, timeout=30)
        checked['independent_transition_words'] = check_numeric_transitions(executable)
        for mask in range(32):
            if mask.bit_count() < 3:
                continue
            result = subprocess.run([str(executable), str(mask)], check=True,
                                    capture_output=True, text=True, timeout=30)
            counts, ranks, digest = Counter(), Counter(), sha256()
            for line in result.stdout.splitlines():
                args = line.split()
                need(args[0] == 'HIT' and int(args[1]) == mask, 'Search record format')
                ids = list(map(int, args[2:]))
                need(len(ids) == 5, 'Five exact native/query calls')
                stats = A.stats(A.literal(mask, ids))
                counts['numeric_survivors'] += 1
                need(stats['central_query_on_every_output'],
                     'A numeric survivor must pass the distinct-variable replay')
                counts['symbolic_all_Q'] += 1
                ranks[stats['coefficient_rank_sum']] += 1
                counts['factored'] += int(stats['coefficient_rank_sum'] == 4)
                digest.update((line + '\n').encode())
            need('full=1680 thin=105' in result.stderr, 'Search inventory sizes')
            need('mask=' + str(mask) + ' hits=' + str(counts['numeric_survivors'])
                 in result.stderr, 'Complete survivor stream')
            # The prefix counts authenticate the actually run search, not a saved list.
            cases[str(mask)] = {'counts': dict(sorted(counts.items())),
                                'rank_sum_histogram': {str(k): v for k, v in sorted(ranks.items())},
                                'survivor_sha256': digest.hexdigest(),
                                'prefix_census': result.stderr.splitlines()[-1]}
            all_counts.update(counts)
    need(all_counts['factored'] == 0 and all_counts['symbolic_all_Q'] == 12480,
         'Frozen complete census')
    return {'schema': 'productive-controller-basis-search/1',
            'status': 'PASS_FINITE_FIVE_CALL_NO_IDLE_BINARY_SEARCH_NO_KAPPA',
            'cases': cases, 'totals': dict(sorted(all_counts.items())),
            'controls': checked, 'new_kappa': None}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    receipt = run()
    target = HERE / 'RESULT.json'
    if args.write:
        target.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    else:
        need(receipt == json.loads(target.read_text()), 'Committed exact receipt')
    print(receipt['status'])
    print(json.dumps(receipt['totals'], sort_keys=True))
