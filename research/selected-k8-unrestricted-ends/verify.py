#!/usr/bin/env python3
"""Unrestricted terminal endpoint/frame bound, with variable-mass excess prices.

Adapts Gareth Davidson PR1995, mathematical commit 73e323159d65c974debb180189694fd59144da5f.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
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
RANKS = range(1, 10)
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
    cones = [[q, support] for q, support in sorted(model.cones.items())]
    return {"nodes_sha256": U.digest(nodes), "domains_sha256": U.digest(domains),
            "edges_sha256": U.digest(edges), "cones_sha256": U.digest(cones),
            "node_count": len(nodes), "edge_count": len(edges), "cone_helpers": len(cones), "cone_edges": len(model.cone_edges)}


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
    costs = {d: C.child_cost(d, 73, a) for d in RANKS}
    idle = C.child_cost(51, 73, a)
    # Local mass varies. Reprice every released unit as idle, not as saved work.
    return {d: (73*(costs[d][0]-Q(d,51)*idle[1]),
                73*(costs[d][1]-Q(d,51)*idle[0])) for d in RANKS}


def lower(vec, bounds):
    return sum((value * bounds[d][0 if value > 0 else 1]
                for d, value in vec.items() if value), Q(0))


def check_duals(M, model, data, assignment, profile, all_bounds):
    comps = model.components()
    need(len(data["components"]) == len(comps), "component coverage")
    stats = Counter()
    total = Counter({d:n for d,n in model.fixed_profile().items() if n})
    distinct_reduced = set()
    for comp, record in zip(comps, data["components"]):
        need(record["first"] == json.dumps(comp[0]) and record["nodes"] == len(comp), "component identity")
        labels, unary, pairs = model.component_problem(comp)
        for node in comp:
            domain = labels[node]
            k = len(model.hi[node])-len(model.lo[node])
            need(len(domain) == len(set(domain)) == subspace_count(k), "complete frame interval")
            need(all(M.M.contained(model.lo[node], f) and M.M.contained(f, model.hi[node]) for f in domain),
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
        baseline = M.assignment_cost(labels, unary, pairs, {n: assignment[n] for n in comp})
        need(all(objective[d] == baseline[d] for d in RANKS), "dual/primal coefficient identity")
        total.update({d: baseline[d] for d in range(1, 10) if baseline[d]})
        stats.update(rows=len(rows), columns=len(cols), components=1)
    need(dict(total) == profile, "full fixed and variable cost coverage")
    stats["distinct_reduced_vectors"] = len(distinct_reduced)
    return dict(stats)


def local(name):
    spec=importlib.util.spec_from_file_location("endpoint_"+name,HERE/(name+".py"))
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def run():
    U.source_bindings()
    word=U.word()
    M,C,P=local("model"),U.retained("ceiling.py"),local("materialize")
    model=M.Model(word)
    need(model.profile(model.baseline())==U.PROFILE,"baseline profile")
    assignment,profile=P.primal(U,model)
    need(profile=={1:2400,2:446,3:416,4:142,5:82,8:8},"optimal profile binding")
    lo,hi=C.ceiling(profile,73,896,9,64)
    need(BASE_HI<lo<hi<TARGET,"new relaxation ceiling below target")
    data=U.duals()
    bounds={str(a):charges(C,a) for a in (hi,TARGET)}
    stats=check_duals(M,model,data,assignment,profile,bounds)
    billing=C.model(profile,73,896,9,64)
    need(billing["local_mass"]==5582 and billing["idle_mass"]==1650 and billing["R"]==51,
         "variable local mass recharged as idle")
    bills={}
    for a in (lo,hi,TARGET):
        left,right=C.relax(profile,73,896,9,64,a)
        need(right<1 if a==lo else left>1,"ceiling bracket sign")
        bills[str(a)]=[str(left-1),str(right-1)]
    free_ends=[n for n in model.domain if n[0]=="E"]
    need(len(model.original_caps)==78 and len(free_ends)==78,"all endpoint coverage")
    endpoint_intervals=Counter((len(model.lo[n]),len(model.hi[n]),len(model.domain[n])) for n in free_ends)
    need(endpoint_intervals=={(4,9,374):32,(7,9,5):46},"complete unrestricted endpoint domains")
    min_mass=5586+sum(len(model.lo[("E",q)])-len(cap) for q,cap in model.original_caps.items())
    max_mass=5586+sum(9-len(cap) for cap in model.original_caps.values())
    need((min_mass,max_mass)==(5540,5792) and 7232-max_mass>=0,"all endpoint choices have nonnegative idle mass")
    changed_ends=[q for q,cap in sorted(model.original_caps.items())
                  if model.frame_of(("E",q),assignment)!=cap]
    need(changed_ends==[574,575,580,581],"attaining contracted ends")
    return {"schema":"selected-k8-unrestricted-end-bound-v1",
            "status":"PASS_SELECTED_K8_UNRESTRICTED_END_BOUND","word_sha256":U.WORD_SHA,
            "duals_sha256":U.digest(data),"primal_sha256":U.digest(U.primal_data()),
            "profile":{str(r):n for r,n in profile.items()},"local_mass":5582,"idle_mass":1650,
            "gates":len(model.gates),"free_gates":len(model.domain)-len(free_ends),
            "restricted_ends":78,"free_ends":[n[1] for n in free_ends],
            "forced_ends":sorted(set(model.original_caps)-{n[1] for n in free_ends}),
            "endpoint_intervals":[{"lower_dimension":a,"upper_dimension":b,"choices":c,"count":n}
                                  for (a,b,c),n in sorted(endpoint_intervals.items())],
            "all_assignment_local_mass_interval":[min_mass,max_mass],
            "all_assignment_idle_mass_interval":[7232-max_mass,7232-min_mass],
            "attaining_changed_ends":changed_ends,
            "component_sizes":{str(k):v for k,v in sorted(Counter(map(len,model.components())).items())},
            "domain_sizes":{str(k):v for k,v in sorted(Counter(map(len,model.domain.values())).items())},
            "graph":graph_receipt(model),"duality":stats,
            "a_bracket":[str(lo),str(hi)],"kappa_cap":str(hi/(1+hi)),"target_a":str(TARGET),
            "ceiling_ratio_upper":str(hi/BASE_LO),"bills":bills,
            "scope":"fixed scalar word and entrances; arbitrary terminal subspaces of formerly restricted helpers and all gate frames; full idle charge; no global supplier or new kappa"}


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
