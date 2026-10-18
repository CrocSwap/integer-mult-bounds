"""Recompute all interval evidence; default replay never writes artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import planner as p
import oracle
import composition


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def dual_check(solution, edges, k):
    d = solution["distances"]
    p.require(len(d) == k+1 and d[0] == 0, "dual entrance")
    for edge in edges:
        a, b = edge["a"], edge["b"]
        if edge["peak"] <= solution["cap"] and d[a] is not None:
            p.require(d[b] is not None and d[b] <= d[a]+edge["add"]+edge["scale"],
                      "dual edge inequality")
    lookup = {(e["a"],e["b"]):e for e in edges}
    a, cost = 0, 0
    for b in solution["cuts"]:
        edge = lookup[a,b]
        p.require(edge["peak"] <= solution["cap"], "primal cap")
        cost += edge["add"] + edge["scale"]
        a = b
    p.require(a == k and cost == d[k] == solution["boundary_price"], "primal-dual equality")


def table_record(solution, children, m, old, edges, fused=False):
    dual_check(solution, edges, len(children))
    word = p.emit_partition(children, solution["cuts"], m, old, fused)
    report = p.word_report(word, m, old)
    end, _, _ = p.replay(word, p.identity(2+4*m))
    p.require(end == oracle.endpoint(children, m), "source-only endpoint")
    p.require(report["peak"] <= solution["cap"], "whole-word cap")
    p.require(report["add"] == 1964 + 2*solution["boundary_add"] and
              report["scale"] == 2*solution["boundary_scale"], "complete cost")
    return {**solution, "word": report}


def exhaustive_small(old, fused):
    partitions, decisions = 0, 0
    fixtures = [(m,k) for m in range(1,4) for k in range(1,8)]+[(5,12)]
    has_strict_saving = False
    for m,k in fixtures:
        children = old.fixture(k, m, seed=55)
        edges = p.graph(children, m, old, fused)
        lookup = {(e["a"],e["b"]):e for e in edges}
        cases = []
        for cuts in oracle.all_partitions(k):
            word = p.emit_partition(children, cuts, m, old, fused)
            # Literal full-program propagation does not use interval contexts.
            fw_end, fw, _ = p.replay(word, p.identity(2+4*m))
            _, iv, _ = p.replay(old.inverse(word), p.identity(2+4*m))
            a, predicted, cost = 0, 0, 0
            for b in cuts:
                edge = lookup[a,b]
                predicted = max(predicted,edge["peak"])
                adds, scales = oracle.independent_cost(b-a,m,fused and b==k)
                p.require((adds,scales)==(edge["add"],edge["scale"]), "independent tariff")
                cost += adds+scales
                a = b
            p.require(fw_end == oracle.endpoint(children,m), "small endpoint")
            p.require(predicted == max(fw,iv), "context-composition peak")
            cases.append((predicted,cost))
            partitions += 1
        thresholds = {v for peak,_ in cases for v in (max(1,peak-1),peak)}
        for cap in sorted(thresholds):
            eligible = [cost for peak,cost in cases if peak<=cap]
            expected = min(eligible) if eligible else None
            result = p.solve(edges,k,cap)
            p.require((None if result is None else result["boundary_price"]) == expected,
                      "exhaustive optimum")
            decisions += 1
            has_strict_saving |= expected is not None and expected < k*m
    p.require(not fused or has_strict_saving,"positive planner-saving control")
    return {"partitions":partitions,"cap_decisions":decisions,"fixtures":[list(pair) for pair in fixtures],
            "strict_saving_observed":has_strict_saving,"fixture_seed":55}


def controls(children, edges, old, full):
    names = []
    def rejected(name, f):
        try:
            f()
        except (ValueError,KeyError):
            names.append(name)
            return
        raise ValueError("control accepted: "+name)

    solution = p.solve(edges,53,4096)
    bad = json.loads(json.dumps(solution)); bad["cap"] = 3957
    rejected("cap_one_below_attained",lambda: dual_check(bad,edges,53))
    bad_dual = json.loads(json.dumps(solution)); bad_dual["distances"][-1] += 1
    rejected("inflated_lower_bound",lambda: dual_check(bad_dual,edges,53))
    wrong = json.loads(json.dumps(children)); wrong[3]["reader"][1][0] = 1
    rejected("nonintertwining_child",lambda: p.graph(wrong,5,old))
    rejected("nonintegral_halving",lambda: p.replay([("SCALE",1,1,1,2)],p.identity(22)))
    rejected("duplicate_cut",lambda: p.emit_partition(children,[1,1,53],5,old))
    # Omitting the source unload is semantically wrong, even if cuts are correct.
    copy = [("ADD",12+j,2+j,1,1) for j in range(10)]
    group = old.emit_group(children[:52],12,5,"carry")+old.emit_group(children[52:],12,5,"carry")
    bad_word = copy+group+old.inverse(group)
    p.require(p.replay(bad_word,p.identity(22))[0] != oracle.endpoint(children,5),"unload control")
    names.append("source_unload_omission")
    # A midpoint observation would prohibit deleting the output-return pair.
    original_group = old.emit_group(children,12,5,"carry")
    stripped = p.drop_output_return(original_group,53,old)
    p.require(p.replay(stripped,p.identity(22))[0] != p.replay(original_group,p.identity(22))[0],
              "midpoint observation control")
    names.append("uncanonical_midpoint_observation")
    # A boundary evaluated on fresh D misses the carried prior readers.
    prefix = p.prefix_readers(children,5,old)
    correct = p.context(prefix,20,5,"forward_group")
    stale = p.context(prefix,0,5,"forward_group")
    ops = p.interval_word(children,20,36,5,old)
    true_peak = p.replay(ops,correct)[1]
    false_peak = p.replay(ops,stale)[1]
    p.require(true_peak != false_peak,"zero-context control")
    names.append("forgotten_prefix_reader")
    # An unload that also touches D does NOT commute with output restoration.
    alias = [("SCALE",0,0,2,1),("ADD",0,1,1,1),("SCALE",0,0,1,2)]
    p.require(oracle.primitive_state(alias,[0,1]) != oracle.primitive_state([("ADD",0,1,1,1)],[0,1]),
              "disjoint-register control")
    names.append("output_alias_breaks_commutation")
    return {"rejected":names,"context_counterexample":{"interval":[20,36],"true_peak":true_peak,"fresh_output_peak":false_peak}}


def build():
    old = p.predecessor()
    children = old.fixture(53,5,seed=53)
    edges = p.graph(children,5,old,True)
    canonical_edges = p.graph(children,5,old,False)
    # Independently derive every canonical state from eager child maps.
    prefix = p.prefix_readers(children,5,old)
    states = oracle.uniform_forward_states(children,5)
    for kind, values in states.items():
        for at, state in enumerate(values):
            p.require(state == p.context(prefix,at,5,kind),"independent canonical state")
    caps = [128,256,512,1024,2048,4096,8192]
    table = [table_record(p.solve(edges,53,cap),children,5,old,edges,True) for cap in caps]
    frontier, last = [], None
    for cap in sorted({e["peak"] for e in edges}):
        solution = p.solve(edges,53,cap)
        if solution is not None and (last is None or solution["boundary_price"]<last):
            frontier.append(table_record(solution,children,5,old,edges,True))
            last = solution["boundary_price"]
    p.require(len(frontier)==35 and frontier[1]["cap"]==788 and frontier[-1]["cap"]==4116,
              "frontier endpoints")
    p.require(p.solve(edges,53,787)["boundary_price"]==265,"first-saving lower bound")
    p.require(p.solve(edges,53,4115)["boundary_price"]>121,"full-saving lower bound")
    canonical_frontier, last = [], None
    for cap in sorted({e["peak"] for e in canonical_edges}):
        solution = p.solve(canonical_edges,53,cap)
        if solution is not None and (last is None or solution["boundary_price"]<last):
            canonical_frontier.append(table_record(solution,children,5,old,canonical_edges))
            last = solution["boundary_price"]
    p.require(len(canonical_frontier)==31 and canonical_frontier[-1]["cap"]==3932,
              "canonical control frontier")
    eager = old.emit_echo(children,2,12,5,"eager")
    full = old.emit_echo(children,2,12,5,"carry")
    references = {"eager":p.word_report(eager,5,old),"uncut":p.word_report(full,5,old)}
    p.require(references["eager"]["operations"]==2494 and references["eager"]["peak"]==87,
              "frozen eager reference")
    p.require(references["uncut"]["operations"]==2234 and references["uncut"]["peak"]==4195,
              "frozen uncut reference")
    # Code-disjoint Fraction column replay of both directions of three full words.
    checked_columns = 0
    attained_peaks = 0
    for cuts in ([53],[1,53],p.solve(edges,53,4096)["cuts"]):
        word = p.emit_partition(children,cuts,5,old,True)
        for ops in (word,oracle.invert(word)):
            matrix, peak, integral = oracle.inspect(ops,22)
            expected, row_peak, _ = p.replay(ops,p.identity(22))
            p.require(matrix == expected and peak == row_peak and integral,"column oracle")
            checked_columns += 22
            _, _, witness = p.replay(ops,p.identity(22))
            partial = ops[:witness["step"]]
            row = p.replay(partial,p.identity(22))[0][witness["row"]]
            signs = [(value>0)-(value<0) for value in row]
            p.require(abs(oracle.primitive_state(partial,signs)[witness["row"]])==peak,
                      "attaining sign input")
            attained_peaks += 1
    return {"schema_version":1,"status":"PASS_PRECISION_CAPPED_UNIPOTENT_CUTS",
            "assignment_seed":55,"fixture_seed":53,"base":"64039f1bd3b6a523b96083fd858ad040a75e3030",
            "predecessor_head":"407f00df6ca0bf86b455b5640f18ec2f62ee77b9",
            "domain":{"k":53,"m":5,"partitions":2**52,"intervals":len(edges),
                      "contextual_replays":4*len(edges)-2*53,"cap":"both literal directions; exact row-L1", "tariff":"ADD=SCALE=1"},
            "edges_sha256":hashlib.sha256(canonical(edges)).hexdigest(),
            "references":references,"caps":table,"frontier":frontier,
            "canonical_control":{"edges_sha256":hashlib.sha256(canonical(canonical_edges)).hexdigest(),
                                 "frontier":canonical_frontier},
            "independent_contexts":216,"fraction_basis_columns":checked_columns,
            "attained_prefix_peaks":attained_peaks,
            "small_exhaustion":{"fused":exhaustive_small(old,True),"canonical":exhaustive_small(old,False)},
            "nested_composition":composition.check(p,old),
            "controls":controls(children,edges,old,full),
            "scope":"Fixed-fixture canonical partitions with one optional disjoint terminal-return cancellation; no supplier admission, bit-runtime or kappa claim."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit",action="store_true")
    args = parser.parse_args()
    receipt = build()
    if args.emit:
        print(json.dumps(receipt,indent=2,sort_keys=True))
        return
    p.require(receipt == json.loads((HERE/"RESULT.json").read_text()),"receipt mismatch")
    print("PASS_PRECISION_CAPPED_UNIPOTENT_CUTS cap256=2494 first_saving_cap=788 "
          "cap4096_operations=2222 peak=3958 intervals=1431 frontier=35 controls=9 no_new_kappa")


if __name__ == "__main__":
    main()
