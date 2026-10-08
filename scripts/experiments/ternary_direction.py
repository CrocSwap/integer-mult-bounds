#!/usr/bin/env python3
"""Exact prime-family ceilings and PR7/dependency-guard compatibility.

The prime-family calculation is an optimistic screen, not a construction.
The guard witness retains Zhihao Chen's PR7 exponent unchanged. See NOTICE
and docs/research/ternary-direction.md for provenance and proof scope.
"""
from dataclasses import replace
from fractions import Fraction as Q
from itertools import combinations
from math import comb
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from certify import require
from prepare_layers import serializable
from search_network import log_integer_bounds, log_ratio_bounds
from prime_field_network import parameters, bit_counts, complex_counts, witness
from paired_complex import PairedComplex
from complex_circuit import Checks, compile_roles
from experiments import assembly_breakthrough_guard as dg
from audit_kappa_targets import saving_enclosure

ALIGNED_KAPPA = Q(1624, 10**12)
PR7_KAPPA = Q(373, 10**11)


def prime_case(p, h, output_floor):
    """Retain three stages, common-(p-1) centers and negative sources."""
    require(p in (3, 5, 7), 'Finite screen covers only p=3,5,7')
    require(h >= 2*p, 'Ground set too small')
    k = 2*p-1
    v, centers, multiplicity = comb(h, k), comb(h, p-1), comb(k, p-1)
    deficit = v-6*centers*(h-p+1)
    if deficit <= 0:
        return None
    roles = multiplicity*v+centers if output_floor else 0
    eta = Q(deficit, 2*h**3*(v+roles))
    low, high = log_ratio_bounds(1/(1-eta), terms=4)
    log_low, log_high = log_integer_bounds(h**3)
    return dict(p=p, h=h, vertices=v, centers=centers,
                center_dimension=h-p+1, output_multiplicity=multiplicity,
                role_floor=roles, eta=eta,
                bit_saving_lower=low/log_high, bit_saving_upper=high/log_low)


def prime_family(p, output_floor, cutoff=200):
    require(cutoff >= 200, 'The tail proof is certified from h=200')
    cases = [row for h in range(2*p, cutoff)
             if (row := prime_case(p, h, output_floor)) is not None]
    best = max(cases, key=lambda row: row['bit_saving_lower'])
    require(all(best['bit_saving_lower'] > row['bit_saving_upper']
                for row in cases if row['h'] != best['h']),
            'Optimistic maximizer not separated')
    factor = 1+comb(2*p-1, p-1) if output_floor else 1
    tail = 1/((2*cutoff**3*factor-1)*log_integer_bounds(cutoff**3)[0])
    require(tail < best['bit_saving_lower'], 'Infinite tail not excluded')
    ceiling = best['bit_saving_upper']/2
    return best | dict(output_floor=output_floor, positive_finite_cases=len(cases),
                       tail_h=cutoff, tail_bit_saving_upper=tail,
                       kappa_upper=ceiling,
                       factor_over_aligned_upper=ceiling/ALIGNED_KAPPA,
                       factor_over_pr7_upper=ceiling/PR7_KAPPA)


def larger_prime_output_tail():
    # For p>=11, h>=2p and b=C(2p-1,p-1) both increase with p.
    # Discard all center losses and use eta<1/[2 h^3(1+b)].
    h, b = 22, comb(21, 10)
    upper = 1/(2*(2*h**3*(1+b)-1)*log_integer_bounds(h**3)[0])
    require(upper < PR7_KAPPA, 'Large-prime screen changed')
    return dict(first_prime=11, minimum_h=h, minimum_output_multiplicity=b,
                kappa_strict_upper=upper,
                scope='Only the retained separate-output compiler; no free-scratch claim.')


def fixed_h28_role_targets():
    """Necessary total role budgets for the retained h28 loss and assembly."""
    h, v = 28, comb(28, 5)
    deficit = v-6*comb(h, 2)*(h-2)

    def enclosure(roles):
        eta = Q(deficit, 2*h**3*(v+roles))
        return tuple(value/2 for value in saving_enclosure(eta, h**3))

    result = {}
    for factor in (10, 100, 1000):
        target = factor*ALIGNED_KAPPA
        if enclosure(0)[1] < target:
            result[str(factor)] = dict(target=target, impossible_even_with_free_roles=True)
            continue
        low, high = 0, 10**9
        require(enclosure(high)[1] < target, 'Role search bracket too small')
        while high-low > 1:
            mid = (low+high)//2
            if enclosure(mid)[1] > target:
                low = mid
            else:
                high = mid
        require(enclosure(low)[0] > target, 'Boundary needs tighter logarithm intervals')
        result[str(factor)] = dict(target=target, necessary_roles_at_most=low,
                                  first_excluded_roles=high,
                                  necessary_additions_at_most_with_direct_outputs=low-v-comb(h, 2))
    return dict(h=h, targets=result,
                scope='Necessary only, at fixed h28 with unchanged center loss, bank sharing '
                      'and kappa<a_b/2. Passing this screen is not a circuit or exponent witness.')


def paired_guard_control(h=28):
    c = PairedComplex(h)
    checks, code = Checks(c), compile_roles(c)
    dimensions = {node: checks.label(node).dim for node in c.active}
    invocations = [dg.invocation(c, code, dimensions, stage, inverse)
                   for stage, inverse in ((1, False), (2, True), (3, False))]
    triples = list(combinations(range(h), 3))
    require(h % 2 == 0, 'Partner involution requires even h')
    images = [tuple(sorted(i ^ 1 for i in t)) for t in triples]
    require(len(set(images)) == len(triples), 'Bank matching is not a permutation')
    require(all(len(set(t) & set(u)) % 2 == 0 for t, u in zip(triples, images)),
            'Bank join is not orthogonal over F2')
    require(h <= h**3-h, 'Stage-1 to stage-3 join decreases dimension')
    return dict(h=h, invocations=invocations,
                shared_bank_join=dict(permutation_size=len(triples),
                                      source_dimension=h, target_dimension=h**3-h,
                                      all_binary_inner_products_zero=True,
                                      chronological_stage_pair=[1, 3]),
                three_stage_path_descent_upper=3*h,
                three_stage_path_rank_upper=h**3+6*h)


def combined_witness():
    original = witness()
    beta = Q(1, 1000)
    p = replace(parameters(), beta=beta, C1=beta+(1-beta)*dg.RHO+dg.ZETA)
    n = complex_counts()
    result = dg.research_witness(n=n, parameters=p)
    # Verify exponent support, independently of the assembly-only helper.
    bn = bit_counts()
    require(bn['eta'] > (1-p.tau)*original['log_upper']['bit'], 'Bit saving unsupported')
    require(n['eta'] > (1-p.sigma)*original['log_upper']['complex'], 'Complex saving unsupported')
    result.update(status='SAME PR7 KAPPA WITH DEPENDENCY-PATH GUARD',
                  bit=bn, complex=n,
                  scope='PR7 construction plus the written dependency-path guard; no new exponent.',
                  complex_leaf_saving=(1-beta)*(1-p.sigma),
                  leaf_saving_over_current_bit=(1-beta)*(1-p.sigma)/(1-p.tau))
    return result


def certificate():
    rows = [prime_family(p, outputs) for p in (3, 5, 7) for outputs in (False, True)]
    require(max(row['kappa_upper'] for row in rows if row['output_floor'])
            < 12*PR7_KAPPA, 'Separate-output screen changed')
    return dict(status='RESEARCH DIRECTION; NO NEW MULTIPLICATION EXPONENT',
                pr7=dict(url='https://github.com/CrocSwap/integer-mult-bounds/pull/7',
                         head='6725c6a17b17871a35353fd29157f4ed851bc114',
                         author='Zhihao Chen (jacklightChen)', kappa=PR7_KAPPA),
                prime_family_ceilings=rows,
                larger_prime_output_tail=larger_prime_output_tail(),
                fixed_h28_role_targets=fixed_h28_role_targets(),
                paired_complex_guard=paired_guard_control(),
                unchanged_pr7_witness_with_new_guard=combined_witness(),
                distinction='Optimistic ceilings discard real circuit costs; finite controls '
                            'and exact assembly do not replace the general written proofs.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=ROOT/'certificates/ternary-direction.json')
    args = parser.parse_args()
    args.output.write_text(json.dumps(serializable(certificate()), indent=2, sort_keys=True)+'\n')
    print('PASS prime-family screens and PR7/dependency-guard composition; unchanged kappa', PR7_KAPPA)
