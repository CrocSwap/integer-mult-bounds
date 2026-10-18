import sys, random, collections
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
from kit import *; from satlib import enumerate_B; from cr2 import cfg_data; from col import col_split
P,Q=load_cfg('tied_min.json'); R,A,free=setup(P,Q); pi,sig=cfg_data(P,Q); D=[pi[t]&sig[t] for t in range(12)]
c=collections.Counter()
for ent in enumerate_B(P,Q,(4,4,4)):
    B=[[int(t==s) for s in range(12)] for t in range(12)]
    for t,s in ent: B[t][s]=1
    ch=col_split(B,D); c[('opt', ch is not None, len(ent))]+=1
random.seed(2)
for _ in range(200):
    g=random.getrandbits(72); B=tomat(g,free,12); c[('rand', col_split(B,D) is not None)]+=1
B=tomat((1<<72)-1,free,12); c[('full', col_split(B,D) is not None)]+=1
print(sorted(c.items(), key=str))
