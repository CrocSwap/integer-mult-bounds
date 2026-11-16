# AUDIT-SC re-implementation of SC-A Lemma P (L1/L2) + SC-A2 Lemma P' row test, with sigma/omega' from AUDIT-SC's own covering data.
import csv, ast, itertools, json
from math import comb
G={1:1,2:2,3:4,4:8,5:12,6:20,7:36}
def params(S):
    s=sum(G[x] for x in S)
    if s<=3: return [(s,0)]                      # fact (a); F4 min leftover >= 6
    if s==4: return [(4 if sum(S)<=3 else 5,0)]  # fact (b)
    if s==5: return [(9,0)]                      # fact (c)
    if sorted(S) in ([1,1,3],[2,3]): return [(34,0)]   # fact (d) bound 6+28; fact (h)
    if sorted(S)==[4]: return [(9,0),(9,32)]     # facts (e),(i)
    if sorted(S)==[1,4]: return [(17,0),(17,32)] # facts (f),(i)
    return None
def L2(m,sg,om):
    ok=False
    if m>=5:
        pairs=sg*min(7+sg,3*((m-1)//2-1))
        if comb(m,5)>pairs+om*(m-4): ok=True
        if om==0 and m-sg>=5: ok=True
        n3=(m*((m-1)//2))//3
        if om*(m-4)<2*comb(m,5)-n3*comb(m-3,2): ok=True     # Lemma P'
    return ok
def lemmaP(ws,e):
    small=sorted(x for x in ws if x<=4)
    for k in range(len(small)+1):
        for S in sorted(set(itertools.combinations(small,k))):
            S=list(S); s=sum(G[x] for x in S)
            if s>9: continue
            rest=list(ws)
            for x in S: rest.remove(x)
            ep=e-len(S); m=sum(1 for x in rest if x<=6)
            if ep<=2 and m>=4: return ('L1',S,ep,m)
            if ep==3:
                P=params(S)
                if P and all(L2(m,sg,om) for sg,om in P): return ('L2/P\'',S,ep,m,P)
    return None
if __name__=='__main__':
    rows=list(csv.DictReader(open('../SPANCOVER/ledger.csv')))
    out={}
    for i,r in enumerate(rows):
        ws=ast.literal_eval(r['weights']); e=int(r['e'])
        v=lemmaP(ws,e)
        out[i]=v
    json.dump({str(k):v for k,v in out.items()},open('lemp_results.json','w'))
    from collections import Counter
    print('Lemma P kills (all 603 rows):',sum(1 for v in out.values() if v), Counter(v[0] for v in out.values() if v))
    A=list(csv.DictReader(open('../SC-A2/killed2.csv')))
    keyA={(int(r['d']),tuple(sorted(ast.literal_eval(r['weights'])))) for r in A}
    mine={(int(rows[i]['d']),tuple(sorted(ast.literal_eval(rows[i]['weights'])))) for i,v in out.items() if v}
    print('SC-A/A2 74 rows reproduced:',len(keyA&mine),'/',len(keyA),' extra rows outside class A:',len(mine-keyA))
