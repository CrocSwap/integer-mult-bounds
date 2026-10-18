#!/usr/bin/env python3
"""Reproduce the source-bound all-dyadic X4 forest exclusion, offline."""
import argparse
import importlib.util
import json
from pathlib import Path
from fractions import Fraction as Q

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = '018418fd789ce12a8c176279fe012138713ff53d'


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


primary = module('dyadic_primary', 'census.py')
independent = module('dyadic_independent', 'independent.py')
require = primary.require


def source_pins():
    pins = json.loads((HERE / 'SOURCE-PINS.json').read_text(encoding='utf-8'))
    require(pins['base_commit'] == BASE, 'base pin')
    required = {
        primary.ARCHIVE,
        'certificates/checkpoints/frontier799.json',
        'research/gauge44-frames-x/construction/jx/LOCAL-PINS-jx-X4.json',
        'research/complex-x4-target-forest/PROOF.md',
        'research/complex-x4-target-forest/RECIPE.json',
        'research/complex-x4-target-forest/SOURCES.json',
        'research/complex-x4-scaled-pairs/PROOF.md',
        'research/complex-sw4-frame8/local/hpe_emit_local.py',
    }
    require(set(pins['files']) == required, 'source pin coverage')
    for name, digest in pins['files'].items():
        require(primary.sha((ROOT / name).read_bytes()) == digest, 'source pin: ' + name)
    require(pins['files'][primary.ARCHIVE] == primary.ARCHIVE_SHA, 'immutable archive pin')
    require(pins['canonical_word_sha256'] == primary.WORD_SHA, 'immutable word pin')
    return pins


def validate_census(result):
    require(result['ordered_pairs'] == 12432 and result['coefficients'] == 1086
            and result['cases'] == 13501152, 'finite coverage')
    expected = {(Q(tick, 8).numerator, Q(tick, 8).denominator)
                for tick in range(-543, 544) if tick}
    records = result['records']
    keys = [(row['numerator'], row['denominator']) for row in records]
    require(len(keys) == len(set(keys)) == 1086 and set(keys) == expected, 'coefficient coverage')
    for record in records:
        require(all(type(record[key]) is int for key in (
            'numerator', 'denominator', 'min_margin', 'max_margin', 'negative_edges',
            'zero_edges', 'min_dominance_margin', 'strict_improvement_dominance',
            'dominance_zero_edges')), 'typed certificate integer')
    nonunits = [row for row in records if abs(row['numerator']) != row['denominator']]
    require(all(row['min_dominance_margin'] > 0 and row['strict_improvement_dominance'] == 0
                and row['dominance_zero_edges'] == 0 for row in nonunits), 'nonunit dominance')
    require(min(row['min_dominance_margin'] for row in nonunits) == 56, 'finite minimum gap')
    require(sum(row['negative_edges'] for row in nonunits) == 970, 'root gains')
    require(sum(row['zero_edges'] for row in nonunits) == 34, 'root ties')
    require(result['unit_forest']['cost'] == 10883, 'unit forest floor')


def cycle_certificate(rows, forest):
    """Check every graph edge against its selected-tree path maximum."""
    tree = {vertex: [] for vertex in [-1, *rows]}
    for price, child, parent, sign in forest['edges']:
        if child == -1:
            actual = sum(primary.cost(Q(a, 4)) for a in rows[parent].values())
            require(sign == 0, 'root edge sign')
        else:
            require(sign in (-1, 1), 'unit edge sign')
            actual = 8 + sum(primary.cost(Q(rows[child].get(h, 0) - sign * rows[parent].get(h, 0), 4))
                             for h in rows[child].keys() | rows[parent].keys())
        require(price == actual, 'tree edge invoice')
        tree[child].append((parent, price)); tree[parent].append((child, price))
    require(len(forest['edges']) == 112, 'tree edge count')
    path_max = {}
    for start in tree:
        seen = {start: 0}; pending = [start]
        for vertex in pending:
            for other, price in tree[vertex]:
                if other not in seen:
                    seen[other] = max(seen[vertex], price); pending.append(other)
        require(len(seen) == 113, 'tree connectivity')
        path_max[start] = seen
    checked = 0
    for child in rows:
        price = sum(primary.cost(Q(a, 4)) for a in rows[child].values())
        require(price >= path_max[-1][child], 'root cycle inequality'); checked += 1
        for parent in rows:
            if parent >= child: continue
            for sign in (-1, 1):
                price = 8 + sum(primary.cost(Q(rows[child].get(h, 0) - sign * rows[parent].get(h, 0), 4))
                                for h in rows[child].keys() | rows[parent].keys())
                require(price >= path_max[child][parent], 'unit cycle inequality'); checked += 1
    require(checked == 12544, 'cycle coverage')
    return checked


def compare_independent(result, other):
    by_coefficient = {(r['numerator'], r['denominator']): r for r in other['coefficients']}
    require(len(by_coefficient) == len(other['coefficients']) == 1086, 'independent coverage')
    for row in result['records']:
        match = by_coefficient[row['numerator'], row['denominator']]
        require(primary.canonical(row) == primary.canonical({k: match[k] for k in row}),
                'independent coefficient mismatch')
    require(other['signed_unit_prim']['cost'] == result['unit_forest']['cost'], 'independent Prim floor')
    require(other['edge_count'] == result['cases'], 'independent edge coverage')


def run():
    source_pins()
    rows = primary.load()
    result = primary.census(rows)
    result['unit_forest'] = primary.signed_unit_floor(rows)
    validate_census(result)
    checked = cycle_certificate(rows, result['unit_forest'])
    targets, helpers, dense = independent.read_rows(ROOT / primary.ARCHIVE)
    other = independent.census(targets, dense)
    compare_independent(result, other)
    controls = independent.run_controls(targets, helpers, dense, other, 'complete')
    return result, {'independent_census_sha256': other['census_sha256'],
                    'independent_prim_floor': other['signed_unit_prim']['cost'],
                    'cycle_inequalities': checked, 'controls': controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-new', type=Path, help='Write regenerated certificate to a NEW path')
    parser.add_argument('--json', action='store_true', help='Print compact verification receipt')
    args = parser.parse_args()
    if args.write_new is not None:
        require(not args.write_new.exists(), 'output already exists')
    result, evidence = run()
    expected = json.loads((HERE / 'CERTIFICATE.json').read_text(encoding='utf-8'))
    require(primary.canonical(result) == primary.canonical(expected), 'committed certificate mismatch')
    if args.write_new is not None:
        with args.write_new.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(json.dumps(result, sort_keys=True, indent=2) + '\n')
    if args.json:
        print(json.dumps(evidence, sort_keys=True, indent=2))
    print('PASS_X4_DYADIC_FOREST coefficients=1086 ordered_pairs=12432 cases=13501152 '
          'nonunit_root_gains=970 dominating_units_or_roots=all floor=10883 no_new_kappa')


if __name__ == '__main__':
    main()
