"""Authenticate the minimal Round 19 closure and reproduce both sealed receipts."""

import argparse
from hashlib import sha256
from pathlib import Path, PurePosixPath
import subprocess
import sys

REPLAY_FILES = frozenset({
    'AUDIT.json',
    'TRANSPORT.json',
    'ORDERED.json',
    'audit_transport.py',
    'deps/round11/frontier/independent_adapter_price.py',
    'deps/round13/alternative/reprice.py',
    'deps/round18/complex-free/AUDIT.json',
    'deps/round18/complex-free/FREE.json',
    'deps/round18/complex/AUDIT.json',
    'deps/round18/complex/STOCK.json',
    'deps/round18/complex/audit_stock.py',
    'deps/round18/complex/stock_gate.py',
    'inputs/caller/CALLER.json',
    'inputs/native/RESULT.json',
    'inputs/native/WORD.json.gz',
    'transport_stock.py',
})


def authenticate(root, inputs, deps):
    seen = set()
    paths = {'inputs': inputs, 'deps': deps}
    for row in (root / 'REPLAY.sha256').read_text(encoding='ascii').splitlines():
        digest, key = row.split('  ', 1)
        rel = PurePosixPath(key)
        if rel.as_posix() != key or key not in REPLAY_FILES or key in seen:
            raise ValueError(f'Unexpected or duplicate replay path: {key}')
        seen.add(key)
        base = paths.get(rel.parts[0])
        path = root / rel if base is None else base.joinpath(*rel.parts[1:])
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f'SHA-256 mismatch: {key}')
    if seen != REPLAY_FILES:
        raise ValueError(f'Missing replay paths: {sorted(REPLAY_FILES - seen)}')


def compare(script, args, receipt):
    command = [sys.executable, '-I', '-B', str(script), *map(str, args)]
    result = subprocess.run(command, capture_output=True, check=False)
    if result.returncode:
        sys.stderr.buffer.write(result.stderr)
        raise ValueError(f'{script.name} exited with status {result.returncode}')
    if result.stderr:
        sys.stderr.buffer.write(result.stderr)
        raise ValueError(f'{script.name} produced unexpected stderr')
    if result.stdout != receipt.read_bytes():
        raise ValueError(f'Byte mismatch: {receipt.name}')


def main():
    if not __debug__ or sys.implementation.name != 'cpython' or sys.version_info[:2] != (3, 12):
        raise ValueError('Use CPython 3.12 with assertions enabled')
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, default=root / 'inputs')
    parser.add_argument('--deps', type=Path, default=root / 'deps')
    args = parser.parse_args()
    inputs, deps = args.inputs.resolve(), args.deps.resolve()
    authenticate(root, inputs, deps)
    transport = root / 'TRANSPORT.json'
    compare(root / 'transport_stock.py', (inputs, deps, '--cap', 256, '--seconds', 720), transport)
    compare(root / 'audit_transport.py', (inputs, deps, transport, '--ordered-cut'),
            root / 'ORDERED.json')
    print('PASS_EXISTING_PAID_CROSS_CHART_STOCK transports=48 checks=128 pending=73')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        sys.exit(str(error))
