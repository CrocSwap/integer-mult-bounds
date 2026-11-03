"""Exact checker for three-query dyadic cubic repairs at new arities.

Independent of search.py: weights are obtained by exact Gaussian elimination
on the first three coefficient equations, not by the closed form.  Each
certificate is checked by coefficient comparison and by literal execution of
the retained children followed by the appended repair on dirty integer and
rational inputs.  Rejection controls must fail.  Standard library only.

Nick Petalas. Apache-2.0.
"""
from __future__ import annotations

import json
import random
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def fail(msg: str) -> None:
    print("FAIL", msg)
    sys.exit(1)


def power_sums(r: int) -> tuple[int, int, int]:
    return (sum(range(r)), sum(i * i for i in range(r)), sum(i ** 3 for i in range(r)))


def solve3(mat: list[list[Fraction]], rhs: list[Fraction]) -> list[Fraction]:
    a = [row[:] + [v] for row, v in zip(mat, rhs)]
    for col in range(3):
        piv = next(i for i in range(col, 3) if a[i][col] != 0)
        a[col], a[piv] = a[piv], a[col]
        for i in range(3):
            if i != col and a[i][col] != 0:
                f = a[i][col] / a[col][col]
                a[i] = [x - f * y for x, y in zip(a[i], a[col])]
    return [a[i][3] / a[i][i] for i in range(3)]


def solved_weights(r: int, c: list[Fraction]) -> tuple[list[Fraction], Fraction]:
    """Weights from A^3, A^2B, AB^2 equations; return them and the B^3 residual."""
    s1, s2, s3 = power_sums(r)
    w = solve3([[Fraction(1)] * 3, c, [x * x for x in c]],
               [Fraction(0), Fraction(s1), Fraction(s2)])
    return w, sum(wj * cj ** 3 for wj, cj in zip(w, c)) - s3


def is_dyadic(x: Fraction) -> bool:
    d = x.denominator
    return d & (d - 1) == 0


def run_program(r: int, prog: list[tuple[str, Fraction]], y, a, b):
    """Retained children y += a^3; a += b (r times), then the appended repair."""
    for _ in range(r):
        y += a ** 3
        a += b
    for op, k in prog:
        if op == "shear":
            a += k * b
        else:
            y += k * a ** 3
    return y, a, b


def schedule(r: int, c: list[int], w: list[Fraction]) -> list[tuple[str, Fraction]]:
    prog, pos = [], r
    for cj, wj in zip(c, w):
        if cj != pos:
            prog.append(("shear", Fraction(cj - pos)))
        prog.append(("query", -wj))
        pos = cj
    if pos != 0:
        prog.append(("shear", Fraction(-pos)))
    return prog


def program_ok(r: int, prog, rng: random.Random) -> bool:
    for trial in range(12):
        if trial < 6:
            y, a, b = (Fraction(rng.randint(-10**6, 10**6)) for _ in range(3))
        else:
            y, a, b = (Fraction(rng.randint(-999, 999), rng.randint(1, 97)) for _ in range(3))
        got = run_program(r, prog, y, a, b)
        if got != (y + r * a ** 3, a, b):
            return False
    return True


def is_power_of_two(x: int) -> bool:
    return x >= 1 and x & (x - 1) == 0


def covered(r: int) -> bool:
    return (r % 3 == 2 or r in (3, 4) or r % 9 in (0, 1)
            or is_power_of_two(r) or is_power_of_two(r - 1))


def main() -> None:
    rng = random.Random(20261103)

    # 1. Node-condition identity (written proof, corroborated on random triples):
    #    B^3 residual = S1 * (m*e1 - e2 - S1) and closed-form weights agree.
    for _ in range(400):
        r = rng.randint(3, 300)
        c = [Fraction(rng.randint(-500, 500), rng.randint(1, 9)) for _ in range(3)]
        if len(set(c)) < 3:
            continue
        s1 = Fraction(r * (r - 1), 2)
        m = Fraction(2 * r - 1, 3)
        e1 = sum(c)
        e2 = c[0] * c[1] + c[0] * c[2] + c[1] * c[2]
        w, resid = solved_weights(r, c)
        if resid != s1 * (m * e1 - e2 - s1):
            fail("node-condition identity")
        for j in range(3):
            k, l = (i for i in range(3) if i != j)
            if w[j] != s1 * (m - c[k] - c[l]) / ((c[j] - c[k]) * (c[j] - c[l])):
                fail("closed-form weight")
    print("PASS node condition and weight formula on random rational triples")

    # 2. Positive anchor: PR6250's published r=33 weights.
    w33, res33 = solved_weights(33, [Fraction(0), Fraction(16), Fraction(32)])
    if res33 != 0 or w33 != [Fraction(-869, 32), Fraction(341, 16), Fraction(187, 32)]:
        fail("r=33 anchor")
    readme = (ROOT / "research/cubic-equal-step-classification/README.md").read_text("utf-8")
    if "(187/32)(A+32B)^3 + (341/16)(A+16B)^3 - (869/32)A^3" not in readme:
        fail("PR6250 r=33 text not found in pinned input")
    pure_b = (ROOT / "research/cubic-pure-b-boundary/README.md").read_text("utf-8")
    if "| 0, 1, 2, 5, 8 | 3 |" not in pure_b or "| 3, 4, 6, 7 | 4 |" not in pure_b:
        fail("PR6215 residue table not found in pinned input")
    dyadic = (ROOT / "research/dyadic-cubic-repair/README.md").read_text("utf-8")
    if "two queries suffice **only for r=2**" not in dyadic:
        fail("PR6212 two-query statement not found in pinned input")
    print("PASS predecessor anchors (r=33 weights, PR6215 table, PR6212 two-query bound)")

    # 3. Certificates.
    data = json.loads((HERE / "CERTIFICATES.json").read_text("utf-8"))
    certs = data["certificates"]
    expect_unc = [r for r in range(3, data["search"]["max_r"] + 1) if not covered(r)]
    if data["uncovered_arities"] != expect_unc:
        fail("uncovered arity list")
    seen = set()
    for cert in certs:
        r, c = cert["r"], cert["directions"]
        if covered(r) or r in seen or not (c[0] < c[1] < c[2]):
            fail(f"certificate domain r={r}")
        seen.add(r)
        cf = [Fraction(x) for x in c]
        w, resid = solved_weights(r, cf)
        if resid != 0:
            fail(f"B^3 coefficient r={r}")
        if [str(x) for x in w] != cert["weights"]:
            fail(f"recorded weights r={r}")
        if any(x == 0 or not is_dyadic(x) for x in w):
            fail(f"weights not nonzero dyadic r={r}")
        prog = schedule(r, c, w)
        if sum(op == "query" for op, _ in prog) != 3:
            fail(f"query count r={r}")
        if not program_ok(r, prog, rng):
            fail(f"literal execution r={r}")
    if sorted(seen | set(data["no_certificate_in_box"])) != expect_unc:
        fail("certificate/no-certificate partition")
    print(f"PASS {len(certs)} certificates: exact identity, dyadic weights, "
          f"literal dirty execution; arities {sorted(seen)}")

    # 4. Rejection controls (each must be rejected).
    r, c = certs[0]["r"], certs[0]["directions"]
    w, _ = solved_weights(r, [Fraction(x) for x in c])
    good = schedule(r, c, w)
    controls = {
        "perturbed weight": [(op, k + (Fraction(1, 2) if i == 1 else 0)) for i, (op, k) in enumerate(good)],
        "omitted restoring shear": good[:-1] if good[-1][0] == "shear" else good + [("shear", Fraction(1))],
        "query before first shear": [good[1], good[0]] + good[2:],
        "wrong arity": None,
        "omitted query": [step for i, step in enumerate(good) if i != next(j for j, s in enumerate(good) if s[0] == "query")],
    }
    for name, prog in controls.items():
        if name == "wrong arity":
            rejected = not program_ok(r + 1, good, rng)
        else:
            rejected = not program_ok(r, prog, rng)
        if not rejected:
            fail(f"control accepted: {name}")
    if solved_weights(10, [Fraction(0), Fraction(1), Fraction(5)])[1] == 0:
        fail("control accepted: r=10 non-node")
    print(f"PASS {len(controls) + 1} rejection controls")
    print("PASS_CUBIC_THREE_QUERY_ARITIES")


if __name__ == "__main__":
    main()
