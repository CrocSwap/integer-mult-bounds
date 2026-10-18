#!/usr/bin/env python3
"""Independent finite checks for four reviewed positive-transfer splices.

This module imports no predecessor verifier, search code, or composition
builder. Integer maps are recovered one input column at a time. Boolean maps
are separately replayed on every local input.

Composition argument: each new forward block matrix equals its old matrix,
and each new reversed-positive block matrix is entrywise no greater. Embed
these maps as identity outside the block registers. All intervening matrices
have nonnegative entries, so substitution in their ordered product preserves
forward equality and reverse domination. This does not require disjoint wire
sets; the source intervals must be disjoint. The full B products are also
checked directly below. Within a positive-addition block, every intermediate
coordinate is bounded by its terminal coordinate on nonnegative inputs.

Literal reverse cleanup is an inverse over F2 because every singleton addition
is an involution there. That statement does not assert equality of the complete
positive-integer word including cleanup. Full-word cleanup, hosting, and native
accounting checks belong to the composition verifier.

Prepared with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path


SOURCE_WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
SPECS = (
    (507, 128, 163, 30, (0, 3, 11, 61, 62, 63, 68, 69, 72, 465),
     "research/r439-block1-schedule/CANDIDATE.json"),
    (519, 163, 205, 32, (15, 23, 30, 41, 49, 53, 59, 70, 75, 82, 91, 96),
     "research/r439-frame519-seed02/CANDIDATE.json"),
    (508, 205, 242, 30, (19, 27, 35, 43, 57, 65, 66, 74, 89, 97, 466),
     "research/r439-block508-schedule/CERTIFICATE.json"),
    (524, 449, 490, 27, (8, 12, 31, 37, 40, 45, 73, 78, 81, 86, 105, 110),
     "research/r439-frame524-seed13/CANDIDATE.json"),
)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def load_blocks(root):
    """Decode only the pinned four witnesses, normalizing physical gates."""
    blocks = []
    for frame, start, stop, count, registers, source in SPECS:
        item = json.loads((Path(root) / source).read_text(encoding="utf-8"))
        if frame == 507:
            need(item["phase"] == "B" and item["frame"] == frame
                 and item["start"] == start and item["stop"] == stop,
                 "frame507 witness binding changed")
            need(item["registers"] == list(registers), "frame507 wire order changed")
            gates = []
            for op in item["replacement"]:
                need(type(op) is list and len(op) == 2
                     and all(type(x) is int and 0 <= x < len(registers) for x in op),
                     "invalid frame507 local index")
                gates.append([frame, registers[op[0]], [registers[op[1]]]])
        elif frame == 508:
            binding = item["binding"]
            need(binding["section"] == "B" and binding["frame"] == frame
                 and binding["slice"] == [start, stop]
                 and binding["registers"] == list(registers),
                 "frame508 witness binding changed")
            gates = item["gates"]
        elif frame == 519:
            need(item["frame"] == frame and item["slice"] == [start, stop]
                 and item["registers"] == list(registers),
                 "frame519 witness binding changed")
            gates = [g for factor in item["factors"] for g in factor["program"]]
        else:
            need(item["frame"] == frame and item["source_range"] == [start, stop]
                 and item["registers"] == list(registers),
                 "frame524 witness binding changed")
            gates = item["candidate_gates"]
        need(len(gates) == count, "predecessor gate count changed")
        blocks.append(dict(frame=frame, start=start, stop=stop,
                           registers=list(registers), gates=gates, source=source))
    return blocks


def validate_gates(gates, registers, frame=None, singleton=False):
    allowed = set(registers)
    need(type(gates) is list, "gate sequence must be a list")
    for gate in gates:
        need(type(gate) is list and len(gate) == 3, "malformed gate")
        f, dst, sources = gate
        need(type(f) is int and f >= 0 and (frame is None or f == frame),
             "wrong gate frame")
        need(type(dst) is int and dst in allowed, "unexpected destination")
        need(type(sources) is list and sources, "empty or malformed source list")
        need(not singleton or len(sources) == 1, "non-elementary replacement")
        need(all(type(src) is int and src in allowed and src != dst for src in sources),
             "unexpected or self source")
        need(len(sources) == len(set(sources)), "duplicate source")


def transfer_columns(gates, registers, reverse=False):
    """Recover a matrix as columns by separately executing integer unit inputs."""
    positions = {r: i for i, r in enumerate(registers)}
    order = list(reversed(gates)) if reverse else gates
    columns = []
    for input_wire in range(len(registers)):
        values = [int(j == input_wire) for j in range(len(registers))]
        for _, dst, sources in order:
            for src in sources:
                values[positions[dst]] += values[positions[src]]
        columns.append(values)
    return columns


def boolean_table(gates, registers):
    """Independent truth-table interpreter using one packed scalar per input."""
    positions = {r: i for i, r in enumerate(registers)}
    result = []
    for bits in range(1 << len(registers)):
        state = bits
        for _, dst, sources in gates:
            parity = 0
            for src in sources:
                parity ^= (state >> positions[src]) & 1
            state ^= parity << positions[dst]
        result.append(state)
    return result


def participants(gates):
    return sorted({wire for _, dst, sources in gates for wire in [dst, *sources]})


def domination_counts(old, new):
    need(len(old) == len(new) and all(len(a) == len(b) for a, b in zip(old, new)),
         "matrix dimensions differ")
    need(all(b <= a for col_a, col_b in zip(old, new) for a, b in zip(col_a, col_b)),
         "reverse-positive domination failed")
    return sum(b < a for col_a, col_b in zip(old, new) for a, b in zip(col_a, col_b))


def verify_blocks(word, blocks, candidate_b=None):
    """Check exact witnesses and their combined B map; return fresh evidence."""
    need(type(blocks) is list and len(blocks) == len(SPECS), "wrong block set")
    need(type(word.get("B")) is list, "source lacks B")
    original_b = word["B"]
    combined_b = []
    cursor = 0
    receipts = []
    for block, spec in zip(blocks, SPECS):
        frame, start, stop, count, registers, source = spec
        need(type(block) is dict, "block must be an object")
        need(all(type(block.get(k)) is int for k in ("frame", "start", "stop")),
             "noninteger block binding")
        need(type(block.get("registers")) is list
             and all(type(r) is int for r in block["registers"]),
             "noninteger register binding")
        need((block["frame"], block["start"], block["stop"]) == (frame, start, stop)
             and block["registers"] == list(registers) and block["source"] == source,
             "block binding changed")
        need(cursor <= start < stop <= len(original_b), "overlapping or invalid slices")
        old = original_b[start:stop]
        new = block["gates"]
        validate_gates(old, registers, frame, singleton=True)
        validate_gates(new, registers, frame, singleton=True)
        need(len(new) == count, "replacement length changed")
        need(participants(old) == participants(new) == list(registers),
             "changed physical participant set")
        old_forward = transfer_columns(old, registers)
        new_forward = transfer_columns(new, registers)
        need(old_forward == new_forward, "local integer map differs")
        old_reverse = transfer_columns(old, registers, reverse=True)
        new_reverse = transfer_columns(new, registers, reverse=True)
        strict = domination_counts(old_reverse, new_reverse)
        old_table, new_table = boolean_table(old, registers), boolean_table(new, registers)
        need(old_table == new_table, "local Boolean truth table differs")
        inverse_table = boolean_table(list(reversed(new)), registers)
        need(all(inverse_table[value] == i for i, value in enumerate(new_table)),
             "literal local Boolean inverse failed")
        receipts.append(dict(frame=frame, source_slice=[start, stop],
                             original_adds=len(old), replacement_adds=len(new),
                             registers=list(registers), boolean_inputs=len(old_table),
                             integer_forward_equal=True,
                             reverse_positive_dominated=True,
                             reverse_strict_entries=strict,
                             forward_columns_sha256=digest(old_forward),
                             old_reverse_columns_sha256=digest(old_reverse),
                             new_reverse_columns_sha256=digest(new_reverse),
                             gates_sha256=digest(new)))
        combined_b.extend(copy.deepcopy(original_b[cursor:start]))
        combined_b.extend(copy.deepcopy(new))
        cursor = stop
    combined_b.extend(copy.deepcopy(original_b[cursor:]))
    all_registers = participants(original_b)
    if candidate_b is not None:
        validate_gates(candidate_b, all_registers)
        need(candidate_b == combined_b, "candidate B differs from independent composition")
    validate_gates(original_b, all_registers)
    validate_gates(combined_b, all_registers)
    need(participants(combined_b) == all_registers, "combined B participants changed")
    old_map = transfer_columns(original_b, all_registers)
    new_map = transfer_columns(combined_b, all_registers)
    need(old_map == new_map, "combined B integer map differs")
    old_reverse = transfer_columns(original_b, all_registers, reverse=True)
    new_reverse = transfer_columns(combined_b, all_registers, reverse=True)
    strict = domination_counts(old_reverse, new_reverse)
    old_adds = sum(len(g[2]) for g in original_b)
    new_adds = sum(len(g[2]) for g in combined_b)
    need(old_adds - new_adds == 36, "combined B saving differs from 36")
    return dict(status="PASS_R439_FOUR_BLOCK_MAPS", blocks=receipts,
                original_b_adds=old_adds, replacement_b_adds=new_adds,
                forward_adds_saved=old_adds - new_adds,
                boolean_inputs=sum(x["boolean_inputs"] for x in receipts),
                combined_register_count=len(all_registers),
                combined_forward_equal=True, combined_reverse_dominated=True,
                combined_reverse_strict_entries=strict,
                combined_forward_columns_sha256=digest(old_map),
                old_combined_reverse_columns_sha256=digest(old_reverse),
                new_combined_reverse_columns_sha256=digest(new_reverse),
                combined_b_sha256=digest(combined_b))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    word = json.loads(gzip.decompress((args.root / SOURCE_WORD).read_bytes()))
    print(json.dumps(verify_blocks(word, load_blocks(args.root)), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
