"""Fresh all-column scalar and actual/reflected rational-projector ledger audit.
Independent audit by OpenAI Codex against pinned PR473 exported records.
"""
import gzip,hashlib,json,sys
from collections import Counter
from pathlib import Path
import sympy as S
ROOT=Path(sys.argv[1]).resolve();OUT=Path(sys.argv[2]).resolve()
read=lambda p:json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
t=read(OUT/'hosted/GLOBAL-TEMPLATE.json.gz');fs=read(OUT/'native/records/frames.json')['frames'];state=read(OUT/'native/records/249-states.json');w=read(ROOT/'data/word.json')
n=240+w['R'];I=S.eye(8);P={};D={};hashes={}
for f,z in fs.items():
 B=S.Matrix(z['B']) if z['B'] else S.zeros(0,8)
 p=B.T*(B*B.T).inv()*B if B.rows else S.zeros(8)
 assert p==p.T and p*p==p and p.trace()==z['dim'];P[int(f)]=p;D[int(f)]=z['dim']
 for rev in (False,True):hashes[rev,int(f)]=hashlib.sha256(str(I-p if rev else p).encode()).hexdigest()
transition=set();results={}
for rev in (False,True):
 ori='reverse' if rev else 'forward';start='final' if rev else 'initial';end='initial' if rev else 'final'
 cur=[state[start][str(i)] for i in range(n)]+[-1];rows=[1<<i for i in range(n)]+[0];center=None;hist=Counter();ledger=hashlib.sha256();adds=copies=0
 for k,z in enumerate(t['local_programs'][ori]):
  op,x=z[:2]
  if op==0:
   _,x,old,new,r,rr=z;assert bool(rr)==rev and cur[x]==old
   key=(rev,old,new,r)
   if key not in transition:
    a=I-P[old] if rev else P[old];b=I-P[new] if rev else P[new];delta=b-a
    assert a*b==b*a==a and delta*delta==delta and delta.trace()==r
    transition.add(key)
   cur[x]=new;hist[r]+=bool(r)
  elif op==1:
   _,x,y,c,f,rr=z;assert bool(rr)==rev and cur[x]==cur[y]==f
   assert x!=y and x!=center and (y<n or center is not None)
   ledger.update(json.dumps([k,x,y,c,hashes[rev,f]],separators=(',',':')).encode()+b'\n')
   if c&1:rows[x]^=rows[y]
   adds+=1
  elif op==2:
   _,x,y,a,b,r,rr=z;assert bool(rr)==rev and y==n and center is None and cur[x]==a and rows[n]==0
   assert r==abs(D[a]-D[b])==8;center=x;cur[n]=b;rows[n]=rows[x];hist[r]+=1;copies+=1
  else:
   _,x,y,a,b,r,rr=z;assert bool(rr)==rev and op==3 and x==center and y==n and cur[x]==a and cur[n]==b
   assert rows[n]==rows[x];rows[n]=0;cur[n]=-1;center=None
 assert center is None and rows[n]==0 and cur[:n]==[state[end][str(i)] for i in range(n)]
 for i in range(n):assert rows[i]==(1<<i)^((1<<(i-120)) if 120<=i<240 else 0)
 results[ori]=dict(independent_input_columns=n,dirty_helpers=w['R'],instructions=len(t['local_programs'][ori]),common_actual_frame_adds=adds,copies=copies,all_helpers_restored=True,private_centre_erased=True,actual_projector_add_ledger_sha256=ledger.hexdigest(),paid_profile={str(r):v for r,v in hist.items() if v})
assert results['forward']['paid_profile']==results['reverse']['paid_profile']
out=dict(status='PASS_ALL_LOCAL_COLUMNS_AND_BOTH_ACTUAL_REFLECTED_FRAME_LEDGERS',source_frames=len(P),exact_oriented_transition_pairs=len(transition),orientations=results)
(OUT/'LOCAL-ACTUAL-LEDGERS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
