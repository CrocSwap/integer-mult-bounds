# BUDGET-X §3 size-only deletion-lemma optimiser, own code
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get('BX_DATA', os.path.join(HERE, '..', '..', 'data', 'data.json'))
WORK = os.environ.get('BX_WORK', '.')
import itertools
cap={0:2,1:4,2:8,3:12,4:20,5:36}
def table(d):
    for t in range(1,7):
        row=[]
        for b in range(1,9):
            best=None
            for k in range(1,t+b+1):
                for sig in itertools.combinations_with_replacement(range(5,-1,-1),k):  # nonincreasing
                    a=[cap[x] for x in sig]
                    if all(sum(a[j:])>=d[b-j] for j in range(b)):
                        s=sum(sig); best=s if best is None or s<best else best
            row.append(max(0,6*b-best))
        print(' t=%d'%t,row)
print('d2=76'); table({1:53,2:76,3:92,4:100,5:106,6:109,7:111,8:112})
