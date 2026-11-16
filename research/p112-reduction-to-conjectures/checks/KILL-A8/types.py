# non-root h types (maximal parabolic perp = E8 minus node i, i=1..7: D7,A7,A1A6,A1A2A4,A4A3,D5A2,E6A1) : Off(h), frame orbits under W(perp h)
import itertools,sys
from fractions import Fraction as Fr
src=open('gen.py').read(); src=src[:src.index("ms=set()")]; sys.argv=['x','4']; exec(src)
al=[(1,-1,-1,-1,-1,-1,-1,1),(2,2,0,0,0,0,0,0),(-2,2,0,0,0,0,0,0),(0,-2,2,0,0,0,0,0),(0,0,-2,2,0,0,0,0),(0,0,0,-2,2,0,0,0),(0,0,0,0,-2,2,0,0),(0,0,0,0,0,-2,2,0)]
G=[[Fr(ip(a,b)) for b in al] for a in al]
def solve(rhs):  # coefficients x with sum_j x_j <al_i,al_j> = rhs_i
  M=[G[i][:]+[Fr(rhs[i])] for i in range(8)]
  for c in range(8):
    p=next(r for r in range(c,8) if M[r][c]!=0); M[c],M[p]=M[p],M[c]; M[c]=[x/M[c][c] for x in M[c]]
    for r in range(8):
      if r!=c and M[r][c]!=0: M[r]=[x-M[r][c]*y for x,y in zip(M[r],M[c])]
  return [M[i][8] for i in range(8)]
n=120; orth=[[ip(L[a],L[b])==0 for b in range(n)] for a in range(n)]
fr=set()
def ext(c,cand):
  if len(c)==8: fr.add(frozenset(c)); return
  for i in cand: ext(c+[i],[j for j in cand if j>i and orth[i][j]])
for a in range(n): ext([a],[j for j in range(n) if j>a and orth[a][j]])
assert len(fr)==2025
d4=open('dat_4.txt').read().split('\n'); masks=d4[2+6:]
names=['D7','A7','A1A6','A1A2A4','A4A3','D5A2','E6A1','E7(root)']
for i in range(8):
  x=solve([1 if j==i else 0 for j in range(8)]); h=[sum(x[j]*al[j][k] for j in range(8)) for k in range(8)]
  hp=lambda t: sum(a*b for a,b in zip(L[t],h))
  perp=[t for t in range(n) if hp(t)==0]; off=sum(1<<t for t in range(n) if hp(t)!=0)
  def refl(r,v): k=ip(v,r); return canon(tuple(a-k*b for a,b in zip(v,r)))
  perm=[[idx[refl(L[r],L[t])] for t in range(n)] for r in perp]
  seen=set(); reps=[]
  for f in fr:
    if f in seen: continue
    orb={f}; st=[f]
    while st:
      g=st.pop()
      for p in perm:
        hh=frozenset(p[t] for t in g)
        if hh not in orb: orb.add(hh); st.append(hh)
    seen|=orb; reps.append(sorted(f))
  print(i+1,names[i],'|perp lines|',len(perp),'|Off|',bin(off).count('1'),'frame orbits',len(reps))
  with open('dat_h%d.txt'%(i+1),'w') as F:
    F.write('2 %s\n'%d4[0].split()[1]); F.write(d4[1]+'\n'); F.write('%d %d\n'%(off&((1<<64)-1),off>>64)); F.write('\n'.join(masks))
  with open('fr_h%d.txt'%(i+1),'w') as F:
    for f in reps: m=sum(1<<t for t in f); F.write('%d %d 0\n'%(m&((1<<64)-1),m>>64))
