#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Price a balanced alternative, not the current capped-phase-fusion route.

Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
This arithmetic comparison neither admits nor rejects the current outer route.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import json
from pathlib import Path
import price

HERE = Path(__file__).resolve().parent
PINS = {
    'price.py': '76f6b7c9d8fdfbf3c86726e2c34f5a13129717511e04876494bda94979474a1a',
    'RESTRICTED-PROFILE.json': '479c54182b51f200402387ff9bb4b8d911f89615d701a64e76bd543a9dbfcff6',
    'EXACT-CAPACITY-WITNESSES.json': '45a4c4f4d7c91c581aec023f54946c8f4cbe28bbe60d59eb2653de289a4e07bc',
    '../PR2374-SPEC.json': '546c3bcf6fda7f7b5186f68756ce7b5bc139d5273923d75c7c5e4a375527810f',
    '../PR2374-OUTER-CLAIM.json': 'f3e40f917ad36e963b43adbcd2490f37211e863b9b68bdd83a6b1ad8a6169aae',
    '../PR2374-check_ledger.py': '9e12909c73d3b3a31a45d801ae76c034510d6306400412e474df79bc4f1dc67e',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    need(__debug__, 'Optimized Python unsupported by inherited exact engines')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    for name, pin in PINS.items():
        price.pin(HERE/name, pin)
    price.pin(price.OLD/'budget/verify_nine_capacity.py', price.PINS['budget/verify_nine_capacity.py'])
    v = price.load(price.OLD/'budget/verify_nine_capacity.py', 'balanced_cost')
    # This relation belongs to the alternative balanced assembly. The current
    # PR2374 capped-phase-fusion route instead has kappa=C-1/FLOOR-BACKOFF.
    rate = price.B/(1-price.B)
    profiles = {'restricted': {int(r):Q(n) for r,n in price.read(HERE/'RESTRICTED-PROFILE.json').items()}}
    witness = price.read(HERE/'EXACT-CAPACITY-WITNESSES.json')
    for provider in ('gauge44','extra'):
        label = provider+'/high48/aliases4/splits4'
        case = witness['capacity_witnesses'][label]
        profile = Counter({int(r):666*Q(n) for r,n in case['local_profile'].items()})
        profile.update({int(r):Q(n) for r,n in case['idle'].items()})
        profiles[label] = profile
    engines = {}
    for filename, pin in v.ENGINES.items():
        price.pin(v.INHERITED/filename, pin)
        engine = price.load(v.INHERITED/filename, 'balanced_'+filename[:-3])
        cost = {r:v.E(r,rate,engine) for profile in profiles.values() for r in profile}
        cases = {}
        for label, profile in profiles.items():
            lo = sum(n*cost[r][0] for r,n in profile.items())-23680
            hi = sum(n*cost[r][1] for r,n in profile.items())-23680
            need((lo>0) if label=='restricted' else (hi<0), 'unexpected alternative-budget sign')
            cases[label] = dict(excess_minus_deficit=v.iv(lo,hi), below_one=hi<0)
        engines[filename] = cases
    receipt = dict(
        status='PASS_ALTERNATIVE_BALANCED_RATE_ARITHMETIC_NOT_CURRENT_OUTER_ROUTE',
        comparison_kappa=str(price.B), alternative_primitive_rate=str(rate),
        alternative_relation='b = kappa/(1-kappa)',
        current_route=dict(source_pr=2374, head='5449da65da12bdfd94675dccc38731eaa91e93b6',
                           kappa='C - 1/FLOOR - BACKOFF', primitive_rate='C - R0'),
        engines=engines, pins=PINS, engine_pins=v.ENGINES,
        scope='An alternative balanced assembly only. Its positive literal-owner margin does not reject the current capped-phase-fusion route. The two favorable cases are fractional capacity witnesses, not complete geometric constructions. No current outer admission or new kappa is certified.')
    if args.out:
        args.out.write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['status'])


if __name__ == '__main__':
    main()
