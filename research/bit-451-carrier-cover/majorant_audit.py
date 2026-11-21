#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Rational cross multiplication and integer powers on one frozen compiler estimate."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import signal

PINS = {
    'BIT-451.json': '538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749',
    'inputs/framework/research/p104-shared-native-helper-splits/retained/compiler/PROOF.md':
        '95cc9e31bc030ec94b04decddcca2d28ee98cfec0ca7803b54666b2b76a5c9ab',
    'inputs/cache/parent/qualify_complex.py':
        '236988674f4efe96134de83a224f9c5f4508f6049237415bc24a18669cf5ad67',
    'inputs/7786/research/p104-iterated-returns/continuation/audit_expanded.py':
        '0316153c1822724e1a3d08066aec9601a891073b0209954eaf302ffa014bf5ac',
}
CAP = Q('.00387992804367877')
OLD_CLAIM = Q('.00387992804356')
TICK = Q(1,10**14)


def need(flag, what):
    if not flag:
        raise ValueError(what)


def verify(root):
    for path,digest in PINS.items():
        need(sha256((root/path).read_bytes()).hexdigest()==digest, path)
    item=json.loads((root/'BIT-451.json').read_text())
    uniform=item['uniform']
    count=item['partition']['factors']
    H=uniform['H']
    C=Q(item['separation']['trial'])
    need((count,H,C)==(451,1202400000000000,Q('.003879928046148')),'source')
    need(item['partition']['cutoff']=='11^451' and item['partition']['productive_floor']=='16^451'
         and item['partition']['working_ambient']=='134^451','stock parameters')
    paid=11**count; floor=16**count; ambient=134**count
    t=1-C; theta_bar=Q(173,200); p=Q(237,4); E=Q(2969,H)
    # The certified test uses the *actual* finite ambient and maximum paid cutoff.
    need(paid**200 < floor**173,'strict true exit ratio')
    need((1<<27)*paid**200 <= ambient**173,'shifted exit inequality')
    elo,ehi=map(Q,uniform['eta']); alo,ahi=map(Q,uniform['ambient_power'])
    need(0<elo<=ehi<1 and 1<alo<=ahi and elo*alo<=t<=ehi*ahi,'archived interval directions')
    # Check from both the archived eta enclosure and an independent integer
    # form after substituting t/(ambient^C) using the archived upper endpoint.
    need(theta_bar**237 < elo**4 and theta_bar**237 * ahi**4 < t**4,'complement margin')
    need(ahi**4 < 2**237,'ambient base condition')
    need((H+1)**237 < 2**(4*2969),'one fixed carrier and suggested uniform loss')
    need((H+1)*E>2*p,'eventual tail monotonicity')
    # Old source control and three single-coordinate perturbations.
    need(Q(13,15)**60<elo and ahi<2**60 and (H+1)**60<2**3006,'known-good old majorant')
    need(Q(13,15)**59>=ehi,'old p=59 complement must fail')
    need(theta_bar**236 >= ehi**4,'lowering new p to 59 must fail')
    need((H+1)**237 >= 2**(4*2968),'reducing new carrier exponent by one must fail')
    need((H+1)**60 >= 2**2969,'old p does not establish the new loss')
    phase=item['cover_and_stock'];rho=Q(phase['rho']); seed=Q(phase['seed'])
    need(phase['q_condition']=='odd prime q > 2^52*N^5 avoiding frozen finite catalogue witnesses','same q contract')
    d=1/Q(H*2**44);bad=Q(phase['bad_surcharge_upper'])
    log_lower=Q(1,2)*Q(2,3)+Q(1,2)*Q(1,2)
    need(log_lower>Q(1,2) and 1+H*d*log_lower > 1+Q(1,2**45) > 1+bad,'same full fallback')
    base=C-E-d; previous=seed; steps=[]
    for _ in range(7):
        envelope=(1-rho)*base+rho*previous
        scaling=10**24; rate=Q((envelope*scaling).__floor__()-1,scaling)
        need(previous<rate<envelope<base<rho<1-envelope,'root cost, ownership and finite gaps')
        steps.append(dict(previous=str(previous),rate=str(rate),recursive_gap=str(envelope-rate)))
        previous=rate
    need(previous>CAP,'strict ordinary service endpoint')
    rawlo,rawhi=map(Q,item['raw_crossing'])
    need((rawlo,rawhi)==(Q('.003879928046154'),Q('.003879928046155')),'old crossing')
    old_e=Q(uniform['uniform_loss']);old_fixed=rawhi-old_e-d-7*TICK
    # This control forgives the whole old cover loss and stage rounding.
    generous=rawhi-old_e-7*TICK
    # Actual equality of the rank-selected outer branch is bound separately by
    # the replay. Here assume the signed rational branch is not the bottleneck.
    grid=(CAP//TICK-8)*TICK; tested=grid+7*TICK
    need(CAP>tested>grid>generous>=old_fixed>OLD_CLAIM,'target separation')
    return dict(pins=PINS,theta=str(theta_bar),p=str(p),H=H,H_times_uniform_loss=2969,
                directed_ambient=list(map(str,(alo,ahi))),directed_eta=list(map(str,(elo,ehi))),
                uniform_loss=str(E),cover_loss=str(d),covered_rate=str(base),ordinary_steps=steps,
                cap=str(CAP),candidate_grid_claim=str(grid),candidate_tested=str(tested),
                old_fixed_loss_complete_upper=str(old_fixed),old_cover_forgiven_upper=str(generous),
                separation_even_forgiving_cover=str(grid-generous),price_delta_vs_8026=str(grid-OLD_CLAIM),
                exact_relative_percent_vs_8026=str(100*(grid-OLD_CLAIM)/OLD_CLAIM),
                verification='Independent component and grid bound; verify_majorant.py replays and binds the complete application',
                controls=['p=60 original passes','p=59 complement fails on old and new theta',
                          '2968 instead of 2969 rejected','p=60 fails at 2969'])


def bind_outer(directory, result):
    """Authenticate the installed ordinary input, grid result and both output bytes."""
    app = json.loads((directory / 'APPLICATION.json').read_bytes())
    audit = json.loads((directory / 'AUDIT.json').read_bytes())
    summary = json.loads((directory / 'receipt.json').read_bytes())
    need(Q(app['binary_ordinary']) == Q(audit['outer']['pinned_binary_cap']) == Q(summary['cap']) == CAP,
         'installed cap')
    need(Q(audit['outer']['finite_compiler']['tested']) == Q(summary['tested']) == Q(result['candidate_tested']),
         'tested point')
    need(Q(app['application']['claim']) == Q(summary['claim']) == Q(result['candidate_grid_claim']),
         'outer claim')
    for path in ('APPLICATION.json', 'AUDIT.json'):
        need(sha256((directory / path).read_bytes()).hexdigest() == summary['output_sha256'][path], path)


def main():
    signal.alarm(60)
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('producer', type=Path)
    parser.add_argument('out', type=Path)
    parser.add_argument('--outer', type=Path)
    args = parser.parse_args()
    result = verify(args.producer)
    if args.outer:
        bind_outer(args.outer, result)
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS_451_MAJORANT_COMPONENT', result['candidate_grid_claim'], result['price_delta_vs_8026'])


if __name__ == '__main__':
    main()
