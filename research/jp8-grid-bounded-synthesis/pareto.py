#!/usr/bin/env python3
"""Exact instruction/source-read Pareto audit of the same 49 bounded graphs.

Prepared for Philipp (@mightyOil), with substantial OpenAI Codex assistance.
Apache-2.0. No emitted circuit is changed. The optional weighted-cost
diagnostic is algebraic sensitivity, not a physical source-read price.

Run with Python 3.11+: python3 -I -B research/jp8-grid-bounded-synthesis/pareto.py
The label search is certified by complete state coverage, rational witness
replay, pairwise nondomination and every-edge local closure. The checker
constructs successors independently with Fraction arithmetic. It does not
trust the search's integer successor table or pruning decisions.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import heapq
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROGRAM = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/jp8/LOCAL-PROGRAMS.json.gz"
OPERATIONS = ("double", "halve", "add", "subtract", "negate")
T, S, W = ("T", 0), ("S", 0), ("W", 0)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def domain(a, d):
    need(type(a) is int and 1 <= a <= 127, "Pareto numerator domain")
    need(type(d) is int and d in (1, 2, 4, 8, 16), "Pareto denominator domain")
    need(Q(a, d).numerator == a and (a, d) != (1, 1), "Pareto reduced nonunit domain")
    return a*d


def successors(state, d, bound):
    """Search edges retain differently priced operations to the same state."""
    edges = [(2*state, "double", 0), (state+d, "add", 1),
             (state-d, "subtract", 1), (-state, "negate", 0)]
    if state % 2 == 0:
        edges.append((state//2, "halve", 0))
    return [(nxt, op, reads) for nxt, op, reads in edges if abs(nxt) <= bound]


def covered(pair, pairs):
    return any(x <= pair[0] and y <= pair[1] for x, y in pairs)


def synthesize(a, d):
    """Label-setting search; positive instruction cost makes cycle pruning safe."""
    bound = domain(a, d)
    labels = {state: {} for state in range(-bound, bound+1)}
    labels[d][(0, 0)] = ()
    queue = [(0, 0, d, ())]
    while queue:
        steps, reads, state, word = heapq.heappop(queue)
        if labels[state].get((steps, reads)) != word:
            continue
        for nxt, operation, increment in successors(state, d, bound):
            pair = steps+1, reads+increment
            if covered(pair, labels[nxt]):
                continue
            labels[nxt] = {old: path for old, path in labels[nxt].items()
                           if not (pair[0] <= old[0] and pair[1] <= old[1])}
            path = word+(operation,)
            labels[nxt][pair] = path
            heapq.heappush(queue, (*pair, nxt, path))
    return {"bound": bound, "labels": labels}


def rational_step(value, operation):
    if operation == "double": return value*2
    if operation == "halve": return value/2
    if operation == "negate": return -value
    if operation == "add": return value+1
    if operation == "subtract": return value-1
    raise ValueError("Pareto unknown operation")


def witness(a, d, word):
    value, reads = Q(1), 0
    for operation in word:
        value = rational_step(value, operation)
        need(abs(value) <= a, "Pareto witness magnitude")
        need(d % value.denominator == 0, "Pareto witness grid")
        reads += operation in ("add", "subtract")
    return int(value*d), reads


def validate(a, d, certificate):
    """A witnessed, closed antichain proves all Pareto labels without searching.

    Any finite walk is dominated by a stored label, by induction from (0,0)
    using local closure. Every stored label has an actual witness. Thus the
    two reachable upward closures agree; pairwise antichains give the exact
    Pareto sets. This checks all prefixes of every witness and every edge.
    """
    bound = domain(a, d)
    need(type(certificate["bound"]) is int and certificate["bound"] == bound,
         "Pareto declared bound")
    labels = certificate["labels"]
    need(set(labels) == set(range(-bound, bound+1)), "Pareto state coverage")
    need(labels[d].get((0, 0)) == (), "Pareto initial label")
    for state, costs in labels.items():
        need(type(state) is int and costs, "Pareto empty or invalid state")
        for pair, word in costs.items():
            need(len(pair) == 2 and all(type(x) is int and x >= 0 for x in pair),
                 "Pareto label type")
            need(pair[0] == len(word), "Pareto witness instruction count")
            end, reads = witness(a, d, word)
            need(reads == pair[1], "Pareto witness source-read count")
            need(end == state, "Pareto witness endpoint")
        for pair in costs:
            need(not covered(pair, [other for other in costs if other != pair]),
                 "Pareto dominated state label")
    edge_obligations = 0
    for state, costs in labels.items():
        for operation in OPERATIONS:
            value = rational_step(Q(state, d), operation)
            if abs(value) > a or d % value.denominator:
                continue
            target = int(value*d)
            increment = int(operation in ("add", "subtract"))
            for steps, reads in costs:
                need(covered((steps+1, reads+increment), labels[target]),
                     "Pareto edge closure")
                edge_obligations += 1
    return edge_obligations


def endpoint_frontier(a, labels):
    result = {}
    for goal in (a, -a):
        for pair, word in sorted(labels[goal].items()):
            if not covered(pair, result):
                result = {old: path for old, path in result.items()
                          if not (pair[0] <= old[0] and pair[1] <= old[1])}
                result[pair] = (goal, word)
    return [{"preparation_instructions": steps, "preparation_source_reads": reads,
             "macro_instructions": steps+3, "macro_source_reads": reads+1,
             "end_sign": 1 if goal > 0 else -1, "operations": list(word)}
            for (steps, reads), (goal, word) in sorted(result.items())]


def macro_word(word, sign=1):
    result = [("copy", W, S)]
    result.extend((op, W, S) if op in ("add", "subtract") else (op, W) for op in word)
    return result+[("add" if sign > 0 else "subtract", T, W), ("clear", W)]


def macro_stats(word, a, d):
    need(word[0] == ("copy", W, S), "Pareto macro initial copy")
    need(word[-1] == ("clear", W) and word[-2] in (("add", T, W), ("subtract", T, W)),
         "Pareto macro paid boundary")
    reads = sum(len(op) == 3 and op[0] in ("copy", "add", "subtract") and op[2] == S
                for op in word)
    value, grid, magnitude = Q(1), True, True
    for op in word[1:-2]:
        need(op[1] == W, "Pareto comparator writes another register")
        need((len(op) == 3 and op[2] == S) if op[0] in ("add", "subtract") else len(op) == 2,
             "Pareto comparator source operand")
        value = rational_step(value, op[0])
        grid &= d % value.denominator == 0
        magnitude &= abs(value) <= a
    need(value*(1 if word[-2][0] == "add" else -1) == Q(a, d),
         "Pareto comparator endpoint")
    return {"instructions": len(word), "source_reads": reads,
            "within_grid": grid, "within_magnitude": magnitude}


def pinned_inputs():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    payload = gzip.decompress((ROOT / PROGRAM).read_bytes())
    need(hashlib.sha256(payload).hexdigest() == pins["files"][PROGRAM]["sha256"],
         "Pareto program source pin")
    for name in ("vendor/pr837/lower.py", "vendor/pr837/vendor/pr696_lower.py"):
        need(hashlib.sha256((HERE / name).read_bytes()).hexdigest() == pins["vendored"][name]["sha256"],
             "Pareto comparator source pin")
    spec = importlib.util.spec_from_file_location("pareto_pinned_horner", HERE / "vendor/pr837/lower.py")
    horner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(horner)
    programs = json.loads(payload)
    counts = {orientation: Counter(abs(Q(e[1][3], e[1][4])) for e in events
              if e[0] == "scalar" and e[1][0] == "add") for orientation, events in programs.items()}
    need(set(counts) == {"forward", "backward"}, "Pareto orientation coverage")
    return counts, horner


def negative_controls():
    certificate = synthesize(5, 2)
    validate(5, 2, certificate)
    mutations = {}
    missing = deepcopy(certificate)
    del missing["labels"][5][(4, 1)]
    mutations["missing_lower_read_tradeoff"] = (missing, "Pareto edge closure")
    forged = deepcopy(certificate)
    forged["labels"][5][(3, 1)] = forged["labels"][5].pop((3, 2))
    mutations["forged_source_reads"] = (forged, "Pareto witness source-read count")
    wrong = deepcopy(certificate)
    wrong["bound"] += 1
    mutations["wrong_magnitude_bound"] = (wrong, "Pareto declared bound")
    rejected = {}
    for name, (bad, reason) in mutations.items():
        try:
            validate(5, 2, bad)
        except ValueError as error:
            need(str(error) == reason, "Pareto control wrong rejection: "+name)
            rejected[name] = reason
        else:
            raise ValueError("Pareto accepted control: "+name)
    try:
        macro_stats(macro_word(("halve", "add", "add"))[1:], 5, 2)
    except ValueError as error:
        need(str(error) == "Pareto macro initial copy", "Pareto copy control wrong rejection")
        rejected["uncharged_initial_copy"] = str(error)
    else:
        raise ValueError("Pareto accepted uncharged copy")
    return rejected


def sensitivity(selected, counts):
    """Exact lower envelope for an explicitly hypothetical nonnegative price."""
    breaks = set()
    for row in selected:
        left, right = row["frontier"]
        breaks.add(Q(right["macro_instructions"]-left["macro_instructions"],
                     left["macro_source_reads"]-right["macro_source_reads"]))
    breaks = sorted(breaks)
    intervals = []
    for lower, upper in zip([Q(0)]+breaks, breaks+[None]):
        price = (lower+upper)/2 if upper is not None else lower+1
        deltas = {o: [0, 0] for o in sorted(counts)}
        chosen = {}
        for row in selected:
            point = min(row["frontier"], key=lambda x:
                        x["macro_instructions"]+price*x["macro_source_reads"])
            chosen[row["coefficient"]] = [point["macro_instructions"], point["macro_source_reads"]]
            base = row["comparators"]["binary-forward"]
            for orientation, counter in counts.items():
                n = 2*counter[Q(row["coefficient"])]
                deltas[orientation][0] += n*(point["macro_instructions"]-base["instructions"])
                deltas[orientation][1] += n*(point["macro_source_reads"]-base["source_reads"])
        intervals.append({"lower": str(lower), "upper": str(upper) if upper is not None else None,
                          "delta_instructions_source_reads_vs_696": deltas, "choices": chosen})
    current_deltas = intervals[0]["delta_instructions_source_reads_vs_696"]
    need(current_deltas["forward"] == current_deltas["backward"], "Pareto current orientation sensitivity")
    primitive_delta, read_delta = current_deltas["forward"]
    need(primitive_delta < 0 < read_delta, "Pareto current tradeoff sign")
    return {"model": "instructions + p * source_reads; p >= 0 is hypothetical additional overhead",
            "physical_price_claimed": False, "breakpoints": list(map(str, breaks)),
            "endpoint_rule": "Intervals describe interiors; adjacent choices tie at a breakpoint; p=0 uses the first.",
            "intervals": intervals,
            "current_schedule_gain_vs_696": f"{-primitive_delta} - {read_delta}*p per orientation",
            "current_schedule_break_even": str(Q(-primitive_delta, read_delta)),
            "lower_read_15_over_4_prior_art": "Bounded signed-Horner word credited to PR734; no new construction claim."}


def verify(entries):
    """Return a deterministic receipt; accepts the existing entry list or map."""
    values = list(entries.values()) if isinstance(entries, dict) else list(entries)
    counts, horner = pinned_inputs()
    expected = {q for counter in counts.values() for q in counter
                if q != 1 and q.numerator <= 127 and q.denominator <= 16}
    supplied = [Q(e["numerator"], e["denominator"]) for e in values]
    need(len(supplied) == len(set(supplied)) == 49 and set(supplied) == expected,
         "Pareto coefficient coverage")
    summaries, selected = [], []
    totals = Counter()
    for entry in sorted(values, key=lambda x: Q(x["numerator"], x["denominator"])):
        a, d = entry["numerator"], entry["denominator"]
        certificate = synthesize(a, d)
        obligations = validate(a, d, certificate)
        labels = certificate["labels"]
        frontier = endpoint_frontier(a, labels)
        end, reads = witness(a, d, entry["operations"])
        need(type(entry["end_sign"]) is int and entry["end_sign"] in (-1, 1) and
             end == entry["end_sign"]*a, "Pareto current witness endpoint")
        need(type(entry["preparation_steps"]) is int and entry["preparation_steps"] == len(entry["operations"]),
             "Pareto current instruction count")
        need((len(entry["operations"]), reads) ==
             (frontier[0]["preparation_instructions"], frontier[0]["preparation_source_reads"]),
             "Pareto current shortest witness does not minimize reads")
        for point in frontier:
            stats = macro_stats(macro_word(point["operations"], point["end_sign"]), a, d)
            need((stats["instructions"], stats["source_reads"]) ==
                 (point["macro_instructions"], point["macro_source_reads"]), "Pareto macro accounting")
        serialized = [[state, [[*pair, list(word)] for pair, word in sorted(costs.items())]]
                      for state, costs in sorted(labels.items())]
        summary = {"coefficient": str(Q(a, d)), "vertices": len(labels),
                   "labels": sum(map(len, labels.values())), "edge_label_obligations": obligations,
                   "label_certificate_sha256": hashlib.sha256(canonical(serialized)).hexdigest(),
                   "macro_frontier": [[p["macro_instructions"], p["macro_source_reads"]] for p in frontier]}
        summaries.append(summary)
        for key in ("vertices", "labels", "edge_label_obligations"):
            totals[key] += summary[key]
        op = ["add", list(T), list(S), a, d]
        comparators = {name: macro_stats(word, a, d) for name, word in horner.candidates(op).items()}
        baseline = comparators["binary-forward"]
        need(baseline["source_reads"] == a.bit_count() and baseline["instructions"] ==
             2+(a.bit_length()-1)+a.bit_count()+(d.bit_length()-1), "Pareto binary accounting")
        is_selected = frontier[0]["macro_instructions"] < min(x["instructions"] for x in comparators.values())
        need(entry["strict_horner_improvement"] is is_selected, "Pareto selected coefficient flag")
        if is_selected:
            selected.append({"coefficient": str(Q(a, d)), "frontier": frontier, "comparators": comparators,
                             "occurrences": {o: c[Q(a, d)] for o, c in sorted(counts.items())}})
    need(len(selected) == 7 and all(len(row["frontier"]) == 2 for row in selected) and
         all(len(row["macro_frontier"]) == (2 if row["coefficient"] in
             {s["coefficient"] for s in selected} else 1) for row in summaries), "Pareto frontier inventory")
    aggregate = {}
    for orientation, counter in sorted(counts.items()):
        costs = {name: [0, 0] for name in ("original-binary", "binary-forward", "naf-forward",
                 "binary-reverse", "naf-reverse", "best-four-stable", "best-four-min-read-cost-tie", "current")}
        for row in selected:
            n = 2*counter[Q(row["coefficient"])]
            pairs = {k: [v["instructions"], v["source_reads"]] for k, v in row["comparators"].items()}
            pairs["original-binary"] = [pairs["binary-forward"][0]+1, pairs["binary-forward"][1]]
            best = min(row["comparators"], key=lambda k: row["comparators"][k]["instructions"])
            pairs["best-four-stable"] = pairs[best]
            minimum = min(v["instructions"] for v in row["comparators"].values())
            pairs["best-four-min-read-cost-tie"] = [minimum, min(v["source_reads"] for v in
                row["comparators"].values() if v["instructions"] == minimum)]
            pairs["current"] = [row["frontier"][0]["macro_instructions"], row["frontier"][0]["macro_source_reads"]]
            for name, pair in pairs.items():
                costs[name][0] += n*pair[0]
                costs[name][1] += n*pair[1]
        aggregate[orientation] = costs
    return {"status": "PASS_JP8_PARETO_SOURCE_READS", "coefficients": len(summaries),
            "cost_coordinates": ["primitive_instructions", "reads_of_unchanged_macro_source"],
            "common_nonunit_macro_overhead": [3, 1], "state_totals": dict(totals),
            "all_submitted_shortest_witnesses_minimize_reads": True, "graphs": summaries,
            "selected_frontiers": selected, "selected_occurrence_totals_both_real_components": aggregate,
            "hypothetical_sensitivity": sensitivity(selected, counts), "negative_controls": negative_controls(),
            "emitted_circuits_changed": False}


if __name__ == "__main__":
    certificate = json.loads((HERE / "CERTIFICATE.json").read_text())
    print(json.dumps(verify(certificate["entries"]), indent=2, sort_keys=True))
