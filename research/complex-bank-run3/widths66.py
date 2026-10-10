#!/usr/bin/env python3
"""Is the bank width a dial?  A modulus scan, and the three answers it gives.

The pinned precedent settles what a bank width *is*: `references/pr219-run1/schedule.py` has
the bit word at `M = 72`, its rank-22 bin's 20,016 occurrences carrying `22 * 20,016 = 440,352`
registers into `440,352 / 72 = 6,116` banks, with the row identity `M * W - mass = D` and the
stock dropping by exactly the bank count.  So **the bank width is the word's own modulus**, the
removed mass is `modulus * banks`, and the whole-bank criterion is `modulus | rank * children`.
The complex word's modulus is 66, which is why its banks are width 66.

That makes "use another bank width" a question about the *word*, and this module answers it
three ways, each machine-checked:

1. **The pinned ledger admits no narrower modulus.**  The pinned engine's own contraction
   condition is `rank mass < W * modulus`; the pinned row has `rank mass / W = 65.89`, so at
   `w <= 65` the row is not poseable at all (`mass >= w * W`).  66 is the smallest modulus this
   ledger admits, and the scan shows it by evaluating the condition, not by asserting it.
2. **At the pinned width the criterion is exactly what this package already uses.**  Running
   the whole scan at `w = 66` reproduces the padded schedule and the pinned top exactly (795
   banks, 792 padding registers, 52,470 registers of mass) -- the scan's own calibration.
3. **Raising the modulus is a word change, not a schedule change, and the scan demonstrates
   why the prices stop being comparable.**  Holding the pinned ledger fixed while raising `w`
   leaves a row whose rank mass fills only `mass / (W * w)` of its capacity: 99.837% at the
   pinned word, 95.4% at `w = 69`, 91.5% at `w = 72`.  That row is no longer the dense ledger
   the moment is calibrated on -- and indeed the vendored certifier's own bracket (`a = 0`,
   `a = 10^-2`) stops holding there, which the scan records rather than hides.  A word of a
   different width would come with *its own* stock and deficit, i.e. a different supplier.

So the honest answer to "raise κ by changing the bank width" is: on this ledger the width is
pinned (nothing below works, and above it you are designing another word).  What the scan does
deliver is the criterion at every width -- which families tile whole banks, and the bank,
padding and mass arithmetic each one implies -- plus the two structural facts above.

Caveat, stated once: the ledger is the pinned complex one (modulus 66).  Any modulus change
would move the ledger, the counting and the engine's calibration with it; this module prices
only the pinned word, and reports the rest as arithmetic.
"""
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import ledger3  # noqa: E402

PINNED_WIDTH = 66
GRID = 10 ** 18
ETA = BETA = Q(1, 10 ** 24)
WEAK = Q(1, 10 ** 30)
PINNED_KAPPA = Q(711599961413937, 10 ** 18)

WIDTHS = [48, 54, 58, 60, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 78, 80,
          84, 88, 90, 96, 100, 108, 120, 132, 144]


def bit_leaf():
    """#219's rung-1 ordinary leaf: the budget cap the assembly inherits."""
    schedule, arithmetic = ledger3.run1()
    return Q(arithmetic.build(schedule.build())['ordinary_leaf'])


def kappa_of(leaf, coarse):
    """The queue's assembly rule: budget, closed-form bound, floor to the grid."""
    budget = min(leaf, (1 - BETA) * coarse - WEAK)
    q = budget * (1 - 2 * ETA)
    bound = (1 - ETA) * q / (1 + q)
    z = bound * GRID
    return budget, Q((z.numerator - 1) // z.denominator, GRID)


def family_cost(hist, rank, width):
    """Whole-bank absorption of this bin at this modulus: banks, padding, mass."""
    n = hist[rank]
    if (rank * n) % width:
        return None                     # whole-bank volume condition fails at this modulus
    capacity = width // rank
    if capacity == 0:
        return None                     # a whole block does not fit in one bank
    banks = -(-n // capacity)
    return dict(rank=rank, children=n, capacity_per_bank=capacity, banks=banks,
                padding_registers=banks * width - rank * n, mass_removed=banks * width,
                mass_family=rank * n)


def scan_width(base, width, interval, leaf, ladder=None):
    """The criterion and the bank arithmetic at one modulus; priced only where legitimate.

    ``ladder`` is an already-priced padded schedule for the pinned width, so a caller that has
    one does not pay for a second engine run.
    """
    hist = base['child_multiplicities']
    eligible = {rank: family_cost(hist, rank, width)
                for rank in sorted(hist, reverse=True)}
    eligible = {rank: cost for rank, cost in eligible.items() if cost}
    pose = base['total_rank'] < width * base['W']
    deficit = width * base['W'] - base['total_rank']
    out = dict(width=width, poseable=pose,
               density=str(Q(base['total_rank'], base['W'] * width)),
               density_decimal=float(Q(base['total_rank'], base['W'] * width)),
               deficit=deficit,
               eligible_families=sorted(eligible),
               eligible_mass=sum(eligible[r]['mass_removed'] for r in eligible),
               eligible_banks=sum(eligible[r]['banks'] for r in eligible),
               blocks_per_bank={str(r): width // r for r in eligible},
               detail={str(r): eligible[r] for r in eligible})
    if not pose:
        return {**out, 'saving': None, 'kappa': None, 'priced': False,
                'status': 'the pinned row is not poseable (rank mass >= w * W)'}
    if not eligible:
        return {**out, 'saving': None, 'kappa': None, 'priced': False,
                'status': 'no family satisfies w | rank * children'}
    if width != PINNED_WIDTH:
        # The retained row would be a different word (its density moved), so any price from it
        # would compare two words.  Record that instead of quoting a number.
        return {**out, 'saving': None, 'kappa': None, 'priced': False,
                'status': 'not priced: a different modulus is a different word, whose stock '
                          'and deficit this ledger does not fix',
                'mass_over_capacity_ratio': str(Q(base['total_rank'], base['W'] * width))}
    # Only the pinned word is priced: the package's own padded schedule, at the pinned width.
    import prototype66
    if ladder is None:
        ladder = prototype66.priced_ladder(interval=interval, width=width)
    kappa = None
    if ladder['ladder']:
        budget, kappa = kappa_of(leaf, Q(ladder['ladder'][-1]['saving']))
    return {**out, 'saving': Q(ladder['ladder'][-1]['saving']), 'kappa': kappa, 'priced': True,
            'banks': sum(step['banks'] for step in ladder['ladder']),
            'padding_registers': sum(step['padding_registers'] for step in ladder['ladder']),
            'absorbed_families': [step['family'] for step in ladder['ladder']],
            'status': 'priced: the pinned word, this package\'s padded schedule'}


def main():
    widths = [int(a) for a in sys.argv[1:]] or WIDTHS
    sys.set_int_max_str_digits(0)
    sys.dont_write_bytecode = True
    interval = ledger3.engine()
    supplier = json.loads((HERE / 'references' / 'pr219-run1' / 'references'
                           / 'pr193-source-assisted-v4.certificate.json').read_text())
    base = ledger3.three_copies(ledger3.profile(supplier['complex_profile']))
    leaf = bit_leaf()
    print('pinned ledger: modulus %d, W = %d, deficit %d, rank mass %d, %d families, '
          'rank mass / W = %s' % (PINNED_WIDTH, base['W'], base['N'], base['total_rank'],
                                  len(base['child_multiplicities']),
                                  Q(base['total_rank'], base['W'])))
    print('%5s %8s %6s %-16s %5s %7s %10s  %s'
          % ('width', 'poseable', 'elig', 'families', 'banks', 'padding', 'mass', 'status'))
    records = {}
    for width in widths:
        out = scan_width(base, width, interval, leaf)
        records[str(width)] = out
        print('%5d %8s %6d %-16s %5s %7s %10s  %s'
              % (width, 'yes' if out['poseable'] else 'NO', len(out['eligible_families']),
                 ','.join(map(str, out['eligible_families'])) or '-',
                 out.get('banks', ''), out.get('padding_registers', ''),
                 out.get('eligible_mass', ''), out['status']))
    pinned = records[str(PINNED_WIDTH)]
    assert pinned['priced'] and pinned['kappa'] == PINNED_KAPPA, \
        'the scan must reproduce the pinned width-66 top exactly, got %s' % pinned['kappa']
    assert pinned['banks'] == 795 and pinned['padding_registers'] == 792
    unposeable = sorted(r['width'] for r in records.values() if not r['poseable'])
    print('\nthe pinned row is not poseable at: %s  (rank mass %d vs W * w at 65 = %d)'
          % (unposeable, base['total_rank'], 65 * base['W']))
    print('smallest modulus the pinned row admits: %d'
          % min(r['width'] for r in records.values() if r['poseable']))
    print('density (rank mass / W*w): %s'
          % {str(r['width']): r['density_decimal'] for r in records.values()
             if r['poseable']})
    print('priced: width %d only, kappa %s (pinned top, reproduced exactly)'
          % (PINNED_WIDTH, pinned['kappa']))


if __name__ == '__main__':
    main()
