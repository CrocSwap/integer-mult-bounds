# classify helper intermediate stays: outs-only / ins-only / mixed; partner kinds
import sys; sys.path.insert(0,'../fewstops')
from load import *
from collections import Counter, defaultdict
exec(open('../fewstops/stays.py').read().split('from load import *')[1])
c=Counter(); pk_=Counter()
for r in range(n):
    if kind(r)!='H': continue
    S=stays[r]
    for k in range(1,len(S)-1):
        s=S[k]; ni=len(s['ins']); no=len(s['outs'])
        t='out-only' if ni==0 and no>0 else ('in-only' if no==0 and ni>0 else ('mixed' if ni and no else 'empty'))
        c[(dim[s['f']],t)]+=1
        if t=='out-only' and no==1:
            pk_[kind(s['outs'][0][1])]+=1
for k in sorted(c): print(k,c[k])
print('single-out stays partner kinds',pk_)
