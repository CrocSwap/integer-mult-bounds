"""Independent bounded review of D's chronology/pure-span implementation."""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util,itertools,gzip,json,hashlib,sys
HERE=Path(__file__).resolve().parent
D=HERE.parent
REVIEWED_SHA256='cba22ca6fa82e4476e95dee808408a46871640943c6edcaea3215ad111771d8b'
if hashlib.sha256((D/'verify.py').read_bytes()).hexdigest()!=REVIEWED_SHA256:
 raise ValueError('Reviewed verifier bytes changed; independent review must be renewed')
spec=importlib.util.spec_from_file_location('reviewed',D/'verify.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def need(c,s):
 if not c:raise ValueError(s)

def rank(rows):
 a=[[Q(x)for x in row]for row in rows];at=0
 if not a:return 0
 for j in range(len(a[0])):
  p=next((i for i in range(at,len(a))if a[i][j]),None)
  if p is None:continue
  a[at],a[p]=a[p],a[at];z=a[at][j];a[at]=[v/z for v in a[at]]
  for i in range(at+1,len(a)):
   z=a[i][j]
   if z:a[i]=[u-z*v for u,v in zip(a[i],a[at])]
  at+=1
  if at==len(a):break
 return at

fixtures=0
vectors=[v for v in itertools.product((-1,0,1),repeat=3)if any(v)]
for indices in itertools.combinations(range(len(vectors)),3):
 rows=[vectors[i]for i in indices]
 sparse=[{i:Q(x)for i,x in enumerate(row)if x}for row in rows]
 pure=m.pure_basis(sparse,{0,1});p=[[r.get(i,0)for i in range(3)]for r in pure]
 expected=rank(rows)-rank([[row[2]]for row in rows])
 need(len(pure)==expected==rank(p),'independent pure-space dimension')
 need(all(not row[2]for row in p),'pure supports')
 need(rank(rows+p)==rank(rows),'returned pure rows belong to original span')
 fixtures+=1

raw=gzip.decompress((D/'inputs/WORD.json.gz').read_bytes());word=json.loads(raw)
canonical=json.dumps(word,sort_keys=True,separators=(',',':')).encode()
need(hashlib.sha256(canonical).hexdigest()==m.PAYLOAD,'native payload')
trace=m.trace(word);contacts,intervals,group,_,_=trace
operations=[]
for e in word['program']:
 op,r=e[:2]
 operations.append((op,r,e[2]if op in('ADD','COPY')else None,Q(e[-2])if op in('ADD','COPY','SCALE')else None))

def put(v,k,x):
 if x:v[k]=x
 else:v.pop(k,None)

def prefix_adjoint(time,role):
 v={role:Q(1)}
 for op,r,s,c in reversed(operations[:time//2]):
  if op in('INIT','CLEAR'):v.pop(r,None)
  elif op=='SCALE':put(v,r,v.get(r,0)*c)
  elif op in('ADD','COPY'):
   x=v.get(r,0)
   if op=='COPY':v.pop(r,None)
   if x:put(v,s,v.get(s,0)+c*x)
 return v

def suffix_forward(time,role):
 v={role:Q(1)}
 for op,r,s,c in operations[time//2:]:
  if op in('INIT','CLEAR'):v.pop(r,None)
  elif op=='SCALE':put(v,r,v.get(r,0)*c)
  elif op in('ADD','COPY'):
   x=c*v.get(s,0)
   put(v,r,x if op=='COPY'else v.get(r,0)+x)
 return v

sample_counts=[]
for side,fn in ((0,prefix_adjoint),(1,suffix_forward)):
 flat=sorted((time,role,frame,vector)for frame,items in contacts[side].items()for time,role,vector in items)
 # Time quantiles plus all opcode-adjacent contact kinds and owned contacts.
 chosen={0,len(flat)-1}|{i*(len(flat)-1)//31 for i in range(32)}
 for parity in (0,1):
  k=next((i for i,v in enumerate(flat)if v[0]%2==parity and v[1]>=word['public']),None)
  if k is not None:chosen.add(k)
 for i in sorted(chosen):
  t,r,f,vector=flat[i];need(fn(t,r)==vector,'independent all-column contact reconstruction')
 sample_counts.append(len(chosen))

receipt=json.loads((D/'RESULT.json').read_text())
groups=receipt['audit']['groups'];witnesses=[]
for result in groups:
 w=result['first_rank_one']
 if w:
  gram=[[Q(x)for x in row]for row in w['gram']]
  need(rank(gram)==1,'independent witness Gram rank')
  collection=[{int(k):Q(v)for k,v in row.items()}for row in w['collection']]
  delivery=[{int(k):Q(v)for k,v in col.items()}for col in w['delivery']]
  rebuilt=[[sum(v*col.get(k,0)for k,v in row.items())for col in delivery]for row in collection]
  need(rebuilt==gram,'direct witness bilinear pairing')
  witnesses.append({'boundary':result['boundary'],'frame':w['frame'],'time2':w['time2'],'gram_rank':1,'rows':len(gram),'columns':len(gram[0])})
result={'status':'PASS_INDEPENDENT_HUB_REVIEW','reviewed_verifier_sha256':hashlib.sha256((D/'verify.py').read_bytes()).hexdigest(),'receipt_sha256':hashlib.sha256((D/'RESULT.json').read_bytes()).hexdigest(),'payload_sha256':m.PAYLOAD,'pure_intersection_fixtures':fixtures,'contact_reconstructions':sample_counts,'bilinear_witnesses':witnesses,'limits':'No independent full 4296-cut rerun here; direct time-quantile samples, all-column algebra review, exhaustive small pure-space cases and exact retained Gram witness.'}
encoded=json.dumps(result,indent=2)+'\n'
if '--emit' in sys.argv:(HERE/'REVIEW-RESULT.json').write_text(encoded)
else:need((HERE/'REVIEW-RESULT.json').read_text()==encoded,'Exact independent review receipt')
print(json.dumps(result,indent=2))
