#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent binomial atoms and integer binomial-basis coefficient audit."""
from argparse import ArgumentParser
from fractions import Fraction as F
from hashlib import sha256
from math import comb, lcm
from pathlib import Path
import json
import signal

BIT = '538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749'
GRID = '69c8f917d6b2676897639eef67e8f15aae1c23a6bfb608dcd38aed236f299818'
V, H_SCALE = 451, 1804


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source(path, digest):
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == digest, path.name)
    return json.loads(raw)


def paid_bounds(src, old, p):
    require(max(map(int, src['native']['paid'])) < 11**2, 'raw support')
    require(F(old['mean_upper']) < F(3, 4), 'raw mean')
    separation = src['separation']
    uplift = F(separation['paid_uplift_upper'][1])
    alpha = F(separation['three_engine_intervals']['source_1']['alpha'][0])
    eps = F(1, 10**15)
    require(0 <= uplift < eps*alpha**V, 'complete paid surplus')
    atom_weights = [comb(V,k)*3**k*5**(V-k) for k in range(V+1)]
    require(sum(atom_weights) == 8**V, 'unit probability')
    require((F(old['mean_upper'])+eps)/(1+eps) < F(3,4), 'complete mean')
    mu = [F(1)]
    for i in range(1,p+1):
        raw_moment = F(sum(w*(2*k)**i for k,w in enumerate(atom_weights)), 8**V*V**i)
        clipped = min(F(1), raw_moment)
        full = (clipped + eps)/(1+eps)
        mu.append(min(full,F(3,4)) if i == 1 else full)
    return mu


def differences(values):
    first = []
    while values:
        first.append(values[0])
        values = [b-a for a,b in zip(values,values[1:])]
    return first


def ratios(mu,p):
    # Partial sequence for 6*(7/6+sum X) in integer moment units.
    Q = lcm(*(m.denominator for m in mu))
    mu = [int(m*Q) for m in mu]
    v = [7**i for i in range(p+1)]
    kernel = [[comb(i,k)*6**k*mu[k] for k in range(i+1)] for i in range(p+1)]
    nums, dens = [], []
    for g in range(p+1):
        v = [sum(coef*v[i-k] for k,coef in enumerate(row))
             for i,row in enumerate(kernel)]
        nums.append(F(v[-1], 6**p*Q**(g+1)))
        dens.append(F((319+115*g)**p,100**p))
    top,bottom = differences(nums),differences(dens)
    require(all(n >= 0 and d > 0 for n,d in zip(top,bottom)), 'Newton signs')
    return [n/d for n,d in zip(top,bottom)]


def evaluate(src, old, p):
    require(1 <= p <= 64, 'single integral power in audit domain')
    require(old['p_minimum']==27 and old['h']==H_SCALE and old['uniform_J']==1061, 'prior')
    mus = paid_bounds(src,old,p)
    coeffs = ratios(mus,p)
    eta = F(src['uniform']['eta'][0])
    worst = max(coeffs)
    require(worst < eta, 'all-height coefficient capacity')
    H,h = src['uniform']['H'],H_SCALE
    guard = (1+F((134**V).bit_length()-1,h))**p
    require(guard > F(src['uniform']['ambient_power'][1]),'normalized base')
    J = ((H+h)**p//h**p).bit_length()
    require((h**p << (J-1)) <= (H+h)**p < (h**p << J), 'minimum strict J')
    require(F(J,H)*(H+h) > 2*p,'tail derivative')
    rate = F(src['separation']['trial'])-F(J,H)-F(1,H*2**44)
    require(F(src['cover_and_stock']['bad_surcharge_upper']) < F(1,2**45),'same cover')
    rho = F(src['cover_and_stock']['rho'])
    prev = F(src['cover_and_stock']['seed'])
    stages = []
    for _ in range(7):
        ceiling = rate-rho*(rate-prev)
        value = F((ceiling*10**24).__floor__()-1,10**24)
        require(prev < value < ceiling < rate < rho < 1-ceiling, 'strict ordinary stage')
        stages.append([str(value),str(ceiling-value)])
        prev = value
    cap = F((prev*10**17).__floor__(),10**17)
    tick = F(1,10**14)
    claim = (cap//tick-8)*tick
    tested = claim+7*tick
    old_claim = F(old['candidate_grid_claim'])
    old_ceiling = F(src['raw_crossing'][1])-F(old['uniform_loss'])-7*tick
    require(old_claim < old_ceiling < claim < tested < cap,'strict complete comparison')
    return dict(pins={'BIT-451.json': BIT,'grid/RESULT.json': GRID},
                p=p,h=h,atoms=V+1,moments=list(map(str,mus)),
                epsilon_upper='1/1000000000000000',coefficients=list(map(str,coeffs)),
                worst_index=coeffs.index(worst),worst_upper=str(worst),eta_lower=str(eta),
                uniform_J=J,uniform_loss=str(F(J,H)),stages=stages,cap=str(cap),
                candidate_tested=str(tested),candidate_grid_claim=str(claim),
                old_cover_forgiven_upper=str(old_ceiling),separation=str(claim-old_ceiling),
                absolute_gain=str(claim-old_claim),exact_relative_percent=str(100*(claim-old_claim)/old_claim))


def bind(result, root):
    rec = json.loads((root/'receipt.json').read_bytes())
    data = {}
    for key in ('APPLICATION.json','AUDIT.json'):
        data[key] = source(root/key,rec['output_sha256'][key])
    app,audit = data['APPLICATION.json'],data['AUDIT.json']['outer']
    require(F(result['cap']) == F(rec['cap']) == F(app['binary_ordinary']) == F(audit['pinned_binary_cap']), 'outer cap')
    require(F(result['candidate_tested']) == F(rec['tested']) == F(audit['finite_compiler']['tested']), 'outer tested')
    require(F(result['candidate_grid_claim']) == F(rec['claim']) == F(app['application']['claim']), 'outer claim')


if __name__ == '__main__':
    signal.alarm(60)
    parser = ArgumentParser(description=__doc__)
    for arg in ('root','prior','out'):
        parser.add_argument(arg,type=Path)
    parser.add_argument('--power',type=int,required=True)
    parser.add_argument('--outer',type=Path)
    args = parser.parse_args()
    result = evaluate(source(args.root/'BIT-451.json',BIT),source(args.prior,GRID),args.power)
    if args.outer:
        bind(result,args.outer)
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS_BINOMIAL_TENSOR',result['p'],result['uniform_J'],result['candidate_grid_claim'])
