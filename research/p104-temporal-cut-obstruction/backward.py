#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent reverse information-flow check for the frozen P104 frame word.

Uses explicit F2 span sets and backwards target relevance.  Imports no channel
producer, native compiler, or forward reachability checker.  No files are
modified.  This checks a temporal scalar-register cut, not a universal barrier.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path

WITNESS_SHA256 = "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e"
CUT_INDICES = (2463, 2472, 2479, 2487, 2495, 2503, 2510, 2518)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def span(generators) -> frozenset[int]:
    """Enumerate the full subspace; no canonical-basis routine is used."""
    values = {0}
    for generator in generators:
        require(isinstance(generator, int) and 0 <= generator < 512,
                "frame generator is outside F2^9")
        values |= {value ^ generator for value in tuple(values)}
    return frozenset(values)


def dimension(frame: frozenset[int]) -> int:
    require(len(frame) > 0 and len(frame) & (len(frame) - 1) == 0,
            "frame size is not a power of two")
    return len(frame).bit_length() - 1


def parse_word(witness: dict) -> tuple[dict, dict, list, dict]:
    """Check the chronological frame word and normalize each literal event."""
    initial = {register: span(gens)
               for register, gens in witness["initial_frames"].items()}
    final = {register: span(gens)
             for register, gens in witness["final_frames"].items()}
    require(len(initial) == 280 and set(initial) == set(final),
            "unexpected boundary register inventory")
    current = dict(initial)
    events = []
    positive_ranks = Counter()
    private_births = private_deaths = 0
    for index, event in enumerate(witness["program"]):
        kind = event[0]
        if kind == "transport":
            _, register, before_basis, after_basis, rank = event
            before, after = span(before_basis), span(after_basis)
            require(current.get(register) == before,
                    f"incorrect transport source frame at {index}")
            require(before <= after or after <= before,
                    f"nonnested transport at {index}")
            require(rank == abs(dimension(after) - dimension(before)) and rank > 0,
                    f"incorrect positive rank at {index}")
            events.append((kind, register, before, after, rank))
            current[register] = after
            positive_ranks[rank] += 1
        elif kind == "add":
            _, target, source, coefficient, frame_basis = event
            frame = span(frame_basis)
            require(current.get(target) == current.get(source) == frame,
                    f"unequal-frame scalar addition at {index}")
            Fraction(coefficient)  # Require an exact rational literal.
            events.append((kind, target, source, frame))
        elif kind == "zero":
            _, register, frame_basis = event
            frame = span(frame_basis)
            require(register not in current and register == "C",
                    f"private allocation overwrites a live register at {index}")
            current[register] = frame
            events.append((kind, register, frame))
            private_births += 1
        elif kind == "copy":
            _, target, source, frame_basis = event
            frame = span(frame_basis)
            require(current.get(target) == current.get(source) == frame,
                    f"unequal-frame private copy at {index}")
            require(target == "C", f"copy destination outside private role at {index}")
            events.append((kind, target, source, frame))
        elif kind == "erase":
            _, register, frame_basis = event
            frame = span(frame_basis)
            require(current.get(register) == frame and register == "C",
                    f"invalid private discard at {index}")
            del current[register]
            events.append((kind, register, frame))
            private_deaths += 1
        else:
            raise ValueError(f"unknown event kind {kind}")
    require(current == final, "final frames mismatch")
    require(private_births == private_deaths == 8, "private lifetime count mismatch")
    derived_cut = tuple(index for index, event in enumerate(events)
                        if event[0] == "transport" and event[1] == "C"
                        and dimension(event[2]) == 8 and dimension(event[3]) == 1)
    require(derived_cut == CUT_INDICES, "private drop edge indices mismatch")
    return initial, final, events, {
        "event_count": len(events),
        "transport_profile": {str(rank): count for rank, count in sorted(positive_ranks.items())},
        "private_lifetimes": private_births,
    }


def backwards(initial: dict, final: dict, events: list,
              blocked: frozenset[int]) -> dict:
    """Propagate arbitrary output dependence backwards through the supergraph.

    At every time cut, one relevant register makes *every* live register with
    the same complete F2 frame relevant.  These complete frame classes admit
    more scalar communication than the published word.  Blocked transport
    events delete only their through-register edge; all other registers retain
    their through-time identity edges.
    """
    frames = dict(final)
    relevant = {register for register in final if register.startswith("Y")}
    require(len(relevant) == 104, "target count mismatch")
    cut_relevance = []
    maximal_relevant = len(relevant)

    def mix() -> None:
        nonlocal maximal_relevant
        visible_frames = {frames[register] for register in relevant}
        relevant.update(register for register, frame in frames.items()
                        if frame in visible_frames)
        maximal_relevant = max(maximal_relevant, len(relevant))

    mix()
    for index in range(len(events) - 1, -1, -1):
        event = events[index]
        kind = event[0]
        if kind == "transport":
            _, register, before, after, _ = event
            require(frames[register] == after,
                    f"reverse frame mismatch at {index}")
            if index in blocked:
                cut_relevance.append({"index": index,
                                      "relevant_after_edge": register in relevant})
                relevant.discard(register)
            frames[register] = before
        elif kind == "copy":
            _, target, source, _ = event
            if target in relevant:
                relevant.add(source)
            # Assignment overwrites C.  The complete common-frame mix before
            # this event will independently restore any permitted dependence.
            relevant.discard(target)
        elif kind == "zero":
            _, register, frame = event
            require(frames[register] == frame, "reverse allocation mismatch")
            relevant.discard(register)
            del frames[register]
        elif kind == "erase":
            _, register, frame = event
            require(register not in frames, "reverse erase finds live private role")
            frames[register] = frame
        elif kind == "add":
            _, target, source, _ = event
            if target in relevant:
                relevant.add(source)
        mix()
    require(frames == initial, "backwards replay did not reach initial frames")
    reached_sources = sorted((register for register in relevant
                              if register.startswith("X")), key=lambda name: int(name[1:]))
    return {
        "source_count": len(reached_sources),
        "sources": reached_sources,
        "maximum_relevant_registers": maximal_relevant,
        "cut_relevance": sorted(cut_relevance, key=lambda row: row["index"]),
    }


def analyze(witness: dict) -> dict:
    """Check a caller-supplied witness; the caller owns source authentication."""
    initial, final, events, metadata = parse_word(witness)
    barrier = backwards(initial, final, events, frozenset(CUT_INDICES))
    require(barrier["source_count"] == 0,
            "a source-to-target path survives deletion of the eight drops")
    intact = backwards(initial, final, events, frozenset())
    require(intact["source_count"] == 104,
            "intact information graph lacks some source-to-target paths")
    restored = []
    for restored_index in CUT_INDICES:
        result = backwards(initial, final, events,
                           frozenset(set(CUT_INDICES) - {restored_index}))
        require(result["source_count"] > 0,
                "restoring one drop unexpectedly leaves a separating cut")
        restored.append({"restored_edge": restored_index,
                         "source_count": result["source_count"]})
    return {
        "status": "PASS_P104_BACKWARD_TEMPORAL_CUT",
        "algorithm": "reverse relevance with explicitly enumerated F2 span classes",
        **metadata,
        "deleted_transport_indices": list(CUT_INDICES),
        "blocked_source_count": barrier["source_count"],
        "intact_source_count": intact["source_count"],
        "single_restored_edge_controls": restored,
        "scope": "Frozen frame chronology, arbitrary scalar mixing within each exact frame class; no supplier or kappa claim.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("witness", nargs="?", type=Path,
                        default=Path(__file__).resolve().parents[1] /
                        "p104-native-channel" / "inputs" / "LOWRANK-WITNESS.json")
    args = parser.parse_args()
    payload = args.witness.read_bytes()
    require(hashlib.sha256(payload).hexdigest() == WITNESS_SHA256,
            "source witness SHA256 mismatch")
    result = analyze(json.loads(payload))
    result["witness_sha256"] = WITNESS_SHA256
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
