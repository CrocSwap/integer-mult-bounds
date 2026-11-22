#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Check the pinned PR2374 endpoint-to-kappa identity, not its full theorem."""
import hashlib
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

if not __debug__:
    raise RuntimeError('assertions must remain enabled')
sys.set_int_max_str_digits(0)
HERE = Path(__file__).resolve().parent
PINS = {
    'PR2374-check_ledger.py': '9e12909c73d3b3a31a45d801ae76c034510d6306400412e474df79bc4f1dc67e',
    'PR2374-SPEC.json': '546c3bcf6fda7f7b5186f68756ce7b5bc139d5273923d75c7c5e4a375527810f',
    'PR2374-OUTER-CLAIM.json': 'f3e40f917ad36e963b43adbcd2490f37211e863b9b68bdd83a6b1ad8a6169aae',
}


def main():
    for name, expected in PINS.items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == expected, name
    spec = json.loads((HERE / 'PR2374-SPEC.json').read_text())
    claim = json.loads((HERE / 'PR2374-OUTER-CLAIM.json').read_text())
    C = Q(spec['expected']['complex_lower'])
    K = Q(claim['kappa'])
    assert K == Q(claim['kappa_rational'])
    D = spec['outer_refinement']['endpoint_digits']
    assert D == 3000
    R = Q(1, 10**(D+80))
    F = 10**(D+46)
    B = Q(1, 10**(D+22))
    b = C - R
    q = b - R
    eps = 1 - Q(1025, 1024)*R
    saving = eps*q
    derived = Q((saving*F).__floor__(), F)-B
    assert 0 < C-saving < Q(1, F)
    assert (C*F).denominator == 1
    assert derived == C-Q(1,F)-B == K
    # The historical b/(1+b) transfer is a different, strictly smaller value.
    assert b/(1+b) < K
    # Removing the backoff or the grid step does not reproduce the pinned claim.
    assert C-Q(1,F) != K
    assert C-B != K
    digest = hashlib.sha256(claim['kappa'].encode()).hexdigest()
    assert digest == 'b14d377d6aa465aafd8d8f23953a210763744fbc7a538fd378f89c48704885be'
    out = dict(
        status='PASS_PINNED_PR2374_EXACT_ENDPOINT_TRANSFER_IDENTITY',
        source_commit='5449da65da12bdfd94675dccc38731eaa91e93b6',
        source_package='research/gmx-t74-borrow43-handoff',
        pins=PINS, endpoint_digits=D, kappa_decimal_sha256=digest,
        identity='K = C - 10^-3046 - 10^-3022',
        supplier_parameters='b=C-10^-3080; q=C-2*10^-3080; epsilon=1-(1025/1024)*10^-3080',
        target_for_same_fixed_grid_transfer='C_new > K + 1/F_new + B_new; b_new=C_new-R_new',
        negative_controls=['historical b/(1+b) is strictly smaller', 'omitted backoff does not match', 'omitted grid step does not match'],
        scope='Exact arithmetic comparison identity only. Does not validate PR2374 supplier, all-size theorem, current accepted frontier, or any seed39 global/outer admission.')
    (HERE/'COMPARISON-TRANSFER-CHECK.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out['status'])


if __name__ == '__main__':
    main()
