# SPDX-License-Identifier: Apache-2.0
"""Independent literal-owner and rational-moment audit for shared-kernel repacking.
Prepared by Yiyang with OpenAI Codex assistance; arithmetic extends our T248 audit.

No producer, inherited checker or numerical library is imported. For 1<=y<=2,
log(y)=2*sum_{j>=0} z^(2j+1)/(2j+1), z=(y-1)/(y+1). After100 terms the tail
is at most 2*z^201/(201*(1-z^2)). Binary range reduction and outward rational
rounding at10^-45 preserve inclusion. For0<=x<1, the Taylor sum through degree18
has positive remainder at most (x^18/18!)*x/19/(1-x/20). The geometric denominator
bounds all ratios after the first omitted term. All subsequent operations use
Fraction. The resulting finite intervals certify moment signs, not physical
realization or an unconditional multiplication theorem.
"""
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
from collections import Counter,defaultdict
import argparse,json,hashlib,gzip
SCALE=10**45

def need(c,m):
 if not c:raise ValueError(m)
def blob(pin,data):
 need(hashlib.sha256(data).hexdigest()==pin['sha256'],'source SHA256: '+pin['name'])
 need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==pin['git_blob'],'source Git blob: '+pin['name'])
# Exact fixture pins from PR2833, PR2843 and PR2848; source bytes are never executed.
FIXED_PINS = {'PR2833-WORD-base.json.gz': ('dda9878455b3a3bec64ca16b1ac7789bbf5ffb603d5713b8df8644485e85b1b7', 'd3878e3be59c50ef60ef1d758215547554134c39'), 'PR2833-WORD-extra.json.gz': ('bbe6bcba59e45e827a8e932ee4b23650d56ed4a0b8e0875c14f23c36b9e47eac', '0638b6ad9d29eec2be61bdb46140c0c5b7b0d21b'), 'PR2833-T37-TEMPLATE.json.gz': ('21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e', '114808c32b1799da53524bdc25cea67efb60009e'), 'PR2833-PROVIDERS.json': ('3666edf67d61b01336e58166ec9edebd72902cc37a2da693b05691ab2a387cda', 'bf7c87b4d1b0fc72b8048751782f9ea6d6657096'), 'PR2833-PLAN.json': ('163431bf8d3bc0d9b894994b1a3cfa7947367b2243b3c0b3a97d740195a1cb08', '5af9dd20821ae5b79778d85cd7183873c5999732'), 'PR2833-ORDER.json': ('aa7c53c188c90fd74421a804f4c6fb13aa1187c06dbac51fa147830a40e00667', '7141bd58cc465e28f0189345713ddd366c814ca4'), 'PR2833-DISPATCH.json': ('fd8132ec8957b908ee6d871216848f18bafc6bd9304acd6185519ee26d97b1ca', '693ed0d022791c43d59000718521fded1ef8def7'), 'PR2843-ORDER.json': ('5fc45c6e6a50db17c1eb2577d36e0dab3057005bc269ea6be1241c79f61aeced', 'b5cc1c6e73ea923bfbc78a493dd25eccf47b532c'), 'PR2843-DISPATCH.json': ('e06a95c589425f92e4cce90b0d71664b96d5955bb34d9ffefdae4b432fa8746b', '1c0260deab477a1600254e3bfc6a3dc69ae483b8'), 'PR2848-CLAIM.json': ('aceb1394b3e8f3abcc9b1a0dc82756ab937ffbefc2f37305a229a00ccc5137e9', '16125d43c4479676f3aa7593574be30780cd3506'), 'PR2848-ORDER.json': ('f6b3bcd6ae7e7f0339cd881204bffc095509cf738982a2d8e221cd622cd54fb1', '73cc025938918fd7876bbcfc0daf54783d7d2629'), 'PR2848-DISPATCH.json': ('24d263f53c792558b1639a85e9f6ed4ee8633d36812db82957006bfbb7e523f7', '30e94fd4fcff569217e0d8b2c8fcceb74d6d21e2')}

FIXED_PINS.update({'PR2833-T37-OWNERS.json.gz': ('3a56f578b2db5647cf6cb811bc6263c7a802ae3e31e9e672596d43185e4e5c9f', '34fa5d69aaa2574af60f1e8f7d43640b03698bca'), 'PR2833-T37-DISPATCH.json': ('b7b971df9dce435556145df307e2bb5138d87e5aa933f1fe61fcc5b5163301c4', '613e01490d24a39e551ba75915320617003c1c81')})

def sources(folder):
 folder=folder/'sources' if (folder/'sources').is_dir() else folder
 raw={};pins=[]
 for name,(sha,git) in FIXED_PINS.items():
  p=folder/name
  if p.exists():data=p.read_bytes()
  elif name=='PR2833-PLAN.json' and (folder/(name+'.gz')).exists():data=gzip.decompress((folder/(name+'.gz')).read_bytes())
  else:continue
  pin={'name':name,'sha256':sha,'git_blob':git};blob(pin,data);raw[name]=data;pins.append(pin)
 return pins,raw

def decode(data,compressed=False):return json.loads(gzip.decompress(data)if compressed else data)
@lru_cache(None)
def logarithm(x):
 need(x>=1,'log argument');k=0
 while x>=2:x/=2;k+=1
 def unit(y):
  z=(y-1)/(y+1);power=z;total=Q(0)
  for j in range(100):total+=power/(2*j+1);power*=z*z
  total*=2;tail=2*power/(201*(1-z*z))
  return total,total+tail
 lo,hi=unit(x);l2,h2=unit(Q(2));lo+=k*l2;hi+=k*h2
 return Q((lo*SCALE).__floor__(),SCALE),Q((hi*SCALE).__ceil__(),SCALE)
def exponential(x):
 need(0<=x<1,'exp argument');term=total=Q(1)
 for j in range(1,19):term*=x/j;total+=term
 tail=term*x/19/(1-x/20)
 return total,total+tail
def moment(profile,b,W):
 lo=hi=Q(0)
 for rank,count in profile.items():
  need(0<rank<73 and count>0,'child profile');l,h=logarithm(Q(73,rank));e0=exponential(b*l)[0];e1=exponential(b*h)[1]
  lo+=Q(count*rank,73*W)*e0;hi+=Q(count*rank,73*W)*e1
 return Q((lo*SCALE).__floor__(),SCALE),Q((hi*SCALE).__ceil__(),SCALE)

def read(path):return decode(path.read_bytes(),path.suffix=='.gz')
CANDIDATE_WORD_PINS={'gauge44':'001b14314d8db873d4d80826d4af9c40a3e5a1fecde743e5a26391bdf673f458','extra':'bc5bfe51178f0c3312d28318412ec490463c896ceed0660b9c443fcb76496546'}
def frame_rank(vectors):
 rows={}
 for x in vectors:
  while x:
   k=x.bit_length()-1
   if k in rows:x^=rows[k]
   else:rows[k]=x;break
 return len(rows)
def audit(base,D,words_dir):
 pins,raw=sources(base)
 def source(name):return decode(raw[name],name.endswith('.gz'))
 order=read(D/'ORDER.json');rows=read(D/'FILL.json.gz')['rows'];drows=read(D/'DISPATCH.json');dispatch={(s,r):p for s,r,p in drows};providers=read(D/'PROVIDERS.json')
 template=source('PR2833-T37-TEMPLATE.json.gz');plan=source('PR2833-PLAN.json');oldproviders=source('PR2833-PROVIDERS.json')
 order_source=None
 for prefix in ['PR2848','PR2843','PR2833']:
  if prefix+'-ORDER.json'not in raw or prefix+'-DISPATCH.json'not in raw:continue
  old_order=source(prefix+'-ORDER.json');old_dispatch=source(prefix+'-DISPATCH.json')
  if order==old_order and dispatch=={(s,r):p for s,r,p in old_dispatch}:order_source=prefix;break
 if order_source is None and 'PR2833-T37-OWNERS.json.gz'in raw:
  timecalls={}
  for row in source('PR2833-T37-OWNERS.json.gz'):
   t=row['time'];pair_=[row['stage'],row['replica']]
   need(t not in timecalls or timecalls[t]==pair_,'unique source T37 time-to-call map');timecalls[t]=pair_
  need(set(timecalls)==set(range(333)),'complete source T37 chronology')
  old_order=[timecalls[t]for t in range(333)];old_dispatch=source('PR2833-T37-DISPATCH.json')
  if order==old_order and dispatch=={(s,r):p for s,r,p in old_dispatch}:order_source='PR2833-T37'
 need(order_source is not None,'authenticated exact call order and provider dispatch')
 T=1+max(r for s,r in order);calls=9*T;W=896*T
 need(len(order)==len(set(map(tuple,order)))==len(dispatch)==len(drows)==calls,'complete unique calls')
 need(set(providers)==set(oldproviders),'provider coverage')
 word_hashes={};canonical_hashes={}
 for pid,p in providers.items():
  word_name='WORD-base.json.gz'if pid=='gauge44'else'WORD-extra.json.gz';word_bytes=(words_dir/word_name).read_bytes();word_hashes[pid]=hashlib.sha256(word_bytes).hexdigest()
  need(word_hashes[pid]==CANDIDATE_WORD_PINS[pid],'fixed candidate word SHA256')
  word=decode(word_bytes,True);canonical_hashes[pid]=hashlib.sha256(json.dumps(word,sort_keys=True,separators=(',',':')).encode()).hexdigest()
  ids=[q for q in range(2*word['report']['v'],2*word['report']['v']+word['report']['R'])if q not in set(word['removed'])]
  ordered_widths=[frame_rank(word['helper_final'].get(str(q),[1<<j for j in range(9)]))-frame_rank(word['start_extra'].get(str(q),[]))for q in ids]
  need(p['widths']==ordered_widths and {int(r):n for r,n in p['actual_paid_profile'].items()}=={int(r):n for r,n in word['report']['local_profile'].items()},'provider bound to fixed word profile and independently derived ordered widths')
  old=oldproviders[pid];ww=p['widths'];pr={int(r):n for r,n in p['actual_paid_profile'].items()}
  need(len(ww)==408 and all(type(w)is int and 1<=w<=9 for w in ww),'helper ABI')
  need(all(type(n)is int and n>0 and 0<r<73 for r,n in pr.items()),'positive local profile')
  need(sum(r*n for r,n in pr.items())-sum(int(r)*n for r,n in old['actual_paid_profile'].items())==sum(ww)-sum(old['widths']),'local width/profile rank conservation')
 blocks={};stage=None;tail=[]
 for ix,e in enumerate(template['execution_schedule']):
  if e['kind']in('bank_padding_cover_sweep','translate_every_live_family'):tail.append(ix);continue
  if e['kind']=='local_cover_sweep':stage=e['stage'];blocks[stage]=[]
  need(stage is not None,'event preceding stage');blocks[stage].append((ix,e))
 need(tail==[30,31],'unchanged terminal global events')
 pair={e['stage']:e['pair']for e in template['recipe']if e['kind']=='local'};rank={}
 for e in template['idle_children']:
  need(e['child']not in rank or rank[e['child']]==e['rank'],'capacity consistency');rank[e['child']]=e['rank']
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
 need(set(projection)==set(range(T))and all(v==list(range(30))for v in projection.values()),'all complete source-event projections')
 need(len(call_clock)==calls,'all local event times')
 masks={};helpers=[0]*calls;families=[set()for _ in order]
 for row in rows:
  need(len(row)==6 and all(type(x)is int for x in row),'integer six-field role')
  t,h,owner,ch,port,off=row;need(0<=t<calls and 0<=owner<T and 0<=h<408 and ch in rank and 0<=port<112 and off>=0,'role ranges')
  width=providers[dispatch[tuple(order[t])]]['widths'][h];begin,end=interval[owner,ch]
  need(begin<call_clock[t]<end,'strict source-event window')
  family=owner*896+(2*plan['pairs'][str(ch)]+plan['sides'][str(ch)])*112+port
  need(family not in families[t],'per-call physical-family collision');families[t].add(family)
  need(not helpers[t]>>h&1,'duplicate helper');helpers[t]|=1<<h
  key=owner,ch,port;bits=((1<<width)-1)<<off
  need(off+width<=rank[ch]and not(masks.get(key,0)&bits),'bin capacity or overlapping offsets');masks[key]=masks.get(key,0)|bits
 need(len(rows)==calls*408 and all(x==(1<<408)-1 for x in helpers),'complete helper roles')
 idle=Counter()
 for owner in range(T):
  for ch,cap in rank.items():
   for port in range(112):
    mask=masks.get((owner,ch,port),0);need(not(mask&(mask+1)),'internal unused gap')
    rem=cap-mask.bit_count()
    if rem:idle[rem]+=1
 profile=Counter(idle)
 for s,r in order:
  for degree,n in providers[dispatch[s,r]]['actual_paid_profile'].items():profile[int(degree)]+=n
 if(D/'PROFILE.json').exists():need(dict(profile)=={int(r):n for r,n in read(D/'PROFILE.json').items()},'candidate full profile receipt')
 mass=sum(r*n for r,n in profile.items());need(mass==65088*T,'complete rank mass')
 prior=Q(source('PR2848-CLAIM.json')['kappa']);tests={}
 for gain in [Q(0),Q(1,10**7),Q(1,10**6)]:
  a,b=moment(profile,prior+gain,W);tests[str(gain)]='PASS_STRICT_MOMENT'if b<1 else'FAIL_STRICT_MOMENT'if a>1 else'UNRESOLVED'
 G=10**25;low=0;high=G//100
 need(moment(profile,Q(low,G),W)[1]<1<moment(profile,Q(high,G),W)[0],'root initial interval')
 while high-low>1:
  mid=(low+high)//2;a,b=moment(profile,Q(mid,G),W)
  if b<1:low=mid
  elif a>1:high=mid
  else:raise ValueError('root interval precision exhausted')
 return dict(complex_lower=str(Q(low,G)),complex_upper=str(Q(high,G)),gain_lower=str(Q(low,G)-prior),gain_upper=str(Q(high,G)-prior),candidate_word_sha256=word_hashes,candidate_word_canonical_sha256=canonical_hashes,status='PASS_INDEPENDENT_ACTUAL_REPACK_OWNERS',order_source=order_source,roles=len(rows),calls=calls,replicas=T,live=W,rank_mass=mass,profile=dict(sorted(profile.items())),idle=dict(sorted(idle.items())),gain_thresholds=tests,prior_kappa=str(prior),window_coordinate='expanded source-event positions, strict endpoints; exact per-replica event projection checked',candidate_sha256={name:hashlib.sha256((D/name).read_bytes()).hexdigest()for name in ['FILL.json.gz','ORDER.json','DISPATCH.json','PROVIDERS.json']},source_sha256={pin['name']:pin['sha256']for pin in pins},scope='Literal unchanged-order owner feasibility, all idle costs and independent exact moment signs. Candidate provider scalar/native validity and full prefix/outer admission remain separate.')

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--base','--source-dir',dest='base',type=Path,required=True);ap.add_argument('--candidate','--candidate-dir',dest='candidate',type=Path,required=True);ap.add_argument('--words-dir',type=Path,required=True);a=ap.parse_args();print(json.dumps(audit(a.base,a.candidate,a.words_dir),sort_keys=True,indent=2))
