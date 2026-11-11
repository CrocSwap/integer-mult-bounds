"""Authenticate the fixed #7161 stock census and reproduce its full receipt."""

import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
from tempfile import TemporaryDirectory

STOCK_SHA = '39a33d2ddcff886fd4be1591bcf15f94cc317f1f7aa09a85c3ac6a2529fb09ad'
STOCK_BYTES = 4194679
REPLAY_FILES = frozenset({
    'AUDIT.json',
    'SUMMARY.json',
    'audit.py',
    'deps/canonical/research/shared-wire-split-composition/frozen/clifford_exact.py',
    'deps/canonical/research/shared-wire-split-composition/frozen/native_verify.py',
    'deps/round13/alternative/reprice.py',
    'inputs/caller/CALLER.json',
    'inputs/native/RESULT.json',
    'inputs/native/WORD.json.gz',
    'stock.py',
})
SUMMARY_KEYS = (
    'source_head', 'source_tree', 'target', 'cap', 'reason', 'pending_moves',
    'native_moves', 'stages', 'paid_positions', 'productive_targets',
    'stage_deficit_upper', 'baseline', 'literal_classes', 'canonical_classes',
    'signed_quotient_classes', 'target_monomial_cosets', 'target_coset_basis_size',
    'target_coset_all_clock_discarded', 'target_coset_chronological_discarded',
    'zero_rows', 'serial_runs', 'controls', 'site_tests', 'prices',
)


def summary(raw):
    report = json.loads(raw)
    result = {key: report[key] for key in SUMMARY_KEYS}
    result['stock_receipt_bytes'] = len(raw)
    result['stock_receipt_sha256'] = sha256(raw).hexdigest()
    return result


def authenticate(root, inputs, deps):
    seen = set()
    bases = {'inputs': inputs, 'deps': deps}
    for row in (root / 'REPLAY.sha256').read_text(encoding='ascii').splitlines():
        digest, key = row.split('  ', 1)
        rel = PurePosixPath(key)
        if rel.as_posix() != key or key not in REPLAY_FILES or key in seen:
            raise ValueError(f'Unexpected or duplicate replay path: {key}')
        seen.add(key)
        base = bases.get(rel.parts[0])
        path = root / rel if base is None else base.joinpath(*rel.parts[1:])
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f'SHA-256 mismatch: {key}')
    if seen != REPLAY_FILES:
        raise ValueError(f'Missing replay paths: {sorted(REPLAY_FILES - seen)}')


def run(script, args, stdout):
    command = [sys.executable, '-I', '-B', str(script), *map(str, args)]
    result = subprocess.run(command, stdout=stdout, stderr=subprocess.PIPE, check=False)
    if result.stderr:
        sys.stderr.buffer.write(result.stderr)
    if result.returncode or result.stderr:
        raise ValueError(f'{script.name} did not finish cleanly (exit {result.returncode})')
    return result.stdout


def main():
    if not __debug__:
        raise RuntimeError('Run with assertions enabled')
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, default=root / 'inputs')
    parser.add_argument('--deps', type=Path, default=root / 'deps')
    args = parser.parse_args()
    inputs, deps = args.inputs.resolve(), args.deps.resolve()
    authenticate(root, inputs, deps)
    with TemporaryDirectory(prefix='consolidation-') as scratch:
        receipt = Path(scratch) / 'STOCK.json'
        with receipt.open('wb') as output:
            run(root / 'stock.py', (inputs, deps, '--cap', 6279, '--seconds', 600), output)
        raw = receipt.read_bytes()
        if len(raw) != STOCK_BYTES or sha256(raw).hexdigest() != STOCK_SHA:
            raise ValueError('Byte mismatch: full generated STOCK.json')
        if summary(raw) != json.loads((root / 'SUMMARY.json').read_text(encoding='utf-8')):
            raise ValueError('Mismatch: SUMMARY.json')
        audit = run(root / 'audit.py', (inputs, deps, receipt), subprocess.PIPE)
        if audit != (root / 'AUDIT.json').read_bytes():
            raise ValueError('Byte mismatch: AUDIT.json')
    print('PASS_FIXED_MAP_CONSOLIDATION moves=6279 quotient_classes=2229 target_classes=978 saving=0')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        sys.exit(str(error))
