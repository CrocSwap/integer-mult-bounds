"""Fresh exact paid moments, three finite ordinary levels and outer47 assembly.
Expected output values are compared only after their fresh calculation.
Assisted with ChatGPT. Original arithmetic source headers remain unchanged.
"""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util,json
HERE=Path(__file__).resolve().parent

def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def serial(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):serial(v)for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [serial(v)for v in x]
    return x

def profile(h,m,W):
    h={int(r):n for r,n in h.items()if n}
    assert all(0<r<m and type(n)is int and n>0 for r,n in h.items())
    mass=sum(r*n for r,n in h.items());deficit=m*W-mass
    assert deficit>0
    return dict(m=m,W=W,histogram={str(r):n for r,n in sorted(h.items())},calls=sum(h.values()),rank_mass=mass,deficit=deficit,maxchild=max(h))

def run(raw,complex_histogram):
    math=load('v8_exact_moments',HERE/'code/five_stage_bit_cost_20261009.py')
    outer=load('v8_outer47',HERE/'code/paired_cube_assembly.py')
    bp=profile(raw['five_stage_profile']['histogram'],120,23683)
    cp=profile(complex_histogram,110,14692)
    assert (bp['calls'],bp['rank_mass'],bp['deficit'],bp['maxchild'])==(495304,2837560,4400,100)
    assert (cp['calls'],cp['rank_mass'],cp['deficit'],cp['maxchild'])==(361405,1613040,3080,46)
    coarse=Q(704197288590873,10**18);b=Q(747454944651775,10**18)
    bm=math.moment({int(k):v for k,v in bp['histogram'].items()},120,23683,coarse,True)
    cm=math.moment({int(k):v for k,v in cp['histogram'].items()},110,14692,b,False)
    assert bm[1]<1 and cm[1]<1
    chain=[Q(384599,10**10)]
    for _ in range(3):
        a=(1-coarse)*coarse+coarse*chain[-1]
        assert chain[-1]<a<coarse<1-a
        chain.append(a)
    bit=chain[-1];eta=Q(1,10**12);beta=Q(1,10**9)
    assert bit<(1-beta)*b
    bridge=dict(proof='PROOF.md',representation='Exact powers with source-bound finite overcharges',
                semantic=dict(G=dict(base=2,exponent=30000),E=dict(base=2,exponent=100000),B_upper=dict(base=2,exponent=100001),C0=dict(base=2,exponent=210000),C1=1,strict_literal_gap=1,induction_gap_lower=1),
                rows=dict(coefficient=20161,degree=10**6,suffix_slope=4*10**6,degree_gap=Q(10**6)-Q(51*20161,25)))
    assert bridge['rows']['degree_gap']>0
    q=bit*(1-2*eta);minimum=(1-eta)*q/(1+q);ticks=minimum*10**18
    kappa=Q(ticks.numerator//ticks.denominator,10**18)
    if kappa==minimum:kappa-=Q(1,10**18)
    result=outer.assembly(bit,b,bridge,kappa,eta=eta,beta=beta)
    assert len(result['strict_constraints'])==47 and len(result['margins'])==7
    assert all(x>0 for x in result['strict_constraints'].values())
    try:outer.assembly(bit,b,bridge,kappa+Q(1,10**18),eta=eta,beta=beta)
    except AssertionError:adjacent_rejected=True
    else:raise AssertionError('adjacent kappa grid point admitted')
    actual=serial(dict(bit_profile=bp,complex_profile=cp,bit_moment_interval=bm,complex_moment_interval=cm,ordinary_bootstrap_chain=chain,finite_bridge=bridge,assembly=result,kappa=kappa,kappa_decimal=math.decimal(kappa)))
    expected=json.loads((HERE/'expected-math.json').read_text())['mathematics']
    for key,value in actual.items():assert value==expected[key],('changed deterministic mathematics',key)
    return dict(status='PASS_FRESH_EXACT_MOMENTS_BOOTSTRAP_AND_OUTER47',mathematics=actual,adjacent_grid_point_rejected=adjacent_rejected)
