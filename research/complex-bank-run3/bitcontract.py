#!/usr/bin/env python3
"""Authoring script: writes export-contract-bit.json, the bit-side twin contract.

Every citation is pulled out of the pinned bytes here, so the contract cannot quote a digest, a
count or a status that is not there.  verify.py -> check_bit_export_contract then re-resolves all of
them from the written file, and asserts against the drop in `exports-bit/`.
"""
import json
import sys
from pathlib import Path

sys.set_int_max_str_digits(0)
ROOT = Path(__file__).resolve().parent

ACC = 'references/pr219-run1/certificate.json'
OCC = 'references/pr219-run1/inputs/absorbed-occurrences.json'
OBL = 'references/pr219-run1/obligations.json'
BIT = 'references/pr219-run1/references/pr200-bit.certificate.json'
PACK = 'references/pr219-run1/references/pr205-packed.certificate.json'

DOC = {name: json.loads((ROOT / name).read_text()) for name in (ACC, OCC, OBL, BIT, PACK)}


def g(source, *keys):
    node = DOC[source]
    for key in keys:
        node = node[key]
    return node


def citation(source, keys, reading):
    return {'source': source, 'keys': list(keys), 'value': g(source, *keys), 'reading': reading}


contract = {}
contract['contract'] = ('bit-side twin of the normalizer export contract: what the bit supplier\'s '
                        'program must publish for the rank-22 realization obligations R1-R4 to close')
contract['version'] = 2
contract['source'] = ('research/complex-bank-run3/EXPORT-CONTRACT-BIT.md (the prose twin this file '
                      'makes checkable)')
contract['scope'] = (
    'The four physical realization obligations of the pinned rank-22 package (R1-R4, '
    'references/pr219-run1/obligations.json) reduce to one missing layer: the word\'s physical bodies, '
    'republished and re-run on the *banked* word. This file names the required exports, their '
    'verifiable form, the digest or count each body must reproduce, and the acceptance tests. It is '
    'the twin of export-contract.json, the complex side\'s contract, and reuses its shape exactly: the '
    'same schema, the same seven acceptance tests A1-A7, the same gate/replay split, and a pinned '
    'checker that gates the replay. verify.py -> check_bit_export_contract resolves every citation '
    'below against the pinned bytes, asserts the state of the drop, and importer66.py consumes it like '
    'any other contract.')

contract['precedent'] = {}

contract['precedent']['word_physical_layer_shape'] = {
    'reading': 'The bit word\'s physical layer is *built and pinned before* the rank-22 absorption: '
               'charts, incidence and colouring with their bounds and a PASS status. That is the shape '
               'R1-R4 must reach again on the absorbed word, and the precedent R1 extends -- which is '
               'why this twin is half-met where the complex side is empty.',
    'citations': [
        citation(PACK, ['physical', 'status'], 'the supplier\'s own verdict on the built physical layer'),
        citation(PACK, ['physical', 'm'], 'the banked width'),
        citation(PACK, ['physical', 'banks'], 'the banked row\'s banks'),
        citation(PACK, ['physical', 'gauge_roles'], 'the absorbed gauge family\'s roles'),
        citation(PACK, ['physical', 'distinct_gauges'], 'and the frames they sit on, which A2 holds'),
        citation(PACK, ['physical', 'incidences'], 'the built incidence count'),
        citation(PACK, ['physical', 'physical_roles'], 'the physical roles A7 must witness'),
        citation(PACK, ['physical', 'color_stats'], 'the colouring\'s exact statistics'),
        citation(PACK, ['physical', 'conflicting_assignment_rejected'],
                  'the colouring reject control, claimed true'),
        citation(PACK, ['physical', 'max_den'], 'the chart denominator bound A3 holds the export to'),
        citation(PACK, ['physical', 'max_num'], 'the chart numerator bound A3 holds the export to'),
        citation(PACK, ['physical', 'max_chart_factors'], 'the factor count per frame'),
        citation(PACK, ['physical', 'patterns'], 'the block patterns of the banked row'),
        citation(PACK, ['physical', 'word_sha256'], 'the banked word'),
        citation(PACK, ['physical', 'chart_sha256'],
                  'the chart stream\'s digest: now reproduced in the drop, not just cited'),
        citation(PACK, ['physical', 'incidence_sha256'], 'and the incidence stream\'s'),
        citation(PACK, ['pinned_bit_files'], 'the word files the packed row pinned and did not publish')]}

contract['precedent']['terminal_word_formal_layer'] = {
    'reading': 'The formal columns and the prime witnesses are built and pinned on the *terminal* '
               'word: R2 and R3 are the same checks re-run on the absorbed word, not new mathematics. '
               'The formal layer publishes its F2 identity and its defining-integer decoder as '
               'booleans, which is exactly what A4 refuses to take on trust.',
    'citations': [
        citation(BIT, ['bit', 'terminal', 'status'], 'the terminal word\'s formal/geometry verdict'),
        citation(BIT, ['bit', 'formal'], 'the two formal rows: F2 identity, integer defining decoder'),
        citation(BIT, ['bit', 'terminal', 'formal'], 'the terminal replay per direction and mode'),
        citation(BIT, ['bit', 'terminal', 'integer_residual_bound'], 'the defining-integer residual bound'),
        citation(BIT, ['bit', 'terminal', 'packed_digit_bits'], 'the packed digit width'),
        citation(BIT, ['bit', 'terminal', 'new_frames_added'],
                  'the terminal word adds no frame: R1 may not add one either without re-pricing'),
        citation(BIT, ['bit', 'profile', 'child_histogram', '22'], 'the rank-22 bin before absorption'),
        citation(BIT, ['bit', 'profile', 'R'], 'the word\'s physical roles'),
        citation(BIT, ['bit', 'profile', 'W_per_vertex'], 'the word\'s stock'),
        citation(BIT, ['bit', 'profile', 'changed_operation_frames'], 'the frames a re-run must cover'),
        citation(BIT, ['bit', 'profile', 'selected_roles'], 'the selected gauge family'),
        citation(BIT, ['bit', 'prime_witnesses', 'status'], 'the witness layer\'s verdict'),
        citation(BIT, ['bit', 'prime_witnesses', 'total_used_frames'], 'the frames witnessed'),
        citation(BIT, ['bit', 'prime_witnesses', 'unique_used_bases'], 'distinct bases'),
        citation(BIT, ['bit', 'prime_witnesses', 'maximum_determinant_bits'], 'the determinant scale'),
        citation(BIT, ['bit', 'prime_witnesses', 'witness_sha256'],
                  'the witness body\'s digest: now reproduced in the drop'),
        citation(BIT, ['bit', 'prime_witnesses', 'witness_file'],
                  'the witness body\'s upstream path, and the reason an index is needed beside it'),
        citation(BIT, ['bit', 'prime_witnesses', 'script_sha256'], 'the supplier\'s witness script'),
        citation(BIT, ['bit', 'prime_witnesses', 'rule'], 'the rule A7\'s bound is held to')]}

contract['precedent']['the_family_is_enumerated'] = {
    'reading': 'The absorbed family is enumerated, its provenance is pinned and it is the *same word* '
               'the packed row banked: the inventory\'s word digest is PR205\'s physical.word_sha256. '
               'So the twin asks for bodies behind digests of a word this repository already '
               'half-holds -- the schedule, the retained ledger and the whole-bank condition are '
               'published accounting, not the physical layer.',
    'citations': [
        citation(OCC, ['status'], 'what the enumeration is'),
        citation(OCC, ['counts_per_vertex'], 'the family\'s counts B2 must reproduce exactly'),
        citation(OCC, ['row_identity_per_vertex'], 'the row the enumeration was taken in'),
        citation(OCC, ['source_pins'], 'the word, the base checker and the certificate, by digest'),
        citation(ACC, ['status'], 'the accounting package\'s own verdict and its declared conditionality'),
        citation(ACC, ['schedule', 'status'], 'the literal statement that no physical layer is built'),
        citation(ACC, ['obligations'], 'the four obligations this contract answers'),
        citation(ACC, ['schedule', 'banks'], 'the whole-bank condition and the bank count it implies'),
        citation(ACC, ['schedule', 'row_identity'], 'the retained row identity'),
        citation(ACC, ['schedule', 'block_tilings', 'feasible_patterns'],
                  'the admissible tilings R1 must select from'),
        citation(ACC, ['kappa'], 'the conditional kappa R4\'s parity test protects')],
    'cross_reading': 'the inventory\'s source_pins.word_p12_sha256 equals the packed row\'s '
                     'physical.word_sha256: the enumerated family and the banked row are the same word, '
                     'so the contract asks for bodies behind existing digests rather than for new trust'}

contract['precedent']['what_the_obligations_say'] = {
    'reading': 'the four obligations, quoted from the pinned statement rather than paraphrased; every '
               'export below is mapped to one or more of them, so the twin cannot answer an obligation '
               'the package did not state',
    'citations': [
        citation(OBL, ['obligations', 0, 'statement'], 'R1: the residual type, the bank blocks, the assignment'),
        citation(OBL, ['obligations', 1, 'statement'], 'R2: the formal columns of the modified word'),
        citation(OBL, ['obligations', 2, 'statement'], 'R3: charts, colouring and prime witnesses'),
        citation(OBL, ['obligations', 3, 'statement'], 'R4: the moment envelope and the recomputation rule')]}

contract['today'] = {
    'bodies_present': 0,
    'of_required': 6,
    'about': 'the pinned *certificates*: what the supplier published as bytes rather than as hashes',
    'verdict': 'fail closed: not one required export is published as a body by the pins. The physical '
               'layer the pins hold belongs to the *unabsorbed* word (PR200\'s formal columns and '
               'witnesses, PR205\'s charts, incidence and colouring) and is published as digests and '
               'statuses; the pinned rank-22 package certifies the accounting and says so in its own '
               'schedule.status. See `drop` for what has since been assembled and reproduced outside '
               'the pins.',
    'published_only_as': ['digest', 'count', 'status', 'enumeration', 'path'],
    'evidence': [
        citation(ACC, ['status'], 'the package\'s own verdict: R1-R4 OPEN, kappa conditional'),
        citation(ACC, ['schedule', 'status'], 'no physical column, chart or prime witness is built there'),
        citation(ACC, ['obligations'], 'the four obligations, still OPEN'),
        citation(BIT, ['bit', 'prime_witnesses', 'input_sha256'],
                  'the five word bodies exist as digests in the supplier\'s workspace, not in the pins'),
        citation(BIT, ['bit', 'prime_witnesses', 'witness_file'], 'the witness body\'s path, not its bytes'),
        citation(PACK, ['physical', 'chart_sha256'], 'the chart stream: digest only, in the pins'),
        citation(PACK, ['physical', 'incidence_sha256'], 'the incidence stream: digest only, in the pins'),
        citation(PACK, ['physical', 'word_sha256'], 'the word body: digest only'),
        citation(BIT, ['bit', 'prime_witnesses', 'witness_sha256'], 'the witness body: digest only'),
        citation(OCC, ['source_pins', 'checker_sha256'], 'the checker this contract pins: digest only')]}

contract['drop'] = {
    'about': 'the import directory this package now ships, and what a partial run of the gate makes '
             'of it: the two export groups whose bytes the supplier published as digests, reproduced '
             'and anchored, and the declarations they do not carry themselves',
    'dir': 'exports-bit',
    'bodies': 10,
    'anchored': 8,
    'exports_complete': ['B1', 'B3'],
    'exports_absent': ['B2', 'B4', 'B5', 'B6'],
    'streams': ['charts.json', 'incidence.json'],
    'reproduced': 'the five word bodies and the witness body are the supplier\'s own bytes, each '
                  'hashing to the digest its certificate published. The chart and incidence streams do '
                  'not exist upstream as files: PR205 published digests of canonical streams. Running '
                  'PR205\'s packer unmodified on the word bodies in this drop re-derives both streams '
                  'byte for byte, and the packer\'s recomputed physical block differs from PR205\'s '
                  'published block in no field (exports-bit/physical.rebuilt.json)',
    'declarations': 'what the bodies do not declare is declared by two index bodies, derived by '
                    'bitindex.py from the bodies and the pinned certificates rather than typed in: '
                    'index.json.gz (B1: the sibling digests, the terminal geometry, the selected gauge '
                    'family and its 220 distinct frames) and charts.index.json.gz (B3: the colouring '
                    'and chart statistics, the banked row and the 24,401-entry witness table A7 is '
                    'held to). Neither is anchored: an index is a declaration, and the bodies it '
                    'describes are what carry the digests',
    'verdict': 'the gate decides A2 and A3 on the real bytes and the declarations derived from them: '
               'A2 on the six index counts, the frame-record bijection and the foreign-replay bound, '
               'A3 on the chart and witness bounds. A1 passes its eight digest anchors and nine index '
               'checks and still lacks a manifest; A6 and A7 pass seventeen chart/index checks each '
               'and still lack B5\'s controls; A4 lacks B4 and A5 lacks B2. So the drop is reportable '
               'in part and never admissible: the default import refuses it (code 2), the partial run '
               'reports it (code 4) and nothing is discharged. R1-R4 stay OPEN',
    'gate': {
        'command': 'python3 -B importer66.py --contract export-contract-bit.json --exports '
                   'exports-bit --partial',
        'exit_code': 4,
        'default_exit_code': 2,
        'by_test': {
            'A1': '17 checks pass, 0 fail; not runnable while integrity.json is absent',
            'A2': 'PASS, 9 checks',
            'A3': 'PASS, 17 checks',
            'A4': 'no check yet: B4 is absent',
            'A5': 'no check yet: B2 is absent',
            'A6': '17 checks pass, 0 fail; not runnable while controls.json is absent',
            'A7': '17 checks pass, 0 fail; not runnable while controls.json is absent'},
        'report': 'bit-drop-report.json',
        'report_reading': 'the same partial run, as JSON, and verify.py re-runs it and compares',
        'note': 'two of the seven acceptance tests are decided on published bytes; the other five '
                'wait for bodies this drop does not hold'},
    'evidence': [
        citation(PACK, ['physical', 'chart_sha256'], 'the chart stream the drop reproduces'),
        citation(PACK, ['physical', 'incidence_sha256'], 'the incidence stream the drop reproduces'),
        citation(PACK, ['physical', 'distinct_gauges'], 'the 220 distinct gauge frames A2 holds'),
        citation(BIT, ['bit', 'prime_witnesses', 'input_sha256'], 'the five word digests the drop reproduces'),
        citation(BIT, ['bit', 'prime_witnesses', 'witness_sha256'], 'the witness digest the drop reproduces'),
        citation(OCC, ['source_pins', 'checker_sha256'], 'the checker the drop pins')]}

contract['required_exports'] = []

contract['required_exports'].append({
    'id': 'B1',
    'name': 'the word, its frames and the selected gauge family',
    'publishes': 'the five bodies behind the terminal word\'s input digests -- word.json.gz (the '
                 'packed word), frames.json.gz (integer kernel basis per frame), graph.json (parents, '
                 'children and edges), kchron.json (the chronology) and profile.json (the histogram '
                 'and ledger row) -- verbatim and anchored, together with index.json.gz, which '
                 'declares their digests, the terminal column geometry, the selected gauge family and '
                 'the bijection between its 220 distinct frames and their records in the frame table',
    'form': 'five JSON/gz bodies as published, plus one JSON/gz index (integers and digests only)',
    'cardinality': {'formal_columns': g(BIT, 'bit', 'terminal', 'formal', 0, 'formal_columns'),
                    'dirty_columns': g(BIT, 'bit', 'terminal', 'formal', 0, 'dirty_columns'),
                    'changed_operation_frames': g(BIT, 'bit', 'profile', 'changed_operation_frames'),
                    'used_frames': g(BIT, 'bit', 'prime_witnesses', 'total_used_frames'),
                    'selected_roles': g(BIT, 'bit', 'profile', 'selected_roles'),
                    'gauge_frames': g(PACK, 'physical', 'distinct_gauges')},
    'must_reproduce': [
        citation(BIT, ['bit', 'prime_witnesses', 'input_sha256'],
                  'all five word digests must come out of the published bodies'),
        citation(BIT, ['bit', 'prime_witnesses', 'total_used_frames'], 'the witness table the index counts'),
        citation(BIT, ['bit', 'profile', 'selected_roles'], 'the selected family the index derives'),
        citation(PACK, ['physical', 'distinct_gauges'], 'and the frames it sits on, bijectively'),
        citation(PACK, ['physical', 'word_sha256'], 'the word digest PR205 banked, unchanged')],
    'bodies': [
        {'file': 'index.json.gz', 'anchored_digest': None},
        {'file': 'word.json.gz', 'stream': False,
         'anchored_digest': g(BIT, 'bit', 'prime_witnesses', 'input_sha256',
                              'research/paired-cube-diagonal-bit-168/selected/bit/word_p12.json.gz')},
        {'file': 'frames.json.gz', 'stream': False,
         'anchored_digest': g(BIT, 'bit', 'prime_witnesses', 'input_sha256',
                              'research/paired-cube-diagonal-bit-168/selected/bit/frames_p12.json.gz')},
        {'file': 'graph.json', 'stream': False,
         'anchored_digest': g(BIT, 'bit', 'prime_witnesses', 'input_sha256',
                              'research/paired-cube-diagonal-bit-168/selected/bit/graph_p12.json')},
        {'file': 'kchron.json', 'stream': False,
         'anchored_digest': g(BIT, 'bit', 'prime_witnesses', 'input_sha256',
                              'research/paired-cube-diagonal-bit-168/selected/bit/kchron_p12.json')},
        {'file': 'profile.json', 'stream': False,
         'anchored_digest': g(BIT, 'bit', 'prime_witnesses', 'input_sha256',
                              'research/paired-cube-diagonal-bit-168/selected/bit/profile_p12.json')}],
    'gate': {'test': ['A1', 'A2'],
             'equals': {'formal_columns': g(BIT, 'bit', 'terminal', 'formal', 0, 'formal_columns'),
                        'dirty_columns': g(BIT, 'bit', 'terminal', 'formal', 0, 'dirty_columns'),
                        'changed_operation_frames': g(BIT, 'bit', 'profile',
                                                      'changed_operation_frames'),
                        'used_frames': g(BIT, 'bit', 'prime_witnesses', 'total_used_frames'),
                        'selected_roles': g(BIT, 'bit', 'profile', 'selected_roles'),
                        'gauge_frames': g(PACK, 'physical', 'distinct_gauges')},
             'bijection': ['gauge_frame_map'],
             'flags_present': ['input_sha256'],
             'at_most': {'foreign_producer_replays': g(BIT, 'bit', 'foreign_producer_replays')}},
    'acceptance': ['A1', 'A2'],
    'unblocks': ['R2', 'R3']})

contract['required_exports'].append({
    'id': 'B2',
    'name': 'the bank blocks and the per-occurrence assignment',
    'publishes': 'the rank-22 residual item (one per enumerated occurrence of the pinned inventory), '
                 'its coordinate-block shape in a bank of width 72, the selected tiling of that width, '
                 'and the per-occurrence assignment (item -> bank, offset) with the normalizer sending '
                 'each item\'s true residual projector to its assigned block',
    'form': 'JSON: the selected pattern, the bank table (banks x 72 offsets) and the item assignment, '
            'integers only, with the assignment hashed',
    'cardinality': {'items': g(ACC, 'schedule', 'absorbed_family', 'occurrences_three_copies'),
                    'banks': g(ACC, 'schedule', 'banks', 'banks_from_volume'),
                    'width': g(ACC, 'schedule', 'banks', 'width'),
                    'registers': g(ACC, 'schedule', 'absorbed_family', 'dirt_volume_registers'),
                    'occurrences_per_vertex': g(ACC, 'schedule', 'absorbed_family',
                                                'ledger_bin_per_vertex'),
                    'normalization_factor': g(ACC, 'schedule', 'absorbed_family',
                                              'normalization_factor')},
    'must_reproduce': [
        citation(ACC, ['schedule', 'banks'], 'the whole-bank condition and the bank count'),
        citation(ACC, ['schedule', 'absorbed_family'], 'the family\'s exact inventory, with provenance'),
        citation(ACC, ['schedule', 'block_tilings', 'feasible_patterns'], 'the admissible tilings'),
        citation(OCC, ['counts_per_vertex'], 'the pinned enumeration\'s counts'),
        citation(OCC, ['row_identity_per_vertex'], 'the row the occurrences were enumerated in')],
    'bodies': [{'file': 'assignment.json', 'stream': False, 'anchored_digest': None}],
    'gate': {'test': ['A5'],
             'equals': {'items': g(ACC, 'schedule', 'absorbed_family', 'occurrences_three_copies'),
                        'banks': g(ACC, 'schedule', 'banks', 'banks_from_volume'),
                        'width': g(ACC, 'schedule', 'banks', 'width'),
                        'registers': g(ACC, 'schedule', 'absorbed_family', 'dirt_volume_registers'),
                        'occurrences_per_vertex': g(ACC, 'schedule', 'absorbed_family',
                                                    'ledger_bin_per_vertex')},
             'bijection': ['assignment'],
             'equals_in': [
                 {'body_key': 'counts_per_vertex', 'source': OCC, 'keys': ['counts_per_vertex'],
                  'why': 'the export must name exactly the counts the pinned inventory names: this is '
                         'what makes A5 a bijection against the enumeration rather than a restatement'},
                 {'body_key': 'bank_table', 'source': ACC, 'keys': ['schedule', 'banks'],
                  'why': 'the export\'s bank table must be the one the schedule\'s whole-bank '
                         'condition implies, not a restatement of it'},
                 {'body_key': 'row_identity', 'source': ACC, 'keys': ['schedule', 'row_identity'],
                  'why': 'and the absorbed row must be the row R4 prices'}]},
    'acceptance': ['A5'],
    'unblocks': ['R1', 'R4']})

contract['required_exports'].append({
    'id': 'B3',
    'name': 'charts, incidence colouring and prime witnesses',
    'publishes': 'the chart stream (integer kernel bases with fraction-free inverses and the replayed '
                 'elementary factors, frame by frame), the incidence stream (one coloured incidence '
                 'per line), and the witness table, each verbatim and anchored, plus '
                 'charts.index.json.gz, which declares the colouring and chart statistics the streams '
                 'carry but do not name, the banked row, and the witness table A7 is held to',
    'form': 'two canonical byte streams (hashed as published, not parsed) and the witness JSON/gz, '
            'plus one JSON/gz index',
    'cardinality': {'used_frames': g(BIT, 'bit', 'prime_witnesses', 'total_used_frames'),
                    'physical_roles': g(BIT, 'bit', 'profile', 'R'),
                    'gauge_roles': g(PACK, 'physical', 'gauge_roles'),
                    'distinct_gauges': g(PACK, 'physical', 'distinct_gauges'),
                    'incidences': g(PACK, 'physical', 'incidences'),
                    'banks': g(PACK, 'physical', 'banks'),
                    'max_chart_factors': g(PACK, 'physical', 'max_chart_factors'),
                    'swaps': g(PACK, 'physical', 'color_stats', 'swaps'),
                    'longest_swapped_path': g(PACK, 'physical', 'color_stats',
                                              'longest_swapped_path')},
    'must_reproduce': [
        citation(PACK, ['physical', 'chart_sha256'], 'the chart stream\'s digest'),
        citation(PACK, ['physical', 'incidence_sha256'], 'the incidence stream\'s digest'),
        citation(PACK, ['physical', 'max_den'], 'the denominator bound the re-run must not exceed'),
        citation(PACK, ['physical', 'max_num'], 'the numerator bound'),
        citation(PACK, ['physical', 'color_stats'], 'the colouring\'s exact statistics'),
        citation(PACK, ['physical', 'conflicting_assignment_rejected'], 'and its reject control'),
        citation(PACK, ['physical', 'incidences'], 'the incidence count'),
        citation(BIT, ['bit', 'prime_witnesses', 'witness_sha256'], 'the witness body behind its digest'),
        citation(BIT, ['bit', 'prime_witnesses', 'total_used_frames'], 'the frames witnessed'),
        citation(BIT, ['bit', 'prime_witnesses', 'unique_used_bases'], 'distinct bases'),
        citation(BIT, ['bit', 'prime_witnesses',
                       'all_remaining_factors_below_retained_prime_lower_bound'],
                  'every remaining factor below the retained prime bound'),
        citation(BIT, ['bit', 'prime_witnesses', 'rule'], 'the rule A7\'s bound rests on')],
    'bodies': [
        {'file': 'charts.index.json.gz', 'stream': False, 'anchored_digest': None},
        {'file': 'charts.json', 'stream': True,
         'anchored_digest': g(PACK, 'physical', 'chart_sha256')},
        {'file': 'incidence.json', 'stream': True,
         'anchored_digest': g(PACK, 'physical', 'incidence_sha256')},
        {'file': 'prime-witnesses.json.gz', 'stream': False,
         'anchored_digest': g(BIT, 'bit', 'prime_witnesses', 'witness_sha256')}],
    'gate': {'test': ['A3', 'A6', 'A7'],
             'equals': {'used_frames': g(BIT, 'bit', 'prime_witnesses', 'total_used_frames'),
                        'physical_roles': g(BIT, 'bit', 'profile', 'R'),
                        'gauge_roles': g(PACK, 'physical', 'gauge_roles'),
                        'distinct_gauges': g(PACK, 'physical', 'distinct_gauges'),
                        'incidences': g(PACK, 'physical', 'incidences'),
                        'banks': g(PACK, 'physical', 'banks'),
                        'W': g(PACK, 'physical', 'W'),
                        'rank_mass': g(PACK, 'physical', 'rank_mass'),
                        'deficit': g(PACK, 'physical', 'deficit'),
                        'swaps': g(PACK, 'physical', 'color_stats', 'swaps'),
                        'longest_swapped_path': g(PACK, 'physical', 'color_stats',
                                                  'longest_swapped_path'),
                        'max_chart_factors': g(PACK, 'physical', 'max_chart_factors')},
             'at_most': {'max_denominator': g(PACK, 'physical', 'max_den'),
                         'max_abs_numerator': g(PACK, 'physical', 'max_num')},
             'flags_true': ['conflicting_assignment_rejected'],
             'flags_present': ['color_stats'],
             'distinct_below': {'witnesses': 'prime_witnesses', 'bound': 'q_bound'}},
    'acceptance': ['A1', 'A3', 'A6', 'A7'],
    'unblocks': ['R1', 'R3']})

contract['required_exports'].append({
    'id': 'B4',
    'name': 'columns of the banked word',
    'publishes': 'per direction and per ring the formal column tables of the *banked* word: every '
                 'source, target and dirty-register column over F2 and over the defining integers, '
                 'with the rank-22 transitions realized by bank re-assignment rather than by paid '
                 'children, the residual bound and the packed digits as in the terminal replay',
    'form': 'JSON tables of integer addresses, one row per column',
    'cardinality': {'formal_columns': g(BIT, 'bit', 'terminal', 'formal', 0, 'formal_columns'),
                    'dirty_columns': g(BIT, 'bit', 'terminal', 'formal', 0, 'dirty_columns'),
                    'source_columns': g(BIT, 'bit', 'terminal', 'formal', 0, 'source_columns'),
                    'target_columns': g(BIT, 'bit', 'terminal', 'formal', 0, 'target_columns'),
                    'integer_residual_bound': g(BIT, 'bit', 'terminal', 'integer_residual_bound'),
                    'packed_digit_bits': g(BIT, 'bit', 'terminal', 'packed_digit_bits')},
    'must_reproduce': [
        citation(BIT, ['bit', 'terminal', 'formal'], 'the terminal replay\'s own column geometry'),
        citation(BIT, ['bit', 'terminal', 'integer_residual_bound'], 'the defining-integer residual bound'),
        citation(BIT, ['bit', 'terminal', 'packed_digit_bits'], 'the packed digit width'),
        citation(BIT, ['bit', 'formal'], 'the F2 identity and the defining-integer decoder, as claims'),
        citation(BIT, ['bit', 'terminal', 'status'], 'the verdict the re-run must reach again'),
        citation(OBL, ['obligations', 1, 'statement'], 'R2, word for word')],
    'bodies': [{'file': 'columns.json', 'stream': False, 'anchored_digest': None}],
    'gate': {'test': ['A4'],
             'equals': {'formal_columns': g(BIT, 'bit', 'terminal', 'formal', 0, 'formal_columns'),
                        'dirty_columns': g(BIT, 'bit', 'terminal', 'formal', 0, 'dirty_columns'),
                        'source_columns': g(BIT, 'bit', 'terminal', 'formal', 0, 'source_columns'),
                        'target_columns': g(BIT, 'bit', 'terminal', 'formal', 0, 'target_columns'),
                        'checked_source_columns': g(BIT, 'bit', 'terminal', 'formal', 0,
                                                    'source_columns'),
                        'checked_target_rows': g(BIT, 'bit', 'terminal', 'formal', 0,
                                                 'target_columns'),
                        'checked_dirty_columns': g(BIT, 'bit', 'terminal', 'formal', 0,
                                                   'dirty_columns'),
                        'integer_residual_bound': g(BIT, 'bit', 'terminal', 'integer_residual_bound'),
                        'packed_digit_bits': g(BIT, 'bit', 'terminal', 'packed_digit_bits')},
             'counted_in_tables': {'source_columns': 'checked_source_columns',
                                   'target_rows': 'checked_target_rows',
                                   'dirty_columns': 'checked_dirty_columns'}},
    'acceptance': ['A4'],
    'unblocks': ['R2']})

contract['required_exports'].append({
    'id': 'B5',
    'name': 'the reject controls',
    'publishes': 'the negative controls the word\'s own certificates ran, re-run on the banked word '
                 'and published with the rejected object: the 4 word controls, the 3 terminal '
                 'controls, the 21 adverse coarse controls, the 2 rejected adjacent grids and the 6 '
                 'rejected bank partitions with their 12 weighted partition cases',
    'form': 'JSON: per control the mutated object, the predicate it violates and the observed rejection',
    'cardinality': {'adverse_controls': g(BIT, 'arithmetic', 'adverse_control_count'),
                    'word_controls': len(g(BIT, 'bit', 'word_controls')),
                    'terminal_controls': len(g(BIT, 'bit', 'terminal', 'controls')),
                    'rejected_partitions': len(g(PACK, 'bank_controls', 'rejected')),
                    'weighted_partition_cases': g(PACK, 'bank_controls', 'weighted_partition_cases'),
                    'formal_columns_per_case': g(PACK, 'bank_controls',
                                                 'formal_columns_per_case')},
    'must_reproduce': [
        citation(BIT, ['arithmetic', 'adverse_control_count'], 'the adverse controls the coarse run counted'),
        citation(BIT, ['bit', 'word_controls'], 'the word\'s four controls'),
        citation(BIT, ['bit', 'terminal', 'controls'], 'the terminal controls and their verdicts'),
        citation(BIT, ['bit', 'coarse', 'controls'], 'the two rejected adjacent grids'),
        citation(BIT, ['bit', 'coarse', 'scope'], 'what the rejection does and does not claim'),
        citation(PACK, ['bank_controls'], 'the rejected bank partitions and the cases run'),
        citation(OBL, ['obligations', 2, 'statement'], 'R3\'s reject-control half, word for word')],
    'bodies': [{'file': 'controls.json', 'stream': False, 'anchored_digest': None}],
    'gate': {'test': ['A6', 'A7'],
             'equals': {'adverse_controls': g(BIT, 'arithmetic', 'adverse_control_count'),
                        'word_controls': len(g(BIT, 'bit', 'word_controls')),
                        'terminal_controls': len(g(BIT, 'bit', 'terminal', 'controls')),
                        'rejected_partitions': len(g(PACK, 'bank_controls', 'rejected')),
                        'weighted_partition_cases': g(PACK, 'bank_controls',
                                                      'weighted_partition_cases'),
                        'formal_columns_per_case': g(PACK, 'bank_controls',
                                                     'formal_columns_per_case')},
             'flags_true': ['next_coarse_grid_rejected', 'previous_atom_grid_rejected'],
             'flags_present': ['rejected', 'controls']},
    'acceptance': ['A6', 'A7'],
    'unblocks': ['R2', 'R3']})

contract['required_exports'].append({
    'id': 'B6',
    'name': 'envelope and integrity',
    'publishes': 'the paid moment envelope of the banked word in the form arithmetic.py consumes '
                 '(retained stock, deficit, retained histogram, worst-case bad fraction 1e-16 and the '
                 'fallback 32*72^2 per retained child), the completion-child ledger R1 may have '
                 'extended with the recomputed kappa if it did, and the manifest listing every digest '
                 'of B1-B5, the streams included, and the acceptance predicates actually run',
    'form': 'JSON envelope plus manifest',
    'cardinality': {'W_after': g(ACC, 'schedule', 'retained_profile', 'W_after'),
                    'deficit': g(ACC, 'schedule', 'retained_profile', 'deficit'),
                    'rank_mass_after': g(ACC, 'schedule', 'retained_profile', 'rank_mass_after'),
                    'retained_children': g(ACC, 'schedule', 'retained_profile', 'children_after'),
                    'maxchild': g(ACC, 'schedule', 'retained_profile', 'maxchild'),
                    'banks': g(ACC, 'schedule', 'banks', 'banks_from_volume'),
                    'registers': g(ACC, 'schedule', 'absorbed_family', 'dirt_volume_registers'),
                    'bad_fraction_inverse': 10 ** 16,
                    'fallback_registers_per_child': 32 * 72 ** 2},
    'must_reproduce': [
        citation(ACC, ['schedule', 'retained_profile', 'W_after'], 'the absorbed stock'),
        citation(ACC, ['schedule', 'retained_profile', 'deficit'], 'the unchanged deficit'),
        citation(ACC, ['schedule', 'retained_profile', 'rank_mass_after'], 'the retained rank mass'),
        citation(ACC, ['schedule', 'retained_profile', 'children_after'], 'the retained children'),
        citation(ACC, ['schedule', 'retained_profile', 'maxchild'], 'the largest retained child'),
        citation(ACC, ['schedule', 'retained_profile', 'histogram'], 'the histogram arithmetic.py prices'),
        citation(ACC, ['schedule', 'row_identity'], 'the row identity the envelope must satisfy'),
        citation(ACC, ['kappa'], 'the conditional kappa R4\'s parity test protects'),
        citation(ACC, ['schedule', 'absorbed_family'], 'the family the envelope drops'),
        citation(OBL, ['obligations', 3, 'statement'], 'R4, word for word, including the recomputation rule')],
    'bodies': [{'file': 'envelope.json', 'stream': False, 'anchored_digest': None},
               {'file': 'integrity.json', 'stream': False, 'anchored_digest': None}],
    'gate': {'test': ['A1'],
             'equals': {'W_after': g(ACC, 'schedule', 'retained_profile', 'W_after'),
                        'deficit': g(ACC, 'schedule', 'retained_profile', 'deficit'),
                        'rank_mass_after': g(ACC, 'schedule', 'retained_profile', 'rank_mass_after'),
                        'retained_children': g(ACC, 'schedule', 'retained_profile', 'children_after'),
                        'maxchild': g(ACC, 'schedule', 'retained_profile', 'maxchild'),
                        'banks': g(ACC, 'schedule', 'banks', 'banks_from_volume'),
                        'registers': g(ACC, 'schedule', 'absorbed_family', 'dirt_volume_registers'),
                        'bad_fraction_inverse': 10 ** 16,
                        'fallback_registers_per_child': 32 * 72 ** 2,
                        'kappa': g(ACC, 'kappa')},
             'at_most': {'completion_children': 0},
             'declares_every_body_on': 'integrity.json'},
    'acceptance': ['A1'],
    'unblocks': ['R4']})

contract['acceptance_tests'] = [
    {'id': 'A1', 'name': 'body hashes to the published digest',
     'test': 'every exported body hashes to the digest the word\'s certificates already published -- '
             'the five word bodies, the witness body, and PR205\'s chart and incidence streams -- and '
             'the index bodies, which are declarations, are hashed by the manifest instead',
     'bound': 'word 1cb7e8ed..., frames ad8e2705..., graph 31a09a55..., chronology 0fab548e..., '
              'profile c44ef864..., witness 612f0b91..., word 0728ed1c..., chart 22662b85..., '
              'incidence 76bff256...',
     'reject_control': 'any altered byte fails the hash; a matching hash is evidence of identity, '
                       'not correctness, and the contract says so'},
    {'id': 'A2', 'name': 'frame-record bijection',
     'test': 'the selected gauge family is the word\'s own rank-20 family, and each of its distinct '
             'frames is bijectively recorded in the frame table',
     'bound': '2,200 selected roles over 220 distinct gauge frames, 24,401 used frames, 17,114 '
              'physical roles',
     'reject_control': 'a frame used by a selected role with no record, or a map that is not a '
                       'bijection, or an id used twice'},
    {'id': 'A3', 'name': 'charts and factors',
     'test': 'fraction-free chart inversion and replayed elementary factors on every frame the new '
             'blocks use, with the denominator and numerator bounds PR205 published, and the chart '
             'stream anchored to the digest PR205 published',
     'bound': 'max_denominator <= 18, max_abs_numerator <= 5, max_chart_factors <= 171, and the '
              'chart stream hashing to 22662b85...',
     'reject_control': 'a factor that does not replay, a denominator above 18, or a stream that does '
                       'not hash to the published digest'},
    {'id': 'A4', 'name': 'columns of the banked word',
     'test': 'the formal columns re-run on the banked word: every source, target and dirty-register '
             'column over F2 and over the defining integers, with the rank-22 transitions realized by '
             'bank re-assignment instead of paid children',
     'bound': '20,634 formal columns and 17,114 dirty columns per direction, 1,760 source and 1,760 '
              'target columns, integer residual bound 39,780, packed digit bits 24',
     'reject_control': 'counts quoted from the certificate instead of coming out of the exported '
                       'tables, and any column that no longer restores'},
    {'id': 'A5', 'name': 'per-child bijection',
     'test': 'the exported occurrences map onto the pinned inventory\'s items -- 6,672 rank-22 ledger '
             'children per vertex under the row\'s factor-3 normalization, 20,016 three-copy items -- '
             'onto 6,116 banks of width 72, with no other bin touched',
     'bound': '20,016 items over 6,116 x 72 = 440,352 registers, 1,320 + 24 + 880 per vertex',
     'reject_control': 'an occurrence outside the ledger\'s rank-22 bin, a block left without its '
                       'item, or counts that are not the pinned inventory\'s'},
    {'id': 'A6', 'name': 'incidence colouring',
     'test': 'the colouring of the new bank incidences with the conflicting assignment rejected, and '
             'the incidence stream anchored to the digest PR205 published',
     'bound': '154,026 incidences, 45,842 banks, PR205\'s statistics: swaps 733, longest_swapped_path '
              '11, conflicting_assignment_rejected true, and the stream hashing to 76bff256...',
     'reject_control': 'a conflicting assignment accepted, or a stream that does not hash to the '
                       'published digest'},
    {'id': 'A7', 'name': 'prime witnesses',
     'test': 'distinct integer Gram/prime witnesses for every frame the new blocks use, with residual '
             'factors below the retained q bound',
     'bound': '24,401 used frames, 24,401 distinct bases, maximum determinant 118 bits, the retained '
              'rule q > 2^80',
     'reject_control': 'a repeated witness, or a factor above the retained bound'}]

contract['obligation_mapping'] = {
    'R1': ['B2', 'B3'],
    'R2': ['B1', 'B4', 'B5'],
    'R3': ['B1', 'B3', 'B5'],
    'R4': ['B2', 'B6']}

contract['not_required'] = [
    'internal id stability: the word\'s frame ids are already the canonical annihilator ids (its own '
    'conventions say so), so no renumbering map is asked for -- only A2\'s frame-record bijection',
    'program text beyond canonical data: B1 is the word, its frames, its graph, its chronology and '
    'its profile, not a listing in the supplier\'s own language',
    'sources for the supplier\'s own claims: the importer re-runs the columns (A4) and re-charts the '
    'frames (A3), so bit.formal\'s identity and defining_decoder booleans are claims to reproduce, '
    'not results',
    'a re-derivation of the accounting: the schedule, the whole-bank condition, the retained ledger '
    'and the conditional kappa are the pinned package\'s, and B6 must reproduce them; the one place '
    'an export may move a published number is R4\'s completion child, and then the recomputed kappa '
    'must be published and this contract\'s kappa citation re-anchored',
    'the gauge family\'s own absorption: it is already built and pinned in PR205 and is the '
    'precedent here, not a target',
    'anchored indexes: the two index bodies are declarations and are not anchored, because the '
    'bodies they describe are what carry the digests; the manifest is what ties them together',
    'any asymptotic interface: general Clifford/tensor, uniform weighted compilation, restored rows, '
    'routing, paid layout, prime supply, precision/recovery and fixed tape stay the stated '
    'assumptions they already are, so this contract can buy a completed conditional finite witness '
    'and never a theorem']

contract['import_harness'] = {
    'module': 'importer66.py',
    'contract': 'export-contract-bit.json',
    'exports_dir': 'exports-bit',
    'usage': 'python3 -B importer66.py --contract export-contract-bit.json --exports DIR '
             '[--checker FILE] [--partial] | --self-test',
    'exit_codes': {
        '0': 'admissible: every body present, the gate green and the pinned replay checker passed',
        '1': 'a check failed: the report names the test, its bound and what was seen',
        '2': 'refusing: at least one required body is absent, or the supplied checker is not the one '
             'the contract pins, so nothing is run and nothing is certified',
        '3': 'gate green, replay NOT RUN: no checker was supplied',
        '4': 'partial: the gate was run on the bodies present, for reporting only; nothing is discharged'},
    'layers': {
        'gate': 'decidable from the bodies\' declared data: hashes (A1, streams included, hashed as '
                'published), cardinalities and the frame-record bijection (A2), the chart and witness '
                'bounds (A3, A7), the colouring statistics (A6), the per-child bijection against the '
                'pinned inventory (A5) and the column counts that must come out of the exported '
                'tables rather than the certificate (A4)',
        'replay': 'the physics: the formal columns over F2 and over the defining integers, the '
                  'fraction-free chart replay, the incidence colouring and the moment envelope '
                  're-derived. The harness does not reimplement any of it and never claims to have run '
                  'it: the checker whose digest this contract pins must be supplied, and until it is '
                  'the replay is reported NOT RUN'},
    'replay_requirement': {
        'checker_digest': g(OCC, 'source_pins', 'checker_sha256'),
        'checker_source': 'source_pins.checker_sha256 of the pinned rank-22 occurrence inventory, '
                          'references/pr219-run1/inputs/absorbed-occurrences.json',
        'why': 'the physics is the bit word\'s own base checker, not a reimplementation, and the '
               'inventory is where the word pins it. The complex side\'s replay checker '
               '(lift.checker_sha256 of the PR193 certificate) is a different digest and is not '
               'accepted here: the two contracts pin their own supplier\'s checker'},
    'anchored_digests_are_of_published_bytes': 'hash files as published, gzip bodies and canonical '
                                                'streams included, and read .gz fields after '
                                                'decompressing; a body declared "stream" is hashed '
                                                'and never parsed',
    'self_test': '--self-test builds synthetic bit bodies in a temporary directory, patches the '
                 'anchored digests to the synthetic hashes -- streams included, written as they are '
                 'published -- and then exercises all seven checks, all four refusal codes and the '
                 'partial report, so the harness is proven to work and to reject while the real bit '
                 'drop is only part assembled'}

contract['failure_semantics'] = {
    'today': '0 of 6 bodies published by the pins; the drop assembled beside them holds B1 and B3, '
             'which the default import still refuses (code 2) and the partial report runs (code 4), '
             'so nothing is discharged',
    'order_of_discharge': 'A1 admits the word and witness bodies and the two streams, so B1 and B3 '
                          'are real re-runs rather than digests; B2\'s assignment is the one genuinely '
                          'new artifact R1 asks for, and schedule.py already supplies the admissible '
                          'tilings; A4 re-runs R2 on the banked word; A6-A7 close R3; B6 closes R4 by '
                          'reproducing the retained ledger exactly. If R1 introduces a completion '
                          'child the kappa moves: the export must then publish the recomputed kappa '
                          'and this contract\'s kappa citation must be re-anchored, which is the one '
                          'edit R4 licenses here',
    'never': 'no export can make the bound unconditional; see references/pr219-run1/obligations.json '
             '-> claim_scope and the complex side\'s contract for the interfaces this can never buy'}

contract['status'] = ('CONTRACT PUBLISHED AND MACHINE-CHECKED: verify.py -> check_bit_export_contract '
                      'resolves every citation against the pinned bytes, asserts the state of the drop, '
                      'that its eight anchored bodies are the published bytes and that the gate decides '
                      'A2 and A3 on them while refusing the rest; importer66.py --contract '
                      'export-contract-bit.json --self-test proves the gate on synthetic bit bodies and '
                      'the partial report on the real drop')

target = ROOT / 'export-contract-bit.json'
target.write_text(json.dumps(contract, indent=1, ensure_ascii=False) + '\n', newline='\n')


def resolve(node, keys):
    for key in keys:
        node = node[key]
    return node


fresh = json.loads(target.read_text())
checked = 0
for block in fresh['precedent'].values():
    for row in block['citations']:
        assert resolve(DOC[row['source']], row['keys']) == row['value'], row
        checked += 1
for row in fresh['today']['evidence'] + fresh['drop']['evidence']:
    assert resolve(DOC[row['source']], row['keys']) == row['value'], row
    checked += 1
for export in fresh['required_exports']:
    for row in export['must_reproduce']:
        assert resolve(DOC[row['source']], row['keys']) == row['value'], row
        checked += 1
bodies = [b for e in fresh['required_exports'] for b in e['bodies']]
print('wrote %s: %d citations resolve, %d exports, %d tests, %d bodies (%d anchored, %d streams)'
      % (target.name, checked, len(fresh['required_exports']), len(fresh['acceptance_tests']),
         len(bodies), sum(1 for b in bodies if b['anchored_digest']),
         sum(1 for b in bodies if b.get('stream'))))
