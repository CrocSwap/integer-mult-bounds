"""Independent literal dyadic primitive replay of the emitted Hamming word.
Does not import the Hamming producer or its scalar emitter.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from hashlib import sha256
import gzip,json,sys
if not __debug__: raise SystemExit('Assertions required')
assert len(sys.argv)==3, 'Usage: primitive_audit.py FRESH_SPLIT_DIRECTORY NEW_RECEIPT'
D=Path(sys.argv[1]).resolve();OUTPUT=Path(sys.argv[2]).resolve();assert not OUTPUT.exists();ir=json.loads(gzip.decompress((D/'GLOBAL-TEMPLATE.json.gz').read_bytes()));c=json.loads(gzip.decompress((D/'CANONICAL-WORD.json.gz').read_bytes()));inv=json.loads((D/'INTEGRATION.json').read_bytes());N=2*c['v']+c['R'];assert N==800
W=('W',0)
def run(events,omit=False):
 rows={('L',r):{r:Q(1)}for r in range(N)};norm={r:Q(1)for r in rows};count=Counter();peak=Q(1);largest=Q(1);denmax=1;removed=False;trace=sha256()
 def op(tag,t,s=None,a=1):
  nonlocal peak,largest,denmax,removed
  if omit and not removed and tag=='halve':removed=True;return
  count[tag]+=1;trace.update((json.dumps([tag,t,s,a],separators=(',',':'))+'\n').encode())
  if tag=='clear':rows[t]={};norm[t]=Q(0)
  elif tag=='copy':rows[t]=dict(rows[s]);norm[t]=norm[s]
  elif tag in ('double','halve','negate'):
   k={'double':Q(2),'halve':Q(1,2),'negate':Q(-1)}[tag];rows[t]={j:q*k for j,q in rows[t].items()};norm[t]*=abs(k)
  elif tag=='accumulate':
   row=rows.setdefault(t,{});norm[t]=norm.get(t,Q(0))+abs(a)*norm[s]
   for j,q in list(rows[s].items()):
    v=row.get(j,Q(0))+a*q
    if v:row[j]=v
    else:row.pop(j,None)
  else:raise AssertionError(tag)
  peak=max(peak,norm[t])
  for q in rows[t].values():largest=max(largest,abs(q));denmax=max(denmax,q.denominator)
 for event in events:
  if event[0] in ('climb','center'):assert not rows.get(W,{})
  if event[0]!='scalar':continue
  e=event[1];tag=e[0];t=tuple(e[1])
  if tag in ('copy','clear'):op(tag,t,tuple(e[2])if tag=='copy'else None)
  elif tag=='scale':
   q=Q(e[2],e[3]);a,b=abs(q.numerator),q.denominator;assert a&(a-1)==0 and b&(b-1)==0
   for _ in range(a.bit_length()-1):op('double',t)
   for _ in range(b.bit_length()-1):op('halve',t)
   if q<0:op('negate',t)
  else:
   assert tag=='add';s=tuple(e[2]);q=Q(e[3],e[4]);a,b=abs(q.numerator),q.denominator;assert a and b&(b-1)==0 and t!=s
   op('clear',W)
   for i,bit in enumerate(bin(a)[2:]):
    if i:op('double',W)
    if bit=='1':op('accumulate',W,s)
   for _ in range(b.bit_length()-1):op('halve',W)
   op('accumulate',t,W,1 if q>0 else-1);op('clear',W)
 want={('L',r):{r:Q(1)}for r in range(N)};back=events is ir['local_programs']['backward']
 for t in range(c['v']):want['L',t if back else c['v']+t][c['v']+t if back else t]=Q(-1 if back else 1)
 correct=all(rows[k]==v for k,v in want.items())and all(not row for k,row in rows.items()if k[0]!='L')
 if omit:assert removed and not correct;return dict(omitted_actual_first_halve_rejected=True)
 assert correct and peak<2**192
 return dict(columns=N,all_live_endpoints_exact=True,private_work_zero=True,primitive_counts=dict(count),real_component_primitives=2*sum(count.values()),primitive_trace_sha256=trace.hexdigest(),cancellation_free_peak=str(peak),prefix_bits_bound=peak.numerator.bit_length()-peak.denominator.bit_length()+1,largest_actual_scalar=str(largest),largest_actual_denominator=denmax)
out={}
for ori,events in ir['local_programs'].items():
 z=run(events);assert z['real_component_primitives']==inv['local_program_checks'][ori]['real_component_primitive_bound'];z.update(run(events,True));out[ori]=z;print(ori,z['real_component_primitives'],z['prefix_bits_bound'],flush=True)
r=dict(status='PASS_INDEPENDENT_LITERAL_PRIMITIVES_ALL800_COLUMNS_AND_ACTUAL_PAYMENT',orientations=out,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),canonical_word_sha256=sha256((D/'CANONICAL-WORD.json.gz').read_bytes()).hexdigest(),global_template_sha256=sha256((D/'GLOBAL-TEMPLATE.json.gz').read_bytes()).hexdigest(),canonical_word_uncompressed_sha256=sha256(gzip.decompress((D/'CANONICAL-WORD.json.gz').read_bytes())).hexdigest(),global_template_uncompressed_sha256=sha256(gzip.decompress((D/'GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest(),scope='Finite scalar lowering, private coefficient lifetime and paid literal dyadic primitives only; generalized complex lifting, full global geometry, bit supplier and analytic conditions remain separate.')
OUTPUT.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');print('PASS',sha256(OUTPUT.read_bytes()).hexdigest())
