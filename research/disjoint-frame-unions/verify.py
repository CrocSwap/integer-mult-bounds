#!/usr/bin/env python3
"""Opt-in exact union propagation for the complete historical tensor audit."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = '2921874911956718fcaaaf9396fe8267b3cfa9f0'
FIXTURE = 'certificates/disjoint-tensor-compression.json'


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


def replay(engine='propagated'):
    if sys.flags.optimize:
        raise ValueError('Inherited full audit requires assertions; omit -O')
    if engine not in ('baseline', 'propagated'):
        raise ValueError('Unknown engine')
    start = time.perf_counter()
    pins = admit_sources()
    sys.path[:0] = [str(ROOT / 'scripts'), str(HERE)]
    import audit_disjoint_tensor as audit
    from experiments.disjoint_tensor import DisjointTensor
    from accelerator import frame_data
    previous = DisjointTensor.frame_data
    try:
        if engine == 'propagated':
            DisjointTensor.frame_data = frame_data
        receipt = audit.serializable(audit.certificate())
    finally:
        DisjointTensor.frame_data = previous
    raw = (json.dumps(receipt, indent=2, sort_keys=True) + '\n').encode()
    if raw != (ROOT / FIXTURE).read_bytes():
        raise ValueError('Complete historical certificate mismatch')
    for module in list(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path is not None and Path(path).resolve().is_relative_to(ROOT / 'scripts'):
            name = Path(path).resolve().relative_to(ROOT).as_posix()
            if name not in pins['files']:
                raise ValueError('Unpinned imported module: ' + name)
    return dict(status='PASS_DISJOINT_FRAME_UNIONS', engine=engine,
                scope='complete_historical_audit', base_commit=BASE,
                receipt_sha256=sha(raw), source_files=len(pins['files']),
                source_manifest_sha256=sha((HERE / 'SOURCES.json').read_bytes()),
                seconds=time.perf_counter() - start)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', choices=('baseline', 'propagated'), default='propagated')
    parser.add_argument('--output', type=Path, help='New file; existing output is never replaced')
    args = parser.parse_args()
    if args.output is not None and args.output.exists():
        parser.error('Output already exists')
    result = replay(args.engine)
    encoded = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output is not None:
        with args.output.open('x') as stream:
            stream.write(encoded)
    print(encoded, end='')


if __name__ == '__main__':
    main()
