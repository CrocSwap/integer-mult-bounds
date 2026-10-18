#!/usr/bin/env python3
"""Exact dual certificate and full cost bound for the selected k8 frame domain.

The frame model is retained, credited navinor code. This successor binds the
different selected word and checks every new dual constraint. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("k8_common", HERE / "common.py")
U = importlib.util.module_from_spec(spec)
spec.loader.exec_module(U)
need = U.need
RANKS = range(2, 10)
BASE_LO = Q(1690054109088, 10**15)
BASE_HI = Q(1690054109089, 10**15)
TARGET = Q(21, 20) * BASE_HI


def span_mask(frame):
    values = {0}
    for vector in frame:
        values |= {x ^ vector for x in values}
    return sum(1 << x for x in values)


def graph_receipt(model):
    nodes = [[list(n), span_mask(model.lo[n]), span_mask(model.hi[n])] for n in sorted(model.lo)]
    domains = [[list(n), sorted(span_mask(f) for f in model.domain[n])] for n in sorted(model.domain)]
    edges = [[list(a), list(b), k] for (a, b), k in sorted(model.edges.items())]
    cones = [[k, span_mask(f)] for k, f in sorted(model.ceil.items())]
    return {"nodes_sha256": U.digest(nodes), "domains_sha256": U.digest(domains),
            "edges_sha256": U.digest(edges), "cones_sha256": U.digest(cones),
            "node_count": len(nodes), "edge_count": len(edges), "cone_registers": len(cones)}


def subspace_count(k):
    total = 0
    for d in range(k+1):
        top = bottom = 1
        for j in range(d):
            top *= (1 << (k-j)) - 1
            bottom *= (1 << (d-j)) - 1
        total += top // bottom
    return total


def charges(C, a):
    costs = {d: C.child_cost(d, 73, a) for d in range(1, 10)}
    return {d: (73*(costs[d][0]-d*costs[1][1]), 73*(costs[d][1]-d*costs[1][0]))
            for d in RANKS}


def lower(vec, bounds):
    return sum((value * bounds[d][0 if value > 0 else 1]
                for d, value in vec.items() if value), Q(0))


def check_duals(M, model, data, all_bounds):
    comps = model.components()
    need(len(data["components"]) == len(comps), "component coverage")
    stats = Counter()
    total = Counter(model.fixed_profile())
    distinct_reduced = set()
    for comp, record in zip(comps, data["components"]):
        need(record["first"] == json.dumps(comp[0]) and record["nodes"] == len(comp), "component identity")
        labels, unary, pairs = model.component_problem(comp)
        for node in comp:
            domain = labels[node]
            k = len(model.hi[node])-len(model.lo[node])
            need(len(domain) == len(set(domain)) == subspace_count(k), "complete frame interval")
            need(all(M.contained(model.lo[node], f) and M.contained(f, model.hi[node]) for f in domain),
                 "frame outside interval")
        rows, rhs, cols = M.lp(labels, unary, pairs)
        keys = [json.dumps(row) for row in rows]
        need(set(record["duals"]) <= set(keys), "dual row domain")
        dual = []
        for key in keys:
            vec = {int(d): Q(v) for d, v in record["duals"].get(key, {}).items()}
            need(all(d in RANKS for d in vec), "dual rank coordinate")
            dual.append(vec)
        for _, cost, entries in cols:
            residual = {d: Q(cost[d]) for d in RANKS}
            for row, multiplier in entries:
                for d, value in dual[row].items():
                    residual[d] -= multiplier*value
            if any(residual.values()):
                for bounds in all_bounds.values():
                    need(lower(residual, bounds) > 0, "negative or uncertified reduced cost")
                stats["positive"] += 1
            else:
                stats["zero"] += 1
            distinct_reduced.add(tuple(str(residual[d]) for d in RANKS))
        objective = {d: sum((rhs[i]*v.get(d, 0) for i, v in enumerate(dual)), Q(0)) for d in RANKS}
        baseline = M.assignment_cost(labels, unary, pairs, {n: model.baseline()[n] for n in comp})
        need(all(objective[d] == baseline[d] for d in RANKS), "dual objective does not equal baseline")
        total.update({d: baseline[d] for d in range(1, 10) if baseline[d]})
        stats.update(rows=len(rows), columns=len(cols), components=1)
    need(dict(total) == U.PROFILE, "full fixed and variable cost coverage")
    stats["distinct_reduced_vectors"] = len(distinct_reduced)
    return dict(stats)


def rank_chain(C, model, a):
    """A weaker independent-register relaxation, with exact interval dynamic programming."""
    scale = 1 << C.PREC
    cost = {0: (0, 0)}
    for d in range(1, 10):
        cost[d] = tuple(int(x*scale) for x in C.child_cost(d, 73, a))
    lower_total = upper_total = 0
    for chain in model.chains.values():
        dp = {len(model.lo[chain[0]]): (0, 0)}
        for node in chain[1:]:
            nxt = {}
            for d in range(len(model.lo[node]), len(model.hi[node])+1):
                options = [(v[0]+cost[d-e][0], v[1]+cost[d-e][1]) for e, v in dp.items() if e <= d]
                if options:
                    nxt[d] = (min(x[0] for x in options), min(x[1] for x in options))
            dp = nxt
        need(len(dp) == 1, "rank-chain fixed endpoint")
        lo, hi = next(iter(dp.values()))
        lower_total += lo
        upper_total += hi
    for d in model.centre_children:
        lower_total += cost[d][0]
        upper_total += cost[d][1]
    idle = C.child_cost(51, 73, a)
    return ((Q(lower_total, scale)+Q(1646, 51)*idle[0])/Q(896, 9),
            (Q(upper_total, scale)+Q(1646, 51)*idle[1])/Q(896, 9))


def run():
    U.source_bindings()
    word = U.word()
    M, C = U.retained("frame_model.py"), U.retained("ceiling.py")
    model = M.Model(word)
    need(model.profile(model.baseline()) == U.PROFILE, "literal baseline frame bill")
    need(C.ceiling(U.PROFILE, 73, 896, 9, 64) == (BASE_LO, BASE_HI), "exact baseline ceiling bracket")
    data = U.duals()
    bounds = {str(a): charges(C, a) for a in (BASE_HI, TARGET)}
    stats = check_duals(M, model, data, bounds)
    q = C.model(U.PROFILE, 73, 896, 9, 64)
    need(q["local_mass"] == 5586 and q["idle_mass"] == 1646 and q["R"] == 51,
         "full coverage-law invoice")
    bills = {}
    for a in (BASE_HI, TARGET):
        lo, hi = C.relax(U.PROFILE, 73, 896, 9, 64, a)
        need(lo > 1, "packing ceiling not excluded")
        bills[str(a)] = {"lower_minus_one": str(lo-1), "upper_minus_one": str(hi-1)}
    chain = rank_chain(C, model, TARGET)
    need(chain[0] > 1, "rank-chain screen does not reject target")
    components = model.components()
    return {"schema": "selected-k8-frame-ceiling-v1", "status": "PASS_SELECTED_K8_FRAME_CEILING",
            "word_sha256": U.WORD_SHA, "duals_sha256": U.digest(data),
            "profile": {str(r): n for r, n in U.PROFILE.items()}, "local_mass": 5586, "idle_mass": 1646,
            "gates": len(model.gates), "free_gates": len(model.domain),
            "component_sizes": {str(k): v for k, v in sorted(Counter(map(len, components)).items())},
            "domain_sizes": {str(k): v for k, v in sorted(Counter(map(len, model.domain.values())).items())},
            "graph": graph_receipt(model), "duality": stats,
            "baseline_a_bracket": [str(BASE_LO), str(BASE_HI)], "target_a": str(TARGET),
            "kappa_cap": str(BASE_HI/(1+BASE_HI)), "bills": bills,
            "rank_chain_target": [str(chain[0]-1), str(chain[1]-1)],
            "scope": "fixed selected scalar word, endpoints and chronology; complete frame reassignment and ideal idle packing; no new supplier or kappa"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-expected", action="store_true")
    args = parser.parse_args()
    receipt = run()
    path = HERE / "EXPECTED.json"
    if args.write_expected:
        path.write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
    else:
        need(U.parse(path.read_bytes()) == receipt, "receipt mismatch")
    print(receipt["status"], "components="+str(receipt["duality"]["components"]),
          "columns="+str(receipt["duality"]["columns"]), "receipt_sha256="+U.digest(receipt))


if __name__ == "__main__":
    main()
