#!/usr/bin/env python3
"""Bounded auxiliary-state/return-marker screen on the selected R420 word.

This is a favorable cost relaxation, not an executable improved supplier.
Prepared for Ishan (@ishan-1729) with substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0
"""

from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("exterior_verifier", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def rank_f2(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


def replay(word, dimensions, cleanup=True):
    n = 2 * word["v"] + word["R"]
    current = word["start"][:]
    values = [1 << r for r in range(n)]
    profile, xors = Counter(), Counter()

    def climb(register, frame):
        old = current[register]
        if old != frame:
            v.need(set(word["frames"][old]) <= set(word["frames"][frame]), "non-nested climb")
            delta = dimensions[frame] - dimensions[old]
            v.need(delta > 0, "nonpositive climb")
            profile[delta] += 1
            current[register] = frame

    def gates(section):
        for frame, dst, sources in word[section]:
            for register in [dst] + sources:
                climb(register, frame)
            for source in sources:
                values[dst] ^= values[source]
                xors[section] += 1

    gates("D")
    gates("A")
    # Retained helper copies are still paid and targets are still at frame zero.
    v.need(all(dimensions[current[word["v"] + t]] == 0 for t in range(word["v"])),
           "target left zero before scatter")
    for register in word["ret"]:
        profile[dimensions[current[register]]] += 1
    for target, retained_indices in enumerate(word["scatter"]):
        for index in retained_indices:
            values[word["v"] + target] ^= values[word["ret"][index]]
    gates("B")
    if cleanup:
        gates("C")
    # Keep the original endpoint contract even when the scalar cleanup is gifted.
    for register, frame in enumerate(word["final"]):
        climb(register, frame)
    return values, v.counts(profile), v.counts(xors)


def restored(values, word):
    ports = word["v"]
    for r, value in enumerate(values):
        expected = (1 << r) ^ (1 << (r - ports)) if ports <= r < 2 * ports else 1 << r
        v.need(value == expected, "restoration/target identity")


def fixed_outer(bit, complex_rate):
    # Literal seven-level/final-grid arithmetic of the pinned #626 assembly.
    eta = beta = Q(1, 10**24)
    s = min(bit, (1 - beta) * complex_rate) - Q(1, 10**27)
    a = Q(384599, 10**10)
    for _ in range(7):
        a = (1 - s) * s + s * a
    q = a * (1 - 2 * eta)
    margin = (1 - eta) * q / (1 + q)
    ticks = margin * 10**18
    return Q((ticks.numerator - 1) // ticks.denominator, 10**18)


def screen(word, frame_receipt, assembly):
    dimensions = [r["dimension"] for r in frame_receipt["frames"]]
    full = next(i for i, d in enumerate(dimensions) if d == 8)
    v.need(all(g[0] == full for g in word["C"]), "cleanup must use full frame")
    normal, profile, xors = replay(word, dimensions)
    restored(normal, word)
    ghost, relaxed_profile, _ = replay(word, dimensions, cleanup=False)
    ports, n = word["v"], len(normal)
    z = list(range(ports)) + list(range(2 * ports, n))
    target_mask = sum(1 << r for r in range(ports, 2 * ports))
    v.need(all(ghost[r] & target_mask == 0 for r in z), "target feeds a ghost register")
    target_ok = all(ghost[r] == normal[r] for r in range(ports, 2 * ports))
    v.need(target_ok and profile == relaxed_profile, "favorable relaxation changed target/profile")
    debt = [ghost[r] ^ (1 << r) for r in z]
    v.need(all(row for row in debt), "expected every source/helper row to carry debt")
    helper_mask = sum(1 << r for r in range(2 * ports, n))
    source_drift_rank = rank_f2(debt[:ports])
    helper_source_rank = rank_f2([ghost[r] & helper_mask for r in range(ports)])
    v.need(source_drift_rank == helper_source_rank == ports, "source drift is not surjective")
    witness = next(r for r in range(2 * ports, n) if (ghost[0] >> r) & 1)
    # Applying the exact ghost map twice gives y + Pz + PUz. A restored
    # canonical shear applied twice would give y. Test an explicit helper input.
    second_target_zero = (1 << ports) ^ (1 << 0) ^ ghost[0]
    v.need((second_target_zero >> witness) & 1, "second-call witness lost")
    rejected = []
    for name, values in [("no_cleanup", ghost)]:
        try:
            restored(values, word)
        except v.Reject:
            rejected.append(name)
        else:
            raise v.Reject("incorrect ghost return accepted")
    mutant = deepcopy(word)
    mutant["C"].pop()
    try:
        restored(replay(mutant, dimensions)[0], word)
    except v.Reject:
        rejected.append("last_cleanup_gate_omitted")
    else:
        raise v.Reject("omitted cleanup accepted")

    b, c, kappa = (Q(assembly[k]) for k in ("complex_lower", "bit_lower", "kappa"))
    v.need(assembly["binding"] == "complex" and c > b, "complex must bind")
    v.need(fixed_outer(c, b) == fixed_outer(2 * c, b) == kappa, "fixed assembly comparison")
    # Inherited rejected moment endpoint; this screen does not re-prove that moment.
    upper_b = b + Q(1, 10**24)
    endpoints = assembly["moments"]
    v.need(any(r["side"] == "complex" and not r["accept"] and Q(r["endpoint"]) == upper_b
               for r in endpoints), "complex upper endpoint not present")
    optimistic_cap = upper_b / (1 + upper_b)
    v.need(kappa < optimistic_cap < kappa + Q(1, 10**18), "next-grid favorable ceiling")
    return {
        "status": "PASS_R420_GHOST_RETURN_SCREEN",
        "scope": "Fixed word, frames, endpoint frames and global hosting; gift all scalar C work, retain every child/copy. No new construction or kappa.",
        "word_semantic_sha256": v.digest(word),
        "full_frame": full,
        "cleanup_gates": len(word["C"]),
        "cleanup_scalar_xors": xors["C"],
        "ordinary_child_profile": profile,
        "gifted_cleanup_child_profile": relaxed_profile,
        "rank_mass": sum(int(r) * count for r, count in profile.items()),
        "source_rows_with_debt": sum(ghost[r] != 1 << r for r in range(ports)),
        "helper_rows_with_debt": sum(ghost[r] != 1 << r for r in range(2 * ports, n)),
        "restoration_debt_rank_F2": rank_f2(debt),
        "debt_rows_sha256": v.digest(debt),
        "carryover_obstruction": {
            "source_drift_rank_F2": source_drift_rank,
            "helper_to_source_rank_F2": helper_source_rank,
            "unit_helper_input_register": witness,
            "original_sources_all_zero": True,
            "second_call_target": 0,
            "second_call_target_error": 1,
        },
        "correct_target_rows_before_return": ports,
        "columns_replayed": n,
        "rejected_return_controls": rejected,
        "assembly": {
            "source_semantic_sha256": v.digest(assembly),
            "bit_lower": str(c), "complex_lower": str(b), "kappa": str(kappa),
            "kappa_with_optimistically_doubled_bit_rate": str(fixed_outer(2 * c, b)),
            "complex_rejected_endpoint": str(upper_b),
            "complex_fixed_favorable_cap": str(optimistic_cap),
            "cap_minus_selected_kappa": str(optimistic_cap - kappa),
            "next_1e_minus_18_grid_tick_excluded": True,
        },
    }


def main():
    source = json.loads((HERE / "SOURCE.json").read_text())
    word = v.load_word(v.ROOT / source["word"]["path"], source)
    frame_receipt = v.build_receipt(word, source)
    v.need(frame_receipt == json.loads((HERE / "CERTIFICATE.json").read_text()), "frame certificate mismatch")
    assembly = json.loads((v.ROOT / source["assembly"]["path"]).read_text())
    v.need(v.digest(assembly) == source["assembly"]["semantic_sha256"], "assembly source mismatch")
    result = screen(word, frame_receipt, assembly)
    v.need(result == json.loads((HERE / "GHOST-SCREEN.json").read_text()), "ghost screen mismatch")
    print("PASS_R420_GHOST_RETURN_SCREEN: debt rank 539; 2973 gifted XORs; "
          "child profile unchanged; selected kappa unchanged; 2 rejected returns")


if __name__ == "__main__":
    try:
        main()
    except (v.Reject, OSError, ValueError, KeyError, TypeError) as error:
        print("REJECT:", error, file=sys.stderr)
        sys.exit(1)
