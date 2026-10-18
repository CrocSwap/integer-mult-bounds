from pathlib import Path
import sys,json,gzip,copy,hashlib
from collections import Counter,defaultdict
from fractions import Fraction as Q
OLD,WORD,PLAN,OWNERS,PROFILE,OUT=map(Path,sys.argv[1:]);read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes());old=read(OLD);word=read(WORD);plan=read(PLAN);roles=read(OWNERS);lp=read(PROFILE)['local_profile_after'];assert plan['order']==old['order']and plan['windows']==old['windows']and plan['pairs']==old['pairs']and plan['sides']==old['sides'];assert len(word['ports'])==112 and word['report']['R']==504
widths=[]
for h in range(504):
 basis=word['start_extra'].get(str(224+h),[]);piv={}
 for x in basis:
  y=int(x)
  while y:
   j=y.bit_length()-1
   if j in piv:y^=piv[j]
   else:piv[j]=y;break
  assert y!=0
 widths.append(9-len(basis))
assert widths==plan['baseline_widths']
def audit(rs):
 by=defaultdict(list);bins=defaultdict(list)
 for r in rs:
  t=r['time'];s,rep=plan['order'][t];assert[s,rep]==[r['stage'],r['replica']];assert r['width']==widths[r['helper']]
  owner,port=divmod(r['copy'],112);i=r['child'];assert owner==r['owner_replica']and port==r['port'];assert r['family']==896*owner+(2*plan['pairs'][str(i)]+plan['sides'][str(i)])*112+port;assert 0<=r['family']<7168;assert t in old['windows'][f'{owner},{i}'][1]
  by[t].append(r);bins[i,r['copy']].append(r)
 assert len(rs)==36288 and set(by)==set(range(72))
 for t,xs in by.items():
  s,rep=plan['order'][t];assert len(xs)==504 and {r['helper']for r in xs}==set(range(504));fam={r['family']for r in xs};assert len(fam)==504;pair=max(0,(s-1)//2);data=set(range(rep*896+pair*224,rep*896+(pair+1)*224));assert not fam&data
 H=Counter({int(r):72*n for r,n in lp.items()});rem=Counter();patterns=Counter()
 for rep in range(8):
  for c in range(18):
   rank=old['windows'][f'{rep},{c}'][0]
   for port in range(112):
    at=0;ws=[]
    for r in sorted(bins[c,rep*112+port],key=lambda r:r['offset']):assert r['offset']==at;at+=r['width'];ws.append(r['width'])
    assert at<=rank;patterns[rank,tuple(sorted(ws))]+=1
    if rank>at:H[rank-at]+=1;rem[rank-at]+=1
 assert dict(H)=={int(r):n for r,n in plan['profile'].items()};assert 73*7168-sum(r*n for r,n in H.items())==2560
 return dict(sorted(H.items())),dict(sorted(rem.items())),patterns
H,rem,pat=audit(roles);controls=[]
for name in['alias','width','offset','time','active_data']:
 bad=copy.deepcopy(roles)
 if name=='alias':bad[1]=dict(bad[0],helper=bad[1]['helper'])
 elif name=='width':bad[0]['width']+=1
 elif name=='offset':bad[0]['offset']+=1
 elif name=='time':bad[0]['time']=(bad[0]['time']+1)%72
 else:bad[0]['family']=0
 try:audit(bad)
 except(AssertionError,IndexError,KeyError):controls.append(name)
 else:raise AssertionError('accepted '+name)
D=Counter({int(r):n for r,n in H.items()});D.subtract({int(r):n for r,n in old['profile'].items()});D={r:n for r,n in D.items()if n};assert sum(r*n for r,n in D.items())==0
# Range-reduced positive atanh series, with an exact rational geometric tail.
def little_log(x,N=18):
 z=(x-1)/(x+1);s=2*sum((z**(2*k+1)/Q(2*k+1)for k in range(N)),Q(0));return s,s+2*z**(2*N+1)/(Q(2*N+1)*(1-z*z))
l2,u2=little_log(Q(2))
def logs(r):
 k=r.bit_length()-1;l,u=little_log(Q(r,2**k));return k*l2+l,k*u2+u
lower=Q(0);M=Q(0)
for r,n in D.items():
 l,u=logs(r);lower+=n*r*(l if n>0 else u);M+=abs(n)*r*u*u
assert lower>22585 and M<216748;assert Q(22585)-Q(216748,1000)>0
res={'status':'PASS_EXACT_UNIFORM_RESOURCE_CALCULUS','roles':36288,'calls':72,'helpers_per_call':504,'pending_bins':16128,'source_width_inventory':dict(Counter(widths)),'profile':H,'remainders':rem,'patterns':[[r,list(ws),n]for(r,ws),n in sorted(pat.items())],'controls_rejected':controls,'universal_context_dominance':{'saving_interval':'0 < b <= 1/500','delta':D,'mass_delta':0,'g_prime_1_lower':22585,'absolute_second_derivative_upper':216748,'strict_negative_linear_margin':'5592063/250'},'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in[OLD,WORD,PLAN,OWNERS,PROFILE]},'scope':'Exact source-width, actual whole-family/time assignment and full paid profile; full source-specific charts/normalized wrappers and finite invoice are separately required.'}
OUT.write_text(json.dumps(res,indent=2)+'\n',encoding='utf8',newline='\n');print(json.dumps(res,indent=2))
