#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independently price p=21 and reject p<=20 on the one fixed tensor envelope."""
from argparse import ArgumentParser
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import signal

AUDIT = 'd8bed723957dcd30cc6462562b8e9d5ee33a36891c73916a986459969895993e'
TENSOR = '288e194853bb736973600eb51da2983414679a185629c30f769d701f4c55e811'


def main():
    signal.alarm(60)
    cli = ArgumentParser(description=__doc__)
    for key in ('root','grid','tensor','out'):
        cli.add_argument(key,type=Path)
    cli.add_argument('--outer',type=Path)
    cli.add_argument('--tensor-audit',type=Path,default=Path(__file__).with_name('audit.py'))
    args = cli.parse_args()
    # Execute exactly the verified bytes, without resolving imports through the checkout.
    code = args.tensor_audit.read_bytes()
    if sha256(code).hexdigest() != AUDIT:
        raise ValueError('tensor/audit.py source hash')
    old_module = {'__name__': 'pinned_tensor_audit'}
    exec(compile(code,'tensor/audit.py','exec'), old_module)
    source, require = old_module['source'], old_module['require']
    bit = source(args.root/'BIT-451.json', old_module['BIT'])
    grid = source(args.grid, old_module['GRID'])
    prior = source(args.tensor, TENSOR)
    require(prior['p']==23 and prior['h']==1804 and prior['uniform_J']==904,'R337 prior')
    good = old_module['evaluate'](bit,grid,21)
    require(good['moments']==prior['moments'][:22],'same formal envelope')
    lower, upper = map(F,bit['uniform']['eta'])
    leading_base = F(good['moments'][1])/F(23,20)
    bad = leading_base**20
    require(0 < leading_base < 1 and bad > upper >= lower > F(good['worst_upper']),
            'p20 limit and p21 all-height capacity')
    require(F(good['coefficients'][-1]) == leading_base**21, 'leading coefficient index')
    tick = F(1,10**14)
    claim = F(good['candidate_grid_claim'])
    old_claim = F(prior['candidate_grid_claim'])
    ceiling = F(bit['raw_crossing'][1])-F(prior['uniform_loss'])-7*tick
    require(claim>ceiling>old_claim, 'strict previous-complete ceiling')
    good.update(pins={**good['pins'],'tensor/audit.py':AUDIT,'tensor/RESULT.json':TENSOR},
                old_cover_forgiven_upper=str(ceiling),separation=str(claim-ceiling),
                absolute_gain=str(claim-old_claim),exact_relative_percent=str(100*(claim-old_claim)/old_claim),
                rejected_power=20,rejected_limit=str(bad),eta_upper=str(upper),
                limiting_base=str(leading_base),fixed_envelope_minimum_power=21)
    if args.outer:
        old_module['bind'](good,args.outer)
    args.out.write_text(json.dumps(good,indent=2)+'\n')
    print('PASS_TENSOR_INTEGER_POWER',good['fixed_envelope_minimum_power'],good['uniform_J'],good['candidate_grid_claim'])


if __name__ == '__main__':
    main()
