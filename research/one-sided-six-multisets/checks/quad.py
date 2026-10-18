# search: 4 E8 lines, pairwise non-orthogonal, labels summing to 0 (sum of roots in 2E8), roots linearly independent
import itertools, numpy as np
exec(open('gen.py').read().split('# directions:')[0])
L=lines  # 120 E8 lines (doubled coords)
lab120=[lab(r) for r in L]
cnt=0; ex=[]
idx=range(120)
nb={i:[j for j in idx if dot(L[i],L[j])!=0 and j!=i] for i in idx}
for a in idx:
  for b in nb[a]:
    if b<=a: continue
    for c in nb[a]:
      if c<=b or c not in nb[b]: continue
      for d in nb[a]:
        if d<=c or d not in nb[b] or d not in nb[c]: continue
        if lab120[a]^lab120[b]^lab120[c]^lab120[d]: continue
        M=np.array([L[a],L[b],L[c],L[d]],dtype=float)
        if np.linalg.matrix_rank(M)<4: continue
        cnt+=1
        if len(ex)<3: ex.append((a,b,c,d))
print('quadruples (pairwise nonorth, label sum 0, rank 4):',cnt)
for q in ex: print([L[i] for i in q])
