"""Fresh-process alternating complete-replay benchmark; no timing assertion."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

P = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--pairs', type=int, default=3)
    args = ap.parse_args()
    if not 1 <= args.pairs <= 10:
        raise ValueError('one to ten benchmark pairs')
    runs = []
    with tempfile.TemporaryDirectory(prefix='p104-cache-bench-') as tmp:
        for pair in range(args.pairs):
            for mode in (['reference', 'cached'] if pair % 2 == 0 else ['cached', 'reference']):
                dest = Path(tmp)/f'{pair}-{mode}.json'
                command = [sys.executable, '-I', '-O', '-B', str(P/'accelerated.py'), '--out', str(dest)]
                if mode == 'reference':
                    command.append('--reference')
                start = time.perf_counter()
                subprocess.run(command, check=True, capture_output=True, text=True, timeout=300)
                elapsed = time.perf_counter()-start
                result = json.loads(dest.read_text())
                payload = json.dumps(result['source_receipt'], sort_keys=True, separators=(',', ':')).encode()
                runs.append({'pair': pair, 'mode': mode, 'seconds': elapsed,
                             'complete_receipt_sha256': hashlib.sha256(payload).hexdigest(),
                             'cache_statistics': result['cache_statistics']})
                print(f'{mode} pair={pair} seconds={elapsed:.6f}', flush=True)
    if len({r['complete_receipt_sha256'] for r in runs}) != 1:
        raise ValueError('complete mathematical receipt mismatch')
    med = {mode: statistics.median(r['seconds'] for r in runs if r['mode'] == mode)
           for mode in ['reference', 'cached']}
    out = {'python': platform.python_version(), 'platform': platform.platform(),
           'processor': platform.processor(), 'runs': runs, 'median_seconds': med,
           'reference_over_cached_median': med['reference']/med['cached'],
           'scope': 'Fresh-process same-fixture full native replay, including all five original faults; wall times include startup, source hashing and receipt comparison. One machine, no guaranteed speedup.'}
    with args.out.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(out, handle, indent=2)
        handle.write('\n')


if __name__ == '__main__':
    main()
