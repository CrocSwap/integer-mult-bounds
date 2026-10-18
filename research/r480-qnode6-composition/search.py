#!/usr/bin/env python3
"""Bounded Q-node6 search with four composition backgrounds; Apache-2.0.

Prepared for @CubeJerry with OpenAI Codex assistance. The elimination algorithm
is martinxxx9's retained PR1089 implementation, imported unchanged and explicitly
bound to Q-node6. This contribution does not claim a new synthesis algorithm.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FRAME, START, STOP = 488, 2460, 2511
REGS = [11, 14, 34, 36, 41, 44, 83, 86, 91, 93, 113, 116]
SEED, TRIALS = 2026101406, 1000
SOURCE = 'research/e8-r480-dead-totals/data/bitE8mut-r480.json.gz'


def load(relative):
    spec = importlib.util.spec_from_file_location('qnode6_search_dependency', ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_sources():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for name, pin in pins['files'].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != pin['sha256']:
            raise ValueError('source pin: ' + name)


def prior_programs():
    q2 = json.loads((ROOT / 'research/r480-qnode-seed02/RECIPE.json').read_text())
    q5 = json.loads((ROOT / 'research/r480-qnode5-seed05/CANDIDATE.json').read_text())
    return q2['replacement_A_events'], q5['best']['gates']


def compose(word, q2, q5, q6, mask):
    """Offsets refer to the frozen original; splice in descending order."""
    changed = dict(word)
    changed['A'] = list(word['A'])
    replacements = [(2250, 2302, q2), (2409, 2460, q5), (START, STOP, q6)]
    for bit in (2, 1, 0):
        if mask & (1 << bit):
            start, stop, gates = replacements[bit]
            changed['A'][start:stop] = gates
    changed['C'] = [[1, d, list(ss)] for _, d, ss in reversed(changed['A'] + changed['B'])
                    if d < word['v'] or d >= 2 * word['v']]
    return changed


def run():
    check_sources()
    engine = load('research/r480-qnode5-seed05/search.py')
    # Only the object binding changes. The pinned algorithm and bound evaluator
    # are unmodified; this module instance has no effects on other packages.
    engine.FRAME, engine.START, engine.STOP, engine.REGS = FRAME, START, STOP, REGS
    word = json.loads(gzip.decompress((ROOT / SOURCE).read_bytes()))
    q2, q5 = prior_programs()
    target = engine.matrix(word['A'][START:STOP])
    rng, histogram = random.Random(SEED), Counter()
    best = None
    priced = admitted = 0
    for trial in range(TRIALS):
        gates = engine.synthesize(target, rng)
        histogram[len(gates)] += 1
        # Longer than the incumbent cannot win the stated lexicographic rule.
        if len(gates) >= 51 or (best is not None and len(gates) > len(best['gates'])):
            continue
        priced += 1
        budgets = [engine.bounds(compose(word, q2, q5, gates, mask)) for mask in range(4, 8)]
        if any(payload >= 1 << 104 for _, _, payload in budgets):
            continue
        admitted += 1
        key = (len(gates), max(x[2] for x in budgets), gates)
        if best is None or key < (len(best['gates']), best['worst_payload'], best['gates']):
            best = dict(trial=trial, gates=gates, budgets=budgets, worst_payload=key[1])
    if best is None:
        raise ValueError('No shorter candidate admitted; this is a bounded search failure only')
    return dict(format='r480-qnode6-composition-search-v1', assignment_seed=6,
                seed=SEED, trajectories=TRIALS, frame=FRAME, start=START, stop=STOP,
                registers=REGS, target_f2_rows=target, histogram=dict(sorted(histogram.items())),
                candidates_priced_in_four_backgrounds=priced, candidates_admitted=admitted,
                selection_rule='gate count, maximum complete payload over masks 4..7, lexicographic gates',
                best=best)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='new JSON file')
    args = parser.parse_args()
    result = run()
    with args.output.open('x', encoding='utf-8') as output:
        json.dump(result, output, indent=2, sort_keys=True)
        output.write('\n')
    print('SEARCH_COMPLETE trajectories=1000 qnode6=51->%s all_four_backgrounds_admitted' %
          len(result['best']['gates']))
