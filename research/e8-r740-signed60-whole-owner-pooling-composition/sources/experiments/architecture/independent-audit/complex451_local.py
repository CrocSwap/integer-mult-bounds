from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import gzip,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[2];S=R/'experiments/architecture/complex-direct8-eleven451/split-centres';w=json.loads(gzip.decompress((S/'FULL-WORD.json.gz').read_bytes()));p=json.load(gzip.open(S/'SIGNED-PROGRAM.json.gz','rt'));n=240+w['report']['R'];assert n==800
# Sparse elementary matrix evaluation independent of producer clean discovery.
def run(word,initial=None):
 A=[{i:Q(1)} for i in range(n)] if initial is None else [dict(row) for row in initial];peak=1
 for e in word:
  if e[0]=='add':
   _,t,s,a,b,*_=e;c=Q(a,b)
   for k,v in list(A[s].items()):
    A[t][k]=A[t].get(k,0)+c*v
    if not A[t][k]:del A[t][k]
  else:
   _,t,a,b,*_=e;A[t]={k:Q(a,b)*v for k,v in A[t].items()}
  peak=max(peak,sum(map(abs,A[e[1]].values())))
 return A,peak
def inv(e):
 x=e[:]
 if x[0]=='add':x[3]=-x[3]
 else:x[2],x[3]=x[3],x[2]
 return x
A,peak=run(p['program']);expected=[{i:Q(1)} for i in range(n)]
for i in range(120):expected[120+i][i]=1
assert A==expected
back,backpeak=run([inv(e) for e in reversed(p['program'])],A);assert back==[{i:Q(1)} for i in range(n)]
inverse_matrix,inverse_prefix=run([inv(e) for e in reversed(p['program'])]);negative=[{i:Q(1)} for i in range(n)]
for i in range(120):negative[120+i][i]=-1
assert inverse_matrix==negative
# Derive dirt by transposed elementary propagation, not producer forward K rows.
main=w['A']+w['cut']+w['B']+w['cleanup'];actualD={(e[1],e[2]):Q(e[3],e[4]) for e in p['D']}
for t in range(120):
 cov={120+t:Q(1)}
 for e in reversed(main):
  if e[0]=='add':
   _,dst,src,a,b,*_=e;cov[src]=cov.get(src,0)+cov.get(dst,0)*Q(a,b)
  else:_,dst,a,b,*_=e;cov[dst]=cov.get(dst,0)*Q(a,b)
 for h in range(240,n):assert actualD.get((120+t,h),0)==-cov.get(h,0)
# Independent GF2 rowspace normalization/common-frame containment ledger.
def span(vs):
 b={}
 for x in vs:
  while x:
   j=x.bit_length()-1
   if j in b:x^=b[j]
   else:b[j]=x;break
 return b

def inside(vs,ws):
 b=span(ws)
 for x in vs:
  while x:
   j=x.bit_length()-1
   if j not in b:return False
   x^=b[j]
 return True
full=[1<<i for i in range(9)];cur=[[port] for port in w['ports']]+[[] for _ in range(n-120)];H=Counter()
def climb(r,F):
 assert inside(cur[r],F);delta=len(span(F))-len(span(cur[r]));assert delta>=0
 if delta:H[delta]+=1
 cur[r]=list(F)
def phase(events):
 for e in events:
  F=e[-1];assert F is not None
  climb(e[1],F)
  if e[0]=='add':climb(e[2],F)
phase(w['A']);assert [cur[i] for i in w['centers']]==w['center_frames']
for F in w['center_frames']:H[len(span(F))]+=1
phase(w['B'])
for r in range(n):
 cap=span([x for x in range(1,512) if (x&w['ports'][r-120]).bit_count()%2==0]) if 120<=r<240 else span(full)
 climb(r,list(cap.values()))
phase(w['cleanup']);assert dict(H)=={int(k):v for k,v in w['report']['local_profile'].items()}
fees=sum(abs(Q(e[3],e[4])) for e in p['D']);out={'status':'PASS_INDEPENDENT_OWN433_DIRECT_CENTRE_ALL800_COLUMNS_DIRT_INVERSE_AND_FRAME_PROFILE','registers':n,'forward_actual_row_prefix':str(peak),'inverse_from_endpoint_actual_prefix':str(backpeak),'literal_inverse_actual_row_prefix':str(inverse_prefix),'compensation_absolute_coefficients':str(fees),'local_profile':dict(H),'rank_mass':sum(k*v for k,v in H.items()),'source_word_sha256':hashlib.sha256(gzip.decompress((S/'FULL-WORD.json.gz').read_bytes())).hexdigest(),'scope':'Exact scalar dirty matrix,120independent adjoint K compensators,implicit monotoneGF2frame climbs and retained centre-copy rank. Cut copy/address phases and scalar/dyadic compiler lowered prefix/invoice require full actual supplier emission and separate gate.'}
(P/'COMPLEX451-LOCAL.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
