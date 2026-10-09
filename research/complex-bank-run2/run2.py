#!/usr/bin/env python3
"""Price rung 2 of the bank ladder and record exactly what blocks it.

Rung 1 (#219) absorbs the bit word's rank-22 bin into 6,116 width-72 banks.  Rung 2
would additionally absorb the complex supplier's rank-11 bin into that supplier's own
banks, which is the only way to go higher: once rung 1 is in place the composition binds
on the complex branch, and this package shows in `calibrations.run1` that rung 1 already
sits **at the complex branch's ceiling** -- so a rung above it cannot be taken anywhere
except on the complex word.

What this script does, all in exact rational arithmetic from pinned inputs:

1. **Calibration, frontier (#207).**  Reproduces #207's published `kappa` from its own
   `a_bit`/`a_complex` in the assembly convention of the queue's latest rungs
   (`eta = beta = 10^-24`, `weak = 10^-30`, `10^-18` grid) -- exactly, not to a tolerance.
2. **Calibration, rung 1 (#219).**  Rebuilds rung 1 by importing the vendored #219 package
   itself (`references/pr219-run1/`), reproducing its published
   `kappa = 700427501305159/10^18` and showing the assembly binds on the complex branch
   with the ceiling gap below one grid step.
3. **The rung-2 ledger** (`ledger.py`): whole-bank volume, retained row identity, stock
   drop equal to the bank count, and the two paid moments on the `10^-18` grid.
4. **The rung-2 assembly**: PR184/#219's unchanged 47-constraint assembly at the rung-2
   budget, with the adjacent `10^-18` point rejected.
5. **A second, independent replica** at my PR208 pricing model's convention
   (`stop = 10^-9`, `eta = 10^-8`, `10^-10` grid), which must reproduce PR208's own priced
   ladder value `3541457/5*10^9` for the same ledger.
6. **The blocker**, as facts rather than assertions: the complex supplier's certificate
   carries no bank infrastructure, the only bank construction in the pinned set is the bit
   word's entrance-gauge pack, and no package enumerates the complex rank-11 family's
   provenance.

    python3 -B run2.py [--out certificate.json]
"""
import argparse
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import ledger  # noqa: E402  (local module, imported after the path is set)
import pins  # noqa: E402

REFERENCES = HERE / 'references'
FRONTIER = REFERENCES / 'pr207-coordinated-crossover.certificate.json'
PR193 = REFERENCES / 'pr219-run1' / 'references' / 'pr193-source-assisted-v4.certificate.json'
PR205 = REFERENCES / 'pr219-run1' / 'references' / 'pr205-packed.certificate.json'

# The convention of the queue's latest rungs (#207, #219).
ETA = BETA = Q(1, 10 ** 24)
WEAK = Q(1, 10 ** 30)
GRID = 10 ** 18
# The convention of PR208's pricing model, for the independent replica.
STOP_208 = Q(1, 10 ** 9)
ETA_208 = Q(1, 10 ** 8)
GRID_208 = 10 ** 10
RUN1_KAPPA = Q(700427501305159, 10 ** 18)          # #219's published rung-1 claim
RUN2_REPLICA = Q(3541457, 5 * 10 ** 9)             # PR208's priced rung-2 target


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
            note='the pinned construction banks the bit word\'s selected entrance-gauge '
                 'exteriors into width-72 banks; it is the only bank construction in the pins'),
        complex_family_inventory=None,
        complex_family_inventory_note='the only occurrence inventory in the pins is '
                                      '#219\'s bit-side inputs/absorbed-occurrences.json '
                                      '(rank 22); the complex rank-11 family has no such '
                                      'enumeration, so even the item-to-block map of C1 '
                                      'has no starting inventory',
    )


def build():
    interval = ledger.engine()
    schedule, arithmetic = ledger.run1()
    frontier = json.loads(FRONTIER.read_text())
    supplier = json.loads(PR193.read_text())
    supplier['assembly']['finite_bridge']['rows']['degree_gap'] = Q(
        supplier['assembly']['finite_bridge']['rows']['degree_gap'])

    # --- 1. the frontier's own number, in this convention ----------------------
    a_bit = Q(frontier['a_bit'])
    a_complex = Q(frontier['a_complex'])
    budget, bound, kappa = frontier_kappa(a_bit, a_complex)
    assert kappa == Q(frontier['kappa']), 'the frontier claim must be reproduced exactly'
    calibration_frontier = dict(
        published=str(Q(frontier['kappa'])), reproduced=str(kappa), equal=True,
        a_bit=str(a_bit), a_complex=str(a_complex), binding=frontier['binding'],
        bound=str(bound), grid_gap=str(bound - kappa))

    # --- 2. rung 1, rebuilt by #219's own vendored code ------------------------
    result1 = arithmetic.build(schedule.build())
    kappa1 = result1['after_assembly']['kappa']
    assert kappa1 == RUN1_KAPPA, 'rung 1 must reproduce #219\'s published grid point'
    assert result1['after_assembly']['binding'] == 'complex', 'rung 1 binds on the complex branch'
    complex_coarse_1 = result1['complex_coarse']
    ceiling_1 = ledger.ceiling(complex_coarse_1)
    assert 0 <= ceiling_1 - kappa1 < Q(1, GRID), 'rung 1 must sit on the complex ceiling'
    calibration_run1 = dict(
        published=str(RUN1_KAPPA), reproduced=str(kappa1), equal=True,
        binding=result1['after_assembly']['binding'],
        bit_coarse_after=str(result1['bit_coarse_after']),
        complex_coarse=str(complex_coarse_1),
        complex_ceiling=str(ceiling_1),
        ceiling_gap=str(ceiling_1 - kappa1),
        bit_headroom=str(min(Q(result1['ordinary_leaf']), (1 - BETA) * complex_coarse_1 - WEAK)
                         - ((1 - BETA) * complex_coarse_1 - WEAK)),
        conclusion='rung 1 already sits on the complex branch ceiling, so every further '
                   'rung has to raise the complex supplier\'s own coarse saving',
    )

    # --- 3. the rung-2 ledger -------------------------------------------------
    half = ledger.complex_ledger(PR193, interval)
    assert half['base_saving'] == Q(frontier['complex']['saving']) == a_complex, \
        'the pinned complex supplier is the one the frontier prices'
    supplier_field = Q(supplier['complex_saving'])
    assert supplier_field < a_complex, 'the supplier field sits below the certified moment'
    assert half['base_excluded'] and half['absorbed']['next_excluded'], 'adjacent grid points'
    assert half['absorbed']['rank_divides_width'], 'the new blocks need no mixture'
    assert half['absorbed']['blocks_per_bank'] == 6, 'width 66 = 6 * 11'

    # --- 4. the rung-2 assembly ----------------------------------------------
    absorbed_saving = Q(half['absorbed']['saving'])
    leaf = result1['ordinary_leaf']
    budget2, bound2, kappa2 = frontier_kappa(leaf, absorbed_saving)
    assert budget2 == (1 - BETA) * absorbed_saving - WEAK, 'the complex branch binds at rung 2'
    out = supplier_assembly(supplier, budget2, absorbed_saving, kappa2)
    next_rejected = True
    try:
        supplier_assembly(supplier, budget2, absorbed_saving, kappa2 + Q(1, GRID))
    except AssertionError:
        pass
    else:
        next_rejected = False
    assert next_rejected, 'the adjacent 10^-18 point must be rejected'
    ceiling_2 = ledger.ceiling(absorbed_saving)
    assert 0 <= ceiling_2 - kappa2 < Q(1, GRID), 'rung 2 sits on the new complex ceiling'

    # --- 5. the independent replica at PR208's convention ---------------------
    bit_row = ledger.profile(frontier['bit_profile'])
    bit_mass = ledger.check_row(bit_row)
    bit_absorbed = ledger.absorb(ledger.three_copies(bit_row), 22)
    bit_coarse = arithmetic.certify(interval, bit_absorbed['retained'], True)['saving']
    replica_budget, replica_minimum, replica = replica_kappa(bit_coarse, absorbed_saving)
    assert replica == RUN2_REPLICA, 'PR208\'s priced ladder value must be reproduced'
    replica_rung1_budget, _, replica_rung1 = replica_kappa(bit_coarse, Q(frontier['complex']['saving']))

    # The supplier's own headline field is its value on the 10^-10 grid, 4.39e-11 below
    # the 10^-18 certified moment of the same profile.  Both the frontier certificate and
    # rung 1 price the certified moment, which this package reproduces; the coarser field
    # is priced here as a conservative variant rather than silently ignored -- on it the
    # complex branch's ceiling already sits at rung 1, so the rung is only visible on the
    # refined grid.
    conservative_budget, conservative_bound, conservative = frontier_kappa(
        leaf, supplier_field)

    certificate = dict(
        status='MODEL AND TARGET, NOT CONSTRUCTED: the rung-2 ledger (whole-bank volume, '
               'retained row identity, stock drop, both paid moments on the 10^-18 grid) and '
               'the 47-constraint assembly are certified here, but the rung needs a bank '
               'construction on the complex supplier that no package in the pins provides '
               '(obligations.json C1-C5, plus #219\'s inherited R1-R4). The kappa below is '
               'conditional on those and is not a completed finite witness.',
        rung=2,
        kappa=kappa2, decimal=float(kappa2), binding='complex',
        gain_vs_rung1=kappa2 / RUN1_KAPPA - 1,
        gain_vs_frontier=kappa2 / Q(frontier['kappa']) - 1,
        calibrations=dict(frontier=calibration_frontier, run1=calibration_run1),
        ledger=half,
        assembly=dict(budget=str(budget2), bound=str(bound2), grid=10 ** 18,
                      grid_gap=str(bound2 - kappa2), constraints=47, margins=7,
                      adjacent_grid_rejected=True,
                      minimum_constraint=str(out['minimum_constraint']),
                      complex_ceiling=str(ceiling_2), ceiling_gap=str(ceiling_2 - kappa2),
                      bit_leaf_headroom=str(Q(leaf) - budget2)),
        replica=dict(model='PR208 (research/composed-diagonal-bit-bootstrap), stop=10^-9, '
                           'eta=10^-8, 10^-10 grid',
                     bit_coarse=str(bit_coarse), budget=str(replica_budget),
                     minimum=str(replica_minimum), kappa=str(replica),
                     matches_pr208_priced_rung=str(replica == RUN2_REPLICA),
                     rung1_same_model=str(replica_rung1)),
        blocked_on=bank_evidence(),
        obligations=['C1', 'C2', 'C3', 'C4', 'C5', 'R1', 'R2', 'R3', 'R4'],
        supplier_field=dict(
            published_saving=str(supplier_field), certificate='pr193-source-assisted-v4',
            certified_moment_of_same_profile=str(a_complex),
            delta=str(supplier_field - a_complex),
            note='PR193 publishes 219037/312500000 = 7.009184e-4, its value on the '
                 '10^-10 grid, 4.3859411e-11 below the 10^-18 certified paid moment of '
                 'the same complex profile. The frontier certificate (a_complex) and the '
                 'rung 1 package both price the certified moment, which this package '
                 'reproduces exactly; a reviewer who prefers the coarser published field '
                 'can read the conservative variant, where the complex branch ceiling '
                 'already sits at rung 1.',
            conservative_variant=dict(budget=str(conservative_budget),
                                      bound=str(conservative_bound), kappa=str(conservative),
                                      vs_rung1=str(conservative / RUN1_KAPPA - 1))),
        comparison=dict(rung1=str(RUN1_KAPPA), frontier=str(Q(frontier['kappa'])),
                        pr208_priced_rung2=str(RUN2_REPLICA)),
        source_pins=pins.manifest(),
    )
    return certificate


def supplier_assembly(supplier, budget, complex_saving, kappa):
    """PR184/#219's unchanged 47-constraint assembly at a given grid point."""
    assembly = ledger.load('run2_assembly', ledger.RUN1 / 'paired_cube_assembly.py')
    out = assembly.assembly(budget, complex_saving, supplier['assembly']['finite_bridge'],
                            kappa, eta=ETA, beta=BETA)
    assert len(out['strict_constraints']) == 47 and len(out['margins']) == 7
    return dict(minimum_constraint=min(out['strict_constraints'].values()))


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
    print('rung 1    kappa = %s (reproduced exactly, binding %s, ceiling gap %s)' %
          (record['calibrations']['run1']['published'], record['calibrations']['run1']['binding'],
           record['calibrations']['run1']['ceiling_gap']))
    print('rung 2    kappa = %s = %.17g  (binding %s, +%.4f%% over rung 1, +%.4f%% over the frontier)' %
          (record['kappa'], float(Q(record['kappa'])), record['binding'],
           float(Q(record['gain_vs_rung1'])) * 100, float(Q(record['gain_vs_frontier'])) * 100))
    print('ledger    m=%s: %s children x3, volume %s = %s banks, stock %s -> %s (drop %s)' %
          (record['ledger']['one_copy']['m'], record['ledger']['one_copy']['bin_children'],
           record['ledger']['absorbed']['volume'], record['ledger']['absorbed']['banks'],
           record['ledger']['absorbed']['stock_before'], record['ledger']['absorbed']['stock_after'],
           record['ledger']['absorbed']['stock_drop']))
    print('moments   complex coarse %s -> %s; ceilings %s -> %s' %
          (record['ledger']['base_saving'], record['ledger']['absorbed']['saving'],
           record['ledger']['ceilings']['base'], record['ledger']['ceilings']['absorbed']))
    print('replica   %s at PR208\'s convention (matches PR208: %s)' %
          (record['replica']['kappa'], record['replica']['matches_pr208_priced_rung']))
    print('supplier  field %s vs certified moment %s (delta %s); conservative variant %s' %
          (record['supplier_field']['published_saving'],
           record['supplier_field']['certified_moment_of_same_profile'],
           record['supplier_field']['delta'],
           record['supplier_field']['conservative_variant']['kappa']))
    print('blocked   complex supplier bank keys: %s; frontier bank keys: %s; pinned bit bank '
          'construction: %s banks' %
          (record['blocked_on']['complex_supplier_has_bank_keys'],
           record['blocked_on']['frontier_certificate_has_bank_keys'],
           record['blocked_on']['pinned_bit_bank_construction']['physical_banks']))
    print('write     ' + str(args.out))


if __name__ == '__main__':
    main()
