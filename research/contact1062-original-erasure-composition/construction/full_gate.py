# SPDX-License-Identifier: Apache-2.0
"""Full original-interface replay and exact signed route replay for the labelled word."""
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
from runpy import run_path
from gate import GRID, HEADS, ROOT, canonical, need, pack, roles, sha

def compare(a,b,label):
    if a!=b:
        j=next(j for j in sorted(a.keys()|b.keys()) if a.get(j,0)!=b.get(j,0))
        raise ValueError(dict(check=label,input=j,reference=str(Fraction(a.get(j,0),GRID)),
                             observed=str(Fraction(b.get(j,0),GRID))))

def clockmap(seqs):
    maps={n:{t:i for i,(t,e) in enumerate(s)} for n,s in seqs.items()}
    keys=list(dict.fromkeys(t for seq in seqs.values() for t,e in seq))
    edits={t for t in keys if not isinstance(t,int) or any(t not in m for m in maps.values())}
    for t in keys:
        if t not in edits and len({tuple(seqs[n][m[t]][1]) for n,m in maps.items()})>1: edits.add(t)
    data={"columns":list(maps),"unchanged_intervals":[],"anchors":[]}
    for t in keys:
        clocks=[m.get(t) for m in maps.values()]
        if t in edits:
            data["anchors"].append(dict(origin=t,clocks=clocks,
                events=[None if i is None else seqs[n][i][1] for n,i in zip(maps,clocks)]))
            continue
        shifts=[i-t for i in clocks]
        runs=data["unchanged_intervals"]
        if runs and runs[-1][1]+1==t and runs[-1][2]==shifts: runs[-1][1]=t
        else: runs.append([t,t,shifts])
    return maps,data

def full(word,seqs,repl,args):
    receipt=json.loads((ROOT/"first-receipt.json").read_bytes())
    need(receipt["status"]=="PASS_FIRST" and receipt["provenance_sha256"]==
         sha((ROOT/"first-provenance.json.gz").read_bytes()),"first gate receipt or provenance")
    prev=args.source7644
    v=run_path(str(prev/"independent.py"))
    engine=prev/"retained/pr7605/retained/role902/independent/engines"
    maps,clock=clockmap(seqs)
    n=word["public"]
    base=seqs["7605"]
    owned=[t for t,e in base if max(roles(e))>=n]
    # Every exterior source read after each complete repair. For the two
    # contact exits also include receiver-side and MOVE observations.
    restore={46:47958,588:45376,1456:45376,82:42194,185:43586,196:43586,
             134:seqs["7642"][42086][0],329:seqs["7642"][41142][0]}
    retained=[(t,r) for t,e in base for r in roles(e) if r in restore and t>restore[r]
              and ((e[0] in ("COPY","ADD") and e[2]==r) or r in (134,329))]
    common={t for t,r in retained}|set(owned)
    audits={}
    physical=[]
    report={}
    for name in ("7605","7643","7644","combined"):
        seq=seqs[name]
        prog=dict(word,program=[e for t,e in seq])
        idx=maps[name]
        need(all(t in idx for t in common),"removed observable clock")
        public_watch={idx[t] for t in common}
        a=v["replay"](prog,public_watch,False)
        need(not a["bad_helpers"],f"{name} dirty helper returns {a['bad_helpers']}")
        audits[name]=a
        if name=="7605": continue
        ref=audits["7605"]
        for k in ("owned_events","lifetime","peak","rises","copies","targets"):
            need(a[k]==ref[k],f"{name} {k} schedule")
        need([t for t,e in seq if max(roles(e))>=n]==owned,f"{name} ordered owned tags")
        for t in owned:
            for r,left,right in zip(roles(base[t][1]),ref["readings"][t],a["readings"][idx[t]]):
                compare(dict(left),dict(right),[name,"private entry",t,idx[t],r])
        for t,r in retained:
            k=roles(base[t][1]).index(r)
            compare(dict(ref["readings"][t][k]),dict(a["readings"][idx[t]][k]),
                    [name,"exterior return",t,idx[t],r])
        need(len(a["erased"])==len(ref["erased"])==74,"erasure count")
        for i,(x,y) in enumerate(zip(ref["erased"],a["erased"])):
            need(x[:2]==y[:2],f"{name} erasure label {i}")
            compare(dict(x[2]),dict(y[2]),[name,"erased",i,x[:2]])
        for r,(x,y) in enumerate(zip(ref["rows"],a["rows"])):
            compare(x,y,[name,"output",r])
    a=audits["combined"]
    result_rows=[sorted(row.items()) for row in a["rows"]]
    report.update(private_events=len(owned),private_pre_operands=sum(len(roles(base[t][1])) for t in owned),
        private_exit_rule="same full pre-operand rows and same instruction determine every post-destination",
        private_trace_sha256=sha(canonical([[t,base[t][1],audits["7605"]["readings"][t]] for t in owned])),
        erasures=len(a["erased"]),nonzero_erasures=sum(bool(x[2]) for x in a["erased"]),
        clear44=a["erased"][44],grid_denominator=GRID,erasures_sha256=sha(canonical(a["erased"])),
        owned_peak=a["peak"],owned_fields=word["owned_fields"],lifetimes=len(a["lifetime"]),copy_zero=a["copies"],
        endpoints=len(a["rows"]),public=n,helpers=sum(a["targets"].values()),endpoint_sha256=sha(canonical(result_rows)),
        retained_returns=[[t,maps["combined"][t],r] for t,r in retained],
        retained_sha256=sha(canonical([[t,r,audits["7605"]["readings"][t][roles(base[t][1]).index(r)]] for t,r in retained])))
    # Authenticate every differing pair, including main 46 and the two contact streams.
    source=engine/"clifford_exact.py"
    def contraction(legs):
        changes=[{"old":[["MOVE",r,x,y,False],["MOVE",r,y,z,False]],
                  "new":[["MOVE",r,x,z,False]]} for r,x,y,z in legs]
        for ch in changes:
            for name,key in (("7605","old"),("combined","new")):
                for e in ch[key]:
                    need(any(event==e for _,event in seqs[name]),f"{name} absent phase route {e}")
        return v["physical"](word["frames"],changes,source)
    physical.append(contraction([(82,740,1062,1071),(185,401,1062,922),(46,914,245,127)]))
    contact=run_path(str(args.contact_check))
    for file in ("clifford_exact.py","native_verify.py"):
        need(sha((engine/file).read_bytes())==contact["RAW_PINS"]["engines/"+file],"contact engine "+file)
    old=[tuple(e[2:4]) for e in contact["OLD"].values() if e[0]=="MOVE"]
    new=[tuple(e[2:4]) for e in contact["NEW"].values() if e and e[0]=="MOVE"]
    need(repl==contact["NEW"],"contact phase literal")
    physical.append(contact["phase_check"](word,old,new,engine,{}))
    report["physical"]=physical
    # Two independently located legal scalar faults, each on the one frozen word.
    controls=[]
    for needle,target in ((["ADD",196,991,"-1/16",3],196),(["ADD",185,7,"-5/4",922],185)):
        tag,i=next((t,i) for i,(t,e) in enumerate(seqs["combined"]) if isinstance(t,tuple) and t[0]==44 and e==needle)
        seq=seqs["combined"]
        prog=dict(word,program=[e for _,e in seq])
        mutant=v["replay"](prog,set(),False,(i,[*needle[:3],"1",needle[-1]]))
        x=a["rows"][target]; y=mutant["rows"][target]
        j=next((j for j in sorted(x.keys()|y.keys()) if x.get(j,0)!=y.get(j,0)),None)
        need(j is not None,f"accepted coefficient fault {i}")
        controls.append(dict(origin=tag,clock=i,old=needle,new_scalar="1",output=target,input=j,
                             expected=str(Fraction(x.get(j,0),GRID)),mutant=str(Fraction(y.get(j,0),GRID))))
    raw=canonical(dict(word,program=[e for t,e in seqs["combined"]]))
    data=pack(raw)
    file=ROOT/"candidate.json.gz"
    if file.exists(): need(file.read_bytes()==data,"existing candidate differs")
    else:
        temp=ROOT/"candidate.pending"
        temp.write_bytes(data); temp.replace(file)
    (ROOT/"clock-map.json").write_bytes(canonical(clock))
    report.update(status="PASS_FULL",heads=HEADS,events=len(seqs["combined"]),canonical_sha256=sha(raw),
        gzip_sha256=sha(data),first_provenance_sha256=receipt["provenance_sha256"],controls=controls,
        clock_map_sha256=sha(canonical(clock)),generator="gate.py build plus full_gate.py freeze",
        method="exact integer grid on arbitrary public inputs, all private and returned rows in original frame, exact signed Gaussian route compilation")
    (ROOT/"full-receipt.json").write_bytes(canonical(report))
    return {k:report[k] for k in ("status","events","canonical_sha256","gzip_sha256","private_events","erasures","endpoints","controls")}
