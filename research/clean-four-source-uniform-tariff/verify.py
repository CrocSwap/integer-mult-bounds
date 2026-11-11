#!/usr/bin/env python3
"""Exact four-source clean-row tariff certificate. Apache-2.0."""
from collections import deque
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
from random import Random


WORDS = (
    (0, 1, 0, 2, 1, 3, 2, 3),
    (0, 1, 0, 2, 0, 1, 0, 3, 2, 3),
    (0, 1, 0, 2, 0, 1, 0, 3, 0, 2, 0, 3),
    (0, 1, 0, 2, 0, 1, 0, 3, 0, 1, 0, 2, 1, 3),
    (0, 1, 0, 2, 0, 1, 0, 3, 0, 1, 0, 2, 0, 1, 0, 3),
)
PROFILES = ((8, 23), (10, 21), (12, 19), (14, 17), (16, 15))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def prefixes(word):
    require(isinstance(word, tuple) and len(word) <= 16, "word capacity")
    result = [0]
    for label in word:
        require(type(label) is int and 0 <= label < 4, "source label")
        result.append(result[-1] ^ (1 << label))
    require(result[-1] == 0, "owned row not restored")
    return result


def representations(values):
    """Shortest paths in the additive group, with explicit finite bounds."""
    require(len(values) <= 15 and len(set(values)) == len(values), "value set")
    require(all(type(v) is int and 1 <= v <= 15 for v in values), "mask")
    paths = [None] * 16
    paths[0] = ()
    queue = deque([0])
    for _ in range(16):
        if not queue:
            break
        current = queue.popleft()
        for value in values:
            target = current ^ value
            if paths[target] is None:
                paths[target] = paths[current] + (value,)
                queue.append(target)
    require(not queue, "additive-state capacity")
    return paths


def subset_distances(values):
    """Independent 0/1 subset dynamic program, not a group-graph BFS."""
    distances = [99] * 16
    distances[0] = 0
    for value in values:
        old = distances
        distances = [min(old[m], 1 + old[m ^ value]) for m in range(16)]
    return distances


def schedule(word):
    walk = prefixes(word)
    values = tuple(sorted(set(walk) - {0}))
    paths = representations(values)
    require(all(p is not None for p in paths), "source span")
    at_vertex = [[] for _ in range(16)]
    for target in range(1, 16):
        for value in paths[target]:
            at_vertex[value].append(target)
    calls = [("allocate", 0), ("zero", 0)]
    used = set()
    for index, label in enumerate(word):
        calls.append(("B", label))
        vertex = walk[index + 1]
        if vertex not in used:
            calls.extend(("A", target) for target in at_vertex[vertex])
            used.add(vertex)
    calls.append(("release", 0))
    return tuple(calls), tuple(paths)


def check_formal(calls):
    require(len(calls) <= 50, "call capacity")
    active = False
    allocated = False
    released = False
    current = None
    outputs = [0] * 16
    counts = [0, 0]
    for kind, index in calls:
        if kind == "allocate":
            require(not allocated and not released, "allocation lifetime")
            allocated = True
        elif kind == "zero":
            require(allocated and not active and not released, "zero lifetime")
            active = True
            current = 0
        elif kind in ("A", "B"):
            require(active and not released, "call lifetime")
            if kind == "B":
                require(type(index) is int and 0 <= index < 4, "B index")
                current ^= 1 << index
                counts[0] += 1
            else:
                require(type(index) is int and 1 <= index < 16, "A index")
                outputs[index] ^= current
                counts[1] += 1
        elif kind == "release":
            require(active and not released and current == 0, "release restoration")
            released = True
            active = False
        else:
            raise ValueError("unknown call")
    require(released and outputs == list(range(16)), "target endpoint")
    return tuple(counts)


def closed_visited_sets():
    """All useful walks, merging states only by position and visited set."""
    # Zero is always visited, so at most 16 * 2^15 states exist.
    start = (1 << 4)
    distances = {start: 0}
    queue = deque([start])
    closed = {}
    for _ in range(16 * (1 << 15)):
        if not queue:
            break
        state = queue.popleft()
        length = distances[state]
        position, visited = state & 15, state >> 4
        if position == 0 and visited not in closed:
            closed[visited] = length
        if length == 16:
            continue
        for label in range(4):
            next_position = position ^ (1 << label)
            if length + 1 + next_position.bit_count() > 16:
                continue
            next_visited = visited | (1 << next_position)
            next_state = (next_visited << 4) | next_position
            if next_state not in distances:
                distances[next_state] = length + 1
                queue.append(next_state)
    require(not queue, "walk-state capacity")
    return closed, len(distances)


def check_oracle():
    closed, state_count = closed_visited_sets()
    candidates = []
    spanning = 0
    spectrum = {}
    for visited, length in sorted(closed.items()):
        values = tuple(m for m in range(1, 16) if visited & (1 << m))
        paths = representations(values)
        distances = subset_distances(values)
        require(distances == [99 if p is None else len(p) for p in paths],
                "independent XOR distances")
        if 99 in distances:
            continue
        spanning += 1
        reads = sum(distances)
        spectrum[length] = min(spectrum.get(length, 99), reads)
        candidates.append((length, reads))
    frontier = []
    best_reads = 99
    for pair in sorted(set(candidates)):
        if pair[1] < best_reads:
            frontier.append(pair)
            best_reads = pair[1]
    frontier = tuple(frontier)
    require(frontier == PROFILES, "exact finite frontier")
    require(tuple(sorted(spectrum.items())) == PROFILES, "length spectrum")
    return candidates, {"walk_states": state_count, "closed_sets": len(closed),
                        "spanning_closed_sets": spanning, "frontier": frontier}


def check_prices(candidates):
    prices = [(Fraction(b), Fraction(a)) for b in range(1, 13)
              for a in range(1, 13)]
    prices += [(Fraction(1, 3), Fraction(2, 7)),
               (Fraction(2, 7), Fraction(1, 3)), (Fraction(5, 11), Fraction(5, 11))]
    for b, a in prices:
        actual = min(length * b + reads * a for length, reads in candidates)
        require(actual == min(8 * b + 23 * a, 16 * b + 15 * a), "price theorem")
    return len(prices)


def linear_map(rows, value):
    return sum(((row & value).bit_count() % 2) << i for i, row in enumerate(rows))


def execute(calls, source_maps, output_maps, initial):
    # Layout: four two-bit sources; fifteen two-bit outputs; three owned bits;
    # three untouched dirty-connector bits. All 44 incoming bits are admitted.
    sources = tuple((initial >> (2 * j)) & 3 for j in range(4))
    outputs = [(initial >> (8 + 2 * j)) & 3 for j in range(15)]
    owned = (initial >> 38) & 7
    dirty = (initial >> 41) & 7
    for kind, index in calls:
        if kind == "zero":
            owned = 0
        elif kind == "B":
            owned ^= linear_map(source_maps[index], sources[index])
        elif kind == "A":
            outputs[index - 1] ^= linear_map(output_maps[index - 1], owned)
        else:
            require(kind in ("allocate", "release"), "execution action")
    expected = [(initial >> (8 + 2 * j)) & 3 for j in range(15)]
    for target in range(1, 16):
        combined = 0
        for j in range(4):
            if target & (1 << j):
                combined ^= linear_map(source_maps[j], sources[j])
        expected[target - 1] ^= linear_map(output_maps[target - 1], combined)
    require(outputs == expected and owned == 0, "rectangular endpoint")
    require(sources == tuple((initial >> (2 * j)) & 3 for j in range(4)), "source")
    require(dirty == ((initial >> 41) & 7), "dirty connector")


def check_endpoints(schedules):
    total = 0
    states = [0] + [1 << bit for bit in range(44)]
    states += [((1 << 44) - 1) // (i + 1) for i in range(1, 17)]
    for seed in range(16):
        rng = Random(seed)
        source_maps = tuple(tuple(rng.randrange(4) for _ in range(3))
                            for _ in range(4))
        output_maps = tuple(tuple(rng.randrange(8) for _ in range(2))
                            for _ in range(15))
        if seed == 0:
            source_maps = ((0, 0, 0),) * 4
            output_maps = ((0, 0),) * 15
        for calls in schedules:
            for initial in states:
                execute(calls, source_maps, output_maps, initial)
                total += 1
    return total


def check_controls(schedules):
    rejected = 0
    for calls in schedules:
        for index in range(len(calls)):
            # Every emitted call in an attaining schedule is essential.
            try:
                check_formal(calls[:index] + calls[index + 1:])
            except ValueError:
                rejected += 1
            else:
                raise ValueError("deleted-call control accepted")
    for word in ((4, 4), (0,), (True, True), tuple([0] * 18)):
        try:
            prefixes(word)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid-word control accepted")
    return rejected


def source_bindings(package):
    metadata = json.loads((package / "SOURCES.json").read_text())
    root = package.parent.parent
    for row in metadata["files"]:
        if row["usage"] == "input":
            require(sha256((root / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                    "source hash: " + row["path"])
    return {p.name: sha256(p.read_bytes()).hexdigest()
            for p in sorted(package.iterdir()) if p.is_file()}


def main():
    package = Path(__file__).resolve().parent
    hashes = source_bindings(package)
    schedules = []
    for word, expected in zip(WORDS, PROFILES, strict=True):
        calls, _ = schedule(word)
        require(check_formal(calls) == expected, "attaining profile")
        schedules.append(calls)
    candidates, coverage = check_oracle()
    coverage["price_comparisons"] = check_prices(candidates)
    coverage["rectangular_executions"] = check_endpoints(schedules)
    coverage["rejecting_controls"] = check_controls(schedules)
    print(json.dumps({"status": "PASS_CLEAN_FOUR_SOURCE_UNIFORM_TARIFF",
                      "coverage": coverage, "sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
