"""Exact price of resetting at every non-scalar boundary versus PR1259."""
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('v', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def check_predecessor(rows, actual):
    v.need(set(actual) == {r['helper'] for r in rows}, 'complete predecessor helper coverage')
    for row in rows:
        v.need(actual[row['helper']] == row['delta_real'], 'PR1259 minimum mismatch')


def compute():
    lib = v.engine()
    word, programs, _, _ = lib.load()
    helpers, _ = lib.domain(word, programs)
    predecessor = json.loads((HERE / 'vendor/pr1259/CERTIFICATE.json').read_text())
    cert = json.loads((HERE / 'CERTIFICATE.json').read_text())
    answer = {'status': 'PASS_ZERO_BOUNDARY_PRICE_COMPARISON', 'pr1259_head':
              '61367611154266a982fe25e1a6243a8aad77227d', 'orientations': {}}
    for orientation, events in programs.items():
        streams = v.terms(lib, events, helpers)
        prior = predecessor['orientations'][orientation]['census']
        wanted_helpers = set(predecessor['helpers']) | {359, 427}
        rows, actual = [], {}
        for h in sorted(wanted_helpers):
            runs = list(streams[h].values())
            relaxed = v.solve_run([term for run in runs for term in run])['delta']
            reset = sum(v.solve_run(run)['delta'] for run in runs)
            v.need(reset >= relaxed, 'restriction cannot improve optimum')
            v.need(reset == next(r[1] for r in cert['orientations'][orientation]['rows'] if r[0] == h),
                   'reset census binding')
            if h in predecessor['helpers']:
                actual[h] = relaxed
            rows.append({'helper': h, 'unrestricted_delta_per_component': relaxed,
                         'reset_delta_per_component': reset, 'reset_price_per_component': reset - relaxed})
        check_predecessor(prior, actual)
        for h, premium in ((276, 2), (359, 0), (427, 2)):
            v.need(next(r['reset_price_per_component'] for r in rows if r['helper'] == h) == premium,
                   'named boundary price')
        # Actual certificate price corruption and missing-domain controls.
        bad = dict(actual)
        bad[276] += 1
        rejected = 0
        for corrupted in (bad, {h: d for h, d in actual.items() if h != 276}):
            try:
                check_predecessor(prior, corrupted)
            except ValueError:
                rejected += 1
        v.need(rejected == 2, 'comparison controls')
        answer['orientations'][orientation] = {'predecessor_minima_checked': len(actual),
                                               'rows': rows, 'rejection_controls': rejected}
    return answer


if __name__ == '__main__':
    result = compute()
    path = HERE / 'BOUNDARY-COMPARISON.json'
    if '--write' in sys.argv:
        path.write_text(json.dumps(result, indent=2) + '\n')
    else:
        v.need(result == json.loads(path.read_text()), 'saved boundary comparison')
    print(result['status'], 'PR1259 minima 32', 'comparison controls 4',
          'complex reset price L276=4 L359=0 L427=4')
