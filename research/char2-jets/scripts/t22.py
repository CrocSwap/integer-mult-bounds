import sys, json, time
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
from kit import *; from satlib import cost_leq
P,Q=json.load(open(PKG+'/data/jf0.json')); v=len(P); R,A,free=setup(P,Q)
for K in range(10, 20):
    t=time.time(); B=cost_leq(P,Q,K)
    print('jf0 cost<=%d: %s (%.0fs)'%(K,'SAT ranks %s'%blockranks(B,R,A) if B else 'UNSAT',time.time()-t), flush=True)
    if B: json.dump(B,open('jf0_min.json','w')); break
