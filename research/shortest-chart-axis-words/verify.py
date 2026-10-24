"""Independent graph counts and literal shortest-word certificate."""

import hashlib
import itertools
import json
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import words


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArithmeticError(message)


def span(rows: tuple[int, ...]) -> frozenset[int]:
    result = {0}
    for row in rows:
        result |= {x ^ row for x in result}
    return frozenset(result)


def lagrangians(n: int) -> list[frozenset[int]]:
    """Enumerate RREF spaces, independently of the transvection graph."""
    require(1 <= n <= 3, "certificate enumeration bound")
    spaces = []
    for pivots in itertools.combinations(range(2 * n), n):
        cells = [(i, j) for i, p in enumerate(pivots)
                 for j in range(p + 1, 2 * n) if j not in pivots]
        for bits in range(1 << len(cells)):
            rows = [1 << p for p in pivots]
            for k, (i, j) in enumerate(cells):
                rows[i] |= ((bits >> k) & 1) << j
            isotropic = all(sum(((a >> j) & 1) * ((b >> (j + n)) & 1)
                                + ((b >> j) & 1) * ((a >> (j + n)) & 1)
                                for j in range(n)) % 2 == 0
                            for a in rows for b in rows)
            if isotropic:
                spaces.append(span(tuple(rows)))
    require(len(set(spaces)) == len(spaces), "duplicate RREF chart")
    return spaces


def graph_certificate(n: int) -> dict[str, int]:
    charts = lagrangians(n)
    edges = [[j for j, b in enumerate(charts) if len(a & b) == 1 << (n - 1)]
             for a in charts]
    pair_checks = 0
    for target in range(len(charts)):
        depths = [-1] * len(charts)
        paths = [0] * len(charts)
        depths[target], paths[target] = 0, 1
        queue = deque([target])
        for _ in range(len(charts)):
            require(bool(queue), "disconnected chart graph")
            node = queue.popleft()
            for neighbor in edges[node]:
                if depths[neighbor] == -1:
                    depths[neighbor] = depths[node] + 1
                    queue.append(neighbor)
                if depths[neighbor] == depths[node] + 1:
                    paths[neighbor] += paths[node]
        require(not queue, "graph traversal bound exceeded")
        for start, chart in enumerate(charts):
            r = n - ((len(chart & charts[target])).bit_length() - 1)
            require(depths[start] == r, "minimum-length formula")
            require(paths[start] == words.count(n, r, literal=False), "chart path count")
            actual = sum(words.distance(words.move(chart, a, n), charts[target], n) == r - 1
                         for a in range(1, 1 << (2 * n))) if r else 0
            expected = (1 << (n - 1)) * ((1 << r) - 1)
            require(actual == expected, "shortest-word first-letter count")
            require(words.count(n, r) == paths[start] * (1 << (r * (n - 1))),
                    "literal-word multiplicity")
            pair_checks += 1
    return {"n": n, "charts": len(charts), "ordered_pairs": pair_checks}


def literal_certificate() -> dict[str, int]:
    executions = 0
    roundtrips = 0
    for n in (1, 2):
        charts = lagrangians(n)
        for left in charts:
            for right in charts:
                r = words.distance(left, right, n)
                actual = []
                for word in itertools.product(range(1, 1 << (2 * n)), repeat=r):
                    current = left
                    for axis in word:
                        current = words.move(current, axis, n)
                    if current == right:
                        actual.append(word)
                    executions += 1
                require(len(actual) == words.count(n, r), "literal exhaustive count")
                for index, word in enumerate(actual):
                    require(words.unrank(left, right, n, index) == word, "lexicographic unrank")
                    require(words.rank(left, right, n, word) == index, "lexicographic rank")
                    roundtrips += 1
    return {"enumerated_axis_words": executions, "all_small_word_roundtrips": roundtrips}


def larger_and_controls() -> dict[str, int]:
    samples = 0
    for n in range(3, 7):
        left = span(tuple(1 << i for i in range(n)))
        for r in range(n + 1):
            right = span(tuple(1 << (i + n if i < r else i) for i in range(n)))
            total = words.count(n, r)
            for index in sorted({0, total // 2, total - 1}):
                word = words.unrank(left, right, n, index)
                require(words.rank(left, right, n, word) == index, "larger roundtrip")
                samples += 1
    good = frozenset({0, 1, 2, 3})
    target = frozenset({0, 4, 8, 12})
    controls = [lambda: words.count(0, 0), lambda: words.count(2, 3),
                lambda: words.count(True, 0), lambda: words.validate(good, 7),
                lambda: words.validate(frozenset({0, 1, 2, 4}), 2),
                lambda: words.validate(frozenset({0, 1, 4, 5}), 2),
                lambda: words.unrank(good, target, 2, -1),
                lambda: words.unrank(good, target, 2, 12),
                lambda: words.rank(good, target, 2, (1,)),
                lambda: words.rank(good, target, 2, (0, 4)),
                lambda: words.rank(good, target, 2, (1, 4))]
    for check in controls:
        try:
            check()
        except ValueError:
            continue
        raise ArithmeticError("rejection control unexpectedly accepted")
    return {"larger_roundtrips": samples, "rejection_controls": len(controls)}


def main() -> None:
    result = {"status": "PASS_SHORTEST_CHART_AXIS_WORDS",
              "graph_certificates": [graph_certificate(n) for n in (1, 2, 3)],
              **literal_certificate(), **larger_and_controls()}
    package = Path(__file__).resolve().parent
    result["source_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sorted(package.iterdir()) if p.is_file()}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
