"""Independent exact pricing cross-check of a completed PR254-plus25 replay.

Consumes the fresh physical word and bank allocation, not an estimated gain.
Uses the two original Python moment engines and outer assembler archived in
the source-bound replay, independently of the native atanh moment checker.
Prepared with substantial OpenAI Codex assistance; original notices retained.
"""
from pathlib import Path
from array import array
from collections import Counter
from fractions import Fraction as Q
import hashlib,importlib.util,json,sys
assert __debug__
R=Path(sys.argv[1]).resolve(); U=R/'upstream'; L=R/'lead'
read=lambda p:json.loads(p.read_text())
def module(name):
    s=importlib.util.spec_from_file_location('independent254_'+name,U/(name+'.py'))
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
cost=module('moment');base2=module('base_two_moment');outer=module('outer')
raw=array('i');data=(L/'COHORT249-RECORDS.bin').read_bytes();raw.frombytes(data)
H=Counter()
for k in range(0,len(raw),6):
    op,a,b,c,f,z=raw[k:k+6]
    if op==0 and f:H[f]+=1
    elif op==2:H[z]+=1
local=dict(H);H=Counter({r:40*n for r,n in H.items()})
for r in (4,23,46,50):H[r]+=16*1760
bank=read(R/'compiler/COHORT-BANK-REVIEW.json');assert bank['literal_stock']%5==0
W=bank['literal_stock']//5;native=read(L/'COHORT-EXACT-PRICE.json')['cohort_candidate']
assert W==native['stock'] and dict(H)=={int(r):n for r,n in native['histogram'].items()}
root=cost.certify(dict(H),120,W,True);coarse=Q(int(Q(root['lower'])*10**18),10**18)
assert coarse==Q(native['coarse'])
current=cost.moment(H,120,W,coarse,True);adjacent=cost.moment(H,120,W,coarse+Q(1,10**18),True)
assert current[1]<1<adjacent[0]
fallback=32*120*120*sum(H.values())
_,upper=base2.moment(120,W,list(H.items()),coarse)
_,bad=base2.moment(120,W,[(1,fallback)],coarse)
lower,_=base2.moment(120,W,list(H.items()),coarse+Q(1,10**18))
badlower,_=base2.moment(120,W,[(1,fallback)],coarse+Q(1,10**18))
assert upper+Q(1,10**16)*bad<1<lower+Q(1,10**16)*badlower
chain=[Q(384599,10**10)]
for _ in range(3):chain.append((1-coarse)*coarse+coarse*chain[-1])
bit=chain[-1];complex_coarse=Q(747454944651775,10**18)
eta=Q(1,10**12);beta=Q(1,10**9)
bridge=dict(proof='inherited source527 bridge',representation='Exact powers with retained finite overcharges',semantic=dict(G=dict(base=2,exponent=30000),E=dict(base=2,exponent=100000),B_upper=dict(base=2,exponent=100001),C0=dict(base=2,exponent=210000),C1=1,strict_literal_gap=1,induction_gap_lower=1),rows=dict(coefficient=20161,degree=10**6,suffix_slope=4*10**6,degree_gap=Q(10**6)-Q(51*20161,25)))
q=bit*(1-2*eta);minimum=(1-eta)*q/(1+q);ticks=minimum*10**18
kappa=Q((ticks.numerator-1)//ticks.denominator,10**18)
assert kappa==Q(native['kappa'])>Q(71046520063283,10**17)
assembly=outer.assembly(bit,complex_coarse,bridge,kappa,eta=eta,beta=beta)
assert len(assembly['strict_constraints'])==47 and len(assembly['margins'])==7
assert min(assembly['strict_constraints'].values())>0
try:outer.assembly(bit,complex_coarse,bridge,kappa+Q(1,10**18),eta=eta,beta=beta)
except AssertionError:pass
else:raise AssertionError('adjacent kappa admitted')
def serial(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):serial(v)for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [serial(v)for v in x]
    return x
result=dict(status='PASS_FRESH_PHYSICAL_WORD_TWO_INDEPENDENT_PYTHON_MOMENTS_AND_OUTER47',physical_word_sha256=hashlib.sha256(data).hexdigest(),local_histogram=local,normalized_histogram=dict(H),normalized_stock=W,coarse=coarse,coarse_root_interval=root,ordinary_chain=chain,kappa=kappa,kappa_decimal=cost.decimal(kappa),assembly=assembly,adjacent_coarse_rejected=True,adjacent_kappa_rejected=True,independent_base_two_pass=True,scope='Independent pricing cross-check; physical, bank and finite admission is provided by the immutable full construction replay, with the same inherited conditional all-size interfaces.')
(R/'INDEPENDENT-PYTHON-PRICE.json').write_text(json.dumps(serial(result),indent=2)+'\n')
print('PASS independent Python pricing',cost.decimal(kappa),flush=True)
