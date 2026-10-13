"""Independent bounded-minor/center accounting audit; no profiler rerun.
The exact all-minor argument is dimension-general PR32/PR34 inherited math.
This script certifies h25 arithmetic and optionally reads an explicitly supplied
fresh DAG/profile. No producer imports or sibling-checkout paths are used.
With no input arguments only reproducible CRT unit controls run. Source
adaptation retains icekylinx PR32/36 and the cited prior compiler credits.
"""
from hashlib import sha256
from math import comb,factorial,gcd,isqrt,prod
from pathlib import Path
import argparse,json,struct,sys

H=25


def prime(e):
    assert all(e%d for d in range(2,isqrt(e)+1))
    p=2**e-1;s=4
    for _ in range(e-2):s=(s*s-2)%p
    assert s==0
    return p


def pivots(matrix,p):
    A=[[x%p for x in row] for row in matrix];result=[]
    for i,row in enumerate(A):
        j=next((j for j in range(len(row)-1,-1,-1) if row[j]),None)
        if j is None:continue
        result.append((i,j))
        for k in range(i+1,len(A)):
            ratio=A[k][j]*pow(row[j],p-2,p)%p
            A[k]=[(x-ratio*y)%p for x,y in zip(A[k],row)]
    return result


def merge(profiles,n):
    def ne(i,j):return max(sum(r<i and c>=j for r,c in P) for P in profiles)
    result=[]
    for i in range(n):
        for j in range(n):
            indicator=ne(i+1,j)-ne(i,j)-ne(i+1,j+1)+ne(i,j+1)
            assert indicator in (0,1)
            if indicator:result.append((i,j))
    return result


def run(dag=None, record=None, profile=None, profiler_source=None):
    if sys.flags.optimize:
        raise RuntimeError("Run exact audit without -O")
    zmax=3*(H+1)-10
    bounds={1:dict(D=12*(H+1),B=2*zmax+24*(H+1)+4*(H-1)*zmax),
            2:dict(D=3*(H+1)*(H-1),B=zmax+12*(H+1)+4*(H-2)*zmax+3*(H+1)),
            3:dict(D=6*(H+1),B=4*zmax)}
    denoms={1,6*(H+1)};checks=0
    for c in (1,2):
        s=3-c
        for n in range(1,H-c+1):
            D=3*(H+1)*(s*s+(c-1)*n);denoms.add(D)
            assert D<=bounds[c]['D']
            for row in ('core','out','neither'):
                for col in ('core','out','neither'):
                    oi=int(row=='out');oj=int(col=='out')
                    wi=3+int(row=='core');zj=3*(H+1)*int(col=='core')-10
                    numerator=s*oi*zj+3*(H+1)*s*wi*oj+n*wi*zj-3*(H+1)*(c-1)*oi*oj
                    assert abs(numerator)<=bounds[c]['B'];checks+=1
    D0=max(x['D'] for x in bounds.values());B0=max(x['B'] for x in bounds.values())
    Dmax=D0**2;Bmax=2*D0*B0
    bound=sum(comb(H,j)*factorial(j)*Bmax**j*Dmax**(4-j) for j in range(5))
    primes=[prime(e) for e in (61,31,19,17,13)];modulus=prod(primes)
    assert modulus>bound and min(primes)>D0
    assert all(gcd(d,p)==1 for d in denoms for p in primes)
    # Dmax is an upper bound, NOT a common denominator divisible by all D.
    assert 390 in denoms and Dmax%390!=0
    assert max(len(pivots([[5,0],[0,7]],p)) for p in (5,7))==1
    assert 35==5*7 # missing rational determinant is exactly the forbidden bound case
    profiles=[pivots([[5,7],[0,0]],p) for p in (5,7)]
    assert merge(profiles,2)==[(0,1)]
    assert len(set().union(*map(set,profiles)))==2
    crt=dict(status='PASS independent h25 CRT unit controls',h=H,
        frame_bounds=bounds,uniform_frame=dict(D=D0,B=B0),
        difference=dict(rank_correction=4,D_upper=Dmax,B_upper=Bmax),
        all_minor_integer_bound=bound,bound_bits=bound.bit_length(),
        primes=primes,prime_product=modulus,product_bits=modulus.bit_length(),
        frame_denominators=sorted(denoms),membership_checks=checks,
        negative_controls=['D_upper is not an actual common denominator',
            'insufficient CRT product misses rational rank','pivot union corrupts profile'])
    if dag is None:
        if any(x is not None for x in (record,profile,profiler_source)):
            raise ValueError('Artifact replay requires dag, record and profile together')
        return crt
    if record is None or profile is None:
        raise ValueError('Artifact replay requires dag, record and profile together')
    dag=Path(dag);record_path=Path(record);profile_path=Path(profile)
    raw=dag.read_bytes();h,v,n,q=struct.unpack_from('<4I',raw)
    assert (h,v,q)==(H,comb(H,3),3*comb(H,3)+H)
    offset=16
    def read(code,count):
        nonlocal offset
        values=struct.unpack_from('<'+str(count)+code,raw,offset)
        offset+=struct.calcsize('<'+str(count)+code)
        return values
    args=read('I',2*n);core=read('Q',n);cover=read('Q',n)
    roots=read('I',q);kinds=read('I',q);active=read('B',n)
    assert offset==len(raw)
    centers=[roots[j] for j,k in enumerate(kinds) if k]
    assert len(centers)==H and len(set(centers))==H
    assert len(set(core[x] for x in centers))==H
    for x in centers:
        assert active[x] and core[x].bit_count()==1 and cover[x]==(1<<H)-1
        assert cover[x].bit_count()-core[x].bit_count()==H-1
    c=sum(bool(args[2*x]) and bool(active[x]) for x in range(n))
    record=json.loads(record_path.read_text())
    original=record['original']
    assert (c,q,v)==(original['c'],original['q'],original['v'])
    assert original['R']==c+q-original['matched']
    assert original['loss']==H*(H-1)
    assert original['histogram'][H]==H and original['histogram'][H-1]==H
    profile=json.loads(profile_path.read_text())
    assert profile['h']==H and profile['R']==original['R']
    assert profile['rank_sum']==original['rank_sum']==H*original['R']+2*H*(H-1)
    assert profile['blocks'][H]==H
    assert profile['distinct_matrices']==profile['crt_matrices']
    fixed=list(profile['blocks']);fixed[H]-=H;fixed[1]+=H
    assert all(x>=0 for x in fixed)
    assert sum(i*x for i,x in enumerate(fixed))==H*original['R']+H*(H-1)
    assert all(fixed[i]==profile['blocks'][i] for i in range(H+1) if i not in (1,H))
    # In particular do NOT replace the retained rank24 projector's ordered
    # blocks by a generic rank24 profile. Every old such occurrence stays.
    artifacts=dict(dag=dag,producer_record=record_path,profile=profile_path)
    if profiler_source is not None:artifacts['profiler_source']=Path(profiler_source)
    # Logical names make this derived receipt portable; the retained historical
    # review record beside this module keeps the original source-path evidence.
    return dict(**{**crt,'status':'PASS h25 CRT and copied center accounting; common basis proof separate'},
        selected_dag=dict(h=h,v=v,nodes=n,outputs=q,additions=c,centers=len(centers),
            center_rank=H-1,roles=original['R'],matching=original['matched']),
        original_fixed_profile=profile,copied_blocks=fixed,
        copied_rank_mass=sum(i*x for i,x in enumerate(fixed)),saved_rank=H*(H-1),
        artifact_sha256={name:sha256(path.read_bytes()).hexdigest() for name,path in artifacts.items()})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-dir',type=Path,help='Generated producer directory containing h25.bin/profile')
    parser.add_argument('--dag',type=Path,help='Explicit DAG; overrides work-dir default')
    parser.add_argument('--record',type=Path,help='Combined producer report or producer-input-25.json')
    parser.add_argument('--profile',type=Path,help='Explicit completed profile; overrides work-dir default')
    parser.add_argument('--profiler-source',type=Path,help='Optional profiler C++ source to bind by hash')
    parser.add_argument('--output',type=Path,help='Write exact portable receipt; otherwise JSON to stdout')
    args=parser.parse_args()
    dag=args.dag or (args.work_dir/'h25.bin' if args.work_dir else None)
    profile=args.profile or (Path(str(dag)+'.h25_five_prime_profiles.json') if dag else None)
    result=run(dag,args.record,profile,args.profiler_source)
    encoded=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.output:args.output.write_text(encoded)
    else:print(encoded,end='')


if __name__=='__main__':main()
