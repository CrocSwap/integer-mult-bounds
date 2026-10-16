#!/usr/bin/env python3
"""Run the pinned Windows successor and complete composed output comparison.

ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import compare_logs as comparison
from compare_logs import require


def successor_module():
    module = comparison.load('pinned_windows_successor', 'vendor/pr2336/verify.py')
    # Bind repository constants explicitly for the deeper vendored location.
    module.ROOT = ROOT
    module.PACKAGE = ROOT / 'research/complex-t16-rare-pattern-exchanges'
    module.A1042 = ROOT / 'research/community-frontier1042-audit'
    module.A1094 = ROOT / 'research/community-frontier1094-audit'
    return module


def authenticate():
    comparison.authenticate_vendors()
    for row in json.loads((HERE / 'SOURCES.json').read_bytes())['files']:
        if row['usage'] == 'input':
            raw = (ROOT / row['path']).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == row['sha256'],
                    'immutable input changed: ' + row['path'])
    module = successor_module()
    module.authenticate()
    return module


def context(work, local, external, style='posix'):
    return {'work': {'style': style, 'path': work},
            'local': {'style': style, 'path': local}, 'external': external}


def fixtures(work, module):
    module.extract(module.A1042 / 'selected-replay.tar.gz', work / 'in1042', 'slots/local/')
    local = work / 'in1042/slots/local'
    receipt = module.read_json(module.A1042 / 'RESULT.json')
    bound = {name: value for name, value in receipt['artifacts'].items()
             if name.startswith('slots/local/')}
    require(len(bound) == 10 and set(bound) == {'slots/local/' + p.name for p in local.iterdir()},
            'archived local input inventory differs')
    for name, digest in bound.items():
        require(module.sha((work / 'in1042' / name).read_bytes()) == digest,
                'archived local input changed: ' + name)
    module.extract(module.A1094 / 'selected-replay.tar.gz', work / 'reference')
    reference = work / 'reference/candidate/strict'
    for name in ('RESULT.json', 'STAGES.json'):
        require((work / 'reference' / name).read_bytes() == (module.A1094 / name).read_bytes(),
                'archived reference receipt changed')
    for name in ('REPLAY.json', 'ASSEMBLY.json'):
        require((reference / name).read_bytes() == (module.A1094 / name).read_bytes(),
                'archived reference result changed')
    selected = module.read_json(module.A1094 / 'RESULT.json')
    require(selected['baseline_receipt_sha256'] == module.sha((module.A1042 / 'RESULT.json').read_bytes()),
            'wrong baseline reference')
    stage = [row for row in selected['stages'] if row['name'] == 'rare-pattern-exchanges']
    require(len(stage) == 1 and stage[0]['script_sha256'] ==
            module.sha((module.PACKAGE / 'verify.py').read_bytes()), 'wrong selected entry point')
    external = {'local-word': (local / 'CANONICAL-WORD.json.gz').read_bytes(),
                'local-replay': (local / 'INDEPENDENT-LOCAL-REPLAY.json').read_bytes(),
                'owners': (module.PACKAGE / 'data/OWNERS.json.gz').read_bytes()}
    ref_context = context('/private/tmp/batch1099-selected/candidate',
                          '/private/tmp/batch1047-selected/slots/local', external)
    return reference, local, external, ref_context


def run(work, controls=True):
    module = authenticate()
    reference, local, external, ref_context = fixtures(work, module)
    out = work / 'run'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONOPTIMIZE', None)
    log = work / 'successor.log'
    start = time.monotonic()
    with log.open('wb') as stream:
        result = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'verify.py'),
                                 '--stage', '--local', str(local), '--work', str(out)],
                                cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT,
                                timeout=300)
    require(result.returncode == 0, 'successor failed: ' + log.read_text(encoding='utf-8', errors='replace')[-5000:])
    candidate_context = context(str(out), str(local), external,
                                'windows-drive' if os.name == 'nt' else 'posix')
    left = comparison.closed.read_files(reference)
    right = comparison.closed.read_files(out / 'strict')
    ref_outer = (work / 'reference/rare-pattern-exchanges.log').read_bytes()
    run_outer = log.read_bytes()
    verdict = comparison.compare(left, right, ref_context, candidate_context, ref_outer, run_outer)
    require(verdict['equivalent'], 'complete fresh replay differs: ' + json.dumps(verdict))
    result = {'status': 'PASS_SELECTED_WINDOWS_LOG_CLOSURE', 'checked_files': verdict['checked_files'],
              'authenticated_raw_edges_per_side': verdict['authenticated_raw_edges_per_side'],
              'inner_logs': len(comparison.closed.STAGES),
              'raw_file_differences': sum(left[name] != right[name] for name in left),
              'native_stage_seconds': round(time.monotonic() - start, 3),
              'python': sys.version, 'platform': platform.platform(),
              'scope': 'Selected final stage with authenticated archived local inputs; not cold ancestry'}
    if controls:
        import test_controls
        result['controls'] = test_controls.exercise(left, right, ref_context, candidate_context,
                                                    ref_outer, run_outer)
        require(result['controls'] == json.loads((HERE / 'CONTROLS.json').read_bytes()),
                'control receipt differs')
    else:
        result['status'] = 'DIAGNOSTIC_NATIVE_COMPARISON_ONLY_CONTROLS_NOT_RUN'
    authenticate()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--local', type=Path)
    parser.add_argument('--work', type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--skip-controls', action='store_true', help='diagnostic only, not registered acceptance')
    args = parser.parse_args()
    if args.stage:
        require(args.local is not None and args.work is not None, 'stage paths required')
        module = authenticate()
        code = module.successor((module.PACKAGE / 'verify.py').read_bytes())
        sys.argv = [str(module.PACKAGE / 'verify.py'), '--main', str(ROOT),
                    '--local', str(args.local), '--work', str(args.work)]
        exec(code, {'__name__': '__main__', '__file__': str(module.PACKAGE / 'verify.py')})
        return
    if args.work:
        require(not args.work.exists(), 'use a fresh work directory')
        args.work.mkdir(parents=True)
        result = run(args.work.resolve(), not args.skip_controls)
    else:
        with tempfile.TemporaryDirectory(prefix='selected-log-closure-') as directory:
            result = run(Path(directory).resolve(), not args.skip_controls)
    if args.report:
        args.report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
