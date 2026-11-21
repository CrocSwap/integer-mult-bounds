# Why is each stay boundary forced (fixed order)? Typed causal bounds: L from sources {Xinit, Hinit, own}, U from sinks {Yfin, Hfin, own}.
from ls import *
from lub import join
from collections import Counter
setup(W); st=stays_of(W)
FULL=(1<<512)-1; ZERO=1  # mask of {0}
def typed_bounds(src, snk):
    init=[]; fin=[]
    for r in range(n):
        k=kind(r); m=SM_[W['initial'][r]]
        t='Xinit' if k in('X','X2') else ('Hinit' if k=='H' else 'Yinit')
        init.append(m if t in src else ZERO)
        mf=SM_[W['final'][r]]
        tf='Yfin' if k in('Y','Y2') else ('Hfin' if k=='H' else 'Xfin')
        fin.append(mf if tf in snk else FULL)
    L=[None]*len(P); U=[None]*len(P); cl=list(init)
    for i,e in enumerate(P):
        if e[0]=='ADD':
            d,s_=e[1],e[2]
            if d<n and s_<n: g=join(cl[d],cl[s_]); cl[d]=cl[s_]=g; L[i]=g
            elif d<n or s_<n:
                r=d if d<n else s_; g=SM_[e[4]] if 'own' in src else cl[r]; cl[r]=g; L[i]=g
        elif e[0]=='SCALE' and e[1]<n: L[i]=cl[e[1]]
    cu=list(fin)
    for i in range(len(P)-1,-1,-1):
        e=P[i]
        if e[0]=='ADD':
            d,s_=e[1],e[2]
            if d<n and s_<n: g=cu[d]&cu[s_]; cu[d]=cu[s_]=g; U[i]=g
            elif d<n or s_<n:
                r=d if d<n else s_; g=SM_[e[4]] if 'own' in snk else cu[r]; cu[r]=g; U[i]=g
        elif e[0]=='SCALE' and e[1]<n: U[i]=cu[e[1]]
    return L,U
SRC=['Xinit','Hinit','own']; SNK=['Yfin','Hfin','own']
TB={}
for a in SRC:
    for b in SNK:
        TB[(a,b)]=typed_bounds({a},{b})
LA,UA=typed_bounds(set(SRC),set(SNK))
def forced(L,U,e1,e2):
    jl=None; mu=FULL
    for i in e1+e2:
        jl=L[i] if jl is None else join(jl,L[i]); mu&=U[i]
    return jl&mu!=jl
res=Counter(); total=Counter()
for r in range(n):
    kk='M' if kind(r)!='H' else 'H'
    for k in range(len(st[r])-1):
        e1=st[r][k][1]; e2=st[r][k+1][1]
        if not forced(LA,UA,e1,e2): total[(kk,'unforced')]+=1; continue
        total[(kk,'forced')]+=1
        why=tuple(sorted(p[0]+'/'+p[1] for p,(L,U) in TB.items() if forced(L,U,e1,e2)))
        res[(kk,why if why else ('joint-only',))]+=1
print(sorted(total.items()))
for (kk,w),v in sorted(res.items(),key=lambda t:-t[1])[:25]: print(kk,v,w)
agg=Counter()
for (kk,w),v in res.items():
    S=set(w)
    if 'Xinit/Yfin' in S: c='XY (x-port past vs y-perp future)'
    elif any('own' not in p for p in S): c='publics-only other: '+','.join(sorted(p for p in S if 'own' not in p))
    elif S=={'joint-only'}: c='joint only'
    else: c='needs owned (pinned D/R chart)'
    agg[(kk,c)]+=v
for k,v in sorted(agg.items(),key=lambda t:-t[1]): print(k,v)
