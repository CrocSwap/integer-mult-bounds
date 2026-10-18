#!/usr/bin/env python3
"""Exact dirty-response rank audit; no geometric entrance-feasibility claim.
Prepared with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--gk-dir', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    assert __debug__ and not args.out.exists()
    sys.path.insert(0, str(args.gk_dir.resolve()))
    import gk_word as g
    import gk_common as co
    g.V = co.V = 112
    g.DATA = co.DATA = 7168
    raw = gzip.decompress(args.word.read_bytes())
    word = json.loads(raw)
    columns = g.responses(word)
    basis, selected = {}, []
    for helper, column in enumerate(columns):
        row = column.copy()
        while row:
            pivot = min(row)
            if pivot not in basis:
                scale = row[pivot]
                basis[pivot] = {key: value / scale for key, value in row.items()}
                selected.append(helper)
                break
            scale = row[pivot]
            for key, value in basis[pivot].items():
                new = row.get(key, Q(0)) - scale * value
                if new:
                    row[key] = new
                else:
                    row.pop(key, None)
    zero = [helper for helper, column in enumerate(columns) if not column]
    serialized = json.dumps([{str(key): str(value) for key, value in sorted(column.items())}
                             for column in columns], sort_keys=True, separators=(',', ':')).encode()
    record = dict(status='PASS_EXACT_DIRTY_RESPONSE_RANK',
                  source_content_sha256=hashlib.sha256(raw).hexdigest(),
                  matrix_sha256=hashlib.sha256(serialized).hexdigest(),
                  helpers=len(columns), rank=len(selected), nullity=len(columns) - len(selected),
                  zero_response_helpers=zero, independent_helper_columns=selected,
                  remaining_nonzero_nullity=len(columns) - len(selected) - len(zero),
                  scope='Exact rational rank after the literal main word and target preconditioner. '
                        'Nullity alone says nothing about compatible entrance frames, donor reuse, '
                        'dyadic circuit coefficients, wrapper costs or whole-owner hosting.')
    args.out.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({key: value for key, value in record.items()
                      if key not in ('zero_response_helpers', 'independent_helper_columns')}, indent=2))


if __name__ == '__main__':
    main()
