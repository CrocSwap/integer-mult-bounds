"""Read-only finite corroboration. Produced by Nick Petalas. Apache-2.0."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from model import independent_target, matmul, rank, require, walsh, witness
sys.path.pop(0)


def census():
    result = {}
    for t in range(1, 4):
        n = 1 << t
        h, counts = walsh(t), Counter()
        halves = list(combinations(range(n), n // 2))
        for rows in halves:
            for columns in halves:
                a = [[h[i][j] for j in columns] for i in rows]
                r = rank(a)
                require(r == rank(a, 101), "rational/modular ranks disagree")
                require(4 * r >= n, "balanced submatrix violates the rank floor")
                counts[r] += 1
        require(sum(counts.values()) == len(halves) ** 2, "incomplete partition census")
        result[str(n)] = {str(k): v for k, v in sorted(counts.items())}
    return result


def family():
    result = []
    for t in range(2, 7):
        f, q, d, _ = witness(t)
        n, m = 1 << t, 1 << (t - 2)
        identity = [[int(i == j) for j in range(n)] for i in range(n)]
        delta = [[d[i][j] - f[i][j] for j in range(n)] for i in range(n)]
        q_delta = [[q[i][j] - identity[i][j] for j in range(n)] for i in range(n)]
        require(d == independent_target(t), "four-coordinate identity failed")
        require(matmul(q, q) == identity, "repair is not an involution")
        require(matmul(d, [list(c) for c in zip(*d)]) ==
                [[n * v for v in row] for row in identity], "normalized target is not orthogonal")
        require(rank(d) == n, "target lost an independent coordinate")
        require(rank(delta) == rank(q_delta) == m, "sharp correction rank failed")
        state, u = [row[:] for row in f], (1, -1, 1, 1)
        for suffix in range(m):
            total = [sum(u[a] * state[a * m + suffix][j] for a in range(4))
                     for j in range(n)]
            for a in range(4):
                row = a * m + suffix
                state[row] = [v - Fraction(u[a] * w, 2) for v, w in zip(state[row], total)]
        require(state == d, "literal sequence of disjoint reflections failed")
        for bank in range(2):
            rows = range(bank * n // 2, (bank + 1) * n // 2)
            other = range((1 - bank) * n // 2, (2 - bank) * n // 2)
            require(all(d[i][j] == 0 for i in rows for j in other), "cross-bank leakage")
        result.append({"tensor_factors": t, "addresses": n, "repair_rank": m})
    return result


def omitted_reflections():
    count = 0
    for t in range(2, 6):
        f, q, _, _ = witness(t)
        n, m, u = 1 << t, 1 << (t - 2), (1, -1, 1, 1)
        for omitted in range(m):
            mutant = [row[:] for row in q]
            for a in range(4):
                for b in range(4):
                    mutant[a * m + omitted][b * m + omitted] += Fraction(u[a] * u[b], 2)
            d = matmul(mutant, f)
            require(any(d[i][j] for i in range(n // 2) for j in range(n // 2, n)),
                    "omitted reflection was not detected")
            count += 1
    return count


def gaussian_kernel():
    phases, checked = ((1, 0), (0, 1), (-1, 0), (0, -1)), 0
    for t in range(2, 7):
        f, _, _, permutation = witness(t)
        for x, row in enumerate(f):
            for j, value in enumerate(row):
                y = permutation[j]
                direct = phases[(t - (x ^ y).bit_count()) % 4]
                exponent = t - x.bit_count() + 3 * y.bit_count()
                a, b = phases[exponent % 4]
                require(direct == (value * a, value * b), "Gaussian monomial identity failed")
                checked += 1
    return checked


def controls():
    rejected = 0
    for t in (-1, 7, True, Fraction(2)):
        try:
            walsh(t)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid exponent accepted")
    try:
        rank([[1], [1, 2]])
    except ValueError:
        rejected += 1
    else:
        raise ValueError("ragged matrix accepted")
    f, _, d, _ = witness(2)
    require(f != d and any(f[i][j] for i in range(2) for j in range(2, 4)),
            "uncorrected pooling unexpectedly succeeded")
    h = walsh(1)
    d = [[Fraction(3), Fraction(0)], [Fraction(0), Fraction(-1, 2)]]
    require(rank(d) == 2 and rank([[d[i][j] - h[i][j] for j in range(2)]
                                  for i in range(2)]) == 1, "two-address boundary failed")
    return rejected


def receipt(evidence):
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "model.py", "verify.py")
    hashes = {}
    for name in names:
        with (PACKAGE / name).open("rb") as source:
            payload = source.read(128 * 1024 + 1)
        require(len(payload) <= 128 * 1024, "package file exceeds receipt memory bound")
        hashes[name] = sha256(payload).hexdigest()
    return {"claim_type": "scoped proof with finite corroboration", "evidence": evidence,
            "source_sha256": hashes}


def main():
    require(len(sys.argv) == 1, "this read-only verifier accepts no arguments")
    evidence = {"balanced_submatrix_rank_histograms": census(), "sharp_family": family(),
                "omitted_reflection_controls": omitted_reflections(),
                "gaussian_kernel_entries": gaussian_kernel(), "invalid_inputs_rejected": controls()}
    print(json.dumps(receipt(evidence), indent=2, sort_keys=True))
    print("PASS_BALANCED_WALSH_POOLING")


if __name__ == "__main__":
    main()
