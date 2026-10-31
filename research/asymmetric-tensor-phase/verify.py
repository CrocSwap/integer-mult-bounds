#!/usr/bin/env python3
"""Exact corroboration of the asymmetric tensor-phase theorem.

Finite fixtures support PROOF.md; they do not replace its universal argument.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
ENV = runpy.run_path(str(HERE / "envelope.py"))


def check(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    count = 0
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        data = (HERE.parents[1] / row["path"]).read_bytes()
        check(hashlib.sha256(data).hexdigest() == row["sha256"],
              "source digest mismatch: " + row["path"])
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        check(blob == row["git_blob"], "source Git blob mismatch")
        count += 1
    return count


def periodic_arcs(width, tolerance):
    return [(max(F(0), (2 * k - 2 * tolerance) / width),
             min(F(1), (2 * k + 2 * tolerance) / width))
            for k in range(width + 1)
            if max(F(0), (2 * k - 2 * tolerance) / width)
            <= min(F(1), (2 * k + 2 * tolerance) / width)]


def arc_oracle(a, b):
    intervals = [(max(x[0], y[0]), min(x[1], y[1]))
                 for x in periodic_arcs(2, a) for y in periodic_arcs(3, b)
                 if max(x[0], y[0]) <= min(x[1], y[1])]
    return max(hi for _, hi in intervals)


def angular_checks():
    count, boundary = 0, 0
    for i in range(101):
        for j in range(101):
            a, b = F(i, 200), F(j, 200)
            _, value = ENV["angular_envelope"](a, b)
            check(value == arc_oracle(a, b), "angular arc disagreement")
            count += 1
    for i in range(101):
        b = F(i, 200)
        a = (1 - 2 * b) / 3
        branch, value = ENV["angular_envelope"](a, b)
        check(branch == "high" and value == arc_oracle(a, b), "closed threshold")
        if a:
            check(ENV["angular_envelope"](a - F(1, 100000), b)[0] == "low",
                  "left-of-threshold branch")
        boundary += 1
    return {"angular_grid_pairs": count, "exact_jump_points": boundary}


def rational_phase_checks():
    phases = {(F(n * n - m * m, n * n + m * m),
               F(2 * n * m, n * n + m * m))
              for n in range(1, 17) for m in range(17)}
    digest = []
    for c, d in sorted(phases):
        check(c * c + d * d == 1, "nonunit phase")
        s, t, distance = 4 * (1 - c * c), 2 - 2 * (4 * c ** 3 - 3 * c), 2 - 2 * c
        _, _, hi = ENV["squared_envelope"](s, t)
        check(distance <= hi, "literal phase exceeds claimed envelope")
        digest.append([str(s), str(t), str(distance)])
    return {"literal_rational_phases": len(phases),
            "phase_digest": hashlib.sha256(json.dumps(digest).encode()).hexdigest()}


def add(z, w):
    return z[0] + w[0], z[1] + w[1]


def mul(z, w):
    return z[0] * w[0] - z[1] * w[1], z[0] * w[1] + z[1] * w[0]


def conjugate(z):
    return z[0], -z[1]


def matmul(a, b):
    return [[sum_pairs(mul(x, y) for x, y in zip(row, column))
             for column in zip(*b)] for row in a]


def sum_pairs(values):
    result = (F(0), F(0))
    for value in values:
        result = add(result, value)
    return result


def adjoint(a):
    return [[conjugate(x) for x in row] for row in zip(*a)]


def tensor(a, b):
    return [[mul(a[i][j], b[k][l]) for j in range(len(a[0]))
             for l in range(len(b[0]))] for i in range(len(a)) for k in range(len(b))]


def power_tensor(a, width):
    result = [[(F(1), F(0))]]
    for _ in range(width):
        result = tensor(result, a)
    return result


def rotation(c, s):
    return [[(c, F(0)), (-s, F(0))], [(s, F(0)), (c, F(0))]]


def literal_defect(a, b, v, phases, width):
    aa, bb, vv = [power_tensor(x, width) for x in (a, b, v)]
    defect = [[add(x, (-y[0], -y[1])) for x, y in zip(r, q)] for r, q in zip(aa, bb)]
    diagonal = matmul(matmul(adjoint(vv), matmul(adjoint(defect), defect)), vv)
    eigenvalues = []
    for word in itertools.product(phases, repeat=width):
        z = (F(1), F(0))
        for letter in word:
            z = mul(z, letter)
        eigenvalues.append(2 - 2 * z[0])
    for i, row in enumerate(diagonal):
        for j, entry in enumerate(row):
            check(entry == (eigenvalues[i] if i == j else F(0), F(0)),
                  "literal tensor spectral comparison")
    return max(eigenvalues)


def matrix_checks():
    phases = [(F(3, 5), F(4, 5)), (F(-3, 5), F(4, 5)),
              (F(5, 13), F(12, 13)), (F(1), F(0))]
    v, b = rotation(F(5, 13), F(12, 13)), rotation(F(3, 5), F(4, 5))
    count, noncommuting = 0, 0
    for z, w in itertools.product(phases, repeat=2):
        diagonal = [[z, (F(0), F(0))], [(F(0), F(0)), w]]
        u = matmul(matmul(v, diagonal), adjoint(v))
        a = matmul(b, u)
        noncommuting += matmul(a, b) != matmul(b, a)
        defects = [literal_defect(a, b, v, (z, w), j) for j in (1, 2, 3)]
        _, _, hi = ENV["squared_envelope"](*defects[1:])
        check(defects[0] <= hi, "matrix norm exceeds bound")
        count += 1
    check(noncommuting == 12, "noncommuting fixture coverage changed")
    return {"dense_unitary_pairs": count, "noncommuting_pairs": noncommuting,
            "tensor_gram_entries": count * (4 + 16 + 64)}


def rational_jump_checks():
    count = 0
    for j in range(33):
        q = 1 + F(j, 32)
        s, t = 4 - q * q, 2 + (q * q - 3) * q
        branch, lo, hi = ENV["squared_envelope"](s, t)
        check(branch == "high" and lo <= 2 + q <= hi,
              "rational squared-budget jump equality")
        if t > 0:
            delta = min(t / 2, F(1, 1000000))
            check(ENV["squared_envelope"](s, t - delta)[0] == "low",
                  "below algebraic jump")
            count += 1
        if t < 4:
            delta = min((4 - t) / 2, F(1, 1000000))
            check(ENV["squared_envelope"](s, t + delta)[0] == "high",
                  "above algebraic jump")
            count += 1
    return {"rational_jump_points": 33, "one_sided_jump_checks": count}


def controls():
    rejected = 0
    for args in [(-1, 0), (0, 5), (True, 0), (0.5, 0)]:
        try:
            ENV["squared_envelope"](*args)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid budget accepted")
    for bits in (0, 257, True):
        try:
            ENV["squared_envelope"](1, 1, bits)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid enclosure precision accepted")
    for a, b in [(F(1, 6), F(1, 4)), (F(1, 3), F(0)), (F(0), F(1, 2))]:
        check(arc_oracle(a, b) > min(a, 2 * b / 3), "strict-threshold mutant survived")
        rejected += 1
    check(ENV["squared_envelope"](0, 4)[1] == 4, "exact square allows minus one")
    check(ENV["squared_envelope"](4, 0)[1] == 3, "exact cube allows cube root")
    check(ENV["squared_envelope"](0, 0)[2] == 0, "exact pair distinguishes phases")
    check(arc_oracle(F(1, 10), F(2, 5)) != arc_oracle(F(2, 5), F(1, 10)),
          "interchanging unequal budgets was not detected")
    nonunitary = [abs(F(1, 2) ** j - F(-1, 2) ** j) for j in (1, 2, 3)]
    check(nonunitary == [1, 0, F(1, 4)]
          and ENV["squared_envelope"](0, F(1, 16))[2] == 0,
          "nonunitary tensor counterexample was lost")
    return {"invalid_input_controls": 7, "strict_threshold_mutants": 3,
            "width_and_phase_controls": 5, "rejected_controls": rejected + 5}


def run():
    result = {"source_files_authenticated": authenticate()}
    for check_group in (angular_checks, rational_phase_checks, matrix_checks,
                        rational_jump_checks, controls):
        result.update(check_group())
    result["package_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sorted(HERE.iterdir()) if p.is_file()
                                and p.name not in ("RESULT.json", "VALIDATION.md")}
    return result


def validate_receipt(receipt):
    path = HERE / "RESULT.json"
    if path.exists():
        check(json.loads(path.read_text()) == receipt, "committed receipt mismatch")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    receipt = run()
    if args.output:
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(receipt, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        validate_receipt(receipt)
    print("PASS_ASYMMETRIC_TENSOR_PHASE " + json.dumps(receipt, sort_keys=True))
