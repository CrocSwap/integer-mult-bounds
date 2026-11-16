# frames (8 mutually orthogonal E8 lines) up to the pointwise stabiliser W(A3^perp)=W(D5) of the A3 chain of gen.py (P=4); writes frame reps as masks
import itertools,sys
src=open('gen.py').read(); src=src[:src.index("ms=set()")]; sys.argv=['x','4']; exec(src)
ch=[R[0]]
while len(ch)<3: ch.append(next(r for r in R if ip(r,ch[-1])==-1 and all(ip(r,c)==0 for c in ch[:-1])))
n=120; orth=[[ip(L[a],L[b])==0 for b in range(n)] for a in range(n)]
fr=set()
def ext(c,cand):
  if len(c)==8: fr.add(frozenset(c)); return
  for i in cand:
    if i>c[-1]: ext(c+[i],[j for j in cand if j>i and orth[i][j]])
for a in range(n): ext([a],[j for j in range(n) if j>a and orth[a][j]])
fr=list(fr); print('frames',len(fr),file=sys.stderr)
gens=[r for r in L if all(ip(r,b)==0 for b in ch)]
def refl(r,v): k=ip(v,r); return canon(tuple(x-k*y for x,y in zip(v,r)))
perm=[[idx[refl(r,L[t])] for t in range(n)] for r in gens]
seen={}; reps=[]
for f in fr:
  if f in seen: continue
  orb={f}; st=[f]
  while st:
    g=st.pop()
    for p in perm:
      h=frozenset(p[t] for t in g)
      if h not in orb: orb.add(h); st.append(h)
  for g in orb: seen[g]=1
  reps.append((sorted(f),len(orb)))
print('D5 generators',len(gens),'orbits',len(reps),[o for _,o in reps],file=sys.stderr)
with open('frames_rep.txt','w') as F:
  for f,o in reps:
    m=sum(1<<t for t in f); F.write('%d %d %d\n'%(m&((1<<64)-1),m>>64,o))
