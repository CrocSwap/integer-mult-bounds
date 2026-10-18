import sys,pickle,collections,time
sys.path.insert(0,__import__('os').environ['EO_ROOT']+'/cards/B251')
from ev import *
P=(1<<61)-1
rows=[{k:1} for k in range(n)]
def norm(r):
    if not r:return ()
    k0=min(r);inv=pow(r[k0],P-2,P)
    return tuple(sorted((k,x*inv%P) for k,x in r.items()))
key=[norm(r) for r in rows]
holders=collections.defaultdict(set)
for q in range(n):holders[key[q]].add(q)
Yev=[]   # (op idx, tag, e, carrier key, holders snapshot(set copy))
t0=time.time()
def setrow(q,r):
    holders[key[q]].discard(q)
    rows[q]=r;key[q]=norm(r);holders[key[q]].add(q)
for idx,(tag,e) in enumerate(prog):
    if e[0]=='scale':
        q=e[1];f=e[2]*pow(e[3],P-2,P)%P
        r={k:x*f%P for k,x in rows[q].items()};setrow(q,r);continue
    t,s=e[1],e[2];num=e[3]*pow(e[4],P-2,P)%P
    if tag[0]=='B' and 112<=t<224:
        Yev.append((idx,tag,e,key[s],frozenset(holders[key[s]])))
    r=dict(rows[t])
    for k,x in rows[s].items():
        a=(r.get(k,0)+num*x)%P
        if a:r[k]=a
        else:r.pop(k,None)
    setrow(t,r)
print(len(Yev),time.time()-t0)
pickle.dump(Yev,open('yev.pkl','wb'))
