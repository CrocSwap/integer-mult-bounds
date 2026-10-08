#!/usr/bin/env python3
"""Fresh literal-word replay, exact fixed-I+J profiling, and rational assembly.

Research adapter to pinned PR62, ad0f25ff7b23cff7f08ad237c2254e6ecf74257e.
The input/data geometry and all-size analytic/compiler/tape arguments are
inherited. Every supplied changed XOR word and its actual frame path is replayed.
No external network access and no mutation of the frozen source checkout.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
from itertools import combinations
import json
import gzip
from math import comb
from pathlib import Path
import subprocess
import sys
import time

if sys.flags.optimize:
    raise RuntimeError('Run the verification without Python -O/-OO; assertion checks are required.')

HERE = Path(__file__).resolve().parent
PIN = 'ad0f25ff7b23cff7f08ad237c2254e6ecf74257e'


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_source(upstream):
    expected = json.loads((HERE/'frozen-sources.json').read_text())
    adapters=expected['verification_adapter_files']
    required={'verify_words.py','batch_axes.py','screen_axes.py','check_guards.py','export_weighted_case.py'}
    if set(adapters)!=required:
        raise ValueError('missing or unexpected frozen verification adapters')
    for name,digest in adapters.items():
        if sha256((HERE/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('verification adapter changed: '+name)
    head = subprocess.check_output(['git','-C',str(upstream),'rev-parse','HEAD'], text=True).strip()
    if head != PIN:
        raise ValueError('wrong frozen PR62 source commit: '+head)
    for name, digest in expected['files'].items():
        if sha256((upstream/name).read_bytes()).hexdigest() != digest:
            raise ValueError('frozen consumed source changed: '+name)
    return expected


def check_word_structure(d):
    R,nf=d['R'],len(d['frames'])
    assert type(R) is int and R>0 and d['h'] in (23,25)
    # Explicit bounds avoid Python's negative-index interpretation of a word.
    assert all(type(s) is int and 0<=s<R for s in d['sources'].values())
    assert all(type(a) is int and type(b) is int and type(g) is int and
               0<=a<R and 0<=b<R and 0<=g<nf for a,b,g in d['ops'])
    assert all(0<=s<R and 0<=g<nf for s,g,_,_ in d['outputs'])
    assert all(0<=a<2*d['v']+R and 0<=b<2*d['v']+R for a,b in d['scatter'])
    triples=list(combinations(range(d['h']),3))
    index={t:i for i,t in enumerate(triples)}
    charged_scatter=[]
    for s,g,common,triple in d['outputs']:
        targets=([i for i,t in enumerate(triples) if common in t]
                 if len(triple)==1 else [index[tuple(triple)]])
        charged_scatter.extend((d['v']+i,2*d['v']+s) for i in targets)
    assert Counter(map(tuple,d['scatter']))==Counter(charged_scatter), 'uncharged or mismatched literal scatter'


def axis(word, output, profiler, upstream):
    started = time.monotonic()
    raw=word.read_bytes()
    d=json.loads(gzip.decompress(raw) if str(word).endswith('.gz') else raw)
    check_word_structure(d)
    replay = load_module('literal_binary_replay', upstream/'scripts/experiments/binary_frame_replay.py').replay
    prepare = load_module('literal_binary_prepare', upstream/'scripts/experiments/binary_frame_profile_prepare.py').prepare
    receipt = replay(word)
    output.mkdir(parents=True, exist_ok=True)
    transitions = output/'transitions.bin'
    prepared = prepare(word, transitions)
    subprocess.run([str(profiler),str(transitions)], check=True)
    prof = json.loads(Path(str(transitions)+'.profiles.json').read_text())
    h = prof['h']
    assert h in (23,25)
    assert prof['R'] == receipt['roles'] == prepared['R']
    assert prof['rank_sum'] == receipt['rank_mass'] == prepared['rank_mass']
    assert prof['crt_disagreements'] == 0
    assert prof['field_prime'] == 2**61-1
    assert prof['v'] == comb(h,3) and prof['loss'] == h*(h-1)
    assert sum(t*n for t,n in enumerate(prof['blocks'])) == h*prof['R']+prof['loss']
    assert prof['blocks'][h] == 0
    result = dict(status='PASS fresh full input/dirty basis both orientations, independent literal frame path, exact fixed profiles',
                  word_sha256=prepared['word_sha256'], gzip_sha256=sha256(word.read_bytes()).hexdigest(),
                  replay=receipt, prepared=prepared, profile=prof, elapsed_seconds=time.monotonic()-started)
    (output/'verified-axis.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS axis',h,'roles',prof['R'],'full_basis_vectors',receipt['full_basis_vectors'],flush=True)
    return result


def collect(axes, arithmetic):
    profiles = [x['profile'] for x in axes]
    assert sorted(x['h'] for x in profiles)==[23,25]
    a,b=23,25
    m,N=a*b,comb(a,3)*comb(b,3)
    W=2*N+sum(N//x['v']*x['R'] for x in profiles)
    L=sum(N//x['v']*x['loss'] for x in profiles)
    parts={'data':Counter({1:18*N,21:2*N,17:2*N,481:2*N}), 'paid_endpoint_copy':Counter({1:N})}
    for x in profiles:
        h=x['h']; rep=N//x['v']; bank=rep*x['R']
        parts[f'internal_{h}']=Counter({t:n*rep for t,n in enumerate(x['blocks']) if t and n})
        parts[f'exterior_{h}']=Counter({h:bank,m-2*h:bank})
        parts[f'data_growth_{h}']=Counter({1:2*N,h-2:2*N})
        arithmetic.exactness(h)
    rows=sum(parts.values(),Counter())
    mass=sum(t*n for t,n in rows.items())
    assert mass==m*W-N+L
    assert m*W-mass==1846900 and max(rows)==529
    assert all(0<t<m and n>0 for t,n in rows.items())
    return dict(m=m,N=N,W=W,L=L,total_rank=mass,deficit=m*W-mass,maxchild=max(rows),
                child_multiplicities=dict(sorted(rows.items())),parts=parts,axes=profiles)


def choose_saving(p, arithmetic, denominator):
    # Optimize the exact *upper enclosure*, not a floating logarithm or root.
    lo,hi=0,denominator//10000
    rows=p['child_multiplicities']
    while lo+1<hi:
        mid=(lo+hi)//2
        if arithmetic.moment(p['m'],p['W'],rows,Q(mid,denominator))['upper']<1:
            lo=mid
        else:
            hi=mid
    assert lo>0
    return Q(lo,denominator)


def compose(p, upstream, arithmetic, saving, kappa, h, denominator):
    old=upstream/'references/frame-compiler/pr48/research/copied-fixed'
    balanced=load_module('balanced_candidate_arithmetic',old/'balanced_assembly.py')
    prior=json.loads((old/'certificate.json').read_text())
    bridge=deepcopy(prior['finite_bridge'])
    bridge['bit'].update(W=p['W'],maxchild=p['maxchild'],m=p['m'],wire_bits=p['W'].bit_length(),
                         halving_degree=balanced.halving_degree(p['m'],p['maxchild']))
    coefficient=sum(bridge[name]['halving_degree']*bridge[name]['wire_bits'] for name in ('bit','complex'))
    bridge['rows'].update(coefficient=coefficient,degree_gap=str(Q(bridge['rows']['degree'])-Q(51,25)*coefficient))
    assert Q(bridge['rows']['suffix_slope'])==4*Q(bridge['rows']['degree'])
    moment=arithmetic.moment(p['m'],p['W'],p['child_multiplicities'],saving)
    assert moment['upper']<1
    if kappa is None:
        q=saving*(1-2*h)
        control=(1-h)*q/(1+q)
        scaled=control*denominator
        floor=scaled.numerator//scaled.denominator
        # The floor is already strictly below a nonintegral rational control.
        # Back off one grid point only if the control itself lies on the grid.
        kappa=Q(floor-(scaled.denominator==1),denominator)
    assembled=balanced.assembly(bridge,saving,kappa,h=h,a_complex=Q(717,10**7))
    assert len(assembled['constraints'])==47 and len(assembled['margins'])==7
    assert all(v>0 for v in assembled['constraints'].values())
    frozen=json.loads((upstream/'research/pair-assembly/frame/frame-certificate.json').read_text())
    frozen_ab=Q(frozen['bit_saving']); frozen_kappa=Q(frozen['kappa'])
    prior_rows={int(t):n for t,n in frozen['bit']['child_multiplicities'].items()}
    prior_moment=arithmetic.moment(frozen['bit']['m'],frozen['bit']['W'],prior_rows,saving)
    return dict(status='PASS exact characteristic upper enclosure, all 47 strict constraints and seven margins',
                bit_saving=saving,kappa=kappa,explicit_h=h,bit=dict(p,moment=moment),assembly=assembled,
                finite_bridge=bridge,eventual_bounds=balanced.cutoffs(bridge,assembled),
                exactness=[arithmetic.exactness(x) for x in (23,25)],
                comparison=dict(frozen62_bit_saving=frozen_ab,frozen62_kappa=frozen_kappa,
                                kappa_gain=kappa-frozen_kappa,roles_frozen62=[27918,36586],
                                frozen62_refined_kappa=Q(25508460085039,500000000000000000),
                                kappa_gain_above_refined=kappa-Q(25508460085039,500000000000000000),
                                frozen62_network_at_new_saving_lower=prior_moment['lower'],
                                frozen62_network_rejected_at_new_saving=prior_moment['lower']>1),
                scope='Fresh changed-word/full-basis/frame/profile/CRT and rational arithmetic validation. '
                      'Unchanged 4,073,300-pair data geometry and its recovered rational cases inherited from PR62; '
                      'all-size analytic log/exp enclosure, compiler/frame transfer, finite-alphabet tape, routing, '
                      'prime-selection/recovery and eventual setup arguments remain conditional.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream',type=Path,required=True)
    parser.add_argument('--profiler',type=Path,default=HERE/'frame-profiles.exe')
    parser.add_argument('--word23',type=Path)
    parser.add_argument('--word25',type=Path)
    parser.add_argument('--receipt23',type=Path,help='Previously fresh verified-axis.json for inexpensive recomposition')
    parser.add_argument('--receipt25',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--axis-only',action='store_true')
    parser.add_argument('--saving',type=Q)
    parser.add_argument('--kappa',type=Q)
    parser.add_argument('--h',type=Q,default=Q(1,10**18))
    parser.add_argument('--denominator',type=int,default=10**19)
    args=parser.parse_args()
    sys.dont_write_bytecode=True
    upstream=args.upstream.resolve(); args.output.mkdir(parents=True,exist_ok=True)
    source=check_source(upstream)
    arithmetic=load_module('exact_candidate_math',upstream/'scripts/experiments/binary_frame_math.py')
    axes=[]
    for h,word,cached in [(23,args.word23,args.receipt23),(25,args.word25,args.receipt25)]:
        assert not (word is not None and cached is not None)
        if word is not None:
            axes.append(axis(word.resolve(),args.output/f'h{h}',args.profiler.resolve(),upstream))
        elif cached is not None:
            receipt=json.loads(cached.read_text())
            assert receipt['status'].startswith('PASS fresh full') and receipt['profile']['h']==h
            receipt['reused_verified_receipt_sha256']=sha256(cached.read_bytes()).hexdigest()
            axes.append(receipt)
    if args.axis_only:
        return
    assert len(axes)==2
    p=collect(axes,arithmetic)
    saving=args.saving or choose_saving(p,arithmetic,args.denominator)
    result=compose(p,upstream,arithmetic,saving,args.kappa,args.h,args.denominator)
    result['source']=source
    result['fresh_word_receipts']=axes
    result['verifier_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    (args.output/'candidate-certificate.json').write_text(json.dumps(arithmetic.js(result),indent=2,sort_keys=True)+'\n')
    print('PASS kappa',str(result['kappa']),float(result['kappa']),'W',p['W'],'saving',str(saving),flush=True)


if __name__=='__main__':
    main()
