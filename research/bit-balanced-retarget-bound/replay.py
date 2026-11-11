#!/usr/bin/env python3
"""Replay the exhaustive fixed-clock BIT reassignment bound without network access."""
import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
from tempfile import TemporaryDirectory

PACKAGE = Path(__file__).resolve().parent
GENERATED = ('round22', 'round23', 'round24', 'bit-price', 'round25')
SCRIPTS = {'verify.py', 'audit.py', 'SOURCES.tsv'}
RECORDS = {'RESULT.json', 'AUDIT.json'}
NATIVE = 'research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz'


def safe_key(value):
    key = PurePosixPath(value)
    if not key.parts or key.is_absolute() or '..' in key.parts or key.as_posix() != value:
        raise ValueError(f'Invalid replay path: {value}')
    return key


def stage(root):
    seen, staged, top_level = set(), set(), set()
    for line in (PACKAGE/'REPLAY.sha256').read_text(encoding='ascii').splitlines():
        digest, value = line.split('  ', 1)
        key = safe_key(value)
        if key in seen:
            raise ValueError(f'Duplicate replay path: {value}')
        seen.add(key)
        data = (PACKAGE/key).read_bytes()
        if sha256(data).hexdigest() != digest:
            raise ValueError(f'SHA-256 mismatch: {value}')
        category, *subpath = key.parts
        if category in ('inputs', 'predecessor') and subpath:
            relative = PurePosixPath(*subpath)
            if relative in staged:
                raise ValueError(f'Duplicate staged input: {relative}')
            staged.add(relative)
            destination = root.joinpath('inputs', *subpath)
        elif value in SCRIPTS | RECORDS:
            top_level.add(value)
            destination = root/key
        else:
            raise ValueError(f'Unexpected replay path: {value}')
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    if top_level != SCRIPTS | RECORDS:
        raise ValueError('Missing script, source list or record in replay manifest')
    dependencies = {}
    for line in (root/'SOURCES.tsv').read_text(encoding='utf-8').splitlines():
        value, digest, _ = line.split('\t')
        key = safe_key(value)
        if key in dependencies:
            raise ValueError(f'Duplicate source path: {value}')
        dependencies[key] = digest
    generated = {PurePosixPath(prior,'RESULT.json') for prior in GENERATED}
    auxiliary = {PurePosixPath('round25', name) for name in ('audit.py','AUDIT.json')}
    if staged != (dependencies.keys() - generated) | auxiliary:
        raise ValueError('Staged sources differ from the exact dependency inventory')
    for key, digest in dependencies.items():
        if key in staged and sha256((root/'inputs'/key).read_bytes()).hexdigest() != digest:
            raise ValueError(f'SHA-256 mismatch: {key}')
    return dependencies


def invoke(script, *args, timeout):
    return subprocess.run([sys.executable, '-I', '-B', str(script), *map(str,args)],
                          capture_output=True, check=False, timeout=timeout)


def successful(script, *args, timeout=480):
    proc = invoke(script, *args, timeout=timeout)
    if proc.returncode or proc.stderr:
        sys.stderr.buffer.write(proc.stderr)
        raise ValueError(f'{script.name} failed with exit {proc.returncode}')
    return proc.stdout


def negative(script, marker, *args):
    proc = invoke(script, *args, timeout=30)
    if proc.returncode != 1 or proc.stdout or marker not in proc.stderr:
        raise ValueError(f'Negative control did not reject: {marker.decode()}')


def regenerate(root, pins):
    for prior in GENERATED:
        receipt = root/prior/'RESULT.json'
        options = [root/'round24'/'RESULT.json'] if prior == 'bit-price' else []
        raw = successful(receipt.with_name('verify.py'),root,*options)
        if sha256(raw).hexdigest() != pins[PurePosixPath(prior,'RESULT.json')]:
            raise ValueError(f'Byte mismatch: regenerated {prior} receipt')
        receipt.write_bytes(raw)
    prior_audit = root/'round25'/'audit.py'
    raw = successful(prior_audit,root,prior_audit.with_name('RESULT.json'))
    if raw != prior_audit.with_name('AUDIT.json').read_bytes():
        raise ValueError('Byte mismatch: independently regenerated carrier audit')


def controls(root, receipt):
    inputs = root/'inputs'
    forged = json.loads(receipt.read_bytes())
    forged['clocks'][0]['cyclic_balancing_incidences'].append([0,1,2])
    path = root/'forged.json'
    path.write_text(json.dumps(forged),encoding='utf-8')
    negative(root/'audit.py', b'AssertionError: cyclic_balancing_incidences',inputs,path)

    path = inputs/NATIVE
    path.write_bytes(path.read_bytes()+b'\0')
    negative(root/'verify.py',b'SHA-256 mismatch: '+NATIVE.encode('ascii'),inputs)


def main():
    if not __debug__ or sys.version_info[:2] != (3,12) or sys.implementation.name != 'cpython':
        raise ValueError('Use CPython 3.12 with assertions enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--controls',action='store_true')
    options = parser.parse_args()
    with TemporaryDirectory(prefix='bit-balanced-retarget-') as directory:
        root = Path(directory)
        pins = stage(root)
        inputs = root/'inputs'
        regenerate(inputs,pins)

        primary = root/'RESULT.json'
        raw = successful(root/'verify.py',inputs,'--seconds',480,timeout=485)
        if raw != primary.read_bytes():
            raise ValueError('Byte mismatch: regenerated 1,200-pair census')
        audit = successful(root/'audit.py',inputs,primary)
        if audit != (root/'AUDIT.json').read_bytes():
            raise ValueError('Byte mismatch: independent exact audit')
        if options.controls:
            controls(root,primary)
    print('PASS_BIT_BALANCED_RETARGET pairs=1200 arcs=20 cycles=10 balanced_selections=1024 expansions=0 kappa_change=0')
    if options.controls:
        print('PASS_BIT_BALANCED_RETARGET_CONTROLS changed_source=1 forged_arc=1')


if __name__ == '__main__':
    try:
        main()
    except (OSError,ValueError,subprocess.TimeoutExpired) as exc:
        sys.exit(str(exc))
