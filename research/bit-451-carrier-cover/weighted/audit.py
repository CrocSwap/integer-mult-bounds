#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Newton-difference replay for one fixed weighted-exit certificate."""
from argparse import ArgumentParser
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
from hashlib import sha256
from math import comb
from pathlib import Path
import json
import signal

PIN='538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749'
PRIOR='ff9cf4ca87fa4480daac4c93aa1fa5744f5eec97385c7bae203ca2d3d874d0d9'
LAW='28e0308f315a583282291fa01998d53a874b4b7e3073cacc3ddbb38c5a7f66c7'


def need(ok, item):
    if not ok:
        raise ValueError(item)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def mean_bound(data):
    with localcontext() as ctx:
        ctx.prec=64
        t=1-D('0.003879928046148')
        numer=denom=F(0)
        for grade, n in data['native']['paid'].items():
            if grade=='1':
                denom+=n
                continue
            log=D(grade).ln()
            lower=(t*log.next_minus()).next_minus().exp().next_minus()
            upper=(t*log.next_plus()).next_plus().exp().next_plus()
            numer+=n*F(upper)*F(log.next_plus())
            denom+=n*F(lower)
        raw=numer/(denom*F(D(11).ln().next_minus()))
    sep=data['separation']
    alpha=F(sep['three_engine_intervals']['source_1']['alpha'][0])
    extra=F(sep['paid_uplift_upper'][1])/alpha**451
    return raw,extra


def differences(values):
    heads=[]
    while values:
        heads.append(values[0])
        values=[b-a for a,b in zip(values,values[1:])]
    return heads


def run(data, prior):
    h,p,H=1804,45,1202400000000000
    v=451
    need(data['uniform']['H']==H and data['partition']['cutoff']=='11^451','fixed carrier')
    need(prior['H']==H and prior['uniform_integer_J_minimum']==2218,'previous budget')
    raw, extra=mean_bound(data)
    need(raw+extra<F(3,4),'true tilted law admits probability bound')
    # Abar>=h ln2/ln J, Bunder<=(h ln2+ln A)/ln J and beta<=ln k/ln J.
    need(h==4*v and 2**24 <= 11**7 and (16*134)**100 >= 11**319 and 16**20 >= 11**23,'log enclosures')
    # E[(7/6+Binomial(g+1,3/4))^p] as a directly enumerated exact binomial.
    num=[]; den=[]
    for g in range(p+1):
        n=g+1
        num.append(F(sum(comb(n,i)*3**i*(7+6*i)**p for i in range(n+1)),4**n*6**p))
        den.append((F(319,100)+F(23,20)*g)**p)
    # kth forward difference is k! times the coefficient of the falling factorial (g)_k.
    top,bottom=differences(num),differences(den)
    need(all(d>0 for d in bottom) and all(c>=0 for c in top),'Newton coefficient signs')
    eta=F(data['uniform']['eta'][0])
    for k in (0,p):
        need(top[k]<eta*bottom[k],f'endpoint {k}')
    ratios=[u/d for u,d in zip(top,bottom)]
    largest=max(ratios); who=ratios.index(largest)
    need(largest<eta,'all 46 independent coefficients')
    A=134**v; amin=A.bit_length()-1
    need((1+F(amin,h))**p>F(data['uniform']['ambient_power'][1]),'entire ordinary base interval')
    num_final=(h+H)**p;den_final=h**p
    J=(num_final//den_final).bit_length()
    need((den_final<<(J-1))<=num_final<(den_final<<J),'minimal integral budget at this scale')
    e=F(J,H);need(e*(H+h)>2*p,'eventual tail')
    C=F(data['separation']['trial']);d=F(prior['charged_cover_loss'])
    need(H*d==F(1,2**44) and F(data['cover_and_stock']['bad_surcharge_upper'])<H*d/2,'covered original')
    covered=C-e-d; prev=F(data['cover_and_stock']['seed']);rho=F(data['cover_and_stock']['rho'])
    stages=[]
    for j in range(7):
        ub=covered-(covered-prev)*rho
        chosen=F((ub*10**24).__floor__()-1,10**24)
        need(prev<chosen<ub<covered<rho<1-ub,'stage')
        stages.append([str(chosen),str(ub-chosen)]);prev=chosen
    cap=F((prev*10**17).__floor__(),10**17)
    tick=F(1,10**14);claim=(cap//tick-8)*tick;tested=claim+7*tick
    u=F(data['raw_crossing'][1])-F(prior['uniform_loss'])-7*tick
    need(cap>tested>claim>u>F(prior['candidate_grid_claim']),'separation')
    # Destroy the certificate by replacing its q bound by 1 at leading degree.
    need(F(1,1)/F(23,20)**p>eta,'all paid ranks maximized fails leading term')
    return dict(pins={'BIT-451.json':PIN,'ENDPOINT.json':PRIOR,'WEIGHTED-EXITS.md':LAW},
                q='3/4',p=p,h=h,A_bar='7/6',B_under='319/100',beta='23/20',
                mean_plus_tail_ceiling_15dp=str(F(-(-(raw+extra)*10**15).__floor__(),10**15)),
                coefficients=len(ratios),maximum_index=who,maximum_ratio=str(largest),eta_lower=str(eta),
                all_ratios=[str(x) for x in ratios],uniform_J=J,uniform_loss=str(e),covered_rate=str(covered),
                stages=stages,cap=str(cap),candidate_grid_claim=str(claim),candidate_tested=str(tested),
                old_cover_forgiven_upper=str(u),separation=str(claim-u),absolute_gain=str(claim-F(prior['candidate_grid_claim'])),
                exact_relative_percent=str(100*(claim-F(prior['candidate_grid_claim']))/F(prior['candidate_grid_claim'])))


if __name__=='__main__':
    signal.alarm(60)
    cli=ArgumentParser();cli.add_argument('producer',type=Path);cli.add_argument('previous',type=Path)
    cli.add_argument('law',type=Path);cli.add_argument('out',type=Path);cli.add_argument('--outer',type=Path)
    args=cli.parse_args()
    path=args.producer/'BIT-451.json'
    need(digest(path)==PIN and digest(args.previous)==PRIOR and digest(args.law)==LAW,'source integrity')
    res=run(json.loads(path.read_bytes()),json.loads(args.previous.read_bytes()))
    if args.outer:
        receipt=json.loads((args.outer/'receipt.json').read_bytes())
        app=json.loads((args.outer/'APPLICATION.json').read_bytes());audit=json.loads((args.outer/'AUDIT.json').read_bytes())
        need(F(receipt['cap'])==F(app['binary_ordinary'])==F(audit['outer']['pinned_binary_cap'])==F(res['cap']),'outer cap')
        need(F(receipt['claim'])==F(app['application']['claim'])==F(res['candidate_grid_claim']),'outer claim')
        need(F(receipt['tested'])==F(audit['outer']['finite_compiler']['tested'])==F(res['candidate_tested']),'outer tested')
        for key in ('APPLICATION.json','AUDIT.json'):
            need(digest(args.outer/key)==receipt['output_sha256'][key],key)
    args.out.write_text(json.dumps(res,indent=2)+'\n')
    print('PASS',res['maximum_index'],res['uniform_J'],res['cap'],res['candidate_grid_claim'])
