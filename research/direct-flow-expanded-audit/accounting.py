"""Exact counted call DAG for the nested-width compiler.

Dillon with OpenAI Codex assistance. Apache-2.0.
No count is recovered from the rank-mass identity being audited.
"""
from collections import Counter


def need(condition, message):
    if not condition:
        raise ValueError(message)


def inventory_mass(items):
    return sum(rank * count for rank, count in items.items())


def validate_flow(flow, targets, paid, n):
    """Check the local premises before recursively expanding an invoice."""
    s, e, units = flow["sources"], flow["exits"], flow["units_by_column"]
    need(bool(s), "nonempty source inventory")
    for hist in (s, e, units):
        need(all(type(k) is int and type(v) is int and k > 0 and v > 0
                 for k, v in hist.items()), "positive integer inventory")
    need(all(k <= n for k in s), "source rank fits")
    need(all(k < n for k in e), "strict exit descent")
    need(flow["units"] == sum(units.values()), "local unit census")
    need(flow["column_mass"] == inventory_mass(units), "local column census")
    delta = inventory_mass(targets) - inventory_mass(paid)
    need(inventory_mass(s) - inventory_mass(e) == delta * flow["column_mass"],
         "local rank mass")
    w, p = sum(targets.values()), sum(paid.values())
    need(type(flow["matched_jobs"]) is int and flow["matched_jobs"] >= 0,
         "nonnegative integer matched jobs")
    need(sum(s.values()) + flow["matched_jobs"] == w * flow["units"],
         "all target slots accounted for")
    need(sum(e.values()) + flow["matched_jobs"] == p * flow["units"],
         "all paid slots accounted for")
    need(sum(s.values()) + sum(e.values()) + 2 * flow["matched_jobs"]
         == (w + p) * flow["units"], "local slot census")
    need(flow["routing_slots"] == sum(s.values()) + sum(e.values())
         + (w + p) * flow["units"], "local routing convention")


def compile_dag(targets, paid, maximum, make_flow):
    """Build each smaller supplier once, retaining every edge multiplicity.

    A call node denotes one whole batch of width B[rank]. Reusing its stored
    description does not merge its physical invocation instances.
    """
    m = max(targets)
    delta = inventory_mass(targets) - inventory_mass(paid)
    nodes, counts, flows = [], [], {}
    for n in range(maximum + 1):
        if n < m:
            nodes.append({"rank": n, "width": 1, "replication": 0,
                          "raw": [], "calls": [], "base_leaves": n,
                          "local_routes": 0})
            counts.append({"B": 1, "P": n, "U": 0, "Q": 0, "routes": 0})
            continue
        flow = make_flow(targets, paid, n)
        validate_flow(flow, targets, paid, n)
        flows[n] = flow
        replication = counts[n-1]["B"]
        width = replication * sum(flow["sources"].values())
        raw = [(column, replication * instances)
               for column, instances in sorted(flow["units_by_column"].items())]
        calls = []
        for kind, hist in (("complement", flow["sources"]), ("exit", flow["exits"])):
            for rank, amount in sorted(hist.items()):
                child = n - rank if kind == "complement" else rank
                need(0 <= child < n, "strict recursive descent")
                jobs = replication * amount
                batches, remainder = divmod(jobs, counts[child]["B"])
                need(remainder == 0, "integer child batches")
                calls.append({"kind": kind, "rank": child, "jobs": jobs,
                              "batches": batches})
        node = {"rank": n, "width": width, "replication": replication,
                "raw": raw, "calls": calls, "base_leaves": 0,
                "local_routes": replication * flow["routing_slots"]}
        value = {"B": width, "P": 0, "U": sum(v for _, v in raw),
                 "Q": sum(c * v for c, v in raw), "routes": node["local_routes"]}
        for call in calls:
            for key in ("P", "U", "Q", "routes"):
                value[key] += call["batches"] * counts[call["rank"]][key]
        need(width % counts[n-1]["B"] == 0, "nested widths")
        check_expanded(n, value, delta, sum(targets.values()) + sum(paid.values()))
        nodes.append(node)
        counts.append(value)
    return nodes, counts, flows


def check_expanded(n, value, delta, slots_per_unit):
    need(all(type(v) is int and v >= 0 for v in value.values()),
         "nonnegative expanded counts")
    need(value["B"] > 0, "positive expanded width")
    need(value["B"] * n - value["P"] == delta * value["Q"],
         "expanded rank mass")
    need(value["U"] <= value["Q"], "positive raw columns")
    need(value["routes"] <= 2 * slots_per_unit * value["U"],
         "expanded routing bound")
    if delta > 0:
        need(delta * value["Q"] <= value["B"] * n,
             "positive-surplus instance bound")


def require_positive_surplus_bound(delta):
    need(delta > 0, "positive surplus required for division bound")


def reverse_expand(nodes, rank):
    """Independent evaluation: push invocation weights from root to leaves.

    Unlike bottom-up memoization, this computes a census of all invocation
    ranks first, then reads primitive records. It never uses the mass formula.
    """
    invocations = Counter({rank: 1})
    result = {"B": nodes[rank]["width"], "P": 0, "U": 0, "Q": 0, "routes": 0}
    for n in range(rank, -1, -1):
        weight = invocations[n]
        node = nodes[n]
        result["P"] += weight * node["base_leaves"]
        result["routes"] += weight * node["local_routes"]
        for column, copies in node["raw"]:
            result["U"] += weight * copies
            result["Q"] += weight * copies * column
        for call in node["calls"]:
            need(call["rank"] < n, "reverse expansion descent")
            invocations[call["rank"]] += weight * call["batches"]
    return result, dict(sorted((k, v) for k, v in invocations.items() if v))
