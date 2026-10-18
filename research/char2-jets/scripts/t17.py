# adversarial-ish random search for no-wild configurations where a harmonic line cannot be moved at first order
import sys, random, collections
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
from kit import *; from phi import *; from tangent import tangent_cr2; from gen import prim, dot
seed=int(sys.argv[1]); random.seed(seed); st=collections.Counter(); bad=[]
def rv(r,E,supp):
    return prim([random.choice([1,-1])*r**random.randint(0,E) if j in supp else 0 for j in range(3)])
for it in range(int(sys.argv[2])):
    r=random.choice([2,3]); E=random.choice([0,1,2])
    pts=[rv(r,E,random.choice([{0,1,2},{0,1,2},{0,1},{0,2},{1,2}])) for _ in range(random.randint(3,7))]
    # candidate lines: through two pool points, harmonic partners, and random two-support lines
    from gen import cross
    lines=[]
    for _ in range(12):
        a,b=random.sample(pts,2); q=prim(cross(a,b))
        if q: lines.append(q)
    for p in pts:
        for k in range(3):
            i,j=[x for x in range(3) if x!=k]
            if p[i] and p[j]: q=[0,0,0]; q[i]=p[j]; q[j]=p[i]; lines.append(prim(q))
    lines=[q for q in lines if sum(1 for x in q if x)<=2 or random.random()<0.3]
    v=random.randint(5,12); P=[];Q=[]
    for _ in range(200):
        if len(P)>=v: break
        p=random.choice(pts); q=random.choice(lines)
        if dot(p,q)!=0: P.append(p); Q.append(q)
    if len(P)<4: continue
    w,H=classify(P,Q)
    if w or not H: st['skip']+=1; continue
    v=len(P); R,A,free=setup(P,Q)
    pi=[{j for j in range(3) if P[t][j]} for t in range(v)]; sig=[{j for j in range(3) if Q[t][j]} for t in range(v)]
    phi=make_phi(); Pt=[[phi(x) for x in p] for p in P]; Qt=[[phi(x) for x in q] for q in Q]
    res,dim=tangent_cr2(Pt,Qt,pi,sig,free,H); ok=all(res.values())
    st[('nowild with H', ok)]+=1
    if not ok: bad.append((P,Q,[t for t in H if not res[t]]))
print(seed, sorted(st.items(),key=str)); 
for b in bad[:3]: print(b)
