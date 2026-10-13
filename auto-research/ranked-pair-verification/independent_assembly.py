"""Independent transcription of the 47 balanced-assembly inequalities.

Mathematical source: PR23/29/34/36/48 balanced assembly, retained by PR57/58.
Credit: Zhihao Chen, RaD/hipotures, James Chang, icekylinx, Chafik Boukhalfa,
and the community's retained notices. This is an arithmetic audit, not a
proof of the analytic or physical assumptions that justify these constraints.
Unlike the contributor verifier, this script imports no upstream module.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import json
from independent_moment import encode, require, moment

def assemble(c, a, k, h):
    b,beta=Q(717,10**7),Q(1,20)
    f=c['finite_bridge']
    require(all(f['bit'][key]==c['bit'][key] for key in ('m','W','maxchild')),
            'finite bridge must describe the actual bit profile')
    for key in ('bit','complex'):
        p=f[key];m,W,t=p['m'],p['W'],p['maxchild']
        D=p['halving_degree']
        require(W>0 and 0<t<m and D>0, 'positive bridge constants')
        require(m**D>2*t**D and (D==1 or m**(D-1)<=2*t**(D-1)), 'halving degree')
        require(W.bit_length()==p['wire_bits'], 'wire bits')
    p=f['complex'];W,m,s,G=(p[x] for x in ('W','m','s','scalar_group_upper'))
    require(0<s<m*W and G>0,'complex finite bounds')
    E=64*(W+m+G+1)**3;B=s+E;C0=32*m*B*B
    literal=2*G*W*W+8*s+4*W+4+32*m
    require(E>literal and 2*B*(m-p['maxchild'])>=s+E and C0>2*B+18,'semantic envelope')
    expected=dict(E=E,B=B,C0=C0,C1=1,literal_charge=literal,
                  strict_literal_gap=E-literal,induction_gap=2*B*(m-p['maxchild'])-(s+E))
    require(all(Q(f['semantic'][key])==value for key,value in expected.items()),'semantic binding')
    stock=sum(f[t]['halving_degree']*f[t]['wire_bits'] for t in ('bit','complex'))
    rowgap=f['rows']['degree']-Q(51,25)*stock
    require(f['rows']['coefficient']==stock and Q(f['rows']['degree_gap'])==rowgap>0,'row stock')
    require(f['rows']['suffix_slope']==4*f['rows']['degree'],'row suffix')
    q=a*(1-2*h);c0=q+h/4;e=(1-h)/(1+q)
    tau,sigma=1-a,1-b
    lp=1-q;lam=(tau+lp)/2;g=e*q;r=(g+1-e)/2;delta=h/8
    internal=tau+(1-beta)*max(sigma-tau,Q(0));leaf=sigma+beta*(1-sigma)
    margins=dict(g1=1-e,g2=a,g3=g,g4=a,g5=min(1-e-delta,r-delta),g6=1-e-delta,g7=e)
    checks=dict(a_positive=a,a_below_b=b-a,b_below_one_over32=Q(1,32)-b,
        beta_positive=beta,beta_below_one=1-beta,phase_leaf_above_bit=(1-beta)*b-a,
        q_positive=q,q_below_internal=1-internal-q,q_below_leaf=1-leaf-q,
        c_positive=c0,c_below_one=1-c0,q_below_reservations=c0-q,
        lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,
        lambda_above_internal=lam-internal,lambda_prime_above_lambda=lp-lam,
        compact_leaf=lp-leaf,compact_reservations=lp-(1-c0),lambda_prime_below_one=q,
        epsilon_positive=e,epsilon_below_one=1-e,guard_width=1-e,
        K_geometry=1-e*(1+c0),K_dominates_log=e*c0,record_suffix=1-e,
        phase_local=1-e-delta,phase_boundary=r-delta,gamma_sublinear=1-e-r,
        cell_above_band=e-(1-r)/2,prime_interval_packing=1-e,alpha_positive=r,
        alpha_below_one=1-r,alpha_below_one_fourth=Q(1,4)-r,delta_positive=delta,
        delta_below_one_eighth=Q(1,8)-delta,short_record_fallback=e-a,
        small_field_exposure=1-e-g,artificial_boundary=8-e+r-delta-g,
        literal_scalar_guard=E-literal,row_product_gap=rowgap)
    checks.update({name+'_above_kappa':v-k for name,v in margins.items()})
    require(len(checks)==47 and len(margins)==7,'complete constraint names')
    require(0<h<Q(1,2) and 0<k,'parameter domain')
    require(all(v>0 for v in checks.values()),str({n:str(v) for n,v in checks.items() if v<=0}))
    require(min(margins.values())==g and 1-e-g==h and 1-e-r==h/2,'balancing identities')
    require(1-e*(1+c0)==h-e*h/4,'geometry identity')
    return dict(a_bit=a,a_complex=b,kappa=k,h=h,minimum_margin=g,
                absorption_gap=g-k,scoped_limit=a/(1+a),phase_capacity=(1-beta)*b,
                constraints=checks,margins=margins)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('certificate',type=Path)
    ap.add_argument('--root-certificate',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();c=json.loads(args.certificate.read_text())
    old=assemble(c,Q(c['bit_saving']),Q(c['kappa']),Q(c['assembly']['parameters']['h']))
    require(old['constraints']=={n:Q(v) for n,v in c['assembly']['constraints'].items()},'original constraints differ')
    require(old['margins']=={n:Q(v) for n,v in c['assembly']['margins'].items()},'original margins differ')
    out=dict(published=old,scope='Conditional arithmetic only; structural transfer not proved')
    if args.root_certificate:
        root=json.loads(args.root_certificate.read_text());a=Q(root['root_bracket'][0]);h=Q(1,10**18)
        p=c['bit'];rows={int(t):n for t,n in p['child_multiplicities'].items()}
        low,high=moment(p['m'],p['W'],rows,a)
        require(high<1,'independent refined moment')
        q=a*(1-2*h);g=(1-h)*q/(1+q);scale=10**22
        k=Q((g*scale).numerator//(g*scale).denominator-1,scale)
        new=assemble(c,a,k,h)
        require(k>Q(c['kappa']),'no strict improvement')
        out.update(refined=new,refined_moment=[low,high],
                   improvement=k-Q(c['kappa']),physical_profile_unchanged=True)
    args.output.write_text(json.dumps(encode(out),indent=2)+'\n')
    print(json.dumps(encode({x:out[x]['kappa'] for x in ('published','refined') if x in out}),indent=2))

if __name__=='__main__':main()
