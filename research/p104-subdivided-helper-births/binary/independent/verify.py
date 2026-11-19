#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independently verify the literal binary births, caller tariff and ordinary bound."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import literal
import price

HERE = Path(__file__).resolve().parent


def encode(receipt):
    return (json.dumps(receipt, indent=2, sort_keys=True) + '\n').encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--source-root', type=Path, required=True, help='sparse root of pinned public PR #7776'
    )
    parser.add_argument(
        '--word',
        type=Path,
        default=HERE.parent / 'WORD.json.gz',
        help='checked-in compressed binary tape',
    )
    parser.add_argument(
        '--out', type=Path, required=True, help='destination for combined verification receipt'
    )
    args = parser.parse_args()

    native = literal.verify(args.source_root, args.word)
    finite = price.verify(args.source_root, native, sha256(encode(native)).hexdigest())
    status = 'PASS_INDEPENDENT_BINARY_BIRTHS_AND_FINITE_ORDINARY'
    args.out.write_bytes(encode(dict(status=status, native=native, finite=finite)))
    print(native['status'], native['public'], native['native_calls'])
    print(
        finite['status'], finite['published_ordinary_admitted'], *finite['raw_crossing']['bracket']
    )
    print(status)


if __name__ == '__main__':
    main()
