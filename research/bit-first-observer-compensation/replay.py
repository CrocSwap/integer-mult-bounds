"""Reconstruct and independently check the fixed first-read BIT bound offline."""
from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
from tempfile import TemporaryDirectory

PACKAGE = Path(__file__).resolve().parent
GENERATED = ('round22', 'round23', 'round24', 'bit-price', 'round25')
NATIVE = 'research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz'
SCRIPTS = frozenset({'SOURCES.tsv', 'verify.py', 'audit.py'})
RECORDS = frozenset({'SUMMARY.json', 'AUDIT.json'})


def safe_key(value):
    key = PurePosixPath(value)
    if not key.parts or key.is_absolute() or '..' in key.parts or key.as_posix() != value:
        raise ValueError(f'Invalid replay path: {value}')
    return key


def stage(root):
    manifest = {}
    for line in (PACKAGE / 'REPLAY.sha256').read_text(encoding='ascii').splitlines():
        digest, value = line.split('  ', 1)
        key = safe_key(value)
        if key in manifest:
            raise ValueError(f'Duplicate replay path: {value}')
        manifest[key] = digest
    for key, digest in manifest.items():
        category, *subpath = key.parts
        source = PACKAGE / key
        data = source.read_bytes()
        if sha256(data).hexdigest() != digest:
            raise ValueError(f'SHA-256 mismatch: {key}')
        if category in ('inputs', 'predecessor') and subpath:
            destination = root.joinpath('inputs', *subpath)
        elif key.as_posix() in SCRIPTS:
            destination = root / key
        elif key.as_posix() in RECORDS:
            continue
        else:
            raise ValueError(f'Unexpected replay path: {key}')
        if destination.exists():
            raise ValueError(f'Duplicate staged path: {destination.relative_to(root)}')
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    if {p.as_posix() for p in manifest if len(p.parts)==1} != SCRIPTS | RECORDS:
        raise ValueError('Missing script, source list or record in replay manifest')
    dependencies = {}
    for line in (root / 'SOURCES.tsv').read_text(encoding='utf-8').splitlines():
        key,digest,_ = line.split('\t')
        safe_key(key)
        if key in dependencies:
            raise ValueError(f'Duplicate source path: {key}')
        dependencies[key] = digest
    return dependencies


def invoke(script, *args):
    return subprocess.run([sys.executable, '-I', '-B', str(script), *map(str, args)],
                          capture_output=True, check=False)


def successful(script, *args):
    proc = invoke(script, *args)
    if proc.returncode or proc.stderr:
        sys.stderr.buffer.write(proc.stderr)
        raise ValueError(f'{script.name} failed with exit {proc.returncode}')
    return proc.stdout


def negative(script, marker, *args):
    proc = invoke(script, *args)
    if proc.returncode != 1 or proc.stdout or marker not in proc.stderr:
        raise ValueError(f'Negative control did not reject: {marker.decode()}')


def controls(root, result):
    inputs = root / 'inputs'
    # Change a real exact input. The check must reject before scientific stdout.
    path = inputs / NATIVE
    original = path.read_bytes()
    path.write_bytes(original + b'\0')
    negative(root/'verify.py', b'SHA-256 mismatch:', inputs)
    path.write_bytes(original)
    sources = root / 'SOURCES.tsv'
    original = sources.read_bytes()
    sources.write_bytes(original + original.splitlines(keepends=True)[0])
    negative(root/'verify.py', b'duplicate dependency path:', inputs)
    sources.write_bytes(original)
    # Alter both the clock record and recipient claim in separate controls.
    forged = json.loads(result.read_bytes())
    witness = next(record['witness'] for bank in forged['scopes'][0]['clocks'][0]['recipients']
                   for record in bank['observed_markers'])
    witness[0] = -1
    path = root / 'forged-clock.json'
    path.write_text(json.dumps(forged), encoding='utf-8')
    negative(root/'audit.py', b'in paths', inputs, path)
    forged = json.loads(result.read_bytes())
    forged['scopes'][1]['clocks'][1]['recipients'][0]['new_quotient_basis'] = [[0]]
    path = root / 'forged-expansion.json'
    path.write_text(json.dumps(forged), encoding='utf-8')
    negative(root/'audit.py', b"len(p['new_quotient_basis'])", inputs, path)


def main():
    if not __debug__ or sys.version_info[:2] != (3, 12) or sys.implementation.name != 'cpython':
        raise ValueError('Use CPython 3.12 with assertions enabled')
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--controls', action='store_true')
    parser.add_argument('--write-result', type=Path, metavar='PATH',
                        help='write the regenerated full proof receipt to a new file')
    options = parser.parse_args()
    with TemporaryDirectory(prefix='bit-first-observer-') as directory:
        root = Path(directory)
        pins = stage(root)
        inputs = root / 'inputs'
        for prior in GENERATED:
            target = inputs / prior / 'RESULT.json'
            opts = [inputs / 'round24/RESULT.json'] if prior == 'bit-price' else ['--seconds', 480]
            raw = successful(target.with_name('verify.py'), inputs, *opts)
            if sha256(raw).hexdigest() != pins[f'{prior}/RESULT.json']:
                raise ValueError(f'Byte mismatch: regenerated {prior} receipt')
            target.write_bytes(raw)
        prior_audit = inputs / 'round25/audit.py'
        if successful(prior_audit, inputs, inputs/'round25/RESULT.json') != prior_audit.with_name('AUDIT.json').read_bytes():
            raise ValueError('Byte mismatch: independently regenerated carrier audit')
        summary = json.loads((PACKAGE / 'SUMMARY.json').read_bytes())
        result = root / 'RESULT.json'
        raw = successful(root/'verify.py', inputs, '--seconds', 480)
        if len(raw) != summary['result_bytes'] or sha256(raw).hexdigest() != summary['result_sha256']:
            raise ValueError('Byte mismatch: regenerated first-observer receipt')
        result.write_bytes(raw)
        audit = successful(root/'audit.py', inputs, result)
        if audit != (PACKAGE / 'AUDIT.json').read_bytes() or sha256(audit).hexdigest() != summary['independent_audit_sha256']:
            raise ValueError('Byte mismatch: independently regenerated first-observer audit')
        certificate = json.loads(raw)
        for name,value in zip(summary['scope_labels'],summary['scope'],strict=True):
            if certificate[name] != value:
                raise ValueError(f'Summary scope differs: {name}')
        scopes = certificate['scopes']
        if any([
            summary['status'] != certificate['status'],
            summary['verified_kappa_gain'] != '0',
            summary['rank'] != [s['rank'] for s in scopes],
            summary['nullity'] != [s['nullity'] for s in scopes],
            summary['expanded_singleton_uppers'] != [[c['expanded_singleton_upper'] for c in s['clocks']] for s in scopes],
            any(c['price'] != summary['prices'] for s in scopes for c in s['clocks']),
        ]):
            raise ValueError('Summary does not match the regenerated certificate')
        if options.controls:
            controls(root, result)
        if options.write_result:
            with options.write_result.open('xb') as stream:
                stream.write(raw)
    print('PASS_BIT_FIRST_OBSERVER_COMPENSATION slots=180 variables=1036 rank=148 nullity=888 expansions=0 kappa_change=0')
    if options.controls:
        print('PASS_BIT_FIRST_OBSERVER_CONTROLS changed_source=1 duplicate_path=1 forged_clock=1 forged_expansion=1')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as exc:
        sys.exit(str(exc))
