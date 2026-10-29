# independent: positive-root counts of all parabolic subdiagrams of E8 from the Cartan matrix (Bourbaki labelling)
import itertools
edges=[(1,3),(3,4),(4,5),(5,6),(6,7),(7,8),(2,4)]
A=[[0]*8 for _ in range(8)]
for i in range(8): A[i][i]=2
for a,b in edges: A[a-1][b-1]=A[b-1][a-1]=-1
def npos(J):
    J=list(J); k=len(J)
    roots=set(tuple(1 if t==i else 0 for t in range(k)) for i in range(k))
    fr=list(roots)
    while fr:
        new=[]
        for r in fr:
            for i in range(k):
                # <r,alpha_i^vee> = sum_j r_j A[J[j]][J[i]]
                p=sum(r[j]*A[J[j]][J[i]] for j in range(k))
                # simply-laced: r+alpha_i is root iff p == -1 (r != alpha_i)
                if p==-1:
                    s=list(r); s[i]+=1; s=tuple(s)
                    if s not in roots: roots.add(s); new.append(s)
        fr=new
    return len(roots)
from collections import Counter
for r in (7,6,5,4,3,2,1):
    print(r, sorted(Counter(npos(J) for J in itertools.combinations(range(8),r)).items(),reverse=True)[:4])
