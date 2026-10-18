#!/usr/bin/env python3
"""Opt-in complete historical audit with a pinned exact central-factor adapter."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = '47481c89fd30a43f8f882eb4b391e89c29273fd0'
FIXTURE = 'certificates/dyadic-central-factor.json'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def admit_sources(root=ROOT):
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    if pins['base_commit'] != BASE:
        raise ValueError('Wrong base commit')
    for name, expected in pins['files'].items():
        path = root / name
        if not path.is_file() or sha(path.read_bytes()) != expected:
            raise ValueError('Source pin mismatch: ' + name)
    for name, expected in pins['adapter_files'].items():
        if sha((HERE / name).read_bytes()) != expected:
            raise ValueError('Adapter pin mismatch: ' + name)
    return pins


def replay(engine='packed', factor_only=False):
    if not __debug__:
        raise ValueError('Full inherited audit requires Python assertions; omit -O')
    started = time.perf_counter()
    pins = admit_sources()
    sys.path.insert(0, str(ROOT / 'scripts'))
    sys.path.insert(0, str(HERE))
    import audit_complex_centers as audit
    import experiments.complex_centers as original
    import packed
    verifier = {'baseline': original.verify_factor, 'packed': packed.verify_factor}[engine]
    if factor_only:
        receipt = verifier(original.factor(26))
        expected = json.loads((ROOT / FIXTURE).read_text())['central_factor']
        if receipt != expected:
            raise ValueError('Central-factor receipt mismatch')
        raw = (json.dumps(receipt, indent=2, sort_keys=True) + '\n').encode()
    else:
        # audit imports this single function by name. All other implementation
        # and source hashing stay original, and the patch is confined to this call.
        previous = audit.verify_factor
        try:
            audit.verify_factor = verifier
            receipt = audit.serializable(audit.certificate())
        finally:
            audit.verify_factor = previous
        raw = (json.dumps(receipt, indent=2, sort_keys=True) + '\n').encode()
        if raw != (ROOT / FIXTURE).read_bytes():
            raise ValueError('Complete historical certificate mismatch')
    # Detect an incomplete manifest or unexpected imported repository module.
    for module in list(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path is None:
            continue
        path = Path(path).resolve()
        if path.is_relative_to(ROOT / 'scripts'):
            name = path.relative_to(ROOT).as_posix()
            if name not in pins['files']:
                raise ValueError('Unpinned imported module: ' + name)
    return dict(status='PASS_CENTRAL_FACTOR_PACKED', engine=engine,
                scope='factor' if factor_only else 'complete_historical_audit',
                base_commit=BASE, coefficients_checked=2600**2,
                receipt_sha256=sha(raw), source_files=len(pins['files']),
                source_manifest_sha256=sha((HERE / 'SOURCES.json').read_bytes()),
                seconds=time.perf_counter() - started)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', choices=('baseline', 'packed'), default='packed')
    parser.add_argument('--factor-only', action='store_true')
    parser.add_argument('--output', type=Path, help='New result file; existing files are never replaced')
    args = parser.parse_args()
    if args.output is not None and args.output.exists():
        parser.error('Output already exists')
    result = replay(args.engine, args.factor_only)
    encoded = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output is not None:
        with args.output.open('x') as stream:
            stream.write(encoded)
    print(encoded, end='')


if __name__ == '__main__':
    main()
