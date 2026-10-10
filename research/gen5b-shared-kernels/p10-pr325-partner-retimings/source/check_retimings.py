from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import packet325 as contract
contract.require_assertions()
contract.verify_inputs()
"""Independent PR325 bounded source-retiming census. Upstream files are inert.
Own construction and proof code, OpenAI assistance; Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
from functools import lru_cache
from math import gcd,lcm
import json,gzip,hashlib
P=contract.SOURCE
if not __debug__:raise RuntimeError('Assertions must be enabled')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(n):
 b=(P/n).read_bytes();return json.loads(gzip.decompress(b)if str(n).endswith('.gz')else b)
def dump(n,x):
 b=(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode();(P/n).write_bytes(gzip.compress(b,mtime=0)if n.endswith('.gz')else b)
def rr(rows):
 a=[list(map(Q,row))for row in rows];k=0;piv=[]
 for j in range(20):
  z=next((i for i in range(k,len(a))if a[i][j]),None)
  if z is None:continue
  a[k],a[z]=a[z],a[k];v=a[k][j];a[k]=[q/v for q in a[k]]
  for i in range(len(a)):
   if i!=k and a[i][j]:v=a[i][j];a[i]=[q-v*r for q,r in zip(a[i],a[k])]
  piv.append(j);k+=1
 return a[:k],piv
def integer(row):
 d=lcm(*(x.denominator for x in row));v=[int(x*d)for x in row];g=gcd(*v);return[x//g for x in v]if g else v
def null(rows):
 a,p=rr(rows);out=[]
 for j in range(20):
  if j in p:continue
  v=[Q(0)]*20;v[j]=Q(1)
  for i,k in enumerate(p):v[k]=-a[i][j]
  out.append(integer(v))
 return out
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def histogram(ds):
 assert all(a<=b for a,b in zip(ds,ds[1:]));return Counter(b-a for a,b in zip(ds,ds[1:])if b>a)
def run():
 S=read('SOURCES.json');assert S['head']=='0eca9340a3df6141b8e71a41638c3937b3522888'
 manifest=read('inputs/MANIFEST.json');assert sha(P/'inputs/MANIFEST.json')==S['manifest_sha256']=='dfbb1190533dd8fb52eeafc2483f7992bdc3909607097947960ffa830bf373f6'
 for z in S['files']:
  b=(P/'inputs'/z['local']).read_bytes();assert len(b)==z['bytes']and hashlib.sha256(b).hexdigest()==z['sha256'];assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==z['git_blob']
  if z['path']!='MANIFEST.json':assert manifest['files'][z['path']]==z['sha256']
 load=lambda name:read('inputs/bitword__selected__bit__'+name+'_p10.json'+('.gz'if name in('word','frames')else''))
 w,g,F,K=(load(n)for n in('word','graph','frames','kchron'));F={int(k):v for k,v in F['frames'].items()};K=K['entries'];pins=read('inputs/word-pins.json');v=g['v'];assert v==960 and g['h']==20 and len(K)==480
 ops=w['ops'];R=1+max(max(r[:2])for r in ops);phase=sorted(w['phase1']);ps=set(phase);rest=[i for i in range(len(ops))if i not in ps];order=phase+rest;assert len(order)==len(set(order))==len(ops)
 aliases={b:a for a,b in w['pairs']};assert len(aliases)==len(set(aliases.values()))==960 and not set(aliases)&set(aliases.values());regs=sorted(set(range(R))-set(aliases));idx={r:1920+i for i,r in enumerate(regs)};phys=lambda r:idx[aliases.get(r,r)];n=1920+len(regs);source={int(k):s for k,s in w['sources'].items()};assert set(source)==set(range(v))and len(set(source.values()))==v
 assert not set(source.values())&(set(aliases)|set(aliases.values()));assert R==9060 and n==10020
 gauges={z['role']:z for z in w['gauges']};assert len(gauges)==2160 and not set(gauges)&set(source.values())
 # Entire literal scalar/COPY projection from this word, including compensated aliases.
 adj=[{}for _ in range(R)]
 for z,r in zip(g['roots'],w['rootroles']):
  assert z['coefficient']==1
  for t in z['targets']:adj[r][t]=adj[r].get(t,0)+1
 for i in reversed(order):
  a,b,_=ops[i]
  for t,c in adj[a].items():adj[b][t]=adj[b].get(t,0)+c
 events=[];even=0
 def emit(op,a,b,c,f,semantic):
  nonlocal even
  if op==1 and not c%2:even+=1;return
  events.append(dict(op=op,a=a,b=b,c=c,frame=f,semantic=semantic))
 def add(a,b,c,f,s):assert a!=b;emit(1,a,b,c,f,s)
 def compensate(r):
  f=gauges[r]['frame']if r in gauges else-1
  for t,c in sorted(adj[r].items()):add(960+t,phys(r),-c,f,['gauge'if r in gauges else'plain',r,t])
 for r in range(R):
  if r not in gauges:compensate(r)
 for q in range(v):add(phys(source[q]),q,1,w['source_frame'][q],['inject',q])
 def gate(i,sign):
  a,b,_=ops[i];add(phys(a),phys(b),sign,w['op_frame'][i]if sign==1 else w['full_frame'],['forward'if sign==1 else'inverse',i])
 for i in phase:gate(i,1)
 for j,(z,r)in enumerate(zip(g['roots'],w['rootroles'])):
  if z['kind']=='center':
   emit(2,phys(r),n,0,w['root_frame'][j],['copy',j])
   for t in z['targets']:add(960+t,n,1,-1,['center_read',j,t])
   emit(3,phys(r),n,0,w['root_frame'][j],['erase',j])
 at=defaultdict(list)
 for z in reversed(w['gauges']):at[w['reads'].get(str(z['role']),len(phase))-len(phase)].append(z['role'])
 assert set(at)<=set(range(len(rest)+1))
 for j,i in enumerate(rest):
  for r in at[j]:compensate(r)
  gate(i,1)
 for r in at[len(rest)]:compensate(r)
 deliveries=defaultdict(list)
 for k,e in enumerate(K):deliveries[e['deliver_after_root']].append(k)
 setup={};delivery=defaultdict(list);cleanup={}
 for j,(z,r)in enumerate(zip(g['roots'],w['rootroles'])):
  if z['kind']=='side':
   for t in z['targets']:add(960+t,phys(r),1,w['root_frame'][j],['root',j,t])
  for k in deliveries[j]:
   e=K[k];a,b=e['carrier'],e['passive'];setup[k]=len(events);add(a,b,1,e['mix_frame'],['partner_setup',k,j])
   for t in e['receivers']:delivery[k].append(len(events));add(960+t,a,1,e['deliver_frame'],['partner_delivery',k,j,t])
 for k,e in enumerate(K):cleanup[k]=len(events);add(e['carrier'],e['passive'],-1,w['full_frame'],['partner_cleanup',k])
 for i in reversed(order):gate(i,-1)
 for q in range(v):add(phys(source[q]),q,-1,w['full_frame'],['uninject',q])
 assert sum(e['op']==1 for e in events)==pins['weighted_scalar_events']==350640
 assert sum(abs(e['c'])for e in events if e['op']==1)==pins['literal_unit_additions']==352560
 assert even==pins['removed_even_adds']==578560
 def replay(reverse=False):
  col=[1<<i for i in range(n+1)];norm=[1]*(n+1);work=False;peak=1
  for e in reversed(events)if reverse else events:
   op,a,b,c=e['op'],e['a'],e['b'],e['c'];op=(5-op)if reverse and op in(2,3)else op
   if op==1:col[a]^=col[b];norm[a]+=abs(c)*norm[b];peak=max(peak,norm[a])
   elif op==2:assert not work;work=True;col[b]=col[a];norm[b]=norm[a]
   else:assert op==3 and work and col[a]==col[b];work=False;col[b]=0;norm[b]=0
  assert not work
  for q in range(n):assert col[q]==((1<<q)^(1<<(q-v))if v<=q<2*v else 1<<q),('F2 failure',q,reverse)
  return peak
 fw,bw=replay(),replay(True);assert(fw,bw)==(pins['forward_max_row_l1'],pins['inverse_max_row_l1'])
 original_scalar=[[e[k]for k in('op','a','b','c')]for e in events]
 original_copy=[dict(e)for e in events if e['op']in(2,3)]
 @lru_cache(None)
 def frame(f):
  z=F[f];B=z.get('b');A=z.get('a');B=null(A)if B is None else B;A=null(B)if A is None else A
  assert len(rr(B)[0])==z['dim']and len(rr(A)[0])==20-z['dim'];assert all(dot(a,b)==0 for a in A for b in B);return B,A,z['dim']
 def sub(a,b):B,_,d=frame(a);_,A,e=frame(b);return d<=e and all(dot(x,y)==0 for x in A for y in B)
 chi=[[int(j in g['labels'][q])for j in range(20)]for q in range(v)]
 used=Counter();oldH=Counter();newH=Counter();selection=[];controls=Counter();orig_frames=[e['frame']for e in events]
 for k,e in enumerate(K):
  a,b=e['carrier'],e['passive'];old,new=e['mix_frame'],e['deliver_frame'];B,A,d=frame(new);M,MA,md=frame(old);assert(md,d)==(2,18)
  assert g['partner_mix'][k]=={x:e[x]for x in('carrier','passive','receivers')}
  assert len(set(g['labels'][a])&set(g['labels'][b]))==1 and sub(old,new)
  assert all(dot(row,chi[q])==0 for row in A+MA for q in(a,b));assert len(rr([chi[a],chi[b]])[0])==2
  assert len(e['receivers'])==2 and len(set(e['receivers']))==2
  j=e['deliver_after_root'];assert g['roots'][j]['kind']=='side'and sorted(g['roots'][j]['targets'])==sorted(e['receivers'])
  assert all(dot([3*z-1 for z in chi[t]],row)==0 for t in e['receivers']for row in B)
  assert setup[k]+1==delivery[k][0]and delivery[k][0]+1==delivery[k][1]<cleanup[k]
  assert events[setup[k]]['a']==a and events[setup[k]]['b']==b and events[setup[k]]['frame']==old
  chains={};newchains={}
  for q in(a,b):
   f=w['source_frame'][q];SB,SA,sd=frame(f);assert sd==1 and all(dot(row,chi[q])==0 for row in SA)and sub(f,old)
   ch=[f,old]+([new]if q==a else[])+[w['full_frame']];assert ch==e['carrier_chain'if q==a else'passive_chain'];nh=[f,new,w['full_frame']]
   for x,y in zip(ch,ch[1:]):assert sub(x,y)
   for x,y in zip(nh,nh[1:]):assert sub(x,y)
   oldH.update(histogram([frame(x)[2]for x in ch]));newH.update(histogram([frame(x)[2]for x in nh]));used[q]+=1;chains[q]=ch;newchains[q]=nh
  # Small exact integral Gram witness for codimension two, G_inverse=I-J/11.
  H=[[11*dot(x,y)-sum(x)*sum(y)for y in A]for x in A];det=H[0][0]*H[1][1]-H[0][1]*H[1][0];assert det!=0
  assert len(rr(B[:-1])[0])==17;controls['deleted_basis_row']+=1
  bad=[row[:]for row in A];bad[0][g['labels'][a][0]]+=1;assert any(dot(row,chi[a])for row in bad);controls['wrong_containment']+=1
  assert old!=new;controls['retained_rank2_rejected']+=1
  # Omitting this setup or its inverse changes the formal source endpoint.
  assert {a:1,b:-1}!={a:1}and {a:1,b:1}!={a:1};controls['setup_omission']+=1;controls['cleanup_omission']+=1
  selection.append(dict(pair=k,carrier=a,passive=b,physical_source_helpers=[phys(source[a]),phys(source[b])],setup_event=setup[k],delivery_events=delivery[k],cleanup_event=cleanup[k],deliver_after_root=j,old_frame=old,new_frame=new,new_basis=B,new_annihilator=A,old_chains=chains,new_chains=newchains,gram_inverse_integer=H,gram_inverse_integer_determinant=det))
  events[setup[k]]['frame']=new
 assert used==Counter({q:1 for q in range(v)})and oldH=={1:960,2:480,16:480,18:480}and newH=={2:960,17:960}
 # Scan actual source operands across the entire reconstructed scalar word.
 states=[{q:1}for q in range(v)];paths={q:[w['source_frame'][q]]for q in range(v)};projection=[];integer_checks=0
 for i,e in enumerate(events):
  if e['op']!=1:continue
  ext=[q for q in(e['a'],e['b'])if q<v]
  if not ext:continue
  f=e['frame'];B,A,d=frame(f)
  for q in ext:
   assert sub(paths[q][-1],f)
   if paths[q][-1]!=f:paths[q].append(f)
   for source_id,coefficient in states[q].items():
    assert coefficient and all(dot(row,chi[source_id])==0 for row in A);integer_checks+=1
  if e['a']<v:
   a,b,c=e['a'],e['b'],e['c'];assert b<v
   for q,k in states[b].items():states[a][q]=states[a].get(q,0)+c*k
   states[a]={q:k for q,k in states[a].items()if k}
  projection.append(dict(event=i,**e))
 assert states==[{q:1}for q in range(v)]
 for z in selection:
  for q,ch in z['new_chains'].items():assert paths[q]==ch
 assert len(projection)==3840 and integer_checks==6240
 uses=defaultdict(list)
 for e in projection:
  for q in (e['a'],e['b']):
   if q<v:uses[q].append(e)
 for z in selection:
  a,b=z['carrier'],z['passive'];z['carrier_uses']=[e['event']for e in uses[a]];z['passive_uses']=[e['event']for e in uses[b]]
  assert [e['semantic'][0]for e in uses[a]]==['inject','partner_setup','partner_delivery','partner_delivery','partner_cleanup','uninject']
  assert [e['semantic'][0]for e in uses[b]]==['inject','partner_setup','partner_cleanup','uninject']
  assert z['carrier_uses'][1]==z['passive_uses'][1]==z['setup_event']and z['carrier_uses'][-2]==z['passive_uses'][-2]==z['cleanup_event']
 changed=[i for i,e in enumerate(events)if e['frame']!=orig_frames[i]];assert changed==sorted(setup.values())and len(changed)==480
 scalar_projection=[[e[k]for k in('op','a','b','c')]for e in events]
 assert scalar_projection==original_scalar and [e for e in events if e['op']in(2,3)]==original_copy
 dump('retiming-selection.json',dict(schema='pr325-partner-mix-retiming/1',head=S['head'],entries=selection))
 dump('source-events.json.gz',projection);dump('scalar-events.json.gz',events);dump('physical-source-map.json',{q:dict(virtual=source[q],physical=phys(source[q]))for q in range(v)})
 delta=newH.copy();delta.subtract(oldH);delta={r:c for r,c in sorted(delta.items())if c}
 out=dict(status='PASS_ALL480_PR325_PARTNER_MIX_RETIMINGS_RAW_LOCAL_PROOF',head=S['head'],word_gzip_sha256=sha(P/'inputs/bitword__selected__bit__word_p10.json.gz'),frames_gzip_sha256=sha(P/'inputs/bitword__selected__bit__frames_p10.json.gz'),sources_sha256=sha(P/'SOURCES.json'),checker_sha256=sha(Path(__file__)),admitted=480,rejected=0,source_columns=960,physical_helpers=8100,formal_columns=n,all_source_pairs_disjoint=True,all_actual_source_incidence_paths_pass=True,all_integer_operand_sources_contained=True,integer_operand_source_checks=integer_checks,source_incidence_events=len(projection),changed_setup_frames=len(changed),source_histogram_before=oldH,source_histogram_after=newH,local_histogram_delta=delta,source_rank_mass=sum(r*c for r,c in newH.items()),all480_new_frames_G_nondegenerate=True,gram_determinants=dict(Counter(z['gram_inverse_integer_determinant']for z in selection)),source_endpoints_exactly_restored=True,scalar_projection_unchanged=True,COPY_and_ERASE_records_byte_equivalent=True,all480_passive_sources_have_no_intervening_use=True,retained_framed_word_invariant_required=True,scalar_projection_sha256=hashlib.sha256(json.dumps(scalar_projection,separators=(',',':')).encode()).hexdigest(),full_F2_forward_and_inverse_all_columns_pass=True,weighted_additions=350640,literal_unit_additions=352560,copies=20,forward_norm=fw,inverse_norm=bw,removed_even_additions=even,controls=dict(controls),upstream_programs_executed=False,prior_role_or_frame_selections_imported=False,scope='Bounded local source-retiming proof on independently reconstructed PR325 scalar/COPY projection. No kernels or packing constructed. Endpoint bank, complete helper/target raw frame admission, global compiler, prime/field coverage, full-C/complex, price/invoice and all-size interfaces remain separate. No numerical kappa is certified.',artifacts={name:sha(P/name)for name in['retiming-selection.json','source-events.json.gz','scalar-events.json.gz','physical-source-map.json']})
 dump('RESULT.json',out);print(json.dumps(out,indent=2))
if __name__=='__main__':run()
