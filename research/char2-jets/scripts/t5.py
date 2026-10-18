import sys, json, collections
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
import kit; kit.BIN=os.environ.get('TTD_BIN') or PKG+'/c/bin'
from kit import *; from cr2 import *
P0,Q0 = load_cfg('tied_min.json')
non = json.load(open(PKG+'/data/tm_noncr2.json'))
stat=collections.Counter(); bad=[]
for S in non:
    P=[P0[i] for i in S]; Q=[Q0[i] for i in S]; R,A,free=setup(P,Q)
    if len(free)>26: stat[(len(S),'skip f=%d'%len(free))]+=1; continue
    pi,sig=cfg_data(P,Q); best,ms=enum_raw(len(S),R,A,free,0)
    ncr=0
    for c,g in ms:
        E=[free[i] for i in range(len(free)) if g>>i&1]
        if isinstance(realise(pi,sig,set(E),k=1),dict) or isinstance(realise(pi,sig,set(E),k=2),dict): ncr+=1
    stat[(len(S), best-len(S), 'someCR2' if ncr else 'NONE', ncr==len(ms))]+=1
    if not ncr: bad.append(S)
print(sorted(stat.items(), key=str)); print('bad', bad[:10])
