#!/usr/bin/env python3
"""Offline verification of the rungs 3 and 4 ledgers, their prices and their assemblies.

Read-only unless `--write`: pins every vendored byte, rebuilds the whole complex-side ladder
(base, rung 2, rungs 3 and 4), both paid moments per rung, the two 47-constraint assemblies,
the PR208-convention replica and the eligibility scan, and compares the result with
`certificate.json`.

    python3 -B verify.py           # check
    python3 -B verify.py --write   # authoring: regenerate certificate.json and SOURCE.json

The complex-side bank construction obligations (C1-C7 and T1 in `obligations.json`, plus the
inherited R1-R4 of #219) are checked for presence and are **not** discharged here; the
certificate's scope says so literally.  Passing this script means the accounting is
consistent and the prices are exact -- not that the rung is physical.
"""
import argparse
import json
import sys
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

import pins  # noqa: E402
import run3  # noqa: E402
import schedule66  # noqa: E402

WIDTH = 66


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def read_manifest():
    return json.loads((HERE / 'SOURCE.json').read_text())['files']


def check_manifest():
    actual = pins.manifest()
    assert actual == read_manifest(), 'pinned input bytes changed'
    return actual


def check_schedule():
    """T1's enumeration: the pinned scan must equal a fresh one, findings and all."""
    pinned = json.loads((HERE / 'schedule66.json').read_text())
    fresh = json.loads(json.dumps(schedule66.tiling(), default=str))
    assert pinned == fresh, 'schedule66.json differs from a fresh enumeration'
    families = pinned['families']
    assert pinned['width'] == 66 and pinned['copies'] == 3, 'the scan must be width 66'
    assert families['11']['priced_banks'] == families['11']['capacity_minimum_banks'] == 531
    for family in ('16', '20'):
        entry = families[family]
        assert entry['whole_bank_volume'], 'the family must fill whole banks by volume'
        assert entry['priced_banks'] < entry['capacity_minimum_banks'], \
            'the priced bank count must fall below the capacity bound'
        assert not entry['fits_the_priced_banks'], 'and the priced count must not fit'
    assert pinned['findings']['mixed_uniform_tilings'] == 0
    assert all(not pinned['subsets'][key]['admissible']
               for key in ('11,16', '11,20', '16,20', '11,16,20')), \
        'no mixed subset may admit a uniform tiling'
    return pinned


def check_prototype(record):
    """The padded schedule's own invariants, as rebuilt into the certificate."""
    padded = record['padded_schedule']
    assert padded['width'] == 66 and padded['copies'] == 3, 'the prototype is width 66'
    assert [step['family'] for step in padded['ladder']] == [11, 16, 20], 'rung order'
    assert [step['banks'] for step in padded['ladder']] == [531, 198, 66], \
        'the prototype must use the capacity minimum, not the volume criterion'
    assert [step['padding_per_bank'] for step in padded['ladder']] == [0, 2, 6], \
        'the padding of T1'
    for step in padded['ladder']:
        assert step['pattern_sum'] == 66, 'every bank must be exactly filled'
        assert step['blocks_per_bank'] * step['banks'] == step['items'], \
            'the schedule must be saturated'
        assert step['stock_drop'] == step['banks'], \
            'the stock must fall by exactly the bank count'
        assert step['family'] == 11 or step['padding_registers'] % step['banks'] == 0
        assert step['eligibility_after'] in ([16, 20], [20], []), 'the ladder climbs'
    assert padded['exhaustive'] and padded['residual_eligibility'] == [], \
        'the whole-bank criterion must be exhausted at the padded top'
    assert Q(record['top']['kappa']) > Q(record['comparison']['volume_criterion_top']), \
        'the padded schedule must beat the volume-criterion accounting it replaces'
    assert record['top']['banks'] == 795, '531 + 198 + 66 banks, the padded schedule'
    return padded


def check_scan_and_construction(record):
    """The width scan and the instanced schedule, as rebuilt into the certificate."""
    scan = record['width_scan']
    pinned = scan[str(WIDTH)]
    assert pinned['priced'] and Q(pinned['kappa']) == Q(record['top']['kappa']), \
        'the scan must reproduce the top at the pinned width'
    assert pinned['banks'] == record['top']['banks'], 'and its bank count'
    for width, entry in scan.items():
        if not entry['poseable']:
            assert int(width) < WIDTH, 'only narrower moduli may be unposeable'
            assert Q(entry['density']) >= 1, 'an unposeable row has rank mass >= W * w'
        elif int(width) != WIDTH:
            assert not entry['priced'], 'a different modulus is a different word'
        else:
            assert entry['priced'], 'the pinned width must be priced'
    assert min(int(w) for w, e in scan.items() if e['poseable']) == WIDTH, \
        'the pinned width must be the smallest poseable modulus'

    construction = record['construction']
    totals = construction['totals']
    assert totals['banks'] == record['top']['banks'] == 795, '795 banks addressed'
    items = 0
    for family, inv in construction['inventories'].items():
        assert inv['banks'] * inv['capacity_per_bank'] == inv['items'], 'saturated'
        assert inv['banks'] * 66 \
            == inv['items'] * int(family) + inv['padding_registers'], 'banks exactly filled'
        assert inv['padding_registers'] == inv['banks'] * inv['padding_per_bank']
        assert len(inv['bank_table_digest']) == 64, 'a digest per family'
        items += inv['items']
    assert items == totals['items'] == 4176, '4,176 items addressed'
    assert totals['padding_registers'] == 792, '792 registers of padding, as in the schedule'
    assert construction['pins_gap']['complex_supplier_bank_keys'] == []
    assert construction['pins_gap']['complex_supplier_status_says_no_operation_program']
    assert construction['pins_gap']['pinned_item_inventory']['per_vertex_keys'], \
        'the shape the complex side owes must be recorded from the pinned bit inventory'
    assert construction['ledger_cross_check']['stock_drops'] == [531, 198, 66]
    assert construction['ledger_cross_check']['criterion_exhausted']
    return scan, construction


def check_suppliers_and_requirements(record):
    """The two density measurements and the inverted targets, rebuilt from the record.

    Everything here is re-derived from the certificate's own numbers with the package's own
    assembly rule: the ceiling the pinned bit leaf allows, each target's minimal budget, the
    one-grid-step miss below it, the required complex coarse saving clearing that budget after
    the beta and weak haircuts, and the two calibrations of the density curve.
    """
    GRID = run3.GRID
    top = Q(record['kappa'])
    leaf = Q(record['calibrations']['run1']['bit_leaf'])
    ceiling = Q(record['weighted_ceiling']['kappa_suppliers_admit_today'])
    assert ceiling == run3.kappa_of_budget(leaf), \
        'the complex-side ceiling must be the budget the pinned bit leaf allows'
    assert ceiling > top, 'and it must sit above this certificate\'s top'
    assert Q(record['weighted_ceiling']['gain_vs_top']) == ceiling / top - 1

    lines = record['bit_requirement']
    assert [line['target'] for line in lines] == ['9/12500', '3/4000', '1/1250', '1/1000'], \
        'the targets are 7.2e-4, 7.5e-4, 8e-4 and 1e-3'
    for line in lines:
        target, budget = Q(line['target']), Q(line['required_budget'])
        assert line['required_bit_leaf'] == line['required_budget'], \
            'the required budget is read off the bit leaf'
        assert run3.kappa_of_budget(budget) >= target > run3.kappa_of_budget(budget - Q(1, GRID)), \
            'the required budget must be the minimal grid point reaching the target'
        coarse = Q(line['required_complex_coarse_saving'])
        assert (1 - run3.BETA) * coarse - run3.WEAK > budget, \
            'the complex cap must clear the budget, not merely meet it'
        selected, _bound, kappa = run3.frontier_kappa(budget, coarse)
        assert selected == budget and kappa >= target, \
            'the pair (budget, coarse) must reach the target'
        assert Q(line['bit_leaf_now']) == leaf and Q(line['complex_coarse_now']) \
            == Q(record['top']['coarse']), 'the two branches must be the certified ones'
        assert line['bit_branch_short'] == (budget > leaf), 'bit-branch reading'
        assert line['complex_branch_short'] == (coarse > Q(record['top']['coarse'])), \
            'complex-branch reading'
        assert Q(line['bit_leaf_gain']) == budget / leaf - 1
    assert not lines[0]['bit_branch_short'] and lines[0]['complex_branch_short'], \
        '7.2e-4 needs more complex supply only'
    assert all(line['bit_branch_short'] and line['complex_branch_short'] for line in lines[1:]), \
        'the three higher targets are short on both branches, the bit word included'
    for need, line in zip(record['needed_for'], lines):
        if need['needs_new_bit']:
            assert need['required_bit_leaf'] == line['required_bit_leaf'], \
                'the two inversions of the same target must agree'
            assert Q(line['kappa_at_the_bit_ceiling_now']) < Q(line['target']), \
                'the pinned bit leaf must not already reach a target that needs a new word'

    measured = record['supplier_density']
    scan = measured['corpus']
    assert scan['profiles_scanned'] >= 10, 'the corpus scan must find the pinned ledgers'
    assert scan['below_pinned_count'] == 0, \
        'no poseable ledger may be less dense than the word priced here'
    assert Q(scan['least_dense_overall']['density']) == Q(measured['pinned_density']), \
        'the least dense poseable ledger in the repository must be this word itself'
    curve = {entry['modulus']: entry for entry in measured['curve']}
    assert curve[66]['priced'] and Q(curve[66]['kappa']) == top, \
        'the curve must reproduce the top at the pinned width'
    assert Q(curve[66]['stock_min']) == 12052, \
        'and require exactly the stock the pinned ledger carries'
    for width in (48, 54, 60):
        entry = curve[width]
        if entry['priced']:
            assert Q(entry['kappa']) == ceiling, \
                'that narrow a word stops binding on the complex side'
            assert Q(entry['saving']) > Q(record['calibrations']['run1']['complex_coarse'])
    assert not curve[72]['priced'], 'the pinned width must not tile after the ladder'
    assert all(Q(entry['kappa']) < top for entry in measured['curve']
               if entry['priced'] and entry['modulus'] > 66), 'a wider word must be worse'
    return ceiling, scan, curve


def check_obligations():
    obligations = json.loads((HERE / 'obligations.json').read_text())
    owed = [item['id'] for item in obligations['obligations']]
    assert owed == ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'T1'], owed
    status = {item['id']: item['status'] for item in obligations['obligations']}
    assert all(status[key] == 'OPEN' for key in ('C1', 'C2', 'C3', 'C4')), \
        'the physical obligations must still be open'
    assert status['T1'] == 'SETTLED_AT_SCHEDULE_LEVEL', \
        "T1 is settled by the schedule prototype, and must be recorded as such"
    assert all(status[key] == 'INVENTORY_INSTANCED_AT_SCHEDULE_LEVEL'
               for key in ('C5', 'C6', 'C7')), \
        'the inventories are instanced at the schedule level and must say so'
    t1 = next(item for item in obligations['obligations'] if item['id'] == 'T1')
    assert 'resolution' in t1 and 'prototype66' in t1['resolution'], \
        'T1 must name the artifact that settles it'
    inherited = [item['id'] for item in obligations['inherited']]
    assert inherited == ['R1', 'R2', 'R3', 'R4'], inherited
    assert all(item['status'] == 'OPEN' for item in obligations['inherited'])
    vendored = json.loads((HERE / 'references' / 'pr219-run1' / 'obligations.json').read_text())
    assert [item['id'] for item in vendored['obligations']] == inherited, \
        "the inherited obligation set must be #219's own"
    certificate = json.loads((HERE / 'certificate.json').read_text()) \
        if (HERE / 'certificate.json').exists() else {}
    if certificate:
        assert certificate['obligations'] == owed + inherited, 'certificate obligation list'
        assert not any('bank' in key for key in certificate['blocked_on']
                       ['complex_supplier_has_bank_keys']), \
            'the complex supplier must still have no bank keys'
    return owed + inherited


def check_unconditionality():
    """The pinned bytes' own verdict on unconditionality, read back rather than asserted.

    The record in `obligations.json` quotes four strings from the pinned files. This reads the
    files and matches the quotes, so the package's claim about what is and is not reachable is
    a checked fact about the pins: the supplier is published as a conditional finite witness,
    the operation program the normalizer needs is declared not exported, the literal program is
    a downstream integration task, and the vendored package states the house convention that
    discharging its obligations is not an unconditional multiplication theorem.
    """
    vendored = HERE / 'references' / 'pr219-run1'
    supplier = json.loads((vendored / 'references'
                           / 'pr193-source-assisted-v4.certificate.json').read_text())
    readings = {
        'references/pr219-run1/references/pr193-source-assisted-v4.certificate.json#status':
            supplier['status'],
        'references/pr219-run1/references/pr193-source-assisted-v4.certificate.json'
        '#complex_profile.status': supplier['complex_profile']['status'],
        'references/pr219-run1/references/pr193-source-assisted-v4.certificate.json'
        '#assembly.construction_receipts.status':
            supplier['assembly']['construction_receipts']['status'],
        'references/pr219-run1/obligations.json#claim_scope':
            json.loads((vendored / 'obligations.json').read_text())['claim_scope'],
    }
    assert readings[list(readings)[0]] == 'PASS conditional finite witness', \
        'the complex supplier must be published as a conditional finite witness'
    assert 'not exported' in readings[list(readings)[1]], \
        'the operation program must still be declared not exported'
    assert 'downstream integration task' in readings[list(readings)[2]], \
        'the literal program must still be a downstream task'
    assert 'not an unconditional multiplication theorem' in readings[list(readings)[3]], \
        'the house convention must still be stated by the vendored package'
    block = json.loads((HERE / 'obligations.json').read_text())['unconditionality']
    recorded = {row['source'] + '#' + row['path']: row['value']
                for row in block['evidence']}
    assert len(block['evidence']) == 4 and len(recorded) == 4, 'one row per reading'
    for key, value in readings.items():
        assert key in recorded, 'the record must name every pinned reading: %s' % key
        quoted = recorded[key]
        if quoted.startswith('...'):                    # a quoted tail of a long string
            assert value.endswith(quoted[3:]), 'the recorded tail must be the pinned tail'
        else:
            assert value == quoted, 'the recorded value must be the pinned value: %s' % key
    needs = block['what_each_item_needs']
    assert sorted(needs) == ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7',
                             'R1', 'R2', 'R3', 'R4'], 'all eleven items must be named'
    return block


def resolve(node, keys):
    """Walk a citation's key list through a pinned JSON document."""
    for key in keys:
        node = node[key]
    return node


def check_export_contract():
    """The normalizer export contract, resolved against the pinned bytes.

    The contract's whole point is that its citations are real: every digest, count and status it
    quotes from the supplier is read back out of the pinned file and compared, the precedent
    values are read back out of the pinned banked word and inventory, and the state it declares
    -- 0 of 6 bodies exported -- is asserted rather than described.
    """
    contract = json.loads((HERE / 'export-contract.json').read_text())
    cache = {}

    def pinned(source):
        if source not in cache:
            cache[source] = json.loads((HERE / source).read_text())
        return cache[source]

    def check(citations, where):
        for row in citations:
            found = resolve(pinned(row['source']), row['keys'])
            assert found == row['value'], \
                '%s: %s -> %s is %r, contract records %r' % (where, row['source'],
                                                            row['keys'], found, row['value'])

    assert contract['version'] == 1 and contract['scope'], 'the contract must state its scope'
    check(contract['precedent']['banked_word_export_shape']['citations'], 'precedent/banked word')
    check(contract['precedent']['occurrence_inventory_shape']['citations'], 'precedent/inventory')
    check(contract['precedent']['exact_object_disclaimer']['citations'], 'precedent/disclaimer')
    check(contract['today']['evidence'], 'today/evidence')

    supplier = pinned('references/pr219-run1/references/pr193-source-assisted-v4.certificate.json')
    assert supplier['status'] == 'PASS conditional finite witness'
    assert 'not exported' in supplier['complex_profile']['status']
    assert contract['today']['bodies_present'] == 0, \
        'no body export exists in the pins and the contract must say so'
    assert contract['today']['of_required'] == len(contract['required_exports']) == 6, \
        '0 of the six required bodies'

    tests = {test['id'] for test in contract['acceptance_tests']}
    assert tests == {'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7'}, 'the seven acceptance tests'
    for export in contract['required_exports']:
        assert export['id'] in ('E1', 'E2', 'E3', 'E4', 'E5', 'E6'), export['id']
        assert export['publishes'] and export['form'] and export['cardinality'], export['id']
        assert export['unblocks'], 'every export must unblock something'
        assert set(export['acceptance']) <= tests, 'the acceptance tests must exist: %s' % export['id']
        check(export['must_reproduce'], 'export/' + export['id'])
    assert len({export['id'] for export in contract['required_exports']}) == 6, 'unique ids'

    mapping = contract['obligation_mapping']
    assert sorted(mapping) == ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7',
                               'R1', 'R2', 'R3', 'R4'], 'all eleven obligations mapped'
    assert all(mapping[key] for key in mapping), 'no obligation may map to nothing'
    exports = {export['id'] for export in contract['required_exports']}
    for key, value in mapping.items():
        assert set(value) <= exports, '%s must map to required exports' % key
    assert contract['failure_semantics']['today'].startswith('0 of 6')
    assert 'never' in contract['failure_semantics'] and contract['not_required'], \
        'the contract must say what it does not ask for, and what it can never buy'
    for test in contract['acceptance_tests']:
        assert test['bound'] and test['reject_control'], \
            'every test needs a bound and a reject control: %s' % test['id']
    return contract


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--write', action='store_true',
                        help='authoring: regenerate certificate.json and SOURCE.json')
    args = parser.parse_args()
    assert not sys.flags.optimize, 'assertions must stay enabled'

    if not args.write:
        check_manifest()
    check_schedule()
    record = run3.build()
    check_prototype(record)
    check_scan_and_construction(record)
    ceiling, scan, curve = check_suppliers_and_requirements(record)
    check_obligations()
    unconditionality = check_unconditionality()
    contract = check_export_contract()
    target = HERE / 'certificate.json'
    if args.write:
        (HERE / 'SOURCE.json').write_text(
            json.dumps({'files': pins.manifest()}, indent=1, sort_keys=True) + '\n',
            newline='\n')
        target.write_text(json.dumps(record, indent=1, sort_keys=True, default=str) + '\n',
                          newline='\n')
        print('wrote certificate.json and SOURCE.json')
        return
    read = json.loads(target.read_text())
    assert read == json.loads(json.dumps(record, default=str)), 'certificate.json differs'
    print('certificate.json matches a fresh rebuild')
    print('tiling        rank 16 and rank 20 price %s and %s banks where their capacity '
          'requires %s and %s; mixed uniform tilings: %d'
          % (record['tiling']['families']['16']['priced_banks'],
             record['tiling']['families']['20']['priced_banks'],
             record['tiling']['families']['16']['capacity_minimum_banks'],
             record['tiling']['families']['20']['capacity_minimum_banks'],
             record['tiling']['findings']['mixed_uniform_tilings']))
    print('prototype     padded schedule %s banks (%s + %s + %s), padding %s per bank, '
          'stock drops %s'
          % (record['top']['banks'], *[step['banks']
                                       for step in record['padded_schedule']['ladder']],
             [step['padding_per_bank'] for step in record['padded_schedule']['ladder']],
             [step['stock_drop'] for step in record['padded_schedule']['ladder']]))
    print('widths        unposeable at %s; priced: %s; the modulus is the word'
          % (sorted(int(w) for w, e in record['width_scan'].items() if not e['poseable']),
             sorted(int(w) for w, e in record['width_scan'].items() if e['priced'])))
    print('instanced     %d items addressed over %d banks, %d registers of padding'
          % (record['construction']['totals']['items'],
             record['construction']['totals']['banks'],
             record['construction']['totals']['padding_registers']))
    print('export contract %d exports (%s), %d acceptance tests, bodies exported today: %d/%d'
          % (len(contract['required_exports']),
             ','.join(export['id'] for export in contract['required_exports']),
             len(contract['acceptance_tests']), contract['today']['bodies_present'],
             contract['today']['of_required']))
    print('unconditional not available: supplier status %s; operation program not exported; %s'
          % (json.loads((HERE / 'references' / 'pr219-run1' / 'references'
                         / 'pr193-source-assisted-v4.certificate.json').read_text())['status'],
             unconditionality['status']))
    print('rungs %s at %s banks, kappa %s'
          % (record['top']['families_absorbed'], record['top']['banks'], record['kappa']))
    print('suppliers     %d poseable ledgers scored, %d below the pinned density %s; least '
          'dense overall: %d wide at %.5f'
          % (scan['profiles_scanned'], scan['below_pinned_count'],
             Q(record['supplier_density']['pinned_density']),
             scan['least_dense_overall']['m'], scan['least_dense_overall']['density_decimal']))
    print('density curve %s'
          % ', '.join('w%d %s' % (entry['modulus'],
                                  (Q(entry['kappa']) if entry['priced'] else entry['status']))
                      for entry in record['supplier_density']['curve']))
    print('ceiling       a width 48-60 word with this shape pays %s; every target above 7.2e-4 '
          'still needs the bit word'
          % ceiling)
    for line in record['bit_requirement']:
        print('target %-8s bit leaf %-20s (%+.3f%%), complex coarse %-20s (%+.3f%% over the top)'
              % (line['target'], line['required_bit_leaf'], float(Q(line['bit_leaf_gain'])) * 100,
                 line['required_complex_coarse_saving'],
                 float(Q(line['complex_coarse_gain_vs_ladder_top'])) * 100))


if __name__ == '__main__':
    main()
