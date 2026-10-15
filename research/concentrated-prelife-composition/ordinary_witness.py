#!/usr/bin/env python3
"""Supplemental exact finite ordinary-rate arithmetic for a supplied modern ledger.

No supplier, moment-engine or optimizer imports. This is conditional on the
retained stopped-ordinary recursion and inherited interfaces, not an original
runtime acceptance gate or a complete multiplication theorem.
Apache-2.0. Marius-Paul Dumitrean with substantial OpenAI Codex assistance.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys


def main():
    if not __debug__:
        raise RuntimeError('Assertions are required; run without optimized Python.')
    sys.set_int_max_str_digits(0)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ledger', type=Path, required=True)
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError('Use a fresh output file')
    ledger = json.loads(args.ledger.read_bytes())
    spec = json.loads(args.spec.read_bytes())
    row = ledger['rows']['struct_boundary_radix_union']
    a = Q(row['a']['rational'])
    b = Q(ledger['complex_lower_short']['rational'])
    C = Q(ledger['complex_lower_pinned']['rational'])
    s = (a+b)/2
    beta = (b-s)/(2*b)
    seed = Q(384599, 10**10)
    assert 0 < seed < a < s < (1-beta)*b < b < C < Q('0.001733427039589844234749')
    assert s < Q(1, 500)
    # A finite witness for this chosen atom/seed, not an optimal stage count.
    u, n = seed, 0
    while u <= a:
        u = s*(1-s)+s*u
        n += 1
        assert n < 100, 'This bounded supplement is for the24-digit candidate'
    assert a < u < s and s-u == s**n*(s-seed)
    md = spec['outer_refinement']['margin_digits']
    legacy_s = min(Q('0.001733427039589844234749'), (1-Q(1, 10**md))*C)-Q(1, 1000*10**md)
    assert legacy_s < a
    result = {
        'status': 'PASS_SUPPLEMENTAL_ACTUAL_CANDIDATE_MODERN_ORDINARY_TARGET',
        'source_heads': {'2679':'2e2cf56521df8a2b816b2689144765ee00b69a24',
                         '2696':'5a42add713e09a8798a84d0be7a8276626d9e785'},
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'source_ledger_sha256': hashlib.sha256(args.ledger.read_bytes()).hexdigest(),
        'source_spec_sha256': hashlib.sha256(args.spec.read_bytes()).hexdigest(),
        'exact_modern_kappa': row['kappa']['rational'],
        'actual_modern_a': str(a), 'actual_coarse_b': str(b), 'actual_complex_C': str(C),
        'chosen_atom_s': str(s), 'chosen_beta': str(beta), 'seed': str(seed),
        'sufficient_stage_count': n, 'minimum_or_optimal_stage_count_claimed': False,
        'exact_recurrence': 'u0=384599/10^10; uj=s(1-s)+s*u(j-1)',
        'closed_form_verified_exactly': 's-uN=s^N*(s-u0)',
        'final_gap_u_minus_a': str(u-a),
        'all_four_gaps_proof': 'For every j>=1, seed<uj<s<1/500. Atom=s-uj>0; borrowing=1-uj-s>1-2s>0; remainder=1-uj-s*(1-u(j-1))>borrowing>0; stock=1-s>0.',
        'cutoff_recipe': 'At each finite stage choose ell_j dominating every carried/fresh finite implementation constant. Choose a finite power-of-two L_j with L_j*delta_j^2>=36 and L_j*delta_j>=2*(4+ell_j); carry the previous finite constant forward. No fixed numerical bound on hidden constants is assumed.',
        'original_legacy_bootstrap_steps': spec['outer_refinement']['bootstrap_steps'],
        'legacy_atom_below_actual_modern_a': True,
        'inherited_conditions': [
            'Completed stopped-ordinary recursion and uniform finite carried implementation constants.',
            'All-size machine/compiler/common-label realization.',
            'Physical sequential complete-call borrowing, cleanup, hosting and routing.',
            'Uniform precision/fixed tape/exact recovery and analytic transfer.',
            'Retained native recurrence corrections, cited PR589 bit-supplier hypotheses and modern outer assumptions.'
        ],
        'scope': 'Additive finite arithmetic witness. It does not relabel the historical12-stage bootstrap as a modern-target witness, add a gate to the original replay, or prove an unconditional multiplication theorem.'
    }
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], n)


if __name__ == '__main__':
    main()
