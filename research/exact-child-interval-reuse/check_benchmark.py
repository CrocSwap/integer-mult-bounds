"""Bind a historical timing receipt to the exact driver, adapter and proof trace.

This validates a recorded measurement; it does not remeasure performance.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import hashlib
import math
import statistics
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from session import canonical, need
from verify import read, paths_and_pins


def check(path):
    b = read(path);result = read(HERE / 'RESULT.json');_, pins = paths_and_pins()
    need(b['schema'] == 'exact-child-interval-benchmark/1', 'benchmark schema')
    need(b['source_sha256'] == pins and b['context']['source_sha256'] == pins, 'benchmark source binding')
    for key, name in [('driver_sha256', 'benchmark.py'), ('adapter_sha256', 'session.py')]:
        need(b[key] == hashlib.sha256((HERE / name).read_bytes()).hexdigest(), 'benchmark code binding')
    need(b['context']['precision'] == result['precision'] and
         b['expected_trace_sha256'] == result['baseline']['trace_sha256'], 'benchmark trace binding')
    need([x['mode'] for x in b['initial']] == ['initial_uncached', 'initial_fill'], 'initial timing coverage')
    rows = b['interleaved_pairs']
    need([(x['pair'], x['mode']) for x in rows] ==
         [(0, 'uncached'), (0, 'warm'), (1, 'warm'), (1, 'uncached'), (2, 'uncached'), (2, 'warm')],
         'interleaved timing coverage')
    expected = {'initial_uncached': 'baseline', 'uncached': 'baseline',
                'initial_fill': 'initial_fill', 'warm': 'warm'}
    for row in b['initial'] + rows:
        seconds = row['wall_seconds']
        need(type(seconds) in (int, float) and math.isfinite(seconds) and seconds > 0, 'positive finite duration')
        need(canonical(row['evidence']) == canonical(result[expected[row['mode']]]), 'complete timed evidence differs')
    a = statistics.median(x['wall_seconds'] for x in rows if x['mode'] == 'uncached')
    c = statistics.median(x['wall_seconds'] for x in rows if x['mode'] == 'warm')
    need(a == b['uncached_median_seconds'] and c == b['warm_median_seconds'] and
         a / c == b['warm_speed_ratio'], 'recorded warm statistics')
    need(b['initial'][0]['wall_seconds'] / b['initial'][1]['wall_seconds'] == b['initial_fill_speed_ratio'],
         'recorded initial statistics')
    return b


if __name__ == '__main__':
    for name in ('BENCHMARK.json', 'BENCHMARK-PY314.json'):
        check(HERE / name)
    print('PASS_HISTORICAL_BENCHMARK_BINDINGS', 'not_a_new_timing_measurement')
