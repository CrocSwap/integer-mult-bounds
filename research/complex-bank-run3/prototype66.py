#!/usr/bin/env python3
"""The complex-side bank construction, prototyped at the schedule level.

`schedule66.py` settles obligation T1 the hard way: no *uniform* tiling of a width-66 bank
absorbs a whole rank-16 or rank-20 bin, and none absorbs two bins at once.  What it leaves is
the obvious repair -- **pad the bank**.  A bank that cannot be filled by the family alone can
be filled by the family plus a fixed pattern of *retained* blocks, and then every register of
the bank is accounted for:

* rank 16: ``66 = 4 * 16 + 2``, so a bank carries **four rank-16 blocks and 2 registers of
  padding**; 792 three-copy items fill 198 banks exactly (4 x 198 = 792, no family slot
  unused), and the padding is 396 registers;
* rank 20: ``66 = 3 * 20 + 6``, so **three rank-20 blocks and 6 registers of padding**; 198
  items fill 66 banks exactly, padding again 396 registers;
* rank 11: ``66 = 6 * 11``, no padding (rung 2 as PR224 built it).

The padding is drawn from a family the ledger keeps -- 2 registers is one rank-2 block or two
rank-1 blocks; 6 is one rank-6, two rank-3, three rank-2, or six rank-1 blocks, and so on --
so the padded absorption removes *part* of a retained bin.  That is the step the priced ledger
never took, and it is exactly consistent: if the padding registers leave with the blocks, the
retained row still satisfies ``m * W - rank_mass = deficit`` and the stock falls by **exactly
the bank count**, because the mass removed is ``banks * m`` by construction.  Each padding
option is a free parameter of the construction, so this module enumerates them and prices each
one with the pinned engine, reporting the best.

What this is and is not: it is a **schedule-level construction** -- banks, blocks per bank, the
item-to-bank/offset assignment (``item i -> bank i // k_f, block i % k_f``), the padding draw
and the ledger it induces, all checked.  It is not the physical construction: the normalizer
that sends each item's residual projector to its block, the charts and the prime witnesses are
still C1-C7, and the padding blocks are ordinary retained children, not new frames.

Everything is exact rational arithmetic from the pinned complex profile, through the pinned
interval-moment engine, priced on the complex side (`bit=False`) exactly as PR219 prices it.
"""
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import ledger3  # noqa: E402

WIDTH = 66
COPIES = 3
RUNGS = (11, 16, 20)
FRONTIER = HERE / 'references' / 'pr207-coordinated-crossover.certificate.json'


def partitions(total, sizes):
    """Every multiset of `sizes` summing to exactly `total`, largest block first."""
    sizes = sorted(s for s in sizes if 0 < s <= total)
    out = []

    def walk(remaining, index, chosen):
        if remaining == 0:
            out.append(tuple(sorted(chosen, reverse=True)))
            return
        for j in range(index, len(sizes)):
            if sizes[j] > remaining:
                break
            walk(remaining - sizes[j], j, chosen + [sizes[j]])

    walk(total, 0, [])
    return out


def schedule(row, family, width=WIDTH):
    """The saturated bank schedule for one family, with every padding option.

    Returns the bank count (the family's capacity minimum, not the volume criterion's
    number), the blocks per bank, and one entry per padding tiling: the draw it takes from
    the ledger, the retained row, and the ledger facts that must hold for each.
    """
    m, W, D = row['m'], row['W'], row['N']
    hist = dict(row['child_multiplicities'])
    n = hist[family]
    capacity = width // family
    banks = -(-n // capacity)                     # capacity minimum, ceil(n / k_f)
    assert banks * capacity >= n, 'every item must land in a block'
    assert (n + capacity - 1) // capacity == banks, 'the bank count is the minimum'
    padding = banks * width - family * n          # registers of padding, total
    assert banks * width == family * n + padding, 'the bank must be exactly filled'
    assert n == capacity * banks, 'the schedule must be saturated: no family slot unused'
    assert padding % banks == 0, 'every bank must carry the same padding'
    per_bank_padding = padding // banks
    assert per_bank_padding == width - family * capacity, 'padding = the unfilled registers'

    options = []
    for pattern in (partitions(per_bank_padding, sorted(hist))
                    if per_bank_padding else [()]):
        assert sum(pattern) == per_bank_padding, 'the padding must fill the bank'
        assert all(size in hist for size in pattern), 'padding blocks come from the ledger'
        if any(size == family for size in pattern):
            continue                    # a padding block of the same rank is that family's item
        per_bank = {}
        for size in pattern:
            per_bank[size] = per_bank.get(size, 0) + 1
        draw = {size: per_bank[size] * banks for size in per_bank}
        if any(draw[size] > hist[size] for size in draw):
            continue                                  # the ledger cannot supply the draw
        kept = dict(hist)
        kept[family] -= n                             # the whole bin leaves
        del kept[family]
        for size in draw:
            kept[size] -= draw[size]
            if kept[size] == 0:
                del kept[size]
        mass = sum(r * c for r, c in kept.items())
        stock, remainder = divmod(mass + D, m)
        assert remainder == 0, 'half-filled stock'
        assert W - stock == banks, 'the stock must fall by exactly the bank count'
        retained = dict(m=m, W=stock, N=D, L=row.get('L', 0), child_multiplicities=kept,
                        total_rank=mass, maxchild=max(kept))
        assert ledger3.check_row(retained) == mass
        assert family * n + sum(s * draw[s] for s in draw) == banks * m, \
            'the removed mass must be exactly the bank volume'
        options.append(dict(
            padding_per_bank={str(s): per_bank[s] for s in sorted(per_bank)},
            padding_registers=padding, draw={str(s): draw[s] for s in sorted(draw)},
            registers_drawn=sum(s * draw[s] for s in draw),
            retained=retained, stock=stock, stock_drop=W - stock,
            children=sum(kept.values()),
            share_of_padding_bin={str(s): Q(draw[s], hist[s]) for s in sorted(draw)},
        ))

    # the assignment itself: item i of the family -> bank i // k_f, block i % k_f
    blocks_per_bank = {}
    for block in range(capacity):
        blocks_per_bank[block + 1] = [i for i in range(n) if i % capacity == block]
    assert sum(len(items) for items in blocks_per_bank.values()) == n, 'an item was lost'
    assert all(len(items) == banks for items in blocks_per_bank.values()), \
        'every block must be filled in every bank'
    return dict(family=family, banks=banks, items=n, capacity_per_bank=capacity,
                blocks_per_bank=capacity, padding_registers=padding,
                padding_per_bank=padding // banks,
                pattern_sum=family * capacity + padding // banks,
                options=options, block_assignment=banks)


def priced_ladder(certificate_path=FRONTIER, interval=None, width=WIDTH):
    """Rung 2, then the padded rungs 3 and 4: the schedule, the ledger; and the price.

    Each rung takes the padding option that raises the complex paid moment the most, and the
    chain is carried on from there, since the padding changes the retained histogram.
    """
    interval = interval or ledger3.engine()
    certificate = json.loads(Path(certificate_path).read_text())
    row = ledger3.profile(certificate['complex_profile'])
    ledger3.check_row(row)

    base = ledger3.certify(interval, row)
    work = ledger3.three_copies(row)
    ladder, exhaustive = [], True
    for family in RUNGS:
        step = schedule(work, family, width)
        priced = []
        for option in step['options']:
            saving = ledger3.certify(interval, option['retained'])['saving']
            priced.append(dict(option, saving=saving, ceiling=ledger3.ceiling(saving)))
        assert priced, 'a family that fills whole banks must have a padding option'
        best = max(priced, key=lambda entry: entry['saving'])
        work = best['retained']
        ladder.append(dict(
            family=family, banks=step['banks'], items=step['items'],
            blocks_per_bank=step['blocks_per_bank'], capacity_per_bank=step['capacity_per_bank'],
            padding_registers=step['padding_registers'],
            padding_per_bank=step['padding_per_bank'], pattern_sum=step['pattern_sum'],
            block_assignment=step['block_assignment'],
            options=len(priced), chosen=dict(
                padding_per_bank=best['padding_per_bank'], draw=best['draw'],
                registers_drawn=best['registers_drawn'],
                share_of_padding_bin={k: str(v)
                                      for k, v in best['share_of_padding_bin'].items()}),
            alternatives=[dict(padding_per_bank=entry['padding_per_bank'],
                               draw=entry['draw'], saving=entry['saving'],
                               ceiling=entry['ceiling']) for entry in priced],
            saving=best['saving'], ceiling=best['ceiling'],
            stock=best['stock'], stock_drop=best['stock_drop'],
            children=best['children'], mass=best['retained']['total_rank'],
            families_left=len(best['retained']['child_multiplicities']),
            largest_child=max(best['retained']['child_multiplicities']),
            whole_bank_volume=(family * step['items']) % width == 0,
            volume_criterion_banks=family * step['items'] // width,
            eligibility_after=ledger3.eligibility(best['retained']),
        ))
    exhaustive = ladder[-1]['eligibility_after'] == []
    return dict(width=width, copies=COPIES, source=Path(certificate_path).name,
                base_saving=base['saving'], ledger_check=ledger3.check_row(work) == work['total_rank'],
                ladder=ladder, exhaustive=exhaustive,
                final=dict(W=work['W'], deficit=work['N'], mass=work['total_rank'],
                           children=sum(work['child_multiplicities'].values()),
                           families=len(work['child_multiplicities']),
                           largest_child=max(work['child_multiplicities'])),
                residual_eligibility=ledger3.eligibility(work))


def main():
    sys.set_int_max_str_digits(0)
    sys.dont_write_bytecode = True
    out = priced_ladder()
    print('padded schedule prototype, width %d, source %s' % (out['width'], out['source']))
    print('base complex coarse saving %s' % out['base_saving'])
    for step in out['ladder']:
        print('  rank %-3d %4d items -> %4d banks x %d blocks/bank + %d registers padding '
              '(%d options)' % (step['family'], step['items'], step['banks'],
                                step['blocks_per_bank'], step['padding_per_bank'],
                                step['options']))
        print('        chosen padding %s (draw %s), coarse saving %s, ceiling %s'
              % (step['padding_per_bank'], step['chosen']['draw'], step['saving'],
                 step['ceiling']))
        print('        stock %d (drop %d = banks), children %d, families left %d, '
              'eligibility after %s' % (step['stock'], step['stock_drop'], step['children'],
                                        step['families_left'], step['eligibility_after']))
    print('exhausted at the padded top: %s' % out['exhaustive'])


if __name__ == '__main__':
    main()
