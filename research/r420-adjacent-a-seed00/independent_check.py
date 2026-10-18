#!/usr/bin/env python3
"""Independent exact check of R420 adjacent A-gate frame rigidity. Apache-2.0.

Uses Fraction elimination, closed-root sets and full symbolic A replays.
Imports no other project checker.
Prepared for Sagar Thakrar with substantial OpenAI Codex assistance.
"""

import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def echelon(rows):
    basis = {}
    for row in rows:
        row = list(map(Fraction, row))
        for pivot in sorted(basis):
            scale = row[pivot]
            if scale:
                row = [a - scale * b for a, b in zip(row, basis[pivot])]
        pivot = next((j for j, value in enumerate(row) if value), None)
        if pivot is not None:
            scale = row[pivot]
            basis[pivot] = [value / scale for value in row]
    return basis


def inside(row, basis):
    row = list(map(Fraction, row))
    for pivot in sorted(basis):
        scale = row[pivot]
        if scale:
            row = [a - scale * b for a, b in zip(row, basis[pivot])]
    return not any(row)


def orthogonal(basis, dimension):
    result = []
    for free in range(dimension):
        if free in basis:
            continue
        vector = [Fraction(int(j == free)) for j in range(dimension)]
        for pivot in sorted(basis, reverse=True):
            vector[pivot] = -sum(
                basis[pivot][j] * vector[j] for j in range(pivot + 1, dimension)
            )
        result.append(vector)
    return result


def main():
    path = Path(__file__).resolve().parents[1] / "e8-bit-r420/data/bitE8mut-r420.json.gz"
    raw = path.read_bytes()
    require(
        hashlib.sha256(raw).hexdigest()
        == "9721a3819efd68307f66f00d84a952eb28eb7c3ad2ce79653ce295c98a764784",
        "source word SHA256 differs from pinned PR543 R420 word",
    )
    word = json.loads(gzip.decompress(raw))
    gates = word["A"]
    frames = list(map(frozenset, word["frames"]))
    lines = word["lines"]
    dimension = word["h"]
    bases = [echelon(lines[line] for line in frame) for frame in frames]
    ranks = list(map(len, bases))
    perpendiculars = [orthogonal(basis, dimension) for basis in bases]
    require(len(set(frames)) == len(frames), "duplicate catalogue frames")
    for index, frame in enumerate(frames):
        closure = frozenset(j for j, line in enumerate(lines) if inside(line, bases[index]))
        require(closure == frame, f"frame {index} is not closed")
        require(
            all(sum(a * b for a, b in zip(row, normal)) == 0
                for row in bases[index].values() for normal in perpendiculars[index]),
            f"frame {index} has an invalid orthogonal basis",
        )
        require(
            len(echelon(perpendiculars[index])) + ranks[index] == dimension,
            f"frame {index} has an incomplete orthogonal basis",
        )

    operands = [set([destination] + sources) for _, destination, sources in gates]
    before = []
    current = word["start"][:]
    for gate, registers in zip(gates, operands):
        before.append(current[:])
        for register in registers:
            current[register] = gate[0]
    end = current[:]
    after = []
    current = end[:]
    for gate, registers in zip(reversed(gates), reversed(operands)):
        after.append(current[:])
        for register in registers:
            current[register] = gate[0]
    after.reverse()

    def replay(sequence, check_frames=True):
        values = [1 << register for register in range(len(word["start"]))]
        current = word["start"][:]
        jumps = Counter()
        for frame, destination, sources in sequence:
            if check_frames:
                for register in [destination] + sources:
                    old = current[register]
                    if old != frame:
                        require(frames[old] < frames[frame] and ranks[old] < ranks[frame],
                                f"illegal ascent for register {register}: {old} to {frame}")
                        jumps[ranks[frame] - ranks[old]] += 1
                        current[register] = frame
            for source in sources:
                values[destination] ^= values[source]
        return values, current, jumps

    baseline = replay(gates)
    census = Counter()
    commuting = rejected = same_destination = 0
    for index in range(len(gates) - 1):
        left, right = gates[index:index + 2]
        swapped = gates[:index] + [right, left] + gates[index + 2:]
        if left[1] in right[2] or right[1] in left[2]:
            require(replay(swapped, check_frames=False)[0] != baseline[0],
                    f"dependency negative control {index} did not change the symbolic map")
            rejected += 1
            continue
        commuting += 1
        same_destination += left[1] == right[1]
        for gate_index in (index, index + 1):
            registers = operands[gate_index]
            lower = set().union(*(frames[before[index][r]] for r in registers))
            upper_ids = [after[index + 1][r] for r in registers]
            low_rank = len(echelon(lines[line] for line in lower))
            upper_rank = dimension - len(echelon(
                vector for frame in upper_ids for vector in perpendiculars[frame]
            ))
            original = gates[gate_index][0]
            require(lower <= frames[original]
                    and all(frames[original] <= frames[frame] for frame in upper_ids),
                    f"original frame not between pair {index} gate {gate_index} boundaries")
            require(low_rank == upper_rank == ranks[original],
                    f"pair {index} gate {gate_index} has subspace freedom")
            census[low_rank] += 1
        require(replay(swapped) == baseline,
                f"pair {index} changed the A map, boundary frames or rank-jump histogram")

    require((commuting, rejected, same_destination) == (1735, 328, 726),
            "adjacent-pair census changed")
    require(census == {1: 479, 2: 360, 4: 2140, 6: 480, 8: 11},
            "forced-frame dimension census changed")
    require(baseline[2] == {1: 600, 2: 989, 4: 60}, "A rank-jump histogram changed")
    print("PASS independent exact check: 672 closed frames; 1735 rigid commuting pairs;")
    print("1735 equal symbolic maps, A-end frames and histograms; 328 dependency controls rejected.")
    print("Forced-frame rank census:", json.dumps(dict(sorted(census.items()))))
    print("A rank-jump histogram:", json.dumps(dict(sorted(baseline[2].items()))))


if __name__ == "__main__":
    main()
