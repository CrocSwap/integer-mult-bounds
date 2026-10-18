#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared for Hao Yan (@FanPUYen) with substantial OpenAI Codex assistance.
# The original circuit is DreamingOfClouds' PR #503/#510 R480 adaptation of
# eumemic's PR #493 carrier skeleton. The mutable-source interface follows
# Zhihao Chen's PR #425, as documented in the predecessor package.
"""Independent set-valued audit of the seed-1 R480 six-wire replacement.

No producer, synthesis, pricing, or primary-verifier module is imported.  Every
register carries a set of formal input columns and addition is symmetric
difference.  The six-wire check treats its inputs as independently dirty even
though they are correlated at the actual point in the complete word.

This checks finite word semantics over F2 and the inherited mutable-source interface.
It does not prove the all-size compiler, a finite-prefix invoice, or a saving
constant.  The positive-integer transfer certificate is checked separately.

Usage: python independent_check.py --word /path/to/full-word.json[.gz]
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parent / "e8-r480-dead-totals/data/bitE8mut-r480.json.gz"
ORIGINAL_SHA256 = "92e399e9a486b55229b5624632ac54f800dd9e022f2aee97f1e5f264bbc0ef5c"
START, END, FRAME = 621, 639, 303
WIRES = (487, 504, 550, 574, 598, 622)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_word(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def reduced_basis(rows):
    """Canonical rational row reduction, independent of the word generators."""
    rows = [[Fraction(x) for x in row] for row in rows]
    pivot_row = 0
    for col in range(8):
        candidates = [i for i in range(pivot_row, len(rows)) if rows[i][col]]
        if not candidates:
            continue
        chosen = candidates[0]
        rows[pivot_row], rows[chosen] = rows[chosen], rows[pivot_row]
        factor = rows[pivot_row][col]
        rows[pivot_row] = [x / factor for x in rows[pivot_row]]
        for i in range(len(rows)):
            if i != pivot_row:
                factor = rows[i][col]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[pivot_row])]
        pivot_row += 1
    return tuple(tuple(row) for row in rows[:pivot_row])


class Frames:
    def __init__(self, word):
        self.bases = [reduced_basis([word["lines"][r] for r in frame])
                      for frame in word["frames"]]
        self.ranks = [len(basis) for basis in self.bases]
        zero = [i for i, rank in enumerate(self.ranks) if rank == 0]
        full = [i for i, rank in enumerate(self.ranks) if rank == 8]
        require(len(zero) == len(full) == 1, "unique zero and full frames")
        self.zero, self.full = zero[0], full[0]
        self.nested_cache = {}

    def nested(self, lower, upper):
        pair = lower, upper
        if pair not in self.nested_cache:
            combined = self.bases[lower] + self.bases[upper]
            self.nested_cache[pair] = reduced_basis(combined) == self.bases[upper]
        return self.nested_cache[pair]


def check_interface(word, frames):
    v = word["v"]
    n = 2 * v + word["R"]
    is_target = lambda r: v <= r < 2 * v
    is_z = lambda r: 0 <= r < n and not is_target(r)
    for section in ("D", "A", "B", "C"):
        for f, destination, sources in word[section]:
            if is_z(destination):
                require(all(is_z(s) for s in sources), "target feeds source/helper")
    require(all(f == frames.zero and is_target(d)
                and all(2 * v <= s < n for s in sources)
                for f, d, sources in word["D"]), "dirty correction interface")
    require(all(is_z(d) for _, d, _ in word["A"]), "A writes target")
    require(all(is_target(d) for _, d, _ in word["B"]), "B writes source/helper")
    require(all(f == frames.full and is_z(d) and all(is_z(s) for s in sources)
                for f, d, sources in word["C"]), "cleanup interface")
    z_gates = [[frames.full, d, sources] for section in ("A", "B")
               for _, d, sources in word[section] if is_z(d)]
    require(word["C"] == list(reversed(z_gates)), "cleanup is not literal inverse")
    require(len(word["scatter"]) == v
            and all(type(k) is int and 0 <= k < len(word["ret"])
                    for row in word["scatter"] for k in row), "scatter interface")
    require(all(2 * v <= q < n for q in word["ret"]), "total is not a helper")


def replay(word, frames, track_frames=True):
    """All formal columns at once, represented by Python sets (not bit masks)."""
    v = word["v"]
    n = 2 * v + word["R"]
    state = [{i} for i in range(n)]
    current = list(word["start"])
    paths = [[f] for f in current]
    climbs = Counter()

    def climb(register, frame):
        previous = current[register]
        if frame == previous:
            return
        require(frames.ranks[previous] < frames.ranks[frame]
                and frames.nested(previous, frame), "non-nested frame climb")
        climbs[frames.ranks[frame] - frames.ranks[previous]] += 1
        current[register] = frame
        paths[register].append(frame)

    def run(gates):
        for frame, destination, sources in gates:
            registers = [destination] + sources
            require(type(frame) is int and 0 <= frame < len(frames.bases), "invalid frame")
            require(all(type(r) is int and 0 <= r < n for r in registers)
                    and len(set(registers)) == len(registers), "invalid gate registers")
            if track_frames:
                for register in registers:
                    climb(register, frame)
            for source in sources:
                state[destination].symmetric_difference_update(state[source])

    run(word["D"])
    if track_frames:
        require(all(current[r] == frames.zero for r in range(v, n)), "D moved non-source")
    run(word["A"])
    if track_frames:
        require(all(current[v + t] == frames.zero for t in range(v)), "target left zero before scatter")
        require(all(current[q] == frames.full for q in word["ret"]), "total not at full frame")
    totals = [set(state[q]) for q in word["ret"]]
    for t, row in enumerate(word["scatter"]):
        for k in row:
            state[v + t].symmetric_difference_update(totals[k])
    run(word["B"])
    run(word["C"])
    if track_frames:
        for register, frame in enumerate(word["final"]):
            climb(register, frame)
    return state, paths, climbs


def require_identity_plus_source(state, v=120):
    for register, support in enumerate(state):
        expected = {register, register - v} if v <= register < 2 * v else {register}
        require(support == expected, f"formal column map fails at register {register}")


def local_map(gates):
    state = {wire: {i} for i, wire in enumerate(WIRES)}
    for frame, destination, sources in gates:
        require(frame == FRAME and destination in state and len(sources) == 1
                and sources[0] in state and sources[0] != destination, "local six-wire gate")
        state[destination].symmetric_difference_update(state[sources[0]])
    return [sorted(state[wire]) for wire in WIRES]


def candidate_block(original, candidate):
    require(candidate.keys() == original.keys(), "word schema changed")
    require(all(candidate[key] == original[key] for key in original if key not in ("A", "C")),
            "non-A/C data changed")
    suffix_length = len(original["A"]) - END
    new_end = len(candidate["A"]) - suffix_length
    require(START < new_end < END, "replacement is not strictly shorter")
    require(candidate["A"][:START] == original["A"][:START]
            and candidate["A"][new_end:] == original["A"][END:], "A changed outside selected quad")
    return candidate["A"][START:new_end]


def expect_rejected(name, operation):
    try:
        operation()
    except ValueError as error:
        return {"name": name, "rejected": True, "reason": str(error)}
    raise ValueError(f"negative control accepted: {name}")


def controls(candidate, block, local_expected, frames):
    results = []
    # Reflecting every deletion into C preserves literal source/helper cleanup;
    # a clean-input-only test could miss the changed local dirty-helper action.
    for omitted in range(len(block)):
        mutant = deepcopy(candidate)
        del mutant["A"][START + omitted]
        mutant["C"] = [[frames.full, d, sources] for _, d, sources in reversed(mutant["A"])]
        check_interface(mutant, frames)
        shortened = block[:omitted] + block[omitted + 1:]
        result = expect_rejected(
            f"omit_local_gate_{omitted}_and_reflect_cleanup",
            lambda gates=shortened: require(local_map(gates) == local_expected,
                                           "arbitrary six-wire dirty-input map changed"))
        output, _, _ = replay(mutant, frames, track_frames=False)
        result["full_word_map_also_changed"] = any(
            support != ({r, r - 120} if 120 <= r < 240 else {r})
            for r, support in enumerate(output))
        results.append(result)

    for name, predicate in (("omit_helper_cleanup", lambda d: d >= 240),
                            ("omit_source_cleanup", lambda d: d < 120)):
        mutant = deepcopy(candidate)
        index = next(i for i, (_, d, _) in enumerate(mutant["C"]) if predicate(d))
        del mutant["C"][index]
        results.append(expect_rejected(name, lambda word=mutant:
                       require_identity_plus_source(replay(word, frames, False)[0])))

    mutant = deepcopy(candidate)
    removed = mutant["D"][0][2].pop(0)
    result = expect_rejected("omit_one_dirty_correction_source", lambda:
                            require_identity_plus_source(replay(mutant, frames, False)[0]))
    result["omitted_dirty_column"] = removed
    results.append(result)

    mutant = deepcopy(candidate)
    mutant["A"][START][0] = frames.zero
    results.append(expect_rejected("move_one_local_gate_to_zero_frame", lambda:
                                  replay(mutant, frames)))
    return results


def audit(word_path):
    require(hashlib.sha256(ORIGINAL.read_bytes()).hexdigest() == ORIGINAL_SHA256,
            "pinned original word bytes changed")
    original, candidate = load_word(ORIGINAL), load_word(word_path)
    block = candidate_block(original, candidate)
    frames = Frames(original)
    expected_local = local_map(original["A"][START:END])
    require(local_map(block) == expected_local, "local arbitrary dirty-input map changed")
    for word in (original, candidate):
        check_interface(word, frames)
    original_state, original_paths, original_climbs = replay(original, frames)
    state, paths, climbs = replay(candidate, frames)
    require_identity_plus_source(original_state)
    require_identity_plus_source(state)
    require(state == original_state, "original/candidate symbolic maps differ")
    require(paths == original_paths, "a register's frame path changed")
    require(climbs == original_climbs, "paid climb histogram changed")
    negative_controls = controls(candidate, block, expected_local, frames)
    return {
        "status": "PASS_INDEPENDENT_SET_VALUED_DIRTY_INPUT_REPLAY",
        "original_file_sha256": ORIGINAL_SHA256,
        "candidate_content_sha256": digest(candidate),
        "formal_columns": len(state),
        "source_columns": 120,
        "target_columns": 120,
        "dirty_helper_columns": 480,
        "all_source_and_helper_columns_restored": True,
        "all_targets_add_exactly_their_source": True,
        "local_arbitrary_dirty_input_columns": len(WIRES),
        "local_matrix_supports": expected_local,
        "interface_hypotheses_checked": True,
        "selected_frame": FRAME,
        "selected_frame_exact_rational_rank": frames.ranks[FRAME],
        "all_720_register_frame_paths_identical": True,
        "register_path_sha256": digest(paths),
        "local_paid_climb_histogram": dict(sorted(climbs.items())),
        "old_local_gate_count": END - START,
        "new_local_gate_count": len(block),
        "negative_controls": negative_controls,
        "scope": "Finite word and local arbitrary dirty-input semantics; no prefix invoice, all-size compiler, or saving-constant claim.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", type=Path, required=True)
    parser.add_argument("--json", type=Path, help="optional receipt path")
    args = parser.parse_args()
    result = audit(args.word)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
