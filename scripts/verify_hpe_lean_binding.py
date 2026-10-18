#!/usr/bin/env python3
"""Bind emitted HPE wrapper recipes to the literal pairs proved by Lean.

This checks source/instance correspondence; it does not replace lake build.
"""
import argparse
import ast
import copy
import gzip
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / 'research/hyperplane-end-lean/HyperplaneEnd/Exact.lean'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def literal_pairs():
    text = LEAN.read_text(encoding='utf-8')
    pairs = {}
    for n in (1, 2, 3):
        match = re.search(r'def pair%d : Pair := (.*?)\n\n' % n, text, re.S)
        require(match is not None, 'Missing literal Lean pair')
        data = ast.literal_eval(match[1].replace('⟨', '[').replace('⟩', ']'))
        entrance, terminal, left, right = data
        fields = ('quadratic_rows', 'linear_Z4', 'matrix_rows', 'offset', 'phase')
        pairs[tuple(entrance), tuple(terminal)] = {
            'left': dict(zip(fields, left, strict=True)),
            'right': dict(zip(fields, right, strict=True)),
        }
    require(len(pairs) == 3, 'Duplicate Lean pair')
    return pairs


def check(word, adapters, pairs):
    found = set()
    for gate in word['tail']:
        require(gate[0] == 'add' and gate[3:5] == [-1, 1], 'Tail is not h -= p')
        helper, terminal = gate[1], gate[-1]
        entrance = word['start'][helper]
        require(word['final'][helper] == terminal, 'Wrong terminal label')
        key = tuple(word['frames'][entrance]), tuple(word['frames'][terminal])
        require(key in pairs, 'Pair absent from Lean proof')
        recipe = adapters['recipes'][f'{entrance}:{terminal}']
        require(recipe['rank'] == 7, 'Wrong residual width')
        for side in ('left', 'right'):
            require(recipe[side] == pairs[key][side], 'Emitted recipe differs from Lean: ' + side)
        found.add(key)
    require(len(word['tail']) == 38 and len(found) == 3, 'Selected instance inventory')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('runs', type=Path, nargs='+')
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    pairs = literal_pairs()
    results = []
    for run in a.runs:
        word = json.loads(gzip.decompress((run / 'CANONICAL-WORD.json.gz').read_bytes()))
        adapters = json.loads((run / 'RESIDUAL-ADAPTERS.json').read_bytes())
        check(word, adapters, pairs)
        h, u = word['tail'][0][1], word['tail'][0][-1]
        key = f"{word['start'][h]}:{u}"
        rejected = []
        for side in ('left', 'right'):
            bad = copy.deepcopy(adapters)
            bad['recipes'][key][side]['phase'] ^= 1
            try:
                check(word, bad, pairs)
            except ValueError:
                rejected.append(side + '_phase')
            else:
                raise ValueError('Changed wrapper accepted')
        results.append({'run': run.name, 'helpers': 38, 'pairs': 3, 'rejected': rejected})
    result = {'status': 'PASS_EMITTED_HPE_RECIPES_EQUAL_LEAN_LITERALS',
              'lean_source_sha256': hashlib.sha256(LEAN.read_bytes()).hexdigest(), 'instances': results}
    a.out.write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'])


if __name__ == '__main__':
    main()
