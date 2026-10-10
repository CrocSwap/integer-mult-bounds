#!/usr/bin/env python3
"""The rank-3 rung's export contract, derived rather than typed.

`obligations.json` states C1-C7 for the complex ladder of this package; `EXPORT-CONTRACT.md`
turns them into an interface the importer can accept or refuse, addressed to the supplier
whose word the ladder banks.  This module writes the **same** contract for **one rung** --
the rank-3 family on PR233's new row (`references/pr233-source-assisted-v4-layer.certificate.json`,
head `109a857`) -- where the geometry is simpler than the old rungs 3 and 4 and the money is
different:

* the rung's family **divides the bank width** (`66 = 22 * 3`), so the assignment is one
  uniform tiling with **no padding at all** -- the T1 obligation the padded schedule exists
  to satisfy does not arise here (`occurrences-rank3.json`);
* the retained row prices **higher** than the published top of the ladder, and it prices
  **bit-bound**: after this rung the complex coarse saving no longer binds, so the next
  lever is the bit leaf and not the supplier.

Every number below is derived in `build()` -- from the vendored row certificate, from this
package's own ledger and instanced assignment, from the re-derived bit leaf (rebuilt through
#219's vendored arithmetic, not read off a certificate), and from the queue's unchanged
47-constraint assembly -- and `verify.py -> check_rank3_export_contract` re-derives all of
them and resolves every citation.  Nothing here is a published claim: the row's PR is not
merged, so the point is a target the contract is addressed to, and the certificate.json of
this package still carries the old ladder's kappa.
"""
import json
import sys
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

# The gate of G1-G6 is not a description: every export below names the bodies it requires and
# declares its checks in the importer's own vocabulary (equals, bijection, at_most, flags,
# witnesses, tables, equals_in, declares_every_body_on), so `importer66.py --contract
# export-contract-rank3.json --self-test` exercises it on synthetic bodies and the default import
# refuses the real drop.  Two of the checks are comparisons this package already holds --
# occurrences-rank3.json's table digest and the row's own histogram -- rather than restatements.
import instantiate_rank3  # noqa: E402
import ledger3  # noqa: E402
import run3  # noqa: E402

ROW = instantiate_rank3.ROW
ROW_NAME = instantiate_rank3.ROW_NAME
FAMILY = 3
WIDTH = instantiate_rank3.WIDTH
COPIES = instantiate_rank3.COPIES
GRID = 10 ** 18
HEAD = '109a857a329d18ed5552d5573f17ddfa886ae57f'


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def cite(source, keys, value):
    return dict(source=source, keys=keys, value=value)


def body(file_name, stream=False, anchored=None):
    """One body the contract requires: named, hashed as published, parsed only if it is not a
    stream.  The importer's vocabulary, so the contract needs no translation to be executable."""
    return dict(file=file_name, stream=stream, anchored_digest=anchored)


def price(interval, retained):
    """The rung's own price: the retained coarse saving, the bit leaf, the assembly."""
    certified = ledger3.certify(interval, retained)
    coarse = Q(certified['saving'])
    assert certified['next_excluded']['lower'] > 1, \
        'the next 10^-18 grid point up must be excluded by the interval moment'
    schedule, arithmetic = ledger3.run1()
    leaf = arithmetic.build(schedule.build())['ordinary_leaf']
    published_leaf = Q(json.loads((HERE / 'certificate.json').read_text())
                       ['calibrations']['run1']['bit_leaf'])
    assert leaf == published_leaf, 'the re-derived leaf must be the published one'
    budget, bound, kappa = run3.frontier_kappa(leaf, coarse)
    supplier = json.loads(run3.PR193.read_text())
    supplier['assembly']['finite_bridge']['rows']['degree_gap'] = Q(
        supplier['assembly']['finite_bridge']['rows']['degree_gap'])
    assembly = run3.assemble(supplier, budget, coarse, kappa)
    adjacent_rejected = True
    try:
        run3.assemble(supplier, budget, coarse, kappa + Q(1, GRID))
    except AssertionError:
        pass
    else:
        adjacent_rejected = False
    assert adjacent_rejected, 'the adjacent 10^-18 point must be rejected'
    complex_branch = (1 - run3.BETA) * coarse - run3.WEAK
    assert budget == leaf < complex_branch, 'this rung is bit-bound, not complex-bound'
    # The assembly is green at this budget, and green *tightly*: its tightest strict
    # constraint is lambda - tau, which at a budget equal to the bit branch's own saving is
    # exactly the design backoff, a * eta.  Checked rather than described.
    assert assembly['minimum_constraint'] == budget * run3.ETA, \
        'the tightest of the 47 constraints must be the design backoff a * eta'
    return dict(coarse=coarse, next_excluded=coarse + Q(1, GRID),
                next_excluded_excluded=True, plateau_top=True,
                leaf=leaf, budget=budget, bound=bound, kappa=kappa,
                binding='bit', complex_branch=complex_branch,
                complex_ceiling=ledger3.ceiling(coarse),
                ceiling_gap=ledger3.ceiling(coarse) - kappa,
                leaf_headroom=leaf - budget, assembly=assembly,
                adjacent_grid_rejected=adjacent_rejected)


def build():
    sys.set_int_max_str_digits(0)
    certificate = instantiate_rank3.row_certificate()
    row = instantiate_rank3.row()
    assert row['m'] == WIDTH, 'the row must be the width-66 word'
    copied = ledger3.three_copies(row)
    instance = instantiate_rank3.build(certificate, copied)
    step = ledger3.absorb(copied, FAMILY)
    retained = step['retained']
    table = instance['assignment']
    point = price(ledger3.engine(), retained)
    published_top = Q(json.loads((HERE / 'certificate.json').read_text())['top']['kappa'])
    frontier_kappa = Q(json.loads((HERE / 'references'
                                   / 'pr207-coordinated-crossover.certificate.json')
                            .read_text())['kappa'])
    assert point['kappa'] > published_top and point['kappa'] > frontier_kappa, \
        'the rung must beat both the top this package publishes and the pinned frontier'
    row_own = dict(complex_saving=Q(certificate['complex_saving']),
                   kappa=Q(certificate['kappa']),
                   bit_effective=Q(certificate['assembly']['bit_effective_saving']))
    gain = point['kappa'] / published_top - 1

    def hist_cite(source, keys, key_name):
        """A citation for a histogram, in the certificate's own integer keys."""
        return cite(source, keys + [key_name], certificate['complex_profile']
                    ['child_histogram'][key_name])

    out = {}
    out['contract'] = (
        "the rank-3 rung's export contract: what the supplier's program must publish for the "
        "rank-3 family of PR233's row to become a bank increment, C1-C7 restated at this rung")
    out['version'] = 3
    out['source'] = 'research/complex-bank-run3/EXPORT-CONTRACT-RANK3.md (the prose twin this ' \
                    'file makes checkable)'
    out['scope'] = (
        "One rung of the complex ladder, on the new row: the rank-3 family leaves the ledger "
        "into %d whole width-66 banks with no padding (rank 3 divides the width), and the "
        "retained row re-prices the top of the ladder bit-bound. C1-C7 of obligations.json are "
        "restated here at this rung's numbers; the required exports G1-G6 are the bodies that "
        "would turn that restatement into a bank increment, each with the form, cardinality, "
        "digest and acceptance test it is held to. verify.py -> check_rank3_export_contract "
        "re-derives every number and resolves every citation, so the contract cannot cite a "
        "digest, a count or a status that is not there -- and cannot claim the rung is built."
        % table['banks'])
    out['rung'] = dict(
        family=FAMILY, width=WIDTH, copies=COPIES,
        name='the rank-3 family of the row below, absorbed into whole width-66 banks',
        not_this="rung 3 of run3.py's ladder: that rung absorbs rank 16 on PR207/PR193's row "
                 "and needs the padded schedule of T1.  On this row the first family whose own "
                 "volume fills whole banks is rank 3, and the padding does not arise.",
        row=dict(
            source=ROW_NAME, head=HEAD, head_subject=certificate['status'],
            sha256=digest(ROW), bytes=len(ROW.read_bytes()),
            not_vendored_from='the pins: this file is #233\'s certificate at head %s, and the '
                              'digest above is what pins it.  The PR is not merged, so if the '
                              'branch moves the pin fails closed (verify.py -> check_manifest) '
                              'and this contract must be re-taken rather than reused.' % HEAD,
            head_commit_subject='Pairs only: PR168\'s frames unchanged, PR200\'s maximum-weight '
                                'reuse pairing; complex saving 3549537/5000000000 = 7.0991e-4 '
                                '(+1.28% over PR194)',
            status=certificate['status'],
            audit_status=certificate['layer']['audit_status'],
            own_kappa=str(row_own['kappa']), own_complex_saving=str(row_own['complex_saving']),
            own_bit_effective=str(row_own['bit_effective'])),
        geometry=dict(children_per_vertex=row['child_multiplicities'][FAMILY],
                      registers_per_vertex=FAMILY * row['child_multiplicities'][FAMILY],
                      volume_three_copies=step['volume'], banks=step['banks'],
                      banks_per_copy=instance['banks_per_copy'],
                      blocks_per_bank=instance['blocks_per_bank'],
                      registers_per_block=FAMILY,
                      padding_per_bank=table['padding_per_bank'],
                      padding_registers=table['padding_registers'],
                      rank_divides_width=True,
                      volume_is_whole_banks=step['volume'] == step['banks'] * WIDTH,
                      tiling='66 = 22 * 3: the bank is exactly filled by 22 rank-3 blocks, so '
                             'the padding registers the padded schedule needs at ranks 16 and '
                             '20 (T1) are zero here'),
        citations=[
            cite(ROW_NAME, ['complex_profile', 'm'], certificate['complex_profile']['m']),
            cite(ROW_NAME, ['complex_profile', 'W_per_vertex'],
                 certificate['complex_profile']['W_per_vertex']),
            cite(ROW_NAME, ['complex_profile', 'deficit_per_vertex'],
                 certificate['complex_profile']['deficit_per_vertex']),
            cite(ROW_NAME, ['complex_profile', 'rank_per_vertex'],
                 certificate['complex_profile']['rank_per_vertex']),
            cite(ROW_NAME, ['complex_saving'], certificate['complex_saving']),
            cite(ROW_NAME, ['kappa'], certificate['kappa']),
            cite(ROW_NAME, ['binding'], certificate['binding']),
            cite(ROW_NAME, ['lift', 'nodes'], certificate['lift']['nodes']),
            cite(ROW_NAME, ['lift', 'physical_R'], certificate['lift']['physical_R']),
            cite(ROW_NAME, ['lift', 'max_denominator'], certificate['lift']['max_denominator']),
            cite(ROW_NAME, ['layer', 'frames'], certificate['layer']['frames']),
            cite(ROW_NAME, ['layer', 'pairs'], certificate['layer']['pairs']),
            cite(ROW_NAME, ['layer', 'frames_changed_from_pr168'],
                 certificate['layer']['frames_changed_from_pr168']),
            cite(ROW_NAME, ['layer', 'formal', 'packed_digit_bits'],
                 certificate['layer']['formal']['packed_digit_bits']),
            cite(ROW_NAME, ['layer', 'formal', 'columns', 0, 'source_columns'],
                 certificate['layer']['formal']['columns'][0]['source_columns']),
            cite(ROW_NAME, ['layer', 'formal', 'columns', 0, 'target_columns'],
                 certificate['layer']['formal']['columns'][0]['target_columns']),
            cite(ROW_NAME, ['layer', 'formal', 'columns', 0, 'dirty_columns'],
                 certificate['layer']['formal']['columns'][0]['dirty_columns']),
            cite(ROW_NAME, ['layer', 'formal', 'columns', 1, 'dirty_columns'],
                 certificate['layer']['formal']['columns'][1]['dirty_columns']),
            cite(ROW_NAME, ['contract_checks', 'read_counts'],
                 certificate['contract_checks']['read_counts']),
            cite(ROW_NAME, ['contract_checks', 'checked_source_columns'],
                 certificate['contract_checks']['checked_source_columns']),
            cite(ROW_NAME, ['contract_checks', 'checked_target_rows'],
                 certificate['contract_checks']['checked_target_rows']),
            cite(ROW_NAME, ['contract_checks', 'all_fresh_columns_equal_identity'],
                 certificate['contract_checks']['all_fresh_columns_equal_identity']),
            cite(ROW_NAME, ['flow', 'new_W'], certificate['flow']['new_W']),
            cite(ROW_NAME, ['flow', 'new_R'], certificate['flow']['new_R']),
            cite(ROW_NAME, ['flow', 'deficit'], certificate['flow']['deficit']),
            cite(ROW_NAME, ['flow', 'loss'], certificate['flow']['loss']),
            hist_cite(ROW_NAME, ['complex_profile', 'child_histogram'], '3'),
            hist_cite(ROW_NAME, ['complex_profile', 'child_histogram'], '4'),
            hist_cite(ROW_NAME, ['complex_profile', 'child_histogram'], '18'),
            hist_cite(ROW_NAME, ['complex_profile', 'child_histogram'], '20'),
        ],
        )

    out['machine_read'] = dict(
        about='what the row publishes as *bodies*, read out of the pinned file rather than '
              'assumed: this is what makes the 0-of-6 below a reading rather than a verdict',
        bank_keys=[], assignment_keys=[], occurrence_keys=[],
        audit_source_digests=sorted(certificate['layer']['audit_source_sha256']),
        note='the row certificate carries the word\'s formal columns, the fused physical '
             'candidate and the accounting.  It carries no bank key, no assignment key and no '
             'occurrence key: the map instanced by this package (occurrences-rank3.json) has '
             'no counterpart in the row, and the normalizer (C1\'s physical half) has no '
             'exported projector to move.')

    out['our_side'] = dict(
        about='the half of this contract that does exist, in this package, and is the '
              'bijection target the export is checked against',
        body='occurrences-rank3.json', module='instantiate_rank3.py',
        assignment=dict(table),
        ledger=instance['ledger'],
        retained_eligibility=instance['retained_eligibility'],
        remaining_whole_bank_families=instance['remaining_whole_bank_families'],
        still_owed='the physical half of C1 (the normalizer), the provenance half of C5 (each '
                   'child\'s frame or chain identity) and C2-C4: see still_owed below',
        citations=[cite('occurrences-rank3.json', ['assignment', 'items'], table['items']),
                   cite('occurrences-rank3.json', ['assignment', 'banks'], table['banks']),
                   cite('occurrences-rank3.json', ['banks_per_copy'],
                        instance['banks_per_copy']),
                   cite('occurrences-rank3.json', ['assignment', 'padding_registers'],
                        table['padding_registers']),
                   cite('occurrences-rank3.json', ['ledger', 'stock_drop'], step['stock_drop'])],
        allowed_to_move=dict(
            why='one number in this contract is derived and not published today: the point '
                'below.  The row\'s PR is not merged, so certificate.json still carries the '
                'old ladder\'s kappa, and the contract must be read as a target rather than '
                'as a claim.',
            published_top_kappa=str(published_top),
            rung_kappa=str(point['kappa']),
            gain_vs_published_top=str(gain),
            publication_status='the rung is a derived target on an unmerged row: this contract '
                               'states what it would take, and the comparison below is against '
                               'numbers this package already publishes',
            beats_published_top=str(point['kappa'] > published_top),
            beats_pinned_frontier=str(point['kappa'] > frontier_kappa),
            published_top=str(published_top), pinned_frontier=str(frontier_kappa),
            kappa=str(point['kappa'])))

    out['point'] = dict(
        about='the price of the retained row, derived here and not published: the row\'s PR is '
              'not merged, so this is the target the contract is addressed to',
        coarse=str(point['coarse']), coarse_decimal=float(point['coarse']),
        next_excluded=str(point['next_excluded']),
        next_excluded_bound_above_one=point['next_excluded_excluded'],
        leaf=str(point['leaf']), leaf_decimal=float(point['leaf']),
        budget=str(point['budget']), budget_is_the_leaf=point['budget'] == point['leaf'],
        kappa=str(point['kappa']), kappa_decimal=float(point['kappa']),
        binding=point['binding'],
        complex_branch=str(point['complex_branch']),
        complex_branch_decimal=float(point['complex_branch']),
        complex_ceiling=str(point['complex_ceiling']),
        complex_ceiling_decimal=float(point['complex_ceiling']),
        ceiling_gap=str(point['ceiling_gap']),
        bit_leaf_headroom=str(point['leaf_headroom']),
        assembly=dict(
            tightest_constraint=str(point['assembly']['minimum_constraint']),
            tightest_constraint_decimal=float(point['assembly']['minimum_constraint']),
            tightest_constraint_name='lambda - tau = budget * eta (the design backoff)',
            constraints=47, margins=7,
            reading='all 47 strict constraints are positive, and the tightest is the design '
                    'backoff rather than room: with the budget at the bit leaf the assembly '
                    'is exactly as green as its own eta.'),
        adjacent_grid_rejected=point['adjacent_grid_rejected'],
        published_top_kappa=str(published_top),
        gain_vs_published_top=str(gain), gain_vs_published_top_percent=float(gain) * 100,
        beats_published_top=point['kappa'] > published_top,
        frontier_kappa=str(frontier_kappa), frontier_kappa_decimal=float(frontier_kappa),
        gain_vs_frontier=str(point['kappa'] / frontier_kappa - 1),
        gain_vs_frontier_percent=float(point['kappa'] / frontier_kappa - 1) * 100,
        beats_frontier=point['kappa'] > frontier_kappa,
        frontier_source='references/pr207-coordinated-crossover.certificate.json -> kappa: the '
                        'pinned frontier this package prices against, and the number the '
                        'comparison is made against offline',
        reading='after this rung the complex branch no longer binds: the budget is the bit '
                'leaf, so the rung is bit-bound and the next lever is the leaf, not the '
                'supplier.  The complex ceiling is still %.6e above the kappa, which is why '
                'the rung is not ceiling-tight the way the published ladder\'s rungs are.'
                % float(point['ceiling_gap']))

    out['precedent'] = dict(
        banked_word_export_shape=dict(
            reading='the one banked word in the pins publishes its physical layer as counts, '
                    'digests and a colouring status: that is the shape G1 and G4 must reach '
                    'on this row\'s 4,086 banks',
            citations=[
                cite('references/pr219-run1/references/pr205-packed.certificate.json',
                     ['physical', 'm'], 72),
                cite('references/pr219-run1/references/pr205-packed.certificate.json',
                     ['physical', 'banks'], 45842),
                cite('references/pr219-run1/references/pr205-packed.certificate.json',
                     ['physical', 'physical_roles'], 17114),
                cite('references/pr219-run1/references/pr205-packed.certificate.json',
                     ['physical', 'color_stats', 'swaps'], 733),
                cite('references/pr219-run1/references/pr205-packed.certificate.json',
                     ['physical', 'color_stats', 'longest_swapped_path'], 11),
                cite('references/pr219-run1/references/pr205-packed.certificate.json',
                     ['physical', 'status'],
                     'PASS exact actual-chain chart and incidence checks')]),
        occurrence_inventory_shape=dict(
            reading='#219\'s bit-side inventory is the format precedent for G5: counts per '
                    'vertex, occurrences as integer tuples per kind, the row identity, and the '
                    'source pins that tie the inventory to the word it was enumerated on',
            citations=[
                cite('references/pr219-run1/inputs/absorbed-occurrences.json',
                     ['counts_per_vertex', 'ledger_bin_22_per_vertex'], 6672),
                cite('references/pr219-run1/inputs/absorbed-occurrences.json',
                     ['counts_per_vertex', 'normalization_factor_in_row'], 3),
                cite('references/pr219-run1/inputs/absorbed-occurrences.json',
                     ['row_identity_per_vertex', 'm'], 72),
                cite('references/pr219-run1/inputs/absorbed-occurrences.json',
                     ['source_pins', 'package'], 'research/paired-cube-diagonal-bit-168')]),
        the_contract_this_specialises=dict(
            reading='this package\'s complex-side contract is the general form; this file is '
                    'that contract instantiated at one rung, with the rung\'s own numbers',
            citations=[
                cite('export-contract.json', ['today', 'of_required'], 6),
                cite('export-contract.json', ['required_exports', 0, 'id'], 'E1'),
                cite('export-contract.json', ['acceptance_tests', 6, 'id'], 'A7')]),
    )

    out['today'] = dict(
        bodies_present=0, of_required=6,
        gate_exit_codes=dict(default=2, partial=4, gate_green_without_a_checker=3),
        about='the supplier\'s side of this rung: what the row publishes as bodies rather '
              'than as digests, counts or statuses',
        verdict='fail closed: not one of the six required exports exists as a body. The row '
                'publishes the word\'s accounting and the physical candidate\'s column '
                'counts; it publishes no bank, no block layout, no item address and no '
                'per-child provenance, so the import is refused, the rung stays a scheduled '
                'target and the kappa keeps its conditional flag.',
        published_only_as=['digest', 'count', 'status', 'path'],
        evidence=[
            cite(ROW_NAME, ['status'], certificate['status']),
            cite(ROW_NAME, ['layer', 'audit_status'], certificate['layer']['audit_status']),
            cite(ROW_NAME, ['contract_checks',
                            'all_fresh_columns_equal_identity'],
                 certificate['contract_checks']
                 ['all_fresh_columns_equal_identity']),
            cite(ROW_NAME, ['layer', 'formal', 'columns', 0, 'every_formal_column'],
                 certificate['layer']['formal']['columns'][0]['every_formal_column']),
            cite(ROW_NAME, ['lift', 'status'], certificate['lift']['status']),
        ])

    out['required_exports'] = [
        dict(
            id='G1', name='the assignment and the bank table',
            publishes='the item-to-bank/block/offset map for all %d three-copy items of the '
                      'rank-3 family onto %d banks x %d blocks x %d registers, the per-bank '
                      'layout of all %d registers (none of them padding), the per-copy table '
                      'of %d banks, and a digest over the whole table'
                      % (table['items'], table['banks'], instance['blocks_per_bank'],
                         FAMILY, WIDTH, instance['banks_per_copy']),
            form='JSON, integers only: `item_to_block`, one entry per item carrying its '
                 'address as [bank, block, offset]; `bank_table`, the per-bank block layout; '
                 'the counts `items`, `banks`, `blocks_per_bank`, `registers_per_block`, '
                 '`registers_per_bank`, `banks_per_copy`, `padding_per_bank` and '
                 '`padding_registers`; and `bank_table_digest`, the digest over the whole '
                 'table',
            cardinality=dict(items=table['items'], banks=table['banks'],
                             blocks_per_bank=instance['blocks_per_bank'],
                             registers_per_block=FAMILY, registers_per_bank=WIDTH,
                             banks_per_copy=instance['banks_per_copy'],
                             padding_per_bank=0, padding_registers=0),
            must_reproduce=[
                cite('occurrences-rank3.json', ['assignment', 'bank_table_digest'],
                     table['bank_table_digest']),
                cite('occurrences-rank3.json', ['assignment', 'items'], table['items']),
                cite('occurrences-rank3.json', ['assignment', 'banks'], table['banks'])],
            bodies=[body('assignment.json')],
            gate=dict(test=['A2'],
                      equals=dict(items=table['items'], banks=table['banks'],
                                  blocks_per_bank=instance['blocks_per_bank'],
                                  registers_per_block=FAMILY, registers_per_bank=WIDTH,
                                  banks_per_copy=instance['banks_per_copy'],
                                  padding_per_bank=0, padding_registers=0),
                      bijection=['item_to_block'],
                      equals_in=[dict(
                          body_key='bank_table', source='occurrences-rank3.json',
                          keys=['assignment'],
                          fields=['items', 'banks', 'capacity_per_bank', 'padding_per_bank',
                                  'bank_table_digest'],
                          per_key_of_body=True,
                          why='the export must name the same items, banks, capacity and table '
                              'digest this package has already instanced from the addressing '
                              'rule, which is what makes A2 a bijection against that rule '
                              'rather than a count of it')]),
            acceptance=['A1', 'A2', 'A3'], unblocks=['C1', 'C5']),
        dict(
            id='G2', name='the normalizer',
            publishes='the literal operation program of this layer in canonical order -- per '
                      'node its canonical id, kind, incoming and outgoing edge ids and span -- '
                      'together with the map that sends each of the %d items\' true residual '
                      'projectors to the block G1 assigns it' % table['items'],
            form='JSON, integers only: the program as `nodes`, `physical_R` and the node and '
                 'edge records themselves; `items_moved` and `banks`, the two counts the '
                 're-assignment reaches; and `audit_source_digests`, the digest set the '
                 'export is audited against',
            cardinality=dict(nodes=certificate['lift']['nodes'],
                             physical_R=certificate['lift']['physical_R'],
                             max_denominator=certificate['lift']['max_denominator'],
                             items_moved=table['items'], banks=table['banks'],
                             audit_sources=len(certificate['layer']['audit_source_sha256'])),
            must_reproduce=[
                cite(ROW_NAME, ['lift', 'nodes'], certificate['lift']['nodes']),
                cite(ROW_NAME, ['lift', 'physical_R'], certificate['lift']['physical_R']),
                cite(ROW_NAME, ['lift', 'max_denominator'],
                     certificate['lift']['max_denominator'])],
            bodies=[body('normalizer.json')],
            gate=dict(test=['A1', 'A5'],
                      equals=dict(nodes=certificate['lift']['nodes'],
                                  physical_R=certificate['lift']['physical_R'],
                                  items_moved=table['items'], banks=table['banks']),
                      at_most=dict(max_denominator=int(certificate['lift']['max_denominator'])),
                      equals_in=[dict(
                          body_key='audit_source_digests', source=ROW_NAME,
                          keys=['layer', 'audit_source_sha256'],
                          why='the normalizer must be audited against the sources the row '
                              'itself audits against: the digest set is the row\'s published '
                              'one, not a count of it')]),
            acceptance=['A1', 'A5'], unblocks=['C1']),
        dict(
            id='G3', name='the program and the columns of the modified word',
            publishes='the renumbered program and the complete formal-column checks re-run on '
                      'the word after the re-assignment: every source, target and dirty-register '
                      'column over F2 and over the defining integers, with the target chronology '
                      'nested, the source controls at paid-parity frames, and the two mutation '
                      'controls rejected',
            form='JSON tables of integer addresses under `tables`, one row per column, plus '
                 'the summary counts `checked_source_columns`, `checked_target_rows`, '
                 '`checked_dirty_columns`, `packed_digit_bits`, `pairs` and `read_counts`',
            cardinality=dict(checked_source_columns=
                             certificate['contract_checks']
                             ['checked_source_columns'],
                             checked_target_rows=
                             certificate['contract_checks']
                             ['checked_target_rows'],
                             dirty_columns=certificate['layer']['formal']['columns'][0]
                             ['dirty_columns'],
                             packed_digit_bits=certificate['layer']['formal']
                             ['packed_digit_bits']),
            must_reproduce=[
                cite(ROW_NAME, ['contract_checks', 'checked_source_columns'],
                     certificate['contract_checks']
                     ['checked_source_columns']),
                cite(ROW_NAME, ['contract_checks', 'checked_target_rows'],
                     certificate['contract_checks']['checked_target_rows']),
                cite(ROW_NAME, ['contract_checks', 'read_counts'],
                     certificate['contract_checks']['read_counts']),
                cite(ROW_NAME, ['layer', 'formal', 'columns', 0, 'dirty_columns'],
                     certificate['layer']['formal']['columns'][0]['dirty_columns']),
                cite(ROW_NAME, ['layer', 'pairs'], certificate['layer']['pairs']),
                cite(ROW_NAME, ['layer', 'mutations'], certificate['layer']['mutations'])],
            bodies=[body('columns.json')],
            gate=dict(test=['A5'],
                      equals=dict(checked_source_columns=certificate['contract_checks']
                                  ['checked_source_columns'],
                                  checked_target_rows=certificate['contract_checks']
                                  ['checked_target_rows'],
                                  checked_dirty_columns=
                                  certificate['layer']['formal']['columns'][0]['dirty_columns'],
                                  packed_digit_bits=certificate['layer']['formal']
                                  ['packed_digit_bits'],
                                  pairs=certificate['layer']['pairs']),
                      counted_in_tables=dict(source_columns='checked_source_columns',
                                             target_rows='checked_target_rows',
                                             dirty_columns='checked_dirty_columns'),
                      equals_in=[dict(
                          body_key='read_counts', source=ROW_NAME,
                          keys=['contract_checks', 'read_counts'],
                          why='the centre, deferred and side read counts the row publishes, '
                              'reproduced verbatim: A5 is a re-run of the columns, so the '
                              'counts it was driven by are part of the body')]),
            acceptance=['A5'], unblocks=['C2', 'C1']),
        dict(
            id='G4', name='charts, colouring and prime witnesses',
            publishes='exact charts (integer kernel bases, fraction-free inverses, replayed '
                      'elementary factors) for every frame the new bank blocks use, the incidence '
                      'colouring of the %d new bank incidences, and distinct integer Gram/prime '
                      'witnesses for every one of those frames' % (table['banks'] * WIDTH),
            form='JSON bodies per chart, plus an index carrying the counts `charts` and '
                 '`incidences`, the colouring `color_stats`, the control flag '
                 '`conflicting_assignment_rejected` and the witness table `prime_witnesses` '
                 'with its bound `q_bound`; the two streams are published byte-for-byte',
            cardinality=dict(charts=table['banks'] * instance['blocks_per_bank'],
                             incidences=table['banks'] * WIDTH,
                             max_denominator=certificate['lift']['max_denominator'],
                             physical_roles=17114),
            must_reproduce=[
                cite(ROW_NAME, ['lift', 'max_denominator'],
                     certificate['lift']['max_denominator']),
                cite('references/pr219-run1/references/pr205-packed.certificate.json',
                     ['physical', 'physical_roles'], 17114),
                cite('references/pr219-run1/references/pr205-packed.certificate.json',
                     ['physical', 'color_stats', 'swaps'], 733)],
            bodies=[body('charts.index.json.gz'), body('charts.json', stream=True),
                    body('incidence.json', stream=True), body('prime-witnesses.json.gz')],
            gate=dict(test=['A6', 'A7'],
                      equals=dict(charts=table['banks'] * instance['blocks_per_bank'],
                                  incidences=table['banks'] * WIDTH),
                      at_most=dict(max_denominator=int(certificate['lift']['max_denominator'])),
                      flags_true=['conflicting_assignment_rejected'],
                      distinct_below=dict(witnesses='prime_witnesses', bound='q_bound'),
                      equals_in=[dict(
                          body_key='color_stats',
                          source='references/pr219-run1/references/pr205-packed.certificate.json',
                          keys=['physical', 'color_stats'],
                          fields=['swaps', 'longest_swapped_path'],
                          per_key_of_body=True,
                          why='the only incidence colouring in the pins is the bit word\'s, '
                              'and its two numbers are what a new colouring is compared '
                              'against: the export must reproduce them rather than report '
                              'a status')]),
            acceptance=['A6', 'A7'], unblocks=['C3']),
        dict(
            id='G5', name='the per-child provenance inventory',
            publishes='one entry per child of the rank-3 family with its frame or chain '
                      'identity, in the shape of the pinned bit-side inventory: counts per '
                      'vertex, occurrences as integer tuples per kind, the row identity, and '
                      'the source pins that tie the inventory to the word it was enumerated on',
            form='JSON: counts_per_vertex, occurrences_per_vertex, row_identity_per_vertex, '
                 'source_pins, and the re-assignment counts `children_per_vertex`, `items`, '
                 '`banks`, `blocks_per_bank` and `registers_per_block`',
            cardinality=dict(children_per_vertex=row['child_multiplicities'][FAMILY],
                             items=table['items'], banks=table['banks'],
                             blocks_per_bank=instance['blocks_per_bank']),
            must_reproduce=[
                cite(ROW_NAME, ['complex_profile', 'child_histogram', '3'],
                     row['child_multiplicities'][FAMILY]),
                cite('references/pr219-run1/inputs/absorbed-occurrences.json',
                     ['counts_per_vertex', 'normalization_factor_in_row'], 3),
                cite('occurrences-rank3.json', ['assignment', 'items'], table['items']),
                cite('occurrences-rank3.json', ['assignment', 'banks'], table['banks'])],
            bodies=[body('children.json')],
            gate=dict(test=['A3'],
                      equals=dict(children_per_vertex=row['child_multiplicities'][FAMILY],
                                  items=table['items'], banks=table['banks'],
                                  blocks_per_bank=instance['blocks_per_bank'],
                                  registers_per_block=FAMILY),
                      equals_in=[dict(
                          body_key='counts_per_vertex', source=ROW_NAME,
                          keys=['complex_profile', 'child_histogram'],
                          fields=['3'], per_key_of_body=True,
                          why='the export must carry the row\'s own rank-3 count, read out '
                              'of the row\'s histogram rather than from this contract: that is '
                              'what makes the inventory a bijection with the enumerated '
                              'occurrences rather than a restatement')]),
            acceptance=['A3'], unblocks=['C5', 'C6', 'C7', 'C1']),
        dict(
            id='G6', name='the envelope and the integrity manifest',
            publishes='the paid moment envelope of the retained row in the form arithmetic.py '
                      'consumes (retained stock, deficit, the retained histogram, the '
                      'worst-case bad fraction, the convention\'s fallback), plus every digest '
                      'of G1-G5 and the list of acceptance predicates actually run',
            form='JSON envelope plus manifest.  The envelope carries the retained counts '
                 '`retained_stock`, `retained_deficit`, `retained_mass`, `retained_children` '
                 'and `retained_families`, the bank count, the retained histogram digest, and '
                 'the rung\'s own point as exact fraction strings `coarse` and `kappa` with '
                 '`binding`; the manifest is `integrity.json`, one digest per published body',
            cardinality=dict(retained_stock=retained['W'], retained_deficit=retained['N'],
                             retained_mass=retained['total_rank'],
                             retained_children=sum(retained['child_multiplicities'].values()),
                             retained_families=len(retained['child_multiplicities']),
                             banks=table['banks']),
            must_reproduce=[
                cite('occurrences-rank3.json', ['ledger', 'retained_W'], retained['W']),
                cite('occurrences-rank3.json', ['ledger', 'retained_deficit'], retained['N']),
                cite('occurrences-rank3.json', ['ledger', 'retained_mass'],
                     retained['total_rank']),
                cite('occurrences-rank3.json', ['ledger', 'retained_histogram_digest'],
                     instance['ledger']['retained_histogram_digest'])],
            bodies=[body('envelope.json'), body('integrity.json')],
            gate=dict(test=['A4'],
                      equals=dict(retained_stock=retained['W'],
                                  retained_deficit=retained['N'],
                                  retained_mass=retained['total_rank'],
                                  retained_children=sum(
                                      retained['child_multiplicities'].values()),
                                  retained_families=len(retained['child_multiplicities']),
                                  banks=table['banks'], coarse=str(point['coarse']),
                                  kappa=str(point['kappa']), binding=point['binding']),
                      declares_every_body_on='integrity.json',
                      equals_in=[dict(
                          body_key='retained_histogram_digest',
                          source='occurrences-rank3.json',
                          keys=['ledger', 'retained_histogram_digest'],
                          why='the retained histogram is the one object of this rung the '
                              'contract can compare byte for byte: the envelope must carry '
                              'the digest of the row the absorption induces, so a single '
                              'child moving in any other bin is caught by the gate rather '
                              'than by the physics')]),
            acceptance=['A4'], unblocks=['C4', 'R4']),
    ]

    out['import_harness'] = dict(
        module='importer66.py',
        contract='export-contract-rank3.json',
        exports_dir='exports-rank3',
        usage='python3 -B importer66.py --contract export-contract-rank3.json --exports DIR '
              '[--checker FILE] [--partial] | --self-test',
        exit_codes={
            '0': 'admissible: every body present, the gate green and the pinned replay '
                 'checker passed',
            '1': 'a check failed: the report names the test, its bound and what was seen',
            '2': 'refusing: at least one required body is absent, or the supplied checker is '
                 'not the one the contract pins, so nothing is run and nothing is certified',
            '3': 'gate green, replay NOT RUN: no checker was supplied',
            '4': 'partial: the gate was run on the bodies present, for reporting only; '
                 'nothing is discharged'},
        layers=dict(
            gate='decidable from the bodies\' declared data: the hashes and the manifest '
                 '(A1), the item-to-block bijection, the counts and the instanced table digest '
                 '(A2), the row\'s own rank-3 count (A3), the retained envelope, the histogram '
                 'digest and the point (A4), the column counts that must come out of the '
                 'exported tables and the row\'s read counts (A5), the colouring control and '
                 'the precedent it is compared against (A6) and the witnesses (A7).  The '
                 'importer runs these checks and only these; every one of them is exercised '
                 'by --self-test',
            replay='the physics: the formal columns over F2 and the defining integers, the '
                   'fraction-free chart replay, the incidence colouring and the moment '
                   'envelope re-derived.  The harness does not reimplement any of it and '
                   'never claims to have run it'),
        replay_requirement=dict(
            checker_digest=None,
            checker_source='none: the row this rung is priced on publishes no checker digest',
            why='the general contract (export-contract.json -> E3) pins the supplier\'s own '
                'checker by digest because that certificate publishes one '
                '(lift.checker_sha256).  This row does not, and that is a reading rather than '
                'a gap in the harness: a walk of the pinned bytes finds no key containing '
                '"checker" anywhere in the certificate, and its nearest published evidence is '
                'layer.audit_source_sha256, five source digests, which is a digest set and not '
                'a checker.  So there is no digest for the harness to accept: with no checker '
                'supplied the replay is reported NOT RUN (exit 3), and a checker that is '
                'supplied cannot match and the import is refused (exit 2).  verify.py asserts '
                'the absence against the pinned bytes.',
            resolves_to='a checker digest the row would have to publish; when it does, this '
                        'field becomes that digest and the replay becomes runnable'),
        anchored_digests_are_of_published_bytes='hash files as published, gzip bodies and '
                                                'canonical streams included, and read .gz '
                                                'fields after decompressing',
        self_test='--self-test builds synthetic rank-3 bodies in a temporary directory, '
                  'patches the anchored digests to the synthetic hashes -- streams included, '
                  'written as they are published -- and exercises every declared check, all '
                  'four refusal codes and the partial report, so the gate is proven to work '
                  'and to reject while the real bodies are absent',
    )

    # the bodies the gate waits for, counted off the exports rather than stated: the importer's
    # refusal report is per body, so the contract records the same unit
    out['today']['required_bodies'] = sum(len(export['bodies'])
                                         for export in out['required_exports'])

    out['acceptance_tests'] = [
        dict(id='A1', name='body hashes to the published digest',
             test='every exported body hashes to a digest the row or this package already '
                  'published, and the row\'s own audit sources are declared by digest',
             bound='%d audit source digests (layer.audit_source_sha256), max_denominator %s, '
                   'the assignment table digest %s'
                   % (len(certificate['layer']['audit_source_sha256']),
                      certificate['lift']['max_denominator'], table['bank_table_digest'][:16]),
             reject_control='any altered byte fails the hash; a matching hash is evidence of '
                            'identity, not correctness'),
        dict(id='A2', name='the assignment is a bijection with no padding',
             test='the exported map is a bijection from the %d items onto %d banks x %d blocks '
                  'x %d registers, every bank uses all %d registers, and the per-copy table '
                  'carries %d banks'
                  % (table['items'], table['banks'], instance['blocks_per_bank'], FAMILY,
                     WIDTH, instance['banks_per_copy']),
             bound='%d items, %d banks, %d blocks per bank, padding %d'
                   % (table['items'], table['banks'], instance['blocks_per_bank'],
                      table['padding_per_bank']),
             reject_control='an item placed twice, a block left without its item, or a bank '
                            'with an unused register -- the padding the old rungs 3 and 4 need '
                            'at ranks 16 and 20 would fail here, which is what makes "no '
                            'padding" a test rather than a remark'),
        dict(id='A3', name='no other bin of the ledger moves',
             test='the retained row differs from the row exactly by the rank-3 bin: the '
                  'children fall by the family\'s own count, the families from %d to %d, the '
                  'mass by exactly banks * width and the stock by exactly the bank count, and '
                  'the retained histogram reproduces its digest'
                  % (instance['ledger']['families_before'], instance['ledger']['families_after']),
             bound='children %d -> %d, mass %d -> %d (drop %d = %d banks x %d), stock %d -> %d '
                   '(drop %d), maxchild %d unchanged'
                   % (instance['ledger']['children_before'], instance['ledger']['children_after'],
                      instance['ledger']['mass_before'], instance['ledger']['mass_after'],
                      instance['ledger']['mass_before'] - instance['ledger']['mass_after'],
                      table['banks'], WIDTH, instance['ledger']['stock_before'],
                      instance['ledger']['stock_after'], instance['ledger']['stock_drop'],
                      instance['ledger']['maxchild_before']),
             reject_control='a single child of another bin moving, or a stock drop that is not '
                            'the bank count'),
        dict(id='A4', name='the retained row re-prices the top, bit-bound',
             test='the retained envelope reproduces the rung\'s coarse saving, the next '
                  '10^-18 grid point up is excluded by the interval moment, the budget is the '
                  'bit leaf (so the complex branch does not bind), the 47-constraint assembly '
                  'is green at that budget and rejects its own adjacent grid point, and the '
                  'kappa is the assembly rule\'s floor on the grid',
             bound='coarse %s = %.12e, leaf %s = %.12e, kappa %s = %.12e, binding %s, complex '
                   'ceiling %.12e, tightest of the 47 constraints %.6e (= budget * eta), '
                   'adjacent point rejected %s, gain over the published top (%s) %+.4f%%'
                   % (point['coarse'], float(point['coarse']), point['leaf'], float(point['leaf']),
                      point['kappa'], float(point['kappa']), point['binding'],
                      float(point['complex_ceiling']),
                      float(point['assembly']['minimum_constraint']),
                      point['adjacent_grid_rejected'], published_top, float(gain) * 100),
             reject_control='quoting the row\'s own coarse saving (%s) or the row\'s own kappa '
                            '(%s), or a point whose next 10^-18 step also assembles'
                            % (row_own['complex_saving'], row_own['kappa'])),
        dict(id='A5', name='the columns of the modified word',
             test='every source, target and dirty-register column over F2 and over the defining '
                  'integers, in both directions, with the target chronology nested, the source '
                  'controls at paid-parity frames and both mutation controls rejected',
             bound='%d source columns, %d target rows, %d dirty columns per direction, '
                   'packed_digit_bits %d, %d pairs, read_counts %s'
                   % (certificate['contract_checks']
                      ['checked_source_columns'],
                      certificate['contract_checks']['checked_target_rows'],
                      certificate['layer']['formal']['columns'][0]['dirty_columns'],
                      certificate['layer']['formal']['packed_digit_bits'],
                      certificate['layer']['pairs'],
                      certificate['contract_checks']['read_counts']),
             reject_control='counts quoted from the row instead of coming out of the exported '
                            'tables, or a control run that reports PASS'),
        dict(id='A6', name='the incidence colouring',
             test='the new bank incidences are coloured with a two-colouring and a conflicting '
                  'assignment is rejected, at the fraction-free chart inversion',
             bound='PR205 precedent: swaps %d, longest_swapped_path %d, physical_roles %d; '
                   'this rung\'s incidences %d'
                   % (733, 11, 17114, table['banks'] * WIDTH),
             reject_control='a conflicting assignment accepted'),
        dict(id='A7', name='the prime witnesses',
             test='distinct integer Gram/prime witnesses for every frame the new blocks use, '
                  'residual factors below the retained q bound',
             bound='the retained prime threshold (PR205: 17114 physical roles, all used frames '
                   'witnessed); this rung\'s charts %d'
                   % (table['banks'] * instance['blocks_per_bank']),
             reject_control='a repeated witness, or a factor above the bound'),
    ]

    out['obligations_restated'] = [
        dict(id='C1', quote=cite('obligations.json', ['obligations', 0, 'statement'],
                                 json.loads((HERE / 'obligations.json').read_text())
                                 ['obligations'][0]['statement']),
             at_this_rung='build the %d banks of width %d and the normalizer that sends each '
                          'of the %d items\' true residual projectors to its assigned block. '
                          'The combinatorial half is instanced here (G1\'s bijection target, '
                          'occurrences-rank3.json); the physical half is G2 and is open.'
                          % (table['banks'], WIDTH, table['items']),
             exports=['G1', 'G2', 'G3', 'G5'],
             status='OPEN_PHYSICAL_HALF_INSTANCED_COMBINATORIAL_HALF'),
        dict(id='C2', quote=cite('obligations.json', ['obligations', 1, 'statement'],
                                 json.loads((HERE / 'obligations.json').read_text())
                                 ['obligations'][1]['statement']),
             at_this_rung='re-run the formal columns on the word after the rank-3 family leaves: '
                          'the row already publishes the counts this must reproduce (%d source, '
                          '%d target, %d dirty per direction), and the exported tables are what '
                          'A5 reads them out of.'
                          % (certificate['contract_checks']
                             ['checked_source_columns'],
                             certificate['contract_checks']
                             ['checked_target_rows'],
                             certificate['layer']['formal']['columns'][0]['dirty_columns']),
             exports=['G3'], status='OPEN'),
        dict(id='C3', quote=cite('obligations.json', ['obligations', 2, 'statement'],
                                 json.loads((HERE / 'obligations.json').read_text())
                                 ['obligations'][2]['statement']),
             at_this_rung='charts, colouring and witnesses for the %d new blocks and their %d '
                          'incidences.  Rank 3 divides the width, so the blocks are uniform and '
                          'no padding frame is introduced -- a simpler chart set than the padded '
                          'schedule\'s.'
                          % (table['banks'] * instance['blocks_per_bank'], table['banks'] * WIDTH),
             exports=['G4'], status='OPEN'),
        dict(id='C4', quote=cite('obligations.json', ['obligations', 3, 'statement'],
                                 json.loads((HERE / 'obligations.json').read_text())
                                 ['obligations'][3]['statement']),
             at_this_rung='the envelope parity at this rung\'s numbers: retained three-copy '
                          'stock %d, deficit %d, mass %d, children %d, families %d, histogram '
                          'digest %s; the coarse saving is %s and the kappa is bit-bound at %s.'
                          % (retained['W'], retained['N'], retained['total_rank'],
                             sum(retained['child_multiplicities'].values()),
                             len(retained['child_multiplicities']),
                             instance['ledger']['retained_histogram_digest'][:16],
                             point['coarse'], point['kappa']),
             exports=['G6'], status='OPEN'),
        dict(id='C5', quote=cite('obligations.json', ['obligations', 4, 'statement'],
                                 json.loads((HERE / 'obligations.json').read_text())
                                 ['obligations'][4]['statement']),
             at_this_rung='the rank-3 family\'s provenance: %d children per vertex, %d items '
                          'onto %d banks x %d blocks, each with its frame or chain identity. '
                          'The addresses exist (occurrences-rank3.json); the identity does not, '
                          'and that is what G5 adds.' % (row['child_multiplicities'][FAMILY],
                                                         table['items'], table['banks'],
                                                         instance['blocks_per_bank']),
             exports=['G5'], status='INVENTORY_INSTANCED_AT_SCHEDULE_LEVEL'),
        dict(id='C6', quote=cite('obligations.json', ['obligations', 5, 'statement'],
                                 json.loads((HERE / 'obligations.json').read_text())
                                 ['obligations'][5]['statement']),
             at_this_rung='on the retained row the next whole-bank family is %s: %d banks by the '
                          'volume criterion at its capacity bound, and it does not divide the '
                          'width, so this one still owes the padded tiling T1 as well as its '
                          'provenance.  Outside this rung\'s scope by construction.'
                          % (', '.join('rank %d (%d banks)'
                                       % (entry['family'], entry['banks'])
                                       for entry in instance['remaining_whole_bank_families']),
                             sum(entry['banks']
                                 for entry in instance['remaining_whole_bank_families'])),
             exports=['G5'], status='OPEN_NOT_THIS_RUNG'),
        dict(id='C7', quote=cite('obligations.json', ['obligations', 6, 'statement'],
                                 json.loads((HERE / 'obligations.json').read_text())
                                 ['obligations'][6]['statement']),
             at_this_rung='the same, for the families beyond: the retained row\'s eligibility '
                          'is %s, and every one of them fails rank-divides-width, so the '
                          'padding of T1 stays owed after this rung.  Outside its scope.'
                          % instance['retained_eligibility'],
             exports=['G5'], status='OPEN_NOT_THIS_RUNG'),
    ]
    out['obligation_mapping'] = {row['id']: row['exports'] for row in out['obligations_restated']}
    out['inherited'] = json.loads((HERE / 'obligations.json').read_text())['inherited']

    out['still_owed'] = dict(
        C1_physical='the normalizer sending each item\'s residual projector to its block: the '
                    'addresses exist (G1\'s bijection target), the projectors the row exports '
                    'do not (machine_read above)',
        C2='formal columns of the modified complex word after the re-assignment',
        C3='charts, colouring and prime witnesses for the new blocks',
        C4='moment-envelope parity for the re-assigned word, at the numbers A4 binds',
        C5='per-child provenance for the rank-3 family: the item addresses exist, the '
           'frame/chain identity of each child does not',
        C6_C7='the retained row\'s further whole-bank families, which this rung deliberately '
              'does not touch -- and which still owe the padded tiling of T1, since none of '
              'them divides the bank width',
        importer='the gate is executable: importer66.py consumes this contract directly '
                 '(--contract export-contract-rank3.json), runs G1-G6\'s declared checks on '
                 'whatever bodies are present, and refuses by default while they are absent.  '
                 'What it cannot run is the replay: this row publishes no checker digest, so '
                 'the harness has none to accept (import_harness.replay_requirement).  A green '
                 'gate would therefore still not be an admissible import.)')

    out['verification'] = dict(
        what_verify_checks='verify.py -> check_rank3_export_contract: every citation above is '
                           'resolved against the pinned bytes (the vendored row certificate, '
                           'the pinned PR205 certificate, the pinned PR219 inventory, '
                           'occurrences-rank3.json and export-contract.json), and every derived '
                           'number is re-derived -- the assignment from the addressing rule, '
                           'the ledger from the row, the leaf through #219\'s vendored '
                           'arithmetic, and the point through the queue\'s assembly rule and '
                           'the unchanged 47-constraint assembly.',
        what_the_import_checks='the gate, executed rather than described: importer66.py '
                              'runs A1-A7 on the bodies and --self-test proves on synthetic '
                              'bodies that every declared check is decided and that a broken '
                              'one is rejected, with the four refusal codes and the partial '
                              'report.  A1 and A5 are decidable from the bodies\' declared '
                              'data and the row\'s published counts; A2 and A3 against '
                              'occurrences-rank3.json and the row\'s histogram; A4 against '
                              'the retained ledger; A6 and A7 against the pinned colouring '
                              'precedent.  What no import can decide is the replay: the row '
                              'publishes no checker digest, so the physics stays a stated '
                              'dependency of this rung rather than something the harness runs.',
        what_it_can_never_buy='no export can make the bound unconditional: C1-C7 and the '
                              'inherited R1-R4 are one missing artifact, and the asymptotic '
                              'interfaces stay assumptions (obligations.json -> '
                              'unconditionality)')

    out['not_required'] = [
        'internal id stability: only a canonical renumbering map and the bijection test A2',
        'program text beyond canonical data: G2 is nodes, kinds, edges and spans',
        'sources for the row\'s own claims: the importer re-runs the columns (A5) and re-charts '
        'the frames (A6), so a boolean in contract_checks is a claim to reproduce',
        'the padding the old rungs 3 and 4 need: rank 3 divides the width, so this rung\'s bank '
        'is exactly filled and A2 rejects a padding register rather than asking for one',
        'anything about the retained row\'s further families (C6, C7): they are the next rung\'s '
        'business and are named only so the contract does not look exhaustive',
        'any asymptotic interface: general Clifford/tensor, uniform weighted compilation, '
        'restored rows, routing, paid layout, prime supply, precision/recovery and fixed tape '
        'stay the stated assumptions they already are',
    ]

    out['failure_semantics'] = dict(
        today='0 of 6 bodies: the import fails closed, the rung stays a scheduled target and '
              'the kappa keeps its conditional flag.  The combinatorial half is the exception '
              'and it is on this package\'s side of the interface (occurrences-rank3.json).',
        order_of_discharge='A1 admits the anchored bodies and G2\'s normalizer becomes a '
                           're-assignment over published frames; A2 makes the assignment a '
                           'bijection with no padding; A3 closes the inventory and the '
                           'item-to-block half of C1; A5 re-runs C2; A4 closes C4 and R4; A6 '
                           'and A7 close C3.',
        never='no export can make the bound unconditional; see obligations.json -> '
              'unconditionality.  And no export can make this rung\'s row merged: the row is '
              'pinned by digest to an unmerged branch, and this contract is a target.')

    out['status'] = (
        'CONTRACT PUBLISHED, MACHINE-CHECKED AND IMPORTABLE at the rung: the gate of G1-G6 is '
        'executable (importer66.py --contract export-contract-rank3.json --self-test), and '
        'verify.py -> '
        'check_rank3_export_contract resolves every citation against the pinned bytes, '
        're-derives the assignment, the retained ledger and the point, and asserts the 0-of-6 '
        'reading.  It is a target, not a claim: the row\'s PR is not merged and the rung is '
        'not built.')
    return out


def main():
    sys.set_int_max_str_digits(0)
    sys.dont_write_bytecode = True
    out = build()
    target = HERE / 'export-contract-rank3.json'
    target.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + '\n',
                      newline='\n')
    rung = out['rung']
    print('rung    rank %d on %s (%s, %d bytes); %d items -> %d banks x %d blocks, padding %d'
          % (FAMILY, ROW_NAME.rsplit('/', 1)[-1], rung['row']['sha256'][:16],
             rung['row']['bytes'], rung['geometry']['volume_three_copies'] // FAMILY,
             rung['geometry']['banks'], rung['geometry']['blocks_per_bank'],
             rung['geometry']['padding_per_bank']))
    test = out['acceptance_tests'][3]['bound']
    print('point   ' + test)
    print('exports %s; tests %s; obligations %s'
          % (','.join(export['id'] for export in out['required_exports']),
             ','.join(t['id'] for t in out['acceptance_tests']),
             ','.join(row['id'] for row in out['obligations_restated'])))
    print('bodies  %d of %d required bodies exported by the row across %d exports; the gate '
          'is executable (importer66.py --contract export-contract-rank3.json --self-test)'
          % (out['today']['bodies_present'], out['today']['required_bodies'],
             out['today']['of_required']))
    print('write ' + str(target))


if __name__ == '__main__':
    main()
