#!/usr/bin/env python3
"""Optimistic ceiling for the frozen PR564 provider alphabet.

All actual local children are charged. Idle mass may be rearranged freely
into ranks at most 48, ignoring geometry and indivisible helper footprints.
This is an upper bound for that family, not a realizable construction.
"""

import importlib.util
import json
import os
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ENGINES = Path(os.environ.get('GAIN_PR564_SOURCE', ROOT / 'research/complex-allcold')).resolve() / 'engines'


def load(name):
    spec = importlib.util.spec_from_file_location(name, ENGINES / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def profile(promotions):
    counts = {1: 72 * 2301 + 2 * promotions,
              2: 72 * 442 - 2 * promotions,
              3: 72 * 470 - promotions,
              4: 72 * 184 + promotions, 5: 4032, 6: 4032, 8: 576}
    idle_mass = 520704 - sum(rank * count for rank, count in counts.items())
    full, remainder = divmod(idle_mass, 48)
    counts[48] = full
    if remainder:
        counts[remainder] = counts.get(remainder, 0) + 1
    assert sum(rank * count for rank, count in counts.items()) == 520704
    return counts, idle_mass


def main():
    moment = load("moment")
    independent = load("base_two_moment")
    baseline_kappa = Fraction("0.001593134158181640")
    results = {}
    for name, promotions in (("retained_15_2_55_mix", 448), ("all_eight_cold", 576)):
        counts, idle_mass = profile(promotions)
        certificate = moment.certify(counts, 73, 7168, False)
        lower, upper = map(Fraction, (certificate["lower"], certificate["upper"]))
        assert independent.moment(73, 7168, list(counts.items()), lower)[1] < 1
        assert independent.moment(73, 7168, list(counts.items()), upper)[0] > 1
        results[name] = dict(total_promotions=promotions, idle_mass=idle_mass,
                             relaxed_profile=counts, exact_moment=certificate,
                             kappa_ceiling_gain_percent=moment.decimal(
                                 100 * (upper / (1 + upper) / baseline_kappa - 1)))
    ceiling = Fraction(results["all_eight_cold"]["exact_moment"]["upper"])
    margins = []
    for promotions in range(0, 577, 4):
        counts, _ = profile(promotions)
        a = moment.moment(counts, 73, 7168, ceiling, False)[0] - 1
        b = independent.moment(73, 7168, list(counts.items()), ceiling)[0] - 1
        assert a > 0 and b > 0
        margins.append(min(a, b))
    receipt = dict(status="EXACT_OPTIMISTIC_CEILING_NOT_SUPPLIER_ADMISSION",
                   baseline_pr=564,
                   baseline_head="c18417b02b80594b2ca1c8c21185d28befafc935",
                   m=73, live=7168, physical=7682, calls=72,
                   helper_roles=36288, rank_mass=520704, deficit=2560,
                   variants_checked=145, results=results,
                   every_variant_rejected_at_common_upper=True,
                   minimum_exact_rejection_margin=str(min(margins)),
                   proof="For 0<alpha<1, moving rank mass from a smaller positive child "
                         "to a larger one decreases the power sum until the smaller is "
                         "zero or the larger reaches 48. Thus floor(S/48) full children "
                         "and S mod 48 give a lower bound on every legal idle bill. "
                         "All 72 local provider bills remain fully charged. Every "
                         "possible total promotion count 0,4,...,576 is rejected by "
                         "both rational engines at the common upper endpoint.",
                   scope="Fixed current cold 0/4/8 provider words, 72 complete calls, "
                         "m=73, W=7168, existing rank-at-most-48 pending factors, "
                         "native complex moment. Ignores owner windows and integer "
                         "helper packing; therefore no attainability is claimed. "
                         "New words, frames, cuts, decoder, alphabet or ambient "
                         "geometry are outside this ceiling.")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
