# For a main: which actual stops does B2 drop, and which contacts pin each dropped stop under B3 windows.
import sys, pickle, b3
from collections import Counter
b2=pickle.load(open('b2.pkl','rb'))
def why(m, verbose=True):
    S,F,path,blocks=b3.build(m); r=b2[m]; keep=set(r['chain'])
    dropped=[G for G in path[1:-1] if G not in keep]
    pins={}
    for G in dropped:
        # contacts whose window set allows NO chart of the B2 chain other than ... i.e. contacts pinned to charts not in the B2 chain
        pins[G]=sum(1 for b in blocks for H in b if G in H and not (H & keep))
    if verbose:
        print(m,b3.cls[m],'path dims',[b3.dim[x] for x in path],'B2 dims',[b3.dim[x] for x in r['chain']],
              'gain %.2f'%(r['bound']-r['actual']),'dropped stops -> #contacts pinned there (window set misses B2 chain):',{G:pins[G] for G in dropped})
    return pins
for m in (113,883,79,849,206): why(m)
tot=Counter(); n=Counter()
for m in b2:
    for G,c in why(m,False).items(): tot[min(c,5)]+=1
print('dropped stops by #pinned contacts (5=5+):',sorted(tot.items()))
