#!/usr/bin/env python3
"""Portable exact arithmetic for a changed PR118 deferred complex profile.

Only the published PR118 bit supplier is used. The pr118_sources helper pins
the complete reused source closure before imports. This verifies arithmetic, not
the generator's scalar/frame/gauge claims. Requires this file, moments.py,
pr118_sources.py and
an unchanged PR118 source closure; the repository may have additive commits.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import moments
import pr118_sources

sys.dont_write_bytecode=True
if not __debug__:raise SystemExit('Assertions required; optimized Python is forbidden')
PIN='ec862a5af51537495c745d9f2323e8a5736ee265'
MANIFEST='9c5cc05d04537e6604a2dfa0e5f19295599df2fd6f7b72e4822eca51b854b583'
CGRID=10**14;KGRID=10**17;BACKOFF=Q(1,10**14)


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


def load(repo):
    pr118_sources.check_base(repo)
    package=repo/pr118_sources.PACKAGE
    api=module('portable_pinned_arithmetic',package/'certificate.py')
    old=api.exact()
    assert api.js(old)==json.loads((package/'certificate.json').read_text())
    moments.configure(repo)
    return api,old


def profile(p):
    p=dict(p);p['child_multiplicities']={int(t):n for t,n in p['child_multiplicities'].items()}
    assert (p['h'],p['v'],p['m'],p['N'])==(24,2024,576,2024**2)
    assert p['W']==2*p['N']+2*p['v']*p['R']
    assert p['L']==2*p['v']*24*23
    assert p['total_rank']==p['W']*p['m']-p['N']+p['L']
    assert p['deficit']==p['N']-p['L']==1862080
    z=p['child_multiplicities']
    assert all(type(t) is int and 0<t<p['m'] and type(n) is int and n>0 for t,n in z.items())
    assert max(z)==p['maxchild'] and sum(t*n for t,n in z.items())==p['total_rank']
    return p


def enclose(api,p,a):
    first=moments.exact_moment(p['m'],p['W'],p['child_multiplicities'],a)
    lo,hi=moments.independent_moment(p,a,api.js(first['terms']))
    return dict(primary=first,independent=dict(lower=lo,upper=hi))


def root(api,p):
    lo,hi=1,CGRID//1000
    while hi-lo>1:
        middle=(lo+hi)//2
        interval=moments.exact_moment(p['m'],p['W'],p['child_multiplicities'],Q(middle,CGRID))
        if interval['upper']<1:lo=middle
        elif interval['lower']>1:hi=middle
        else:raise ArithmeticError('Insufficient interval precision')
    a,b=Q(lo,CGRID),Q(hi,CGRID)
    yes,no=enclose(api,p,a),enclose(api,p,b)
    assert yes['primary']['upper']<1 and yes['independent']['upper']<1
    assert no['primary']['lower']>1 and no['independent']['lower']>1
    return dict(saving=a,next_saving=b,accepted=yes,rejected=no)


def changed_bridge(api,bit,p):
    row=dict(h=24,v=2024,c=p['additions'],central_disjoint=24)
    bridge=api.copied_bridge(bit,p,[row,row])
    local=p['safe_one_axis_scalar_groups']
    assert type(local) is int and local>0 and p['exact_clean_roots']
    assert p['adjoint_denominator']==42
    assert local==(4*p['max_coefficient_bits']+16)*p['literal_scalar_terms']
    sparse=bridge['complex']['scalar_group_upper'];G=max(sparse,4*p['v']*local)
    W,m,s=p['W'],p['m'],p['total_rank'];L=W+m+G+1
    E=64*L**3;charge=2*G*W*W+8*s+4*W+4+32*m;B=s+E;C0=32*m*B*B
    assert charge<=50*L**3<E and 2*B*(m-p['maxchild'])>=s+E and 2*B+18<C0
    bridge['complex'].update(scalar_group_upper=G,inherited_sparse_bound=sparse,
        single_stage_single_axis_bound=local,axis_stage_copies=4*p['v'],
        max_coefficient_bits=p['max_coefficient_bits'])
    bridge['semantic'].update(E=E,literal_charge=charge,strict_literal_gap=E-charge,
        B=B,C0=C0,C1=1,induction_gap=2*B*(m-p['maxchild'])-s-E,
        fixed_odd_divisor=21,
        exact_grid='Common dyadic grid times21^(-G*(Dcomplex+1)); denominator42 fixed coefficients; no child rounding')
    coarse=bridge.pop('bit');bridge['bit_coarse']=coarse;bridge['ordinary_leaf_row_degree']=252
    coeff=coarse['halving_degree']*coarse['wire_bits']+252+bridge['complex']['halving_degree']*bridge['complex']['wire_bits']
    degree=1000*((51*coeff)//25000+1)
    bridge['rows']=dict(coefficient=coeff,degree=degree,suffix_slope=4*degree,
        degree_gap=Q(degree)-Q(51*coeff,25),
        contract='Published ordinary leaf plus complete coarse/complex stock; prefix/padding; sequential reuse')
    return bridge


def assemble(api,b,bridge,ordinary):
    a=min(ordinary,(1-api.BETA)*b-BACKOFF)
    first=api.assembly(a,b,bridge,Q(1,KGRID),beta=api.BETA)
    k=Q(moments.ceiling_scaled(first['minimum_margin'],KGRID)-1,KGRID)
    full=api.assembly(a,b,bridge,k,beta=api.BETA)
    assert len(full['strict_constraints'])==47 and len(full['margins'])==7
    try:api.assembly(a,b,bridge,k+Q(1,KGRID),beta=api.BETA)
    except AssertionError as error:negative=str(error)
    else:raise AssertionError('Next kappa grid accepted')
    return dict(kappa=k,actual_bit_saving=ordinary,selected_bit_parameter=a,
        active_primitive=('bit' if a==ordinary else 'complex stopped leaf'),
        finite_bridge=bridge,assembly=full,next_kappa_rejection=negative)


def verify(repo,input_profile):
    api,baseline=load(repo)
    p=profile(json.loads(input_profile.read_text()))
    bit=baseline['bit_profile'];ordinary=baseline['actual_bit_saving']
    bitproof=enclose(api,bit,api.COARSE)
    assert bitproof['primary']['upper']<1 and bitproof['independent']['upper']<1
    price=root(api,p);bridge=changed_bridge(api,bit,p)
    selected=assemble(api,price['saving'],bridge,ordinary)
    controlprofile=profile(baseline['complex_profile']);controlprice=root(api,controlprofile)
    control=assemble(api,controlprice['saving'],baseline['finite_bridge'],ordinary)
    delta=selected['kappa']-control['kappa']
    return api.js(dict(scope=__doc__,upstream_pin=PIN,source_manifest_sha256=MANIFEST,
        grids=dict(complex=CGRID,kappa=KGRID,leaf_backoff=BACKOFF),
        complete_profile=p,complex_moment=price,published_bit_moment=bitproof,
        selected=selected,common_control=dict(profile=controlprofile,moment=controlprice,**control),
        comparison=dict(public_kappa=baseline['kappa'],common_control_kappa=control['kappa'],
            absolute_gain_over_public=selected['kappa']-baseline['kappa'],
            absolute_gain_over_common=delta,relative_gain_over_public=selected['kappa']/baseline['kappa']-1,
            relative_gain_over_common=delta/control['kappa'],
            grid_only_control_gain=control['kappa']-baseline['kappa']),
        hashes=dict(profile=sha256(input_profile.read_bytes()).hexdigest(),
            verifier=sha256(Path(__file__).read_bytes()).hexdigest(),moments=sha256(Path(moments.__file__).read_bytes()).hexdigest(),
            additional_log_source=moments.LOG_SOURCE,
            source_binding=sha256(Path(pr118_sources.__file__).read_bytes()).hexdigest())))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',type=Path,required=True)
    ap.add_argument('--profile',type=Path,required=True)
    ap.add_argument('--receipt',type=Path,required=True)
    a=ap.parse_args();assert not a.receipt.exists()
    receipt=verify(a.repo.resolve(),a.profile.resolve())
    a.receipt.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print('PASS portable exact full assembly',receipt['selected']['kappa'],
        'delta common',receipt['comparison']['absolute_gain_over_common'],flush=True)


if __name__=='__main__':main()

