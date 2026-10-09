#!/usr/bin/env python3
"""Independent literal replay, fixed-basis CRT profiles and exact comparison.

The second axis is the unchanged PR71/73 certified h25 word/profile. This script
makes no all-size machine-transfer claim. Assertions must remain enabled.
"""
import argparse,gzip,hashlib,json,subprocess,sys,time
from pathlib import Path
from itertools import combinations
from collections import Counter
from fractions import Fraction as Q
from math import comb
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
PIN='253ecc88faeed55a950c76026d1fe67a7f690123'

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def scatter_binding(d):
    h,v,R=d['h'],d['v'],d['R'];triples=list(combinations(range(h),3))
    assert len(triples)==v and set(map(int,d['sources']))==set(range(v))
    assert len(set(d['sources'].values()))==v
    assert all(type(s) is int and 0<=s<R for s in d['sources'].values())
    expected=[];seen=set();central=0
    for s,f,c,t in d['outputs']:
        assert type(s) is int and 0<=s<R and s not in seen;seen.add(s)
        assert type(f) is int and 0<=f<len(d['frames']) and 0<=c<h
        if len(t)==1:
            assert t==[c];central+=1;destinations=[i for i,x in enumerate(triples) if c in x]
        else:
            assert len(t)==3 and t==sorted(t) and c in t
            destinations=[triples.index(tuple(t))]
        expected.extend([v+i,2*v+s] for i in destinations)
    assert central==h and d['scatter']==expected,'Unbound or malformed scatter'
    return dict(status='PASS',copied_centers=central,scatter_xors=len(expected),output_records=len(seen),
                scatter_sha256=hashlib.sha256(json.dumps(expected,separators=(',',':')).encode()).hexdigest())
def assemble(profiles):
    a,b=23,25;m=a*b;N=comb(a,3)*comb(b,3)
    W=2*N+sum(N//f['v']*f['R'] for f in profiles)
    parts={'data':Counter({1:18*N,21:2*N,17:2*N,481:2*N}), 'paid_endpoint_copy':Counter({1:N})}
    for f in profiles:
        h=f['h'];rep=N//f['v'];bank=rep*f['R']
        assert h in (23,25) and f['v']==comb(h,3) and f['crt_disagreements']==0
        assert sum(t*n for t,n in enumerate(f['blocks']))==h*f['R']+h*(h-1)==f['rank_sum']
        parts[f'internal_{h}']=Counter({t:n*rep for t,n in enumerate(f['blocks']) if t and n})
        parts[f'exterior_{h}']=Counter({h:bank,m-2*h:bank})
        parts[f'data_growth_{h}']=Counter({1:2*N,h-2:2*N})
    rows=sum(parts.values(),Counter());mass=sum(t*n for t,n in rows.items())
    assert mass==m*W-1846900
    return dict(m=m,N=N,W=W,total_rank=mass,deficit=m*W-mass,child_multiplicities=dict(sorted(rows.items())),parts=parts)
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--upstream',required=True,type=Path);p.add_argument('--candidate',required=True,type=Path)
    p.add_argument('--h',required=True,type=int,choices=(23,25));p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();root=a.upstream.resolve();a.output.mkdir(parents=True,exist_ok=True)
    assert subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()==PIN
    assert not subprocess.check_output(['git','-C',str(root),'status','--porcelain','--untracked-files=no'],text=True).strip()
    here=root/'scripts/experiments';sys.path.insert(0,str(here))
    from split_pair_compose import check_sources
    from split_pair_arithmetic import refine
    from binary_frame_replay import replay
    from binary_frame_profile_prepare import prepare
    import binary_frame_math as arithmetic
    check_sources()
    arithmetic.exactness(23); arithmetic.exactness(25)
    word=a.candidate/f'balanced-split-word-{a.h}.json.gz';meta=json.loads((a.candidate/f'balanced-split-{a.h}.json').read_text())
    raw=gzip.decompress(word.read_bytes());assert hashlib.sha256(raw).hexdigest()==meta['word_sha256']
    assert digest(word)==meta['gzip_sha256'];d=json.loads(raw)
    scatter=scatter_binding(d);start=time.monotonic();r=replay(word)
    print('PASS full dirty basis and scalar outputs:',time.monotonic()-start,flush=True)
    assert r['roles']==meta['compiled']['roles'] and r['rank_mass']==meta['compiled']['rank_mass']
    binary=a.output/f'balanced-split-{a.h}.bin';prepared=prepare(word,binary)
    assert prepared['word_sha256']==meta['word_sha256']
    profiler=a.output/'profiles'
    subprocess.run(['c++','-O3','-std=c++17','-I',str(root/'references/frame-compiler/pr48/scripts/partial_swap'),str(here/'binary_frame_profiles.cpp'),'-o',str(profiler)],check=True)
    subprocess.run([str(profiler),str(binary)],check=True)
    prof=json.loads(Path(str(binary)+'.profiles.json').read_text())
    assert prof['R']==r['roles'] and prof['rank_sum']==prepared['rank_mass'] and prof['field_prime']==2**61-1
    baseline=[json.loads((root/f'certificates/split-pair-profiles-{h}.json').read_text()) for h in (23,25)]
    old=assemble(baseline);new=assemble([prof if f['h']==a.h else f for f in baseline])
    public_path=root/'research/round6-pr71/parameter-certificate.json';public=json.loads(public_path.read_text())
    assert old['W']==public['bit']['W'] and old['child_multiplicities']=={int(t):n for t,n in public['bit']['child_multiplicities'].items()}
    saving=Q(public['bit_saving'])
    old_moment=refine.exact_moment(old['m'],old['W'],old['child_multiplicities'],saving)
    new_moment=refine.exact_moment(new['m'],new['W'],new['child_multiplicities'],saving)
    difference=dict(lower=new_moment['lower']-old_moment['upper'],upper=new_moment['upper']-old_moment['lower'])
    result=dict(status='PASS exact local word/profile and complete hybrid comparison',source_pin=PIN,h=a.h,
        experiment_sha256=digest(Path(__file__)),generator_receipt_sha256=digest(a.candidate/f'balanced-split-{a.h}.json'),
        word_sha256=meta['word_sha256'],binary_sha256=digest(binary),profile_sha256=digest(Path(str(binary)+'.profiles.json')),
        public_baseline_sha256=digest(public_path),source_sha256={name:digest(here/name) for name in ('binary_frame_replay.py','binary_frame_profile_prepare.py','binary_frame_profiles.cpp')},
        scatter=scatter,replay=r,transitions=prepared,profile=prof,baseline=old,candidate=new,
        target_saving=saving,baseline_moment=old_moment,candidate_moment=new_moment,difference=difference,
        improves_at_target=difference['upper']<0,worsens_at_target=difference['lower']>0,
        scope='Finite hybrid profile only; changed axis freshly replayed/profiled, other axis and fixed data/exterior/copy geometry inherited at the pinned source. No all-size machine proof.')
    (a.output/f'comparison-{a.h}.json').write_text(json.dumps(arithmetic.js(result),indent=2)+'\n')
    print(json.dumps(dict(roles=prof['R'],old_W=old['W'],new_W=new['W'],moment_difference_approx=float((difference['lower']+difference['upper'])/2),improves=result['improves_at_target'],worsens=result['worsens_at_target'])),flush=True)
if __name__=='__main__':main()
