#!/usr/bin/env python3
"""PR21 finite interfaces with the attributed PR20 semantic/bulk transfer.

Zhihao Chen (jacklightChen), with OpenAI Codex assistance. Apache-2.0.
Arithmetic verifies the stated construction; analytic/tape proofs are dependencies.
"""
from fractions import Fraction as Q
from pathlib import Path
from math import comb
from hashlib import sha256
import argparse,json,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PRIOR=ROOT/'research/translated-partial'
REF=ROOT/'references/rad20'
sys.path.insert(0,str(PRIOR));sys.path.insert(0,str(ROOT/'scripts'))
import complex_source
from paired_complex import PairedComplex

KAPPA=Q(1099,10**8)

def ceil(x):return -(-x.numerator//x.denominator)
def js(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [js(v) for v in x]
    return x

def pinned_inputs():
    old=json.loads((PRIOR/'certificate.json').read_text())
    for name,digest in old['source_sha256'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    for name,digest in old['retained_pr18']['sha256'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    ref=json.loads((REF/'SOURCE.json').read_text())
    for name,digest in ref['source_sha256'].items():
        assert sha256((REF/name).read_bytes()).hexdigest()==digest,name
    assert Q(old['bit']['strict_gap'])>0 and Q(old['complex']['strict_moment_gap'])>0
    assert old['controls']['regenerated_producer']['regenerated_from_source']
    return old,ref

def halving(m,r):
    k=1
    while m**k<=2*r**k:k+=1
    assert m**(k-1)<=2*r**(k-1)
    return k

def finite_bridge(old):
    b=old['bit'];c=complex_source.run()
    assert Q(b['saving'])==Q(11,10**6) and c['a_c']==Q(18,10**6)
    p=PairedComplex(28);v=comb(28,3)
    # Four mixer sweeps, two source copies and two side injections, and
    # four grouped central operations per scalar invocation. Counting input
    # nodes as mixer gates overestimates rather than omits scalar work.
    G=3*v*v*(4*len(p.active)+4*v+4)
    W,m,s=c['W'],c['m'],c['s'];E=64*(W+m+1)**3
    charge=2*G*W*W+8*s+4*W+4+32*m
    assert charge<E
    B=s+E;C0=32*m*B*B;M=max(c['child_counts'])
    assert 2*B*(m-M)>=s+E and 2*B+18<C0
    mb=int(b['counts']['m']);Wb=int(b['counts']['W'])
    Mb=max(int(r) for r,n in b['child_width_multiplicities'])
    db,dc=halving(mb,Mb),halving(m,M)
    wb,wc=Wb.bit_length(),W.bit_length()
    coeff=wb*db+wc*dc;degree=1000*ceil(Q(coeff*51,25000))
    assert degree>Q(coeff*51,25)
    return dict(bit=dict(m=mb,W=Wb,maxchild=Mb,halving_degree=db,wire_bits=wb),
        complex=dict(m=m,W=W,s=s,maxchild=M,halving_degree=dc,wire_bits=wc,
            active_nodes=len(p.active),roles=p.roles,scalar_group_upper=G),
        semantic=dict(E=E,literal_charge=charge,strict_literal_gap=E-charge,B=B,
            C0=C0,C1=1,induction_gap=2*B*(m-M)-s-E),
        rows=dict(coefficient=coeff,degree=degree,suffix_slope=4*degree,
            degree_gap=degree-Q(coeff*51,25),
            contract='W_complex^D_complex * W_bit^D_bit; one leading prefix, one padding, nested bit factors restored'))

def assembly(f,kappa=KAPPA,old_guard=False,old_exposures=False):
    a,b=Q(11,10**6),Q(18,10**6);h=Q(1,10**8);beta=Q(1,4)
    tau,sigma=1-a,1-b;q=a*(1-2*h);lp=1-q;lam=(tau+lp)/2
    c=q*(1+h);eps=(1-h)/(1+c+q);G=eps*q
    r=(G+1-eps)/2;delta=h/8
    C1=Q(19991,10000) if old_guard else Q(1)
    margins=dict(g1=1-eps*(1+c),g2=a,g3=G,g4=a,
        g5=min(1-eps-delta,r-delta),g6=1-eps-delta,g7=eps)
    if old_exposures:margins.update(g2=eps*c*a,g4=a*(1-eps))
    internal=tau+(1-beta)*max(sigma-tau,Q(0));leaf=sigma+beta*(1-sigma)
    slacks=dict(a_positive=a,a_below_b=b-a,b_below_one_over32=Q(1,32)-b,
        beta_positive=beta,beta_below_one=1-beta,phase_leaf_above_bit=(1-beta)*b-a,
        q_positive=q,q_below_internal=1-internal-q,q_below_leaf=1-leaf-q,
        c_positive=c,c_below_one=1-c,q_below_reservations=c-q,
        lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,
        lambda_above_internal=lam-internal,lambda_prime_above_lambda=lp-lam,
        compact_leaf=lp-leaf,compact_reservations=lp-(1-c),lambda_prime_below_one=q,
        epsilon_positive=eps,epsilon_below_one=1-eps,guard_width=1-eps*C1,
        K_geometry=1-eps*(1+c),K_dominates_log=eps*c,
        record_suffix=1-eps,phase_local=1-eps-delta,phase_boundary=r-delta,
        gamma_sublinear=1-eps-r,cell_above_band=eps-(1-r)/2,
        prime_interval_packing=1-eps,alpha_positive=r,alpha_below_one=1-r,
        alpha_below_one_fourth=Q(1,4)-r,delta_positive=delta,
        delta_below_one_eighth=Q(1,8)-delta,short_record_fallback=eps-a,
        small_field_exposure=1-eps-G,artificial_boundary=8-eps+r-delta-G,
        literal_scalar_guard=Q(f['semantic']['strict_literal_gap']),
        row_product_gap=f['rows']['degree_gap'])
    slacks.update({name+'_above_kappa':val-kappa for name,val in margins.items()})
    assert all(x>0 for x in slacks.values()),{k:str(v) for k,v in slacks.items() if v<=0}
    assert min(margins.values())==G and margins['g1']-G==h
    assert kappa>Q(1,2**17)
    p=dict(a_bit=a,a_complex=b,tau=tau,sigma=sigma,beta=beta,q=q,c=c,
        epsilon=eps,lambda_=lam,lambda_prime=lp,alpha_squared_power=r,
        delta=delta,C0=f['semantic']['C0'],C1=C1,kappa=kappa)
    return dict(parameters=p,constraints=slacks,margins=margins,minimum_margin=G,
        absorption_gap=G-kappa,gap_above_2_minus17=kappa-Q(1,2**17),
        recurrence=dict(internal=internal,leaf=leaf,reservations=1-c))

def cutoffs(f,a):
    p=a['parameters'];e,c,r,beta=p['epsilon'],p['c'],p['alpha_squared_power'],p['beta']
    ka,km,kb=ceil(1/r),ceil(1/(e*c)),ceil(1/(1-e));C0=f['semantic']['C0']
    minimum=max(f['bit']['m'],f['complex']['m']);ks=ceil(1/(e*beta))
    cuts=dict(gamma=ceil(7/(1-e-r)),logarithmic_alpha=16*ka*ka+1,
        full_guard=ceil(Q((2*C0).bit_length())/(1-e)),
        phase_cell=ceil(9/(e-(1-r)/2)),compact_controls=64*km*km+1,
        K_geometry=ceil(3/(1-e*(1+c))),microbox_period=128*kb*kb+1,
        reservoirs=14,stopped_leaf=ks*(4*minimum).bit_length())
    cuts['common']=max(cuts.values());L=cuts['common']
    def power(exponent,rhs):
        assert exponent>=rhs.bit_length()
        return dict(exponent=exponent,rhs=rhs,rhs_bit_length=rhs.bit_length(),strict=True)
    checks=dict(compact=power(L//km,32*L+192),period=power(L//kb,16*L+56),
        alpha=power(L//ka,8*L+64))
    checks['row_stock']=[power((L*2**j)//kb,f['rows']['suffix_slope']*(L*2**j+8)) for j in range(6)]
    checks['stopped_leaf']=[power((L*2**j)//ks,4*minimum) for j in range(6)]
    assert L>=max(2*ka,2*km,2*kb,25)
    assert L*(1-e)>=(2*C0).bit_length() and L*(1-e-r)>=7
    assert L*(e-(1-r)/2)>=9 and L*(1-e*(1+c))>=3
    return dict(cutoff_log2_input_bits=cuts,compressed_power_checks=checks,
        additional_eventual_conditions=['BHP prime threshold and 12 d^2 < x^(19/40)',
          'Fixed rational basis, shared eligible prime and native table setup',
          'Polynomial descriptor and catalogue domination; e<=C*p,p>=C',
          'Strict logarithmic absorption and inherited exact-recovery thresholds'],
        practical_runtime_claim=False)

def run():
    old,ref=pinned_inputs();f=finite_bridge(old);a=assembly(f);cs=cutoffs(f,a)
    negative=[]
    for name,kwargs in [('old_quadratic_guard',dict(old_guard=True)),
        ('old_separate_exposure',dict(old_exposures=True)),
        ('unsupported_2_minus16',dict(kappa=Q(1,2**16)))]:
        try:assembly(f,**kwargs)
        except AssertionError:negative.append(name)
        else:raise AssertionError(name)
    return dict(status='CONDITIONAL FINAL KAPPA 1099/10^8 > 2^-17; NOT FORMAL VERIFICATION',
        baseline_PR21='5ba6cf0bfb68f2be8d15610e7972207c50254d6a',
        PR20_source=ref['commit'],finite_bridge=f,assembly=a,eventual_bounds=cs,
        negative_controls=negative,
        input_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in
            [PRIOR/'certificate.json',REF/'SOURCE.json',Path(__file__).resolve(),HERE/'controls.py',ROOT/'notes/semantic-bulk-17-note.tex']},
        scope='PR21 finite circuits unchanged. New semantic guard and row stock are derived for their exact whole-child interfaces. PR20 router, phase-cell inverse, bulk locality and tape proofs are attributed analytic dependencies. Original prefix retained.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=HERE/'certificate.json');args=p.parse_args()
    x=run();args.output.write_text(json.dumps(js(x),indent=2,sort_keys=True)+'\n')
    print('PASS kappa='+str(KAPPA)+' > 2^-17; constraints='+str(len(x['assembly']['constraints']))+';7 margins')
    print('Absorption gap:',float(x['assembly']['absorption_gap']))
    print('Product row degree:',x['finite_bridge']['rows']['degree'])
