#!/usr/bin/env python3
"""Reject this all-role echo recurrence and quantify unchanged supplier ceilings."""
import argparse
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]


def need(ok,message):
    if not ok:raise ValueError(message)


def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def main():
    need(__debug__,'Pinned rational moment engine requires assertions; do not use -O')
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    pins=load('price_provenance',HERE/'provenance.py').check()
    echo=load('priced_echo',HERE.parent/'cyclic-dirty-commutator-audit/echo.py')
    boundaries=load('exact_boundaries',HERE/'boundaries.py')
    rows=[]
    for n in (2,3,4,8,16,64,512):
        for fanout in sorted({2,8,n}):
            depth,N=echo.resources(n,fanout);W=2*((depth+3)//2);calls=3*(W//2)*N
            profile={1:calls};mass=calls;deficit=W*n-mass
            coefficient=Q(calls,W*n)
            need(N>=4*n-4 and coefficient>=Q(6*n-6,n)>1 and deficit<0,'noncontractive complete bill')
            rows.append(dict(factors=n,fanout=fanout,roles=W,borrowed_depth=depth,echo_leaves=N,
                             optimistic_one_call_leaf_children=calls,profile=profile,rank_mass=mass,rank_deficit=deficit,
                             moment_at_saving_zero=coefficient,all_nonnegative_savings_rejected=True))
    # Cost omission: a raw shear appears cheap if restored spectators are
    # counted as successfully transformed output roles. Functional controls
    # separately expose their unchanged outputs.
    n=8;W=10;N=echo.resources(n,8)[1]
    false_coefficient=Q(N,W*n);correct_coefficient=Q(3*N,2*n)
    need(false_coefficient<1<correct_coefficient,'missing all-role contract cost control')
    # The older local quadratic count is not the supplier child histogram.
    engines=ROOT/'research/complex-k492-owner-repair/vendor/multicold/engines'
    M=load('integration_moment',engines/'moment.py')
    bit=json.loads((ROOT/'research/e8-bit-p111-tuned/tune/EXPECTED.json').read_text())['nine']
    complex_=json.loads((HERE.parent/'gauge44-notri-fine-grid/evidence/CERTIFICATE.json').read_text())
    profiles={'bit':(64,bit['bit']['live'],{int(k):v for k,v in bit['profile'].items()},True,Q(bit['bit_lower'])),
              'complex':(73,7168,{int(k):v for k,v in complex_['global_profile'].items()},False,Q(complex_['complex_lower']))}
    targets=[];brackets={}
    for name,(m,W,H,bad,lower) in profiles.items():
        accepted=M.moment(H,m,W,lower,bad);rejected=M.moment(H,m,W,lower+Q(1,10**24),bad)
        need(accepted[1]<1<rejected[0],'supplier adjacent root bracket '+name)
        upper=lower+Q(1,10**24)
        brackets[name]=dict(lower=lower,upper=upper,upper_kappa_ceiling=upper/(1+upper),upper_kappa_decimal=M.decimal(upper/(1+upper)))
        for kappa in (Q(1,500),Q(1,200),Q(1,100)):
            required=kappa/(1-kappa);lo,hi=M.moment(H,m,W,required,bad)
            need(lo>1,'existing supplier unexpectedly reaches target')
            reduction=(lo-1)/lo
            targets.append(dict(supplier=name,kappa_target=kappa,necessary_supplier_saving=required,
                                current_moment=[lo,hi],current_moment_decimal=[M.decimal(lo),M.decimal(hi)],
                                optimistic_uniform_bill_reduction_lower=reduction,
                                reduction_percent_lower=M.decimal(100*reduction),
                                caveat='Diagnostic uniform scaling of every paid term including fallback, with fixed m and live volume. Not a feasible deletion or an admitted replacement profile.'))
    need(profiles['bit'][4]<Q(1,500)/(1-Q(1,500)),'bit cap control')
    result=dict(status='REJECT_DIRECT_ECHO_SUPPLIER_NO_KAPPA_GAIN',inherited_source_hashes=pins['files'],adapter_profiles=rows,
                omission_control=dict(false_raw_shear_coefficient=false_coefficient,complete_all_role_coefficient=correct_coefficient),
                unchanged_supplier_brackets=brackets,target_budgets=targets,
                newton_boundary=boundaries.newton_boundary(),finite_field_boundary=boundaries.bit_field_boundary(),
                cost_scope='Even granting one recursive child per additive leaf and zero scalar, routing, phase, preparation and precision cost, the complete all-role adapter has moment at least 6-6/n>1. Actual lowering can only add costs. This rejects this adapter, not all structural integration routes.')
    args.out.write_text(json.dumps(result,indent=2,default=str)+'\n')
    for row in targets:
        print(row['supplier'],'target',float(row['kappa_target']),'requires >',float(row['optimistic_uniform_bill_reduction_lower']*100),'percent uniform bill reduction')
    print(result['status'])


if __name__=='__main__':main()
