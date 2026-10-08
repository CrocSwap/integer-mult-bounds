#!/usr/bin/env python3
"""Quick concrete PR67-cost + PR68-live-anchor candidate generation.

Exact paid profiles/arithmetic are screened first; deferred full replay is
explicitly recorded. Rohan Arun's PR67 cost/oracle, Dominik Scholz's PR68
live anchors, and all PR57/60/62 graph/compiler notices remain applicable.
Prepared with substantial OpenAI GPT-6 Astra assistance. Apache-2.0.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
import argparse
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PR67=HERE.parent/'slot-cost-rank-pair'
sys.path.insert(0,str(ROOT/'scripts/experiments'))
import binary_frame_math as arithmetic
from binary_frame_profile_prepare import prepare
from binary_frame_replay import replay


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h',required=True,type=int,choices=(23,25))
    parser.add_argument('--full-replay',action='store_true')
    args=parser.parse_args()
    for name,digest in json.loads((HERE/'preserved-manifest.json').read_text()).items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name+' changed'
    work=HERE/'build';work.mkdir(exist_ok=True)
    oracle=work/'profile-oracle'
    profiler=work/'profiles'
    for source,binary in ((HERE/'profile_oracle.cpp',oracle),(ROOT/'scripts/experiments/binary_frame_profiles.cpp',profiler)):
        if not binary.exists():
            subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17',
                '-I',str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),str(source),'-o',str(binary)],check=True)
    records_path=HERE/'frame-compiler.json'
    if not records_path.exists():
        records=json.loads((PR67/'frame-compiler.json').read_text())
        records['source_sha256']={}
        records['artifact_sha256']={}
        for h in (23,25):
            for prefix,suffix in (('frame-word-','.json.gz'),('frame-profiles-','.json'),('frame-transitions-','.json')):
                shutil.copyfile(PR67/f'{prefix}{h}{suffix}',HERE/f'{prefix}{h}{suffix}')
    else:
        records=json.loads(records_path.read_text())
    compiler=load(HERE/'compiler.py','cost_live_compiler')
    compiler.graph=load(ROOT/'research/pair-assembly/pair_graph.py','pinned_cost_live_graph').graph
    compiler.ORACLE_EXE=str(oracle)
    compiler.ORACLE_INPUT=str(work/f'oracle-{args.h}.bin')
    compiler.oracles=[]
    try:
        compiled,word=compiler.compile_(args.h,matching=True,reclaim=True,dirty=args.full_replay)
    finally:
        for proc in compiler.oracles:
            proc.stdin.close()
            assert proc.wait()==0
    compiled.pop('seconds')
    raw=(json.dumps(word,separators=(',',':'))+'\n').encode()
    packed=HERE/f'frame-word-{args.h}.json.gz'
    with packed.open('wb') as stream:
        with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0) as archive:
            archive.write(raw)
    if args.full_replay:
        receipt=replay(packed)
    else:
        receipt=dict(roles=compiled['roles'],rank_mass=compiled['rank_mass'],
                     status='PENDING independent complete dirty-basis replay')
    transitions=work/f'word-{args.h}.bin'
    prepared=prepare(packed,transitions)
    (HERE/f'frame-transitions-{args.h}.json').write_text(json.dumps(prepared,indent=2)+'\n')
    subprocess.run([str(profiler),str(transitions)],check=True)
    prof=json.loads(Path(str(transitions)+'.profiles.json').read_text())
    (HERE/f'frame-profiles-{args.h}.json').write_text(json.dumps(prof,indent=2)+'\n')
    records['axes'][str(args.h)]=dict(compiled=compiled,replay=receipt,
        compiler='cost-live-composition/compiler.py',compiler_sha256=sha256((HERE/'compiler.py').read_bytes()).hexdigest(),
        gzip_sha256=sha256(packed.read_bytes()).hexdigest(),word_sha256=sha256(raw).hexdigest())
    records_path.write_text(json.dumps(records,indent=2)+'\n')
    constructor=load(ROOT/'research/pair-assembly/frame/frame_verify.py','cost_live_profile')
    constructor.check_sources()
    profiles=[json.loads((HERE/f'frame-profiles-{h}.json').read_text()) for h in (23,25)]
    constructor.WIRES_S=2*4073300+sum(4073300//f['v']*f['R'] for f in profiles)
    constructor.MASS_S=575*constructor.WIRES_S-1846900
    profile=constructor.profile(profiles,records)
    exact=load(PR67/'arithmetic/refine.py','pr67_exact_moment')
    rows=profile['child_multiplicities']
    scale=10**18
    low,high=5100000*10**7,5110000*10**7
    while low+1<high:
        mid=(low+high)//2
        check=exact.exact_moment(575,profile['W'],rows,Q(mid,scale))
        if check['upper']<1:low=mid
        elif check['lower']>1:high=mid
        else:raise ArithmeticError('Fine moment enclosure inconclusive')
    ab=Q(low,scale)
    accepted=exact.exact_moment(575,profile['W'],rows,ab)
    rejected=exact.exact_moment(575,profile['W'],rows,Q(high,scale))
    assert accepted['upper']<1<rejected['lower']
    bridge=json.loads((PR67/'paired-candidate.json').read_text())['finite_bridge']
    bridge['bit']['W']=profile['W']
    result=exact.assemble(bridge,ab,Q(1,10**12),scale)
    kappa=result['kappa']
    old=Q(10206752116843,2*10**17)
    pending=[h for h in (23,25) if records['axes'][str(h)]['replay'].get('status','').startswith('PENDING')]
    coarse_ab=Q(low//10**7,10**11)
    coarse=exact.assemble(bridge,coarse_ab,Q(1,10**12),10**11)
    candidate=dict(status='Concrete exact candidate; full replay PENDING' if pending else 'Full focused finite candidate',
        pending_full_replay_axes=pending,kappa=kappa,bit_saving=ab,
        preferred=result,coarse_grid=dict(bit_saving=coarse_ab,**coarse),
        bit=profile,accepted_moment=accepted,rejected_moment=rejected,finite_bridge=bridge,
        comparison=dict(pr67_commit='b3745601e947a94316bf25c2c6263d93c06e3364',pr67_kappa=old,difference=kappa-old,
                        pr68_kappa=Q(5102938,10**11)),
        source_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in
            (HERE/'compiler.py',HERE/'profile_oracle.cpp',Path(__file__),PR67/'arithmetic/refine.py',
             ROOT/'research/pair-assembly/pair_graph.py')},
        scope='Paid profile and exact arithmetic; explicitly pending dirty replay and broad tests. All inherited theorem interfaces remain conditional.')
    (HERE/'candidate.json').write_text(json.dumps(arithmetic.js(candidate),indent=2,sort_keys=True)+'\n')
    print('CONCRETE CANDIDATE',args.h,'kappa',kappa,'bit',ab,'difference PR67',kappa-old,
          'coarse',coarse['kappa'],'pending dirty axes',pending,flush=True)


if __name__=='__main__':
    main()
