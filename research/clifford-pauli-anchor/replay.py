#!/usr/bin/env python3
"""Opt-in replay of the unchanged PR3202 audit with one comparator substitution.

Tekalign / OpenAI Codex, Apache-2.0. Original audit: 24kHandsome1201.
Packed kernel: Sagar Thakrar. Cached baseline: ywz65 and Charles Bethin.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import time
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ORIGINAL = 'research/pr3044-r2-native-slice/'
KERNEL = 'research/frontier1094-recipes-exact-seed76/clifford.py'
CACHED = 'research/packed-clifford-gate-tables/adapter.py'
TABLES = 'research/clifford-state-performance/fast_state.py'
VENDOR = 'research/clifford-pauli-anchor/vendor/pr3202/'


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def capture(root=ROOT):
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_bytes())
    found = {}
    for row in manifest['files'] + manifest['vendored_files']:
        path = row['path']
        if row['usage'] != 'input' and not path.startswith(VENDOR):
            continue
        raw = (root / path).read_bytes()
        need(digest(raw) == row['sha256'], 'source drift: ' + path)
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        need(hashlib.sha1(blob, usedforsecurity=False).hexdigest() == row['git_blob'], 'source blob')
        target = ORIGINAL + path[len(VENDOR):] if path.startswith(VENDOR) else path
        need(target not in found, 'duplicate snapshot destination')
        found[target] = raw
    need(len(found) == 25, 'complete snapshot inventory')
    return found


def module(raw, name, path):
    obj = types.ModuleType(name)
    obj.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), obj.__dict__)
    return obj


def run(mode='anchor'):
    need(mode in ('packed', 'cached', 'anchor'), 'engine mode')
    start = time.perf_counter()
    sources = capture()
    new_engine_raw = (PACKAGE / 'engine.py').read_bytes()
    new_engine = module(new_engine_raw, 'pauli_anchor_engine', PACKAGE / 'engine.py')
    cached = module(sources[CACHED], 'credited_cached_adapter', ROOT / CACHED)
    counts = {'calls': 0, 'accepted': 0, 'rejected': 0}
    call_inputs = []
    engine_seconds = 0.0
    def install(kernel):
        if mode == 'cached':
            p, d = cached.table_functions(sources[TABLES])
            kernel._permutation_table, kernel._phase_table = p, d
            exec(compile(cached.transform(sources[KERNEL]), KERNEL, 'exec'), kernel.__dict__)
        compare = new_engine.same_operator if mode == 'anchor' else kernel.same_operator
        def checked(a, b):
            nonlocal engine_seconds
            before = time.perf_counter()
            result = compare(a, b)
            engine_seconds += time.perf_counter() - before
            call_inputs.append(digest(canonical([a, b, result])))
            counts['calls'] += 1
            counts['accepted' if result else 'rejected'] += 1
            return result
        kernel.same_operator = checked
    with tempfile.TemporaryDirectory(prefix='pauli-anchor-') as directory:
        snapshot = Path(directory)
        for path, raw in sources.items():
            target = snapshot / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        raw = sources[ORIGINAL + 'verify.py']
        anchor = "    exec(compile(blobs[KERNEL], KERNEL, 'exec'), kernel.__dict__)"
        text = raw.decode()
        need(text.count(anchor) == 1, 'unique comparator installation anchor')
        changed = text.replace(anchor, anchor + '\n    _install_comparator(kernel)').encode()
        verifier = types.ModuleType('source_bound_r2_audit')
        verifier.__file__ = str(snapshot / ORIGINAL / 'verify.py')
        verifier._install_comparator = install
        exec(compile(changed, verifier.__file__, 'exec'), verifier.__dict__)
        result = verifier.compute(snapshot / ORIGINAL / 'data')
        expected = json.loads(sources[ORIGINAL + 'RESULT.json'])
        need(canonical(result) == canonical(expected), 'complete predecessor result mismatch')
        for path, raw in sources.items():
            need((snapshot / path).read_bytes() == raw, 'snapshot mutation')
    return {'mode': mode, 'reference_result': result, 'reference_result_sha256': digest(canonical(result)),
            'calls': counts, 'executed_verifier_sha256': digest(changed),
            'call_multiset_sha256': digest(canonical(sorted(call_inputs))),
            'anchor_engine_sha256': digest(new_engine_raw),
            'source_sha256': {p: digest(b) for p, b in sorted(sources.items())},
            'engine_seconds': engine_seconds, 'wall_seconds': time.perf_counter() - start,
            'reference_kernel_field': 'The unchanged nested result names the loaded source kernel; execution mode and comparator source are recorded separately here.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mode', choices=('packed', 'cached', 'anchor'), default='anchor')
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    need(args.output is None or not args.output.exists(), 'output already exists')
    result = run(args.mode)
    if args.output:
        with args.output.open('x') as f:
            json.dump(result, f, sort_keys=True, indent=2)
            f.write('\n')
    print('PASS_R2_EXACT_COMPARATOR', args.mode, 'calls=' + str(result['calls']),
          'wall_seconds=' + str(round(result['wall_seconds'], 3)))


if __name__ == '__main__':
    main()
