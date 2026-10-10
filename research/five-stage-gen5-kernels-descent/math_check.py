"""Source-bound banked five-stage moments and all47outerconstraints.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
Uses PR234 five-stage architecture and complex baseline, the gen5 helper and
PR197-derived actual five-stage entrance banks. Inputs must be live verifier outputs.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import importlib.util
HERE=Path(__file__).resolve().parent

def load(name):
 p=HERE/(name+'.py');s=importlib.util.spec_from_file_location('banked527_'+name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def serial(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {str(k):serial(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return list(map(serial,x))
 return x

def hist(x):return Counter({int(k):v for k,v in x.items()if v})
from pins import pin

def run(raw,complex_histogram,banks,global_result):
 cost=load('moment');other=load('base_two_moment');outer=load('outer')
 assert raw['source_aliases']==0 and raw['physical_R']==15886 and raw['h']==24 and raw['v']==1760
 H=hist(raw['five_stage_profile']['histogram']);assert H==hist(global_result['paid_histogram'])
 assert global_result['paid_rank_mass']==sum(k*n for k,n in H.items())==pin('five_stage_rank_mass',global_result['paid_rank_mass'])
 gauges=hist(raw['auxiliary_entrance_rank_histogram']);pin('entrance_rank_histogram',dict(gauges))
 assert banks['assignments']==4765800 and banks['gen5_roles']==15886 and banks['physical_replicas']==60
 pin('literal_stock',banks['literal_stock']);pin('banks_total',banks['banks_total']);pin('charts',banks['charts'])
 for a,n in gauges.items():
  assert H[5*a]>=n;H[5*a]-=n
  if not H[5*a]:del H[5*a]
 assert len(H)>0 and min(H.values())>0 and max(H)==50
 literal={k:n*60 for k,n in H.items()};literal_mass=sum(k*n for k,n in literal.items());literal_W=banks['literal_stock']
 assert 120*literal_W-literal_mass==60*4400
 # Divide the literal profile by5 to an integer normalization. The executed
 # realization is still60replicas, and finite accounting uses its literalstock.
 assert literal_W%5==0 and all(n%5==0 for n in literal.values())
 normalized={k:n//5 for k,n in literal.items()};W=literal_W//5;m=120;mass=sum(k*n for k,n in normalized.items())
 bp=dict(m=m,W=W,histogram=normalized,calls=sum(normalized.values()),rank_mass=mass,deficit=m*W-mass,maxchild=max(normalized),normalization=12,physical_replicas=60,literal_stock=literal_W,literal_children=sum(literal.values()),literal_rank_mass=literal_mass)
 root=cost.certify(normalized,m,W,True);c=Q(int(Q(root['lower'])*10**18),10**18);bm=cost.moment(normalized,m,W,c,True);nextbm=cost.moment(normalized,m,W,c+Q(1,10**18),True);assert bm[1]<1<nextbm[0]
 fallback=32*m*m*sum(normalized.values())
 _,upper=other.moment(m,W,list(normalized.items()),c);_,bad=other.moment(m,W,[(1,fallback)],c)
 lower,_=other.moment(m,W,list(normalized.items()),c+Q(1,10**18));badlower,_=other.moment(m,W,[(1,fallback)],c+Q(1,10**18));assert upper+Q(1,10**16)*bad<1<lower+Q(1,10**16)*badlower
 CH=hist(complex_histogram);assert sum(CH.values())==361405 and sum(k*n for k,n in CH.items())==1613040
 cp=dict(m=110,W=14692,histogram=dict(CH),calls=sum(CH.values()),rank_mass=sum(k*n for k,n in CH.items()),deficit=3080,maxchild=max(CH));b=Q(747454944651775,10**18);cm=cost.moment(dict(CH),110,14692,b,False);assert cm[1]<1
 chain=[Q(384599,10**10)]
 for _ in range(3):
  a=(1-c)*c+c*chain[-1];assert chain[-1]<a<c<1-a;chain.append(a)
 bit=chain[-1];eta=Q(1,10**12);beta=Q(1,10**9);assert bit<(1-beta)*b
 bridge=dict(proof='PROOF.md',representation='Exact powers with source-bound finite overcharges',semantic=dict(G=dict(base=2,exponent=30000),E=dict(base=2,exponent=100000),B_upper=dict(base=2,exponent=100001),C0=dict(base=2,exponent=210000),C1=1,strict_literal_gap=1,induction_gap_lower=1),rows=dict(coefficient=20161,degree=10**6,suffix_slope=4*10**6,degree_gap=Q(10**6)-Q(51*20161,25)))
 assert bridge['rows']['degree_gap']>0
 q=bit*(1-2*eta);minimum=(1-eta)*q/(1+q);ticks=minimum*10**18;k=Q((ticks.numerator-1)//ticks.denominator,10**18)
 assembly=outer.assembly(bit,b,bridge,k,eta=eta,beta=beta);assert len(assembly['strict_constraints'])==47 and len(assembly['margins'])==7 and min(assembly['strict_constraints'].values())>0
 try:outer.assembly(bit,b,bridge,k+Q(1,10**18),eta=eta,beta=beta)
 except AssertionError:pass
 else:raise AssertionError('Adjacentkappaadmitted')
 return serial(dict(status='PASS_BANKED_FIVE_STAGE_GEN5_EXACT_MOMENTS_AND_OUTER47',mathematics=dict(bit_profile=bp,complex_profile=cp,bit_coarse=c,complex_coarse=b,bit_moment_interval=bm,complex_moment_interval=cm,next_bit_grid_excluded=nextbm,independent_base_two_pass=True,ordinary_bootstrap_chain=chain,finite_bridge=bridge,assembly=assembly,kappa=k,kappa_decimal=cost.decimal(k),kappa_scientific=format(float(k),'.15e'),binding='bit'),adjacent_grid_point_rejected=True))
