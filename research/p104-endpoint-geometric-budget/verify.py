# SPDX-License-Identifier: Apache-2.0
"""Check separate endpoint geometric attainability and its two-history bill."""

import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

from geometry import pair_oracle, plane_cover, reconstruct, require, residuals

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = {1: 1074, 2: 58, 3: 86, 4: 104, 5: 48, 6: 24, 7: 8, 8: 8}
SELECTED = Q(67018507072324140917, 40000000000000000000000)
ROOT_LO, ROOT_HI = Q('0.002104152801941'), Q('0.002104152801942')
TYPES = [(36, 24, 12), (44, 28, 24), (45, 30, 8),
         (46, 29, 24), (47, 30, 24), (48, 30, 12)]


def unique(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), 'duplicate JSON key')
    return result


def read_json(path):
    require(path.stat().st_size <= 2_000_000, 'JSON size bound')
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)


def sources():
    manifest = read_json(PACKAGE / 'SOURCES.json')
    for record in manifest['files']:
        if record['usage'] != 'input':
            continue
        data = (ROOT / record['path']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == record['sha256'], 'input hash')
    return (read_json(ROOT / 'research/p104-native-channel/inputs/LOWRANK-WITNESS.json'),
            read_json(ROOT / 'research/p104-native-channel/inputs/P104-FIXTURE.json'))


def interval_module():
    spec = importlib.util.spec_from_file_location(
        'p104_ceiling', ROOT / 'research/complex-local-word-ceiling/ceiling.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def minimum_cheap(records):
    require(len(records) == 104, '104 endpoints')
    marginals = []
    for row in records:
        d, b = row['demand'], row['capacity']
        require(0 < b < d <= 2 * b, 'decreasing positive marginals')
        marginals.extend((b, d - b))
    marginals.sort(reverse=True)
    remaining = sum(row['demand'] for row in records)
    curve = [remaining]
    for marginal in marginals:
        remaining -= marginal
        curve.append(remaining)
    require(curve[-1] == 0, 'complete geometric coverage')
    return curve, min(marginals)


def geometry_receipt(witness, fixture):
    ports, paths, paid = reconstruct(witness, fixture)
    require(paid == BASE, 'whole original channel price')
    receipt, all_rows = {}, []
    for orientation, (sets, normals) in residuals(ports, paths).items():
        rows = []
        for points, normal in zip(sets, normals, strict=True):
            row = plane_cover(points, normal)
            require(pair_oracle(points, normal) == (row['capacity'], row['demand']),
                    'independent pair union optimum')
            rows.append(row)
        types = sorted((d, b, count) for (d, b), count in Counter(
            (r['demand'], r['capacity']) for r in rows).items())
        require(types == TYPES, 'predecessor endpoint types')
        curve, marginal = minimum_cheap(rows)
        require(sum(r['demand'] for r in rows) == 4656 and marginal == 12,
                'demand and smallest marginal')
        receipt[orientation] = {'endpoint_types': types, 'minimum_cheap_by_units': curve,
                                'minimum_positive_marginal': marginal}
        all_rows.append(rows)
    receipt['cover_witness_sha256'] = hashlib.sha256(
        json.dumps(all_rows, sort_keys=True).encode()).hexdigest()
    return receipt


def moment(module, cheap, units, a):
    require(type(cheap) is int and type(units) is int and min(cheap, units) >= 0,
            'nonnegative integer helper counts')
    require(cheap + units <= 482 and 0 <= a <= Q(1, 100), 'price domain')
    profile = BASE | {1: BASE[1] + 2 * cheap + 9 * units, 7: BASE[7] + cheap}
    return module.relax(profile, 73, 832, 9, 56, a)


def price_receipt(module, geometry):
    curve = geometry['arrival']['minimum_cheap_by_units']
    feasible = [(c, u) for u, c in enumerate(curve) if u + c <= 482]
    selected = moment(module, 0, 208, SELECTED)
    require(selected[1] < 1, 'selected optimistic price passes')
    # Independent finite price check supports the all-positive-a written proof.
    for c, u in feasible:
        if (c, u) != (0, 208):
            require(moment(module, c, u, SELECTED)[0] > selected[1],
                    'unique selected-price optimizer')
    below, above = moment(module, 0, 208, ROOT_LO), moment(module, 0, 208, ROOT_HI)
    require(below[1] < 1 < above[0], 'strict rational root bracket')
    return {'cheap': 0, 'units': 208, 'local_rank_mass': 4240, 'idle_rank_mass': 2472,
            'feasible_minimal_profiles': len(feasible),
            'selected_moment': [str(v) for v in selected],
            'root_bracket': [str(ROOT_LO), str(ROOT_HI)],
            'root_moments': [[str(v) for v in pair] for pair in (below, above)]}


def compute():
    witness, fixture = sources()
    geometry = geometry_receipt(witness, fixture)
    return {'geometry': geometry, 'price': price_receipt(interval_module(), geometry)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = compute()
    encoded = json.dumps(result, sort_keys=True, indent=2)
    if args.emit:
        print(encoded)
        return
    expected = json.dumps(read_json(PACKAGE / 'RESULT.json'), sort_keys=True, indent=2)
    require(encoded == expected, 'complete typed receipt')
    print('PASS_P104_ENDPOINT_GEOMETRIC_BUDGET endpoints=208 units=208 '
          'root=(0.002104152801941,0.002104152801942) no_new_kappa')


if __name__ == '__main__':
    main()
