"""Exact F2 suffix-response retarget screen on the R480 bit circuit.
Same-frame whole-gate retargeting and zero-response deletions; discovery only.
Prepared for rohanarun with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction as Q
import gzip,json,math,time,copy,hashlib
import sympy as S
R=Path(__file__).resolve().parent;O=R/'trace541-observable-slice';O.mkdir(exist_ok=False);t=time.monotonic();p=R/'trace541-rebuild/WORD.json.gz';w=json.load(gzip.open(p));v=w['v'];n=2*v+w['R'];Zregs=list(range(v))+list(range(2*v,n));mask=[sum(1<<i for i in f)for f in w['frames']];dims=[S.Matrix([w['lines'][i]for i in f]).rank()if f else 0 for f in w['frames']];le=lambda a,b:mask[a]&mask[b]==mask[a];full=next(i for i,d in enumerate(dims)if d==8);fee=lambda k:k*math.expm1(.001587447108*math.log(64/k))if k else 0
original=copy.deepcopy(w);moves=[];trials=Counter();best_negative=[]
def scalar(word):
 z=[1<<r for r in range(n)]
 for sec in ['D','A','B','C']:
  if sec=='B':
   held=[z[r]for r in word['ret']]
   for j,cs in enumerate(word['scatter']):
    for c in cs:z[v+j]^=held[c]
  for f,d,ss in word[sec]:
   for s in ss:z[d]^=z[s]
 assert all(z[r]==((1<<r)|(1<<(r-v))if v<=r<2*v else 1<<r)for r in range(n))
def profiles(word):
 cur=list(word['start']);h=Counter()
 def go(r,f):
  a=cur[r];assert le(a,f)
  if a!=f:h[int(dims[f]-dims[a])]+=1;cur[r]=f
 for sec in ['D','A','B','C']:
  if sec=='B':
   for r in word['ret']:go(r,full);h[8]+=1
  for f,d,ss in word[sec]:
   for r in [d]+ss:go(r,f)
 for r,f in enumerate(word['final']):go(r,f)
 return h
base=profiles(w);scalar(w)
# Delete all zero-target-response instructions together; individually neutral deletions
# may expose a frame transition only after the whole dead segment disappears.
resp=[0]*n
for j in range(v):resp[v+j]=1<<j
for f,d,ss in reversed(w['B']):
 for q in ss:resp[q]^=resp[d]
for j,cs in enumerate(w['scatter']):
 for c in cs:resp[w['ret'][c]]^=resp[v+j]
dead=[]
for i in reversed(range(len(w['A']))):
 f,d,ss=w['A'][i]
 if resp[d]==0:dead.append(i)
 for q in ss:resp[q]^=resp[d]
oldA=copy.deepcopy(w['A']);deadset=set(dead);w['A']=[g for i,g in enumerate(w['A'])if i not in deadset]
w['C']=[[full,d,list(ss)]for f,d,ss in reversed(w['A'])];scalar(w);sliced=profiles(w)
used=set(w['ret'])
for sec in ['D','A','B','C']:
 for f,d,ss in w[sec]:used.update([d]+ss)
unused=sorted(set(range(2*v,n))-used)
slice_record=dict(removed_indices=sorted(dead),removed_gates=[oldA[i]for i in sorted(dead)],old_profile=dict(base),sliced_profile=dict(sliced),unused_helpers=unused)
(O/'SLICE.json').write_text(json.dumps(slice_record,indent=2)+'\n');print('SIMULTANEOUS_SLICE',len(dead),dict(sliced),'unused',unused,flush=True)
for sweep in range(8):
 # Backward exact target response, including the center copy and scatter.
 resp=[0]*n
 for j in range(v):resp[v+j]=1<<j
 for f,d,ss in reversed(w['B']):
  for s in ss:resp[s]^=resp[d]
 for j,cs in enumerate(w['scatter']):
  for c in cs:resp[w['ret'][c]]^=resp[v+j]
 suffix=[None]*len(w['A'])
 for i in reversed(range(len(w['A']))):
  suffix[i]=resp[:];f,d,ss=w['A'][i]
  for s in ss:resp[s]^=resp[d]
 # Exact neighboring frame events before and after each candidate gate.
 prev=[];cur=list(w['start'])
 for f,d,ss in w['A']:
  prev.append(cur[:])
  for r in [d]+ss:assert le(cur[r],f);cur[r]=f
 nxt=list(w['final'])
 for f,d,ss in reversed(w['C']+[]):
  for r in [d]+ss:nxt[r]=f
 for f,d,ss in reversed(w['B']):
  for r in [d]+ss:nxt[r]=f
 for r in w['ret']:nxt[r]=full
 after=[None]*len(w['A'])
 for i in reversed(range(len(w['A']))):
  after[i]=nxt[:];f,d,ss=w['A'][i]
  for r in [d]+ss:nxt[r]=f
 proposals=[]
 for i,(f,d,ss)in enumerate(w['A']):
  H=suffix[i];a,b=prev[i],after[i]
  def removal(r):return fee(dims[b[r]]-dims[a[r]])-fee(dims[f]-dims[a[r]])-fee(dims[b[r]]-dims[f])
  if H[d]==0:
   trials['zero_response_gates']+=1;change=sum(removal(r)for r in [d]+ss)
   if change < -1e-12:proposals.append((change,i,None))
  for d2 in Zregs:
   if d2==d or d2 in ss or H[d2]!=H[d]:continue
   trials['response_equal']+=1
   if not (le(a[d2],f)and le(f,b[d2])):continue
   trials['frame_legal']+=1
   change=removal(d)+fee(dims[f]-dims[a[d2]])+fee(dims[b[d2]]-dims[f])-fee(dims[b[d2]]-dims[a[d2]])
   if change < -1e-12:proposals.append((change,i,d2))
 print('sweep',sweep,'trials',dict(trials),'profitable',len(proposals),flush=True)
 if not proposals:break
 change,i,d2=min(proposals,key=lambda x:(x[0],x[1],-1 if x[2]is None else x[2]));f,d,ss=w['A'][i];old=profiles(w)
 move=dict(sweep=sweep,index=i,frame=f,old_destination=d,new_destination=d2,sources=ss,fee_delta=change,target_response=str(suffix[i][d]))
 if d2 is None:del w['A'][i]
 else:w['A'][i][1]=d2
 w['C']=[[full,d,list(ss)]for f,d,ss in reversed(w['A'])];scalar(w);new=profiles(w);assert abs((sum(fee(r)*c for r,c in new.items())-sum(fee(r)*c for r,c in old.items()))-change)<1e-9
 move.update(old_profile=dict(old),new_profile=dict(new));moves.append(move)
(O/'WORD.json.gz').write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0))
res=dict(status='COMPLETE_SCOPED_OBSERVABLE_SLICE_AND_RETARGET_SCREEN',word_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),slice_record=slice_record,trials=dict(trials),moves=moves,baseline_profile=dict(base),final_profile=dict(profiles(w)),scalar_basis_columns=n,seconds=time.monotonic()-t,scope='Same-frame whole-gate destination changes in A when exact suffix target columns agree, plus target-zero whole-gate deletions. Greedy bounded search with float moment proxy; each accepted move has full scalar F2 and nested-frame checks. No emitted physical operator, finite prefix invoice, or new kappa claimed. Source/helper inverse cleanup regenerated exactly; D/B/scatter and live stock unchanged.')
(O/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print({k:v for k,v in res.items()if k!='slice_record'},flush=True)
