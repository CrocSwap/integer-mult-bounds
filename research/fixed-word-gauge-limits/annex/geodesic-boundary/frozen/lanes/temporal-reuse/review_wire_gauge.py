"""Independently check a wire-gauge flow certificate from pinned local programs."""

from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import gzip
import io
import json
import subprocess
import tarfile


BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
MEMBERS = {
    "slots/local/CANONICAL-WORD.json.gz": "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    "slots/local/LOCAL-PROGRAMS.json.gz": "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
}


def check(value, message):
    if not value:
        raise ValueError(message)


def load_source(repo):
    raw = subprocess.check_output(["git", "show", BASE + ":" + ARCHIVE], cwd=repo)
    check(sha256(raw).hexdigest() == "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754", "Archive pin")
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        output = []
        for name, expected in MEMBERS.items():
            payload = archive.extractfile(name).read()
            check(sha256(payload).hexdigest() == expected, "Member pin: " + name)
            output.append(json.loads(gzip.decompress(payload)))
    return output


def gf2_basis(rows):
    pivot = {}
    for value in rows:
        while value:
            index = value.bit_length() - 1
            if index not in pivot:
                pivot[index] = value
                break
            value ^= pivot[index]
    return list(pivot.values())


def lagrangian(frame):
    orthogonal = gf2_basis(x for x in range(1, 512)
                          if all((x & row).bit_count() % 2 == 0 for row in frame))
    rows = [u | (u << 9) for u in frame] + [v << 9 for v in orthogonal]
    check(len(gf2_basis(rows)) == 9, "Canonical Lagrangian dimension")
    return rows


def transform(rows, line):
    return [v ^ (line if ((v >> 9) & line).bit_count() % 2 else 0) for v in rows]


def frame_span(frame):
    result = {0}
    for row in frame:
        result |= {value ^ row for value in result}
    return result


def scalar_endpoint(word, program, backward):
    n = len(word["start"])
    rows = [{j: Fraction(1)} for j in range(n + 8)]
    def index(register):
        return register[1] + (n if register[0] == "C" else 0)
    for event in program:
        if event[0] != "scalar":
            continue
        gate = event[1]
        i = index(gate[1])
        if gate[0] == "clear":
            rows[i] = {}
        elif gate[0] == "copy":
            rows[i] = rows[index(gate[2])].copy()
        elif gate[0] == "scale":
            factor = Fraction(gate[2], gate[3])
            rows[i] = {j: factor * value for j, value in rows[i].items()}
        else:
            check(gate[0] == "add", "Scalar opcode")
            factor = Fraction(gate[3], gate[4])
            for j, value in list(rows[index(gate[2])].items()):
                value = rows[i].get(j, Fraction(0)) + factor * value
                if value:
                    rows[i][j] = value
                else:
                    rows[i].pop(j, None)
    expected = [{j: Fraction(1)} for j in range(n)] + [{} for _ in range(8)]
    for p in range(word["v"]):
        if backward:
            expected[p][word["v"] + p] = Fraction(-1)
        else:
            expected[word["v"] + p][p] = Fraction(1)
    check(rows == expected, "The original scalar endpoint is not the stated dirty shear")


def check_orientation_duality(word, programs):
    records = []
    for name in ("forward", "backward"):
        current = {("L", r): ("L", r, 0) for r in range(len(word["start"]))}
        serial = Counter()
        clear_count = Counter()
        scalar_links = Counter()
        native_edges = []
        for event in programs[name]:
            kind = event[0]
            if kind == "scalar":
                gate, frame = event[1:]
                target = tuple(gate[1])
                if gate[0] == "clear":
                    clear_count[target] += 1
                    level = "dead" if clear_count[target] == 2 else ("high" if frame else "low")
                    current[target] = ("C", target[1], level)
                elif gate[0] in ("add", "copy"):
                    scalar_links[tuple(sorted((current[target], current[tuple(gate[2])])))] += 1
            elif kind == "center":
                _, register, before, after, rank = event
                old = current["C", register]
                current["C", register] = ("C", register, "high" if after else "low")
                native_edges.append(("center", tuple(sorted((old, current["C", register]))),
                                     tuple(sorted((before, after))), rank))
            elif kind in ("climb", "adapter", "residual_adapter"):
                register = event[2]
                old = current["L", register]
                serial[register] += 1
                current["L", register] = ("L", register, serial[register])
                native_edges.append((kind, old, current["L", register], tuple(event[1:])))
        check(set(clear_count.values()) == {2} and len(clear_count) == 8,
              "Private lifetimes for orientation duality")
        records.append((scalar_links, native_edges,
                        [current["L", r] for r in range(len(word["start"]))]))
    check(records[0] == records[1], "The forward and backward gauge graphs differ")


def rebuild_graph(word, program, certificate):
    labels = []
    links = []
    native = []
    current = {}
    def fresh(frame):
        labels.append(frame)
        return len(labels) - 1
    for r, frame in enumerate(word["start"]):
        current["L", r] = fresh(frame)
    starts = [current["L", r] for r in range(len(word["start"]))]
    previous_scalar = None
    for event_index, event in enumerate(program):
        kind = event[0]
        if kind == "phase":
            continue
        if kind == "scalar":
            gate, frame = event[1:]
            target = tuple(gate[1])
            if gate[0] == "clear":
                check(target[0] == "C", "Persistent CLEAR")
                current[target] = fresh(frame)
            else:
                check(target in current and labels[current[target]] == frame, "Scalar target frame")
                if gate[0] in ("add", "copy"):
                    source = tuple(gate[2])
                    check(source in current and labels[current[source]] == frame, "Scalar source frame")
                    links.append((current[target], current[source]))
                    if gate[0] == "copy":
                        check(previous_scalar == ["scalar", ["clear", list(target)], frame],
                              "COPY must follow a fresh CLEAR in this source word")
                else:
                    check(gate[0] == "scale", "Unexpected scalar operation")
            previous_scalar = event
            continue
        if kind == "climb":
            _, _, register, before, after, rank = event
            key = ("L", register)
        elif kind == "center":
            _, register, before, after, rank = event
            key = ("C", register)
        else:
            check(kind in ("adapter", "residual_adapter"), "Unexpected native operation")
            key = ("L", event[2])
            before = after = labels[current[key]]
            rank = 0
        check(labels[current[key]] == before, "Native entrance frame")
        old = current[key]
        current[key] = fresh(after)
        native.append((old, current[key], before, after, rank, kind, event_index))
    ends = [current["L", r] for r in range(len(starts))]
    check([labels[node] for node in ends] == word["final"], "Persistent final frames")
    for helper in range(2 * word["v"], len(starts)):
        links.append((starts[helper], ends[helper]))
    for port in range(word["v"]):
        for node in (starts[word["v"] + port], ends[port], ends[word["v"] + port]):
            links.append((starts[port], node))

    # Components are built after all constraints, with a different root rule.
    parent = list(range(len(labels)))
    def find(node):
        while parent[node] != node:
            node = parent[node]
        return node
    for left, right in links:
        a, b = find(left), find(right)
        parent[max(a, b)] = min(a, b)
    roots = {find(node) for node in range(len(labels))}
    graph = certificate["graph"]
    check(graph["paired_boundaries"] and not graph["fixed"], "Boundary mode")
    check(len(labels) == graph["raw_segments"], "Segment count")
    check(len(roots) == len(graph["labels"]), "Component count")
    check(len(labels) - len(roots) == graph["scalar_access_unions"], "Union count")
    check(len(native) == len(graph["edges"]), "Native edge count")
    mapping = {}
    inverse = {}
    centres = []
    for position, (ours, saved) in enumerate(zip(native, graph["edges"])):
        check(list(ours[2:]) == saved[2:], "A native edge differs from the source word")
        for node, component in zip(ours[:2], saved[:2]):
            root = find(node)
            check(mapping.get(root, component) == component, "A source component was split")
            check(inverse.get(component, root) == root, "Source components were merged")
            mapping[root] = component
            inverse[component] = root
        if ours[5] == "center":
            centres.append(position)
    check(centres == graph["centre_edges"] and len(centres) == 8, "Centre traversal inventory")
    check(len(roots - mapping.keys()) == 8, "Unexpected isolated wire components")
    check(len(set(range(len(roots))) - inverse.keys()) == 8, "Unexpected isolated certificate components")
    return graph["edges"]


def reduce_energy(edges, fixed, count):
    values = defaultdict(lambda: [0, 0])
    constant = 0
    capacity = Counter()
    for (u, v), weight in edges.items():
        if u in fixed and v in fixed:
            constant += weight * (fixed[u] != fixed[v])
        elif u in fixed or v in fixed:
            anchor, other = (u, v) if u in fixed else (v, u)
            for bit in (0, 1):
                values[other][bit] += weight * (fixed[anchor] != bit)
        else:
            check(weight >= 0, "A negative edge is not covered by a branch variable")
            capacity[u, v] += weight
            capacity[v, u] += weight
    for node, (zero_cost, one_cost) in values.items():
        constant += min(zero_cost, one_cost)
        if one_cost > zero_cost:
            capacity[count, node] += one_cost - zero_cost
        elif zero_cost > one_cost:
            capacity[node, count + 1] += zero_cost - one_cost
    return constant, {pair: value for pair, value in capacity.items() if value}


def check_flow_cut(case, signed_edges, count, fixed, expected_energy):
    check(case["fixed"] == [list(item) for item in sorted(fixed.items())], "Fixed branch assignments")
    selected = set(case["flipped_frames"])
    check(len(selected) == len(case["flipped_frames"]) and selected <= set(range(count)), "Selected nodes")
    check(all((node in selected) == bool(bit) for node, bit in fixed.items()), "Cut violates a fixed bit")
    constant, capacity = reduce_energy(signed_edges, fixed, count)
    check(constant == case["constant"], "Cut constant")
    flow = {}
    for u, v, value in case["flow"]:
        check(all(type(x) is int for x in (u, v, value)) and 0 <= u < v < count + 2,
              "Flow entry type or node")
        check((u, v) not in flow, "Duplicate flow entry")
        flow[u, v], flow[v, u] = value, -value
    divergence = Counter()
    for (u, v), value in flow.items():
        check(-capacity.get((v, u), 0) <= value <= capacity.get((u, v), 0), "Flow capacity")
        divergence[u] += value
    check(all(divergence[node] == 0 for node in range(count)), "Flow conservation")
    flow_value = divergence[count]
    check(flow_value == case["flow_value"] and divergence[count + 1] == -flow_value,
          "Flow terminal values")
    zero_side = {count} | (set(range(count)) - set(fixed) - selected)
    cut = sum(value for (u, v), value in capacity.items() if u in zero_side and v not in zero_side)
    check(cut == flow_value, "The feasible flow and cut do not agree")
    energy = sum(weight for (u, v), weight in signed_edges.items() if (u in selected) != (v in selected))
    check(energy == flow_value + constant == expected_energy, "Exact objective")
    return energy, capacity, flow, selected


def zero_cut_rigidity(capacity, flow, count, fixed, native):
    forward, reverse = defaultdict(list), defaultdict(list)
    for u, v in capacity.keys() | flow.keys():
        if capacity.get((u, v), 0) - flow.get((u, v), 0) > 0:
            forward[u].append(v)
            reverse[v].append(u)
    def reachable(start, adjacency):
        seen, pending = {start}, [start]
        while pending:
            for target in adjacency[pending.pop()]:
                if target not in seen:
                    seen.add(target)
                    pending.append(target)
        return seen
    zero = reachable(count, forward) - {count}
    one = reachable(count + 1, reverse) - {count + 1}
    check(not (zero & one), "A residual source to sink path remains")
    forced = dict(fixed)
    forced.update((node, 0) for node in zero)
    forced.update((node, 1) for node in one)
    incident = {node for edge in native for node in edge[:2]}
    check(incident <= forced.keys(), "A native gauge is free in an optimal cut")
    values = {forced[node] for node in incident}
    check(len(values) == 1, "An optimal native gauge is not constant")
    check(len(set(range(count)) - forced.keys()) == 8,
          "The optimal cut has unexpected isolated freedom")
    return dict(common_native_bit=values.pop(), forced_native_components=len(incident),
                free_isolated_zero_components=8)


def check_profile(case, native, deltas, selected):
    profile = Counter()
    by_kind = Counter()
    centres = []
    for index, (edge, delta) in enumerate(zip(native, deltas)):
        u, v, _, _, rank, kind, _ = edge
        crossed = (u in selected) != (v in selected)
        profile[rank + delta * crossed] += 1
        by_kind[kind] += delta * crossed
        if kind == "center" and crossed:
            centres.append(index)
    check(dict(profile) == {int(k): v for k, v in case["profile"].items()}, "Candidate child profile")
    check(dict(by_kind) == case["kind_rank_delta"], "Candidate operation cost")
    check(sum(by_kind.values()) == case["rank_delta"] and centres == case["changed_centres"], "Changed centre set")


def check_case(case, signed_edges, native, deltas, count, fixed):
    energy, capacity, flow, selected = check_flow_cut(case, signed_edges, count, fixed, case["rank_delta"])
    check_profile(case, native, deltas, selected)
    rigidity = (zero_cut_rigidity(capacity, flow, count, fixed, native)
                if energy == 0 and case["forced_centre_cross"] is None else None)
    return energy, rigidity


def run(repo, certificate_path):
    raw = certificate_path.read_bytes()
    digest = sha256(raw).hexdigest()
    certificate = json.loads(gzip.decompress(raw) if certificate_path.suffix == ".gz" else raw)
    word, programs = load_source(repo)
    check(certificate["source_base"] == BASE, "Certificate source base")
    check(certificate["word_sha256"] == MEMBERS["slots/local/CANONICAL-WORD.json.gz"], "Certificate word pin")
    check(certificate["programs_sha256"] == MEMBERS["slots/local/LOCAL-PROGRAMS.json.gz"], "Certificate program pin")
    for name, program in programs.items():
        scalar_endpoint(word, program, name == "backward")
    check_orientation_duality(word, programs)
    orientation = certificate["orientation"]
    native = rebuild_graph(word, programs[orientation], certificate)
    frames = word["frames"]
    spaces = list(map(frame_span, frames))
    lagrangians = list(map(lagrangian, frames))
    count = len(certificate["graph"]["labels"])
    distinct_pairs = {(before, after, rank) for _, _, before, after, rank, _, _ in native}
    for before, after, rank in distinct_pairs:
        check(len(gf2_basis(lagrangians[before] + lagrangians[after])) - 9 == rank, "Original native rank")
    summaries = []
    rank_checks = 0
    all_common = sorted(set.intersection(*(spaces[f] for f in word["center_frames"])))
    all_common = [a for a in all_common if a.bit_count() % 2]
    for entry in certificate["lines"]:
        line = entry["line"]
        check(line in all_common, "The gauge line is not odd and common to the centre frames")
        changed = [transform(rows, line) for rows in lagrangians]
        pair_delta = {}
        for before, after, rank in distinct_pairs:
            left = len(gf2_basis(changed[before] + lagrangians[after])) - 9
            right = len(gf2_basis(lagrangians[before] + changed[after])) - 9
            both = len(gf2_basis(changed[before] + changed[after])) - 9
            check(left == right and both == rank, "Gauge bit symmetry")
            lower, upper = (before, after) if len(frames[before]) <= len(frames[after]) else (after, before)
            nested = spaces[lower] <= spaces[upper]
            check(nested, "A native edge is not nested")
            good = line in spaces[upper] and all((line & u).bit_count() % 2 == 0 for u in frames[lower])
            check(left - rank == (-1 if good else 1), "Signed edge price differs from direct Lagrangian rank")
            pair_delta[before, after, rank] = left - rank
            rank_checks += 3
        deltas = [pair_delta[edge[2], edge[3], edge[4]] for edge in native]
        signed = Counter()
        for edge, delta in zip(native, deltas):
            if edge[0] != edge[1]:
                signed[tuple(sorted(edge[:2]))] += delta
        signed = {key: value for key, value in signed.items() if value}
        cover = entry["negative_cover"]
        check(len(set(cover)) == len(cover) and all(0 <= node < count for node in cover), "Branch cover nodes")
        check(all(u in cover or v in cover for (u, v), weight in signed.items() if weight < 0), "Negative edge cover")
        expected = {}
        scenarios = [(None, {})]
        for index in certificate["graph"]["centre_edges"]:
            u, v = native[index][:2]
            check(u != v, "A centre traversal is internally identified")
            scenarios.extend(((index, bit), {u: bit, v: 1 - bit}) for bit in (0, 1))
        for scenario, forcing in scenarios:
            for bits in product((0, 1), repeat=len(cover)):
                fixed = dict(zip(cover, bits))
                if any(node in fixed and fixed[node] != bit for node, bit in forcing.items()):
                    continue
                fixed.update(forcing)
                expected[scenario, bits] = fixed
        cases = {}
        zero_cut_rigidity = []
        for case in entry["cases"]:
            scenario = case["forced_centre_cross"]
            scenario = tuple(scenario) if scenario is not None else None
            key = scenario, tuple(case["branch"])
            check(key in expected and key not in cases, "Missing or repeated scenario")
            cases[key], rigidity = check_case(case, signed, native, deltas, count, expected[key])
            if rigidity is not None:
                zero_cut_rigidity.append(rigidity)
        check(cases.keys() == expected.keys(), "The exhaustive branch list is incomplete")
        ordinary = min(value for (scenario, _), value in cases.items() if scenario is None)
        forced = min(value for (scenario, _), value in cases.items() if scenario is not None)
        check(ordinary == entry["minimum_rank_delta"] and forced == entry["minimum_with_centre_cross"], "Reported minima")
        summaries.append(dict(line=line, certified_cases=len(cases), minimum_rank_delta=ordinary,
                              minimum_if_any_centre_traversal_changes=forced,
                              all_zero_cost_cuts_constant_on_native_components=zero_cut_rigidity))
    check(sha256(certificate_path.read_bytes()).hexdigest() == digest, "Certificate changed during review")
    return dict(
        status="PASS_INDEPENDENT_BOUNDARY_PAIRED_WIRE_GAUGE_CERTIFICATE",
        certificate=str(certificate_path.resolve()), certificate_sha256=digest,
        source_base=BASE, source_member_pins=MEMBERS,
        original_scalar_endpoint_columns=712, original_scalar_orientations=2,
        forward_backward_gauge_graph_isomorphism=True,
        native_events=len(native), native_event_kinds=dict(Counter(e[5] for e in native)),
        raw_segments=certificate["graph"]["raw_segments"], components=count,
        fixed_external_components=0, isolated_final_zero_components=8,
        direct_binary_rank_checks=rank_checks, common_odd_centre_lines=all_common,
        all_common_odd_lines_reviewed=sorted(x["line"] for x in summaries) == all_common,
        lines=summaries,
        total_flow_cut_cases=sum(x["certified_cases"] for x in summaries),
        proof_scope="A common odd line, two gauge values I and C_a, the old scalar schedule, and actual wire segments with paired boundary gauges.",
        native_rank_scope="Exact binary ranks. The symbolic boundary identity includes phases; no changed native recipe is admitted.",
        not_checked=["a changed native lowering", "whole-call hosting", "complete recursive moment", "selected cold replay"],
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.repo, args.certificate)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])
    print("lines=" + str(len(result["lines"])) + " flow_cut_cases=" + str(result["total_flow_cut_cases"]))
