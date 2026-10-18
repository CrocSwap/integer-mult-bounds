import sys, os
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
from kit import *; from cr2 import *
for nm in sorted(os.listdir(PKG+'/data')):
    try: P,Q = load_cfg(nm)
    except Exception as e: continue
    if not (isinstance(P[0],list) and isinstance(P[0][0], int)): continue
    R,A,free = setup(P,Q); pi,sig = cfg_data(P,Q)
    res=[]
    for k in (1,2,3,4):
        r = realise(pi,sig,set(free),k=k,limit=3*10**5)
        res.append('R' if isinstance(r,dict) else ('-' if r is None else 'T'))
        if res[-1]=='R': break
    print(nm, len(P), len(free), res)
