import pickle,sys,itertools as it
from collections import Counter
I=pickle.load(open('info.pkl','rb'))
pairs,HALF,P,v,FULLT=I['pairs'],I['HALF'],I['P'],I['v'],I['FULLT']
def basis(vectors):
    b={}
    for x in vectors:
        for p in sorted(b,reverse=True):
            if x>>p&1:x^=b[p]
        if x:
            p=x.bit_length()-1
            for q in b:
                if b[q]>>p&1:b[q]^=x
            b[p]=x
    return tuple(b[p] for p in sorted(b,reverse=True))
def perp(F,port):return all((x&port).bit_count()%2==0 for x in F)
print('pairs',len(pairs),'selected',sum(p['selected'] for p in pairs))
# FULLT
sel_one=0;sel_both=0;sel_none=0
for pr in pairs:
    if not pr['selected']:continue
    k=[(key[1],key[2]) in FULLT for key in pr['keys']]
    if all(k):sel_both+=1
    elif any(k):sel_one+=1
    else:sel_none+=1
print('selected pairs: both FULLT',sel_both,'one FULLT',sel_one,'none',sel_none,'|FULLT|',len(FULLT))
cnt=Counter();dims=Counter()
for pid,pr in enumerate(pairs):
    if pr['selected']:continue
    t,u=pr['targets'];k1,k2=pr['keys']
    fr=[]
    for key in (k1,k2):
        (a,al,fa),(b,be,fb)=HALF[key];fr+= [fa,fb]
    ok_t=all(perp(f,P[t]) for f in fr);ok_u=all(perp(f,P[u]) for f in fr)
    ok_both=ok_t and ok_u
    J=basis(sum(fr,()))
    cnt[(ok_t,ok_u)]+=1;dims[(len(J),tuple(len(f) for f in fr))]+=1
print('nonselected raw-half frames inside hyper(Pt),hyper(Pu):',dict(cnt));print(dims)
print('--- value gate: m10*m01+m00*m11==0 (target-basis T solves), nonselected vs selected')
c=Counter()
for pr in pairs:
    m=pr['matrix'];ok=(m[1][0]*m[0][1]+m[0][0]*m[1][1]==0);zero=any(x==0 for r in m for x in r)
    c[(pr['selected'],ok,zero)]+=1
print(dict(c))
print(Counter(abs(x) for pr in pairs for r in pr['matrix'] for x in r))
print('--- coded-frame gate: curY after selected loads vs partner hyperplane')
curY=I['curY'];c=Counter();dd=Counter()
for pid,pr in enumerate(pairs):
    if pr['selected']:continue
    t,u=pr['targets']
    a=perp(curY[t],P[u]);b=perp(curY[u],P[t])
    c[(a,b)]+=1;dd[(len(curY[t]),len(curY[u]))]+=1
print(dict(c),dict(dd))
# per-target: how many partners u (across the 2 nonselected pairs) 
print('--- ordering feasibility: loads of another pair X\' (halves of both keys, J dim 6) inside partner hyperplane')
bytarget={}
for pid,pr in enumerate(pairs):
    for t in pr['targets']:bytarget.setdefault(t,[]).append(pid)
assert all(len(x)==3 for x in bytarget.values())
def Jf(pr):
    fr=[]
    for key in pr['keys']:
        (a,al,fa),(b,be,fb)=HALF[key] if key in HALF else (None,None)
        fr+=[fa,fb]
    return basis(sum(fr,()))
# HALF only has nonselected keys; selected keys loads: use curY info instead
res=Counter()
for pid,pr in enumerate(pairs):
    if pr['selected']:continue
    t,u=pr['targets']
    for me,partner in ((t,u),(u,t)):
        for xp in bytarget[me]:
            if xp==pid:continue
            X=pairs[xp]
            if X['selected']:
                ok='sel:'+str(perp(curY[me],P[partner]))
            else:
                ok='non:'+str(perp(Jf(X),P[partner]))
            res[ok]+=1
print(dict(res))
print('--- single-half granularity')
res=Counter()
for pid,pr in enumerate(pairs):
    if pr['selected']:continue
    t,u=pr['targets']
    for me,partner in ((t,u),(u,t)):
        for xp in bytarget[me]:
            if xp==pid or pairs[xp]['selected']:continue
            for key in pairs[xp]['keys']:
                for (a,al,fa) in HALF[key]:
                    res[perp(fa,P[partner])]+=1
print(dict(res))
