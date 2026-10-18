#!/usr/bin/env python3
"""Exact exhaustive search for the two-role D8 rotation/inverse target."""
from __future__ import annotations

import itertools
import json
from pathlib import Path

# D8 elements are r^i s^e, i in Z/4, e in {0,1}; s r = r^-1 s.
ELEMENTS = tuple((i, e) for i in range(4) for e in range(2))
INDEX = {x: i for i, x in enumerate(ELEMENTS)}
IDENTITY = INDEX[(0, 0)]

def multiply(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    i, e = x
    j, f = y
    return ((i + (-j if e else j)) % 4, e ^ f)

S = INDEX[(0, 1)]
T = INDEX[(3, 1)]  # t=s r = r^-1 s, so s*t=r.
R = INDEX[(1, 0)]
RINV = INDEX[(3, 0)]
assert multiply(ELEMENTS[S], ELEMENTS[S]) == (0, 0)
assert multiply(ELEMENTS[T], ELEMENTS[T]) == (0, 0)
assert multiply(ELEMENTS[S], ELEMENTS[T]) == ELEMENTS[R]
assert multiply(ELEMENTS[T], ELEMENTS[S]) == ELEMENTS[RINV]
RIGHT = [[INDEX[multiply(x, ELEMENTS[g])] for x in ELEMENTS] for g in (S, T)]
def translate(mask: int, table: list[int]) -> int:
    out = 0
    while mask:
        bit = mask & -mask
        idx = bit.bit_length() - 1
        out ^= 1 << table[idx]
        mask ^= bit
    return out

def right_x(mask: int, gi: int) -> int:
    return mask ^ translate(mask, RIGHT[gi])

# Row-major 2x2 matrices over F2[D8], each coefficient stored as an 8-bit mask.
IMAT = (1 << IDENTITY, 0, 0, 1 << IDENTITY)
VECTORS = (1, 2, 3)
IDEMPOTENTS = tuple(
    (u, v) for u in VECTORS for v in VECTORS
    if ((u & v).bit_count() & 1) == 1
)
assert len(IDEMPOTENTS) == 6
FACTORS = tuple(
    (gi, u, v)
    for gi in range(2) for u, v in IDEMPOTENTS
)
assert len(FACTORS) == 12

def right_factor(mat: tuple[int, ...], gi: int, u: int, v: int) -> tuple[int, ...]:
    """mat * (I + (1+[g]) u v^T), in characteristic two."""
    out = list(mat)
    for i in range(2):
        z = (mat[2 * i] if (u & 1) else 0) ^ (mat[2 * i + 1] if (u & 2) else 0)
        zx = right_x(z, gi)
        if v & 1:
            out[2 * i] ^= zx
        if v & 2:
            out[2 * i + 1] ^= zx
    return tuple(out)

TARGET = (1 << R, 0, 0, 1 << RINV)

def label(fi: int) -> str:
    gi, u, v = FACTORS[fi]
    return f"{'s' if gi == 0 else 't'}:u{u:02b}v{v:02b}"

def direct_four_call_check() -> tuple[bool, list[int]]:
    seq = []
    for gi in (0, 1):
        seq.append(FACTORS.index((gi, 1, 1)))
    for gi in (1, 0):
        seq.append(FACTORS.index((gi, 2, 2)))
    mat = IMAT
    for fi in seq:
        mat = right_factor(mat, *FACTORS[fi])
    return mat == TARGET, seq

def exhaustive_search(max_length: int = 3):
    counts = []
    found = []
    for n in range(max_length + 1):
        checked = 0
        for word in itertools.product(range(len(FACTORS)), repeat=n):
            checked += 1
            mat = IMAT
            for fi in word:
                mat = right_factor(mat, *FACTORS[fi])
            if mat == TARGET:
                found.append({"length": n, "factor_indices": list(word),
                              "word": [label(fi) for fi in word]})
        counts.append({"length": n, "factor_words_checked": checked,
                       "expected": len(FACTORS) ** n, "complete": checked == len(FACTORS) ** n})
    return counts, found

def main() -> None:
    direct_ok, direct_word = direct_four_call_check()
    if not direct_ok:
        raise SystemExit("direct four-call construction failed")
    counts, found = exhaustive_search(3)
    result = {
        "status": "PASS_D8_ROTATION_PAIR_SEARCH",
        "group": "D8 = <s,t | s^2=t^2=1,(st)^4=1>",
        "elements": [f"r^{i}s^{e}" for i, e in ELEMENTS],
        "paid_factors": len(FACTORS),
        "factor_alphabet": [label(i) for i in range(len(FACTORS))],
        "rank_one_idempotents": len(IDEMPOTENTS),
        "target": "diag([r],[r^-1]) where r=st",
        "direct_four_call": {"status": "PASS", "word": [label(fi) for fi in direct_word]},
        "length_census": counts,
        "factorizations_at_or_below_3": found,
        "claim_scope": "exactly r=2, F2[D8], labels {s,t}, target diag([st],[ts])",
        "stopping_rule": "complete enumeration of all 12^n paid-factor words for n=0,1,2,3",
    }
    Path(__file__).with_name("RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
