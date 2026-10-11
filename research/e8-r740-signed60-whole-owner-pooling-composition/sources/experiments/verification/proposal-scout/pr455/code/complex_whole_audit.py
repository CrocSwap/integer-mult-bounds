"""Independent complete whole-residual complex routing audit (stdlib only)."""
from pathlib import Path
from collections import Counter
import gzip,hashlib,json,sys,copy
read=lambda p:json.loads(p.read_text())
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit(t,phase,source):
 V,R,T,K,L,H=120,560,8,5,11,9
 assert(t['m'],t['live'],t['physical'])==(89,9600,10178)
 assert t['selection_sha256']==source['selection_sha256']
 assert t['exact_data_phase_recipe_sha256']==source['phase_sha256']
 last={};locals_=[];win={};idle={}
 for pos,e in enumerate(t['execution_schedule']):
  if e['kind']=='local':last[e['pair']]=pos;locals_.append((pos,e['stage'],e['pair']))
  elif e['kind']=='bridge':last[e['dst']]=pos;last[e['src']]=pos
  elif e['kind']=='idle':
   pair=e['pair'];lo=last.get(pair,-1);st={s for q,s,p in locals_ if lo<q<pos and p!=pair};idle[e['idx']]=e
   if st and e['rank']:win[e['idx']]=(pair,e['rank'],st)
 localH={}
 for ori,es in t['local_programs'].items():
  assert hashlib.sha256(canon(es)).hexdigest()==source['local_checks'][ori]['sha256'];h=Counter()
  for z in es:
   if z[0]in('climb','center'):h[z[-1]]+=1
  assert dict(h)=={int(r):n for r,n in source['local_checks'][ori]['paid_profile'].items()};localH[ori]=h
 occ=set();used=Counter();seen=set();Hpaid=Counter();foreign=0;calls={};owner_count=0
 for call in t['calls']:
  s,rep,p=call['stage'],call['replica'],call['pair'];assert 0<=rep<T and(s,rep)not in calls;calls[s,rep]=call
  ori=call['orientation'];assert ori==('backward'if s%2 else'forward');assert p==(s+1)//2-1 if s else p==0
  assert call['local_program_sha256']==source['local_checks'][ori]['sha256'];Hpaid.update(localH[ori]);own=call['owners'];assert len(own)==800
  for j in range(2*V):assert own[j]==[rep*1200+(2*p+j//V)*V+j%V,[1,s,j%V]]
  for h,(f,route)in enumerate(own[240:]):
   assert len(route)==4 and route[0]==3;_,i,off,w=route;assert w==9 and i in win;pair,rr,st=win[i];assert s in st and pair!=p
   hr,within=divmod(f,1200);sideport=within-2*pair*V;assert 0<=hr<T and 0<=sideport<240
   side,port=divmod(sideport,V);assert 0<=off and off+w<=rr
   ch=idle[i]['phase_children'][side];axes=phase['recipes'][port]['idle_children'][ch]['orthogonal_axes'];assert len(axes)==rr
   for a in axes[off:off+w]:assert(f,a)not in occ;occ.add((f,a))
   used[i,hr,side,port]+=w;assert(s,rep,h)not in seen;seen.add((s,rep,h));foreign+=int(hr!=rep);owner_count+=1
 assert len(calls)==88 and len(seen)==49280 and len(occ)==49280*9
 idle_seen=set()
 for x in t['idle_children']:
  i,rep,side,port=x['idle'],x['replica'],x['side'],x['port'];key=(i,rep,side,port);assert key not in idle_seen;idle_seen.add(key)
  e=idle[i];ch=e['phase_children'][side];ph=phase['recipes'][port]['idle_children'][ch]
  assert x['phase_child']==ch and x['translation_after']==ph['translation_after'];assert x['rank']==e['rank']-used[key] and x['hosted']==used[key] and x['replicas']==1
  if x['rank']:Hpaid[x['rank']]+=1
 assert len(idle_seen)==len(idle)*T*240
 assert sum(r*n for r,n in Hpaid.items())==851136 and 89*9600-851136==3264
 assert t['cover_final_correction']['families']==[0,9600] and t['cover_final_correction']['charged_calls_per_cover']==9600
 assert t['execution_schedule'][-1]==t['cover_final_correction'] and t['terminal_translations']['pairs']==list(range(5))
 return dict(status='PASS_INDEPENDENT_WHOLE_COMPLEX_POOL',profile=dict(sorted(Hpaid.items())),rank_mass=851136,deficit=3264,live=9600,physical=10178,maxchild=max(Hpaid),calls=len(calls),whole_residuals=owner_count,foreign_replica_residuals=foreign,occupied_axis_cells=len(occ),split_residuals=0)
def main():
 out,src,selection=map(Path,sys.argv[1:]);p=out/'GLOBAL-TEMPLATE.json.gz';t=json.loads(gzip.decompress(p.read_bytes()));phase=read(out/'DATA-PHASES.json');source=dict(selection_sha256=sha(selection),phase_sha256=sha(out/'DATA-PHASES.json'),local_checks=read(src/'LOCAL-CHECKS.json'));got=audit(t,phase,source);mut={}
 def test(name,fn):
  w=copy.deepcopy(t);fn(w)
  try:audit(w,phase,source)
  except (AssertionError,KeyError,IndexError):mut[name]='REJECTED'
  else:raise AssertionError('vacuous mutation '+name)
 test('split helper rank',lambda w:w['calls'][0]['owners'][240][1].__setitem__(3,8))
 test('wrong stage',lambda w:w['calls'][0].__setitem__('stage',10))
 test('active data alias',lambda w:w['calls'][0]['owners'][240].__setitem__(0,w['calls'][0]['owners'][0][0]))
 test('duplicate helper slot',lambda w:w['calls'][0]['owners'].__setitem__(241,copy.deepcopy(w['calls'][0]['owners'][240])))
 test('omitted owner',lambda w:w['calls'][0]['owners'].pop())
 test('outside child',lambda w:w['calls'][0]['owners'][240][1].__setitem__(2,100))
 test('forged idle remainder',lambda w:w['idle_children'][0].__setitem__('rank',1+w['idle_children'][0]['rank']))
 test('omitted idle child',lambda w:w['idle_children'].pop())
 test('missing cover correction',lambda w:w['execution_schedule'].pop())
 test('corrupted literal program',lambda w:w['local_programs']['forward'].pop())
 global_=read(out/'GLOBAL.json');assert got['profile']=={int(r):n for r,n in global_['profile'].items()};got.update(template_sha256=hashlib.sha256(canon(t)).hexdigest(),mutations_rejected=mut,source_bindings=source);assert got['template_sha256']==global_['template_sha256'];(out/'AUDIT.json').write_text(json.dumps(got,indent=2)+'\n');print(json.dumps(got))
if __name__=='__main__':main()
