#!/usr/bin/env python3
"""Check a source-bound primal/dual certificate without running the optimizer.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
Apache-2.0. This is a finite communication relaxation, not a circuit certificate.
"""
from collections import Counter, defaultdict, deque
from functools import lru_cache
from fractions import Fraction
import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_price_model", HERE / "model.py")
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
need, Invalid = model.need, model.Invalid


def certificate(graph, solution):
    """Ordinary flow conservation and LP weak duality, independently of solve.py."""
    need(set(solution) == {"value", "cost", "flow", "potential", "frontier", "graph_sha256"},
         "certificate fields")
    need(solution["graph_sha256"] == graph.fingerprint(), "graph binding")
    flow, potential = solution["flow"], solution["potential"]
    need(len(flow) == len(graph.edges) and len(potential) == len(graph.labels), "certificate lengths")
    need(all(type(x) is int for x in flow + potential), "integer certificate")
    value, stated_cost = solution["value"], solution["cost"]
    need(type(value) is type(stated_cost) is int, "integer value/cost")
    balance = [0] * len(graph.labels)
    residual = [[] for _ in graph.labels]
    nonpaid_in = [0] * len(graph.labels)
    nonpaid_out = [0] * len(graph.labels)
    cost = penalty = 0
    negative = []
    for i, ((u, v, cap, price, kind), f) in enumerate(zip(graph.edges, flow)):
        need(0 <= f <= cap, "flow capacity")
        balance[u] -= f
        balance[v] += f
        cost += f * price
        reduced = price + potential[u] - potential[v]
        if f < cap:
            need(reduced >= 0, "forward reduced cost")
            residual[u].append(v)
        if f:
            need(reduced <= 0, "reverse reduced cost")
            residual[v].append(u)
        penalty += cap * max(0, -reduced)
        if reduced < 0:
            negative.append([i, cap, -reduced])
        if kind != "paid":
            nonpaid_out[u] += f
            nonpaid_in[v] += f
    need(balance[:2] == [-value, value] and not any(balance[2:]), "flow conservation")
    need(cost == stated_cost, "stated cost")
    gap = potential[1] - potential[0]
    need(value * gap - penalty == cost, "primal/dual equality")
    # These are the pre/post-cut occupancy bounds in the lifting proof.
    for v, label in enumerate(graph.labels[2:], 2):
        need(nonpaid_in[v] <= label[2] and nonpaid_out[v] <= label[2], "frame-class occupancy")
    reached = {0}
    queue = deque([0])
    while queue:
        for v in residual[queue.popleft()]:
            if v not in reached:
                reached.add(v)
                queue.append(v)
    need(1 not in reached, "flow is not maximum")
    return {"value": value, "cost": cost, "dual_gap": gap,
            "capacity_penalty": penalty, "negative_arcs": negative}


def path_prices(graph, solution):
    """Extract integral paths, proving feasible upper bounds for every flow size."""
    left = solution["flow"].copy()
    adjacency = [[] for _ in graph.labels]
    for i, e in enumerate(graph.edges):
        adjacency[e[0]].append(i)
    prices = []
    for _ in range(solution["value"]):
        parent = {0: None}
        queue = deque([0])
        while queue and 1 not in parent:
            for i in adjacency[queue.popleft()]:
                v = graph.edges[i][1]
                if left[i] and v not in parent:
                    parent[v] = i
                    queue.append(v)
        need(1 in parent, "path decomposition")
        v, price = 1, 0
        while v:
            i = parent[v]
            left[i] -= 1
            price += graph.edges[i][3]
            v = graph.edges[i][0]
        prices.append(price)
    need(not any(left), "unreported flow circulation")
    return sorted(prices)


@lru_cache(None)
def basis(vectors):
    """Independent Gaussian-elimination frame oracle (model.py enumerates spans)."""
    rows = [0] * 9
    for v in vectors:
        need(type(v) is int and 0 <= v < 512, "reference frame vector")
        while v:
            i = v.bit_length() - 1
            if rows[i]:
                v ^= rows[i]
            else:
                rows[i] = v
                break
    for i in range(9):
        if rows[i]:
            for j in range(i + 1, 9):
                if rows[j] >> i & 1:
                    rows[j] ^= rows[i]
    return tuple(v for v in rows if v)


@lru_cache(None)
def frame_key(b):
    values = [0]
    for v in b:
        values += [x ^ v for x in values]
    return hex(sum(1 << x for x in values))


def expanded_dual(w, graph, potentials):
    """Lift the potential to PR2163's full per-register, per-layer network.

    No compressed edge list is used. Rebuild all 1427 frame/liveness layers
    with Gaussian elimination, then check the potentials on every unit edge.
    Hub/entry/exit arcs have zero reduced cost by construction; source/sink
    and nested arcs are explicitly checked. This gives a separate lower-bound
    check directly on the uncompressed model.
    """
    labels = defaultdict(dict)
    for i, label in enumerate(graph.labels[2:], 2):
        c, key, _ = label
        need(key not in labels[c], "duplicate class epoch")
        labels[c][key] = potentials[i]
    current = dict(labels[0])
    state = {r: basis(tuple(f)) for r, f in w["initial_frames"].items()}
    private = None
    births = 0
    penalty = 0
    negative = []
    units = len(state)
    layers = 1
    for r, b in state.items():
        if r.startswith("X"):
            need(current[frame_key(b)] <= potentials[0], "expanded source arc")

    def paid_arcs():
        fs = sorted(set(state.values()))
        count = 0
        for i, a in enumerate(fs):
            for b in fs[i + 1:]:
                joined = basis(a + b)
                if joined in (a, b):
                    gap = abs(len(a) - len(b))
                    pa, pb = current[frame_key(a)], current[frame_key(b)]
                    need(gap >= abs(pa - pb), "expanded paid arc")
                    count += 2
        return count

    checked_paid = None
    for index, e in enumerate(w["program"]):
        if index == model.CUT:
            checked_paid = paid_arcs()
        kind = e[0]
        if kind in ("add", "copy"):
            dst = private if e[1] == "C" else e[1]
            src = private if e[2] == "C" else e[2]
            need(state[dst] == state[src] == basis(tuple(e[-1])), "reference common frame")
            continue
        previous = state.copy()
        old_potential = current.copy()
        if kind == "transport":
            r = private if e[1] == "C" else e[1]
            a, b = basis(tuple(e[2])), basis(tuple(e[3]))
            need(state[r] == a and basis(a + b) in (a, b), "reference transport")
            need(e[4] == abs(len(a) - len(b)), "reference rank")
            state[r] = b
        elif kind == "zero":
            need(private is None, "reference lifetime birth")
            private = f"C#{births}"
            births += 1
            state[private] = basis(tuple(e[2]))
        elif kind == "erase":
            need(private in state and state[private] == basis(tuple(e[2])), "reference lifetime end")
            del state[private]
            private = None
        else:
            raise Invalid("reference event")
        current.update(labels[index + 1])
        for r, b in state.items():
            key = frame_key(b)
            need(key in current, "missing class potential")
            if r in previous:
                change = current[key] - old_potential[frame_key(previous[r])]
                if change > 0:
                    penalty += change
                    negative.append([index + 1, r, change])
        units += len(state)
        layers += 1
    for r, b in state.items():
        need(b == basis(tuple(w["final_frames"][r])), "reference final frames")
        if r.startswith("Y"):
            need(current[frame_key(b)] >= potentials[1], "expanded sink arc")
    need(checked_paid == graph.facts["paid_edges"], "expanded paid edge inventory")
    return {"layers": layers, "register_unit_edges": units + 104,
            "paid_arcs": checked_paid, "capacity_penalty": penalty,
            "negative_unit_edges": negative}


def verify(path=None, source=None):
    w = model.load_source(source)
    graph = model.build(w)
    saved = json.loads((Path(path) if path else HERE / "CERTIFICATE.json").read_text())
    need(set(saved) == {"schema_version", "source_sha256", "facts", "baseline", "paid"}, "receipt fields")
    need(type(saved["schema_version"]) is int and saved["schema_version"] == 1, "schema")
    need(saved["source_sha256"] == model.SOURCE_HASH, "receipt source")
    need(model.canonical(saved["facts"]) == model.canonical(graph.facts), "receipt facts")
    baseline_graph = model.build(w, paid=False)
    baseline = certificate(baseline_graph, saved["baseline"])
    paid = certificate(graph, saved["paid"])
    prices = path_prices(graph, saved["paid"])
    frontier = [[0, 0]]
    cost = 0
    for f, price in enumerate(prices, 1):
        cost += price
        need(cost == max(0, paid["dual_gap"] * f - paid["capacity_penalty"]), "frontier duality")
        frontier.append([f, cost])
    need(model.canonical(frontier) == model.canonical(saved["paid"]["frontier"]), "frontier receipt")
    base_prices = path_prices(baseline_graph, saved["baseline"])
    need(base_prices == [0] * 8 and model.canonical(saved["baseline"]["frontier"])
         == model.canonical([[f, 0] for f in range(9)]),
         "baseline frontier")
    full = expanded_dual(w, graph, saved["paid"]["potential"])
    need(full["capacity_penalty"] == paid["capacity_penalty"], "expanded dual penalty")
    need((baseline["value"], paid["value"], paid["cost"], paid["dual_gap"], paid["capacity_penalty"])
         == (8, 104, 864, 9, 72), "result differs")
    need(Counter(prices) == {0: 8, 9: 96}, "path price histogram")
    # Only this arithmetic is checked: the coverage contract is inherited.
    boundary = sum(abs(len(basis(tuple(w["final_frames"][r])))
                       - len(basis(tuple(w["initial_frames"][r]))))
                   for r in w["initial_frames"])
    mass = graph.facts["original_rank_mass"]
    idle = 72 * 832 - 9 * boundary
    capacity = 73 * 832
    slack = Fraction(capacity - 9 * mass - idle, 9)
    moment = Fraction(9 * (mass + paid["cost"]) + idle, capacity)
    need((boundary, mass, idle, slack, moment)
         == (2312, 2368, 39096, Fraction(328, 9), Fraction(8523, 7592)), "budget arithmetic")
    return {"status": "PASS_P104_SINGLE_CUT_PRICE", "cut": model.CUT,
            "baseline": baseline["value"], "flow": paid["value"], "cost": paid["cost"],
            "dual_gap": paid["dual_gap"], "capacity_penalty": paid["capacity_penalty"],
            "path_prices": dict(sorted(Counter(prices).items())),
            "graph_sha256": graph.fingerprint(), "expanded": full,
            "conditional_budget": {"boundary": boundary, "original_rank_mass": mass,
                                   "idle": idle, "slack": str(slack), "moment_at_zero": str(moment),
                                   "credit_to_reach_equality": str(paid["cost"] - slack)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify(args.certificate, args.source)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS_P104_SINGLE_CUT_PRICE cut=2429 flow=104 cost=864 baseline=8 "
              "dual=9*flow-72 frontier=0..104 no_new_kappa")


if __name__ == "__main__":
    main()
