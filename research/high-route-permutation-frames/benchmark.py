"""One fresh-process, instrumented before/after fixture benchmark.

Run three alternating pairs externally; timings are not proof predicates.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from check_physical import cases, run_case

parser = argparse.ArgumentParser()
parser.add_argument("--optimized", action="store_true")
args = parser.parse_args()
receipt, seconds = run_case(cases()[0],args.optimized)
print(json.dumps(dict(optimized=args.optimized,seconds=seconds,
                      python=platform.python_version(),platform=platform.platform(),
                      native_calls=receipt["calls"]["swaps"],physical_io=receipt["total"],
                      receipt_sha256=sha256(json.dumps(receipt,sort_keys=True,
                                                       separators=(",",":")).encode()).hexdigest()),
                 sort_keys=True))
