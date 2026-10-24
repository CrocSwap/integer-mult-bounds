#!/usr/bin/env python3
"""Independent rational review of mixed-target outer allocations and compiler grid.
No candidate Python code is imported or executed. Standard library only.
Predecessors for exponent contracts: Jacob Alan Sussman, zxv, Cao Yifan,
Cinna Davis, and Chris R / Clear1nsight's independently transcribed PR5241
ledger preserved by PR5384. Substantial OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse, hashlib, json, platform, resource, time

def need(ok, msg):
    if not ok: raise AssertionError(msg)
def encode(x):
    if isinstance(x,Q): return str(x)
    if isinstance(x,dict): return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [encode(v) for v in x]
    return x

def family(k,s,bit=Q('.0034')):
    g=(s-k)/7
    return dict(kappa=k,tested_saving=s,complex_uniform_saving=k+6*g,
                b=k+5*g,a=k+4*g,q=k+3*g,bit_saving=bit,epsilon=1-g,
                beta=1-3*g,r0=g/10,stop=g,layout=g,d=g)

def outer(p,atom=Q('.004')):
    # Exponents are calculated from the stopping, grouping and routing rules.
    k,b,a,q,ep,be,r,stop,layout=(p[n] for n in
        ('kappa','b','a','q','epsilon','beta','r0','stop','layout'))
    sigma,tau=1-b,1-a
    internal=tau+(1-stop)*max(sigma-tau,Q(0))
    leaf=sigma+stop*(1-sigma)
    lam=1-(q+a)/2
    xi=ep*(1+q)-Q(3,32)+layout
    key=be+1-ep
    m=dict(main_transform=ep*q,global_coordinate_router=a,
      fused_gaussian=1-ep+q*be,group_bit_router=1-ep+a*be,
      group_scans=1-ep+be,boundary_algebraic_matrix=Q(3,32)+xi-ep,
      sparse_union_movement=xi+Q(1,2)-ep,polynomial_products=ep,
      microbox_face_corrections=79-ep-be)
    c=dict(actual_bit_above_effective=p['bit_saving']-a,
      complex_above_effective=b-a,q_positive=q,complex_endpoint=b-q,
      q_below_effective=a-q,stop_positive=stop,stop_below_one=1-stop,
      leaf_saving_above_effective=(1-stop)*b-a,
      q_below_internal=1-internal-q,q_below_leaf=1-leaf-q,
      lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,
      lambda_above_internal=lam-internal,lambda_prime_above_lambda=1-q-lam,
      lambda_prime_above_leaf=1-q-leaf,epsilon_positive=ep,
      epsilon_below_one=1-ep,cap_above_band=xi-Q(1,2),cap_below_cell=ep-xi,
      group_positive=be,group_below_dimension=ep-be,support_router_span=1-be,
      group_gauge_power_slack=3-2*xi-r-be,
      actual_logarithmic_group_guard=3-2*xi-be,
      global_gamma_power_slack=1-ep-r,actual_logarithmic_gamma_guard=1-ep,
      alpha_logarithm_absorption=r,group_key_fits_record=1-key,
      membership_arithmetic_fits_record=1-be-2*(1-ep),
      microbox_halo_volume=80-be,positive_layout_slack=layout,
      short_record_fallback=ep-a,complex_below_one_over_32=Q(1,32)-b,
      strassen_integer_power_gap=Q(2**45-7**16),
      theta_positive_polynomial_power=Q(2),cap_below_phase_cell_power=2-xi,
      halo_covers_generic_inverse_radius=Q(5),union_tag_work_per_visit_fits_record=1-be,
      union_header_fits_record=1-be,source_axis_superpolynomial=1-ep,
      gaussian_above_main=m['fused_gaussian']-m['main_transform'],
      new_complex_uniform_saving_above_b=p['complex_uniform_saving']-b,
      improvement_over_user_baseline=k-Q('.001730970419199163702738'),
      new_semantic_guard_with_C1_one=1-ep,fine_prime_halo_umbrella=Q(7,2))
    c.update({n+'_above_kappa':v-k for n,v in m.items()})
    f=dict(new_semantic_group_guard=1-be,
      new_BIT_row_stock_sublinear_in_active_group=be*Q(997,1000),
      fixed_halo_explicit_metadata_branch=79-ep-be,
      actual_new_BIT_stock_sublinear=be*(1-atom))
    return dict(parameters=dict(p,cap_xi=xi,lambda_=lam,lambda_prime=1-q),
                margins=m,strict_checks=c,functional_checks=f)

def compiler(k,s,reserve,record=None):
    gap=(s-k)/7
    need(gap>0 and gap.numerator==1,'positive unit-fraction compiler grid')
    step=gap.denominator
    power,v=1000,1024
    def wins(j):return (step*j+1)**power<2**j
    left,right=1,2
    while not wins(right): left,right=right,2*right
    while right-left>1:
        mid=(left+right)//2
        if wins(mid):right=mid
        else:left=mid
    H=step*right
    normalized=1/(1+v*reserve)+Q(4,2**32)
    checks=dict(height_above_8v=H>8*v,integer_success=wins(right),
      preceding_integer_grid_fails=not wins(right-1),
      rounding_and_completion_funded=normalized<1,
      strict_uniform_below_tested=k+6*gap<s,
      completion_decay=4*Q(97,100)**v<Q(4,2**32),
      block_decay=Q(97,100)**128<Q(1,16),
      target_splitting=20**64<21**63,
      shifted_exits=2*20**(v*64)<=145**(v*63))
    need(all(checks.values()),'compiler arithmetic capacity')
    if record:
        need(Q(record['gap'])==gap,'recorded gap')
        need(record['H']==H and record['integer_test_exponent']==right,'recorded compiler threshold')
        need(Q(record['uniform_saving'])==k+6*gap,'recorded uniform saving')
    # A strictly concave log(step*j+1)-j*log(2)/power has one positive
    # crossing after f(0)=0 and f(1)>0. A success and previous failure
    # prove the least winning positive integer grid index, not least arbitrary H.
    return dict(gap=gap,step=step,j=right,H=H,N_encoding='2^'+str(H),
      checks=checks,normalized_paid_upper=normalized,rounding_reserve=1-normalized,
      reserve_must_exceed=Q(4,2**32)/(v*(1-Q(4,2**32))),
      word_materialized=False,threshold_scope='Least winning integer j on H=step*j for this sufficient inequality; no globally optimal compiler claim.')

def run(name,path,bit_source):
    raw=path.read_bytes(); rec=json.loads(raw); ar=rec.get('arithmetic',rec)
    k,s=Q(ar['kappa']),Q(ar['strictification']['tested'])
    reserve=Q(ar['strictification']['reserve'])
    p=family(k,s); out=outer(p)
    need(len(out['strict_checks'])==54 and len(out['functional_checks'])==4,'54+4 inventory')
    need(all(v>0 for g in ('strict_checks','functional_checks') for v in out[g].values()),'strict outer funding')
    for g in ('margins','strict_checks','functional_checks'):
        need(out[g]=={n:Q(v) for n,v in ar['outer'][g].items()},'record equality '+g)
    need(all(Q(ar['outer']['parameters'][n])==v for n,v in p.items()),'recorded parameter family')
    comp=compiler(k,s,reserve,ar['compiler'])
    controls={}
    for label,patch in [('insufficient_BIT',{'bit_saving':Q('.0027')}),
        ('closed_BIT',{'bit_saving':p['a']}),('closed_uniform',{'complex_uniform_saving':p['b']}),
        ('unfunded_endpoint',{'kappa':s}),('closed_epsilon',{'epsilon':Q(1)}),
        ('missing_layout',{'layout':Q(0)})]:
        bad=outer(dict(p,**patch))
        failures={n:v for n,v in bad['strict_checks'].items() if v<=0}
        need(failures,'reject '+label);controls[label]=failures
    try:compiler(k,s,Q(1,10**13))
    except AssertionError:controls['unfunded_rounding']='rejected by normalized paid bound'
    else:raise AssertionError('unfunded rounding accepted')
    controls['lower_compiler_integer_grid']='rejected by independently evaluated strict integer inequality at j-1'
    try:compiler(s,s,reserve)
    except AssertionError:controls['closed_compiler_gap']='rejected by positive gap requirement'
    else:raise AssertionError('closed compiler gap accepted')
    bit=ar['ordinary_BIT']; need(bit==bit_source,'retained source BIT record unchanged'); atom=Q(bit['atom'])
    ordinary=(1-atom)*Q(bit['after_cover'])+atom*Q('.0000384599')
    need(ordinary==Q(bit['ordinary_saving']),'ordinary BIT interpolation')
    need(atom==Q('.004') and atom>ordinary>Q(bit['admitted'])>s and atom<1-ordinary,'BIT chain and active stock')
    need(Q(bit['admitted'])==p['bit_saving'],'same retained BIT admission')
    margins=out['margins']; limiter=min(margins,key=margins.get)
    return dict(status='PASS_INDEPENDENT_OUTER_AND_FINITE_COMPILER_ARITHMETIC',candidate=name,
      source_path=str(path.resolve()),source_sha256=hashlib.sha256(raw).hexdigest(),
      kappa=k,tested=s,reserve=reserve,outer=out,compiler=comp,controls=controls,
      limiting_outer_row=limiter,limiting_outer_headroom=margins[limiter]-k,
      minimum_strict_slack=min(out['strict_checks'].values()),
      BIT=dict(atom=atom,ordinary=ordinary,admitted=Q(bit['admitted']),
        effective_required=p['a'],headroom=Q(bit['admitted'])-p['a'],
        positive_sublinear_active_stock=0<p['beta']*(1-atom)<1),
      saving_order=dict(tested_above_uniform=s>p['complex_uniform_saving'],
        uniform_above_b=p['complex_uniform_saving']>p['b'],b_above_a=p['b']>p['a'],
        a_above_q=p['a']>p['q'],q_above_kappa=p['q']>k),
      unexecuted=['Independent invoice and alpha/gamma/delta/eta intervals delegated to pricing lane',
        'Physical/native/all-size applicability delegated to other review lanes',
        'No global optimum or selected-frontier promotion; no expanded word materialized'])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--candidate',action='append',nargs=2,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--bit-source',type=Path,required=True)
    args=ap.parse_args();t=time.monotonic();bit_source=json.loads(args.bit_source.read_bytes())['ordinary_BIT']
    result=dict(status='PASS_SCOPED_ARITHMETIC',candidates=[run(n,Path(p),bit_source) for n,p in args.candidate],
      python=platform.python_version(),seconds=time.monotonic()-t,
      retained_BIT_source=str(args.bit_source.resolve()),
      retained_BIT_source_sha256=hashlib.sha256(args.bit_source.read_bytes()).hexdigest(),
      maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    args.out.write_text(json.dumps(encode(result),indent=2,sort_keys=True)+'\n')
    print(json.dumps(encode({k:v for k,v in result.items() if k!='candidates'})))
if __name__=='__main__':main()
