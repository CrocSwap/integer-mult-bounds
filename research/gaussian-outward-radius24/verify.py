"""Construct and check an exact orbit flow for the radius-24 rounding graph."""

from collections import Counter
from dataclasses import dataclass
from itertools import combinations_with_replacement, product
from math import factorial, isqrt, prod

Point = tuple[int, int, int, int]

RADIUS = 24
TOP = 78
BOTTOM = 73


def squared_norm(point: Point) -> int:
    return sum(coordinate * coordinate for coordinate in point)


def orbit_key(point: Point) -> Point:
    a, b, c, d = sorted(map(abs, point))
    return (-a if prod(point) < 0 else a, b, c, d)


def orbit_size(point: Point) -> int:
    counts = Counter(map(abs, point))
    permutations = 24 // prod(factorial(count) for count in counts.values())
    return permutations * 2 ** min(3, 4 - counts[0])


def input_orbits() -> dict[Point, int]:
    orbits = {}
    for point in combinations_with_replacement(range(RADIUS + 1), 4):
        if squared_norm(point) <= RADIUS**2:
            orbits[point] = orbit_size(point)
            if point[0] != 0:
                a, b, c, d = point
                orbits[-a, b, c, d] = orbit_size(point)
    return orbits


def rounded_neighbors(point: Point) -> list[Point]:
    a, b, c, d = point
    twice = (a + b + c + d, a - b + c - d, a + b - c - d, a - b - c + d)
    low = tuple(entry // 2 for entry in twice)
    if twice[0] % 2:
        return list(product(*[(entry, entry + 1) for entry in low]))
    neighbors = [low]
    for axis in range(4):
        for step in (-1, 1):
            shifted = list(low)
            shifted[axis] += step
            neighbors.append(tuple(shifted))
    return neighbors


def allowed_gap(output_norm: int, input_norm: int) -> bool:
    """Compare sqrt(output_norm) - sqrt(input_norm) with sqrt(78) - sqrt(73)."""
    delta = output_norm - input_norm
    if delta <= 0:
        return True
    total = TOP + BOTTOM
    radicand = TOP * BOTTOM
    linear = 2 * delta + 4 * input_norm
    # Substitute t = total - 2*sqrt(radicand) into t*t - linear*t + delta*delta.
    p = total**2 + 4 * radicand - linear * total + delta**2
    q = 2 * linear - 4 * total
    if q > 0:
        return p < 0 and p**2 >= q**2 * radicand
    if q < 0:
        return p <= 0 or p**2 <= q**2 * radicand
    return p <= 0


@dataclass
class Edge:
    target: int
    back: int
    room: int


def connect(graph: list[list[Edge]], start: int, end: int, capacity: int) -> Edge:
    forward = Edge(end, len(graph[end]), capacity)
    reverse = Edge(start, len(graph[start]), 0)
    graph[start].append(forward)
    graph[end].append(reverse)
    return reverse


def levels_from(graph: list[list[Edge]], source: int) -> list[int]:
    levels = [-1] * len(graph)
    levels[source] = 0
    queue = [source]
    cursor = 0
    for _ in range(len(graph)):
        if cursor == len(queue):
            break
        vertex = queue[cursor]
        cursor += 1
        for edge in graph[vertex]:
            if edge.room > 0 and levels[edge.target] == -1:
                levels[edge.target] = levels[vertex] + 1
                queue.append(edge.target)
    return levels


def augment(
    graph: list[list[Edge]],
    levels: list[int],
    next_edge: list[int],
    source: int,
    sink: int,
    arc_count: int,
) -> int:
    """Send flow along one admissible path, or mark the level graph blocked."""
    vertex = source
    path = []
    for _ in range(2 * arc_count + 1):
        if vertex == sink:
            amount = min(graph[node][offset].room for node, offset in path)
            for node, offset in path:
                edge = graph[node][offset]
                edge.room -= amount
                graph[edge.target][edge.back].room += amount
            return amount
        for offset in range(next_edge[vertex], len(graph[vertex])):
            edge = graph[vertex][offset]
            if edge.room > 0 and levels[edge.target] == levels[vertex] + 1:
                next_edge[vertex] = offset
                path.append((vertex, offset))
                vertex = edge.target
                break
        else:
            levels[vertex] = -1
            if not path:
                return 0
            vertex, offset = path.pop()
            next_edge[vertex] = offset + 1
    raise RuntimeError("level path exceeded its arc bound")


def send_flow(graph: list[list[Edge]], source: int, sink: int, demand: int) -> int:
    arc_count = sum(map(len, graph))
    sent = 0
    for _ in range(len(graph) - 1):
        levels = levels_from(graph, source)
        if levels[sink] < 0:
            return sent
        next_edge = [0] * len(graph)
        for _ in range(arc_count):
            added = augment(graph, levels, next_edge, source, sink, arc_count)
            if added == 0:
                break
            sent += added
            if sent == demand:
                return sent
        else:
            raise RuntimeError("blocking flow exceeded its arc bound")
    raise RuntimeError("flow exceeded its distance bound")


def make_witness(inputs: dict[Point, int]) -> tuple[list[tuple[Point, Point, int]], int]:
    outputs = {}
    pairs = []
    left_count = len(inputs)
    for row, (point, capacity) in enumerate(inputs.items()):
        input_norm = squared_norm(point)
        for target in sorted({orbit_key(output) for output in rounded_neighbors(point)}):
            if allowed_gap(squared_norm(target), input_norm):
                column = outputs.setdefault(target, left_count + len(outputs))
                pairs.append((row, column, point, target, capacity))
    source = left_count + len(outputs)
    sink = source + 1
    graph = [[] for _ in range(sink + 1)]
    arcs = [
        (point, target, connect(graph, row, column, capacity))
        for row, column, point, target, capacity in pairs
    ]
    for row, capacity in enumerate(inputs.values()):
        connect(graph, source, row, capacity)
    for target, column in outputs.items():
        connect(graph, column, sink, orbit_size(target))
    demand = sum(inputs.values())
    sent = send_flow(graph, source, sink, demand)
    if sent != demand:
        raise ValueError(f"flow sends {sent} of {demand} required units")
    return [(point, target, back.room) for point, target, back in arcs if back.room], len(outputs)


def check_witness(inputs: dict[Point, int], witness: list[tuple[Point, Point, int]]) -> None:
    used_left = Counter()
    used_right = Counter()
    for point, target, amount in witness:
        if point not in inputs or not 0 < amount <= inputs[point]:
            raise ValueError("invalid input orbit or amount")
        if target not in {orbit_key(output) for output in rounded_neighbors(point)}:
            raise ValueError("flow uses a forbidden rounding edge")
        if not allowed_gap(squared_norm(target), squared_norm(point)):
            raise ValueError("flow exceeds the outward gap")
        used_left[point] += amount
        used_right[target] += amount
    if used_left != inputs:
        raise ValueError("flow leaves an input orbit unsaturated")
    if any(used > orbit_size(target) for target, used in used_right.items()):
        raise ValueError("flow exceeds an output capacity")


def check_controls() -> None:
    if not allowed_gap(78, 73) or allowed_gap(79, 73):
        raise ValueError("exact threshold boundary failed")
    if not allowed_gap(73, 78) or allowed_gap(2, 1):
        raise ValueError("gap sign control failed")
    point = (0, 0, 0, 0)
    check_witness({point: 1}, [(point, point, 1)])
    unit = (0, 0, 0, 1)
    bad_witnesses = (
        ({point: 1}, []),
        ({point: 1}, [(point, (0, 0, 0, 2), 1)]),
        ({point: 1}, [(point, point, 2)]),
        ({point: 1, unit: 1}, [(point, point, 1), (unit, point, 1)]),
    )
    for inputs, bad in bad_witnesses:
        try:
            check_witness(inputs, bad)
        except ValueError:
            continue
        raise ValueError("witness checker accepted an invalid flow")
    # A direct greedy pass strands vertex 1. A residual path reroutes vertex 0.
    graph = [[] for _ in range(6)]
    for start, end in [(4, 0), (4, 1), (0, 2), (0, 3), (1, 2), (2, 5), (3, 5)]:
        connect(graph, start, end, 1)
    if send_flow(graph, 4, 5, 2) != 2:
        raise ValueError("flow failed on the rerouting control")


def main() -> None:
    check_controls()
    inputs = input_orbits()
    witness, output_count = make_witness(inputs)
    check_witness(inputs, witness)
    total = sum(inputs.values())
    # Count integral points independently by slicing in the fourth coordinate.
    interval = range(-RADIUS, RADIUS + 1)
    ball_count = 0
    for a, b, c in product(interval, repeat=3):
        remainder = RADIUS**2 - a * a - b * b - c * c
        if remainder >= 0:
            ball_count += 2 * isqrt(remainder) + 1
    if total != ball_count or total != 1_638_241:
        raise ValueError("input orbit cover disagrees with the ball count")
    print(f"PASS_GAUSSIAN_OUTWARD_RADIUS24 inputs={total} left_orbits={len(inputs)} "
          f"right_orbits={output_count} positive_flows={len(witness)} gap=sqrt(78)-sqrt(73)")


if __name__ == "__main__":
    main()
