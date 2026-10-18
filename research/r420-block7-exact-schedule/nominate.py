#!/usr/bin/env python3
"""Exact finite schedule nomination. Yuzhou Wang + OpenAI Codex, Apache-2.0."""
import functools
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
N = 12


def matrix(ops):
    rows = [[int(i == j) for j in range(N)] for i in range(N)]
    for d, s in ops:
        rows[d] = [a + b for a, b in zip(rows[d], rows[s])]
    return rows


def solve(ops):
    m = matrix(ops)
    if any(x not in (0, 1) for row in m for x in row) or any(m[i][i] != 1 for i in range(N)):
        raise ValueError('nomination class requires binary integer matrix with diagonal one')
    rows = [sum(x << i for i, x in enumerate(row)) for row in m]
    dp = [10**9] * (1 << N)
    dp[0] = 0
    previous = {}
    feasible = 0
    for state in range(1 << N):
        for d in range(N):
            if state >> d & 1:
                continue
            wanted = rows[d] ^ (1 << d)
            donors = [(s, rows[s] if state >> s & 1 else 1 << s)
                      for s in range(N) if s != d]
            donors = [(s, row) for s, row in donors if row & ~wanted == 0]

            @functools.lru_cache(None)
            def cover(remaining):
                if not remaining:
                    return ()
                bit = remaining & -remaining
                best = None
                for s, row in donors:
                    if row & bit and row & remaining == row:
                        tail = cover(remaining ^ row)
                        if tail is not None:
                            choice = tuple(sorted((s,) + tail))
                            if best is None or (len(choice), choice) < (len(best), best):
                                best = choice
                return best

            sources = cover(wanted)
            if sources is None:
                continue
            feasible += 1
            following = state | (1 << d)
            if dp[state] + len(sources) < dp[following]:
                dp[following] = dp[state] + len(sources)
                previous[following] = (state, d, sources)
    if any(d == 10**9 for d in dp):
        raise ValueError('unexpected unreachable state')
    batches = []
    state = (1 << N) - 1
    while state:
        state, d, sources = previous[state]
        batches.append([d, list(sources)])
    batches.reverse()
    return {'original_gates': len(ops), 'rows': rows, 'potentials': dp,
            'minimum': dp[-1], 'feasible_state_destination_pairs': feasible,
            'batches': batches}


def nominate():
    word = json.loads(gzip.decompress((ROOT / 'research/e8-bit-r420/data/bitE8mut-r420.json.gz').read_bytes()))
    block = word['B'][471:512]
    registers = sorted({r for _, d, ss in block for r in [d] + ss})
    ix = {r: i for i, r in enumerate(registers)}
    ops = [(ix[d], ix[s]) for _, d, ss in block for s in ss]
    return {'schema': 1, 'seed': 17, 'block': 7, 'frame': 549, 'slice': [471, 512],
            'split': 17, 'registers': registers, 'factors': [solve(ops[:17]), solve(ops[17:])]}


if __name__ == '__main__':
    print(json.dumps(nominate(), indent=2, sort_keys=True))
