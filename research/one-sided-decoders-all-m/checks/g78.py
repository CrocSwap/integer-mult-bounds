# exact g(8) and g(7): maximum number of P112 lines in a label flat of dimension 8 (one hyperplane of F2^9) and 7 (two hyperplanes).
# A label flat of dim d = the lines whose label lies in a d-dim subspace; every subspace of dim 7/8 is an intersection of 2/1 hyperplanes.
from base import *
par=lambda x: bin(x).count('1')&1
mask={z:sum(1<<t for t in range(v) if not par(z&LAB[t])) for z in range(1,512)}
pc=lambda m: bin(m).count('1')
g8=max(pc(m) for m in mask.values())
sizes={}
n7=0
for a in range(1,512):
    for b in range(a+1,512):
        if a^b<b: continue          # each 2-dim subspace {0,a,b,a^b} once (a<b<a^b)
        n7+=1; k=pc(mask[a]&mask[b]); sizes[k]=sizes.get(k,0)+1
g7=max(sizes)
print('hyperplane (dim 8) flats: 511, max lines g(8) =',g8)
print('dim-7 flats:',n7,'max lines g(7) =',g7,'; number of 7-flats with g(7) lines:',sizes[g7])
assert n7==43435 and g8==64 and g7==36
print('g78 OK')
