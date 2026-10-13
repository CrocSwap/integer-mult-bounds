import argparse
import copy
import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVIDER = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck/"
PACKAGE = "research/complex-k492-owner-repair/"
SEED = 39
SUPERROOT = -1


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read_json(path):
    data = path.read_bytes()
    if path.suffix == ".gz":
        data = gzip.decompress(data)
    return json.loads(data)


def check_sources():
    manifest = read_json(HERE / "SOURCES.json")
    for name, pin in manifest["files"].items():
        data = (ROOT / name).read_bytes()
        if pin["encoding"] == "gzip-payload":
            data = gzip.decompress(data)
        require(hashlib.sha256(data).hexdigest() == pin["sha256"], f"source pin: {name}")
    word = read_json(ROOT / PROVIDER / "CANONICAL-WORD.json.gz")
    programs = read_json(ROOT / PROVIDER / "LOCAL-PROGRAMS.json.gz")
    spec = read_json(ROOT / PACKAGE / "data/SPEC.json")["providers"]["ck"]
    for name, value in (("CANONICAL-WORD.json.gz", word), ("LOCAL-PROGRAMS.json.gz", programs)):
        require(digest(value) == spec["artifact_semantic_sha256"][name], f"selected SPEC binding: {name}")
    for orientation, events in programs.items():
        require(digest(events) == spec["program_hashes"][orientation], "selected program binding")
    require((word["v"], word["R"], word["h"]) == (112, 492, 9), "CK geometry")
    return word, programs, spec


def add_cost(numerator, denominator=4):
    q = Fraction(numerator, denominator)
    if not q:
        return 0
    a, b = abs(q.numerator), q.denominator
    require(b & (b - 1) == 0, "non-dyadic addition")
    return 3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1


def compensation_rows(word):
    rows = {t: {} for t in range(112, 224)}
    for op, target, source, a, b, frame in word["compensation"]:
        require(op == "add" and target in rows and source >= 224 and frame == 0, "compensation interface")
        require(word["start"][target] == word["start"][source] == 0, "nonzero entrance in panel")
        value = 4 * Fraction(a, b)
        require(value.denominator == 1 and value != 0, "quarter-grid coefficient")
        require(source not in rows[target], "duplicate compensation cell")
        rows[target][source] = int(value)
    return rows


def difference(left, right, sign):
    return {s: value for s in left.keys() | right.keys()
            if (value := left.get(s, 0) - sign * right.get(s, 0))}


def row_cost(row):
    return sum(add_cost(value) for value in row.values())


def graph(rows):
    edges = [(row_cost(row), SUPERROOT, target, 0) for target, row in rows.items()]
    for a in rows:
        for b in rows:
            if a < b:
                for sign in (-1, 1):
                    edges.append((8 + row_cost(difference(rows[a], rows[b], sign)), a, b, sign))
    return edges


def kruskal(edges, targets):
    parent = {v: v for v in [SUPERROOT, *targets]}

    def root(v):
        while parent[v] != v:
            v = parent[v]
        return v

    def tie(edge):
        return hashlib.sha256(f"{SEED}:{tuple(edge)}".encode()).digest()

    selected = []
    for edge in sorted(edges, key=lambda e: (e[0], tie(e))):
        a, b = root(edge[1]), root(edge[2])
        if a != b:
            parent[a] = b
            selected.append(edge)
        if len(selected) == len(targets):
            break
    require(len(selected) == len(targets), "disconnected graph")
    return selected


def orient(selected, targets):
    adjacency = {v: [] for v in [SUPERROOT, *targets]}
    for weight, a, b, sign in selected:
        require(a in adjacency and b in adjacency and a != b, "invalid tree vertex")
        adjacency[a].append((b, sign, weight))
        adjacency[b].append((a, sign, weight))
    queue = [(SUPERROOT, None, 0, 0)]
    seen = {SUPERROOT}
    result = []
    for vertex, parent, _, depth in queue:
        for child, sign, _ in sorted(adjacency[vertex]):
            if child == parent:
                continue
            require(child not in seen, "tree cycle")
            seen.add(child)
            queue.append((child, vertex, sign, depth + 1))
            result.append((child, vertex, sign, depth))
    require(seen == set(adjacency) and len(selected) == len(targets), "incomplete tree")
    return result, adjacency


def cycle_certificate(edges, selected, targets):
    _, adjacency = orient(selected, targets)
    maxima = {}
    for start in adjacency:
        stack = [(start, None, 0)]
        for vertex, parent, maximum in stack:
            maxima[start, vertex] = maximum
            for child, _, weight in adjacency[vertex]:
                if child != parent:
                    stack.append((child, vertex, max(maximum, weight)))
    available = set(edges)
    require(all(tuple(edge) in available for edge in selected), "unpriced tree edge")
    slacks = [weight - maxima[a, b] for weight, a, b, _ in edges]
    require(min(slacks) >= 0, "nonminimal tree: improving fundamental cycle")
    return {"inequalities": len(slacks), "minimum_slack": min(slacks), "slacks_sha256": digest(slacks)}


def compile_panel(rows, selected):
    order, _ = orient(selected, rows)
    preparation = [["add", t, p, -sign, 1, 0] for t, p, sign, _ in reversed(order) if p != SUPERROOT]
    updates = []
    for target, parent, sign, _ in order:
        residual = rows[target] if parent == SUPERROOT else difference(rows[target], rows[parent], sign)
        for source, value in sorted(residual.items()):
            q = Fraction(value, 4)
            updates.append(["add", target, source, q.numerator, q.denominator, 0])
    restoration = [["add", t, s, -a, b, f] for _, t, s, a, b, f in reversed(preparation)]
    return preparation + updates + restoration, {
        "roots": sum(p == SUPERROOT for _, p, _, _ in order),
        "maximum_depth": max(depth for _, _, _, depth in order),
        "preparation_additions": len(preparation),
        "residual_additions": len(updates),
        "restoration_additions": len(restoration),
    }


def dual(gate):
    op, t, s, a, b, f = gate
    require(op == "add", "panel has a non-addition")
    return [op, s, t, -a, b, f]


def event(gate, backward):
    gate = list(gate)
    if gate[0] == "add":
        if backward:
            gate = dual(gate)
        _, t, s, a, b, frame = gate
        return ["scalar", ["add", ["L", t], ["L", s], a, b], frame]
    require(gate[0] == "scale", "unexpected precondition gate")
    _, t, a, b, frame = gate
    if backward:
        a, b = b, a
    return ["scalar", ["scale", ["L", t], a, b], frame]


def replace_panel(word, programs, replacement):
    result = {}
    first = 1 + len(word["precondition"])
    end = first + len(word["compensation"])
    for name, events in programs.items():
        backward = name == "backward"
        original = [event(g, backward) for g in word["precondition"] + word["compensation"]]
        require(events[:end] == [["phase", "zero_frame_precondition"], *original], "panel location")
        require(events[end] == ["phase", "entry_adapters"], "panel phase boundary")
        candidate = events[:first] + [event(g, backward) for g in replacement] + events[end:]
        require([e for e in events if e[0] != "scalar"] ==
                [e for e in candidate if e[0] != "scalar"], "non-scalar event changed")
        result[name] = candidate
    return result


def price_program(events):
    norms = {("L", r): Fraction(1) for r in range(716)}
    peak = Fraction(1)
    real = macros = 0
    profile = Counter()
    coefficients = set()
    for ev in events:
        if ev[0] in ("climb", "center"):
            profile[ev[-1]] += 1
        if ev[0] != "scalar":
            continue
        gate = ev[1]
        op, target = gate[0], tuple(gate[1])
        macros += 1
        if op == "clear":
            count = 1
            norms[target] = Fraction(0)
        elif op == "copy":
            count = 1
            norms[target] = norms[tuple(gate[2])]
        elif op == "scale":
            q = Fraction(gate[2], gate[3])
            a, b = abs(q.numerator), q.denominator
            require(a > 0 and a & (a - 1) == b & (b - 1) == 0, "invalid dyadic scale")
            count = abs(a.bit_length() - b.bit_length()) + int(q < 0)
            norms[target] *= abs(q)
        else:
            require(op == "add" and gate[1] != gate[2], "invalid scalar addition")
            source = tuple(gate[2])
            q = Fraction(gate[3], gate[4])
            require(q != 0, "zero macro")
            count = add_cost(q.numerator, q.denominator)
            coefficients.add(q)
            peak = max(peak, abs(q.numerator) * norms[source])
            norms[target] = norms.get(target, Fraction(0)) + abs(q) * norms[source]
        real += 2 * count
        peak = max(peak, norms[target])
    require(peak < 2**192, "prefix allowance exceeded")
    require(all(v == 0 for r, v in norms.items() if r[0] == "C"), "private center uncleared")
    return {"events": len(events), "scalar_macros": macros, "real_primitives": real,
            "prefix_l1_upper": str(peak),
            "prefix_bits_upper": peak.numerator.bit_length() - peak.denominator.bit_length() + 1,
            "paid_profile": dict(sorted(profile.items()))}, coefficients


def lower_add(q):
    operations = [("clear",)]
    for index, bit in enumerate(bin(abs(q.numerator))[2:]):
        if index:
            operations.append(("double",))
        if bit == "1":
            operations.append(("source_add",))
    operations.extend([("halve",)] * (q.denominator.bit_length() - 1))
    operations.extend([("accumulate", 1 if q > 0 else -1), ("clear",)])
    return operations


def replay_lowering(operations):
    work = [Fraction(0), Fraction(0), Fraction(1)]
    target = [Fraction(1), Fraction(0), Fraction(0)]
    for op in operations:
        if op[0] == "clear":
            work = [Fraction(0)] * 3
        elif op[0] == "double":
            work = [2 * x for x in work]
        elif op[0] == "halve":
            work = [x / 2 for x in work]
        elif op[0] == "source_add":
            work[1] += 1
        elif op[0] == "accumulate":
            target = [x + op[1] * y for x, y in zip(target, work)]
        else:
            raise ValueError("unknown primitive")
    return target, work


def check_lowerings(coefficients):
    for q in coefficients:
        operations = lower_add(q)
        require(len(operations) == add_cost(q.numerator, q.denominator), "primitive bill")
        target, work = replay_lowering(operations)
        require(target == [1, q, 0] and work == [0, 0, 0], "coefficient boundary")


def replay_panel(gates, columns=range(716)):
    columns = set(columns)
    rows = [{r: Fraction(1)} if r in columns else {} for r in range(716)]
    for op, target, source, a, b, frame in gates:
        require(op == "add" and target != source and frame == 0, "panel gate/frame")
        require(0 <= target < 716 and 0 <= source < 716, "panel register")
        q = Fraction(a, b)
        for column, value in list(rows[source].items()):
            new = rows[target].get(column, 0) + q * value
            if new:
                rows[target][column] = new
            else:
                rows[target].pop(column, None)
    return rows


def negative_controls(word, rows, edges, tree, panel, details):
    rejected = []
    expected = replay_panel(word["compensation"])

    def reject_panel(name, bad):
        try:
            actual = replay_panel(bad)
        except ValueError:
            rejected.append(name)
            return
        require(actual != expected, f"mutation accepted: {name}")
        rejected.append(name)

    prep = details["preparation_additions"]
    restore = details["restoration_additions"]
    reject_panel("missing_preparation", panel[prep:])
    require(replay_panel(panel[prep:], range(224, 716)) ==
            replay_panel(word["compensation"], range(224, 716)), "helper-only false-positive control")
    reject_panel("missing_restoration", panel[:-restore])
    reject_panel("reversed_preparation_order", list(reversed(panel[:prep])) + panel[prep:])
    reject_panel("reversed_restoration_order", panel[:-restore] + list(reversed(panel[-restore:])))
    bad = copy.deepcopy(panel)
    bad[prep][3] *= -1
    reject_panel("wrong_residual_sign", bad)
    bad = copy.deepcopy(panel)
    bad[0][-1] = 1
    reject_panel("nonzero_panel_frame", bad)
    bad = copy.deepcopy(panel)
    bad[prep][2] = bad[prep][1]
    reject_panel("aliased_source", bad)
    bad_tree = [(row_cost(row), SUPERROOT, target, 0) for target, row in rows.items()]
    try:
        cycle_certificate(edges, bad_tree, rows)
    except ValueError:
        rejected.append("nonminimal_star")
    else:
        raise ValueError("nonminimal star accepted")
    try:
        cycle_certificate(edges, tree[:-1] + [tree[0]], rows)
    except ValueError:
        rejected.append("disconnected_cyclic_recipe")
    else:
        raise ValueError("invalid tree accepted")
    for name, operations in (("missing_initial_work_clear", lower_add(Fraction(3, 4))[1:]),
                             ("missing_final_work_clear", lower_add(Fraction(3, 4))[:-1])):
        target, work = replay_lowering(operations)
        require(target != [1, Fraction(3, 4), 0] or work != [0, 0, 0], f"mutation accepted: {name}")
        rejected.append(name)
    return rejected


def native_replay(word, programs):
    with tempfile.TemporaryDirectory(prefix="ck-target-forest-") as directory:
        output = Path(directory)
        (output / "CANONICAL-WORD.json.gz").write_bytes(gzip.compress(canonical(word), mtime=0))
        for script in ("hpe_emit_local.py", "hpe_audit_local.py"):
            run = subprocess.run([sys.executable, "-I", "-B", str(ROOT / PACKAGE / "code" / script), directory],
                                 check=True, capture_output=True, text=True)
            print(run.stdout.strip(), flush=True)
        require(read_json(output / "LOCAL-PROGRAMS.json.gz") == programs, "native emission differs")
        receipt = read_json(output / "INDEPENDENT-LOCAL-REPLAY.json")
        return {"status": receipt["status"], "local": receipt["local"],
                "negative_controls_rejected": receipt["negative_controls_rejected"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    arguments = parser.parse_args()
    word, programs, spec = check_sources()
    rows = compensation_rows(word)
    edges = graph(rows)
    tree = kruskal(edges, rows)
    cycles = cycle_certificate(edges, tree, rows)
    panel, details = compile_panel(rows, tree)
    require(replay_panel(panel) == replay_panel(word["compensation"]), "forward panel boundary")
    require(replay_panel([dual(g) for g in panel]) ==
            replay_panel([dual(g) for g in word["compensation"]]), "inverse-transpose panel boundary")
    candidate = replace_panel(word, programs, panel)
    bills = {}
    coefficients = set()
    for name in ("forward", "backward"):
        before, old_coefficients = price_program(programs[name])
        after, new_coefficients = price_program(candidate[name])
        prior = spec["complete_contract"]["local"][name]
        require(before["real_primitives"] == prior["real_component_primitives"] and
                before["prefix_l1_upper"] == prior["prefix_l1"], "baseline recount differs")
        require(before["paid_profile"] == after["paid_profile"], "recursive profile changed")
        bills[name] = {"before": before, "after": after,
                       "real_saved": before["real_primitives"] - after["real_primitives"]}
        coefficients |= old_coefficients | new_coefficients
    check_lowerings(coefficients)
    controls = negative_controls(word, rows, edges, tree, panel, details)
    modified_word = dict(word, compensation=panel)
    native = native_replay(modified_word, candidate)
    for name in bills:
        require(native["local"][name]["prefix_l1_upper"] == bills[name]["after"]["prefix_l1_upper"],
                "native prefix differs")
    cost = sum(edge[0] for edge in tree)
    require(sum(add_cost(g[3], g[4]) for g in panel) == cost, "complete forest bill")
    recipe = {"assignment_seed": SEED, "tree_edges": tree, "compensation": panel}
    result = {"status": "PASS_CK_SIGNED_TARGET_FOREST", "base_commit": read_json(HERE / "SOURCES.json")["base_commit"],
              "assignment_seed": SEED, "domain": {"targets": len(rows), "signed_pair_edges": len(edges) - len(rows),
                                                  "root_edges": len(rows), "edge_prices_sha256": digest(edges)},
              "recipe_sha256": digest(recipe), "details": details, "cycle_certificate": cycles,
              "forest_class_complex_primitive_floor": cost,
              "compensation_before": len(word["compensation"]), "compensation_after": len(panel),
              "scalar_bills": bills, "coefficient_lowerings": len(coefficients),
              "boundary_columns_per_orientation": 716, "negative_controls_rejected": controls,
              "native_replay": native, "kappa": "unchanged"}
    if arguments.record:
        (HERE / "RECIPE.json").write_bytes(canonical(recipe) + b"\n")
        (HERE / "EXPECTED.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(canonical(recipe) == canonical(read_json(HERE / "RECIPE.json")), "recipe differs")
        require(canonical(result) == canonical(read_json(HERE / "EXPECTED.json")), "expected certificate differs")
    run = subprocess.run([sys.executable, "-I", "-B", str(HERE / "independent.py")],
                         check=True, capture_output=True, text=True)
    print(run.stdout.strip())
    print(f"PASS_CK_SIGNED_TARGET_FOREST compensation={len(word['compensation'])}->{len(panel)} "
          f"saved={bills['forward']['real_saved']}/{bills['backward']['real_saved']} "
          f"forest_floor={cost} columns=716 controls={len(controls)}+{len(native['negative_controls_rejected'])} kappa=unchanged")


if __name__ == "__main__":
    main()
