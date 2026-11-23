"""Check the changed signed profile and exercise real ordinary stage seams."""

from dataclasses import replace
from fractions import Fraction as Q
import json
from pathlib import Path
import sys

RUNTIME = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(RUNTIME))
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.append(str(HERE.parent / 'tiered-native-multiplier' / 'source'))
from upstream import install

install()
from check_stage_seam import verify_stage, verify_tape
from band_product import prepare_native
from installations import BINARY_C, ENTRY, GAUSSIAN_C, TERMINAL
from ordinary_carrier import stage_for_width_log
from outer_budget import qualify
from staged_carriers import entrance_logs

DEBIT = Q(130699669, 2**30)
ORDINARY_DEBIT = Q(11204, 8192)
G = Q(1, 10**18)
assert TERMINAL.rank_logs == (8192, 121057, 524288)
assert TERMINAL.complex_log == 496174
assert TERMINAL.kappa == Q('.003898221247474783')
assert max(*TERMINAL.rank_logs, TERMINAL.complex_log) == 524288

prior = replace(TERMINAL, rank_logs=(8192, 117168, 524288), complex_log=501831,
                kappa=Q('.003898219753506'))
prior_ceiling = Q(523210198560303585338978849681,
                  134217728000000000000000000000000)
assert TERMINAL.kappa > prior_ceiling > prior.kappa
old, new = prepare_native(prior), prepare_native(TERMINAL)
assert old[-1].targets is new[-1].targets and old[-1].cells is new[-1].cells
assert all(recipe.level_floor == 18960 for recipe in (*old[:-1], *new[:-1]))
assert all(a.targets is b.targets and a.paid is b.paid and a.cells is b.cells
           for a, b in zip(old[:-1], new[:-1], strict=True))

booked = Q(0)
for height in TERMINAL.rank_logs[:-1]:
    rate = min(TERMINAL.eta,
               (249 * (BINARY_C - ORDINARY_DEBIT / height) + booked) / 250)
    booked = Q((rate * 10**21).__floor__() - 1, 10**21)
ordinary = min(TERMINAL.eta,
               (249 * (BINARY_C - ORDINARY_DEBIT / TERMINAL.rank_logs[-1]) + booked) / 250)
positive = GAUSSIAN_C - DEBIT / TERMINAL.complex_log
assert TERMINAL.ordinary < min(ordinary, positive)
assert qualify(TERMINAL.kappa, G, TERMINAL.ordinary, positive)['strict'] == 54
assert 1731 + 320 * sum(TERMINAL.rank_logs) + 220 * TERMINAL.complex_log == 318291851
assert 318291851 < 318291911 < 318292011

def must_reject(kappa, positive_rate):
    try:
        qualify(kappa, G, kappa + 5*G, positive_rate)
    except ArithmeticError:
        return True
    raise AssertionError('an unfunded candidate was accepted')

# The old suffix debit cannot finance the new signed rate.  A rate above the
# new exact Gaussian limit also fails the inherited outer budget itself.
old_positive = GAUSSIAN_C - Q(64939, 524288*TERMINAL.complex_log)
assert must_reject(TERMINAL.kappa, old_positive)
assert TERMINAL.kappa + Q(2, 10**18) + 5*G > ordinary

cuts = tuple(entrance_logs(TERMINAL.rank_logs))
assert cuts == (8290, 129411, 653763)
for i, cut in enumerate(cuts, 1):
    assert [stage_for_width_log(cut+d, 3, TERMINAL.rank_logs) for d in (-1, 0, 1)] == [i-1, i, i]
    assert stage_for_width_log(cut+1, i-1, TERMINAL.rank_logs) == i-1
direct = [verify_stage(TERMINAL, cuts, 2, 140000), verify_stage(TERMINAL, cuts, 3, 670000)]
compiled = [verify_stage(TERMINAL, cuts, 2, 1100000), verify_stage(TERMINAL, cuts, 3, 4400000)]
assert all(s['direct'] for s in direct) and not any(s['direct'] for s in compiled)
tape = [verify_tape(1, [0,1], [2,1]), verify_tape(2, [1,7], [3,1])]
print('PASS_COMBINED_SIGNED_SEAMS', json.dumps({
    'prior_booked': str(prior.kappa), 'prior_stopped_ceiling': str(prior_ceiling),
    'candidate': str(TERMINAL.kappa), 'ordinary_upper': str(ordinary),
    'gaussian_upper': str(positive), 'ordinary_slack': str(ordinary-TERMINAL.ordinary),
    'gaussian_slack': str(positive-TERMINAL.ordinary),
    'prior_debit_rejected': True, 'overbooked_ordinary_rate_rejected': True,
    'cuts': cuts, 'direct': direct, 'compiled': compiled, 'signed_tape': tape,
}, sort_keys=True))
