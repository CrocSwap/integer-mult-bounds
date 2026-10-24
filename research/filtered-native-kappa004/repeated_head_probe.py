#!/usr/bin/env python3
"""Bind PR5270's literal main-path operators to their actual axis usage.

The emitted replay uses the same nine axes at every stage, whereas its invoice
credits independent fresh eight-axis blocks. A gauge-equivalence replay does
not certify that missing target binding. Apache-2.0; OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256
from types import SimpleNamespace
import json

from snapshot_probe import load, need

HERE = Path(__file__).resolve().parent
SOURCE_COMMIT = 'df9e5037587ce0cfbd23c2a944515526b301e820'


def trace(module, p):
    calls = []

    def gaussian(bank, axes, inverse=False):
        calls.append({'kind': 'gaussian', 'axes': list(axes), 'power': -1 if inverse else 1})
        return bank

    def gaussian_power(bank, axes, power=1):
        calls.append({'kind': 'power', 'axes': list(axes), 'power': power})
        return bank

    # Empty payloads trace the actual replay's operator dispatch without
    # replacing its listing, branches, IDLE powers, or stage chronology.
    module.gaussian_power = gaussian_power
    L = SimpleNamespace(gaussian=gaussian, add=lambda a, b, s=1: a)
    gates = module.listing(p)
    _, rec = module.replay(p, gates, [[] for _ in range(2*p)], L,
                           lambda x: x, lambda x: x)
    active = sorted(set(x for c in calls for x in c['axes']))
    need(active == list(range(9)), 'Every stage reuses the same nine coordinates')
    middle = [g for g in gates if g[0] == 'IDLE' and g[-1] == 'middle']
    need(len(middle) == p-1 and all(g[3] == 1 for g in middle), 'Literal middle R jobs')
    T, P = module.invoice(p, module.pattern_of(p), frozenset(range(1, 2*p, 2)), module.P_NEW)
    need(max(T) == 1+8*p, 'Advertised fresh-stage target')
    # Even granting the unproved R upgrade, finite owner mixing cannot make
    # a matrix block use more address bits than the whole literal alphabet.
    # Price a direct R upgrade separately: D -> DQ on both banks per FULL.
    target_upper = Counter({r: p*n for r, n in module.H.items()})
    target_upper[9] += 2*p*112
    paid_lower = Counter({r: p*n for r, n in module.P_NEW.items()})
    paid_lower[1] += 112*(p+1)+224*p
    surplus_upper = sum(r*n for r, n in target_upper.items())-sum(r*n for r, n in paid_lower.items())
    need(surplus_upper < 0, 'Direct R-upgrade relaxation fails already at exponent zero')
    return {'pairs': p, 'literal_gate_records': len(gates), 'recodings': rec,
            'gaussian_axis_support': active, 'maximum_literal_active_rank': 9,
            'advertised_maximum_target_rank': max(T),
            'literal_middle_idle_field_jobs': 224*len(middle), 'literal_middle_idle_rank': 9,
            'invoice_middle_idle_field_jobs': 0,
            'direct_D_to_R_upgrade_rank_one_jobs': 224*p,
            'optimistic_surplus_after_direct_upgrade_ignoring_all_idles': surplus_upper,
            'axis_trace': calls}


def main():
    path = HERE/'inputs/pr5270_p19_word.py'
    m = load('k004_p19_literal', path)
    out = {'status': 'REJECT_REPEATED_HEAD_AS_FRESH_STAGE_SUPPLIER',
           'source_commit': SOURCE_COMMIT, 'source_pr': 5270,
           'source_sha256': sha256(path.read_bytes()).hexdigest(),
           'cases': [trace(m, p) for p in (2, 19)],
           'scope': 'The literal main-path listing at this pinned head, its axis dispatch and its mismatch with the advertised invoice. This does not refute a different fresh-stage construction or all coded reverse callers.',
           'support_argument': 'At column width f every literal Q, R and K acts on the same nine f-bit coordinate blocks. Each original-to-output matrix block has row support at most 2^(9f). A rank-r Gaussian has row support 2^(rf). Fixed finite ordinary owner mixing and monomial boundary recodings cannot bridge this gap for r>9 at all widths.',
           'gauge_replay_limit': 'Equality to a reference word using the same reused R proves gauge equivalence only. It does not prove independent-stage target ranks or that a native D call supplies an R letter.',
           'direct_upgrade_limit': 'The 224 H1 per native call is the explicit post-Q-on-both-banks recipe, not a lower bound against every redesigned implementation.',
           'new_kappa_claimed': False}
    (HERE/'evidence/repeated-head-probe.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({'status': out['status'], 'cases': [{k: v for k, v in r.items() if k != 'axis_trace'} for r in out['cases']]}))


if __name__ == '__main__':
    main()
