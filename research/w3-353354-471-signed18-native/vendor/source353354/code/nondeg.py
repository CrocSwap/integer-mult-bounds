"""Exact checks of every frame of WORD not identical in BASE: integer rank of B = dim, A.B = 0, dim A + dim B = h = 20, and
G = I - J/9 nondegeneracy (det(9 B B^T - s s^T) != 0, exact Bareiss). Also: every frame referenced by a record is checked
if new. usage: nondeg.py WORD BASE"""
import json,sys,collections
H=20
def det(M):
    M=[r[:] for r in M];n=len(M);sg=1;prev=1
    for k in range(n-1):
        if M[k][k]==0:
            sw=next((i for i in range(k+1,n) if M[i][k]!=0),None)
            if sw is None: return 0
            M[k],M[sw]=M[sw],M[k];sg=-sg
        for i in range(k+1,n):
            for j in range(k+1,n): M[i][j]=(M[i][j]*M[k][k]-M[i][k]*M[k][j])//prev
        prev=M[k][k]
    return sg*M[n-1][n-1]
def rank(B):
    M=[r[:] for r in B];r=0
    for c in range(H):
        p=next((i for i in range(r,len(M)) if M[i][c]!=0),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]
        for i in range(len(M)):
            if i!=r and M[i][c]!=0: a,b=M[r][c],M[i][c];M[i]=[x*a-y*b for x,y in zip(M[i],M[r])]
        r+=1
    return r
fr=json.load(open(sys.argv[1]+'/frames.json'))['frames'];old=json.load(open(sys.argv[2]+'/frames.json'))['frames']
new=[k for k in fr if k not in old or fr[k]['B']!=old[k]['B'] or fr[k]['A']!=old[k]['A']]
bad=0;st=collections.Counter()
for k in new:
    B=fr[k]['B'];A=fr[k]['A'];d=len(B)
    if d==0: continue
    assert rank(B)==d,('rank',k);assert len(A)+d==H,('Adim',k);assert all(sum(a*b for a,b in zip(x,y))==0 for x in A for y in B),('AB',k)
    if A: assert rank(A)==len(A)
    s=[sum(r) for r in B];M=[[9*sum(B[i][t]*B[j][t] for t in range(H))-s[i]*s[j] for j in range(d)] for i in range(d)]
    z=det(M)!=0;st[(d,z)]+=1;bad+=not z
print('new/changed frames',len(new),'degenerate',bad,'by (dim,nondeg)',dict(sorted(st.items())))
assert bad==0
