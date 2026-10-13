#!/usr/bin/env python3
"""Check finite multi-gate helper instances and the retained Lean literal pairs.

Cold-pair identities are checked by exact Clifford arithmetic here, not claimed
as new literal Lean theorems. Uniform tape/hosting assumptions remain.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from collections import Counter

from verify_hpe_lean_binding import literal_pairs, require

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('runs', type=Path, nargs='+')
    ap.add_argument('--entering', type=int, required=True)
    ap.add_argument('--cold', type=int, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    os.environ['MULTICOLD_SOURCE'] = str(ROOT / 'research/complex-multicold')
    source = ROOT / 'research/complex-571-cold14-b3/code/hpe_adapters_local.py'
    spec = importlib.util.spec_from_file_location('cold617_adapters', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pairs = literal_pairs()
    results = []
    for run in a.runs:
        word = json.loads(gzip.decompress((run / 'CANONICAL-WORD.json.gz').read_bytes()))
        recipes = json.loads((run / 'RESIDUAL-ADAPTERS.json').read_bytes())['recipes']
        helpers = [r for r in range(2 * word['v'], len(word['start'])) if word['final'][r] != 1]
        last = {}
        for gate in word['tail']:
            require(gate[0] in ('add', 'scale'), 'Unknown tail gate')
            for r in [gate[1]] + ([gate[2]] if gate[0] == 'add' else []):
                last[r] = gate[-1]
        for gate in word['cleanup']:
            require(gate[0] in ('add', 'scale'), 'Unknown cleanup gate')
            require(not set(helpers).intersection([gate[1]] + ([gate[2]] if gate[0] == 'add' else [])),
                    'Cleanup touches an early-ended helper')
        counts = Counter()
        checked = set()
        for r in helpers:
            e, u = word['start'][r], word['final'][r]
            require(last.get(r) == u, 'Last tail frame differs from terminal frame')
            E, U = word['frames'][e], word['frames'][u]
            recipe = recipes[f'{e}:{u}']
            key = tuple(E), tuple(U)
            if E:
                counts['entering'] += 1
                require(key in pairs and recipe['rank'] == 7, 'Unknown entering pair')
                for side in ('left', 'right'):
                    require(recipe[side] == pairs[key][side], 'Different Lean literal recipe')
            else:
                counts['cold'] += 1
                require(len(U) == 4 and recipe['rank'] == 4, 'Wrong cold width')
            if key in checked:
                continue
            require(module.wrapped_ok(E, recipe, U), 'Exact wrapper identity fails')
            for side in ('left', 'right'):
                bad = copy.deepcopy(recipe)
                bad[side]['phase'] = (bad[side]['phase'] + 1) % 4
                require(not module.wrapped_ok(E, bad, U), 'Changed global phase accepted')
            checked.add(key)
        require(counts['entering'] == a.entering and counts['cold'] == a.cold,
                'Unexpected helper inventory')
        results.append({'run': run.name, 'counts': dict(counts), 'exact_pairs': len(checked),
                        'phase_mutations_rejected': 2 * len(checked),
                        'canonical_sha256': hashlib.sha256((run / 'CANONICAL-WORD.json.gz').read_bytes()).hexdigest()})
    a.out.write_text(json.dumps({'status': 'PASS_FINITE_MULTI_TAIL_AND_EXACT_WRAPPER_BINDING',
                                'instances': results,
                                'scope': 'Entering pairs equal Lean literals; cold pairs use exact finite Clifford checks. '
                                         'Multi-tail last-frame and no-later-touch hypotheses checked. '
                                         'Not a full physical realization or multiplication proof.'}, indent=2) + '\n')
    print('PASS finite helper-interface binding')


if __name__ == '__main__':
    main()
