import sys
from pathlib import Path
import json,collections,time
import numpy as np
import sympy as S
p=Path(sys.argv[1]).resolve();F=json.loads((p/'input/frames.json').read_text())['frames'];D=json.loads((p/'baseline-candidates.json').read_text());pool=json.loads((p/'pair-pool.json').read_text()); G=S.eye(24)-S.ones(24)/9
donor_uses=collections.defaultdict(list)
for x in D:
 for b in x['partners']:donor_uses[b].append(x)
cache={};stats=collections.Counter();out=[]
def annih(B):
 return S.Matrix.hstack(*B.nullspace()).T if B.rank()<24 else S.zeros(0,24)
def sub(U,V):
 return S.Matrix.vstack(U,V).rank()==V.rows
def inter_frames(fa,fb):
 k=tuple(sorted([fa,fb]))
 if k not in cache:
  A=F[str(fa)]['A']+F[str(fb)]['A']
  if np.linalg.matrix_rank(np.array(A,dtype=float),tol=1e-9)==24:cache[k]=None
  else:
   ns=S.Matrix(A).nullspace();cache[k]=S.Matrix.hstack(*ns).T if ns else None
 return cache[k]
seen=set()
for z in pool:
 c,a,b=z['cut'],z['pivot'],z['donor'];key=(c,a,b)
 if key in seen:continue
 seen.add(key);E=inter_frames(z['pivot_meta']['frame'],z['donor_meta']['frame'])
 if E is None:stats['zero_intersection']+=1;continue
 # Make the new donor entrance compatible with every later old entrance.
 later=[S.Matrix(q['basis']) for q in donor_uses[b] if q['cut']>c]
 earlier=[S.Matrix(q['basis']) for q in donor_uses[b] if q['cut']<c]
 same=[S.Matrix(q['basis']) for q in donor_uses[b] if q['cut']==c]
 for U in later:
  ns=S.Matrix.vstack(annih(E),annih(U)).nullspace();E=S.Matrix.hstack(*ns).T if ns else S.zeros(0,24)
 if not E.rows:stats['zero_compatibility']+=1;continue
 for U in same:
  if not sub(E,U) and not sub(U,E):
   ns=S.Matrix.vstack(annih(E),annih(U)).nullspace();E=S.Matrix.hstack(*ns).T if ns else S.zeros(0,24)
 if not E.rows or any(not sub(U,E) for U in earlier):stats['earlier_incompatible']+=1;continue
 H=E*G*E.T
 if H.det()==0:
  kept=None
  for drop in range(E.rows):
   C=E[[i for i in range(E.rows) if i!=drop],:]
   if C.rows and (C*G*C.T).det()!=0 and all(sub(U,C) for U in earlier) and all(sub(C,U) or sub(U,C) for U in same):kept=C;break
  if kept is None:stats['degenerate']+=1;continue
  E=kept
 # Clear denominators rowwise for stable integer vectors.
 B=[]
 for i in range(E.rows):
  l=S.ilcm(*[t.q for t in E.row(i)])
  B.append([str(t*l) for t in E.row(i)])
 item=dict(roles=[a,b],pivot=a,a=a,partners=[b],dim=E.rows,E_dimension=E.rows,basis=B,cut=c,kind=z['kind'])
 out.append(item);stats['admitted_'+z['kind']]+=1
print('stats',dict(stats));print('admitted by dim',dict(collections.Counter(x['dim'] for x in out)));print('reuse candidates',[(x['a'],x['partners'],x['dim'],x['cut']) for x in out if x['kind']=='reuse'][:40])
(p/'geometric-pairs.json').write_text(json.dumps(out,indent=2))
