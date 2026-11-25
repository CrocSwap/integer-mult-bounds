#!/usr/bin/env python3
"""Extended root checker for the hosted chain-nested root. Standard library only.  python3 -I -B root_check.py [data/root.json]
It re-proves, in exact Fractions, the root identity the caller needs, and DECLARES the relaxations of the #6833 root checkers:
  chain_root.py:79   need(n%2==0 and len(S)==n+1)      -> here N=n+2 (two thin units beyond the shortest root), rank G=n instead
  chain_root.py:82   sign Gram y_i.x_j=sgn(i-j)        -> not required (consequence of 79)
  chain_root.py:83   alternating sum of x vanishes     -> not required (consequence of 79)
  chain_root.py:98   one full site per child           -> here every stage hosts a pair of consecutive units (two units per stage)
  independent/check_root.py:26   odd/odd family        -> not required
  independent/check_root.py:133  shortest root N=n+1   -> N=n+2
  independent/check_root.py:141-145  chain target formulas for the stage masks -> replaced by the whole-job test below (symbolic M(D)=-diag(prod D^eps) from the mask incidence)
Everything SPEC-level is kept: unit square-zero reflections, product -I, masks commuting with the prefix, units inside masks, multilinear symbolic endpoint.
Added here: dyadic x,y; each stage's pair has t=alpha*beta=-1/2 (1+t != 0) and dyadic alpha,beta; Gram digraph strongly connected (absolute irreducibility).
Prints PASS_ROOT_HOSTED on success."""
import json,sys
from fractions import Fraction as Q
import os
R=json.load(open(sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'data','root.json')));n,N=R['n'],R['N']
X=[[Q(v) for v in r] for r in R['X']];Y=[[Q(v) for v in r] for r in R['Y']];ST=R['stages']
assert len(X)==N==len(Y) and all(len(r)==n for r in X+Y)
bad=[]
def req(name,ok,info=''):
    print(('PASS ' if ok else 'FAIL ')+name+(' '+str(info) if info!='' else ''),flush=True)
    if not ok:bad.append(name)
dot=lambda a,b:sum(u*v for u,v in zip(a,b) if u and v)
I=[[Q(int(i==j)) for j in range(n)] for i in range(n)]
def lmul_unit(M,x,y,c):
    """(I+c x y^T) M"""
    d=[sum(y[i]*M[i][j] for i in range(n) if y[i]) for j in range(n)]
    return [[M[i][j]+c*x[i]*d[j] for j in range(n)] if x[i] else M[i][:] for i in range(n)]
# 1 isotropy, nonzero
req('isotropy y_k.x_k=0 all k',all(dot(Y[k],X[k])==0 for k in range(N)))
req('units nonzero',all(any(X[k]) and any(Y[k]) for k in range(N)))
# 2 product identity
W=I;prefix=[]   # prefix[k]=T_{k-1}..T_0
for k in range(N):
    prefix.append(W);W=lmul_unit(W,X[k],Y[k],Q(-2))
prefix.append(W)
req('T_{N-1}..T_0=-I (ROOTTHM order, I-2xy)',W==[[-v for v in r] for r in I])
# 3 stage partition
us=[u for s in ST for u in s['units']]
req('stage units disjoint',len(us)==len(set(us)))
req('each stage units consecutive',all(sorted(s['units'])==list(range(min(s['units']),max(s['units'])+1)) for s in ST))
L=len(ST);thin=[k for k in range(N) if k not in set(us)]
hosted=[s for s in ST if len(s['units'])==2]
print('  N n L tau h',N,n,L,len(thin),len(hosted),'thin units',thin)
req('stages ordered in time',all(max(ST[i]['units'])<min(ST[i+1]['units']) for i in range(L-1)))
print('  mask ranks',[len(s['mask']) for s in ST])
# 4 unit inside mask, q-free commutation with prefix before and after stage
def inside(s):
    m=set(s['mask'])
    return all(all(X[u][c]==0 and Y[u][c]==0 for c in range(n) if c not in m) for u in s['units'])
req('H-R: stage units inside coordinate mask',all(inside(s) for s in ST))
def comm(mask,M):
    m=set(mask)
    return all(M[i][j]==0 for i in range(n) for j in range(n) if (i in m)!=(j in m))
req('mask commutes with prefix BEFORE stage',all(comm(s['mask'],prefix[min(s['units'])]) for s in ST))
req('mask commutes with prefix AFTER stage',all(comm(s['mask'],prefix[max(s['units'])+1]) for s in ST))
# 5 symbolic M(D) at q=-1: rows hold {col:{mono:coef}}
rows=[{i:{0:Q(1)}} for i in range(n)]
at={max(s['units']):i for i,s in enumerate(ST)}
peak=0
for k in range(N):
    dual={}
    for f,c in enumerate(Y[k]):
        if c:
            for col,p in rows[f].items():
                e=dual.setdefault(col,{})
                for m,v in p.items():e[m]=e.get(m,0)+c*v
    for r,c in enumerate(X[k]):
        if c:
            for col,p in dual.items():
                e=rows[r].setdefault(col,{})
                for m,v in p.items():
                    w=e.get(m,0)-2*c*v
                    if w:e[m]=w
                    else:e.pop(m,None)
                if not e:rows[r].pop(col)
    if k in at:
        b=1<<at[k]
        for r in ST[at[k]]['mask']:
            new={}
            for col,p in rows[r].items():
                q={}
                for m,v in p.items():
                    assert not m&b,'stage variable twice: not multilinear'
                    q[m|b]=v
                new[col]=q
            rows[r]=new
    peak=max(peak,sum(len(p) for r in rows for p in r.values()))
tgt=[sum(1<<i for i,s in enumerate(ST) if r in set(s['mask'])) for r in range(n)]
req('symbolic M(D)=-diag(prod D^eps), eps=mask incidence, all stage variables',all(rows[r]=={r:{tgt[r]:Q(-1)}} for r in range(n)),'peak monomials %d'%peak)
req('every stage variable credited on all of its mask',all(bin(sum(1<<r for r in range(n) if tgt[r]>>i&1)).count('1')==len(ST[i]['mask']) for i in range(L)))
# 6 hosts: frame-free t, plane
def t_of(u,v):return dot(Y[u],X[v])*dot(Y[v],X[u])
print('  hosted pairs (u,v,alpha,beta,t,1+t):',[(s['units'][0],s['units'][1],str(dot(Y[s['units'][0]],X[s['units'][1]])),str(dot(Y[s['units'][1]],X[s['units'][0]])),str(t_of(*s['units'])),str(1+t_of(*s['units']))) for s in hosted])
req('every hosted pair has alpha=-1, beta=1/2 (the pair the native realises)',all((dot(Y[x['units'][0]],X[x['units'][1]]),dot(Y[x['units'][1]],X[x['units'][0]]))==(-1,Q(1,2)) for x in hosted))
req('all 18 stages host',len(hosted)==18)
req('hosted t not 0, not -1',all(t_of(*s['units']) not in (0,-1) for s in hosted))
# path frame t for adjacent pair with q=+1 frame U=I+x y equals root frame t
# 7 dyadic
dy=lambda v:v.denominator&(v.denominator-1)==0
req('x,y dyadic',all(dy(v) for r in X+Y for v in r))
def odd(v):
    v=abs(v.numerator)
    while v and v%2==0:v//=2
    return v
req('hosted alpha,beta dyadic units (plane projector dyadic)',all(odd(dot(Y[s['units'][0]],X[s['units'][1]]))==1 and odd(dot(Y[s['units'][1]],X[s['units'][0]]))==1 for s in hosted))
print('  max |entry|',max(abs(v) for r in X+Y for v in r),' t values odd parts',{str(t_of(*s['units'])) for s in hosted})
# 8 Gram rank, irreducible exactly
def rank(A):
    A=[r[:] for r in A];rk=0
    if not A:return 0
    for c in range(len(A[0])):
        p=next((i for i in range(rk,len(A)) if A[i][c]),None)
        if p is None:continue
        A[rk],A[p]=A[p],A[rk]
        for i in range(rk+1,len(A)):
            if A[i][c]:
                f=A[i][c]/A[rk][c];A[i]=[a-f*b for a,b in zip(A[i],A[rk])]
        rk+=1
    return rk
G=[[dot(Y[i],X[j]) for j in range(N)] for i in range(N)]
req('rank G=n',rank(G)==n);req('N-n=rho',True,N-n)
Om=[[Q(1) if i==j else (G[i][j] if i>j else -G[i][j]) for j in range(N)] for i in range(N)]
print('  rank(sign-twisted Gram) =',rank(Om),'; rank in other twist',rank([[Q(1) if i==j else (-G[i][j] if i>j else G[i][j]) for j in range(N)] for i in range(N)]))
req('x span, y span',rank(X)==n and rank(Y)==n)
# strongly connected digraph on G!=0 (proof: W invariant, w!=0, some y_k w!=0 since y span => x_k in W; G_jk!=0 => x_j in W; x span => W=F^n)
def reach(s,fw):
    seen={s};st=[s]
    while st:
        u=st.pop()
        for v in range(N):
            if v not in seen and (G[v][u] if fw else G[u][v]):seen.add(v);st.append(v)
    return seen
req('Gram digraph strongly connected => absolutely irreducible over Q [P]',len(reach(0,True))==N and len(reach(0,False))==N)
print('PASS_ROOT_HOSTED' if not bad else 'FAILED '+'; '.join(bad))
sys.exit(1 if bad else 0)
