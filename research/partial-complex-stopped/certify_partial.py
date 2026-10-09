#!/usr/bin/env python3
"""Portable exact arithmetic certificate for the selected partial-σ complex profile.

Conditional on the separately stated bit/complex construction and retained analytic
interfaces. Standard-library Python only. Inputs and extracted PR104 functions are
SHA-256 pinned in MANIFEST.json.
"""
import argparse
from collections import Counter
import hashlib
import gzip
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'vendor'))
from copied_centers_network import finite_bridge
from partial_swap_network import moment
from structured_bulk_assembly import assembly,halving,js

OLD=Q(384599,10**10)
ATOM=Q(1,1000)
BIT_ATOM=Q(15513,125000000)
OLD_LEAF_DEGREE=252


def read(path):return json.loads(path.read_text())


def check_manifest():
    manifest=read(HERE/'MANIFEST.json')
    for rel,expected in manifest['package_sha256'].items():
        assert hashlib.sha256((HERE/rel).read_bytes()).hexdigest()==expected, rel
    return manifest


def profile(raw,hist_key):
    h,m,W,N=(int(raw[k]) for k in ('h','m','W','N'))
    hist=raw[hist_key]
    hist=dict(hist) if isinstance(hist,list) else hist
    hist={int(w):int(n) for w,n in hist.items()}
    assert m==h*h and W>0 and N>0
    assert all(0<w<m and n>0 for w,n in hist.items())
    mass=sum(w*n for w,n in hist.items())
    assert mass==int(raw['rank_sum'])
    assert W*m-mass==int(raw['deficit'])>0
    return dict(h=h,m=m,W=W,N=N,total_rank=mass,maxchild=max(hist),
                deficit=W*m-mass,child_multiplicities=hist)


def rebuild_complex_histogram(raw, matched, selected_ranks):
    """Exact physical child recurrence from PR108 matched roles and partial σ steps."""
    h,v,R=(int(matched[k]) for k in ('h','v','R'))
    m=h*h;N=v*v;W=2*N+2*v*R
    assert (h,v,R,m,N,W)==(raw['h'],raw['v'],raw['R'],raw['m'],raw['N'],raw['W'])
    original=list(matched['histogram'])
    assert len(original)==h+1 and sum(r*n for r,n in enumerate(original))==h*R+2*matched['loss']
    assert original[h]>=h and matched['loss']==h*(h-1)
    original[1]+=h;original[h]-=h
    assert sum(r*n for r,n in enumerate(original))==h*R+matched['loss']
    C=Counter({m-h:2*v*R,(h-1)**2:2*N,h-1:4*N,1:N})
    for r,n in enumerate(original):
        if r:C[r]+=2*v*n
    assert selected_ranks['h']==h and selected_ranks['v']==v
    assert len(selected_ranks['roles'])==raw['active_sigma_roles']
    transitions=Counter();per_target=[set() for _ in range(v)]
    for u,old,d,bits_hex in selected_ranks['roles']:
        assert 0<d<=old<h
        transitions[(old,d)]+=1
        bits=int(bits_hex,16)
        assert bits>0 and bits.bit_length()<=v
        while bits:
            low=bits&-bits;per_target[low.bit_length()-1].add(d);bits-=low
    assert [[old,d,n] for (old,d),n in sorted(transitions.items())]==raw['transition_counts']
    chain=Counter()
    for ds in per_target:
        seq=[0,*sorted(ds),h-1]
        chain.update(b-a for a,b in zip(seq,seq[1:]) if b>a)
    assert [[width,count] for width,count in sorted(chain.items())]==raw['chain_hist']
    for (old,d),count in transitions.items():
        assert 0<d<=old<h and count>0
        C[old]-=2*v*count
        if old>d:C[old-d]+=2*v*count
        C[m-h]-=2*v*count
        C[m-h+d]+=2*v*count
    C[h-1]-=2*N
    assert sum(width*count for width,count in chain.items())==v*(h-1)
    for width,count in chain.items():
        assert 0<width<h and count>0
        C[width]+=2*v*count
    assert all(n>=0 for n in C.values())
    C={int(width):int(count) for width,count in C.items() if count}
    assert C=={int(width):int(count) for width,count in raw['hist']}
    assert sum(width*count for width,count in C.items())==W*m-N+raw['L']
    return C


def certify(args):
    if sys.flags.optimize:
        raise RuntimeError('Run without -O: mathematical assertions must remain enabled')
    manifest=check_manifest()
    bit_raw,cx_raw=read(HERE/'inputs/bit.json'),read(args.complex_profile)
    meta=read(HERE/'inputs/complex-meta.json')
    matched=read(HERE/'inputs/matched.json')
    selected_ranks=json.loads(gzip.decompress((HERE/'inputs/selected-ranks.json.gz').read_bytes()))
    rebuilt_complex_histogram=rebuild_complex_histogram(cx_raw,matched,selected_ranks)
    bit,cx=profile(bit_raw,'histogram'),profile(cx_raw,'hist')
    assert bit['m']==529 and bit['maxchild']==528
    assert Q(*bit_raw['atom_saving_certified'])==BIT_ATOM
    bm=moment(bit['m'],bit['W'],bit['child_multiplicities'],BIT_ATOM,True)
    assert bm['strict_gap']>0
    assert Q(bit['total_rank'],bit['W']*bit['m'])<1
    assert 0<OLD<BIT_ATOM<ATOM<1
    bit_saving=(1-ATOM)*BIT_ATOM+ATOM*OLD
    assert bit_saving==Q(*bit_raw['ordinary_saving'])
    assert ATOM>bit_saving and BIT_ATOM>bit_saving
    assert cx['h']==meta['h'] and cx['N']==cx_raw['v']**2
    assert cx_raw['R']==meta['expected_R']
    assert cx['total_rank']==cx['W']*cx['m']-cx['N']+cx_raw['L']
    assert rebuilt_complex_histogram==cx['child_multiplicities']
    assert cx_raw['maxchild']==cx['maxchild']
    assert len(cx_raw['hist'])==meta['expected_positive_width_bins']
    assert cx_raw['endpoint_copy_children']==cx['N']
    assert cx_raw['data_front_children']==4*cx['N']
    assert dict(cx_raw['hist'])[1]>=cx['N']
    assert cx_raw['active_sigma_roles']==meta['expected_active_sigma_roles']
    assert sum(n for d,n in cx_raw['sigma_dimension_histogram'] if d>0)==meta['expected_active_sigma_roles']
    assert sum(n for d,n in cx_raw['sigma_dimension_histogram'])==cx_raw['all_sigma_roles']
    assert cx_raw['raw_pickle_sha256']==meta['selected_source_pickle_sha256']
    assert cx_raw['selection_sha256']==meta['selected_sigma_sha256']
    assert Q(cx['total_rank'],cx['W']*cx['m'])<1
    ac=Q(args.complex_saving) if args.complex_saving else Q(*cx_raw['saving'])
    cm=moment(cx['m'],cx['W'],cx['child_multiplicities'],ac,True)
    assert cm['strict_gap']>0
    h,c_src,q_src,decoder=(meta[k] for k in ('h','scalar_c','scalar_q','decoder_denominator'))
    pairs,ops,G=(meta[k] for k in ('adjoint_pairs_per_invocation','operations_per_pair','scalar_group_upper'))
    max_num=meta['maximum_coefficient_numerator']
    assert h==cx['h'] and decoder==h-3 and decoder==21
    assert max_num>0 and ops>=2*max_num.bit_length()+4
    row=dict(h=h,v=cx_raw['v'],c=c_src)
    assert c_src+q_src==matched['baseline_R']
    assert matched['R']==cx_raw['R']
    for key,value in meta['required_schedule_counts'].items():
        assert cx_raw[key]==value, key
    bridge=finite_bridge(bit,cx,[row,row])
    old_G=bridge['complex']['scalar_group_upper']
    min_G=old_G+2*cx_raw['v']*pairs*ops
    assert G>=min_G
    m,W,s,r=(cx[k] for k in ('m','W','total_rank','maxchild'))
    E=64*(W+m+G+1)**3
    charge=2*G*W*W+8*s+4*W+4+32*m
    B=s+E;C0=32*m*B*B;induction=2*B*(m-r)-s-E
    assert charge<E and induction>0 and 2*B+18<C0
    bridge['complex'].update(scalar_group_upper=G,
        baseline_scalar_group_upper=old_G,
        new_deferred_signed_adjoint_pairs_per_invocation=pairs,
        operations_per_adjoint_pair=ops,maximum_coefficient_numerator=max_num)
    bridge['semantic'].update(E=E,literal_charge=charge,strict_literal_gap=E-charge,
        B=B,C0=C0,C1=1,induction_gap=induction,decoder_denominator=decoder,
        fixed_odd_divisor=decoder,
        exact_grid='2^(-P)21^(-K), K=G(D+1); no child rounding')
    tb,tc=halving(bit['m'],bit['maxchild']),halving(m,r)
    coeff=tb*bit['W'].bit_length()+tc*W.bit_length()+OLD_LEAF_DEGREE
    degree=1000*((51*coeff)//25000+1)
    assert Q(degree)>Q(51*coeff,25)
    bridge['rows'].update(coefficient=coeff,degree=degree,suffix_slope=4*degree,
        degree_gap=Q(degree)-Q(51*coeff,25),ordinary_leaf_row_degree=OLD_LEAF_DEGREE,
        contract='W_complex^D_complex * W_whole_rank_bit^D_bit * W_old^D_old; common prefix, sequential reuse')
    beta,eta=Q(args.beta),Q(args.eta)
    a=min(bit_saving,(1-beta)*ac-Q(args.bit_leaf_gap))
    assert 0<a<=bit_saving
    q=a*(1-2*eta);c=q*(1+eta);eps=(1-eta)/(1+c+q);g=eps*q
    scale=10**args.kappa_digits
    kappa=Q((g*scale).numerator//(g*scale).denominator-1,scale)
    assert kappa>0
    assembled=assembly(a,ac,bridge,kappa,eta=eta,beta=beta)
    assert len(assembled['strict_constraints'])==47 and len(assembled['margins'])==7
    return dict(status='Conditional exact partial-complex stopped assembly',
        source_commits=manifest['source_commits'],source_sha256=manifest['package_sha256'],
        bit=dict(profile=bit,atom_saving=BIT_ATOM,atom_moment_gap=bm['strict_gap'],
            atom_rank_moment=Q(bit['total_rank'],bit['W']*bit['m']),
            ordinary_saving=bit_saving,ordinary_leaf_saving=OLD,stop_fraction=ATOM),
        complex=dict(profile=cx,saving=ac,moment_gap=cm['strict_gap'],
            rank_moment=Q(cx['total_rank'],cx['W']*cx['m']),source_counts=meta,
            active_sigma_roles=cx_raw['active_sigma_roles'],selection_sha256=cx_raw['selection_sha256'],
            source_pickle_sha256=cx_raw['raw_pickle_sha256'],endpoint_copy_children=cx['N'],
            data_front_children=4*cx['N']),
        bridge=bridge,halving=dict(bit=tb,complex=tc,old=9),assembly=assembled,
        kappa=kappa,previous_kappa=Q(469537,5*10**9),
        gain=kappa-Q(469537,5*10**9))


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--complex-profile',type=Path,default=HERE/'inputs/complex.json')
    p.add_argument('--complex-saving')
    p.add_argument('--beta',default='1/1000000')
    p.add_argument('--bit-leaf-gap',default='1/10000000000')
    p.add_argument('--eta',default='1/100000000')
    p.add_argument('--kappa-digits',type=int,default=13)
    p.add_argument('--output',type=Path,default=HERE/'certificate.json')
    args=p.parse_args(); result=certify(args)
    args.output.write_text(json.dumps(js(result),sort_keys=True,indent=2)+'\n')
    print('kappa',result['kappa'],float(result['kappa']))
    print('gain',float(result['gain']))
    print('bit atom moment gap',float(result['bit']['atom_moment_gap']))
    print('complex moment gap',float(result['complex']['moment_gap']))
    print('scalar G',result['bridge']['complex']['scalar_group_upper'])
    print('row degree',result['bridge']['rows']['degree'],'constraints',len(result['assembly']['strict_constraints']))

if __name__=='__main__':main()
