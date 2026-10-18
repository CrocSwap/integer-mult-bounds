import pickle,collections
from cand import *
import closure as C
S=pickle.load(open('S161.pkl','rb'));ok=pickle.load(open('ok161.pkl','rb'))
def lay(h):
    return ('cold0' if len(start[h])==0 else 'enter%d'%len(start[h]))+('/endFULL' if end[h]==FULLB else '/endU')
base=simulate(prog)
print('baseline',base[0],base[3])
cnt=collections.Counter();feas=[]
for h in ok:
    ok1,why,paid,m=simulate(newprog_for([h]),removed={h})
    key=(lay(h),'FEAS' if ok1 else why.split(' reg')[0].split(' ')[0][0]+' '+why.split()[0] )
    cnt[(lay(h),ok1)]+=1
    if ok1:feas.append((h,m))
    else: print(h,lay(h),why)
print(cnt);print('feasible single',feas)
# closures
cc=collections.Counter()
for h in S:
    r,why=C.closure(h)
    if r is None:cc[why.split()[0]]+=1;continue
    P,rem=r;ok1,why2,paid,m=simulate(P,removed=set(rem))
    cc['feas' if ok1 else 'infeas']+=1
    if ok1:print('closure feasible',h,rem,m)
print(cc)
