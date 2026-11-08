"""Independent opposite-direction full-contact and coefficient-nullspace audit.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The primary RESULT supplies only the cut census and expected dimensions/ranks.
No executable from the primary package is imported.
"""
from pathlib import Path
import json,gzip,collections,time,bisect,heapq,argparse,hashlib,itertools
from fractions import Fraction as Q
HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--emit',action='store_true');parser.add_argument('--package',type=Path)
args=parser.parse_args()
D=args.package or (HERE.parent if (HERE.parent/'verify.py').exists() else HERE.parent.parent/'worker-d/research/p104-two-channel-hub')
def need(condition,message):
 if not condition:raise ValueError(message)
PINS={'verify.py':'cba22ca6fa82e4476e95dee808408a46871640943c6edcaea3215ad111771d8b','RESULT.json':'08ca4c0f548d7d55e006781ca964a1ac9ea47503fc74bbee747771d8cb607753','inputs/WORD.json.gz':'aa7f815ad796141d0440f1078f4153af141d71a8316b98c0c7946eea7db29ba4'}
for name,h in PINS.items():need(hashlib.sha256((D/name).read_bytes()).hexdigest()==h,'Pinned input '+name)
started=time.time()
w=json.loads(gzip.decompress((D/'inputs/WORD.json.gz').read_bytes()));r=json.loads((D/'RESULT.json').read_text());events=w['program'];size=w['public']+w['owned_fields']
requested={row[0]for g in r['audit']['groups']for row in g['census']}
def span(b):
 s={0}
 for x in b:s|={v^x for v in tuple(s)}
 return s
frames=list(map(span,w['frames']));used={f for f,x in enumerate(frames)if 1<len(x)<max(map(len,frames))};inside={}
for i,e in enumerate(events):
 if e[0]=='MOVE':
  a,b=e[2:4];inside[i]=[f for f in used if frames[a]<frames[f]<frames[b]or frames[b]<frames[f]<frames[a]]
contacts=[collections.defaultdict(set),collections.defaultdict(set)];charts=w['initial']+[None]*w['owned_fields']
def record(side,f,t,role):
 if f in used:contacts[side][f].add((t,role))
for role,f in enumerate(w['initial']):record(0,f,0,role)
for i,e in enumerate(events):
 op,d=e[:2]
 if op=='MOVE':
  for f in inside[i]:record(0,f,2*i+1,d);record(1,f,2*i+1,d)
  charts[d]=e[3]
 elif op in('INIT','CLEAR'):charts[d]=e[2]if op=='INIT'else None
 record(0,charts[d],2*i+2,d)
 # Suffix contacts are before the operation, using actual before-event charts.
 if op=='MOVE':record(1,e[2],2*i,d)
 elif op=='INIT':pass
 elif op=='CLEAR':record(1,e[2],2*i,d)
 else:
  record(1,charts[d],2*i,d)
  if op in('ADD','COPY'):record(1,charts[e[2]],2*i,e[2])
for role,f in enumerate(w['final']):record(1,f,2*len(events),role)
pre=[[]for _ in range(size)];post=[[]for _ in range(size)];ops={}
for i,e in enumerate(events):
 op,d=e[:2]
 if op=='MOVE':continue
 s=e[2]if op in('ADD','COPY')else None;c=Q(e[-2])if op in('ADD','COPY','SCALE')else None
 ops[i]=(op,d,s,c);pre[d].append(i)
 if op in('SCALE','INIT','CLEAR','COPY'):post[d].append(i)
 if op in('ADD','COPY'):post[s].append(i)

def propagate(side,t,role):
 indexes=pre if side==0 else post;direction=-1 if side==0 else 1
 v={role:Q(1)};heap=[];version={};steps=0
 def setv(k,x):
  if x:v[k]=x
  else:v.pop(k,None)
 def schedule(k,bound):
  version[k]=version.get(k,0)+1
  if k not in v:return
  ix=indexes[k];p=bisect.bisect_left(ix,bound)-1 if side==0 else bisect.bisect_right(ix,bound)
  if 0<=p<len(ix):heapq.heappush(heap,(direction*ix[p],k,version[k]))
 # Odd time lies inside a MOVE, whose scalar action is identity.
 bound=t//2 if side==0 else t//2-1
 schedule(role,bound)
 while heap:
  signed,k,ver=heapq.heappop(heap);i=direction*signed
  if version.get(k)!=ver:continue
  op,d,s,c=ops[i];steps+=1
  if op in('INIT','CLEAR'):setv(d,0);changed=[d]
  elif op=='SCALE':setv(d,c*v.get(d,0));changed=[d]
  elif side==0:
   x=v.get(d,0)
   if op=='COPY':setv(d,0)
   setv(s,v.get(s,0)+c*x);changed=[d,s]
  else:
   x=c*v.get(s,0)
   setv(d,x if op=='COPY'else v.get(d,0)+x);changed=[d,s]
  for key in set(changed):schedule(key,i)
 return v,steps

def slow(side,t,role):
 v={role:Q(1)}
 def setv(k,x):
  if x:v[k]=x
  else:v.pop(k,None)
 indices=range(t//2-1,-1,-1)if side==0 else range(t//2,len(events))
 for i in indices:
  if i not in ops:continue
  op,d,s,c=ops[i]
  if op in('INIT','CLEAR'):setv(d,0)
  elif op=='SCALE':setv(d,c*v.get(d,0))
  elif side==0:
   x=v.get(d,0)
   if op=='COPY':setv(d,0)
   setv(s,v.get(s,0)+c*x)
  else:
   x=c*v.get(s,0);setv(d,x if op=='COPY'else v.get(d,0)+x)
 return v

cache=[{},{}];contact_hash=hashlib.sha256();prop_steps=0;slow_controls=0
for side in(0,1):
 keys=sorted({x for entries in contacts[side].values()for x in entries})
 selected={i*(len(keys)-1)//15 for i in range(16)}
 for at,(t,role)in enumerate(keys):
  vector,steps=propagate(side,t,role);cache[side][t,role]=vector;prop_steps+=steps
  need(all(0<=axis<size for axis in vector),'All physical input/output axes')
  if at in selected:need(vector==slow(side,t,role),'Dependency walk versus full chronological opposite propagation');slow_controls+=1
  contact_hash.update(json.dumps([side,t,role,[[k,str(v)]for k,v in sorted(vector.items())]],separators=(',',':')).encode()+b'\n')
 print(json.dumps({'phase':'contacts','side':side,'vectors':len(keys),'seconds':round(time.time()-started,3)}),flush=True)
contact_lists=[{},{}];times=[{},{}]
for side in(0,1):
 for f,entries in sorted(contacts[side].items()):
  contact_lists[side][f]=[(t,role,cache[side][t,role])for t,role in sorted(entries)if cache[side][t,role]]
  times[side][str(f)]=sorted({t for t,role,v in contact_lists[side][f]})
time_payload={'prefix':times[0],'suffix':times[1],'scope':'All nonzero contacts independently reconstructed on every nontrivial stored frame; time2 encoding. No independent cut-domain enumeration.'}
time_encoded=json.dumps(time_payload,sort_keys=True,indent=2)+'\n'
if args.emit:(HERE/'CONTACT-TIMES.json').write_text(time_encoded)
else:need((HERE/'CONTACT-TIMES.json').read_text()==time_encoded,'Read-only contact times receipt')

# This stage first spans the full 801-coordinate vectors in ordinary coordinate
# order, independent of helper group. Purity is imposed later by a nullspace of
# the transposed outside-coordinate matrix, whose variables are basis coefficients.
def insert(basis,original):
 v=dict(original)
 while v:
  k=min(v)
  if k not in basis:
   z=v[k];basis[k]={j:x/z for j,x in v.items()};return True
  z=v[k]
  for j,x in basis[k].items():
   y=v.get(j,0)-z*x
   if y:v[j]=y
   else:v.pop(j,None)
 return False

def full_basis(vectors):
 b={}
 for v in vectors:insert(b,v)
 return [b[k]for k in sorted(b)]

def nullspace(equations,width):
 # Dense forward elimination, then back-substitution for each free variable.
 a=[list(map(Q,row))for row in equations if any(row)];pivots=[];at=0
 for col in range(width):
  pivot=next((i for i in range(at,len(a))if a[i][col]),None)
  if pivot is None:continue
  a[at],a[pivot]=a[pivot],a[at];z=a[at][col]
  a[at]=[x/z for x in a[at]]
  for i in range(at+1,len(a)):
   z=a[i][col]
   if z:a[i]=[x-z*y for x,y in zip(a[i],a[at])]
  pivots.append(col);at+=1
  if at==len(a):break
 free=[i for i in range(width)if i not in pivots];answer=[]
 for j in free:
  v=[Q(0)]*width;v[j]=Q(1)
  for i,col in reversed(list(enumerate(pivots))):v[col]=-sum(a[i][k]*v[k]for k in range(col+1,width))
  answer.append(v)
 return answer

def pure(vectors,group):
 outside=sorted({j for v in vectors for j in v if j not in group})
 equations=[[v.get(j,0)for v in vectors]for j in outside]
 kernels=nullspace(equations,len(vectors));answer=[]
 for coefficients in kernels:
  row={}
  for c,v in zip(coefficients,vectors):
   if c:
    for j,x in v.items():row[j]=row.get(j,0)+c*x
  row={j:x for j,x in row.items()if x}
  need(row and set(row)<=group,'Nonzero pure direction with all dirty axes cancelled');answer.append(row)
 return answer

def dense_rank(matrix):
 if not matrix:return 0
 a=[list(map(Q,row))for row in matrix];at=0
 for col in range(len(a[0])):
  pivot=next((i for i in range(at,len(a))if a[i][col]),None)
  if pivot is None:continue
  a[at],a[pivot]=a[pivot],a[at];z=a[at][col];a[at]=[v/z for v in a[at]]
  for i in range(at+1,len(a)):
   z=a[i][col]
   if z:a[i]=[x-z*y for x,y in zip(a[i],a[at])]
  at+=1
  if at==len(a):break
 return at

fixtures=0;small=[v for v in itertools.product((-1,0,1),repeat=3)if any(v)]
for choice in itertools.combinations(small,3):
 vectors=[{j:Q(x)for j,x in enumerate(v)if x}for v in choice]
 b=full_basis(vectors);p=pure(b,{0,1});dim=dense_rank(choice)-dense_rank([[v[2]]for v in choice])
 need(len(p)==dim,'Nullspace purity dimension control')
 need(dense_rank(list(choice)+[[v.get(j,0)for j in range(3)]for v in p])==len(b),'Pure result belongs to original span')
 fixtures+=1
need(dense_rank([[1,0],[0,1]])==2,'Rank-two positive control')
need(len(pure(full_basis([{0:Q(1),2:Q(1)},{1:Q(1)}]),{0,1}))==1,'Dirty-axis contamination retained')
need(len(pure(full_basis([{0:Q(1),2:Q(1)},{2:Q(1)},{1:Q(1)}]),{0,1}))==2,'Exact dirty cancellation recovers direction')

cut_times=collections.defaultdict(set)
for group in r['audit']['groups']:
 for f,t,*_ in group['census']:cut_times[f].add(t)
basis_store={};views={}
for side in(0,1):
 for f,thresholds in sorted(cut_times.items()):
  entries=sorted(contact_lists[side].get(f,[]),key=lambda x:(x[0],x[1]),reverse=bool(side));at=0;b={};version=0
  basis_store[side,f,0]=[]
  for cut in sorted(thresholds,reverse=bool(side)):
   while at<len(entries)and(entries[at][0]<=cut if side==0 else entries[at][0]>=cut):
    if insert(b,entries[at][2]):
     version+=1;basis_store[side,f,version]=[b[k]for k in sorted(b)]
    at+=1
   views[side,f,cut]=(side,f,version)
print(json.dumps({'phase':'full_bases','versions':len(basis_store),'seconds':round(time.time()-started,3)}),flush=True)
main=set(w['live'])|{x+112 for x in w['live']};pure_cache={};hist=collections.Counter();census=[];groups_out=[]
for g in r['audit']['groups']:
 boundary=tuple(g['boundary']);eligible={role for role in range(w['public'])if role not in main and(w['initial'][role],w['final'][role])==boundary}
 need(len(eligible)==g['eligible_helpers'],'Independent boundary group labels')
 gh=collections.Counter()
 for f,cut,pivots,expected_c,expected_d,expected_rank in g['census']:
  sides=[]
  for side in(0,1):
   key=(boundary,views[side,f,cut])
   if key not in pure_cache:pure_cache[key]=pure(basis_store[key[1]],eligible)
   sides.append(pure_cache[key])
  collection,delivery=sides
  need((len(collection),len(delivery))==(expected_c,expected_d),'Independent pure dimensions at certified cut')
  gram=[[sum(value*col.get(axis,0)for axis,value in row.items())for col in delivery]for row in collection]
  rank=dense_rank(gram);need(rank==expected_rank and rank<=1,'Independent full Gram rank at certified cut')
  hist[rank]+=1;gh[rank]+=1;census.append([list(boundary),f,cut,len(collection),len(delivery),rank])
 groups_out.append({'boundary':list(boundary),'cuts':len(g['census']),'rank_histogram':dict(sorted(gh.items()))})
 print(json.dumps({'phase':'group','boundary':boundary,'cuts':len(g['census']),'seconds':round(time.time()-started,3)}),flush=True)
need(len(census)==4296 and hist=={0:4292,1:4},'Full certified cut count and ranks')
result={'status':'PASS_INDEPENDENT_FULL_HUB_REVIEW','input_sha256':PINS,'axes':size,'events':len(events),'certified_groups':len(groups_out),'certified_cuts':len(census),'rank_histogram':dict(sorted(hist.items())),'contact_vectors':[len(x)for x in cache],'nonzero_contact_records':[sum(len(x)for x in side.values())for side in contact_lists],'nontrivial_catalogue_frames':len(used),'opposite_scalar_updates':prop_steps,'contact_vectors_sha256':contact_hash.hexdigest(),'contact_times_sha256':hashlib.sha256(time_encoded.encode()).hexdigest(),'full_basis_versions':len(basis_store),'coefficient_nullspaces':len(pure_cache),'small_nullspace_fixtures':fixtures,'slow_opposite_controls':slow_controls,'groups':groups_out,'census':census,'limits':'The pinned primary RESULT supplies the certified cut domain and expected dimensions/ranks. No independent cut-domain enumeration is claimed here. Every required collection/delivery contact is independently reconstructed in the opposite direction on all 801 axes, and all 4296 pure-space pairing ranks are independently recomputed via coefficient nullspaces and dense rational Gaussian elimination. No primary trace/pure_basis/pairing_rank code is imported.'}
encoded=json.dumps(result,indent=2)+'\n'
if args.emit:(HERE/'REVIEW-RESULT.json').write_text(encoded)
else:need((HERE/'REVIEW-RESULT.json').read_text()==encoded,'Read-only complete independent review receipt')
print(json.dumps({k:v for k,v in result.items()if k not in('groups','census')},indent=2));print('elapsed_seconds',round(time.time()-started,3))
