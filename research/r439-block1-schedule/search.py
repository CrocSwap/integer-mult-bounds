"""Exact nomination in two destination-once positive-addition classes.

Prepared for @Deftsalt-debug with substantial OpenAI Codex assistance.
Apache-2.0. Related fixed-factor scheduling: PR789 and PR844; no code imported.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = ROOT / "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
REGS = [0, 3, 11, 61, 62, 63, 68, 69, 72, 465]
N = len(REGS)


def matrix(gates):
    rows = [[int(i == j) for j in range(N)] for i in range(N)]
    for d, s in gates:
        rows[d] = [a + b for a, b in zip(rows[d], rows[s])]
    return rows


def solve(target):
    """State S: rows in S are final; every other row is its input unit.

    An edge finalizes r by adding a subset of the other current rows. Positive
    coefficients and a diagonal of one prohibit repeated donors: each current
    row has its own diagonal one, and all targets here are zero/one matrices.
    """
    if any(x not in (0, 1) for row in target for x in row):
        raise ValueError("this search class requires binary positive targets")
    if any(target[i][i] != 1 for i in range(N)):
        raise ValueError("non-unit diagonal")
    base = N + 1  # no carry even for the sum of all N binary rows
    unit = [base ** i for i in range(N)]
    packed = [sum(x * b for x, b in zip(row, unit)) for row in target]
    distance = [10**9] * (1 << N)
    parent = [None] * (1 << N)
    distance[0] = 0
    edges = 0
    reachable = 0
    for state in range(1 << N):
        if distance[state] == 10**9:
            continue
        reachable += 1
        current = [packed[i] if state >> i & 1 else unit[i] for i in range(N)]
        sums = [0] * (1 << N)
        by_sum = {}
        for donors in range(1 << N):
            if donors:
                bit = donors & -donors
                sums[donors] = sums[donors ^ bit] + current[bit.bit_length() - 1]
            by_sum.setdefault(sums[donors], []).append(donors)
        for r in range(N):
            if state >> r & 1:
                continue
            choices = [d for d in by_sum.get(packed[r] - unit[r], []) if not d >> r & 1]
            if not choices:
                continue
            donors = min(choices, key=lambda d: (d.bit_count(), d))
            edges += 1
            nxt = state | (1 << r)
            cost = distance[state] + donors.bit_count()
            if cost < distance[nxt]:
                distance[nxt] = cost
                parent[nxt] = (state, r, donors)
    if parent[-1] is None:
        raise ValueError("no schedule in the nominated class")
    batches = []
    state = (1 << N) - 1
    while state:
        prev, r, donors = parent[state]
        batches.append((r, [s for s in range(N) if donors >> s & 1]))
        state = prev
    batches.reverse()
    gates = [[r, s] for r, donors in batches for s in donors]
    if matrix(gates) != target:
        raise ValueError("nomination endpoint failed")
    return {"minimum": distance[-1], "reachable_states": reachable,
            "reachable_edges": edges, "batches": batches, "gates": gates,
            "distance": [None if d == 10**9 else d for d in distance]}


def nominate():
    word = json.loads(gzip.decompress(WORD.read_bytes()))
    original = [[REGS.index(d), REGS.index(ss[0])] for f, d, ss in word["B"][128:163]
                if f == 507 and len(ss) == 1]
    if len(original) != 35:
        raise ValueError("wrong block")
    factors = [solve(matrix(original[:14])), solve(matrix(original[14:]))]
    new = [g for factor in factors for g in factor["gates"]]
    reverse_old = matrix(original[::-1])
    reverse_new = matrix(new[::-1])
    dominated = all(b <= a for x, y in zip(reverse_old, reverse_new) for a, b in zip(x, y))
    return {"block": 1, "phase": "B", "start": 128, "stop": 163, "frame": 507,
            "registers": REGS, "split": 14, "original": original, "replacement": new,
            "factors": factors, "reverse_dominated": dominated,
            "source_sha256": hashlib.sha256(WORD.read_bytes()).hexdigest()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--write", action="store_true")
    args = p.parse_args()
    result = nominate()
    path = HERE / "CANDIDATE.json"
    if args.write:
        path.write_text(json.dumps(result, indent=2) + "\n")
    elif json.loads(path.read_text()) != json.loads(json.dumps(result)):
        raise ValueError("candidate does not match exhaustive nomination")
    print("PASS_R439_BLOCK1_SEARCH", "gates=35->" + str(len(result["replacement"])),
          "minima=" + "+".join(str(f["minimum"]) for f in result["factors"]),
          "reverse_dominated=" + str(result["reverse_dominated"]))


if __name__ == "__main__":
    main()
