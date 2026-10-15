#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Verify the all-depth parity floor for the pinned QQ16 cover-map action."""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
CERTIFICATE = ROOT / "research/joint-query/certificate.json.gz"
CERTIFICATE_SHA256 = "a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7"
BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
PORT_FRAMES = {
    0: "f117",
    7: "f124",
    20: "f137",
    27: "f144",
    36: "f153",
    46: "f163",
    57: "f174",
    111: "f228",
}
PRIVATE_FRAME = "f0"
DIMENSION = 73


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def bits(value: int):
    while value:
        low = value & -value
        yield low.bit_length() - 1
        value ^= low


def canonical(entries):
    coefficients = {}
    for axis, coefficient in entries:
        coefficients[axis] = (coefficients.get(axis, 0) + coefficient) % 4
    return tuple(sorted((axis, coefficient)
                        for axis, coefficient in coefficients.items()
                        if coefficient))


def act(columns, vector: int) -> int:
    out = 0
    for index in bits(vector):
        out ^= columns[index]
    return out


def rank_columns(columns) -> int:
    basis = {}
    for column in columns:
        value = column
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return len(basis)


def frame_terms(record):
    return canonical((int(axis), int(coefficient))
                     for axis, coefficient in record["line_terms_Z4"])


def output_frame(stage: int, port: int, label: int):
    """Rebuild the Y-port boundary frame from the pinned native recipe."""
    entries = [(1 << index, 1) for index in range(9 + 8 * stage)]
    entries.append((label, -1))
    return canonical(entries)


def odd_support(terms):
    return frozenset(axis for axis, coefficient in terms if coefficient & 1)


def move_frame(terms, mapping):
    columns = mapping["owner_right_matrix_columns"]
    shift = int(mapping["payload_translation_at_identity_owner"])
    moved = [(act(columns, axis), coefficient) for axis, coefficient in terms]
    moved.extend((1 << index, 2) for index in bits(shift))
    return canonical(moved)


def load_packet():
    raw = CERTIFICATE.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == CERTIFICATE_SHA256,
         "pinned QQ16 certificate digest")
    task = json.loads((PACKAGE / "TASK.json").read_text())
    need(task["base_commit"] == BASE_COMMIT, "scientific base pin")
    return json.loads(gzip.decompress(raw))


def run():
    packet = load_packet()
    need(packet["schema"] == "conserved-qq16-full-cover-native-words-v1",
         "pinned QQ16 certificate schema")
    need("M(g,delta)f(d,z_1,...,z_lambda)=" in packet["cover_map_semantics"],
         "cover-map action formula present")
    need(packet["map_composition"] ==
         "(g,a)(h,b)=(g*h,a XOR g*b); inverse=(g^-1,g^-1*a).",
         "pinned cover-map composition law")

    frames = packet["native_frame_registry"]
    private = frame_terms(frames[PRIVATE_FRAME])
    need(not private, "private C fields return to frame I")
    port_terms = {}
    for port, frame_id in PORT_FRAMES.items():
        need(frame_id in frames, f"registered frame {frame_id}")
        terms = frame_terms(frames[frame_id])
        recipe = packet["native_line_recipes"][f"positive_{port}"]
        rebuilt = output_frame(1, port, int(recipe["label"]))
        need(terms == rebuilt, f"frame {frame_id} matches the Y_A port recipe")
        need(len(terms) == 18, f"18 exact Z4 terms in {frame_id}")
        need(all(coefficient in (1, 3) for _, coefficient in terms),
             f"all {frame_id} terms are odd")
        port_terms[port] = terms

    maps = packet["map_registry"]
    need(len(maps) == 3650, "complete registered cover-map inventory")
    map_records = list(maps.values())
    for index, mapping in enumerate(map_records):
        columns = [int(value) for value in mapping["owner_right_matrix_columns"]]
        need(len(columns) == DIMENSION, f"map {index} matrix width")
        need(all(0 <= column < (1 << DIMENSION) for column in columns),
             f"map {index} matrix range")
        need(rank_columns(columns) == DIMENSION,
             f"map {index} owner action is invertible")
        shift = int(mapping["payload_translation_at_identity_owner"])
        need(0 <= shift < (1 << DIMENSION), f"map {index} translation range")

    checked_actions = 0
    for terms in port_terms.values():
        before = len(odd_support(terms))
        for mapping in map_records:
            moved = move_frame(terms, mapping)
            need(len(odd_support(moved)) == before,
                 "cover map changed odd-support weight")
            checked_actions += 1

    # A concrete depth-two path is a positive control for iterated action.
    first = map_records[1]
    second = map_records[10]
    sample = port_terms[0]
    direct = move_frame(move_frame(sample, first), second)
    need(len(odd_support(direct)) == 18,
         "positive control: two composed maps preserve the 18 odd terms")

    # Controls show both hypotheses matter: an odd payload shift can cancel
    # an odd term, and a singular owner action is rejected by the rank check.
    odd_shift_control = canonical(((1, 1), (1, 3)))
    need(not odd_shift_control, "negative control: odd shift can cancel parity")
    one_line_edit = canonical(((1, 1), (1, -1)))
    need(len(odd_support(((1, 1),))) - len(odd_support(one_line_edit)) == 1,
         "one-term line edit can cancel only its selected parity bit")
    singular_columns = list(map_records[0]["owner_right_matrix_columns"])
    singular_columns[1] = singular_columns[0]
    need(rank_columns(singular_columns) < DIMENSION,
         "negative control: duplicated owner column is singular")

    per_port_floor = len(odd_support(next(iter(port_terms.values()))))
    need(per_port_floor == 18, "one-term line floor per port")
    total_floor = per_port_floor * len(port_terms)
    need(total_floor == 144 and total_floor > 2,
         "full line floor exceeds favorable two-call slack")

    result = {
        "status": "PASS_QQ16_MAP_PARITY_FLOOR",
        "source_base": BASE_COMMIT,
        "certificate_sha256_compressed": CERTIFICATE_SHA256,
        "registered_maps": len(map_records),
        "invertible_owner_maps": len(map_records),
        "source_frames": {str(port): PORT_FRAMES[port]
                          for port in PORT_FRAMES},
        "odd_terms_per_source_frame": per_port_floor,
        "target_odd_terms": len(odd_support(private)),
        "direct_map_frame_checks": checked_actions,
        "two_map_positive_control": "18 odd terms remain after two exact actions",
        "one_term_line_calls_lower_bound": total_floor,
        "cover_map_operations_at_two_per_line": 2 * total_floor,
        "scalar_copy_primitives": 8 * 4,
        "terminal_clear_primitives": 8,
        "extra_clear_if_existing_next_core_runs": 0,
        "favorable_extra_rank_one_equivalent_budget": 2,
        "all_depth_conclusion": "cover maps preserve mod-2 odd-support weight; depth two, three, and all larger depths retain the 144-line floor",
        "controls": [
            "two-map composition preserves odd-support weight",
            "odd coefficient shift can cancel an odd term",
            "one-term line correction toggles at most its selected parity bit",
            "singular owner action is rejected",
        ],
        "scope": "Eight pinned Y_A frames at the post-B_1_2 cut; registered invertible cover-map actions and the one-term Z4 line model only.",
        "no_controller_or_kappa_claim": True,
    }
    receipt = PACKAGE / "RESULT.json"
    if receipt.exists():
        recorded = json.loads(receipt.read_text())
        need(recorded == result, "reproduced result receipt")
    print("PASS_QQ16_MAP_PARITY_FLOOR "
          f"ports={len(port_terms)} maps={len(map_records)} "
          f"frame_checks={checked_actions} lines={total_floor} "
          f"cover_maps={2 * total_floor} no_kappa")
    return result


if __name__ == "__main__":
    run()
