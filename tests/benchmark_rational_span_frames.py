"""One fresh-process benchmark of the existing exact mixed-point cut customers.

Usage: python3 -B benchmark.py CHECKOUT OUTPUT_JSON [--cpu CPU_NUMBER]
Run each baseline/patched sample as a new process; impose matching resource
limits externally. This benchmark uses only the public checkout and stdlib.
"""
import argparse
import hashlib
import json
from pathlib import Path
import os
import resource
import sys
import time

if sys.flags.optimize:
    raise SystemExit('Run without -O: audit assertions must remain enabled')

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('checkout', type=Path)
parser.add_argument('output', type=Path)
parser.add_argument('--cpu', type=int)
args = parser.parse_args()
if args.cpu is not None:
    os.sched_setaffinity(0, {args.cpu})
sys.path.insert(0, str(args.checkout.resolve()/'scripts'))
started = time.monotonic()
from experiments.mixed_point_circuit import build, factored_transpose
from rational_span_frames import audit

results = []
for h, expected in ((10, 16), (12, 320)):
    circuit, _ = factored_transpose(build(h, 3, 3, 1))
    assert circuit.verify()
    result = audit(circuit)
    assert result['singular_source_spans'] == expected
    assert result['cut_certified']
    assert result['compiled']['forward_nested'] and result['compiled']['reverse_nested']
    results.append(result)
record = dict(status='PASS complete mixed-point cut audits',
              audit_seconds=repr(time.monotonic()-started),
              peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              result=results,
              result_sha256=hashlib.sha256(json.dumps(
                  results, sort_keys=True, separators=(',', ':')).encode()).hexdigest())
with args.output.open('x') as stream:
    stream.write(json.dumps(record, indent=2)+'\n')
print(json.dumps({k: v for k, v in record.items() if k != 'result'}))
