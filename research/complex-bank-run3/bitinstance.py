#!/usr/bin/env python3
"""Instancing B1: the bit-side rung's items, their blocks, and the padding they draw.

`bitrung.py` measures the rung this package's top stands on -- three families leaving #219's
rung-1 retained bit row into 7,342 width-72 banks -- and this module *instances* it, the way
`instantiate66.py` instances the complex ladder and `instantiate_rank3.py` instances the rung on
#233's row.  That is what B1 asks for, and it is answered in the only two halves the pins allow:

**Instanced here, and checked rather than described.**

* **the item-to-block map.**  Each family's children are enumerated over its own bin of the
  retained row (rank 7: 4,080 per vertex, 12,240 in the row; rank 8: 2,514 and 7,542; rank 20:
  5,280 and 15,840) and every item gets exactly one address: item `i` goes to bank `i // k_f`,
  block `i % k_f`, at offset `(i % k_f) * rank`, where `k_f = 72 // rank` is the family's blocks
  per bank (10, 9 and 3).  The map is a bijection onto the bank x block grid, every block holds
  exactly one item, every bank carries each of its blocks exactly once, and a deterministic
  digest over the whole table is recorded so a reviewer can compare bytes.
* **the bank tables.**  Per family: the bank count (1,224 + 838 + 5,280 = 7,342), the block
  layout, and the registers of each bank the family does not occupy -- the padding every bank
  admits, `72 - rank * k_f` per bank (2, 0 and 12).
* **the padding inventory.**  The padding is a **partial removal from the retained singleton
  bin**, exactly as T1's is on the complex side, and it is named rather than counted: the draw
  takes the first `banks * padding_per_bank` children of that bin in index order,
  `padding_per_bank` of them per bank, so 2,448 rank-7 registers and 63,360 rank-20 registers
  come out of the 377,316 the retained row carries, leaving 311,508 -- the count the measured
  rung's retained histogram holds for the same bin.
* **the ledger the assignment induces.**  The retained row after all three families leave
  (stock 42,944, rank mass 3,086,160, deficit 5,808, 756,192 children over 18 families), with
  the stock falling by exactly the 7,342 banks and the mass by exactly `banks * 72`.  The
  binary's own measured row is re-derived here from the **pinned packed certificate** with plain
  integer arithmetic, not read from `bitrung.json`.

**Not instanced, and that is the half of B1 that stays open: the frame/chain identity of each
child.**  `pins_gap()` reads the pinned bytes rather than asserting the gap: the packed bit
certificate carries no key containing `occurrence`, `assign` or `block` at all, so nothing in
the pins says *which* frame or chain occurrence any of these 35,622 children comes from.  The
only per-child inventory the pins hold is #219's `inputs/absorbed-occurrences.json` -- the
rank-22 family's, with its chain/frame provenance, which is what made that absorption a closed
checklist -- and its key set is recorded here, so what this module owes is stated as an artifact
with fields rather than as a remark.

Nothing here is built physically: the absorbed families need the new residual types #219's
obligations reserve (R1-R4) and the complex side's normalizer (C1's physical half).
"""
import hashlib
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import instantiate66  # noqa: E402
import ledger3  # noqa: E402

WIDTH = 72
COPIES = 3
RUNGS = (7, 8, 20)
RUN1 = HERE / 'references' / 'pr219-run1'
PACKED = RUN1 / 'references' / 'pr205-packed.certificate.json'
BIT_CERTIFICATE = RUN1 / 'references' / 'pr200-bit.certificate.json'
BIT_OCCURRENCES = RUN1 / 'inputs' / 'absorbed-occurrences.json'


def retained_row():
    """The rung-1 retained bit row, from the pinned packed certificate alone.

    Plain integer arithmetic on the pinned bytes: the packed bit word banks its rank-22 bin
    whole (6,116 width-72 banks), and what is left is the ledger this rung absorbs from.  The
    result is cross-checked below against the vendored schedule module's own retained profile,
    so a divergence between the two readings of the same pinned bytes cannot pass silently.
    """
    packed = json.loads(PACKED.read_text())['physical']
    histogram = {int(r): int(n) for r, n in packed['child_histogram'].items()}
    deficit = int(packed['deficit'])
    stock = int(packed['W'])
    mass_before = sum(r * n for r, n in histogram.items())
    assert 72 * stock - mass_before == deficit, 'the packed row identity'
    absorbed = 22 * histogram[22]
    assert absorbed % 72 == 0, "rung 1 absorbs a whole number of banks"
    histogram.pop(22)
    mass = mass_before - absorbed
    row = dict(m=WIDTH, W=(mass + deficit) // 72, deficit=deficit, mass=mass,
               histogram=histogram)
    assert 72 * row['W'] == mass + deficit == 72 * (stock - absorbed // 72), 'retained identity'
    assert sum(r * n for r, n in histogram.items()) == mass and max(histogram) == 21
    return row


def vendored_retained_row():
    """The same row as the vendored rung-1 schedule builds it, for the cross-check."""
    schedule_module, _arithmetic = ledger3.run1()
    profile = schedule_module.build()['retained_profile']
    histogram = {int(r): int(n) for r, n in profile['histogram'].items()}
    return dict(m=int(profile['m']), W=int(profile['W_after']), deficit=int(profile['deficit']),
                mass=int(profile['rank_mass_after']), histogram=histogram)


def histogram_digest(histogram):
    """The canonical digest of a child histogram: `rank:count` lines, ranks ascending, no
    trailing newline, sha256 over ASCII -- the same rule `instantiate_rank3.py` states."""
    text = '\n'.join('%d:%d' % (rank, count) for rank, count in sorted(histogram.items()))
    return hashlib.sha256(text.encode('ascii')).hexdigest()


def padding_inventory(row, family, banks, padding_per_bank):
    """The padding a family's banks draw from the retained singleton bin, named item by item.

    T1's padded schedule, one word over: the registers a bank cannot fill with the family's own
    blocks are filled with single-register blocks of a bin the ledger keeps.  The draw is the
    first `banks * padding_per_bank` children of the singleton bin in index order, taken
    `padding_per_bank` per bank in bank order -- deterministic, so it can be digested.
    """
    singleton_before = row['histogram'][1]
    drawn = banks * padding_per_bank
    assert drawn <= singleton_before, 'the singleton bin must be able to supply the draw'
    assert banks == 0 or drawn % banks == 0 and drawn // banks == padding_per_bank, \
        'the draw is uniform across the banks'
    indices = list(range(drawn))
    offsets = [WIDTH - padding_per_bank + j for j in range(padding_per_bank)]
    if drawn:
        assert indices[-1] < singleton_before, 'a partial removal, not the whole bin'
        assert offsets and offsets[-1] == WIDTH - 1, 'the padding closes the bank'
    digest = hashlib.sha256('\n'.join(str(i) for i in indices).encode()).hexdigest()
    return dict(family=family, banks=banks, padding_registers_per_bank=padding_per_bank,
                registers=drawn,
                rule='the first banks * padding_per_bank children of the retained singleton '
                     'bin, in index order, padding_per_bank of them per bank in bank order'
                     if drawn else 'the rank divides the width: this family\'s banks draw no '
                     'padding at all',
                first_bank=dict(bank=0, items=indices[:padding_per_bank], offsets=offsets),
                last_bank=dict(bank=banks - 1, items=indices[-padding_per_bank:] if drawn else [],
                               offsets=offsets),
                last_index=drawn - 1 if drawn else None, digest=digest,
                singleton_bin_before=singleton_before,
                singleton_bin_after=singleton_before - drawn,
                share_of_the_bin=str(Q(drawn, singleton_before)))


def pins_gap():
    """What the pins do not export for this rung, read from the pinned bytes."""
    packed = json.loads(PACKED.read_text())
    bit = json.loads(BIT_CERTIFICATE.read_text())
    occurrences = json.loads(BIT_OCCURRENCES.read_text())
    rank22 = bit['bit']['profile']['child_histogram'].get('22')

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

    return dict(
        packed_certificate_block_keys=keys_with(packed, 'block'),
        packed_certificate_occurrence_keys=keys_with(packed, 'occurrence'),
        packed_certificate_assignment_keys=keys_with(packed, 'assign'),
        bit_certificate_occurrence_keys=keys_with(bit, 'occurrence'),
        rank22_bin_in_the_packed_row=int(packed['physical']['child_histogram']['22']),
        rank22_bin_in_the_bit_certificate=int(rank22),
        pinned_item_inventory=dict(
            path='references/pr219-run1/inputs/absorbed-occurrences.json',
            top_level_keys=sorted(occurrences),
            per_vertex_keys=sorted(occurrences['occurrences_per_vertex']),
            counts_per_vertex=occurrences['counts_per_vertex'],
            note="the pins' only per-child inventory: the rank-22 family's, one entry per child "
                 "with its chain/frame provenance, which is what made rung 1 a closed checklist. "
                 "Nothing in the pins enumerates a rank-7, rank-8 or rank-20 child of this word, "
                 "so B1's provenance half owes this shape for three families and cannot be closed "
                 "from the pinned bytes."),
    )


def build():
    """The instanced rung: maps, bank tables, padding inventory, induced ledger and the gap."""
    row = retained_row()
    vendored = vendored_retained_row()
    assert row == vendored, 'the two readings of the retained row must agree'
    base = dict(row)
    base['child_multiplicities'] = dict(row['histogram'])

    inventories, draws = {}, {}
    for family in RUNGS:
        table = instantiate66.inventory(base, family, width=WIDTH, copies=COPIES)
        assert family * table['items'] + table['padding_registers'] == table['banks'] * WIDTH, \
            'every bank is exactly filled: the family blocks plus the padding it draws'
        assert table['padding_registers'] == table['banks'] * (WIDTH % family), \
            'the padding is what the rank leaves over, in every bank'
        inventories[str(family)] = table
        draws[str(family)] = padding_inventory(base, family, table['banks'],
                                              table['padding_per_bank'])

    # the ledger the assignment induces: every family removed whole, the padding out of the bin
    histogram, mass = dict(base['child_multiplicities']), base['mass']
    banks_total = 0
    for family in RUNGS:
        table, draw = inventories[str(family)], draws[str(family)]
        histogram[family] -= table['items']
        assert histogram[family] == 0, 'the family leaves whole'
        del histogram[family]
        histogram[1] -= draw['registers']
        assert histogram[1] >= 0, 'the singleton bin must survive the draw'
        banks_total += table['banks']
        mass -= table['banks'] * WIDTH
        assert sum(r * n for r, n in histogram.items()) == mass, 'rank mass after rank %d' % family
        assert 72 * ((mass + base['deficit']) // 72) == mass + base['deficit'], 'integral stock'
    stock = (mass + base['deficit']) // 72
    padding_total = sum(draw['registers'] for draw in draws.values())
    assert banks_total == sum(table['banks'] for table in inventories.values()) == 7342
    assert histogram[1] == base['child_multiplicities'][1] - padding_total == 311508, \
        'the measured rung keeps exactly this many singleton children'

    remaining = []
    for family in sorted(histogram):
        children = histogram[family]
        volume, capacity, gap = family * children, WIDTH // family, WIDTH % family
        whole = volume % WIDTH == 0
        remaining.append(dict(family=family, children=children, volume=volume,
                              volume_banks=volume // WIDTH if whole else None,
                              divides_width=gap == 0, blocks_per_bank=capacity,
                              padding_registers_per_bank=gap,
                              padded_saturates=(gap != 0 and children % capacity == 0)))

    return dict(
        status='B1 schedule half INSTANCED at the schedule level for the rung this package '
               'prices: every item of the rank-7, rank-8 and rank-20 families has a bank, a '
               'block and an offset, every bank is exactly filled by the family blocks plus the '
               'padding it draws from the retained singleton bin, the draw is named item by item '
               'and digested, and the ledger the assignment induces is re-derived from the '
               'pinned packed certificate. B1 provenance half (each child\'s frame/chain '
               'identity) remains open: nothing in the pins enumerates a child of these three '
               'families, and the only per-child inventory the pins hold is #219\'s rank-22 one. '
               'The physical realization (R1-R4 and C1\'s physical half) is as open as before.',
        width=WIDTH, copies=COPIES, rungs=list(RUNGS),
        retained_row=dict(source='references/pr219-run1/references/pr205-packed.certificate.json',
                          W=row['W'], deficit=row['deficit'], rank_mass=row['mass'],
                          children=sum(row['histogram'].values()),
                          families=len(row['histogram']), maxchild=max(row['histogram']),
                          cross_checked_against='references/pr219-run1/schedule.py '
                                                '(retained_profile)'),
        inventories=inventories,
        padding=dict(draws=draws,
                     registers_total=padding_total,
                     share_of_the_singleton_bin=str(Q(padding_total,
                                                      row['histogram'][1])),
                     singleton_before=row['histogram'][1],
                     singleton_after=row['histogram'][1] - padding_total),
        totals=dict(banks=banks_total,
                    items=sum(table['items'] for table in inventories.values()),
                    blocks=sum(table['items'] for table in inventories.values()),
                    padding_registers=padding_total),
        induced_ledger=dict(stock_before=row['W'], stock_after=stock, stock_drop=banks_total,
                            mass_before=row['mass'], mass_after=mass,
                            children_before=sum(row['histogram'].values()),
                            children_after=sum(histogram.values()),
                            families_before=len(row['histogram']),
                            families_after=len(histogram), maxchild_after=max(histogram),
                            singleton_after=histogram[1],
                            histogram_digest=histogram_digest(histogram)),
        remaining_families=remaining,
        pins_gap=pins_gap(),
    )


def main():
    sys.set_int_max_str_digits(0)
    sys.dont_write_bytecode = True
    out = build()
    target = HERE / 'occurrences-bitrung.json'
    target.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + '\n',
                      newline='\n')
    for family in RUNGS:
        table = out['inventories'][str(family)]
        draw = out['padding']['draws'][str(family)]
        print('rank %-3d %5d per vertex x %d = %6d items -> %4d banks x %d blocks '
              '(+%2d padding registers per bank, %6d total), table digest %s'
              % (family, table['children_per_vertex'], COPIES, table['items'], table['banks'],
                 table['capacity_per_bank'], table['padding_per_bank'], draw['registers'],
                 table['bank_table_digest'][:16]))
    ledger = out['induced_ledger']
    print('totals  %d banks, %d items addressed, %d registers of padding (%s of the %d-child '
          'singleton bin)'
          % (out['totals']['banks'], out['totals']['items'], out['totals']['padding_registers'],
             out['padding']['share_of_the_singleton_bin'], out['padding']['singleton_before']))
    print('ledger  stock %d -> %d (drop %d = banks), mass %d -> %d, children %d -> %d over %d '
          'families, singleton %d'
          % (ledger['stock_before'], ledger['stock_after'], ledger['stock_drop'],
             ledger['mass_before'], ledger['mass_after'], ledger['children_before'],
             ledger['children_after'], ledger['families_after'], ledger['singleton_after']))
    print('gap     packed certificate block keys %s, occurrence keys %s; the pins\' only '
          'per-child inventory is %s (%s)'
          % (out['pins_gap']['packed_certificate_block_keys'],
             out['pins_gap']['packed_certificate_occurrence_keys'],
             out['pins_gap']['pinned_item_inventory']['path'],
             ','.join(out['pins_gap']['pinned_item_inventory']['per_vertex_keys'])))
    print('write ' + str(target))


if __name__ == '__main__':
    main()
