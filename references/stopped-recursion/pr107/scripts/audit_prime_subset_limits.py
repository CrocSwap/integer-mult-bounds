#!/usr/bin/env python3
from hashlib import sha256
from pathlib import Path
import json
from certify import verify_sources
from prepare_layers import serializable
from experiments.prime_subset_limits import local_identity,partial_output_control,screen
ROOT=Path(__file__).resolve().parents[1]


def certificate():
    source=('scripts/audit_prime_subset_limits.py','scripts/experiments/prime_subset_limits.py',
            'scripts/experiments/core_limits.py','scripts/search_network.py',
            'docs/research/prime-subset-limits.md')
    return dict(status='SCOPED PRIME-POWER FAMILY CEILING; NO NEW KAPPA',
        upstream_commit=verify_sources(),
        local_controls=[local_identity(q,True) for q in (2,3)],
        distinct_output_controls=[partial_output_control(2,6),partial_output_control(3,9)],
        envelope=screen(),source_sha256={s:sha256((ROOT/s).read_bytes()).hexdigest() for s in source})

if __name__=='__main__':
    out=certificate()
    (ROOT/'certificates/prime-subset-limits.json').write_text(json.dumps(serializable(out),indent=2,sort_keys=True)+'\n')
    b=out['envelope']['best_finite_upper']
    print('PASS common-subset prime-power family cannot reach 2^-26; best finite optimistic ceiling',b['q'],b['h'],float(b['kappa_upper']))
