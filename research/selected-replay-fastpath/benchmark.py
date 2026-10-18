#!/usr/bin/env python3
"""Measure complete U8 phase commands and require exact recipe equality."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tarfile
import tempfile
import time

from sources import HERE, ROOT, SOURCE, verify_sources


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_sources():
    return {p.name: digest(p) for p in HERE.iterdir()
            if p.is_file() and (p.suffix == '.py' or p.name == 'SOURCES.json')}


def proof_review(data):
    value = json.loads(data)
    del value['seconds']
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def measure(command, log, env):
    start = time.perf_counter()
    with log.open('wb') as stream:
        process = subprocess.Popen(command, cwd=ROOT, env=env,
                                   stdout=stream, stderr=subprocess.STDOUT)
        pid, status, usage = os.wait4(process.pid, 0)
        process.returncode = os.waitstatus_to_exitcode(status)
    elapsed = time.perf_counter() - start
    if process.returncode:
        raise RuntimeError(log.read_text())
    return dict(wall_seconds=elapsed, user_seconds=usage.ru_utime,
                system_seconds=usage.ru_stime,
                peak_rss_bytes=usage.ru_maxrss * (1 if sys.platform == 'darwin' else 1024),
                exit_code=process.returncode, log_sha256=digest(log))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pairs', type=int, default=3)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.pairs < 1 or args.out.exists():
        raise ValueError('Use a positive pair count and a fresh output file')
    if not hasattr(os, 'wait4'):
        raise RuntimeError('This memory benchmark requires POSIX wait4')
    verify_sources()
    frozen = package_sources()
    with tarfile.open(ROOT / SOURCE['archive']) as archive:
        word = archive.extractfile(SOURCE['word_member']).read()
        recipes = archive.extractfile(SOURCE['recipes_member']).read()
        review = proof_review(archive.extractfile(SOURCE['review_member']).read())
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
               MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
    for key in ('PYTHONOPTIMIZE', 'PYTHONPATH'):
        env.pop(key, None)
    records = []
    with tempfile.TemporaryDirectory(prefix='selected-phase-benchmark-') as temporary:
        work = Path(temporary)
        input_path = work / 'CANONICAL-WORD.json.gz'
        input_path.write_bytes(word)
        for pair in range(args.pairs):
            order = ('original', 'dense', 'sparse') if pair % 2 == 0 else (
                'sparse', 'dense', 'original')
            for engine in order:
                output = work / f'{pair}-{engine}'
                if engine == 'original':
                    output.mkdir()
                    (output / input_path.name).write_bytes(word)
                    command = [sys.executable, '-B', str(ROOT / SOURCE['original_driver']),
                               str(output), str((ROOT / SOURCE['algebra']).parent)]
                else:
                    command = [sys.executable, '-B', str(HERE / 'run.py'), '--engine', engine,
                               '--word', str(input_path), '--out', str(output)]
                record = measure(command, work / f'{pair}-{engine}.log', env)
                actual = (output / 'CLIFFORD-RECIPES.json').read_bytes()
                if actual != recipes:
                    raise AssertionError('Complete recipe bytes differ: ' + engine)
                if proof_review((output / 'CLIFFORD-REVIEW.json').read_bytes()) != review:
                    raise AssertionError('Proof-relevant review fields differ: ' + engine)
                if input_path.read_bytes() != word:
                    raise AssertionError('Input changed during benchmark')
                record.update(pair=pair, engine=engine, command=command,
                              recipe_sha256=hashlib.sha256(actual).hexdigest())
                records.append(record)
                print(engine, round(record['wall_seconds'], 3),
                      record['peak_rss_bytes'], flush=True)
    verify_sources()
    if frozen != package_sources():
        raise AssertionError('Package changed during benchmark')
    summary = {engine: {
        'median_wall_seconds': statistics.median(r['wall_seconds'] for r in records
                                               if r['engine'] == engine),
        'max_peak_rss_bytes': max(r['peak_rss_bytes'] for r in records
                                 if r['engine'] == engine),
    } for engine in ('original', 'dense', 'sparse')}
    result = dict(status='PASS_COMPLETE_U8_PHASE_RECIPES_IDENTICAL',
                  python=sys.version, executable=sys.executable, platform=platform.platform(),
                  machine=platform.machine(), source_files=SOURCE['files'],
                  package_sha256=frozen, word_sha256=hashlib.sha256(word).hexdigest(),
                  recipe_sha256=hashlib.sha256(recipes).hexdigest(),
                  scope='Complete archived U8 phase compilation; not a cold supplier replay.',
                  concurrency='One process at a time in this lane. Other sprint lanes share the host.',
                  caches='Fresh Python process per command. OS caches are not flushed.',
                  summary=summary, runs=records)
    with args.out.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(result['status'])


if __name__ == '__main__':
    main()
