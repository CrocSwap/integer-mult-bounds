# Independent re-check (impl 2, no networkx, no grrc.py) of the j=2 GRRC kills.
# Facts: NEG = multisets proven non-coverable (both impls); cap rule: cap < 57 => no root cover, cap < 78 => no non-root cover.
import itertools, csv, json
G={1:1,2:2,3:4,4:8,5:12,6:20,7:36,8:64}
NEG_ROOT={(6,6,4,4,1),(6,6,4,4,1,1),(6,6,4,4,2),(6,6,5,3,1),(6,6,5,4)}
NEG_D7={(6,6,6,4,4,1,1),(6,6,6,4,4,2),(6,6,6,4,4,3),(6,6,6,5,4)}
srt=lambda x: tuple(sorted(x,reverse=True))
cap=lambda x: sum(G[w] for w in x)
def no_root(x): x=srt(x); return cap(x)<57 or x in NEG_ROOT or any(srt(y)==x for y in [])
def no_nonroot(x):
    x=srt(x); c=cap(x)
    if c<78: return True
    return c<83 and x in NEG_D7          # cap 78..82: only D7 (78) of the minimal non-root Off sets fits
def scenarios(ws,d,s):
    if s==7: yield 'ClassI',list(ws),d,[]; return
    yield 'beta1',list(ws),d,[]
    yield 'alpha',list(ws),d,[1]
    for x in sorted(set(ws)):
        w=list(ws); w.remove(x); w.append(x+1); yield 'bump%d'%x,w,d,[]
    if 7 in ws:
        w=list(ws); w.remove(7); yield 'b3B',w,d-1,[]
def j2kill(ws,d,ex):
    ws=srt(ws)
    for K0 in set(itertools.combinations(ws,d-2)):            # multiset choice of K0
        comp=list(ws)
        for x in K0: comp.remove(x)
        nodes=[i for i in range(len(comp)) if no_nonroot([comp[k] for k in range(len(comp)) if k!=i]+ex) and not no_root([comp[k] for k in range(len(comp)) if k!=i]+ex)]
        for Q in itertools.combinations(nodes,4):
            if all(no_root([comp[k] for k in range(len(comp)) if k not in (a,b)]+ex) for a,b in itertools.combinations(Q,2)):
                return 'K0=%s comp=%s nodes(removed)=%s'%(K0,srt(comp),[comp[i] for i in Q])
    return None
def imm(ws,d,ex):
    for K in set(itertools.combinations(srt(ws),d-1)):
        c=list(ws)
        for x in K: c.remove(x)
        if no_root(c+ex): return 'IMM'
    return None
import os
L=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','data','ledger2_consolidated.csv')
T=[169,303,312,315,316,332,333,400,401,402,409,411,417,418,420,424,425,426,427,430,435,464]
cert={}
for r in csv.DictReader(open(L)):
    R=int(r['row'])
    if R not in T: continue
    d=int(r['d']); ws=json.loads(r['weights']); s=int(r['slack'])
    ok=True; cs=[]
    for tag,w,dd,ex in scenarios(ws,d,s):
        k=imm(w,dd,ex) or j2kill(w,dd,ex)
        cs.append((tag,k)); ok&=bool(k)
    cert[R]=cs
    print(R,'KILLED' if ok else 'open',[t for t,k in cs if not k])
json.dump(cert,open('certs_chk2.json','w'),indent=1)
