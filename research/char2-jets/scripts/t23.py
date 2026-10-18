# B-dependent first-order jet test (E = supp B) on all minimisers of jf1, jf2
import sys, json, collections
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
import kit; kit.BIN=os.environ.get('TTD_BIN') or PKG+'/c/bin'
from kit import *; from phi import *; from tangent import tangent_cr2; from cr2 import realise
for i in (1,2):
    P,Q=json.load(open(PKG+'/data/jf%d.json'%i)); v=len(P); R,A,free=setup(P,Q); w,H=classify(P,Q)
    pi=[{j for j in range(3) if P[t][j]} for t in range(v)]; sig=[{j for j in range(3) if Q[t][j]} for t in range(v)]
    Pt=[[1 if x else 0 for x in p] for p in P]; Qt=[[1 if x else 0 for x in q] for q in Q]
    best,ms=enum_raw(v,R,A,free,0); c=collections.Counter()
    for _,g in ms:
        E=[free[k] for k in range(len(free)) if g>>k&1]
        res,_=tangent_cr2(Pt,Qt,pi,sig,E,H); cr=isinstance(realise(pi,sig,set(E),k=1),dict) or isinstance(realise(pi,sig,set(E),k=2),dict)
        c[('jet1',all(res.values()),'CR2',cr)]+=1
    print('jf%d min cost %d, %d minimisers:'%(i,best,len(ms)), dict(c))
