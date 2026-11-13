#!/usr/bin/env python3
"""Read-only self-contained replay; emits one semantic receipt to stdout."""
from contextlib import redirect_stdout
from pathlib import Path
import gzip
import hashlib
import importlib.util
import io
import json
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
WORD = ROOT / 'inputs/WORD.json.gz'
WORD_SHA256 = 'acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9'
NOTICE = ROOT / 'NOTICE'
NOTICE_SHA256 = '78e060cbd33ebc4078cabf39e50191a977fb9eb5c41104533079e22da1d9d248'


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def need(condition, label):
    if not condition:
        raise AssertionError(label)


def main():
    raw = WORD.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == WORD_SHA256, 'exact native WORD pin')
    need(hashlib.sha256(NOTICE.read_bytes()).hexdigest() == NOTICE_SHA256,
         'retained NOTICE pin')
    word = json.loads(gzip.decompress(raw))

    screen = load('cache_kernel_screen', 'kernel_screen.py')
    history_filter = load('cache_history_filter', 'history_filter.py')
    history_exact = load('cache_history_exact', 'history_exact.py')
    prefilter_controls = load('cache_prefilter_controls', 'prefilter_controls.py')
    temporal_author = load('cache_temporal_author', 'temporal_author.py')
    temporal_exact = load('cache_temporal_exact', 'temporal_exact.py')
    main_probes = load('cache_main_probes', 'main_probes.py')
    all_author = load('cache_all_history_author', 'all_history_author.py')
    all_independent = load('cache_all_history_independent', 'all_history_independent.py')

    # All parsers must reject changed source bytes before scientific work.
    changed = bytearray(raw)
    changed[len(changed)//2] ^= 1
    with tempfile.TemporaryDirectory(prefix='cache-source-control-') as td:
        bad = Path(td)/'changed.gz'
        bad.write_bytes(changed)
        for name, call in [
            ('kernel', lambda: screen.run(seconds=1, source=bad, output=None)),
            ('streaming', lambda: history_filter.run(source=bad, prior=None)),
            ('independent', lambda: history_exact.run(source=bad, kr=None)),
            ('temporal_author', lambda: temporal_author.run(source=bad, prior=None)),
            ('temporal_exact', lambda: temporal_exact.run(source=bad, author=None, kernel=None)),
            ('main_probes', lambda: main_probes.run(source=bad)),
            ('all_history_author', lambda: all_author.run(source=bad)),
            ('all_history_independent', lambda: all_independent.verify(bad)),
        ]:
            caught = False
            try:
                call()
            except (ValueError, AssertionError) as exc:
                need('pin' in str(exc) or 'hash' in str(exc), 'source mutation rejected at binding')
                caught = True
            need(caught, name+' rejects changed source')

    quiet = io.StringIO()
    with redirect_stdout(quiet):
        kernel = screen.run(seconds=60, source=WORD, output=None)
        need(kernel['status'] == 'COMPLETE_EXACT_GLOBAL_KERNEL_RELOCATION_CENSUS',
             'full source candidate census completed')
        filtered = history_filter.run(source=WORD, prior=kernel,
                                      seconds=60, output=None)
        direct = history_exact.run(source=WORD, kr=kernel)
        controls = prefilter_controls.run()
        temporal_a = temporal_author.run(source=WORD, prior=kernel, seconds=60)
        need(temporal_a["status"] == "COMPLETE_EXACT_TEMPORAL_TWO_CACHE_FILTER",
             "additional temporal cuts completed")
        temporal_b = temporal_exact.run(source=WORD, author=temporal_a, kernel=kernel)

    need(controls['status'] == 'PASS', 'source-kernel synthetic controls')
    need(filtered['status'] == 'COMPLETE_EXACT_CUMULATIVE_HISTORY_FILTER',
         'history filter completed')
    need(filtered['checked_candidates'] == direct['source_span_survivors'] == 49,
         'both history engines cover all 49 source survivors')
    need(filtered['cumulative_hits'] == direct['candidate_history_hits'] == 0,
         'both history engines reject all candidates')
    need(filtered['destination_classes'] == direct['coframed_destination_subspaces'] == 40,
         'frame-class coverage agrees')
    need(filtered['independent_history_generators'] ==
         direct['independent_history_generators'] == 1465,
         'history rank coverage agrees')
    b_records = {r['event']: r for r in filtered['records']}
    c_records = {r['event']: r for r in direct['records']}
    need(set(b_records) == set(c_records), 'same exact candidate cuts')
    need(all(not b_records[e]['cumulative_span_hit'] and
             not c_records[e]['member_before_arrival'] and
             b_records[e]['historical_rank'] == c_records[e]['destination_history_rank']
             for e in b_records), 'per-cut exact history decisions and ranks agree')
    need(kernel['counts'] == {
        'public_source_False': 6214,
        'public_source_True': 18,
        'public_destination_False': 18,
        'owned_source_True': 31,
        'owned_destination_False': 31,
        'owned_source_False': 16,
    }, 'complete prefilter source/destination counts')

    probe_result = main_probes.run()
    need(probe_result['cuts'] == 33, '33 main-only history certificates')
    all_a = all_author.run(WORD)
    all_b = all_independent.verify(WORD, max_seconds=120)
    all_controls = all_independent.controls()
    need(all_a['unrestricted']['rational_nonmembership_certified'] ==
         all_b['MOVE_arrivals'] == 6279, 'all original history innovations agree')
    need(all_a['maximal_neutral']['rational_nonmembership_certified'] ==
         all_b['nonzero_projected_MOVEs'] == 6207, 'all projected nonzero innovations agree')
    need(all_a['unrestricted']['final_total_history_rank'] ==
         all_b['original_total_row_rank'] == 7780, 'unrestricted complete generator rank')
    need(all_a['maximal_neutral']['final_total_history_rank'] ==
         all_b['max_neutral_nonzero_row_rank'] == 7636, 'projected complete generator rank')
    for key in ('neutral_helpers', 'zero_MOVE_events', 'neutral_target_histogram', 'neutral_paid_histogram'):
        need(all_a[key] == all_b[key], 'fresh independently derived neutral source data: '+key)
    compact_b = {k:v for k,v in all_b.items()
                 if k not in ('records', 'seconds', 'replay_seconds', 'primary_input_only')}
    compact_b['full_per_coframe_certificates_sha256'] = hashlib.sha256(
        json.dumps(all_b['records'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    receipt = dict(
        status='PASS_P104_EARLIER_DESTINATION_CACHE_EXCLUSION',
        source_mutation_rejected_by_eight_engines=True,
        source_sha256=WORD_SHA256,
        notice_sha256=NOTICE_SHA256,
        instructions=len(word['program']),
        moves=kernel['checked_moves'],
        source_prefilter=dict(public_misses=6214, public_survivors=18,
                              owned_misses=16, owned_survivors=31),
        candidate_ranks={str(k): v for k, v in sorted(
            __import__('collections').Counter(r['rank'] for r in direct['records']).items())},
        destination_subspaces=direct['coframed_destination_subspaces'],
        initial_public_history_generators=direct['initial_public_rows_inserted'],
        nonzero_move_arrivals=direct['nonzero_MOVE_arrivals_to_target_subspaces'],
        independent_history_generators=direct['independent_history_generators'],
        coframed_scalar_operations=direct['coframed_scalar_events_using_target_history'],
        candidate_source_witnesses_reconstructed=direct['all_49_exact_source_witnesses_reconstructed'],
        history_hits=0,
        all_owned_temporal=dict(cuts=temporal_b['owned_MOVEs'],
            earlier_destination_hits=temporal_b['earlier_hits'],
            later_source_hits=temporal_b['later_hits'],
            separately_checked_new_cuts=temporal_b['independent_author_cases'],
            inserted_arrival_controls=temporal_b['inserted_arrival_controls'],
            past_subspaces=temporal_b['past_subspaces'],
            future_subspaces=temporal_b['future_subspaces']),
        union_earlier_destination_exclusions=65,
        all_original_earlier_destination_exclusions=6279,
        all_history_and_neutral_subsets=dict(author=all_a, independent=compact_b,
            independent_controls=all_controls,
            all_subsets='Every subset of the 72 derived neutral helpers, by the written unit-extension proof.'),
        main_only_history_separators=probe_result,
        history_engines='exact Fraction streaming filter and independent direct Fraction replay agree at all 49 strict-before cuts',
        prefilter_controls=controls,
        output='stdout only; no package files written')
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
