# K9 (graphic) test controls for impl A's k9.py (cwd must contain lines.txt): A8 root subsystem of E8 must EMBED K9; E6 (roots orth. to an A2) must NOT.
import sys; sys.argv=['x']
import numpy as np, k9
L=k9.L
S=[(1,-1,-1,-1,-1,-1,-1,1),(2,2,0,0,0,0,0,0),(-2,2,0,0,0,0,0,0),(0,-2,2,0,0,0,0,0),(0,0,-2,2,0,0,0,0),(0,0,0,-2,2,0,0,0),(0,0,0,0,-2,2,0,0),(0,0,0,0,0,-2,2,0)]
S=np.array(S); coef=[2,3,4,6,5,4,3,2]
theta=sum(c*S[i] for c,i in zip(coef,range(8)))        # highest root (Bourbaki coefficients)
assert tuple(theta) in {tuple(v) for v in L} or tuple(-theta) in {tuple(v) for v in L}
chain=[S[0],S[2],S[3],S[4],S[5],S[6],S[7],-theta]       # extended Dynkin diagram minus node 2 = A8
roots={tuple(int(x) for x in v) for v in chain}
ch=True
while ch:
    ch=False
    for a in list(roots):
        for b in list(roots):
            d=sum(x*y for x,y in zip(a,b))//4
            w=tuple(x-d*y for x,y in zip(a,b))
            if w not in roots: roots.add(w); ch=True
lines=sorted({k9.pos[r] for r in roots})
print('A8 lines',len(lines),'(expect 36)')
a=np.array(L[0]); b=[np.array(w) for w in L if int(a@np.array(w))//4==-1][0]
e6=[t for t in range(120) if int(np.array(L[t])@a)==0 and int(np.array(L[t])@b)==0]
print('E6 lines',len(e6),'(expect 36)')
ra=k9.has_k9(tuple('r%d'%t for t in lines)); re_=k9.has_k9(tuple('r%d'%t for t in e6))
print('control A8 K9 embeds:',ra,'| control E6 K9 embeds:',re_)
print('CTL-OK' if (len(lines)==36 and len(e6)==36 and ra and not re_) else 'CTL-BAD')
