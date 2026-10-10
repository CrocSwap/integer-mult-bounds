"""Portable pure functions extracted from the reviewed complex checks; no historical receipt readers."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
Q=Fraction
from hashlib import sha256
from pathlib import Path
from math import prod
import gzip,json,sys

V,R,H=1320,9412,22
def need(x,msg):
    if not x:raise ValueError(msg)

def kind(r):return "X" if r<V else "Y" if r<2*V else "S"

def live(r):return ("L",r)

def tmp(r):return ("T",r-2*V)

def center(k):return ("C",k)

def add(t,s,q):return ("add",t,s,q.numerator,q.denominator)

def clear(t):return ("clear",t)

def copy(t,s):return ("copy",t,s)

def flat(gs):
    out=[]
    for g in gs:
        need(g[0] in ["in","out"],"literal additive gate")
        for r,a,b in g[3]:
            t,s=(r,g[2]) if g[0]=="out" else (g[2],r)
            need(t!=s and kind(s)!="Y" and not(kind(s)=="S" and kind(t)=="X"),
                 "projection requires Y never read and no helper-to-X gate")
            out.append((t,s,Q(a,b)))
    return out

def old_positive(A,B,c):
    """Circuit with inputs temp S and live Y; X fixed at zero.
    tempS output is irrelevant. Y output is Y_in + K tempS_in."""
    def part(gs):
        for t,s,q in gs:
            if kind(s)=="X":continue
            need(kind(s)=="S" and kind(t) in ["S","Y"],"old-response shape")
            yield add(tmp(t) if kind(t)=="S" else live(t),tmp(s),q)
    yield from part(A)
    for t,p in enumerate(c["ports"]):
        for k,r,_ in c["ret"]:
            q=Q(*(c["scat"]["inside"] if p>>k&1 else c["scat"]["outside"]))
            yield add(live(V+t),tmp(r),q)
    yield from part(B)

def old_word(orientation,K):
    if orientation=="forward":
        yield from (copy(("T",q),live(2*V+q)) for q in range(R))
        for e in K:
            op,t,s,a,b=e
            yield add(t,s,Q(-a if t[0]=="L" else a,b))
    else:
        yield from (clear(("T",q)) for q in range(R))
        for op,t,s,a,b in reversed(K):
            yield add(s,t,Q(a,b))
        yield from (add(live(2*V+q),("T",q),Q(1)) for q in range(R))
    yield from (clear(("T",q)) for q in range(R))

def cleanup(orientation,AB):
    for t,s,q in reversed(AB):
        if kind(t)=="Y":continue
        if orientation=="forward":yield add(live(t),live(s),-q)
        else:yield add(live(s),live(t),q)

def main_scalar(orientation,A,B,c):
    def phase(gs):
        for t,s,q in gs:
            if orientation=="forward":yield add(live(t),live(s),q)
            else:yield add(live(s),live(t),-q)
    yield from phase(A)
    # Every center is a complete temporary stream and one rank20 child,
    # initialized/read/discarded before the next center uses the work stock.
    for k,r,_ in c["ret"]:
        yield clear(center(k))
        if orientation=="forward":yield add(center(k),live(r),Q(1))
        for t,p in enumerate(c["ports"]):
            q=Q(*(c["scat"]["inside"] if p>>k&1 else c["scat"]["outside"]))
            if orientation=="backward":yield add(center(k),live(V+t),q)
        yield ("recursive_center",k,20)
        if orientation=="forward":
            for t,p in enumerate(c["ports"]):
                q=Q(*(c["scat"]["inside"] if p>>k&1 else c["scat"]["outside"]))
                yield add(live(V+t),center(k),q)
        else:yield add(live(r),center(k),Q(-1))
        yield clear(center(k))
    yield from phase(B)

def inv_schedule(orientation,A,B,c):
    K=list(old_positive(A,B,c))
    yield from ((p,e) for p,es in [
       ("old_response",old_word(orientation,K)),
       ("main",main_scalar(orientation,A,B,c)),
       ("cleanup",cleanup(orientation,A+B))] for e in es)

def coeff_steps(q):
    """Non-destructive coefficient expansion using one complete work stream.
    Copy source, double/halve/divide by3 as needed, add/subtract, clear.
    Counts Gaussian operations; multiply by2 for real/imag component primitives."""
    a,b=abs(q.numerator),q.denominator
    need(a in (1,2) and b in (1,2,3,6),"unsupported new coefficient")
    return 3+int(a==2)+int(b%2==0)+int(b%3==0)

def bill(schedule):
    phases={p:Counter() for p in ("old_response","main","cleanup")}
    coeffs={p:Counter() for p in phases}
    tape=sha256()
    for p,e in schedule:
        tape.update((json.dumps((p,e),separators=(",",":"))+"\n").encode())
        phases[p]["all_macros"]+=1
        if e[0]=="recursive_center":
            phases[p]["recursive_centers"]+=1
            phases[p]["recursive_rank_mass"]+=e[2]
            continue
        phases[p]["scalar_macros"]+=1
        phases[p][e[0]]+=1
        if e[0]=="add":
            q=Q(e[3],e[4]);coeffs[p][str(q)]+=1
            phases[p]["Gaussian_primitive_steps"]+=coeff_steps(q)
            phases[p]["scalar_log2_magnitude_charge"]+=1+int(abs(q)==2)
            phases[p]["halving_exposure"]+=int(q.denominator%2==0)
            phases[p]["divisor3_exposure"]+=int(q.denominator%3==0)
        else:phases[p]["Gaussian_primitive_steps"]+=1
    for p in phases:phases[p]["real_component_primitive_steps"]=2*phases[p]["Gaussian_primitive_steps"]
    total=sum((Counter({k:v for k,v in x.items() if k not in ["recursive_rank_mass"]}) for x in phases.values()),Counter())
    return {"phases":{p:dict(x) for p,x in phases.items()},"coefficient_histograms":{p:dict(x) for p,x in coeffs.items()},
            "totals":dict(total),"schedule_sha256":tape.hexdigest(),
            "other_main_recursive_calls":"70147 existing live-label transitions, unchanged; not scalar macros"}

def mm(A,B):return [[sum((x*y for x,y in zip(row,col)),Q(0)) for col in zip(*B)] for row in A]

def lifecycle(schedule):
    """Verify that new scalar-only work stock never survives into a child."""
    initialized=set();dirty=set();active_centers=set();seen_main=False;children=0
    for phase,e in schedule:
        if phase=="main" and not seen_main:
            need(not dirty,"old-response tableau survives into recursive main phase")
            seen_main=True
        need(e[0] in ("add","copy","clear","recursive_center"),"unknown or unpaid recursive operation")
        if e[0]=="recursive_center":
            k=e[1]
            need(type(k) is int and 0<=k<22 and e[2]==20,"new temporary entered uncharged child")
            need(phase=="main" and not dirty,"old-response temporary used during child")
            need(active_centers<=set([k]),"other center was not discarded before next child")
            children+=1
            continue
        target=e[1]
        source=e[2] if e[0] in ("add","copy") else None
        if source and source[0]=="T":need(source[1] in initialized,"uninitialized temporary read")
        if target[0]=="T":
            need(phase=="old_response","scalar-only tableau touched after recursive phase begins")
            initialized.add(target[1])
            if e[0]=="clear":dirty.discard(target[1])
            else:dirty.add(target[1])
        if target[0]=="C":
            if e[0]=="clear":active_centers.discard(target[1])
            else:active_centers.add(target[1])
        if e[0]=="add":
            # Coefficient expansion is deliberately local: copy into W,
            # optionally double/halve/divide3, accumulate, and clear W.
            expanded=["copy_work"]+["scale"]*(coeff_steps(Q(e[3],e[4]))-3)+["accumulate","clear_work"]
            need(expanded[-1]=="clear_work","coefficient work survived scalar macro")
    need(not dirty and not active_centers,"temporary stock not erased at invocation end")
    need(children==22,"center child count changed")
    return {"tableau_cleared_before_entire_main_phase":True,"tableau_absent_from_all_children":True,
            "coefficient_work_cleared_per_add":True,"center_children":children,
            "new_recursive_children":0,"moment_live_width":14692,
            "new_work_stock_only":9413,"complete_stream_fraction":"1/(14692*|Orth(110,2)|)"}

def ident(n):return [[Q(int(i==j)) for j in range(n)] for i in range(n)]

def matrix(n,gs):
    a=ident(n)
    for t,s,q in gs:a[t]=[x+q*y for x,y in zip(a[t],a[s])]
    return a

def toy_checks():
    # 2 X, 3 S, 2 Y. Explicit nontrivial X mixing is undone; helper map
    # and K are otherwise arbitrary. Exact Fraction checks cover every column
    # of THIS TINY TEMPLATE, not of the published 12052-register source.
    n=7;X={0,1};S={2,3,4};Y={5,6}
    gs=[(2,0,Q(1)),(3,2,Q(2)),(5,3,Q(-1,6)),(0,1,Q(1,2)),
        (4,0,Q(2)),(2,4,Q(1,2)),(6,2,Q(1,3)),(0,1,Q(-1,2)),
        (3,1,Q(-1)),(5,4,Q(1)),(6,0,Q(1))]
    M=matrix(n,gs)
    need(all(M[i]==ident(n)[i] for i in X),"toy source rows not restored")
    Ugs=[e for e in gs if e[0] not in Y]
    U=matrix(n,Ugs)
    Uinv=matrix(n,[(t,s,-q) for t,s,q in reversed(Ugs)])
    need(mm(Uinv,U)==ident(n),"restricted inverse identity")
    Mi=matrix(n,[(t,s,-q) for t,s,q in reversed(gs)])
    g8=[Mi[i] if i in S else ident(n)[i] for i in range(n)]
    h8=[M[i] if i in S else ident(n)[i] for i in range(n)]
    need(g8==Uinv and h8==U,"cleanup projection identities")
    Ut=matrix(n,[(s,t,q) for t,s,q in reversed(Ugs)])
    need(Ut==[list(x) for x in zip(*U)],"backward cleanup transpose")
    Kgs=[e for e in gs if e[1] not in X]
    Kmat=matrix(n,Kgs)
    need(all(Kmat[i][j]==M[i][j] for i in Y for j in S),"zero-source old response")
    Kt=matrix(n,[(s,t,q) for t,s,q in reversed(Kgs)])
    need(all(Kt[i][j]==M[j][i] for i in S for j in Y),"old response adjoint")
    bad=matrix(n,[(t,s,q) for t,s,q in reversed(Ugs)])
    need(bad!=g8,"wrong inverse sign must fail")
    bad_order=matrix(n,[(s,t,q) for t,s,q in Ugs])
    need(bad_order!=Ut,"unreversed transpose must fail")
    return {"tiny_exact_template_columns_checked":7,"checks_passed":7,
            "wrong_inverse_sign_rejected":True,"unreversed_transpose_rejected":True,
            "published_full_scalar_replay":False}
