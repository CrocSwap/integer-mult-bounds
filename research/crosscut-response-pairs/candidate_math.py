#!/usr/bin/env python3
"""Exact fixed-prime arithmetic for a source-bound multicut candidate.

This additive module retains PR265's original moment engines and assembly.
It is not a substitute for the complete native physical replay. Candidate
profile counts are recounted from the native price and literal invoice.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse, hashlib, importlib.util, json, sys

if sys.flags.optimize:
    raise SystemExit('assertions required')
sys.dont_write_bytecode=True
PRIMITIVES_SHA256='fb8f2cf17eec6e9996200f01d4f11e2d4f45a2d98d96105c7113ff5c58108125'
ENGINE_HASHES={
    'moment':'9d465c716c6b910ff66e1453e3bf0057608a787b5f5361be93781f42cb3370f7',
    'base_two_moment':'aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098',
    'outer':'c1ebb52163a7219504c728a5c2b098bf1e50bf20148a2879c5a74c3cadc7c03c',
}
BASELINE_KAPPA=Q(711032242134072007667807,10**27)

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def compute(native_price, invoice, repository, primitives_path, baseline_mathematics,
            require_improvement=True):
    repository=Path(repository)
    primitives_path=Path(primitives_path)
    assert digest(primitives_path)==PRIMITIVES_SHA256, 'retained PR265 primitives changed'
    spec=importlib.util.spec_from_file_location('retained_pr265_primitives',primitives_path)
    retained=importlib.util.module_from_spec(spec);spec.loader.exec_module(retained)
    assert retained.ETA==Q(1,10**24) and retained.BETA==Q(1,10**9)
    assert retained.GRID==10**27 and retained.PRIME==(1<<127)-1
    assert retained.M==120 and retained.RHO==Q(3456000,retained.PRIME)
    engines={}
    for name,sha in ENGINE_HASHES.items():
        path=retained.source_path(repository,name)
        assert digest(path)==sha, 'retained arithmetic source changed: '+name
        engines[name]=retained.load('candidate_'+name,path)
    cost,other,outer=(engines[k] for k in ('moment','base_two_moment','outer'))
    assert native_price['status']=='PASS_EXACT_COHORT_CONDITIONAL_PRICING_47_AND_ADJACENT_CONTROLS'
    assert invoice['status']=='PASS_COHORT_LITERAL_FIVE_STAGE_FINITE_INVOICE_AND_POSITIVE_CUTOFFS'
    assert Q(baseline_mathematics['kappa'])==BASELINE_KAPPA
    p=native_price['cohort_candidate']
    h={int(r):int(n) for r,n in p['histogram'].items()}
    assert all(0<r<60 and n>0 for r,n in h.items())
    stock,calls,mass,deficit=(int(p[k]) for k in ('stock','calls','rank_mass','deficit'))
    assert stock>0 and sum(h.values())==calls and sum(r*n for r,n in h.items())==mass
    assert 120*stock-mass==deficit==35200
    literal={int(r):int(n) for r,n in invoice['literal_histogram'].items()}
    assert literal=={r:5*n for r,n in h.items()}, 'literal/normalized histogram mismatch'
    assert invoice['physical_replicas']==40 and invoice['literal_stock']==5*stock
    assert invoice['normalized_stock']==stock and int(invoice['literal_rank_mass'])==5*mass
    assert int(invoice['literal_deficit'])==5*deficit
    assert int(invoice['positive_rank_children'])==sum(literal.values())==5*calls
    coefficient=int(invoice['full_counted_primitive_coefficient'])
    assert 0<coefficient<2**80<retained.PRIME and stock<retained.PRIME
    assert 0<int(invoice['extra_selector_calls'])<2**40
    assert 0<int(invoice['new_chart_factor_max'])<=548
    assert int(invoice['normalizer_factor_bound'])==787
    assert invoice['external_complex_row_coefficient']==20161
    assert invoice['internal_row_coefficient']==14401
    assert invoice['simultaneous_extra_work_streams']==1
    assert 0<int(invoice['payload_signed_prefix_upper'])<2**104

    # Preserve the exact original PR249 regression, which the unchanged native
    # price checker rebuilds by subtracting the complete candidate delta.
    assert Q(native_price['baseline']['kappa'])==Q(88799023305857,125000000000000000)
    native_c=Q(p['coarse'])
    native_chain=[retained.INITIAL_LEAF]
    for _ in range(3):native_chain.append((1-native_c)*native_c+native_c*native_chain[-1])
    assert list(map(str,native_chain))==p['bootstrap_chain']
    assert native_chain[-1]==Q(p['ordinary_bit'])
    native_assembly=outer.assembly(native_chain[-1],retained.COMPLEX_SAVING,
                                  retained.bridge_template(),Q(p['kappa']),
                                  eta=Q(1,10**12),beta=retained.BETA)
    assert p['positive_constraints']==47 and int(p['next_kappa_rejected'])>0

    coarse,next_coarse,first,first_next,second,second_next=retained.certify_coarse(
        h,120,stock,calls,cost,other)
    cap=retained.grid_kappa(coarse)
    chain=[retained.INITIAL_LEAF];gaps=[]
    for level in range(1,21):
        old=chain[-1];new=(1-coarse)*coarse+coarse*old
        assert old<new<coarse<1-new
        row=dict(atom=coarse-new,borrowing=1-new-coarse,
                 remainder=1-new-coarse*(1-old),stock=1-coarse)
        assert min(row.values())>0
        chain.append(new);gaps.append(dict(level=level,gaps=row,minimum_gap=min(row.values())))
        assert retained.grid_kappa(new)<=cap
        if retained.grid_kappa(new)==cap:break
    else:raise AssertionError('finite chain did not reach coarse grid cap in twenty levels')
    assembly=outer.assembly(chain[-1],retained.COMPLEX_SAVING,
                            retained.bridge_template(),cap,eta=retained.ETA,beta=retained.BETA)
    assert len(assembly['strict_constraints'])==47 and len(assembly['margins'])==7
    assert min(assembly['strict_constraints'].values())>0
    assert min(assembly['margins'].values())>cap
    for rate in (chain[-1],coarse):
        try:
            outer.assembly(rate,retained.COMPLEX_SAVING,retained.bridge_template(),
                           cap+Q(1,retained.GRID),eta=retained.ETA,beta=retained.BETA)
        except AssertionError:pass
        else:raise AssertionError('adjacent kappa grid point admitted')
    delta_tau=1-first[1]
    delta_linear=1-Q(mass,120*stock)-retained.RHO*Q(32*120*calls,stock)
    assert delta_tau>0 and delta_linear>0
    cuts=[];log_coefficient=(coefficient-1).bit_length()
    for row in gaps:
        delta=row['minimum_gap']
        cutoff=max(1,retained.ceil_fraction(Q(36)/delta**2),
                   retained.ceil_fraction(Q(2*(4+log_coefficient))/delta))
        assert Q(cutoff)*delta**2>=36 and Q(cutoff)*delta>=2*(4+log_coefficient)
        cuts.append(dict(level=row['level'],minimum_gap=delta,log2_cutoff=cutoff))
    gain=cap-BASELINE_KAPPA
    assert gain>0 if require_improvement else gain==0
    return retained.serial(dict(
        schema='crosscut-fixed-prime-candidate-mathematics/1',
        status='PASS_EXACT_ARITHMETIC_AND_FINITE_INVOICE',
        full_physical_replay_claimed=False,
        prime=retained.PRIME,rare_density=retained.RHO,full_fallback_kept=True,
        eta=retained.ETA,beta=retained.BETA,grid=retained.GRID,
        retained_primitive_sha256=PRIMITIVES_SHA256,retained_engine_hashes=ENGINE_HASHES,
        bit_profile=dict(m=120,stock=stock,calls=calls,rank_mass=mass,deficit=deficit,
                         histogram=h,maxchild=max(h),physical_replicas=40,normalization=5),
        coarse_rate=dict(exact_grid_rate=coarse,bracket=[coarse,next_coarse],
                         first_engine_interval=first,first_engine_next_interval=first_next,
                         second_engine_interval=second,second_engine_next_interval=second_next),
        ordinary_bootstrap=dict(initial=chain[0],levels=level,chain=chain,gaps=gaps),
        native_assembly=native_assembly,assembly=assembly,
        finite_admission=dict(coefficient=coefficient,delta_tau=delta_tau,
                              delta_linear=delta_linear,finite_cutoff_checks=cuts,
                              literal_invoice=invoice),
        kappa=cap,baseline_kappa=BASELINE_KAPPA,exact_gain=gain,
        adjacent_grid_point_rejected_at_finite_saving=True,
        adjacent_grid_point_rejected_at_coarse_cap=True,
        scope='Conditional on unchanged inherited all-size interfaces; full native physical replay must separately bind these inputs.'))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--native-price','--price',dest='price',type=Path,required=True)
    ap.add_argument('--invoice',type=Path,required=True)
    ap.add_argument('--repository','--runtime',dest='runtime',type=Path,required=True)
    ap.add_argument('--primitives',type=Path,
                    default=Path(__file__).resolve().parent.parent /
                    'multicut-kernel-condensation-descent-fixed-prime/fixed_prime_math.py')
    ap.add_argument('--baseline-certificate','--baseline',dest='baseline',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--baseline-regression',action='store_true')
    a=ap.parse_args()
    read=lambda p:json.loads(p.read_text())
    result=compute(read(a.price),read(a.invoice),a.runtime,a.primitives,
                   read(a.baseline)['mathematics'],not a.baseline_regression)
    assert not a.output.exists(), 'use a fresh output path'
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','kappa','baseline_kappa','exact_gain')}))

if __name__=='__main__':main()
