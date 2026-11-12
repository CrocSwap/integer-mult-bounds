"""Reproduce the exact typed stock, source availability and finite-arm gates."""

import argparse
from hashlib import sha256
import json
import shutil
from pathlib import Path, PurePosixPath
import subprocess
import sys
from tempfile import TemporaryDirectory

FROZEN = {
    'TWO-ARM.json': (233402, '92095d8281ee0c895aafee22092c21786d905948ace6fdf2902bc7f0642eb408'),
    'TYPED.json': (4875219, '68202ba9326938cb0bf5abbabb893c3db01090a22acb6ba55afaef1dbae2bf9c'),
    'GATE.json': (465446, 'd047446188cd0bb93c5835a536560dc6509e8369e774c017e0f4a63c98cdc61d'),
}
SCRIPTS = frozenset({
    'typed_stock.py', 'decode_gate.py', 'audit.py',
    'two_arm_gate.py', 'audit_two_arm.py',
})
REPLAY_FILES = SCRIPTS | {
    'AUDIT.json',
    'TWO-ARM-AUDIT.json',
    'contracts/PROOF.md',
    'contracts/SOURCES.json',
    'contracts/canonical-PROOF-REVIEW.md',
    'contracts/pr7161-PROOF.md',
    'CAP-ONE.json',
    'SUMMARY.json',
    'deps/canonical/research/shared-wire-split-composition/frozen/clifford_exact.py',
    'deps/canonical/research/shared-wire-split-composition/frozen/native_verify.py',
    'deps/round11/frontier/independent_adapter_price.py',
    'deps/round13/alternative/reprice.py',
    'deps/round20/complex-stock/stock.py',
    'inputs/caller/CALLER.json',
    'inputs/native/RESULT.json',
    'inputs/native/WORD.json.gz',
}
TYPED_KEYS = (
    'source_head', 'source_tree', 'target', 'cap', 'stop_reason', 'status', 'moves_checked',
    'moves_pending', 'original_paid_positions', 'original_productive_targets', 'stages',
    'row_groups', 'target_cosets', 'eligible_groups', 'eligible_members', 'eligible_member_hist',
    'skipped_child_hist', 'baseline', 'raw_margin_upper', 'complete_saving_interval',
)
GATE_KEYS = (
    'head', 'target', 'scope', 'status', 'stop_reason', 'max_seconds', 'tested_pairs',
    'total_pairs', 'completed_groups', 'pending_groups', 'passed_by_mode', 'eligible_groups_by_mode',
    'pending_ideal_hist', 'price_one_retained', 'price_overgrant_multiple_retained',
    'controls', 'site_tests',
)


def summary(typed_raw, gate_raw):
    typed, gate = json.loads(typed_raw), json.loads(gate_raw)
    return {
        'typed_stock': {key: typed[key] for key in TYPED_KEYS},
        'source_availability': {key: gate[key] for key in GATE_KEYS},
        'survivor_counts': {key: len(rows) for key, rows in gate['survivors'].items()},
        'receipts': {
            name: {'bytes': len(raw), 'sha256': sha256(raw).hexdigest()}
            for name, raw in [('TYPED.json', typed_raw), ('GATE.json', gate_raw)]
        },
    }


def stage(root, inputs, deps, scratch):
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
        raw = path.read_bytes()
        if sha256(raw).hexdigest() != digest:
            raise ValueError(f'SHA-256 mismatch: {key}')
        if base is not None or key in SCRIPTS or rel.parts[0] == 'contracts':
            target = scratch / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    if seen != REPLAY_FILES:
        raise ValueError(f'Missing replay paths: {sorted(REPLAY_FILES - seen)}')


def call(root, script, args=(), expect_ok=True):
    command = [sys.executable, '-I', '-B', str(root / script), str(root), *args]
    result = subprocess.run(command, capture_output=True, check=False)
    if expect_ok and (result.returncode or result.stderr):
        sys.stderr.buffer.write(result.stderr)
        raise ValueError(f'{script} did not finish cleanly (exit {result.returncode})')
    return result


def exact_receipt(scratch, name, script, args):
    raw = call(scratch, script, args).stdout
    if (len(raw), sha256(raw).hexdigest()) != FROZEN[name]:
        raise ValueError(f'Byte mismatch: generated {name}')
    (scratch / name).write_bytes(raw)
    return raw


def controls(root, scratch, gate_raw):
    cap = call(scratch, 'typed_stock.py', ('--cap', '1', '--seconds', '480')).stdout
    if cap != (root / 'CAP-ONE.json').read_bytes():
        raise ValueError('Byte mismatch: CAP-ONE.json')
    gate = json.loads(gate_raw)
    circular = gate['survivors']['support_any_original_resident']
    assert circular and not gate['survivors']['support_independent_original_resident']
    gate['survivors']['support_independent_original_resident'] = circular[:1]
    (scratch / 'GATE.json').write_text(json.dumps(gate), encoding='utf-8')
    mutant = call(scratch, 'audit.py', expect_ok=False)
    expected = b"assert not gate['survivors']['support_independent_original_resident']"
    if mutant.returncode != 1 or mutant.stdout or expected not in mutant.stderr:
        raise ValueError('Independent audit did not reject the forged surviving source')
    print('PASS_CAP_ONE_PENDING_AND_FORGED_SOURCE_REJECTION')


def main():
    if not __debug__ or sys.implementation.name != 'cpython' or sys.version_info[:2] != (3, 12):
        raise ValueError('Use CPython 3.12 with assertions enabled')
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, default=root / 'inputs')
    parser.add_argument('--deps', type=Path, default=root / 'deps')
    parser.add_argument('--controls', action='store_true')
    args = parser.parse_args()
    with TemporaryDirectory(prefix='typed-arm-') as name:
        scratch = Path(name)
        stage(root, args.inputs.resolve(), args.deps.resolve(), scratch)
        typed = exact_receipt(scratch, 'TYPED.json', 'typed_stock.py', ('--cap', '6281', '--seconds', '480'))
        gate = exact_receipt(scratch, 'GATE.json', 'decode_gate.py', ('--seconds', '180'))
        if summary(typed, gate) != json.loads((root / 'SUMMARY.json').read_text(encoding='utf-8')):
            raise ValueError('Mismatch: SUMMARY.json')
        audit = call(scratch, 'audit.py').stdout
        if audit != (root / 'AUDIT.json').read_bytes():
            raise ValueError('Byte mismatch: AUDIT.json')
        previous = scratch / 'prior'
        previous.mkdir()
        for name in ('TYPED.json', 'GATE.json', 'typed_stock.py', 'decode_gate.py', 'audit.py'):
            shutil.copyfile(scratch / name, previous / name)
        exact_receipt(scratch, 'TWO-ARM.json', 'two_arm_gate.py',
                      ('--cap', '2602', '--seconds', '180'))
        tensor_audit = call(scratch, 'audit_two_arm.py').stdout
        if tensor_audit != (root / 'TWO-ARM-AUDIT.json').read_bytes():
            raise ValueError('Byte mismatch: TWO-ARM-AUDIT.json')
        if args.controls:
            controls(root, scratch, gate)
    print('PASS_FINITE_MONOMIAL_ARM_STOCK moves=6281 pairs=2602 tensor_reject=1516 circular=1086 saving=0')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        sys.exit(str(error))
