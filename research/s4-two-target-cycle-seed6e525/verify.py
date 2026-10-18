"""Exact bounded S4 three-register paid-word search. Apache-2.0."""
from __future__ import annotations

import hashlib
import itertools
import json
import resource
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MAX_SECONDS = 110
MAX_RSS_BYTES = 1024**3
START = time.monotonic()


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_budget() -> None:
    elapsed = time.monotonic() - START
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss = raw * (1024 if sys.platform.startswith("linux") else 1)
    need(elapsed <= MAX_SECONDS, f"search time cap reached at {elapsed:.1f}s")
    need(rss <= MAX_RSS_BYTES, f"search RSS cap reached at {rss} bytes")


# S4 is represented by permutations of four points. Multiplication composes
# functions right-to-left: (a*b)(i)=a(b(i)).
GROUP = tuple(itertools.permutations(range(4)))
GID = {g: i for i, g in enumerate(GROUP)}
IDENTITY_PERM = GID[tuple(range(4))]


def compose(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a[b[i]] for i in range(4))


MUL = tuple(
    tuple(GID[compose(a, b)] for b in GROUP)
    for a in GROUP
)


def adjacent_swap(i: int) -> int:
    p = list(range(4))
    p[i], p[i + 1] = p[i + 1], p[i]
    return GID[tuple(p)]


SIMPLE = (adjacent_swap(0), adjacent_swap(1), adjacent_swap(2))
CYCLE = MUL[MUL[SIMPLE[0]][SIMPLE[1]]][SIMPLE[2]]
E_BIT = 1 << IDENTITY_PERM
C_BIT = 1 << CYCLE


def make_translations() -> tuple[tuple[tuple[int, ...], ...], ...]:
    """Lookup tables for right multiplication of F2[S4] coefficient masks."""
    all_tables = []
    for g in range(len(GROUP)):
        chunks = []
        for chunk in range(3):
            lookup = []
            for small in range(256):
                out = 0
                for j in range(8):
                    if (small >> j) & 1:
                        old = chunk * 8 + j
                        if old < len(GROUP):
                            out ^= 1 << MUL[old][g]
                lookup.append(out)
            chunks.append(tuple(lookup))
        all_tables.append(tuple(chunks))
    return tuple(all_tables)


TRANSLATE_CHUNKS = make_translations()


def translate(mask: int, g: int) -> int:
    t = TRANSLATE_CHUNKS[g]
    return t[0][mask & 255] ^ t[1][(mask >> 8) & 255] ^ t[2][(mask >> 16) & 255]


def encode(cells: list[int] | tuple[int, ...]) -> bytes:
    out = bytearray(27)  # nine cells, each a 24-bit group-algebra element
    for i, v in enumerate(cells):
        out[3 * i] = v & 255
        out[3 * i + 1] = (v >> 8) & 255
        out[3 * i + 2] = (v >> 16) & 255
    return bytes(out)


def decode(state: bytes) -> list[int]:
    return [state[i] | (state[i + 1] << 8) | (state[i + 2] << 16) for i in range(0, 27, 3)]


IDENTITY = encode([E_BIT, 0, 0, 0, E_BIT, 0, 0, 0, E_BIT])
TARGET = encode([C_BIT, 0, 0, 0, C_BIT, 0, 0, 0, E_BIT])


def rank_one_idempotents() -> tuple[tuple[int, int], ...]:
    pairs = []
    for u in range(1, 8):
        for v in range(1, 8):
            if (u & v).bit_count() & 1:
                pairs.append((u, v))
    return tuple(pairs)


PROJECTORS = rank_one_idempotents()
GENERATORS = tuple((g, u, v) for g in SIMPLE for u, v in PROJECTORS)
GENERATOR_ID = {gen: i for i, gen in enumerate(GENERATORS)}


def step(state: bytes, gen: tuple[int, int, int]) -> bytes:
    """Right multiply exactly by I+([g]+[e])uv^T over F2[S4]."""
    g, u, v = gen
    cells = decode(state)
    for row in range(3):
        signal = 0
        base = 3 * row
        for k in range(3):
            if (u >> k) & 1:
                signal ^= cells[base + k]
        delta = signal ^ translate(signal, g)
        if delta:
            for col in range(3):
                if (v >> col) & 1:
                    cells[base + col] ^= delta
    return encode(cells)


def coeff_product(left: int, right: int) -> int:
    """Independent, literal convolution in F2[S4]."""
    out = 0
    a = left
    while a:
        abit = a & -a
        i = abit.bit_length() - 1
        a ^= abit
        b = right
        while b:
            bbit = b & -b
            j = bbit.bit_length() - 1
            b ^= bbit
            out ^= 1 << MUL[i][j]
    return out


def matrix_product(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    out = [0] * 9
    for i in range(3):
        for j in range(3):
            value = 0
            for k in range(3):
                value ^= coeff_product(a[3 * i + k], b[3 * k + j])
            out[3 * i + j] = value
    return tuple(out)


def factor_matrix(gen: tuple[int, int, int]) -> tuple[int, ...]:
    g, u, v = gen
    out = [E_BIT if i == j else 0 for i in range(3) for j in range(3)]
    t = E_BIT ^ (1 << g)
    for i in range(3):
        if (u >> i) & 1:
            for j in range(3):
                if (v >> j) & 1:
                    out[3 * i + j] ^= t
    return tuple(out)


def multiply_word(word: tuple[int, ...] | list[int]) -> bytes:
    result = tuple(decode(IDENTITY))
    for gi in word:
        result = matrix_product(result, factor_matrix(GENERATORS[gi]))
    return encode(result)


def ball(root: bytes, radius: int) -> tuple[dict[bytes, tuple[bytes, int] | None], list[int]]:
    """Enumerate all exact states within a paid-call radius; retain parents."""
    seen: dict[bytes, tuple[bytes, int] | None] = {root: None}
    frontier = [root]
    layer_counts = [1]
    for _depth in range(1, radius + 1):
        following: list[bytes] = []
        for state_no, state in enumerate(frontier):
            if (state_no & 1023) == 0:
                check_budget()
            for gi, gen in enumerate(GENERATORS):
                nxt = step(state, gen)
                if nxt not in seen:
                    seen[nxt] = (state, gi)
                    following.append(nxt)
        layer_counts.append(len(following))
        frontier = following
        if not frontier:
            break
    check_budget()
    return seen, layer_counts


def reconstruct(parents: dict[bytes, tuple[bytes, int] | None], state: bytes) -> list[int]:
    reverse_path = []
    while parents[state] is not None:
        previous, gi = parents[state]  # type: ignore[misc]
        reverse_path.append(gi)
        state = previous
    reverse_path.reverse()
    return reverse_path


def labels(word: list[int]) -> list[dict[str, int | str]]:
    names = {g: f"s{i + 1}" for i, g in enumerate(SIMPLE)}
    return [
        {"address": names[GENERATORS[i][0]], "u": GENERATORS[i][1], "v": GENERATORS[i][2]}
        for i in word
    ]


def direct_word() -> list[int]:
    out = []
    for role in (1, 2):
        for g in SIMPLE:
            out.append(GENERATOR_ID[(g, role, role)])
    return out


def run() -> dict[str, object]:
    need(len(GROUP) == 24 and len(PROJECTORS) == 28 and len(GENERATORS) == 84, "alphabet cardinality")
    current = IDENTITY_PERM
    for _ in range(4):
        current = MUL[current][CYCLE]
    need(current == IDENTITY_PERM, "the selected address product does not have order four")
    need(CYCLE not in (IDENTITY_PERM, *SIMPLE), "the selected three-letter product is not a 4-cycle")

    # Each simple transposition has order two. Verify each paid factor is an
    # involution by literal F2[S4] matrix multiplication before the symmetric
    # meet-in-the-middle argument uses inverse balls.
    for gen in GENERATORS:
        m = factor_matrix(gen)
        need(matrix_product(m, m) == tuple(decode(IDENTITY)), "paid generator is not involutive")

    direct = direct_word()
    need(len(direct) == 6 and multiply_word(direct) == TARGET, "six-call direct construction")
    deletion_controls = 0
    for omitted in range(len(direct)):
        shortened = direct[:omitted] + direct[omitted + 1 :]
        need(multiply_word(shortened) != TARGET, "single-call omission control")
        deletion_controls += 1

    left, left_layers = ball(IDENTITY, 2)
    right, right_layers = ball(TARGET, 3)
    meetings = [state for state in left if state in right]
    witness = None
    if meetings:
        state = min(meetings)
        a = reconstruct(left, state)
        target_path = reconstruct(right, state)
        candidate = a + list(reversed(target_path))
        need(len(candidate) <= 5 and multiply_word(candidate) == TARGET, "meeting did not yield a formal word")
        witness = candidate
    else:
        need(not meetings, "empty intersection control")

    # A one-sided endpoint change is a semantic negative control.
    changed = encode([C_BIT, 0, 0, 0, C_BIT, 0, 0, 0, C_BIT])
    need(changed != TARGET and multiply_word(direct) != changed, "changed-third-role control")

    outcome = "FIVE_CALL_WORD_FOUND" if witness is not None else "NO_WORD_THROUGH_FIVE_MINIMUM_SIX"
    return {
        "schema_version": 1,
        "status": "PASS_S4_TWO_TARGET_CYCLE",
        "outcome": outcome,
        "group": "S4",
        "group_order": 24,
        "address_generators": ["s1=(12)", "s2=(23)", "s3=(34)"],
        "scalar_registers": 3,
        "rank_one_idempotents": len(PROJECTORS),
        "paid_generator_count": len(GENERATORS),
        "target": "diag([s1*s2*s3],[s1*s2*s3],[e])",
        "radius_left": 2,
        "radius_right": 3,
        "left_layer_counts": left_layers,
        "right_layer_counts": right_layers,
        "left_state_count": len(left),
        "right_state_count": len(right),
        "intersection_count": len(meetings),
        "direct_call_count": len(direct),
        "direct_word": labels(direct),
        "witness_call_count": None if witness is None else len(witness),
        "witness": None if witness is None else labels(witness),
        "semantic_controls": {
            "all_paid_factors_literal_square_to_identity": True,
            "single_call_omissions_rejected": deletion_controls,
            "changed_third_role_rejected": True,
        },
        "complete_domain": "all ordered words of length <=5 over the 84 paid involutive factors; proved by radius-2/radius-3 exact meet",
        "time_cap_seconds": MAX_SECONDS,
        "rss_cap_bytes": MAX_RSS_BYTES,
        "selected_kappa_claimed": False,
    }


if __name__ == "__main__":
    receipt = run()
    path = HERE / "CERTIFICATE.json"
    if "--write" in sys.argv:
        path.write_text(json.dumps(receipt, indent=2) + "\n")
    else:
        need(path.is_file(), "missing committed certificate; run verify.py --write once")
        need(receipt == json.loads(path.read_text()), "certificate mismatch")
    print(
        receipt["status"],
        receipt["outcome"],
        "layers=" + str(receipt["left_layer_counts"]) + "/" + str(receipt["right_layer_counts"]),
        "states=" + str(receipt["left_state_count"]) + "/" + str(receipt["right_state_count"]),
        "meetings=" + str(receipt["intersection_count"]),
    )
