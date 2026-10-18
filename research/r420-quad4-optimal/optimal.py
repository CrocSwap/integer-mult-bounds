#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared for Chris Barber (@cbarber1) with OpenAI Codex assistance.
"""Exhaust the inverse-subtraction DAG of one nonnegative integer matrix.

Only in-place row additions r[a] += r[b] (a != b), with no extra registers,
permutations, subtraction or F2 cancellation, are in the certified class.
"""
from collections import Counter
from functools import lru_cache
import hashlib
import json


def minimum_additions(target):
    n = len(target)
    identity = tuple(tuple(int(i == j) for j in range(n)) for i in range(n))
    root = tuple(tuple(row) for row in target)
    if not n or any(len(row) != n for row in root):
        raise ValueError('target must be a nonempty square matrix')
    if any(type(x) is not int or x < 0 for row in root for x in row):
        raise ValueError('target entries must be nonnegative integers')
    if any(root[i][i] < 1 for i in range(n)):
        raise ValueError('target diagonal must be positive')
    states = {}
    edges = 0

    @lru_cache(None)
    def distance(matrix):
        nonlocal edges
        if matrix == identity:
            states[matrix] = 0
            return 0
        best = None
        for dst in range(n):
            for src in range(n):
                if dst == src:
                    continue
                row = tuple(a - b for a, b in zip(matrix[dst], matrix[src]))
                # Every forward addition keeps all entries nonnegative and
                # each diagonal entry >= its initial value 1.
                if row[dst] < 1 or any(x < 0 for x in row):
                    continue
                child = list(matrix)
                child[dst] = row
                edges += 1
                cost = distance(tuple(child))
                if cost is not None and (best is None or cost + 1 < best):
                    best = cost + 1
        states[matrix] = best
        return best

    minimum = distance(root)
    digest = hashlib.sha256()
    for matrix, cost in sorted(states.items()):
        digest.update((json.dumps([matrix, cost], separators=(',', ':')) + '\n').encode())
    histogram = Counter('unreachable' if c is None else str(c) for c in states.values())
    return {
        'minimum_additions': minimum,
        'states': len(states),
        'edges': edges,
        'distance_histogram': dict(sorted(histogram.items())),
        'state_distance_sha256': digest.hexdigest(),
        'coverage': 'All nonnegative inverse row subtractions preserving diagonal >= 1, from the fixed target to all reachable matrices.',
    }
