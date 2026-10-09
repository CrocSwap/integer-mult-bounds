#!/usr/bin/env python3
"""Bounded forward-expansion search; rejected on exact scalar role counts."""
from hashlib import sha256
from pathlib import Path
import gc
import json

from audit_mixed_point import scalar_check, optimistic_score
from certify import require, verify_sources
from experiments.mixed_point_circuit import build, factored_transpose
from experiments.early_sharing import refactor
from prepare_layers import serializable

ROOT = Path(__file__).resolve().parents[1]


def certificate():
    small = []
    for h in (10,12,20):
        c = build(h,3,3,1)
        for _ in range(2):
            c,_ = factored_transpose(c)
        baseline = scalar_check(c)
        trials = []
        for depth,fanout in ((2,2),(3,2),(3,4)):
            candidate,stats = refactor(c,depth,fanout)
            record = scalar_check(candidate)
            require(record['roles'] >= baseline['roles'], 'Improved candidate needs frame review')
            trials.append(dict(search=stats,scalar=record))
        small.append(dict(baseline=baseline,trials=trials))
    c = build(50,3,3,1)
    build.cache_clear()
    for _ in range(4):
        c,_ = factored_transpose(c)
        gc.collect()
    baseline = scalar_check(c)
    candidate,stats = refactor(c,2,2)
    record = scalar_check(candidate)
    require(baseline['roles'] == 447488 and record['roles'] == 510700,
            'Bounded early-sharing result changed')
    proofs = ['scripts/experiments/early_sharing.py','docs/research/early-sharing-and-centers.md']
    return dict(status='EARLY-SHARING COUNT SCREEN; NO NEW KAPPA',
                upstream_commit=verify_sources(),small_trials=small,
                full_size=dict(baseline=baseline,search=stats,scalar=record,
                               optimistic_score=optimistic_score(50,record['roles'])),
                source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in proofs},
                new_frame_certificates_supplied=False,
                decision='Stop this expansion/pair-refactoring heuristic: all nine small trials and the full-size trial increase roles. This is not an impossibility result for earlier sharing.')


if __name__ == '__main__':
    result = certificate()
    (ROOT/'certificates/early-sharing-audit.json').write_text(
        json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS early-sharing screen: 447488 -> 510700 scalar roles; candidate rejected.')
