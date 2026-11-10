#!/usr/bin/env python3
"""Source-bound obstruction for independent four-contact cycles. Apache-2.0."""

from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json
import random
import tempfile

from geometry import (brute, cycle_minimum, cycle_reference, invoice, label_distance, need)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
EXPECTED = (2, 2, 2, 2, 2, 2, 2, 0, 0)
SHARP_VERTICES = (10875, 10876, 10898, 10899)
SHARP_LABELS = (59, 59, 59, 59)
SHARP_DELTA = (-2, 2, 0, 0, 0, 0, 0, 2, -2, 0)
SHARP_EDGES = (
    (6733, 10875, 0, 1),
    (6737, 10876, 0, 1),
    (10874, 10875, 8, 7),
    (10876, 10877, 0, 1),
    (10897, 10898, 8, 7),
    (10898, 11060, 1, 0),
    (10899, 10900, 0, 1),
    (10899, 11061, 1, 0),
)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "module loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate(root):
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            actual = sha256((root / row["path"]).read_bytes()).hexdigest()
            need(actual == row["sha256"], "source bytes: " + row["path"])


def source_controls(directory):
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    inputs = [row["path"] for row in sources["files"] if row["usage"] == "input"]
    need(len(inputs) == 5, "complete source-control domain")
    root = directory / "source-controls"
    for name in inputs:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / name).read_bytes())
    authenticate(root)
    rejected = 0
    for name in inputs:
        target = root / name
        original = target.read_bytes()
        need(bool(original), "nonempty source input")
        target.write_bytes(original[:-1] + bytes((original[-1] ^ 1,)))
        try:
            authenticate(root)
        except ValueError:
            rejected += 1
        target.write_bytes(original)
    need(rejected == len(inputs), "each altered source rejects")
    return rejected


def load_graph(directory):
    builder = load_module(
        "retained_centre_builder",
        ROOT / "research/sol1337-contact-frontier/build_graph.py",
    )
    metadata = builder.build(directory)
    lines = (directory / "center-contact-graph.txt").read_text(encoding="utf-8").splitlines()
    nodes_n, frames, _maps, edges_n = map(int, lines[0].split())
    need((nodes_n, frames, edges_n) == (19197, 4429, 34830), "exact graph dimensions")
    need(len(lines) == 1 + nodes_n + frames + 145 + edges_n, "complete graph payload")
    nodes = tuple(tuple(map(int, line.split())) for line in lines[1:1 + nodes_n])
    lags = tuple(tuple(map(int, line.split())) for line in lines[1 + nodes_n:1 + nodes_n + frames])
    edges = tuple(tuple(map(int, line.split())) for line in lines[1 + nodes_n + frames + 145:])
    validate_graph(nodes, lags, edges)
    need(metadata["inputs"] == 640 and metadata["independent_center_reward"] == 0,
         "retained arbitrary inputs and no independent centre credit")
    need(metadata["helpers"] == {4: 28, 7: 7, 8: 47, 9: 326}, "unchanged helper credits")
    return nodes, lags, edges


def validate_graph(nodes, lags, edges):
    need(len(nodes) == 19197 and len(lags) == 4429 and len(edges) == 34830, "bounded original graph")
    need(all(len(row) == 2 and 0 <= row[0] < len(lags) and row[1] in (0, 1) for row in nodes),
         "node domain")
    need(all(len(row) == 9 and all(0 <= value < 1 << 18 for value in row) for row in lags),
         "nine-dimensional frame bases")
    need(lags[0] == tuple(1 << (9 + i) for i in range(9)), "literal empty chart")
    for row in edges:
        need(len(row) == 5, "edge shape")
        left, right, rank, sign, map_id = row
        need(0 <= left < len(nodes) and 0 <= right < len(nodes), "edge endpoints")
        need(0 <= rank <= 9 and sign == 1 and 0 <= map_id < 145, "paid edge domain")
        if nodes[left][1] == 0 or nodes[right][1] == 0:
            need(map_id == 0 and left != right, "identity-map contact edge")
    paid = Counter(rank for _left, _right, rank, _sign, _map in edges if rank)
    need(paid == {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8}, "baseline bill")


def cycle_order(adjacency, vertices):
    members = set(vertices)
    start = min(vertices)
    neighbours = sorted(vertex for vertex in adjacency[start] if vertex in members)
    need(len(neighbours) == 2, "induced cycle degree")
    order = [start, neighbours[0]]
    previous = start
    while len(order) < 4:
        current = order[-1]
        nxt = [vertex for vertex in adjacency[current] if vertex in members and vertex != previous]
        need(len(nxt) == 1, "unique cycle continuation")
        order.append(nxt[0])
        previous = current
    first, second, third, fourth = order
    need(second in adjacency[first] and third in adjacency[second]
         and fourth in adjacency[third] and first in adjacency[fourth], "cycle edges")
    need(third not in adjacency[first] and fourth not in adjacency[second], "no cycle chords")
    return tuple(order)


def prepare(nodes, lags, edges, quad):
    selected = {i for i, (_frame, fixed) in enumerate(nodes) if fixed == 0}
    empty = {i for i in selected if nodes[i][0] == 0}
    need(len(selected) == 184 and len(empty) == 176, "contact domains")
    incident = {i: [] for i in empty}
    internal = []
    for left, right, rank, _sign, _map in edges:
        if left in empty:
            incident[left].append((right, rank))
        if right in empty:
            incident[right].append((left, rank))
        if left in empty and right in empty:
            need(rank == 0, "old internal rank zero")
            if left < right:
                internal.append((left, right))
    need(len(internal) == 256 and all(len(rows) == 4 for rows in incident.values()),
         "complete empty-chart incident edges")
    adjacency = quad.adjacency_from_edges(empty, internal)
    degrees = Counter(len(adjacency[vertex]) for vertex in empty)
    need(dict(degrees) == {2: 16, 3: 160}, "internal degrees are only 2 and 3")
    by_side = quad.induced_cycles(adjacency, internal)
    by_opposite = quad.cycles_from_opposites(adjacency)
    need(by_side == by_opposite, "the two induced-cycle enumerations agree")
    shapes = quad.connected_shape_counts(adjacency)
    need(shapes == {(3, (1, 1, 2, 2)): 716, (3, (1, 1, 1, 3)): 160, (4, (2, 2, 2, 2)): 62},
         "every connected four-contact block is a path, claw or 4-cycle")
    need(len(by_side) == 62, "sixty-two induced cycles")
    orders = tuple(cycle_order(adjacency, vertices) for vertices in sorted(by_side))
    need(len({tuple(sorted(order)) for order in orders}) == 62, "one walk per cycle")
    images = quad.neighbours(9)
    frame_ids = {nodes[other][0] for rows in incident.values() for other, _rank in rows}
    need(len(frame_ids) == 31, "external frame cache domain")
    ranks = {frame: tuple(quad.binary_rank(image + lags[frame], 9) - 9 for image in images)
             for frame in sorted(frame_ids)}
    unary = {}
    for node in sorted(empty):
        unary[node] = tuple(
            tuple(sum(min(ranks[nodes[other][0]][label], prefix) - min(rank, prefix)
                      for other, rank in incident[node])
                  for label in range(1022))
            for prefix in range(1, 10))
    index = {}
    for position, row in enumerate(edges):
        index.setdefault(row[0], []).append(position)
        index.setdefault(row[1], []).append(position)
    return orders, unary, images, index


def direct_delta(block, labels, nodes, lags, edges, images, index):
    changed = {vertex: images[label] for vertex, label in zip(block, labels, strict=True)}
    seen = set()
    delta = [0] * 10
    for vertex in block:
        for position in index[vertex]:
            if position in seen:
                continue
            seen.add(position)
            left, right, old, _sign, map_id = edges[position]
            need(map_id == 0, "literal joint uses identity-map edges")
            left_frame = changed[left] if left in changed else lags[nodes[left][0]]
            right_frame = changed[right] if right in changed else lags[nodes[right][0]]
            new = load_rank(left_frame, right_frame)
            delta[new] += 1
            delta[old] -= 1
    return tuple(delta)


def load_rank(left, right):
    return RANKER(left + right, 9) - 9


def full_delta(block, labels, nodes, lags, edges, images):
    changed = {vertex: images[label] for vertex, label in zip(block, labels, strict=True)}
    delta = [0] * 10
    for left, right, old, _sign, map_id in edges:
        if left in changed or right in changed:
            need(map_id == 0, "full scan uses identity-map edges")
            left_frame = changed[left] if left in changed else lags[nodes[left][0]]
            right_frame = changed[right] if right in changed else lags[nodes[right][0]]
            new = load_rank(left_frame, right_frame)
            delta[new] += 1
            delta[old] -= 1
    return tuple(delta)


def changed_rank_edges(block, labels, nodes, lags, edges, images, index):
    changed = {vertex: images[label] for vertex, label in zip(block, labels, strict=True)}
    seen = set()
    rows = []
    for vertex in block:
        for position in index[vertex]:
            if position in seen:
                continue
            seen.add(position)
            left, right, old, _sign, _map = edges[position]
            left_frame = changed[left] if left in changed else lags[nodes[left][0]]
            right_frame = changed[right] if right in changed else lags[nodes[right][0]]
            new = load_rank(left_frame, right_frame)
            if new != old:
                rows.append((left, right, old, new))
    return tuple(sorted(rows))


def prefix_values(delta):
    return tuple(sum(delta[rank] * min(rank, prefix) for rank in range(10)) for prefix in range(1, 10))


def label_axis(quad, label, width=9):
    normal = label // 2 + 1
    tag = label % 2
    pivot = (normal & -normal).bit_length() - 1
    axis = normal | (tag << (width + pivot))
    origin = tuple(1 << (width + j) for j in range(width))
    image = tuple(value ^ axis if (value >> width & normal).bit_count() % 2 else value for value in origin)
    need(quad.neighbours(width)[label] == image, "transvection image")
    return normal, tag, axis


def prove_cycles(orders, unary, nodes, lags, edges, images, index):
    minima = [10 ** 9] * 9
    checked = 0
    sharp_orders = []
    for order in orders:
        values = []
        for prefix in range(1, 10):
            costs = tuple(unary[vertex][prefix - 1] for vertex in order)
            value, labels = cycle_minimum(costs, prefix)
            need(value >= EXPECTED[prefix - 1], "induced-cycle prefix floor")
            delta = direct_delta(order, labels, nodes, lags, edges, images, index)
            need(prefix_values(delta)[prefix - 1] == value, "reduction matches the literal invoice")
            values.append(value)
            checked += 1
            if value < minima[prefix - 1]:
                minima[prefix - 1] = value
        if tuple(values) == EXPECTED:
            sharp_orders.append(order)
    need(tuple(minima) == EXPECTED, "attained componentwise cycle minima")
    need(len(sharp_orders) == 1, "one cycle meets every prefix at once")
    sharp = sharp_orders[0]
    need(tuple(sorted(sharp)) == SHARP_VERTICES, "sharp cycle vertices")
    named = direct_delta(sharp, SHARP_LABELS, nodes, lags, edges, images, index)
    need(named == SHARP_DELTA, "named cycle histogram")
    need(prefix_values(named) == EXPECTED, "named labels attain every prefix")
    need(full_delta(sharp, SHARP_LABELS, nodes, lags, edges, images) == named,
         "incident index agrees with the full edge scan")
    need(changed_rank_edges(sharp, SHARP_LABELS, nodes, lags, edges, images, index) == SHARP_EDGES,
         "named changed-rank edges")
    members = set(sharp)
    need(all(left not in members or right not in members for left, right, _old, _new in SHARP_EDGES),
         "internal cycle edges keep rank zero")
    for prefix in range(1, 10):
        costs = tuple(unary[vertex][prefix - 1] for vertex in sharp)
        value, _labels = cycle_minimum(costs, prefix)
        reference, _reference_labels = cycle_reference(costs, prefix)
        need(value == reference == invoice(costs, SHARP_LABELS, prefix) == EXPECTED[prefix - 1],
             "sharp cycle agrees across elimination, transform and histogram")
    mutated = list(unary[10875][0])
    mutated[59] -= 1
    costs = []
    for vertex in sharp:
        if vertex == 10875:
            costs.append(tuple(mutated))
        else:
            costs.append(unary[vertex][0])
    dropped, _labels = cycle_minimum(tuple(costs), 1)
    need(dropped <= 1, "removing one unit from the sharp unary drops the floor")
    return {"prefix_minima": minima, "sharp_cycle": sharp, "sharp_labels": SHARP_LABELS,
            "sharp_delta": named, "literal_prefix_checks": checked}


def controls(quad):
    geometry_cases = 0
    for width in range(1, 6):
        images = quad.neighbours(width)
        for left_index, left in enumerate(images):
            for right_index, right in enumerate(images):
                need(quad.binary_rank(left + right, width) - width == label_distance(left_index, right_index),
                     "literal paired-neighbour geometry")
                geometry_cases += 1
    need(label_axis(quad, 59) == (30, 1, 1054), "label 59 is normal 30, tag 1, axis 1054")
    generator = random.Random(20261102)
    product_cases = 0
    reference_cases = 0
    for width in (2, 4, 6, 8):
        for _seed in range(4):
            costs = [tuple(generator.randrange(-5, 6) for _label in range(width)) for _vertex in range(4)]
            for prefix in (1, 2, 9):
                value, labels = cycle_minimum(costs, prefix)
                exhaustive, _exhaustive_labels = brute(costs, prefix)
                need(value == exhaustive == invoice(costs, labels, prefix),
                     "cycle partition attains the full product")
                product_cases += 1
                if width >= 4 and prefix in (1, 9):
                    reference, _reference_labels = cycle_reference(costs, prefix)
                    need(reference == value, "fixed-label transform agrees on the small product")
                    reference_cases += 1
    diagonal = [[40] * 8 for _vertex in range(4)]
    diagonal[0][0] = diagonal[0][1] = 0
    diagonal[2][0] = diagonal[2][1] = 0
    diagonal[1][2] = diagonal[1][3] = 0
    diagonal[3][4] = diagonal[3][5] = 0
    diagonal = [tuple(row) for row in diagonal]
    for prefix in (1, 2, 9):
        value, _labels = cycle_minimum(diagonal, prefix)
        exhaustive, _exhaustive_labels = brute(diagonal, prefix)
        need(value == exhaustive, "single-diagonal pattern")
        product_cases += 1
    distinct = [[80] * 10 for _vertex in range(4)]
    for pair, vertex in ((0, 1), (1, 2), (2, 3)):
        distinct[vertex][2 * pair] = 0
        distinct[vertex][2 * pair + 1] = 4
    distinct[0][6] = 0
    distinct[0][7] = 3
    for pair in range(5):
        if pair == 3:
            continue
        if distinct[0][2 * pair] == 80:
            distinct[0][2 * pair] = 9
            distinct[0][2 * pair + 1] = 9
    distinct = [tuple(row) for row in distinct]
    value, labels = cycle_minimum(distinct, 2)
    exhaustive, _exhaustive_labels = brute(distinct, 2)
    need(value == exhaustive and len({label // 2 for label in labels}) == 4,
         "four distinct pairs remain available")
    product_cases += 1
    rejected = 0
    for bad_costs, prefix in (
        ([(0, 0), (0, 0), (0, 0)], 1),
        ([(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)], 1),
        ([(0, 0), (0, 0), (0, 0), (0, 0)], 0),
        ([(0, 0), (0, 0), (0, 0), (0, 0)], 10),
        ([(0, 0), (0, 0), (0, 0), (0, 0.5)], 1),
    ):
        try:
            cycle_minimum(bad_costs, prefix)
        except ValueError:
            rejected += 1
    need(rejected == 5, "invalid cycle inputs reject")
    return {"geometry_cases": geometry_cases, "full_product_oracles": product_cases,
            "reference_oracles": reference_cases, "invalid_input_controls": rejected}


def graph_controls(nodes, lags, edges):
    index = next(i for i, (left, right, _rank, _sign, _map) in enumerate(edges)
                 if nodes[left][1] == 0 or nodes[right][1] == 0)
    rejected = 0
    for field, value in ((3, -1), (4, 1), (2, 10)):
        bad = list(edges)
        row = list(bad[index])
        row[field] = value
        bad[index] = tuple(row)
        try:
            validate_graph(nodes, lags, bad)
        except ValueError:
            rejected += 1
    need(rejected == 3, "negative charge, changed map and invalid rank reject")
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output is not None:
        need(not args.output.resolve().is_relative_to(ROOT), "receipt must stay outside checkout")
    authenticate(ROOT)
    quad = load_module("quad_tree_geometry", ROOT / "research/independent-centre-quad-trees/geometry.py")
    global RANKER
    RANKER = quad.binary_rank
    checked = controls(quad)
    with tempfile.TemporaryDirectory(prefix="independent-centre-four-cycles-") as raw:
        nodes, lags, edges = load_graph(Path(raw))
        orders, unary, images, index = prepare(nodes, lags, edges, quad)
        result = prove_cycles(orders, unary, nodes, lags, edges, images, index)
        checked["graph_rejection_controls"] = graph_controls(nodes, lags, edges)
        checked["source_rejection_controls"] = source_controls(Path(raw))
    result.update(status="PASS_INDEPENDENT_CENTRE_FOUR_CYCLES", cycles=len(orders), labels=1022,
                  controls=checked, claim_type="scoped proof with exact finite certificate",
                  moment_lower_bound="2*(1+7^theta-8^theta)", theta_domain="0<theta<1",
                  sharp_vertices=SHARP_VERTICES)
    result["package_sha256"] = {path.name: sha256(path.read_bytes()).hexdigest()
                                 for path in sorted(HERE.iterdir()) if path.is_file()}
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")


if __name__ == "__main__":
    main()
