"""Check every odd-line path certificate from source-derived native ranks.

This check uses the independently reviewed source and graph reader. It
does not import the path producer, its rank formula, or its graph builder.
"""

from collections import Counter
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import gzip
import json
import time


def require(condition, label):
    if not condition:
        raise ValueError(label)


def main(args):
    checker_path = Path(__file__).with_name("review_wire_gauge.py")
    require(sha256(checker_path.read_bytes()).hexdigest() == "1cce6ddeabd60f52e9ebafb02e2db4d289e68cdf5baaa106ca2397bf9cf7241a", "reviewed graph reader pin")
    spec = spec_from_file_location("independent_graph", checker_path)
    checker = module_from_spec(spec)
    spec.loader.exec_module(checker)
    receipts = [json.loads(gzip.decompress(path.read_bytes())) for path in args.certificates]
    word, programs = checker.load_source()
    for side in programs:
        checker.scalar_endpoint(word, programs[side], side == "backward")
    checker.check_orientation_duality(word, programs)
    for receipt in receipts:
        require(receipt["source_base"] == checker.BASE, "source base")
        require(receipt["word_sha256"] == checker.MEMBERS["slots/local/CANONICAL-WORD.json.gz"], "word pin")
        require(receipt["programs_sha256"] == checker.MEMBERS["slots/local/LOCAL-PROGRAMS.json.gz"], "program pin")
        checker.rebuild_graph(word, programs["forward"], receipt)
        require(receipt["graph"] == receipts[0]["graph"], "same graph in every receipt")
    graph = receipts[0]["graph"]
    native = graph["edges"]
    pairs = {(before, after, rank) for u, v, before, after, rank, kind, event in native}
    labels = list(map(checker.lagrangian, word["frames"]))
    for before, after, rank in pairs:
        require(len(checker.gf2_basis(labels[before] + labels[after])) - 9 == rank, "baseline rank")
    rows = [row for receipt in receipts for row in receipt["lines"] if "paths" in row]
    wanted = {a for a in range(1, 512) if a.bit_count() % 2}
    require(len(rows) == len(wanted) and {row["line"] for row in rows} == wanted, "all 256 odd lines exactly once")
    summaries, rank_checks = [], 0
    started = time.monotonic()
    for row in rows:
        a = row["line"]
        changed = [checker.transform(basis, a) for basis in labels]
        prices = {}
        for before, after, old in pairs:
            new = len(checker.gf2_basis(labels[before] + changed[after])) - 9
            prices[before, after, old] = new - old
            rank_checks += 1
        signed = Counter()
        for u, v, before, after, old, kind, event in native:
            if u != v:
                signed[tuple(sorted((u, v)))] += prices[before, after, old]
        positive = {edge: value for edge, value in signed.items() if value > 0}
        negative = {edge: -value for edge, value in signed.items() if value < 0}
        require(row["negative_edges"] == len(negative), "negative edge count")
        require(row["negative_mass"] == sum(negative.values()), "negative mass")
        supplied, used = Counter(), Counter()
        for route in row["paths"]:
            pair = tuple(route["negative_edge"])
            amount, path = route["amount"], route["path"]
            require(pair in negative, "negative demand belongs to source graph")
            require(type(amount) is int and amount > 0, "positive integer path amount")
            require(len(path) >= 2 and (path[0], path[-1]) == pair, "path endpoints")
            require(all(type(v) is int and 0 <= v < len(graph["labels"]) for v in path), "path vertices")
            supplied[pair] += amount
            for u, v in zip(path, path[1:]):
                edge = tuple(sorted((u, v)))
                require(edge in positive, "path uses a positive source edge")
                used[edge] += amount
        require(dict(supplied) == negative, "all negative demands covered exactly")
        require(all(amount <= positive[edge] for edge, amount in used.items()), "positive capacities")
        require(row["certified_minimum"] == 0, "constant gauge attains the proved bound")
        parent = list(range(len(graph["labels"])))

        def find(node):
            while parent[node] != node:
                parent[node] = parent[parent[node]]
                node = parent[node]
            return node

        for (u, v), capacity in positive.items():
            if capacity > used[u, v]:
                parent[find(u)] = find(v)
        live = {node for edge in native for node in edge[:2]}
        summaries.append({"line": a, "negative_edges": len(negative),
                          "paths": len(row["paths"]), "minimum_rank_delta": 0,
                          "unused_positive_components_on_live_vertices": len({find(i) for i in live})})
        if len(summaries) % 32 == 0:
            print("checked", len(summaries), "rank checks", rank_checks,
                  "seconds", round(time.monotonic() - started, 1), flush=True)
    even_rank_checks = 0
    for a in range(1, 512):
        if a.bit_count() % 2:
            continue
        changed = [checker.transform(basis, a) for basis in labels]
        for before, after, old in pairs:
            new = len(checker.gf2_basis(labels[before] + changed[after])) - 9
            require(new >= old, "an even line decreases a native rank")
            even_rank_checks += 1
    output = {"status": "PASS_ALL_PAIRED_WIRE_LINE_RANKS", "source_base": checker.BASE,
              "independent_graph_reader_sha256": sha256(checker_path.read_bytes()).hexdigest(),
              "certificate_sha256": {str(path): sha256(path.read_bytes()).hexdigest() for path in args.certificates},
              "odd_lines": len(rows), "native_rank_checks": rank_checks,
              "even_lines": 255, "even_native_rank_checks": even_rank_checks,
              "both_scalar_maps_checked_on_columns": len(word["start"]) + 8,
              "lines": summaries,
              "scope": "All 511 nonzero fixed-line gauges on the paired graph have minimum total rank change zero. Even lines never decrease a native edge rank. No general claim about all odd-line zero cuts or other cost functions."}
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(output["status"], "lines", len(rows), "native rank checks", rank_checks, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("certificates", type=Path, nargs="+")
    main(parser.parse_args())
