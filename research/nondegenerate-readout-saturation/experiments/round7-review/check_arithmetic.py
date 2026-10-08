#!/usr/bin/env python3
"""Independent arithmetic audit of the published round-seven profiles.

Imports only the previous local audit's exact elementary function bounds.
No upstream certifier is imported. Arithmetic-only variants are labeled.
"""
from collections import Counter
from fractions import Fraction as Q
import importlib.util
import json
from math import comb, exp, log
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('trusted_research_check',HERE.parents[1]/'scripts/check_research.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)


def root(c):
    lo,hi=0.,.001
    for _ in range(70):
        a=(lo+hi)/2
        f=sum(n*w/c['m']/c['W']*exp(a*log(c['m']/w)) for w,n in c['hist'])
        if f<1:lo=a
        else:hi=a
    return (lo+hi)/2


def exact_moment(c,a):
    return audit.moment_interval(dict(m=c['m'],W=c['W'],child_multiplicities=dict(c['hist'])),a)


def assembly(d,c):
    ab,ac=Q(*d[c]['a']),Q(*d['cx']['a']);k=d['kappa' if c=='bit' else 'kappaplain']
    beta,eps,x,c1,kap=[Q(*k[n]) for n in ('beta','eps','x','c1','kappa')]
    tau,sigma=1-ab,1-ac;chi=tau+(1-beta)*max(sigma-tau,0);leaf=sigma+beta*(1-sigma)
    lam=max(tau,sigma,chi)+Q(1,10**16);lp=max(lam,leaf)+Q(1,10**16)
    delta=Q(1,10**22)/x;poly=(1+x)*delta
    _,lnhi=audit.log_interval(Q(d['cx']['s']))
    constraints=dict(crude_guard=c1-2-k['mc']*lnhi,
                     compact_saving=1-lp,
                     reservation=1-eps*(2-lp),
                     scalar_depth=1+x-eps*c1,
                     precision=1+x-3*eps,
                     eps_positive=eps,eps_below_one=1-eps,
                     beta_positive=beta,beta_below_one=1-beta,
                     delta_positive=delta,delta_below_eighth=Q(1,8)-delta)
    margins=dict(prefix=1-eps,butterfly=eps*(1-lp),
                 small_field_and_Gaussian=1-eps-poly,
                 polynomial=eps,axis_reverse=max(eps,1-eps)*ab)
    assert all(a>0 for a in constraints.values()) and all(a>kap for a in margins.values())
    return dict(kappa=str(kap),kappa_float=float(kap),
                exceeds_user_threshold=kap>Q('0.000052445080818074'),
                exceeds_two_to_minus14=kap>Q(1,2**14),
                constraints=len(constraints),cost_margins=len(margins),
                min_absorption_gap=float(min(margins.values())-kap),
                precision_x=int(x),crude_C1=int(c1),
                parameter_headroom=float(ab/(1+ab)-kap))


def main():
    d=json.loads((HERE/'vendor/lean/round7-histograms.json').read_text());out={}
    for name in ('bit','bitplain','cx'):
        c=d[name];a=Q(*c['a']);rank=sum(w*n for w,n in c['hist']);assert rank==c['s']
        lo,hi=exact_moment(c,a);assert hi<1
        lnext,hnext=exact_moment(c,a+Q(1,10**9))
        mu=sum(n*w/c['m']/c['W']*log(c['m']/w) for w,n in c['hist'])
        row=dict(m=c['m'],W=c['W'],rank=rank,deficit=c['m']*c['W']-rank,
                 certified_saving=str(a),moment_lower=float(lo),moment_upper=float(hi),
                 moment_gap_lower=float(1-hi),moment_enclosure_width=float(hi-lo),
                 next_grid_moment_lower=float(lnext),next_grid_gap_lower=float(lnext-1),
                 next_grid_certified_false=lnext>1,characteristic_root_float=root(c),
                 weighted_log_cost=mu,child_occurrences=sum(n for w,n in c['hist']))
        if name!='cx':row['assembly']=assembly(d,name)
        out[name]=row
    h=23;v=comb(h,3);N=v*v;R=(d['bit']['W']-2*N)//(2*v)
    assert d['bit']['W']==2*N+2*v*R and d['bit']['s']==d['bit']['W']*h*h-N+2*v*h*(h-1)
    widths=dict(d['bit']['hist']);dims={h-(h*h-w)//2:n//(2*v) for w,n in widths.items() if w>=h*h-2*h}
    assert sum(dims.values())==R
    out['readout_distribution']=dict(R=R,v=v,N=N,readout_dimensions=dims,
         deferred_slots=sum(n for dim,n in dims.items() if dim),
         average_sigma_dimension=sum(dim*n for dim,n in dims.items())/sum(n for dim,n in dims.items() if dim))
    diff=Counter(dict(d['bit']['hist']));diff.subtract(dict(d['bitplain']['hist']))
    out['staircase_vs_plain']=dict(child_changes={w:n for w,n in diff.items() if n},
         saving_gain_ratio=float(Q(*d['bit']['a'])/Q(*d['bitplain']['a'])))
    (HERE/'arithmetic-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))


if __name__=='__main__':main()
