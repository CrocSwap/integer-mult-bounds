#!/usr/bin/env python3
"""Complete PR3218 R2 replay with source-specific mutation-path copies.
Tekalign / OpenAI Codex, Apache-2.0. See NOTICE.md for retained-source credit.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import tempfile
import time
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PRIOR = 'research/clifford-pauli-anchor/'
VENDOR = 'research/r2-mutation-path-copy/vendor/pr3218/'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load(raw, name, path, extra=None):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    module.__dict__.update(extra or {})
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def capture(root=ROOT):
    retained = json.loads((PACKAGE / 'RETAINED.json').read_bytes())['files']
    source = json.loads((PACKAGE / 'SOURCES.json').read_bytes())['files']
    captured = {}
    for row in retained + [r for r in source if r['usage'] == 'input']:
        raw = (root / row['path']).read_bytes()
        need(digest(raw) == row['sha256'], 'source drift: ' + row['path'])
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        need(hashlib.sha1(blob, usedforsecurity=False).hexdigest() == row['git_blob'], 'source blob')
        need(row['path'] not in captured, 'duplicate captured path')
        captured[row['path']] = raw
    need(len(captured) == 40, 'complete source inventory')
    return captured


def run(mode='paths', differential=False):
    start = time.perf_counter()
    captured = capture()
    adapter_raw = (PACKAGE / 'adapter.py').read_bytes()
    A = load(adapter_raw, 'mutation_adapter', PACKAGE / 'adapter.py')
    H = A.Harness(mode, captured['research/r2-mutation-path-copy/vendor/pr1939/fast_copy.py'], differential)
    changed = A.transform_replay(captured[VENDOR + 'replay.py'])
    with tempfile.TemporaryDirectory(prefix='r2 mutation snapshot ') as directory:
        snapshot = Path(directory)
        for name, raw in captured.items():
            target = snapshot / (PRIOR + name[len(VENDOR):] if name.startswith(VENDOR) else name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        R = load(changed, 'retained_anchor_replay', snapshot / PRIOR / 'replay.py',
                 {'_harness': H, '_transform_audit': A.transform_audit})
        result = R.run('anchor')
        for tag, row in H.providers.items():
            need(row['mutants'] == result['reference_result']['providers'][tag]['rejected_controls'],
                 'original rejection inventory')
        need(H.current is None and set(H.providers) == {'base', 'extra'}, 'complete providers')
        for name, raw in captured.items():
            path = snapshot / (PRIOR + name[len(VENDOR):] if name.startswith(VENDOR) else name)
            need(path.read_bytes() == raw, 'snapshot file mutation')
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return {'mode': mode, 'differential': differential, 'reference_result': result['reference_result'],
            'reference_result_sha256': result['reference_result_sha256'],
            'call_multiset_sha256': result['call_multiset_sha256'], 'decisions': result['calls'],
            'providers': H.providers, 'copy_seconds': H.copy_seconds,
            'wall_seconds': time.perf_counter() - start,
            'peak_rss_bytes': peak if sys.platform == 'darwin' else peak * 1024,
            'marshal_stats': H.marshal_stats, 'adapter_sha256': digest(adapter_raw),
            'executed_replay_sha256': digest(changed),
            'executed_audit_sha256': result['executed_verifier_sha256'],
            'source_sha256': {p: digest(b) for p, b in sorted(captured.items())}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('paths', 'deepcopy', 'marshal'), default='paths')
    parser.add_argument('--differential', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    need(args.output is None or not args.output.exists(), 'fresh output required')
    result = run(args.mode, args.differential)
    if args.output:
        with args.output.open('x') as stream:
            json.dump(result, stream, sort_keys=True, indent=2)
            stream.write('\n')
    print('PASS_R2_MUTATION_COPY', args.mode, 'differential=' + str(args.differential),
          'mutants=32', 'wall_seconds=' + str(round(result['wall_seconds'], 3)))


if __name__ == '__main__':
    main()
