#!/usr/bin/env python3
"""General stopped-depth lemma and hypothetical target parameters."""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import json

from certify import require,verify_sources
from general_network_guard import guard,strict_integer_power,limiting_ceiling,hypothetical_parameters
from experiments.subset_core_family import complex_count_screen
from prepare_layers import serializable

ROOT=Path(__file__).resolve().parents[1]


def certificate():
    old=json.loads((ROOT/'certificates/complex-compression.json').read_text())
    n=old['counts'];a=old['assembly_control'];p=a['parameters']
    retained=guard(int(n['m']),int(n['s']),int(a['guard_node_charge']),Q(p['beta']),Q(1,1000),Q(5))
    require(retained['C0']==int(a['guard_C0']) and retained['C1']==Q(a['guard_C1']),
            'Retained guard constants changed')
    target=hypothetical_parameters(Q(16,10**8),Q(32,10**8),Q(7),Q(1,2))
    weak=hypothetical_parameters(Q(16,10**8),Q(16,10**8),Q(7),Q(1,100))
    require(target['parameter_system_passes'] and not weak['parameter_system_passes'],
            'Unexpected hypothetical target result')
    sizes=[]
    for h in (22,24,26,28,30):
        for side in (None,0):
            c=complex_count_screen(h,4,side)
            sizes.append(dict(h=h,side_model='raw' if side is None else 'free hypothetical',
                m=c['m'],s=c['s'],strict_integer_residual_exponent=strict_integer_power(c['m'],c['s']),
                complete_complex_frame_certificate=False,scalar_node_charge_verified=False))
    ceiling=[dict(alpha=Q(L),**limiting_ceiling(Q(16,10**8),Q(32,10**8),Q(L)))
             for L in (5,6,7,8,9,10,12)]
    sources=('scripts/audit_general_guard.py','scripts/general_network_guard.py',
             'notes/general-network-guard.tex','docs/research/general-network-guard.md',
             'certificates/complex-compression.json','scripts/experiments/subset_core_family.py')
    return dict(status='GENERAL GUARD LEMMA AND HYPOTHETICAL TARGETS; NO NEW KAPPA',
                upstream_commit=verify_sources(),retained_guard_regression=retained,
                hypothetical_target=target,hypothetical_insufficient_headroom=weak,
                necessary_ceiling_examples=ceiling,unproved_complex_family_size_profiles=sizes,
                scope='The depth lemma assumes a verified scalar recurrence. New finite networks and node charges are not supplied by this certificate.',
                source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/general-network-guard.json').write_text(json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS general residual-exponent guard; retained constants identical; hypothetical 2^-25 target only.')
