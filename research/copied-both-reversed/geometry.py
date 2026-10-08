#!/usr/bin/env python3
"""Complete both-fixed reversed23/25 geometry, with exact bad-prime controls.

PR34 James Chang: reversed prescriptions and all-weight rank cuts. PR32/36
icekylinx: fixed I+J profiling and copied centers. PR37/39 and all earlier
source credits retained. New contribution: exhaustive simultaneous fixed
pair compatibility, with complete alternate-prime replay for unlucky pairs.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
from hashlib import sha256
import argparse,importlib.util,json,os,shlex,subprocess,tempfile,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PARENT_COMMIT='70ae24129649f6d6d4ec6360962a80c3c42a38f1'


def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()


def sources():
    result=json.loads((HERE/'geometry-source.json').read_text())
    assert result['parent_commit']==PARENT_COMMIT
    for name,digest in result['sha256'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,'Changed geometry source: '+name
    assert result['archived_run_receipt']['source_sha256']==result['sha256']['research/copied-both-reversed/geometry.cpp']
    return result


def replay_cpp():
    mount=Path('/Volumes/SP AI 01_16');workspace=mount/'CodexWorkspaces'
    if ROOT.resolve().is_relative_to(workspace):assert mount.is_mount() and os.access(workspace,os.W_OK)
    work=ROOT/'build/copied-both-reversed';work.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='geometry-',dir=work) as name:
        tmp=Path(name);env=os.environ.copy();env['TMPDIR']=str(tmp);env['CLANG_MODULE_CACHE_PATH']=str(tmp/'clang-cache')
        binary=tmp/'geometry';compiler=shlex.split(os.environ.get('CXX','c++'))
        subprocess.run([*compiler,'-O3','-std=c++17',str(HERE/'geometry.cpp'),'-o',str(binary)],check=True,env=env,capture_output=True,text=True)
        completed=subprocess.run([str(binary)],check=True,env=env,capture_output=True,text=True)
        return json.loads(completed.stdout)


def rational_pair(left,right,expected):
    a,b=23,25;m=a*b;d=a+b-1;R=list(range(a))+[a-1]+list(range(a));C=list(range(a))+[0]+list(range(a))
    def weights(h,T):
        p=[Q(i in T)+3 for i in range(h)];xi=[(Q(i in T)-Q(10,3*(h+1)))/2 for i in range(h)]
        assert sum(v*w for v,w in zip(p,xi))==1
        return [v*w for v,w in zip(p,xi)]
    x,y=weights(a,left),weights(b,right)
    A=[[Q(R[i]==C[j])/x[R[i]]+Q(i%b==(m-d+j)%b)/y[i%b]-1 for j in range(d)] for i in range(d)]
    available=set(range(d));values=[]
    for i in range(d):
        j=max(j for j in available if A[i][j]);assert j==expected[i]
        value=A[i][j];assert value;values.append(value);available.remove(j)
        for r in range(i+1,d):
            if A[r][j]:
                factor=A[r][j]/value
                for c in available:A[r][c]-=factor*A[i][c]
                A[r][j]=0
    return values


def run(full=False,modular=None):
    manifest=sources()
    path=ROOT/'research/copied-reversed/geometry.py'
    spec=importlib.util.spec_from_file_location('copied_both_reversed_parent_geometry',path)
    inherited=importlib.util.module_from_spec(spec);spec.loader.exec_module(inherited)
    geometry=inherited.run();assert geometry['profile']==[1]*9+[21,17,481]
    perms=geometry['permutations'];a,b,m=23,25,575
    # Actual index identities transfer ANY local matrix. Fixed source-line
    # scales below are checked for every individual line, without genericity.
    for i in range(a):
        for j in range(a):
            assert (perms[i%b][i//b],perms[(m-a+j)%b][(m-a+j)//b],i%b,(m-a+j)%b)==(i,j,i,j+2)
    assert [perms[i%b][i//b] for i in range(b)]==list(range(a))+[22,0]
    assert [perms[(m-b+j)%b][(m-b+j)//b] for j in range(b)]==[22,0]+list(range(a))
    centers=[];line_counts={};weights={}
    for h in (a,b):
        line_count=0
        for T in combinations(range(h),3):
            p=[Q(i in T)+3 for i in range(h)];xi=[(Q(i in T)-Q(10,3*(h+1)))/2 for i in range(h)]
            assert all(p) and all(xi) and sum(v*w for v,w in zip(p,xi))==1;line_count+=1
        line_counts[h]=line_count
        weights[h]=dict(inside=str(2*(1-Q(10,3*(h+1)))),outside=str(-Q(5,h+1)))
        for center in range(h):
            p=[Q(j==center)+Q(2,h-9) for j in range(h)]
            xi=[Q(h-9,12)*(1-3*Q(j==center)) for j in range(h)]
            assert sum(v*w for v,w in zip(p,xi))==1
            assert [x-sum(p)/9 for x in p]==[Q(j==center)-Q(1,3) for j in range(h)]
            v=[x+sum(p) for x in p];nu=[x-sum(xi)/(h+1) for x in xi]
            assert v==[Q(j==center)+Q(3*h-7,h-9) for j in range(h)]
            assert nu==[Q(h-9,3*(h+1))-Q(h-9,4)*Q(j==center) for j in range(h)]
            assert all(v) and all(nu) and sum(x*y for x,y in zip(v,nu))==1
            centers.append(dict(h=h,center=center,primal=[str(x) for x in v],dual=[str(x) for x in nu],rank_one=True))
    assert line_counts=={23:1771,25:2300}
    if modular is None:modular=json.loads((HERE/'geometry-certificate.json').read_text())['modular']
    assert sha256(canonical(modular)).hexdigest()==manifest['modular_sha256'],'Changed saved modular witness'
    if full:assert replay_cpp()==modular,'Complete Cartesian replay mismatch'
    assert modular['dimensions']==[23,25] and modular['pairs']==1771*2300==4073300
    assert modular['nonzero_prefixes']==modular['pairs']*47==191445100
    assert modular['ordered_zero_checks']==modular['pairs']*346==1409361800
    assert modular['unresolved_failures']==0
    assert modular['primes']==[1000003,2147483647,1000000007]
    assert modular['successful_pairs_by_prime']==[4073290,10,0]
    assert modular['primary_modular_failures']==len(modular['fallbacks'])==10
    left=list(combinations(range(23),3));right=list(combinations(range(25),3));seen=set();rational=[]
    for item in modular['fallbacks']:
        index=item['index'];assert index not in seen;seen.add(index)
        assert tuple(item['left'])==left[index//2300] and tuple(item['right'])==right[index%2300]
        vals=rational_pair(item['left'],item['right'],geometry['pivots'])
        row,col=item['primary_zero'];assert geometry['pivots'][row]==col
        value=vals[row];primary=modular['primes'][0];fallback=item['successful_prime']
        assert value and value.numerator%primary==0 and value.denominator%primary!=0
        assert fallback==2147483647
        assert all(v.numerator%fallback and v.denominator%fallback for v in vals)
        rational.append(dict(index=index,left=item['left'],right=item['right'],primary_zero=item['primary_zero'],
            exact_nonzero_value=str(value),all_rational_pivots=[str(v) for v in vals],successful_prime=fallback))
    receipt=manifest['archived_run_receipt']
    assert receipt['exit_code']==0
    for key in ('pairs','nonzero_prefixes','ordered_zero_checks','primary_modular_failures','unresolved_failures','successful_pairs_by_prime','primes','denominators'):
        assert receipt[key]==modular[key]
    return dict(status='COMPLETE ACTUAL BOTH-FIXED FAMILY CERTIFICATE; INHERITED UNIVERSAL ZERO IDENTITIES RETAINED',
        dimensions=[23,25],fixed_bases=['I23+J23','I25+J25'],data_profile=geometry['profile'],
        modular=modular,line_counts={str(k):v for k,v in line_counts.items()},line_weights={str(k):v for k,v in weights.items()},
        center_complements=centers,rational_bad_prime_controls=rational,
        inherited_geometry_sha256=sha256(canonical(geometry)).hexdigest(),
        parent_commit=PARENT_COMMIT,source_sha256=manifest['sha256'],
        scope='Both factor bases and controlled permutations are fixed. Every actual pair is covered; no generic-factor argument remains. Default checks pinned saved full-run evidence and exact rational controls; --full replays every pair. Zero identities, physical profiles and machine interfaces are separate inherited obligations.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--full',action='store_true');parser.add_argument('--output',type=Path);args=parser.parse_args();started=time.monotonic()
    result=run(full=args.full)
    if args.output:args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:assert result==json.loads((HERE/'geometry-certificate.json').read_text())
    print('PASS both-fixed geometry:4073300 pairs,191445100 prefixes,10 exact bad-prime controls; replay='+str(args.full)+'; elapsed_seconds='+str(time.monotonic()-started))
