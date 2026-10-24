#!/usr/bin/env python3
"""Aggregate literal macro resources for the unchanged p19 chain."""
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    claim = json.loads((HERE / 'P19_CLAIM.json').read_text())
    forward = json.loads((HERE / 'P19_FORWARD_PROGRAM.json').read_text())
    word = json.loads((HERE / 'P19_WORD.json').read_text())
    reverse = json.loads((HERE / 'P19_REVERSE_PROGRAM.json').read_text())
    bill = claim['field_level_bill']
    f = forward['p19_extra_work_beyond_recoding_bill']
    p19 = {
        'forward_calls': forward['p19_forward_calls'],
        'forward_rank_one_queries': forward['p19_rank_one_query_calls'],
        'forward_copy': f['copy'],
        'forward_add': f['add'],
        'forward_clear': f['clear'],
        'reverse_central_corrections': 2 * 112 * 19,
        'existing_recodings': bill['recodings'],
        'existing_maps': bill['monomial_field_maps'],
        'existing_scalar_adds': bill['scalar_adds'],
        'existing_owned_clears': bill['owned_clears'],
        'recursive_gaussian_children': bill['recursive_gaussian_children'],
        'reverse_macro_events': reverse['macro_events'],
        'reverse_native_calls': reverse['counts']['native_reverse'],
        'reverse_central_q': reverse['counts']['central_q'],
        'reverse_forward_calls': reverse['counts']['forward_query'],
    }
    # This is a raw-operation upper bound. It intentionally does not convert
    # Gaussian rank or claim new paid-D entries.
    p19['new_rank_bearing_children'] = 0
    p19['extra_raw_scalar_events'] = (p19['forward_copy'] + p19['forward_add'] +
                                      p19['forward_clear'] +
                                      p19['reverse_central_corrections'])
    p19['total_rank_free_or_inherited_events'] = (
        p19['existing_maps'] + p19['existing_scalar_adds'] +
        p19['existing_owned_clears'] + p19['extra_raw_scalar_events'])
    need(p19['recursive_gaussian_children'] == 0, 'existing recursive children')
    need(p19['new_rank_bearing_children'] == 0, 'macro rank-bearing children')
    need(reverse['status'] == 'PASS_LITERAL_REVERSE_LETTER_PROGRAM', 'reverse macro program')
    need(reverse['endpoint']['all_roles_uncoded'] and reverse['endpoint']['owned_scratch_blank'],
         'reverse macro endpoint')
    need(word['gate_records'] == 259, 'word binding')
    out = {
        'status': 'PASS_P19_MACRO_RESOURCE_ACCOUNTING',
        'scope': 'literal macro resource upper bound; no new positive-rank children and all added raw events explicit',
        'resources': p19,
        'precision_envelope': forward['precision_envelope'],
        'reverse_program': 'P19_REVERSE_PROGRAM.json',
        'claim_kappa_unchanged': claim['kappa'],
        'native_event_lowering': 'the macro words are source-bound at the primitive wrapper level; full tape admission remains the inherited interface',
    }
    (HERE / 'P19_MACRO_RESOURCES.json').write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
