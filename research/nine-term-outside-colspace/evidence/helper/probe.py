import os  # (working-card chdir removed)
import sys,time
sys.argv=['x','P112']
# (working-card sys.path entry removed)
t=time.time()
from m9lib import *
print('h',h,'v',v,'classes',len(ks),'frames',len(frames),'surv',len(surv),'NS',len(NS),'small',len(small),time.time()-t)
print('perms',len(D['perms']), 'orbs', [len(o) for o in D['orbs']])
import collections
print(collections.Counter(pc(cls[c]) for c in ks))
print(sorted(set(lb(cls[c]) for c in ks)))
print([ (c,pc(cls[c])) for c in surv])
