"""Independent rank-eight Gram reconstruction from the frozen port matrix."""
from pathlib import Path
from fractions import Fraction as F
import json
from hashlib import sha256
P=Path(__file__).resolve().parent

def need(c,m):
    if not c:raise ValueError(m)

def inverse(a):
    n=len(a);a=[row[:]+[F(i==j)for j in range(n)]for i,row in enumerate(a)]
    for j in range(n):
        k=next(i for i in range(j,n)if a[i][j]);a[j],a[k]=a[k],a[j]
        d=a[j][j];a[j]=[v/d for v in a[j]]
        for i in range(n):
            if i!=j:
                d=a[i][j];a[i]=[v-d*w for v,w in zip(a[i],a[j])]
    return [row[n:]for row in a]

def main():
    raw=(P/'CODE.json').read_bytes();a=[[F(x)for x in row]for row in json.loads(raw)['A']];n=112
    need(len(a)==n and all(len(row)==n for row in a),'Code dimensions')
    q=[[(F(i==j)-a[i][j])/14 for j in range(n)]for i in range(n)]
    basis={};cols=[]
    for col in zip(*q):
        v=list(col)
        for pivot,b in sorted(basis.items()):
            c=v[pivot];v=[x-c*y for x,y in zip(v,b)]
        k=next((i for i,x in enumerate(v)if x),None)
        if k is not None:
            d=v[k];basis[k]=[x/d for x in v];cols.append(list(col))
    need(len(cols)==8,'Eight independent image columns')
    gram=[[sum(x*y for x,y in zip(c,d))for d in cols]for c in cols];gi=inverse(gram)
    # Independently reconstruct the unique orthogonal projection onto these columns.
    cg=[[sum(cols[k][i]*gi[k][j]for k in range(8))for j in range(8)]for i in range(n)]
    for i in range(n):
        for j in range(n):need(q[i][j]==sum(cg[i][k]*cols[k][j]for k in range(8)),'Full Gram projector equality')
    need(all(a[i][i]==0 for i in range(n)),'Zero code diagonal')
    need(sum(a[i][j]!=0 for i in range(n)for j in range(n)if i!=j)==5824,'Off-diagonal support')
    print(json.dumps({'status':'PASS_INDEPENDENT_EIGHT_MODE_GRAM','public_code_sha256':sha256(raw).hexdigest(),'rank':8,'spectrum':{'1':104,'-13':8},'condition_number_2':13},sort_keys=True))
if __name__=='__main__':main()
