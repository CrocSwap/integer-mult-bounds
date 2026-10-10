#!/usr/bin/env python3
"""Instantiating C1's combinatorial half, and C5-C7's inventories, on the padded schedule.

`prototype66.py` fixes the schedule: 531 banks of six rank-11 blocks, 198 banks of four
rank-16 blocks plus 2 registers of padding, 66 banks of three rank-20 blocks plus 6.  This
module *instances* it -- names the items, puts each one in a block, and records what is still
missing -- which is what C5, C6, C7 and the item-to-block half of C1 ask for.

What is built here, and checked rather than described:

* **the inventories (C5, C6, C7).**  Each absorbed family's children are enumerated per vertex
  and over the three copies (1,062 / 264 / 66 per vertex; 3,186 / 792 / 198 in total), and each
  item gets exactly one address: item `i` of a family goes to bank `i // k_f`, block
  `i % k_f`, at offset `(i % k_f) * rank`.  The map is a bijection onto the bank/block/offset
  grid, every block holds exactly one item, and a deterministic digest over the whole table is
  recorded so a reviewer can compare bytes.
* **the bank tables (C1, combinatorial half).**  For each bank, the block layout (which
  registers each block occupies, and which are padding), the padding draw from the retained
  ledger, and the ledger facts the schedule induces (stock drop equal to the bank count).
* **the gap, read from the pins rather than asserted.**  The complex supplier's certificate
  exports no bank construction and -- by its own status line -- no literal operation program;
  the only per-child inventory in the pins is #219's bit-side
  `inputs/absorbed-occurrences.json`.  That file fixes the *shape* the complex side owes, and
  its key set is recorded here, which is what turns "an inventory is owed" into "this artifact,
  with these fields, is owed".

What is still not built, and is not claimed: the physical realization.  The normalizer that
sends each item's residual projector to its block, the frames and charts, the routing and the
prime witnesses (C1's physical half, C2, C3, C4) need data the pinned certificates do not
export -- the item addresses exist here, the residual projectors they must move do not.
"""
import hashlib
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import ledger3  # noqa: E402
import prototype66  # noqa: E402

WIDTH = 66
COPIES = 3
RUNGS = (11, 16, 20)
SUPPLIER = (HERE / 'references' / 'pr219-run1' / 'references'
            / 'pr193-source-assisted-v4.certificate.json')
PR205 = HERE / 'references' / 'pr219-run1' / 'references' / 'pr205-packed.certificate.json'
BIT_OCCURRENCES = HERE / 'references' / 'pr219-run1' / 'inputs' / 'absorbed-occurrences.json'


def address(item, capacity, rank, width):
    """The bank/block/offset address of one item: bank = i // k, block = i % k."""
    bank, block = divmod(item, capacity)
    return dict(item=item, bank=bank, block=block, offset=block * rank,
                registers=rank, padding_registers=list(range(rank * capacity + block * 0,
                                                              rank * capacity + rank * 0)))


def inventory(base, family, width=WIDTH, copies=COPIES):
    """One family's inventory over the copies, with its bank table and digest.

    ``base`` is the *three-copy* row (as the ledger modules build it), so the per-vertex count
    is its bin divided by the copy count: 264 rank-16 children per vertex is 792 in the row.
    """
    per_vertex = base['child_multiplicities'][family] // copies
    assert base['child_multiplicities'][family] % copies == 0, 'copies must divide the bin'
    items = copies * per_vertex
    capacity = width // family
    assert items % capacity == 0, 'the schedule must be saturated: items = k * banks'
    banks = items // capacity
    padding_per_bank = width - family * capacity
    table = [address(i, capacity, family, width) for i in range(items)]
    assert len({(row['bank'], row['block']) for row in table}) == items, 'addresses collide'
    assert all(0 <= row['offset'] < width for row in table), 'offsets must sit in the bank'
    assert all(row['offset'] + family <= width for row in table), 'a block must fit'
    per_bank = {}
    for row in table:
        per_bank.setdefault(row['bank'], []).append(row['block'])
    assert len(per_bank) == banks, 'every bank must be filled'
    assert all(sorted(blocks) == list(range(capacity)) for blocks in per_bank.values()), \
        'every bank must carry each block exactly once'
    digest = hashlib.sha256(
        '\n'.join('%d,%d,%d,%d' % (row['item'], row['bank'], row['block'], row['offset'])
                  for row in table).encode()).hexdigest()
    return dict(family=family, children_per_vertex=per_vertex, copies=copies, items=items,
                capacity_per_bank=capacity, banks=banks, padding_per_bank=padding_per_bank,
                padding_registers=banks * padding_per_bank,
                padding_blocks_per_bank=padding_per_bank,   # rank-1 padding blocks
                address_rule='item i -> bank i // k, block i % k, offset (i % k) * rank',
                bank_table_digest=digest, first_addresses=table[:2], last_address=table[-1])


def pins_gap():
    """What the pins do not export, read from the pinned bytes."""
    supplier = json.loads(SUPPLIER.read_text())
    profile = supplier['complex_profile']
    packed = json.loads(PR205.read_text())
    bit_occ = json.loads(BIT_OCCURRENCES.read_text())

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

    status = profile['status']
    return dict(
        complex_supplier_bank_keys=keys_with(supplier, 'bank'),
        complex_supplier_occurrence_keys=keys_with(supplier, 'occurrence'),
        complex_supplier_status_says_no_operation_program='not exported' in status,
        complex_supplier_status=status,
        pinned_item_inventory=dict(
            path='references/pr219-run1/inputs/absorbed-occurrences.json',
            top_level_keys=sorted(bit_occ),
            per_vertex_keys=sorted(bit_occ['occurrences_per_vertex']),
            counts_per_vertex=bit_occ['counts_per_vertex'],
            note='the only per-child inventory in the pins: it is the bit word\'s rank-22 '
                 'family, and it is what closes #219 R1.  The shape the complex side owes is '
                 'this shape -- one entry per child with its chain/frame provenance.'),
        pinned_bank_construction=dict(
            path='references/pr219-run1/references/pr205-packed.certificate.json',
            physical_banks=int(packed['physical']['banks']),
            gauge_roles=packed['physical']['gauge_roles'],
            bank_controls_keys=sorted(packed['bank_controls']),
            note='width-72 entrance-gauge banks on the bit word: the only bank construction '
                 'in the pins, and the one whose block/normalizer pattern a complex-side '
                 'construction would have to mirror without inheriting'),
    )


def build(base=None, interval=None, ladder=None):
    """The instanced schedule: inventories, bank tables, ledger cross-check, gap.

    ``ladder`` lets a caller that has already priced the padded schedule pass it in, so the
    engine runs once for the whole package rather than once per module.
    """
    interval = interval or ledger3.engine()
    if ladder is None:
        ladder = prototype66.priced_ladder(interval=interval, width=WIDTH)
    if base is None:
        certificate = json.loads(prototype66.FRONTIER.read_text())
        base = ledger3.three_copies(ledger3.profile(certificate['complex_profile']))
    inventories = [inventory(base, family) for family in RUNGS]
    for inv, step in zip(inventories, ladder['ladder']):
        assert inv['family'] == step['family'], 'rung order'
        assert inv['banks'] == step['banks'], 'the schedules must agree on the bank count'
        assert inv['padding_registers'] == step['padding_registers'], 'and on the padding'
        assert step['stock_drop'] == inv['banks'], 'the stock must drop by the bank count'
        assert step['pattern_sum'] == WIDTH, 'every bank must be exactly filled'
    draw = sum(inv['padding_registers'] for inv in inventories)
    kept_bin = base['child_multiplicities'][1]        # three-copy, like the draw
    assert draw <= kept_bin, 'the padding draw must exist in the retained ledger'
    return dict(
        status='C1 combinatorial half and C5-C7 inventories INSTANCED at the schedule level: '
               'every item of every absorbed family has a bank, a block and an offset, and the '
               'ledger the schedule induces is re-derived. The physical half of C1 (the '
               'normalizer) and C2-C4 (formal columns, charts and prime witnesses, moment '
               'envelope parity) remain open: the pins export the item counts, not the '
               'residual projectors the normalizer must move.',
        width=WIDTH, copies=COPIES, rungs=list(RUNGS),
        inventories={str(inv['family']): inv for inv in inventories},
        totals=dict(banks=sum(inv['banks'] for inv in inventories),
                    items=sum(inv['items'] for inv in inventories),
                    padding_registers=draw,
                    padding_share_of_the_kept_bin=str(Q(draw, kept_bin))),
        ledger_cross_check=dict(stock_drops=[step['stock_drop'] for step in ladder['ladder']],
                                retained_stock=ladder['final']['W'],
                                rank_mass=ladder['final']['mass'],
                                children=ladder['final']['children'],
                                criterion_exhausted=ladder['exhaustive']),
        still_owed=dict(
            C1_physical='the normalizer sending each item\'s residual projector to its block: '
                        'the addresses exist here (bank, block, offset), the projectors the '
                        'pinned certificates export do not',
            C2='formal columns of the modified complex word after re-assignment',
            C3='charts, routing and prime witnesses for the new complex blocks',
            C4='complex moment-envelope parity for the re-assigned word',
            C5='per-child provenance for the rank-11 family: the item addresses exist, the '
               'chain/frame identity of each child does not (see the gap)',
            C6='the same for the rank-16 family',
            C7='the same for the rank-20 family',
        ),
        pins_gap=pins_gap(),
    )


def main():
    sys.set_int_max_str_digits(0)
    sys.dont_write_bytecode = True
    out = build()
    target = HERE / 'occurrences66.json'
    target.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + '\n',
                      newline='\n')
    for family in RUNGS:
        inv = out['inventories'][str(family)]
        print('rank %-3d %4d per vertex x %d = %5d items -> %4d banks x %d blocks '
              '(+%d padding registers), digest %s'
              % (family, inv['children_per_vertex'], COPIES, inv['items'], inv['banks'],
                 inv['capacity_per_bank'], inv['padding_registers'],
                 inv['bank_table_digest'][:16]))
    print('totals: %d banks, %d items addressed, %d registers of padding (%s of the kept '
          'rank-1 bin)' % (out['totals']['banks'], out['totals']['items'],
                           out['totals']['padding_registers'],
                           out['totals']['padding_share_of_the_kept_bin']))
    print('ledger: stock drops %s, retained stock %d, criterion exhausted %s'
          % (out['ledger_cross_check']['stock_drops'], out['ledger_cross_check']['retained_stock'],
             out['ledger_cross_check']['criterion_exhausted']))
    print('gap: complex supplier bank keys %s; its status says no operation program: %s'
          % (out['pins_gap']['complex_supplier_bank_keys'],
             out['pins_gap']['complex_supplier_status_says_no_operation_program']))
    print('     the shape owed exists in the pins for the bit word: %s (%s per vertex keys)'
          % (out['pins_gap']['pinned_item_inventory']['path'],
             ','.join(out['pins_gap']['pinned_item_inventory']['per_vertex_keys'])))
    print('write ' + str(target))


if __name__ == '__main__':
    main()
