"""Review the paired line-gauge paths by symplectic pairing ranks."""

from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import resource
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
PINS = {
    ARCHIVE: "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754",
    "slots/local/CANONICAL-WORD.json.gz": "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    "slots/local/LOCAL-PROGRAMS.json.gz": "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
}


def require(condition, label):
    if not condition:
        raise ValueError(label)


def binary_basis(vectors):
    out = []
    for value in vectors:
        for pivot in out:
            value = min(value, value ^ pivot)
        if value:
            out.append(value)
            out.sort(reverse=True)
    return out


def omega(left, right):
    return (((left & 511) & (right >> 9)).bit_count()
            + ((left >> 9) & (right & 511)).bit_count()) % 2


def load_source():
    output = []
    for name in list(PINS)[1:]:
        compressed = (PACKAGE / "data" / Path(name).name).read_bytes()
        require(sha256(compressed).hexdigest() == PINS[name], "Source member pin")
        output.append(json.loads(gzip.decompress(compressed)))
    return output


def components(word, program):
    frame = {("L", i, 0): value for i, value in enumerate(word["start"])}
    current = {("L", i): ("L", i, 0) for i in range(len(word["start"]))}
    sequence, clears = Counter(), Counter()
    parent = {node: node for node in frame}
    native = []

    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def join(left, right):
        a, b = find(left), find(right)
        parent[max(a, b)] = min(a, b)

    previous_scalar = None
    for index, event in enumerate(program):
        kind = event[0]
        if kind == "phase":
            continue
        if kind == "scalar":
            gate, wanted_frame = event[1:]
            key = tuple(gate[1])
            if gate[0] == "clear":
                require(key[0] == "C", "Persistent clear")
                clears[key] += 1
                require(clears[key] <= 2, "Private lifetime count")
                level = "dead" if clears[key] == 2 else ("high" if wanted_frame else "low")
                current[key] = ("C", key[1], level)
                frame[current[key]] = wanted_frame
                parent[current[key]] = current[key]
            else:
                require(frame[current[key]] == wanted_frame, "Scalar target frame")
                if gate[0] in ("add", "copy"):
                    source = current[tuple(gate[2])]
                    require(frame[source] == wanted_frame, "Scalar source frame")
                    if gate[0] == "copy":
                        require(previous_scalar == ["scalar", ["clear", list(key)], wanted_frame], "Copy lifetime")
                    join(current[key], source)
                else:
                    require(gate[0] == "scale", "Scalar opcode")
            previous_scalar = event
            continue
        if kind == "center":
            _, register, before, after, rank = event
            key = ("C", register)
            next_node = ("C", register, "high" if after else "low")
        else:
            require(kind in ("climb", "adapter", "residual_adapter"), "Native opcode")
            key = ("L", event[2])
            if kind == "climb":
                before, after, rank = event[3:]
            else:
                before = after = frame[current[key]]
                rank = 0
            sequence[key] += 1
            next_node = ("L", key[1], sequence[key])
        old = current[key]
        require(frame[old] == before and next_node not in frame, "Native frame or segment")
        frame[next_node] = after
        parent[next_node] = next_node
        current[key] = next_node
        native.append((old, next_node, before, after, rank, kind, index))
    require(len(clears) == 8 and set(clears.values()) == {2}, "Private clears")
    ends = [current["L", i] for i in range(len(word["start"]))]
    require([frame[node] for node in ends] == word["final"], "Source final frames")
    for i in range(2 * word["v"], len(ends)):
        join(("L", i, 0), ends[i])
    for i in range(word["v"]):
        for node in (("L", word["v"] + i, 0), ends[i], ends[word["v"] + i]):
            join(("L", i, 0), node)
    groups = {}
    for node in parent:
        groups.setdefault(find(node), set()).add(node)
    return native, {node: find(node) for node in parent}, {frozenset(group) for group in groups.values()}


def main(args):
    source_dir = PACKAGE / "certificates"
    cert_paths = [source_dir / name for name in ("WIRE-GAUGE-ODD-PATHS.json.gz", "WIRE-GAUGE-LINE42-PATHS.json.gz")]
    certs = [json.loads(gzip.decompress(path.read_bytes())) for path in cert_paths]
    word, programs = load_source()
    forward, roots, groups = components(word, programs["forward"])
    backward, backward_roots, backward_groups = components(word, programs["backward"])
    require(groups == backward_groups, "Both scalar and boundary partitions")
    def edges_up_to_orientation(edges):
        return Counter((tuple(sorted((u, v))), tuple(sorted((before, after))), rank, kind)
                       for u, v, before, after, rank, kind, index in edges)
    require(edges_up_to_orientation(forward) == edges_up_to_orientation(backward), "Both native inventories")
    graph = certs[0]["graph"]
    require(graph == certs[1]["graph"], "Both saved graphs")
    require(graph["paired_boundaries"] is True and graph["fixed"] == [], "Boundary constraints")
    require(len(groups) == len(graph["labels"]) == 1979 and len(roots) == graph["raw_segments"] == 5784, "Graph dimensions")
    require(len(forward) == len(graph["edges"]) == 5064, "Native event count")
    require(len(roots) - len(groups) == graph["scalar_access_unions"] == 3805, "Component identifications")
    mapping, inverse = {}, {}
    for actual, saved in zip(forward, graph["edges"]):
        require(list(actual[2:]) == saved[2:], "Source native event")
        for node, saved_node in zip(actual[:2], saved[:2]):
            root = roots[node]
            require(mapping.get(root, saved_node) == saved_node and inverse.get(saved_node, root) == root, "Saved graph partition")
            mapping[root] = saved_node
            inverse[saved_node] = root
    require(len(groups) - len(mapping) == 8, "Only cleared private segments are isolated")
    profile = Counter(edge[4] for edge in forward)
    require(profile == {0: 1570, 1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}, "Complete source profile")
    require(sum(rank * count for rank, count in profile.items()) == 5586, "Source rank mass")

    labels = []
    for frame in word["frames"]:
        perpendicular = binary_basis(value for value in range(1, 512)
                                     if all(not ((value & u).bit_count() % 2) for u in frame))
        basis = [u | (u << 9) for u in frame] + [v << 9 for v in perpendicular]
        require(len(basis) == len(binary_basis(basis)) == 9, "Lagrangian dimension")
        require(all(not omega(u, v) for u in basis for v in basis), "Lagrangian isotropy")
        labels.append(basis)
    pairings = {}
    for before, after, rank in {(e[2], e[3], e[4]) for e in forward}:
        matrix = [sum(omega(u, v) << j for j, v in enumerate(labels[after])) for u in labels[before]]
        require(len(binary_basis(matrix)) == rank, "Baseline symplectic pairing rank")
        pairings[before, after, rank] = matrix
    require(len(pairings) == 3150, "Distinct native frame pairs")
    rows = {row["line"]: row for cert in certs for row in cert["lines"] if "paths" in row}
    require(set(rows) == {a for a in range(1, 512) if a.bit_count() % 2}, "Odd-line coverage")
    total_paths = total_demand = 0
    capacity_cycle = None
    for a in range(1, 512):
        z_pairings = [sum(((value >> 9) & a).bit_count() % 2 << j for j, value in enumerate(basis))
                      for basis in labels]
        delta = {}
        for key, matrix in pairings.items():
            before, after, old = key
            changed = [row ^ (z_pairings[after] if (z_pairings[before] >> i) & 1 else 0)
                       for i, row in enumerate(matrix)]
            delta[key] = len(binary_basis(changed)) - old
        if not a.bit_count() % 2:
            require(min(delta.values()) >= 0, "Even-line pointwise obstruction")
            continue
        signed = Counter()
        for u, v, before, after, rank, kind, index in graph["edges"]:
            if u != v:
                signed[tuple(sorted((u, v)))] += delta[before, after, rank]
        positive = {edge: weight for edge, weight in signed.items() if weight > 0}
        negative = {edge: -weight for edge, weight in signed.items() if weight < 0}
        row, used, supplied = rows[a], Counter(), Counter()
        require(row["negative_edges"] == len(negative) and row["negative_mass"] == sum(negative.values()), "Negative inventory")
        for route in row["paths"]:
            demand, path, amount = tuple(route["negative_edge"]), route["path"], route["amount"]
            require(demand in negative and type(amount) is int and amount > 0, "Integer demand")
            require(len(path) > 1 and (path[0], path[-1]) == demand, "Path endpoints")
            supplied[demand] += amount
            for u, v in zip(path, path[1:]):
                edge = tuple(sorted((u, v)))
                require(edge in positive, "Positive path edge")
                used[edge] += amount
        require(dict(supplied) == negative, "Exact demand coverage")
        require(all(used[edge] <= positive[edge] for edge in used), "Path capacities")
        total_paths += len(row["paths"])
        total_demand += sum(negative.values())
        if a == 7:
            for route_index, route in enumerate(row["paths"]):
                for position, edge in enumerate(zip(route["path"], route["path"][1:])):
                    if used[tuple(sorted(edge))] == positive[tuple(sorted(edge))]:
                        capacity_cycle = route_index, position
                        break
                if capacity_cycle is not None:
                    break
    require(capacity_cycle is not None, "Saturated edge for capacity control")
    print("independent_pairing_ranks=1609650 odd_lines=256 even_lines=255", flush=True)

    controls = []
    def reject(name, mutate, expected):
        changed = deepcopy(certs[0])
        mutate(changed)
        with tempfile.TemporaryDirectory(prefix="line-path-control-") as temporary:
            path = Path(temporary) / "certificate.json.gz"
            path.write_bytes(gzip.compress(json.dumps(changed).encode(), mtime=0))
            command = [sys.executable, "-I", "-O", "-B", str(HERE / "verify_odd_paths.py"), "--out", str(Path(temporary) / "unexpected.json"), str(path), str(cert_paths[1])]
            run = subprocess.run(command, capture_output=True, text=True, timeout=60)
            require(run.returncode != 0 and expected in run.stderr, "Mutation control: " + name)
            controls.append({"control": name, "exit_code": run.returncode, "rejected_by": expected})
            print("rejected", name, flush=True)

    def first(doc):
        return next(row for row in doc["lines"] if row["line"] == 7)

    def insert_cycle(doc):
        route_index, position = capacity_cycle
        route = first(doc)["paths"][route_index]
        path = route["path"]
        u, v = path[position:position + 2]
        route["path"] = path[:position + 1] + [v, u] + path[position + 1:]

    reject("missing_path", lambda doc: first(doc)["paths"].pop(), "all negative demands covered exactly")
    reject("overused_positive_capacity", insert_cycle, "positive capacities")
    reject("negative_edge_used_as_path", lambda doc: first(doc)["paths"][0].update(path=first(doc)["paths"][0]["negative_edge"]), "path uses a positive source edge")
    reject("noninteger_amount", lambda doc: first(doc)["paths"][0].update(amount=0.5), "positive integer path amount")
    reject("unpaired_boundary", lambda doc: doc["graph"].update(paired_boundaries=False), "Boundary mode")
    reject("native_wrapper_omission", lambda doc: doc["graph"]["edges"].pop(next(i for i, edge in enumerate(doc["graph"]["edges"]) if edge[5] == "adapter")), "Native edge count")
    reject("missing_line", lambda doc: doc["lines"].remove(first(doc)), "all 256 odd lines exactly once")

    paths = cert_paths + [HERE / "verify_odd_paths.py", PACKAGE / "proofs/ALL-LINE-GAUGES.md",
                          HERE / "review_wire_gauge.py", HERE / "check_line_paths.py"]
    receipt = {
        "status": "ACCEPTED_INDEPENDENT_ALL_FIXED_LINE_RANK_MASS_OBSTRUCTION",
        "source_base": BASE,
        "source_pins": PINS,
        "orientations": ["forward", "backward"],
        "graph_components": 1979,
        "native_events": 5064,
        "rank_zero_wrappers": 1570,
        "native_rank_mass": 5586,
        "distinct_native_frame_pairs": 3150,
        "odd_lines": 256,
        "even_lines": 255,
        "independent_symplectic_pairing_rank_checks": 1609650,
        "integer_paths": total_paths,
        "negative_demand_mass": total_demand,
        "negative_controls_under_optimized_python": controls,
        "independent_method": "The review rebuilds live wire partitions with register and lifetime labels. It computes rank from the 9 by 9 symplectic pairing matrix, not the producer's 18-dimensional span calculation or its rank-price formula.",
        "arbitrary_cut_proof": "For each routed demand d from u to v, d times the endpoint cut indicator is at most the sum of d times the indicators on its path. Summing all paths and using the positive capacities bounds every negative cut term. The signed cut energy is therefore nonnegative. A constant gauge attains zero.",
        "binary_rank_proof": "The symplectic pairing has rank 9 minus the Lagrangian intersection dimension. Twisting either endpoint adds the same outer product. Twisting both endpoints leaves the pairing unchanged. Thus the price depends only on the XOR of the two gauge bits.",
        "boundary_scope": "The graph keeps the original scalar program and requires one gauge at each ADD or COPY. Each old data pair has a common gauge on its four boundary points. Each helper has one gauge at its input and output. A CLEAR starts a new private lifetime. These constraints preserve the exact endpoint on arbitrary inputs.",
        "backward_scope": "The two source programs give the same component partition and undirected native inventory. In backward frames D_U=T_U F^-1, the line gauges commute with F. The relative ranks therefore agree in both orientations.",
        "not_claimed": ["Different gauge lines at different components", "All Clifford palettes", "All child costs or moments", "An unchanged rank profile for every zero-rank cut", "A changed scalar program or controller", "A fully emitted changed supplier or a kappa bound"],
        "source_sha256": {str(path.relative_to(PACKAGE)): sha256(path.read_bytes()).hexdigest() for path in paths},
        "maximum_parent_resident_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "maximum_control_child_resident_bytes": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
    }
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    main(parser.parse_args())
