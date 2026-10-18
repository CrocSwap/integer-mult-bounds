"""Exact central-call tariff witnesses and controls. Apache-2.0."""
from fractions import Fraction
from itertools import product
from pathlib import Path
import hashlib,json,sys
HERE=Path(__file__).resolve().parent
def need(ok,msg):
    if not ok:raise ValueError(msg)
def gm(a,b):return a^b^(((a&1)*((b>>1)&1))<<2)
def rm(a,b):
    if not a or not b:return 0
    v=0
    for i,j in product(range(8),repeat=2):
        if (a>>i&1) and (b>>j&1):v^=1<<gm(i,j)
    return v
def mm(a,b):
    n=len(a);c=[[0]*n for _ in range(n)]
    for i,j,k in product(range(n),repeat=3):c[i][j]^=rm(a[i][k],b[k][j])
    return c
def factor(r,g,u,v):return [[int(i==j)^((1|(1<<g)) if (u>>i&1) and (v>>j&1) else 0) for j in range(r)] for i in range(r)]
def evaluate(r,word):
    out=[[int(i==j) for j in range(r)] for i in range(r)]
    for g,u,v in word:out=mm(out,factor(r,g,u,v))
    return out
def goal(r,k):return [[(16 if i<k else 1) if i==j else 0 for j in range(r)] for i in range(r)]
def address(g):return ((1,g&1,(g>>2)&1),(0,1,(g>>1)&1),(0,0,1))
def binary_mm(a,b):return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(len(a)))%2 for j in range(len(a))) for i in range(len(a)))
def sigma(g):return ((g>>1)&1)|((g&1)<<1)|((((g>>2)&1)^((g&1)*((g>>1)&1)))<<2)
def independent(r,word):
    # Faithful regular action, constructed from literal binary address matrices.
    matrices=[address(g) for g in range(8)];index={g:i for i,g in enumerate(matrices)}
    permutations={g:[index[binary_mm(address(g),h)] for h in matrices] for g in (1,2,4)}
    cols=[1<<i for i in range(8*r)]
    for g,u,v in reversed(word):
        out=[]
        for column in cols:
            read=0
            for j in range(r):
                if v>>j&1:read^=(column>>(8*j))&255
            moved=sum(1<<permutations[g][a] for a in range(8) if read>>a&1)
            delta=read^moved
            for i in range(r):
                if u>>i&1:column^=delta<<(8*i)
            out.append(column)
        cols=out
    return cols
def run():
    dep=json.loads((HERE/'PREDECESSOR.json').read_text())
    need(hashlib.sha256((HERE/'PR1573-README.md').read_bytes()).hexdigest()==dep['sha256'],'predecessor bytes')
    for a,b in product(range(8),repeat=2):
        need(binary_mm(address(a),address(b))==address(gm(a,b)),'natural representation')
        need(sigma(gm(a,b))==gm(sigma(a),sigma(b)),'swapped representation')
        need(sigma(sigma(a))==a,'involution')
    fixtures=[];omissions=0
    for k in range(1,5):
        r=k+2
        for central in range(k+1):
            word=[]
            for i in range(k):word += [(g,1<<i,1<<i) for g in ((4,) if i<central else (1,2,1,2))]
            need(evaluate(r,word)==goal(r,k),'formal endpoint')
            wanted=[1<<(8*i+(gm(4,a) if i<k else a)) for i in range(r) for a in range(8)]
            need(independent(r,word)==wanted,'independent faithful replay')
            conjugated=[(g,u,v|(1<<k)) for g,u,v in word]
            expected=goal(r,k)
            for i in range(k):expected[i][k]=17
            need(evaluate(r,conjugated)==expected,'dirty scalar conjugation')
            for j in range(len(word)):
                need(evaluate(r,word[:j]+word[j+1:])!=goal(r,k),'single omission')
                omissions+=1
            fixtures.append({'k':k,'r':r,'central_calls':central,'a_calls':2*(k-central),'b_calls':2*(k-central)})
    tariffs=0
    for k,alpha,beta,gamma in product(range(1,8),range(1,6),range(1,6),range(1,13)):
        low=min(2*max(k-t,0)*(alpha+beta)+gamma*t for t in range(k+5))
        need(low==k*min(2*(alpha+beta),gamma),'exact tariff');tariffs+=1
    for alpha,beta,gamma in [(Fraction(1,3),Fraction(2,7),Fraction(9,8)),(Fraction(7,2),Fraction(1,8),Fraction(1,9))]:
        need(min(2*max(5-t,0)*(alpha+beta)+gamma*t for t in range(10))==5*min(2*(alpha+beta),gamma),'rational tariff');tariffs+=1
    need(evaluate(3,[(4,1,1)])==goal(3,1),'old two-letter floor fails with central calls')
    high=mm(factor(3,4,1,1),factor(3,4,2,2))
    need(high==goal(3,2),'rank-two central control needs two calls')
    bad=goal(3,2);bad[0][2]^=17
    need(bad!=goal(3,2) and all(bad[i][j]==goal(3,2)[i][j] for i in range(3) for j in range(2)),'zero-dirt false positive')
    return {'status':'PASS_UT3_PRICED_CENTRAL','fixtures':fixtures,'omission_controls':omissions,'tariff_checks':tariffs,'representation_products':64,'sharp_cost':'k*min(2*(alpha+beta),gamma)','not_run':['physical call implementation','supplier admission','all-size compiler','hosting','precision/tape','outer assembly'],'new_kappa':False}
if __name__=='__main__':
    receipt=run();path=HERE/'CERTIFICATE.json'
    if '--write' in sys.argv:path.write_text(json.dumps(receipt,indent=2)+'\n')
    else:need(receipt==json.loads(path.read_text()),'receipt mismatch')
    print(receipt['status'],'fixtures='+str(len(receipt['fixtures'])),'tariffs='+str(receipt['tariff_checks']))
