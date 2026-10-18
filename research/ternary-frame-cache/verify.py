#!/usr/bin/env python3
"""Compare complete exact edge streams and alternate fresh-process timings.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

from support import (HERE, ROOT, canonical, compare_traces, digest, need,
                     verify_sources)


def run(engine, path, trace=False):
    command = [sys.executable, '-B', str(HERE / 'run.py'), '--engine', engine,
               '--out', str(path)] + (['--trace'] if trace else [])
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    for key in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONSTARTUP'):
        env.pop(key, None)
    start = time.perf_counter()
    process = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                             text=True, timeout=300)
    wall = time.perf_counter() - start
    path.parent.joinpath(path.name + '.log').write_text(process.stdout + process.stderr)
    need(process.returncode == 0, 'Worker failed: ' + path.name + '\n' + process.stderr)
    report = json.loads((path / 'RESULT.json').read_text())
    need(report['status'] == 'PASS_TERNARY_SMALL_CONTROLS', 'Incomplete worker receipt')
    return report, wall


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--pairs', type=int, default=3)
    args = parser.parse_args()
    pins = verify_sources()
    need(1 <= args.pairs <= 5, 'Use between one and five timing pairs')
    need(not args.out.exists(), 'Use a fresh output directory')
    args.out = args.out.resolve()
    args.out.mkdir(parents=True)
    controls = subprocess.run([sys.executable, '-B', str(HERE / 'test_package.py')],
                              cwd=ROOT, capture_output=True, text=True, timeout=300)
    controls_log = controls.stdout + controls.stderr
    (args.out / 'controls.log').write_text(controls_log)
    need(controls.returncode == 0, 'Semantic or admission control failed\n' + controls_log)
    print('PASS semantic and admission controls', flush=True)
    observed = {}
    for engine in ('reference', 'cached'):
        observed[engine], _ = run(engine, args.out / ('observed-' + engine), True)
        print('PASS complete observed replay:', engine, flush=True)
    need(observed['reference']['controls'] == observed['cached']['controls'],
         'Complete mathematical control receipts differ')
    trace_receipts = {}
    for h in (8, 9):
        payloads = []
        for engine in ('reference', 'cached'):
            with gzip.open(args.out / ('observed-' + engine) / ('trace-h%d.json.gz' % h)) as stream:
                payloads.append(json.load(stream))
        compare_traces(*payloads)
        trace_receipts[str(h)] = observed['reference']['trace'][str(h)]
    need(sum(x['physical_edges'] for x in trace_receipts.values()) == 84672,
         'Both complete historical domains required')
    timings = []
    for pair in range(args.pairs):
        order = ('reference', 'cached') if pair % 2 == 0 else ('cached', 'reference')
        for engine in order:
            report, wall = run(engine, args.out / ('pair-%d-%s' % (pair, engine)))
            need(report['controls'] == observed['reference']['controls'],
                 'Timed run changed a mathematical control')
            timings.append(dict(pair=pair, engine=engine, wall_seconds=wall,
                                frame_seconds=sum(x['frame_seconds'] for x in report['measurements']),
                                max_rss_bytes=report['max_rss_bytes'],
                                measurements=report['measurements']))
            print('PASS timed replay:', pair, engine, round(wall, 3), 'seconds', flush=True)
    verify_sources()
    medians = {engine: statistics.median(x['wall_seconds'] for x in timings if x['engine'] == engine)
               for engine in ('reference', 'cached')}
    result = dict(status='PASS_IDENTICAL_TERNARY_FRAME_REPLAY',
                  base_commit=pins['base_commit'], assignment_seed=93,
                  source_manifest_sha256=digest(pins),
                  implementation_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                         for p in sorted(HERE.glob('*.py'))},
                  control_exit_code=controls.returncode,
                  controls_log_sha256=hashlib.sha256(controls_log.encode()).hexdigest(),
                  historical_controls=observed['reference']['controls'],
                  complete_ordered_edge_transcripts=trace_receipts,
                  timings=timings, median_wall_seconds=medians,
                  ratio_of_medians=medians['reference'] / medians['cached'],
                  python=sys.version, platform=platform.platform(),
                  limits=['Historical h=8,9 small controls only; no h=29 DAG or assembly replay.',
                          'No selected frontier replay, new kappa, or all-size theorem proof.',
                          'Fresh interpreters; shared host; OS caches not flushed; no speed threshold.',
                          'Transcript equality includes full rational matrices; gzip bytes are not compared.'])
    (args.out / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'], '84672 edges;', round(result['ratio_of_medians'], 3), 'ratio of medians')


if __name__ == '__main__':
    main()
