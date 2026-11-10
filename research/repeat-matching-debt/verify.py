"""Exact new-result checks. Produced by Nick Petalas. Apache-2.0."""

import argparse
from collections import deque
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import book_walk, color, prefix_budget, require, support_data


def walk(word: tuple[int, ...]) -> tuple[int, ...]:
    path = [0]
    for bit in word:
        path.append(path[-1] ^ (1 << bit))
    require(path[-1] == 0, "fixture does not close")
    return tuple(path)


def check_walk(n: int, path: tuple[int, ...], omitted: int) -> int:
    positions = path[:-1]
    support = frozenset(positions)
    projected = {x & ~(1 << omitted) for x in support}
    if len(projected) < 2:
        return 0  # Explicitly excluded domain, counted separately.
    data = support_data(n, omitted, support)
    # Independent contraction by set pairs, without the model's pair formula.
    cells = {frozenset((x, x ^ (1 << omitted))) for x in support}
    components = tuple(sum(color(min(cell), omitted) == j for cell in cells)
                       for j in (0, 1))
    require(components == data["components"], "component count mismatch")
    occurrences = tuple(sum(color(x, omitted) == j for x in positions)
                        for j in (0, 1))
    repeats = tuple(occurrences[j] - data["sizes"][j] for j in (0, 1))
    crossing = sum(color(x, omitted) != color(y, omitted)
                   for x, y in zip(path, path[1:]))
    require(crossing % 2 == 0, "odd closed-cut crossing count")
    require(crossing >= 2 * max(components), "component crossing floor")
    require(all(repeats[j] >= data["debt"][j] for j in (0, 1)),
            "repetition bound failed")
    for k in range(1, len(path)):
        budget = prefix_budget(n, omitted, support, len(positions), positions[:k])
        lo, hi = budget["repeat_zero_interval"]
        require(budget["possible"] and lo <= repeats[0] <= hi,
                "a literal completion was rejected")
    return len(positions)


def exhaustive_walks() -> list[dict]:
    results = []
    domains = ((2, 4), (2, 6), (2, 8), (3, 4), (3, 6), (3, 8),
               (3, 10), (4, 4), (4, 6), (4, 8))
    for n, length in domains:
        closed = checked = excluded = prefixes = repeated = universal = 0
        for word in product(range(n), repeat=length):
            if any(word.count(j) % 2 for j in range(n)):
                continue
            path = walk(word)
            support = frozenset(path[:-1])
            closed += 1
            repeated += len(support) < length
            universal += len({x ^ y for x in support for y in support}) == 1 << n
            for omitted in range(n):
                count = check_walk(n, path, omitted)
                checked += count != 0
                excluded += count == 0
                prefixes += count
        results.append({"n": n, "length": length, "closed_words": closed,
                        "repeated_words": repeated, "universal_words": universal,
                        "walk_omissions": checked, "excluded_one_component": excluded,
                        "prefix_omissions": prefixes})
    return results


def shortest_cover(support: frozenset[int], n: int) -> int:
    """Independent BFS over every support-restricted walk, including repeats."""
    vertices = sorted(support)
    require(len(vertices) <= 12, "BFS fixture exceeds twelve vertices")
    bit = {x: 1 << i for i, x in enumerate(vertices)}
    full = (1 << len(vertices)) - 1
    initial = (bit[0], 0)
    queue = deque([(initial, 0)])
    seen = {initial}
    capacity = len(vertices) * (1 << len(vertices))
    for _ in range(capacity):
        if not queue:
            break
        (mask, x), distance = queue.popleft()
        if mask == full and x.bit_count() == 1:
            return distance + 1
        for axis in range(n):
            y = x ^ (1 << axis)
            if y in support:
                state = (mask | bit[y], y)
                if state not in seen:
                    seen.add(state)
                    queue.append((state, distance + 1))
    raise ValueError("BFS found no closed covering walk")


def sharp_family() -> list[dict]:
    rows = []
    for pages in range(1, 17):
        path = book_walk(pages)
        length = len(path) - 1
        support = frozenset(path[:-1])
        require(length == 3 * pages + pages % 2, "book length")
        require(len(support) == 2 * pages + 2, "book support")
        check_walk(pages + 1, path, 0)
        data = support_data(pages + 1, 0, support)
        debt = sum(data["debt"])
        rounded = debt + ((debt - len(support)) % 2)
        require(length - len(support) == rounded, "unattained rounded debt")
        if pages <= 5:
            require(shortest_cover(support, pages + 1) == length, "BFS optimum")
        rows.append({"pages": pages, "length": length, "distinct": len(support),
                     "debt": debt, "repetitions": length - len(support)})
    return rows


def controls() -> int:
    path = book_walk(3)
    support = frozenset(path[:-1])
    rejected = 0
    cases = ((1, 0, support, 10, (0,)), (4, 4, support, 10, (0,)),
             (4, 0, support, 9, (0,)), (4, 0, support, 6, (0,)),
             (4, 0, support, 66, (0,)), (4, 0, support, 10, (0, 3)),
             (4, 0, support, 10, (0, 16)), (4, 0, support, 10, ()),
             (4, 0, frozenset((0, 1)), 4, (0,)))
    for args in cases:
        try:
            prefix_budget(*args)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("malformed input was accepted")
    require(not prefix_budget(4, 0, support, 8, (0,))["possible"], "lost debt")
    square = frozenset((0, 1, 2, 3))
    require(not prefix_budget(2, 0, square, 4, (0, 1, 0))["possible"],
            "lost prefix repeats")
    require(prefix_budget(4, 0, support, 10, (0,))["possible"], "positive budget")
    require(not prefix_budget(4, 0, support, 10, (0, 2, 0, 2, 0))["possible"],
            "lost class-specific budget")
    simple = book_walk(2)
    data = support_data(3, 0, frozenset(simple[:-1]))
    require(sum(data["debt"]) == 0, "simple positive control")
    require(data["sizes"][1] - data["sizes"][0] == 2,
            "pair-omission mutation not detected")
    return rejected + 6


def receipt() -> dict:
    root = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "model.py", "verify.py")
    hashes = {}
    for name in names:
        raw = (root / name).read_bytes()
        require(len(raw) <= 2 * 1024 * 1024, "oversized package source")
        hashes[name] = hashlib.sha256(raw).hexdigest()
    return {"schema_version": 1, "source_sha256": hashes,
            "walk_domains": exhaustive_walks(), "sharp_family": sharp_family(),
            "controls": controls(), "status": "PASS_REPEAT_MATCHING_DEBT"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit-receipt", action="store_true")
    args = parser.parse_args()
    result = receipt()
    if args.emit_receipt:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        root = Path(__file__).resolve().parent
        raw = (root / "RESULT.json").read_bytes()
        require(len(raw) <= 2 * 1024 * 1024, "oversized receipt")
        require(json.loads(raw) == result, "receipt or source mismatch")
        print(result["status"])
        print(json.dumps({"closed_words": sum(x["closed_words"] for x in result["walk_domains"]),
                          "walk_omissions": sum(x["walk_omissions"] for x in result["walk_domains"]),
                          "prefix_omissions": sum(x["prefix_omissions"] for x in result["walk_domains"]),
                          "attaining_fixtures": len(result["sharp_family"]),
                          "controls": result["controls"]}, sort_keys=True))


if __name__ == "__main__":
    main()
