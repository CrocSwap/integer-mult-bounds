#!/usr/bin/env python3
"""Exact backoff refinement of the physically validated cost/live profile.

Parameter refinement follows the PR61 precedent of Alejandro Zarzuelo
Urdiales; exact moment bounds and assembly adapter are Rohan Arun's PR67.
Dominik Scholz with substantial OpenAI GPT-6 Astra assistance. Apache-2.0.
This does not modify or rerun the frozen physical construction.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record',action='store_true',help='Regenerate the exact certificate')
    args=parser.parse_args()
    manifest=json.loads((HERE/'source-manifest.json').read_text())
    for name,digest in manifest.items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name+' changed'
    source=ROOT/'research/slot-cost-rank-pair/arithmetic/refine.py'
    spec=importlib.util.spec_from_file_location('pr67_parameter_refinement',source)
    exact=importlib.util.module_from_spec(spec);spec.loader.exec_module(exact)
    old=json.loads((ROOT/'research/cost-live-both/candidate.json').read_text())
    receipt=json.loads((ROOT/'research/cost-live-both/validation-receipt.json').read_text())
    assert receipt['candidate_sha256']==sha256((ROOT/'research/cost-live-both/candidate.json').read_bytes()).hexdigest()
    profile=old['bit'];rows={int(t):n for t,n in profile['child_multiplicities'].items()}
    ab=Q(old['bit_saving']);old_kappa=Q(old['kappa']);backoff=Q(1,10**18)
    accepted=exact.exact_moment(profile['m'],profile['W'],rows,ab)
    excluded=exact.exact_moment(profile['m'],profile['W'],rows,ab+Q(1,10**18))
    assert accepted['upper']<1<excluded['lower']
    assembled=exact.assemble(old['finite_bridge'],ab,backoff,10**18)
    kappa=assembled['kappa']
    assert old_kappa<kappa<ab/(1+ab)
    result=dict(status='PASS exact parameter-only refinement; frozen physical evidence unchanged',
        kappa=kappa,bit_saving=ab,h_backoff=backoff,
        accepted_moment=accepted,excluded_next_bit_moment=excluded,
        preferred=assembled,finite_bridge=old['finite_bridge'],bit=profile,
        comparison=dict(pr68_commit='85781f6',previous_kappa=old_kappa,
                        difference=kappa-old_kappa,ratio=kappa/old_kappa,
                        same_bit_scoped_limit=ab/(1+ab)),
        source_sha256=manifest,
        physical_validation_receipt_sha256=sha256((ROOT/'research/cost-live-both/validation-receipt.json').read_bytes()).hexdigest(),
        physical_replayed_here=False,
        scope='Exact arithmetic only. The frozen full physical receipt is retained; all inherited all-size interfaces remain conditional.')
    encoded=exact.arithmetic.js(result)
    if args.record:
        (HERE/'certificate.json').write_text(json.dumps(encoded,indent=2,sort_keys=True)+'\n')
    else:
        assert encoded==json.loads((HERE/'certificate.json').read_text()),'Parameter certificate changed'
    print('PARAMETER GAIN',kappa,'bit',ab,'backoff',backoff,'difference',kappa-old_kappa,
          'cutoff',assembled['eventual_bounds']['common_cutoff'],flush=True)


if __name__=='__main__':
    main()
