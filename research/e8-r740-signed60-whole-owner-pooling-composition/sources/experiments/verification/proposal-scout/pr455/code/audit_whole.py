"""Independent audit for whole residuals pooled across replicas. No cross-family splitting.
No generator/flow imports. Source-bound standard-library verification.
"""
from pathlib import Path
from collections import Counter,defaultdict
import json,gzip,hashlib,copy,sys
sys.dont_write_bytecode=True
read=lambda p:json.loads(Path(p).read_text())
def load(p):return json.loads(gzip.decompress(Path(p).read_bytes()))
def audit(t,b,widths):
 L,T,M=t['stages'],t['replicas'],t['m'];R=len(widths[0,0]);K=(L-1)//2;F=240*K;DATA=F*T
 assert (L,T,M,R)==(11,8,78,740) and t['live']==DATA
 mutable={'_expected_registry','version','live','banks_per_stage','hosting','helper_route','calls','schedule'}
 assert set(t)==(set(b)-{'_expected_registry'})|{'hosting'}
 assert {k:v for k,v in t.items()if k not in mutable}=={k:v for k,v in b.items()if k not in mutable}
 schedule=copy.deepcopy(b['schedule']);j=0
 for e in schedule:
  if e['kind']=='idle':e['idx']=j;j+=1
 assert t['schedule']==schedule
 last={};local=[];win={};rank={};pair={};lo={};stagepair={}
 for pos,e in enumerate(schedule):
  if e['kind']=='local_cover_sweep':local.append((pos,e['stage'],e['pair']));last[e['pair']]=pos;stagepair[e['stage']]=e['pair']
  elif e['kind']=='bridge':last[e['dst']]=pos;last[e['src']]=pos
  elif e['kind']=='idle':
   i=e['idx'];win[i]={s for q,s,p in local if last.get(e['pair'],-1)<q<pos and p!=e['pair']};rank[i]=e['rank'];pair[i]=e['pair'];lo[i]=8+7*e['source_level'];assert lo[i]+rank[i]==8+7*e['target_level']
  else:assert e['kind']=='exchange' and pos==len(schedule)-1
 hs=t['hosting'];assert hs['program_registry']==b['_expected_registry'];expected_variants={(c['stage'],c['replica'])for c in b['calls']if c['orientation'].startswith('variant-')};assert set(map(tuple,hs.get('variant_calls',[])))==expected_variants
 assert hs['windows']=={str(i):[pair[i],rank[i],sorted(win[i])]for i in win if rank[i]>0 and win[i]}
 assert hs['banks_per_stage']=={str(s):0 for s in range(L)} and t['banks_per_stage']==hs['banks_per_stage']
 # Every physical coordinate is accounted globally, including distinct idle children.
 occupied={};owned={};used=Counter();crossrep=0;crosschild=0;maxpieces=0
 for s,rep,h,segs in hs['pieces']:
  assert 0<=s<L and 0<=rep<T and 0<=h<R and (s,rep,h)not in owned
  assert len(segs)==1 and sum(z[3]for z in segs)==widths[s,rep][h]
  for i,f,o,w in segs:
   assert i in rank and s in win[i] and pair[i]!=stagepair[s]
   assert 0<=f<DATA and 0<=o and w>0 and o+w<=rank[i]
   hostrep,rel=divmod(f,F);pp,port=divmod(rel,120);assert pp//2==pair[i]
   for a in range(lo[i]+o,lo[i]+o+w):
    assert 0<=a<M and (f,a)not in occupied,('physical alias',f,a)
    occupied[f,a]=(s,rep,h,i)
   used[i,f]+=w
  owned[s,rep,h]=segs;maxpieces=max(maxpieces,len(segs));crossrep+=any(f//F!=rep for i,f,o,w in segs);crosschild+=len({z[0]for z in segs})>1
 assert set(owned)=={(s,rep,h)for s in range(L)for rep in range(T)for h in range(R)}
 summaries={};paid=Counter();remainder=Counter()
 for i,r in rank.items():
  if not r:continue
  cc=Counter()
  for rep in range(T):
   for cp in range(240):
    f=rep*F+pair[i]*240+cp;q=r-used[i,f];assert q>=0;cc[q]+=1
    if q:paid[q]+=1;remainder[q]+=1
  summaries[str(i)]={str(k):v for k,v in sorted(cc.items())}
 assert hs['remainders']==summaries
 assert len(t['calls'])==len(b['calls'])==L*T
 seen=set();dg=hashlib.sha256();events=0
 for c,bc in zip(t['calls'],b['calls']):
  assert {k:v for k,v in c.items()if k!='owners'}=={k:v for k,v in bc.items()if k!='owners'}
  s,rep=c['stage'],c['replica'];assert(s,rep)not in seen;seen.add((s,rep))
  assert len(c['owners'])==240+R and c['owners'][:240]==bc['owners'][:240]
  for h,o in enumerate(c['owners'][240:]):
   z=owned[s,rep,h];assert o==[z[0][1],['hosted-whole-pool',z[0][0],z[0][2],z[0][3]]]
  for z in t['local_programs'][c['orientation']]:
   if z[0]==0 and z[4]:paid[z[4]]+=1
   if z[0]==2:paid[z[5]]+=1
   x=[z[0],c['owners'][z[1]]]
   if z[0]==0:x.extend(z[2:])
   else:x.extend([c['owners'][z[2]]if z[2]<240+R else[DATA,['private',0]],*z[3:]])
   dg.update(json.dumps(x,separators=(',',':')).encode()+b'\n');events+=1
 assert M*DATA-sum(r*n for r,n in paid.items())==3264 and M**3>2*max(paid)**3
 return dict(profile={str(r):n for r,n in sorted(paid.items())},live=DATA,physical=DATA+9,hosted_residuals=len(owned),bank_assignments=0,split_residuals=sum(len(z)>1 for z in owned.values()),rank_mass=sum(r*n for r,n in paid.items()),deficit=3264,maxchild=max(paid),paid_calls=sum(paid.values()),cross_replica_residuals=crossrep,cross_child_residuals=crosschild,max_owner_pieces=maxpieces,physical_coordinates_checked=len(occupied),emitted_events=events,emitted_program_sha256=dg.hexdigest(),remainder_profile=dict(remainder))
def scalar_dispatch(t):
 L,T,R,V=11,8,740,120;K=5;n=2*K*V+L*R;loc=2*V+R;calls={(c['stage'],c['replica']):c for c in t['calls']};checked=0
 for rep in range(T):
  vals=[1<<i for i in range(n)]+[0]
  for e in t['schedule']:
   if e['kind']=='local_cover_sweep':
    ss,p=e['stage'],e['pair'];cc=calls[ss,rep];rev=cc['orientation'].endswith('reverse');assert rev==bool(e['reverse']);before=vals[:];opened=False
    def mapper(i):
     if i==loc:return n
     if i<2*V:
      side=i//V;side=1-side if rev else side;return(2*p+side)*V+i%V
     return 2*K*V+ss*R+i-2*V
    for z in t['local_programs'][cc['orientation']]:
     if z[0]==0:continue
     x,y=mapper(z[1]),mapper(z[2])
     if z[0]==1:
      if z[3]&1:vals[x]^=vals[y]
     elif z[0]==2:assert not opened;vals[n]=vals[x];opened=True
     else:assert z[0]==3 and opened and vals[n]==vals[x];vals[n]=0;opened=False
    assert not opened
    d=(2*p+(0 if rev else 1))*V;src=(2*p+(1 if rev else 0))*V
    for j in range(V):before[d+j]^=before[src+j]
    assert vals==before,('mixed local endpoint',ss,rep)
   elif e['kind']=='bridge':
    d,src=e['dst'],e['src']
    for j in range(V):vals[2*d*V+j]^=vals[2*src*V+j];vals[(2*src+1)*V+j]^=vals[(2*d+1)*V+j]
   elif e['kind']=='exchange':
    for j in range(K):
     for port in range(V):x,y=2*j*V+port,(2*j+1)*V+port;vals[x],vals[y]=vals[y],vals[x]
  assert vals==[1<<i for i in range(n)]+[0],rep
  checked+=n
 return dict(replicas=T,columns_per_replica=n,total_columns=checked,local_invocations=L*T,all_helper_columns_restored=True,private_work_erased=True)

def main(base,changed,out,variant=None):
 b=load(base/'nine/GLOBAL-TEMPLATE.json.gz');t=load(changed/'GLOBAL-TEMPLATE.json.gz');g=read(changed/'GLOBAL.json');bg=read(base/'nine/GLOBAL.json');st=read(base/'records/249-states.json')['initial'];fs=read(base/'records/frames.json')['frames'];widths=[8-fs[str(st[str(h)])]['dim']for h in range(240,980)]
 canon=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 def registry(gg,tt,init):return dict(word_sha256=gg['word_sha256'],source_records_sha256=gg['source_records_sha256'],entrance_rank_total=gg['entrance_rank_total'],helper_start_frames=[init[str(h)]for h in range(240,980)],residual_isometries_sha256=canon(tt['residual_isometries']),local_hashes={ori:d['sha256']for ori,d in gg['local_checks'].items()})
 b['_expected_registry']={'base':registry(bg,b,st)}
 widths={(ss,rep):widths[:] for ss in range(11)for rep in range(8)};variant_calls=set(map(tuple,t['hosting'].get('variant_calls',[])))
 assert len(variant_calls)==len(t['hosting'].get('variant_calls',[])) and (variant is not None or not variant_calls)
 if variant:
  st2=read(variant/'records/249-states.json')['initial'];fs2=read(variant/'records/frames.json')['frames'];vw=[8-fs2[str(st2[str(h)])]['dim']for h in range(240,980)]
  for key in variant_calls:
   assert key in widths;widths[key]=vw[:]
  vb=load(variant/'nine/GLOBAL-TEMPLATE.json.gz');vg=read(variant/'nine/GLOBAL.json');b['_expected_registry']['variant']=registry(vg,vb,st2)
  assert (vb['stages'],vb['replicas'],vb['m'])==(b['stages'],b['replicas'],b['m'])
  for ori,prog in vb['local_programs'].items():b['local_programs']['variant-'+ori]=prog
  for c in b['calls']:
   if (c['stage'],c['replica'])in variant_calls:
    c['local_hash']=vg['local_checks'][c['orientation']]['sha256'];c['orientation']='variant-'+c['orientation']
 r=audit(t,b,widths);assert all(r[k]==g[k]for k in r if k in g)
 assert g['template_sha256']==hashlib.sha256(gzip.decompress((changed/'GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest() and g['parent_template_sha256']==bg['template_sha256']
 assert g['route_extra_required']>=2+r['max_owner_pieces']
 controls=[]
 def reject(name,fn):
  q=copy.deepcopy(t);fn(q)
  try:audit(q,b,widths)
  except(AssertionError,KeyError,IndexError,TypeError):controls.append(name)
  else:raise AssertionError('mutation accepted '+name)
 pcs=lambda q:q['hosting']['pieces'];p0=lambda q:pcs(q)[0];z0=lambda q:p0(q)[3][0]
 reject('omitted residual',lambda q:pcs(q).pop())
 reject('duplicate residual',lambda q:pcs(q).append(copy.deepcopy(p0(q))))
 reject('width changed',lambda q:z0(q).__setitem__(3,z0(q)[3]+1))
 reject('negative offset',lambda q:z0(q).__setitem__(2,-1))
 reject('out of stock family',lambda q:z0(q).__setitem__(1,9600))
 reject('changed child',lambda q:z0(q).__setitem__(0,999))
 reject('unaccounted foreign replica',lambda q:q['calls'][0]['owners'][240].__setitem__(0,9600))
 reject('omitted remainder',lambda q:q['hosting']['remainders'].pop(next(iter(q['hosting']['remainders']))))
 reject('stale stage count',lambda q:q.__setitem__('stages',9))
 reject('understated live stock',lambda q:q.__setitem__('live',9599))
 reject('changed parent scalar',lambda q:q['local_programs']['forward'][0].__setitem__(0,999))
 reject('wrong local source hash',lambda q:q['calls'][0].__setitem__('local_hash','0'*64))
 reject('wrong provider source hash',lambda q:q['hosting']['program_registry']['base'].__setitem__('word_sha256','0'*64))
 reject('wrong call orientation',lambda q:q['calls'][0].__setitem__('orientation','reverse'))
 if variant_calls:
  reject('wrong variant dispatch',lambda q:q['calls'][0].__setitem__('orientation','variant-forward'))
  reject('extra variant dispatch record',lambda q:q['hosting']['variant_calls'].append([0,0]))
 def outside(q):
  p=p0(q);i=p[3][0][0];ss=set(q['hosting']['windows'][str(i)][2]);p[0]=next(s for s in range(11)if s not in ss)
 reject('outside idle window',outside)
 def alias(q):
  ps=pcs(q);a=ps[0];b=next(p for p in ps[1:]if p[0]==a[0]and p[3][0][3]==a[3][0][3]);b[3][0]=copy.deepcopy(a[3][0])
 reject('cross-residual physical alias',alias)
 def split(q):
  z=z0(q);ww=z[3];assert ww>1;z[3]=1;p0(q)[3].append([z[0],z[1]+1,0,ww-1])
 reject('forbidden cross-family residual split',split)
 r['fresh_mixed_unbanked_scalar_replay']=scalar_dispatch(t)
 r.update(status='PASS_INDEPENDENT_WHOLE_RESIDUAL_GLOBAL_POOL',template_sha256=g['template_sha256'],mutations_rejected=controls,route_extra_required=2+r['max_owner_pieces'],operator_identity='Each helper remains in one physical family. Same-family coordinate factorization and unchanged idle-window commutation; no family-space factorization.',scope='Finite changed owner, physical-coordinate, chronological-window, instruction and profile audit. Inherits dirty invocation and all-size compiler interfaces. No Lean certificate.')
 out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
if __name__=='__main__':main(*map(Path,sys.argv[1:]))
