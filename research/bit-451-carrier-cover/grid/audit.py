#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Construct the actual dyadic comparison distribution, then test two supplied powers."""
from argparse import ArgumentParser
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
from hashlib import sha256
from math import comb
from pathlib import Path
import json
import signal

PRIOR='e6919418a22bd2679320b0178860b506357dd882415b2431b96ffa879976eed6'
BIT='538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749'
Q=65536


def require(flag,msg):
    if not flag:
        raise ValueError(msg)


def checked(path,digest):
    raw=path.read_bytes()
    require(sha256(raw).hexdigest()==digest,path.name)
    return json.loads(raw)


def round_out(q,digits,down):
    unit=10**digits
    return F((q*unit).__floor__() if down else -(-q*unit).__floor__(),unit)


def distribution(bit):
    lo=[F(0)]*3;hi=[F(0)]*3
    with localcontext() as ctx:
        ctx.prec=72
        t=1-D('0.003879928046148')
        ref=D(11).ln()
        for key,n in bit['native']['paid'].items():
            if key=='1':
                lo[0]+=n;hi[0]+=n
                continue
            l=D(key).ln()
            ymin=F(l.next_minus())/F(ref.next_plus());ymax=F(l.next_plus())/F(ref.next_minus())
            weight_lo=F((t*l.next_minus()).next_minus().exp().next_minus())
            weight_hi=F((t*l.next_plus()).next_plus().exp().next_plus())
            for j in range(3):
                lo[j]+=n*weight_lo*ymin**j
                hi[j]+=n*weight_hi*ymax**j
    mean_l=lo[1]/hi[0];mean_h=hi[1]/lo[0]
    e2=hi[2]/lo[0];var=(e2-mean_l**2)/451
    require(0<mean_l<=mean_h<1 and var>0,'directed tensor bounds')
    sep=bit['separation']
    eps=F(sep['paid_uplift_upper'][1])/F(sep['three_engine_intervals']['source_1']['alpha'][0])**451
    require(0<eps<F(1,10**15),'all post-split paid surplus')
    cut=[0]
    for i in range(1,16):
        z=F(i,16)
        raw=F(1) if z<=mean_h else var/(var+(z-mean_h)**2)
        after=(raw+eps)/(1+eps)
        bucket=(Q*(1-after)).__floor__()
        cut.append(max(cut[-1],bucket))
    cut.append(Q)
    mass=[b-a for a,b in zip(cut,cut[1:])]
    require(sum(mass)==Q and min(mass)>=0,'positive probability law')
    return mass,dict(mean_lower=str(round_out(mean_l,18,True)),mean_upper=str(round_out(mean_h,18,False)),
                     second_upper=str(round_out(e2,18,False)),tensor_variance_upper=str(round_out(var,18,False)),
                     epsilon_upper='1/1000000000000000',cdf_numerators=cut)


def rows(mass,p,ng):
    # Exact integer raw moments of T=56+3*sum(integer bin). T/48 = 7/6+sum Z.
    powers=[sum(m*(3*i)**k for i,m in enumerate(mass,1)) for k in range(p+1)]
    work=[56**k for k in range(p+1)]
    factors=[[comb(i,k)*powers[k] for k in range(i+1)] for i in range(p+1)]
    for g in range(ng+1):
        work=[sum(weight*work[i-k] for k,weight in enumerate(factors[i])) for i in range(p+1)]
        yield F(work[p],48**p*Q**(g+1)),F((319+115*g)**p,100**p)


def newton(v):
    out=[]
    while v:
        out.append(v[0]);v=[y-x for x,y in zip(v,v[1:])]
    return out


def evaluate(src,old,p,K,g_bad):
    require(1<p and K>=0 and g_bad>=-1 and K+p+2+max(g_bad,0)<=1024,'case limits')
    mass,env=distribution(src)
    lower,upper=map(F,src['uniform']['eta'])
    mean=F(sum(k*m for k,m in enumerate(mass,1)),16*Q)
    small=p-1
    if g_bad<0:
        bad=(mean/F(23,20))**small
    else:
        g5=list(rows(mass,small,g_bad))[-1];bad=g5[0]/g5[1]
    require(bad>upper,'the adjacent lower integer fails the capacity')
    obs=list(rows(mass,p,K+p))
    prefix=[x/y for x,y in obs[:K]]
    ns,ds=zip(*obs[K:])
    n,d=newton(list(ns)),newton(list(ds))
    require(all(a>=0 and b>0 for a,b in zip(n,d)),'tail differences')
    tail=[x/y for x,y in zip(n,d)]
    largest=max(prefix+tail)
    require(largest<lower,'strict prefix and infinite tail')
    require(F(7,6)+1 < F(319,100) and 1<F(23,20),'all termwise ratios below one')
    h,H=1804,src['uniform']['H']
    require(old['p']==31 and old['h']==h and old['uniform_J']==1218,'unchanged component')
    require((1+F((134**451).bit_length()-1,h))**p>F(src['uniform']['ambient_power'][1]),'base')
    J=(((H+h)**p)//h**p).bit_length()
    require((h**p<<(J-1))<=(H+h)**p<(h**p<<J) and F(J,H)*(H+h)>2*p,'strict carrier and tail')
    rate=F(src['separation']['trial'])-F(J,H)-F(1,H*2**44)
    require(F(src['cover_and_stock']['bad_surcharge_upper'])<F(1,2**45),'same covered route')
    prev=F(src['cover_and_stock']['seed']);rho=F(src['cover_and_stock']['rho']);stages=[]
    for _ in range(7):
        maximum=rate-rho*(rate-prev);step=F((maximum*10**24).__floor__()-1,10**24)
        require(prev<step<maximum<rate<rho<1-maximum,'signed ordinary prices')
        stages.append([str(step),str(maximum-step)]);prev=step
    cap=F((prev*10**17).__floor__(),10**17);tick=F(1,10**14)
    claim=(cap//tick-8)*tick;tested=claim+7*tick
    old_claim=F(old['candidate_grid_claim']);ceiling=F(src['raw_crossing'][1])-F(old['uniform_loss'])-7*tick
    require(cap>tested>claim>ceiling>old_claim,'complete separation')
    return dict(pins={'BIT-451.json':BIT,'SECOND.json':PRIOR},integer_masses=mass,denominator=Q,**env,
                p_minimum=p,h=h,shift=K,failed_power=small,failed_height=g_bad,failed_ratio=str(bad),
                eta_lower=str(lower),eta_upper=str(upper),comparison_mean=str(mean),worst_upper=str(largest),
                prefix_ratios=list(map(str,prefix)),shifted_ratios=list(map(str,tail)),uniform_J=J,
                uniform_loss=str(F(J,H)),stages=stages,cap=str(cap),candidate_grid_claim=str(claim),
                candidate_tested=str(tested),old_cover_forgiven_upper=str(ceiling),separation=str(claim-ceiling),
                absolute_gain=str(claim-old_claim),exact_relative_percent=str(100*(claim-old_claim)/old_claim))


def bind(data,r):
    rec=json.loads((r/'receipt.json').read_bytes());app=json.loads((r/'APPLICATION.json').read_bytes());audit=json.loads((r/'AUDIT.json').read_bytes())
    require(F(rec['cap'])==F(app['binary_ordinary'])==F(audit['outer']['pinned_binary_cap'])==F(data['cap']),'cap')
    require(F(rec['tested'])==F(audit['outer']['finite_compiler']['tested'])==F(data['candidate_tested']),'tested')
    require(F(rec['claim'])==F(app['application']['claim'])==F(data['candidate_grid_claim']),'claim')
    for key in ('APPLICATION.json','AUDIT.json'):
        require(sha256((r/key).read_bytes()).hexdigest()==rec['output_sha256'][key],key)


if __name__=='__main__':
    signal.alarm(60);cli=ArgumentParser(description=__doc__)
    for k in ('root','prior','out'):cli.add_argument(k,type=Path)
    cli.add_argument('--power',type=int,required=True);cli.add_argument('--shift',type=int,required=True)
    cli.add_argument('--failed-height',type=int,required=True);cli.add_argument('--outer',type=Path)
    args=cli.parse_args()
    result=evaluate(checked(args.root/'BIT-451.json',BIT),checked(args.prior,PRIOR),args.power,args.shift,args.failed_height)
    if args.outer:bind(result,args.outer)
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS_451_DYADIC_LAW',result['p_minimum'],result['uniform_J'],result['candidate_grid_claim'])
