#!/usr/bin/env python3
"""Exact ternary quaternion pair certificate. Apache-2.0."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_NAMES = (
    "README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py", "regular.py"
)
# Group basis: 1,z,i,zi,j,zj,k,zk. This sign is a group coordinate.
AXIS = ((0, 1, 2, 3), (1, 0, 3, 2), (2, 3, 0, 1), (3, 2, 1, 0))
NEG = ((0, 0, 0, 0), (0, 1, 0, 1), (0, 1, 1, 0), (0, 0, 1, 1))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def group_product(a, b):
    x, y = a // 2, b // 2
    return 2 * AXIS[x][y] + (a % 2 + b % 2 + NEG[x][y]) % 2


TABLE = tuple(tuple(group_product(a, b) for b in range(8)) for a in range(8))


def scalar_product(a, b):
    return tuple(
        sum(a[2 * i + k] * b[2 * k + j] for k in range(2)) % 3
        for i in range(2) for j in range(2)
    )


def determinant(p):
    return (p[0] * p[3] - p[1] * p[2]) % 3


def is_projector(p):
    return (len(p) == 4 and all(type(x) is int and 0 <= x < 3 for x in p)
            and (p[0] + p[3]) % 3 == 1 and determinant(p) == 0
            and scalar_product(p, p) == p)


def endpoint(a, b):
    out = [0] * 32
    out[a] = out[24 + b] = 1
    return bytes(out)


def apply_factor(matrix, p, label):
    """Left multiply by I+([label]-[1])p, retaining every formal coefficient."""
    require(len(matrix) == 32 and all(x < 3 for x in matrix), "bad matrix")
    require(is_projector(p) and label in (2, 3, 4, 5), "bad factor")
    out = list(matrix)
    for i, j, k in itertools.product(range(2), repeat=3):
        c = p[2 * i + k]
        if c:
            for h in range(8):
                source = (2 * k + j) * 8 + h
                out[(2 * i + j) * 8 + h] -= c * matrix[source]
                out[(2 * i + j) * 8 + TABLE[label][h]] += c * matrix[source]
    return bytes(value % 3 for value in out)


def ball(start, factors, inverse=False):
    seen, frontier = {start: ()}, {start: ()}
    sizes, transitions = [1], 0
    for _depth in range(2):
        following = {}
        for matrix, word in frontier.items():
            for index, (p, label) in enumerate(factors):
                value = apply_factor(matrix, p, label + 1 if inverse else label)
                transitions += 1
                if value not in seen and value not in following:
                    following[value] = word + (index,)
        sizes.append(len(following))
        seen.update(following)
        frontier = following
    require(len(seen) <= 1 + 24 + 24**2, "ball capacity exceeded")
    return seen, sizes, transitions


def digest(states):
    return hashlib.sha256(b"".join(sorted(states))).hexdigest()


def evaluate(word, factors):
    value = endpoint(0, 0)
    for index in word:
        require(0 <= index < len(factors), "invalid word index")
        value = apply_factor(value, *factors[index])
    return value


def character_matrix(matrix, which):
    weights = (1, 1, 2, 2, 1, 1, 2, 2) if which == 0 else (
        1, 1, 1, 1, 2, 2, 2, 2)
    return tuple(sum(matrix[8 * e + h] * weights[h] for h in range(8)) % 3
                 for e in range(4))


def algebra_checks(projectors, factors):
    for a, b, c in itertools.product(range(8), repeat=3):
        require(TABLE[TABLE[a][b]][c] == TABLE[a][TABLE[b][c]], "associativity")
    require(TABLE[2][2] == TABLE[4][4] == 1, "generator squares")
    require(TABLE[2][4] == 6 and TABLE[4][2] == 7, "noncommuting order")
    invertibles = [s for s in itertools.product(range(3), repeat=4) if determinant(s)]
    closure = 0
    for s in invertibles:
        invdet = determinant(s)
        si = tuple(invdet * x % 3 for x in (s[3], -s[1], -s[2], s[0]))
        require(scalar_product(s, si) == (1, 0, 0, 1), "scalar inverse")
        for p in projectors:
            require(scalar_product(scalar_product(s, p), si) in projectors, "closure")
            closure += 1
    identity = endpoint(0, 0)
    for p, label in factors:
        value = apply_factor(identity, p, label)
        require(apply_factor(value, p, label + 1) == identity, "inverse factor")
        for which in range(2):
            expected = 2 if label == (2, 4)[which] else 1
            require(determinant(character_matrix(value, which)) == expected, "character")
    return {"associativity_triples": 512, "scalar_invertibles": len(invertibles),
            "scalar_conjugations": closure, "factor_inverse_checks": len(factors),
            "factor_character_checks": 2 * len(factors)}


def controls(factors, word, target):
    omissions = 0
    for index in range(len(word)):
        require(evaluate(word[:index] + word[index + 1:], factors) != target, "omission")
        omissions += 1
    planted = evaluate(word[:4], factors)
    forward, _, _ = ball(endpoint(0, 0), factors)
    reverse, _, _ = ball(planted, factors, inverse=True)
    require(bool(forward.keys() & reverse.keys()), "planted meet missed")
    leak = bytearray(target)
    leak[16] = 1
    require(bytes(leak) != target and leak[:8] == target[:8]
            and leak[24:] == target[24:], "dirty off-diagonal control")
    wrong = bytearray(32)
    wrong[2] = wrong[28] = 2
    require(bytes(wrong) != target, "group inverse confused with scalar minus")
    require(character_matrix(target, 0) == (2, 0, 0, 1), "first target character")
    require(character_matrix(target, 1) == (1, 0, 0, 2), "second target character")
    require(character_matrix(endpoint(0, 0), 0) != character_matrix(target, 0), "parity")
    rejected = 0
    for p, g in (((0, 1, 0, 0), 2), ((1, 0, 0, 1), 2), ((1, 0, 0, 0), 0)):
        try:
            apply_factor(target, p, g)
        except ValueError:
            rejected += 1
    require(rejected == 3, "invalid factors admitted")
    return {"omission_rejections": omissions, "planted_four_call_meet": True,
            "dirty_leak_rejection": True, "group_sign_control": True,
            "invalid_factor_rejections": rejected}


def compute():
    projectors = tuple(p for p in itertools.product(range(3), repeat=4) if is_projector(p))
    require(len(projectors) == 12, "incomplete projector set")
    factors = tuple((p, g) for p in projectors for g in (2, 4))
    target = endpoint(3, 5)
    forward, fs, ft = ball(endpoint(0, 0), factors)
    backward, bs, bt = ball(target, factors, inverse=True)
    require(not forward.keys() & backward.keys(), "shorter word found")
    word = (factors.index(((1, 0, 0, 0), 2)),) * 3 + (
        factors.index(((0, 0, 0, 1), 4)),) * 3
    require(evaluate(word, factors) == target, "six-call endpoint")
    return {
        "schema_version": 1, "field": 3, "roles": 2, "exact_minimum": 6,
        "group_basis": ["1", "z", "i", "zi", "j", "zj", "k", "zk"],
        "target_indices": [3, 5], "projectors": projectors, "paid_factors": 24,
        "forward_layers": fs, "reverse_layers": bs,
        "forward_transitions": ft, "reverse_transitions": bt,
        "forward_sha256": digest(forward), "reverse_sha256": digest(backward),
        "meet_intersections": 0, "attaining_word_indices": word,
        "algebra_checks": algebra_checks(projectors, factors),
        "controls": controls(factors, word, target),
        "source_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                          for name in SOURCE_NAMES},
    }


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print a generated receipt")
    args = parser.parse_args()
    actual = compute()
    if args.emit:
        print(json.dumps(actual, indent=2) + "\n", end="")
        return
    expected = json.loads((ROOT / "RESULT.json").read_text(), object_pairs_hook=unique_object)
    require(canonical(actual) == canonical(expected), "receipt differs from recomputation")
    print("PASS_TERNARY_Q8_NEGATIVE_PAIR minimum=6 projectors=12 "
          "forward=491 reverse=491 intersections=0 no_new_kappa")


if __name__ == "__main__":
    main()
