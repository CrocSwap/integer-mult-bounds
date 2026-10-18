# SPDX-License-Identifier: Apache-2.0
"""Independent shared-kernel changed-inventory LP and rational-moment audit.
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
from itertools import product

def rank(vs):
 piv={}
 for x in vs:
  while x:
   k=x.bit_length()-1
   if k in piv:x^=piv[k]
   else:piv[k]=x;break
 return len(piv)

def widths(word):
 v=word['report']['v'];n=2*v+word['report']['R'];removed=set(word['removed']);out={}
 for q in range(2*v,n):
  if q not in removed:out[q]=rank(word['helper_final'].get(str(q),[1<<j for j in range(9)]))-rank(word['start_extra'].get(str(q),[]))
 return out

def run_audit(base,receipt_path,candidate_dir=None):
 receipt=json.loads(receipt_path.read_bytes())
 pins,raw=sources(base)
 def source(name):return decode(raw[name],name.endswith('.gz'))
 oldproviders=source('PR2833-PROVIDERS.json');template=source('PR2833-T37-TEMPLATE.json.gz')
 T=receipt['replicas'];W=896*T;order_source=None
 for prefix in ['PR2848','PR2843','PR2833']:
  if prefix+'-ORDER.json'not in raw or prefix+'-DISPATCH.json'not in raw:continue
  order=source(prefix+'-ORDER.json');dispatch=source(prefix+'-DISPATCH.json');sourceT=1+max(r for s,r in order)
  need(len(order)==len(dispatch)==len(set(map(tuple,order)))==9*sourceT,'source replica/call law')
  if T%sourceT==0:
   calls=Counter(p for s,r,p in dispatch);calls=Counter({p:n*(T//sourceT)for p,n in calls.items()});order_source=prefix;break
 need(T==248 and order_source is not None,'authenticated call-count lift for LP')
 need(W==receipt['live'] and dict(calls)==receipt['calls'],'actual live and call multiplicities')
 cap_by_child={}
 for row in template['idle_children']:
  c=row['child'];n=row['rank'];need(c not in cap_by_child or cap_by_child[c]==n,'consistent source capacities');cap_by_child[c]=n
 bins=Counter()
 for n in cap_by_child.values():bins[n]+=T*112
 need(dict(bins)=={int(k):v for k,v in receipt['bins'].items()},'complete bin inventory')
 providers={k:{'widths':v['widths'],'profile':{int(r):n for r,n in v['actual_paid_profile'].items()}}for k,v in oldproviders.items()}
 changes={}
 for pid,entry in receipt['candidate_local_checks'].items():
  p=(candidate_dir/('WORD-base.json.gz'if pid=='gauge44'else'WORD-extra.json.gz'))if candidate_dir else Path(entry['word_path']);blob_=p.read_bytes();need(hashlib.sha256(blob_).hexdigest()==entry['word_sha256'],'candidate word digest')
  new=decode(blob_,p.suffix=='.gz');old=source('PR2833-WORD-'+('base'if pid=='gauge44'else'extra')+'.json.gz');ww=widths(new);ow=widths(old)
  need(list(ww)==list(ow) and list(ow.values())==oldproviders[pid]['widths'],'fixed helper identity and baseline widths')
  pnew={int(r):n for r,n in new['report']['local_profile'].items()};need(pnew=={int(r):n for r,n in entry['frame_check']['profile'].items()},'profile receipt bound to literal word report')
  providers[pid]={'widths':list(ww.values()),'profile':pnew};changes[pid]=[[q,ow[q],n]for q,n in ww.items()if n!=ow[q]]
 inventory=Counter();local=Counter()
 for pid,p in providers.items():
  for w in p['widths']:inventory[w]+=calls[pid]
  for r,n in p['profile'].items():local[r]+=calls[pid]*n
 need(dict(inventory)=={int(k):v for k,v in receipt['width_inventory'].items()},'every helper width charged')
 need(dict(local)=={int(k):v for k,v in receipt['local_paid'].items()},'every local profile charged')
 caps=sorted(bins);ws=sorted(inventory);patterns=[]
 # Independent bounded count-vector enumeration, not recursive sequence construction.
 for cap in caps:
  for counts in product(*(range(cap//w+1)for w in ws)):
   used=sum(w*n for w,n in zip(ws,counts))
   if used<=cap:patterns.append((cap,counts,cap-used))
 need(len(patterns)==receipt['patterns']==1163,'finite pattern coverage')
 allkeys={(cap,counts)for cap,counts,r in patterns};need(len(allkeys)==len(patterns),'unique patterns')
 primal_bins=Counter();primal_widths=Counter();idle=Counter()
 for p in receipt['active_patterns']:
  cap=p['capacity'];counts=tuple(p['widths'].count(w)for w in ws);n=Q(p['count']);need(n>=0 and (cap,counts)in allkeys and set(p['widths'])<=set(ws),'primal pattern')
  primal_bins[cap]+=n
  for w,m in zip(ws,counts):primal_widths[w]+=n*m
  r=cap-sum(p['widths'])
  if r:idle[r]+=n
 need(primal_bins==bins and primal_widths==inventory,'all exact primal balance equations')
 need(dict(idle)=={int(k):Q(v)for k,v in receipt['idle'].items()},'idle remainder bill')
 hist=Counter(local);hist.update(idle);need(dict(hist)=={int(k):Q(v)for k,v in receipt['global_paid'].items()},'complete global profile')
 mass=sum(r*n for r,n in hist.items());need(mass==65088*T==16141824,'rank-mass identity')
 lo,hi=Q(receipt['complex_lower']),Q(receipt['complex_upper']);need(moment(hist,lo,W)[1]<1<moment(hist,hi,W)[0],'independent exact root bracket')
 prior=Q(source('PR2848-CLAIM.json')['kappa']);need(lo-prior==Q(receipt['exact_gain_lower'])and hi-prior==Q(receipt['exact_gain_upper']),'gain bound to incumbent')
 ranks=receipt['dual']['rank_basis'];need(ranks==sorted({r for cap,counts,r in patterns if r}),'dual covers every positive idle rank')
 Y=[[Q(z)for z in row]for row in receipt['dual']['coefficients']];need(len(Y)==len(caps)+len(ws)and all(len(row)==len(ranks)for row in Y),'dual dimension')
 H={r:moment({r:73},hi,1)for r in ranks};tight=[];minimum=None
 for cap,counts,r in patterns:
  a=[int(cap==k)for k in caps]+list(counts)
  coeff=[Q(int(k==r))-sum(n*Y[j][i]for j,n in enumerate(a))for i,k in enumerate(ranks)]
  if not any(coeff):tight.append((cap,counts));continue
  lower=sum(n*H[k][0 if n>0 else 1]for k,n in zip(ranks,coeff))
  need(lower>0,'dual sign/slack failure')
  minimum=lower if minimum is None else min(minimum,lower)
 expected={(p['capacity'],tuple(p['widths'].count(w)for w in ws))for p in receipt['dual']['tight_patterns']}
 need(set(tight)==expected and len(patterns)-len(tight)==receipt['dual']['strict_positive'],'tight pattern and strict slack counts')
 active={(p['capacity'],tuple(p['widths'].count(w)for w in ws))for p in receipt['active_patterns']}
 need(active<=set(tight),'complementary slackness')
 thresholds={}
 for gain,expected in receipt['material_gain_checks'].items():
  a,b=moment(hist,prior+Q(gain),W);actual='PASS_EXACT_PRIMAL_MOMENT'if b<1 else'FAIL_EXACT_PRIMAL_MOMENT'if a>1 else'UNRESOLVED'
  need(actual==expected,'independent material threshold '+gain);thresholds[gain]=actual
 return dict(status='PASS_INDEPENDENT_FULL_PATTERN_RELAXATION_AUDIT',replicas=T,live=W,calls=dict(calls),call_count_source=order_source,patterns=len(patterns),patterns_by_capacity=dict(Counter(cap for cap,counts,r in patterns)),tight_patterns=len(tight),strict_patterns=len(patterns)-len(tight),minimum_slack_lower=str(minimum),rank_mass=str(mass),material_gain_checks=thresholds,changed_helpers=changes,complex_lower=str(lo),complex_upper=str(hi),gain_lower=str(lo-prior),gain_upper=str(hi-prior),receipt_sha256=hashlib.sha256(receipt_path.read_bytes()).hexdigest(),source_sha256={pin['name']:pin['sha256']for pin in pins},scope='Complete fractional nonchronological bin-pattern relaxation and independent exact moment/dual signs. Local word/frame validity is separately audited; a positive fractional primal is not an actual owner witness.')

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--base','--source-dir',dest='base',type=Path,required=True);ap.add_argument('--receipt',type=Path,required=True);ap.add_argument('--candidate-dir',type=Path);a=ap.parse_args();print(json.dumps(run_audit(a.base,a.receipt,a.candidate_dir),sort_keys=True,indent=2))
