# SPDX-License-Identifier: Apache-2.0
"""Check selected equality and malformed physical-domain controls."""
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('domain_guard', HERE / 'guard.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)
need = guard.need

def main():
    args = dict(local={1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8},
                m=73, families=896, stages=9, centre=64)
    checked = guard.ceiling(**args)
    expected = json.loads((guard.ROOT / 'research/complex-local-word-ceiling/RESULT.json').read_text())['ceiling']
    need(checked == (Q(expected['a_relaxation_achievable']), Q(expected['a_ceiling'])), 'selected bracket changed')
    raw = guard.implementation()
    negative_charge = raw.ceiling(**dict(args, centre=-1))
    need(negative_charge[0] > checked[1], 'invalid negative charge no longer reproduces a larger ceiling')
    bad = [dict(centre=-1), dict(centre=0.5), dict(centre=True), dict(grid=0),
           dict(grid=-Q(1, 10**15)), dict(grid=0.001), dict(grid=Q(1, 10)),
           dict(m=1), dict(m=True), dict(m=73.0), dict(families=0), dict(families=-1),
           dict(stages=0), dict(stages=-1), dict(stages=True), dict(unpaid=0),
           dict(unpaid=73), dict(unpaid=Q(3, 2)), dict(R=0), dict(R=-1), dict(R=52),
           dict(R=51.0), dict(local={1: -1}), dict(local={0: 1}), dict(local={73: 1}),
           dict(local={Q(3, 2): 1}), dict(local={1: True}), dict(local={1: 0.5}),
           dict(local={1: 100000})]
    for change in bad:
        try:
            guard.inputs(**dict(args, **change))
        except ValueError:
            pass
        else:
            raise ValueError('invalid input accepted: ' + repr(change))
    guard.inputs(**dict(args, local={1: Q(1, 2)}, centre=Q(1, 2)))
    guard.inputs(**dict(args, centre=0, R=48, unpaid=2))
    guard.inputs(**dict(args, local={}))
    print(json.dumps({'selected_bracket': list(map(str, checked)),
                      'raw_negative_centre_bracket': list(map(str, negative_charge)),
                      'malformed_controls_rejected': len(bad),
                      'status': 'PASS_COMPLEX_CEILING_DOMAIN_GUARD'}, indent=2))

if __name__ == '__main__':
    main()
