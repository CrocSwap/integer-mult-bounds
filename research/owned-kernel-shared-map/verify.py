#!/usr/bin/env python3
"""Exact rank-table and invoice calibration; no search or supplier admission.

Apache-2.0; substantial OpenAI Codex assistance and retained source credit.
"""
from itertools import product
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shared_maps as S


def rank(vectors):
    pivots = {}
    for v in vectors:
        while v:
            p = v.bit_length() - 1
            if p in pivots:
                v ^= pivots[p]
            else:
                pivots[p] = v
                break
    return len(pivots)


def geometry():
    comparisons = maps = 0
    for n in (1, 2, 3):
        spaces = {frozenset({0})}
        for v in range(1, 1 << n):
            for old in list(spaces):
                if v not in old:
                    spaces.add(frozenset(set(old) | {x ^ v for x in old}))
        groups = [cols for cols in product(range(1, 1 << n), repeat=n) if rank(cols) == n]
        maps += len(groups)
        for A in spaces:
            images = [(cols[0] == 1, S.M.mask(S.M.mv(cols, x) for x in A)) for cols in groups]
            for B in spaces:
                amask, bmask = S.M.mask(A), S.M.mask(B)
                free = min(S.M.fourier_rank(image, bmask) for _, image in images)
                line = min(S.M.fourier_rank(image, bmask) for fixed, image in images if fixed)
                S.need(S.minimum_rank(amask, bmask) == free, 'Exact unconstrained native minimum')
                S.need(S.minimum_rank(amask, bmask, (1, 1)) == line, 'Exact shared-line native minimum')
                comparisons += 2
    S.need(S.minimum_rank(S.M.mask({0, 1}), S.M.mask({0, 2}), (1, 1)) == 2,
           'Equal dimensions cannot evade a preserved line')
    return {'minimum_comparisons': comparisons, 'invertible_maps': maps}


def main():
    model = S.build(S.payload(), [1])
    paid, helpers = S.M.invoice(model, [])
    S.need(len(model['owned_copies']) == 8, 'Eight owned inputs released')
    for row in model['owned_copies']:
        S.need(row['node'] not in model['fixed'], 'Owned source is actually variable')
        changed, _ = S.M.invoice(model, [row['node']])
        S.need(changed[8] == 7 and changed[7] == 1, 'Actual changed center rank charged')
    print(json.dumps({'status': 'PASS_SHARED_MAP_RANK_AND_BASELINE_CALIBRATION_ONLY',
        'geometry': geometry(), 'paid': dict(paid), 'helpers': dict(helpers),
        'changed_native_tables': model['changed_native_tables'],
        'free_shared_late_maps': len(model['shared_late_maps']),
        'preserved_prelude_lines': len(model['prelude_lines']),
        'new_kappa': False}, sort_keys=True))


if __name__ == '__main__':
    main()
