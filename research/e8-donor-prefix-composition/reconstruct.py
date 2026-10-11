"""Source-bound exact three-prefix witness, without search or external dependencies.

Discovery adapts Chafik Boukhalfa's PR402 helper-window resynthesis and eumemic's
PR411 protected donor-prefix mechanism. Prepared with OpenAI Codex assistance.
This reconstruction is not a compiler, bank or asymptotic theorem admission.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
import copy,hashlib,json,sys
if not __debug__:raise RuntimeError('Assertions required')
SOURCE='7ff1782ab6fa0b846d7b00f57a034c05cd64b286eb9c3215efb184d5e9511408'
EXPECTED='01cae52711bb22f4e3255b0b9e96053a90b76aeaa6799bda9f0fb6aea3618112'
PLANS=[dict(target=171,cut=1230,deliveries=[[2000,336,563,-1,2],[2494,723,686,-1,1],[3138,723,277,-1,1],[3139,723,277,1,1]]),dict(target=208,cut=1207,deliveries=[[2004,311,255,-1,4],[3102,935,777,1,8],[3103,935,808,3,4]]),dict(target=172,cut=1237,deliveries=[[2001,336,563,-1,2],[2953,724,503,-1,1],[2953,904,358,1,2],[3140,724,280,-1,2]])]
def encode(c):return json.dumps(c,sort_keys=True,separators=(',',':')).encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def adds(g):return[(r,g[2],Q(a,b))for r,a,b in g[3]]if g[0]=='out'else[(g[2],r,Q(a,b))for r,a,b in g[3]]
def regs(g):return[g[2]]+[r for r,a,b in g[3]]+(g[4]if g[0]=='out'else[])
def axpy(t,s,q):
 for k,a in list(s.items()):
  z=t.get(k,Q(0))+q*a
  if z:t[k]=z
  else:t.pop(k,None)
def operator(c):
 v=c['v'];n=2*v+c['R'];rows=[{i:Q(1)}for i in range(n)];tot=None
 for phase in ['A','B']:
  if phase=='B':
   tot={k:dict(rows[s])for k,s,f in c['ret']}
   for t,es in enumerate(c['scat']['table']):
    for k,a,b in es:axpy(rows[v+t],tot[k],Q(a,b))
  for g in c[phase]:
   if g[0]=='out':
    src=dict(rows[g[2]])
    for t,a,b in g[3]:axpy(rows[t],src,Q(a,b))
   else:
    for s,a,b in g[3]:axpy(rows[g[2]],dict(rows[s]),Q(a,b))
 return rows,tot
def nested(a,b):
 piv={}
 for x in b:
  while x:
   k=x.bit_length()-1
   if k in piv:x^=piv[k]
   else:piv[k]=x;break
 for x in a:
  while x:
   k=x.bit_length()-1
   if k not in piv:return False
   x^=piv[k]
 return True
def histogram(c):
 v=c['v'];n=2*v+c['R'];cur=list(c['start']);H={k:Counter()for k in ['x','y','s','c']};walk=[[]for _ in range(n)]
 def climb(r,f):
  if cur[r]!=f:
   assert nested(c['frames'][cur[r]],c['frames'][f]),(r,cur[r],f)
   H['x'if r<v else'y'if r<2*v else's'][len(c['frames'][f])-len(c['frames'][cur[r]])]+=1;cur[r]=f
  if not walk[r]or walk[r][-1]!=f:walk[r].append(f)
 for phase in ['A','B']:
  if phase=='B':
   for k,s,f in c['ret']:H['c'][len(c['frames'][f])]+=1
  for g in c[phase]:
   for r in regs(g):climb(r,g[1])
 for r,f in enumerate(c['final']):climb(r,f)
 blocks={k:{str(r):z for r,z in sorted(h.items())}for k,h in H.items()}
 return blocks,sum(r*z for h in H.values()for r,z in h.items()),walk
def build(c):
 assert digest(encode(c))==SOURCE
 v=c['v'];n=2*v+c['R'];nA=len(c['A']);assert(v,n,nA)==(120,1021,1995)
 d=copy.deepcopy(c);cuts={};at=defaultdict(list)
 for p in PLANS:
  r,cut=p['target'],p['cut'];cuts[r]=cut
  assert c['B'][cut][1]>0 and any(src==r for t,src,q in adds(c['B'][cut]))
  for bi,g in enumerate(c['B'][:cut]):
   for t,src,q in adds(g):
    if src==r:assert g[1]==0
    if t==r:assert g[0]=='in'and src>=2*v
  lastzero=max([nA+bi+1 for bi,g in enumerate(c['B'][:cut])if any(src==r for t,src,q in adds(g))]+[nA])
  for pos,f,src,a,b in p['deliveries']:
   assert lastzero<=pos<=nA+cut and src>=2*v
   at[pos].append(['in',f,r,[[src,a,b]]])
 B=[]
 for bi,g in enumerate(c['B']):
  B+=sorted(at.get(nA+bi,[]),key=lambda z:len(c['frames'][z[1]]))
  if g[0]=='in'and g[2]in cuts and bi<cuts[g[2]]:B.extend(['out',g[1],src,[],[]]for src,a,b in g[3])
  else:B.append(copy.deepcopy(g))
 d['B']=B;d['blocks'],d['N'],newwalk=histogram(d);_,oldmass,oldwalk=histogram(c);assert d['N']==oldmass
 assert all(oldwalk[r]==newwalk[r]for r in range(2*v,n))
 old,ot=operator(c);new,nt=operator(d);ext=dict(c['ext']);protected=lambda row:{k:q for k,q in row.items()if k<2*v or k in ext}
 assert ot==nt and all(protected(a)==protected(b)for a,b in zip(old,new))
 assert all(old[r]==new[r]for r in list(range(v))+list(range(2*v,n)))
 assert all(new[v+t].get(r,Q(0))==0 for t in range(v)for r in ext)
 assert all({k:q for k,q in new[v+t].items()if v<=k<2*v}=={v+t:Q(1)}for t in range(v))
 K=[[t,r,q.numerator,q.denominator]for t in range(v,2*v)for r,q in sorted(new[t].items())if r>=2*v];assert len(K)==7079 and all(e[3]in(1,2,3,6)for e in K)
 changed_rows=[t for t in range(v,2*v)if old[t]!=new[t]];assert changed_rows==[124,125,171,172]
 delta=Counter()
 for h in d['blocks'].values():delta.update({int(k):z for k,z in h.items()})
 for h in c['blocks'].values():delta.subtract({int(k):z for k,z in h.items()})
 delta={k:z for k,z in delta.items()if z};assert delta=={1:-1,2:1,3:-2,5:1}
 assert digest(encode(d))==EXPECTED
 # Each actual new delivery is essential, independent of compiler projection.
 controls=[]
 for r,s in[(171,563),(172,563),(208,255)]:
  bad=copy.deepcopy(d);i=next(i for i,g in enumerate(bad['B'])if g[0]=='in'and g[2]==r and any(e[0]==s for e in g[3]));bad['B'].pop(i)
  rows,_=operator(bad);assert any(protected(a)!=protected(b)for a,b in zip(old,rows));controls.append(dict(target=r,source=s,omitted_delivery_rejected=True))
 return d,dict(status='PASS_EXACT_THREE_PROTECTED_PREFIXES_REQUIRES_FRESH_K_COMPILER',source_sha256=SOURCE,candidate_sha256=EXPECTED,plans=PLANS,all_raw_columns=n,all_helper_walks_equal=True,all_X_Y_gauged_columns_equal=True,helper_cleanup_rows_and_retained_totals_equal=True,actual_nongauged_response_changed=old!=new,changed_nongauged_response_rows=changed_rows,recomputed_response_entries=len(K),recomputed_response_sha256=digest(json.dumps(K,separators=(',',':')).encode()),histogram_delta=delta,controls_rejected=controls)
if __name__=='__main__':
 assert len(sys.argv)==3
 source,out=map(Path,sys.argv[1:]);assert digest(source.read_bytes())==SOURCE and not out.exists();c,r=build(json.loads(source.read_bytes()));out.mkdir(parents=True);(out/'candidate.json').write_bytes(encode(c));(out/'RECONSTRUCTION.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');print(r['status'],EXPECTED)
