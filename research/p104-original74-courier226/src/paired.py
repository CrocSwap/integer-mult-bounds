#!/usr/bin/env python3
"""Exact paired replay, negative controls, and fixed-caller invoice for 226/990."""
import copy,gzip,hashlib,importlib.util,json,time,traceback
from collections import Counter
from pathlib import Path
D=Path(__file__).resolve().parent
P=D
spec=importlib.util.spec_from_file_location('independent7644',P/'source7644/independent.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def load(p):return json.loads(gzip.decompress(p.read_bytes()))
def canon(w):return hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def save(name,x):(D/name).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
a=load(P/'baseline.json.gz');b=load(D/'candidate.json.gz'); M=json.loads((D/'manifest.json').read_text());align={int(k):v for k,v in M['aligned_origins'].items()}
assert canon(a)==M['source_word_sha256'] and canon(b)==M['candidate_word_sha256']
assert all(a['program'][i]==b['program'][j] for i,j in align.items())
n=a['public'];operands=lambda e:e[1:3] if e[0] in ('ADD','COPY') else e[1:2]
watch={i:j for i,j in align.items() if max(operands(a['program'][i]))>=n or a['program'][i][0]=='COPY'}
assert len(watch)==630,(len(watch),n)
t=time.monotonic();print('starting paired exact replay',flush=True)
x=m.replay(a,set(watch));print('baseline replay seconds',round(time.monotonic()-t,3),flush=True)
y=m.replay(b,set(watch.values()));print('candidate replay seconds',round(time.monotonic()-t,3),flush=True)
for k in ('rows','erased','lifetime','peak','rises','owned_events','copies','targets','grid','mass'):assert x[k]==y[k],k
assert len(x['erased'])==74 and not x['bad_helpers'] and not y['bad_helpers']
assert all(x['readings'][i]==y['readings'][j] for i,j in watch.items())
delta=Counter(y['paid']);delta.subtract(x['paid']);delta={str(k):v for k,v in sorted(delta.items()) if v};assert delta=={'1':-1,'2':-1,'3':1},delta
def observable_hash(z, indices):
 data = {'rows': z['rows'], 'erased': z['erased'], 'lifetime': z['lifetime'],
         'peak': z['peak'], 'rises': z['rises'], 'owned_events': z['owned_events'],
         'copies': z['copies'], 'targets': z['targets'], 'grid': z['grid'], 'mass': z['mass'],
         'readings': [z['readings'][i] for i in indices]}
 return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
source_observables = observable_hash(x, sorted(watch))
candidate_observables = observable_hash(y, [watch[i] for i in sorted(watch)])
assert source_observables == candidate_observables, 'observable digest mismatch'
result={'status':'PASS_PAIRED_EXACT_STRICT74','source_sha256':canon(a),'candidate_sha256':canon(b),'source_observable_sha256':source_observables,'candidate_observable_sha256':candidate_observables,'public_rows':n,'observations':len(watch),'ordered_clears':len(x['erased']),'copies':len(x['copies']),'peak':x['peak'],'rises':x['rises'],'native_paid_delta':delta,'source_paid':dict(x['paid']),'candidate_paid':dict(y['paid']),'source_targets':dict(x['targets']),'candidate_targets':dict(y['targets']),'grid':x['grid'],'mass':x['mass'],'mass_source_at':x['mass_at'],'mass_candidate_at':y['mass_at'],'elapsed_seconds':round(time.monotonic()-t,3)}
save('paired.json',result);print(json.dumps(result,sort_keys=True),flush=True);print('PASS paired; beginning controls',flush=True)
# Full-caller invoice inherits all fixed external terms and adjusts only exact native delta.
inv=json.loads((P/'baseline-invoice.json').read_text()); inv2=copy.deepcopy(inv)
for k,v in delta.items():inv2['paid'][k]+=17*v
assert sum(inv['paid'].values())==110298 and sum(inv2['paid'].values())==110281
assert inv['targets']==inv2['targets'] and sum(inv2['targets'].values())==22461
assert json.loads((D/'candidate-invoice.json').read_text()) == inv2, 'candidate invoice mismatch'
def hist(z):
 p={int(k):v for k,v in z['paid'].items()};t={int(k):v for k,v in z['targets'].items()};return {r:t.get(r,0)-p.get(r,0) for r in p.keys()|t.keys()}
from fractions import Fraction
old,new=hist(inv),hist(inv2);lo,hi=m.crossing(old);nl,nh=m.crossing(new)
assert nl>hi
# Conservative public claim follows the original public gate slack of 7e-14 and 1e-13 granularity.
slack=Fraction(7,10**14); scaled=(nl-slack)*10**13;claim=Fraction((scaled.numerator-1)//scaled.denominator,10**13)
assert claim>hi
points={}
for label,h,q,expect in [('candidate_claim_plus_slack',new,claim+slack,1),('old_at_new_claim',old,claim,-1),('candidate_claim',new,claim,1)]:
 dl,du=m.decimal_moment(h,q); il,iu=m.dyadic_moment(h,q)
 assert (dl>0 and il>0) if expect==1 else (du<0 and iu<0)
 points[label]={'point':str(q),'decimal_lower':str(dl),'decimal_upper':str(du),'dyadic_lower':str(il),'dyadic_upper':str(iu)}
price={'source_bracket':[str(lo),str(hi)],'candidate_bracket':[str(nl),str(nh)],'strict_gain_lower':str(nl-hi),'public_claim':str(claim),'public_claim_decimal':str(float(claim)),'public_slack':str(slack),'points':points,'native_paid_delta':delta,'source_paid_count':sum(inv['paid'].values()),'candidate_paid_count':sum(inv2['paid'].values()),'productive_count':sum(inv2['targets'].values()),'method':'#7644 decimal directed bisection plus dyadic integer-root signs, 17-call inherited full invoice'}
save('price.json',price);print('PASS directed prices',price['candidate_bracket'],price['public_claim_decimal'],flush=True)
controls={}
def control(name,mutate):
 bad=copy.deepcopy(b); mutate(bad['program'])
 try:
  z=m.replay(bad,set(watch.values()))
  ok=(z['rows']!=x['rows'] or z['erased']!=x['erased'] or any(z['readings'][j]!=x['readings'][i] for i,j in watch.items()))
  assert ok,'mutation was not rejected'
  controls[name]={'rejected':True,'reason':'paired output or protected observation differs'}
 except (AssertionError,ValueError) as e:
  if str(e)=='mutation was not rejected':raise
  controls[name]={'rejected':True,'reason':str(e)}
 print('control',name,controls[name],flush=True);save('controls.json',controls)
def wrong_sign(p):
 i=p.index(['ADD',990,226,'-1',719]);p[i]=['ADD',990,226,'1',719]
def chronology(p):
 i=p.index(['ADD',990,226,'1',127]);e=p.pop(i);j=p.index(['ADD',1477,226,'1',127]);p.insert(j+1,e)
control('wrong_encode_sign',wrong_sign)
# A late decode after a read of 226 may be observationally equivalent: use the meaningful control
# decode before 990 arrives at chart 127, which must fail legality.
def bad_chronology(p):
 i=p.index(['ADD',990,226,'1',127]);e=p.pop(i);j=p.index(['MOVE',990,907,127,False]);p.insert(j,e)
control('decode_before_990_arrives',bad_chronology)
print('PASS all controls elapsed',round(time.monotonic()-t,3),flush=True)
