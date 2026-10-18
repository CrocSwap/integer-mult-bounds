#!/usr/bin/env python3
"""Exact two-role GL3 order-four CNOT certificate. Standard library only."""
from __future__ import annotations

import argparse
from collections import Counter, deque
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
I3 = (1, 2, 4)
H = (2, 4, 7)
PAIRS = tuple((i, j) for i in range(3) for j in range(3) if i != j)
IDEMPOTENTS = tuple((u, v) for u in range(1, 4) for v in range(1, 4)
                    if (u & v).bit_count() % 2)
GENERATORS = tuple((i, j, u, v) for i, j in PAIRS for u, v in IDEMPOTENTS)
I6 = sum(1 << (7 * i) for i in range(6))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows):
    basis = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return len(basis)


def multiply_rows(a, b):
    result = []
    for row in a:
        value = 0
        for j in range(len(b)):
            if row >> j & 1:
                value ^= b[j]
        result.append(value)
    return tuple(result)


def address_gate(i, j):
    rows = list(I3)
    rows[i] ^= 1 << j
    return tuple(rows)


def direct_census():
    words = {I3: ()}
    queue = deque([I3])
    while queue:
        state = queue.popleft()
        for gi, (i, j) in enumerate(PAIRS):
            changed = list(state)
            changed[i] ^= changed[j]
            changed = tuple(changed)
            if changed not in words:
                words[changed] = words[state] + (gi,)
                queue.append(changed)
    return words


def strongly_connected(a):
    for start in range(3):
        reached = {start}
        for _ in range(3):
            reached |= {j for i in tuple(reached) for j in range(3)
                        if i != j and a[i] >> j & 1}
        if len(reached) != 3:
            return False
    return True


def order(a):
    value = I3
    for k in range(1, 169):
        value = multiply_rows(a, value)
        if value == I3:
            return k
    raise ValueError("noninvertible address matrix")


def target_matrix(h=H, active=(True, True)):
    value = 0
    for i in range(3):
        for p in range(2):
            row = h[i] if active[p] else I3[i]
            expanded = sum(1 << (2 * j + p) for j in range(3) if row >> j & 1)
            value |= expanded << (6 * (2 * i + p))
    return value


def natural_step(state, generator):
    i, j, u, v = generator
    source = 0
    if v & 1:
        source ^= (state >> (12 * j)) & 63
    if v & 2:
        source ^= (state >> (12 * j + 6)) & 63
    if u & 1:
        state ^= source << (12 * i)
    if u & 2:
        state ^= source << (12 * i + 6)
    return state


def unpack(state):
    return tuple((state >> (6 * i)) & 63 for i in range(6))


def pack(rows):
    return sum(row << (6 * i) for i, row in enumerate(rows))


def multiply_natural(a, b):
    return pack(multiply_rows(unpack(a), unpack(b)))


def natural_layers(depth=4, generators=GENERATORS):
    seen = {I6}
    layers = [{I6}]
    attempts = 0
    for _ in range(depth):
        following = set()
        for state in layers[-1]:
            for generator in generators:
                attempts += 1
                changed = natural_step(state, generator)
                if changed not in seen:
                    following.add(changed)
        seen.update(following)
        layers.append(following)
    return layers, attempts


def state_hash(states):
    digest = hashlib.sha256()
    for state in sorted(states):
        digest.update(state.to_bytes(5, "little"))
    return digest.hexdigest()


def bounded_meets(layers, target_inverse, left_radius, right_radius):
    left = set().union(*layers[:left_radius + 1])
    right = set().union(*layers[:right_radius + 1])
    return sum(multiply_natural(p, target_inverse) in right for p in left)


class Formal:
    """Four coefficient bitsets in F2[GL3]; never a natural-image oracle."""

    def __init__(self, group):
        self.group = tuple(sorted(group))
        self.index = {g: i for i, g in enumerate(self.group)}
        self.one = 1 << self.index[I3]
        self.permutations = {
            (i, j): tuple(self.index[multiply_rows(address_gate(i, j), g)]
                          for g in self.group) for i, j in PAIRS
        }

    def translate(self, coefficients, pair):
        result = 0
        permutation = self.permutations[pair]
        while coefficients:
            low = coefficients & -coefficients
            result ^= 1 << permutation[low.bit_length() - 1]
            coefficients ^= low
        return result

    def step(self, state, generator):
        i, j, u, v = generator
        result = list(state)
        for column in range(2):
            source = 0
            for q in range(2):
                if v >> q & 1:
                    source ^= state[2 * q + column]
            delta = source ^ self.translate(source, (i, j))
            for p in range(2):
                if u >> p & 1:
                    result[2 * p + column] ^= delta
        return tuple(result)

    def word(self, word, check_alphabet=True):
        state = (self.one, 0, 0, self.one)
        for generator in word:
            if check_alphabet:
                require(generator in GENERATORS, "illegal paid generator")
            state = self.step(state, generator)
        return state

    def target(self, h=H):
        label = 1 << self.index[h]
        return (label, 0, 0, label)

    def natural(self, state):
        rows = [0] * 6
        for p in range(2):
            for q in range(2):
                coefficient = state[2 * p + q]
                for gi, g in enumerate(self.group):
                    if coefficient >> gi & 1:
                        for i in range(3):
                            for j in range(3):
                                if g[i] >> j & 1:
                                    rows[2 * i + p] ^= 1 << (2 * j + q)
        return pack(rows)


def source_checks(package=HERE):
    pins = json.loads((package / "SOURCES.json").read_text())
    root = package.parents[1]
    count = 0
    for entry in pins["files"]:
        if entry["usage"] == "input":
            actual = hashlib.sha256((root / entry["path"]).read_bytes()).hexdigest()
            require(actual == entry["sha256"], "source SHA256 mismatch: " + entry["path"])
            count += 1
    return count


def load_independent():
    spec = importlib.util.spec_from_file_location("gl3_independent", HERE / "independent.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def controls(formal, witness, layers):
    passed = []
    target = formal.target()
    for i in range(len(witness)):
        require(formal.word(witness[:i] + witness[i + 1:]) != target,
                "omitted-call control accepted")
        passed.append("omit-call-" + str(i))
    changed = list(witness)
    i, j, u, v = changed[0]
    changed[0] = (j, i, u, v)
    require(formal.word(changed) != target, "reversed-CNOT control accepted")
    passed.append("reverse-CNOT-direction")
    require(formal.word(tuple(reversed(witness))) != target, "inverse-target control accepted")
    passed.append("reverse-chronology")
    wrong = list(target)
    wrong[1] = formal.one
    require(formal.natural(tuple(wrong)) != target_matrix(), "cross-role leakage accepted")
    passed.append("cross-role-dirty-input-leakage")
    powers = [I3]
    for _ in range(3):
        powers.append(multiply_rows(H, powers[-1]))
    kernel = sum(1 << formal.index[g] for g in powers)
    wrong = list(target)
    wrong[1] ^= kernel
    require(tuple(wrong) != target and formal.natural(tuple(wrong)) == target_matrix(),
            "nonfaithful-image control failed")
    require(kernel.bit_count() == 4, "kernel unexpectedly zero")
    passed.append("natural-image-is-not-formal-equality")
    widened = (formal.one, 0, 0, formal.one)
    for i, j, _, _ in witness[:4]:
        widened = formal.step(widened, (i, j, 1, 1))
        widened = formal.step(widened, (i, j, 2, 2))
    require(widened == target, "rank-two-scope control failed")
    passed.append("rank-two-projector-underpricing")
    invalid = (0, 1, 1, 2)
    try:
        formal.word([invalid])
    except ValueError:
        passed.append("nonidempotent-paid-generator")
    else:
        raise ValueError("nonidempotent generator accepted")
    half = formal.word(witness[:4])
    require(half[0] == target[0] and half[3] != target[3], "second-role control failed")
    passed.append("only-one-role-completed")
    require(bounded_meets(layers, I6, 0, 0) == 1, "identity positive control failed")
    single = target_matrix(active=(True, False))
    single_inverse = target_matrix(multiply_rows(H, multiply_rows(H, H)), (True, False))
    require(bounded_meets(layers, single_inverse, 1, 2) == 0,
            "single-role length-three exclusion failed")
    require(bounded_meets(layers, single_inverse, 2, 2) > 0,
            "single-role length-four positive control failed")
    require(formal.natural(half) == single, "single-role formal/natural mismatch")
    return passed, {"identity_minimum": 0, "single_role_minimum": 4,
                    "kernel_group_elements_rows": [list(g) for g in powers]}


def certificate():
    inputs = source_checks()
    words = direct_census()
    require(len(words) == 168, "GL3 coverage mismatch")
    require(len(words[H]) == 4 and order(H) == 4, "target length/order mismatch")
    require(rank(tuple(a ^ b for a, b in zip(H, I3))) == 2, "rank-gap mismatch")
    candidates = sorted(g for g, w in words.items() if len(w) == 4 and order(g) == 4
                        and rank(tuple(a ^ b for a, b in zip(g, I3))) == 2
                        and strongly_connected(g))
    require(candidates[0] == H, "target selection rule mismatch")
    witness = tuple((*PAIRS[gi], u, u) for u in (1, 2) for gi in words[H])
    formal = Formal(words)
    require(formal.word(witness) == formal.target(), "formal upper witness failed")
    independent = load_independent()
    independent_words, independent_layers, independent_meets = independent.census()
    require({g: len(w) for g, w in words.items()} == independent_words,
            "independent direct distances differ")
    layers, attempts = natural_layers()
    require(layers == independent_layers, "independent full layer sets differ")
    inverse = multiply_rows(H, multiply_rows(H, H))
    meets = bounded_meets(layers, target_matrix(inverse), 3, 4)
    require(meets == 0, "short natural word exists: full formal follow-up required")
    require(independent_meets == meets, "independent meet test differs")
    regular_columns = independent.check_regular(witness, H)
    control_names, fixtures = controls(formal, witness, layers)
    return {
        "schema_version": 1,
        "claim": "FINITE_MINIMUM_EIGHT_EXACTLY_TWO_REGISTERS",
        "target_rows": list(H), "target_order": 4, "target_displacement_rank": 2,
        "address_group_size": len(words),
        "address_distance_layers": [Counter(map(len, words.values()))[i] for i in range(7)],
        "direct_word_chronological": [list(PAIRS[gi]) for gi in words[H]],
        "formal_witness_chronological": [list(g) for g in witness],
        "scalar_idempotents": [list(n) for n in IDEMPOTENTS],
        "paid_generator_count": len(GENERATORS),
        "natural_distance_layers": [len(layer) for layer in layers],
        "natural_layer_sha256": [state_hash(layer) for layer in layers],
        "directed_transition_attempts": attempts,
        "radius_three_size": sum(map(len, layers[:4])),
        "radius_four_size": sum(map(len, layers)),
        "radius_three_four_target_meets": meets,
        "independent_full_layer_comparison": True,
        "independent_target_meets": independent_meets,
        "faithful_regular_basis_columns": regular_columns,
        "positive_fixtures": fixtures, "controls": control_names,
        "live_source_hashes_checked": inputs,
        "not_checked": ["extra scalar registers", "physical supplier realization",
                        "compiler/hosting/precision/tape/analytic transfer", "Lean proof"],
    }


def compare_receipt(actual, expected):
    require(actual == expected, "expected receipt mismatch")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="compute JSON without comparing EXPECTED.json")
    parser.add_argument("--expected", type=Path, default=HERE / "EXPECTED.json")
    args = parser.parse_args()
    actual = certificate()
    if args.emit:
        print(json.dumps(actual, indent=2, sort_keys=True))
    else:
        compare_receipt(actual, json.loads(args.expected.read_text()))
        print("PASS_GL3_ORDER4_REGISTER_CENSUS minimum=8 registers=2 address_group=168 "
              "direct_length=4 natural_short_words=0 regular_columns=336 "
              f"controls={len(actual['controls'])} no_new_kappa")


if __name__ == "__main__":
    main()
