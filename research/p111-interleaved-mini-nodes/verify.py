#!/usr/bin/env python3
"""Check the finite optimality certificate and the complete dirty R439 word.

Ryan Haines, with substantial OpenAI Codex assistance. Apache-2.0.
This verifier does not import search.py or PR728's implementation.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import itertools
import json
import struct
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"


class Reject(Exception):
    pass


def need(ok, message):
    if not ok:
        raise Reject(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def xor_all(values):
    result = 0
    for value in values:
        result ^= value
    return result


def rows_of(columns):
    return tuple(sum(((column >> i) & 1) << j for j, column in enumerate(columns))
                 for i in range(len(columns)))


def check_graph(records, k):
    """Certify closure and exact distances using row-coordinate transitions.

    Edge inequalities give lower bounds for EVERY path from the start.
    A distance-decreasing predecessor for every other state gives attainment.
    Closure prevents an omitted state from hiding a shorter circuit.
    """
    table = {}
    matrices = set()
    for columns, seen, distance in records:
        need(len(columns) == k and all(type(c) is int and 0 < c < 1 << k for c in columns),
             "invalid matrix column")
        span = {xor_all(columns[i] for i in range(k) if bits >> i & 1)
                for bits in range(1 << k)}
        need(len(span) == 1 << k, "singular state")
        need(type(seen) is int and 0 <= seen < 1 << (1 << k) and not seen & 1,
             "invalid exposure set")
        need(all(seen >> c & 1 for c in [*columns, *(1 << i for i in range(k))]),
             "missing initial/current exposure")
        need(type(distance) is int and distance >= 0, "invalid distance")
        matrix = rows_of(columns)
        key = matrix, seen
        need(key not in table, "duplicate graph state")
        table[key] = distance
        matrices.add(matrix)
    identity = tuple(1 << i for i in range(k))
    initial = identity, sum(1 << i for i in identity)
    need(table.get(initial) == 0, "missing distance-zero initial state")
    reached = {initial}
    edge_count = 0
    for (matrix, seen), distance in table.items():
        for d, s in itertools.permutations(range(k), 2):
            # Right multiplication by the forward transvection d += s.
            changed = tuple(row ^ (((row >> d) & 1) << s) for row in matrix)
            exposed = [sum(((row >> j) & 1) << i for i, row in enumerate(changed))
                       for j in range(k)]
            after = changed, seen | sum(1 << c for c in exposed)
            need(after in table, "graph is not transition-closed")
            need(table[after] <= distance + 1, "distance potential violates an edge")
            if table[after] == distance + 1:
                reached.add(after)
            edge_count += 1
    need(reached == set(table), "state lacks a decreasing-distance predecessor")
    need(len(matrices) == {2: 6, 3: 168}[k], "incomplete general linear group")
    return table, {"states": len(table), "matrices": len(matrices), "edges_checked": edge_count}


def injection_prices(seen, k):
    """Independent exhaustive SUBSET census, rather than the generator's BFS."""
    available = [p for p in range(1, 1 << k) if seen >> p & 1]
    costs = [1 << k] * (1 << k)
    for subset in range(1 << len(available)):
        value = xor_all(p for i, p in enumerate(available) if subset >> i & 1)
        costs[value] = min(costs[value], subset.bit_count())
    need(max(costs) < 1 << k, "unspanned injection pattern")
    return costs


def transfer(gates, registers):
    """Set-valued symbolic replay, separate from generator bit-vector arithmetic."""
    state = {r: {i} for i, r in enumerate(registers)}
    for _, destination, sources in gates:
        need(destination in state and len({destination, *sources}) == len(sources) + 1,
             "invalid local gate")
        for source in sources:
            need(source in state, "undeclared local wire")
            state[destination].symmetric_difference_update(state[source])
    return tuple(sum(1 << i for i in state[r]) for r in registers)


def check_node(word, node, table):
    frame = node["frame"]
    indices = [i for i, gate in enumerate(word["A"]) if gate[0] == frame]
    need(indices == node["original_a_indices"] and indices == list(range(indices[0], indices[-1] + 1)),
         "node source range mismatch")
    old = [word["A"][i] for i in indices]
    destinations = [d for _, d, _ in old]
    external = sorted({s for _, _, ss in old for s in ss} - set(destinations))
    need(destinations == node["destinations"] and external == node["external"], "node wires mismatch")
    need(len(set(destinations)) == len(destinations), "repeated original destination")
    registers, k = destinations + external, len(destinations)
    expected = transfer(old, registers)
    linear = tuple(row & ((1 << k) - 1) for row in expected[:k])
    patterns = [sum(((row >> (k + j)) & 1) << i for i, row in enumerate(expected[:k]))
                for j in range(len(external))]
    need(rows_of(node["linear_columns"]) == linear and node["input_patterns"] == patterns,
         "advertised local map mismatch")
    candidates = sorted([distance + sum(injection_prices(seen, k)[p] for p in patterns), distance, seen]
                        for (matrix, seen), distance in table.items() if matrix == linear)
    need(candidates == node["terminal_costs"], "incomplete terminal cost census")
    minimum, distance, seen = candidates[0]
    need([minimum, distance, seen] == [node["minimum_xors"], node["destination_xors"],
                                     node["terminal_exposure_mask"]], "false optimum")
    circuit = node["replacement"]
    need(all(f == frame and d in destinations and len(ss) == 1
             and ss[0] in registers and ss[0] != d for f, d, ss in circuit),
         "circuit is outside the read-only external class")
    need(len(circuit) == minimum, "circuit has an unpaid operation")
    need(sum(ss[0] in destinations for _, _, ss in circuit) == distance, "wrong basis-change bill")
    actual_columns = [1 << i for i in range(k)]
    actual_seen = sum(1 << col for col in actual_columns)
    for _, d, (source,) in reversed(circuit):
        if source in destinations:
            actual_columns[destinations.index(source)] ^= actual_columns[destinations.index(d)]
            actual_seen |= sum(1 << col for col in actual_columns)
    need(actual_columns == node["linear_columns"] and actual_seen == seen,
         "witness destination path does not match the certified terminal state")
    need(transfer(circuit, registers) == expected, "replacement has the wrong arbitrary-input map")
    before_cost = sum(len(ss) for _, _, ss in old)
    need(before_cost == node["original_xors"], "incorrect original bill")

    # Exhaustive Boolean truth tables also check original and emitted gate ordering.
    def evaluate(gates, value):
        values = {r: (value >> i) & 1 for i, r in enumerate(registers)}
        for _, d, ss in gates:
            for s in ss:
                values[d] ^= values[s]
        return tuple(values[r] for r in registers)
    for value in range(1 << len(registers)):
        need(evaluate(old, value) == evaluate(circuit, value), "Boolean input counterexample")

    # Recompute PR728's single-injection-layer minima without importing its code.
    group_distances = {}
    for (matrix, _), cost in table.items():
        group_distances[matrix] = min(cost, group_distances.get(matrix, cost))
    single_layer = []
    for post, post_cost in group_distances.items():
        columns = rows_of(post)
        inverse = {xor_all(columns[i] for i in range(k) if bits >> i & 1): bits
                   for bits in range(1 << k)}
        pre_columns = tuple(inverse[col] for col in rows_of(linear))
        single_layer.append(post_cost + group_distances[rows_of(pre_columns)]
                            + sum(inverse[p].bit_count() for p in patterns))
    return {"frame": frame, "before": before_cost, "after": minimum,
            "destination_xors": distance, "external_reads": minimum - distance,
            "single_layer_minimum": min(single_layer), "single_layer_candidates": len(single_layer),
            "boolean_inputs_checked": 1 << len(registers), "terminal_states": len(candidates)}


def rebuild_cleanup(word):
    v = word["v"]
    full = next(i for i, frame in enumerate(word["frames"]) if len(frame) == v)
    return [[full, d, list(ss)] for _, d, ss in reversed(word["A"] + word["B"])
            if d < v or d >= 2 * v]


def build_word(word, nodes):
    replacements = {node["original_a_indices"][0]: node for node in nodes}
    result = copy.deepcopy(word)
    result["A"] = []
    index = 0
    while index < len(word["A"]):
        if index in replacements:
            node = replacements[index]
            result["A"].extend(copy.deepcopy(node["replacement"]))
            index += len(node["original_a_indices"])
        else:
            result["A"].append(copy.deepcopy(word["A"][index]))
            index += 1
    result["C"] = rebuild_cleanup(result)
    return result


def frame_paths(word):
    frames = [set(f) for f in word["frames"]]
    paths = [[f] for f in word["start"]]
    def move(r, f):
        if paths[r][-1] != f:
            need(frames[paths[r][-1]] < frames[f], "illegal frame descent or lateral move")
            paths[r].append(f)
    for section in "DABC":
        for f, d, ss in word[section]:
            for r in [d, *ss]:
                move(r, f)
    for r, f in enumerate(word["final"]):
        move(r, f)
    return paths


def whole_endpoint(word):
    n, v = 2 * word["v"] + word["R"], word["v"]
    state = [{i} for i in range(n)]
    def run(section):
        for _, d, sources in word[section]:
            for s in sources:
                state[d].symmetric_difference_update(state[s])
    run("D")
    run("A")
    snapshots = [state[r].copy() for r in word["ret"]]
    for t, reads in enumerate(word["scatter"]):
        for k in reads:
            state[v + t].symmetric_difference_update(snapshots[k])
    run("B")
    run("C")
    for r, actual in enumerate(state):
        expected = {r, r - v} if v <= r < 2 * v else {r}
        need(actual == expected, "dirty-input endpoint mismatch at register " + str(r))
    return n


def load_checker():
    path = ROOT / "research/e8-bit-p111-tuned/code/xcheck_p.py"
    spec = importlib.util.spec_from_file_location("p111_original_xcheck", path)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    return checker


def export_and_bound(word, out):
    path = out / "word.json.gz"
    path.parent.mkdir(parents=True)
    path.write_bytes(gzip.compress(canonical(word), mtime=0))
    exporter = ROOT / "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
    subprocess.run([sys.executable, "-I", "-B", str(exporter), str(path), str(out / "records")],
                   check=True, capture_output=True, text=True)
    raw = (out / "records/249-records.bin").read_bytes()
    need(len(raw) % 24 == 0, "misaligned exporter records")
    records = list(struct.iter_unpack("<6i", raw))
    n = 2 * word["v"] + word["R"]
    bounds = []
    for reverse in (False, True):
        norms, maximum, opened = [1] * (n + 1), 1, False
        for op, a, b, coefficient, _, _ in (reversed(records) if reverse else records):
            if op == 0:
                continue
            if reverse and op in (2, 3):
                op = 5 - op
            if op == 1:
                norms[a] += abs(coefficient) * norms[b]
                maximum = max(maximum, norms[a])
            elif op == 2:
                need(not opened, "nested retained copy")
                norms[b], opened = norms[a], True
            elif op == 3:
                need(opened, "unmatched retained erase")
                norms[b], opened = 0, False
            else:
                raise Reject("unknown record opcode")
        need(not opened, "unclosed retained copy")
        bounds.append(maximum)
    payload = 64 * bounds[0] ** 3 * bounds[1] ** 2
    need(payload < 1 << 104, "native positive-prefix cap exceeded")
    return {"records": len(records), "adds": sum(r[0] == 1 for r in records),
            "copies": sum(r[0] == 2 for r in records), "erasures": sum(r[0] == 3 for r in records),
            "forward_positive_bound": bounds[0], "reverse_positive_bound": bounds[1],
            "payload_upper": str(payload), "payload_bits": payload.bit_length(),
            "record_sha256": hashlib.sha256(raw).hexdigest()}, records


def must_reject(name, action):
    try:
        action()
    except Reject:
        return name
    raise Reject("negative control accepted: " + name)


def verify(out):
    certificate = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    need(certificate["schema"] == "p111-interleaved-mini-nodes/1", "unknown schema")
    for path, digest in certificate["source_sha256"].items():
        need(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, "source mismatch: " + path)
    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    tables, coverage = {}, {}
    for k in (2, 3):
        tables[k], coverage[str(k)] = check_graph(certificate["graphs"][str(k)], k)
    nodes = certificate["nodes"]
    need([node["frame"] for node in nodes] == list(range(506, 510)), "incomplete mini-node census")
    results = [check_node(word, node, tables[len(node["destinations"])]) for node in nodes]
    need({str(r["frame"]): r["single_layer_minimum"] for r in results}
         == certificate["comparison_minima"], "single-layer predecessor comparison differs")
    candidate = build_word(word, nodes)
    need(all(candidate[k] == word[k] for k in word if k not in ("A", "C")), "unrelated field changed")
    need(candidate["C"] == rebuild_cleanup(candidate), "literal cleanup reversal fails")
    before_paths, after_paths = frame_paths(word), frame_paths(candidate)
    need(before_paths == after_paths, "paid frame path changed")
    whole_endpoint(word)
    n = whole_endpoint(candidate)
    checker = load_checker()
    W, labels, flow, hypotheses, conclusion, _ = checker.check(candidate)
    need(all(hypotheses.values()) and all(conclusion.values()), "inherited interface guard fails")
    profile = Counter(W.fdim[b] - W.fdim[a] for path in after_paths for a, b in itertools.pairwise(path))
    profile.update(t["rank"] for t in flow["totals"])
    before_bill, before_records = export_and_bound(word, out / "before")
    after_bill, after_records = export_and_bound(candidate, out / "after")
    # MOVE order may differ inside the same frame; every wire's complete path agrees.
    need(Counter(r for r in before_records if r[0] != 1)
         == Counter(r for r in after_records if r[0] != 1), "non-ADD event inventory changed")
    need(before_bill["adds"] - after_bill["adds"] == 32, "complete ADD saving differs")

    controls = []
    bad = copy.deepcopy(certificate["graphs"]["3"])
    bad.pop()
    controls.append(must_reject("incomplete_graph", lambda: check_graph(bad, 3)))
    bad = copy.deepcopy(certificate["graphs"]["3"])
    next(row for row in bad if row[2] == 1)[2] = 2
    controls.append(must_reject("inflated_distance_potential", lambda: check_graph(bad, 3)))
    bad_node = copy.deepcopy(nodes[0])
    bad_node["minimum_xors"] -= 1
    controls.append(must_reject("unpaid_gate", lambda: check_node(word, bad_node, tables[3])))
    bad_node = copy.deepcopy(nodes[0])
    ext = bad_node["external"]
    bad_node["replacement"][:0] = [[506, ext[0], [ext[1]]]] * 2
    # This neutral pair preserves the exact map but violates the optimization class.
    controls.append(must_reject("neutral_external_writes", lambda: check_node(word, bad_node, tables[3])))
    bad_word = copy.deepcopy(candidate)
    bad_word["C"].pop()
    controls.append(must_reject("omitted_cleanup", lambda: whole_endpoint(bad_word)))
    bad_word = copy.deepcopy(candidate)
    idx = next(i for i, (f, _, ss) in enumerate(bad_word["A"]) if f == 506 and ss[0] in ext)
    del bad_word["A"][idx]
    bad_word["C"] = rebuild_cleanup(bad_word)
    controls.append(must_reject("missing_injection_with_matching_cleanup", lambda: whole_endpoint(bad_word)))
    bad_word = copy.deepcopy(candidate)
    next(g for g in bad_word["A"] if g[0] == 506)[0] = 0
    controls.append(must_reject("illegal_frame_descent", lambda: frame_paths(bad_word)))
    stale = copy.deepcopy(candidate)
    stale["C"] = word["C"]
    whole_endpoint(stale)  # Positive semantic control; rejected only by literal H4.
    controls.append(must_reject("stale_cleanup_literal_H4",
                                lambda: need(stale["C"] == rebuild_cleanup(stale), "H4 fails")))

    return {"status": "PASS_P111_INTERLEAVED_MINI_NODES", "graph_coverage": coverage,
            "nodes": results, "columns": n, "closed_frames": labels["frames"],
            "copy_ranks": [t["rank"] for t in flow["totals"]],
            "paid_profile": {str(k): v for k, v in sorted(profile.items())},
            "rank_mass": sum(k * v for k, v in profile.items()),
            "identical_register_frame_paths": len(after_paths),
            "hypotheses": hypotheses, "conclusion": conclusion,
            "before": before_bill, "after": after_bill,
            "word_sha256": hashlib.sha256(canonical(candidate)).hexdigest(),
            "negative_controls": controls,
            "extra_saving_over_pr728": 12, "new_kappa_claim": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="new output directory; must not exist")
    parser.add_argument("--record-expected", type=Path, help="write a NEW expected receipt after all checks")
    args = parser.parse_args()
    if args.out:
        args.out.mkdir(parents=True, exist_ok=False)
        result = verify(args.out)
    else:
        with tempfile.TemporaryDirectory(prefix="p111-interleaved-") as directory:
            result = verify(Path(directory))
    if args.record_expected:
        with args.record_expected.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    else:
        expected = json.loads((HERE / "EXPECTED.json").read_text(encoding="utf-8"))
        need(result == expected, "deterministic receipt differs from EXPECTED.json")
    if args.out:
        (args.out / "receipt.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PASS_P111_INTERLEAVED_MINI_NODES states=866 minima=13,9,9,8 "
          "ADDs=24305->24273 saved=32 extra_vs_PR728=12 columns=661 controls=8 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (Reject, ValueError, OSError) as error:
        raise SystemExit("REJECT: " + str(error)) from error
