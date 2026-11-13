#!/usr/bin/env python3
"""Bounded fresh-source screen for public MOVE helper-relation caches.

The first pass keeps only main-projection history bases at normalized
coframes for all 6,279 MOVEs. A second pass keeps full histories only for a
deterministic rank-stratified sample of public main-history hits.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys


PACKAGE = Path(__file__).resolve().parents[1]
WORD = PACKAGE / "inputs/WORD.json.gz"
CALLER = PACKAGE / "inputs/CALLER.json"
INVOICE = PACKAGE / "inputs/CURRENT-PRICE.json"
WORD_SHA = "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9"
CALLER_SHA = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
INVOICE_SHA = "86f71ccbc923db5d7a6753aa971c3a9c8a572680534498ed17be072cfa2aae6b"
MAX_PER_RANK = 2


def need(ok, label):
    if not ok:
        raise ValueError(label)


def add(dst, src, factor=Q(1)):
    for h, value in src.items():
        result = dst.get(h, Q(0)) + factor * value
        if result:
            dst[h] = result
        else:
            dst.pop(h, None)


def reduce_row(row, basis):
    out = row.copy()
    for pivot in sorted(basis):
        if out.get(pivot):
            add(out, basis[pivot], -out[pivot])
    return out


def insert(basis, row):
    out = reduce_row(row, basis)
    if not out:
        return False
    pivot = min(out)
    scale = out[pivot]
    basis[pivot] = {h: value/scale for h,value in out.items()}
    return True


def echelon(rows):
    basis = {}
    for row in rows:
        insert(basis, row)
    return basis


def span_key(frame):
    span = {0}
    for vector in frame:
        old = tuple(span)
        span.update(value ^ vector for value in old)
    need(len(span) == 1 << len(frame), "every native frame basis is independent")
    return frozenset(span)


def kernel_lifts(rows, project):
    image = {}
    image_lifts = {}
    kernel = {}
    for original in rows:
        projected = project(original)
        lift = original.copy()
        for pivot in sorted(image):
            coefficient = projected.get(pivot)
            if coefficient:
                factor = -coefficient
                add(projected, image[pivot], factor)
                add(lift, image_lifts[pivot], factor)
        if projected:
            pivot = min(projected)
            scale = projected[pivot]
            image[pivot] = {h:v/scale for h,v in projected.items()}
            image_lifts[pivot] = {h:v/scale for h,v in lift.items()}
        else:
            insert(kernel, lift)
    return kernel, len(image)


def serialize_row(row):
    return {str(h): str(value) for h,value in sorted(row.items()) if value}


def frame_ranks(word):
    spans = [span_key(frame) for frame in word["frames"]]
    dims = [len(frame) for frame in word["frames"]]
    for ins in word["program"]:
        if ins[0] == "MOVE":
            old, new = ins[2:4]
            need(spans[old] <= spans[new] or spans[new] <= spans[old],
                 "every MOVE source/target pair is nested")
    n = word["public"]
    mains = (set(word["live"]) | {h+112 for h in word["live"]} |
             set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"]))
    helpers = set(range(n))-mains
    target_ranks = {}
    for h in helpers:
        old, new = word["initial"][h], word["final"][h]
        need(spans[old] <= spans[new] or spans[new] <= spans[old],
             "every helper entrance/final pair is nested")
        target_ranks[h] = abs(dims[old]-dims[new])
    return spans, dims, mains, helpers, target_ranks


def main_projection_screen(word, spans, dims, mains, helpers):
    public_count = word["public"]
    move_events = [(e, ins) for e,ins in enumerate(word["program"]) if ins[0] == "MOVE"]
    destination_keys = {spans[ins[3]] for _,ins in move_events}
    history = {key:{} for key in destination_keys}
    rows = [{h:Q(1)} for h in range(public_count)] + [None]*word["owned_fields"]
    charts = list(word["initial"])+[None]*word["owned_fields"]
    for h, frame in enumerate(word["initial"]):
        key=spans[frame]
        if key in history and h in mains:
            insert(history[key], {h:Q(1)})

    records=[]
    helper_only=[]
    public_hits=[]
    op_counts=Counter()
    for event,ins in enumerate(word["program"]):
        op, owner=ins[:2]
        op_counts[op]+=1
        if op=="MOVE":
            old,new=ins[2:4]
            need(charts[owner]==old and rows[owner] is not None,"MOVE live source frame")
            target=rows[owner].copy()
            target_main={h:value for h,value in target.items() if h in mains}
            rank=abs(dims[old]-dims[new])
            key=spans[new]
            main_hist=history[key]
            if not target_main:
                helper_only.append(event)
                kind="helper_only"
            elif reduce_row(target_main,main_hist):
                kind="main_miss"
            else:
                kind="main_hit"
                if not ins[4] and rank>0:
                    record={"event":event,"owner":owner,"source":old,"destination":new,
                            "owned":bool(ins[4]),"target_rank":rank,
                            "main_history_rank":len(main_hist),"main_support":len(target_main)}
                    public_hits.append(record)
            if target_main:
                records.append({"event":event,"owned":bool(ins[4]),"target_rank":rank,"class":kind})
            rows[owner]=target
            charts[owner]=new
            if key in history and target_main:
                insert(history[key],target_main)
        elif op=="INIT":
            need(owner>=public_count and charts[owner] is None and rows[owner] is None,"INIT owned lifecycle")
            charts[owner],rows[owner]=ins[2],{}
        elif op=="CLEAR":
            need(owner>=public_count and charts[owner]==ins[2] and rows[owner] is not None,"CLEAR owned lifecycle")
            charts[owner],rows[owner]=None,None
        elif op=="SCALE":
            need(charts[owner]==ins[3] and rows[owner] is not None,"SCALE coframe")
            coefficient=Q(ins[2]);need(coefficient,"nonzero SCALE")
            rows[owner]={h:coefficient*v for h,v in rows[owner].items() if coefficient*v}
        elif op in ("ADD","COPY"):
            donor=ins[2]
            need(owner!=donor and charts[owner]==charts[donor]==ins[4],"coframed scalar contact")
            if op=="COPY":need(owner>=public_count and not rows[owner],"COPY zero owned destination")
            add(rows[owner],rows[donor],Q(ins[3]))
        else:
            raise ValueError("unknown native opcode")
    need(charts==list(word["final"])+[None]*word["owned_fields"],"final owner chart map")
    need(len(move_events)==6279,"all 6,279 MOVE targets processed")
    need(len(helper_only)==468,"fresh helper-only MOVE count")

    classes=Counter(r["class"] for r in records)
    classes_by_owner=Counter((r["class"],"owned" if r["owned"] else "public") for r in records)
    ranks_by_class=Counter((r["class"],r["target_rank"]) for r in records)
    ranks_by_class_owner=Counter((r["class"],"owned" if r["owned"] else "public",r["target_rank"])
                                for r in records)
    public_rank_counts=Counter(r["target_rank"] for r in public_hits)
    selected=[]
    for rank in range(9,0,-1):
        group=sorted((r for r in public_hits if r["target_rank"]==rank),key=lambda r:r["event"])
        selected.extend(group[:MAX_PER_RANK])
    selected.sort(key=lambda r:(-r["target_rank"],r["event"]))
    return {"records":records,"helper_only_events":helper_only,"public_hits":public_hits,
            "selected":selected,"classes":dict(classes),
            "classes_by_owner":{f"{c}|{o}":n for (c,o),n in classes_by_owner.items()},
            "ranks_by_class":{f"{c}|{r}":n for (c,r),n in ranks_by_class.items()},
            "ranks_by_class_owner":{f"{c}|{o}|{r}":n for (c,o,r),n in ranks_by_class_owner.items()},
            "public_hit_rank_counts":dict(sorted(public_rank_counts.items())),
            "move_count":len(move_events),"operation_counts":dict(op_counts)}


def _solve_relation(row, history_rows, target):
    all_rows=list(history_rows)+[target]
    target_index=len(history_rows)
    basis={};expressions={}
    for index,original in enumerate(all_rows):
        value=original.copy();expr={index:Q(1)}
        for pivot in sorted(basis):
            coefficient=value.get(pivot)
            if coefficient:
                add(value,basis[pivot],-coefficient)
                add(expr,expressions[pivot],-coefficient)
        if value:
            pivot=min(value);scale=value[pivot]
            basis[pivot]={h:v/scale for h,v in value.items()}
            expressions[pivot]={i:v/scale for i,v in expr.items()}
    residual=row.copy();expr={}
    for pivot in sorted(basis):
        coefficient=residual.get(pivot)
        if coefficient:
            add(residual,basis[pivot],-coefficient)
            add(expr,expressions[pivot],coefficient)
    need(not residual,"helper relation lies in full history plus target span")
    alpha=expr.get(target_index,Q(0))
    need(alpha,"enabling relation has nonzero target coefficient")
    normalized={h:value/alpha for h,value in row.items()}
    history_coefficients={i:str(-value/alpha) for i,value in expr.items()
                          if i<target_index and value}
    check=normalized.copy()
    for i,coefficient in expr.items():
        if i<target_index:
            add(check,history_rows[i],-coefficient/alpha)
    need(check==target,"exact relation identity c = u/alpha - history combination")
    return normalized,history_coefficients,str(alpha)


def _minimum_enabling_relation(L, P_helper, target_ranks):
    """Minimum one-row basis price among enabling representatives outside P_H."""
    L_rows=list(L.values());PH_rows=list(P_helper.values())
    need(len(L_rows)==len(PH_rows)+1,
         "single cache adds one helper relation modulo prior helper history")
    support=set().union(*(set(row) for row in L_rows))
    need(support,"nonzero helper-extension support")
    minimum=min(target_ranks[h] for h in support)
    cheapest=sorted(h for h in support if target_ranks[h]==minimum)
    chosen=None
    for row in L_rows:
        if any(row.get(h) for h in cheapest) and reduce_row(row,P_helper):
            chosen=row.copy()
            break
    if chosen is None:
        # A cheapest coordinate may occur only in the already observed
        # helper-history subspace. Add a genuine quotient direction to that
        # history vector. This remains outside P_H and keeps the cheap column,
        # so one sacrificed target of rank `minimum` suffices.
        history_row=next((row for row in L_rows
                          if any(row.get(h) for h in cheapest) and not reduce_row(row,P_helper)),None)
        quotient_row=next((reduce_row(row,P_helper) for row in L_rows
                           if reduce_row(row,P_helper)),None)
        need(history_row is not None and quotient_row is not None,
             "cheapest support and new quotient direction exist")
        for coordinate in cheapest:
            if not history_row.get(coordinate):
                continue
            for scalar in (Q(1),Q(2)):
                candidate=quotient_row.copy()
                add(candidate,history_row,scalar)
                if candidate.get(coordinate):
                    chosen=candidate
                    break
            if chosen is not None:
                break
    need(chosen is not None,"an enabling representative uses a cheapest support column")
    need(reduce_row(chosen,L)=={},"minimum relation witness lies in L_E")
    need(reduce_row(chosen,P_helper),"minimum relation witness is not pre-existing history")
    need(min(target_ranks[h] for h in chosen)==minimum,"minimum support rank is attained")
    coordinate=next(h for h in cheapest if chosen.get(h))
    return minimum,chosen,{"minimum_paid_target_rank":minimum,
        "cheapest_helper_coordinate":coordinate,"L_dimension":len(L_rows),
        "prior_helper_history_dimension":len(PH_rows),
        "why_history_component_can_be_added":"Any p in P_H may be added to a new relation representative; it remains outside P_H and can expose the cheapest L support coordinate."}


def full_candidate_replay(word, spans, dims, mains, helpers, target_ranks, selected_events):
    selected=set(selected_events)
    selected_destinations={spans[word["program"][e][3]] for e in selected}
    arrivals={key:{} for key in selected_destinations}
    public_count=word["public"]
    rows=[{h:Q(1)} for h in range(public_count)]+[None]*word["owned_fields"]
    charts=list(word["initial"])+[None]*word["owned_fields"]
    for h,frame in enumerate(word["initial"]):
        key=spans[frame]
        if key in arrivals:insert(arrivals[key],{h:Q(1)})
    results={}
    for event,ins in enumerate(word["program"]):
        op,owner=ins[:2]
        if op=="MOVE":
            old,new=ins[2:4]
            need(charts[owner]==old and rows[owner] is not None,"candidate replay MOVE value")
            target=rows[owner].copy();key=spans[new]
            if event in selected:
                need(not ins[4],"selected public MOVE remains public")
                P=arrivals[key]
                full_miss=bool(reduce_row(target,P))
                target_main={h:v for h,v in target.items() if h in mains}
                main_basis=echelon({h:v for h,v in row.items() if h in mains} for row in P.values())
                need(target_main and not reduce_row(target_main,main_basis),"selected event remains main-history hit")
                rank=abs(dims[old]-dims[new])
                result={"event":event,"owner":owner,"source":old,"destination":new,
                    "target_rank":rank,"strict_history_rank":len(P),"full_history_miss":full_miss,
                    "target":serialize_row(target),
                    "history_basis":{str(p):serialize_row(r) for p,r in P.items()}}
                if full_miss:
                    extended={p:r.copy() for p,r in P.items()}
                    insert(extended,target)
                    L,main_rank=kernel_lifts(list(extended.values()),
                        lambda row:{h:v for h,v in row.items() if h in mains})
                    P_helper,_=kernel_lifts(list(P.values()),
                        lambda row:{h:v for h,v in row.items() if h in mains})
                    need(len(L)==len(extended)-main_rank,"cache L_E projection rank-nullity")
                    need(len(L)==len(P_helper)+1,"one new helper direction modulo prior helper history")
                    need(all(set(row)<=helpers for row in L.values()),"L_E is helper-only")
                    support=set().union(*(set(row) for row in L.values()))
                    minimum,witness,minimum_certificate=_minimum_enabling_relation(L,P_helper,target_ranks)
                    relation,history_coefficients,alpha=_solve_relation(witness,list(P.values()),target)
                    need(set(relation)<=helpers and min(target_ranks[h] for h in relation)==minimum,
                         "normalized enabling relation paid target rank")
                    result.update({"L_dimension":len(L),"prior_helper_history_dimension":len(P_helper),
                        "L_support":sorted(support),
                        "L_support_target_rank_histogram":dict(sorted(Counter(target_ranks[h] for h in support).items())),
                        "L_support_minimum_rank_without_history_quotient":min(target_ranks[h] for h in support),
                        "minimum_enabling_relation_rank":minimum,
                        "minimum_enabling_relation":serialize_row(relation),
                        "relation_history_basis_coefficients":history_coefficients,
                        "relation_target_coefficient_before_normalization":alpha,
                        "minimum_certificate":minimum_certificate})
                results[event]=result
            if key in arrivals:
                insert(arrivals[key],target)
            rows[owner]=target
            charts[owner]=new
        elif op=="INIT":
            need(owner>=public_count and charts[owner] is None and rows[owner] is None,"candidate replay INIT")
            charts[owner],rows[owner]=ins[2],{}
        elif op=="CLEAR":
            need(owner>=public_count and charts[owner]==ins[2] and rows[owner] is not None,"candidate replay CLEAR")
            charts[owner],rows[owner]=None,None
        elif op=="SCALE":
            need(charts[owner]==ins[3] and rows[owner] is not None,"candidate replay SCALE")
            coefficient=Q(ins[2]);need(coefficient,"candidate replay nonzero scale")
            rows[owner]={h:coefficient*v for h,v in rows[owner].items() if coefficient*v}
        elif op in ("ADD","COPY"):
            donor=ins[2]
            need(owner!=donor and charts[owner]==charts[donor]==ins[4],"candidate replay coframed contact")
            if op=="COPY":need(owner>=public_count and not rows[owner],"candidate replay COPY destination")
            add(rows[owner],rows[donor],Q(ins[3]))
        else:raise ValueError("unknown candidate replay opcode")
    need(set(results)==selected,"all selected candidate histories reconstructed")
    return results


def run():
    raw=WORD.read_bytes();need(sha256(raw).hexdigest()==WORD_SHA,"exact #7481 WORD bytes")
    word=json.loads(gzip.decompress(raw))
    payload=sha256(json.dumps(word,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    need(payload=="64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8",
         "canonical native payload")
    spans,dims,mains,helpers,target_ranks=frame_ranks(word)
    screen=main_projection_screen(word,spans,dims,mains,helpers)
    selected=screen["selected"]
    screen_summary={"move_count":screen["move_count"],"screen_classes_all_moves":screen["classes"],
        "screen_classes_by_owner":screen["classes_by_owner"],
        "screen_rank_histogram":screen["ranks_by_class"],
        "screen_rank_histogram_by_owner":screen["ranks_by_class_owner"],
        "helper_only_move_count":len(screen["helper_only_events"]),
        "public_nonzero_main_history_hit_rank_counts":screen["public_hit_rank_counts"],
        "selected_count":len(selected),"selected_events":[r["event"] for r in selected]}
    full=full_candidate_replay(word,spans,dims,mains,helpers,target_ranks,
                               [record["event"] for record in selected])

    caller_raw=CALLER.read_bytes();need(sha256(caller_raw).hexdigest()==CALLER_SHA,"exact signed caller")
    caller=json.loads(caller_raw)
    calls=sum(event[0]=="J" for event in caller["events"])
    need(calls==caller["stages"]==17,"actual 17-call signed caller")
    invoice_raw=INVOICE.read_bytes();need(sha256(invoice_raw).hexdigest()==INVOICE_SHA,"complete price invoice")
    invoice=json.loads(invoice_raw)
    need(invoice["new_native"]==payload,"complete invoice native binding")
    base={int(r):int(n) for r,n in invoice["after"]["T"].items()}
    for r,n in invoice["after"]["P"].items():
        base[int(r)]=base.get(int(r),0)-int(n)
    base={r:n for r,n in base.items() if n}
    price_path=PACKAGE/"verifier/integer_prices.py"
    spec=importlib.util.spec_from_file_location("wave52_integer_prices",price_path)
    power=importlib.util.module_from_spec(spec);sys.modules[spec.name]=power;spec.loader.exec_module(power)
    baseline=power.moment(base)
    need(baseline[1]<0,"fixed baseline is negative at .0038")
    required=(-baseline[1]/calls,-baseline[0]/calls)

    candidate_results=[]
    for record in selected:
        result=full[record["event"]]
        result.update({"screen_main_history_rank":record["main_history_rank"],
                       "screen_target_rank":record["target_rank"]})
        if not result["full_history_miss"]:
            result["optimistic_single_cache_saving_0038"]={"exact":["0","0"],
                "decimal_display_only":["0","0"],"classification":"already_in_full_history"}
        else:
            profile=Counter({result["target_rank"]:1})
            profile[result["minimum_enabling_relation_rank"]]-=1
            profile={r:n for r,n in profile.items() if n}
            delta=power.moment(profile)
            result["optimistic_single_cache_saving_profile"]={str(r):n for r,n in profile.items()}
            result["optimistic_single_cache_saving_0038"]=power.display(delta)
            result["optimistic_single_cache_saving_classification"]=(
                "positive" if delta[0]>0 else "negative" if delta[1]<0 else "interval_overlap")
        candidate_results.append(result)

    best_positive=max(
        ((Q(result["optimistic_single_cache_saving_0038"]["exact"][1]), result)
         for result in candidate_results
         if result.get("optimistic_single_cache_saving_classification")=="positive"),
        default=(Q(0),None), key=lambda pair:pair[0])
    result_doc={
        "status":"FRESH_EXACTQ_PUBLIC_MAIN_HISTORY_SCREEN_WITH_BOUNDED_FULL_RELATION_SAMPLE",
        "source_sha256":WORD_SHA,"source_payload_sha256":payload,
        "caller_sha256":CALLER_SHA,"invoice_sha256":INVOICE_SHA,"native_calls":calls,
        "frame_count":len(word["frames"]),"move_count":screen["move_count"],
        "all_move_frame_pairs_nested":True,
        "main_helper_count":{"main":len(mains),"helper":len(helpers)},
        "screen_classes_all_moves":screen["classes"],
        "screen_classes_by_owner":screen["classes_by_owner"],
        "screen_rank_histogram":screen["ranks_by_class"],
        "screen_rank_histogram_by_owner":screen["ranks_by_class_owner"],
        "helper_only_move_count":len(screen["helper_only_events"]),
        "public_nonzero_main_history_hit_rank_counts":screen["public_hit_rank_counts"],
        "selected_rule":f"up to {MAX_PER_RANK} earliest public positive-rank main-history hits per MOVE-rank, rank descending",
        "selected_count":len(selected),"selected_events":[r["event"] for r in selected],
        "selected_full_history_hits":sum(not x["full_history_miss"] for x in candidate_results),
        "selected_full_history_misses":sum(x["full_history_miss"] for x in candidate_results),
        "candidate_relations":candidate_results,
        "baseline_full_signed_moment_0038":power.display(baseline),
        "required_net_native_saving_per_call_0038":power.display(required),
        "best_positive_sample_saving_upper_0038":power.display((best_positive[0],best_positive[0])),
        "best_positive_event":None if best_positive[1] is None else best_positive[1]["event"],
        "limitations":"Only the all-MOVE main-projection screen is exhaustive. Full P_E/L_E and one-relation prices are computed for the deterministic bounded sample only. Savings are optimistic rank-price bounds, ignore preparation/ordinary/lifetime costs and do not establish a realizable relation, shared multi-target relation, source admission, or kappa.",
    }
    return result_doc
