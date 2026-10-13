#!/usr/bin/env python3
"""Fixed L25 compatibility in the inherited PR37 reversed23/25 common family.

Credits: James Chang PR34 prescriptions/rank cuts, icekylinx PR32 fixed I+J
and PR36 copied centers, PR37 integration and all inherited source credits.
The complete modular witness proves nonvanishing only; the inherited exact
all-weight rank cuts prove the required zero identities.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
from hashlib import sha256
import argparse,importlib.util,json,os,shlex,subprocess,tempfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PARENT_COMMIT='2f7578affce416ad4b6c41f3438ebb734f66a899'


def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()


def verify_sources():
    manifest=json.loads((HERE/'geometry-source.json').read_text())
    assert manifest['parent_commit']==PARENT_COMMIT
    for name,digest in manifest['sha256'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest, 'Geometry source changed: '+name
    return manifest


def replay_cpp():
    mount=Path('/Volumes/SP AI 01_16');workspace=mount/'CodexWorkspaces'
    # Enforce this development host's SSD policy only for its managed path.
    # Reviewers on other hosts build beneath their own checkout as usual.
    if ROOT.resolve().is_relative_to(workspace):
        assert mount.is_mount() and os.access(workspace,os.W_OK)
    work=ROOT/'build/copied-fixed-reversed';work.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='geometry-',dir=work) as name:
        tmp=Path(name);env=os.environ.copy();env['TMPDIR']=str(tmp);env['CLANG_MODULE_CACHE_PATH']=str(tmp/'clang-cache')
        binary=tmp/'geometry';compiler=shlex.split(os.environ.get('CXX','c++'))
        subprocess.run([*compiler,'-O3','-std=c++17',str(HERE/'geometry.cpp'),'-o',str(binary)],check=True,env=env,capture_output=True,text=True)
        result=subprocess.run([str(binary)],check=True,env=env,capture_output=True,text=True)
        return json.loads(result.stdout)


def run(full=False,modular=None):
    manifest=verify_sources()
    path=ROOT/'research/copied-reversed/geometry.py'
    spec=importlib.util.spec_from_file_location('copied_fixed_reversed_parent_geometry',path)
    family=importlib.util.module_from_spec(spec);spec.loader.exec_module(family)
    geometry=family.run()
    a,b=23,25;m=a*b;d=a+b-1
    assert geometry['profile']==[1]*9+[21,17,481]
    inside=Q(4,2)*(1-Q(10,3*(b+1)));outside=-Q(3,2)*Q(10,3*(b+1))
    assert (inside,outside)==(Q(68,39),Q(-5,26)) and 3*inside+(b-3)*outside==1
    forbidden=[(i,j) for i in range(4) for j in range(b-2)
               if i*inside+j*outside in (0,1) and (i,j) not in [(0,0),(3,b-3)]]
    assert not forbidden
    assert 3*Q(67,36)+(b-3)*Q(-5,48)!=1
    centers=[]
    for center in range(b):
        p=[Q(j==center)+Q(2,b-9) for j in range(b)]
        xi=[Q(b-9,12)*(1-3*Q(j==center)) for j in range(b)]
        assert sum(x*y for x,y in zip(p,xi))==1
        assert [x-sum(p)/9 for x in p]==[Q(j==center)-Q(1,3) for j in range(b)]
        v=[x+sum(p) for x in p];nu=[x-sum(xi)/(b+1) for x in xi]
        assert v==[Q(j==center)+Q(17,4) for j in range(b)]
        assert nu==[Q(8,39)-4*Q(j==center) for j in range(b)]
        assert all(v) and all(nu) and sum(x*y for x,y in zip(v,nu))==1
        perms=geometry['permutations'];rf=[perms[j%b][j//b] for j in range(b)]
        cf=[perms[(m-b+j)%b][(m-b+j)//b] for j in range(b)]
        first_p=[Q(j+1) for j in range(a)];z=sum(j*j for j in range(1,a+1));first_xi=[Q(j+1,z) for j in range(a)]
        for i in range(b):
            for j in range(b):
                alpha,beta=divmod(i,b);gamma,delta=divmod(m-b+j,b)
                actual=first_p[perms[beta][alpha]]*first_xi[perms[delta][gamma]]*v[beta]*nu[delta]
                assert actual==first_p[rf[i]]*v[i]*nu[j]*first_xi[cf[j]]
        centers.append(dict(center=center,primal=[str(x) for x in v],dual=[str(x) for x in nu],rank_one=True,actual_local_transfer=True))
    if modular is None:modular=json.loads((HERE/'geometry-certificate.json').read_text())['modular']
    assert sha256(canonical(modular)).hexdigest()==manifest['modular_sha256'], 'Saved modular certificate changed'
    if full:assert replay_cpp()==modular, 'Complete modular replay mismatch'
    assert modular['prime']==1000003
    assert [(u,v,w) for u,v,w,p in modular['records']]==list(combinations(range(b),3))
    assert all(0<p<modular['prime'] for u,v,w,p in modular['records'])
    assert modular['triple_count']==2300 and modular['nonzero_pivots']==2300*d
    assert modular['ordered_zero_checks']==2300*(21*20//2+17*16//2)
    return dict(status='COMPLETE FIXED25 NONVANISHING CERTIFICATE; GENERIC GL23 COMMON-BASIS ARGUMENT AND INHERITED ALL-WEIGHT ZEROS RETAINED',
                dimensions=[a,b],fixed_middle='I+J',triple_weights=dict(inside=str(inside),outside=str(outside)),
                modular=modular,ordinary_first_factor='generic GL23 remains free',data_profile=geometry['profile'],
                inherited_geometry_sha256=sha256(canonical(geometry)).hexdigest(),
                completed_permutations_and_restriction_trees=True,center_complements=centers,
                negative_controls=['h47 numerical triple weights fail normalization'],
                source_sha256=manifest['sha256'],parent_commit=PARENT_COMMIT,
                scope='Replay mode is invocation metadata, not a mathematical certificate field. Default validates pinned saved data and exact rational controls; --full freshly compiles/replays all2300 triples. Fixed internal profile and physical arithmetic are separate.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--full',action='store_true');parser.add_argument('--output',type=Path);args=parser.parse_args()
    result=run(full=args.full)
    if args.output:args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:assert result==json.loads((HERE/'geometry-certificate.json').read_text())
    print('PASS fixed25 geometry:2300 triples,108100 prefixes,25 copied-center complements; replay='+str(args.full))
