#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""One fixed mean 749/1000, power 20, original 451-fold paid tensor."""
from argparse import ArgumentParser
from fractions import Fraction as F
from hashlib import sha256
from math import comb
from pathlib import Path
import json
import signal

TENSOR_AUDIT = 'd8bed723957dcd30cc6462562b8e9d5ee33a36891c73916a986459969895993e'
MINIMUM = '2c7692f263da6ccaacb7054471aff9d8a693371e8dcb3b83390d70a7bcff4d10'


def evaluate(base, bit, grid, old):
    require = base['require']
    h, v, p = 1804,451,20
    mean, eps = F(749,1000),F(1,10**15)
    require(old['fixed_envelope_minimum_power']==21 and old['uniform_J']==825,'predecessor')
    require(max(map(int,bit['native']['paid'])) < 11**2,'bounded original ranks')
    raw_mean = F(grid['mean_upper'])
    u = F(bit['separation']['paid_uplift_upper'][1])
    a = F(bit['separation']['three_engine_intervals']['source_1']['alpha'][0])
    require(0 <= u < eps*a**v and raw_mean < (raw_mean+eps)/(1+eps) < mean, 'complete mean and split')
    # Chord endpoints have raw probability mean/2 of the value two.
    prob = mean/2
    l,den = prob.numerator,prob.denominator
    masses = [comb(v,k)*l**k*(den-l)**(v-k) for k in range(v+1)]
    total = den**v
    require(sum(masses)==total,'452-atom unit mass')
    mu = [F(1),mean]
    for i in range(2,p+1):
        moment = F(sum(m*(2*k)**i for k,m in enumerate(masses)),total*v**i)
        mu.append((min(1,moment)+eps)/(1+eps))
    coefficients = base['ratios'](mu,p)
    lower,upper = map(F,bit['uniform']['eta'])
    maximum = max(coefficients)
    require(len(coefficients)==p+1 and maximum < lower < upper < F(old['rejected_limit']), 'contraction and old failing control')
    require(coefficients[-1]==(mean/F(23,20))**p,'leading ratio')
    H = bit['uniform']['H']
    require((1+F((134**v).bit_length()-1,h))**p > F(bit['uniform']['ambient_power'][1]),'ordinary base')
    J = ((h+H)**p//h**p).bit_length()
    require((h**p << (J-1)) <= (H+h)**p < (h**p << J) and F(J,H)*(h+H)>2*p,'strict carrier and derivative')
    rate = F(bit['separation']['trial'])-F(J,H)-F(1,H*2**44)
    stock = bit['cover_and_stock']
    require(F(stock['bad_surcharge_upper']) < F(1,2**45),'charged cover')
    value, rho = F(stock['seed']), F(stock['rho'])
    stages = []
    for _ in range(7):
        bound = rate-rho*(rate-value)
        new = F((bound*10**24).__floor__()-1,10**24)
        require(value < new < bound < rate < rho < 1-bound,'strict stage')
        stages.append([str(new),str(bound-new)])
        value = new
    units = (value*10**17).__floor__()
    cap = F(units,10**17)
    tick = F(1,10**14)
    claim = (cap//tick-8)*tick
    tested = claim + 7*tick
    old_claim = F(old['candidate_grid_claim'])
    ceiling = F(bit['raw_crossing'][1])-F(old['uniform_loss'])-7*tick
    require(old_claim < ceiling < claim < tested < cap,'complete strict comparison')
    return dict(pins={'BIT-451.json':base['BIT'],'grid/RESULT.json':base['GRID'],
                      'tensor/MINIMUM.json':MINIMUM,'tensor/audit.py':TENSOR_AUDIT},
                p=p,h=h,atoms=v+1,mean=str(mean),raw_mean_upper=str(raw_mean),
                completed_mean_upper=str((raw_mean+eps)/(1+eps)),epsilon_upper=str(eps),
                moments=list(map(str,mu)),coefficients=list(map(str,coefficients)),
                worst_upper=str(maximum),worst_index=coefficients.index(maximum),eta_lower=str(lower),
                prior_rejected_limit=old['rejected_limit'],uniform_J=J,uniform_loss=str(F(J,H)),
                cap=f'{units//10**17}.{units%10**17:017d}',stages=stages,candidate_tested=str(tested),
                candidate_grid_claim=str(claim),old_cover_forgiven_upper=str(ceiling),
                separation=str(claim-ceiling),absolute_gain=str(claim-old_claim),
                exact_relative_percent=str(100*(claim-old_claim)/old_claim))


def main():
    signal.alarm(60)
    parser = ArgumentParser(description=__doc__)
    for name in ('root','grid','minimum','out'):
        parser.add_argument(name,type=Path)
    parser.add_argument('--tensor-audit',type=Path,default=Path(__file__).with_name('audit.py'))
    parser.add_argument('--outer',type=Path)
    args = parser.parse_args()
    code = args.tensor_audit.read_bytes()
    if sha256(code).hexdigest()!=TENSOR_AUDIT:
        raise ValueError('tensor/audit.py')
    base = {'__name__':'pinned_tensor_audit'}
    exec(compile(code,'tensor/audit.py','exec'),base)
    source,require = base['source'],base['require']
    bit = source(args.root/'BIT-451.json',base['BIT'])
    result = evaluate(base,bit,source(args.grid,base['GRID']),source(args.minimum,MINIMUM))
    if args.outer:
        base['bind'](result,args.outer)
        r = json.loads((args.outer/'receipt.json').read_bytes())
        key = 'adapter/binary/FINITE.json'
        finite = source(args.outer/key,r['output_sha256'][key])
        require(finite['ordinary_admitted']==r['cap']==result['cap'] and
                finite['word_sha256']==bit['native']['candidate_canonical_sha256'],'actual finite supply')
        require({'low_cap_rejected','extra_rank_1_charge_rejected'}.issubset(r['controls']), 'signed consumer negative controls')
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS_COMPLETE_MEAN',result['mean'],result['p'],result['cap'],result['candidate_grid_claim'])


if __name__=='__main__':
    main()
