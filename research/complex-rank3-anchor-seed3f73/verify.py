#!/usr/bin/env python3
"""Verify a reversible rank-three common-sum anchor and its exact cost screen."""

from __future__ import annotations

import hashlib
import importlib
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "research/complex-local-word-ceiling"))
ceiling = importlib.import_module("ceiling")

PINNED = {
    "certificates/selected-result.json": "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
    "docs/research/agent-task-catalog.json": "d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7",
    "docs/research/community-batch1099-review.md": "7e76d2c38e5fce30587835b7251df1430488ae4dd372611ef69a3f03f476b6cb",
    "research/community-frontier1094-audit/SELECTED-SOURCE.json": "79b3de5db3dbcb9829789ba58e9e45758926031e2a7d80667a08429d369be53b",
    "research/community-frontier1094-audit/ASSEMBLY.json": "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
    "research/complex-local-word-ceiling/README.md": "b60be039cb0e03e064a27407d0bce9e58908d793da5ee405c876de5aebfa5f81",
    "research/complex-local-word-ceiling/ceiling.py": "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc",
}
BASE_PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
CEILING_KW = dict(m=73, families=896, stages=9, centre=64, grid=Q(1, 10**12))


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def product(j: int) -> tuple[str, int, str, int]:
    return ("x", j, "y", j)


def expected_symbolic(q: int, r: int) -> list[set[tuple]]:
    n = r + q - 1
    result = [set() for _ in range(q)]
    result[0].update(product(j) for j in range(r))
    for i in range(1, q):
        result[i].add(("d", i))
        result[i].update(product(j) for j in range(r))
        result[i].add(product(r + i - 1))
    require(n == max(j for row in result for item in row if len(item) == 4 for j in (item[1],)) + 1,
            "symbolic variable count")
    return result


def symbolic_schedule(q: int, r: int) -> tuple[list[set[tuple]], list[set[tuple]]]:
    """Execute products, fanouts, then the literal reverse on formal GF(2) monomials."""
    out = [set() for _ in range(q)]
    anchor: set[tuple] = set()
    for j in range(r):
        anchor.symmetric_difference_update({product(j)})
    out[0] = set(anchor)  # A0 starts clean.
    for i in range(1, q):
        out[i] = {("d", i), product(r + i - 1)}
    for i in range(1, q):
        out[i].symmetric_difference_update(anchor)

    reverse = [set(row) for row in out]
    for i in range(q - 1, 0, -1):
        reverse[i].symmetric_difference_update(reverse[0])
        reverse[i].symmetric_difference_update({product(r + i - 1)})
    for j in range(r - 1, -1, -1):
        reverse[0].symmetric_difference_update({product(j)})
    return out, reverse


def bits_forward(q: int, r: int, x: int, y: int, dirty: int, *, skip_fanout: int = -1,
                 omit_anchor_product: int = -1, dirty_anchor: int = 0) -> tuple[int, ...]:
    anchor = dirty_anchor
    for j in range(r):
        if j != omit_anchor_product:
            anchor ^= (((x >> j) & 1) & ((y >> j) & 1))
    outputs = [anchor]
    for i in range(1, q):
        k = r + i - 1
        value = (dirty >> (i - 1)) & 1
        value ^= (((x >> k) & 1) & ((y >> k) & 1))
        if i != skip_fanout:
            value ^= anchor
        outputs.append(value)
    return tuple(outputs)


def bits_inverse(q: int, r: int, x: int, y: int, final: tuple[int, ...]) -> tuple[int, ...]:
    state = list(final)
    for i in range(q - 1, 0, -1):
        state[i] ^= state[0]
        k = r + i - 1
        state[i] ^= (((x >> k) & 1) & ((y >> k) & 1))
    for j in range(r - 1, -1, -1):
        state[0] ^= (((x >> j) & 1) & ((y >> j) & 1))
    return tuple(state)


def check_anchor() -> dict:
    q, r = 4, 3
    n = r + q - 1
    states = 0
    for x in range(1 << n):
        for y in range(1 << n):
            anchor = sum(((x >> j) & (y >> j)) for j in range(r)) & 1
            for dirty in range(1 << (q - 1)):
                got = bits_forward(q, r, x, y, dirty)
                want = [anchor]
                for i in range(1, q):
                    k = r + i - 1
                    want.append(((dirty >> (i - 1)) & 1) ^ anchor
                                ^ (((x >> k) & 1) & ((y >> k) & 1)))
                require(got == tuple(want), "q=4 dirty-output endpoint")
                require(bits_inverse(q, r, x, y, got) == (0,) + tuple(
                    (dirty >> (i - 1)) & 1 for i in range(1, q)), "q=4 restoration")
                states += 1

    # Controls: a missing product, a missing fanout, and a dirty anchor violate the contract.
    x = y = 1 << 2
    dirty = 0
    clean = bits_forward(q, r, x, y, dirty)
    omitted_product = bits_forward(q, r, x, y, dirty, omit_anchor_product=2)
    require(clean[0] == 1 and omitted_product[0] == 0, "omitted anchor-product control")
    x = y = 1  # The first anchor product is one, so every non-anchor output needs its fanout.
    with_fanout = bits_forward(q, r, x, y, 0)
    without_fanout = bits_forward(q, r, x, y, 0, skip_fanout=2)
    require(with_fanout[2] != without_fanout[2], "omitted fanout control")
    dirty_anchor_case = bits_forward(q, r, 0, 0, 0, dirty_anchor=1)
    require(dirty_anchor_case[0] != 0, "clean-anchor precondition control")

    for width in range(2, 113):
        actual, restored = symbolic_schedule(width, 3)
        require(actual == expected_symbolic(width, 3), f"symbolic identity q={width}")
        require(restored[0] == set(), f"anchor restoration q={width}")
        for i in range(1, width):
            require(restored[i] == {("d", i)}, f"dirty restoration q={width}, target={i}")
    return {"exhaustive_q4_boolean_states": states, "symbolic_widths": 111,
            "controls_rejected": 3, "anchor_products": 3}


def screen(profile: dict[int, int]) -> tuple[Q, Q]:
    return ceiling.ceiling(profile, **CEILING_KW)


def cost_screen() -> dict:
    base = screen(BASE_PROFILE)
    rank2_profile = {**BASE_PROFILE, 1: 1968}
    rank2 = screen(rank2_profile)
    two_blocks = 2
    q, r = 112, 3
    separate_each = (r + 1) * q - 1
    anchor_each = q + r - 1
    saved_per_block = separate_each - anchor_each
    candidate_profile = {**BASE_PROFILE, 1: BASE_PROFILE[1] - two_blocks * saved_per_block}
    candidate = screen(candidate_profile)
    at_411 = screen({**candidate_profile, 1: candidate_profile[1] + 411})
    at_412 = screen({**candidate_profile, 1: candidate_profile[1] + 412})
    target = Q(21, 20) * base[1]
    require(separate_each == 447 and anchor_each == 114 and saved_per_block == 333,
            "rank-three per-block product invoice")
    require(candidate_profile[1] == 1746, "two-block rank-one profile")
    require(candidate[0] > target, "ideal rank-three profile clears 5 percent")
    require(at_411[0] >= target, "411 extra rank-one equivalents still pass")
    require(at_412[1] < Q(21, 20) * base[0], "412 extra rank-one equivalents fail")
    require(rank2_profile[1] == 1968, "rank-two predecessor profile control")
    return {
        "base_cap": [str(x) for x in base],
        "rank2_two_block_control_cap": [str(x) for x in rank2],
        "rank3_two_block_profile": {str(k): v for k, v in sorted(candidate_profile.items())},
        "rank3_cap": [str(x) for x in candidate],
        "rank3_gain_interval": [str(candidate[0] / base[1]), str(candidate[1] / base[0])],
        "target_ratio": "21/20",
        "max_extra_rank1_equivalents_passing": 411,
        "first_failing_extra_rank1_equivalents": 412,
        "cap_at_411": [str(x) for x in at_411],
        "cap_at_412": [str(x) for x in at_412],
    }


def check_pins() -> dict:
    result = {}
    for rel, expected in PINNED.items():
        source = PACKAGE / "task-catalog-snapshot.json" if rel == "docs/research/agent-task-catalog.json" else ROOT / rel
        got = hashlib.sha256(source.read_bytes()).hexdigest()
        require(got == expected, f"source pin {rel}")
        result[rel] = got
    selected = json.loads((ROOT / "certificates/selected-result.json").read_text())
    require(selected["review"] == "docs/research/community-batch1099-review.md", "selected review binding")
    require(selected["source_manifest"] == "research/community-frontier1094-audit/SELECTED-SOURCE.json",
            "selected source manifest binding")
    require(selected["certificate"] == "research/community-frontier1094-audit/ASSEMBLY.json",
            "selected certificate binding")
    require(selected["reproduce"] == "make frontier1094-verify", "selected reproduction binding")
    return result


def main() -> None:
    pins = check_pins()
    construction = check_anchor()
    costs = cost_screen()
    result = {
        "status": "scoped_local_construction",
        "task_id": "complex-new-helper-inventory",
        "seed": "3f73d5ee4dbd507bc342bd8da6003a48",
        "base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
        "selected_record_sha256": PINNED["certificates/selected-result.json"],
        "contract": {
            "anchor_products": 3,
            "q_domain": "2..112",
            "products_per_block": "q+2",
            "fanout_adds_per_block": "q-1",
            "separate_products_per_block": "4q-1",
            "two_q112_blocks": {"products": 228, "fanout_adds": 222,
                                  "products_saved_vs_separate": 666},
        },
        "construction_checks": construction,
        "moment_screen": costs,
        "source_pins": pins,
        "limits": [
            "The profile is a local conditional construction, not a selected-provider placement.",
            "The 222 affine fanout additions are a separate scalar-operation charge.",
            "Provider source mapping, frame/copy/hosting/precision/restoration and interface costs remain open.",
            "No selected supplier, kappa or frontier change is claimed.",
        ],
        "predecessor": "local rank-two common-sum anchor, commit dc29def3, Discussion #1167 comment 18931234",
    }
    (PACKAGE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS_RANK3_SUM_ANCHOR q=2..112 products=114 fanouts=111 two_blocks_saved=666 cap_extra=411/412 local_only")


if __name__ == "__main__":
    main()
