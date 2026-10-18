#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Verify the retained PR589 provenance/deficit contract without a cold replay."""
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('retained_bit_guard', HERE / 'guard.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def verify(root=guard.ROOT, assembly=None, bit_result=None):
    ctx = guard.context(root)
    assemblies = [assembly] if assembly is not None else [root / name for name in guard.ASSEMBLIES]
    assembly_bytes = [path.read_bytes() for path in assemblies]
    for raw in assembly_bytes:
        guard.check_assembly(json.loads(raw), ctx)
    result_path = bit_result if bit_result is not None else root / guard.BIT_RESULT
    result_bytes = result_path.read_bytes()
    guard.check_bit_result(json.loads(result_bytes), ctx)
    return dict(status='PASS_RETAINED_PR589_SUPPLIER_BINDING', base_commit=ctx['base_commit'],
                supplier=ctx['supplier'], git_objects=ctx['git_objects'],
                record_sha256=ctx['record_sha256'], word_content_sha256=ctx['word_content_sha256'],
                assemblies_checked=len(assemblies), bit_results_checked=1,
                assembly_sha256=[sha256(raw).hexdigest() for raw in assembly_bytes],
                bit_result_sha256=sha256(result_bytes).hexdigest(),
                live=ctx['derived']['live'], rank_mass=ctx['derived']['rank_mass'],
                scope='Pinned PR589 source identity, COPY-frame ranks and profile deficit; '
                      'no scalar/phase/native replay, certified moment or all-size theorem.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=guard.ROOT)
    parser.add_argument('--assembly', type=Path, help='Also guard a newly emitted assembly instead of the four fixtures')
    parser.add_argument('--bit-result', type=Path, help='Guard a newly emitted RESULT9.json instead of the archived fixture')
    parser.add_argument('--write', type=Path, help='Write an explicitly requested receipt')
    args = parser.parse_args()
    try:
        receipt = verify(args.root, args.assembly, args.bit_result)
        if args.write is None and args.assembly is None and args.bit_result is None:
            guard.require(receipt == json.loads((HERE / 'RESULT.json').read_bytes()), 'committed receipt differs')
        if args.write:
            args.write.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
        print(receipt['status'], 'assemblies=' + str(receipt['assemblies_checked']),
              'deficit=' + str(receipt['supplier']['derived_deficit']))
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        print('FAIL_RETAINED_PR589_SUPPLIER_BINDING:', exc, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
