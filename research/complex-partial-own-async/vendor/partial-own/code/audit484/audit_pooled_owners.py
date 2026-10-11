"""Independent actual whole-owner charts and full paid-profile recount for PR484.
Uses raw canonical word, local programs and emitted owner arrays, no package imports.
OpenAI Codex audit; inherited all-size assumptions are outside this finite check.
"""
from pathlib import Path
from collections import Counter,defaultdict
import json,gzip,hashlib
import sys
O=Path(sys.argv[1]);V=Path(sys.argv[2]);HOSTED=Path(sys.argv[3]);PHASES=Path(sys.argv[4])
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
w=read(V/'split-centres/CANONICAL-WORD.json.gz');t=read(HOSTED/'GLOBAL-TEMPLATE.json.gz');parent=read(V/'split-centres/GLOBAL-TEMPLATE.json.gz');ph=read(PHASES);host=read(HOSTED/'HOSTED.json');M=73;DATA=7680;H=9;n=800
assert (w['v'],w['R'],w['h'])==(120,560,9)and t['live']==7680
widths=[H-len(w['frames'][w['start'][240+i]])for i in range(560)]
def par(a):return a.bit_count()&1
def basis(q):
 j=0 if not(q&1)else next(i for i in range(1,9)if not(q>>i&1));u=q^(1<<j);cols=[]
 for z in range(9):
  i=j if z==0 else 0 if z==j else z;x=1<<i;cols.append(x^u if par(x&u)else x)
 cols += [1<<i for i in range(9,M)]
 assert all(par(x&y)==(i==j)for i,x in enumerate(cols)for j,y in enumerate(cols));return cols
B=[basis(q)for q in w['ports']];assert [p['q']for p in ph['recipes']]==w['ports']
local={};paid=Counter();ledger={}
for ori,evs in t['local_programs'].items():
 c=Counter()
 for e in evs:
  if e[0]=='climb':c[e[5]]+=1
  elif e[0]=='center':c[e[4]]+=1
 local[ori]=c
 assert c==Counter({int(r):k for r,k in w['local_profile'].items()})
 ledger[ori]=hashlib.sha256(json.dumps(evs,sort_keys=True,separators=(',',':')).encode()).hexdigest()
expected_sigmas={};sigma_stream=hashlib.sha256();cross_replica=0
assert t['local_programs']==parent['local_programs']
used=defaultdict(set);bank=defaultdict(set);specs=[];charts=hashlib.sha256();hosted=banked=0;calls=set();chartcache=set()
for call in t['calls']:
 s,rep,pair=call['stage'],call['replica'],call['pair'];assert (s,rep)not in calls;calls.add((s,rep));own=call['owners'];assert len(own)==n and len({f for f,r in own})==n
 assert all(0<=f<t['live']for f,r in own)
 assert own[:240]==next(c for c in parent['calls']if(c['stage'],c['replica'])==(s,rep))['owners'][:240]
 ori=call['orientation'];assert call['local_program_sha256']==ledger[ori];paid.update(local[ori])
 for h,(f,r)in enumerate(own[240:]):
  w0=widths[h];e0=9-w0
  if r[0]in(3,4):
   assert f<DATA; owner_replica=f//960
   port=f%120;ch,off=r[1:3];pend=ph['recipes'][port]['idle_children'][ch]['orthogonal_axes'];axes=pend[off:off+w0];assert len(axes)==w0
   idx=[B[port].index(x)for x in axes]
   sp=[]if not e0 else r[4];assert (r[0]==4)==bool(e0)
   if e0:assert r[3]==w0 and sp==[i for i in range(M)if i not in idx][:e0]
   key=(owner_replica,ch,port);assert not set(range(off,off+w0))&used[key];used[key].update(range(off,off+w0));hosted+=1
   chart=idx+sp+[i for i in range(M)if i not in idx+sp]
   sigma=[B[port][i]for i in chart];sh=hashlib.sha256(json.dumps(sigma,separators=(',',':')).encode()).hexdigest();expected_sigmas[sh]=sigma
   cross_replica+=owner_replica!=rep
   sigma_stream.update(json.dumps([s,rep,h,f,sh],separators=(',',':')).encode()+b'\n')
   assert len(chart)==M and len(set(chart))==M
  else:
   assert r[0]==2 and DATA<=f<t['live']
   if len(r)==2:assert w0==9;off=9*r[1];sp=[]
   else:off=r[1];assert r[2]==w0 and e0>0;sp=r[3]
   idx=list(range(off,off+w0));assert len(sp)==e0 and len(set(idx+sp))==9
   assert not set(idx)&bank[f];bank[f].update(idx);specs.append((f,sp,e0));banked+=1
   chart=idx+sp+[i for i in range(M)if i not in idx+sp];assert len(chart)==M and set(chart)==set(range(M))
  charts.update(json.dumps([s,rep,h,f,chart],separators=(',',':')).encode()+b'\n');chartcache.add((r[0],f%120 if f<DATA else-1,tuple(chart)))
assert len(calls)==72 and calls=={(s,r)for s in range(9)for r in range(8)}
expected_idle=[];side={};pairs={}
for event in parent['execution_schedule']:
 if event['kind']=='idle_cover_sweep':
  for sd,ch in enumerate(event['child_indices']):side[ch]=sd;pairs[ch]=event['pair']
for it in parent['idle_children']:
 ch,port,r=it['child'],it['port'],it['rank'];assert it['replicas']==8
 for rep in range(8):
  cells=used[rep,ch,port];assert all(0<=x<r for x in cells);left=r-len(cells)
  if left:
   paid[left]+=1
   expected_idle.append(dict(child=ch,port=port,replica=rep,replicas=1,family=rep*960+(2*pairs[ch]+side[ch])*120+port,rank=left,hosted=len(cells),pending_offset=len(cells)))
assert t['idle_children']==expected_idle
assert expected_sigmas==read(HOSTED/'ACTUAL-SIGMAS.json.gz')
assert len(expected_idle)<=sum(x['replicas']for x in parent['idle_children'])
assert sorted(bank)==list(range(DATA,t['live']))
for f,cells in bank.items():
 assert cells==set(range(len(cells)));pad=M-len(cells);parts=(pad+50)//51
 for i in range(parts):paid[pad//parts+(i<pad%parts)]+=1
for f,sp,e0 in specs:assert sp==list(range(len(bank[f]),len(bank[f])+e0))
assert paid==Counter({int(r):k for r,k in host['global_profile'].items()});mass=sum(r*k for r,k in paid.items());assert M*t['live']-mass==2496
out=dict(status='PASS_INDEPENDENT_ACTUAL_OWNER_CHARTS_AND_COMPLETE_PAID_PROFILE',calls=len(calls),actual_73column_sigmas=len(expected_sigmas),sigma_stream_sha256=sigma_stream.hexdigest(),cross_replica_helper_roles=cross_replica,explicit_idle_remainder_children=len(expected_idle),source_idle_children_charged=sum(x['replicas']for x in parent['idle_children']),actual_helper_owner_charts=hosted+banked,distinct_charts=len(chartcache),hosted_residuals=hosted,banked_residuals=banked,all_800_owners_per_call_distinct=True,entering_helpers=sum(w<9 for w in widths),widths=dict(Counter(widths)),live=t['live'],physical=t['physical'],banks=len(bank),rank_mass=mass,deficit=2496,paid_profile=dict(sorted(paid.items())),owner_charts_sha256=charts.hexdigest(),local_program_sha256=ledger,scope='Every residual plus spectator chart extends to one complete invertible orthogonal73-axis basis within its single owner family; unique owners prevent within-call aliasing. Individual normalized helper identity supplied by fresh512-column LemmaA/G check; all-size compiler assumptions retained.')
(O/'OWNERS-AND-PROFILE.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
