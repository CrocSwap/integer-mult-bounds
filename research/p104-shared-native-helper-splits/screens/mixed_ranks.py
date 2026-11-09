"""Source-bound finite fresh-frame screen. @CubeJerry, OpenAI assistance.
Kernel elimination adapts Ali Romman's helper method. Apache-2.0.
Floating point selects the finite domain; exact arithmetic checks its cuts.
"""
import sys,json,gzip,time,itertools
from pathlib import Path
from fractions import Fraction as Q
from collections import defaultdict,Counter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from linear import read,span,add,need,main_roles,digest
from split import basis
import argparse
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--word',required=True)
ap.add_argument('--output',required=True)
args=ap.parse_args();ROOT=Path(args.output);ROOT.mkdir(parents=True,exist_ok=True);SOURCE=Path(args.word)
w=read(SOURCE);need(digest(w)=='c9f6308b8570e5eadc4b493fa764c4f884560d4eca11a8ba03c8ea8cbd2631b6','Exact 46-split input');n=w['public'];N=n+w['owned_fields'];dims=list(map(len,w['frames']));spaces=[span(b)for b in w['frames']];existing=set(spaces)
group={r for r in range(n)if r not in main_roles(w)and(w['initial'][r],w['final'][r])==(3,127)}
contacts=defaultdict(list);moves=defaultdict(list)
for i,e in enumerate(w['program']):
 if e[0]=='MOVE':moves[e[1]].append(i)
 else:
  contacts[e[1]].append(i)
  if e[0]in('ADD','COPY'):contacts[e[2]].append(i)
windows=[]
for r in range(N):
 touch=[-1]+contacts[r]+[len(w['program'])]
 for lo,hi in zip(touch,touch[1:]):
  mi=[i for i in moves[r]if lo<i<hi]
  if len(mi)!=1:continue
  e=w['program'][mi[0]];a,b=e[2:4]
  if abs(dims[a]-dims[b])<2:continue
  lower,upper=(a,b)if dims[a]<dims[b]else(b,a)
  windows.append(dict(role=r,lo=lo+1,hi=hi,old=a,new=b,moves=mi,old_paid=[abs(dims[a]-dims[b])],new_paid=[],private=e[4],lower=lower,upper=upper))

def canonical_basis(space):
 out=[];have={0}
 for x in sorted(space):
  if x not in have:out.append(x);have|={y^x for y in tuple(have)}
 return out

def join(a,b):
 result=set(a)
 for x in b:
  if x not in result:result|={y^x for y in tuple(result)}
 return frozenset(result)

geometries={};optimistic={};pairs=0;t=1-.00355220
for i,A in enumerate(windows):
 for j in range(i):
  B=windows[j]
  if A['role']==B['role']or not({A['role'],B['role']}&group):continue
  lo,hi=max(A['lo'],B['lo']),min(A['hi'],B['hi'])
  if lo>hi:continue
  pairs+=1;lower=join(spaces[A['lower']],spaces[B['lower']]);upper=spaces[A['upper']]&spaces[B['upper']]
  if not lower<=upper:continue
  for F in (lower,frozenset(upper)):
   k=len(canonical_basis(F))
   if F in existing or k in(0,9):continue
   bill=sum(abs(k-dims[h['old']])**t+abs(dims[h['new']]-k)**t-h['old_paid'][0]**t for h in(A,B))
   gain=k**t+(9-k)**t-9**t-bill
   if gain<=1e-12:continue
   optimistic[F]=max(optimistic.get(F,-1),gain)
   geometries.setdefault(F,set()).add(lo)
print('coast_windows',len(windows),'overlap_pairs',pairs,'fresh_frame_geometries',len(geometries),flush=True)
t=1-.00355220;cost=2-2**t
cases=defaultdict(list);casecount=0
for F,seedcuts in sorted(geometries.items(),key=lambda x:(-optimistic[x[0]],canonical_basis(x[0])))[:2048]:
 k=len(canonical_basis(F));gain=k**t+(9-k)**t-9**t
 if gain<=2*cost:continue
 eligible=[i for i,h in enumerate(windows)if spaces[h['lower']]<F<spaces[h['upper']]]
 # Endpoint changes of these constant-value windows cover every pool regime.
 cuts=sorted({windows[i]['lo']for i in eligible})
 for cut in cuts:
  active=[i for i in eligible if windows[i]['lo']<=cut<=windows[i]['hi']]
  if len(active)<2 or not any(windows[i]['role']in group for i in active):continue
  roles={windows[i]['role']:i for i in active}
  costs={r:abs(k-dims[windows[i]['old']])**t+abs(dims[windows[i]['new']]-k)**t-windows[i]['old_paid'][0]**t for r,i in roles.items()}
  cases[cut].append(dict(frame_basis=canonical_basis(F),dimension=k,window_of=roles,costs=costs,gain=gain))
  casecount+=1
print('candidate_frame_cut_cases',casecount,flush=True)

def pure(rows,roles):
 pivots={};out=[]
 for r in roles:
  outside={k:v for k,v in rows[r].items()if k not in group};inside={k:v for k,v in rows[r].items()if k in group};coeff={r:Q(1)}
  while outside:
   p=min(outside)
   if p not in pivots:
    q=1/outside[p];pivots[p]=[{k:v*q for k,v in row.items()}for row in(outside,inside,coeff)];break
   q=-outside[p]
   for target,source in zip((outside,inside,coeff),pivots[p]):add(target,source,q)
  if not outside:out.append((inside,coeff))
 return out

def encode(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {str(k):encode(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [encode(v)for v in x]
 return x

jobs=defaultdict(list);seen=set();planned=0;cap=500000
for cut,case in sorted(((cut,c)for cut,cc in cases.items()for c in cc),key=lambda x:(-x[1]['gain'],x[0],x[1]['frame_basis'])):
 roles=sorted(case['window_of'],key=lambda r:(r not in group,r))
 for size in range(2,min(4,len(roles))+1):
  if case['gain']<=sum(sorted(case['costs'].values())[:size]):continue
  for rr in itertools.combinations(roles,size):
   if not set(rr)&group or sum(case['costs'][r]for r in rr)>=case['gain']:continue
   jcut=max(windows[case['window_of'][r]]['lo']for r in rr)
   key=(tuple(case['frame_basis']),tuple(sorted(case['window_of'][r]for r in rr)))
   if key in seen:continue
   seen.add(key);jobs[jcut].append((case,rr));planned+=1
   if planned>=cap:break
  if planned>=cap:break
 if planned>=cap:break
print('selected_two_to_four_path_subsystems',planned,'cap',cap,flush=True)
rows=[{r:Q(1)}if r<n else{}for r in range(N)];saved=defaultdict(list);start=time.time()
for cut in range(len(w['program'])+1):
 if cut:
  e=w['program'][cut-1];op,r=e[:2]
  if op in('INIT','CLEAR'):rows[r]={}
  elif op=='SCALE':rows[r]={k:v*Q(e[2])for k,v in rows[r].items()}
  elif op in('ADD','COPY'):
   if op=='COPY':rows[r]={}
   add(rows[r],rows[e[2]],Q(e[3]))
 for case,roles in jobs.get(cut,[]):
  prefix=pure(rows,roles)
  if prefix:saved[cut].append((case,roles,prefix))
print('pure_prefix_subsystems',sum(map(len,saved.values())),'seconds',time.time()-start,flush=True)
cols=[{r:Q(1)}if r<n else{}for r in range(N)];hits=[];dominated=0;paired=0;nonzero_pair=0;alphabet_rejections=[];keys=set()
for cut in range(len(w['program']),-1,-1):
 for case,roles,prefix in saved.get(cut,[]):
  suffix=pure(cols,roles)
  for c,a in prefix:
   for rd,rb in suffix:
    pair=sum(v*rd.get(k,0)for k,v in c.items())
    if not pair:continue
    nonzero_pair+=1
    b={k:v/pair for k,v in rb.items()};d={k:v/pair for k,v in rd.items()}
    if sum(v*b.get(k,0)for k,v in a.items())!=1:continue
    paired+=1
    p=min(set(roles)&group,key=lambda p:len(basis(c,d,p,3))+len(basis(a,b,p,len(w['frames']))))
    used=set(a)|set(b)|{p};m=len(used);gain=case['gain']-sum(case['costs'][r]for r in used)
    if gain<=1e-12:continue
    paths=[dict(windows[case['window_of'][r]],frame=len(w['frames']),cost=case['costs'][r],new_paid=[abs(case['dimension']-dims[windows[case['window_of'][r]]['old']]),abs(dims[windows[case['window_of'][r]]['new']]-case['dimension'])])for r in sorted(used)]
    for h in paths:h.pop('lower');h.pop('upper')
    program=basis(c,d,p,3)+basis(a,b,p,len(w['frames']))
    legal=True
    for e in program:
     q=Q(e[-2]);aa,dd=abs(q.numerator),q.denominator
     if dd&(dd-1)or abs(q)+1>=2**16 or(e[0]=='SCALE'and aa&(aa-1)):legal=False
    if not legal:
     alphabet_rejections.append(dict(frame_basis=case['frame_basis'],cut=cut,roles=roles,a=a,b=b,c=c,d=d,paths=paths,program=program));continue
    best=-1e10;bestframe=None
    for fid,F in enumerate(spaces):
     k=dims[fid]
     if k in(0,9):continue
     if not all(spaces[windows[case['window_of'][r]]['lower']]<=F<=spaces[windows[case['window_of'][r]]['upper']]for r in used):continue
     paidcost=sum(abs(k-dims[h['old']])**t+abs(dims[h['new']]-k)**t-h['old_paid'][0]**t for h in paths)
     value=k**t+(9-k)**t-9**t-paidcost
     if value>best:best,bestframe=value,fid
    if best>=gain-1e-12:dominated+=1;continue
    key=(tuple(case['frame_basis']),p,tuple(sorted(a.items())),tuple(sorted(b.items())),tuple(sorted(c.items())),tuple(sorted(d.items())))
    if key in keys:continue
    keys.add(key);hits.append(dict(frame=len(w['frames']),new_frame_basis=case['frame_basis'],pivot=p,cut=cut,ranks=[case['dimension'],9-case['dimension']],gain=gain,paths=paths,a=a,b=b,c=c,d=d,best_old_frame=bestframe,best_old_frame_gain=best))
 if cut:
  e=w['program'][cut-1];op,r=e[:2]
  if op in('INIT','CLEAR'):cols[r]={}
  elif op=='SCALE':cols[r]={k:v*Q(e[2])for k,v in cols[r].items()}
  elif op in('ADD','COPY'):
   add(cols[e[2]],cols[r],Q(e[3]))
   if op=='COPY':cols[r]={}
(ROOT/'ALPHABET-REJECTIONS.json').write_text(json.dumps(encode(alphabet_rejections),sort_keys=True,indent=2)+'\n')
hits.sort(key=lambda h:-h['gain']);(ROOT/'HITS.json').write_text(json.dumps(encode(hits),sort_keys=True,indent=2)+'\n')
receipt=dict(source_payload_sha256=digest(w),coast_windows=len(windows),geometry_cap=2048,overlap_pairs=pairs,fresh_geometries=len(geometries),frame_cut_cases=casecount,subsystem_cap=cap,subsystems=planned,pure_prefix_subsystems=sum(map(len,saved.values())),paired=paired,nonzero_boundary_pairs=nonzero_pair,dominated_by_old_frame=dominated,nondominated_hits=len(hits),seconds=time.time()-start)
(ROOT/'SURVEY.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(json.dumps(receipt,sort_keys=True),flush=True)
for h in hits[:5]:print({k:v for k,v in encode(h).items()if k not in('a','b','c','d')},flush=True)

expected=read(Path(__file__).resolve().parents[1]/'SEARCH.json')['new_frame_screens']['mixed_ranks']
need({k:v for k,v in receipt.items()if k!='seconds'}==expected,'Reproduce the recorded finite search domain and outcome')
print('PASS_RECORDED_MIXED_RANKS_SCREEN')
