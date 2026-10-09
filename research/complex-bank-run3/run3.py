#!/usr/bin/env python3
"""Rungs 3 and 4 of the bank ladder: the complex ledger's bankable remainder, priced.

Rung 2 (PR224, `research/complex-bank-run2`) absorbs the complex word's rank-11 family and
lands on the *new* complex ceiling, so every further rung must again raise the complex
coarse saving.  This package prices the rest of that ledger, exactly:

* **rung 3** absorbs the complex rank-16 family (264 children per vertex, volume
  12,672 = 66 * 192 whole banks) on top of rung 2;
* **rung 4** adds the rank-20 family (66 per vertex, volume 3,960 = 66 * 60) and is the
  **top of the complex-side ladder**: after it no family of the remaining ledger has a
  whole-bank volume, so the accounting criterion the built rungs use is exhausted.

What this script does, all in exact rational arithmetic from pinned inputs:

1. **Calibration, frontier (#207).**  Reproduces #207's published `kappa` from its own
   `a_bit`/`a_complex` in the assembly convention of the queue's latest rungs
   (`eta = beta = 10^-24`, `weak = 10^-30`, `10^-18` grid) -- exactly, not to a tolerance.
2. **Calibration, rung 1 (#219).**  Rebuilds rung 1 by importing the vendored #219 package
   itself (`references/pr219-run1/`), reproducing its published
   `kappa = 700427501305159/10^18` and its complex-ceiling landing.
3. **Calibration, rung 2 (#224).**  Rebuilds rung 2 (`ledger3.py`) from the pinned complex
   profile, reproducing PR224's published complex coarse saving and grid point exactly.
4. **Rungs 3 and 4** (`ledger3.py`): whole-bank volume, retained row identity, stock drop
   equal to the bank count, both paid moments, and the eligibility scan that shows the
   ladder's top.
5. **The assemblies**: PR184/#219's unchanged 47-constraint assembly at each rung's budget,
   with the adjacent `10^-18` point rejected and the ceiling gap recorded.
6. **What beating the top would take**: the complex coarse saving each round target needs,
   and the point at which the bit branch starts binding instead.
7. **The blocker**, as facts rather than assertions (`obligations.json` C1-C7 + T1, plus
   #219's inherited R1-R4).
8. **T1's enumeration** (`schedule66.py`): the admissible uniform tilings of a width-66
   bank, exhaustively.  Rank 11 tiles alone (four patterns, rung 2's 531 the tightest);
   ranks 16 and 20 tile alone only *above* the bank counts their own volume criterion
   prices (198 and 66, against 192 and 60); and no uniform tiling absorbs two bins at once.
9. **The prototype** (`prototype66.py`): the bank schedule those rungs need, at the bank
   count their capacity requires -- every bank exactly filled (four rank-16 blocks and 2
   registers of padding, three rank-20 blocks and 6), the item-to-block assignment, the
   padding drawn from a retained bin, the ledger it induces (the stock falling by exactly
   the bank count) and the price of every padding option.  The padded schedule beats the
   volume-criterion accounting it replaces, so the certificate's top rung is the padded one.
10. **The width question** (`widths66.py`): the bank width is the word's modulus, so a scan
   over widths is a scan over words.  66 is the smallest modulus the pinned row admits (at 65
   its rank mass exceeds `W * w`), and every wider modulus is a different word whose stock and
   deficit this ledger does not fix -- recorded, not priced.  At the pinned width the scan
   reproduces this package's own top exactly, which is its calibration.
11. **The instanced schedule** (`instantiate66.py`): C1's combinatorial half and the C5-C7
   inventories -- every item of the three families addressed to a bank, a block and an offset,
   with the bank tables, the padding draw, the digests and a machine-read statement of what the
   pins still do not export (the residual projectors, not the counts).

    python3 -B run3.py [--out certificate.json]
"""
import argparse
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import instantiate66  # noqa: E402
import ledger3  # noqa: E402  (local module, imported after the path is set)
import pins  # noqa: E402
import prototype66  # noqa: E402
import schedule66  # noqa: E402
import widths66  # noqa: E402

REFERENCES = HERE / 'references'
FRONTIER = REFERENCES / 'pr207-coordinated-crossover.certificate.json'
PR193 = REFERENCES / 'pr219-run1' / 'references' / 'pr193-source-assisted-v4.certificate.json'
PR205 = REFERENCES / 'pr219-run1' / 'references' / 'pr205-packed.certificate.json'

# The convention of the queue's latest rungs (#207, #219, #224).
ETA = BETA = Q(1, 10 ** 24)
WEAK = Q(1, 10 ** 30)
GRID = 10 ** 18
# The convention of PR208's pricing model, for the independent replica.
STOP_208 = Q(1, 10 ** 9)
ETA_208 = Q(1, 10 ** 8)
GRID_208 = 10 ** 10
RUN1_KAPPA = Q(700427501305159, 10 ** 18)          # #219's published rung-1 claim
RUN2_KAPPA = Q(354145785295363, 5 * 10 ** 17)      # PR224's published rung-2 claim
RUN2_COARSE = Q(708793603125109, 10 ** 18)         # PR224's published rung-2 coarse saving
RUN2_REPLICA = Q(3541457, 5 * 10 ** 9)             # PR208's priced rung-2 target
RUNGS = (11, 16, 20)                               # every whole-bank family of this ledger
TARGETS = (Q(72, 10 ** 5), Q(75, 10 ** 5), Q(8, 10 ** 3), Q(1, 10 ** 3))


def frontier_kappa(bit_saving, complex_saving):
    """The queue's assembly rule: budget, closed-form bound, floor to the grid."""
    a = min(bit_saving, (1 - BETA) * complex_saving - WEAK)
    q = a * (1 - 2 * ETA)
    bound = (1 - ETA) * q / (1 + q)
    z = bound * GRID
    return a, bound, Q((z.numerator - 1) // z.denominator, GRID)


def replica_kappa(bit_saving, complex_saving):
    """PR208's convention, on its own grid."""
    budget = min(bit_saving, (1 - STOP_208) * complex_saving - Q(1, GRID_208))
    q = budget * (1 - 2 * ETA_208)
    minimum = (1 - ETA_208) * q / (1 + q)
    kappa = Q(minimum.numerator * GRID_208 // minimum.denominator, GRID_208)
    if kappa == minimum:
        kappa -= Q(1, GRID_208)
    return budget, minimum, kappa


def kappa_of_budget(budget):
    """The queue's assembly rule on a given budget, floored to the 10^-18 grid."""
    q = budget * (1 - 2 * ETA)
    z = ((1 - ETA) * q / (1 + q)) * GRID
    return Q((z.numerator - 1) // z.denominator, GRID)


def complex_for_target(target, bit_leaf):
    """The smallest complex coarse saving on the 10^-18 grid that reaches `target`.

    `kappa` is monotone in the budget, so bisect the budget on the grid, then read the
    complex coarse saving that produces it (`a = (1 - beta) * C - weak`) and round up.
    The bit leaf is what stops the search when it is the smaller branch there.
    """
    low, high = 1, GRID                      # budget units on the 10^-18 grid
    assert kappa_of_budget(Q(high, GRID)) >= target, 'target above the assembly bound'
    while low < high:
        mid = (low + high) // 2
        if kappa_of_budget(Q(mid, GRID)) >= target:
            high = mid
        else:
            low = mid + 1
    budget = Q(low, GRID)
    if Q(bit_leaf) < budget:
        # No complex saving can reach the target while the bit branch is the smaller
        # one: the budget itself is capped by the bit leaf, so a new bit word is needed.
        return dict(target=str(target), budget=str(budget), coarse=None, kappa=None,
                    binding='bit', needs_new_bit=True,
                    kappa_at_the_bit_ceiling=str(kappa_of_budget(Q(bit_leaf))),
                    required_bit_leaf=str(budget))
    exact = (budget + WEAK) / (1 - BETA)
    z = exact * GRID
    coarse = Q(-((-z.numerator) // z.denominator), GRID)      # ceil to the grid
    a, _, kappa = frontier_kappa(bit_leaf, coarse)
    assert (a == (1 - BETA) * coarse - WEAK) or a == Q(bit_leaf), 'branch identity'
    if a != Q(bit_leaf):
        assert kappa >= target, 'the rounded grid point must reach the target'
    return dict(target=str(target), budget=str(budget), coarse=str(coarse),
                coarse_decimal=float(coarse), kappa=str(kappa),
                binding='complex' if a == (1 - BETA) * coarse - WEAK else 'bit',
                needs_new_bit=(a != (1 - BETA) * coarse - WEAK))


def serial(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def bank_evidence():
    """What the pins say about bank constructions, read rather than assumed."""
    supplier = json.loads(PR193.read_text())
    frontier = json.loads(FRONTIER.read_text())

    def keys_with(node, needle):
        found = []

        def walk(value, path):
            if isinstance(value, dict):
                for key, child in value.items():
                    walk(child, path + '/' + str(key))
            elif isinstance(value, list) and value and isinstance(value[0], (dict, list)):
                walk(value[0], path + '[0]')
            else:
                if needle in path.lower():
                    found.append(path)
        walk(node, '')
        return sorted(found)

    packed = json.loads(PR205.read_text())
    return dict(
        complex_supplier_has_bank_keys=keys_with(supplier, 'bank'),
        frontier_certificate_has_bank_keys=keys_with(frontier, 'bank'),
        pinned_bit_bank_construction=dict(
            source='references/pr219-run1/references/pr205-packed.certificate.json (#205)',
            physical_banks=int(packed['physical']['banks']),
            physical_copies=packed['physical']['copies'],
            gauge_roles=packed['physical']['gauge_roles'],
            distinct_gauges=packed['physical']['distinct_gauges'],
            bank_controls_keys=sorted(packed['bank_controls']),
            note="the pinned construction banks the bit word's selected entrance-gauge "
                 'exteriors into width-72 banks; it is the only bank construction in the '
                 'pins'),
        complex_family_inventory=None,
        complex_family_inventory_note='the only occurrence inventory in the pins is '
                                      "#219's bit-side inputs/absorbed-occurrences.json "
                                      '(rank 22); the complex rank-11 family of PR224, and '
                                      'the rank-16 and rank-20 families this package '
                                      'absorbs, have no such enumeration, so the '
                                      'item-to-block map of C1 has no starting inventory',
    )


def assemble(supplier, budget, complex_saving, kappa):
    """PR184/#219's unchanged 47-constraint assembly at a given grid point."""
    assembly = ledger3.load('run3_assembly', ledger3.RUN1 / 'paired_cube_assembly.py')
    out = assembly.assembly(budget, complex_saving, supplier['assembly']['finite_bridge'],
                            kappa, eta=ETA, beta=BETA)
    assert len(out['strict_constraints']) == 47 and len(out['margins']) == 7
    return dict(minimum_constraint=min(out['strict_constraints'].values()))


def rung_record(supplier, step, leaf, index):
    """Price one rung's assembly and record the ledger around it."""
    coarse = Q(step['saving'])
    budget, bound, kappa = frontier_kappa(leaf, coarse)
    out = assemble(supplier, budget, coarse, kappa)
    rejected = True
    try:
        assemble(supplier, budget, coarse, kappa + Q(1, GRID))
    except AssertionError:
        pass
    else:
        rejected = False
    assert rejected, 'the adjacent 10^-18 point must be rejected'
    ceiling = ledger3.ceiling(coarse)
    assert 0 <= ceiling - kappa < Q(1, GRID), 'the rung must sit on its own ceiling'
    return dict(rung=index, family=step['family'], kappa=kappa, coarse=coarse,
                binding='complex' if budget == (1 - BETA) * coarse - WEAK else 'bit',
                complex_ceiling=ceiling, ceiling_gap=ceiling - kappa,
                bit_leaf_headroom=Q(leaf) - budget, assembly=out,
                adjacent_grid_rejected=rejected)


def build():
    interval = ledger3.engine()
    schedule, arithmetic = ledger3.run1()
    frontier = json.loads(FRONTIER.read_text())
    supplier = json.loads(PR193.read_text())
    supplier['assembly']['finite_bridge']['rows']['degree_gap'] = Q(
        supplier['assembly']['finite_bridge']['rows']['degree_gap'])

    # --- 1. the frontier's own number, in this convention ----------------------
    a_bit = Q(frontier['a_bit'])
    a_complex = Q(frontier['a_complex'])
    _, _, frontier_published = frontier_kappa(a_bit, a_complex)
    assert frontier_published == Q(frontier['kappa']), 'the frontier claim must reproduce'
    calibration_frontier = dict(
        published=str(Q(frontier['kappa'])), reproduced=str(frontier_published), equal=True,
        a_bit=str(a_bit), a_complex=str(a_complex), binding=frontier['binding'])

    # --- 2. rung 1, rebuilt by #219's own vendored code ------------------------
    result1 = arithmetic.build(schedule.build())
    kappa1 = result1['after_assembly']['kappa']
    assert kappa1 == RUN1_KAPPA, "rung 1 must reproduce #219's published grid point"
    assert result1['after_assembly']['binding'] == 'complex', 'rung 1 binds on complex'
    complex_coarse_1 = result1['complex_coarse']
    ceiling_1 = ledger3.ceiling(complex_coarse_1)
    assert 0 <= ceiling_1 - kappa1 < Q(1, GRID), 'rung 1 sits on the complex ceiling'
    leaf = result1['ordinary_leaf']
    calibration_run1 = dict(
        published=str(RUN1_KAPPA), reproduced=str(kappa1), equal=True,
        binding='complex', complex_coarse=str(complex_coarse_1),
        complex_ceiling=str(ceiling_1), ceiling_gap=str(ceiling_1 - kappa1),
        bit_leaf=str(leaf), bit_coarse_after=str(result1['bit_coarse_after']),
        conclusion='rung 1 already sits on the complex branch ceiling, so every further '
                   'rung has to raise the complex supplier\'s own coarse saving')

    # --- 3. the complex side: base, rung 2, rungs 3 and 4 ---------------------
    part = ledger3.side(FRONTIER, interval, RUNGS)
    assert Q(part['base_saving']) == a_complex, \
        'the pinned complex supplier is the one the frontier prices'
    assert [step['family'] for step in part['ladder']] == list(RUNGS), 'rung order'
    assert Q(part['ladder'][0]['saving']) == RUN2_COARSE, "rung 2 must reproduce PR224"
    assert part['final_eligibility'] == [], 'the ladder must be exhausted at the top'

    # --- 3b. T1: the width-66 tilings the rungs above rung 2 owe --------------
    tiling = schedule66.tiling()
    families = tiling['families']
    assert families['11']['priced_banks'] == families['11']['capacity_minimum_banks'] \
        == part['ladder'][0]['banks'] == 531, \
        "rung 2's rank-11 absorption must be the tightest admissible tiling"
    for family, entry in families.items():
        assert entry['whole_bank_volume'] == (entry['volume_registers'] % tiling['width'] == 0)
        assert entry['capacity_minimum_banks'] == -(-entry['three_copies']
                                                    // entry['capacity_per_bank'])
        assert entry['fits_the_priced_banks'] == (entry['priced_banks']
                                                  >= entry['capacity_minimum_banks'])
    assert not families['16']['fits_the_priced_banks'], 'rung 3 prices 192 of 198 banks'
    assert not families['20']['fits_the_priced_banks'], 'rung 4 prices 60 of 66 banks'
    assert families['11']['divides_width'] and not families['16']['divides_width'] \
        and not families['20']['divides_width'], 'rank-divides-width is what separates them'
    assert [step['banks'] for step in part['ladder']] \
        == [families[f]['priced_banks'] for f in ('11', '16', '20')], \
        'the ledger must price exactly the volume counts the tiling scan examines'
    assert tiling['findings']['mixed_uniform_tilings'] == 0, \
        'no uniform tiling may absorb two bins at once'
    assert all(not tiling['subsets'][key]['admissible']
               for key in ('11,16', '11,20', '16,20', '11,16,20')), \
        'every mixed subset must be infeasible'
    assert tiling['subsets']['16,20']['closest_attempt']['overflow'] == 18, \
        'the tightest mixed attempt on {16, 20} must be 84 registers into a 66 bank'

    rungs = [rung_record(supplier, step, leaf, index + 3)
             for index, step in enumerate(part['ladder'][1:])]

    # --- 3c. the prototype: the padded schedule those rungs need --------------
    padded = prototype66.priced_ladder(FRONTIER, interval)
    assert Q(padded['base_saving']) == a_complex, 'the prototype prices the same supplier'
    assert [step['family'] for step in padded['ladder']] == list(RUNGS), 'rung order'
    pad_rung2 = padded['ladder'][0]
    assert pad_rung2['banks'] == part['ladder'][0]['banks'] == 531 \
        and Q(pad_rung2['saving']) == RUN2_COARSE, \
        'the prototype must reproduce rung 2 exactly, and it needs no padding there'
    assert pad_rung2['padding_per_bank'] == 0, 'rank 11 tiles its banks on its own'
    for step, priced_step in zip(part['ladder'], padded['ladder']):
        assert step['banks'] <= priced_step['banks'], 'the padded count is the upper one'
        assert priced_step['banks'] == families[str(priced_step['family'])][
            'capacity_minimum_banks'], 'the prototype must use the capacity minimum'
        assert priced_step['stock_drop'] == priced_step['banks'], \
            'the stock must fall by exactly the bank count'
        assert priced_step['pattern_sum'] == 66, 'every bank must be exactly filled'
        assert priced_step['blocks_per_bank'] * priced_step['banks'] \
            == priced_step['items'], 'the schedule must be saturated'
    assert all(step['whole_bank_volume'] for step in padded['ladder']), \
        'the padded families are the ones the volume criterion already selects'
    assert padded['ladder'][1]['banks'] == 198 and padded['ladder'][2]['banks'] == 66
    assert padded['ladder'][1]['padding_registers'] == 396 \
        and padded['ladder'][2]['padding_registers'] == 396, 'the padding of T1'
    assert padded['exhaustive'] and padded['residual_eligibility'] == [], \
        'the padded top must still exhaust the whole-bank criterion'
    for step in padded['ladder']:
        assert step['options'] >= 1, 'every step must offer a padding option'
        assert all(Q(option['saving']) <= Q(step['saving'])
                   for option in step['alternatives']), 'the chosen option is the best one'
        assert any(Q(option['saving']) == Q(step['saving'])
                   for option in step['alternatives']), 'the best must be among the options'
        assert all(Q(option['saving']) > Q(part['base_saving'])
                   for option in step['alternatives']), \
            'every padding option must raise the complex coarse saving'
        assert step['whole_bank_volume'], 'the padded families are the volume ones'
    assert all(Q(step['saving']) > Q(part['base_saving']) for step in padded['ladder']), \
        'every rung must raise the complex coarse saving'
    padded_rungs = [rung_record(supplier, step, leaf, index + 3)
                    for index, step in enumerate(padded['ladder'][1:])]

    # --- 3d. is the bank width a dial?  (widths66.py) ------------------------
    padded_base = ledger3.three_copies(ledger3.profile(
        json.loads(FRONTIER.read_text())['complex_profile']))
    ledger3.check_row(padded_base)
    assert [padded_base['W'], padded_base['N'], padded_base['total_rank']] == [
        part['three_copy']['W'], part['three_copy']['deficit'], part['three_copy']['mass']], \
        'the scan must start from the same three-copy row the ladder prices'
    scan = {str(width): widths66.scan_width(padded_base, width, interval, leaf,
                                             ladder=padded if width == widths66.PINNED_WIDTH
                                             else None)
            for width in widths66.WIDTHS}
    pinned_width = str(widths66.PINNED_WIDTH)
    assert scan[pinned_width]['priced'] \
        and scan[pinned_width]['kappa'] == Q(padded_rungs[-1]['kappa']), \
        'the width scan must reproduce this package\'s top at the pinned width'
    assert scan[pinned_width]['banks'] == padded['ladder'][0]['banks'] \
        + padded['ladder'][1]['banks'] + padded['ladder'][2]['banks']
    narrower = [w for w, entry in scan.items() if not entry['poseable']]
    assert narrower, 'some narrower modulus must be unposeable, or the claim is empty'
    assert all(int(w) < 66 for w in narrower), 'only narrower moduli may be unposeable'
    assert all(entry['poseable'] for w, entry in scan.items() if int(w) >= 66), \
        'every width at or above the pinned one must be poseable'
    assert min(int(w) for w, entry in scan.items() if entry['poseable']) == 66, \
        '66 must be the smallest modulus the pinned row admits'
    assert all(not entry['priced'] for w, entry in scan.items() if int(w) > 66), \
        'no width other than the pinned one may be priced (it is a different word)'
    widest = max(scan, key=lambda w: scan[w]['density_decimal'] if scan[w]['poseable'] else 0)
    assert widest == pinned_width, 'the pinned word must be the densest row in the scan'

    # --- 3e. the instanced schedule (instantiate66.py) ------------------------
    construction = instantiate66.build(padded_base, interval, padded)
    for family in RUNGS:
        inv = construction['inventories'][str(family)]
        step = next(s for s in padded['ladder'] if s['family'] == family)
        assert inv['banks'] == step['banks'] and inv['items'] == step['items'], 'schedules agree'
        assert inv['padding_registers'] == step['padding_registers'], 'and the padding'
        assert inv['banks'] * inv['capacity_per_bank'] == inv['items'], 'saturated'
        assert inv['banks'] * (inv['padding_per_bank'] + family * inv['capacity_per_bank']) \
            == inv['banks'] * 66, 'every bank exactly filled'
        assert len(inv['bank_table_digest']) == 64, 'the digest must be recorded'
    assert construction['totals']['banks'] == sum(
        padded['ladder'][i]['banks'] for i in range(3)), '795 banks over the three rungs'
    assert construction['totals']['items'] == sum(
        construction['inventories'][str(f)]['items'] for f in RUNGS)
    assert construction['pins_gap']['complex_supplier_bank_keys'] == [], \
        'the complex supplier must still have no bank construction in the pins'
    assert construction['pins_gap']['complex_supplier_status_says_no_operation_program'], \
        "the supplier's own status must say the operation program is not exported"
    top = padded_rungs[-1]                      # the realizable top, not the volume one
    kappa_top, coarse_top = top['kappa'], top['coarse']
    assert coarse_top == Q(padded['ladder'][-1]['saving'])
    assert kappa_top > RUN2_KAPPA, 'the top rung must beat rung 2'
    assert kappa_top > rungs[-1]['kappa'], \
        'the padded top must beat the unpadded count it replaces'

    # --- 4. the independent replica at PR208's convention ---------------------
    bit_row = ledger3.profile(frontier['bit_profile'])
    ledger3.check_row(bit_row)
    bit_absorbed = ledger3.absorb(ledger3.three_copies(bit_row), 22)
    bit_coarse = arithmetic.certify(interval, bit_absorbed['retained'], True)['saving']
    replica = []
    for index, step in enumerate(part['ladder']):
        _, _, value = replica_kappa(bit_coarse, Q(step['saving']))
        replica.append(dict(family=step['family'], kind='rung %d' % (index + 2),
                            kappa=str(value), published=('3541457/5000000000'
                                                         if index == 0 else None),
                            matches_published=(value == RUN2_REPLICA if index == 0 else None)))
    assert replica[0]['matches_published'] is True, "PR208's priced rung 2 must reproduce"

    # --- 5. what beating the top would take ----------------------------------
    supplier_field = Q(supplier['complex_saving'])
    assert supplier_field < a_complex, 'the supplier field sits below the certified moment'
    _budget_c, _bound_c, conservative_top = frontier_kappa(leaf, supplier_field + (
        coarse_top - Q(part['ladder'][0]['saving'])))
    needs = []
    for target in TARGETS:
        info = complex_for_target(target, leaf)
        info['gain_vs_top'] = (Q(info['coarse']) / coarse_top - 1
                               if info['coarse'] is not None else None)
        needs.append(info)

    certificate = dict(
        status='MODEL AND TARGET, NOT CONSTRUCTED: the ledger and the bank schedule above '
               'rung 2 are certified here -- whole-bank volumes, the padded width-66 schedule '
               'itself (banks, blocks per bank, item-to-block assignment, padding draw), the '
               'retained row identities with the stock falling by exactly the bank count, both '
               'paid moments on the 10^-18 grid, and the two 47-constraint assemblies -- but '
               'the physical construction on the complex supplier is still owed '
               '(obligations.json C1-C7, plus #219\'s inherited R1-R4; T1 is settled by the '
               'schedule prototype and its negative uniform-tiling result). The kappa below '
               'is conditional on those and is not a completed finite witness.',
        rung=4,
        kappa=kappa_top, decimal=float(kappa_top), binding=top['binding'],
        gain_vs_rung1=kappa_top / RUN1_KAPPA - 1,
        gain_vs_rung2=kappa_top / RUN2_KAPPA - 1,
        gain_vs_frontier=kappa_top / Q(frontier['kappa']) - 1,
        calibrations=dict(frontier=calibration_frontier, run1=calibration_run1,
                          run2=dict(published=str(RUN2_KAPPA), reproduced=str(
                              Q(part['ladder'][0]['saving'])), equal=True,
                              coarse=str(RUN2_COARSE),
                              note='rebuilt here by this package\'s own ledger module '
                                   'from the pinned complex profile, not imported')),
        ledgers=part,
        tiling=tiling,
        rungs=rungs,
        padded_schedule=padded,
        padded_rungs=padded_rungs,
        width_scan=scan,
        construction=construction,
        replica=replica,
        top=dict(kappa=str(kappa_top), coarse=str(coarse_top), binding=top['binding'],
                 families_absorbed=list(RUNGS), banks=sum(step['banks']
                                                          for step in padded['ladder']),
                 banks_by_volume_criterion=sum(step['banks'] for step in part['ladder']),
                 schedule='padded prototype (prototype66.py): 531 + 198 + 66 = 795 banks, '
                          'the rank-16 and rank-20 banks padded with 2 and 6 registers of '
                          'retained blocks',
                 stock=padded['final']['W'], rank_mass=padded['final']['mass'],
                 children=padded['final']['children'],
                 families_left=padded['final']['families'],
                 largest_child=padded['final']['largest_child'],
                 eligibility_exhausted=True,
                 ceiling=str(top['complex_ceiling']), ceiling_gap=str(top['ceiling_gap']),
                 note='no family of the remaining complex ledger has a whole-bank volume, '
                      'so the accounting criterion the built rungs use cannot be applied '
                      'again without a different bank width or a mixed tiling that reopens '
                      'the volume condition; the T1 scan of this certificate shows the '
                      'mixed tiling has no uniform solution either, and that rungs 3 and 4 '
                      'are priced at 192 and 60 banks where their own capacities require '
                      '198 and 66'),
        needed_for=needs,
        conservative_variant=dict(
            supplier_field=str(supplier_field), certified_moment=str(a_complex),
            delta=str(supplier_field - a_complex),
            top_kappa_on_the_field=str(conservative_top),
            note='PR193 publishes 219037/312500000 = 7.009184e-4, its value on the 10^-10 '
                 'grid, 4.3859411e-11 below the 10^-18 certified paid moment of the same '
                 'profile; the ladder above is priced on the certified moment, which #207 '
                 "and #219's rung 1 also price. A reviewer who prefers the coarser field "
                 'sees a smaller top rung: recorded here rather than hidden.'),
        blocked_on=bank_evidence(),
        obligations=['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'T1', 'R1', 'R2', 'R3', 'R4'],
        comparison=dict(rung1=str(RUN1_KAPPA), rung2=str(RUN2_KAPPA), frontier=str(
            Q(frontier['kappa'])), pr208_priced_rung2=str(RUN2_REPLICA),
            volume_criterion_top=str(rungs[-1]['kappa']),
            padded_top=str(padded_rungs[-1]['kappa']),
            note='the volume-criterion rows are the accounting the criterion gives; the padded '
                 'prototype is the schedule a width-66 bank actually admits, and it is '
                 'higher, so the top of the ladder is the padded rung 4'),
        source_pins=pins.manifest(),
    )
    return certificate


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out', type=Path, default=HERE / 'certificate.json')
    args = parser.parse_args()
    sys.set_int_max_str_digits(0)
    assert not sys.flags.optimize, 'assertions must stay enabled'
    record = serial(build())
    args.out.write_text(json.dumps(record, indent=1, sort_keys=True) + '\n', newline='\n')
    print('frontier  kappa = %s (reproduced exactly)' % record['calibrations']['frontier']['published'])
    print('rung 1    kappa = %s (binding complex, ceiling gap %s)'
          % (record['calibrations']['run1']['published'],
             record['calibrations']['run1']['ceiling_gap']))
    print('rung 2    coarse %s, kappa %s (reproduced exactly)'
          % (record['calibrations']['run2']['coarse'], record['calibrations']['run2']['published']))
    for step, rung in zip(record['ledgers']['ladder'][1:], record['rungs']):
        print('volume    rank %-3s volume %-7s = %-4s banks   coarse %-19s kappa %-19s %+.4f%% vs rung 2'
              % (step['family'], step['volume'], step['banks'], step['saving'],
                 rung['kappa'], float(Q(rung['kappa']) / RUN2_KAPPA - 1) * 100))
    for step, rung in zip(record['padded_schedule']['ladder'][1:], record['padded_rungs']):
        print('prototype rank %-3s %4d items = %4d banks x %d blocks + %d pad  coarse %-19s '
              'kappa %-19s %+.4f%% vs rung 2'
              % (step['family'], step['items'], step['banks'], step['blocks_per_bank'],
                 step['padding_per_bank'], step['saving'], rung['kappa'],
                 float(Q(rung['kappa']) / RUN2_KAPPA - 1) * 100))
    print('top       kappa = %s = %.17g  (binding %s, %+.4f%% over rung 1, %+.4f%% over rung 2, '
          '%+.4f%% over the frontier)'
          % (record['kappa'], float(Q(record['kappa'])), record['binding'],
             float(Q(record['gain_vs_rung1'])) * 100, float(Q(record['gain_vs_rung2'])) * 100,
             float(Q(record['gain_vs_frontier'])) * 100))
    print('top row   W=%s rank mass=%s children=%s families=%s largest child=%s (padded ledger)'
          % (record['top']['stock'], record['top']['rank_mass'], record['top']['children'],
             record['top']['families_left'], record['top']['largest_child']))
    print('exhausted %s (families with a whole-bank volume left)'
          % record['padded_schedule']['residual_eligibility'])
    for need in record['needed_for']:
        if need['coarse'] is None:
            print('to reach  %-8s needs a NEW BIT WORD: the bit leaf %s caps the budget at %s '
                  'and the target needs %s on the bit side'
                  % (need['target'], record['calibrations']['run1']['bit_leaf'][:12] + '...',
                     need['kappa_at_the_bit_ceiling'], need['required_bit_leaf']))
        else:
            print('to reach  %-8s needs complex coarse %-20s (%+.3f%% over the top, binding %s)'
                  % (need['target'], need['coarse'], float(Q(need['gain_vs_top'])) * 100,
                     need['binding']))
    print('replica   rung 2 %s matches PR208: %s; rungs 3/4 %s'
          % (record['replica'][0]['kappa'], record['replica'][0]['matches_published'],
             [r['kappa'] for r in record['replica'][1:]]))
    print('blocked   complex supplier bank keys: %s; pinned bit bank construction: %s banks'
          % (record['blocked_on']['complex_supplier_has_bank_keys'],
             record['blocked_on']['pinned_bit_bank_construction']['physical_banks']))
    unpose = sorted(int(w) for w, entry in record['width_scan'].items()
                    if not entry['poseable'])
    print('widths    pinned row unposeable at %s; priced widths: [%s] (the modulus is the word)'
          % (unpose, ','.join(w for w, entry in record['width_scan'].items()
                              if entry['priced'])))
    inst = record['construction']['inventories']
    print('instanced %s items addressed over %d banks; padding %d registers (%s of the kept '
          'rank-1 bin); digests %s'
          % (record['construction']['totals']['items'], record['construction']['totals']['banks'],
             record['construction']['totals']['padding_registers'],
             record['construction']['totals']['padding_share_of_the_kept_bin'][:12] + '...',
             [inst[str(f)]['bank_table_digest'][:12] for f in RUNGS]))
    print('write     ' + str(args.out))


if __name__ == '__main__':
    main()
