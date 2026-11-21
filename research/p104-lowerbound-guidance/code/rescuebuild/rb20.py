import sys;sys.path.insert(0,'.')
from rb19 import climb
from rb13 import *
A5=F(range(5))
# c33-type nested frame at k=5 (two all-main hubs, nested blocks) - coordinate start
S5=[(A5,[]),(A5,[]),(F({0,1,2}),[F({0}),F({1}),F({2})]),(F({0,1,2}),[F({0}),F({1}),F({2})]),(F({1,2}),[F({1}),F({2})]),(F({1,2}),[F({1}),F({2})]),
    (F({3,4}),[F({3}),F({4})]),(F({3,4}),[F({3}),F({4})])]
print('start chat',float(chat(5,S5)),check_design(5,S5),flush=True)
best,val,res=climb(5,S5,nw=3,tr=8)
print('climb',val,[(sorted(M),[sorted(p) for p in P]) for M,P in best] if best else res,flush=True)
