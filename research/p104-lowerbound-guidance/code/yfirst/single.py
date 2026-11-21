import sys; sys.path.insert(0,'../fewstops')
from load import *
from collections import Counter
exec(open('../fewstops/stays.py').read().split('from load import *')[1])
c=Counter()
for r in range(n):
    if kind(r)!='H': continue
    S=stays[r]
    for k in range(1,len(S)-1):
        s=S[k]; g=len(s['ins'])+len(s['outs'])
        c[min(g,6)]+=1
print('intermediate helper stays by #gates',sorted(c.items()))
