#!/usr/bin/env python3
"""Check a fixed P104 chain cover's exact concave-tariff optimality duals."""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from itertools import pairwise
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/p104-target-order-delivery/SCHEDULE.json"
LIMIT = 262144


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_bytes(path: Path) -> bytes:
    require(path.is_file() and not path.is_symlink(), f"not a regular file: {path}")
    with path.open("rb") as stream:
        data = stream.read(LIMIT + 1)
    require(len(data) <= LIMIT, f"file exceeds {LIMIT} bytes: {path}")
    return data


def read_json(path: Path):
    return json.loads(read_bytes(path))


def input_pins() -> dict[str, str]:
    manifest = read_json(HERE / "SOURCES.json")
    require(len(manifest["files"]) <= 8, "source manifest capacity")
    result = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            path = row["path"]
            require(path in {SOURCE, "research/p104-target-order-delivery/README.md"},
                    "unexpected live input")
            digest = sha256(read_bytes(ROOT / path)).hexdigest()
            require(digest == row["sha256"], f"source hash: {path}")
            result[path] = digest
    require(len(result) == 2, "missing live input")
    return result


def validate_cover(nodes, chains, centre: int) -> None:
    require(isinstance(chains, list) and 1 <= len(chains) <= 20, "chain capacity")
    flattened = []
    for chain in chains:
        require(isinstance(chain, list) and 1 <= len(chain) <= 20, "path capacity")
        require(all(type(mask) is int and 1 <= mask <= 255 for mask in chain),
                "chain mask")
        require(all(mask & (1 << centre) for mask in chain), "lost survivor")
        require(all(u != v and u & v == u for u, v in pairwise(chain)),
                "nonnested chain")
        flattened.extend(chain)
    require(sorted(flattened) == list(nodes), "missing or duplicate read frame")


def problem(schedule):
    edges = schedule["parent_edges"]
    require(isinstance(edges, list) and len(edges) == 116, "prefix edge count")
    nodes = [[] for _ in range(8)]
    masks = set()
    for edge in edges:
        require(isinstance(edge, list) and len(edge) == 2, "prefix edge shape")
        mask, centre = edge
        require(type(mask) is int and 1 <= mask <= 255, "prefix mask")
        require(type(centre) is int and 0 <= centre < 8, "prefix centre")
        require(mask & (1 << centre) and mask not in masks, "prefix survivor/duplicate")
        nodes[centre].append(mask)
        masks.add(mask)
    chains = schedule["chains"]
    require(isinstance(chains, list) and len(chains) == 8, "centre count")
    for centre in range(8):
        nodes[centre].sort()
        require(1 <= len(nodes[centre]) <= 20, "node capacity")
        validate_cover(nodes[centre], chains[centre], centre)
        antichain = [mask for mask in nodes[centre] if mask.bit_count() == 4]
        require(len(antichain) == len(chains[centre]), "rank-four saturation")
    require(sum(map(len, chains)) == 32, "total chain count")
    return nodes, chains


def histogram(chains) -> dict[str, int]:
    counts = Counter()
    for centre_chains in chains:
        for chain in centre_chains:
            ranks = [1, *[mask.bit_count() for mask in chain], 9]
            counts.update(v - u for u, v in pairwise(ranks) if v > u)
    return {str(rank): counts[rank] for rank in sorted(counts)}


def residual_arcs(nodes, chains, hinge: int):
    """Unit-capacity matching residual graph; source=2n, sink=2n+1."""
    n = len(nodes)
    index = {mask: i for i, mask in enumerate(nodes)}
    matching = {(index[u], index[v]) for chain in chains for u, v in pairwise(chain)}
    left_used = {i for i, _ in matching}
    right_used = {j for _, j in matching}
    source, sink = 2 * n, 2 * n + 1
    arcs = []
    for i in range(n):
        arcs.append((i, source, 0) if i in left_used else (source, i, 0))
        arcs.append((sink, n + i, 0) if i in right_used else (n + i, sink, 0))
    for i, lower in enumerate(nodes):
        for j, upper in enumerate(nodes):
            if lower != upper and lower & upper == lower:
                a, b = lower.bit_count(), upper.bit_count()
                cost = min(b - a, hinge) - min(9 - a, hinge) - min(b - 1, hinge)
                arcs.append((n + j, i, -cost) if (i, j) in matching
                            else (i, n + j, cost))
    return arcs


def check_dual(nodes, chains, record) -> int:
    require(type(record["hinge"]) is int and 1 <= record["hinge"] <= 7,
            "hinge domain")
    potentials = record["potentials"]
    require(isinstance(potentials, list) and len(potentials) == 2 * len(nodes) + 2,
            "potential dimension")
    require(all(type(value) is int and -256 <= value <= 256 for value in potentials),
            "potential integer/capacity")
    arcs = residual_arcs(nodes, chains, record["hinge"])
    for u, v, cost in arcs:
        require(cost + potentials[u] - potentials[v] >= 0, "negative reduced cost")
    return len(arcs)


def check_certificate(schedule, certificate, source_digest: str):
    nodes, chains = problem(schedule)
    require(certificate["schema"] == "p104-prefix-tail-duals/v1", "certificate schema")
    require(certificate["source_sha256"] == source_digest, "certificate source binding")
    actual_histogram = histogram(chains)
    require(certificate["optimal_histogram"] == actual_histogram, "false optimum value")
    require(actual_histogram == {"1": 85, "2": 17, "3": 19, "4": 20}, "stated histogram")
    records = certificate["centres"]
    require(isinstance(records, list) and len(records) == 8, "dual centre count")
    inequalities = 0
    for centre in range(8):
        record = records[centre]
        require(record["centre"] == centre and type(record["centre"]) is int,
                "dual centre identity")
        require(record["nodes"] == nodes[centre], "dual node identity")
        require(record["chain_count"] == len(chains[centre]), "dual chain count")
        require(record["rank_four_witness"] ==
                [mask for mask in nodes[centre] if mask.bit_count() == 4], "antichain identity")
        duals = record["hinges"]
        require(isinstance(duals, list) and len(duals) == 7, "dual hinge count")
        for hinge, dual in enumerate(duals, 1):
            require(dual["hinge"] == hinge, "missing/duplicate hinge")
            inequalities += check_dual(nodes[centre], chains[centre], dual)
    return nodes, chains, inequalities


def shortest_potentials(arcs, vertices: int) -> list[int]:
    """Generate a witness, never use a solver status as acceptance."""
    distances = [0] * vertices
    for _ in range(vertices):
        changed = False
        for u, v, cost in arcs:
            if distances[v] > distances[u] + cost:
                distances[v] = distances[u] + cost
                changed = True
        if not changed:
            break
    require(all(cost + distances[u] - distances[v] >= 0 for u, v, cost in arcs),
            "no optimality potential for the supplied cover")
    return distances


def make_certificate(schedule, source_digest: str):
    nodes, chains = problem(schedule)
    records = []
    for centre in range(8):
        duals = []
        for hinge in range(1, 8):
            arcs = residual_arcs(nodes[centre], chains[centre], hinge)
            duals.append({"hinge": hinge, "potentials":
                          shortest_potentials(arcs, 2 * len(nodes[centre]) + 2)})
        records.append({"centre": centre, "nodes": nodes[centre],
                        "chain_count": len(chains[centre]), "rank_four_witness":
                        [mask for mask in nodes[centre] if mask.bit_count() == 4],
                        "hinges": duals})
    return {"schema": "p104-prefix-tail-duals/v1", "source_sha256": source_digest,
            "optimal_histogram": histogram(chains), "centres": records}


def rejected(schedule, certificate, source_digest: str) -> None:
    try:
        check_certificate(schedule, certificate, source_digest)
    except ValueError:
        return
    raise ValueError("semantic rejection control was accepted")


def controls(schedule, certificate, source_digest: str) -> list[str]:
    tested = []
    for mode in range(8):
        changed_schedule, changed_certificate = deepcopy(schedule), deepcopy(certificate)
        if mode == 0:
            changed_schedule["chains"][0][0].append(changed_schedule["chains"][0][0][-1])
        elif mode == 1:
            changed_schedule["chains"][0][0].pop()
        elif mode == 2:
            changed_schedule["chains"][0][0].reverse()
        elif mode == 3:
            changed_schedule["parent_edges"][0][1] = 0
        elif mode == 4:
            changed_certificate["optimal_histogram"]["1"] += 1
        elif mode == 5:
            changed_certificate["centres"][0]["hinges"][0]["potentials"].pop()
        elif mode == 6:
            dual = changed_certificate["centres"][0]["hinges"][1]
            nodes = changed_certificate["centres"][0]["nodes"]
            u, v, cost = residual_arcs(nodes, schedule["chains"][0], 2)[0]
            dual["potentials"][v] = dual["potentials"][u] + cost + 1
        else:
            changed_certificate["centres"][0]["hinges"][1]["hinge"] = 1
        rejected(changed_schedule, changed_certificate, source_digest)
        tested.append(["duplicate-frame", "omitted-frame", "reversed-chain",
                       "wrong-survivor", "false-optimum", "short-potential",
                       "negative-reduced-cost", "duplicate-hinge"][mode])
    return tested


def make_receipt(pins, nodes, chains, inequalities: int, tested):
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "CERTIFICATE.json", "verify.py")
    files = {name: sha256(read_bytes(HERE / name)).hexdigest() for name in names}
    return {"schema": "p104-prefix-tail-result/v1", "claim_type": "scoped proof",
            "files_sha256": files, "inputs_sha256": pins,
            "read_frames": sum(map(len, nodes)), "chains": sum(map(len, chains)),
            "chain_counts": list(map(len, chains)), "hinge_duals": 56,
            "checked_residual_inequalities": inequalities,
            "optimal_histogram": histogram(chains), "rank_mass": 256,
            "hinge_optima": {str(j): sum(count * min(int(rank), j)
                                         for rank, count in histogram(chains).items())
                              for j in range(1, 9)}, "controls_rejected": tested}


def write_json(path: Path, value) -> None:
    text = json.dumps(value, indent=2, sort_keys=True) + "\n"
    require(path.write_text(text) == len(text), "short artifact write")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    outputs = parser.add_mutually_exclusive_group()
    outputs.add_argument("--emit-certificate", type=Path)
    outputs.add_argument("--emit-receipt", type=Path)
    args = parser.parse_args()
    pins = input_pins()
    schedule = read_json(ROOT / SOURCE)
    if args.emit_certificate:
        certificate = make_certificate(schedule, pins[SOURCE])
        check_certificate(schedule, certificate, pins[SOURCE])
        write_json(args.emit_certificate, certificate)
        print("PASS_GENERATED_P104_PREFIX_TAIL_DUALS")
        return
    certificate = read_json(HERE / "CERTIFICATE.json")
    nodes, chains, inequalities = check_certificate(schedule, certificate, pins[SOURCE])
    tested = controls(schedule, certificate, pins[SOURCE])
    receipt = make_receipt(pins, nodes, chains, inequalities, tested)
    if args.emit_receipt:
        write_json(args.emit_receipt, receipt)
    else:
        require(read_json(HERE / "RESULT.json") == receipt, "receipt mismatch")
    print(f"PASS_P104_PREFIX_TAIL_OPTIMUM chains=32 frames=116 duals=56 "
          f"inequalities={inequalities} controls={len(tested)} all_concave no_new_kappa")


if __name__ == "__main__":
    main()
