#!/usr/bin/env python3
"""Authenticate root's fresh full selected catalogue runs, distinct from rerunning."""
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    review = HERE/'review/catalogue'
    record = json.loads((review/'catalogue-replay.json').read_text())
    need(record['status'] == 'PASS_FRESH_COMPLETE_SELECTED_CATALOGUE', 'fresh completion status')
    need(record['base'] == 'e54523517d0f03e58352e647c403a5af3e525a57', 'exact selected base')
    for path, expected in record['source_sha256'].items():
        need(sha256((HERE/'inputs'/path).read_bytes()).hexdigest() == expected, 'fresh catalogue source: '+path)
    need([s['slice'] for s in record['slices']] == [[0,1000],[1000,2000],[2000,3057]], 'complete disjoint slice coverage')
    counts = boundaries = 0
    for i,slice_ in enumerate(record['slices']):
        raw = (review/f'catalogue-{i}.log').read_bytes()
        historical = (HERE/f'inputs/docs/research/pr-intake-evidence/pr7000-application/native-catalogue-{i}.log').read_bytes()
        need(raw == historical and slice_['byte_identical_log'], 'fresh and historical exact output agreement')
        need(sha256(raw).hexdigest() == slice_['fresh_log_sha256'] == slice_['historical_log_sha256'], 'fresh log authentication')
        text = raw.decode(); data = json.loads(text[text.index('{'):])
        need(data['status'] == 'PASS_CURRENT_NATIVE_CATALOGUE_SLICE', 'fresh catalogue success')
        for key in ['checked_maps','main_boundary_pairs','phase_control_rejected','catalogue_digest','exact_recipe_digest','main_boundary_digest']:
            need(data[key] == slice_[key], 'fresh catalogue receipt field: '+key)
        need(data['phase_control_rejected'], 'fresh phase-only corruption rejected')
        counts += data['checked_maps']; boundaries += data['main_boundary_pairs']
    need(counts == 3057 and boundaries == 104, 'complete selected native coverage')
    print(json.dumps(dict(status='PASS_FRESH_CATALOGUE_RECEIPT_BINDINGS', maps=counts,
                         boundary_pairs=boundaries, phase_controls=3,
                         observed_completed_utc=record['observed_completed_utc'],
                         scope='Authenticate completed fresh root runs; this short command does not rerun their full calculation.'),indent=2))


if __name__ == '__main__':
    main()
