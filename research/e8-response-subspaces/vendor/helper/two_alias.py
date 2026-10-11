"""Reconstruct PR374's retimed E8 unit with one exact clean-form substitution.
Source: PR374 21a03d2f706cdde13217e2dce8bcde0970564885, source365/data/retimed.json.gz.
PR365/374 retimings retained; helper706 replaced by helper268, then compact roles.
Frame repair follows search_bit's deterministic backward-upper/forward-lower rule.
Prepared with OpenAI Codex assistance; Apache-2.0. Inherited notices apply.
Usage: python3 -B reconstruct.py SOURCE374_RETIMED_JSON_GZ OUTPUT_JSON
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from hashlib import sha256
import copy,gzip,json,sys
assert __debug__, 'Assertions are required'
SOURCE_SHA256='31467ace2b1667630b72e488e688911a0404b4755d0d2c87560b111ed4c07998'
CANDIDATE_SHA256='82edee98e743d40654c622bca63d74937e51e49bb8c65df73c3d0499e435bed3'
DROP,USE=706,268

def canon(vals):
 b={}
 for x in vals:
  for k in sorted(b,reverse=True):
   if x>>k&1:x^=b[k]
  if x:
   k=x.bit_length()-1
   for j in list(b):
    if b[j]>>k&1:b[j]^=x
   b[k]=x
 return tuple(b[k]for k in sorted(b,reverse=True))
def inside(a,b):
 for x in a:
  for y in b:
   if x>>(y.bit_length()-1)&1:x^=y
  if x:return False
 return True
def join(a,b):return canon(a+b)
def meet(a,b):
 vals=[0]
 for x in a:vals += [y^x for y in vals]
 return canon(x for x in vals if inside((x,),b))

def build(c, drop=DROP, use=USE):
 DROP,USE=drop,use
 assert c['format']=='gcert/1' and (c['h'],c['v'])==(9,120) and c['R']in(783,782)
 v=c['v'];n=2*v+c['R'];ops=[]
 assert DROP!=USE and 2*v<=DROP<n and 2*v<=USE<n
 for phase in ['A','B']:
  for g in c[phase]:
   assert g[0]in['in','out'] and (g[0]!='out' or not g[4])
   for r,a,b in g[3]:
    d,s=(g[2],r)if g[0]=='in'else(r,g[2]);ops.append((g[1],d,s,Q(a,b)))
  if phase=='A':split=len(ops)
 assert DROP not in {r for k,r,f in c['ret']} and USE not in {r for k,r,f in c['ret']}
 # Exact original clean forms establish every substituted read and reject
 # zero-value or self-read special cases. No sampled columns or floats.
 values=[{i:Q(1)}if i<v else{}for i in range(n)];reads=writes=0
 for f,d,s,q in ops:
  if s==DROP:
   assert d!=USE and values[DROP] and values[DROP]==values[USE]
   reads+=1
  if d==DROP:writes+=1
  for key,value in list(values[s].items()):
   z=values[d].get(key,Q(0))+q*value
   if z:values[d][key]=z
   else:values[d].pop(key,None)
 assert reads and writes
 framebasis=[tuple(f)for f in c['frames']]
 gs=[(i,f,d,USE if s==DROP else s,q)for i,(f,d,s,q)in enumerate(ops)if d!=DROP]
 assert all(d!=s for i,f,d,s,q in gs)
 fixed={}
 for _,r,f in c['ret']:
  sites=[j for j,(i,ff,d,s,q)in enumerate(gs)if i<split and r in(d,s)];assert sites
  fixed[sites[-1]]=framebasis[f]
 upper=[None]*len(gs);cur=[framebasis[f]for f in c['final']]
 for j in range(len(gs)-1,-1,-1):
  _,f,d,s,q=gs[j];u=meet(cur[d],cur[s])
  if j in fixed:assert inside(fixed[j],u);u=fixed[j]
  upper[j]=u;cur[d]=cur[s]=u
 cur=[framebasis[f]for f in c['start']]
 for j,(i,f,d,s,q)in enumerate(gs):
  lo=join(cur[d],cur[s])
  if j in fixed:lo=join(lo,fixed[j])
  assert inside(lo,upper[j]);cur[d]=cur[s]=lo
 cur=[framebasis[f]for f in c['start']];new=[]
 for j,(i,f,d,s,q)in enumerate(gs):
  fr=join(join(cur[d],cur[s]),meet(framebasis[f],upper[j]))
  if j in fixed:fr=join(fr,fixed[j])
  assert inside(fr,upper[j]);cur[d]=cur[s]=fr;new.append((i,fr,d,s,q))
 out=copy.deepcopy(c);out['R']-=1;physical=[r for r in range(n)if r!=DROP];ix={r:i for i,r in enumerate(physical)}
 out['start']=[c['start'][r]for r in physical];out['final']=[c['final'][r]for r in physical];out['ret']=[[k,ix[r],f]for k,r,f in c['ret']]
 ids={tuple(f):i for i,f in enumerate(out['frames'])}
 def fid(fr):
  if fr not in ids:ids[fr]=len(out['frames']);out['frames'].append(list(fr))
  return ids[fr]
 for phase in ['A','B']:
  out[phase]=[['in',fid(fr),ix[d],[[ix[s],q.numerator,q.denominator]]]for i,fr,d,s,q in new if(i<split)==(phase=='A')]
 cur=list(out['start']);hs={k:Counter()for k in 'xysc'}
 def climb(r,f):
  old=cur[r];assert inside(tuple(out['frames'][old]),tuple(out['frames'][f]))
  if f!=old:hs['x'if r<v else'y'if r<2*v else's'][len(out['frames'][f])-len(out['frames'][old])]+=1
  cur[r]=f
 for phase in ['A','B']:
  if phase=='B':
   for _,r,f in out['ret']:assert cur[r]==f;hs['c'][len(out['frames'][f])]+=1
  for _,f,d,ss in out[phase]:
   climb(d,f)
   for s,_,_ in ss:climb(s,f)
 for r,f in enumerate(out['final']):climb(r,f)
 out['blocks']={k:{str(r):cnt for r,cnt in sorted(h.items())}for k,h in hs.items()};out['N']=sum(r*cnt for h in hs.values()for r,cnt in h.items())
 # This exact legacy discovery metadata string is retained to reproduce the
 # frozen candidate bytes; source attribution is recorded above and in receipt.
 out['derived_from']='Pinned PR373 Sussman E8 unit: exact clean-form helper substitution with nested frame repair'
 return out,dict(drop=DROP,use=USE,substituted_reads=reads,deleted_writes=writes,original_scalar_primitives=len(ops),candidate_scalar_primitives=len(new),original_roles=n,candidate_roles=n-1)

if __name__=='__main__':
 assert len(sys.argv)==3,'SOURCE374_RETIMED_JSON_GZ OUTPUT_JSON'
 raw=Path(sys.argv[1]).read_bytes();assert sha256(raw).hexdigest()==SOURCE_SHA256
 c=json.loads(gzip.decompress(raw));receipts=[]
 for drop,use,want in [(706,268,'82edee98e743d40654c622bca63d74937e51e49bb8c65df73c3d0499e435bed3'),(707,323,'65067f247fcc5400f000d757f62a07bd77d57626c34223e59d0d7bc0cee056ff')]:
  c,receipt=build(c,drop,use);body=json.dumps(c,sort_keys=True,separators=(',',':')).encode();assert sha256(body).hexdigest()==want
  receipt['output_sha256']=want;receipts.append(receipt)
 Path(sys.argv[2]).write_bytes(body)
 print(json.dumps(dict(status='PASS_TWO_DETERMINISTIC_HELPER_SUBSTITUTIONS',source_sha256=SOURCE_SHA256,steps=receipts),indent=2))
