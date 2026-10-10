"""Portable pure functions extracted from the reviewed complex checks; no historical receipt readers."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
Q=Fraction
from hashlib import sha256
from pathlib import Path
from math import prod
import gzip,json,sys

BASE = dict(h=22, v=1320, R=9412, cst=440, N=262944)
EXPECTED_H = {1:29178,2:12667,3:9988,4:3839,5:1976,6:1491,7:642,8:1478,
              9:404,10:805,11:353,12:1141,13:168,14:725,15:605,16:81,
              17:39,18:2640,19:1441,20:22}
class Reject(ValueError):
    pass

def need(ok, msg):
    if not ok:
        raise Reject(msg)

def digest(obj):
    return sha256(json.dumps(obj, separators=(",",":"), sort_keys=True).encode()).hexdigest()

def hist(counter):
    return {str(k):v for k,v in sorted(counter.items()) if v}

def role(r,v):
    return "x" if r < v else "y" if r < 2*v else "s"

def reduce_binary(x, frame):
    for b in frame:
        if x & (1 << (b.bit_length()-1)):
            x ^= b
    return x

def coeff(a,b, where):
    need(type(a) is int and type(b) is int and b>0, f"{where}: coefficient shape")
    q=Fraction(a,b)
    odd=q.denominator
    while odd%2==0:
        odd//=2
    need(odd in (1,3), f"{where}: literal coefficient outside dyadic/divisor-three grid")
    return q

def replay_label_counts(c):
    """Full finite LABEL walk only. Never multiplies the 12,052-square scalar map."""
    need(c.get("format")=="gcert/1", "format")
    need(all(c.get(k)==v for k,v in BASE.items()), "baseline parameter/count mismatch")
    h,v,R=c["h"],c["v"],c["R"]; n=2*v+R
    need(c.get("ext")==[], "baseline has no exterior-gauged helper inputs")
    frames=c["frames"]; dim=list(map(len,frames))
    need(len(frames)==18248, "baseline frame-table count")
    need(frames[0]==[] and frames[1]==[1<<i for i in range(h-1,-1,-1)], "zero/full frames")
    need(len({tuple(f) for f in frames})==len(frames), "duplicate frames")
    for f in frames:
        need(all(type(b) is int and 0<b<1<<h for b in f), "frame bit range")
        piv=[b.bit_length()-1 for b in f]
        need(all(piv[i]>piv[i+1] for i in range(len(piv)-1)), "frame pivot order")
        need(all(not(b>>p&1) for i,b in enumerate(f) for j,p in enumerate(piv) if i!=j),
             "frame is not reduced echelon")
    ports=c["ports"]
    need(len(ports)==v==len(set(ports)), "port count/uniqueness")
    need(all(type(p) is int and 0<p<(1<<h)-1 and p.bit_count()%2 for p in ports), "unit port/gap")
    start=c["start"]; final=c["final"]
    need(len(start)==len(final)==n, "live invocation role count")
    need(all(type(f) is int and 0<=f<len(frames) for f in start+final), "endpoint frame ID")
    for t,p in enumerate(ports):
        need(frames[start[t]]==[p] and final[t]==1, "X endpoint")
        need(start[v+t]==0 and dim[final[v+t]]==h-1 and
             all((p&u).bit_count()%2==0 for u in frames[final[v+t]]), "Y endpoint")
    need(all(f==0 for f in start[2*v:]) and all(f==1 for f in final[2*v:]), "helper endpoints")
    need(c["ret"] and len(c["ret"])==22, "temporary-center count")
    need([x[0] for x in c["ret"]]==list(range(22)), "center numbering")
    need(len({x[1] for x in c["ret"]})==22, "center retained slots repeat")
    need(c["scat"]=={"inside":[1,3],"outside":[-1,6]}, "baseline scatter rule")
    need(len(c["A"])==13123 and len(c["B"])==39177, "phase gate count")
    cur=start.copy(); pairs=set()
    by_role={r:Counter() for r in "xysc"}
    by_phase={p:Counter() for p in ("A","copy","B","final")}
    literal=Counter(); kind=Counter(); ybracket=Counter(); ypiv=set(); ytarget=set()
    totals={p:dict(gates=0,scalar_additions=0,register_visits=0,spectator_visits=0)
            for p in ("A","B")}
    transitions=0
    def climb(reg,new,phase):
        nonlocal transitions
        old=cur[reg]
        if old==new:
            return
        need(dim[old]<dim[new], f"{phase}: frame does not strictly climb")
        pair=(old,new)
        if pair not in pairs:
            need(all(reduce_binary(b,frames[new])==0 for b in frames[old]), f"{phase}: nonnested frames")
            pairs.add(pair)
        rank=dim[new]-dim[old]
        by_role[role(reg,v)][rank]+=1; by_phase[phase][rank]+=1
        cur[reg]=new;transitions+=1
    for phase in ("A","B"):
        for i,g in enumerate(c[phase]):
            where=f"{phase}[{i}]"
            need(isinstance(g,list) and len(g)>=4 and g[0] in ("out","in"), where+": gate shape")
            tag,f,pivot,terms=g[:4]
            need(len(g)==(5 if tag=="out" else 4), where+": gate arity")
            need(type(f) is int and 0<=f<len(frames), where+": frame ID")
            need(all(isinstance(x,list) and len(x)==3 for x in terms), where+": terms")
            spectators=g[4] if tag=="out" else []
            regs=[pivot]+[x[0] for x in terms]+spectators
            need(all(type(r) is int and 0<=r<n for r in regs) and len(set(regs))==len(regs),
                 where+": duplicate/out-of-range register")
            need(phase!="A" or all(not(v<=r<2*v) for r in regs), where+": Y role before scatter")
            totals[phase]["gates"]+=1
            totals[phase]["register_visits"]+=len(regs)
            totals[phase]["spectator_visits"]+=len(spectators)
            for reg,a,b in terms:
                target,source=(reg,pivot) if tag=="out" else (pivot,reg)
                sr,tr=role(source,v),role(target,v)
                need((sr,tr) in {("x","s"),("s","s"),("s","y"),("x","y"),("x","x"),("y","y")},
                     where+": forbidden role direction")
                need(phase!="A" or (sr,tr) in {("x","s"),("s","s")}, where+": phase A role direction")
                q=coeff(a,b,where)
                need(q!=0,where+": zero scalar addition")
                literal[str(q)]+=1;kind[f"{phase}:{sr}->{tr}"]+=1
                totals[phase]["scalar_additions"]+=1
                if sr==tr=="y":
                    ybracket[(source,target)]+=q;ypiv.add(source);ytarget.add(target)
            for r in regs:
                climb(r,f,phase)
        if phase=="A":
            cut=cur.copy()
            need(all(cur[v+t]==0 for t in range(v)), "scatter: Y role moved too early")
            for k,r,f in c["ret"]:
                need(type(r) is int and 2*v<=r<n, "scatter: center source is not a helper role")
                need(type(f) is int and 0<=f<len(frames) and cur[r]==f and dim[f]==20,
                     "scatter: center label/rank mismatch")
                by_role["c"][20]+=1;by_phase["copy"][20]+=1
    need(not ypiv.intersection(ytarget) and all(q==0 for q in ybracket.values()), "Y bracket cancellation")
    before_final=cur.copy()
    for r,f in enumerate(final):
        climb(r,f,"final")
    need(cur==final,"final label state")
    measured={r:hist(cn) for r,cn in by_role.items()}
    need(measured==c["blocks"], "role histogram/count mismatch")
    combined=sum(by_role.values(),Counter())
    need(dict(combined)==EXPECTED_H, "baseline invocation histogram mismatch")
    mass=sum(r*k for r,k in combined.items())
    need(mass==c["N"]==R*h+2*v*(h-1)+c["cst"], "rank mass")
    need(sum(r*k for r,k in by_role["c"].items())==c["cst"],"temporary-center rank mass")
    scatter=Counter(str(coeff(*(c["scat"]["inside"] if p>>k&1 else c["scat"]["outside"]),"scatter"))
                    for p in ports for k in range(22))
    return {
        "frame_count":len(frames),"tested_distinct_nested_pairs":len(pairs),
        "live_registers_per_invocation":n,"temporary_centers":22,
        "ranked_live_transitions":transitions,
        "phase_stats":totals,"role_histograms":measured,
        "phase_histograms":{p:hist(x) for p,x in by_phase.items()},
        "invocation_histogram":hist(combined),"invocation_calls":sum(combined.values()),
        "invocation_rank_mass":mass,"retained_centers":c["ret"],
        "phase_state_sha256":{"start":digest(start),"after_A":digest(cut),
                              "after_B":digest(before_final),"final":digest(final)},
        "literal_gate_coefficients":dict(sorted(literal.items())),
        "scalar_role_directions":dict(sorted(kind.items())),
        "scatter_coefficients":dict(sorted(scatter.items())),
        "scatter_additions":sum(scatter.values()),"Cc_copy_additions":22,
        "two_hosts_metadata_count":len(c.get("two_hosts",[])),
        "two_hosts_note":"Metadata only; not an independent allocator or host-use proof.",
        "Y_bracket_pairs":len(ybracket),
        "literal_inverse":"Each nonself additive shear inverts by negating its coefficient; inverse phase reverses order; inverse transpose keeps chronological order and swaps source/target with negation.",
        "limits":["No scalar all-column replay","No old-response or cleanup matrix formed",
                  "No generated Lean data comparison or kernel build","No physical stream compiler"]
    }

def scalar_word(ops):
    matrix=[[int(i==j) for j in range(4)] for i in range(4)]
    for target,source,q in ops:
        matrix[target]=[a+q*b for a,b in zip(matrix[target],matrix[source])]
    return matrix
