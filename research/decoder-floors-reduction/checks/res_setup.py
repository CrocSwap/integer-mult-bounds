import json, numpy as np, sys
from collections import Counter
D=json.load(open('data.json')); L=np.array(D['L']); LAB=D['LAB']; F0=np.array(D['F0']); v=112
par=lambda x: bin(x).count('1')&1
Om=lambda a,b: par(a&b)
Lam={z:[s for s in range(v) if not par(z&LAB[s])] for z in range(1,512)}   # lines with Omega(u_s,z)=0
O={z:[s for s in range(v) if par(z&LAB[s])] for z in range(1,512)}
# frame classes z_i: O_z = lines non-orthogonal... find z with Lam_z = lines orthogonal to f_i? (cat1: O_phi = lines orthogonal to f_i)
framez={}
for i,f in enumerate(F0):
    S=set(s for s in range(v) if abs(L[s]@f)<1e-9)
    m=[z for z in range(1,512) if set(O[z])==S]
    framez[i]=m
if __name__=='__main__':
    print(np.abs(L*2-np.round(L*2)).max(), framez)
    print(Counter(len(Lam[z]) for z in Lam))
    rk=Counter()
    for z in range(1,512):
        r=np.linalg.matrix_rank(L[O[z]]); rk[(len(Lam[z]),r)]+=1
    print(rk)
