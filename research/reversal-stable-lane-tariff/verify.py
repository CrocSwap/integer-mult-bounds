"""Construct and independently check bounded stable-lane reversal routes."""

from dataclasses import dataclass
from hashlib import sha256
from itertools import permutations, product
import json
from math import prod
from pathlib import Path


MAX_RECORDS = 4096
MAX_STAGES = 12
MAX_LANES = 16


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Stage:
    before: tuple[int, ...]
    after: tuple[int, ...]
    lanes: tuple[int, ...]
    capacity: int


def validate(n: int, radices: tuple[int, ...]) -> None:
    require(type(n) is int and 1 <= n <= MAX_RECORDS, "record bound")
    require(type(radices) is tuple and len(radices) <= MAX_STAGES, "stage bound")
    require(all(type(t) is int and 1 <= t <= MAX_LANES for t in radices),
            "lane bound")
    require(n <= prod(radices), "insufficient lane product")


def route(n: int, radices: tuple[int, ...]) -> tuple[Stage, ...]:
    """Complement one mixed-radix digit per pass, retaining only n tokens."""
    validate(n, radices)
    coordinates = list(range(n))
    before = tuple(range(n))
    stages = []
    stride = 1
    for radix in radices:
        lanes = tuple((coordinates[x] // stride) % radix for x in before)
        for token in range(n):
            digit = (coordinates[token] // stride) % radix
            coordinates[token] += (radix - 1 - 2 * digit) * stride
        after = tuple(token for _, token in sorted(
            (coordinates[token], token) for token in range(n)))
        stages.append(Stage(before, after, lanes, radix))
        before = after
        stride *= radix
    require(before == tuple(reversed(range(n))), "constructor endpoint")
    return tuple(stages)


def check_stage(stage: Stage) -> None:
    """Compare actual input/output lane streams, without coordinate arithmetic."""
    n = len(stage.before)
    require(1 <= n <= MAX_RECORDS, "stage record bound")
    require(type(stage.capacity) is int and 1 <= stage.capacity <= MAX_LANES,
            "stage lane bound")
    require(sorted(stage.before) == list(range(n)), "input permutation")
    require(sorted(stage.after) == list(range(n)), "output permutation")
    require(len(stage.lanes) == n, "lane coverage")
    require(all(type(x) is int and 0 <= x < stage.capacity for x in stage.lanes),
            "lane index")
    by_token = [0] * n
    inputs = [[] for _ in range(stage.capacity)]
    outputs = [[] for _ in range(stage.capacity)]
    for token, lane in zip(stage.before, stage.lanes, strict=True):
        by_token[token] = lane
        inputs[lane].append(token)
    for token in stage.after:
        outputs[by_token[token]].append(token)
    require(inputs == outputs, "within-lane order changed")


def check_route(n: int, radices: tuple[int, ...], stages: tuple[Stage, ...]) -> None:
    validate(n, radices)
    require(len(stages) == len(radices), "missing or extra stage")
    current = tuple(range(n))
    for radix, stage in zip(radices, stages, strict=True):
        require(stage.before == current and stage.capacity == radix, "stage seam")
        check_stage(stage)
        current = stage.after
    require(current == tuple(reversed(range(n))), "route endpoint")


def decreasing_length(p: tuple[int, ...]) -> int:
    """Quadratic subsequence DP, independent of route coordinates and lanes."""
    require(len(p) <= MAX_RECORDS, "subsequence bound")
    lengths = [1] * len(p)
    for j in range(len(p)):
        for i in range(j):
            if p[i] > p[j]:
                lengths[j] = max(lengths[j], lengths[i] + 1)
    return max(lengths, default=0)


def minimum_depth(n: int, lanes: int) -> int:
    require(type(lanes) is int and 2 <= lanes <= MAX_LANES, "fixed lane bound")
    require(type(n) is int and 1 <= n <= MAX_RECORDS, "depth record bound")
    capacity = 1
    for depth in range(MAX_STAGES + 1):
        if capacity >= n:
            return depth
        capacity *= lanes
    raise ValueError("depth capacity exhausted")


def literal_distance(n: int, lanes: int) -> tuple[int, int]:
    """BFS in the entire small symmetric group using every admissible pass."""
    require(1 <= n <= 6 and 2 <= lanes <= 4, "BFS bound")
    identity = tuple(range(n))
    target = tuple(reversed(identity))
    if identity == target:
        return 0, 1
    generators = tuple(p for p in permutations(range(n))
                       if decreasing_length(p) <= lanes)
    seen = {identity}
    frontier = {identity}
    for depth in range(1, n + 1):
        following = set()
        for state in frontier:
            for generator in generators:
                endpoint = tuple(state[x] for x in generator)
                if endpoint not in seen:
                    following.add(endpoint)
        if target in following:
            return depth, len(generators)
        seen.update(following)
        frontier = following
    raise ValueError("BFS did not reach reversal")


def expect_rejected(n: int, radices: tuple[int, ...]) -> None:
    try:
        route(n, radices)
    except ValueError:
        return
    raise ValueError("invalid route accepted")


def route_census() -> dict[str, int]:
    contexts = cases = stages_checked = rejected = 0
    for length in range(5):
        for radices in product(range(1, 5), repeat=length):
            contexts += 1
            for n in range(1, prod(radices) + 1):
                stages = route(n, radices)
                check_route(n, radices, stages)
                cases += 1
                stages_checked += len(stages)
            expect_rejected(prod(radices) + 1, radices)
            rejected += 1
    for radices in ((2,) * 12, (16, 16, 16), (16,) * 12):
        stages = route(MAX_RECORDS, radices)
        check_route(MAX_RECORDS, radices, stages)
        cases += 1
        stages_checked += len(stages)
    return dict(contexts=contexts, routes=cases, stages=stages_checked,
                insufficient_capacity_rejections=rejected)


def independent_minima() -> list[dict[str, int]]:
    results = []
    for n in range(1, 7):
        for lanes in range(2, 5):
            distance, generators = literal_distance(n, lanes)
            expected = minimum_depth(n, lanes)
            require(distance == expected, "literal minimum disagrees")
            check_route(n, (lanes,) * expected, route(n, (lanes,) * expected))
            results.append(dict(n=n, lanes=lanes, minimum=distance,
                                generators=generators))
    return results


def controls() -> int:
    invalid = ((0, (2,)), (4097, (16,) * 4), (True, (2,)),
               (2, (0,)), (2, (17,)), (2, (2,) * 13))
    for n, radices in invalid:
        expect_rejected(n, radices)
    stages = route(7, (3, 3))
    first = stages[0]
    mutations = (
        stages[:-1],
        (Stage(first.before, first.after, (0,) * 7, 3), stages[1]),
        (Stage(first.before, first.after[::-1], first.lanes, 3), stages[1]),
        (first, Stage(first.before, stages[1].after, stages[1].lanes, 3)),
        (Stage(first.before, first.after, first.lanes[:-1], 3), stages[1]),
        (Stage(first.before, (0,) * 7, first.lanes, 3), stages[1]),
    )
    for mutation in mutations:
        try:
            check_route(7, (3, 3), mutation)
        except ValueError:
            continue
        raise ValueError("route mutation survived")
    return len(invalid) + len(mutations)


def main() -> None:
    report = dict(census=route_census(), minima=independent_minima(),
                  rejected_controls=controls())
    package = Path(__file__).resolve().parent
    files = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "verify.py")
    report["source_sha256"] = {
        name: sha256((package / name).read_bytes()).hexdigest() for name in files}
    print("PASS_REVERSAL_STABLE_LANE_TARIFF")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
