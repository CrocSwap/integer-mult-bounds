#!/usr/bin/env python3
"""Exact rank-one-idempotent word search in F2[D10] on three registers."""
from __future__ import annotations

import hashlib
import json
from itertools import product
from pathlib import Path

NREG = 3
NGROUP = 10
MASK = (1 << NREG) - 1
IDENTITY_MATRIX = sum(1 << (i * NREG + i) for i in range(NREG))


def group_mul(a: int, b: int) -> int:
    """Encode D10 elements r^k s^e by 2*k+e; r=st, s^2=t^2=1."""
    ka, ea = divmod(a, 2)
    kb, eb = divmod(b, 2)
    k = (ka + (-kb if ea else kb)) % 5
    return 2 * k + (ea ^ eb)


E = 0
S = 1
T = 9  # s*r = r^-1*s, since t=s*r and r=st
R = 2
R_INV = 8


def mat_mul(a: int, b: int) -> int:
    """Multiply encoded 3x3 matrices over F2."""
    out = 0
    for i in range(NREG):
        row = (a >> (i * NREG)) & MASK
        for j in range(NREG):
            col = sum(((b >> (k * NREG + j)) & 1) << k for k in range(NREG))
            if (row & col).bit_count() & 1:
                out |= 1 << (i * NREG + j)
    return out


MATMUL = [[mat_mul(a, b) for b in range(1 << 9)] for a in range(1 << 9)]


def mat_rank(a: int) -> int:
    rows = [(a >> (i * NREG)) & MASK for i in range(NREG)]
    rank = 0
    for col in range(NREG):
        pivot = next((i for i in range(rank, NREG) if (rows[i] >> col) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(NREG):
            if i != rank and ((rows[i] >> col) & 1):
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def rank_one_idempotents() -> list[int]:
    vals = set()
    for x in range(1, 1 << NREG):
        for y in range(1, 1 << NREG):
            if (x & y).bit_count() & 1:
                n = sum((((x >> i) & 1) * (((y >> j) & 1)) << (i * NREG + j))
                        for i in range(NREG) for j in range(NREG))
                vals.add(n)
    result = sorted(vals)
    assert len(result) == 28
    assert all(MATMUL[n][n] == n and mat_rank(n) == 1 for n in result)
    return result


PROJECTORS = rank_one_idempotents()
EXPECTED_PRIMARY_DIGESTS = {
    0: "992d20f65528722d3c9f89c6ecd3876deae0d0084d271d8dffa254f1e21dfeae",
    1: "75d31c5b61a5e4704d487416541aae736b9a7d35a809c094a12b80a465a57194",
    2: "3a734c7f69b67583fd847a2df0919430092d755c757eb9fa2d2aa8dffb71669c",
    3: "32cdd595df3a5b2f39853beceb0f4e395f9e1277b1059204f3aeddd2cbee6258",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError("D10 certificate mismatch: " + message)


CERTIFICATE = json.loads(Path(__file__).with_name("CERTIFICATE.json").read_text(encoding="utf-8"))
require(CERTIFICATE["search"]["primary_state_sha256"] ==
        {str(k): v for k, v in EXPECTED_PRIMARY_DIGESTS.items()}, "primary state digests")
require(CERTIFICATE["search"]["candidate_counts"] ==
        {"0": 1, "1": 56, "2": 3136, "3": 175616}, "candidate counts")
require(CERTIFICATE["search"]["exact_endpoint_hits"] ==
        {"0": 0, "1": 0, "2": 0, "3": 0}, "hit counts")
require(CERTIFICATE["target"] == "diag([st],[ts],[e])", "target statement")
GROUP_TABLE = [[group_mul(a, b) for b in range(NGROUP)] for a in range(NGROUP)]
assert all(GROUP_TABLE[E][g] == g and GROUP_TABLE[g][E] == g for g in range(NGROUP))
assert all(GROUP_TABLE[g][GROUP_TABLE[g][E]] == E for g in (S, T))
assert GROUP_TABLE[S][T] == R and GROUP_TABLE[T][S] == R_INV
assert group_mul(R, R) == 4 and group_mul(group_mul(R, R), group_mul(R, R)) == R_INV
assert group_mul(R, R_INV) == E and group_mul(R_INV, R) == E
assert group_mul(group_mul(R, R), group_mul(group_mul(R, R), R)) == E
assert all(group_mul(group_mul(a, b), c) == group_mul(a, group_mul(b, c))
           for a in range(NGROUP) for b in range(NGROUP) for c in range(NGROUP))

# A state is a tuple of ten coefficient matrices, one per group element.
ZERO = (0,) * NGROUP
UNIT = tuple(IDENTITY_MATRIX if g == E else 0 for g in range(NGROUP))


def right_multiply_call(state: tuple[int, ...], label: int, n: int) -> tuple[int, ...]:
    """Right multiply by I + ([label]+[e])N in characteristic two."""
    id_part = IDENTITY_MATRIX ^ n
    out = [0] * NGROUP
    for g, coeff in enumerate(state):
        if coeff:
            out[g] ^= MATMUL[coeff][id_part]
            out[GROUP_TABLE[g][label]] ^= MATMUL[coeff][n]
    return tuple(out)


def word_state(labels: tuple[int, ...], projectors: tuple[int, ...]) -> tuple[int, ...]:
    state = UNIT
    for label, n in zip(labels, projectors):
        state = right_multiply_call(state, label, n)
    return state


def target_state() -> tuple[int, ...]:
    coeffs = [0] * NGROUP
    coeffs[R] = 1 << 0
    coeffs[R_INV] = 1 << (1 * NREG + 1)
    coeffs[E] = 1 << (2 * NREG + 2)
    return tuple(coeffs)

TARGET = target_state()


def direct_four_call() -> tuple[tuple[int, ...], tuple[int, ...]]:
    e00 = 1 << 0
    e11 = 1 << 4
    labels = (S, T, T, S)
    projectors = (e00, e00, e11, e11)
    assert all(n in PROJECTORS for n in projectors)
    return labels, projectors


def exhaustive(max_length: int = 3) -> dict[int, tuple[tuple[int, ...], tuple[int, ...]] | None]:
    hits = {k: None for k in range(max_length + 1)}
    counts = {k: 0 for k in range(max_length + 1)}
    hit_counts = {k: 0 for k in range(max_length + 1)}
    digests = {k: hashlib.sha256() for k in range(max_length + 1)}
    for k in range(max_length + 1):
        for labels in product((S, T), repeat=k):
            for projectors in product(PROJECTORS, repeat=k):
                counts[k] += 1
                state = word_state(labels, projectors)
                record = bytes(labels)
                record += b"".join(n.to_bytes(2, "little") for n in projectors)
                record += b"".join(c.to_bytes(2, "little") for c in state)
                digests[k].update(record)
                if state == TARGET:
                    hit_counts[k] += 1
                    if hits[k] is None:
                        hits[k] = (labels, projectors)
    expected = {0: 1, 1: 56, 2: 3136, 3: 175616}
    assert counts == expected, (counts, expected)
    assert hit_counts == {0: 0, 1: 0, 2: 0, 3: 0}, hit_counts
    assert {k: d.hexdigest() for k, d in digests.items()} == EXPECTED_PRIMARY_DIGESTS
    print("SEARCH_COUNTS", counts)
    print("SEARCH_HITS", hit_counts)
    print("SEARCH_STATE_SHA256", {k: d.hexdigest() for k, d in digests.items()})
    return hits


def main() -> None:
    hits = exhaustive(3)
    direct_labels, direct_projectors = direct_four_call()
    direct = word_state(direct_labels, direct_projectors)
    assert direct == TARGET
    assert all(hits[k] is None for k in range(4))
    # The supplied four-call word is a positive control; every one-factor
    # deletion and one label mutation fails exact full-group-algebra equality.
    for drop in range(4):
        reduced_labels = direct_labels[:drop] + direct_labels[drop + 1:]
        reduced_ns = direct_projectors[:drop] + direct_projectors[drop + 1:]
        assert word_state(reduced_labels, reduced_ns) != TARGET
    mutated_labels = list(direct_labels)
    mutated_labels[1] = S
    assert word_state(tuple(mutated_labels), direct_projectors) != TARGET
    swapped_target = tuple((1 << 0) if g == R_INV else
                           (1 << 4) if g == R else
                           (1 << 8) if g == E else 0
                           for g in range(NGROUP))
    assert TARGET != swapped_target
    assert direct != swapped_target
    swapped_direct = word_state((T, S, S, T), (1, 1, 16, 16))
    assert swapped_direct == swapped_target
    print("DIRECT_CONTROL labels=stts calls=4 exact_endpoint=true")
    print("NEGATIVE_CONTROLS deleted_calls=4 label_mutation=1 role_swap_distinct=true")
    print("PASS_D10_INVERSE_ROTATION_MINIMUM min_calls=4 tested_words_le3=178809 projectors=28 group_order=10")


if __name__ == "__main__":
    main()
