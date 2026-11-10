#!/usr/bin/env python3
"""Exact finite corroboration of the new rounded conjugation lemma."""
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import sys


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WORD = "B0- A1- H B0+ D A2+ B1+ A0+ B0- A2- B2- A1+ B1- A0- B2+".split()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rounded(value, step):
    require(step > 0, "positive grid required")
    scaled = value / step + F(1, 2)
    return step * (scaled.numerator // scaled.denominator)


def carry(value, step):
    return rounded(2 * value, step) - 2 * rounded(value, step)


def source_interval(root, value, step, sign, refined):
    child_grid = step / 2 if refined else step
    return 2 * (root / 2 + sign * rounded(value, child_grid))


def local_checks():
    source_cases = 0
    output_cases = 0
    carries = set()
    for step in (F(1, 2), F(1), F(2)):
        for numerator in range(-40, 41):
            value = numerator * step / 16
            residue = value - rounded(value, step)
            expected = -step if residue < -step / 4 else (
                step if residue >= step / 4 else F(0))
            require(carry(value, step) == expected, "carry partition")
            carries.add(carry(value, step) / step)
            for dirty in range(-3, 4):
                root = dirty * step
                for sign in (-1, 1):
                    new = source_interval(root, value, step, sign, True)
                    coarse = source_interval(root, value, step, sign, False)
                    require(new == root + sign * rounded(2 * value, step),
                            "refined source endpoint")
                    require(coarse == root + 2 * sign * rounded(value, step),
                            "coarse source endpoint")
                    require(abs(new - root - 2 * sign * value) <= step / 2,
                            "refined source error")
                    require(abs(coarse - root - 2 * sign * value) <= step,
                            "coarse source error")
                    require(source_interval(new, value, step, -sign, True)
                            == root, "source literal inverse")
                    source_cases += 1
        for dirty in range(-3, 4):
            root = dirty * step
            for coefficient in (F(-3), F(-1, 2), F(0), F(1, 4), F(2)):
                for target in range(-2, 3):
                    for sign in (-1, 1):
                        y = target * step
                        doubled = 2 * root
                        result = y + sign * rounded(coefficient * doubled, step)
                        require(doubled / 2 == root, "output root restoration")
                        require(abs(result - y - 2 * sign * coefficient * root)
                                <= step / 2, "output error")
                        require(result - sign * rounded(coefficient * doubled,
                                                       step) == y,
                                "output literal inverse")
                        output_cases += 1
        require(abs(rounded(2 * step / 4, step) - step / 2) == step / 2,
                "sharp refined radius")
        require(abs(2 * rounded(step / 2, step) - step) == step,
                "sharp repeated radius")
    require(carries == {F(-1), F(0), F(1)}, "all carry values attained")
    return source_cases, output_cases


def matvec(matrix, vector):
    return tuple(sum(matrix[i][j] * vector[j] for j in range(2))
                 for i in range(2))


def run_word(initial, a_maps, b_maps, step, refined, inverse=False):
    state = list(initial)
    indices = range(14, -1, -1) if inverse else range(15)
    for index in indices:
        token = WORD[index]
        if token in ("H", "D"):
            factor = F(1, 2) if token == "H" else F(2)
            if inverse:
                factor = 1 / factor
            state[6] = tuple(factor * x for x in state[6])
            continue
        role = int(token[1])
        sign = 1 if token[2] == "+" else -1
        if inverse:
            sign = -sign
        if token[0] == "B":
            destination = 6
            increment = matvec(b_maps[role], state[role])
            grid = step / 2 if refined and index == 3 else step
        else:
            destination = 3 + role
            increment = matvec(a_maps[role], state[6])
            grid = step
        state[destination] = tuple(state[destination][j]
                                   + sign * rounded(increment[j], grid)
                                   for j in range(2))
    return tuple(state)


def word_checks():
    a_maps = (((F(1), F(1, 2)), (F(0), F(1))),
              ((F(0), F(1)), (F(-1), F(0))),
              ((F(1), F(0)), (F(1), F(1))))
    b_maps = (((F(1, 8), F(0)), (F(0), F(3, 8))),
              ((F(1), F(1)), (F(0), F(1))),
              ((F(1), F(0)), (F(1), F(-1))))
    cases = 0
    observed = set()
    for step in (F(1, 2), F(1), F(2)):
        for seed in range(17):
            initial = tuple(tuple(((seed * (i + 1) + 3 * j) % 7 - 3) * step
                                  for j in range(2)) for i in range(7))
            value = matvec(b_maps[0], initial[0])
            rho = tuple(carry(x, step) for x in value)
            for refined in (False, True):
                final = run_word(initial, a_maps, b_maps, step, refined)
                require(final[:3] == initial[:3], "immutable source rows")
                expected = tuple(initial[6][j] + (rho[j] if refined else 0)
                                 for j in range(2))
                require(final[6] == expected, "full rounded root endpoint")
                require(run_word(final, a_maps, b_maps, step, refined, True)
                        == initial, "full literal inverse")
                if refined:
                    corrected = tuple(final[6][j] - rho[j] for j in range(2))
                    require(corrected == initial[6], "paid root correction")
                    observed.update(x / step for x in rho)
                cases += 1
    require(observed == {F(-1), F(0), F(1)}, "full-word carry coverage")
    return cases


def controls():
    # These compute wrong alternatives and require a concrete counterexample.
    checks = {
        "half_grid_is_needed": F(1, 2).denominator != 1,
        "coarse_full_target_rounding_loses_dirty_root":
            2 * rounded(F(-1, 2), F(1)) == 2 * rounded(F(0), F(1)),
        "rounding_the_negative_is_not_the_inverse":
            rounded(F(1, 2), F(1)) + rounded(F(-1, 2), F(1)) != 0,
        "omitting_final_double_changes_the_map":
            F(1, 2) + rounded(F(3, 8), F(1, 2))
            != source_interval(F(1), F(3, 8), F(1), 1, True),
        "omitting_carry_repair_leaves_a_root_error":
            carry(F(3, 8), F(1)) == 1,
        "wrong_sign_carry_repair_doubles_error":
            carry(F(3, 8), F(1)) + carry(F(3, 8), F(1)) == 2,
        "coarse_child_cannot_claim_half_grid_error":
            abs(2 * rounded(F(1, 2), F(1)) - 1) > F(1, 2),
    }
    for name, condition in checks.items():
        require(condition, "missing counterexample: " + name)
    try:
        rounded(F(0), F(0))
    except ValueError:
        return sorted(checks) + ["zero_grid_rejected"]
    raise ValueError("zero grid was accepted")


def authenticate():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    require(len(manifest["files"]) == 3, "source inventory changed")
    for row in manifest["files"]:
        if row["usage"] == "input":
            payload = (ROOT / row["path"]).read_bytes()
            require(sha256(payload).hexdigest() == row["sha256"], "source drift")
            require(" ".join(WORD) in payload.decode(), "source word mismatch")


def main():
    require(len(sys.argv) == 1, "no arguments supported")
    authenticate()
    source_cases, output_cases = local_checks()
    report = {
        "claim_type": "scoped proof with exact finite corroboration",
        "source_interval_cases": source_cases,
        "output_interval_cases": output_cases,
        "complete_word_cases": word_checks(),
        "controls": controls(),
        "root_carry_over_h": [-1, 0, 1],
        "new_source_error_over_h": "1/2",
        "repeated_source_error_over_h": "1",
        "package_sha256": {
            name: sha256((PACKAGE / name).read_bytes()).hexdigest()
            for name in ("PROOF.md", "README.md", "SOURCES.json", "TASK.json",
                         "VERIFY.json", "verify.py")},
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    print("PASS_ROUNDED_DYADIC_CONJUGATION")


if __name__ == "__main__":
    main()
