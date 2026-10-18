"""Independent chronological audit of the complete PR1552 reset certificate.

Unlike PR1552's algebraic contexts and forward planner, this checker obtains
incoming states by executing the eager complete echoes, and uses suffix costs.
Hanson Sun with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import copy
from fractions import Fraction
from hashlib import sha1, sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def check(ok, message):
    if not ok:
        raise ValueError(message)


def readers(k, m, seed):
    result = []
    for index in range(k):
        top, bottom = [], []
        for block in range(m):
            a = (-1, 1)[bin(seed+index*m+block).count("1") % 2]
            top += [a, (seed+2*index+block) % 3-1]
            bottom += [0, a]
        result.append([top,bottom])
    return result


def reverse(program):
    opposite = {"+":"-", "-":"+", "*":"/", "/":"*"}
    return [(opposite[op],d,s) for op,d,s in program[::-1]]


def shear(d, s, exponent):
    bits, result, shifts = abs(exponent), [], 0
    while bits:
        if shifts:
            result.append(("*",s,s))
        if bits % 2:
            result.append(("+" if exponent > 0 else "-",d,s))
        shifts += 1
        bits //= 2
    result += [("/",s,s)]*max(0,shifts-1)
    return result


def block(rs, m, lo, hi):
    work, out = 2+2*m, []
    for index in range(lo,hi):
        if index != lo:
            out.append(("+",0,1))
        for target,row in enumerate(rs[index]):
            for coord,value in enumerate(row):
                out += [("+" if value > 0 else "-",target,work+coord)]*abs(value)
        out += [("+",work+2*j,work+2*j+1) for j in range(m)]
    for j in range(m):
        out += shear(work+2*j,work+2*j+1,lo-hi)
    out += shear(0,1,lo-hi+1)
    return out


def program(rs, m, cuts):
    g,lo = [],0
    for hi in cuts:
        g += block(rs,m,lo,hi)
        lo = hi
    copy = [("+",2+2*m+j,2+j) for j in range(2*m)]
    return copy+g+reverse(copy)+reverse(g)


def unit(n):
    return [{i:1} for i in range(n)]


def apply(gate, state):
    op,d,s = gate
    if op in ("+","-"):
        sign = 1 if op == "+" else -1
        dst = state[d].copy()
        for column,a in state[s].items():
            dst[column] = dst.get(column,0)+sign*a
            if not dst[column]:
                del dst[column]
        state[d] = dst
    elif op == "*":
        state[d] = {c:2*a for c,a in state[d].items()}
    else:
        check(op == "/" and all(a % 2 == 0 for a in state[d].values()),"inexact sparse halving")
        state[d] = {c:a//2 for c,a in state[d].items()}


def execute(gates, initial):
    state = [row.copy() for row in initial]
    peak = max(sum(abs(a) for a in row.values()) for row in state)
    for gate in gates:
        apply(gate,state)
        peak = max(peak,sum(abs(a) for a in state[gate[1]].values()))
    return state,peak


def semantic(rs, m, sign=1):
    expected = unit(2+4*m)
    for row in (0,1):
        for column in range(2*m):
            a = sign*sum(r[row][column] for r in rs)
            if a:
                expected[row][2+column] = a
    return expected


def eager_snapshots(rs,m):
    """Obtain every interval entrance by real chronological eager execution."""
    k,n = len(rs),2+4*m
    copy = [("+",2+2*m+j,2+j) for j in range(2*m)]
    snapshots = {}
    for inverse in (False,True):
        state = unit(n)
        if not inverse:
            state,_ = execute(copy,state)
        phase = 2 if inverse else 0
        snapshots[phase,0] = state
        for index in range(k):
            state,_ = execute(block(rs,m,index,index+1),state)
            snapshots[phase,index+1] = state
        state,_ = execute(copy if inverse else reverse(copy),state)
        phase += 1
        snapshots[phase,k] = state
        for index in range(k-1,-1,-1):
            state,_ = execute(reverse(block(rs,m,index,index+1)),state)
            snapshots[phase,index] = state
        if inverse:
            state,_ = execute(reverse(copy),state)
        check(state == semantic(rs,m,-1 if inverse else 1),"chronological eager endpoint")
    return snapshots


def interval_table(rs,m):
    snapshots = eager_snapshots(rs,m)
    edges = []
    for hi in range(1,len(rs)+1):
        for lo in range(hi):
            gates = block(rs,m,lo,hi)
            peaks = []
            for phase in range(4):
                backward = phase % 2 == 1
                start,end = (hi,lo) if backward else (lo,hi)
                state,peak = execute(reverse(gates) if backward else gates,snapshots[phase,start])
                check(state == snapshots[phase,end],"sparse interval endpoint")
                peaks.append(peak)
            adds = sum(op in ("+","-") for op,_,_ in gates)
            scales = len(gates)-adds
            child = sum(abs(x) for r in rs[lo:hi] for row in r for x in row)+(hi-lo)*m
            edges.append({"start":lo,"end":hi,"ADD":adds-child,"SCALE":scales,
                          "peak":max(peaks),"peaks":peaks})
    return edges


def suffix_cost(edges,k,cap):
    """Reverse-DAG cost; no imports or distances from the primary planner."""
    dist = [None]*(k+1)
    dist[k] = 0
    by_start = [[] for _ in range(k)]
    for e in edges:
        if e["peak"] <= cap:
            by_start[e["start"]].append(e)
    for i in range(k-1,-1,-1):
        options = [e["ADD"]+e["SCALE"]+dist[e["end"]] for e in by_start[i]
                   if dist[e["end"]] is not None]
        if options:
            dist[i] = min(options)
    return dist[0]


def receipt(gates,n):
    state = unit(n)
    peak = 1
    witness = {"step":0,"row":0,"coefficients":[1]+[0]*(n-1)}
    adds = scales = reads = travel = head = 0
    for step,gate in enumerate(gates,1):
        op,d,s = gate
        apply(gate,state)
        if op in ("+","-"):
            adds += 1
            reads += 2
            travel += abs(head-s)+abs(s-d)
        else:
            scales += 1
            reads += 1
            travel += abs(head-d)
        head = d
        size = sum(abs(a) for a in state[d].values())
        if size > peak:
            peak = size
            witness = {"step":step,"row":d,"coefficients":[state[d].get(c,0) for c in range(n)]}
    return state,{"ADD":adds,"SCALE":scales,"total":adds+scales,"data_reads":reads,
                  "data_writes":len(gates),"instruction_reads":len(gates),
                  "head_travel":travel,"peak":peak,"witness":witness}


def scalar(gates,vector):
    values = list(map(Fraction,vector))
    for op,d,s in gates:
        if op == "+":
            values[d] += values[s]
        elif op == "-":
            values[d] -= values[s]
        elif op == "*":
            values[d] *= 2
        else:
            values[d] /= 2
    return values


def check_echo(rec,rs,m):
    cuts = rec["cuts"]
    check(cuts[0] == 0 and cuts[-1] == len(rs) and
          all(type(x) is int for x in cuts) and
          all(a < b for a,b in zip(cuts,cuts[1:])),"invalid source schedule cuts")
    check(rec["lengths"] == [b-a for a,b in zip(cuts,cuts[1:])],"source schedule lengths")
    gates = program(rs,m,cuts[1:])
    tuples = [("ADD",d,s,1 if op == "+" else -1,1) if op in ("+","-") else
              ("SCALE",d,s,2,1) if op == "*" else ("SCALE",d,s,1,2)
              for op,d,s in gates]
    check(sha256(json.dumps(tuples,separators=(",",":")).encode()).hexdigest() == rec["word_sha256"],
          "independent literal word hash")
    for name,word,sign in (("forward",gates,1),("inverse",reverse(gates),-1)):
        state,bill = receipt(word,2+4*m)
        check(state == semantic(rs,m,sign),"sparse full dirty endpoint")
        original = rec[name]
        for key in ("ADD","SCALE","total","data_reads","data_writes","instruction_reads","peak"):
            check(bill[key] == original[key],"independent full receipt: "+key)
        check(bill["head_travel"] == original["data_head_travel"],"independent travel score")
        w = bill["witness"]
        check({"step":w["step"],"row":w["row"]} == original["witness"],"independent prefix location")
        vector = [(a>0)-(a<0) for a in w["coefficients"]]
        attained = scalar(word[:w["step"]],vector)[w["row"]]
        check(attained == bill["peak"],"scalar growth attainer")
        expected_witness = {"step":w["step"],"row":w["row"],
                            "input_signs":vector,"attained":str(attained)}
        check(expected_witness == original["attaining_witness"],"source attaining witness")
    check(rec["peak"] == max(rec["forward"]["peak"],rec["inverse"]["peak"]),"source schedule peak")
    # Fractional dirty states exercise exact arithmetic outside the integer grid.
    for shift in (0,59):
        vector = [Fraction((7*j+shift)%19-9,1 << (j%4)) for j in range(2+4*m)]
        answer = scalar(gates,vector)
        direct = [sum(a*vector[j] for j,a in row.items()) for row in semantic(rs,m)]
        check(answer == direct and scalar(reverse(gates),answer) == vector,"dirty rational inverse")


def exhaustive_small():
    partition_count = cap_count = 0
    for k in range(1,9):
        rs,m = readers(k,2,59),2
        edges = interval_table(rs,m)
        possibilities = []
        for mask in range(1 << (k-1)):
            cuts = [i+1 for i in range(k-1) if mask & (1 << i)]+[k]
            gates = program(rs,m,cuts)
            endpoint,f = execute(gates,unit(10))
            back,b = execute(reverse(gates),unit(10))
            check(endpoint == semantic(rs,m) and back == semantic(rs,m,-1),"small partition dirty map")
            possibilities.append((max(f,b),len(gates)))
            partition_count += 1
        fixed = 2*sum(abs(x) for r in rs for row in r for x in row)+2*k*m+4*m
        for cap in sorted({e["peak"] for e in edges} | {p[0] for p in possibilities}):
            totals = [total for peak,total in possibilities if peak <= cap]
            brute = min(totals) if totals else None
            found = suffix_cost(edges,k,cap)
            found = None if found is None else fixed+2*found
            check(found == brute,"DAG disagrees with exhaustive full-word partitions")
            cap_count += 1
    return partition_count,cap_count


def authenticate():
    sources = json.loads((HERE/"SOURCES.json").read_text())
    for item in sources["pending_predecessors"]:
        data = (HERE/item["local_path"]).read_bytes()
        check(sha256(data).hexdigest() == item["sha256"],"source SHA256: "+item["local_path"])
        check(sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest() == item["git_blob"],
              "source Git blob: "+item["local_path"])
    return sources


def normalize_edges(certificate):
    contexts = ("ff","fr","rf","rr")
    normalized = []
    for edge in certificate["edges"]:
        check(set(edge["peaks"]) == set(contexts),"context inventory")
        normalized.append({"start":edge["i"],"end":edge["j"],"ADD":edge["ADD"],
                           "SCALE":edge["SCALE"],"peak":edge["peak"],
                           "peaks":[edge["peaks"][name] for name in contexts]})
    return sorted(normalized,key=lambda e:(e["end"],e["start"]))


def verify_potential(point,edges,k):
    """Check each published distance by a separate suffix problem at that vertex."""
    cap,dist = point["cap"],point["distances"]
    check(len(dist) == k+1 and dist[0] == 0,"published distance shape")
    for target in range(1,k+1):
        subgraph = [e for e in edges if e["end"] <= target]
        check(dist[target] == suffix_cost(subgraph,target,cap),"published distance not exact")
    check(dist[k] == point["cost"],"published optimum mismatch")
    cuts = point["cuts"]
    check(cuts[0] == 0 and cuts[-1] == k and all(a < b for a,b in zip(cuts,cuts[1:])),"optimal path cuts")
    lookup = {(e["start"],e["end"]):e for e in edges}
    paid = 0
    for a,b in zip(cuts,cuts[1:]):
        edge = lookup[a,b]
        check(edge["peak"] <= cap,"published path exceeds cap")
        paid += edge["ADD"]+edge["SCALE"]
    check(paid == point["cost"],"published path does not attain optimum")


def verify_graph(certificate,edges,frontier):
    check((certificate["children"],certificate["workspace_pairs"],certificate["fixture_seed"])
          == (53,5,53),"fixed predecessor fixture")
    check(certificate["edge_count"] == 1431 and certificate["contexts_per_edge"] == 4
          and certificate["partition_count"] == 2**52,"claimed coverage counts")
    check(normalize_edges(certificate) == edges,"independent complete edge table")
    check(frontier == [(p["cap"],p["cost"]) for p in certificate["frontier"]],"independent entire frontier")


def negative_controls(certificate,edges,frontier,rs,m,unused):
    rejected = []
    def rejects(call,label):
        try:
            call()
        except (ValueError,KeyError,IndexError):
            rejected.append(label)
            return
        raise ValueError("vacuous negative control: "+label)
    # These operate AFTER source authentication, so rejection is mathematical,
    # not merely a hash mismatch. Include edges absent from all supplied paths.
    altered = copy.deepcopy(certificate)
    dormant = next(e for e in altered["edges"] if (e["i"],e["j"]) == unused[0])
    dormant["peak"] -= 1
    rejects(lambda:verify_graph(altered,edges,frontier),"unused_edge_peak")
    altered = copy.deepcopy(certificate)
    altered["edges"][0]["peaks"]["ff"] += 1
    check(altered["edges"][0]["peak"] == certificate["edges"][0]["peak"],"nonmaximal context control")
    rejects(lambda:verify_graph(altered,edges,frontier),"nonmaximal_context_invisible_to_max")
    altered = copy.deepcopy(certificate)
    altered["edges"][-1] = altered["edges"][0]
    rejects(lambda:verify_graph(altered,edges,frontier),"duplicate_edge_same_inventory_size")
    altered = copy.deepcopy(certificate)
    next(e for e in altered["edges"] if e["SCALE"])["SCALE"] -= 1
    rejects(lambda:verify_graph(altered,edges,frontier),"unpaid_interval_scale")
    altered = copy.deepcopy(certificate)
    altered["frontier"][-1]["cost"] -= 1
    rejects(lambda:verify_graph(altered,edges,frontier),"invented_frontier_saving")
    point = copy.deepcopy(certificate["frontier"][-1])
    point["distances"][1] += 1
    rejects(lambda:verify_potential(point,edges,53),"wrong_nonterminal_distance")
    schedule = copy.deepcopy(certificate["predecessor_unsplit"])
    schedule["forward"]["attaining_witness"]["input_signs"][0] *= -1
    rejects(lambda:check_echo(schedule,rs,m),"false_prefix_attainer")
    schedule = copy.deepcopy(certificate["predecessor_unsplit"])
    schedule["inverse"]["data_reads"] -= 1
    rejects(lambda:check_echo(schedule,rs,m),"undercharged_inverse_access")
    good = program(rs,m,[52,53])
    expected = semantic(rs,m)
    rejects(lambda:check(execute(good[1:],unit(22))[0] == expected,"wrong source load"),
            "omitted_source_load")
    half = next(i for i,g in enumerate(good) if g[0] == "/")
    rejects(lambda:check(execute(good[:half]+good[half+1:],unit(22))[0] == expected,"wrong halving"),
            "omitted_restoring_half")
    return rejected


def build():
    sources = authenticate()
    original_bytes = (HERE/"sources/pr1552-CERTIFICATE.json").read_bytes()
    certificate = json.loads(original_bytes)
    rs,m,k = readers(53,5,53),5,53
    edges = interval_table(rs,m)
    frontier,last = [],None
    thresholds = sorted({e["peak"] for e in edges})
    for cap in thresholds:
        cost = suffix_cost(edges,k,cap)
        if cost is not None and (last is None or cost < last):
            frontier.append((cap,cost))
            last = cost
    verify_graph(certificate,edges,frontier)
    schedules = [certificate["eager"],certificate["predecessor_unsplit"]]+certificate["frontier_schedules"]
    check(len(certificate["frontier_schedules"]) == len(frontier),"frontier witness inventory")
    for point,schedule in zip(certificate["frontier"],certificate["frontier_schedules"]):
        verify_potential(point,edges,k)
        check(point["cuts"] == schedule["cuts"],"frontier path binding")
        check(schedule["peak"] == point["cap"],"frontier cap attainment")
        check(schedule["forward"]["total"] == 1964+2*point["cost"],"complete cost recurrence")
    for item in certificate["bit_caps"]:
        point,schedule = item["optimality"],item["schedule"]
        check(point["cap"] == (1 << item["magnitude_bits"])-1,"magnitude cap encoding")
        verify_potential(point,edges,k)
        check(point["cuts"] == schedule["cuts"] and schedule["peak"] <= point["cap"],"bit-cap binding")
        check(schedule["forward"]["total"] == 1964+2*point["cost"],"bit-cap price")
        schedules.append(schedule)
    for schedule in schedules:
        check_echo(schedule,rs,m)
    # Authenticate the inherited endpoint benchmarks without executing source code.
    prior = json.loads((HERE/"sources/pr1537-RESULT.json").read_text())["echoes"][0]
    for name,current in (("eager",certificate["eager"]),("carry",certificate["predecessor_unsplit"])):
        check(current["word_sha256"] == prior[name]["word_sha256"],"PR1537 literal baseline binding")
        check(current["forward"]["peak"] == int(prior[name]["prefix_row_l1"]),"PR1537 forward benchmark")
        check(current["inverse"]["peak"] == int(prior[name]["inverse_prefix_row_l1"]),"PR1537 inverse benchmark")
    used = {tuple(pair) for schedule in schedules for pair in zip(schedule["cuts"],schedule["cuts"][1:])}
    unused = sorted({(e["start"],e["end"]) for e in edges}-used)
    rejected = negative_controls(certificate,edges,frontier,rs,m,unused)
    partitions,caps = exhaustive_small()
    edge_hash = sha256(json.dumps(edges,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    contextual = next(e for e in edges if (e["start"],e["end"]) == (7,21))
    segment = block(rs,m,7,21)
    isolated = max(execute(segment,unit(22))[1],execute(reverse(segment),unit(22))[1])
    check(isolated < contextual["peak"],"standalone context underestimate")
    return {"schema_version":1,"status":"independent finite verification; no new kappa",
            "base_commit":sources["base_commit"],"assignment_seed":59,
            "audited_pr":1552,"audited_head":"4db7213c90288b1eb83983e08c5ef401d19b7844",
            "certificate_sha256":sha256(original_bytes).hexdigest(),
            "edges":len(edges),"context_replays":4*len(edges),"thresholds":len(thresholds),
            "normalized_edge_sha256":edge_hash,"frontier":[list(x) for x in frontier],
            "full_schedule_records":len(schedules),"distinct_complete_words":len({s["word_sha256"] for s in schedules}),
            "edges_on_supplied_paths":len(used),"edges_off_all_supplied_paths":len(unused),
            "unseen_edge_control":list(unused[0]),
            "exact_distance_entries":sum(len(p["distances"]) for p in certificate["frontier"])
                +sum(len(p["optimality"]["distances"]) for p in certificate["bit_caps"]),
            "small_partitions":partitions,"small_cap_decisions":caps,
            "controls":rejected,"standalone_counterexample":{"interval":[7,21],"standalone":isolated,
                                                                  "contextual":contextual["peak"]}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit",action="store_true",help="print the canonical audit receipt")
    args = parser.parse_args()
    result = build()
    if args.emit:
        print(json.dumps(result,sort_keys=True,indent=2))
    else:
        check(result == json.loads((HERE/"RESULT.json").read_text()),"stored audit receipt mismatch")
        print(f"PASS_INDEPENDENT_RESET_GRAPH edges={result['edges']} contexts={result['context_replays']} "
              f"off_path_edges={result['edges_off_all_supplied_paths']} frontier=31 "
              f"schedules={result['full_schedule_records']} small_partitions=255 "
              f"controls={len(result['controls'])} no_new_kappa")


if __name__ == "__main__":
    main()
