#!/usr/bin/env python3
"""Exact depth-four search in F2[SL2(F3)] for a heterogeneous triple."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CERTIFICATE = ROOT / "CERTIFICATE.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL_SL2F3_CONJUGATE_TRIPLE: " + message)


def mat2_mul(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        sum(a[2 * r + k] * b[2 * k + c] for k in range(2)) % 3
        for r in range(2)
        for c in range(2)
    )


def mat2_det(a: tuple[int, ...]) -> int:
    return (a[0] * a[3] - a[1] * a[2]) % 3


def build_group():
    elements = sorted(
        (a, b, c, d)
        for a in range(3)
        for b in range(3)
        for c in range(3)
        for d in range(3)
        if (a * d - b * c) % 3 == 1
    )
    index = {g: i for i, g in enumerate(elements)}
    identity = index[(1, 0, 0, 1)]
    table = tuple(
        tuple(index[mat2_mul(a, b)] for b in elements) for a in elements
    )
    inverses = tuple(
        next(j for j in range(len(elements)) if table[i][j] == identity and table[j][i] == identity)
        for i in range(len(elements))
    )
    return elements, index, identity, table, inverses


ELEMENTS, GROUP_INDEX, E, GROUP_MUL, GROUP_INV = build_group()
I2 = GROUP_INDEX[(0, 1, 2, 0)]
W = GROUP_INDEX[(0, 2, 1, 2)]
IW = GROUP_INV[W]
C = GROUP_MUL[GROUP_MUL[IW][I2]][W]
GENERATOR_IDS = (I2, GROUP_INV[I2], W, IW)
GENERATOR_NAMES = ("i", "i^-1", "w", "w^-1")


def group_power(g: int, n: int) -> int:
    out = E
    for _ in range(n):
        out = GROUP_MUL[out][g]
    return out


def generator_word_distance(target: int) -> int:
    frontier = [E]
    seen = {E: 0}
    while frontier:
        g = frontier.pop(0)
        if g == target:
            return seen[g]
        for h in GENERATOR_IDS:
            gh = GROUP_MUL[g][h]
            if gh not in seen:
                seen[gh] = seen[g] + 1
                frontier.append(gh)
    raise RuntimeError("target not generated")


def right_translate(mask: int, g: int) -> int:
    """Right-multiply a basis support by one group element over F2."""
    out = 0
    while mask:
        bit = mask & -mask
        a = bit.bit_length() - 1
        out |= 1 << GROUP_MUL[a][g]
        mask ^= bit
    return out


def left_translate(mask: int, g: int) -> int:
    """Left-multiply a basis support by one group element over F2."""
    out = 0
    while mask:
        bit = mask & -mask
        a = bit.bit_length() - 1
        out |= 1 << GROUP_MUL[g][a]
        mask ^= bit
    return out


def identity_state() -> tuple[int, ...]:
    one = 1 << E
    return tuple(one if r == c else 0 for r in range(3) for c in range(3))


def right_call(state: tuple[int, ...], call: tuple[int, int, int]) -> tuple[int, ...]:
    """Return state * (I + ([g]+[e]) x y^T), exactly over F2[G]."""
    g, x, y = call
    out = list(state)
    for r in range(3):
        accumulated = 0
        for k in range(3):
            if (x >> k) & 1:
                accumulated ^= state[3 * r + k]
        delta = accumulated ^ right_translate(accumulated, g)
        for c in range(3):
            if (y >> c) & 1:
                out[3 * r + c] ^= delta
    return tuple(out)


def direct_gate(call: tuple[int, int, int]) -> tuple[int, ...]:
    """Construct I+([g]+[e])N entry by entry, independent of right_call."""
    g, x, y = call
    one = 1 << E
    out = []
    for r in range(3):
        for c in range(3):
            support = one if r == c else 0
            if ((x >> r) & 1) and ((y >> c) & 1):
                support ^= one ^ (1 << g)
            out.append(support)
    return tuple(out)


def convolution(a: int, b: int) -> int:
    """Independent full coefficient multiplication in F2[G]."""
    out = 0
    aa = a
    while aa:
        abit = aa & -aa
        ga = abit.bit_length() - 1
        bb = b
        while bb:
            bbit = bb & -bb
            gb = bbit.bit_length() - 1
            out ^= 1 << GROUP_MUL[ga][gb]
            bb ^= bbit
        aa ^= abit
    return out


def formal_matrix_product(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    out = [0] * 9
    for r in range(3):
        for c in range(3):
            value = 0
            for k in range(3):
                value ^= convolution(a[3 * r + k], b[3 * k + c])
            out[3 * r + c] = value
    return tuple(out)


def word_state(calls: tuple[tuple[int, int, int], ...]) -> tuple[int, ...]:
    state = identity_state()
    for call in calls:
        state = right_call(state, call)
    return state


def target_state(diagonal: tuple[int, int, int]) -> tuple[int, ...]:
    out = [0] * 9
    for r, g in enumerate(diagonal):
        out[3 * r + r] = 1 << g
    return tuple(out)


def left_diagonal(state: tuple[int, ...], diagonal: tuple[int, int, int]) -> tuple[int, ...]:
    return tuple(
        left_translate(state[3 * r + c], diagonal[r])
        for r in range(3)
        for c in range(3)
    )


def pair_state(a: int, b: int, gates):
    return right_call(gates[a], CALLS[b])


def make_calls():
    calls = []
    for g in GENERATOR_IDS:
        for x in range(1, 8):
            for y in range(1, 8):
                dot = sum(((x >> k) & 1) * ((y >> k) & 1) for k in range(3)) & 1
                if dot == 1:
                    calls.append((g, x, y))
    return tuple(calls)


CALLS = make_calls()
CALL_NAMES = {g: name for g, name in zip(GENERATOR_IDS, GENERATOR_NAMES)}


def idempotent_name(x: int, y: int) -> str:
    def vec(v):
        return "".join(str((v >> k) & 1) for k in range(3))
    return f"{vec(x)}*{vec(y)}^T"


def call_name(call: tuple[int, int, int]) -> str:
    g, x, y = call
    return f"D[{CALL_NAMES[g]};{idempotent_name(x, y)}]"


def make_direct_word(call_index):
    def at(g: int, role: int):
        e = 1 << role
        return call_index[(g, e, e)]

    return (
        at(I2, 0),
        at(W, 1),
        at(IW, 2),
        at(I2, 2),
        at(W, 2),
    )


def search_minimum(target: tuple[int, ...], diagonal: tuple[int, int, int], gates, pair_words, call_inverse):
    one_words = {gates[i]: (i,) for i in range(len(CALLS))}
    if target == identity_state():
        return ()
    if target in one_words:
        return one_words[target]
    if target in pair_words:
        return pair_words[target]

    # Every three-call word splits 1+2. Every four-call word splits 2+2.
    # For a suffix b1 b2, its inverse is b2^-1 b1^-1.
    for suffix_state, (a, b) in pair_words.items():
        inv_suffix = pair_state(call_inverse[b], call_inverse[a], gates)
        need_prefix = left_diagonal(inv_suffix, diagonal)
        if need_prefix in one_words:
            return one_words[need_prefix] + (a, b)

    for suffix_state, (a, b) in pair_words.items():
        inv_suffix = pair_state(call_inverse[b], call_inverse[a], gates)
        need_prefix = left_diagonal(inv_suffix, diagonal)
        if need_prefix in pair_words:
            return pair_words[need_prefix] + (a, b)
    return None


def state_digest(states) -> str:
    digest = hashlib.sha256()
    for state in sorted(states):
        for coefficient_support in state:
            digest.update(coefficient_support.to_bytes(3, "little"))
    return digest.hexdigest()


def controls(gates, call_index, direct, target):
    direct_state = word_state(tuple(CALLS[i] for i in direct))
    require(direct_state == target, "direct five-call identity failed")
    for pos in range(len(direct)):
        reduced = direct[:pos] + direct[pos + 1 :]
        require(word_state(tuple(CALLS[i] for i in reduced)) != target,
                f"omission control unexpectedly passed at direct position {pos}")
    wrong = list(direct)
    old = CALLS[wrong[-1]]
    wrong[-1] = call_index[(GROUP_INV[old[0]], old[1], old[2])]
    require(word_state(tuple(CALLS[i] for i in wrong)) != target,
            "mutated-generator control unexpectedly passed")
    positive = target_state((I2, W, E))
    positive_word = (call_index[(I2, 1, 1)], call_index[(W, 2, 2)])
    require(word_state(tuple(CALLS[i] for i in positive_word)) == positive,
            "two-call positive control failed")
    return positive_word


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write the deterministic coverage certificate")
    args = parser.parse_args()

    require(len(ELEMENTS) == 24, "SL2(F3) must have 24 elements")
    require(len(GENERATOR_IDS) == 4 and len(set(GENERATOR_IDS)) == 4,
            "the paid address generators must be four distinct elements")
    require(len(CALLS) == 112, "expected 4 times 28 paid gates")
    require(all(GROUP_MUL[GROUP_MUL[a][b]][c] == GROUP_MUL[a][GROUP_MUL[b][c]]
                for a in range(24) for b in range(24) for c in range(24)),
            "group multiplication table is not associative")
    generated = {E}
    frontier = [E]
    while frontier:
        a = frontier.pop()
        for g in GENERATOR_IDS:
            b = GROUP_MUL[a][g]
            if b not in generated:
                generated.add(b)
                frontier.append(b)
    require(len(generated) == 24, "i and w do not generate all of SL2(F3)")
    require(group_power(I2, 4) == E and group_power(I2, 2) != E,
            "i must have order four")
    require(group_power(W, 3) == E and W != E,
            "w must have order three")
    require(group_power(C, 4) == E and group_power(C, 2) != E,
            "c must have order four")
    require(generator_word_distance(C) == 3, "the stated three-letter direct word is not shortest")

    gates = tuple(right_call(identity_state(), call) for call in CALLS)
    require(all(gates[i] == direct_gate(call) for i, call in enumerate(CALLS)),
            "rank-one update and direct gate construction disagree")
    call_index = {call: i for i, call in enumerate(CALLS)}
    call_inverse = tuple(
        call_index[(GROUP_INV[g], x, y)] for g, x, y in CALLS
    )
    identity = identity_state()
    for k, gate in enumerate(gates):
        require(right_call(gate, CALLS[call_inverse[k]]) == identity,
                f"inverse formula failed for {call_name(CALLS[k])}")

    target_diagonal = (I2, W, C)
    target = target_state(target_diagonal)
    direct = make_direct_word(call_index)
    positive_word = controls(gates, call_index, direct, target)

    pair_words = {}
    for a, gate in enumerate(gates):
        for b, call in enumerate(CALLS):
            state = right_call(gate, call)
            require(state == formal_matrix_product(gate, gates[b]),
                    f"rank-one transition disagrees with full convolution at pair ({a},{b})")
            pair_words.setdefault(state, (a, b))

    found = search_minimum(target, target_diagonal, gates, pair_words, call_inverse)
    if found is None:
        minimum = 5  # The exact search excludes lengths 0..4; direct word attains 5.
        witness = direct
    else:
        minimum = len(found)
        witness = found
        require(word_state(tuple(CALLS[i] for i in witness)) == target,
                "reported short witness fails full group-algebra replay")
    require(minimum <= 5, "direct word did not bound the exact minimum")

    positive_pairs = {}
    for a, gate in enumerate(gates):
        for b, call in enumerate(CALLS):
            positive_pairs.setdefault(right_call(gate, call), (a, b))
    positive_target = target_state((I2, W, E))
    positive_minimum = search_minimum(
        positive_target, (I2, W, E), gates, positive_pairs, call_inverse
    )
    require(positive_minimum is not None and len(positive_minimum) == 2
            and word_state(tuple(CALLS[i] for i in positive_minimum)) == positive_target,
            "search failed its known two-call positive control")

    cert = {
        "schema_version": 1,
        "model": "M3(F2[SL2(F3)])",
        "group_order": len(ELEMENTS),
        "group_generated_by": ["i", "i^-1", "w", "w^-1"],
        "i_matrix_mod3": [[0, 1], [2, 0]],
        "w_matrix_mod3": [[0, 2], [1, 2]],
        "target_c": "w^-1*i*w",
        "target_diagonal": ["i", "w", "c"],
        "rank_one_idempotents": 28,
        "paid_call_alphabet": len(CALLS),
        "direct_paid_bill": 5,
        "search_depth": 4,
        "one_call_states": len(set(gates)),
        "two_call_words": len(CALLS) ** 2,
        "two_call_distinct_states": len(pair_words),
        "two_call_full_convolution_cross_checks": len(CALLS) ** 2,
        "two_call_state_sha256": state_digest(pair_words),
        "result_minimum": minimum,
        "short_witness_indices": list(witness) if len(witness) <= 4 else None,
        "short_witness": [call_name(CALLS[i]) for i in witness] if len(witness) <= 4 else None,
        "positive_control_minimum": len(positive_minimum),
        "direct_word": [call_name(CALLS[i]) for i in direct],
        "omission_controls": len(direct),
        "mutated_generator_control": True,
        "free_scalar_mixing_covered": True,
        "limitations": [
            "finite nonabelian address algebra only",
            "address-operation implementation cost not priced",
            "no selected supplier or kappa change claimed",
        ],
    }

    if args.write:
        CERTIFICATE.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        require(CERTIFICATE.exists(), "missing CERTIFICATE.json; run verify.py --write after review")
        expected = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
        require(cert == expected, "recomputed certificate differs from CERTIFICATE.json")

    print(
        "PASS_SL2F3_CONJUGATE_TRIPLE "
        f"group=24 calls={len(CALLS)} target_minimum={minimum} "
        f"pair_words={len(CALLS)**2} distinct_pair_states={len(pair_words)} "
        f"short_witness={'yes' if len(witness) <= 4 else 'none'}"
    )


if __name__ == "__main__":
    main()
