if not __debug__:
 raise RuntimeError('Assertions are required; run without optimized Python.')
"""Independent literal allocation and rational moment check, no optimizer imports.
Apache-2.0; PR2696/2679/2673/2588/2530 and retained schedule/native authors credited.
Independent AI-assisted audit; no human review is claimed.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
from functools import lru_cache
import argparse,json,gzip,time,hashlib,sys
sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent
read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def span(xs):
 out={0}
 for x in xs:out|={a^x for a in list(out)}
 return frozenset(out)
def dim(s):return len(s).bit_length()-1
FULL=span(1<<i for i in range(9))
def word_invoice(w):
 current=[span([x])for x in w['ports']]+[span([])]*592
 for r,f in w['start_extra'].items():current[int(r)]=span(f)
 starts=list(current);paid=Counter();end=[FULL]*112+[span(x for x in range(512)if(x&p).bit_count()%2==0)for p in w['ports']]+[FULL]*480
 for r,f in w['helper_final'].items():end[int(r)]=span(f)
 def climb(r,f):
  f=span(f);assert current[r]<=f,('nonnested',r);n=dim(f)-dim(current[r]);paid.update({n:1}if n else{});current[r]=f
 def gate(g):
  if g[0]=='warp':assert current[g[1]]==span(g[-2]);current[g[1]]=span(g[-1])
  else:
   for r in g[1:3]if g[0]=='add'else g[1:2]:climb(r,g[-1])
 for g in w['A']:gate(g)
 levels={int(k):span(v)for k,v in w['target_levels'].items()};assert all(current[112+t]==levels.get(t,span([]))for t in range(112))
 for r,f in zip(w['centers'],w['center_frames']):
  f=span(f);assert current[r]==f;targets={levels.get(g[1]-112,span([]))for g in w['cut']if g[2]==r}
  for dest in sorted(targets,key=lambda s:-len(s)):
   assert dest<=f;n=dim(f)-dim(dest);paid.update({n:1}if n else{});f=dest
 warps=defaultdict(list)
 for pos,r,G,U,V in w['warps']:warps[pos].append((r,G,U,V))
 for i in range(len(w['B'])+1):
  for r,G,U,V in warps[i]:
   assert current[r]==span(U);mapped=lambda x:__import__('functools').reduce(int.__xor__,[G[j]for j in range(9)if x>>j&1],0);assert len(span(G))==512;assert frozenset(map(mapped,current[r]))==span(V);current[r]=span(V)
  if i<len(w['B']):gate(w['B'][i])
 for g in w['restore']:gate(g)
 live=[r for r in range(704)if r not in w['removed']]
 for r in live:climb(r,list(end[r]))
 widths=[dim(end[r])-dim(starts[r])for r in live if r>=224];assert dict(paid)=={int(k):v for k,v in w['report']['local_profile'].items()}
 buffers=set()
 for g in w['cleanup']:
  for r in g[1:3]if g[0]=='add'else g[1:2]:
   if r>=704:buffers.add(r-704)
 assert buffers and all(x>=0 for x in buffers)
 return widths,paid,buffers
@lru_cache(None)
def log_interval(x):
 x=Q(x);k=0
 while x>2:x/=2;k+=1
 def unit(y):
  z=(y-1)/(y+1);v=z;lo=Q(0)
  for n in range(32):lo+=2*v/(2*n+1);v*=z*z
  return lo,lo+2*v/(65*(1-z*z))
 l,u=unit(x);a,b=unit(Q(2));return l+k*a,u+k*b
@lru_cache(None)
def exp_interval(x):
 assert 0<=x<Q(1,10)
 t=s=Q(1)
 for j in range(1,24):t=t*x/j;s+=t
 nxt=t*x/24;return s,s+2*nxt
@lru_cache(None)
def cost(r,a):
 l,u=log_interval(Q(73,r));return Q(r,73)*exp_interval(a*l)[0],Q(r,73)*exp_interval(a*u)[1]
def moment(H,a,conservative=False):
 lo=sum(n*cost(r,a)[0]for r,n in H.items())/66304;hi=sum(n*cost(r,a)[1]for r,n in H.items())/66304
 if conservative:
  l,u=log_interval(Q(73));v=Q(32*73*sum(H.values()),10**16*66304);lo+=v*exp_interval(a*l)[0];hi+=v*exp_interval(a*u)[1]
 den=1<<256;return Q((lo.numerator*den)//lo.denominator,den),Q(-((-hi.numerator*den)//hi.denominator),den)

def main():
 p=argparse.ArgumentParser();p.add_argument('--fill',type=Path,required=True);p.add_argument('--order',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--context',type=Path,default=HERE/'independent-inputs');p.add_argument('--profile',type=Path);p.add_argument('--endpoint',default='0.001715599770234969498858');a=p.parse_args();a.out=a.work.resolve();context=a.context.resolve();assert not a.out.is_relative_to(HERE.resolve()),'Externaloutputrequired';a.out.mkdir(exist_ok=False,parents=True);start=time.process_time();manifestpath=context/'MANIFEST.json';manifest=read(manifestpath);required={'GLOBAL-TEMPLATE.json.gz','PLAN.json','base.json.gz','extra.json.gz','DISPATCH.json','BASELINE-PROFILE.json','PROVIDERS.json'};assert required<=set(manifest)
 def context_snapshot():
  for name,h in manifest.items():
   assert Path(name).name==name and hashlib.sha256((context/name).read_bytes()).hexdigest()==h,('Contextpin',name)
 context_snapshot();parentpath=context/'GLOBAL-TEMPLATE.json.gz';planpath=context/'PLAN.json';parent=read(parentpath);plan=read(planpath);order=read(a.order);assert len(order)==666 and set(map(tuple,order))=={(s,r)for s in range(9)for r in range(74)}
 blocks={};stage=None;globals_=[]
 for i,event in enumerate(parent['execution_schedule']):
  if event['kind']in ['bank_padding_cover_sweep','translate_every_live_family']:globals_.append(i);continue
  if event['kind']=='local_cover_sweep':stage=event['stage'];blocks[stage]=[]
  assert stage is not None;blocks[stage].append((i,event))
 assert globals_==[30,31];rank={c['child']:c['rank']for c in parent['idle_children']};pairs={e['stage']:e['pair']for e in parent['recipe']if e['kind']=='local'};touch={};intervals={};callpos={};project=defaultdict(list);pos=0
 for t,(s,r)in enumerate(order):
  for original,e in blocks[s]:
   project[r].append(original)
   if e['kind']=='local_cover_sweep':touch[r,pairs[s]]=pos;callpos[t]=pos
   elif e['kind']=='bridge':touch[r,e['src']]=touch[r,e['dst']]=pos
   elif e['kind']=='idle_cover_sweep':
    for c in e['child_indices']:
     if c in rank:intervals[r,c]=(touch.get((r,e['pair']),-1),pos)
   pos+=1
 assert all(x==list(range(30))for x in project.values())and len(project)==74
 providers={};paid={};buffers={};wordpaths=[]
 for label,name in [('gauge44','base'),('extra','extra')]:
  path=context/f'{name}.json.gz';wordpaths.append(path);providers[label],paid[label],buffers[label]=word_invoice(read(path))
 registry=read(context/'PROVIDERS.json');assert set(registry)==set(providers)
 for pid in providers:assert providers[pid]==registry[pid]['widths']
 helper_counts={len(x)for x in providers.values()};assert len(helper_counts)==1;helper_count=helper_counts.pop();assert helper_count==len(set(range(224,704))-set(read(context/'base.json.gz')['removed']));assert buffers['gauge44']==buffers['extra'];private_count=len(buffers['extra'])
 fill=read(a.fill);rows=fill['rows'];dispatch={(s,r):p for s,r,p in read(context/'DISPATCH.json')}
 for s,r,pid in fill['dispatch_overrides']:dispatch[s,r]=pid
 assert set(dispatch)==set(map(tuple,order))
 seenh=defaultdict(set);seenf=defaultdict(set);masks={};violations=[]
 def validate(row,mutating=False):
  assert len(row)==6 and all(type(x)is int for x in row);t,h,r,c,port,off=row;assert 0<=t<666 and 0<=h<helper_count and 0<=r<74 and c in rank and 0<=port<112;stage,replica=order[t];width=providers[dispatch[stage,replica]][h];lo,hi=intervals[r,c];assert lo<callpos[t]<hi,('strictwindow',row);pair,side=plan['pairs'][str(c)],plan['sides'][str(c)];family=r*896+(2*pair+side)*112+port;assert 0<=family<66304;assert not(r==replica and pair==pairs[stage]),('activefamily',row);assert off>=0 and off+width<=rank[c];assert h not in seenh[t]and family not in seenf[t];key=(r,c,port);mask=((1<<width)-1)<<off;assert not(mask&masks.get(key,0));seenh[t].add(h);seenf[t].add(family);masks[key]=masks.get(key,0)|mask
 for row in rows:validate(row)
 assert len(rows)==len(order)*helper_count;assert len(seenh)==666 and all(x==set(range(helper_count))for x in seenh.values());idle=Counter()
 for r,c in intervals:
  for port in range(112):
   mask=masks.get((r,c,port),0);used=mask.bit_count();assert mask==(1<<used)-1
   if rank[c]>used:idle[rank[c]-used]+=1
 H=Counter(idle)
 for s,r in order:H.update(paid[dispatch[s,r]])
 assert sum(k*v for k,v in H.items())==4816512;assert a.profile is None or dict(H)=={int(k):v for k,v in read(a.profile).items()};assert 74*896==66304 and 66304+helper_count+8+private_count+2==sum([66304,helper_count,8,private_count,2])
 # Meaningful early-rejection controls exercise completeness/window/alias/capacity explicitly.
 assert len(rows[:-1])!=len(order)*helper_count
 first=rows[0];t,h,r,c,port,off=first;bad_owner,bad_child=next((rr,cc)for (rr,cc),(lo,hi)in intervals.items()if not(lo<callpos[t]<hi));badrow=list(first);badrow[2:4]=[bad_owner,bad_child]
 try:validate(badrow)
 except AssertionError as exc:assert exc.args[0][0]=='strictwindow'
 else:raise AssertionError('Invalidwindowmutationaccepted')
 try:validate(list(first))
 except AssertionError:pass
 else:raise AssertionError('Duplicaterowaccepted')
 badslice=list(first);badslice[-1]=rank[c]
 try:validate(badslice)
 except AssertionError:pass
 else:raise AssertionError('Overcapacityrowaccepted')
 assert exp_interval(Q(0))==(Q(1),Q(1));assert log_interval(Q(1))==(Q(0),Q(0));assert all(cost(r,Q(0))==(Q(r,73),Q(r,73))for r in H);endpoint=Q(a.endpoint);baseline={int(k):v for k,v in read(context/'BASELINE-PROFILE.json').items()};prices={}
 for model in ['native','conservative']:
  l,u=moment(H,endpoint,model=='conservative');bl,bu=moment(baseline,endpoint,model=='conservative');prices[model]={'candidate_interval':[str(l),str(u)],'baseline_interval':[str(bl),str(bu)],'delta_interval':[str(l-bu),str(u-bl)],'strictly_cheaper':u<bl,'strictly_worse':l>bu,'candidate_accepts_common_target':u<1,'candidate_rejects_common_target':l>1,'delta_float':float((l+u-bl-bu)/2)}
 context_snapshot();files=[Path(__file__),a.fill,a.order,manifestpath,*[context/name for name in sorted(required)]]+([a.profile]if a.profile else[]);result={'status':'PASS_INDEPENDENT_LITERAL_STOCK_WINDOW_AND_EXACT_MOMENT','roles':len(rows),'calls':666,'helpers_per_call':helper_count,'private_zero_buffers':private_count,'live_stock':66304,'physical_stock':66304+helper_count+8+private_count+2,'rank_mass':4816512,'idle':dict(idle),'global_profile':dict(H),'helper_registry_and_every_actual_role':'PASS','provider_counts':dict(Counter(dispatch[tuple(sr)]for sr in order)),'per_replica_exact_source_events':30,'strict_intervals':len(intervals),'controls':{'missing_role_count':True,'outside_actual_window_mutation_rejected':True,'duplicate_helper_rejected':True,'overcapacity_slice_mutation_rejected':True},'common_target':str(endpoint),'prices':prices,'CPU_seconds':time.process_time()-start,'source_sha256':{str(f):hashlib.sha256(f.read_bytes()).hexdigest()for f in files},'input_list':sorted(required),'baseline_positive_control':'Exact zero-exponent moment; frozen PR2696 baseline profile evaluated by independent engine; full cold phase replay separate','scope':'Independentliteralfiniteallocation+completewordinvoice+own32termatanh/24termTaylorbounds.Nophase/native/global/outeradmissioninferred.'};(a.out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['status','roles','physical_stock','CPU_seconds']}));print(json.dumps({k:{x:v for x,v in p.items()if x not in ['candidate_interval','baseline_interval','delta_interval']}for k,p in prices.items()}))
if __name__=='__main__':main()
