#!/usr/bin/env python3
"""Exact paid suppliers and retained PR168 balanced assembly.

Finite bridge formulas retained from icekylinx/eumemic PR144/152/168.
Least paid atom and fine positive transfer backoffs follow chafreaky's
PR163/164 arithmetic. Apache-2.0; prepared with OpenAI Codex assistance.
"""
import copy
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from math import prod
from pathlib import Path
import sys

from paid_moment import ROOT, OLD, certify as paid_certificate, envelope, profile, require
from interval_moment import moment, saving_grid

sys.dont_write_bytecode=True
if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(0)
AC=Q(6139542,10**10)
ETA=BETA=Q(1,10**24)
WEAKENING=Q(1,10**30)
ASSEMBLY_SOURCE="scripts/paired_cube_assembly.py"


def js(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [js(v) for v in x]
    return x


def nofloat(x):
    require(not isinstance(x,float),"binary floats are not certificate inputs")
    if isinstance(x,dict):
        for v in x.values():nofloat(v)
    if isinstance(x,(list,tuple)):
        for v in x:nofloat(v)


def baseline_complex_profile():
    row=json.loads((ROOT/"certificates/paired-cube-complex-input.json").read_text())
    physical=json.loads((ROOT/"certificates/paired-cube-physical-input.json").read_text())
    require(row["R"]==physical["R"]==row["c"]+row["q"]-row["matched"],"complete logical role bill")
    result=dict(row)
    result.update({k:physical[k] for k in ("W_per_vertex","rank_per_vertex","deficit_per_vertex","child_histogram")})
    result.update(scalar_role_reserve=row["R"],R=physical["physical_R"],reuse_pairs=physical["pairs"],
                  maxchild=max(int(k) for k,n in physical["child_histogram"].items() if n))
    return result


def bridge(row,coarse,atom):
    require(all(type(x) in (int,Q) for x in (coarse,atom)),"exact supplier inputs")
    nofloat(row);p=profile(row)
    h,v,R,c,M=(row[k] for k in ("h","v","R","c","total_M_operations"))
    scalar=row["scalar_role_reserve"];reuse=row["reuse_pairs"]
    require(all(type(z) is int and z>0 for z in (h,v,R,c,M,scalar)),"integer scalar inventory")
    require(scalar==c+row["q"]-row["matched"] and scalar-R==reuse>=0,"physical versus logical stock")
    require(h%2==0 and p["m"]==3*h and p["W"]==2*v+R,"complex dimensions")
    require(p["N"]==2*v-3*row["loss"],"telescoping complex deficit")
    m=3*h;half=m//2
    V=2**(m-1+(half-1)**2)*prod(2**(2*i)-1 for i in range(1,half))
    W=V*p["W"];s=V*p["total_rank"];N=V*v;r=p["maxchild"]
    local=4*(c+v)+10*v+4*h*v+4*h*h+8*h+8+2*h+8*scalar*v*(M+16)+32*v
    logical=3*V*local+8*W+4*N+8*m*scalar*V
    G=64*(m+1)**3*(logical+1)*(W+1)**2
    E=64*(W+m+G+1)**3;charge=2*G*W*W+8*s+4*W+4+32*m
    B=s+E;C0=32*m*B*B;depth=1
    while m**depth<=2*r**depth:depth+=1
    coefficient=depth*W.bit_length()+9909+252;degree=70000
    actual=(1-atom)*coarse+atom*OLD
    require(0<coarse<1 and actual<atom<1-actual,"paid atom and restored-row toll")
    require(E>charge and 2*B*(m-r)>=s+E and C0>2*B+18,"exact semantic induction")
    gap=Q(degree)-Q(51*coefficient,25);require(gap>0,"row reserve")
    return dict(bit_uniform=dict(coarse_saving=coarse,atom_beta=atom,old_atom_saving=OLD,ordinary_saving=actual),
                conservative_old_coarse_row_reserve=9909,ordinary_leaf_row_degree=252,
                complex=dict(m=m,W=W,s=s,N=N,maxchild=r,invocations_per_stage=V,stages=3,
                  auxiliary_banks_after_sharing=1,halving_degree=depth,wire_bits=W.bit_length(),
                  original_X_involution_scalar_group_upper=32*v,local_group_upper=local,
                  logical_group_upper=logical,finite_group_router_upper=G,scalar_group_upper=G,
                  coefficient_bound=h+4,coefficient_denominator_divides=6,
                  physical_roles_per_vertex=R,scalar_role_reserve=scalar,reuse_pairs=reuse),
                semantic=dict(E=E,literal_charge=charge,strict_literal_gap=E-charge,B=B,C0=C0,C1=1,
                  induction_gap=2*B*(m-r)-s-E,fixed_odd_divisor=3),
                rows=dict(coefficient=coefficient,complex_coefficient=depth*W.bit_length(),degree=degree,
                          suffix_slope=4*degree,degree_gap=gap))


def validate_bridge(value,row):
    nofloat(value)
    supplied=value["bit_uniform"]
    expected=bridge(row,Q(supplied["coarse_saving"]),Q(supplied["atom_beta"]))
    for section,values in expected.items():
        if isinstance(values,dict):
            for k,v in values.items():require(Q(value[section][k])==v,"stale bridge "+section+"/"+k)
        else:require(value[section]==values,"stale bridge "+section)
    return value


def below(value,grid=10**18):
    scaled=value*grid
    return Q(-(-scaled.numerator//scaled.denominator)-1,grid)


def assembly(finite,row,a,kappa,b=AC,eta=ETA,beta=BETA):
    require(not sys.flags.optimize,"run certificate with assertions enabled")
    validate_bridge(finite,row)
    require(all(type(x) in (int,Q) for x in (a,kappa,b,eta,beta)),"exact transfer inputs")
    require(0<a<=Q(finite["bit_uniform"]["ordinary_saving"]),"supported ordinary bit supplier")
    spec=importlib.util.spec_from_file_location("retained_pr168_balanced",ROOT/ASSEMBLY_SOURCE)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    result=module.assembly(a,b,finite,kappa,eta,beta)
    require(len(result["strict_constraints"])==47 and all(x>0 for x in result["strict_constraints"].values()),"47 strict constraints")
    require(len(result["margins"])==7 and min(result["margins"].values())>kappa,"seven strict margins")
    return result


def price(row,coarse,atom,b=AC,eta=ETA,beta=BETA):
    finite=bridge(row,coarse,atom);actual=finite["bit_uniform"]["ordinary_saving"]
    a=min(actual,(1-beta)*b-WEAKENING)
    q=a*(1-2*eta);value=(1-eta)*q/(1+q);kappa=below(value)
    receipt=assembly(finite,row,a,kappa,b,eta,beta)
    require(receipt["minimum_margin"]==value,"balanced controlling margin")
    return dict(kappa=kappa,a=a,actual_bit_saving=actual,complex_saving=b,beta=beta,eta=eta,
                weakening=WEAKENING,minimum_margin=value,assembly=receipt,finite_bridge=finite)


def certificate(bit_row,complex_row=None,comparisons=True):
    require(not sys.flags.optimize,"run without optimization")
    cr=baseline_complex_profile() if complex_row is None else complex_row
    require(moment(profile(cr),AC)["upper"]<1,"retained complex supplier contracts")
    complex_moment=saving_grid(profile(cr),10**18)
    b=complex_moment["accepted"]["saving"]
    require(b>=AC,"refined complex supplier covers published supplier")
    paid=paid_certificate(bit_row)
    final=price(cr,paid["coarse_saving"],paid["atom_beta"],b=b)
    controls=[]
    def reject(name,fn):
        try:fn()
        except (KeyError,ValueError,AssertionError):controls.append(name)
        else:raise ValueError("Adverse control accepted: "+name)
    def mutate(name,change):
        bad=copy.deepcopy(final["finite_bridge"]);change(bad)
        reject(name,lambda:validate_bridge(bad,cr))
    mutate("overstated ordinary supplier",lambda x:x["bit_uniform"].update(ordinary_saving=paid["ordinary_saving"]+Q(1,10**24)))
    previous=paid["atom_beta"]-Q(1,10**24)
    mutate("unpaid preceding atom",lambda x:x["bit_uniform"].update(atom_beta=previous,ordinary_saving=(1-previous)*paid["coarse_saving"]+previous*OLD))
    mutate("logical scalar stock collapsed to physical stock",lambda x:x["complex"].update(scalar_role_reserve=cr["R"]))
    mutate("local stock substituted for complete group",lambda x:x["complex"].update(W=cr["W_per_vertex"]))
    mutate("old row reserve omitted",lambda x:x.update(ordinary_leaf_row_degree=0))
    mutate("binary float introduced",lambda x:x.update(metadata=0.5))
    reject("unsupported transfer saving",lambda:assembly(final["finite_bridge"],cr,paid["ordinary_saving"]+Q(1,10**24),final["kappa"],b=b))
    reject("next final grid",lambda:assembly(final["finite_bridge"],cr,final["a"],final["kappa"]+Q(1,10**18),b=b))
    matched=[]
    if comparisons:
        baseline=json.loads((ROOT/"research/paired-cube-bit/out/profile_p12.json").read_text())
        for name,row,bill in (("PR168 fixed word and rounded fallback",baseline,envelope(baseline["m"],"legacy")),
                              ("PR168 fixed word and exact fallback bounds",baseline,envelope(baseline["m"])),
                              ("Selected checked word and exact fallback bounds",bit_row,envelope(bit_row["m"]))):
            p=paid if row==bit_row and bill==paid["envelope"] else paid_certificate(row,bill)
            f=price(cr,p["coarse_saving"],p["atom_beta"],b=b)
            matched.append(dict(name=name,kappa=f["kappa"],coarse_saving=p["coarse_saving"],ordinary_saving=p["ordinary_saving"],atom_beta=p["atom_beta"]))
    return dict(status="PASS exact conditional refinement",kappa=final["kappa"],paid_moment=paid,
                assembly=final,complex_profile=cr,complex_moment=complex_moment,controls=controls,matched_comparisons=matched,
                scope="Finite moment and 47-constraint assembly; finite word replay and source pins are separate obligations. Inherited all-size interfaces remain assumptions.")


if __name__=="__main__":
    row=json.loads((ROOT/"research/paired-cube-bit/out/profile_p12.json").read_text())
    print(json.dumps(js(certificate(row)),sort_keys=True,indent=2))
