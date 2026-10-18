#!/usr/bin/env python3
"""Exact finite reduction for two dirty F2 roots; standard library only.

Adam Gall, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from functools import lru_cache
from itertools import combinations_with_replacement, permutations, product


def dot(a, b):
    return (a & b).bit_count() & 1


def transfer(rows, target):
    a, b = rows
    return (a ^ b, b) if target == 0 else (a, a ^ b)


def inverse_columns(rows):
    return tuple(next(v for v in (1, 2, 3)
                      if (dot(rows[0], v), dot(rows[1], v)) == unit)
                 for unit in ((1, 0), (0, 1)))


def pairings(n=5):
    """Restricted-growth labels, each used exactly twice."""
    def visit(word, counts, fresh):
        if len(word) == 2 * n:
            yield tuple(word)
            return
        for label in range(fresh):
            if counts[label] == 1:
                counts[label] = 2
                word.append(label)
                yield from visit(word, counts, fresh)
                word.pop()
                counts[label] = 1
        if fresh < n:
            counts[fresh] = 1
            word.append(fresh)
            yield from visit(word, counts, fresh + 1)
            word.pop()
            counts[fresh] = 0
    yield from visit([], [0] * n, 0)


def matchings(n=5):
    """Independent least-free-endpoint matching generator."""
    def visit(free, pairs):
        if not free:
            word = [0] * (2 * n)
            for label, (a, b) in enumerate(sorted(pairs)):
                word[a] = word[b] = label
            yield tuple(word)
            return
        for b in free[1:]:
            yield from visit(tuple(k for k in free if k not in (free[0], b)),
                             pairs + [(free[0], b)])
    yield from visit(tuple(range(2 * n)), [])


def prefixes(word):
    points = [0]
    for label in word:
        points.append(points[-1] ^ (1 << label))
    return points


@lru_cache(maxsize=None)
def differences(bits):
    points = [i for i in range(32) if bits >> i & 1]
    result = 0
    for a in points:
        for b in points:
            result |= 1 << (a ^ b)
    return result


def eligible_pairs(words):
    """Necessary relaxed universal coverage; complementary partition once."""
    result = []
    for word in words:
        diff = {a ^ b for a in prefixes(word) for b in prefixes(word)}
        for part in range(1, 16):  # source 4 always in the other nonempty part
            if any(m not in diff and m & part and m & (31 ^ part)
                   for m in range(32)):
                continue
            relaxed = diff | {m & part for m in diff} | {m & (31 ^ part) for m in diff}
            if len(relaxed) == 32:
                result.append((word, part))
    return result


def eligible_pairs_independent(words):
    result = []
    for word in words:
        vertices = [set()]
        for label in word:
            vertices.append(vertices[-1] ^ {label})
        for part in range(1, 16):
            groups = [set(range(5)), {j for j in range(5) if part >> j & 1},
                      {j for j in range(5) if not (part >> j & 1)}]
            masks = set()
            for group in groups:
                values = [v & group for v in vertices]
                masks.update(sum(1 << j for j in a ^ b) for a in values for b in values)
            if len(masks) == 32:
                result.append((word, part))
    return result


def closed_loops(length):
    result = []
    for word in product((0, 1), repeat=length):
        rows = (1, 2)
        for target in word:
            rows = transfer(rows, target)
        if rows == (1, 2):
            result.append(word)
    return result


def orbit(word):
    return {word[k:] + word[:k] for k in range(len(word))} | {
        tuple(1 - p for p in word[k:] + word[:k]) for k in range(len(word))}


def skeleton(word, loop, cuts, directions):
    """Return physical B/transfer events or None for an unavailable injection."""
    rows = (1, 2)
    operations = []
    phase = 0
    for at in range(11):
        while phase < len(loop) and cuts[phase] == at:
            operations.append(["T", loop[phase]])
            rows = transfer(rows, loop[phase])
            phase += 1
        if at < 10:
            columns = inverse_columns(rows)
            direction = directions[word[at]]
            if direction not in columns:
                return None
            operations.append(["B", word[at], columns.index(direction)])
    return operations


def literal_history(operations):
    """Seven independent bits: source increments 0..4, dirt 5..6."""
    roots = [32, 64]
    history = [(0, p, roots[p]) for p in (0, 1)]
    for cut, op in enumerate(operations, 1):
        if op[0] == "T":
            roots[op[1]] ^= roots[1 - op[1]]
        else:
            roots[op[2]] ^= 1 << op[1]
        history.extend((cut, p, roots[p]) for p in (0, 1))
    return roots, history


def literal_coverage(operations):
    roots, history = literal_history(operations)
    if roots != [32, 64]:
        return None
    return {a ^ b for _, _, a in history for _, _, b in history if (a ^ b) < 32}


def segment_census(loop, candidates):
    frames = [(1, 2)]
    for target in loop:
        frames.append(transfer(frames[-1], target))
    placements = list(combinations_with_replacement(range(11), len(loop)))
    histogram = Counter()
    visited = 0
    for word, part in candidates:
        points = prefixes(word)
        for u, v in permutations((1, 2, 3), 2):
            directions = [u if part >> j & 1 else v for j in range(5)]
            active = [0] + [sum(1 << j for j in range(5) if dot(r, directions[j]))
                            for r in (1, 2, 3)]
            segments = []
            for frame in frames:
                columns = inverse_columns(frame)
                phase = []
                for start in range(11):
                    row = [None] * 11
                    bits = [0, 0]
                    for end in range(start, 11):
                        if end > start and directions[word[end - 1]] not in columns:
                            break
                        for port in (0, 1):
                            bits[port] |= 1 << (points[end] & active[frame[port]])
                        row[end] = tuple(bits)
                    phase.append(row)
                segments.append(phase)
            for middle in placements:
                visited += 1
                bounds = (0,) + middle + (10,)
                seen = [0] * 4
                for phase, frame in enumerate(frames):
                    values = segments[phase][bounds[phase]][bounds[phase + 1]]
                    if values is None:
                        break
                    seen[frame[0]] |= values[0]
                    seen[frame[1]] |= values[1]
                else:
                    covered = differences(seen[1]) | differences(seen[2]) | differences(seen[3])
                    histogram[covered.bit_count()] += 1
    return {"placements_tested": visited, "admissible": sum(histogram.values()),
            "histogram": dict(sorted(histogram.items()))}


def direct_census(loop, candidates):
    """Independent backward final-column ports and literal seven-bit replay.

    Unlike segment_census this never computes readout dot products or unions
    phase-prefix tables. Suffix maps determine each physical injection port.
    """
    suffix = [(1, 2)] * (len(loop) + 1)
    # Store columns: right multiplication by the next shear changes one column.
    for phase in range(len(loop) - 1, -1, -1):
        a, b = suffix[phase + 1]
        suffix[phase] = (a, a ^ b) if loop[phase] == 0 else (a ^ b, b)
    histogram = Counter()
    visited = 0
    placements = list(combinations_with_replacement(range(11), len(loop)))
    for word, part in candidates:
        for u, v in permutations((1, 2, 3), 2):
            directions = [u if part >> j & 1 else v for j in range(5)]
            for cuts in placements:
                visited += 1
                phase = 0
                ports = []
                for at, label in enumerate(word):
                    while phase < len(loop) and cuts[phase] <= at:
                        phase += 1
                    columns = suffix[phase]
                    if directions[label] not in columns:
                        break
                    ports.append(columns.index(directions[label]))
                else:
                    operations = []
                    phase = 0
                    for at in range(11):
                        while phase < len(loop) and cuts[phase] == at:
                            operations.append(["T", loop[phase]])
                            phase += 1
                        if at < 10:
                            operations.append(["B", word[at], ports[at]])
                    covered = literal_coverage(operations)
                    if covered is None:
                        raise ValueError("backward-column restoration disagreement")
                    histogram[len(covered)] += 1
    return {"placements_tested": visited, "admissible": sum(histogram.values()),
            "histogram": dict(sorted(histogram.items()))}
