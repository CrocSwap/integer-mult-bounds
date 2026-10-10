"""Independent modular determinant audit with exact Hadamard lifting.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import hashlib,json,math,time
from pathlib import Path
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--proof',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
beg=time.monotonic();base=args.proof.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
raw=(base/'candidate/frames.json').read_bytes();frames=json.loads(raw)['frames'];proof=json.loads((base/'FRAME-PRIMES.json').read_text());assert hashlib.sha256(raw).hexdigest()==proof['input_sha256']
Q=2**127-1
ll=4
for _ in range(125):ll=(ll*ll-2)%Q
assert ll==0 and all(127%d for d in range(2,12))
def det_mod(M):
 n=len(M);A=[[x%Q for x in r]for r in M];d=1
 for i in range(n):
  j=next((j for j in range(i,n)if A[j][i]),None)
  if j is None:return 0
  if j!=i:A[j],A[i]=A[i],A[j];d=-d
  pivot=A[i][i];d=d*pivot%Q;iv=pow(pivot,-1,Q)
  for j in range(i+1,n):
   if not A[j][i]:continue
   z=A[j][i]*iv%Q
   for k in range(i+1,n):A[j][k]=(A[j][k]-z*A[i][k])%Q
   A[j][i]=0
 return d%Q
cache={};seen=set();max_bound=0;max_d=0
for r in proof['witnesses']:
 f=str(r['frame']);kind=r['kind'];key=(f,kind);assert key not in seen;seen.add(key)
 B=frames[f][kind];c=r['columns'];d=int(r['determinant']);assert len(c)==len(B)==r['row_rank'] and len(set(c))==len(c) and all(0<=k<20 for k in c)
 M=tuple(tuple(row[k]for k in c)for row in B)
 bound=math.prod(sum(x*x for x in row)for row in M);assert 4*bound<Q*Q
 assert 0<abs(d)<2**80<Q//2
 if M not in cache:cache[M]=det_mod(M)
 assert cache[M]==d%Q,(key,d,cache[M])
 max_bound=max(max_bound,bound);max_d=max(max_d,abs(d))
assert seen=={(f,k)for f in frames for k in ('A','B')}
assert max_d==int(proof['max_abs_minor'])
assert det_mod(((1,2),(2,4)))==0 and det_mod(((0,1),(2,3)))==Q-2
r=dict(status='PASS_INDEPENDENT_MODULAR_DETERMINANTS_WITH_EXACT_HADAMARD_LIFT',frames=len(frames),witnesses=len(seen),distinct_minor_matrices=len(cache),prime=Q,max_abs_determinant=max_d,max_squared_hadamard_bound=str(max_bound),input_sha256=hashlib.sha256(raw).hexdigest(),witness_sha256=hashlib.sha256((base/'FRAME-PRIMES.json').read_bytes()).hexdigest(),seconds=time.monotonic()-beg,proof='Hadamard gives abs(actual determinant)<Q/2; reported determinant also has abs<Q/2. Equality modulo certified prime Q therefore proves exact integer equality. Every nonzero reported determinant has magnitude below2^80, so all frame bases and annihilators remain full row rank for every prime above2^80.')
(out/'MINOR-AUDIT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
