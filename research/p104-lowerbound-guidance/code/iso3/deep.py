"""full identity-level check: climb with lmax = e_canon+1 (S_l and Toeplitz T_{l+1} up to the top level)."""
import sys,pickle
from syl import *
rows=pickle.load(open(sys.argv[1],'rb')); L=std_set('E7s'); Q=Q_std(L)
VW,VU,D,S,pr,s,c,e=setup(rows,Q)
r=climb(rows,Q,e+1,int(sys.argv[2]),1)
print(sys.argv[1],'e',e,'C',r['C'],'start',r['start'],'bestall',r['bestall'],flush=True)
