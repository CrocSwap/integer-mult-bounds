#!/usr/bin/env python3
"""Independent exact replay of the 48 singleton-read choices per R420 target.

Prepared for thakrarsagar with substantial OpenAI Codex assistance, including a
separate verification worker. Source construction: eumemic, PR543.
SPDX-License-Identifier: Apache-2.0

This uses rational row elimination, without importing the construction or
other checkers. The README supplies the argument covering all real subspaces.
"""

from collections import Counter
from fractions import Fraction
import gzip
import hashlib
from itertools import combinations, permutations, product
import json
from pathlib import Path


PAYLOAD_SHA256 = "e597e3885c0a8daa262afa5985ee2930443329126aece76d33159d81882bdcc2"
SOURCE = Path(__file__).resolve().parents[1] / "e8-bit-r420/data/bitE8mut-r420.json.gz"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def basis(rows):
    pivots = {}
    for row in rows:
        reduced = list(map(Fraction, row))
        for column, vector in sorted(pivots.items()):
            coefficient = reduced[column]
            if coefficient:
                reduced = [x - coefficient * y for x, y in zip(reduced, vector)]
        pivot = next((i for i, value in enumerate(reduced) if value), None)
        if pivot is not None:
            coefficient = reduced[pivot]
            pivots[pivot] = [value / coefficient for value in reduced]
    return list(pivots.values())


def main():
    payload = gzip.decompress(SOURCE.read_bytes())
    require(hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA256, "source pin mismatch")
    word = json.loads(payload)
    bases = {}

    def frame_basis(frame):
        if frame not in bases:
            bases[frame] = basis(word["lines"][i] for i in word["frames"][frame])
        return bases[frame]

    def rank(frame):
        return len(frame_basis(frame))

    def join_rank(left, right):
        return len(basis(frame_basis(left) + frame_basis(right)))

    require(len(word["B"]) == 837, "phase-B gate count changed")
    current = word["start"][:]
    # Scatter changes values at frame zero, so it makes no frame update.
    for frame, destination, sources in word["D"] + word["A"] + word["B"][:717]:
        for register in [destination] + sources:
            current[register] = frame

    tops = word["B"][717:]
    targets = {destination for _, destination, _ in tops}
    usage = Counter(source for _, _, sources in tops for source in sources)
    require(targets == set(range(120, 240)), "top targets changed")
    require(len(usage) == 360 and set(usage.values()) == {1}, "top sources are reused")
    require(not targets.intersection(usage), "a top source is a target")
    require(all(rank(word["final"][source]) == 8 for source in usage), "cleanup boundary changed")
    require(all(rank(frame) == 8 for frame, _, _ in word["C"]), "cleanup frame changed")
    require(all(not targets.intersection([dest] + src) for _, dest, src in word["C"]),
            "cleanup touches a target")

    profiles = Counter()
    per_target = Counter()
    source_pair_ranks = Counter()
    compatible_positions = Counter()
    forbidden_first_reads = 0
    candidates = 0
    for final_frame, target, sources in tops:
        require(len(sources) == 3, "top operand count changed")
        require(final_frame == word["final"][target], "target boundary changed")
        cell = current[target]
        initial = {source: current[source] for source in sources}
        require(rank(cell) == 2 and rank(final_frame) == 7, "target ranks changed")
        require(all(rank(frame) == 6 for frame in initial.values()), "source rank changed")
        require(all(join_rank(frame, final_frame) == 7 for frame in initial.values()),
                "source lies outside the target's final frame")
        compatible = [i for i, source in enumerate(sources)
                      if join_rank(cell, initial[source]) == 6]
        require(len(compatible) == 1, "target does not have exactly one compatible source")
        compatible_positions[compatible[0]] += 1
        for source in sources:
            if join_rank(cell, initial[source]) != 6:
                require(join_rank(cell, initial[source]) == 7, "unexpected first-read span")
                forbidden_first_reads += 1
        for left, right in combinations(sources, 2):
            source_pair_ranks[join_rank(initial[left], initial[right])] += 1

        for order in permutations(sources):
            for choices in product((0, 1), repeat=3):
                candidates += 1
                target_frame = cell
                source_frames = initial.copy()
                profile = Counter()
                for source, use_final in zip(order, choices):
                    read_frame = final_frame if use_final else initial[source]
                    if join_rank(target_frame, read_frame) != rank(read_frame):
                        break
                    for previous in (target_frame, source_frames[source]):
                        increment = rank(read_frame) - rank(previous)
                        if increment:
                            profile[increment] += 1
                    target_frame = source_frames[source] = read_frame
                else:
                    final_increment = 7 - rank(target_frame)
                    if final_increment:
                        profile[final_increment] += 1
                    for frame in source_frames.values():
                        profile[8 - rank(frame)] += 1
                    profiles[tuple(sorted(profile.items()))] += 1
                    per_target[target] += 1

    require(candidates == 5760, "candidate coverage changed")
    require(set(per_target) == targets and set(per_target.values()) == {8},
            "expected exactly eight legal schedules per target")
    require(profiles == {((1, 6), (5, 1)): 720, ((1, 5), (2, 1), (4, 1)): 240},
            "paid profile distribution changed")
    require(source_pair_ranks == {7: 360}, "source pair spans changed")
    require(compatible_positions == {0: 42, 1: 30, 2: 48}, "compatible positions changed")
    require(forbidden_first_reads == 240, "first-D6 negative-control coverage changed")
    print("PASS_INDEPENDENT_SPLIT_READS targets=120 candidates=5760 legal=960 "
          "baseline=720 promoted=240 rejected_first_D6=240")


if __name__ == "__main__":
    main()
