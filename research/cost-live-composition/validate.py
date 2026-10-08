#!/usr/bin/env python3
"""Read-only focused validation of the concrete cost/live-anchor candidate.

Adapted from Rohan Arun's PR67 verifier and inherited PR57/62 checkers.
Dominik Scholz, with substantial OpenAI GPT-6 Astra assistance. Apache-2.0.
Only validation-receipt.json and disposable build outputs are written.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
import os
from pathlib import Path
import shlex
import subprocess
import experiment

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def main():
    candidate=json.loads((HERE/'candidate.json').read_text())
    records=json.loads((HERE/'frame-compiler.json').read_text())
    for path,digest in candidate['source_sha256'].items():
        assert sha256((ROOT/path).read_bytes()).hexdigest()==digest,path+' changed'
    work=HERE/'build/validate';work.mkdir(parents=True,exist_ok=True)
    binary=work/'profiles'
    subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17',
        '-I',str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),
        str(ROOT/'scripts/experiments/binary_frame_profiles.cpp'),'-o',str(binary)],check=True)
    profiles=[];replayed={}
    for h in (23,25):
        path=HERE/f'frame-word-{h}.json.gz'
        packed=path.read_bytes();axis=records['axes'][str(h)]
        assert sha256(packed).hexdigest()==axis['gzip_sha256']
        assert sha256(gzip.decompress(packed)).hexdigest()==axis['word_sha256']
        receipt=experiment.replay(path)
        assert receipt['roles']==axis['compiled']['roles']
        assert receipt['rank_mass']==axis['compiled']['rank_mass']
        replayed[str(h)]=receipt
        transitions=work/f'word-{h}.bin'
        prepared=json.loads(json.dumps(experiment.prepare(path,transitions)))
        assert prepared==json.loads((HERE/f'frame-transitions-{h}.json').read_text())
        subprocess.run([str(binary),str(transitions)],check=True)
        prof=json.loads(Path(str(transitions)+'.profiles.json').read_text())
        assert prof==json.loads((HERE/f'frame-profiles-{h}.json').read_text())
        profiles.append(prof)
        print('PASS complete dirty-basis/frame/profile validation h='+str(h),flush=True)
    constructor=experiment.load(ROOT/'research/pair-assembly/frame/frame_verify.py','cost_live_validated_profile')
    constructor.check_sources()
    constructor.WIRES_S=2*4073300+sum(4073300//f['v']*f['R'] for f in profiles)
    constructor.MASS_S=575*constructor.WIRES_S-1846900
    fresh_records=dict(axes={h:dict(replay=r) for h,r in replayed.items()})
    profile=constructor.profile(profiles,fresh_records)
    assert experiment.arithmetic.js(profile)==candidate['bit']
    exact=experiment.load(HERE.parent/'slot-cost-rank-pair/arithmetic/refine.py','cost_live_validated_arithmetic')
    rows=profile['child_multiplicities'];ab=Q(candidate['bit_saving'])
    accepted=exact.exact_moment(575,profile['W'],rows,ab)
    rejected=exact.exact_moment(575,profile['W'],rows,ab+Q(1,10**18))
    assert experiment.arithmetic.js(accepted)==candidate['accepted_moment']
    assert experiment.arithmetic.js(rejected)==candidate['rejected_moment']
    assert accepted['upper']<1<rejected['lower']
    assembled=exact.assemble(candidate['finite_bridge'],ab,Q(1,10**12),10**18)
    assert experiment.arithmetic.js(assembled)==candidate['preferred']
    result=dict(status='PASS independent full focused finite validation; broad repository checks remain separate',
        kappa=candidate['kappa'],bit_saving=candidate['bit_saving'],
        candidate_sha256=sha256((HERE/'candidate.json').read_bytes()).hexdigest(),
        replay=replayed,profiles_equal=True,all_paid_child_multiplicities_equal=True,
        exact_adjacent_bit_bracket=True,assembly_constraints=47,assembly_margins=7,
        theorem_scope='All inherited all-size analytic/tape/compiler hypotheses remain conditional')
    (HERE/'validation-receipt.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS focused candidate kappa='+candidate['kappa'],flush=True)


if __name__=='__main__':
    main()
