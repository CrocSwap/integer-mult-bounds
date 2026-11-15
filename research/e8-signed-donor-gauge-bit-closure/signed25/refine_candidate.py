"""Exact strict witness and grid optimality within the retained six-round assembly.
Prepared with OpenAI Codex assistance. No circuit or coarse-saving change.
"""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parent

def refine(b,c):
    spec=importlib.util.spec_from_file_location('pinned_outer',ROOT.parent/'pr370-e8-screen/code/pricing/outer.py')
    outer=importlib.util.module_from_spec(spec);spec.loader.exec_module(outer)
    grid=Q(1,10**18);eta=beta=Q(1,10**18);backoff=Q(1,10**24)
    saving=(1-beta)*b-backoff
    assert Q(0)<saving<min(c,(1-beta)*b)<b<Q(1,32)
    initial=Q(384599,10**10);chain=[initial];limit=[initial]
    for _ in range(6):
        chain.append((1-saving)*saving+saving*chain[-1])
        limit.append((1-b)*b+b*limit[-1])
        assert chain[-2]<chain[-1]<saving and chain[-1]<limit[-1]<b
    a=chain[-1];q=a*(1-2*eta);minimum=(1-eta)*q/(1+q)
    scaled=minimum/grid;kappa=grid*((scaled.numerator-1)//scaled.denominator)
    bridge=dict(proof='PROOF.md',representation='Unchanged PR384 inherited finite envelope',
        semantic=dict(G=dict(base=2,exponent=30000),E=dict(base=2,exponent=100000),B_upper=dict(base=2,exponent=100001),C0=dict(base=2,exponent=210000),C1=1,strict_literal_gap=1,induction_gap_lower=1),
        rows=dict(coefficient=20161,degree=10**6,suffix_slope=4*10**6,degree_gap=Q(10**6)-Q(51*20161,25)))
    asm=outer.assembly(a,b,bridge,kappa,eta=eta,beta=beta)
    assert len(asm['strict_constraints'])==47 and all(x>0 for x in asm['strict_constraints'].values())
    assert asm['minimum_margin']==minimum
    rejected=[]
    for name,k,e,be in [('next_grid',kappa+grid,eta,beta),('zero_eta',kappa,Q(0),beta),('zero_beta',kappa,eta,Q(0)),('unit_beta',kappa,eta,Q(1))]:
        try:outer.assembly(a,b,bridge,k,eta=e,beta=be)
        except AssertionError:rejected.append(name)
        else:raise AssertionError('accepted invalid witness '+name)
    # F_s(x)=s(1-s+x) is increasing in x and s for 0<s<b<1/32,
    # x>=0. Thus every allowed six-round chain is below F_b^3(initial).
    # Positive eta lowers compact margin below a/(1+a). This bounds the
    # entire retained parameter family, not merely this chosen witness.
    supremum=limit[-1]/(1+limit[-1])
    assert kappa<minimum<supremum<kappa+grid
    return dict(kappa=str(kappa),kappa_float=float(kappa),eta=str(eta),beta=str(beta),saving_backoff=str(backoff),degraded_bit_saving=str(saving),bit_coarse=str(c),complex_coarse=str(b),bootstrap_rounds=6,bootstrap_chain=list(map(str,chain)),limit_chain=list(map(str,limit)),strict_constraints={k:str(v) for k,v in asm['strict_constraints'].items()},margins={k:str(v) for k,v in asm['margins'].items()},minimum_margin=str(minimum),absorption_gap=str(minimum-kappa),six_round_supremum=str(supremum),next_grid_above_supremum=True,negative_controls_rejected=rejected,finite_envelope=json.loads(json.dumps(bridge,default=str)))
