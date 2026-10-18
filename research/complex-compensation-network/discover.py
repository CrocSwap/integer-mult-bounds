#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Optional deterministic bounded nomination; verification needs no NumPy.
conorholds, with substantial OpenAI Codex assistance.
The alternating signed-forest start credits Stephan Arrington and predecessors.
"""
import argparse
import itertools
import json
from pathlib import Path
import sys
import time
from fractions import Fraction as Q

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from network import add_price, construct, load, matrix, require


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', type=int, default=120)
    parser.add_argument('--out', type=Path, help='fresh nomination file; default checks the saved recipe')
    args = parser.parse_args()
    require(1 <= args.seconds <= 600, 'discovery time budget')
    import numpy as np
    require(np.__version__ == '2.5.1', 'optional discovery requires numpy==2.5.1')
    word, saved, _, _, _ = load(); grid = 256; sources = sorted({e[2] for e in word['compensation']})
    original = np.array(matrix(word, sources, grid), dtype=np.int64)
    start = time.monotonic(); deadline = start+args.seconds; table = np.array([0], dtype=np.int64)
    def guard():
        require(time.monotonic() < deadline, 'discovery cap reached; no search-completeness claim')
    def prices(bound):
        nonlocal table
        require(type(bound) is int and 0 <= bound < 2**24, 'discovery integer/lookup bound')
        if len(table) <= bound:
            table = np.array([add_price(Q(i, grid)) for i in range(max(bound+1, 2*len(table)))], dtype=np.int64)
        return table
    def matrix_price(A):
        return int(prices(int(np.max(np.abs(A))))[np.abs(A)].sum())
    def forest(A):
        count = len(A); tab = prices(2*int(np.max(np.abs(A))))
        edges = [(int(tab[np.abs(A[i])].sum()), count, i, 0) for i in range(count)]
        for i in range(count):
            for j in range(i):
                weights = [int(tab[np.abs(A[i]-s*A[j])].sum())+16 for s in (-1, 1)]
                pick = int(weights[1] < weights[0]); edges.append((weights[pick], j, i, (-1, 1)[pick]))
        edges.sort(); dsu = list(range(count+1)); graph = [[] for _ in range(count+1)]; charge = chosen = 0
        def root(i):
            while dsu[i] != i:
                dsu[i] = dsu[dsu[i]]; i = dsu[i]
            return i
        for cost, i, j, sign in edges:
            a, b = root(i), root(j)
            if a == b:
                continue
            dsu[a] = b; graph[i].append((j, sign)); graph[j].append((i, sign)); charge += cost; chosen += 1
            if chosen == count:
                break
        parent = [None]*count; order = []
        def visit(i, previous):
            for j, sign in graph[i]:
                if j != previous:
                    if i != count:
                        parent[j] = (i, sign)
                    visit(j, i)
            if i != count:
                order.append(i)
        visit(count, -1); D = A.copy(); operations = []
        for i in order:
            if parent[i] is not None:
                j, sign = parent[i]; D[i] = A[i]-sign*A[j]; operations.append((i, j, sign))
        require(matrix_price(D)+16*len(operations) == charge, 'forest price identity')
        return D, operations
    def transform(A, edges):
        D = A.copy()
        for i, j, sign in edges:
            D[i] = A[i]-sign*A[j]
        return D
    target = []; helper = []; path = []
    for _ in range(16):
        guard(); _, target = forest(transform(original.T, helper).T)
        D, helper = forest(transform(original, target).T); D = D.T
        charge = matrix_price(D)+16*(len(target)+len(helper)); path.append(charge)
        if len(path) > 1 and path[-1] >= path[-2]:
            break
    else:
        raise ValueError('forest iteration cap reached')
    ops = [['T', i, j, -sign, 1] for i, j, sign in target] + [['H', j, i, sign, 1] for i, j, sign in helper]
    C = D.copy(); print('FOREST', path, flush=True)
    for step in range(1000):
        guard(); tab = prices(3*int(np.max(np.abs(C)))); entry = tab[np.abs(C)]
        rowcost = entry.sum(axis=1); colcost = entry.sum(axis=0); best = (0, None, None, None, None, None)
        alphabet = [(-2, 1), (-1, 1), (-1, 2), (1, 2), (1, 1), (2, 1)]
        for a in range(C.shape[1]):
            col = C[:, a, None]
            for num, den in alphabet:
                if den == 2 and np.any(col % 2):
                    continue
                gain = colcost-tab[np.abs(C-num*(col//den))].sum(axis=0)-2*add_price(Q(num, den))
                gain[a] = -1; b = int(np.argmax(gain))
                if int(gain[b]) > best[0]:
                    best = (int(gain[b]), 'H', a, b, num, den)
        for b in range(C.shape[0]):
            row = C[b, :]
            for num, den in alphabet:
                if den == 2 and np.any(row % 2):
                    continue
                gain = rowcost-tab[np.abs(C+num*(row//den))].sum(axis=1)-2*add_price(Q(num, den))
                gain[b] = -1; a = int(np.argmax(gain))
                if int(gain[a]) > best[0]:
                    best = (int(gain[a]), 'T', a, b, num, den)
        for kind, costs, M in [('HS', colcost, C.T), ('TS', rowcost, C)]:
            for a, row in enumerate(M):
                for num, den in [(1, 2), (2, 1)]:
                    if den == 2 and np.any(row % 2):
                        continue
                    gain = int(costs[a]-tab[np.abs(num*(row//den))].sum()-4)
                    if gain > best[0]:
                        best = (gain, kind, a, None, num, den)
        gain, kind, a, b, num, den = best
        if not gain:
            break
        if kind == 'H':
            C[:, b] -= num*(C[:, a]//den)
        elif kind == 'T':
            C[a, :] += num*(C[b, :]//den)
        elif kind == 'HS':
            C[:, a] = num*(C[:, a]//den)
        else:
            C[a, :] = num*(C[a, :]//den)
        ops.append([kind, a, b, num, den])
    else:
        raise ValueError('single-operation iteration cap reached')
    for _ in range(200):
        guard(); tab = prices(3*int(np.max(np.abs(C)))); best = (0, None, None, None)
        for kind, M in [('H', C.T), ('T', C)]:
            for i, row in enumerate(M):
                if not np.any(row):
                    continue
                old = int(tab[np.abs(row)].sum()); choices = []
                for j, donor in enumerate(M):
                    if i == j or not np.any(donor):
                        continue
                    for sign in (-1, 1):
                        cost = int(tab[np.abs(row+sign*donor)].sum()); choices.append((cost, j, sign))
                        if old-cost-16 > best[0]:
                            best = (old-cost-16, kind, i, [(j, sign)])
                choices.sort(); choices = choices[:16]
                for (_, j, s), (_, k, t) in itertools.combinations(choices, 2):
                    if j == k:
                        continue
                    gain = old-int(tab[np.abs(row+s*M[j]+t*M[k])].sum())-32
                    if gain > best[0]:
                        best = (gain, kind, i, [(j, s), (k, t)])
        gain, kind, i, donors = best
        if not gain:
            break
        for j, sign in donors:
            if kind == 'T':
                C[i, :] += sign*C[j, :]; ops.append(['T', i, j, sign, 1])
            else:
                C[:, i] += sign*C[:, j]; ops.append(['H', j, i, -sign, 1])
    else:
        raise ValueError('two-donor iteration cap reached')
    boundary = sum(4 if kind.endswith('S') else 2*add_price(Q(num, den)) for kind, a, b, num, den in ops)
    claim = dict(before_real=sum(add_price(Q(e[3], e[4])) for e in word['compensation']),
                 after_real=matrix_price(C)+boundary, before_macros=len(word['compensation']),
                 after_macros=int(np.count_nonzero(C))+2*len(ops), boundary_operations=len(ops))
    claim['saving_real'] = claim['before_real']-claim['after_real']
    recipe = dict(schema_version=1, grid_denominator=grid, sources=sources, operations=ops,
                  word_sha256=saved['word_sha256'], claimed=claim)
    construct(word, recipe)
    if args.out:
        with args.out.open('x') as stream:
            stream.write(json.dumps(recipe, indent=2)+'\n')
    else:
        require(recipe == saved, 'nomination differs from saved literal recipe')
    print('PASS_DETERMINISTIC_NETWORK_DISCOVERY', claim, 'elapsed_seconds', time.monotonic()-start)


if __name__ == '__main__':
    main()
