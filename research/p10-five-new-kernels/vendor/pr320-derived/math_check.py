"""Source-bound banked five-stage moments and all47outerconstraints.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
Uses PR234 five-stage architecture and complex baseline, the p = 10 helper and
PR197-derived actual five-stage entrance banks. Inputs must be live verifier outputs.
p = 10 port (DreamingOfClouds, Anthropic Claude assistance): the bit profile is the p = 10 word's (m = 5h = 100,
deficit 4v - 5h(h-2), counts pinned in word-pins.json). The complex supplier is isolated in complex_supplier().
Complex-bound assembly (draft by DreamingOfClouds with Anthropic Claude assistance, adopted unchanged in logic):
the bit is certified at its true root c with the adjacent grid point rejected; the saving fed to the bootstrap
and the 47 outer constraints is s = min(c, floor((1-beta)b - 10^-18)), re-checked exactly at s (the moment is
increasing in the saving). When s < c the complex supplier binds, and outer.assembly at the cap (1-beta)b itself
must fail on leaf_saving_above_bit.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import importlib.util
from word_pins import expect,shape
HERE=Path(__file__).resolve().parent

def load(name):
 p=HERE/(name+'.py');s=importlib.util.spec_from_file_location('banked527_'+name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def serial(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {str(k):serial(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return list(map(serial,x))
 return x

def hist(x):return Counter({int(k):v for k,v in x.items()if v})

def complex_supplier(cost,other,complex_histogram):
 """The retained complex supplier: profile pins, coarse b and its exact moment certificate (adjacent grid point
 rejected). This is the only complex-specific block of math_check; a transplanted complex chain replaces it.
 b is certified like the bit side: WITH the 10^-16 bad-class fallback envelope (32 m^2 rank-one calls per paid
 child), by both rational moment engines, adjacent 10^-18 grid point rejected. The inherited PR234/PR193
 convention priced the complex side without the fallback; that larger root b0 is re-certified and recorded only."""
 # the centre-sharing complex supplier built with PR #304's pipeline (inputs/complex/centre-mw/).
 CH=hist(complex_histogram);assert sum(CH.values())==351820 and sum(k*n for k,n in CH.items())==1571680
 m,W,grid=110,14316,Q(1,10**18)
 cp=dict(m=m,W=W,histogram=dict(CH),calls=sum(CH.values()),rank_mass=sum(k*n for k,n in CH.items()),deficit=3080,maxchild=max(CH))
 root=cost.certify(dict(CH),m,W,True);b=Q(int(Q(root['lower'])*10**18),10**18);assert b==Q(772714351296671,10**18)
 cm=cost.moment(dict(CH),m,W,b,True);nextcm=cost.moment(dict(CH),m,W,b+grid,True);assert cm[1]<1<nextcm[0]
 fallback=32*m*m*sum(CH.values())
 _,upper=other.moment(m,W,list(CH.items()),b);_,bad=other.moment(m,W,[(1,fallback)],b)
 lower,_=other.moment(m,W,list(CH.items()),b+grid);badlower,_=other.moment(m,W,[(1,fallback)],b+grid);assert upper+Q(1,10**16)*bad<1<lower+Q(1,10**16)*badlower
 b0=Q(772714354722691,10**18);cm0=cost.moment(dict(CH),m,W,b0,False);nextcm0=cost.moment(dict(CH),m,W,b0+grid,False);assert cm0[1]<1<nextcm0[0] and b<b0
 return dict(profile=cp,coarse=b,moment_interval=cm,next_grid_excluded=nextcm,coarse_without_fallback=b0,moment_interval_without_fallback=cm0)

def run(raw,complex_histogram,banks,global_result):
 cost=load('moment');other=load('base_two_moment');outer=load('outer');S=shape();m=S['m'];T=S['replicas']
 assert raw['source_aliases']==0 and raw['physical_R']==expect('final_physical_R',raw['physical_R']) and raw['h']==S['h'] and raw['v']==S['v']
 H=hist(raw['five_stage_profile']['histogram']);assert H==hist(global_result['paid_histogram'])
 assert global_result['paid_rank_mass']==sum(k*n for k,n in H.items())==expect('final_five_stage_rank_mass',global_result['paid_rank_mass'])
 gauges=hist(raw['auxiliary_entrance_rank_histogram']);expect('final_entrance_ranks',gauges)
 completions=hist(raw.get('completion_rank_histogram',gauges));expect('completion_rank_histogram',completions);assert sum(completions.values())==sum(gauges.values())
 assert banks['assignments']==5*T*raw['physical_R'] and banks['physical_roles']==raw['physical_R'] and banks['physical_replicas']==T
 assert banks['literal_stock']==expect('literal_stock',banks['literal_stock']) and banks['banks_total']==5*expect('banks_per_stage',banks['banks_total']//5) and banks['charts']==expect('final_charts',banks['charts'])
 for a,n in completions.items():
  assert H[5*a]>=n;H[5*a]-=n
  if not H[5*a]:del H[5*a]
 assert len(H)>0 and min(H.values())>0 and max(H)==S['idle'][2]
 literal={k:n*T for k,n in H.items()};literal_mass=sum(k*n for k,n in literal.items());literal_W=banks['literal_stock']
 assert m*literal_W-literal_mass==T*S['deficit']
 # Divide the literal profile by5 to an integer normalization. The executed
 # realization is still60replicas, and finite accounting uses its literalstock.
 assert literal_W%5==0 and all(n%5==0 for n in literal.values())
 normalized={k:n//5 for k,n in literal.items()};W=literal_W//5;mass=sum(k*n for k,n in normalized.items())
 bp=dict(m=m,W=W,histogram=normalized,calls=sum(normalized.values()),rank_mass=mass,deficit=m*W-mass,maxchild=max(normalized),normalization=T//5,physical_replicas=T,literal_stock=literal_W,literal_children=sum(literal.values()),literal_rank_mass=literal_mass)
 root=cost.certify(normalized,m,W,True);c=Q(int(Q(root['lower'])*10**18),10**18);bm=cost.moment(normalized,m,W,c,True);nextbm=cost.moment(normalized,m,W,c+Q(1,10**18),True);assert bm[1]<1<nextbm[0]
 fallback=32*m*m*sum(normalized.values())
 _,upper=other.moment(m,W,list(normalized.items()),c);_,bad=other.moment(m,W,[(1,fallback)],c)
 lower,_=other.moment(m,W,list(normalized.items()),c+Q(1,10**18));badlower,_=other.moment(m,W,[(1,fallback)],c+Q(1,10**18));assert upper+Q(1,10**16)*bad<1<lower+Q(1,10**16)*badlower
 expect('bit_root',c)
 supplier=complex_supplier(cost,other,complex_histogram);cp,b,cm=supplier['profile'],supplier['coarse'],supplier['moment_interval']
 # Bit saving fed to the bootstrap: the certified root c, capped below the complex leaf cap (1-beta)*b of outer.py
 # (leaf_saving_above_bit, complex_above_bit). The moment is monotone in the saving, so any grid point s<=c is
 # certified too; it is re-checked exactly. c, bm and nextbm stay the record of the uncapped root.
 grid=Q(1,10**18);eta=Q(1,10**12);beta=Q(1,10**9);cap=(1-beta)*b
 s=min(c,Q(((cap-grid)*10**18).__floor__(),10**18));binding='bit' if s==c else 'complex'
 sm=bm if s==c else cost.moment(normalized,m,W,s,True);assert 0<s<=c and sm[1]<1
 if binding=='complex':assert s+grid>cap-grid   # tight against the complex cap: the next grid point exceeds (1-beta)*b-grid
 chain=[Q(384599,10**10)]
 for _ in range(3):
  a=(1-s)*s+s*chain[-1];assert chain[-1]<a<s<1-a;chain.append(a)
 bit=chain[-1];assert bit<s<=cap-grid<cap
 bridge=dict(proof='PROOF.md',representation='Exact powers with source-bound finite overcharges',semantic=dict(G=dict(base=2,exponent=30000),E=dict(base=2,exponent=100000),B_upper=dict(base=2,exponent=100001),C0=dict(base=2,exponent=210000),C1=1,strict_literal_gap=1,induction_gap_lower=1),rows=dict(coefficient=20161,degree=10**6,suffix_slope=4*10**6,degree_gap=Q(10**6)-Q(51*20161,25)))
 assert bridge['rows']['degree_gap']>0
 q=bit*(1-2*eta);minimum=(1-eta)*q/(1+q);ticks=minimum*10**18;k=Q((ticks.numerator-1)//ticks.denominator,10**18)
 assembly=outer.assembly(bit,b,bridge,k,eta=eta,beta=beta);assert len(assembly['strict_constraints'])==47 and len(assembly['margins'])==7 and min(assembly['strict_constraints'].values())>0
 try:outer.assembly(bit,b,bridge,k+Q(1,10**18),eta=eta,beta=beta)
 except AssertionError:pass
 else:raise AssertionError('Adjacentkappaadmitted')
 if binding=='complex':   # the cap is the outer constraint: a bit saving at (1-beta)*b itself fails leaf_saving_above_bit
  try:outer.assembly(cap,b,bridge,k,eta=eta,beta=beta)
  except AssertionError as e:assert 'leaf_saving_above_bit' in str(e)
  else:raise AssertionError('Complexleafcapadmitted')
 expect('binding',binding);expect('kappa',k)
 return serial(dict(status='PASS_BANKED_FIVE_STAGE_P10_EXACT_MOMENTS_AND_OUTER47',mathematics=dict(bit_profile=bp,complex_profile=cp,bit_coarse=s,bit_root=c,bit_root_moment_interval=bm,complex_coarse=b,complex_coarse_without_fallback=supplier['coarse_without_fallback'],complex_leaf_cap=cap,bit_moment_interval=sm,complex_moment_interval=cm,next_complex_grid_excluded=supplier['next_grid_excluded'],next_bit_grid_excluded=nextbm,independent_base_two_pass=True,ordinary_bootstrap_chain=chain,finite_bridge=bridge,assembly=assembly,kappa=k,kappa_decimal=cost.decimal(k),kappa_scientific=format(float(k),'.15e'),binding=binding),adjacent_grid_point_rejected=True))
