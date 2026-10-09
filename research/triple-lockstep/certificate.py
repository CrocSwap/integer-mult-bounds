#!/usr/bin/env python3
"""Conservative finite PR137 triple-bank stage-one lockstep arithmetic.

Only the numerical rank/moment and coupled assembly are checked here.
This script DOES NOT prove that the synchronized arbitrary-dirty *physical*
word exists; a separate literal combined replay and sign/phase audit are
required before the displayed kappa can be considered a verified theorem.
"""
from __future__ import annotations
from collections import Counter
from fractions import Fraction as Q
from importlib.util import module_from_spec,spec_from_file_location
from math import prod
from pathlib import Path
import argparse,json,sys

if sys.flags.optimize:
    raise RuntimeError("Python -O is forbidden for proof checks")
if hasattr(sys,"set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=ROOT/"research/cover-local-reuse"
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(BASE))
from three_stage_cover_network import log_upper,exp_upper,finite_bridge
from structured_bulk_assembly import assembly,js

spec=spec_from_file_location("frozen_pr137_cover_certificate",BASE/"certificate.py")
assert spec is not None and spec.loader is not None
inherited=module_from_spec(spec)
spec.loader.exec_module(inherited)

KGRID=10**15
CGRID=10**12
STOP=Q(1,10**6)
PR137=Q(206798116851,500000000000000)
TARGET=Q(103,100)*PR137
# Data fronts are not on the auxiliary role streams. Their 3-way merged
# moment gets a strictly positive conservative correction.
def exact_moment_upper(children,m,w,a,data_mass):
    optimistic=sum((Q(r*n,m*w)*exp_upper(a*log_upper(Q(m,r)))
                    for r,n in children.items()),Q(0))
    penalty=(Q(3*data_mass,m*w)*a*log_upper(Q(3))*
             exp_upper(a*log_upper(Q(m))))
    return optimistic+penalty,optimistic,penalty

def certificate():
    baseline=js(inherited.exact())
    frozen=json.loads((BASE/"certificate.json").read_text())
    assert baseline==frozen,"PR137 saved full certificate differs from replay"
    assert Q(baseline["kappa"])==PR137,"Pin PR137 κ"
    p=inherited.cover_profile()
    h,v,R,m,w=(p[k]for k in ("h","v","R","m","roles_per_cell"))
    assert (h,v,R,m,w)==(24,2024,26597,72,91935)
    H={int(r):int(n)for r,n in p["local_child_multiplicities"].items()}
    original=Counter({int(r):int(n)for r,n in p["child_multiplicities"].items()})
    assert sum(r*n for r,n in original.items())==p["rank_per_cell"]==6612144
    assert all(r<h for r in H),"Triple lockstep child must be proper"
    hypothetical=original.copy()
    for r,n in H.items():
        assert hypothetical[r]>=3*n
        hypothetical[r]-=3*n
        hypothetical[3*r]+=n
    hypothetical=Counter({r:n for r,n in hypothetical.items() if n})
    rank=sum(r*n for r,n in hypothetical.items())
    assert rank==p["rank_per_cell"] and w*m-rank==7176
    assert max(hypothetical)==69<72 and min(hypothetical)>0
    # Frozen PR137 source explicitly computes one (h-1)-total-width
    # front for every source wire and every target chain, so the exact
    # *single-invocation* data rank mass is 2v(h-1).
    local_source=(ROOT/"research/cyclic-deferred/complex_deferred.py").read_text()
    for s in ("ds = sorted(levels[t] | {0, h - 1})",
              "z[b - a] += 2 * v","z[h - 1] += 2 * N"):
        assert s in local_source,("Data mass source altered",s)
    data_mass=2*v*(h-1)
    assert data_mass==93104
    def accepts_complex(i):
        return exact_moment_upper(hypothetical,m,w,Q(i,CGRID),data_mass)[0]<1
    lo,hi=0,10**9
    assert accepts_complex(lo) and not accepts_complex(hi)
    while hi-lo>1:
        mid=(lo+hi)//2
        if accepts_complex(mid):lo=mid
        else:hi=mid
    ac=Q(lo,CGRID)
    cm,opt,penalty=exact_moment_upper(hypothetical,m,w,ac,data_mass)
    assert cm<1 and not accepts_complex(lo+1)
    assert penalty>0 and cm>opt
    assert ac==Q(93743897,200000000000), "Pinned arithmetic candidate changed"

    # Reproduce PR137's finite group, virtual scalar and adapter reserves.
    n=m//2
    vertices=(2**(m-1+(n-1)**2)*
              prod(2**(2*i)-1 for i in range(1,n)))
    assert vertices%3==0
    cells=vertices//3
    phase=dict(m=m,N=vertices*v,W=cells*w,total_rank=cells*rank,
               deficit=cells*(w*m-rank),vertices_per_stage=vertices,
               cells_per_stage=cells,maxchild=max(hypothetical))
    row=json.loads((ROOT/"certificates/three-stage-cover-complex-input.json").read_text())
    assert row["R"]==28705 and row["total_M_operations"]==118451
    bridge=finite_bridge(phase,row)
    supplemental=32*(m+1)**3*(vertices*R+2*vertices*v)
    bc=bridge["complex"]
    bc["completed_adapter_group_upper"]=supplemental
    bc["scalar_group_upper"]+=supplemental
    global_w=phase["W"];s=phase["total_rank"];G=bc["scalar_group_upper"]
    E=64*(global_w+m+G+1)**3
    charge=2*G*global_w**2+8*s+4*global_w+4+32*m
    B=s+E;C0=32*m*B*B
    assert charge<E and 2*B*(m-phase["maxchild"])>=s+E and 2*B+18<C0
    bridge["semantic"].update(E=E,literal_charge=charge,strict_literal_gap=E-charge,
        B=B,C0=C0,induction_gap=2*B*(m-phase["maxchild"])-s-E)
    audit=json.loads((ROOT/"research/cyclic-deferred/reflection-audit.json").read_text())
    assert bc["local_group_upper"]>=audit["conservative_local_G"]>=audit["expanded_scalar_operations_per_stage"]
    assert bridge["rows"]["degree"]==160000
    assert bridge["rows"]["coefficient"]==53868

    # Retain the PR137 certified bit supplier unchanged. It now binds.
    bit=inherited.bit_certificate()
    actual_bit=bit["effective_saving"]
    assert actual_bit==Q(11265104579,25000000000000)
    a=min(actual_bit,(1-STOP)*ac-Q(1,10**14))
    def accepts_final(i):
        try:assembly(a,ac,bridge,Q(i,KGRID),beta=STOP)
        except AssertionError:return False
        return True
    low,high=0,int(ac*KGRID)+1
    assert accepts_final(low) and not accepts_final(high)
    while high-low>1:
        mid=(low+high)//2
        if accepts_final(mid):low=mid
        else:high=mid
    k=Q(low,KGRID)
    result=assembly(a,ac,bridge,k,beta=STOP)
    assert not accepts_final(low+1)
    assert len(result["strict_constraints"])==47 and len(result["margins"])==7
    assert k>=TARGET and k>=Q(4,10000)
    assert k==Q(1406870147,3125000000000), "Expected kappa changed"
    return js(dict(
        status="FINITE RATIONAL SCREEN PASS; 3-way lockstep physical word remains a separate unproved obligation",
        baseline_pr137=PR137,
        improvement_ratio=k/PR137,
        target_three_percent=TARGET,
        candidate_kappa=k,conservative_complex_saving=ac,
        unchanged_pr137_bit_saving=actual_bit,assembly_bit_saving=a,
        paired_profile=dict(roles_per_cell=w,total_rank_per_cell=rank,
                            deficit_per_cell=w*m-rank,maxchild=max(hypothetical),
                            child_multiplicities=dict(sorted(hypothetical.items())),
                            original_pr137_child_multiplicities=dict(sorted(original.items())),
                            local_child_multiplicities=dict(sorted(H.items())),
                            nonmergeable_single_core_data_rank_mass=data_mass,
                            optimistic_complex_moment_upper=opt,
                            positive_data_penalty=penalty,
                            total_complex_moment_upper=cm,
                            conservative_moment_gap=1-cm),
        finite_bridge=dict(physical_roles=R,virtual_roles=row["R"],
            completed_adapter_charge=supplemental,scalar_G=G,
            row_coefficient=bridge["rows"]["coefficient"],
            row_degree=bridge["rows"]["degree"],
            semantic_charge_gap=bridge["semantic"]["strict_literal_gap"]),
        constraints=len(result["strict_constraints"]),margins=len(result["margins"]),
        next_grid_rejected=True,
        mathematical_status="Not yet a proved exponent improvement: the synchronized 3-core scalar/Clifford implementation and arbitrary-dirty all-column replay are not established by this numerical certificate.",
        credits="PR137 eumemic, PR132 ikeboy, PR130 icekylinx, PR124 jamesyc, original PR117/PR97 sources; new conservative finite screen with OpenAI assistance."))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    c=certificate()
    text=json.dumps(c,indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.write_text(text)
    else:
        print(text)
    print("FINITE SCREEN PASS κ",c["candidate_kappa"],"47 constraints, 7 margins; physical proof pending",file=sys.stderr)

if __name__=="__main__":main()
