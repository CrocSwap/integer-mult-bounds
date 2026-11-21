#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""One exact normalized logarithmic majorant for the unchanged #7863/#8026 supplier."""
from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import signal


F = Fraction
PINS = {
    'BIT-451.json':'538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749',
    'inputs/framework/research/p104-shared-native-helper-splits/retained/compiler/PROOF.md':
        '95cc9e31bc030ec94b04decddcca2d28ee98cfec0ca7803b54666b2b76a5c9ab',
    'inputs/7786/research/p104-iterated-returns/continuation/audit_expanded.py':
        '0316153c1822724e1a3d08066aec9601a891073b0209954eaf302ffa014bf5ac',
    'inputs/cache/parent/qualify_complex.py':'236988674f4efe96134de83a224f9c5f4508f6049237415bc24a18669cf5ad67',
}
THEOREM_SHA = '04eba2e0a2a6cdd4ee512254142cbe45e647a73b66ad67b2c1c0a62e0883238a'
BASE = F('.00387992804359')
CAP = F('.003879928044147')


def require(flag, why):
    if not flag:
        raise ValueError(why)


def verify(root):
    for key,digest in PINS.items():
        require(sha256((root/key).read_bytes()).hexdigest()==digest,key)
    theorem=Path(__file__).with_name('SHIFTED-LOG.md')
    require(sha256(theorem.read_bytes()).hexdigest()==THEOREM_SHA,'original normalized-majorant theorem')
    data=json.loads((root/'BIT-451.json').read_bytes())
    v=data['partition']['factors']
    H=data['uniform']['H']
    C=F(data['separation']['trial'])
    phase=data['cover_and_stock']
    require((H,C,v)==(1202400000000000,F('.003879928046148'),451),'source parameters')
    require([data['partition'][key] for key in ('working_ambient','cutoff','productive_floor')]==
            ['134^451','11^451','16^451'],'same paid geometry')
    A,r,k=134**v,11**v,16**v
    h,p,a,b,j=1024,60,13,15,2406
    t=1-C
    require(r**b<k**a,'all exits have exponent below the rational upper')
    require((1<<(h*(b-a)))*r**b <= A**a, 'shifted-log guard with h on every exit')
    amin,amax=map(F,data['uniform']['ambient_power'])
    eta_min,eta_max=map(F,data['uniform']['eta'])
    require(0<eta_min<=eta_max<1 and 1<amin<=amax and eta_min*amin<=t<=eta_max*amax,
            'outward interval inputs for A^C and t/A^C')
    require(F(a,b)**p<eta_min and F(a,b)**p*amax<t,'positive complement slack')
    # Since A>2^(2h), (1+log2(A)/h)^p > 3^p.
    # The concavity of log2(1+x/h), with value 0 at x=0, interpolates
    # from this proved endpoint to every intermediate base rank.
    require(A>2**(2*h) and amax < 8192 < 3**p,'endpoint implies all ordinary base ranks')
    require((h+H)**p < h**p*2**j,'uniform loss on fixed carrier')
    require(F(j,H)*(H+h)>2*p,'eventual tail via ln(2)>1/2')
    # Two different perturbations: one fails the complete leaf normalization;
    # another fails the all-exit shift while keeping r,k and theta fixed.
    require((h+H)**p >= h**p*2**(j-1),'undercharging the uniform loss must fail')
    require((H+1)**p >= 2**j,'unnormalized estimate cannot justify this charge')
    require((1<<(16384*(b-a)))*r**b>A**a,'excessive normalization fails the shifted exit')
    require(phase['q_condition']=='odd prime q > 2^52*N^5 avoiding frozen finite catalogue witnesses','same prime')
    d=F(1,H*2**44)
    bad=F(phase['bad_surcharge_upper'])
    require(F(1,2)/F(3,2)+F(1,2)/2>F(1,2) and H*d/2==F(1,2**45)>bad==F(1,2**46),'actual carrier cover margin')
    rho=F(phase['rho']);prev=F(phase['seed'])
    require((rho,prev)==(F(1,250),F('.00385248')),'fixed backend structure')
    e=F(j,H)
    covered=C-e-d
    stages=[]
    for _ in range(7):
        ceiling=covered-rho*(covered-prev)
        scale=10**24
        rate=F((ceiling*scale).__floor__()-1,scale)
        require(prev < rate < ceiling < covered < rho < 1-ceiling,'all ordinary gaps')
        stages.append(dict(previous=str(prev),rate=str(rate),slack=str(ceiling-rate)))
        prev=rate
    require(prev>CAP,'last stage supports chosen ordinary cap')
    tick=F(1,10**14)
    claim=(CAP//tick-8)*tick
    tested=claim+7*tick
    raw=tuple(map(F,data['raw_crossing']))
    require(raw==(F('.003879928046154'),F('.003879928046155')),'raw crossing controls')
    # Give the old proof its raw upper and forgive all old cover and bootstrap loss.
    old_e=F(2969,H)
    old_upper=raw[1]-old_e-7*tick
    require(CAP>tested>claim>old_upper>BASE,'strict separation from previous charged proof')
    return dict(pins=PINS,theorem_sha256=THEOREM_SHA,h=h,p=p,theta=str(F(a,b)),H=H,H_times_e=j,
                log_factor_at_rank_one='1',separately_defined_rank_zero='0',uniform_loss=str(e),
                shift_inequality_bit_lengths=[((1<<(h*(b-a)))*r**b).bit_length(),(A**a).bit_length()],
                charged_cover_loss=str(d),covered=str(covered),stages=stages,cap=str(CAP),
                candidate_grid_claim=str(claim),candidate_tested=str(tested),old_cover_forgiven_upper=str(old_upper),
                old_fixed_loss_upper=str(old_upper-d),claim_minus_old_generous_upper=str(claim-old_upper),
                predecessor_published=str(BASE),absolute_gain=str(claim-BASE),exact_relative_percent=str(100*(claim-BASE)/BASE),
                controls=['J=2405 rejected','unnormalized h=1 fails J=2406','h=16384 violates paid-exit shift'])


def bind_outer(outcome,directory):
    app=json.loads((directory/'APPLICATION.json').read_bytes())
    audit=json.loads((directory/'AUDIT.json').read_bytes())
    receipt=json.loads((directory/'receipt.json').read_bytes())
    require(F(receipt['cap'])==F(app['binary_ordinary'])==F(audit['outer']['pinned_binary_cap'])==CAP,'cap')
    require(F(receipt['tested'])==F(audit['outer']['finite_compiler']['tested'])==F(outcome['candidate_tested']),'tested')
    require(F(receipt['claim'])==F(app['application']['claim'])==F(outcome['candidate_grid_claim']),'claim')
    for key in ('APPLICATION.json','AUDIT.json'):
        require(sha256((directory/key).read_bytes()).hexdigest()==receipt['output_sha256'][key],key)


if __name__=='__main__':
    signal.alarm(60)
    cli=ArgumentParser(description=__doc__)
    cli.add_argument('producer',type=Path)
    cli.add_argument('out',type=Path)
    cli.add_argument('--outer',type=Path)
    args=cli.parse_args()
    result=verify(args.producer)
    if args.outer:
        bind_outer(result,args.outer)
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS_NORMALIZED_451_MAJORANT',result['candidate_grid_claim'],result['absolute_gain'])
