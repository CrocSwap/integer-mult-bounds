"""Independent selected eleven-stage signed79 owner/window/profile check."""
import json,gzip,hashlib
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'experiments/stage-search/pr445-signed79-eleven'
read=lambda p:json.loads(p.read_text())
blob=gzip.decompress((B/'hosted/GLOBAL-TEMPLATE.json.gz').read_bytes());t=json.loads(blob);g=read(B/'hosted/GLOBAL.json')
assert hashlib.sha256(blob).hexdigest()==g['template_sha256']
frames=read(B/'signed/records/frames.json')['frames'];states=read(B/'signed/records/249-states.json')['initial']
widths=[8-len(frames[str(states[str(240+h)])]['B']) for h in range(740)]
assert Counter(widths)=={8:661,7:71,4:8};assert(t['m'],t['replicas'],t['live'])==(78,8,9600)
last={};locals_=[];win={};idx=0
for pos,e in enumerate(t['schedule']):
 if e['kind']=='local_cover_sweep':last[e['pair']]=pos;locals_.append((pos,e['stage'],e['pair']))
 elif e['kind']=='bridge':last[e['dst']]=last[e['src']]=pos
 elif e['kind']=='idle':
  lo=last.get(e['pair'],-1);allowed={s for q,s,p in locals_ if lo<q<pos and p!=e['pair']};win[idx]=(e['pair'],e['rank'],allowed);idx+=1
chosen={};used=defaultdict(set)
for i,cp,off,w,s,h in t['hosting']['slots']:
 pair,rank,allowed=win[i];assert s in allowed and w==widths[h] and 0<=off<off+w<=rank and 0<=cp<240
 assert(s,h)not in chosen;chosen[s,h]=(i,cp,off,w)
 seg=set(range(off,off+w));assert not used[i,cp]&seg;used[i,cp]|=seg
assert len(chosen)==8140
paid=Counter();count=0
for c in t['calls']:
 s,rep,pair=c['stage'],c['replica'],c['pair'];assert len(c['owners'])==980
 for z,(f,route) in enumerate(c['owners'][:240]):
  side,p=divmod(z,120);assert rep*1200+2*pair*120<=f<rep*1200+(2*pair+2)*120
 seen=set()
 for h,(f,route) in enumerate(c['owners'][240:]):
  i,cp,off,w=chosen[s,h];target=win[i][0];side,p=divmod(cp,120)
  assert f==rep*1200+(2*target+side)*120+p and target!=pair and route==['hosted',i,off,w]
  assert(f,tuple(route))not in seen;seen.add((f,tuple(route)));count+=1
 for z in t['local_programs'][c['orientation']]:
  if z[0]==0 and z[4]:paid[z[4]]+=1
  if z[0]==2:paid[z[5]]+=1
for i,(pair,rank,allowed)in win.items():
 rr=Counter(rank-len(used[i,cp])for cp in range(240))
 if str(i) in t['hosting']['remainders']:assert {str(r):n for r,n in sorted(rr.items())}==t['hosting']['remainders'][str(i)]
 for r,n in rr.items():
  if r:paid[r]+=8*n
assert dict(paid)=={int(r):n for r,n in g['profile'].items()}
mass=sum(r*n for r,n in paid.items());assert mass==g['rank_mass'] and 78*9600-mass==g['deficit']
out={'status':'PASS_INDEPENDENT_SIGNED79_ELEVEN_OWNER_WINDOWS_AND_PAID_PROFILE','template_sha256':hashlib.sha256(blob).hexdigest(),'widths':dict(Counter(widths)),'selected_slots_per_replica':len(chosen),'realized_slots':count,'profile':dict(sorted(paid.items())),'rank_mass':mass,'deficit':g['deficit'],'live':9600,'banks':0,'scope':'Assignment, disjoint pending slots, native literal recursive child profile. Sigma/operator, signed local endpoint and prefix/invoice have separate source-linked certificates.'}
(B/'hosted/INDEPENDENT-ASSIGNMENT.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
