"""Independent own-template hosting assignment/profile audit; no generator imports."""
import gzip,json,hashlib,argparse
from pathlib import Path
from collections import Counter,defaultdict

def read(p):return json.loads(p.read_text())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('parent',type=Path);ap.add_argument('hosted',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 oldblob=gzip.decompress((a.parent/'GLOBAL-TEMPLATE.json.gz').read_bytes());newblob=gzip.decompress((a.hosted/'GLOBAL-TEMPLATE.json.gz').read_bytes());old=json.loads(oldblob);new=json.loads(newblob);g=read(a.hosted/'GLOBAL.json')
 assert hashlib.sha256(newblob).hexdigest()==g['template_sha256'];assert new['local_programs']==old['local_programs'];assert len(new['calls'])==len(old['calls'])
 H=new['h'];m=new['m'];T=new['replicas'];V=len(new['calls'][0]['owners'][:240])//2;R=len(new['calls'][0]['owners'])-2*V;DATA=2*4*V*T
 assert(H,m,T,V,R)==(8,64,64,120,740)
 widths=[o[1][2] for o in old['calls'][0]['owners'][2*V:]];assert set(widths)<={4,7,8}
 for c in old['calls']:
  assert [o[1][2]for o in c['owners'][2*V:]]==widths
 last={};locals_=[];win={};idx=0;positions={};schedule=old['schedule']
 for pos,e in enumerate(schedule):
  if e['kind']=='local_cover_sweep':last[e['pair']]=pos;locals_.append((pos,e['stage'],e['pair']))
  elif e['kind']=='bridge':last[e['dst']]=last[e['src']]=pos
  elif e['kind']=='idle':
   lo=last.get(e['pair'],-1);allowed={s for q,s,p in locals_ if lo<q<pos and p!=e['pair']};win[idx]=(e['pair'],e['rank'],allowed);positions[idx]=(lo,pos);idx+=1
 slots=new['hosting']['slots'];chosen={};used=defaultdict(set);remainders={}
 for i,cp,off,w,s,h in slots:
  pair,rank,allowed=win[i];assert s in allowed and w==widths[h] and 0<=off<off+w<=rank and 0<=cp<2*V
  assert(s,h)not in chosen;chosen[s,h]=(i,cp,off,w)
  segment=set(range(off,off+w));assert not used[i,cp]&segment;used[i,cp]|=segment
 # Independent owner realization and complete bank coordinate tiling.
 banks=defaultdict(list);hosted_count=0
 for c0,c in zip(old['calls'],new['calls']):
  assert {k:c[k]for k in ('stage','pair','replica','orientation','local_hash')}=={k:c0[k]for k in ('stage','pair','replica','orientation','local_hash')}
  assert c['owners'][:2*V]==c0['owners'][:2*V]
  s,rep,pair=c['stage'],c['replica'],c['pair'];seen=set()
  for h,(f,route)in enumerate(c['owners'][2*V:]):
   assert 0<=f<new['live'];assert(f,tuple(route))not in seen;seen.add((f,tuple(route)))
   if(s,h)in chosen:
    i,cp,off,w=chosen[s,h];target=win[i][0];side,port=divmod(cp,V)
    assert f==rep*960+(2*target+side)*V+port and target!=pair
    assert route==['hosted',i,off,w];hosted_count+=1
   else:
    assert route[0]=='bank' and route[2]==widths[h] and f>=DATA;banks[s,f].append((route[1],route[2]))
 for key,intervals in banks.items():
  cover=[]
  for off,w in intervals:cover+=list(range(off,off+w))
  assert sorted(cover)==list(range(m))
 # Recompute full paid profile from actual literal calls and pending remainders.
 paid=Counter()
 for c in new['calls']:
  for z in new['local_programs'][c['orientation']]:
   if z[0]==0 and z[4]:paid[z[4]]+=1
   if z[0]==2:paid[z[5]]+=1
 for i,(pair,rank,allowed)in win.items():
  rr=Counter(rank-len(used[i,cp])for cp in range(2*V))
  for r,n in rr.items():
   if r:paid[r]+=n*T
  if str(i)in new['hosting']['remainders']:assert {str(r):n for r,n in sorted(rr.items())}==new['hosting']['remainders'][str(i)]
 assert dict(paid)=={int(r):n for r,n in g['profile'].items()};mass=sum(r*n for r,n in paid.items());assert m*new['live']-mass==m*old['live']-sum(int(r)*n for r,n in read(a.parent/'GLOBAL.json')['profile'].items())
 result={'status':'PASS_INDEPENDENT_OWN_SIGNED75_HOST_ASSIGNMENT_AND_PROFILE','parent_template_sha256':hashlib.sha256(oldblob).hexdigest(),'hosted_template_sha256':hashlib.sha256(newblob).hexdigest(),'residual_widths':dict(Counter(widths)),'replicas':T,'hosted_residuals':hosted_count,'live':new['live'],'rank_mass':mass,'profile':dict(sorted(paid.items())),'bank_families':len(banks),'all_banks_exact64':True,'all_native_local_words_identical':True,'scope':'Independent combinatorial assignment/profile check. Exact orthogonal hosted isometries, signed local endpoint/dirt, reflected words and route invoice require separate source-linked gates; distinct route descriptors alone do not prove physical cover injection.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
if __name__=='__main__':main()
