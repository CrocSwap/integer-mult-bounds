import sys,pickle,collections
sys.path.insert(0,__import__('os').environ['EO_ROOT']+'/cards/B251')
from ev import *
ops,Ls,caps=build_events()
Y=[(i,tag,e) for i,tag,e in ops if i in Ls and e[1] in range(112,224)]
print('Y events',len(Y),collections.Counter(tag[0] for i,tag,e in Y))
# members bitmask of subspaces
def members(b):
    s={0}
    for x in b:s|={y^x for y in s}
    m=0
    for y in s:m|=1<<y
    return m
mm={}
def mem(b):
    if b not in mm:mm[b]=members(b)
    return mm[b]
N=len(Y)
Lm=[mem(Ls[i]) for i,_,_ in Y]
Cm=[mem(end[e[1]]) for _,_,e in Y]
# conflict(i<j in time): join(L_i,L_j) not subset cap_j  <=> L_i not subset cap_j (given L_j subset cap_j; join subset iff both)
adj=[set() for _ in range(N)]
ne=0
for a in range(N):
    for b in range(a+1,N):
        if Lm[a] & ~Cm[b]:
            adj[a].add(b);adj[b].add(a);ne+=1
print('edges',ne,'of',N*(N-1)//2)
pickle.dump((Y,adj),open('graph.pkl','wb'))
