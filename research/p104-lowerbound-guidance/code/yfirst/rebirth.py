import sys; sys.path.insert(0,'../fewstops')
from load import *
from collections import Counter
exec(open('../fewstops/stays.py').read().split('from load import *')[1])
c=Counter(); g0=Counter()
for r in range(n):
    S=stays[r]
    if len(S)<2: continue
    s=S[0]; g=len(s['ins'])+len(s['outs'])+s['scale']
    c[(kind(r),g==0)]+=1
    if kind(r)=='H': g0[min(g,5)]+=1
    # last stay empty?
print('first stay empty?',c); print('helper init-stay gate counts',sorted(g0.items()))
c2=Counter()
for r in range(n):
    S=stays[r]
    if len(S)<2: continue
    s=S[-1]; g=len(s['ins'])+len(s['outs'])+s['scale']
    c2[(kind(r),min(g,3))]+=1
print('last stay gates',sorted(c2.items()))
for r in range(n):
    S=stays[r]
    if kind(r)!='H' or len(S)<2: continue
    g=lambda s: len(s['ins'])+len(s['outs'])+s['scale']
    if g(S[0])==0 or g(S[-1])==0:
        print(r,[dim[s['f']] for s in S],[g(s) for s in S], 'final',dim[W['final'][r]])
