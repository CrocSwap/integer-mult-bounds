# SPDX-License-Identifier: Apache-2.0
# Own full changed-bit profile, both exact moment engines, PR352 E8 pinned input, outer assembly.
import sys,pathlib,json,hashlib,struct,importlib.util
from fractions import Fraction as Q
from collections import Counter
sys.dont_write_bytecode=True
assert __debug__
sys.set_int_max_str_digits(0)
HERE=pathlib.Path(__file__).resolve().parent; ROOT=HERE.parent
P=pathlib.Path(sys.argv[4])
def load(name):
 s=importlib.util.spec_from_file_location('own_'+name,P/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M=load('moment');B=load('base_two_moment');O=load('outer')
cand=pathlib.Path(sys.argv[1]);out=pathlib.Path(sys.argv[2]);bank=pathlib.Path(sys.argv[3]) if len(sys.argv)>3 else None
rd=lambda p:json.loads(p.read_text());frames=rd(cand/'frames.json');frames=frames.get('frames',frames)
meta=rd(cand/'meta.json');ini=rd(cand/'initial.json');fin=rd(cand/'final.json');raw=(cand/'records.bin').read_bytes();sha=hashlib.sha256(raw).hexdigest();assert meta['raw_sha256']==sha
v=meta['v'];assert meta['h']==20 and v==960;H=Counter();copies=adds=units=0
for op,a,b,c,f,z in struct.iter_unpack('<6i',raw):
 if op==0 and f:H[f]+=1
 if op==2:H[z]+=1;copies+=1
 if op==1:adds+=1;units+=abs(c)
assert copies==20
res=sum(frames[str(fin[str(r)])]['dim']-frames[str(ini[str(r)])]['dim'] for r in range(2*v,meta['n']))
T=300; banks=Q(T*res,100);assert banks.denominator==1;stock=Q(4*v*T+5*banks,5);assert stock.denominator==1;stock=int(stock)
if bank:
 br=rd(bank);assert br['banks_per_stage']==banks and br['normalized_stock']==stock and br['physical_replicas']==T
hist={r:T*n for r,n in H.items()}
for r in (4,19,38,42):hist[r]=hist.get(r,0)+2*v*T//5
mass=sum(r*n for r,n in hist.items());deficit=100*stock-mass;assert deficit==122400 and max(hist)==42
root=M.certify(hist,100,stock,True);step=Q(1,10**18);c=Q(int(Q(root['lower'])*10**18),10**18)
a=M.moment(hist,100,stock,c,True);an=M.moment(hist,100,stock,c+step,True);assert a[1]<1<an[0]
fallback=32*100*100*sum(hist.values())
def second(s):
 lo,hi=B.moment(100,stock,list(hist.items()),s);bl,bh=B.moment(100,stock,[(1,fallback)],s);return lo+Q(1,10**16)*bl,hi+Q(1,10**16)*bh
b1=second(c);bn=second(c+step);assert b1[1]<1<bn[0]
receipt=rd(ROOT/'data/E8-KAPPA.json');b=Q(receipt['complex_coarse']);assert b==Q(876248285600677,10**18)
beta=Q(1,10**9);eta=Q(1,10**12);cap=(1-beta)*b;sv=min(c,Q(((cap-step)*10**18).__floor__(),10**18));chain=[Q(384599,10**10)]
for _ in range(3):
 new=(1-sv)*sv+sv*chain[-1];assert chain[-1]<new<sv<1-new;chain.append(new)
bridge=dict(proof='PR315 PROOF.md, inherited finite bridge',representation='Exact powers with source-bound finite overcharges',semantic=dict(G=dict(base=2,exponent=30000),E=dict(base=2,exponent=100000),B_upper=dict(base=2,exponent=100001),C0=dict(base=2,exponent=210000),C1=1,strict_literal_gap=1,induction_gap_lower=1),rows=dict(coefficient=20161,degree=10**6,suffix_slope=4*10**6,degree_gap=Q(10**6)-Q(51*20161,25)))
q=chain[-1]*(1-2*eta);minimum=(1-eta)*q/(1+q);ticks=minimum*10**18;k=Q((ticks.numerator-1)//ticks.denominator,10**18);asm=O.assembly(chain[-1],b,bridge,k,eta=eta,beta=beta);assert len(asm['strict_constraints'])==47 and min(asm['strict_constraints'].values())>0
try:O.assembly(chain[-1],b,bridge,k+step,eta=eta,beta=beta)
except AssertionError:pass
else:raise AssertionError('adjacent admitted')
old=Q(receipt['kappa']);result=dict(status='OWN_CHANGED_WORD_EXACT_PRICE_PHYSICAL_ADMISSION_SEPARATE',source_word_sha256=sha,helpers=meta['n']-2*v,local_histogram=dict(H),local_mass=sum(r*n for r,n in H.items()),adds=adds,unit_adds=units,residual=res,physical_replicas=T,banks_per_stage=banks,normalized_stock=stock,histogram=hist,deficit=deficit,bit_coarse=c,complex_coarse=b,kappa=k,previous_public_kappa=old,relative_percent=100*(k/old-1),first_interval=a,first_next=an,second_interval=b1,second_next=bn,ordinary_chain=chain,assembly=asm,adjacent_kappa_rejected=True,complex_input=dict(public_pr=352,head='04b4c3c478b5bd8797d2663d89d8db4dfd0ad9f2',receipt_sha256=hashlib.sha256((ROOT/'data/E8-KAPPA.json').read_bytes()).hexdigest(),unchanged_public_construction_reverification=False),cohort_candidate=dict(stock=stock,histogram=hist,coarse=c,moment_upper=a[1]),scope='Full actual own changed bit histogram is priced; inherited E8 complex input and analytic interfaces are explicit. Own word, charts, bank tiling, finite invoice remain separately source-bound checks. No unconditional integer-multiplication theorem or new Lean claim.')
out.write_text(json.dumps(result,indent=2,default=str)+'\n');print(json.dumps(dict(kappa=str(k),decimal=float(k),gain_percent=float(result['relative_percent']),c=str(c),b=str(b),banks=str(banks)),indent=2))
