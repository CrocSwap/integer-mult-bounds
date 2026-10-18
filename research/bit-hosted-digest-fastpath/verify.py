"""Bounded differential replay; stdlib only. Matthieu Pascal / Codex, Apache-2.0."""
import argparse
import contextlib
import copy
import gzip
import hashlib
import io
import json
from pathlib import Path
import platform
import random
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fast_digest import (FIXTURE, PACKAGE, ROOT, checked_bytes, digest,
                         instruction_chunks, load_auditor, pins)


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def reference_bytes(t):
    # Literal mapped-array format from the historical specification, without
    # using the fast fragment builder. Baseline digest separately corroborates.
    rows = []
    limit = len(t['calls'][0]['owners'])
    for call in t['calls']:
        for z in t['local_programs'][call['orientation']]:
            x = [z[0], call['owners'][z[1]]]
            if z[0] == 0:
                x.extend(z[2:])
            else:
                x.append(call['owners'][z[2]] if z[2] < limit else [t['live'], ['private', 0]])
                x.extend(z[3:])
            rows.append(json.dumps(x, separators=(',', ':')).encode() + b'\n')
    return b''.join(rows), len(rows)


def fragment_controls(baseline, work):
    rng = random.Random(91)
    values = [None, True, False, 0, -7, 10**80, 0.0, -0.0, 1e-50,
              'quote" slash\\ newline\n unicode\u03ba', {'nested': [1, None, '\u00e9']}]
    checked = 0
    for _ in range(40):
        t = {'live': rng.randrange(100), 'calls': [], 'local_programs': {}}
        for name in ('forward', 'reverse'):
            t['local_programs'][name] = [
                [op, rng.randrange(4)] + ([] if op == 0 else [rng.randrange(7)])
                + [copy.deepcopy(rng.choice(values)) for _ in range(rng.randrange(5))]
                for op in (0, 1, 2, 0, 2, 1)]
        for name in ('forward', 'reverse', 'forward'):
            t['calls'].append({'orientation': name,
                              'owners': [[rng.randrange(10), copy.deepcopy(rng.choice(values))]
                                         for _ in range(4)]})
        expected, count = reference_bytes(t)
        expected_digest = hashlib.sha256(expected).hexdigest(), count
        require(baseline(t) == expected_digest, 'reference disagrees with pinned digest')
        for chunk_size in (1, 37, 1024 * 1024):
            pieces = list(instruction_chunks(t, chunk_size))
            require(b''.join(b for b, _ in pieces) == expected, 'JSON bytes changed')
            require(sum(n for _, n in pieces) == count, 'instruction count changed')
            checked += 1
        require(digest(t) == expected_digest, 'digest differs')
    t = {'live': 99, 'calls': [{'orientation': 'forward', 'owners': [[0, ['data', 1]], [1, ['hosted', 2]]]}],
         'local_programs': {'forward': [[0, 0, 17], [1, 1, 0, 23], [2, 0, 2, 31]]}}
    original = digest(t)
    mutations = {
        'destination owner': lambda q: q['calls'][0]['owners'][0].__setitem__(0, 8),
        'source owner metadata': lambda q: q['calls'][0]['owners'][0][1].__setitem__(1, 9),
        'source owner index': lambda q: q['local_programs']['forward'][1].__setitem__(2, 1),
        'private owner/live stock': lambda q: q.__setitem__('live', 100),
        'operation tail': lambda q: q['local_programs']['forward'][0].__setitem__(2, 19),
        'operation opcode': lambda q: q['local_programs']['forward'][1].__setitem__(0, 2),
        'operation order': lambda q: q['local_programs']['forward'].reverse(),
        'private source boundary': lambda q: q['local_programs']['forward'][2].__setitem__(2, 1),
        'omitted event': lambda q: q['local_programs']['forward'].pop(),
        'duplicated call': lambda q: q['calls'].append(copy.deepcopy(q['calls'][0])),
    }
    for name, mutate in mutations.items():
        q = copy.deepcopy(t)
        mutate(q)
        require(digest(q) == baseline(q), f'{name}: differential mismatch')
        require(digest(q) != original, f'{name}: stale output reused')
        require(digest(t) == original, f'{name}: cache leaked between calls')
    q = copy.deepcopy(t)
    q['local_programs']['forward'][1][2] = None
    for function in (baseline, digest):
        try:
            function(q)
        except TypeError:
            pass
        else:
            raise AssertionError('null source index accepted')
    candidate = work / 'changed-source.py'
    candidate.write_bytes(b'changed source')
    try:
        checked_bytes(candidate, hashlib.sha256(b'original source').hexdigest())
    except ValueError:
        pass
    else:
        raise AssertionError('changed source accepted')
    optimized = subprocess.run([sys.executable, '-O', '-B', str(PACKAGE / 'fast_digest.py')],
                               capture_output=True, text=True)
    require(optimized.returncode != 0 and 'requires assertions' in optimized.stderr,
            'assertion-disabled auditor accepted')
    return {'byte_comparisons': checked, 'changed_input_controls': list(mutations),
            'source_pin_rejected': True, 'null_source_index_rejected': True,
            'disabled_assertions_rejected': True}


def run_audit(auditor, function, parent, hosted, output):
    auditor.digest = function
    argv = sys.argv
    try:
        sys.argv = [auditor.__file__, str(parent), str(hosted), str(output)]
        start = time.perf_counter()
        with contextlib.redirect_stdout(io.StringIO()):
            auditor.main()
        elapsed = time.perf_counter() - start
    finally:
        sys.argv = argv
    return json.loads(output.read_text(encoding='utf-8')), elapsed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, help='optional measurement JSON outside frozen evidence')
    args = parser.parse_args()
    for path, sha in pins().items():
        checked_bytes(ROOT / path, sha)
    auditor = load_auditor()
    baseline = auditor.digest
    source = ROOT / FIXTURE
    auditor.V = json.loads((source / 'v9/nine/GLOBAL.json').read_text(encoding='utf-8'))['v']
    with tempfile.TemporaryDirectory(prefix='bit-hosted-digest-') as tmp:
        work = Path(tmp)
        # Restore the old replay's relative records layout without symlinks or
        # writes to the retained fixture. Only these two small files are copied.
        parent = work / 'parent'
        shutil.copytree(source / 'v9/nine', parent / 'nine',
                        ignore=shutil.ignore_patterns('AUDIT.json', 'GEOMETRY.json'))
        shutil.copytree(source / 'records', parent / 'records')
        controls = fragment_controls(baseline, work)
        template = json.loads(gzip.decompress((source / 'v9/hosted/GLOBAL-TEMPLATE.json.gz').read_bytes()))
        start = time.perf_counter()
        old_digest = baseline(template)
        old_seconds = time.perf_counter() - start
        start = time.perf_counter()
        new_digest = digest(template)
        new_seconds = time.perf_counter() - start
        require(new_digest == old_digest, 'full instruction digest changed')
        old, old_audit = run_audit(auditor, baseline, parent, source / 'v9/hosted', work / 'baseline.json')
        new, new_audit = run_audit(auditor, digest, parent, source / 'v9/hosted', work / 'fast.json')
        retained = json.loads((source / 'v9/hosted/AUDIT.json').read_text(encoding='utf-8'))
        require(old == new == retained, 'full hosted audit differs from retained receipt')
        require((work / 'baseline.json').read_bytes() == (work / 'fast.json').read_bytes(),
                'audit JSON output bytes differ')
        require(len(new['mutations_rejected']) == 16, 'inherited mutation coverage changed')
        result = {'status': 'PASS_EXACT_HOSTED_DIGEST_FASTPATH',
                  'python': platform.python_version(), 'platform': platform.platform(),
                  'fixture': FIXTURE + '/v9/hosted', 'base_commit':
                  json.loads((PACKAGE / 'SOURCES.json').read_text(encoding='utf-8'))['base_commit'],
                  'emitted_program_sha256': new_digest[0], 'emitted_events': new_digest[1],
                  'digest_seconds': {'baseline': old_seconds, 'fast': new_seconds,
                                     'speedup': old_seconds / new_seconds},
                  'full_audit_seconds': {'baseline': old_audit, 'fast': new_audit,
                                         'speedup': old_audit / new_audit},
                  'receipt_bytes_identical': True, 'inherited_mutations_rejected': new['mutations_rejected'],
                  'controls': controls,
                  'scope': 'retained nine-stage PR589 hosted audit only; no cold replay or new kappa'}
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
