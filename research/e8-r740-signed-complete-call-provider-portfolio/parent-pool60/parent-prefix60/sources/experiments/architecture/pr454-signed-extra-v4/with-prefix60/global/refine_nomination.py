"""Conditional finite arithmetic screen; assignment/operator admission is separate."""
from pathlib import Path
from fractions import Fraction as Q
import json,importlib.util,math
from row_bound import bound,controls
P=Path(__file__).resolve().parent;ROOT=P.parents[4];ENG=ROOT/'experiments/bit-search/pr433/source/research/split-centres-global/vendor/engines'
def load(n):
 s=importlib.util.spec_from_file_location('n'+n,ENG/(n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M,O,A=[load(n)for n in ['moment','base_two_moment','outer']]
def cert(H,m,W):
 r=M.certify(H,m,W,True);c=Q(r['lower']);nxt=Q(r['upper']);
 def check(x):
  u,v=O.moment(m,W,list(H.items()),x);p,q=O.moment(m,W,[(1,32*m*m*sum(H.values()))],x);return u+p/10**16,v+q/10**16
 assert check(c)[1]<1<check(nxt)[0]
 return c,r
x=json.loads((P/'hosted/GLOBAL.json').read_text());H={int(k):v for k,v in x['profile'].items()};c,bit=cert(H,78,9600)
cx=json.loads((ROOT/'experiments/stage-search/pr441-signed75-hosting/complex-hosted/HOSTED.json').read_text());C={int(k):v for k,v in cx['global_profile'].items()};b,complex_=cert(C,73,cx['live'])
f=json.loads((P/'signed/GLOBAL-BOUND.json').read_text())['finite'];row=bound(78,9609,max(H),3);assert row['complete_row_coefficient']==19431
eta=beta=Q(1,10**30);grid=Q(1,10**27);lim=min(c,(1-beta)*b);selected=Q(math.floor((lim-grid)*10**27),10**27);assert selected<c<(1-beta)*b
chain=[Q(384599,10**10)];cuts=[]
for i in range(8):
 old=chain[-1];new=(1-selected)*selected+selected*old;gap=min(selected-new,1-new-selected,1-new-selected*(1-old),1-selected)
 assert old<new<selected<1-new and gap>0
 cutoff=max(math.ceil(36/gap**2),math.ceil(2*(4+1024)/gap));assert cutoff*gap**2>=36 and cutoff*gap>=2*(4+1024)
 cuts.append(dict(gap=str(gap),cutoff_log2=str(cutoff)));chain.append(new)
bridge=dict(semantic=dict(C0=dict(base=2,exponent=210000),strict_literal_gap=1),rows=dict(degree_gap=Q(10**6)-Q(51*20161,25)))
q=chain[-1]*(1-2*eta);ticks=(1-eta)*q/(1+q)/grid;k=Q((ticks.numerator-1)//ticks.denominator,10**27);a=A.assembly(chain[-1],b,bridge,k,eta=eta,beta=beta);assert len(a['strict_constraints'])==47 and min(a['strict_constraints'].values())>0
for leaf,kk in [(chain[-1],k+grid),((1-beta)*b,k)]:
 try:A.assembly(leaf,b,bridge,kk,eta=eta,beta=beta)
 except AssertionError:pass
 else:raise AssertionError('bad control accepted')
old=Q(78712924282401861620781,62500000000000000000000000)
r=dict(status='PASS_CONDITIONAL_TARGET_PREFIX60_SIGNED95_FINITE_ARITHMETIC_NOMINATION',kappa=str(k),bit_lower=str(c),complex_lower=str(b),gain_percent=float(100*(k/old-1)),row_bound=row,row_controls=controls(),signed_invoice=f,charged_three_level_bits=1024,bootstrap=cuts,strict_constraints={n:str(v)for n,v in a['strict_constraints'].items()},both_endpoint_engines=True,adjacent_grid_and_complex_cap_rejected=True,scope='Exact arithmetic and full eleven-stage signed prefix scan. Fresh target-prefix signed980, primitive address/common-label routes and sourceconformance require independent admission. The additional current-label target-as-source compiler interface is explicit, with154route factors/newADD charged. No published admission.')
(P/'REFINED-NOMINATION.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['kappa'],r['gain_percent'])
