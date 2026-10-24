#!/usr/bin/env python3
"""ROOT ONLY, HELD: one rational gate after an accepted peer source review.

No logarithm, fractional power, Powers engine, source evaluator, solver or
candidate/partition enumeration. The conclusion is conditional COMPLEX only.
"""
from argparse import ArgumentParser
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json


def need(value, message):
    if not value:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def hist(value):
    return {int(r): int(n) for r, n in value.items()}


def main():
    ap = ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--model', required=True)
    ap.add_argument('--source-gate', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    root = Path(args.root).resolve()
    model_path, gate_path = root/args.model, root/args.source_gate
    model = json.loads(model_path.read_text())
    gate = json.loads(gate_path.read_text())  # Intentionally absent while HOLD.
    need(gate['root_accepted'] is True, 'HOLD: peer source gate not root-accepted')
    need(gate['scope_tag'] == model['scope_tag'], 'different source alphabet')
    need(gate['model_sha256'] == digest(model_path), 'source gate binds a different model')
    need(gate['author_BIT_n4_closed'] is False and gate['BC120_closed'] is False,
         'source gate overstates author BIT or BC120 scope')
    review = root/gate['peer_review_path']
    need(digest(review) == gate['peer_review_sha256'], 'peer source-review bytes changed')
    for row in model['source_bindings']:
        need(digest(root/row['path']) == row['sha256'], 'changed source: '+row['path'])

    # Arithmetic begins only AFTER the independent source gate above.
    kernelP, kernelH = hist(model['kernel_paid']), hist(model['kernel_helpers'])
    need(kernelP == {1:2193,2:412,3:510,4:127,5:40,8:8}, 'different kernel paid alphabet')
    need(kernelH == {4:28,7:7,8:55,9:318}, 'different helper alphabet')
    P = {r:5*n for r, n in kernelP.items()}
    P[1] += 112
    helperT = {r:5*n for r, n in kernelH.items()}
    quotient, remainder = divmod(10, 4)
    degrees = [quotient]*(4-remainder)+[quotient+1]*remainder
    need(degrees == [2,2,3,3], 'written concavity cap changed')
    T = dict(helperT)
    for degree in degrees:
        rank = 1+8*degree
        T[rank] = T.get(rank, 0)+112
    need(P == hist(model['paid']) and T == hist(model['target_cap']), 'model census mismatch')
    C0 = F(33, 10000)
    ranks = sorted(set(P)|set(T))
    L = {r:F(2*(r.bit_length()-1), 3) for r in ranks}
    U = {r:(r-1).bit_length() for r in ranks}
    target_upper = sum(F(n*r)/(1+C0*L[r]) for r, n in T.items())
    paid_lower = sum(F(n*r)*(1-C0*U[r]) for r, n in P.items())
    upper_gate = target_upper-paid_lower
    need(target_upper == F(2012500,2511)+F(82550000,5033)+F(11760000,1261),
         'written target envelope differs')
    need(paid_lower == F(13306541,500), 'written paid envelope differs')
    need(F(2012500,2511)<802 and F(82550000,5033)<16402 and F(11760000,1261)<9326,
         'simple integer envelope failed')
    need(upper_gate < -F(41541,500) < 0, 'negative rational gate failed')
    signed = {r:T.get(r,0)-P.get(r,0) for r in ranks}
    need(all((a<0 and r<7) or (a>0 and r>=7) for r,a in signed.items()),
         'normalized monotonicity sign separation failed')
    need(any(a<0 and r<7 for r,a in signed.items())
         and any(a>0 and r>7 for r,a in signed.items()), 'strict monotonicity absent')
    need(sum(P.values())==16562 and sum(T.values())==2488
         and sum(r*n for r,n in P.items())==26707
         and sum(r*n for r,n in T.items())==26723, 'integer inventories differ')
    result = {
        'schema':'fivefull-onethin-held-rational-gate/1',
        'status':'PASS_CONDITIONAL_COMPLEX_CURRENT_KERNEL_NEGATIVE_GATE_FROM_0033',
        'model_sha256':digest(model_path),'checker_sha256':digest(Path(__file__)),
        'source_gate_sha256':digest(gate_path),
        'peer_source_review':{'path':str(review.relative_to(root)),'sha256':digest(review)},
        'source_bindings':model['source_bindings'],'scope_tag':model['scope_tag'],
        'C0':str(C0),'paid':P,'helper_targets':helperT,'main_balanced_degrees':degrees,
        'target_cap':T,'signed_coefficients':signed,
        'log_lower':{r:str(v) for r,v in L.items()},'log_upper':U,
        'target_upper':str(target_upper),'paid_lower':str(paid_lower),
        'upper_signed_moment_gate':str(upper_gate),
        'strict_simple_upper':'-41541/500',
        'all_C_conclusion':'Tcap_(1-C)-P_(1-C)<0 for33/10000<=C<1 underexacthypotheses',
        'monotonicity':'Divideby7^(1-C):negativecoefficientsbelow7andpositivecoefficientsabove7strictlydecreaseinC;rank7constant.',
        'fractional_power_log_exp_engine_calls':0,'candidate_or_partition_enumerations':0,
        'source_applicability_review_performed_here':False,
        'author_BIT_n4_case_closed':False,'BC120_case_closed':False,
        'complete_caller':False,'new_target_credit_admitted':False,
        'funding_admitted':False,'new_kappa':None,
    }
    out = root/args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'])


if __name__ == '__main__':
    main()
