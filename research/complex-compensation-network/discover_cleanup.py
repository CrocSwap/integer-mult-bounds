#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Optional deterministic cleanup nomination; the exact recipe needs no NumPy.

conorholds, with substantial OpenAI Codex assistance.
Two-sided cleanup factorization credits Stephan Arrington, PR1119.
"""
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from network import add_price, load, price, require, sha, strict_json
from cleanup import construct_cleanup, factor_block, json_bytes, operator


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', type=int, default=120)
    parser.add_argument('--out', type=Path, help='fresh nomination file; default reproduces the saved recipe')
    args = parser.parse_args()
    require(1 <= args.seconds <= 600, 'cleanup nomination time cap')
    import numpy as np
    require(np.__version__ == '2.5.1', 'optional discovery requires numpy==2.5.1')
    word, compensation, _, _, _ = load(); original = operator(word, word['cleanup'])
    active = {i for i, row in enumerate(original) if row != {i: Q(1)}}
    active.update(j for i in active.copy() for j in original[i])
    registers = sorted(active); grid = 65536; size = len(registers)
    C = np.zeros((size, size), dtype=np.int64)
    for i, r in enumerate(registers):
        for j, c in enumerate(registers):
            q = original[r].get(c, Q(0))
            require(grid % q.denominator == 0, 'cleanup initial coefficient grid')
            C[i, j] = q.numerator*(grid//q.denominator)
    start = time.monotonic(); deadline = start+args.seconds; costs = {}
    def matrix_cost(A):
        values, counts = np.unique(A[A != 0], return_counts=True); total = 0
        for value, count in zip(values, counts):
            value = int(value)
            if value not in costs:
                costs[value] = add_price(Q(value, grid))
            total += costs[value]*int(count)
        return total
    rows = list(range(size)); columns = rows.copy(); pivots = []
    for step in range(size):
        require(time.monotonic() < deadline, 'cleanup discovery cap reached; no completeness claim')
        A = C[np.ix_(rows, columns)]
        row_nz = np.count_nonzero(A, axis=1); column_nz = np.count_nonzero(A, axis=0); candidates = []
        for i, j in zip(*np.nonzero(A)):
            value = abs(int(A[i, j]))
            if value & (value-1) == 0:
                r, c = rows[i], columns[j]
                candidates.append((int((row_nz[i]-1)*(column_nz[j]-1)),
                                   int(row_nz[i]+column_nz[j]), int(r != c), r, c))
        candidates.sort(); best = None; old = matrix_cost(C)
        for fill, _, permutation, r, c in candidates[:96]:
            pivot = int(C[r, c]); column = C[:, c].copy(); row = C[r].copy()
            if int(np.max(abs(column)))*int(np.max(abs(row))) > 2**61:
                continue
            product = np.outer(column, row)
            if np.any(product % pivot):
                continue
            changed = C-product//pivot
            changed[r, :] = 0; changed[:, c] = 0; changed[r, c] = pivot
            require(int(np.max(abs(changed))) < 2**60, 'cleanup nomination integer bound')
            left = [Q(-int(column[i]), pivot) for i in np.flatnonzero(column) if i != r]
            right = [Q(-int(row[j]), pivot) for j in np.flatnonzero(row) if j != c]
            charged = sum(add_price(q) for q in left+right)
            score = (charged+matrix_cost(changed)-old+24*permutation,
                     fill, len(left)+len(right), r, c)
            if best is None or score < best[0]:
                best = (score, changed, r, c)
        require(best is not None, 'no bounded-grid dyadic-unit pivot')
        _, C, r, c = best; rows.remove(r); columns.remove(c)
        pivots.append([registers[r], registers[c]])
        if step % 128 == 0:
            print('CLEANUP_PIVOTS', step+1, 'of', size, flush=True)
    gates = factor_block(original, registers, pivots)
    before = sum(map(price, word['cleanup'])); after = sum(map(price, gates))
    recipe = dict(schema_version=1, word_sha256=compensation['word_sha256'],
                  original_cleanup_sha256=sha(json_bytes(word['cleanup'])),
                  blocks=[dict(registers=registers, pivots=pivots)],
                  claimed=dict(before_macros=len(word['cleanup']), after_macros=len(gates),
                               before_real=before, after_real=after, saving_real=before-after))
    construct_cleanup(word, recipe)
    if args.out:
        with args.out.open('x') as stream:
            stream.write(json.dumps(recipe, indent=2)+'\n')
    else:
        require(recipe == strict_json((HERE / 'CLEANUP-RECIPE.json').read_bytes()),
                'cleanup nomination differs from saved exact recipe')
    print('PASS_DETERMINISTIC_CLEANUP_DISCOVERY', recipe['claimed'],
          'elapsed_seconds', time.monotonic()-start)


if __name__ == '__main__':
    main()
