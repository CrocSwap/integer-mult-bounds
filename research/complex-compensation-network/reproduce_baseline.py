#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reproduce the bounded PR1119 routine comparison without modifying its code.

conorholds, with substantial OpenAI Codex assistance.
Stephan Arrington's original solver and AI disclosure remain credited.
This calls its dimension-parameterized routines, not its U8-only main verifier.
"""
import argparse
import importlib.util
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from network import event, load, price, require, sha, strict_json
from comparison import canonical, copy_unit_count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', type=Path, required=True)
    args = parser.parse_args()
    root = args.upstream.resolve()
    record = strict_json((HERE / 'METHOD-BASELINES.json').read_bytes())
    require((record['seed'], record['trial_limit']) == (30, 17), 'published comparison domain')
    for row in record['files']:
        require(sha((root / row['path']).read_bytes()) == row['sha256'], 'published comparison source pin')
    source = root / record['source_path']
    sys.path.insert(0, str(source.parent))
    spec = importlib.util.spec_from_file_location('credited_pr1119', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    word, _, _, _, _ = load()
    dimension = 2*word['v']+word['R']
    require(dimension == record['dimension'], 'published comparison dimension')
    matrix = module.apply_word_to_cols(word['cleanup'], dim=dimension)
    rng = random.Random(record['seed'])
    trials = []; winner = None
    for trial in range(record['trial_limit']):
        swap_pen = rng.choice([3, 4, 5, 6]); scale_pen = rng.choice([0, 1])
        gates, _, _, _, cycles = module.solve_lpr_smart_scale(matrix, swap_pen, scale_pen, rng, dim=dimension)
        horner = sum(map(price, gates)); modern = copy_unit_count([event(g) for g in gates])
        trials.append(dict(trial=trial, swap_penalty=swap_pen, scale_penalty=scale_pen,
                           horner_real=horner, copy_unit_real=modern, macros=len(gates), cycles=cycles))
        if winner is None or (horner, modern, trial) < winner[0]:
            winner = ((horner, modern, trial), gates)
    require(trials == record['trials'], 'published comparison trial receipts')
    require(winner[0][2] == record['selected_trial'], 'published comparison winner')
    gates = winner[1]
    require(sha(canonical(gates)) == record['cleanup_payload_sha256'] and
            gates == strict_json((HERE / 'PR1119-CLEANUP.json').read_bytes()), 'published comparison literal output')
    require(module.apply_word_to_cols(gates, dim=dimension) == matrix, 'published comparison complete operator')
    print('PASS_PR1119_ROUTINE_COMPARISON dimension='+str(dimension)+' seed=30 trials=17 selected='+str(winner[0][2]))


if __name__ == '__main__':
    main()
