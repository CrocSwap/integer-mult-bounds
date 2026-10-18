"""Fixed finite stopped-leaf bootstrap and exact outer witness.
Prepared with OpenAI Codex assistance; reuses the reviewed PR185 mechanism.
"""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parent

def ceil(q):return -(-q.numerator//q.denominator)
def cutoff_log2(delta,coefficient_bits):
    # For any fixed stage constant C<2^coefficient_bits. The actual inherited
    # primitive constant is not claimed to have been measured by this checker.
    assert delta>0 and isinstance(coefficient_bits,int) and coefficient_bits>=1
    L=ceil(max(Q(1),36/delta**2,2*(4+coefficient_bits)/delta))
    assert L*delta**2>=36 and L*delta>=2*(4+coefficient_bits)
    return L

def refine(b,c):
    spec=importlib.util.spec_from_file_location('pinned_outer',ROOT/'source384/code/engines/outer.py')
    outer=importlib.util.module_from_spec(spec);spec.loader.exec_module(outer)
    params=json.loads((ROOT/'PARAMETERS.json').read_text());depth=params['bootstrap_rounds'];assert depth==6
    grid=Q(1,10**18);eta=Q(params['eta']);beta=Q(params['beta']);backoff=Q(params['saving_backoff'])
    saving=(1-beta)*b-backoff
    assert Q(0)<saving<min(c,(1-beta)*b)<b<Q(1,32)
    initial=Q(384599,10**10);chain=[initial];stages=[]
    for j in range(depth):
        old=chain[-1];a=(1-saving)*saving+saving*old
        assert old<a<saving<1-a
        assert a==saving-saving**(j+1)*(saving-initial)
        gaps=dict(atom=saving-a,borrowing=1-a-saving,remainder=1-a-saving*(1-old),stock=1-saving)
        delta=min(gaps.values());assert delta>0
        examples={str(bits):str(cutoff_log2(delta,bits)) for bits in (1,80,210001)}
        stages.append(dict(level=j+1,ordinary_calls_only_to_level=j,gaps={k:str(v) for k,v in gaps.items()},minimum_gap=str(delta),cutoff_examples_by_constant_bits=examples))
        chain.append(a)
    previous=json.loads((ROOT/'THREE-ROUND-WITNESS.json').read_text())
    prior_saving=(1-beta)*Q(previous['complex_coarse'])-backoff
    prior_chain=[initial]
    for _ in range(3):prior_chain.append((1-prior_saving)*prior_saving+prior_saving*prior_chain[-1])
    assert list(map(str,prior_chain))==previous['bootstrap_chain']
    previous_six=json.loads((ROOT/'SIX-ROUND-18-DIGIT-COARSE-WITNESS.json').read_text())
    a=chain[-1];q=a*(1-2*eta);minimum=(1-eta)*q/(1+q)
    scaled=minimum/grid;kappa=grid*((scaled.numerator-1)//scaled.denominator)
    bridge=dict(proof='PROOF.md',representation='Unchanged PR384 inherited finite envelope; fixed-depth PR185 ordinary wrappers restore internal rows',
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
    for name,delta,bits in [('zero_bootstrap_gap',Q(0),80),('invalid_constant_bound',Q(1,2),0)]:
        try:cutoff_log2(delta,bits)
        except AssertionError:rejected.append(name)
        else:raise AssertionError('accepted invalid finite cutoff '+name)
    # For the pinned outer formula all valid witnesses have a<b and eta>0;
    # consequently the compact margin is <a/(1+a)<b/(1+b), independently
    # of bootstrap depth. This is a family ceiling, not a new circuit bound.
    ceiling=b/(1+b)
    assert kappa<minimum<ceiling<kappa+grid
    assert kappa>Q(previous_six['kappa'])
    # Five levels at the same slack values do not yet reach the chosen grid.
    a5=chain[-2];q5=a5*(1-2*eta);assert (1-eta)*q5/(1+q5)<kappa
    return dict(kappa=str(kappa),kappa_float=float(kappa),eta=str(eta),beta=str(beta),saving_backoff=str(backoff),degraded_bit_saving=str(saving),bit_coarse=str(c),complex_coarse=str(b),bootstrap_rounds=depth,bootstrap_chain=list(map(str,chain)),bootstrap_stages=stages,strict_constraints={k:str(v) for k,v in asm['strict_constraints'].items()},margins={k:str(v) for k,v in asm['margins'].items()},minimum_margin=str(minimum),absorption_gap=str(minimum-kappa),fixed_complex_outer_ceiling=str(ceiling),next_grid_above_ceiling=True,five_rounds_insufficient_at_selected_slacks=True,previous_three_round_kappa=previous['kappa'],previous_six_round_kappa=previous_six['kappa'],prior_chain_regression_passed=True,negative_controls_rejected=rejected,finite_envelope=json.loads(json.dumps(bridge,default=str)))
