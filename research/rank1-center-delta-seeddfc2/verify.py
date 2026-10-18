#!/usr/bin/env python3
"""Exact two-bit rank-one center-difference construction and cost screen."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path
import sys


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def source_bytes(path: str) -> bytes:
    target = ROOT / path
    need(target.is_file(), f"missing pinned source: {path}")
    return target.read_bytes()


def check_source_pins() -> dict[str, str]:
    inventory = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    need(inventory["base_commit"] == json.loads((PACKAGE / "TASK.json").read_text(encoding="utf-8"))["base_commit"],
         "task/source base mismatch")
    rows = {row["path"]: row for row in inventory["files"]}
    inputs = [row for row in inventory["files"] if row["usage"] == "input"]
    for row in inventory["files"]:
        data = source_bytes(row["path"])
        need(hashlib.sha256(data).hexdigest() == row["sha256"], f"source SHA256 mismatch: {row['path']}")
    need(inputs, "no live inputs are pinned")
    return {row["path"]: row["sha256"] for row in rows.values()}


def bits2(value: int) -> tuple[int, int]:
    return value & 1, (value >> 1) & 1


def vector2(value: int) -> tuple[int, int]:
    return bits2(value)


def xor2(left: int, right: tuple[int, int]) -> int:
    return left ^ right[0] ^ (right[1] << 1)


def reference_update(x: int, y: int, p: int, q: int, scratch: int) -> tuple[int, int, int, int, int]:
    x0, x1 = bits2(x)
    y0, y1 = bits2(y)
    f0 = (x0 * y0, x1 * y1)
    correction = x0 * y1
    f1 = (f0[0] ^ correction, f0[1] ^ correction)
    return x, y, xor2(p, f0), xor2(q, f1), scratch


def atom_update(
    x: int,
    y: int,
    p: int,
    q: int,
    scratch: int,
    include_delta: bool = True,
    delta_q1: bool = True,
) -> tuple[int, int, int, int, int]:
    """Apply atoms u=x0*y0, v=x1*y1, w=x0*y1 to dirty output panels."""
    x0, x1 = bits2(x)
    y0, y1 = bits2(y)
    u, v, w = x0 * y0, x1 * y1, x0 * y1
    p = xor2(p, (u, v))
    q0, q1 = bits2(q)
    q0 ^= u
    q1 ^= v
    if include_delta:
        q0 ^= w
        if delta_q1:
            q1 ^= w
    return x, y, p, q0 | (q1 << 1), scratch


def gf2_rank(rows: list[int], columns: int) -> int:
    pivot = 0
    rows = list(rows)
    for col in range(columns):
        found = next((r for r in range(pivot, len(rows)) if (rows[r] >> col) & 1), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        for r in range(len(rows)):
            if r != pivot and ((rows[r] >> col) & 1):
                rows[r] ^= rows[pivot]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def load_ceiling():
    path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    spec = importlib.util.spec_from_file_location("pinned_local_word_ceiling", path)
    need(spec is not None and spec.loader is not None, "cannot load pinned ceiling module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_certificate() -> dict:
    pins = check_source_pins()
    task = json.loads((PACKAGE / "TASK.json").read_text(encoding="utf-8"))
    selected = json.loads(source_bytes("research/complex-local-word-ceiling/RESULT.json"))
    selected_record_sha = hashlib.sha256(source_bytes("certificates/selected-result.json")).hexdigest()
    need(selected_record_sha == task["selected_record_sha256"], "selected-record hash differs from the task pin")

    # Slice rows use input monomial order (x0*y0, x0*y1, x1*y0, x1*y1).
    slices = [0b0001, 0b1000, 0b0011, 0b1010]
    slice_rank = gf2_rank(slices, 4)
    need(slice_rank == 3, "joint slice-span flattening no longer has rank three")

    # Exhaust all 4^5 states: shared read-only inputs, two arbitrary dirty outputs,
    # and arbitrary private scratch, then check exact action and restoration.
    checked = 0
    for x in range(4):
        for y in range(4):
            for p in range(4):
                for q in range(4):
                    for scratch in range(4):
                        state = (x, y, p, q, scratch)
                        got = atom_update(*state)
                        expected = reference_update(*state)
                        need(got == expected, f"decomposition mismatch at state {state}")
                        need(atom_update(*got) == state, f"target update is not an involution at {state}")
                        need(got[0] == x and got[1] == y and got[4] == scratch,
                             f"input or scratch changed at {state}")
                        checked += 1
    need(checked == 1024, "incomplete dirty-state domain")

    # Two load-bearing negative controls: the delta contributes to both q lanes.
    witness = (1, 2, 0, 0, 3)  # x0=y1=1, all other input bits zero.
    expected_witness = reference_update(*witness)
    omit_delta = atom_update(*witness, include_delta=False)
    omit_q1 = atom_update(*witness, delta_q1=False)
    need(expected_witness != omit_delta, "negative control failed to detect omitted correction")
    need(expected_witness != omit_q1, "negative control failed to detect missing fanout coefficient")

    # A rank-r bilinear decomposition spans all output slices by at most r
    # product matrices. The three independent slices therefore force r >= 3.
    # The listed atoms attain r=3. Each separate center has slice-span rank 2,
    # so independent evaluation costs 2+2=4 rank-one products.
    need(gf2_rank([0b0001, 0b1000], 4) == 2, "first center rank control")
    need(gf2_rank([0b0011, 0b1010], 4) == 2, "second center rank control")

    # Favorable all-72-pairs scenario from the selected profile. This is a
    # sensitivity screen, not a witnessed word transformation.
    ceiling = load_ceiling()
    selected_profile = {int(r): int(n) for r, n in selected["selected"]["local_profile_per_call"].items()}
    selected_cap = Q(selected["ceiling"]["a_ceiling"])
    need(selected_profile == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8},
         "selected profile differs from pinned result")
    selected_replay_cap = ceiling.ceiling(selected_profile, 73, 896, 9, 64)
    need(selected_replay_cap[1] == selected_cap, "pinned selected ceiling no longer replays")

    candidate_profile = {1: Q(4825, 2), 2: 418, 3: 432, 4: 142, 5: 82, 8: 4}
    candidate_cap = ceiling.ceiling(candidate_profile, 73, 896, 9, 32)
    at_target = ceiling.relax(candidate_profile, 73, 896, 9, 32, Q(1, 99))
    need(candidate_cap[0] > selected_cap, "favorable candidate profile does not improve the selected ceiling")
    need(candidate_cap[1] < Q(1, 99), "screen incorrectly reaches the 1/99 target")
    need(at_target[0] > 1, "target obstruction is not certified by the pinned relaxation")
    need(sum(Q(n) * r for r, n in candidate_profile.items()) == Q(11109, 2),
         "candidate paid local mass mismatch")

    return {
        "status": "PASS_RANK1_CENTER_DELTA_EXACT_LOCAL_CONSTRUCTION",
        "scope": "Two explicit F2^2 bilinear centers with a rank-one difference; arbitrary dirty output panels and untouched scratch. No selected occurrence or kappa claim.",
        "selected_record_sha256": task["selected_record_sha256"],
        "base_commit": task["base_commit"],
        "source_sha256": pins,
        "maps": {
            "F0": ["x0*y0", "x1*y1"],
            "F1": ["x0*y0 + x0*y1", "x1*y1 + x0*y1"],
            "difference": ["x0*y1", "x0*y1"],
            "joint_update": "(p,q) -> (p+F0(x,y), q+F1(x,y)) over F2",
        },
        "general_rank_one_extension": {
            "statement": "If F and F+H each have bilinear rank r in one common frame, and H(x,y)=alpha(x)*beta(y)*c has rank one, then the paired dirty-target map (p,q)->(p+F,q+F+H) has rank at most r+1, versus separate rank 2r.",
            "saving_when_r_at_least_2": "at least r-1 children in the common-frame bilinear-rank model",
            "assumption": "The rank model charges bilinear products; linear output coefficient vectors are part of each tensor atom. Frame changes, copying, precision, hosting and restoration are outside this local lemma.",
        },
        "joint_rank_certificate": {
            "input_monomial_order": ["x0*y0", "x0*y1", "x1*y0", "x1*y1"],
            "output_slices": ["p0:E00", "p1:E11", "q0:E00+E01", "q1:E11+E01"],
            "flattening_rank_lower_bound": slice_rank,
            "rank_one_atoms": [
                {"product": "x0*y0", "output_vector_(p0,p1,q0,q1)": [1, 0, 1, 0]},
                {"product": "x1*y1", "output_vector_(p0,p1,q0,q1)": [0, 1, 0, 1]},
                {"product": "x0*y1", "output_vector_(p0,p1,q0,q1)": [0, 0, 1, 1]},
            ],
            "joint_rank": 3,
            "independent_center_ranks": [2, 2],
            "child_count_saved": 1,
        },
        "dirty_state_replay": {
            "field_domain": "x,y,p,q,scratch independently range over F2^2",
            "states_checked": checked,
            "all_match_direct_map": True,
            "target_update_is_involution": True,
            "inputs_and_scratch_preserved": True,
        },
        "negative_controls": {
            "omitted_rank_one_correction": "rejected by x=01,y=10,p=q=00,scratch=11",
            "omitted_second_output_coefficient": "rejected by same witness",
        },
        "optimistic_selected_profile_screen": {
            "assumption": "All 72 two-call pairs are eligible; no source/frame/hosting/precision/restoration overhead beyond the rank-one correction.",
            "selected_profile_per_call": {str(r): n for r, n in selected_profile.items()},
            "candidate_profile_per_call": {str(r): str(n) if isinstance(n, Q) else n for r, n in candidate_profile.items()},
            "selected_center_per_call": 64,
            "candidate_center_per_call": 32,
            "families": 896,
            "stages": 9,
            "m": 73,
            "rank_mass_saved_per_pair": 63,
            "selected_fixed_word_a_cap": [str(v) for v in selected_replay_cap],
            "candidate_fixed_word_a_cap": [str(v) for v in candidate_cap],
            "candidate_relaxation_at_1_over_99": [str(v) for v in at_target],
            "reaches_1_over_99": False,
            "supplier_or_kappa_claim": False,
        },
        "limitations": [
            "No eligible occurrence is identified in the selected supplier.",
            "No E8 frame, source/target hosting, recursive precision, or restoration integration is instantiated.",
            "The all-pairs profile is a favorable sensitivity screen, not an admitted paid-word change.",
        ],
    }


def main() -> None:
    expected = build_certificate()
    if "--emit-certificate" in sys.argv[1:]:
        print(json.dumps(expected, indent=2, sort_keys=True))
        return
    actual = json.loads((PACKAGE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    need(actual == expected, "certificate differs from exact replay")
    print(f"PASS_RANK1_CENTER_DELTA_EXACT_LOCAL_CONSTRUCTION states={expected['dirty_state_replay']['states_checked']} rank=3/4")


if __name__ == "__main__":
    main()
