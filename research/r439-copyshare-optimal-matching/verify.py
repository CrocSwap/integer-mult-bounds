#!/usr/bin/env python3
"""Check the matching bound, dirty boundary and full finite invoice without a solver.

Apache-2.0; prepared for @CubeJerry with substantial OpenAI Codex assistance.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import itertools
import json
import struct
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


C = module("copyshare_core", HERE / "core.py")
need = C.need


def read_json(path):
    def pairs(items):
        out = {}
        for key, value in items:
            need(key not in out, "duplicate JSON key")
            out[key] = value
        return out
    def bad_constant(value):
        raise ValueError("nonfinite JSON: " + value)
    return json.loads(path.read_text(), object_pairs_hook=pairs, parse_constant=bad_constant)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def source_pins():
    manifest = read_json(HERE / "SOURCES.json")
    need(manifest["base_commit"] == "997e6a9ca7b4f95d50e366f61412fd640d72a88a", "base pin")
    for entry in manifest["files"]:
        if entry["usage"] == "input":
            actual = hashlib.sha256((ROOT / entry["path"]).read_bytes()).hexdigest()
            need(actual == entry["sha256"], "source pin: " + entry["path"])


def support_sets(word):
    """Independent set-valued graph reconstruction, not packed nomination columns."""
    v = word["v"]
    need(len(word["D"]) == v, "one original gate per target")
    need(sorted(g[1] for g in word["D"]) == list(range(v,2*v)), "target permutation")
    pool = set().union(*(set(g[2]) for g in word["D"])) - set(word["ret"])
    need(all(type(a) is int and 2*v <= a < 2*v+word["R"] for a in pool), "helper pool")
    return {a: {d for _, d, src in word["D"] if a in src} for a in sorted(pool)}


def gain(supports, a, b):
    return len(supports[b]) - len(supports[a] ^ supports[b]) - 2


def check_dual(supports, dual):
    prices = dual["vertex_prices_2"]
    need(all(isinstance(p,list) and len(p)==2 and all(type(x) is int for x in p)
             for p in prices), "vertex price type")
    need([p[0] for p in prices] == sorted(supports), "vertex price domain")
    q = dict(prices)
    need(all(x >= 0 for x in q.values()), "negative vertex price")
    sets = []
    for item in dual["odd_sets"]:
        vertices, z = item["vertices"], item["price_2"]
        need(type(z) is int and z > 0, "odd-set price")
        need(all(type(v) is int for v in vertices), "odd-set vertex type")
        need(len(vertices) == len(set(vertices)) and len(vertices) >= 3 and len(vertices)%2 == 1,
             "odd-set cardinality")
        need(set(vertices) <= set(supports), "odd-set domain")
        sets.append((set(vertices), z))
    positive = 0
    for a,b in itertools.combinations(supports, 2):
        weight = max(gain(supports,a,b), gain(supports,b,a))
        positive += weight > 0
        cover = q[a]+q[b]+sum(z for vertices,z in sets if a in vertices and b in vertices)
        need(2*weight <= cover, "dual edge inequality")
    objective = sum(q.values()) + sum((len(v)//2)*z for v,z in sets)
    return {"vertices":len(q), "unordered_edges":len(q)*(len(q)-1)//2,
            "positive_unordered_edges":positive, "odd_sets":len(sets),
            "objective_2":objective}


def check_primal(word, supports, pairs, objective):
    C.construct(word,pairs)  # Validate domain and disjointness before summing.
    saving = sum(gain(supports,a,b) for a,b in pairs)
    need(2*saving == objective, "primal does not attain dual")
    return saving


def d_rows(word):
    n = 2*word["v"]+word["R"]
    rows = [1 << j for j in range(n)]
    for f,d,src in word["D"]:
        need(f == 0, "D frame")
        need(word["v"] <= d < n and src and d not in src and len(src)==len(set(src)), "D operands")
        need(all(word["v"] <= s < n for s in src), "D source access")
        need(not (d >= 2*word["v"] and any(s < 2*word["v"] for s in src)), "D target feedback")
        for s in src:
            rows[d] ^= rows[s]
    return rows


def check_d_columns(word, expected):
    """Numeric input-column engine independent of row-vector substitution."""
    n = len(expected)
    flat = [(d,s) for _,d,src in word["D"] for s in src]
    for j in range(n):
        state = 1 << j
        for d,s in flat:
            if (state >> s) & 1:
                state ^= 1 << d
        want = sum(((row >> j)&1) << r for r,row in enumerate(expected))
        need(state == want, "D input column")


def check_complete(word):
    v, n = word["v"], 2*word["v"]+word["R"]
    want = [(1 << j) ^ ((1 << (j-v)) if v <= j < 2*v else 0) for j in range(n)]
    for reverse in (False,True):
        rows = [1 << j for j in range(n)] + [0]
        for op,d,s in C.ordered(C.instructions(word),reverse):
            if op == "add":
                rows[d] ^= rows[s]
            elif op == "copy":
                need(rows[d]==0,"COPY live destination")
                rows[d] = rows[s]
            else:
                need(rows[d]==rows[s],"ERASE changed copy")
                rows[d] = 0
        need(rows[:-1]==want and rows[-1]==0,"complete dirty boundary")


def frame_paths(word):
    frames = [set(x) for x in word["frames"]]
    paths = [[x] for x in word["start"]]
    for sec in "DABC":
        for f,d,src in word[sec]:
            for r in (d,*src):
                if f != paths[r][-1]:
                    need(frames[paths[r][-1]] < frames[f], "frame path inclusion")
                    paths[r].append(f)
    for r,f in enumerate(word["final"]):
        if f != paths[r][-1]:
            need(frames[paths[r][-1]] < frames[f], "final frame inclusion")
            paths[r].append(f)
    return paths


def exporter_invoice(word):
    """Reconcile every ADD/COPY/ERASE and paid MOVE with the unchanged exporter."""
    with tempfile.TemporaryDirectory(prefix="copyshare-export-") as temp:
        tmp = Path(temp)
        (tmp/"word.json").write_text(canonical(word))
        proc = subprocess.run([sys.executable,"-B",str(ROOT/"research/e8-bit-carrier-skeleton/code/bit/export_records.py"),
                               str(tmp/"word.json"),str(tmp/"out")],capture_output=True,text=True,timeout=120)
        need(proc.returncode==0,"exporter failed: "+proc.stderr)
        blob = (tmp/"out/249-records.bin").read_bytes()
        records = list(struct.iter_unpack("<6i",blob))
        events, profile, copies = [], Counter(), []
        for op,a,b,c,d,e in records:
            if op==0:
                need(d>0,"exporter nonpositive MOVE")
                profile[d]+=1
            elif op==1:
                need(c==1,"exporter ADD coefficient")
                events.append(("add",a,b))
            elif op==2:
                profile[e]+=1
                copies.append(e)
                events.append(("copy",b,a))
            elif op==3:
                events.append(("erase",b,a))
            else:
                raise ValueError("exporter opcode")
        need(events==C.instructions(word),"exporter arithmetic stream differs")
        # Independent positive recurrence over record indices and opcodes.
        peaks = []
        for reverse in (False,True):
            values = [1]*(2*word["v"]+word["R"])+[0]
            peak = 1
            for op,a,b,c,d,e in (reversed(records) if reverse else records):
                if op==1:
                    values[a]+=values[b]
                    peak=max(peak,values[a])
                elif (op==2 and not reverse) or (op==3 and reverse):
                    values[b]=values[a]
                    peak=max(peak,values[b])
                elif op in (2,3):
                    values[b]=0
            peaks.append(peak)
        bill = C.invoice(word)
        need(peaks==[bill["F"],bill["B"]],"exporter envelope differs")
        return {"records":len(records),"sha256":hashlib.sha256(blob).hexdigest(),
                "paid_profile":{str(k):v for k,v in sorted(profile.items())},"copy_ranks":copies}


def reject(name, callback, fragment):
    try:
        callback()
    except ValueError as exc:
        need(fragment in str(exc),name+": unexpected failure: "+str(exc))
        return name
    raise ValueError(name+": mutant accepted")


def run():
    source_pins()
    word = C.load_word()
    receipt = read_json(HERE/"MATCHING.json")
    supports = support_sets(word)
    dual = check_dual(supports, receipt["primary_dual"])
    need(receipt["nodes"]==dual["vertices"] and receipt["positive_unordered_edges"]==dual["positive_unordered_edges"],"census receipt")
    need([x["variant"] for x in receipt["nominations"]]==["sorted","seed3","forward_proxy"],"bounded nomination inventory")
    expected_d = d_rows(word)
    base_paths = frame_paths(word)
    bills = {"base":C.invoice(word)}
    for row in receipt["nominations"]:
        saving = check_primal(word,supports,row["pairs"],dual["objective_2"])
        candidate = C.construct(word,row["pairs"])
        need(d_rows(candidate)==expected_d,"D boundary")
        check_d_columns(candidate,expected_d)
        check_complete(candidate)
        need(frame_paths(candidate)==base_paths,"changed frame paths")
        bill = C.invoice(candidate)
        need(canonical(bill)==canonical(row["invoice"]),"nomination invoice receipt")
        need(row["saving"]==saving==bills["base"]["ADDs"]-bill["ADDs"],"saving invoice")
        need(bill["local_guard"] and bill["nine_stage_guard"],"precision guard")
        bills[row["variant"]]=bill
    greedy = read_json(ROOT/"research/h2sem-matching-f-invoice/MATCHING7.json")
    bills["greedy7"] = C.invoice(C.construct(word,greedy["pairs"]))
    need(bills["greedy7"]["ADDs"]==18060 and bills["greedy7"]["F"]==73805 and bills["greedy7"]["B"]==1187790,"PR2487 calibration")
    selected = min(receipt["nominations"],key=lambda r:(-r["saving"],r["invoice"]["F"],r["invoice"]["B"],r["variant"]))
    need(receipt["selected"]==selected["variant"],"selected nomination")
    need(all(selected["invoice"][key] < bills["greedy7"][key] for key in ("ADDs","F","B")),
         "selected point does not strictly dominate PR2487")
    candidate = C.construct(word,selected["pairs"])
    check_complete(word)
    for key in word:
        if key!="D":
            need(candidate[key]==word[key],"changed non-D field")
    checker = module("selected_xcheck",ROOT/"research/e8-bit-p111-tuned/code/xcheck_p.py")
    wbase,labels,flow,hyp,con,_ = checker.check(word)
    need(all(hyp.values()) and all(con.values()),"virtual splice interface")
    wc = checker.Word(candidate)
    wc.full()
    hc,cc,_ = wc.interface()
    failed = sorted(k for k,v in {**hc,**cc}.items() if not v)
    need(failed==["H2_D_frame0_targets_from_helpers","K_equals_D"],"candidate legacy flags")
    exports = {"base":exporter_invoice(word),"selected":exporter_invoice(candidate)}
    expected_profile = {"1":1323,"2":1342,"3":79,"4":44,"5":102,"6":11,"7":19}
    for out in exports.values():
        need(out["paid_profile"]==expected_profile and out["copy_ranks"]==[7]*9,"exported paid profile")
    own = Counter(wbase.fdim[b]-wbase.fdim[a] for path in base_paths for a,b in itertools.pairwise(path))
    own.update(x["rank"] for x in flow["totals"])
    need({str(k):v for k,v in sorted(own.items())}==expected_profile,"independent paid profile")
    controls=[]
    bad=copy.deepcopy(receipt["primary_dual"])
    bad["vertex_prices_2"]=[[a,0] for a in supports]
    bad["odd_sets"]=[]
    controls.append(reject("underpriced_dual",lambda:check_dual(supports,bad),"dual edge"))
    bad=copy.deepcopy(receipt["primary_dual"])
    bad["vertex_prices_2"][0][1]=-1
    controls.append(reject("negative_vertex_price",lambda:check_dual(supports,bad),"negative vertex"))
    bad=copy.deepcopy(receipt["primary_dual"])
    bad["odd_sets"].append({"vertices":list(supports)[:4],"price_2":2})
    controls.append(reject("even_odd_set",lambda:check_dual(supports,bad),"odd-set cardinality"))
    pairs=selected["pairs"]
    controls.append(reject("reused_helper",lambda:C.construct(word,pairs+[pairs[0]]),"pair overlap"))
    controls.append(reject("missing_pair_not_optimal",lambda:check_primal(word,supports,pairs[1:],dual["objective_2"]),"primal does not attain"))
    badword=copy.deepcopy(candidate)
    badword["D"].pop()
    controls.append(reject("missing_restoration",lambda:need(d_rows(badword)==expected_d,"D boundary"),"D boundary"))
    badword=copy.deepcopy(candidate)
    badword["D"][len(pairs)][2].pop()
    controls.append(reject("missing_middle_operand",lambda:need(d_rows(badword)==expected_d,"D boundary"),"D boundary"))
    badword=copy.deepcopy(candidate)
    badword["D"][0][0]=1
    controls.append(reject("nonzero_D_frame",lambda:d_rows(badword),"D frame"))
    badword=copy.deepcopy(candidate)
    badword["D"][0][2]=[0]
    controls.append(reject("source_read",lambda:d_rows(badword),"D source access"))
    badword=copy.deepcopy(candidate)
    badword["D"][0][2]=[word["v"]]
    controls.append(reject("target_feedback_outside_contract",lambda:d_rows(badword),"D target feedback"))
    return {"status":"PASS_R439_COPYSHARE_OPTIMAL_MATCHING","dual":dual,
            "optimal_saving":dual["objective_2"]//2,"selected":selected["variant"],
            "selected_pairs":len(pairs),"bills":bills,"columns":len(expected_d),
            "exports":exports,"legacy_failures":failed,"controls":controls,
            "candidate_canonical_sha256":hashlib.sha256(canonical(candidate).encode()).hexdigest(),
            "paid_rank_mass":sum(int(k)*v for k,v in expected_profile.items()),"new_kappa":False}


if __name__=="__main__":
    result=run()
    expected=read_json(HERE/"EXPECTED.json")
    need(canonical(result)==canonical(expected),"complete expected receipt mismatch")
    bill=result["bills"][result["selected"]]
    print(f'{result["status"]} saving={result["optimal_saving"]} ADDs={bill["ADDs"]} '
          f'F={bill["F"]} B={bill["B"]} columns={result["columns"]} '
          f'edges={result["dual"]["unordered_edges"]} controls={len(result["controls"])} no_new_kappa')
