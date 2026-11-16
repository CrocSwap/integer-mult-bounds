from lib import *
print(n,len(P),len(fidx))
print('frame orthogonal', all(ip(lines[a],lines[b])==0 for a in fidx for b in fidx if a<b))
print('z rank', f2rank([lab[i] for i in fidx]), 'P112 rank',f2rank([lab[i] for i in P]))
# AG(3,2) check: sums over Hamming 4-sets
import itertools
zs=[lab[i] for i in fidx]
c=0
for S4 in itertools.combinations(range(8),4):
    x=0
    for i in S4: x^=zs[i]
    if x==0: c+=1
print('4-sets summing to 0:',c)
# Off sizes of root directions on P112
offs=sorted(sum(1 for t in P if ip(lines[r],lines[t])!=0) for r in range(n))
from collections import Counter
print(Counter(offs))
# max lines in 7-dim and 8-dim label subspaces on P112
