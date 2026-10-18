#!/usr/bin/env python3
"""Paired before/after timings on the same fixture; measurements, never gates.

Two fixtures:
  unit   -- `replay()` on the two pinned words, five alternating pairs
            (historical scripts/experiments/binary_frame_replay.py vs this
            package's adapter); identical receipts asserted every run.
  suite  -- the frozen historical test module tests/test_joint_reclaim.py run
            unmodified in a clean subprocess through suite_arm.py, three
            alternating pairs: the `historical` arm imports the frozen
            modules, the `fast` arm preloads shim/binary_frame_replay.py so
            the module's own `from binary_frame_replay import replay`
            resolves to the adapter. Every test must pass in both arms.

Only the replay implementation differs between arms; the test module bytes,
the words, the checks and the transitions stage are identical. A suite run is
accepted only when it passes every test, so no speedup can come from dropped
coverage.

Usage: python3 benchmark.py [--pairs 3] [--unit-pairs 5] [--out BENCHMARK.json]
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')

import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORDS = [ROOT / 'certificates/joint-dual-word-23.json.gz',
         ROOT / 'certificates/joint-dual-word-25.json.gz']


def suite_run(arm):
    process = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'suite_arm.py'), str(ROOT), arm],
                             capture_output=True, text=True, cwd=str(ROOT))
    if process.returncode != 0:
        raise SystemExit(f'{arm} arm failed to run:\n{process.stdout}\n{process.stderr}')
    record = json.loads(process.stdout.strip().splitlines()[-1])
    if record['failures'] or record['errors'] or record['tests'] == 0:
        raise SystemExit(f'{arm} arm did not pass cleanly: {record}')
    return record


def unit_pairs(count):
    sys.path.insert(0, str(HERE))
    import fast_replay
    legacy = fast_replay.historical_replay
    rows = []
    for pair in range(count):
        for word in WORDS:
            order = ('historical', 'fast') if pair % 2 == 0 else ('fast', 'historical')
            run = {}
            for arm in order:
                replay = legacy.replay if arm == 'historical' else fast_replay.replay
                start = time.perf_counter()
                receipt = replay(word)
                run[arm] = dict(seconds=time.perf_counter() - start,
                                receipt=hashlib.sha256(
                                    json.dumps(receipt, sort_keys=True).encode()).hexdigest())
            if run['historical']['receipt'] != run['fast']['receipt']:
                raise SystemExit('receipts differ between arms on ' + word.name)
            rows.append(dict(pair=pair, word=word.name, order=list(order),
                             historical=run['historical']['seconds'],
                             fast=run['fast']['seconds']))
    return rows


def summary(rows):
    old = statistics.median(r['historical'] for r in rows)
    new = statistics.median(r['fast'] for r in rows)
    return dict(historical_median=old, fast_median=new, speedup=old / new)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pairs', type=int, default=3)
    parser.add_argument('--unit-pairs', type=int, default=5)
    parser.add_argument('--out', default=str(HERE / 'BENCHMARK.json'))
    args = parser.parse_args()
    unit = unit_pairs(args.unit_pairs)
    suite_rows = []
    for pair in range(args.pairs):
        order = ('historical', 'fast') if pair % 2 == 0 else ('fast', 'historical')
        run = {}
        for arm in order:
            run[arm] = suite_run(arm)
        suite_rows.append(dict(pair=pair, order=list(order),
                               historical=run['historical']['seconds'],
                               fast=run['fast']['seconds'],
                               tests=run['historical']['tests'],
                               fast_tests=run['fast']['tests']))
    document = dict(
        fixture_unit='replay() on certificates/joint-dual-word-{23,25}.json.gz',
        fixture_suite='frozen tests/test_joint_reclaim.py, unmodified, both arms must pass every test',
        python=sys.version.split()[0], platform=sys.platform, cpu_count=os.cpu_count(),
        unit_pairs=unit, unit_summary=summary(unit),
        suite_pairs=suite_rows, suite_summary=summary(suite_rows),
        note='Timings are measurements, never a correctness gate; receipts and test outcomes are asserted.')
    Path(args.out).write_text(json.dumps(document, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(dict(unit=document['unit_summary'], suite=document['suite_summary']), indent=2))


if __name__ == '__main__':
    main()
