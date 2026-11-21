#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""One tensor-second-moment decision by direct power-series convolution."""
from argparse import ArgumentParser
from fractions import Fraction as F
from hashlib import sha256
from math import comb
from pathlib import Path
import json
import signal


PINS={
    'BIT-451.json':'538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749',
    'weighted/RESULT.json':'f2218a9eb212ef7f0ae1c993297df50c401bb6b24537318c2570cea54d6d2b92',
    'minimum_result':'b8a72fc639fecfe4a815421413ff2d47aa7c65d96b35339285be67c557fbdac5',
    'LOG-MOMENTS.md':'f4a067517ebf1db95b3179f30c4f0ec284666052469ed3502f0eb8cbbc4dc131',
}


def check(test, reason):
    if not test:
        raise ValueError(reason)


def pinned_json(path, key):
    raw=path.read_bytes()
    check(sha256(raw).hexdigest()==PINS[key],key)
    return json.loads(raw)


def differences(values):
    out=[]
    while values:
        out.append(values[0])
        values=[y-x for x,y in zip(values,values[1:])]
    return out


def bounded_tensor_mean(src,weighted):
    v=451
    paid={int(k):n for k,n in src['native']['paid'].items()}
    check(v==src['partition']['factors'] and max(paid)==56 and 56<11**2,'Y<=2')
    check(F(weighted['mean_plus_tail_ceiling_15dp'])<F(3,4),'previous directed raw and complete means')
    # E[Y^2]<=2 E[Y], cross terms use the square of the single raw mean.
    M2=F(v-1,v)*F(3,4)**2+F(2,v)*F(3,4)
    check(M2==F(9,16)+F(15,16*v)<1,'raw independent tensor second moment')
    sep=src['separation']
    alpha_lo=F(sep['three_engine_intervals']['source_1']['alpha'][0])
    eps=F(sep['paid_uplift_upper'][1])/alpha_lo**v
    cap_eps=F(1,10**15)
    check(0<eps<cap_eps,'all paid excess')
    clipped_bound=(M2+cap_eps)/(1+cap_eps)
    check((M2+eps)/(1+eps)<clipped_bound<F(3,5),'completed clipped-reference second moment')
    return M2,cap_eps,clipped_bound


def verify(src, weighted, old):
    p,h,H=31,1804,src['uniform']['H']
    check(int(old['normalization'])==h and old['p_minimum']==32 and old['negative_height']==5,'predecessor scope')
    M2,eps_cap,m2_cap=bounded_tensor_mean(src,weighted)
    mu=[F(1),F(3,4)]+[F(3,5)]*(p-1)
    A,B,beta=map(F,(weighted['A_bar'],weighted['B_under'],weighted['beta']))
    eta_lo,eta_hi=map(F,src['uniform']['eta'])
    # Expand the old Bernoulli law at the previously failing height.
    old_g5=F(sum(comb(6,i)*3**i*(7+6*i)**p for i in range(7)),4**6*6**p)/(B+5*beta)**p
    check(old_g5==F(old['negative_ratio'])>eta_hi,'previous height-five control')
    # Coefficients of exp(Az) times the g+1-th power of the formal moment
    # series, scaled by i!; no probability distribution for mu is assumed.
    values=[A**i for i in range(p+1)]
    numer=[];denom=[]
    for g in range(p+1):
        values=[sum(comb(i,k)*values[i-k]*mu[k] for k in range(i+1)) for i in range(p+1)]
        numer.append(values[p])
        denom.append((B+g*beta)**p)
    new_g5=numer[5]/denom[5]
    check(new_g5<eta_lo<eta_hi<old_g5,'decisive fifth-height change')
    ncoeff,dcoeff=differences(numer),differences(denom)
    check(all(x>=0 for x in ncoeff) and all(x>0 for x in dcoeff),'direct Newton differences')
    ratios=[n/d for n,d in zip(ncoeff,dcoeff)]
    maximum=max(ratios)
    check(maximum<eta_lo,'one strict contraction for every height')
    check((1+F((134**451).bit_length()-1,h))**p>F(src['uniform']['ambient_power'][1]),'complete base')
    J=(((H+h)**p)//h**p).bit_length()
    check(h**p*2**(J-1)<=(H+h)**p<h**p*2**J and F(J,H)*(H+h)>2*p,'integer uniform budget and tail')
    d=F(1,H*2**44)
    check(F(src['cover_and_stock']['bad_surcharge_upper'])<H*d/2,'same charged cover')
    covered=F(src['separation']['trial'])-F(J,H)-d
    prev=F(src['cover_and_stock']['seed']);rho=F(src['cover_and_stock']['rho'])
    stages=[]
    for _ in range(7):
        ceiling=covered-rho*(covered-prev);rate=F((ceiling*10**24).__floor__()-1,10**24)
        check(prev<rate<ceiling<covered<rho<1-ceiling,'complete ordinary stages')
        stages.append([str(rate),str(ceiling-rate)]);prev=rate
    cap=F((prev*10**17).__floor__(),10**17); tick=F(1,10**14)
    claim=(cap//tick-8)*tick;tested=claim+7*tick
    old_upper=F(src['raw_crossing'][1])-F(old['uniform_loss'])-7*tick
    old_claim=F(old['candidate_grid_claim'])
    check(cap>tested>claim>old_upper>old_claim,'previous complete ceiling')
    return dict(pins=PINS,h=h,p=p,raw_M2=str(M2),paid_excess_upper=str(eps_cap),
                post_split_M2_upper=str(m2_cap),moment_bounds=['1','3/4','3/5 for every integer i>=2'],
                old_height_5=str(old_g5),new_height_5=str(new_g5),eta_lower=str(eta_lo),
                peak_index=ratios.index(maximum),maximum_ratio=str(maximum),all_ratios=list(map(str,ratios)),
                uniform_J=J,uniform_loss=str(F(J,H)),stages=stages,cap=str(cap),
                candidate_grid_claim=str(claim),candidate_tested=str(tested),old_cover_forgiven_upper=str(old_upper),
                separation=str(claim-old_upper),absolute_gain=str(claim-old_claim),
                exact_relative_percent=str(100*(claim-old_claim)/old_claim))


def bind(result, directory):
    r=json.loads((directory/'receipt.json').read_bytes());a=json.loads((directory/'APPLICATION.json').read_bytes())
    u=json.loads((directory/'AUDIT.json').read_bytes())
    check(F(r['cap'])==F(a['binary_ordinary'])==F(u['outer']['pinned_binary_cap'])==F(result['cap']),'cap')
    check(F(r['claim'])==F(a['application']['claim'])==F(result['candidate_grid_claim']),'claim')
    check(F(r['tested'])==F(u['outer']['finite_compiler']['tested'])==F(result['candidate_tested']),'tested')
    for k in ('APPLICATION.json','AUDIT.json'):
        check(sha256((directory/k).read_bytes()).hexdigest()==r['output_sha256'][k],k)


if __name__=='__main__':
    signal.alarm(60)
    parser=ArgumentParser(description=__doc__)
    for k in ('root','weighted','minimum','out'):parser.add_argument(k,type=Path)
    parser.add_argument('--outer',type=Path)
    args=parser.parse_args()
    check(sha256(Path(__file__).with_name('LOG-MOMENTS.md').read_bytes()).hexdigest()==PINS['LOG-MOMENTS.md'],'theorem')
    result=verify(pinned_json(args.root/'BIT-451.json','BIT-451.json'),pinned_json(args.weighted,'weighted/RESULT.json'),
                  pinned_json(args.minimum,'minimum_result'))
    if args.outer:bind(result,args.outer)
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS_451_SECOND_LOG_MOMENT',result['peak_index'],result['uniform_J'],result['candidate_grid_claim'])
