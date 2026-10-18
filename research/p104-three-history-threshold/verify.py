# SPDX-License-Identifier: Apache-2.0
"""Certify the changed-history boundary of P104's two-history lifetime screen."""

import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
# Resolve the sibling explicitly so isolated (-I) execution uses the same source.
SPEC = importlib.util.spec_from_file_location(
    'p104_binomial', PACKAGE / 'independent.py')
if SPEC is None or SPEC.loader is None:
    raise ValueError('independent checker loader')
INDEPENDENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INDEPENDENT)
independent_moment = INDEPENDENT.moment
SELECTED = Q(67018507072324140917, 40000000000000000000000)
BASE = {1: 1074, 2: 58, 3: 86, 4: 104, 5: 48, 6: 24, 7: 8, 8: 8}
CHEAP = (1, 7, 1)
UNIT = (1,) * 9
MERGED = (1, 1, 2, 1, 1, 1, 1, 1)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unique(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), 'duplicate JSON key')
    return result


def read_json(path):
    require(path.stat().st_size <= 200_000, 'JSON size bound')
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)


def sources():
    manifest = read_json(PACKAGE / 'SOURCES.json')
    records = [r for r in manifest['files'] if r['usage'] == 'input']
    records += manifest['external_sources']
    require(len(records) == 4, 'complete input inventory')
    for row in records:
        path = ROOT / row['path']
        require(path.stat().st_size <= 200_000, 'source size bound')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'],
                'source hash: ' + row['path'])
    spec = importlib.util.spec_from_file_location(
        'p104_authenticated_ceiling',
        ROOT / 'research/complex-local-word-ceiling/ceiling.py')
    require(spec is not None and spec.loader is not None, 'interval engine loader')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def history(jumps):
    require(isinstance(jumps, tuple) and 1 <= len(jumps) <= 9, 'history tuple')
    require(all(type(r) is int and 1 <= r <= 9 for r in jumps) and sum(jumps) == 9,
            'positive composition of nine')
    stops = [0]
    for rank in jumps:
        stops.append(stops[-1] + rank)
    cuts = []
    for k in range(1, 8):
        edges = zip(stops[:-1], stops[1:], strict=True)
        left, right = next((a, b) for a, b in edges if a <= k < b)
        cuts.append(0 if left == 0 or right == 9 else 2 ** (7 - right + left))
    arrival = stops[stops.index(8) - 1] if 8 in stops else 0
    departure = 9 - stops[stops.index(1) + 1] if 1 in stops else 0
    return cuts, arrival, departure


def endpoint_curve(receipt):
    """Reconstruct the credited saturated endpoint curve, not its geometry proof."""
    result = []
    for orientation in ('arrival', 'departure'):
        row = receipt['geometry'][orientation]
        types = row['endpoint_types']
        require(len(types) == 6 and sum(n for _, _, n in types) == 104,
                'endpoint types')
        require(all(0 < b < d <= 2 * b and n > 0 for d, b, n in types),
                'decreasing endpoint marginals')
        marginals = [v for d, b, n in types for _ in range(n) for v in (b, d - b)]
        curve = [sum(d * n for d, _, n in types)]
        for value in sorted(marginals, reverse=True):
            curve.append(curve[-1] - value)
        require(curve == row['minimum_cheap_by_units'], 'inherited endpoint curve')
        require(curve[0] == 4656 and curve[-1] == 0, 'complete endpoint demands')
        result.append(curve)
    require(result[0] == result[1], 'two orientation curves agree')
    return result[0]


def profile(counts):
    require(len(counts) == 3 and all(type(n) is int and n >= 0 for n in counts),
            'three nonnegative integer counts')
    require(sum(counts) <= 482, 'coverage lifetime bound')
    result = Counter(BASE)
    for jumps, count in zip((CHEAP, UNIT, MERGED), counts, strict=True):
        for rank in jumps:
            result[rank] += count
    return dict(sorted(result.items()))


def check_screen(counts, curve, forced):
    paid = profile(counts)
    cheap, units, merged = counts
    require(len(forced) == 7, 'seven cut demands')
    wide = units + merged
    require(cheap >= curve[min(wide, 208)], 'saturated endpoint demands')
    histories = [history(jumps) for jumps in (CHEAP, UNIT, MERGED)]
    cuts = [sum(n * h[0][k] for n, h in zip(counts, histories, strict=True))
            for k in range(7)]
    require(all(v >= d for v, d in zip(cuts, forced, strict=True)),
            'coupled cut demands')
    dimensions = [sum(n * h[k] for n, h in zip(counts, histories, strict=True))
                  for k in (1, 2)]
    require(min(dimensions) >= 832 and sum(counts) >= 208, 'endpoint spans and counts')
    mass = sum(r * n for r, n in paid.items())
    require(mass == 2368 + 9 * sum(counts), 'telescoping boundary rank mass')
    return {'counts': list(counts), 'cut_capacities': cuts,
            'endpoint_dimension_totals': dimensions,
            'local_profile': {str(r): n for r, n in paid.items()},
            'local_rank_mass': mass, 'idle_rank_mass': 6712 - mass}


def outward(interval):
    scale = 10 ** 15
    lo, hi = interval
    return [str(Q(lo.numerator * scale // lo.denominator, scale)),
            str(Q(-((-hi.numerator * scale) // hi.denominator), scale))]


def checked_moment(module, counts):
    primary = module.relax(profile(counts), 73, 832, 9, 56, SELECTED)
    independent = independent_moment(*counts, SELECTED)
    require(max(primary[0], independent[0]) <= min(primary[1], independent[1]),
            'independent binomial enclosure overlaps the logarithm enclosure')
    require(primary[1] - primary[0] < Q(1, 10**60), 'primary interval width')
    require(independent[1] - independent[0] < Q(1, 10**15),
            'independent interval width')
    return {'primary': outward(primary), 'independent': outward(independent)}


def candidates(floor, curve):
    require(type(floor) is int and 208 <= floor <= 482, 'floor domain')
    pairs = []
    for wide in range(483):
        cheap = max(curve[min(wide, 208)], floor - wide, 0)
        if cheap + wide <= 482:
            pairs.append((cheap, 0, wide))
    require(bool(pairs), 'nonempty minimal-cheap candidate set')
    return pairs


def optimum(module, floor, curve, forced):
    """All-unit-to-merged replacement is feasible for every endpoint-feasible pair."""
    constant = module.relax(profile((0, 0, 0)), 73, 832, 9, 56, SELECTED)
    single = [module.relax(profile(n), 73, 832, 9, 56, SELECTED)
              for n in ((1, 0, 0), (0, 0, 1))]
    prices = [(v[0] - constant[1], v[1] - constant[0]) for v in single]
    require(all(lo > 0 for lo, _ in prices), 'positive extra-helper prices')
    bounds = []
    for counts in candidates(floor, curve):
        check_screen(counts, curve, forced)
        c, _, m = counts
        bounds.append((constant[0] + c * prices[0][0] + m * prices[1][0],
                       constant[1] + c * prices[0][1] + m * prices[1][1], counts))
    best = min(bounds, key=lambda row: row[1])
    require(all(lo > best[1] for lo, _, counts in bounds if counts != best[2]),
            'certified unique three-history optimum')
    direct = module.relax(profile(best[2]), 73, 832, 9, 56, SELECTED)
    require(best[0] <= direct[0] <= direct[1] <= best[1],
            'direct price in affine bounds')
    return best[2], direct


def compute():
    module = sources()
    endpoints = read_json(ROOT / 'research/p104-endpoint-geometric-budget/RESULT.json')
    curve = endpoint_curve(endpoints)
    coupled = read_json(ROOT / 'research/p104-coupled-profile-budget/EXPECTED.json')
    forced = coupled['finite_premises']['forced']
    baseline = read_json(PACKAGE / 'inputs/PR2924-RESULT.json')['first_rejecting_floor']
    observed = baseline['cheap'], baseline['units'], baseline['lifetimes']
    require(observed == (232, 191, 423), 'predecessor two-history threshold')
    old = module.relax(profile((232, 191, 0)), 73, 832, 9, 56, SELECTED)
    require([str(v) for v in old] == baseline['selected_moment'] and old[0] > 1,
            'exact predecessor moment reproduced')
    require(history(UNIT)[1:] == history(MERGED)[1:] == (7, 7), 'endpoint signatures')
    # Check every member of the fixed-count fusion family, not only its winner.
    for merged in range(192):
        check_screen((232, 191 - merged, merged), curve, forced)
    cases = {}
    for merged in (0, 10, 11, 191):
        counts = (232, 191 - merged, merged)
        cases[str(merged)] = {**check_screen(counts, curve, forced),
                              'moment': checked_moment(module, counts)}
    require(independent_moment(232, 181, 10, SELECTED)[0] > 1,
            'ten fusions still reject')
    require(independent_moment(232, 180, 11, SELECTED)[1] < 1,
            'eleven fusions pass')
    rank_two = module.child_cost(2, 73, SELECTED)
    rank_one = module.child_cost(1, 73, SELECTED)
    require(rank_two[1] < 2 * rank_one[0], 'strictly cheaper merged history')
    minimum_cut = min(min(check_screen(c, curve, forced)['cut_capacities'])
                      for c in candidates(208, curve))
    optima = {}
    for floor in (423, 435, 436):
        counts, interval = optimum(module, floor, curve, forced)
        require((interval[1] < 1) if floor < 436 else (interval[0] > 1),
                'three-history threshold decision')
        optima[str(floor)] = {'counts': list(counts),
                              'moment': checked_moment(module, counts)}
    return {'forced_cut_demands': forced, 'endpoint_cheap_required_at_191': curve[191],
            'fusion_cases': cases, 'minimum_fusions_in_fixed_family': 11,
            'minimum_cut_over_endpoint_feasible_merged_profiles': minimum_cut,
            'optima': optima, 'first_rejecting_floor_in_three_history_screen': 436}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(json.dumps(result, sort_keys=True, indent=2))
        return
    require(json.dumps(result, sort_keys=True) ==
            json.dumps(read_json(PACKAGE / 'RESULT.json'), sort_keys=True),
            'complete typed receipt')
    print('PASS_P104_THREE_HISTORY_THRESHOLD minimum_fusions=11 '
          'two_history_floor=423 three_history_floor=436 no_new_kappa')


if __name__ == '__main__':
    main()
