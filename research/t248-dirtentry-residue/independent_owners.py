# SPDX-License-Identifier: Apache-2.0
"""Independently recompute source-event windows and literal doubled-replica owner packing.
No predecessor Python or candidate generator is imported.
"""
from pathlib import Path
import gzip,json,hashlib,argparse
from collections import Counter,defaultdict
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--package',type=Path,default=Path(__file__).resolve().parent);args=ap.parse_args();D=args.package.resolve()
pinfile=D/('SOURCE-PINS.json' if (D/'SOURCE-PINS.json').exists() else 'SOURCES.json')
pins=json.loads(pinfile.read_bytes())['files'];authenticated={}
for pin in pins:
 if Path(pin['name']).name!=pin['name']:raise ValueError('unsafe source name')
 data=(D/'sources'/pin['name']).read_bytes()
 if hashlib.sha256(data).hexdigest()!=pin['sha256']:raise ValueError('source SHA256: '+pin['name'])
 if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=pin['git_blob']:raise ValueError('source Git blob: '+pin['name'])
 authenticated[pin['name']]=data
def source(name):
 data=authenticated[name];return json.loads(gzip.decompress(data)if name.endswith('.gz')else data)

def read(p):
 data=p.read_bytes();return json.loads(gzip.decompress(data)if p.suffix=='.gz'else data)
def check(c,m):
 if not c:raise ValueError(m)
prefix='PR2843' if 'PR2843-FILL.json.gz' in authenticated else 'PR2833'
order=read(D/'ORDER.json');rows=read(D/'FILL.json.gz')['rows'];dispatch={(s,r):p for s,r,p in read(D/'DISPATCH.json')};sourceorder=source(prefix+'-ORDER.json');sourcerows=source(prefix+'-FILL.json.gz')['rows'];sourcedispatch={(s,r):p for s,r,p in source(prefix+'-DISPATCH.json')};providers=source('PR2833-PROVIDERS.json');template=source('PR2833-T37-TEMPLATE.json.gz');plan=source('PR2833-PLAN.json')
T=1+max(r for s,r in sourceorder);N=2*T;calls=9*N
check(len(sourceorder)==9*T and len(set(map(tuple,sourceorder)))==9*T,'source call count')
check(len(read(D/'DISPATCH.json'))==len(dispatch)==calls,'dispatch uniqueness')
check(order==[[s,r+T*g]for s,r in sourceorder for g in (0,1)],'call lift')
check(dispatch=={(s,r+T*g):p for (s,r),p in sourcedispatch.items()for g in (0,1)},'provider lift')
expected=[[2*t+g,h,o+T*g,c,p,z]for t,h,o,c,p,z in sourcerows for g in (0,1)]
changes=[(a,b)for a,b in zip(expected,rows)if a!=b];check(len(expected)==len(rows),'role count')
check(changes==[([0,224,0,0,0,0],[0,224,T,0,0,0]),([1,224,T,0,0,0],[1,224,T,0,0,7])],'only declared edits')
# Each stage is an indivisible block of actual source events, including bridges.
blocks={};stage=None;tail=[]
for ix,e in enumerate(template['execution_schedule']):
 if e['kind'] in ('bank_padding_cover_sweep','translate_every_live_family'):tail.append(ix);continue
 if e['kind']=='local_cover_sweep':stage=e['stage'];blocks[stage]=[]
 check(stage is not None,'event preceding stage');blocks[stage].append((ix,e))
check(tail==[30,31],'global terminal events')
pair={e['stage']:e['pair']for e in template['recipe']if e['kind']=='local'}
rank={}
for e in template['idle_children']:
 check(e['child']not in rank or rank[e['child']]==e['rank'],'child capacity disagreement');rank[e['child']]=e['rank']
clock=0;last={};interval={};call_clock=[];projection=defaultdict(list)
for time,(s,r)in enumerate(order):
 for ix,e in blocks[s]:
  projection[r].append(ix)
  if e['kind']=='local_cover_sweep':last[r,pair[s]]=clock;call_clock.append(clock)
  elif e['kind']=='bridge':last[r,e['src']]=clock;last[r,e['dst']]=clock
  elif e['kind']=='idle_cover_sweep':
   for child in e['child_indices']:
    if child in rank:interval[r,child]=(last.get((r,e['pair']),-1),clock)
  clock+=1
check(len(projection)==N and all(v==list(range(30))for v in projection.values()),'complete ordered source-event projection')
check(len(call_clock)==calls,'calls')
mask={};helpers=[0]*calls;families=[set()for _ in order]
for t,h,owner,ch,port,off in rows:
 check(all(type(x)is int for x in (t,h,owner,ch,port,off)),'noninteger row')
 check(0<=t<calls and 0<=owner<N and 0<=port<112 and off>=0,'row range')
 check(0<=h<408,'helper range');width=providers[dispatch[tuple(order[t])]]['widths'][h]
 begin,end=interval[owner,ch];check(begin<call_clock[t]<end,'strict source-event window')
 family=owner*896+(2*plan['pairs'][str(ch)]+plan['sides'][str(ch)])*112+port
 check(family not in families[t],'same physical family twice in one call');families[t].add(family)
 check(not helpers[t]>>h&1,'duplicate helper');helpers[t]|=1<<h
 key=owner,ch,port;bits=((1<<width)-1)<<off
 check(off+width<=rank[ch]and not(mask.get(key,0)&bits),'capacity or overlap');mask[key]=mask.get(key,0)|bits
check(all(x==(1<<408)-1 for x in helpers),'complete helpers')
idle=Counter()
for owner in range(N):
 for ch,cap in rank.items():
  for port in range(112):
   m=mask.get((owner,ch,port),0);check(not(m&(m+1)),'unused internal gap')
   rem=cap-m.bit_count()
   if rem:idle[rem]+=1
profile=Counter(idle)
for s,r in order:
 for rank_,n in providers[dispatch[s,r]]['actual_paid_profile'].items():profile[int(rank_)]+=n
expectedprofile={int(r):n for r,n in read(D/'PROFILE.json').items()}
check(dict(profile)==expectedprofile,'complete profile mismatch')
result=dict(status='PASS_INDEPENDENT_DOUBLE_RESIDUE_WINDOWS_AND_OWNER_PROFILE',baseline=prefix,roles=len(rows),calls=len(order),replica_projections=N,events_per_replica=30,global_tail=tail,edits=changes,changed_bins=[dict(bin=[r,0,0],used=mask.get((r,0,0),0).bit_count(),idle=rank[0]-mask.get((r,0,0),0).bit_count(),source_event_window=list(interval[r,0]),allowed_call_times=[t for t,pos in enumerate(call_clock)if interval[r,0][0]<pos<interval[r,0][1]])for r in (0,T)],window_coordinate='expanded source-event positions, endpoints excluded; allowed_call_times are separately listed',first_call_event_positions=call_clock[:2],idle=dict(sorted(idle.items())),profile=dict(sorted(profile.items())),rank_mass=sum(r*n for r,n in profile.items()),candidate_sha256={name:hashlib.sha256((D/name).read_bytes()).hexdigest()for name in ['FILL.json.gz','ORDER.json','DISPATCH.json','PROFILE.json']},source_sha256={pin['name']:pin['sha256']for pin in pins},scope='Actual source-event windows and complete finite owner/profile recount; no native operator, physical transcript, precision, or outer admission claimed.')
print(json.dumps(result,indent=2,sort_keys=True))
