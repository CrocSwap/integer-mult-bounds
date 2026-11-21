"""ORBITLP dump.py: write aut perms, frames, port/frame orbit ids as plain text for C code."""
from geo import *
F=frames(); A=aut()
with open('geo.txt','w') as f:
    f.write(' '.join(map(str,LAB))+'\n')
    f.write('%d\n'%len(A))
    for p in A: f.write(' '.join(map(str,p))+'\n')
    f.write('%d\n'%len(F))
    fidx={fr:i for i,fr in enumerate(F)}
    # frame orbit ids
    fo=[-1]*len(F); k=0
    for i,fr in enumerate(F):
        if fo[i]>=0: continue
        for p in A: fo[fidx[tuple(sorted(p[list(fr)]))]]=k
        k+=1
    po=[-1]*n; k2=0
    for i in range(n):
        if po[i]>=0: continue
        for p in A: po[p[i]]=k2
        k2+=1
    for i,fr in enumerate(F): f.write(' '.join(map(str,fr))+' %d\n'%fo[i])
    f.write(' '.join(map(str,po))+'\n')
print('frame orbits',k,'port orbits',k2)
