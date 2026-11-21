#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Direct binomial evaluation and shifted Newton certificates for two supplied powers."""
from argparse import ArgumentParser
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import signal


OLD='f2218a9eb212ef7f0ae1c993297df50c401bb6b24537318c2570cea54d6d2b92'
BIT='538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749'


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


def checked(path, pin):
    raw=path.read_bytes()
    require(sha256(raw).hexdigest()==pin,path.name)
    return json.loads(raw)


def height(g, power):
    # A=7/6, B=319/100, beta=23/20, q=3/4. Every numerator term is integer.
    n=g+1
    accumulator=0
    multiplicity=1
    for i in range(n+1):
        accumulator+=multiplicity*(7+6*i)**power
        if i<n:
            multiplicity=multiplicity*(n-i)*3//(i+1)
    return F(accumulator,4**n*6**power), F((319+115*g)**power,100**power)


def newton(values):
    first=[]
    while values:
        first.append(values[0])
        values=[right-left for left,right in zip(values,values[1:])]
    return first


def audit(root, predecessor, p, K, bad_g):
    bit=checked(root/'BIT-451.json',BIT);old=checked(predecessor,OLD)
    require(1<p and K>=0 and bad_g>=0 and K+p+2<=1024 and bad_g<1024,'authorized height census')
    decision=F(bit['uniform']['eta'][0]);eta_hi=F(bit['uniform']['eta'][1])
    require(old['p']==45 and old['coefficients']==46
            and F(old['maximum_ratio'])==max(map(F,old['all_ratios']))<decision,
            'known-good sealed p=45 control')
    require((F(20,23))**p>eta_hi,'maximizing every paid rank breaks the leading coefficient')
    require(tuple(map(F,[old['A_bar'],old['B_under'],old['beta'],old['q']]))==
            (F(7,6),F(319,100),F(23,20),F(3,4)),'retained law')
    require(F(13,6)<F(319,100) and 1<F(23,20),'every realization lies strictly below one')
    no_num,no_den=height(bad_g,p-1); failure=no_num/no_den
    require(failure>eta_hi,'adjacent lower exponent must fail even the upper etabound')
    exact=[height(g,p) for g in range(K+p+1)]
    prefix=[n/d for n,d in exact[:K]]
    nums, dens=zip(*exact[K:])
    heads, bottoms=newton(list(nums)), newton(list(dens))
    require(all(z>0 for z in bottoms) and all(z>=0 for z in heads),'signed shifted coefficients')
    tail=[a/b for a,b in zip(heads,bottoms)]
    ratios=prefix+tail
    bound=max(ratios)
    require(bound<decision,'all prefix heights and infinite tail')
    h=old['h'];H=bit['uniform']['H'];A=134**451
    base_log=A.bit_length()-1
    require((1+F(base_log,h))**p>F(bit['uniform']['ambient_power'][1]),'all ordinary base ranks')
    J=(((H+h)**p)//(h**p)).bit_length()
    require(h**p*2**(J-1)<=(H+h)**p<h**p*2**J,'least integer loss at supplied power')
    require(H>3*h and F(J,H)*(H+h)>2*p,'large-width tail')
    c=F(bit['separation']['trial']);d=F(1,H*2**44)
    require(F(old['covered_rate'])==c-F(old['uniform_loss'])-d,'same complete cover debit')
    covered=c-F(J,H)-d; rate=F(bit['cover_and_stock']['seed']);rho=F(bit['cover_and_stock']['rho']);stages=[]
    for _ in range(7):
        cap=covered-rho*(covered-rate)
        step=F((cap*10**24).__floor__()-1,10**24)
        require(rate<step<cap<covered<rho<1-cap,'strict recurrence')
        stages.append([str(step),str(cap-step)]);rate=step
    cap=F((rate*10**17).__floor__(),10**17)
    tick=F(1,10**14);claim=(cap//tick-8)*tick;tested=claim+7*tick
    generous=F(bit['raw_crossing'][1])-F(old['uniform_loss'])-7*tick
    require(cap>tested>claim>generous>F(old['candidate_grid_claim']),'complete rate comparison')
    return dict(pins={'BIT-451.json':BIT,'weighted/RESULT.json':OLD},
                parent_head='a24daf62b8e63eabefc62afbc5ad4c73b7216e60',
                q=old['q'],normalization=old['h'],p_minimum=p,tail_shift=K,negative_height=bad_g,
                failed_previous_power=p-1,negative_ratio=str(failure),eta_upper=str(eta_hi),eta_lower=str(decision),
                controls=['hash-locked p=45 receipt accepted','q=1 leading coefficient rejected'],
                heights_evaluated=K+p+2,prefix_ratios=list(map(str,prefix)),shifted_ratios=list(map(str,tail)),
                uniform_contraction_bound=str(bound),uniform_J=J,uniform_loss=str(F(J,H)),
                minimum_loss_at_this_power=J,stages=stages,cap=str(cap),
                candidate_grid_claim=str(claim),candidate_tested=str(tested),old_cover_forgiven_upper=str(generous),
                separation=str(claim-generous),absolute_gain=str(claim-F(old['candidate_grid_claim'])),
                exact_relative_percent=str(100*(claim-F(old['candidate_grid_claim']))/F(old['candidate_grid_claim'])))


def bind(out, root):
    r=json.loads((root/'receipt.json').read_bytes());a=json.loads((root/'APPLICATION.json').read_bytes());u=json.loads((root/'AUDIT.json').read_bytes())
    require(F(r['cap'])==F(a['binary_ordinary'])==F(u['outer']['pinned_binary_cap'])==F(out['cap']),'cap')
    require(F(r['claim'])==F(a['application']['claim'])==F(out['candidate_grid_claim']),'claim')
    require(F(r['tested'])==F(u['outer']['finite_compiler']['tested'])==F(out['candidate_tested']),'tested')
    for path in ('APPLICATION.json','AUDIT.json'):
        require(sha256((root/path).read_bytes()).hexdigest()==r['output_sha256'][path],path)


if __name__=='__main__':
    signal.alarm(60)
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('producer',type=Path);parser.add_argument('prior',type=Path);parser.add_argument('out',type=Path)
    parser.add_argument('--power',type=int,required=True);parser.add_argument('--shift',type=int,required=True)
    parser.add_argument('--failed-height',type=int,required=True);parser.add_argument('--outer',type=Path)
    args=parser.parse_args()
    result=audit(args.producer,args.prior,args.power,args.shift,args.failed_height)
    if args.outer:bind(result,args.outer)
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS_451_ALL_HEIGHT',result['p_minimum'],result['uniform_J'],result['candidate_grid_claim'])
