"""Check the actual source matrices for the query separation theorem."""

from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import json


HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "lanes/new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz"
CORE_PIN = "a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa"
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]


def need(value, message):
    if not value:
        raise ValueError(message)


def multiply(a, b):
    bt = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def transpose(a):
    return [list(row) for row in zip(*a)]


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def residue(x, prime):
    x = F(x)
    need(x.denominator % prime != 0, "The residue map must be defined")
    return x.numerator * pow(x.denominator, -1, prime) % prime


def rank_mod(a, prime):
    rows = [[residue(x, prime) for x in row] for row in a]
    rank = 0
    for col in range(len(rows[0])):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = pow(rows[rank][col], -1, prime)
        rows[rank] = [x * scale % prime for x in rows[rank]]
        for i in range(len(rows)):
            if i != rank and rows[i][col]:
                scale = rows[i][col]
                rows[i] = [(x - scale * y) % prime for x, y in zip(rows[i], rows[rank])]
        rank += 1
        if rank == len(rows):
            break
    return rank


def main():
    raw = gzip.decompress(CORE.read_bytes())
    need(sha256(raw).hexdigest() == CORE_PIN, "The actual core pin must match")
    core = json.loads(raw)
    r = [[F(row.get(str(p), 0)) for p in range(112)] for row in core["R"]]
    ordinary = [p for p in range(112) if p not in A]
    ra = [[row[p] for p in A] for row in r]
    ru = [[row[p] for p in ordinary] for row in r]
    d = [[x / 4 for x in row] for row in multiply(transpose(ru), ra)]
    b = transpose(d)
    dt = [d[ordinary.index(p)] for p in T]
    need(multiply(dt, transpose(dt)) == identity(8), "D_T D_T^t must be identity")
    need(multiply(transpose(dt), dt) == identity(8), "D_T^t D_T must be identity")
    need(multiply(b, d) == [[13 * x for x in row] for row in identity(8)], "BD must be 13I")
    m = [[F(0) for _ in ordinary] for _ in A]
    for j, p in enumerate(T):
        for i in range(8):
            m[i][ordinary.index(p)] = dt[j][i]
    need(multiply(m, d) == identity(8), "The sparse log must be a section")
    need(rank_mod(b, 13) == 8, "B must have full row rank at 13")
    need(rank_mod(b + m, 13) == 16, "The dyadic stack must have rank sixteen")

    # Each new row is a dyadic kernel row plus the original section.
    kernel = []
    for j in range(len(ordinary)):
        row = [F(j == k) for k in range(len(ordinary))]
        for i in range(8):
            for k in range(len(ordinary)):
                row[k] -= d[j][i] * m[i][k]
        kernel.append(row)
    cases = 64
    for case in range(cases):
        candidate = [row[:] for row in m]
        for i in range(8):
            row = kernel[(11 * case + 7 * i) % len(kernel)]
            scale = F((case % 5) - 2, 2 ** (case % 4))
            candidate[i] = [x + scale * y for x, y in zip(candidate[i], row)]
        need(multiply(candidate, d) == identity(8), "Each perturbed log must remain a section")
        need(rank_mod(b + candidate, 13) == 16, "Each perturbed stack must have rank sixteen")

    matched = [[x / 13 for x in row] for row in b]
    need(multiply(matched, d) == identity(8), "The matched log must be a rational section")
    need(rank_mod(b + matched, 17) == 8, "The matched stack must have rank eight")
    need(any(x.denominator % 13 == 0 for row in matched for x in row), "The matched log leaves the dyadic ring")
    need(all(13 * x == y for row, source in zip(matched, b) for x, y in zip(row, source)), "The exact row dependence must hold")
    bad = [[13 * x for x in row] for row in m]
    need(rank_mod(b + bad, 13) == 8, "The nonunit control must defeat the residue rank conclusion")
    receipt = {
        "status": "PASS_DYADIC_QUERY_SEPARATION",
        "core_decompressed_sha256": CORE_PIN,
        "proof_sha256": sha256((HERE / "DYADIC-QUERY-SEPARATION-20261018.md").read_bytes()).hexdigest(),
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "selected": A,
        "ordinary_minor": T,
        "BD": "13I",
        "prime": 13,
        "B_rank": 8,
        "dyadic_section_stack_rank": 16,
        "kernel_perturbed_sections": cases,
        "matched_section_stack_rank": 8,
        "scope": "Source information rank and exact representation choice; no native child bound or supplier claim.",
    }
    destination = HERE / "DYADIC-QUERY-SEPARATION-20261018.json"
    destination.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(receipt["status"])


if __name__ == "__main__":
    main()
