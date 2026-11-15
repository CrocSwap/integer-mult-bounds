# Extract per-register chart paths (with time intervals) and per-main contacts from #7617.
import sys, pickle; sys.path.insert(0,'../../PRICEKIT'); import pricekit as pk
from collections import Counter, defaultdict
W=pk.load('../../ATTACK/STACK7616/best7616.json.gz')
n=W['public']; N=n+W['owned_fields']; H=W['hosted']
cls={}
for r in W['live']: cls[r]='X'; cls[r+112]='Y'
for r in H['X2']: cls[r]='X2'
for r in H['Y2']: cls[r]='Y2'
dim=[len(b) for b in W['frames']]
cur=list(W['initial'])+[None]*W['owned_fields']
stays=defaultdict(list)   # reg -> list of [chart, t_in, t_out]
for r in range(n): stays[r].append([cur[r],-1,None])
contacts=defaultdict(list) # main -> (t, partner, chart, role)
for t,e in enumerate(W['program']):
    op=e[0]
    if op=='MOVE':
        r=e[1]; stays[r][-1][2]=t; stays[r].append([e[3],t,None]); cur[r]=e[3]
    elif op=='INIT':
        r=e[1]; stays[r].append([e[2],t,None]); cur[r]=e[2]
    elif op=='CLEAR':
        r=e[1]; stays[r][-1][2]=t; cur[r]=None
    elif op in('ADD','COPY'):
        r,s,f=e[1],e[2],e[4]
        if r in cls: contacts[r].append((t,s,f,'recv'))
        if s in cls: contacts[s].append((t,r,f,'give'))
T=len(W['program'])
for r in stays:
    if stays[r][-1][2] is None: stays[r][-1][2]=T
pickle.dump(dict(cls=cls,stays=dict(stays),contacts=dict(contacts),dim=dim,frames=W['frames']),open('data.pkl','wb'))
# census
pc=Counter(); kinds=Counter(); mm=Counter()
for m in cls:
    ps=set(p for _,p,_,_ in contacts.get(m,[]))
    pc[cls[m]]+=len(ps)
    for p in ps: kinds[(cls[m], cls.get(p,'own' if p>=n else 'H'))]+=1
    path=[dim[s[0]] for s in stays[m]]
    mm[cls[m]]+=len(path)-1
print('partners per class',pc); print('partner kinds',kinds); print('hops per class',mm)
print('contacts total',sum(len(v) for v in contacts.values()))
# contacts per chart position in main path (start/final/interior)
pos=Counter()
for m,cs in contacts.items():
    st=stays[m]
    for (t,p,f,role) in cs:
        i=[k for k,s in enumerate(st) if s[1]<t<s[2]][0]
        pos[(cls[m],'S' if i==0 else 'F' if i==len(st)-1 else 'I', role)]+=1
for k in sorted(pos): print(k,pos[k])
