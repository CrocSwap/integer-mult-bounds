"""Paired full-caller benchmark; timings are descriptive, never acceptance gates."""
from pathlib import Path
import argparse
import json
import platform
import statistics
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import adapter
import verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pairs', type=int, default=3)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    adapter.need(args.pairs > 0, 'Positive pair count')
    records = []
    with tempfile.TemporaryDirectory(prefix='qq16-row-benchmark-') as temporary:
        for pair in range(args.pairs):
            outputs = {}
            order = ('reference', 'integer') if pair % 2 == 0 else ('integer', 'reference')
            for engine in order:
                folder = Path(temporary) / str(pair) / engine
                start = time.perf_counter()
                result, receipt = verify.arm(engine, folder)
                elapsed = time.perf_counter() - start
                outputs[engine] = folder, result, receipt
                records.append({'pair': pair, 'engine': engine, 'seconds': elapsed})
            left, right = outputs['reference'], outputs['integer']
            verify.compare(left[0], right[0], left[2], right[2], left[1].stdout, right[1].stdout)
    medians = {engine: statistics.median(r['seconds'] for r in records if r['engine'] == engine)
               for engine in ('reference', 'integer')}
    result = {'python': sys.version, 'platform': platform.platform(), 'pairs': args.pairs,
              'measurements': records, 'median_seconds': medians,
              'ratio_of_medians': medians['reference'] / medians['integer'],
              'all_original_outputs_and_nine_scalar_calls_equal': True,
              'adapter_sha256': left[2]['adapter_sha256'],
              'scope': 'Fresh processes on a shared host; same complete caller, checks and trace instrumentation. OS caches not flushed. Timings are descriptive.'}
    args.out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
