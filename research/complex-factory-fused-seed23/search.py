#!/usr/bin/env python3
"""Reproduce the bounded ADD-triple nomination; no circuit optimality claim.

Prepared for CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
New search class on Alluri's pinned PR681 circuit. Its inherited admission
checker is reused, but exact nomination uses the row implementation below.
"""
import copy
from fractions import Fraction as Q
import importlib.util
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREDECESSOR = ROOT / 'research/complex-factory5-resynthesis'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def commute(a, b):
    if a[0] == b[0] == 'add':
        return a[1] != b[2] and b[1] != a[2]
    if a[0] == b[0] == 'scale':
        return True
    scale, add = (a, b) if a[0] == 'scale' else (b, a)
    return scale[1] not in add[1:3]


def matrix(events):
    # Fixed dimension includes identity rows for every untouched register.
    rows = [[Q(i == j) for j in range(8)] for i in range(8)]
    for e in events:
        target, source, q = e[1], e[2], Q(e[3], e[4])
        rows[target] = [a + q * b for a, b in zip(rows[target], rows[source])]
    return rows


def nominate(reference, inherited):
    original = reference['replacement']
    word = copy.deepcopy(original)
    passes = []
    for step in range(8):
        counts = dict(triples=0, movable=0, candidate_pairs=0, identities=0, admitted=0)
        offers = []
        for i, j, k in itertools.combinations(range(len(word)), 3):
            triple = [word[x] for x in (i, j, k)]
            if any(e[0] != 'add' for e in triple):
                continue
            counts['triples'] += 1
            if not all(commute(word[j], word[x]) for x in range(i + 1, j)):
                continue
            if not all(commute(word[k], word[x]) for x in range(i + 1, k) if x != j):
                continue
            counts['movable'] += 1
            target = matrix(triple)
            support = {r for e in triple for r in e[1:3]}
            for order in itertools.permutations(range(3), 2):
                pair = [triple[x] for x in order]
                counts['candidate_pairs'] += 1
                if {r for e in pair for r in e[1:3]} != support or matrix(pair) != target:
                    continue
                counts['identities'] += 1
                candidate = word[:i] + pair + [e for x, e in enumerate(word[i + 1:], i + 1)
                                               if x not in (j, k)]
                try:
                    inherited.validate(original, candidate, reference['frame'],
                                       reference['entry_frames'])
                except ValueError:
                    continue
                counts['admitted'] += 1
                offers.append((len(inherited.lowering(candidate)), i, j, k, order, candidate))
        if not offers:
            passes.append(dict(step=step, counts=counts, accepted=None))
            break
        best = min(offers, key=lambda x: x[:5])
        word = best[5]
        passes.append(dict(step=step, counts=counts,
                           accepted=dict(indices=list(best[1:4]), pair_order=list(best[4]),
                                         gates=len(word), primitive_cost=best[0])))
    return word, passes


def main():
    checker = load('factory_fusion_verifier', HERE / 'verify.py')
    checker.check_pins()
    inherited = load('factory_predecessor', PREDECESSOR / 'verify.py')
    reference = json.loads((PREDECESSOR / 'CIRCUIT.json').read_text())
    certificate = json.loads((HERE / 'CIRCUIT.json').read_text())
    word, passes = nominate(reference, inherited)
    checker.require(word == certificate['replacement'] and passes == certificate['search']['passes'],
                    'bounded nomination differs from frozen circuit/search receipt')
    print('PASS_FACTORY_FUSION_SEARCH passes=3 add_triples=8801 ordered_pairs=1950 '
          'accepted=2 terminal_neighborhood_empty no_optimality_claim')


if __name__ == '__main__':
    main()
