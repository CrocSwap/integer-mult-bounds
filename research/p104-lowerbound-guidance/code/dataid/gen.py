import json
exec(open('explore.py').read().split("print(lab==L1")[0])
E8=json.load(open(D+'e8base.json')); C=E8['C']; Gb=E8['Gb']
em=json.load(open('embed.json')); beta=em['beta']; R=em['R']
print(min(min(r) for r in C[:104]),max(max(r) for r in C[:104]))
def L(v): return '['+', '.join(map(str,v))+']'
def LL(m): return '[\n  '+',\n  '.join(L(r) for r in m)+']'
# integer inverse of Gb via fractions
from fractions import Fraction
n=8
A=[[Fraction(Gb[i][j]) for j in range(n)]+[Fraction(int(i==j)) for j in range(n)] for i in range(n)]
for c in range(n):
    p=next(r for r in range(c,n) if A[r][c]!=0); A[c],A[p]=A[p],A[c]
    A[c]=[x/A[c][c] for x in A[c]]
    for r in range(n):
        if r!=c and A[r][c]!=0: A[r]=[x-A[r][c]*y for x,y in zip(A[r],A[c])]
inv=[[A[i][n+j] for j in range(n)] for i in range(n)]
assert all(x.denominator==1 for r in inv for x in r)
inv=[[int(x) for x in r] for r in inv]
out=[]
out.append('def betaTab : List (List Int) := '+LL(beta))
out.append('def gbInvTab : List (List Int) := '+LL(inv))
out.append('def rootTab : List (List Int) := '+LL(R[:104]))
out.append('def coordTab : List (List Int) := '+LL(C[:104]))
out.append('def gramTab : List (List Int) := '+LL(G))
fr=[list(map(int,l.split())) for l in open(D+'frames.txt').read().strip().split('\n')[1:]]
out.append('def frameListsTab : List (List Nat) := '+LL(fr))
open('tables.lean','w').write('\n\n'.join(out)+'\n')
print(len(open('tables.lean').read()))
