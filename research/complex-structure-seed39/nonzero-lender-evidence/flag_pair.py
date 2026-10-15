#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Exact 512-column checks for one nested-flag source33 -> helper644 map.

This checks physical adapters, not the complete correction schedule or bound.
Uses the existing NumPy runtime and pinned PR2226 Gaussian implementation.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np

import census

HERE = Path(__file__).resolve().parent
OPS = census.VENDOR / 'vendor/pr2226/operators.py'


def main():
    if not __debug__:
        raise RuntimeError('assertions must remain enabled')
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, default=HERE / 'FLAG-PAIR.json')
    args = ap.parse_args()
    receipt = census.read(census.STAGE / 'PR2339-SOURCE-RECEIPT.json')
    pin = next(x for x in receipt['files'] if x['vendor_path'] == 'vendor/pr2339/vendor/pr2226/operators.py')
    assert hashlib.sha256(OPS.read_bytes()).hexdigest() == pin['sha256']
    spec = importlib.util.spec_from_file_location('pinned_pr2226_operators', OPS)
    ops = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ops)
    data = census.read(HERE / 'CENSUS.json')
    h = 9
    S, T = [138], [30]
    U = [266, 138, 75, 30]
    F = [486, 65, 20, 10]
    a, b = list(S), list(T)
    for x in census.frame_basis(census.span(U)):
        if census.gf_rank(a + [x]) > len(a):
            a.append(x)
    for x in F:
        if census.gf_rank(b + [x]) > len(b):
            b.append(x)
    G = ops.change(a, b, h)
    E = [ops.linear(G, x) for x in U]
    assert census.span(E) == census.span(F)
    assert ops.linear(G, S[0]) == T[0]
    assert ops.change(U, E, h) == G
    recipe = ops.monomial(G, h)
    identity = lambda: (np.eye(1 << h, dtype=np.int64), np.zeros((1 << h, 1 << h), dtype=np.int64), 0)
    checks = []
    for label, source, target, sign in [
        ('entrance_line_read', S, T, 1),
        ('handoff', U, E, 1),
        ('full_inverse_cleanup', [1 << j for j in range(h)], [1 << j for j in range(h)], -1),
    ]:
        z = ops.frame(identity(), source, h, -1)
        z = ops.apply_mono(z, recipe, sign)
        z = ops.frame(z, target, h, 1)
        checks.append(dict(label=label, source_basis=source, target_basis=target,
                           sign=sign, gaussian_monomial_sha256=ops.check(z), columns=1 << h))
    controls = {}
    for label, bad_recipe in [('omitted_G', None), ('canonical_unflagged_G', ops.monomial(ops.change(U, F, h), h))]:
        z = ops.frame(identity(), S, h, -1)
        if bad_recipe is not None:
            z = ops.apply_mono(z, bad_recipe)
        z = ops.frame(z, T, h, 1)
        rejected = False
        try:
            ops.check(z)
        except AssertionError:
            rejected = True
        assert rejected
        controls[label] = 'REJECTED_NONMONOMIAL'
    pairs = []
    for case in data['cases']:
        original = case['repaired_candidates'][0]
        assert original['register'] == 33
        pair = dict(original['pair'], handoff_basis=E)
        pairs.append(dict(provider=case['provider'], baseline=case['baseline'],
                          pair=pair, restoration_gates=original['restoration_gates'],
                          operator=original['operator'], residual=original['residual']))
    out = dict(status='PASS_EXACT_FLAG_PRESERVING_SOURCE33_ADAPTERS',
               source_entrance=S, target_early_line=T, retirement_basis=U,
               first_helper_frame=F, handoff_basis=E, G_columns=G,
               checks=checks, negative_controls=controls, pairs=pairs,
               scope='Exact physical rank-zero entrance-line read, B handoff, FULL inverse cleanup. Four scalar-repaired diagnostic words retain an uncompensated residual. No correction chronology, complete profile, native admission, owner fill or exponent is certified here.',
               source_sha256={str(p.relative_to(HERE.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in [OPS, HERE / 'census.py', HERE / 'CENSUS.json', Path(__file__).resolve()]},
               source_head='bf1742aee4d855efb8bbd44a8419eddb33a679e5',
               attribution='Tekalign (@tekuuu), with substantial OpenAI Codex assistance; uses Cinna Davis PR2226 exact Gaussian checker, Sagar Thakrar PR2339 and Jeremy Kothe PR2269. Apache-2.0.')
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print(out['status'], '3 products x512 columns;2 negative controls;G', G, 'E', E)


if __name__ == '__main__':
    main()
