# optimistic pass: unknown nonroot -> not coverable (False), unknown root -> coverable (True); record which nonroot facts each kill uses
import grrc, json
used={}
def q(kind,M):
    M=tuple(sorted(M,reverse=True))
    if sum(grrc.g[w] for w in M)<grrc.MINOFF[kind]: return False
    k=kind+':'+','.join(map(str,M))
    if k in grrc.ORACLE: return grrc.ORACLE[k]
    if kind=='nonroot': used[k]=used.get(k,0)+1; return False
    return True
grrc.q=q
for r,(d,ws,s) in sorted(grrc.ROWS.items()):
    used.clear(); out=[(t,grrc.kill(w2,dd,ex)) for t,w2,dd,ex in grrc.scen(ws,d,s)]
    print(r,'KILL-if' if all(k for _,k in out) else 'open', [t for t,k in out if not k], sorted(used,key=lambda k:-grrc.g.get(0,0))[:6])
