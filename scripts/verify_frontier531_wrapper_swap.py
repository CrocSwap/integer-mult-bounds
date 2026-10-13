#!/usr/bin/env python3
"""Correct simultaneous-side-swap control for PR531's normalized wrappers.

The frozen package's similarly named mutation overwrites both slots with the
old right wrapper. Preserve that source and add the intended control here.
Uses its exact Clifford interpreter; not a separate implementation of it.
Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import copy
import gzip
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--local', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    source = ROOT / 'research/direct-delivery504-global/code/adapters_local.py'
    spec = importlib.util.spec_from_file_location('reviewed_wrappers', source)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    c = json.load(gzip.open(a.local / 'CANONICAL-WORD.json.gz'))
    recipes = json.loads((a.local / 'RESIDUAL-ADAPTERS.json').read_text())['recipes']
    rows = []
    for frame, recipe in recipes.items():
        q = copy.deepcopy(recipe)
        q['left'], q['right'] = q['right'], q['left']
        U = c['frames'][int(frame)]
        original, mutant = m.wrapped_ok(U, recipe), m.wrapped_ok(U, q)
        if not original or mutant:
            raise ValueError('Wrapper control failed at frame ' + frame)
        rows.append(dict(frame=int(frame), original_accepted=original, true_side_swap_accepted=mutant))
    if len(rows) != 7:
        raise ValueError('Expected all seven reviewed wrappers')
    result = dict(status='PASS_TRUE_SIMULTANEOUS_SIDE_SWAP_CONTROL', frames=rows)
    a.out.write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'])


if __name__ == '__main__':
    main()
