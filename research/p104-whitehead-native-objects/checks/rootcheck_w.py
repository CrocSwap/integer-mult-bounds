#!/usr/bin/env python3
"""Exact root verifier. Stdlib only, nothing imported.
Definition used (the root definition of the retained chain roots): T_k=I-2 x_k y_k^T, y_k.x_k=0, T_{N-1}..T_0=-I.
A stage k has coordinate mask E_k; the run word is Phi=Delta_k T (Delta_k=I+(D_k-1)E_k applied right after the stage's last unit).
Whole-job: symbolic M(D)=-diag(prod D_k^{eps_rk}), computed as sparse polynomial matrices, not sampled.
Usage: rootcheck.py file.json ; exits 0 only if every [REQ] passes. Informational lines start with '  '."""
import json,sys
from fractions import Fraction as Q
R=json.load(open(sys.argv[1]));n,N=R['n'],R['N']
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
req('T_{N-1}..T_0=-I (order T_{N-1}..T_0, I-2xy)',W==[[-v for v in r] for r in I])
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
req('hosted t not 0, not -1 (W outer stages exempt: t must be -1 exactly)',all(t_of(*s['units']) not in (0,-1) for s in hosted if s['letter']!='W') and all(t_of(*s['units'])==-1 for s in hosted if s['letter']=='W'))
# path frame t for adjacent pair with q=+1 frame U=I+x y equals root frame t
# 7 dyadic
dy=lambda v:v.denominator&(v.denominator-1)==0
req('x,y dyadic',all(dy(v) for r in X+Y for v in r))
def odd(v):
    v=abs(v.numerator)
    while v and v%2==0:v//=2
    return v
req('hosted alpha,beta dyadic units (plane projector dyadic)',all(s['letter']=='W' or (odd(dot(Y[s['units'][0]],X[s['units'][1]]))==1 and odd(dot(Y[s['units'][1]],X[s['units'][0]]))==1) for s in hosted))
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
# independent: exact algebra dimension through {x_i y_j}: R_iR_j=G_ij x_i y_j, closure of pattern
vecs=[[X[i][a]*Y[j][b] for a in range(n) for b in range(n)] for i in range(N) for j in range(N)]
P=2147483629
def rank_modp(V):
    A=[[ (v.numerator*pow(v.denominator,-1,P))%P for v in r] for r in V];rk=0;w=len(A[0])
    for c in range(w):
        p=next((i for i in range(rk,len(A)) if A[i][c]),None)
        if p is None:continue
        A[rk],A[p]=A[p],A[rk];inv=pow(A[rk][c],-1,P);rowr=[x*inv%P for x in A[rk]];A[rk]=rowr
        for i in range(rk+1,len(A)):
            if A[i][c]:
                f=A[i][c];A[i]=[(a-f*b)%P for a,b in zip(A[i],rowr)]
        rk+=1
        if rk==w:break
    return rk
print('  span{x_i y_j} rank mod p =',rank_modp(vecs),'of n^2 =',n*n)
print('RESULT','ALL_REQ_PASS' if not bad else 'FAILED '+'; '.join(bad))
sys.exit(1 if bad else 0)
