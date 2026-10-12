"""Whole-residual global replica-pool transport. One physical family per helper; no splitting.
Adapted operator/owner schema from PR442/448/450/453, Apache-2.0;
new stage-to-coordinate witness has explicit individual residual pieces.
"""
from pathlib import Path
from collections import Counter,defaultdict
import json,gzip,hashlib,sys,copy
sys.dont_write_bytecode=True
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def emit(parent,local,flow,out,variant=None):
 out.mkdir(parents=True,exist_ok=False)
 blob=gzip.decompress((parent/'GLOBAL-TEMPLATE.json.gz').read_bytes());t=json.loads(blob);g=read(parent/'GLOBAL.json');assert hashlib.sha256(blob).hexdigest()==g['template_sha256']
 w=read(flow);L,T,M,R=t['stages'],t['replicas'],t['m'],g['R'];V=120;K=(L-1)//2;FAM=2*K*V;DATA=FAM*T
 assert (L,T,M,R)==(11,8,78,740)
 st=read(local/'records/249-states.json')['initial'];fs=read(local/'records/frames.json')['frames'];width=[8-fs[str(st[str(h)])]['dim'] for h in range(240,240+R)]
 canon=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 def registry(gg,tt,init):return dict(word_sha256=gg['word_sha256'],source_records_sha256=gg['source_records_sha256'],entrance_rank_total=gg['entrance_rank_total'],helper_start_frames=[init[str(h)]for h in range(240,240+R)],residual_isometries_sha256=canon(tt['residual_isometries']),local_hashes={ori:d['sha256']for ori,d in gg['local_checks'].items()})
 providers={'base':registry(g,t,st)}
 widths={(ss,rep):width[:] for ss in range(L)for rep in range(T)};variant_calls=set(map(tuple,w.get('variant_calls',[])))
 if variant:
  vst=read(variant/'records/249-states.json')['initial'];vfs=read(variant/'records/frames.json')['frames'];vw=[8-vfs[str(vst[str(h)])]['dim'] for h in range(240,240+R)]
  for key in variant_calls:
   assert key in widths;widths[key]=vw[:]
  vt=json.loads(gzip.decompress((variant/'nine/GLOBAL-TEMPLATE.json.gz').read_bytes()));vg=read(variant/'nine/GLOBAL.json');providers['variant']=registry(vg,vt,vst);assert (vt['stages'],vt['replicas'],vt['m'])==(L,T,M)
  for ori,pg in vt['local_programs'].items():t['local_programs']['variant-'+ori]=pg
  for cc in t['calls']:
   if (cc['stage'],cc['replica'])in variant_calls:
    cc['local_hash']=vg['local_checks'][cc['orientation']]['sha256'];cc['orientation']='variant-'+cc['orientation']
 win={int(i):(p,r,set(ss))for i,(p,r,ss)in w['windows'].items()};counts={(i,ww,s):q for i,ww,s,q in w['stages']};assert len(counts)==len(w['stages'])
 for ss in range(L):
  for ww in {z for rr in widths.values() for z in rr}:
   assert sum(q for (i,w2,s2),q in counts.items()if w2==ww and s2==ss)==sum(widths[ss,rep].count(ww)for rep in range(T))
 pool=defaultdict(list)
 for ss in range(L):
  for rep in range(T):
   for hh in range(R):pool[ss,widths[ss,rep][hh]].append((rep,hh))
 cursor=Counter();pcs={};used=Counter();idx=0
 for e in t['schedule']:
  if e['kind']=='idle':e['idx']=idx;idx+=1
 slots=defaultdict(list)
 for i,(pair,r,ss)in sorted(win.items()):
  cp=0
  for ii,pat,nn in w['patterns']:
   if ii!=i:continue
   assert nn>0 and sum(pat)<=r
   for _ in range(nn):
    assert cp<240*T;hostrep,localcp=divmod(cp,240);fam=hostrep*FAM+(2*pair+localcp//V)*V+localcp%V;off=0
    for ww in pat:slots[i,ww].append((fam,off));off+=ww
    used[i,fam]=off;cp+=1
  assert cp==240*T
 for (i,ww,ss),nn in sorted(counts.items()):
  assert ss in win[i][2]
  for _ in range(nn):
   rep,hh=pool[ss,ww][cursor[ss,ww]];cursor[ss,ww]+=1
   fam,off=slots[i,ww].pop();assert(ss,rep,hh)not in pcs
   pcs[ss,rep,hh]=[[i,fam,off,ww]]
 assert not any(slots.values()) and all(cursor[k]==len(z)for k,z in pool.items()) and len(pcs)==L*T*R
 for c in t['calls']:
  s,rep=c['stage'],c['replica'];own=c['owners'][:240]
  for h in range(R):
   segs=pcs[s,rep,h];own.append([segs[0][1],['hosted-whole-pool',segs[0][0],segs[0][2],segs[0][3]]])
  c['owners']=own
 paid=Counter()
 for c in t['calls']:
  for z in t['local_programs'][c['orientation']]:
   if z[0]==0 and z[4]:paid[z[4]]+=1
   if z[0]==2:paid[z[5]]+=1
 rem={}
 for e in t['schedule']:
  if e['kind']!='idle' or not e['rank']:continue
  i,r=e['idx'],e['rank'];rr=Counter(r-used[i,rep*FAM+win[i][0]*240+cp]for rep in range(T)for cp in range(240))
  rem[str(i)]={str(k):v for k,v in sorted(rr.items())}
  for k,v in rr.items():
   if k:paid[k]+=v
 t.update(version='whole-residual-global-replica-pooling-v1',live=DATA,banks_per_stage={str(s):0 for s in range(L)},helper_route='one whole residual in one idle family, assigned globally across replicas; full physical coordinates and windows audited',hosting=dict(program_registry=providers,legacy_top_source_fields_describe='base provider only; choose provider by the exact per-call orientation',variant_calls=sorted([list(x)for x in variant_calls]),windows={str(i):[p,r,sorted(ss)]for i,(p,r,ss)in win.items()},pieces=[[s,rep,h,z]for (s,rep,h),z in sorted(pcs.items())],remainders=rem,banks_per_stage={str(s):0 for s in range(L)}))
 mass=sum(r*n for r,n in paid.items());assert M*DATA-mass==3264
 dg=hashlib.sha256();cnt=0
 for c in t['calls']:
  for z in t['local_programs'][c['orientation']]:
   mapped=[z[0],c['owners'][z[1]]]
   if z[0]==0:mapped.extend(z[2:])
   else:mapped.extend([c['owners'][z[2]]if z[2]<240+R else [DATA,['private',0]],*z[3:]])
   dg.update((json.dumps(mapped,separators=(',',':'))+'\n').encode());cnt+=1
 tb=json.dumps(t,sort_keys=True,separators=(',',':')).encode();(out/'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(tb,mtime=0))
 crossrep=sum(any(f//FAM!=rep for i,f,o,ww in segs)for (s,rep,h),segs in pcs.items());crosschild=sum(len({i for i,f,o,ww in segs})>1 for segs in pcs.values());maxpieces=max(map(len,pcs.values()))
 g.update(program_registry=providers,legacy_source_fields_describe='base provider only; selected provider bound by per-call local_hash and hosting.program_registry',status='PASS_WHOLE_RESIDUAL_GLOBAL_POOL_GENERATOR',live=DATA,physical=DATA+9,template_sha256=hashlib.sha256(tb).hexdigest(),parent_template_sha256=g['template_sha256'],profile=dict(sorted(paid.items())),paid_calls=sum(paid.values()),rank_mass=mass,maxchild=max(paid),banks_per_stage_hosted={str(s):0 for s in range(L)},hosted_residuals=L*T*R,hosted_residuals_per_replica=L*R,split_residuals=sum(len(x)>1 for x in pcs.values()),bank_assignments=0,hosted_coordinates=sum(map(sum,widths.values())),emitted_program_sha256=dg.hexdigest(),emitted_events=cnt,halving_depth=3,halving_integer_inequality=[M**3,2*max(paid)**3],deficit=3264,cross_replica_residuals=crossrep,cross_child_residuals=crosschild,max_owner_pieces=maxpieces,route_extra_required=2+maxpieces,flow_sha256=sha(flow),generator_sha256=sha(Path(__file__)))
 (out/'GLOBAL.json').write_text(json.dumps(g,indent=2)+'\n');print(json.dumps({k:g[k]for k in ['profile','cross_replica_residuals','cross_child_residuals','max_owner_pieces','route_extra_required']}),flush=True)
if __name__=='__main__':emit(*map(Path,sys.argv[1:]))

