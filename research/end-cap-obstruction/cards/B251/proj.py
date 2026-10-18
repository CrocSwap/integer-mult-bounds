import sys,pickle,collections,time
sys.path.insert(0,__import__('os').environ['EO_ROOT']+'/cards/B251')
from ev import *
P=(1<<61)-1
KEEP=set(range(224))|set(w['centers'])
rows=[{k:1} for k in range(n)]
def norm(r):
    r={k:x for k,x in r.items() if k in KEEP}
    if not r:return ()
    k0=min(r);inv=pow(r[k0],P-2,P)
    return tuple(sorted((k,x*inv%P) for k,x in r.items()))
key=[norm(r) for r in rows]
holders=collections.defaultdict(set)
for q in range(n):holders[key[q]].add(q)
Yev=[]
def setrow(q,r):
    holders[key[q]].discard(q)
    rows[q]=r;key[q]=norm(r);holders[key[q]].add(q)
for idx,(tag,e) in enumerate(prog):
    if e[0]=='scale':
        q=e[1];f=e[2]*pow(e[3],P-2,P)%P
        setrow(q,{k:x*f%P for k,x in rows[q].items()});continue
    t,s=e[1],e[2];num=e[3]*pow(e[4],P-2,P)%P
    if tag[0]=='B' and 112<=t<224:
        Yev.append((idx,tag,e,key[s],frozenset(r for r in holders[key[s]] if r<224 or r in KEEP)))
    r=dict(rows[t])
    for k,x in rows[s].items():
        a=(r.get(k,0)+num*x)%P
        if a:r[k]=a
        else:r.pop(k,None)
    setrow(t,r)
pickle.dump(Yev,open('yevp.pkl','wb'))
Y,adj=pickle.load(open('graph.pkl','rb'))
byk=collections.defaultdict(list)
for a,(idx,tag,e,k,h) in enumerate(Yev):byk[k].append(a)
print('proj classes',len(byk),'zero-class events',len(byk.get((),[])))
print(collections.Counter((len(v),len({Yev[a][2][2] for a in v})) for v in byk.values()))
def dsat(nodes):
    col={};sat={u:set() for u in nodes}
    for _ in nodes:
        v=max((u for u in nodes if u not in col),key=lambda u:(len(sat[u]),len(adj[u])))
        c=0
        while c in sat[v]:c+=1
        col[v]=c
        for u in adj[v]:
            if u in sat:sat[u].add(c)
    return col
res=[]
for k,ev in byk.items():
    col=dsat(ev);chi=max(col.values())+1
    nh=set()
    for a in ev:nh|=set(Yev[a][4])
    carriers={Yev[a][2][2] for a in ev}
    res.append((k,ev,col,chi,nh,carriers))
print('chi hist',collections.Counter(r[3] for r in res if r[0]!=()))
print('sum chi',sum(r[3] for r in res if r[0]!=()),'sum carriers used',sum(len(r[5]) for r in res if r[0]!=()))
pickle.dump([(r[0],r[1],r[2],r[3],r[4],r[5]) for r in res],open('resp.pkl','wb'))
