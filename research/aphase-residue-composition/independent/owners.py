# SPDX-License-Identifier: Apache-2.0
"""Independent integer-time and mask check of the actual parameterized-replica owner allocation with PR2853 dirt-entry providers.

Chronology/mask method derives from Tekalign's PR2751 independent_owners.py;
Marius-Paul Dumitrean's PR2802 retired7 native construction and the retained
provider frame checker keep their
upstream attribution. No solver, producer, emitter or floating arithmetic is
imported. This checks finite geometry, not global native/outer admission.
"""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,hashlib,gzip,json,sys,types
sys.dont_write_bytecode=True
def need(v,msg):
 if not v:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 b=Path(p).read_bytes();return json.loads(gzip.decompress(b)if str(p).endswith('.gz')else b)
def inputs(PROVIDER):
 provider_pins={'PLAN.json': '5132aa4aba25c98f5b78936c4281c89dad6912696f93e390cb296f94811f28b1', 'GLOBAL-TEMPLATE.json.gz': '1d31424c4e27e26a35a9932ca778e43f1f3577589275422cc642aa68b31112db', 'PROVIDERS.json': 'd4b8c2ecd493a35b99c6c97cd2dfc4131859cce21e98527f45d9fd183c650f7b', 'WORD-base.json.gz': '7f0a0715aa962f24c112ca32d1b57fc275eff0f15eac6eccd684ba702af82f8b', 'WORD-extra.json.gz': 'c94a0ac238ca72951e4580895334d39f66ea950fa7af62ca2667251a2f796d6e', 'independent_local.py': 'ee1faab70095fa312fc61d375ddf015b76104cb1a542ae7876a149e7999faa20'}
 hashes={}
 for n,pin in provider_pins.items():
  p=PROVIDER/n;need(sha(p)==pin,'pinned PR2853 provider source '+n);hashes[str(p)]=pin
 L=types.ModuleType('retained_independent_frames');exec(compile((PROVIDER/'independent_local.py').read_bytes(),'unchanged_PR2827_independent_local.py','exec'),L.__dict__);providers=read(PROVIDER/'PROVIDERS.json')
 for tag,pid in [('base','gauge44'),('extra','extra')]:
  word=read(PROVIDER/f'WORD-{tag}.json.gz');report,start,ends=L.check_frames(word);L.check_cleanup(word);L.algebra(word)
  widths=[L.dm(ends[k])-L.dm(start[k])for k in sorted(start)if k>=224]
  need(widths==providers[pid]['widths']and len(widths)==408,'actual ordered provider frame widths');need(len(word['centers'])==8,'eight centres');providers[pid]['actual_paid_profile']={int(k):v for k,v in report['profile'].items()}
 return read(PROVIDER/'PLAN.json'),read(PROVIDER/'GLOBAL-TEMPLATE.json.gz'),providers,hashes

def windows(template,order,T):
 ranks={c['child']:c['rank']for c in template['idle_children']};pairs={e['stage']:e['pair']for e in template['recipe']if e['kind']=='local'}
 blocks={};stage=None
 for event in template['execution_schedule']:
  if event['kind']in('bank_padding_cover_sweep','translate_every_live_family'):continue
  if event['kind']=='local_cover_sweep':stage=event['stage'];blocks[stage]=[]
  need(stage is not None,'source event before local call');blocks[stage].append(event)
 need(set(blocks)==set(range(9)),'nine source stages')
 progress=[0]*T;last={};result={}
 for t,(stage,replica)in enumerate(order):
  need(0<=replica<T and stage==progress[replica],'order chronology');progress[replica]+=1
  for j,event in enumerate(blocks[stage]):
   kind=event['kind']
   if kind=='local_cover_sweep':need(j==0,'local first position');last[replica,pairs[stage]]=t
   elif kind=='bridge':last[replica,event['src']]=last[replica,event['dst']]=t
   elif kind=='idle_cover_sweep':
    need(j>0,'idle source position');start=last.get((replica,event['pair']),-1)
    for child in event['child_indices']:
     if child in ranks:result[replica,child]=(ranks[child],start,t)
   elif kind in ('terminal_Y_translations','terminal'):pass  # inherited terminal phase; no pending-window endpoints
   else:raise ValueError('unknown source event kind')
 need(progress==[9]*T,'complete replica source progression');return result

def check(T,order,fill,dispatch,claimed,plan,template,providers):
 need(type(T)is int and T>0,'positive T');N=9*T
 need(len(order)==N and set(map(tuple,order))=={(s,r)for s in range(9)for r in range(T)},'complete T call coverage')
 win=windows(template,order,T)
 need(set(dispatch)==set(map(tuple,order))and all(p in providers for p in dispatch.values()),'provider dispatch coverage')
 for s,r,pid in fill.get('dispatch_overrides',[]):need(dispatch.get((s,r))==pid,'final dispatch override binding')
 need(fill['columns']==['time','helper','owner_replica','child','port','offset'],'literal role columns')
 need(len(fill['rows'])==N*408,'complete role count');helpers=[0]*N;families=[0]*N;occupied={};lastrow={}
 for idx,row in enumerate(fill['rows']):
  need(len(row)==6 and all(type(x)is int for x in row),'integer role shape');t,h,o,c,p,z=row
  need(0<=t<N and 0<=h<408 and 0<=p<112 and(o,c)in win,'role bounds')
  cap,lo,hi=win[o,c];need(lo<t<=hi,'literal source window');hb=1<<h;need(not helpers[t]&hb,'duplicate helper');helpers[t]|=hb
  family=o*896+(2*plan['pairs'][str(c)]+plan['sides'][str(c)])*112+p;fb=1<<family
  need(not families[t]&fb,'same-call family collision');families[t]|=fb
  w=providers[dispatch[tuple(order[t])]]['widths'][h];need(0<=z and z+w<=cap,'bin capacity')
  key=(o,c,p);mask=((1<<w)-1)<<z;need(not occupied.get(key,0)&mask,'bin overlap');occupied[key]=occupied.get(key,0)|mask
  if key not in lastrow or z>lastrow[key][0]:lastrow[key]=(z,idx,w)
 need(helpers==[(1<<408)-1]*N,'all helper identities');idle=Counter()
 for(o,c),(cap,_,_)in win.items():
  for p in range(112):
   key=(o,c,p);mask=occupied.get(key,0);used=mask.bit_count();need(mask==(1<<used)-1,'compact bin prefix')
   if used<cap:idle[cap-used]+=1
 profile=Counter(idle)
 for call in order:profile.update(providers[dispatch[tuple(call)]]['actual_paid_profile'])
 if claimed is not None:need(profile==Counter({int(k):v for k,v in claimed.items()}),'complete claimed profile')
 mass=sum(r*n for r,n in profile.items());need(mass==65088*T,'complete rank-mass identity')
 return dict(replicas=T,calls=N,roles=N*408,live=896*T,physical=896*T+490,rank_mass=mass,idle=dict(sorted(idle.items())),profile=dict(sorted(profile.items()))),win,lastrow

def write_receipt(out,result):
 out.parent.mkdir(parents=True,exist_ok=True);lock=out.with_name(out.name+'.lock');handle=lock.open('x')
 try:
  with out.open('x',encoding='utf8',newline='\n')as target:target.write(json.dumps(result,sort_keys=True,indent=2)+chr(10))
 finally:handle.close();lock.unlink()

def main():
 need(__debug__,'assertions required for retained provider frame checker')
 ap=argparse.ArgumentParser();ap.add_argument('--provider-root',type=Path,default=Path(__file__).resolve().parent/'provider');ap.add_argument('--replicas',type=int,required=True);ap.add_argument('--order',type=Path,required=True);ap.add_argument('--fill',type=Path,required=True);ap.add_argument('--dispatch',type=Path,required=True);ap.add_argument('--profile',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();need(not a.out.exists(),'fresh verification output')
 plan,template,providers,pins=inputs(a.provider_root);files=[a.order,a.fill,a.dispatch]+([a.profile]if a.profile else[]);before={str(p.resolve()):sha(p)for p in files};order=read(a.order);fill=read(a.fill);rawdispatch=read(a.dispatch);need(len(rawdispatch)==9*a.replicas and all(len(row)==3 and type(row[0])is int and type(row[1])is int and type(row[2])is str for row in rawdispatch),'literal dispatch shape and count');dispatch={(s,r):p for s,r,p in rawdispatch};need(len(dispatch)==len(rawdispatch),'unique literal dispatch calls');claimed=read(a.profile)if a.profile else None
 result,win,lastrow=check(a.replicas,order,fill,dispatch,claimed,plan,template,providers);rejected=[]
 def reject(name,fn,reason):
  try:fn()
  except ValueError as e:need(str(e)==reason,'wrong rejection reason '+name+': '+str(e));rejected.append(dict(name=name,reason=reason))
  else:raise ValueError('accepted corruption '+name)
 def rerun(T=a.replicas,f=fill,d=dispatch,p=providers,c=claimed):return check(T,order,f,d,c,plan,template,p)
 reject('false_replica_count',lambda:rerun(T=a.replicas+1),'complete T call coverage')
 reject('missing_literal_helper_role',lambda:rerun(f={**fill,'rows':fill['rows'][:-1]}),'complete role count')
 bad=dict(dispatch);bad[tuple(order[0])]='unknown-provider';reject('unbound_provider_at_actual_call',lambda:rerun(d=bad),'provider dispatch coverage')
 def mutate(i,new):rows=list(fill['rows']);rows[i]=new;return{**fill,'rows':rows}
 row=fill['rows'][0];t,h,o,c,p,z=row;owner,child=next(k for k,(cap,lo,hi)in win.items()if not lo<t<=hi)
 reject('unavailable_source_window',lambda:rerun(f=mutate(0,[t,h,owner,child,p,z])),'literal source window')
 j=next(i for i,r in enumerate(fill['rows'][1:],1)if r[0]==t);r=fill['rows'][j];reject('same_call_physical_family_collision',lambda:rerun(f=mutate(j,[r[0],r[1],o,c,p,r[5]])),'same-call family collision')
 key,(z,i,w)=next((k,v)for k,v in lastrow.items()if v[0]+v[2]<win[k[:2]][0]);r=list(fill['rows'][i]);r[5]+=1
 reject('unpaid_hole_in_compact_pending_prefix',lambda:rerun(f=mutate(i,r)),'compact bin prefix')
 wrong=dict(result['profile']);wrong[1]=wrong.get(1,0)+1;reject('changed_total_paid_profile',lambda:rerun(c=wrong),'complete claimed profile')
 need({str(p.resolve()):sha(p)for p in files}==before,'candidate input drift');need(all(sha(Path(p))==h for p,h in pins.items()),'baseline input drift')
 result.update(status='PASS_INDEPENDENT_T_OWNER_CHRONOLOGY_MASKS',controls=rejected,candidate_sha256={label:sha(path)for label,path in [('ORDER',a.order),('FILL',a.fill),('DISPATCH',a.dispatch)]+([('PROFILE',a.profile)]if a.profile else[])},provider_source_sha256={Path(path).relative_to(a.provider_root).as_posix():digest for path,digest in pins.items()},scope='PR2853 headd01045dfb67428679618027dff552f1d032fa999, with unchanged PR2827 independent local algorithm; finite literal whole-owner geometry, scalar endpoints and paid profile only; full native/global/outer admission remains separate.')
 write_receipt(a.out,result);print(json.dumps({k:result[k]for k in['status','replicas','roles','live','physical','profile']}),flush=True)
if __name__=='__main__':main()
