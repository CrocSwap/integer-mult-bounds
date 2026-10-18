#!/usr/bin/env python3
"""Independent exact replay using permutation-built D10 and row-vector matrices."""
from __future__ import annotations

import hashlib
import json
from itertools import product
from pathlib import Path

RREG = 3
BITS = 7
ZERO_M = (0, 0, 0)
ID_M = (1, 2, 4)


def as_perm(k: int, e: int) -> tuple[int, ...]:
    return tuple((k + (-j if e else j)) % 5 for j in range(5))


PERMS = [as_perm(k, e) for k in range(5) for e in range(2)]
PERM_INDEX = {p: i for i, p in enumerate(PERMS)}


def compose(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    """Permutation product a*b means apply b, then a."""
    return tuple(a[b[i]] for i in range(5))


TABLE = [[PERM_INDEX[compose(a, b)] for b in PERMS] for a in PERMS]
E = PERM_INDEX[(0, 1, 2, 3, 4)]
S = PERM_INDEX[(0, 4, 3, 2, 1)]
T = PERM_INDEX[(4, 3, 2, 1, 0)]
R = PERM_INDEX[(1, 2, 3, 4, 0)]
R_INV = PERM_INDEX[(4, 0, 1, 2, 3)]
assert len(PERMS) == 10 and len(PERM_INDEX) == 10
assert TABLE[S][T] == R and TABLE[T][S] == R_INV
assert TABLE[S][S] == E and TABLE[T][T] == E
assert TABLE[R][R] == 4
rot = E
for _ in range(5):
    rot = TABLE[rot][R]
assert rot == E
assert all(TABLE[TABLE[a][b]][c] == TABLE[a][TABLE[b][c]]
           for a in range(10) for b in range(10) for c in range(10))

PROJECTORS = [(x, y) for x in range(1, 8) for y in range(1, 8)
              if (x & y).bit_count() & 1]
assert len(PROJECTORS) == 28
EXPECTED_DIGESTS = {
    0: "626523c7a23825bc1c716fb9540513bfa1ae0543b5a35e31993a89236e5e4d5e",
    1: "53740396a3f0f73e8392fbb7dae15ec29853e43d507ca3b48051b05fa97e7cb3",
    2: "385b9687ea222aa258066118a956483af8faade44fbf6a88bbfd3403018a5854",
    3: "078453f4249334b2553bb29e8bc7c8041a6f6910dfa112d9b9f4e571e7699c29",
}
CERTIFICATE = json.loads(Path(__file__).with_name("CERTIFICATE.json").read_text(encoding="utf-8"))
if CERTIFICATE["search"]["independent_state_sha256"] != {
        str(k): v for k, v in EXPECTED_DIGESTS.items()}:
    raise RuntimeError("D10 certificate mismatch: independent state digests")
if CERTIFICATE["search"]["total_candidates"] != 178809:
    raise RuntimeError("D10 certificate mismatch: total candidates")

# Algebra matrix state: a ten-tuple of three row bitmasks per group element.
UNIT = tuple(ID_M if g == E else ZERO_M for g in range(10))
TARGET = tuple((1, 0, 0) if g == R else
               (0, 2, 0) if g == R_INV else
               (0, 0, 4) if g == E else ZERO_M for g in range(10))


def add_rows(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return (a[0] ^ b[0], a[1] ^ b[1], a[2] ^ b[2])


def right_call(state: tuple[tuple[int, ...], ...], label: int,
               projector: tuple[int, int]) -> tuple[tuple[int, ...], ...]:
    x, y = projector
    out = [ZERO_M for _ in range(10)]
    for g, rows in enumerate(state):
        if rows == ZERO_M:
            continue
        image = tuple(y if (row & x).bit_count() & 1 else 0 for row in rows)
        unchanged = add_rows(rows, image)  # multiply by I+N
        h = TABLE[g][label]
        out[g] = add_rows(out[g], unchanged)
        out[h] = add_rows(out[h], image)
    return tuple(out)


def word_state(labels: tuple[int, ...], projectors: tuple[tuple[int, int], ...]):
    state = UNIT
    for label, projector in zip(labels, projectors):
        state = right_call(state, label, projector)
    return state


def main() -> None:
    expected_counts = {0: 1, 1: 56, 2: 3136, 3: 175616}
    counts = {}
    hits = {}
    digests = {}
    for k in range(4):
        digest = hashlib.sha256()
        count = hit = 0
        for labels in product((S, T), repeat=k):
            for projectors in product(PROJECTORS, repeat=k):
                state = word_state(labels, projectors)
                record = bytes(labels)
                record += b"".join(bytes(p) for p in projectors)
                record += bytes(row for coeff in state for row in coeff)
                digest.update(record)
                count += 1
                hit += state == TARGET
        counts[k] = count
        hits[k] = hit
        digests[k] = digest.hexdigest()
    assert counts == expected_counts
    assert hits == {0: 0, 1: 0, 2: 0, 3: 0}
    assert digests == EXPECTED_DIGESTS

    e00 = (1, 1)
    e11 = (2, 2)
    direct = word_state((S, T, T, S), (e00, e00, e11, e11))
    assert direct == TARGET
    assert word_state((T, S, S, T), (e00, e00, e11, e11)) != TARGET
    print("INDEPENDENT_SEARCH_COUNTS", counts)
    print("INDEPENDENT_SEARCH_HITS", hits)
    print("INDEPENDENT_STATE_SHA256", digests)
    print("PASS_D10_INDEPENDENT_PERMUTATION_REPLAY min_calls=4 tested_words_le3=178809")


if __name__ == "__main__":
    main()
