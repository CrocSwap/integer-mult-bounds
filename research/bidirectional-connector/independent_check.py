#!/usr/bin/env python3
"""Separate dense F2 matrix replay; imports no primary or predecessor checker.

conorholds, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
NAMES = [f"x{j}" for j in range(5)] + [f"y{m}" for m in range(1, 32)] + ["z0", "z1"]


def ensure(ok, reason):
    if not ok:
        raise ValueError(reason)


def apply(matrix, vector):
    return sum(((row & vector).bit_count() % 2) << i for i, row in enumerate(matrix))


def replay(word, incoming, matrices):
    state = dict(incoming)
    for record in word:
        kind = record[0]
        if kind == "B":
            _, j, p = record
            state[f"z{p}"] ^= apply(matrices[f"B{j}"], state[f"x{j}"])
        elif kind == "A":
            _, mask, p = record
            state[f"y{mask}"] ^= apply(matrices[f"A{mask}"], state[f"z{p}"])
        elif kind == "C":
            _, p = record
            state[f"z{p}"] ^= state[f"z{1-p}"]
        else:
            raise ValueError("unknown dense instruction")
    return state


def direct(incoming, matrices, n=5):
    state = dict(incoming)
    for mask in range(1, 1 << n):
        for j in range(n):
            if mask & (1 << j):
                state[f"y{mask}"] ^= apply(matrices[f"A{mask}"],
                                            apply(matrices[f"B{j}"], incoming[f"x{j}"]))
    return state


def comparator_word(reference):
    # Build placements independently, scanning each boundary and each target.
    skeleton = reference["skeleton"]
    word = []
    for slot in range(len(skeleton) + 1):
        for mask in range(1, 32):
            for boundary, port in reference["readouts"][str(mask)]:
                if boundary == slot:
                    word.append(["A", mask, port])
        if slot < len(skeleton):
            op = skeleton[slot]
            word.append(["C", 0] if op[0] == "C" else op)
    return word


def banks(width, n=5):
    identity = [1 << i for i in range(width)]
    rng = random.Random(1009 + width)
    random_maps = {f"{kind}{index}": [rng.randrange(1 << width) for _ in range(width)]
                   for kind, indices in (("B", range(n)), ("A", range(1, 1 << n)))
                   for index in indices}
    all_identity = {name: list(identity) for name in random_maps}
    singular = {name: [0] * width if name == "B0" else [1] + [0] * (width - 1)
                for name in random_maps}
    if width >= 2:
        # Explicit E12 / E21 on the first two coordinates: noncommuting and singular.
        random_maps["B0"] = [2, 0] + [0] * (width - 2)
        random_maps["A1"] = [0, 1] + [0] * (width - 2)
        ensure(apply(random_maps["A1"], apply(random_maps["B0"], 2)) !=
               apply(random_maps["B0"], apply(random_maps["A1"], 2)), "commutation control")
    return [all_identity, singular, random_maps]


def run():
    cert = json.loads((HERE / "CERTIFICATE.json").read_text())
    reference = json.loads((HERE / "references/PR1615-CERTIFICATE.json").read_text())
    programs = [cert["word"], comparator_word(reference)]
    cases = 0
    for width in (1, 2, 3, 5):
        zero = dict.fromkeys(NAMES, 0)
        inputs = []
        for role in NAMES:
            for column in range(width):
                state = dict(zero)
                state[role] = 1 << column
                inputs.append(state)
        rng = random.Random(881 + width)
        inputs += [{role: rng.randrange(1 << width) for role in NAMES} for _ in range(8)]
        for matrices in banks(width):
            for incoming in inputs:
                want = direct(incoming, matrices)
                for word in programs:
                    actual = replay(word, incoming, matrices)
                    ensure(actual == want, "dense arbitrary-dirty endpoint mismatch")
                    ensure(replay(list(reversed(word)), actual, matrices) == incoming, "dense inverse mismatch")
                    cases += 1
    # Independently reject every single omission using full incoming basis vectors.
    mutations = 0
    for word in programs:
        matrices = banks(2)[2]
        basis = []
        for role in NAMES:
            for bit in (1, 2):
                state = dict.fromkeys(NAMES, 0)
                state[role] = bit
                basis.append(state)
        for index in range(len(word)):
            changed = word[:index] + word[index + 1:]
            # One concrete bank can mask omissions through singular maps, so
            # also use the identity bank; acceptance requires both to agree.
            ensure(any(replay(changed, state, bank) != direct(state, bank)
                       for bank in (matrices, banks(2)[0]) for state in basis),
                   "dense omission control accepted")
            mutations += 1
    print(f"PASS_INDEPENDENT_BIDIRECTIONAL cases={cases} directions=2 "
          f"widths=1,2,3,5 omission_controls={mutations} no_new_kappa")
    return cases, mutations


def check_palette():
    literal = json.loads((HERE / "PALETTE6.json").read_text())
    n = literal["sources"]; word = literal["word"]
    ensure(n == 6, "palette domain")
    names = [f"x{j}" for j in range(n)] + [f"y{m}" for m in range(1, 1 << n)] + ["z0", "z1"]
    cases = 0
    for width in (1, 2, 3, 5):
        inputs = []
        for name in names:
            for bit in range(width):
                state = dict.fromkeys(names, 0); state[name] = 1 << bit; inputs.append(state)
        rng = random.Random(711 + width)
        inputs.extend({name: rng.randrange(1 << width) for name in names} for _ in range(8))
        for bank in banks(width, n):
            for state in inputs:
                actual = replay(word, state, bank)
                ensure(actual == direct(state, bank, n), "palette dense endpoint")
                ensure(replay(list(reversed(word)), actual, bank) == state, "palette dense inverse")
                cases += 1
    basis = []
    for name in names:
        for bit in (1, 2):
            state = dict.fromkeys(names, 0); state[name] = bit; basis.append(state)
    for index in range(len(word)):
        changed = word[:index] + word[index+1:]
        ensure(any(replay(changed, state, bank) != direct(state, bank, n)
                   for bank in (banks(2, n)[0], banks(2, n)[2]) for state in basis),
               "palette dense omission accepted")
    print(f"PASS_INDEPENDENT_PALETTE sources=6 cases={cases} directions=2 omissions={len(word)}")


if __name__ == "__main__":
    run()
    check_palette()
