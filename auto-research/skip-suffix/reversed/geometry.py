"""Exact PR34 reversed23/25 geometry controls for a proposed PR36 transfer.
Does not prove the copied-center producer/count integration by itself.
"""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util,json,random,types
HERE=Path(__file__).resolve().parent
SOURCE=HERE/'pr34'


def load(name,file):
    m=types.ModuleType(name);m.__file__=str(file)
    # macOS rejects the inherited RLIMIT_AS setter; omit only host resource caps.
    source='\n'.join(line for line in file.read_text().splitlines() if not line.startswith('resource.setrlimit('))
    exec(compile(source,str(file),'exec'),m.__dict__);return m


def tree(edges,n):
    par=list(range(n))
    def find(x):
        while x!=par[x]:x=par[x]
        return x
    for x,y in edges:
        x,y=find(x),find(y);assert x!=y;par[x]=y
    assert len(edges)==n-1 and len({find(x) for x in range(n)})==1


def run():
    manifest=json.loads((HERE/'geometry-source.json').read_text())
    assert manifest['commit']=='7fecbe3651e095fb0f450756afdeefd2a9ee80a2'
    for name,digest in manifest['sha256'].items():
        assert sha256((HERE/name).read_bytes()).hexdigest()==digest, 'Pinned PR34 source changed: '+name
    checked=load('pr34_independent_reversed23',SOURCE/'independent_controls.py')
    author=load('pr34_author_reversed23',SOURCE/'certify_reversed.py')
    h=23;b=25;m=h*b;d=h+b-1
    rows,cols=checked.corner_labels(h);pivots=checked.expected_pivots(h)
    perms=checked.completion(h,rows,cols)
    cuts=checked.check_cuts(h,rows,cols,pivots)
    independent=[checked.witness(h,rows,cols,k) for k in (1,2)]
    authored=author.certify(h)
    assert authored['pivots']==pivots and authored['permutation_completions']==perms
    assert authored['profile']==[1]*9+[21,17,481]
    tree([(r,h+beta) for r,beta in rows],h+b)
    tree([(c,h+gamma) for c,gamma in cols],h+b)
    rng=random.Random(23025)
    def line(n):
        p=[Q(rng.randrange(1,30)) for _ in range(n)];x=[Q(rng.randrange(1,30)) for _ in range(n)];z=sum(v*w for v,w in zip(p,x));return p,[w/z for w in x]
    p,xi=line(h);v,nu=line(b)
    P=[[x*y for y in xi] for x in p];B=[[x*y for y in nu] for x in v]
    I=[[Q(i==j) for j in range(h)] for i in range(h)];J=[[Q(i==j) for j in range(b)] for i in range(b)]
    A=[[Q(rng.randrange(-9,10),rng.randrange(1,8)) for j in range(h)] for i in range(h)]
    D=[[Q(rng.randrange(-9,10),rng.randrange(1,8)) for j in range(b)] for i in range(b)]
    def actual(X,Y,i,j):
        alpha,beta=divmod(i,b);gamma,delta=divmod(j,b)
        r=perms[beta][alpha];c=perms[delta][gamma]
        return X[r][c]*Y[beta][delta]
    for i in range(h):
        for j in range(h):
            assert actual(A,B,i,m-h+j)==v[i]*A[i][j]*nu[j+2]
            assert actual(I,B,i,m-h+j)==Q(i==j)*v[i]*nu[j+2]
    rs=[perms[i%b][i//b] for i in range(b)];cs=[perms[(m-b+j)%b][(m-b+j)//b] for j in range(b)]
    assert rs==list(range(h))+[h-1,0] and cs==[h-1,0]+list(range(h))
    for i in range(b):
        for j in range(b):
            assert actual(P,D,i,m-b+j)==p[rs[i]]*D[i][j]*xi[cs[j]]
            assert actual(P,J,i,m-b+j)==Q(i==j)*p[rs[i]]*xi[cs[j]]
    # The actual off-diagonal large-projector corner is minus its null corner.
    for i in range(d):
        for j in range(d):
            r,beta=rows[i];c,gamma=cols[j]
            null=actual(P,J,i,m-d+j)+actual(I,B,i,m-d+j)-actual(P,B,i,m-d+j)
            expected=Q(beta==gamma)*p[r]*xi[c]+Q(r==c)*v[beta]*nu[gamma]-p[r]*xi[c]*v[beta]*nu[gamma]
            assert null==expected
    assert (m-d)%b==3 and (m-d)%b!=b-1
    assert any(actual(I,B,i,m-h+i)!=v[i]*nu[i] for i in range(h))
    return dict(status='PASS EXACT REVERSED23/25 GEOMETRY; PR36 PHYSICAL INTEGRATION SEPARATE',
                dimensions=[h,b],m=m,d=d,rank=m-d,profile=[1]*9+[21,17,481],
                permutations=perms,rows=rows,columns=cols,pivots=pivots,cuts=cuts,
                rational_controls=independent,author_witness=authored['witness'],
                physical_blocks=[dict(rows=[1,21],columns=[553,573]),dict(rows=[28,44],columns=[530,546]),dict(rows=[47,527],columns=[47,527])],
                actual_local_and_auxiliary_contractions=True,actual_null_corner=True,both_trees=True,
                negative_controls=['incorrect_unshifted_auxiliary_formula','old_25_23_data_residue_offset'],
                source_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in [SOURCE/'independent_controls.py',SOURCE/'certify_reversed.py']})


if __name__=='__main__':
    result=run();(HERE/'geometry-certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],result['profile'],len(result['cuts']))
