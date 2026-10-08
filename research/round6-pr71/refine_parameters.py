#!/usr/bin/env python3
"""Exact positive-backoff refinement of immutable PR71.

PR71 graph, next-use score and package: Chafik Boukhalfa; prior PR65/67
arithmetic: Rohan Arun; parameter refinement precedent: Alejandro Zarzuelo
Urdiales PR61. Dominik Scholz, with substantial OpenAI GPT-6 Astra assistance.
Apache-2.0; inherited notices and conditional theorem interfaces apply.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=HERE/'baseline'
PIN='1bef94fd40a746452548c84a4a8f8834670a3113'
sys.path.insert(0,str(BASE/'scripts/experiments'))
import split_pair_compose as inherited
import binary_frame_math as arithmetic


def main():
    # This validates the full original source/finite-input closure, including
    # exact predecessor archives and original generator/configuration hashes.
    sources=inherited.check_sources()
    physical=inherited.profile()
    original=json.loads((BASE/'certificates/split-pair-kappa.json').read_text())
    for name,value in arithmetic.js(physical).items():
        assert value==original['bit'][name],name+' differs from pinned complete profile'
    ab=Q(original['bit_saving']);old=Q(original['kappa'])
    assert ab==Q(12854322426487,250000000000000000)
    assert old==Q(51414646104039,10**18)
    rows=physical['child_multiplicities'];scale=10**18
    accepted=inherited.refine.exact_moment(575,physical['W'],rows,ab)
    rejected=inherited.refine.exact_moment(575,physical['W'],rows,ab+Q(1,scale))
    assert accepted['upper']<1<rejected['lower']
    independent=inherited.audit.independent_moment(arithmetic.js(physical),ab,arithmetic.js(accepted['terms']))
    independent_next=inherited.audit.independent_moment(arithmetic.js(physical),ab+Q(1,scale),arithmetic.js(accepted['terms']))
    assert independent[1]<1<independent_next[0]
    old_assembly=inherited.refine.assemble(original['finite_bridge'],ab,Q(1,10**12),scale)
    assert old_assembly['kappa']==old
    result=inherited.refine.assemble(original['finite_bridge'],ab,Q(1,10**18),scale)
    kappa=result['kappa'];assert old<kappa<ab/(1+ab)
    locked=[BASE/'research/split-pair/SOURCE.json',BASE/'certificates/split-pair-kappa.json',Path(__file__)]
    lock=dict(baseline_commit=PIN,files={str(p.relative_to(HERE)):sha256(p.read_bytes()).hexdigest() for p in locked})
    certificate=dict(status='PASS exact arithmetic refinement; unchanged PR71 physical construction',
        kappa=kappa,bit_saving=ab,h_backoff=Q(1,10**18),preferred=result,
        bit=physical,accepted_moment=accepted,rejected_moment=rejected,
        independent_enclosures=dict(accepted=independent,rejected=independent_next),
        finite_bridge=original['finite_bridge'],source_lock=lock,
        comparison=dict(pr71_commit=PIN,pr71_kappa=old,difference=kappa-old,
                        same_bit_scoped_limit=ab/(1+ab)),
        physical_replay_rerun_here=False,
        pending_checks=['Independent fresh dirty-word/profile rebuild of unchanged PR71 physical artifacts, if desired',
                        'Broad repository and CI checks'],
        scope='Source closure, paid-profile reconstruction and exact arithmetic verified; all-size compiler/tape/analytic interfaces remain conditional.')
    (HERE/'parameter-certificate.json').write_text(json.dumps(arithmetic.js(certificate),indent=2,sort_keys=True)+'\n')
    (HERE/'parameter-source-lock.json').write_text(json.dumps(lock,indent=2,sort_keys=True)+'\n')
    print('PR71 BASELINE PASS; NEW EXACT PARAMETER CANDIDATE',kappa,'bit',ab,'gain',kappa-old,
          'cutoff',result['eventual_bounds']['common_cutoff'],flush=True)


if __name__=='__main__':
    main()
