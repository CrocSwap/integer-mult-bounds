"""Measured identical seven-lever sessions; every timed trace is compared in full.

No speed assertion is a correctness test. Module construction and process
startup are outside the timed fixture. Gareth Davidson / OpenAI Codex, Apache-2.0.
"""
from pathlib import Path
import argparse
import hashlib
import json
import platform
import statistics
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from session import Session, canonical, need
from verify import paths_and_pins


def measure():
    paths, pins = paths_and_pins()
    oracle = Session(*paths, pins, reuse=False)
    golden_stdout = oracle.fixture();golden = canonical(oracle.events)
    expected = oracle.evidence(golden_stdout)
    reference, optimized = Session(*paths, pins, reuse=False), Session(*paths, pins)
    def timed(label, session):
        started = time.perf_counter_ns()
        out = session.fixture()
        evidence = session.evidence(out)
        need(canonical(session.events) == golden and out == golden_stdout, 'full timed fixture trace differs')
        elapsed = (time.perf_counter_ns() - started) / 1e9
        return {'mode': label, 'wall_seconds': elapsed, 'evidence': evidence}
    initial = [timed('initial_uncached', reference), timed('initial_fill', optimized)]
    rows = []
    for i in range(3):
        order = [('uncached', reference), ('warm', optimized)] if i % 2 == 0 else [('warm', optimized), ('uncached', reference)]
        for label, session in order:
            row = timed(label, session);row['pair'] = i;rows.append(row)
    a = statistics.median(x['wall_seconds'] for x in rows if x['mode'] == 'uncached')
    b = statistics.median(x['wall_seconds'] for x in rows if x['mode'] == 'warm')
    return {'schema': 'exact-child-interval-benchmark/1', 'python': sys.version,
            'platform': platform.platform(), 'context': reference.context,
            'driver_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'adapter_sha256': hashlib.sha256((HERE / 'session.py').read_bytes()).hexdigest(),
            'source_sha256': pins, 'expected_trace_sha256': expected['trace_sha256'],
            'initial': initial, 'interleaved_pairs': rows, 'uncached_median_seconds': a,
            'warm_median_seconds': b, 'warm_speed_ratio': a / b,
            'initial_fill_speed_ratio': initial[0]['wall_seconds'] / initial[1]['wall_seconds'],
            'timed_boundary': 'Unchanged seven-lever execution, source/context guards, all typed events, canonical trace/hash and exact full-trace/output comparison. Excludes process startup, module construction, the untimed oracle and separate failure controls.',
            'scope': 'Local planner fixture only; no full selected replay or production-adoption claim.'}


def main():
    parser = argparse.ArgumentParser();parser.add_argument('--out', type=Path, required=True);args = parser.parse_args()
    need(not args.out.exists(), 'output already exists')
    result = measure()
    with args.out.open('x') as f:json.dump(result, f, indent=2, sort_keys=True);f.write('\n')
    print('PASS_EXACT_INTERVAL_BENCHMARK', 'warm_ratio=' + str(result['warm_speed_ratio']),
          'initial_fill_ratio=' + str(result['initial_fill_speed_ratio']))


if __name__ == '__main__':
    main()
