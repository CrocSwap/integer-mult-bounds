#!/usr/bin/env python3
"""Compare complete routing receipts and fresh-process timings at a pinned base.

Standard-library Python 3.11+ and Git; run from any directory in a full clone.
Python allocation peaks are measured separately, never in the timed samples.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
import tracemalloc
import types

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SCRIPT = 'scripts/audit_cyclic_topology.py'
CERTIFICATE = 'certificates/cyclic-topology-audit.json'


def canonical(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def git_file(base, name):
    return subprocess.check_output(['git', 'show', base + ':' + name], cwd=ROOT)


def child(mode, memory):
    pins = json.loads((HERE / 'SOURCE.json').read_text(encoding='utf-8'))
    original = git_file(pins['base_commit'], SCRIPT)
    frozen = git_file(pins['base_commit'], CERTIFICATE)
    for name, content in ((SCRIPT, original), (CERTIFICATE, frozen)):
        if sha256(content).hexdigest() != pins['base_sha256'][name]:
            raise ValueError('Changed reference: ' + name)
    for name, expected in pins['dependencies_sha256'].items():
        if sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Changed dependency: ' + name)
    current = (ROOT / SCRIPT).read_bytes()
    module = types.ModuleType('routing_benchmark_subject')
    module.__file__ = str(ROOT / SCRIPT)
    sys.path.insert(0, str(ROOT / 'scripts'))
    exec(compile(original if mode == 'before' else current, module.__file__, 'exec'),
         module.__dict__)
    if memory:
        tracemalloc.start()
    wall, cpu = time.perf_counter(), time.process_time()
    receipt = module.certificate()
    wall, cpu = time.perf_counter() - wall, time.process_time() - cpu
    peak = tracemalloc.get_traced_memory()[1] if memory else None
    if memory:
        tracemalloc.stop()
    normalized = json.loads(json.dumps(receipt))
    normalized['source_sha256'][SCRIPT] = pins['base_sha256'][SCRIPT]
    if normalized != json.loads(frozen):
        raise ValueError('Complete historical receipt differs (beyond the source binding)')
    imports = {Path(m.__file__).resolve() for m in list(sys.modules.values())
               if getattr(m, '__file__', None) and
               Path(m.__file__).resolve().is_relative_to(ROOT / 'scripts')}
    if not {p.relative_to(ROOT).as_posix() for p in imports} <= set(pins['dependencies_sha256']):
        raise ValueError('An imported dependency is missing from SOURCE.json')
    print(json.dumps(dict(mode=mode, audit_wall_seconds=wall, audit_cpu_seconds=cpu,
                         python_allocation_peak_bytes=peak,
                         receipt_sha256=sha256(canonical(receipt)).hexdigest(),
                         normalized_receipt_sha256=sha256(canonical(normalized)).hexdigest(),
                         current_source_sha256=sha256(current).hexdigest())))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pairs', type=int, default=7)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--child', choices=('before', 'after'), help=argparse.SUPPRESS)
    parser.add_argument('--memory', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.child:
        child(args.child, args.memory)
        return
    if args.pairs < 1 or args.out is None or args.out.exists():
        parser.error('Use positive --pairs and a fresh --out file')
    env = dict(os.environ, PYTHONHASHSEED='0', PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONOPTIMIZE', None)
    samples = []
    for pair in range(args.pairs):
        for mode in (('before', 'after') if pair % 2 == 0 else ('after', 'before')):
            start = time.perf_counter()
            process = subprocess.run([sys.executable, '-I', '-B', str(Path(__file__).resolve()),
                                      '--child', mode], cwd=ROOT, env=env,
                                     capture_output=True, text=True, check=True)
            sample = json.loads(process.stdout)
            sample.update(pair=pair, process_wall_seconds=time.perf_counter() - start)
            samples.append(sample)
            print(mode, pair + 1, f"{sample['process_wall_seconds']:.6f}s", flush=True)
    memory = []
    for mode in ('before', 'after'):
        process = subprocess.run([sys.executable, '-I', '-B', str(Path(__file__).resolve()),
                                  '--child', mode, '--memory'], cwd=ROOT, env=env,
                                 capture_output=True, text=True, check=True)
        memory.append(json.loads(process.stdout))
        print(mode, 'Python allocation peak', memory[-1]['python_allocation_peak_bytes'], flush=True)
    all_samples = samples + memory
    for key in ('receipt_sha256', 'normalized_receipt_sha256', 'current_source_sha256'):
        if len({sample[key] for sample in all_samples}) != 1:
            raise ValueError('Inconsistent full receipts or source: ' + key)
    summary = {mode: {metric: statistics.median(s[metric] for s in samples if s['mode'] == mode)
                     for metric in ('process_wall_seconds', 'audit_wall_seconds', 'audit_cpu_seconds')}
               for mode in ('before', 'after')}
    result = dict(status='PASS_IDENTICAL_COMPLETE_ROUTING_RECEIPTS',
                  measured_utc=datetime.now(timezone.utc).isoformat(),
                  python=sys.version, platform=platform.platform(), machine=platform.machine(),
                  processor=platform.processor(), logical_cpus=os.cpu_count(),
                  git=subprocess.check_output(['git', '--version'], text=True).strip(),
                  pins=json.loads((HERE / 'SOURCE.json').read_text(encoding='utf-8')),
                  benchmark_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  samples=samples, separate_memory_samples=memory, medians=summary,
                  process_wall_speedup=summary['before']['process_wall_seconds'] /
                                       summary['after']['process_wall_seconds'],
                  scope='Complete historical certificate only; no selected-frontier or multiplication runtime claim. '
                        'Sequential alternating fresh processes; OS caches not flushed. Allocation peaks use '
                        'tracemalloc in separate untimed processes and are not RSS.')
    with args.out.open('x', encoding='utf-8', newline='\n') as output:
        output.write(canonical(result).decode())
    print(result['status'])


if __name__ == '__main__':
    main()
