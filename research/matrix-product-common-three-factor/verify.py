"""Independent full-endpoint checks for the common ABA constructor.
JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib,itertools,json,random,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from constructor import construct,load_source

def check(ok,message):
    if not ok:raise RuntimeError(message)
def ident(n):return tuple(tuple(int(i==j) for j in range(n)) for i in range(n))
def product(a,b,p):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(len(b)))%p for j in range(len(b[0]))) for i in range(len(a)))
def rank(a,p):
    rows=[list(r) for r in a];i=0
    for j in range(len(rows[0])):
        pivot=next((k for k in range(i,len(rows)) if rows[k][j]%p),None)
        if pivot is None:continue
        rows[i],rows[pivot]=rows[pivot],rows[i]
        scale=pow(rows[i][j]%p,-1,p);rows[i]=[x*scale%p for x in rows[i]]
        for k in range(len(rows)):
            if k!=i:
                scale=rows[k][j];rows[k]=[(x-scale*y)%p for x,y in zip(rows[k],rows[i],strict=True)]
        i+=1
    return i

def endpoint(target,factors,p):
    n=len(target);m=n//2;out=ident(n)
    check(len(factors)==3,'three factors')
    for k,f in enumerate(factors):
        fixed=range(m,n) if k%2==0 else range(m)
        check(all(f[i][j]==int(i==j) for i in range(n) for j in fixed),'common right-vector alphabet')
        out=product(out,f,p)
    check(out==target,'complete endpoint')

def charts(target,p):
    m=len(target)//2;pairs=[(1,t) for t in range(p)]+[(0,1)]
    good=set()
    for z,(a,b) in enumerate(pairs):
        row=tuple(tuple((a*target[i][j]+b*target[m+i][j])%p for j in range(2*m)) for i in range(m))
        for w,(c,d) in enumerate(pairs):
            pivot=tuple(tuple((c*r[j]+d*r[m+j])%p for j in range(m)) for r in row)
            if rank(row,p)==rank(pivot,p):good.add((z,w))
    return good

def reject(fn,message):
    try:fn()
    except (RuntimeError,ValueError):return
    raise RuntimeError('control accepted: '+message)

def source_pins():
    pins=json.loads((HERE/'SOURCES.json').read_text())
    for row in pins['files']:
        check(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source drift: '+row['path'])

def run():
    source_pins();s=load_source(ROOT);rng=random.Random(19144257)
    count=0;digest=hashlib.sha256();samples=[]
    # Complete rank-at-most-one binary 4x4 domain, independently deduplicated.
    vectors=list(itertools.product(range(2),repeat=4))
    tiny={tuple(tuple(x*y for y in v) for x in u) for u in vectors for v in vectors}
    check(len(tiny)==226,'rank-one domain')
    cases=[(2,a) for a in sorted(tiny)]
    for p,m in itertools.product((2,3,5,7),(1,2,3,4)):
        n=2*m
        cases.append((p,tuple((0,)*n for _ in range(n))))
        cases.append((p,ident(n)))
        for _ in range(64):cases.append((p,tuple(tuple(rng.randrange(p) for _ in range(n)) for _ in range(n))))
    for diagonal in [(1,1,1,0),(1,0,1,1),(1,1,0,0),(0,0,1,1)]:
        cases.append((2,tuple(tuple(int(i==j)*diagonal[i] for j in range(4)) for i in range(4))))
    for p,a in cases:
        fs=construct(s,a,p);endpoint(a,fs,p)
        digest.update(json.dumps([p,a,fs],separators=(',',':')).encode());count+=1
        if p==2 and len(a)==4 and len(samples)<8 and a!=tuple((0,)*4 for _ in range(4)):samples.append((a,fs))
    # All six scalar rank-one components from PR4780, embedded in M2(F2).
    tuple_targets=[];common=set(itertools.product(range(3),repeat=2))
    for v in [(1,0),(0,1),(1,1)]:
        for u in [(1,0),(0,1)]:
            small=[[u[i]*v[j] for j in range(2)] for i in range(2)]
            a=tuple(tuple(small[i//2][j//2]*int(i%2==j%2) for j in range(4)) for i in range(4))
            check(rank(a,2)==2 and charts(a,2),'singular component with two-factor chart')
            common &= charts(a,2);tuple_targets.append(a)
    check(not common,'common chart exclusion; independent charts are illegal')
    fs_tuple=[construct(s,a,2) for a in tuple_targets]
    for a,fs in zip(tuple_targets,fs_tuple,strict=True):endpoint(a,fs,2)
    # Common factors act on arbitrary dirty component vectors, not projections.
    executions=0
    for a,fs in zip(tuple_targets,fs_tuple,strict=True):
        for x in vectors:
            state=tuple((v,) for v in x)
            for f in reversed(fs):state=product(f,state,2)
            check(state==product(a,tuple((v,) for v in x),2),'chronology');executions+=1
    controls=0
    for a,fs in samples:
        for k in range(3):
            changed=list(fs);bad=[list(r) for r in changed[k]]
            col=2 if k%2==0 else 0;bad[0][col]^=1;changed[k]=tuple(tuple(r) for r in bad)
            reject(lambda:endpoint(a,changed,2),'illegal fixed column');controls+=1
    # Select a genuinely discriminating noncommuting word for omissions/order.
    witness=next((a,construct(s,a,p)) for p,a in cases if p==2 and len(a)==4 and
                 product(product(construct(s,a,p)[2],construct(s,a,p)[1],p),construct(s,a,p)[0],p)!=a)
    a,fs=witness;reject(lambda:endpoint(a,tuple(reversed(fs)),2),'reverse order');controls+=1
    omitted=0
    for p,a in cases:
        fs=construct(s,a,p)
        for k in range(3):
            altered=list(fs);altered[k]=ident(len(a))
            if product(product(altered[0],altered[1],p),altered[2],p)!=a:
                reject(lambda:endpoint(a,altered,p),'omit factor');omitted|=1<<k
        if omitted==7:break
    check(omitted==7,'all omitted-factor controls discriminate');controls+=3
    reject(lambda:construct(s,((0,),),2),'odd shape');controls+=1
    reject(lambda:construct(s,((True,0),(0,1)),2),'bool is not field integer');controls+=1
    return {'schema_version':1,'status':'PASS_COMMON_ABA','targets':count,'complete_binary_rank_le_one_targets':226,'fields':[2,3,5,7],'block_sizes':[1,2,3,4],'sharp_singular_components':6,'dirty_executions':executions,'controls':controls,'factor_digest':digest.hexdigest(),'scope':'written all-field finite-product theorem; bounded finite corroboration'}

if __name__=='__main__':
    result=run()
    if '--write' in sys.argv:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        expected=json.loads((HERE/'RESULT.json').read_text())
        check(type(expected.get('schema_version')) is int and expected['schema_version']==1,'typed receipt schema')
        check(json.dumps(expected,sort_keys=True)==json.dumps(result,sort_keys=True),'generated receipt mismatch')
    print(json.dumps(result,indent=2,sort_keys=True))
