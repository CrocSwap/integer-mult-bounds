#!/usr/bin/env python3
"""Independent flattened matrix oracle; imports no polynomial-checker code.

Philipp / mightyOil, with substantial OpenAI Codex assistance. Apache-2.0.
These finite substitutions test the implementation; universality comes from
the free-polynomial normal forms and the accompanying algebraic argument.
"""
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]


def subtract(a, b):
    return [[u - v for u, v in zip(r, s)] for r, s in zip(a, b)]


def sum_matrix(a, b):
    return [[u + v for u, v in zip(r, s)] for r, s in zip(a, b)]


def chain(*args):
    out = args[0]
    for arg in args[1:]:
        out = multiply(out, arg)
    return out


def matrices(d, scratch, trial):
    rng = random.Random(810000 + 100 * d + 10 * scratch + trial)
    sizes = [d, d, d, scratch]
    cuts = [0, d, 2 * d, 3 * d, 3 * d + scratch]
    n = cuts[-1]
    I = eye(n)
    mats = {}
    substitutions = {}
    for name in "PQRS":
        m = [[rng.randint(-2, 2) for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if (name in "PQ" and d <= j < 2 * d) or (name in "RS" and i < d):
                    m[i][j] = I[i][j]
        mats[name] = m
        for bi in range(4):
            for bj in range(4):
                substitutions[f"{name}_{bi}{bj}"] = [r[cuts[bj]:cuts[bj + 1]] for r in m[cuts[bi]:cuts[bi + 1]]]
    for name in "AB":
        substitutions[name] = [[rng.randint(-2, 2) for _ in range(d)] for _ in range(d)]
    return mats, substitutions, sizes, cuts


def embed(block, row, col, cuts):
    n = cuts[-1]
    out = [[0] * n for _ in range(n)]
    for i, line in enumerate(block):
        for j, value in enumerate(line):
            out[cuts[row] + i][cuts[col] + j] = value
    return out


def direct(m, values, cuts):
    I = eye(cuts[-1])
    H = embed(values["B"], 2, 0, cuts)
    E = embed(values["A"], 1, 2, cuts)
    U, Ui = sum_matrix(I, H), subtract(I, H)
    V, Vi = sum_matrix(I, E), subtract(I, E)
    # Obtain full parent from four actual dense maps, not the claimed shear.
    F, Fi = chain(Vi, Ui, V, U), chain(Ui, Vi, U, V)
    end = [m["P"], chain(m["Q"], U), chain(m["P"], Ui, V, U), chain(m["Q"], F)]
    inv = [m["R"], chain(Ui, m["S"]), chain(Ui, Vi, U, m["R"]), chain(Fi, m["S"])]
    out = {f"phase_{i}_to_{j}": multiply(end[j], inv[i]) for i in range(4) for j in range(4)}
    out.update(completed_parent=F, completed_parent_inverse=Fi)
    return out


def substitute(encoded, values, sizes, cuts):
    n = cuts[-1]
    out = [[0] * n for _ in range(n)]
    for entry in encoded:
        i, j = entry["row"], entry["column"]
        if not sizes[i] or not sizes[j]:
            continue
        for term in entry["terms"]:
            word = term["word"]
            # An intermediate zero-dimensional block annihilates this word.
            blocks = [values[s] for s in word]
            if any(not b or not b[0] for b in blocks):
                continue
            value = chain(*blocks) if blocks else eye(sizes[i])
            for u in range(sizes[i]):
                for v in range(sizes[j]):
                    out[cuts[i] + u][cuts[j] + v] += term["coefficient"] * value[u][v]
    return out


def run():
    receipt = json.loads((HERE / "CERTIFICATE.json").read_text())
    count = 0
    for d, scratch in [(1, 0), (1, 1), (2, 1), (1, 3), (2, 3), (3, 2)]:
        for trial in range(5):
            m, values, sizes, cuts = matrices(d, scratch, trial)
            actual = direct(m, values, cuts)
            for name, row in receipt["identities"].items():
                if actual[name] != substitute(row["normal_form"], values, sizes, cuts):
                    raise ValueError("dense normal-form disagreement " + name)
                count += 1
    # Concrete invertible shear counterexamples. All unspecified blocks are I,
    # A=B=1, and exactly one of the four invariants is removed at a time.
    witnesses = {}
    for name, (label, position, phase) in {
        "P": ("P_does_not_fix_y", (3, 1), "phase_0_to_2"),
        "Q": ("Q_does_not_fix_y", (3, 1), "phase_0_to_3"),
        "R": ("R_does_not_preserve_x", (0, 3), "phase_0_to_3"),
        "S": ("S_does_not_preserve_x", (0, 3), "phase_1_to_3"),
    }.items():
        cuts = [0, 1, 2, 3, 4]
        m = {k: eye(4) for k in "PQRS"}
        m[name][position[0]][position[1]] += 1
        values = {f"{k}_{i}{j}": [[m[k][i][j]]] for k in "PQRS" for i in range(4) for j in range(4)}
        values.update(A=[[1]], B=[[1]], FAULT=[[1]])
        actual = direct(m, values, cuts)[phase]
        # The generic normal form assumes the invariant and erases the fault;
        # use the residual certificate itself to check the exact defect.
        expected = substitute(receipt["interface_controls"][label]["failed_identities"][phase], values, [1] * 4, cuts)
        # Recompute the stated RHS directly, preserving the removed invariant.
        E, H = embed([[1]], 1, 2, cuts), embed([[1]], 2, 0, cuts)
        U, Vi = sum_matrix(eye(4), H), subtract(eye(4), E)
        G = multiply(E, H)
        if phase == "phase_0_to_2":
            rhs = sum_matrix(multiply(m["P"], m["R"]), chain(E, U, m["R"]))
        elif phase == "phase_1_to_3":
            rhs = subtract(multiply(m["Q"], m["S"]), chain(m["Q"], Vi, H))
        else:
            rhs = sum_matrix(multiply(m["Q"], m["R"]), G)
        defect = subtract(actual, rhs)
        if defect != expected or not any(v for row in defect for v in row):
            raise ValueError("counterexample missing or wrong: " + label)
        witnesses[label] = {"phase": phase, "fault_entry": list(position), "residual": defect}
    return {"status": "PASS_DENSE_PHASE_ORACLE", "substitutions": count, "counterexamples": witnesses}


if __name__ == "__main__":
    result = run()
    expected = json.loads((HERE / "DENSE-CHECK.json").read_text())
    if result != expected:
        raise ValueError("dense receipt mismatch")
    print(result["status"] + " substitutions=" + str(result["substitutions"]))
