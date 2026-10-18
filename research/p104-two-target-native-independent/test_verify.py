#!/usr/bin/env python3
"""Behavioral checks of source binding, fixed evidence and phase sensitivity.

Ross Richardson with OpenAI Codex assistance. Apache-2.0.
"""
import gzip
import hashlib
import importlib._bootstrap_external
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
_loader_path = HERE / 'source_exec.py'
_loader = {'__file__': str(_loader_path)}
exec(compile(_loader_path.read_bytes(), str(_loader_path), 'exec'), _loader)


def need(ok, why):
    if not ok:
        raise ValueError(why)


def snapshot(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def seed_cache(path, extra, mode):
    """Create a loadable CPython cache while leaving its source bytes unchanged."""
    source, stat = path.read_bytes(), path.stat()
    code = compile(source + extra, str(path), 'exec', optimize=1)
    if mode == 'timestamp':
        data = importlib._bootstrap_external._code_to_timestamp_pyc(
            code, int(stat.st_mtime), stat.st_size)
    else:
        need(mode == 'unchecked_hash', 'known cache format')
        data = importlib._bootstrap_external._code_to_hash_pyc(
            code, importlib.util.source_hash(source), checked=False)
    cache = Path(importlib.util.cache_from_source(str(path), optimization=1))
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(data)


def cache_controls(root, package, run):
    """Preserve valid replay and reject a phase fault despite runnable bad caches."""
    base = root / 'research/p104-native-channel'
    bad_phase_predicate = b'''\n# Prior review witness: signed Paulis survive, rank-seven exact phase does not.
def equal(actual, expected, label):
    require(tableau(actual) == tableau(expected), label + ': signed Pauli action')
    if sum(gate[0] == 'C' for gate in actual) != 7:
        require(state(actual) == state(expected), label + ': exact global phase')
print('UNAUTHENTICATED_CACHE_EXECUTED')
'''
    forbidden_cache = b"\nraise ValueError('UNAUTHENTICATED_CACHE_EXECUTED')\n"
    native_path, receipt_path = package / 'NATIVE.json.gz', package / 'RESULT.json'
    native_bytes, receipt_bytes = native_path.read_bytes(), receipt_path.read_bytes()
    for mode in ('timestamp', 'unchecked_hash'):
        for path in (package / 'source_exec.py', package / 'check.py',
                     base / 'check_native.py', base / 'vendor/clifford_exact.py'):
            seed_cache(path, forbidden_cache, mode)
        interpreter = base / 'vendor/native_verify.py'
        seed_cache(interpreter, bad_phase_predicate, mode)
        # Establish that the seeded cache is executable under the actual flags;
        # a malformed/inapplicable cache would be a vacuous positive control.
        probe = ('import importlib.util; '
                 's=importlib.util.spec_from_file_location("cache_probe",' + repr(str(interpreter)) + '); '
                 'm=importlib.util.module_from_spec(s); s.loader.exec_module(m)')
        result = subprocess.run([sys.executable, '-I', '-O', '-B', '-c', probe],
                                text=True, capture_output=True, timeout=30)
        need(result.returncode == 0 and 'UNAUTHENTICATED_CACHE_EXECUTED' in result.stdout,
             mode + ' seeded cache was not executable')
        before = snapshot(root)
        result = run(['--regenerate'])
        need(result.returncode == 0 and 'PASS_P104_TWO_TARGET_NATIVE no_new_kappa' in result.stdout,
             mode + ' valid cached replay failed: ' + result.stderr[-2000:])
        need('UNAUTHENTICATED_CACHE_EXECUTED' not in result.stdout + result.stderr,
             mode + ' replay executed unauthenticated bytecode')
        need(snapshot(root) == before, mode + ' replay changed input files or caches')

        certificate = json.loads(gzip.decompress(native_bytes))
        index = next(i for i, edge in enumerate(certificate['transports']) if edge['rank'] == 7)
        need(index != 0, 'phase witness differs from the first-edge semantic controls')
        phase = certificate['transports'][index]['forward']['left']
        phase['phase'] = (phase['phase'] + 1) % 4
        raw = (json.dumps(certificate, sort_keys=True, indent=2) + '\n').encode()
        native_path.write_bytes(gzip.compress(raw, mtime=0))
        receipt = json.loads(receipt_bytes)
        receipt['certificate_raw_sha256'] = hashlib.sha256(raw).hexdigest()
        receipt_path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
        try:
            result = run()
            need(result.returncode != 0 and 'added forward edge: exact global phase' in result.stderr,
                 mode + ' wrong-phase recipe did not reject at the exact phase predicate')
            need('UNAUTHENTICATED_CACHE_EXECUTED' not in result.stdout + result.stderr,
                 mode + ' phase rejection executed unauthenticated bytecode')
        finally:
            native_path.write_bytes(native_bytes)
            receipt_path.write_bytes(receipt_bytes)
        print('PASS ' + mode + ' caches ignored; valid regeneration accepts; wrong phase rejects')


def main():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    with tempfile.TemporaryDirectory(prefix='p104-native-tests-') as temporary:
        root = Path(temporary)
        package = root / HERE.relative_to(ROOT)
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        for source in sources['files']:
            if source['usage'] == 'input':
                path = root / source['path']
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / source['path'], path)
        command = [sys.executable, '-I', '-O', '-B', str(package / 'verify.py')]

        def run(extra=()):
            return subprocess.run(command + list(extra), cwd=root, text=True,
                                  capture_output=True, timeout=600)

        for name in ('NATIVE.json.gz', 'RESULT.json', 'inputs/CIRCUIT.json'):
            path = package / name
            original = path.read_bytes()
            path.unlink()
            result = run()
            need(result.returncode != 0 and not path.exists(), 'missing evidence regenerated: '+name)
            path.write_bytes(original)
        print('PASS missing fixed evidence fails without regeneration')

        source_path = root / next(s['path'] for s in sources['files'] if s['usage'] == 'input')
        original = source_path.read_bytes()
        source_path.write_bytes(original + b'\n')
        result = run()
        need(result.returncode != 0 and 'input pin mismatch' in result.stderr, 'source drift accepted')
        source_path.write_bytes(original)
        print('PASS immutable source drift rejects')

        path = package / 'RESULT.json'
        original = path.read_bytes()
        path.write_text('{invalid json')
        need(run().returncode != 0, 'malformed receipt accepted')
        path.write_bytes(original)
        destination = root / 'occupied.json'
        destination.write_text('keep this exact text')
        result = run(['--out', str(destination)])
        need(result.returncode != 0 and destination.read_text() == 'keep this exact text',
             'exclusive output damaged existing data')
        destination.unlink()
        print('PASS malformed receipt and occupied output reject')

        # The exact mathematical payload survives a changed gzip timestamp.
        path = package / 'NATIVE.json.gz'
        raw = gzip.decompress(path.read_bytes())
        path.write_bytes(gzip.compress(raw, mtime=123456789))
        before = snapshot(root)
        for p in root.rglob('*'):
            if p.is_file():
                p.chmod(0o444)
        result = run()
        need(result.returncode == 0, 'Git-free read-only recompressed replay failed: '+result.stderr[-2000:])
        need(snapshot(root) == before, 'read-only replay changed files')
        for p in root.rglob('*'):
            if p.is_file():
                p.chmod(0o644)
        print('PASS Git-free read-only replay and equivalent gzip payload')
        cache_controls(root, package, run)

    # Deliberately remove only the phase predicate, leaving every signed Pauli
    # comparison intact. A phase fault must become an unexpected acceptance,
    # so the control suite itself must fail. This changes no source file.
    check = _loader['load_source']('phase_sensitivity_audit', HERE / 'check.py')
    certificate = json.loads(gzip.decompress((HERE / 'NATIVE.json.gz').read_bytes()))
    circuit = json.loads((HERE / 'inputs/CIRCUIT.json').read_text())
    old_equal = check.N.equal

    def tableau_only(actual, expected, label):
        check.N.require(check.N.tableau(actual) == check.N.tableau(expected),
                        label + ': signed Pauli action')

    check.N.equal = tableau_only
    try:
        try:
            check.run_controls(certificate, circuit)
        except ValueError as error:
            need('phase' in str(error).lower() and
                 ('accept' in str(error).lower() or 'reject' in str(error).lower()),
                 'phase-deletion control failed for unrelated reason: '+str(error))
        else:
            raise ValueError('phase controls stayed green after deleting exact phase predicate')
    finally:
        check.N.equal = old_equal
    print('PASS phase-predicate deletion makes controls fail')
    print('PASS_P104_TWO_TARGET_NATIVE_BEHAVIOR groups=8 cache_modes=2')


if __name__ == '__main__':
    main()
