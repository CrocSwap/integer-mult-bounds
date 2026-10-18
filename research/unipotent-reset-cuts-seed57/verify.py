#!/usr/bin/env python3
"""Exact fixed-fixture certificate, Hanson Sun / OpenAI Codex, Apache-2.0.

The row planner and Fraction column oracle are separate implementations in
the same AI-assisted session, not independent human review or formalization.
"""
import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import model

require = model.require


def reverse_word(word):
    # Separate from the pinned emitter's inverse helper.
    out = []
    for op, dst, src, num, den in word[::-1]:
        out.append((op, dst, src, -num, den) if op == "ADD" else (op, dst, src, den, num))
    return out


def scalar_execute(word, data):
    values = list(map(Fraction, data))
    for op, dst, src, num, den in word:
        if op == "ADD":
            values[dst] += num * values[src]
        elif op == "SCALE":
            values[dst] *= Fraction(num, den)
        else:
            raise ValueError("unknown oracle opcode")
    return values


def column_oracle(word, n):
    """Basis-vector executions with Fraction arithmetic; no row propagation."""
    masses = [Fraction(0)] * len(word)
    final = [[Fraction(0)] * n for _ in range(n)]
    for basis in range(n):
        state = [Fraction(int(i == basis)) for i in range(n)]
        for t, (op, dst, src, num, den) in enumerate(word):
            if op == "ADD":
                state[dst] += num * state[src]
            elif op == "SCALE":
                state[dst] *= Fraction(num, den)
            else:
                raise ValueError("unknown oracle opcode")
            require(state[dst].denominator == 1, "column oracle: nonintegral prefix")
            masses[t] += abs(state[dst])
        for i in range(n):
            final[i][basis] = state[i]
    return final, int(max([Fraction(1), *masses]))


def expected(children, m, sign=1):
    rows = model.eye(2+4*m)
    # Direct semantic accumulation, without model.prefixes.
    for leaf in children:
        for i, row in enumerate(leaf["reader"]):
            for j, value in enumerate(row):
                rows[i][2+j] += sign*value
    return rows


def witness_check(word, n, evidence):
    step, row = evidence["witness"]["step"], evidence["witness"]["row"]
    prefix, _ = model.trace(word[:step], model.eye(n))
    signs = [(x > 0) - (x < 0) for x in prefix[row]]
    value = scalar_execute(word[:step], signs)[row]
    require(value == evidence["peak"], "growth witness does not attain claimed peak")
    return {"step":step, "row":row, "input_signs":signs, "attained":str(value)}


def check_schedule(children, m, cuts, columns=False):
    word = model.emit(children, m, cuts)
    n = 2+4*m
    bills = []
    for direction, program, sign in (("forward",word,1), ("inverse",reverse_word(word),-1)):
        actual, bill = model.trace(program, model.eye(n))
        require(actual == expected(children,m,sign), "complete dirty-state map " + direction)
        require((bill["ADD"],bill["SCALE"]) == model.complete_bill(children,m,cuts), "complete recursive invoice")
        require(bill["data_reads"] == 2*bill["ADD"]+bill["SCALE"], "read invoice")
        bill["attaining_witness"] = witness_check(program,n,bill)
        if columns:
            other, peak = column_oracle(program,n)
            require(other == actual and peak == bill["peak"], "independent column oracle")
        bills.append(bill)
    dirty = [Fraction((7*i+57) % 19-9, 2**(i % 3)) for i in range(n)]
    reference = [sum(a*b for a,b in zip(row,dirty)) for row in expected(children,m)]
    got = scalar_execute(word,dirty)
    require(got == reference and scalar_execute(reverse_word(word),got) == dirty, "dirty rational probe/inverse")
    return {"cuts":cuts, "lengths":[j-i for i,j in zip(cuts,cuts[1:])],
            "forward":bills[0], "inverse":bills[1], "peak":max(b["peak"] for b in bills),
            "word_sha256":hashlib.sha256(model.canonical(word)).hexdigest()}


def partition_census():
    """Enumerate every actual word, independently of the interval optimizer."""
    partitions = comparisons = columns = 0
    for k in range(1,10):
        children = model.predecessor.fixture(k,1,seed=57)
        edges = model.graph(children,1)
        lookup = {(e["i"],e["j"]):e for e in edges}
        observed = []
        for mask in range(1 << (k-1)):
            cuts = [0]+[i for i in range(1,k) if mask & (1 << (i-1))]+[k]
            word = model.emit(children,1,cuts)
            a = sum(op[0] == "ADD" for op in word)
            s = len(word)-a
            peaks = []
            for program, sign in ((word,1), (reverse_word(word),-1)):
                actual, peak = column_oracle(program,6)
                require(actual == expected(children,1,sign), "enumerated partition endpoint")
                peaks.append(peak)
                columns += 6
            observed.append((max(peaks),a,s))
            edge_peak = max(lookup[i,j]["peak"] for i,j in zip(cuts,cuts[1:]))
            require(edge_peak == max(peaks), "canonical-cut growth decomposition")
            partitions += 1
        fixed = 2*sum(sum(abs(x) for row in c["reader"] for x in row)+1 for c in children)+4
        for cap in sorted({p for p,a,s in observed}):
            for tariff in (1,2,5):
                best = min(a+tariff*s for p,a,s in observed if p <= cap)
                optimum = model.shortest(edges,k,cap,tariff)
                model.bellman_check(edges,k,optimum,tariff)
                require(fixed+2*optimum["cost"] == best, "partition census optimum")
                comparisons += 1
    return {"partitions":partitions, "cap_tariff_comparisons":comparisons, "basis_columns":columns}


def must_reject(function, label):
    try:
        function()
    except (ValueError,KeyError):
        return label
    raise ValueError("negative control failed: " + label)


def negative_controls(children, edges, at_4095):
    controls = []
    wrong = copy.deepcopy(at_4095)
    wrong["cost"] -= 1
    wrong["distances"][-1] -= 1
    controls.append(must_reject(lambda: model.bellman_check(edges,53,wrong), "invented cheaper potential"))
    wrong = copy.deepcopy(at_4095)
    wrong["cap"] = 3931
    controls.append(must_reject(lambda: model.bellman_check(edges,53,wrong), "one below minimum full-saving cap"))
    wrong = copy.deepcopy(at_4095)
    wrong["cuts"] = [0,53]
    controls.append(must_reject(lambda: model.bellman_check(edges,53,wrong), "unsplit word at twelve-bit cap"))
    word = model.emit(children,5,[0,52,53])
    missing = next(i for i,g in enumerate(word) if g[0] == "SCALE" and g[3:] == (1,2))
    bad = word[:missing]+word[missing+1:]
    def check_bad():
        actual, _ = model.trace(bad,model.eye(22))
        require(actual == expected(children,5), "omitted halving changes dirty map")
    controls.append(must_reject(check_bad, "omitted halving"))
    _, bill = model.trace(word,model.eye(22))
    controls.append(must_reject(lambda: require(bill["ADD"] == bill["total"], "missing SCALE charge"), "omitted scaling cost"))
    bad = copy.deepcopy(children)
    bad[1]["reader"][1][0] = 1
    controls.append(must_reject(lambda: model.prefixes(bad,5), "nonintertwining child"))
    controls.append(must_reject(lambda: model.emit(children,5,[0,52,52,53]), "duplicate cut"))
    controls.append(must_reject(lambda: model.trace([("SCALE",0,0,1,2)],model.eye(2)), "unearned integer halving"))
    # Isolated segment growth omits the output already accumulated at its cut.
    underbounds = []
    for e in edges:
        if not e["i"]:
            continue
        segment = children[e["i"]:e["j"]]
        isolated = check_schedule(segment,5,[0,len(segment)])
        if isolated["peak"] < e["peak"]:
            underbounds.append({"i":e["i"],"j":e["j"],"isolated":isolated["peak"],"actual":e["peak"]})
            break
    require(bool(underbounds), "vacuous accumulated-output control")
    controls.append("zero-origin edge bound underestimates prefix growth")
    group = model.predecessor.emit_group(children[:3],12,5,"carry")
    forward, _ = model.trace(group,model.eye(22))
    backward, _ = model.trace(reverse_word(group),model.eye(22))
    require(forward != backward, "vacuous forward-as-inverse control")
    controls.append("forward group cannot substitute for inverse")
    return {"rejections":controls,"zero_origin_witness":underbounds[0]}


def build_certificate():
    children = model.predecessor.fixture(53,5,seed=53)
    edges = model.graph(children,5)
    points = model.frontier(edges,53)
    lookup = {(e["i"],e["j"]):e for e in edges}
    schedules = []
    for point in points:
        schedule = check_schedule(children,5,point["cuts"])
        require(schedule["peak"] == max(lookup[i,j]["peak"] for i,j in zip(point["cuts"],point["cuts"][1:])), "frontier edge/full-word growth")
        require(schedule["forward"]["total"] == 1964+2*point["cost"], "frontier complete price")
        schedules.append(schedule)
    bit_caps = []
    for bits in range(7,14):
        point = model.shortest(edges,53,2**bits-1)
        model.bellman_check(edges,53,point)
        schedule = check_schedule(children,5,point["cuts"])
        require(schedule["peak"] <= point["cap"], "bit cap")
        bit_caps.append({"magnitude_bits":bits,"optimality":point,"schedule":schedule})
    eager = check_schedule(children,5,list(range(54)))
    original = check_schedule(children,5,[0,53])
    retained = json.loads((HERE/"references/PR1537-RESULT.json").read_text())["echoes"][0]
    for tag, schedule in (("eager",eager),("carry",original)):
        for name in ("ADD","SCALE","total","data_reads","data_writes","instruction_reads","data_head_travel"):
            require(schedule["forward"][name] == retained[tag][name], "predecessor invoice replay")
        require(str(schedule["forward"]["peak"]) == retained[tag]["prefix_row_l1"], "predecessor forward peak")
        require(str(schedule["inverse"]["peak"]) == retained[tag]["inverse_prefix_row_l1"], "predecessor inverse peak")
        require(schedule["word_sha256"] == retained[tag]["word_sha256"], "predecessor literal word identity")
    controls = negative_controls(children,edges,bit_caps[5]["optimality"])
    require(model.shortest(edges,53,3931)["cost"] > 135, "3932 not sharp for full saving")
    require(points[1]["cap"] == 788 and points[-1]["cap"] == 3932, "threshold regression")
    return {"schema_version":1,"status":"fixed-fixture finite optimum; no new kappa",
            "base":"ef5f39403610d231a0c27e8a6b4f08c10209bcd6",
            "assignment_seed":57,"fixture_seed":53,"children":53,"workspace_pairs":5,
            "partition_count":2**52,"edge_count":len(edges),"contexts_per_edge":4,
            "edges":edges,"frontier":points,"frontier_schedules":schedules,
            "bit_caps":bit_caps,"eager":eager,"predecessor_unsplit":original,
            "negative_controls":controls,
            "scope":"Contiguous canonical-reset partitions only; unchanged pinned binary return, fixed child order, alpha=sigma=1. Both complete echo directions. Not a physical precision contract or global circuit optimum."}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit",action="store_true",help="print regenerated certificate; do not modify files")
    ap.add_argument("--certificate-only",action="store_true",help="omit supplementary column and small-partition checks")
    args = ap.parse_args()
    certificate = build_certificate()
    if args.emit:
        print(json.dumps(certificate,indent=2,sort_keys=True))
        return
    require(certificate == json.loads((HERE/"CERTIFICATE.json").read_text()), "committed certificate differs from regenerated mathematics")
    if args.certificate_only:
        print("PASS_RESET_CUT_CERTIFICATE edges=1431 frontier=31 no_new_kappa")
        return
    children = model.predecessor.fixture(53,5,seed=53)
    for schedule in certificate["frontier_schedules"]:
        check_schedule(children,5,schedule["cuts"],columns=True)
    census = partition_census()
    print(json.dumps({"independent_partition_census":census,"frontier_basis_columns":31*2*22,
                      "semantic_controls":len(certificate["negative_controls"]["rejections"])},sort_keys=True))
    print("PASS_UNIPOTENT_RESET_CUTS edges=1431 partitions=4503599627370496 frontier=31 "
          "full_saving_peak=4195_to_3932 total=2234 cap255_total=2494 "
          "first_saving_cap=788 no_new_kappa")


if __name__ == "__main__":
    main()
