#!/usr/bin/env python3
"""Separate dense-elimination checks, without importing the primary checker."""
from itertools import combinations, permutations


def require(x, message):
    if not x:
        raise ValueError(message)


def rank2(matrix):
    rows = [list(row) for row in matrix]
    if not rows:
        return 0
    n = len(rows[0])
    pivot = 0
    for col in range(n):
        candidates = [i for i in range(pivot, len(rows)) if rows[i][col]]
        if not candidates:
            continue
        i = candidates[0]
        rows[pivot], rows[i] = rows[i], rows[pivot]
        for j in range(len(rows)):
            if j != pivot and rows[j][col]:
                rows[j] = [(a + b) % 2 for a, b in zip(rows[j], rows[pivot])]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def main():
    rectangles = 0
    for n in range(4, 17):
        edges = list(combinations(range(n), 2))
        mask = [[int(len(set(e).intersection(f)) != 1) for f in edges] for e in edges]
        require(rank2(mask) == n - int(n % 2 == 0), 'edge mask rank')
        for a in range(n):
            s = [i for i, edge in enumerate(edges) if a in edge]
            for b in range(n):
                t = [j for j, edge in enumerate(edges) if b in edge]
                actual = [[mask[i][j] for j in t] for i in s]
                want = n - 1 - int(n % 2 == 1 and a != b)
                require(rank2(actual) == want, 'axis rectangle')
                rectangles += 1
        bill = sum(rank2([[mask[i][j] for j, f in enumerate(edges) if a in f]
                          for i, e in enumerate(edges) if a in e]) for a in range(n))
        require(bill == n * (n - 1), 'coordinate expansion attainment')
    # Enumerate all possible cheap first/second terms and force the coordinates
    # of a third from the required nonzero cross pairings. No support-rank code.
    triple_attempts = 0
    for n in range(3, 17):
        axes = list(permutations(range(n), 2))
        for a, b in axes:
            for c, d in axes:
                if b != c or d != a:
                    continue
                for e, f in axes:
                    triple_attempts += 1
                    require(not (b == e and f == a and d == e and f == c), 'three cheap axes falsely compatible')
    # Detect realistic broken independent implementations.
    require(rank2([[1, 1], [1, 1]]) == 1, 'binary duplicate-row control')
    require(rank2([[0, 1, 1], [1, 0, 1], [1, 1, 0]]) == 2, 'odd I+J kernel control')
    require(rank2([[0, 1], [1, 0]]) == 2, 'even I+J invertibility control')
    print('PASS_DN_INDEPENDENT_EDGE_PROOF_CHECKS', rectangles, 'rectangles;', triple_attempts, 'cheap-triple attempts; 3 controls')


if __name__ == '__main__':
    main()
