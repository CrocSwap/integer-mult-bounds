#!/usr/bin/env python3
"""The rank-3 rung's assignment, instanced: every item's bank, block and offset, no padding.

The ladder this package prices absorbs the complex ledger's full-bank families through a
padded width-66 schedule; on the **new row** -- PR233's source-assisted v4 layer
(`references/pr233-source-assisted-v4-layer.certificate.json`, head `109a857`) -- the family
whose own volume fills whole banks is **rank 3**, not rank 16: 29,964 children per vertex,
three registers each, so `3 * 29,964 = 89,892` registers per copy and

    3 * 89,892 = 269,676 = 66 * 4,086

three-copy banks.  Rank 3 divides the bank width (`66 = 22 * 3`), so the bank is **exactly
filled by 22 rank-3 blocks** and the padding the old ladder's rungs 3 and 4 needed (T1) does
not arise at this rung at all: `padding_per_bank = 0`.

What this module instances, and checks rather than describes:

* **the item-to-bank/block/offset map (C1's combinatorial half).**  Item `i` goes to bank
  `i // 22`, block `i % 22`, offset `3 * (i % 22)`.  The map is a bijection onto
  4,086 banks x 22 blocks x 3 registers, every block holds exactly one item, every bank's 66
  registers are used, and a deterministic digest over the whole table is recorded so a
  reviewer can compare bytes.
* **the per-copy table.**  The same map read over one copy: 1,362 banks, the count the row's
  per-vertex bin gives on its own.
* **the ledger the assignment induces (C4's input).**  The retained row after the rank-3
  family leaves, with the stock falling by exactly the bank count and the mass by exactly
  `banks * 66`, and the histogram of what remains.
* **the gap, read from the pins rather than asserted.**  The layer certificate exports no
  bank construction and no item addresses -- machine-read below -- so the assignment exists
  here while the residual projectors the normalizer (C1's physical half) must move do not.

The price the retained row carries is the export contract's business, not this module's:
`rank3contract.py` derives it.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import instantiate66  # noqa: E402
import ledger3  # noqa: E402

ROW_NAME = 'references/pr233-source-assisted-v4-layer.certificate.json'
ROW = HERE / ROW_NAME
FAMILY = 3
WIDTH = 66
COPIES = 3


def row_certificate(path=ROW):
    return json.loads(Path(path).read_text())


def row(path=ROW):
    """The supplier row this rung absorbs from, in PR219's profile form."""
    return ledger3.profile(row_certificate(path)['complex_profile'])


def histogram_digest(histogram):
    """The canonical digest of a child histogram.

    Canonical form, stated once so both author and verifier compute the same bytes: one
    `rank:count` line per bin, ranks ascending, counts as decimal integers, `\\n` between
    lines and no trailing newline, hashed with sha256 over the ASCII encoding.  The three
    lines of a bin whose count is zero are omitted (a histogram carries its positive bins).
    """
    text = '\n'.join('%d:%d' % (rank, count) for rank, count in sorted(histogram.items()))
    return hashlib.sha256(text.encode('ascii')).hexdigest()


def pins_gap(certificate=None):
    """What the pins do not export for this rung, read from the pinned bytes."""
    certificate = certificate or row_certificate()

    def keys_with(node, needle):
        found = []

        def walk(value, path):
            if isinstance(value, dict):
                for key, child in value.items():
                    walk(child, path + '/' + str(key))
            elif isinstance(value, list) and value and isinstance(value[0], (dict, list)):
                walk(value[0], path + '[0]')
            elif needle in path.lower():
                found.append(path)
        walk(node, '')
        return sorted(found)

    return dict(
        row_certificate_bank_keys=keys_with(certificate, 'bank'),
        row_certificate_assignment_keys=keys_with(certificate, 'assign'),
        row_certificate_occurrence_keys=keys_with(certificate, 'occurrence'),
        row_certificate_status=certificate['status'],
        row_certificate_audit_status=certificate['layer']['audit_status'],
        note="the row source publishes the word's formal columns, its fused physical "
             "candidate and its accounting; it publishes no bank, no block layout and no "
             "item address, so the map instanced here has no counterpart in the pins and "
             "the normalizer that must move the items' residual projectors (C1's physical "
             "half) has nothing to move them to.  The only per-child inventory the pins "
             "hold is #219's bit-side inputs/absorbed-occurrences.json, which fixes the "
             "shape the provenance half of C5 owes.",
    )


def build(certificate=None, copied=None):
    """The instanced rank-3 assignment: map, per-copy table, bank table, ledger, gap."""
    certificate = certificate or row_certificate()
    profile = ledger3.profile(certificate['complex_profile'])
    mass = ledger3.check_row(profile)
    copied = copied or ledger3.three_copies(profile)
    per_vertex = profile['child_multiplicities'][FAMILY]
    assert copied['child_multiplicities'][FAMILY] == COPIES * per_vertex, 'copies'

    # the assignment itself, by the same addressing rule the padded schedule uses
    table = instantiate66.inventory(copied, FAMILY, width=WIDTH, copies=COPIES)
    assert table['padding_per_bank'] == 0 and table['padding_registers'] == 0, \
        'rank 3 divides the width: this rung needs no padding at all'
    assert table['capacity_per_bank'] * FAMILY == WIDTH, 'every bank is exactly filled'
    assert table['banks'] % COPIES == 0, 'the copies must divide the bank count'
    banks_per_copy = table['banks'] // COPIES
    assert table['banks'] == COPIES * banks_per_copy, 'per-copy table'

    # the ledger the assignment induces
    step = ledger3.absorb(copied, FAMILY)
    retained = step['retained']
    assert step['volume'] == FAMILY * copied['child_multiplicities'][FAMILY], 'volume'
    assert step['volume'] == step['banks'] * WIDTH, 'the volume is whole banks'
    assert step['banks'] == table['banks'], 'the ledger and the table must agree'
    assert step['stock_drop'] == step['banks'], 'the stock falls by the bank count'

    remaining = []
    for family in ledger3.eligibility(retained):
        entry = ledger3.bankable(retained, family)
        remaining.append(dict(family=family, children=entry['children'],
                              volume=entry['volume'], banks=entry['banks'],
                              divides_width=entry['uniform_tiling'],
                              blocks_per_bank=(str(entry['blocks_per_bank'])
                                               if entry['blocks_per_bank'] else None)))

    return dict(
        status='C1 combinatorial half INSTANCED at the schedule level for this rung: every '
               'item of the rank-3 family has a bank, a block and an offset, every bank is '
               'exactly filled with no padding, and the ledger the assignment induces is '
               're-derived. The physical half of C1 (the normalizer), the provenance half of '
               'C5 (each child\'s frame/chain identity) and C2-C4 remain open: the pins '
               'export the item counts and the formal columns, not the residual projectors '
               'the normalizer must move.',
        row=dict(source=ROW_NAME,
                 head='109a857a329d18ed5552d5573f17ddfa886ae57f',
                 head_subject_name='pairs-only / PR200 maximum-weight reuse pairing',
                 family=FAMILY, width=WIDTH, copies=COPIES,
                 children_per_vertex=per_vertex,
                 m=profile['m'], W_per_vertex=profile['W'], mass_per_vertex=mass),
        assignment=dict(table),
        banks_per_copy=banks_per_copy,
        blocks_per_bank=WIDTH // FAMILY,
        padding_per_bank=0,
        ledger=dict(volume=step['volume'], banks=step['banks'],
                    stock_before=step['stock_before'], stock_after=step['stock_after'],
                    stock_drop=step['stock_drop'], mass_before=step['mass_before'],
                    mass_after=step['mass_after'], children_before=step['children_before'],
                    children_after=step['children_after'],
                    maxchild_before=step['maxchild_before'],
                    maxchild_after=step['maxchild_after'],
                    families_before=len(copied['child_multiplicities']),
                    families_after=len(retained['child_multiplicities']),
                    share_of_ledger=str(step['share_of_ledger']),
                    retained_W=retained['W'], retained_deficit=retained['N'],
                    retained_mass=retained['total_rank'],
                    retained_histogram_digest=histogram_digest(
                        retained['child_multiplicities'])),
        retained_eligibility=ledger3.eligibility(retained),
        remaining_whole_bank_families=remaining,
        pins_gap=pins_gap(certificate),
    )


def main():
    sys.set_int_max_str_digits(0)
    sys.dont_write_bytecode = True
    out = build()
    target = HERE / 'occurrences-rank3.json'
    target.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + '\n',
                      newline='\n')
    table, ledger = out['assignment'], out['ledger']
    print('rank %d  %d per vertex x %d = %d items -> %d banks x %d blocks of %d registers, '
          'padding %d' % (FAMILY, table['children_per_vertex'], COPIES, table['items'],
                          table['banks'], table['capacity_per_bank'], FAMILY,
                          table['padding_per_bank']))
    print('        per copy %d banks; table digest %s'
          % (out['banks_per_copy'], table['bank_table_digest'][:16]))
    print('ledger  stock %d -> %d (drop %d = banks), mass %d -> %d (drop %d = banks * %d)'
          % (ledger['stock_before'], ledger['stock_after'], ledger['stock_drop'],
             ledger['mass_before'], ledger['mass_after'],
             ledger['mass_before'] - ledger['mass_after'], WIDTH))
    print('        children %d -> %d, families %d -> %d, retained histogram %s'
          % (ledger['children_before'], ledger['children_after'], ledger['families_before'],
             ledger['families_after'], ledger['retained_histogram_digest'][:16]))
    print('next    whole-bank families left: %s'
          % ', '.join('rank %d (%d banks)' % (entry['family'], entry['banks'])
                      for entry in out['remaining_whole_bank_families']))
    print('gap     row certificate bank keys %s, assignment keys %s, occurrence keys %s'
          % (out['pins_gap']['row_certificate_bank_keys'],
             out['pins_gap']['row_certificate_assignment_keys'],
             out['pins_gap']['row_certificate_occurrence_keys']))
    print('write ' + str(target))


if __name__ == '__main__':
    main()
