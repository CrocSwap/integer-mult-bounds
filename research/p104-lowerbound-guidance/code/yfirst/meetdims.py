import sys; sys.path.insert(0,'../fewstops')
from load import *
from collections import Counter
c=Counter()
for e in P:
    if e[0] in('ADD','COPY'):
        a,b=kind(e[1]),kind(e[2]); d=dim[e[4]]
        if 'H' in (a,b) and a!=b:
            o=b if a=='H' else a; io='H<-' if a=='H' else 'H->'
            c[(o[0],io,d)]+=1
for o in 'XYO':
    for io in ('H<-','H->'):
        print(o,io,[c[(o,io,d)] for d in range(10)])
