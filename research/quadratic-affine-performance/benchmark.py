"""Same-input A/B benchmark for the batched quadratic-affine row engine.

Phase 1 compares every row of every fixture produced by the shipped batched
engine against the verbatim base-commit reference (one `inner` call per pair),
and times both. Phase 2 recomputes the full `audit_quadratic_affine.py`
certificate and requires it to equal the committed
certificates/quadratic-affine-vectors.json byte for byte. Phase 3 runs
negative controls that must fail if the comparison is vacuous.

Usage (from the repository root):

    python3 -B research/quadratic-affine-performance/benchmark.py --out /tmp/qa-benchmark.json

The output path must be fresh. Timing numbers are measurements, not
acceptance thresholds. With help from opencode. Apache-2.0.
"""
import argparse
import json
import platform
import sys
import time
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from experiments.quadratic_affine import family, vector, rank_witness, _orthogonality_rows
from reference import reference_rows, rank_witness_reference

FIXTURES = json.loads((ROOT / 'scripts/experiments/quadratic_affine_witnesses.json').read_text())


def run(out):
    results = []
    total_ref = total_new = 0.0
    rows_compared = 0
    for index, w in enumerate(FIXTURES):
        f = family(w['t'], w['complex_phases'], w['parity'])
        vectors = [vector(f, i) for i in w['sample']]
        start = time.monotonic()
        new = _orthogonality_rows(vectors, f['D'], w['independent_rows'])
        time_new = time.monotonic() - start
        start = time.monotonic()
        ref = reference_rows(vectors, w['independent_rows'])
        time_ref = time.monotonic() - start
        mismatched = sum(1 for i in w['independent_rows'] if new[i] != ref[i])
        rows_compared += len(w['independent_rows'])
        total_ref += time_ref; total_new += time_new
        results.append(dict(fixture=index, t=w['t'], complex_phases=w['complex_phases'],
                            parity=w['parity'], columns=len(vectors), rows=len(w['independent_rows']),
                            rows_mismatched=mismatched,
                            seconds_reference=round(time_ref, 3), seconds_batched=round(time_new, 3)))
        print('rows fixture %d: %d/%d rows equal, reference %.3fs, batched %.3fs'
              % (index, len(w['independent_rows']) - mismatched, len(w['independent_rows']), time_ref, time_new), flush=True)
    assert all(r['rows_mismatched'] == 0 for r in results), 'Row-level mismatch; see JSON'
    heavy = dict(FIXTURES[-1])
    start = time.monotonic()
    witness = rank_witness(**heavy)
    witness_seconds = time.monotonic() - start
    print('heavy rank_witness (batched engine): %.2fs, rank %d' % (witness_seconds, witness['binary_rank_lower']), flush=True)

    import audit_quadratic_affine
    import prepare_layers
    start = time.monotonic()
    certificate = audit_quadratic_affine.certificate()
    certificate_seconds = time.monotonic() - start
    fresh = json.dumps(prepare_layers.serializable(certificate), indent=2, sort_keys=True) + '\n'
    committed = (ROOT / 'certificates/quadratic-affine-vectors.json').read_text(encoding='utf-8')
    certificate_equal = fresh.replace('\r\n', '\n') == committed.replace('\r\n', '\n')
    assert certificate_equal, 'Fresh certificate differs from the committed certificate'

    base = json.loads((Path(__file__).resolve().parent / 'evidence/base-certificate.json').read_text(encoding='utf-8'))
    changed = json.loads(fresh)
    for key in base:
        if key != 'source_sha256':
            assert changed[key] == base[key], 'Certificate field changed versus the base-commit engine: ' + key
    differences = sorted(k for k in set(changed['source_sha256']) | set(base['source_sha256'])
                         if changed['source_sha256'].get(k) != base['source_sha256'].get(k))
    assert differences == ['scripts/experiments/quadratic_affine.py'], differences
    print('certificate equals committed; base-commit certificate differs only in: %s' % differences[0], flush=True)

    x = int.from_bytes(b'\x00\x00\x01\x00', 'little')  # odd lane value 1 sits behind zero lanes
    ones = int.from_bytes(b'\x01' * 4, 'little')
    highs = int.from_bytes(b'\x80' * 4, 'little')
    naive_flags = (x - ones) & ~x & highs
    odd_lane_control = naive_flags != sum(1 << (8 * k + 7) for k in range(4) if k != 2)

    w = FIXTURES[5]
    f = family(w['t'], w['complex_phases'], w['parity'])
    vectors = [vector(f, i) for i in w['sample']]
    good = _orthogonality_rows(vectors, f['D'], w['independent_rows'])
    broken = {i: (good[i] ^ (1 << i)) & ~1 for i in w['independent_rows']}
    broken_gather_control = broken != reference_rows(vectors, w['independent_rows'])

    assert odd_lane_control and broken_gather_control, 'Negative controls are vacuous'
    report = dict(status='PASS_QUADRATIC_AFFINE_BATCHED_ROWS',
                  rows_compared=rows_compared, rows_mismatched=0,
                  seconds_rows_reference=round(total_ref, 3), seconds_rows_batched=round(total_new, 3),
                  heavy_rank_witness_seconds=round(witness_seconds, 3),
                  certificate_seconds=round(certificate_seconds, 3),
                  certificate_sha256=sha256(fresh.encode()).hexdigest(),
                  certificate_equals_committed=True,
                  negative_controls=dict(odd_lane_false_positive_demonstrated=True,
                                         dropped_gather_stage_detected=True),
                  fixtures=results,
                  environment=dict(python=sys.version.split()[0], platform=platform.platform()),
                  scope='Row-engine differential only; the GF(2) elimination is unchanged code.')
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('PASS identical rows (%d rows, 0 mismatches); certificate equals committed; '
          'controls: odd-lane false positive demonstrated, dropped gather stage detected' % rows_compared)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True, help='Fresh output path for the evidence JSON')
    a = p.parse_args()
    assert not a.out.exists(), 'Choose a fresh output path'
    run(a.out.resolve())


if __name__ == '__main__':
    main()
