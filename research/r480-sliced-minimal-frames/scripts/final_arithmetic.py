"""Two exact moments, explicit six-level cutoffs and invalid-assembly controls.
Prepared for rohanarun with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
import json,sys,importlib.util
P=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();assert not out.exists()
def load(n):
 s=importlib.util.spec_from_file_location('final_'+n,P/'engines'/(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M,B,A=[load(n)for n in ['moment','base_two_moment','outer']]
e=json.loads((P/'EXPECTED.json').read_text());baseline=json.loads((P/'inputs/PR510-EXPECTED.json').read_text())['nine'];cp=json.loads((P/'inputs/PR535-EXPECTED.json').read_text());H={int(r):n for r,n in e['profile'].items()};m=baseline['m'];W=baseline['bit']['live'];c=Q(e['bit_lower']);b=Q(e['complex_lower']);N=2*m
assert sum(r*n for r,n in H.items())==baseline['bit']['rank_mass']
factor=Q(2*m**3,2**80)*(6*N*(N-1)+3*N+6*(N-1))*sum(H.values())
moments=[]
for a,ok in [(c,True),(c+Q(1,10**24),False)]:
 l,u=M.moment(H,m,W,a,False);g,h=M.moment({1:1},m,W,a,False);l+=factor*g;u+=factor*h
 ll,uu=B.moment(m,W,list(H.items()),a);gg,hh=B.moment(m,W,[(1,1)],a);ll+=factor*gg;uu+=factor*hh
 assert (u<1 and uu<1)if ok else(l>1 and ll>1)
 moments.append(dict(endpoint=str(a),accept=ok,mercator=[str(l-1),str(u-1)],base_two=[str(ll-1),str(uu-1)]))
CP={int(r):n for r,n in cp['global_profile'].items()}
for a,ok in [(b,True),(b+Q(1,10**24),False)]:
 l,u=M.moment(CP,73,cp['live'],a,True);ll,uu=B.moment(73,cp['live'],list(CP.items()),a);gg,hh=B.moment(73,cp['live'],[(1,32*73**2*sum(CP.values()))],a);ll+=gg/10**16;uu+=hh/10**16
 assert (u<1 and uu<1)if ok else(l>1 and ll>1)
eta=beta=Q(1,10**18);s=min(c,(1-beta)*b)-Q(1,10**24);assert s<c and s<(1-beta)*b;chain=[Q(384599,10**10)];cuts=[]
for _ in range(6):
 old=chain[-1];a=(1-s)*s+s*old;gap=min(s-a,1-a-s,1-a-s*(1-old),1-s);assert old<a<s<1-a and gap>0
 ceil=lambda x:-(-x.numerator//x.denominator)
 cut=max(ceil(36/gap**2),ceil(2*(4+512)/gap));assert cut*gap**2>=36 and cut*gap>=2*(4+512);cuts.append(dict(exponent=str(a),gap=str(gap),cutoff_log2=str(cut)));chain.append(a)
q=chain[-1]*(1-2*eta);margin=(1-eta)*q/(1+q);ticks=margin*10**18;k=Q((ticks.numerator-1)//ticks.denominator,10**18);assert k==Q(e['kappa'])
bridge={'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}}
a=A.assembly(chain[-1],b,bridge,k,eta=eta,beta=beta);assert len(a['strict_constraints'])==47 and all(v>0 for v in a['strict_constraints'].values())
controls=[]
for name,kk,ee,bb in [('next_grid',k+Q(1,10**18),eta,beta),('zero_eta',k,Q(0),beta),('zero_beta',k,eta,Q(0)),('unit_beta',k,eta,Q(1))]:
 try:A.assembly(chain[-1],b,bridge,kk,eta=ee,beta=bb)
 except AssertionError:controls.append(name)
 else:raise AssertionError(name)
res=dict(status='PASS_TWO_ENGINE_MOMENTS_EXPLICIT_BOOTSTRAP_AND_47_OUTER_CONSTRAINTS',kappa=str(k),bit=str(c),complex=str(b),binding='complex'if (1-beta)*b<c else'bit',moment_receipts=moments,bootstrap_cutoffs=cuts,strict_outer_constraints={n:str(v)for n,v in a['strict_constraints'].items()},controls=controls,scope='Exact scalar numerical assembly. Fresh physical invoice separately establishes charged two-level coefficient<=512 and row bound18355; complex535 operator cited. All-size contracts remain conditional.')
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(res,indent=2)+'\n');print(res['status'],e['kappa_decimal'],flush=True)
