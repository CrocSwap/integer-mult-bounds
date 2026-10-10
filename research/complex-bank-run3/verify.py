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
import itertools
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

import bitinstance  # noqa: E402
import bitrung  # noqa: E402
import importer66  # noqa: E402
import instantiate_rank3  # noqa: E402
import pins  # noqa: E402
import rank3contract  # noqa: E402
import rank3stability  # noqa: E402
import rank4rung  # noqa: E402
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


def check_bit_instancing():
    """B1's schedule half: the item maps, the bank tables, the padding draw and the gap.

    The whole instancing is rebuilt and compared with `occurrences-bitrung.json`, and the parts a
    reviewer would check by hand are then re-derived from the artifact with plain arithmetic: the
    addressing rule as a bijection onto bank x block x offset, **both digests recomputed from the
    rule rather than trusted**, the padding as a partial removal from the retained singleton bin
    with the leftover the measured rung holds, and the induced ledger against the row
    `check_bit_rung` prices -- so the two modules cannot disagree about the same rung. What the
    pins do not export is asserted to still be absent, which is what keeps B1's provenance half
    open on paper and not by convention.
    """
    stored = json.loads((HERE / 'occurrences-bitrung.json').read_text())
    fresh = json.loads(json.dumps(bitinstance.build(), default=str))
    assert stored == fresh, 'occurrences-bitrung.json differs from a fresh instantiation'

    row = bitinstance.retained_row()
    assert row == bitinstance.vendored_retained_row(), 'the retained row, both readings of it'
    retained = stored['retained_row']
    assert (retained['W'], retained['deficit'], retained['rank_mass']) \
        == (row['W'], row['deficit'], row['mass']) == (50286, 5808, 3614784), \
        'the ledger this rung absorbs from'
    assert retained['children'] == sum(row['histogram'].values()) == 857622 \
        and retained['families'] == len(row['histogram']) == 21

    draws = {int(key): draw for key, draw in stored['padding']['draws'].items()}
    padding_total = 0
    for key, table in sorted(stored['inventories'].items(), key=lambda entry: int(entry[0])):
        rank, children = int(key), row['histogram'][int(key)]
        capacity, padding = 72 // rank, 72 % rank
        assert table['children_per_vertex'] == children // 3, 'rank %d per vertex' % rank
        assert table['copies'] == 3 and table['items'] == children, 'rank %d items' % rank
        assert (table['capacity_per_bank'], table['padding_per_bank']) == (capacity, padding) \
            and children % capacity == 0 and table['banks'] == children // capacity, \
            'rank %d: the schedule a bank admits' % rank
        addresses = [(item, item // capacity, item % capacity, (item % capacity) * rank)
                     for item in range(children)]
        assert len({(bank, block) for _, bank, block, _ in addresses}) == children \
            and all(offset + rank <= 72 for _, _, _, offset in addresses), \
            'rank %d: bank i // k, block i %% k, offset (i %% k) * rank is a bijection' % rank
        digest = sha256('\n'.join('%d,%d,%d,%d' % address
                                  for address in addresses).encode()).hexdigest()
        assert digest == table['bank_table_digest'], 'rank %d: the table digest' % rank
        draw = draws[rank]
        assert draw['banks'] == table['banks'] \
            and draw['padding_registers_per_bank'] == padding \
            and draw['registers'] == table['banks'] * padding, 'rank %d padding draw' % rank
        assert draw['singleton_bin_before'] == row['histogram'][1] == 377316 \
            and draw['singleton_bin_after'] == 377316 - draw['registers'], 'the bin it comes from'
        assert draw['digest'] == sha256('\n'.join(str(index)
                                                  for index in range(draw['registers']))
                                        .encode()).hexdigest(), 'rank %d draw digest' % rank
        if padding:
            assert draw['last_index'] == draw['registers'] - 1 \
                and draw['first_bank']['offsets'] == [72 - padding + j for j in range(padding)] \
                and draw['first_bank']['items'] == list(range(padding)), \
                'rank %d: the draw is named, per bank, at the tail of each bank' % rank
        padding_total += draw['registers']
    assert padding_total == stored['totals']['padding_registers'] == 65808 \
        and stored['padding']['singleton_after'] == 377316 - padding_total == 311508, \
        'the whole draw, and what the measured rung keeps'
    assert stored['totals']['banks'] == 7342 and stored['totals']['items'] == 35622 \
        and stored['totals']['blocks'] == 35622, 'the rung: one item per block'

    ledger = stored['induced_ledger']
    assert (ledger['stock_after'], ledger['mass_after'], ledger['children_after'],
            ledger['families_after'], ledger['singleton_after']) \
        == (42944, 3086160, 756192, 18, 311508), 'the row the assignment induces'
    assert ledger['stock_drop'] == stored['totals']['banks'] == 7342 \
        and ledger['mass_before'] - ledger['mass_after'] == 7342 * 72, \
        'the stock falls by the bank count, the mass by 72 registers a bank'
    rung = json.loads((HERE / 'bitrung.json').read_text())
    schedule = rung['leader_schedule']
    assert list(bitinstance.RUNGS) == rung['leader']['ranks'] == [7, 8, 20], 'the same rung'
    assert (schedule['retained_W'], schedule['retained_mass'], schedule['retained_children'],
            schedule['retained_families']) == (ledger['stock_after'], ledger['mass_after'],
                                               ledger['children_after'],
                                               ledger['families_after']), \
        'the ledger this instancing induces must be the row check_bit_rung prices'
    histogram = {int(rank): count for rank, count in schedule['retained_histogram'].items()}
    assert histogram == {entry['family']: entry['children']
                         for entry in stored['remaining_families']}, 'and its histogram'
    assert ledger['histogram_digest'] == bitinstance.histogram_digest(histogram), \
        'and the digest of that histogram'

    gap = stored['pins_gap']
    assert gap['packed_certificate_block_keys'] == [] \
        and gap['packed_certificate_occurrence_keys'] == [] \
        and gap['bit_certificate_occurrence_keys'] == [], \
        'the pins must still export no block and no occurrence of this word'
    assert gap['packed_certificate_assignment_keys'] \
        == ['/physical/conflicting_assignment_rejected'], \
        "the only key the packed certificate carries that says 'assign' is its own rejection "\
        'control, not an item assignment: the map instanced here has no counterpart in the pins'
    assert gap['pinned_item_inventory']['per_vertex_keys'] == ['H', 'H_center', 'Y', 'src'], \
        "the shape B1's provenance half owes is #219's rank-22 inventory, key for key"
    assert 'INSTANCED' in stored['status'] and 'provenance half' in stored['status'], \
        'the artifact must state what is instanced and what is still owed'
    return stored


def check_obligations(record):
    """The obligation set of `obligations.json` against a **rebuilt** certificate.

    The rebuilt record is what this compares, not the stored file: authoring mode rewrites the
    certificate after the checks run, so reading it back here would make the check vacuous on the
    first run and stale on every later one.
    """
    obligations = json.loads((HERE / 'obligations.json').read_text())
    owed = [item['id'] for item in obligations['obligations']]
    assert owed == ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'T1', 'B1'], owed
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
    b1 = next(item for item in obligations['obligations'] if item['id'] == 'B1')
    assert status['B1'] == 'INVENTORY_INSTANCED_AT_SCHEDULE_LEVEL' \
        and 'bitrung' in b1['resolution'] and 'bitinstance' in b1['resolution'], \
        'B1 must name both the measurement and the module that instances its schedule'
    assert 'OPEN' not in b1['status'], 'the instanced half must not be reported as open'
    inherited = [item['id'] for item in obligations['inherited']]
    assert inherited == ['R1', 'R2', 'R3', 'R4'], inherited
    assert all(item['status'] == 'OPEN' for item in obligations['inherited'])
    vendored = json.loads((HERE / 'references' / 'pr219-run1' / 'obligations.json').read_text())
    assert [item['id'] for item in vendored['obligations']] == inherited, \
        "the inherited obligation set must be #219's own"
    assert record['obligations'] == owed + inherited, 'the rebuilt obligation list'
    assert not any('bank' in key for key in record['blocked_on']
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


def check_import_harness():
    """The import contract's executable form: coverage, refusals, and that it really works.

    Three things are checked rather than described.  The contract must name the module and the
    four exit codes; the gate must be able to decide all seven acceptance tests, i.e. every test
    appears in some export's declared gate; and the harness's own self-test -- which builds
    synthetic bodies and then breaks each check in turn -- must pass every case, so the refusals
    it will perform on the real drop are demonstrably real.  Finally the real drop, which does
    not exist yet, must be refused with the refusal code.
    """
    contract = json.loads((HERE / 'export-contract.json').read_text())
    harness = contract['import_harness']
    assert harness['module'] == 'importer66.py' and (HERE / harness['module']).is_file(), \
        'the contract must name the module that implements it, and it must exist'
    assert sorted(harness['exit_codes']) == ['0', '1', '2', '3'], 'all four exit codes'
    assert 'gate' in harness['layers'] and 'replay' in harness['layers'], \
        'the two layers must be described, so that no replay is ever claimed by the gate'
    assert harness['replay_requirement']['checker_digest'] == \
        resolve(json.loads((HERE / 'references' / 'pr219-run1' / 'references'
                            / 'pr193-source-assisted-v4.certificate.json').read_text()),
                ['lift', 'checker_sha256']), 'the replay checker digest must be the pinned one'

    declared = set()
    for export in contract['required_exports']:
        assert export['bodies'], 'every required export must name the bodies it waits for'
        assert all(body.get('file') for body in export['bodies']), 'every body needs a file name'
        for body in export['bodies']:
            if body['anchored_digest'] is not None:
                assert len(body['anchored_digest']) == 64, 'anchored digests are sha256 hex'
        declared |= set(export['gate']['test'])
    tests = {test['id'] for test in contract['acceptance_tests']}
    assert declared == tests, \
        'the gate must be able to decide every acceptance test: %s' % sorted(tests - declared)

    observed = importer66.self_test(contract)
    failed = sorted(name for name, ok in observed.items() if not ok)
    assert not failed, 'the harness self-test must pass every case: %s' % failed
    assert len(observed) == 13, 'the self-test must exercise the refusals and the partial report too'
    code, report = importer66.run(contract, HERE / harness['exports_dir'])
    assert code == 2 and report['missing'], \
        'the real drop must still be refused: nothing has been published yet'
    assert len(report['missing']) == sum(len(export['bodies'])
                                         for export in contract['required_exports']), \
        'every required body is missing today'
    return dict(observed=observed, missing=len(report['missing']), verdict=report['verdict'])


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
    assert    contract['today']['bodies_present'] == 0, \
        'no body export exists in the pins and the contract must say so'
    bodies = set()
    for row in contract['today']['evidence']:
        if isinstance(row['value'], str) and row['value'].endswith('.gz'):
            bodies.add(row['value'].rsplit('/', 1)[-1])
        if row['keys'] and row['keys'][-1].endswith('.json'):
            bodies.add(row['keys'][-1])
    for export in contract['required_exports']:
        for row in export['must_reproduce']:
            if row['keys'] and row['keys'][-1].endswith('.json'):
                bodies.add(row['keys'][-1])
    assert bodies, 'the contract must name the bodies it waits for'
    # the pins are the two vendored sources: this package's own files, the bit drop included, are
    # not the supplier's publication and are read separately below
    pinned_names = {name for name in pins.pinned_paths() if name.startswith('references/')}
    assert not any(name.rsplit('/', 1)[-1] in bodies for name in pinned_names), \
        'no body the contract requires may be pinned: the 0-of-6 reading must be a reading'
    assert not any('.work' in name for name in pinned_names), \
        'the supplier workspace the contract names must not be in the pins'
    assert len(bodies) >= 4, 'program, frames, graph, record, witness and lift bodies: %s' % bodies
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


def check_bit_export_contract():
    """The bit-side twin contract, resolved against the pinned bit bytes.

    The twin's citations are the pinned rank-22 package's own data, so this reads every digest,
    count, status and obligation statement back out of the pinned file and compares it: the
    obligations it answers are quoted word for word and all four are still OPEN, the checker it pins
    is the one the pinned inventory carries (and is not the complex side's), the bodies it waits for
    are named and none of them is in the pins, and the harness is proved on synthetic bit bodies --
    so the gate and the refusals it will perform on the real bit drop are demonstrated while that
    drop is absent.
    """
    contract = json.loads((HERE / 'export-contract-bit.json').read_text())
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

    assert contract['version'] == 2 and contract['scope'], 'the twin must state its scope'
    for name, block in contract['precedent'].items():
        check(block['citations'], 'precedent/' + name)
    check(contract['today']['evidence'], 'today/evidence')

    obligations = pinned('references/pr219-run1/obligations.json')['obligations']
    assert [row['id'] for row in obligations] == ['R1', 'R2', 'R3', 'R4'], 'the four obligations'
    assert all(row['status'] == 'OPEN' for row in obligations), 'and all four still open'
    quoted = contract['precedent']['what_the_obligations_say']['citations']
    assert [row['keys'][1] for row in quoted] == [0, 1, 2, 3], 'every obligation is quoted'
    assert 'generated and hashed' in quoted[0]['value'], 'R1 asks for a hashed assignment'
    assert 'fallback 32*72^2 per retained child' in quoted[3]['value'], \
        'R4 must be quoted with its numbers'
    assert 'recomputed' in quoted[3]['value'], 'including its one licence to move a published value'

    assert contract['today']['bodies_present'] == 0, \
        'no bit body export exists in the pins and the contract must say so'
    assert contract['today']['of_required'] == len(contract['required_exports']) == 6, '0 of the six'
    bodies = [body for export in contract['required_exports'] for body in export['bodies']]
    wanted = {body['file'] for body in bodies}
    assert len(wanted) == len(bodies) == 15, 'fifteen distinct bodies: %d' % len(bodies)
    pinned_names = {name.rsplit('/', 1)[-1] for name in pins.pinned_paths()
                    if name.startswith(pins.VENDORED_RUN1 + '/')}
    assert not (wanted & pinned_names), \
        'the pinned supplier publishes no body, only the digests: %s' % sorted(wanted & pinned_names)
    anchored = [body['file'] for body in bodies if body['anchored_digest']]
    assert anchored == ['word.json.gz', 'frames.json.gz', 'graph.json', 'kchron.json',
                        'profile.json', 'charts.json', 'incidence.json', 'prime-witnesses.json.gz'], \
        "eight bodies carry a digest the word's certificates already published: %s" % anchored

    tests = {test['id'] for test in contract['acceptance_tests']}
    assert tests == {'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7'}, \
        'the same seven acceptance tests as the complex side'
    declared = set()
    for export in contract['required_exports']:
        assert export['id'] in ('B1', 'B2', 'B3', 'B4', 'B5', 'B6'), export['id']
        assert export['publishes'] and export['form'] and export['cardinality'], export['id']
        assert export['unblocks'], 'every export must unblock an obligation'
        assert export['acceptance'] and set(export['acceptance']) <= tests, \
            'the acceptance tests must exist: %s' % export['id']
        assert export['bodies'] and all(body.get('file') for body in export['bodies']), export['id']
        assert set(export['gate']['test']) <= tests, \
            'the gate may only declare acceptance tests: %s' % export['id']
        check(export['must_reproduce'], 'export/' + export['id'])
        declared |= set(export['gate']['test'])
    assert declared == tests, \
        "the twin's gate must decide every acceptance test: %s" % sorted(tests - declared)

    mapping = contract['obligation_mapping']
    assert sorted(mapping) == ['R1', 'R2', 'R3', 'R4'], 'all four obligations mapped'
    assert all(mapping[key] for key in mapping), 'no obligation may map to nothing'
    exports = {export['id'] for export in contract['required_exports']}
    for key, value in mapping.items():
        assert set(value) <= exports, '%s must map to required exports' % key
    assert set().union(*mapping.values()) == exports, \
        'every export must be reachable from the obligations it exists for'
    assert contract['failure_semantics']['today'].startswith('0 of 6')
    assert 'never' in contract['failure_semantics'] and contract['not_required'], \
        'the twin must say what it does not ask for, and what it can never buy'
    for test in contract['acceptance_tests']:
        assert test['bound'] and test['reject_control'], \
            'every test needs a bound and a reject control: %s' % test['id']

    harness = contract['import_harness']
    assert harness['module'] == 'importer66.py' and (HERE / harness['module']).is_file(), \
        'the same module implements the twin'
    assert harness['contract'] == 'export-contract-bit.json', 'and it names the twin contract'
    assert harness['exports_dir'] == 'exports-bit', 'the twin has its own drop'
    assert sorted(harness['exit_codes']) == ['0', '1', '2', '3', '4'], \
        'the twin publishes the partial report as its own exit code'
    assert 'gate' in harness['layers'] and 'replay' in harness['layers'], \
        'the two layers must be described, so that no replay is ever claimed by the gate'
    assert harness['replay_requirement']['checker_digest'] == \
        resolve(pinned('references/pr219-run1/inputs/absorbed-occurrences.json'),
                ['source_pins', 'checker_sha256']), \
        "the twin must pin the checker the bit word's own inventory carries"
    assert harness['replay_requirement']['checker_digest'] != \
        resolve(pinned('references/pr219-run1/references/pr193-source-assisted-v4.certificate.json'),
                ['lift', 'checker_sha256']), \
        "the two contracts pin their own supplier's checker, never each other's"

    observed = importer66.self_test(contract)
    failed = sorted(name for name, ok in observed.items() if not ok)
    assert not failed, "the twin's self-test must pass every case: %s" % failed
    assert len(observed) == 13, 'the twin gets the same thirteen-case proof as the complex side'

    # The drop beside the pins: the bytes behind the digests the certificates publish, and what the
    # gate makes of them.  pins.py pins these files, so the same claim is read twice -- once as a
    # manifest and once as an import -- and the second reading is the one that decides tests.
    drop = HERE / harness['exports_dir']
    drop_bodies = [body for export in contract['required_exports'] for body in export['bodies']]
    present = [body for body in drop_bodies if (drop / body['file']).is_file()]
    anchored = [body for body in drop_bodies if body['anchored_digest']]
    absent = sorted(body['file'] for body in drop_bodies if body not in present)
    assert len(present) == contract['drop']['bodies'] == 10, \
        'the drop holds ten of the thirteen required bodies: %d' % len(present)
    assert len(anchored) == contract['drop']['anchored'] == 8, \
        'eight bodies carry a digest the certificates already published: %d' % len(anchored)
    assert sorted(name.rsplit('/', 1)[-1] for name in pins.pinned_paths()
                  if name.startswith('exports-bit/')) == sorted(
        [body['file'] for body in present] + ['physical.rebuilt.json']), \
        'the drop is pinned body for body, reproduction evidence included'
    for body in anchored:
        assert pins.digest(drop / body['file']) == body['anchored_digest'], \
            '%s must be the bytes the certificates hash' % body['file']
    published = pinned('references/pr219-run1/references/pr205-packed.certificate.json')['physical']
    rebuilt = json.loads((drop / 'physical.rebuilt.json').read_text())
    assert set(rebuilt) == set(published) and all(rebuilt[key] == published[key] for key in published), \
        "PR205's packer re-derived the published physical block, and no field of it may differ"

    code, report = importer66.run(contract, drop)
    refused = sorted(row.split(': ', 1)[1] for row in report['missing'])
    assert code == 2 and refused == absent, \
        'the default import must still refuse the drop: nothing is discharged from bodies alone'
    code, report = importer66.run(contract, drop, partial=True)
    tests = report['tests']
    assert code == 4 and report['replay']['status'] == 'NOT RUN', \
        'a partial run is reportable and never admissible, and it never claims the replay'
    assert not any(row['failed'] for row in tests.values()), \
        'no check may fail on the published bytes: %s' % sorted(
            key for key, row in tests.items() if row['failed'])
    assert [key for key, row in sorted(tests.items()) if row['status'] == importer66.PASS] == \
        ['A2', 'A3'], 'the published bytes decide exactly the index and chart tests'
    assert [(key, row['passed']) for key, row in sorted(tests.items())] == \
        [('A1', 17), ('A2', 9), ('A3', 17), ('A4', 0), ('A5', 0), ('A6', 17), ('A7', 17)], \
        'the gate decides what the present bodies declare and nothing more: %s' % [
            (key, row['passed']) for key, row in sorted(tests.items())]
    for key, row in tests.items():
        if row['status'] == importer66.NOT_RUN:
            assert any(name in row['reason'] for name in absent), \
                '%s may only be held by a body this drop does not hold: %s' % (key, row['reason'])
    recorded = contract['drop']['gate']
    assert recorded['exit_code'] == code == 4 and recorded['default_exit_code'] == 2, \
        'the contract must record the codes the drop actually produces'
    assert recorded['by_test']['A2'].startswith('PASS') and recorded['by_test']['A3'].startswith('PASS') \
        and 'integrity.json' in recorded['by_test']['A1'] \
        and 'controls.json' in recorded['by_test']['A6'], \
        'and the per-test reading must name the same two tests and the same two blockers'
    stored = json.loads((HERE / recorded['report']).read_text())
    assert stored['tests'] == tests and stored['missing'] == report['missing'], \
        'the stored partial report must be this run, not an earlier one'
    return contract


def check_rank3_export_contract():
    """The rank-3 rung's export contract, on the new row, re-derived in full.

    Three things are checked rather than read: every citation in the contract is resolved
    against the pinned bytes (the vendored row certificate, the pinned PR205 certificate, the
    pinned PR219 inventory, this package's own occurrences-rank3.json and export-contract.json,
    and obligations.json's own statements); the whole contract is compared with a fresh
    rebuild, which re-derives the assignment from its addressing rule, the retained ledger
    from the row, the bit leaf through #219's vendored arithmetic and the rung's point
    through the queue's assembly rule and the unchanged 47-constraint assembly; and the
    0-of-6 reading is asserted to be a *reading*, by walking the pinned row for bank, assign
    and occurrence keys and finding none.  Nothing here certifies the rung: the row's PR is
    unmerged and the contract says so.
    """
    contract = json.loads((HERE / 'export-contract-rank3.json').read_text())
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

    def walk(node, where):
        if isinstance(node, dict):
            if {'source', 'keys', 'value'} <= set(node):
                check([node], where)
                return
            for key, child in node.items():
                walk(child, where + '/' + str(key))
        elif isinstance(node, list):
            for index, child in enumerate(node):
                walk(child, '%s[%d]' % (where, index))

    walk(contract, 'rank3')
    assert contract['version'] == 3 and contract['scope'] and contract['source'], \
        'the rung contract must state its scope and its prose twin'

    # the row: pinned, and what it publishes as bodies
    row_path = instantiate_rank3.ROW
    assert instantiate_rank3.ROW_NAME in pins.pinned_paths(), \
        'the row certificate must be pinned by digest, not floating'
    assert contract['rung']['row']['sha256'] == digest(row_path) == \
        '691cb0aaeb0d6b993e1e1e5116ae7a5c57af058a8c413249016347d1b40d3b90', 'row digest'
    assert contract['rung']['row']['bytes'] == len(row_path.read_bytes()), 'row size'
    assert contract['rung']['family'] == 3 and contract['rung']['width'] == WIDTH, 'the rung'
    shell = json.loads(row_path.read_text())
    assert contract['rung']['row']['status'] == shell['status'] \
        and contract['rung']['row']['audit_status'] == shell['layer']['audit_status'], \
        'the row verdicts must be the pinned ones'
    fresh_gap = instantiate_rank3.pins_gap(shell)
    assert contract['machine_read']['bank_keys'] == fresh_gap['row_certificate_bank_keys'] == [], \
        'the 0-of-6 reading must be a reading: the row holds no bank key'
    assert contract['machine_read']['assignment_keys'] == \
        fresh_gap['row_certificate_assignment_keys'] == [], 'and no assignment key'
    assert contract['machine_read']['occurrence_keys'] == \
        fresh_gap['row_certificate_occurrence_keys'] == [], 'and no occurrence key'
    assert contract['machine_read']['audit_source_digests'] == \
        sorted(shell['layer']['audit_source_sha256']), 'the audit sources, by digest'

    # the assignment and the ledger, rebuilt rather than read
    instance = instantiate_rank3.build(shell)
    assert contract['our_side']['assignment'] == instance['assignment'], \
        'the assignment must be the one the rule instantiates'
    assert instance['assignment']['padding_per_bank'] == 0 \
        and instance['assignment']['padding_registers'] == 0, \
        'rank 3 divides the width: this rung is unpadded'
    assert instance['assignment']['banks'] == 4086 and instance['banks_per_copy'] == 1362 \
        and instance['assignment']['items'] == 89892, 'the rung\'s geometry'
    assert contract['our_side']['ledger'] == instance['ledger'], 'the ledger the rung induces'
    assert contract['our_side']['retained_eligibility'] == instance['retained_eligibility'] \
        == [4, 18, 20], 'the retained eligibility'
    assert contract['our_side']['remaining_whole_bank_families'] == \
        instance['remaining_whole_bank_families'], 'and the families it still holds'
    stored = json.loads((HERE / 'occurrences-rank3.json').read_text())
    assert stored == json.loads(json.dumps(instance, default=str)), \
        'occurrences-rank3.json differs from a fresh instantiation'

    # the whole contract against a fresh rebuild: every number, not just the cited ones
    rebuilt = json.loads(json.dumps(rank3contract.build(), default=str))
    assert rebuilt == contract, 'export-contract-rank3.json differs from a fresh rebuild'

    # anatomy, and the two facts the rung adds to the general contract
    exports_ids = [export['id'] for export in contract['required_exports']]
    assert exports_ids == ['G1', 'G2', 'G3', 'G4', 'G5', 'G6'], 'the six exports'
    tests_ids = [test['id'] for test in contract['acceptance_tests']]
    assert tests_ids == ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7'], 'the seven tests'
    for export in contract['required_exports']:
        assert export['publishes'] and export['form'] and export['cardinality'], export['id']
        assert export['unblocks'] and set(export['acceptance']) <= set(tests_ids), export['id']
    for test in contract['acceptance_tests']:
        assert test['test'] and test['bound'] and test['reject_control'], test['id']
    assert 'no padding' in contract['acceptance_tests'][1]['name'] and \
        'padding' in contract['acceptance_tests'][1]['reject_control'], \
        'A2 must make the absences of padding a test rather than a remark'
    obligations = contract['obligations_restated']
    assert [row['id'] for row in obligations] == ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7'], \
        'C1-C7, restated at this rung'
    assert [row['quote']['keys'][1] for row in obligations] == list(range(7)), \
        'every obligation is quoted from obligations.json'
    assert contract['obligation_mapping'] == {row['id']: row['exports'] for row in obligations}, \
        'the mapping must be the restatement\'s own'
    assert all(set(row['exports']) <= set(exports_ids) for row in obligations), \
        'no obligation may map to an export that does not exist'
    assert contract['rung']['not_this'].startswith('rung 3 of run3.py'), \
        'the rung must say which rung it is not'
    assert obligations[0]['status'] == 'OPEN_PHYSICAL_HALF_INSTANCED_COMBINATORIAL_HALF', \
        'C1: the assignment is instanced, the normalizer is not'
    assert obligations[5]['status'] == obligations[6]['status'] == 'OPEN_NOT_THIS_RUNG', \
        'C6 and C7 belong to the next rung'
    assert contract['not_required'] and contract['still_owed'] and contract['verification'], \
        'the contract must say what it does not ask, what is owed and what is checked'

    # the point: bit-bound, above the published top, and not a claim
    point = contract['point']
    assert Q(point['kappa']) == Q(contract['required_exports'][5]['gate']['equals']['kappa']), \
        'the envelope\'s gate and the point must be the same kappa'
    assert point['binding'] == 'bit' and point['budget_is_the_leaf'], 'bit-bound'
    assert float(Q(point['complex_ceiling'])) > float(Q(point['kappa'])), \
        'the complex ceiling sits above the binding budget: the rung is not ceiling-tight'
    allowed = contract['our_side']['allowed_to_move']
    frontier = Q(json.loads((HERE / 'references'
                             / 'pr207-coordinated-crossover.certificate.json').read_text())['kappa'])
    assert Q(point['kappa']) > Q(allowed['published_top_kappa']) \
        and Q(point['kappa']) > frontier, 'the rung must price above the published top and the '
    'pinned frontier'
    assert allowed['beats_published_top'] == 'True' and allowed['beats_pinned_frontier'] == 'True' \
        and Q(allowed['published_top']) == Q(allowed['published_top_kappa']) \
        and Q(allowed['pinned_frontier']) == frontier and Q(allowed['kappa']) == Q(point['kappa']), \
        'and the contract must record both comparisons against numbers it can re-derive'
    assert point['beats_published_top'] is True and point['beats_frontier'] is True \
        and Q(point['frontier_kappa']) == frontier, 'the point must carry the comparison itself'
    assert contract['our_side']['allowed_to_move']['publication_status'].startswith(
        'the rung is a derived target'), 'the contract must not present the target as a claim'
    assert contract['today']['bodies_present'] == 0 \
        and contract['today']['of_required'] == len(contract['required_exports']) == 6, \
        '0 of the six bodies are exported by the row'

    # the gate is executable: the contract speaks the importer's own dialect, and the harness
    # proves on synthetic bodies that every declared check decides and that a broken one fails
    harness = contract['import_harness']
    assert harness['module'] == 'importer66.py' \
        and harness['contract'] == 'export-contract-rank3.json', 'the rung must name its harness'
    assert harness['exports_dir'] == 'exports-rank3' and not (HERE / harness['exports_dir']).exists(), \
        'the rung has no drop: the gate must wait for bodies that are not in the package'
    assert sorted(harness['exit_codes']) == ['0', '1', '2', '3', '4'], \
        'the same five codes as the two other contracts'
    vocabulary = {'test', 'equals', 'at_most', 'bijection', 'flags_true', 'flags_present',
                  'distinct_below', 'counted_in_tables', 'equals_in', 'equals_on',
                  'declares_every_body_on'}
    for export in contract['required_exports']:
        declared = export['gate']
        assert set(declared) <= vocabulary, \
            '%s declares a check the harness cannot read: %s' % (export['id'],
                                                                sorted(set(declared) - vocabulary))
        assert set(declared['test']) <= set(tests_ids), export['id']
        assert export['bodies'] and all(body['file'] and 'stream' in body
                                        and 'anchored_digest' in body
                                        for body in export['bodies']), export['id']
        assert all(body['anchored_digest'] is None for body in export['bodies']), \
            'the row publishes no body of its own, so nothing may be anchored'
        assert len({body['file'] for body in export['bodies']}) == len(export['bodies']), \
            '%s names a body twice' % export['id']
        for spec in declared.get('equals_in', []):
            assert (HERE / spec['source']).is_file(), \
                '%s compares against %s, which is not in the package' % (export['id'],
                                                                         spec['source'])
    assert contract['today']['required_bodies'] == \
        sum(len(export['bodies']) for export in contract['required_exports']) == 10, \
        'the gate waits for ten bodies across the six exports'
    observed = importer66.self_test(contract)
    assert len(observed) == 13 and all(observed.values()), \
        'the rank-3 gate must pass its own self-test: %s' % sorted(
            name for name, ok in observed.items() if not ok)
    drop = HERE / harness['exports_dir']
    code, report = importer66.run(contract, drop)
    assert code == 2 and len(report['missing']) == contract['today']['required_bodies'], \
        'the real drop must be refused, body by body, and nothing run'
    assert report['replay'] is None, 'a refusal runs nothing, the replay included'
    code, report = importer66.run(contract, drop, partial=True)
    assert code == 4 and report['replay']['status'] == 'NOT RUN', \
        'and it must be reportable in part, which is never admissible'
    assert not any(row['failed'] for row in report['tests'].values()), \
        'an absent body is a missing datum, not a failed check'
    assert harness['replay_requirement']['checker_digest'] is None, \
        'this row publishes no checker digest for the harness to accept'
    assert 'audit_source_sha256' in harness['replay_requirement']['why'], \
        'and the nearest published evidence must be named in the same breath'

    def keys_containing(node, needle, where=''):
        found = []
        if isinstance(node, dict):
            for key, child in node.items():
                if needle in str(key).lower():
                    found.append(where + '/' + str(key))
                found += keys_containing(child, needle, where + '/' + str(key))
        elif isinstance(node, list):
            for index, child in enumerate(node):
                found += keys_containing(child, needle, where + '[%d]' % index)
        return found

    assert keys_containing(shell, 'checker') == [], \
        'the absence of a checker digest must be a reading of the pinned bytes, not a claim'
    assert len(shell['layer']['audit_source_sha256']) == 5, \
        'the digest set the harness points at is the row\'s, five sources wide'
    assert contract['inherited'] == json.loads((HERE / 'obligations.json').read_text())[
        'inherited'], 'the inherited R1-R4 must travel with the contract unchanged'
    return contract, observed


def check_rank3_stability():
    """The rank-3 rung's stability: every head of #233, and every other width-66 row.

    The whole measurement is re-derived and compared, then the finding it rests on is asserted
    rather than described: that the rung exists on exactly two of the six heads, that the four
    earlier ones miss it by nine registers (one rank-3 child per copy short of the multiple the
    criterion needs) rather than by a different family, that the price is identical wherever it
    exists because the bit leaf binds, that the *next* rung's eligibility differs between the
    two rows that carry it, and that no other width-66 row in the repository carries it at all.
    The modular criterion behind all of it -- eligibility is a divisibility condition on the
    family's own count -- is checked against the ledger's own test on every row examined, and
    the last head is asserted to be the row the export contract is priced on.
    """
    stored = json.loads((HERE / 'rank3-stability.json').read_text())
    fresh = json.loads(json.dumps(rank3stability.build(), default=str))
    assert stored == fresh, 'rank3-stability.json differs from a fresh measurement'

    heads, rows = stored['heads'], stored['rows']
    assert [head['short'] for head in heads] == [
        '52c6fba', '7f909fb', 'cf08677', 'c3f9ba1', '246f6f9', '109a857'], 'the six heads'
    for head in heads:
        source = HERE / head['source']
        assert head['source'] in pins.pinned_paths(), \
            'every head must be pinned: %s' % head['source']
        assert head['sha256'] == digest(source), 'head digest: %s' % head['short']
        assert head['bytes'] == len(source.read_bytes()), 'head size: %s' % head['short']
        assert head['subject'] and head['date'], 'every head keeps its provenance'

    assert [head['short'] for head in heads if head['rank3_eligible']] == \
        ['246f6f9', '109a857'], 'the rung exists on the last two heads and not on the first four'
    stability = stored['stability']
    assert stability['heads'] == 6 and stability['distinct_rows'] == 3, 'six heads, three rows'
    assert stability['heads_where_the_rung_exists'] == 2 \
        and stability['heads_where_it_does_not'] == 4, 'two of the six'
    assert stability['eligibility_stable'] is False, 'the eligibility is not stable'
    assert stability['price_stable'] is True and len(stability['kappas']) == 1, \
        'the price is stable wherever the rung exists'
    assert stability['next_rung_stable'] is False, 'and the next rung is not'

    early = rows[heads[0]['row']]
    assert early['rank3_eligible'] is False and early['eligibility'] == [12, 17, 18, 20], \
        'the first four heads share one row, and the rung is not on it'
    assert early['families_at_width']['3']['registers_short'] == 9, \
        'nine registers over three copies: the early row misses the rung by one child per copy'
    for label in stability['rows_where_the_rung_exists']:
        rung, point = rows[label]['rung'], rows[label]['point']
        assert rung['banks'] == 4086 and rung['padding_per_bank'] == 0 \
            and rung['divides_width'] is True, 'the rung geometry on every row that carries it'
        assert rung['volume'] == 269676 and rung['banks_per_copy'] == 1362, 'and its volume'
        assert point['kappa'] == stability['kappas'][0] and point['binding'] == 'bit' \
            and point['budget_is_the_leaf'] is True, 'and the same bit-bound point'
    assert len({json.dumps(rows[label]['rung']['retained_eligibility'])
                for label in stability['rows_where_the_rung_exists']}) == 2, \
        'the next rung differs between the two rows that carry this one'

    for row in list(rows.values()) + stored['corpus']['rows']:
        assert row['families'] == len(row['families_at_width']), 'every family is recorded'
        for rank, entry in row['families_at_width'].items():
            family = int(rank)
            assert entry['volume'] == family * entry['count'], 'volume = rank * count'
            assert entry['registers_short'] == (-entry['volume']) % WIDTH, 'registers short'
            assert entry['eligible'] == (entry['volume'] % WIDTH == 0), \
                'eligibility is divisibility, at rank %d' % family
            assert entry['eligible'] == \
                (entry['count'] % rank3stability.criterion(family)['divisor'] == 0), \
                'and the count alone decides it, at rank %d' % family

    corpus = stored['corpus']
    assert corpus['width'] == WIDTH and len(corpus['rows']) == 9, \
        'nine distinct width-66 rows in the repository'
    carrying = [row for row in corpus['rows'] if row['rank3_eligible']]
    assert len(carrying) == 2, 'the rung exists on two corpus rows'
    assert all(any('pr233' in source for source in row['sources']) for row in carrying), \
        'and both of them are the #233 rows: the rung is a property of the row, not the family'
    ladder = [row for row in corpus['rows'] if row['W'] == 12052
              and row['eligibility'] == [11, 16, 20]]
    assert len(ladder) == 1 and ladder[0]['rank3_eligible'] is False and \
        ladder[0]['families_at_width']['3']['registers_short'] == 39, \
        'the pinned ladder row does not carry the rung either, and misses it by 39 registers'

    contract = json.loads((HERE / 'export-contract-rank3.json').read_text())
    assert heads[-1]['sha256'] == contract['rung']['row']['sha256'], \
        'the last head is the certificate the export contract is priced on'
    assert rows[heads[-1]['row']]['point']['kappa'] == contract['point']['kappa'], \
        'and the same point: the stability measurement and the contract must agree'
    assert stored['reading'] and stored['status'], 'the measurement must state its reading'
    return stored


def check_rank4_rung():
    """The rank-4 rung on PR233's row, re-derived: the padding of T1, its limits, and the price.

    The whole measurement is rebuilt and compared, then the three readings it rests on are
    asserted rather than described: the volume criterion holds on exactly one head, the padded
    schedule of T1 cannot be saturated there (nine slots short, so its padding is not uniform),
    T1's mixed-tiling enumeration has solutions at three bank counts and every one of them draws
    at least a third of the bank from other bins, and -- the point of the exercise -- the kappa
    does not move, because every rung above rank 3 is bit-bound on the bit leaf.  The required
    leaves are checked against the certificate's own bit-requirement table rather than trusted.
    """
    stored = json.loads((HERE / 'rank4-rung.json').read_text())
    fresh = json.loads(json.dumps(rank4rung.build(), default=str))
    assert stored == fresh, 'rank4-rung.json differs from a fresh measurement'

    criterion = stored['criterion']
    assert criterion['rank'] == 4 and criterion['width'] == WIDTH, 'the rung and the word'
    assert criterion['volume']['rule'] == '66 | 4 * n4' \
        and criterion['capacity']['rule'] == '16 | n4', 'both readings of the criterion'
    assert criterion['padded_pattern'] == '66 = 16 * 4 + 2' \
        and criterion['registers_from_other_bins'] == 2, 'T1\'s pattern for rank 4'

    heads = {head['short']: head for head in stored['heads']}
    assert [head['short'] for head in stored['heads']] == [
        '52c6fba', '7f909fb', 'cf08677', 'c3f9ba1', '246f6f9', '109a857'], 'the six heads'
    for head in stored['heads']:
        assert head['sha256'] == digest(HERE / head['source']), 'head digest: %s' % head['short']
        assert head['bytes'] == len((HERE / head['source']).read_bytes()), head['short']
    dependence = stored['head_dependence']
    assert dependence['heads_carrying_rank3'] == ['246f6f9', '109a857'] \
        and dependence['heads_carrying_the_volume_criterion'] == ['109a857'], \
        'the rank-4 rung exists on one of the six heads, where the rank-3 rung exists on two'
    assert heads['246f6f9']['n4'] == 34506 and heads['109a857']['n4'] == 34551, \
        'the two heads that carry rank 3 straddle the 33-multiple rank 4 needs'
    assert heads['246f6f9']['rank3_eligible'] is True \
        and heads['246f6f9']['volume_whole'] is False, 'rank 3 without rank 4'
    assert not any(head.get('volume_whole') for head in stored['heads'][:4]), \
        'the four early heads carry neither rung'
    assert all(head['verdict'] for head in stored['heads']), 'every head states its reading'

    rung = stored['rung']
    assert rung['n4'] == 34551 and rung['volume'] == 4 * 34551 == 138204, 'the volume'
    assert rung['volume_banks'] == 138204 // WIDTH == 2094 and rung['volume_is_whole_banks'], \
        'the volume criterion prices 2,094 whole banks'
    assert rung['retained_eligibility'] == [18, 20], 'and the retained row keeps two families'
    schedule = rung['padded_schedule']
    assert schedule['saturated'] is False, 'T1\'s padded schedule cannot be saturated here'
    assert schedule['slack_slots'] == (WIDTH // 4) * 2160 - 34551 == 9 \
        and schedule['slack_registers'] == 4 * 9, 'nine slots, thirty-six registers short'
    assert schedule['banks'] == 2160 and schedule['blocks_per_bank'] == 16 \
        and schedule['padding_registers_per_bank'] == 2 and schedule['uniform'] is False, \
        'the capacity bank count, T1\'s pattern, and no uniform padding'
    assert rung['priced_bank_count_hosts_its_items'] is False \
        and 2094 * 16 == 33504 < 34551, \
        'the ledgers this rung prices and the ledgers it could schedule are not the same'
    assert rung['realisable_as_a_saturated_padded_schedule'] is False, 'and it says so'

    tilings = stored['mixed_tilings']
    assert tilings['bank_counts_examined'] == len(rank4rung.divisors(34551)) == 12, \
        'every divisor of n4 is a bank count of T1\'s enumeration'
    assert tilings['feasible_bank_counts'] == [3141, 3839, 11517], \
        'the tiling exists at three bank counts and nowhere else'
    assert tilings['patterns_enumerated'] == 1168 and tilings['candidates_priced'] == 6, \
        'the enumeration is complete and the priced sample is the two extremes per bank count'
    assert tilings['lightest_padding_registers_per_bank'] == 22, \
        'no admissible pattern is lighter than a third of the bank'
    empty = [entry for entry in tilings['enumeration'] if not entry['feasible']]
    assert len(empty) == 9 and all(entry['banks'] in (1, 3, 9, 11, 33, 99, 349, 1047, 34551)
                                  for entry in empty), \
        'the empty bank counts are the capacity-infeasible ones and n4 itself'
    assert tilings['every_priced_candidate_prices_above_the_volume_ledger'] is True, \
        'the tiled ledgers all price above the ledger the volume criterion prices'
    for entry in tilings['priced']:
        assert entry['banks'] in tilings['feasible_bank_counts'], 'a priced candidate'
        assert entry['pattern'] and entry['draw'] and entry['retained_W'] < 32070, 'and a ledger'
        assert Q(entry['coarse']) > Q(stored['point']['rank4_priced']['coarse']), 'above it'
        assert Q(entry['kappa']) == Q(stored['point']['rank3']['kappa']), \
            'no tilable ledger moves the kappa either'

    point = stored['point']
    contract = json.loads((HERE / 'export-contract-rank3.json').read_text())
    assert Q(point['rank3']['kappa']) == Q(contract['point']['kappa']), \
        'the rung below is the one this package prices'
    assert point['kappa_moved'] is False and point['delta_kappa'] == '0', \
        'banking rank 4 does not move the kappa'
    assert point['rank3']['kappa'] == point['rank4_priced']['kappa'] \
        == point['rank4_tiled']['kappa'], 'the same grid point from every ledger'
    assert point['budget_is_the_leaf'] is True \
        and point['rank4_priced']['binding'] == 'bit', 'because the rung is bit-bound'
    assert Q(point['rank4_priced']['coarse']) > Q(point['rank3']['coarse']) \
        and Q(point['rank4_tiled']['coarse']) > Q(point['rank4_priced']['coarse']), \
        'what the rung does buy is slope, on both ledgers, in that order'
    assert point['delta_coarse_priced_percent'] > 8 and point['delta_coarse_tiled_percent'] > 100, \
        'the complex branch stops binding by any margin whatsoever'
    assert Q(point['tightest_constraint']) == Q(point['leaf']) * run3.ETA \
        and point['adjacent_grid_rejected'] is True, \
        'the assembly is exactly as green as its own eta and rejects the adjacent point'

    published = {line['target']: line['required_bit_leaf']
                 for line in json.loads((HERE / 'certificate.json').read_text())['bit_requirement']}
    matched = [line for line in stored['targets'] if line['matches_the_certificate']]
    assert len(matched) == 3, 'the inversion must reproduce the certificate where they overlap'
    for line in matched:
        assert published[line['target']] == line['required_bit_leaf'], \
            'target %s: the certificate and this inversion must agree' % line['target']
    assert all(line['bit_branch_short'] for line in stored['targets']), \
        'every further target needs a bit leaf above the current one, the rung below included'
    leaf = Q(point['leaf'])
    next_leaf_grid = Q(-((-(leaf * run3.GRID)) // 1), run3.GRID)     # ceil of the leaf on the grid
    assert Q(stored['targets'][0]['required_bit_leaf']) == next_leaf_grid \
        and 0 < next_leaf_grid - leaf <= Q(1, run3.GRID), \
        'even the next 10^-18 grid point of the kappa needs the next grid point of the bit leaf'
    assert 'MEASURED NEGATIVE' in stored['verdict'] and stored['status'], \
        'the module must state the negative result and what verify checks'
    return stored


def check_bit_rung():
    """The bit-side rung on #219's word: the criterion, the screen, the plateau and the point.

    The whole measurement is rebuilt and compared with `bitrung.json`, and the reading it turns on
    is then re-derived a second time from the **pinned packed certificate** with plain integer and
    `Fraction` arithmetic -- no package module and no engine: the rung-1 retained row and its row
    identity, the families a bank can host (whole-bank volume, or the padded schedule a rank that
    does not divide the width admits), the leader's three absorptions applied by hand (a whole
    family out, the padding drawn per bank out of the singleton bin, the stock falling by exactly
    the bank count), the vendored three-level bootstrap chain on the extended row, and the queue's
    assembly rule on the extended leaf.  The plateau is asserted rather than described: 108 of the
    377 rungs carry the same kappa, so the point this package quotes does not depend on which rung
    is chosen -- only the cheapest bank count does -- and the binding side of the assembly has
    switched from the bit leaf to the complex branch, which is what makes #233's row's complex
    ceiling the wall for the next increment.
    """
    stored = json.loads((HERE / 'bitrung.json').read_text())
    fresh = json.loads(json.dumps(bitrung.build_artifact(), default=str))
    assert stored == fresh, 'bitrung.json differs from a fresh measurement'

    # 1. the rung-1 retained row, from the pinned packed certificate and nothing else
    packed = json.loads((HERE / 'references' / 'pr219-run1' / 'references'
                         / 'pr205-packed.certificate.json').read_text())['physical']
    packed_row = {int(r): int(n) for r, n in packed['child_histogram'].items()}
    deficit, stock = int(packed['deficit']), int(packed['W'])
    mass_before = sum(r * n for r, n in packed_row.items())
    assert 72 * stock - mass_before == deficit == 5808, 'the packed bit row identity'
    absorbed = 22 * packed_row[22]
    assert absorbed == 440352 and absorbed // 72 == 6116, 'rung 1 takes the rank-22 bin whole'
    row = {r: n for r, n in packed_row.items() if r != 22}
    mass = mass_before - absorbed
    retained_W = (mass + deficit) // 72
    assert 72 * retained_W == mass + deficit and retained_W == stock - 6116 == 50286, \
        'the retained row identity, with the stock dropped by the bank count'
    rung1 = stored['rung1']
    assert (rung1['retained_W'], rung1['retained_deficit'], rung1['retained_mass']) == \
        (retained_W, deficit, mass), 'the row this rung starts from'
    assert rung1['retained_children'] == sum(row.values()) == 857622 \
        and rung1['retained_families'] == len(row) == 21 \
        and rung1['retained_maxchild'] == max(row) == 21, 'its children, families and largest'
    assert Q(rung1['coarse_saving']) == Q(json.loads((HERE / 'certificate.json').read_text())
                                          ['calibrations']['run1']['bit_coarse_after']), \
        'the rung-1 row must be the one the package already calibrates against'

    # 2. the criterion, family by family, on the retained row alone
    measured = {entry['rank']: entry for entry in stored['families']}
    assert sorted(measured) == sorted(row) == list(range(1, 22)), 'every family is measured'
    absorbable = []
    for rank, children in sorted(row.items()):
        entry, volume = measured[rank], rank * children
        capacity, padding = 72 // rank, 72 % rank
        whole, saturated = volume % 72 == 0, padding != 0 and children % capacity == 0
        assert entry['items'] == children and entry['volume'] == volume, 'rank %d' % rank
        assert entry['divides_the_width'] == (padding == 0), 'rank %d and the width' % rank
        assert entry['volume_is_whole'] == whole, 'rank %d whole-bank volume' % rank
        assert entry['volume_banks'] == (volume // 72 if whole else None), 'rank %d banks' % rank
        assert (entry['capacity_blocks_per_bank'], entry['padding_registers_per_bank']) == \
            (capacity, padding), 'rank %d geometry' % rank
        assert entry['padded_saturates'] == saturated, 'rank %d padded schedule' % rank
        if saturated or (whole and padding == 0):
            absorbable.append(rank)
    assert absorbable == stored['absorbable'] \
        == [4, 6, 7, 8, 9, 11, 12, 15, 16, 17, 19, 20, 21], 'the families a bank can host'

    # 3. the screen, and its completeness
    combos = set()
    for depth in (1, 2, 3):
        combos |= {tuple(combo) for combo in itertools.combinations(absorbable, depth)}
    screened = {tuple(entry['ranks']) for entry in stored['screen']['rungs']}
    assert screened == combos and len(screened) == 13 + 78 + 286 == 377, \
        'the screen is every rung of up to three absorbable families, and nothing else'
    assert stored['screen']['depth'] == 3 and len(stored['screen']['rungs']) == 377

    # 4. the leader, applied by hand: whole families out, the padding out of the singleton bin
    leader = stored['leader']
    ledger, banks_total, padding_total = dict(row), 0, 0
    for step in stored['leader_schedule']['steps']:
        rank, children = step['rank'], ledger[step['rank']]
        capacity, padding = 72 // rank, 72 % rank
        if step['reading'] == 'volume':
            assert padding == 0 and (rank * children) % 72 == 0, 'rank %d leaves whole' % rank
            banks, draw = rank * children // 72, 0
            ledger = {r: n for r, n in ledger.items() if r != rank}
        else:
            assert padding and children % capacity == 0, 'rank %d takes a padded schedule' % rank
            banks, draw, kept = children // capacity, (children // capacity) * padding, dict(ledger)
            del kept[rank]
            kept[1] = kept[1] - draw
            assert kept[1] >= 0, 'the singleton bin must be able to supply the padding'
            ledger = kept
        assert (banks, draw) == (step['banks'], step['padding_registers']), \
            'rank %d: the schedule the module reads' % rank
        banks_total, padding_total = banks_total + banks, padding_total + draw
        mass_now = sum(r * n for r, n in ledger.items())
        assert mass_now == step['mass_after'] \
            and (mass_now + deficit) // 72 == step['stock_after'], \
            'the row identity after rank %d' % rank
    assert banks_total == leader['banks'] == 7342 and padding_total == 65808, 'the leader rung'
    assert leader['ranks'] == [7, 8, 20] and leader['binding'] == 'complex'
    assert ledger == {int(r): n for r, n in stored['leader_schedule']['retained_histogram'].items()}
    assert sum(ledger.values()) == stored['leader_schedule']['retained_children'] == 756192 \
        and len(ledger) == stored['leader_schedule']['retained_families'] == 18 \
        and max(ledger) == stored['leader_schedule']['retained_maxchild'] == 21, 'the retained row'
    assert (sum(r * n for r, n in ledger.items()) + deficit) // 72 \
        == stored['leader_schedule']['retained_W'] == leader['stock'] == 42944
    assert row[1] - ledger[1] == padding_total == 65808, \
        'every padding register comes out of the singleton bin, and nothing else touches it'

    # 5. the leaf: the vendored three-level bootstrap, on the rung-1 row and on the leader's
    seed = Q(rung1['seed'])
    chain = [Q(value) for value in rung1['bootstrap_chain']]
    assert chain[0] == seed and len(chain) == 4, 'the chain starts at PR200\'s published leaf'
    for previous, current in zip(chain, chain[1:]):
        coarse = Q(rung1['coarse_saving'])
        assert current == (1 - coarse) * coarse + coarse * previous, 'the bootstrap recurrence'
    assert chain[-1] == Q(rung1['leaf']), 'and reproduces the published rung-1 leaf'
    leaf, leader_coarse = seed, Q(leader['coarse'])
    for _ in range(3):
        leaf = (1 - leader_coarse) * leader_coarse + leader_coarse * leaf
    assert leaf == Q(leader['leaf']) == Q(stored['point']['leaf']) \
        and Q(rung1['leaf']) < leaf < leader_coarse, \
        'the same chain on the retained row gives the leader leaf'

    # 6. the point: the assembly rule, the switch of the binding side, and the plateau
    point = stored['point']
    contract = json.loads((HERE / 'export-contract-rank3.json').read_text())
    complex_coarse = Q(point['complex_coarse'])
    assert complex_coarse == Q(contract['point']['coarse']), \
        'the complex branch must be the one the rank-3 rung already sells'
    branch = (1 - run3.BETA) * complex_coarse - run3.WEAK
    assert branch == Q(point['complex_branch']) \
        and Q(point['complex_ceiling']) == complex_coarse / (1 + complex_coarse), \
        'the branch and its ceiling, from the coarse saving alone'
    assert leaf > branch, 'the extended leaf clears the complex branch'
    assert Q(point['budget']) == Q(leader['budget']) == min(leaf, branch) == branch, \
        'so the budget is the complex branch, not the leaf'
    q = branch * (1 - 2 * run3.ETA)
    bound = (1 - run3.ETA) * q / (1 + q)
    on_the_grid = bound * 10 ** 18
    below = Q((on_the_grid.numerator - 1) // on_the_grid.denominator, 10 ** 18)
    assert Q(point['kappa']) == below and below < bound, \
        'the kappa is the assembly bound, on the grid strictly below it'
    assert point['binding'] == 'complex' and point['adjacent_grid_rejected'] is True, \
        'and the assembly rejects the adjacent 10^-18 point, so the grid step is what it costs'
    assert Q(point['tightest_constraint']) == run3.WEAK, \
        'the tightest of the 47 constraints is the weak haircut that put the budget there'
    assert point['strict_constraints'] == 47 and point['margins'] == 7
    frontier = Q(json.loads((HERE / 'references'
                             / 'pr207-coordinated-crossover.certificate.json').read_text())['kappa'])
    assert Q(point['previous_top']) == Q(contract['point']['kappa']) \
        == Q(1819302815717, 25 * 10 ** 14), 'the rung below is the one this package prices'
    assert Q(point['kappa']) > Q(contract['point']['kappa']) > frontier, 'and both are beaten'
    gain = Q(point['gain_vs_the_rank3_rung'])
    assert gain == Q(point['kappa']) / Q(contract['point']['kappa']) - 1 \
        and Q(14, 100) < gain < Q(15, 100), 'the gain over the rung below'
    assert abs(float(gain) * 100 - point['gain_vs_the_rank3_rung_percent']) < 1e-9, \
        'and its decimal twin, which the JSON records for the reader'
    cap = Q(point['kappa'])
    plateau = [entry for entry in stored['screen']['rungs'] if Q(entry['kappa']) == cap]
    assert len(plateau) == stored['screen']['plateau']['rungs_at_the_cap'] == 108, \
        'the plateau: every rung whose leaf clears the branch lands on the same point'
    assert all(entry['binding'] == 'complex' for entry in plateau) \
        and all(Q(entry['kappa']) < cap for entry in stored['screen']['rungs']
                if entry['binding'] == 'bit'), 'the two sides of the plateau'
    cheapest = min(plateau, key=lambda entry: (entry['banks'], entry['ranks']))
    assert cheapest['ranks'] == leader['ranks'] == [7, 8, 20], \
        'the leader is the cheapest rung on the plateau, and the point does not depend on it'
    assert 'MEASURED AND MACHINE-CHECKED' in stored['status'] and stored['next_step']['cap'], \
        'the module must state its status and what caps the next increment'
    return stored


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
    check_obligations(record)
    unconditionality = check_unconditionality()
    contract = check_export_contract()
    bit_contract = check_bit_export_contract()
    rung3_contract, rung3_gate = check_rank3_export_contract()
    stability = check_rank3_stability()
    rung4 = check_rank4_rung()
    bit_rung = check_bit_rung()
    bit_instance = check_bit_instancing()
    harness = check_import_harness()
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
    print('import harness  self-test %d/%d, %d bodies still missing: %s'
          % (sum(1 for ok in harness['observed'].values() if ok), len(harness['observed']),
             harness['missing'], harness['verdict'][:58]))
    print('export contract %d exports (%s), %d acceptance tests, bodies exported today: %d/%d'
          % (len(contract['required_exports']),
             ','.join(export['id'] for export in contract['required_exports']),
             len(contract['acceptance_tests']), contract['today']['bodies_present'],
             contract['today']['of_required']))
    drop = bit_contract['drop']
    print('bit twin      %d exports (%s), %d acceptance tests, bodies published by the pins: %d/%d, '
          'checker pinned from source_pins.checker_sha256 = %s'
          % (len(bit_contract['required_exports']),
             ','.join(export['id'] for export in bit_contract['required_exports']),
             len(bit_contract['acceptance_tests']), bit_contract['today']['bodies_present'],
             bit_contract['today']['of_required'],
             bit_contract['import_harness']['replay_requirement']['checker_digest'][:16]))
    print('bit drop      %d of %d bodies, %d anchored; %s complete, %s absent; the gate decides '
          'A2 and A3 on the published bytes and the default import still refuses (exit %d) what '
          'the partial report shows (exit %d)'
          % (drop['bodies'], sum(len(export['bodies'])
                                 for export in bit_contract['required_exports']), drop['anchored'],
             ' and '.join(drop['exports_complete']), ' '.join(drop['exports_absent']),
             drop['gate']['default_exit_code'], drop['gate']['exit_code']))
    rung3_point = rung3_contract['point']
    print('rank-3 rung   %d exports (%s), %d acceptance tests, bodies exported by the row: '
          '%d/%d, padding %d; the point %s binding %s, %+.4f%% over the published top, '
          'complex ceiling %.6e'
          % (len(rung3_contract['required_exports']),
             ','.join(export['id'] for export in rung3_contract['required_exports']),
             len(rung3_contract['acceptance_tests']),
             rung3_contract['today']['bodies_present'], rung3_contract['today']['of_required'],
             rung3_contract['rung']['geometry']['padding_per_bank'],
             Q(rung3_point['kappa']), rung3_point['binding'],
             rung3_point['gain_vs_published_top_percent'],
             rung3_point['complex_ceiling_decimal']))
    rung3_harness = rung3_contract['import_harness']
    print('rank-3 gate   %d bodies across %d exports in the importer\'s dialect: self-test '
          '%d/%d, the real drop refused (exit %s) and reportable in part (exit %s); replay NOT '
          'RUN, because the row publishes no checker digest to accept'
          % (rung3_contract['today']['required_bodies'],
             len(rung3_contract['required_exports']),
             sum(1 for ok in rung3_gate.values() if ok), len(rung3_gate),
             rung3_harness['exit_codes']['2'][:1] and 2, 4))
    stable = stability['stability']
    print('rank-3 stabil %d heads of #233 across %d rows, the rung on %d of them (the rest miss '
          'it by %d registers); price stable %s (kappa %s), next rung stable %s; %d width-66 '
          'rows in the repository, the rung on %d (both #233)'
          % (stable['heads'], stable['distinct_rows'], stable['heads_where_the_rung_exists'],
             stability['rows'][stability['heads'][0]['row']]['families_at_width']['3']
             ['registers_short'], stable['price_stable'], stable['kappas'][0],
             stable['next_rung_stable'], len(stability['corpus']['rows']),
             sum(1 for row in stability['corpus']['rows'] if row['rank3_eligible'])))
    rung4_tiling = rung4['mixed_tilings']
    print('rank-4 rung   %d items, volume %d banks, padded schedule %d banks of %d blocks + %d '
          'registers: %s (%d slots short), so the priced bank count cannot host the items (%s); '
          'the mixed tiling exists at %s of %d bank counts (%d patterns), the lightest drawing '
          '%d of the bank, and the best priced reaches coarse %s against the volume ledger\'s %s'
          % (rung4['rung']['n4'], rung4['rung']['volume_banks'],
             rung4['rung']['padded_schedule']['banks'],
             rung4['rung']['padded_schedule']['blocks_per_bank'],
             rung4['rung']['padded_schedule']['padding_registers_per_bank'],
             'saturated' if rung4['rung']['padded_schedule']['saturated'] else 'not saturated',
             rung4['rung']['padded_schedule']['slack_slots'],
             rung4['rung']['priced_bank_count_hosts_its_items'],
             rung4_tiling['feasible_bank_counts'], rung4_tiling['bank_counts_examined'],
             rung4_tiling['patterns_enumerated'],
             rung4_tiling['lightest_padding_registers_per_bank'],
             Q(rung4_tiling['best']['coarse']), Q(rung4['point']['rank4_priced']['coarse'])))
    print('rank-4 point  rank 3 %s -> rank 4 %s, kappa moved %s: the coarse saving rises '
          '%+.4f%% (priced ledger) and %+.4f%% (best tiled), and the lever is the bit leaf -- the '
          'next grid point of kappa needs %s, 7.5e-4 needs %s, 8e-4 needs %s'
          % (Q(rung4['point']['rank3']['kappa']), Q(rung4['point']['rank4_priced']['kappa']),
             rung4['point']['kappa_moved'], rung4['point']['delta_coarse_priced_percent'],
             rung4['point']['delta_coarse_tiled_percent'],
             Q(rung4['targets'][0]['required_bit_leaf']),
             Q(rung4['targets'][1]['required_bit_leaf']),
             Q(rung4['targets'][2]['required_bit_leaf'])))
    bit_point, bit_leader = bit_rung['point'], bit_rung['leader']
    print('bit rung      %d rungs of up to %d families of the retained bit row, %d absorbable '
          '(%s); %d of them land on the same kappa; leader %s at %d banks, leaf %s -> %s, binding '
          '%s, the point %s = %s (%+.4f%% over the rank-3 rung), %d strict constraints'
          % (bit_rung['screen']['rungs_priced'], bit_rung['screen']['depth'],
             len(bit_rung['absorbable']), bit_rung['absorbable'],
             bit_rung['screen']['plateau']['rungs_at_the_cap'], bit_leader['ranks'],
             bit_leader['banks'], bit_rung['rung1']['leaf'], bit_leader['leaf'], bit_point['binding'],
             Q(bit_point['kappa']), bit_point['kappa_decimal'],
             bit_point['gain_vs_the_rank3_rung_percent'], bit_point['strict_constraints']))
    assigned = bit_instance['totals']
    print('B1 instanced  %d items addressed by rule over %d banks (rank 7: %d x %d blocks + %d '
          'padding, rank 8: %d x %d + 0, rank 20: %d x %d + %d), %d registers of padding named '
          'and digested, induced row W %d / mass %d / children %d; the pins still export no '
          'occurrence of these families'
          % (assigned['items'], assigned['banks'],
             bit_instance['inventories']['7']['banks'],
             bit_instance['inventories']['7']['capacity_per_bank'],
             bit_instance['padding']['draws']['7']['registers'],
             bit_instance['inventories']['8']['banks'],
             bit_instance['inventories']['8']['capacity_per_bank'],
             bit_instance['inventories']['20']['banks'],
             bit_instance['inventories']['20']['capacity_per_bank'],
             bit_instance['padding']['draws']['20']['registers'],
             assigned['padding_registers'], bit_instance['induced_ledger']['stock_after'],
             bit_instance['induced_ledger']['mass_after'],
             bit_instance['induced_ledger']['children_after']))
    print('bit cap       the extended leaf clears the complex branch, so the budget is the complex '
          'side: this rung reaches the branch and its ceiling %s caps every further bit '
          'absorption' % bit_point['complex_ceiling'])
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
