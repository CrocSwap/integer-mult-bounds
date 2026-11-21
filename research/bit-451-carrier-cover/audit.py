#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact proof audit for reusing the completed #7863 binary service and cover unchanged."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from time import monotonic

BRIDGE = 'inputs/framework/research/p104-shared-native-helper-splits/retained/compiler/bit-audit/'
PINS = {
    'BIT-451.json':'538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749',
    'consumer-replay/CONSUMER.json':'580ba8c262de41c99142c7ed9b7c412821e12dd3a491fde1ee974bda45af1d54',
    'PROOF.md':'85e4a9a88411e1d763e5d6360b1093f8987c267be853c42322aa5e812dc13698',
    BRIDGE+'retained/DELAYED-COVER-BRIDGE.md':'9731b93026717f5fa15851e3633cbb4bdc76eba2bffb9d6b4a3b69f7dd502443',
    BRIDGE+'PROOF.md':'ab5a2a5da1aab0193e286de8e16bc62840be760679c1f9e70218ce13225f69cf',
    'replay_451.py':'4168fb987bbb75f4d0eee051c8a1c28382dbc53ee062aa794db867a10b0d0643',
}
CAP = Q('0.00387992804364799')


def require(test,msg):
    if not test:
        raise ValueError(msg)


def stage(previous,rate,rho,claim):
    envelope = rate-rho*(rate-previous)
    require(previous < claim < envelope < rate < rho and rho < 1-envelope,'ordinary stage inequalities')
    return dict(previous=str(previous),claim=str(claim),envelope=str(envelope),
                recursive_gap=str(envelope-claim),linear_gap=str(rho-claim),
                adapter_gap=str(1-rho-claim))


def run(root):
    for path, pin in PINS.items():
        require(sha256((root/path).read_bytes()).hexdigest()==pin,'pin mismatch: '+path)
    binary=json.loads((root/'BIT-451.json').read_bytes())
    old=json.loads((root/'consumer-replay/CONSUMER.json').read_bytes())
    phase=binary['cover_and_stock']
    H=binary['uniform']['H']
    C=Q(binary['separation']['trial'])
    E=Q(binary['uniform']['uniform_loss'])
    old_loss=Q(phase['loss']);rho=Q(phase['rho']);seed=Q(phase['seed'])
    require((C,E,old_loss,H,rho,seed)==(Q('.003879928046148'),Q(1,400000000000),Q(1,10**13),1202400000000000,Q(1,250),Q('.00385248')),'fixed source parameters')
    require(phase['q_condition']=='odd prime q > 2^52*N^5 avoiding frozen finite catalogue witnesses','covered prime contract')
    require(binary['partition']['factors']==451 and binary['partition']['cutoff']=='11^451' and binary['partition']['productive_floor']=='16^451','same physical recipe')
    base=Q(phase['covered'])
    require(base==C-E-old_loss,'old losses')
    prev=seed
    for record in phase['stages']:
        require(Q(record['previous'])==prev,'old stage input')
        proof=stage(prev,base,rho,Q(record['claim']))
        require(Q(proof['recursive_gap'])==Q(record['strict_gap_exact']),'old seven-stage control')
        prev=Q(record['claim'])
    require(len(phase['stages'])==7 and prev==Q(old['binary_ordinary'])==Q('.00387992804354799998'),'old final ordinary')
    # The source's full single-factor fallback bound is 2N^3/q * 32N^2.
    bad=Q(64,2**52)
    require(bad==Q(phase['bad_surcharge_upper'])==Q(1,2**46) and bad<old_loss/4,'old surcharge control')
    loss=Q(1,H*2**44)
    require(bad>loss/4 and H*loss<1,'old sufficient shortcuts cannot certify this loss')
    # Integral of 1/t over [1,3/2] and [3/2,2] lower-bounded by right endpoint rectangles.
    log2_lower=Q(1,2)/Q(3,2)+Q(1,2)/2
    require(log2_lower==Q(7,12)>Q(1,2),'logarithmic lower bound')
    # exp(x) >= 1+x. Normalize by the actual N=2^H, not the old floor(log_N).
    raise_lower=1+H*loss*Q(1,2)
    require(1+H*loss*log2_lower>raise_lower==1+Q(1,2**45),'denominator')
    multiplier=(1+bad)/raise_lower
    require(0<multiplier<1 and (1+bad)/(1+0)>1,'full cover multiplier and zero-loss control')
    rate=C-E-loss
    prev=seed;steps=[]
    for j in range(7):
        env=(1-rho)*rate+rho*prev
        # Seven strict analytical rates; weaken the last to the supplied service cap.
        scale=10**24
        claim=Q((env.numerator*scale//env.denominator)-1,scale)
        steps.append(stage(prev,rate,rho,claim))
        prev=claim
    require(prev>CAP>Q(old['binary_ordinary']),'strict ordinary advancement')
    try:
        stage(prev,rate,rho,(1-rho)*rate+rho*prev)
    except ValueError as exc:
        require(str(exc)=='ordinary stage inequalities','stage control')
    else:
        raise ValueError('equal envelope was accepted')
    lower,upper=map(Q,binary['raw_crossing'])
    require(lower==Q('.003879928046154') and upper==Q('.003879928046155'),'untouched native crossing')
    ceiling=upper-E-old_loss
    require(ceiling==Q('.003879928043555') and CAP>ceiling,'old fixed-loss proof ceiling')
    return dict(provenance=PINS,head_7863='b3e4412fe01f07dc58305616fabf96345f49a781',
                C=str(C), uniform_loss=str(E), old_cover_loss=str(old_loss),new_cover_loss=str(loss),
                H=H,q_lower_bound='2^52*N^5',log_two_lower=str(log2_lower),H_times_d=str(H*loss),
                charge_upper=str(bad),normalization_lower=str(raise_lower),multiplier_upper=str(multiplier),
                contraction_slack=str(1-multiplier),covered=str(rate),seven_strict_stages=steps,
                ordinary_cap=str(CAP),old_fixed_loss_component_ceiling=str(ceiling),
                old_native_crossing=[str(lower),str(upper)],old_published=str(Q(old['claim'])),
                condition='Same #7863 opaque physically completed supplier, compiled uniform word, q, cover bound, restored original and nested stock, precision and analytic recovery',
                controls=['same old seven-stage chain','old d/4 shortcut unavailable','zero-loss upper fails','envelope equality rejected'])


def consumer(result,compiled):
    app=json.loads((compiled/'APPLICATION.json').read_bytes())
    audit=json.loads((compiled/'AUDIT.json').read_bytes())
    receipt=json.loads((compiled/'receipt.json').read_bytes())
    require(all(Q(x)==CAP for x in (receipt['cap'],app['binary_ordinary'],audit['outer']['pinned_binary_cap'])),'ordinary binding')
    for key in ('APPLICATION.json','AUDIT.json'):
        require(receipt['output_sha256'][key]==sha256((compiled/key).read_bytes()).hexdigest(),'consumer output pin')
    new=Q(app['application']['claim']); old=Q(result['old_published'])
    tested=Q(audit['outer']['finite_compiler']['tested'])
    require(Q(receipt['claim'])==new==Q('.00387992804356') and Q(receipt['tested'])==tested==Q('.00387992804363'),'outer points')
    require(CAP>tested>new>Q(result['old_fixed_loss_component_ceiling']),'separation from old fixed-loss recurrence')
    require(new-old==Q(1,10**13),'campaign comparison arithmetic')
    result['outer']=dict(claim=str(new),tested=str(tested),bit_headroom=str(CAP-tested),
                         delta=str(new-old),percentage=str(100*(new-old)/old),
                         over_fixed_loss_upper=str(new-Q(result['old_fixed_loss_component_ceiling'])),
                         consumer_hashes=receipt['output_sha256'])


if __name__=='__main__':
    start=monotonic()
    p=ArgumentParser(description=__doc__);p.add_argument('producer_root',type=Path);p.add_argument('out',type=Path)
    p.add_argument('--consumer',type=Path)
    args=p.parse_args()
    data=run(args.producer_root)
    if args.consumer:
        consumer(data,args.consumer)
    data['seconds']=monotonic()-start
    args.out.write_text(json.dumps(data,indent=2)+'\n')
    print('PASS',data['ordinary_cap'],data.get('outer',{}).get('claim'),data['seconds'])
