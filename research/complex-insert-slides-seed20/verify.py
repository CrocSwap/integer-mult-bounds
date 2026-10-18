#!/usr/bin/env python3
"""Re-run the complete SW4 pre-read insertion-slide census and pin its result.

Steps (deterministic; standard library only; refuses -O):
  1. the behavior/failure tests in test_search.py must pass;
  2. search.main() re-enumerates every single, pair and tie-order swap and
     re-runs the controls (pinned recipe reproduction, out-of-window
     rejection, exact-engine sign cross-check);
  3. the fresh EVIDENCE.json must match EXPECTED.json on every pinned count,
     the best root, the improving-row count and the canonical rows digest.

Usage: python3 -B research/complex-insert-slides-seed20/verify.py
Expected final line:
  PASS_INSERT_SLIDES_SEED20 singles=... pairs=... swaps=... improving=...
"""
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
assert __debug__, 'do not run with -O'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rows_digest(evidence):
    rows = evidence['singles'] + evidence['pairs'] + evidence['swaps']
    blob = json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(blob).hexdigest()


def main():
    ts = load('test_search', HERE / 'test_search.py')
    suite = unittest.defaultTestLoader.loadTestsFromModule(ts)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    assert result.wasSuccessful(), 'behavior/failure tests failed'

    ss = load('search', HERE / 'search.py')
    expected = json.loads((HERE / 'EXPECTED.json').read_text(encoding='utf-8'))
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / 'EVIDENCE.json'
        evidence = ss.main(str(out))

    ctl = evidence['controls']
    for key in ('pinned_slides_equal_apply_recipe', 'pinned_output_sha_matches_recipe',
                'pinned_no_refit_problems', 'pinned_profile_matches_recipe',
                'frame8_calibration_matches_selected_endpoint', 'out_of_window_rejected'):
        assert ctl[key] is True, 'control failed: ' + key
    summ = evidence['summary']
    for key in ('singles', 'pairs', 'swaps', 'legal_total', 'illegal_total',
                'inexact_total', 'improving_total'):
        assert summ[key] == expected['summary'][key], (key, summ[key], expected['summary'][key])
    assert abs(summ['best_root'] - expected['summary']['best_root']) < 1e-15
    assert abs(summ['pinned_root'] - expected['summary']['pinned_root']) < 1e-15
    assert rows_digest(evidence) == expected['rows_digest'], 'rows digest mismatch'
    assert evidence['pricing']['exact_engine_crosscheck'] == expected['exact_engine_crosscheck']
    assert all(v['brackets_root'] for v in evidence['pricing']['exact_engine_crosscheck'].values()), \
        'exact-engine bracket failed'
    print('PASS_INSERT_SLIDES_SEED20 singles=%d pairs=%d swaps=%d legal=%d improving=%d best_root=%.12f'
          % (summ['singles'], summ['pairs'], summ['swaps'], summ['legal_total'],
             summ['improving_total'], summ['best_root']))


if __name__ == '__main__':
    main()
