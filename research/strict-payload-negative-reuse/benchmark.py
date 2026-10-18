#!/usr/bin/env python3
"""Full mismatch classify calls on fixed payloads; timing is not a gate.

Nick Petalas. Apache-2.0. Substantial automated assistance was used.
"""
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import statistics
import time
import zlib

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('negative_verifier', HERE / 'verify.py')
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def fixtures():
    fast, paired = verify.setup()
    retained = paired.module(verify.ROOT / paired.OLD / 'verify.py', {'compare': fast.source})
    data = retained.corpus(retained.bound_inputs())
    largest = sorted((len(gzip.decompress(raw)), name, raw) for name, raw in data.items()
                     if name.endswith('.json.gz'))[-5:]
    rows = []
    for size, name, raw in reversed(largest):
        body = gzip.decompress(raw).rstrip()
        verify.require(body.startswith(b'{') and body.endswith(b'}'), 'object fixture required')
        verify.require(b'"_negative_reuse_probe"' not in body, 'probe key already exists')
        changed = gzip.compress(body[:-1] + b',"_negative_reuse_probe":false}', mtime=0)
        rows.append((name, size, raw, changed))
    return fast, rows


def measure(fast, fixture, rounds):
    name, size, raw, changed = fixture
    functions = {'original': fast.original_classify,
                 'paired': fast.parent.classify, 'reuse': fast.classify}
    expected = fast.original_classify(name, raw, changed)
    verify.require(not fast.accepted(expected), 'proof change must be rejected')
    samples = {key: [] for key in functions}
    for trial in range(rounds):
        order = ('original', 'paired', 'reuse')
        shift = trial % len(order)
        for key in order[shift:] + order[:shift]:
            start = time.perf_counter()
            actual = functions[key](name, raw, changed)
            elapsed = time.perf_counter() - start
            verify.require(verify.encoded(actual) == verify.encoded(expected), 'full benchmark result differs')
            samples[key].append(elapsed)
    medians = {key: statistics.median(values) for key, values in samples.items()}
    return {'file': name, 'body_bytes': size,
            'reference_sha256': hashlib.sha256(raw).hexdigest(),
            'changed_sha256': hashlib.sha256(changed).hexdigest(),
            'result': expected, 'seconds': samples, 'median_seconds': medians,
            'median_ratio': medians['paired'] / medians['reuse']}


def run(rounds):
    fast, data = fixtures()
    rows = []
    for fixture in data:
        row = measure(fast, fixture, rounds)
        rows.append(row)
        print(row['file'], round(row['median_ratio'], 3), flush=True)
    return {'python': platform.python_version(), 'platform': platform.platform(),
            'zlib_build': zlib.ZLIB_VERSION, 'zlib_runtime': zlib.ZLIB_RUNTIME_VERSION,
            'rotating_order_trials': rounds, 'files': rows,
            'aggregate_median_ratio': sum(r['median_seconds']['paired'] for r in rows) /
                                      sum(r['median_seconds']['reuse'] for r in rows),
            'scope': 'Same five largest frozen compressed JSON bodies, one added unknown root field; complete calls including decompression/parsing/diagnostics, excluding setup and fixture generation. Machine-dependent observation; no threshold or supplier claim.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rounds', type=int, default=3)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    verify.require(1 <= args.rounds <= 9, 'trial count must be 1 through 9')
    result = run(args.rounds)
    with args.out.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
