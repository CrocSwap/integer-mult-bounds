exec(open((__import__('os').environ['HM_ROOT']+'/cards/B98c/work/gate.py')).read().split("good=[")[0])
import collections
A=[list(e) for e in d['A']]; st=d['start']; cur=list(d['start'])
for e in A:
    f=e[-1]
    for q in regs(e):f=F.join(f,cur[q])
    for q in regs(e):cur[q]=f
print(list(blocks))
for bn in ['(0, 1, 2, 3)','(0, 1, 4, 5)','(0, 1, 6, 7)']:
    scr=list(blocks[bn]); cols=sorted({j for r in scr for j in rows0[r]})
    print(bn,'nscr',len(scr),'ncols',len(cols),scr[:5],scr[-3:],cols[:6],cols[-3:])
    sup=collections.Counter(len(rows0[r]) for r in scr); print(' supp sizes',sorted(sup.items()))
    bd=collections.Counter(len(F.fr[cur[r]]) for r in scr); print(' bound dim',sorted(bd.items()))
    print(' row0 sample',{r:list(rows0[r].items())[:3] for r in scr[:2]})
print('frame vec of cols sample', [F.fr[st[l]] for l in cols[:3]])
print('=====')
def spanset(basis):
    s={0}
    for b in basis: s|={x^b for x in s}
    return s
for bn in ['(0, 1, 2, 3)','(0, 2, 4, 6)']:
    scr=list(blocks[bn]); cols=sorted({j for r in scr for j in rows0[r]})
    vec={l:F.fr[st[l]][0] for l in cols}
    print(bn,len(cols),'distinct vec',len({vec[l] for l in cols}))
    # rank of vecs
    import itertools
    def rank(vs):
        b=[]
        for x in vs:
            for y in b: x=min(x,x^y)
            if x:b.append(x)
        return len(b)
    print(' rank vecs',rank(list(vec.values())))
    for r in scr:
        sp=spanset(F.fr[cur[r]]) if len(F.fr[cur[r]])<=12 else None
        S=rows0[r]
        hs=spanset([vec[p] for p in S]) if len(S)<=12 else None
        B=[l for l in cols if sp and vec[l] in sp]
        H=[l for l in cols if hs and vec[l] in hs]
        print(' ',r,'|S|',len(S),'dimB',len(F.fr[cur[r]]),'|B|',len(B),'|H|',len(H),'rank S',rank([vec[p] for p in S]))
