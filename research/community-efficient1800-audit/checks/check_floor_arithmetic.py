"""Independent exact arithmetic and source checks for the #2854 resolution."""
import ast, hashlib, importlib.util, itertools, json, random, subprocess, time
from fractions import Fraction as Q
from pathlib import Path
import numpy as np
P=Path('/tmp/pr-efficient1800');pkg=P/'sources/2854/research/two-sided-ten-term-floor';repo=Path('/tmp/integer-mult-efficient1100-20261015')
# Load only the bounded rank definition, without executing the package driver/data imports.
tree=ast.parse((pkg/'checks/lib.py').read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='bounded_integer_rank');ns={};exec(compile(ast.Module(body=[node],type_ignores=[]),'rank-definition','exec'),ns);rank=ns[node.name]
def qr(rows):
    if not rows:return 0
    a=[[Q(x) for x in r] for r in rows];k=0
    for j in range(len(a[0])):
        pivot=next((i for i in range(k,len(a)) if a[i][j]),None)
        if pivot is None:continue
        a[k],a[pivot]=a[pivot],a[k];v=a[k][j];a[k]=[x/v for x in a[k]]
        for i in range(k+1,len(a)):
            v=a[i][j];a[i]=[x-v*y for x,y in zip(a[i],a[k])]
        k+=1
        if k==len(a):break
    return k
start=time.monotonic();assert all(65537%i for i in range(2,257));assert 8**4<65537
cases=0
for shape in [(1,3),(2,3),(3,3)]:
    m,n=shape
    for flat in itertools.product((-1,0,1),repeat=m*n):
        rows=[list(flat[i*n:(i+1)*n]) for i in range(m)]
        assert rank(rows)==qr(rows);cases+=1
rng=random.Random(2854)
for _ in range(400):
    n=rng.randrange(1,9);m=rng.randrange(1,15)
    base=[[rng.choice((-1,0,1)) for _ in range(n)] for _ in range(rng.randrange(1,m+1))]
    rows=[rng.choice(base) for _ in range(m)];assert rank(rows)==qr(rows);cases+=1
H=np.array([[1]],dtype=np.int64)
for _ in range(3):H=np.block([[H,H],[H,-H]])
assert rank(H)==8
for invalid in ([[2]],[[Q(1,2)]],[[0]*9],[[float('nan')]]):
    try:rank(invalid)
    except ValueError:pass
    else:raise AssertionError('domain guard accepted invalid input')
# Authenticate exactly the earlier package's data and original submitted manifest.
meta=json.loads((P/'2832.json').read_text());path='research/decoder-floors-reduction/data/data.json';head=meta['headRefOid']
raw=subprocess.check_output(['git','show',head+':'+path],cwd=repo);assert raw==(pkg/'data/data.json').read_bytes()
original=P/'prior-revisions/2854-original/research/two-sided-ten-term-floor'
for line in (original/'MANIFEST.sha256').read_text().splitlines():
    sha,rel=line.split('  ',1);assert hashlib.sha256((original/rel).read_bytes()).hexdigest()==sha
D=json.loads(raw);FC=np.array(D['FC'],dtype=np.int64);assert FC.shape==(112,8) and np.all(np.isin(FC,[-1,0,1])) and np.all(np.count_nonzero(FC,axis=1)==4)
assert all(Q(str(x))*2==int(Q(str(x))*2) for row in D['L']+D['F0'] for x in row)
# Run the corrected decomposition function, independently comparing selected pair answers
# against exact rational span/nonzero-coefficient conditions.
pairs=list(itertools.combinations(range(112),2));p1=np.array([FC[i] for i,j in pairs]);p2=np.array([FC[j] for i,j in pairs]);g11=(p1*p1).sum(1);g22=(p2*p2).sum(1);g12=(p1*p2).sum(1)
ns=dict(np=np,P1=p1,P2=p2,G11=g11,G22=g22,G12=g12,DET=g11*g22-g12*g12,pairs=pairs,CACHE={})
node=next(n for n in ast.parse((pkg/'checks/caseb4.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='decomp');exec(compile(ast.Module(body=[node],type_ignores=[]),'decomp-definition','exec'),ns)
checks=0
for t in range(24):
    i,j=rng.sample(range(112),2);w=FC[i]+FC[j] if t%2 else np.array([rng.choice((-1,0,1)) for _ in range(8)])
    got=set(ns['decomp'](w))
    for a,b in [(min(i,j),max(i,j))]+rng.sample(pairs,31):
        x=FC[a].tolist();y=FC[b].tolist();z=w.tolist()
        want=qr([x,y,z])==2 and qr([x,z])==2 and qr([y,z])==2
        assert ((a,b) in got)==want;checks+=1
out=dict(status='passed',seconds=time.monotonic()-start,exact_rank_cases=cases+1,domain_rejections=4,exact_decomposition_pair_checks=checks,data_binding=dict(commit=head,path=path,sha256=hashlib.sha256(raw).hexdigest()),scope='Exact Fraction elimination against bounded modular rank, input-domain rejection, original manifest/data authentication and rational decomposition controls. Full corrected census remains required.')
(P/'provenance-2854-arithmetic.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
