#!/usr/bin/env python3
"""Refine only final-grid rounding of the fully admitted, pinned PR659 witness."""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENGINE = ROOT/'research/complex-k492-owner-repair/vendor/multicold/engines'
OLD_K = Q('0.001656193765416678')
NEW_K = Q('0.001656193765416678434092')
GRID = 10**24
BRIDGE = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1},
          'rows': {'degree_gap': Q(10**6)-Q(51*20161, 25)}}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def decimal(x):
    with localcontext() as context:
        context.prec = 65
        return str(Decimal(x.numerator)/Decimal(x.denominator))


def round_below(margin, grid):
    ticks = margin*grid
    return Q((ticks.numerator-1)//ticks.denominator, grid)


def certificate(assembly_path):
    need(__debug__, 'The inherited outer engine requires assertions; do not use -O')
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for name, digest in pins['engines'].items():
        need(hashlib.sha256((ENGINE/name).read_bytes()).hexdigest() == digest, 'engine source pin: '+name)
    A = load(ENGINE/'outer.py', 'fine_grid_outer')
    M = load(ENGINE/'moment.py', 'fine_grid_mercator')
    B = load(ENGINE/'base_two_moment.py', 'fine_grid_base_two')
    raw = assembly_path.read_bytes()
    data = json.loads(raw)
    need(data['status'] == 'PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY', 'baseline status')
    need(Q(data['kappa']) == OLD_K, 'baseline kappa')
    need(data['complex_profile'] == pins['global_profile'], 'baseline paid profile')
    need(data['surcharge_model'] == {'complex': False, 'bit': True}, 'surcharge model')
    c, b = Q(data['bit_lower']), Q(data['complex_lower'])
    need(str(b) == pins['complex_lower'] and str(c) == pins['bit_lower'], 'supplier endpoints')
    H = {int(k): v for k, v in data['complex_profile'].items()}
    need(73*7168-sum(k*v for k,v in H.items()) == 2560, 'rank deficit')
    moments = []
    for z, accept in [(b, True), (b+Q(1,10**24), False)]:
        l,u = M.moment(H,73,7168,z,False)
        ll,uu = B.moment(73,7168,list(H.items()),z)
        need((u < 1 and uu < 1) if accept else (l > 1 and ll > 1), 'two moment signs')
        moments.append(dict(endpoint=str(z), admitted=accept, mercator=[str(l-1),str(u-1)], base_two=[str(ll-1),str(uu-1)]))
    eta = beta = Q(1,10**24)
    s = min(c,(1-beta)*b)-Q(1,10**27)
    need(0 < s < c and s < (1-beta)*b, 'common saving')
    a = Q(384599,10**10)
    cuts = []
    for _ in range(7):
        old = a
        a = (1-s)*s+s*old
        gap = min(s-a,1-a-s,1-a-s*(1-old),1-s)
        need(old < a < s < 1-a and gap > 0, 'bootstrap recurrence')
        ceil = lambda x: -(-x.numerator//x.denominator)
        cutoff = max(ceil(36/gap**2),ceil(2*(4+512)/gap))
        need(cutoff*gap**2 >= 36 and cutoff*gap >= 2*(4+512), 'finite cutoff')
        cuts.append(dict(exponent=str(a),gap=str(gap),cutoff_log2=str(cutoff)))
    need(cuts == data['bootstrap'], 'changed bootstrap schedule')
    q = a*(1-2*eta)
    margin = (1-eta)*q/(1+q)
    need(round_below(margin,10**18) == OLD_K, 'original rounding')
    need(round_below(margin,GRID) == NEW_K > OLD_K, 'fine-grid improvement')
    baseline = A.assembly(a,b,BRIDGE,OLD_K,eta=eta,beta=beta)
    need({k:str(v) for k,v in baseline['strict_constraints'].items()} == data['outer'], 'baseline outer binding')
    refined = A.assembly(a,b,BRIDGE,NEW_K,eta=eta,beta=beta)
    slacks = refined['strict_constraints']
    need(len(slacks) == 47 and all(x > 0 for x in slacks.values()), '47 strict inequalities')
    # All 40 feasibility constraints stay identical. Only seven kappa gaps shrink.
    for key, value in slacks.items():
        expected = baseline['strict_constraints'][key] - (NEW_K-OLD_K if key.endswith('_above_kappa') else 0)
        need(value == expected, 'unexpected constraint change: '+key)
    controls=[]
    for name, kk, ee, be in [('next_fine_tick',NEW_K+Q(1,GRID),eta,beta),
                             ('zero_eta',NEW_K,Q(0),beta),('zero_beta',NEW_K,eta,Q(0)),
                             ('unit_beta',NEW_K,eta,Q(1)),('equal_margin',margin,eta,beta)]:
        try:
            A.assembly(a,b,BRIDGE,kk,eta=ee,beta=be)
        except AssertionError:
            controls.append(name)
        else:
            raise ValueError('invalid witness accepted: '+name)
    # Strict floor must also handle an exactly integral number of ticks.
    need(round_below(Q(3,GRID),GRID) == Q(2,GRID), 'exact-grid strictness')
    return dict(status='PASS_PR659_FINE_GRID_CONDITIONAL_KAPPA', source_commit=pins['pr659'],
                baseline_assembly_sha256=hashlib.sha256(raw).hexdigest(),
                old_kappa=str(OLD_K),kappa=str(NEW_K),kappa_decimal=decimal(NEW_K),
                increase=str(NEW_K-OLD_K),increase_decimal=decimal(NEW_K-OLD_K),
                grid=GRID,complex_lower=str(b),bit_lower=str(c),global_profile=H,
                exact_moments=moments,bootstrap=cuts,
                outer_parameters=refined['parameters'],strict_constraints=slacks,
                margin=margin,remaining_margin=margin-NEW_K,negative_controls=controls,
                exact_grid_control=True,scope='Final-grid refinement only; unchanged PR659 construction, costs, suppliers and conditional assumptions. No new circuit or cheaper recurrence.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assembly',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    result=certificate(args.assembly)
    args.out.write_text(json.dumps(result,indent=2,default=str)+'\n')
    print(result['status'],result['kappa_decimal'],'gain',result['increase_decimal'])


if __name__ == '__main__':
    main()
