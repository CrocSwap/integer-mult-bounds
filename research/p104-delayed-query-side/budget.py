"""Exact favorable coverage screen for one fixed delayed-side profile.

Uses Douglas Colkitt's retained interval calculator, without changing its
coverage law. Jose Manuel, with substantial OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util
import json

ROOT=Path(__file__).resolve().parents[2]
if sha256((ROOT/"research/complex-local-word-ceiling/ceiling.py").read_bytes()).hexdigest()!="86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc":
    raise ValueError("interval calculator pin")
sp=importlib.util.spec_from_file_location("p104_cost",ROOT/"research/complex-local-word-ceiling/ceiling.py")
C=importlib.util.module_from_spec(sp);sp.loader.exec_module(C)
PROFILE={1:2564,2:547,3:432,4:142,5:83,6:128,7:11}
MASS=sum(r*n for r,n in PROFILE.items())
CENTRE=56
PROGRESS=MASS-CENTRE
K=Q(836330098538459,500000000000000000)
A=K/(1-K)


def require(ok,why):
    if not ok:raise ValueError(why)


def screen(p):
    s,m,W=2*p+1,16*p+9,208*p
    gap=max(0,s*PROGRESS-(m-1)*W)
    banks=(gap+m-1)//m
    idle=(m-1)*W+m*banks-s*PROGRESS
    require(idle>=0,"minimal favorable auxiliary volume")
    cap=C.max_idle_rank(m)
    lo=hi=Q(0)
    for r,n in PROFILE.items():
        x,y=C.child_cost(r,m,A);lo+=s*n*x;hi+=s*n*y
    x,y=C.child_cost(cap,m,A)
    lo+=Q(idle,cap)*x;hi+=Q(idle,cap)*y
    lo,hi=lo/(W+banks),hi/(W+banks)
    require(lo>1,"fixed profile unexpectedly passes selected saving")
    return dict(p=p,m=m,stages=s,data_families=W,minimum_extra_full_families=banks,
                favorable_idle_mass=idle,moment_lower=str(lo),moment_upper=str(hi),
                moment_midpoint=float((lo+hi)/2))


def main():
    require(MASS==6782 and PROGRESS==6726,"literal rank invoice")
    cases=[screen(p) for p in range(1,16)]
    # At p>=16, m>=265. Discard idle entropy and bound the per-call deficit
    # by48. exp(x)>=1+x converts this into a strict moment obstruction.
    m=265
    lm,um=C.ln(m)
    entropy_lower=sum(Q(r*n)*(lm-C.ln(r)[1]) for r,n in PROFILE.items())
    require(A*entropy_lower>48,"all larger stage counts")
    # Fully paid auxiliary families add m units of idle mass and one family
    # to the denominator. Their own favorable cost is(m/cap)^a>1, so once
    # the minimal-bank moment exceeds1, adding more banks cannot repair it.
    print(json.dumps({"status":"PASS_FIXED_P104_DELAYED_SIDE_BUDGET_OBSTRUCTION",
                      "profile":PROFILE,"rank_mass":MASS,"persistent_progress":PROGRESS,
                      "copy_rank":CENTRE,"selected_a":str(A),"small_p_cases":cases,
                      "large_p":{"from_p":16,"minimum_m":265,"a_times_local_entropy_lower":str(A*entropy_lower),
                                 "per_call_deficit_upper":48},
                      "scope":"This fixed profile under the paired-chain coverage and halving guard, including arbitrary fully paid auxiliary banks. No bound for a redesigned producer or changed coverage law."},indent=2))


if __name__=="__main__":main()
