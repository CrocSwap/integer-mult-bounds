#!/usr/bin/env python3
"""Verify dirty-anchor accumulation of a sum of shared bilinear products."""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research/complex-local-word-ceiling"))
import ceiling as C  # noqa: E402

PINNED_FILES = {
    "certificates/selected-result.json": "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
    "research/community-frontier1094-audit/SELECTED-SOURCE.json": "79b3de5db3dbcb9829789ba58e9e45758926031e2a7d80667a08429d369be53b",
    "docs/research/agent-task-catalog.json": "6686ad58f1fbdbc87134a78901b60fd53a20d3984355e91defbbebc9e9fa8075",
    "research/complex-local-word-ceiling/RESULT.json": "d91d6c46509875abf1f61de67c2609656d3dc685451299f83caa6f922493692d",
    "research/complex-local-word-ceiling/ceiling.py": "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc",
}
BASE_PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
BASE_CEILING = (Q(52814190909, 31250000000000), Q(1690054109089, 10**15))
ILLUSTRATIVE_PROFILE = {1: 2364, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
ILLUSTRATIVE_CEILING = (
    Q(68214620471, 40000000000000),
    Q(53292672243, 31250000000000),
)


def require(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError(why)


def add_scaled(dst: dict[tuple[str, ...], int], src: dict[tuple[str, ...], int], scale: int):
    out = dict(dst)
    for monomial, coefficient in src.items():
        out[monomial] = out.get(monomial, 0) + scale * coefficient
    return {m: c for m, c in out.items() if c}


def product_poly(x: str, y: str) -> dict[tuple[str, ...], int]:
    return {tuple(sorted((x, y))): 1}


def forward_symbolic(q: int, common: list[tuple[str, str]], private: list[tuple[str, str]], *,
                     before: bool = True, after: bool = True, first_scale: int = -1):
    out = [{(f"A{i}",): 1} for i in range(q)]
    if before:
        for i in range(1, q):
            out[i] = add_scaled(out[i], out[0], first_scale)
    for x, y in common:
        out[0] = add_scaled(out[0], product_poly(x, y), 1)
    if after:
        for i in range(1, q):
            out[i] = add_scaled(out[i], out[0], 1)
    for i, (x, y) in enumerate(private):
        out[i] = add_scaled(out[i], product_poly(x, y), 1)
    return out


def inverse_symbolic(out, common, private):
    q = len(out)
    state = [dict(poly) for poly in out]
    for i in range(q - 1, -1, -1):
        state[i] = add_scaled(state[i], product_poly(*private[i]), -1)
    for i in range(q - 1, 0, -1):
        state[i] = add_scaled(state[i], state[0], -1)
    for x, y in reversed(common):
        state[0] = add_scaled(state[0], product_poly(x, y), -1)
    for i in range(1, q):
        state[i] = add_scaled(state[i], state[0], 1)
    return state


def check_symbolic_family() -> None:
    for q in range(2, 6):
        for s in range(1, 5):
            common = [(f"x{j}", f"y{j}") for j in range(s)]
            private = [(f"u{i}", f"v{i}") for i in range(q)]
            result = forward_symbolic(q, common, private)
            for i in range(q):
                expected = {(f"A{i}",): 1}
                for x, y in common:
                    expected = add_scaled(expected, product_poly(x, y), 1)
                expected = add_scaled(expected, product_poly(*private[i]), 1)
                require(result[i] == expected, f"symbolic output identity q={q} s={s} i={i}")
            require(inverse_symbolic(result, common, private) == [{(f"A{i}",): 1} for i in range(q)],
                    f"symbolic inverse q={q} s={s}")


def forward_values(a, x, y, u, v, p, *, before=True, after=True, first_sign=-1):
    q, s = len(a), len(x)
    out = list(a)
    if before:
        for i in range(1, q):
            out[i] = (out[i] + first_sign * out[0]) % p
    for j in range(s):
        out[0] = (out[0] + x[j] * y[j]) % p
    if after:
        for i in range(1, q):
            out[i] = (out[i] + out[0]) % p
    for i in range(q):
        out[i] = (out[i] + u[i] * v[i]) % p
    return out


def inverse_values(out, x, y, u, v, p):
    q, s = len(out), len(x)
    state = list(out)
    for i in range(q - 1, -1, -1):
        state[i] = (state[i] - u[i] * v[i]) % p
    for i in range(q - 1, 0, -1):
        state[i] = (state[i] - state[0]) % p
    for j in range(s - 1, -1, -1):
        state[0] = (state[0] - x[j] * y[j]) % p
    for i in range(1, q):
        state[i] = (state[i] + state[0]) % p
    return state


def check_exhaustive_dirty_states() -> int:
    q, s = 2, 2
    total = 0
    for p in (2, 3):
        for values in itertools.product(range(p), repeat=3 * q + 2 * s):
            pos = 0
            a = values[pos:pos + q]; pos += q
            x = values[pos:pos + s]; pos += s
            y = values[pos:pos + s]; pos += s
            u = values[pos:pos + q]; pos += q
            v = values[pos:pos + q]
            original_sources = (x, y, u, v)
            got = forward_values(a, x, y, u, v, p)
            common_sum = sum(x[j] * y[j] for j in range(s)) % p
            expected = tuple((a[i] + common_sum + u[i] * v[i]) % p for i in range(q))
            require(tuple(got) == expected, f"dirty forward replay p={p} state={values}")
            require(tuple(inverse_values(got, x, y, u, v, p)) == tuple(a),
                    f"dirty inverse replay p={p} state={values}")
            require((x, y, u, v) == original_sources, "source values are read-only")
            total += 1
    return total


def check_failure_controls() -> None:
    # The first wave removes the old dirty anchor; the second installs its update.
    a, x, y, u, v = (1, 0), (0, 0), (0, 0), (0, 0), (0, 0)
    expected = (1, 0)
    require(tuple(forward_values(a, x, y, u, v, 3, before=False)) != expected,
            "missing-old-anchor-wave negative control")
    a, x, y, u, v = (0, 0), (1, 0), (1, 0), (0, 0), (0, 0)
    require(tuple(forward_values(a, x, y, u, v, 3, after=False)) != (1, 1),
            "missing-updated-anchor-wave negative control")
    a, x, y, u, v = (1, 0), (0, 0), (0, 0), (0, 0), (0, 0)
    require(tuple(forward_values(a, x, y, u, v, 3, first_sign=1)) != (1, 0),
            "wrong compensation sign negative control")


def check_cost_formula() -> None:
    for q in range(2, 9):
        for s in range(1, 6):
            direct_children = q * (s + 1)
            shared_children = s + q
            require(direct_children - shared_children == s * (q - 1), "child-call saving formula")
            combined_adds = 2 * (q - 1)
            separate_adds = 2 * s * (q - 1)
            require(separate_adds - combined_adds == 2 * (s - 1) * (q - 1),
                    "coalesced fanout addition saving")


def check_selected_profile_screen() -> None:
    base = C.ceiling(BASE_PROFILE, 73, 896, 9, 64, grid=Q(1, 10**15))
    candidate = C.ceiling(ILLUSTRATIVE_PROFILE, 73, 896, 9, 64, grid=Q(1, 10**15))
    require(base == BASE_CEILING, "selected profile ceiling pin")
    require(candidate == ILLUSTRATIVE_CEILING, "eight-block rank-only candidate ceiling")
    require(candidate[1] < BASE_CEILING[1] * Q(105, 100), "hypothetical profile still misses five-percent gate")


def check_pins() -> None:
    for relative, expected in PINNED_FILES.items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        require(actual == expected, f"source SHA-256 pin: {relative}")


def check_result_record(exhaustive_count: int) -> None:
    result = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    require(result["exhaustive_dirty_states"] == exhaustive_count == 60073, "RESULT exhaustive count")
    require(result["illustrative_profile"] == {str(k): v for k, v in ILLUSTRATIVE_PROFILE.items()},
            "RESULT profile")
    require(result["illustrative_ceiling"] == [str(x) for x in ILLUSTRATIVE_CEILING], "RESULT ceiling")
    require(result["cost_example"] == {
        "q": 3,
        "s": 3,
        "width": 1,
        "direct_children": 12,
        "anchor_children": 6,
        "anchor_adds": 4,
        "separate_fanout_adds": 12,
        "children_saved": 6,
        "fanout_adds_saved": 8,
        "net_saving": "6*mu-4*A_1",
        "break_even": "mu > 2*A_1/3",
    }, "RESULT cost example")


def main() -> None:
    check_pins()
    check_symbolic_family()
    exhaustive = check_exhaustive_dirty_states()
    check_failure_controls()
    check_cost_formula()
    check_selected_profile_screen()
    check_result_record(exhaustive)
    gain = 100 * (ILLUSTRATIVE_CEILING[1] / BASE_CEILING[1] - 1)
    print(
        "PASS_RECURSIVE_MULTITERM_DIRTY_ANCHOR "
        f"symbolic_q=2..5 symbolic_s=1..4 exhaustive_states={exhaustive} "
        f"q3_s3_direct=12_shared=6_adds=4 separate_fanout_adds=12 "
        f"eight_block_rank_only_gain_percent={float(gain):.6f} "
        "supplier_admission=none negative_controls=3"
    )


if __name__ == "__main__":
    main()
