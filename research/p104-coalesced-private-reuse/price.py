#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Price the actual composed word, retaining the predecessor's coverage model.

Adapted from David Arias's PR2152 coalesced_budget.py. Exact interval arithmetic
is the credited retained ceiling engine, not an independent numerical method.
"""
from collections import Counter
from fractions import Fraction as Q


def integers(profile):
    return {int(k): v for k, v in profile.items()}


def bind(C, built, base, hosted):
    F, D = C.F, C.D
    report = built['report']
    public = Counter(e['rank'] for e in built['transport_edges'] if not e['private'])
    private = Counter(e['rank'] for e in built['transport_edges'] if e['private'])
    D.require(public == integers(report['candidate_public_profile']), 'public invoice occurrence binding')
    D.require(private == integers(report['private_COPY_profile']), 'private invoice occurrence binding')
    D.require(D.profile(public + private) == report['combined_profile'], 'combined invoice binding')
    D.require(sum(r*c for r, c in public.items()) == sum(report['complete_public_widths']) == 5838,
              'complete public mass binding')
    D.require(sum(r*c for r, c in private.items()) == 56, 'complete private mass binding')
    D.require(report['complete_public_widths'] == base['report']['complete_public_widths']
              and built['initial'] == base['initial'] and built['final'] == base['final'],
              'source boundary width contract')
    D.require(F.digest(built['scalar_operations']) == report['scalar_operation_word_sha256']
              and F.digest(built['transport_edges']) == report['transport_occurrences_sha256'],
              'priced word binding')
    D.require(hosted['complete_public_widths_sha256'] == F.digest(report['complete_public_widths']),
              'owner invoice width binding')
    D.require(hosted['assigned_roles'] == 144 * 527 and hosted['total_calls'] == 144,
              'owner role coverage')
    D.require(not hosted['global_emitter_admitted'], 'conditional owner invoice is not global admission')
    return public + private


def verify(C, B, built, base, hosted):
    profile = bind(C, built, base, hosted)
    baseline = Counter(integers(base['report']['candidate_public_profile']))
    baseline.update(integers(base['report']['private_COPY_profile']))
    delta = {r: profile[r] - baseline[r] for r in set(profile) | set(baseline)
             if profile[r] != baseline[r]}
    B.require(delta == {2: -1, 7: -1, 9: 1}, 'complete combined profile delta')
    engine, _, _, _ = B.load_inputs()
    width = Q(B.FAMILIES, B.STAGES)
    total = (B.M - 1) * width + B.CENTRE
    B.require(total == 6712 and B.mass(profile) == B.mass(baseline) == 5894,
              'complete unchanged coverage model')
    idle_global = integers(hosted['remaining_idle_profile'])
    idle = {r: Q(n, 144) for r, n in idle_global.items()}
    B.require(B.mass(idle) == 818 and all(0 < r <= 51 and n > 0 for r, n in idle.items()),
              'complete actual owner idle invoice')
    selected_a = B.SELECTED_KAPPA / (1 - B.SELECTED_KAPPA)
    target = B.SELECTED_KAPPA * Q(101, 100)
    target_a = target / (1 - target)

    def scenario(name, local, actual_idle):
        effective = Counter(local)
        if actual_idle:
            effective.update(idle)
        model = engine.model(effective, B.M, B.FAMILIES, B.STAGES, B.CENTRE)
        B.require(model['local_mass'] + model['idle_mass'] == total, 'complete paid mass')
        B.require(model['idle_mass'] == (0 if actual_idle else 818), 'unpriced idle mass')
        zero = engine.relax(effective, B.M, B.FAMILIES, B.STAGES, B.CENTRE, Q(0))
        B.require(zero[0] <= total / (B.M * width) <= zero[1], 'zero-saving coverage identity')
        root = engine.ceiling(effective, B.M, B.FAMILIES, B.STAGES, B.CENTRE)
        B.require(engine.relax(effective, B.M, B.FAMILIES, B.STAGES, B.CENTRE, root[0])[1] < 1
                  and engine.relax(effective, B.M, B.FAMILIES, B.STAGES, B.CENTRE, root[1])[0] > 1,
                  'root bracket is not certified')
        selected = engine.relax(effective, B.M, B.FAMILIES, B.STAGES, B.CENTRE, selected_a)
        target_moment = engine.relax(effective, B.M, B.FAMILIES, B.STAGES, B.CENTRE, target_a)
        B.require(target_moment[0] > 1, 'one-percent rejection changed')
        cap = min(root[1] / (1 + root[1]), B.BIT_LOWER / (1 + B.BIT_LOWER))
        return dict(name=name,
                    idle_invoice='conditional_selected_window' if actual_idle else 'fractional_rank51_relaxation',
                    local_profile=B.profile_json(local), local_mass=B.mass(local), idle_mass='818',
                    complete_paid_mass=str(total), model={k: str(v) for k, v in model.items()},
                    complex_saving_root_interval=B.interval(root),
                    fixed_bit_capped_kappa_upper_bound=str(cap), kappa_upper_bound_decimal=B.decimal(cap),
                    relative_gain_upper_percent_decimal=B.decimal(100 * (cap / B.SELECTED_KAPPA - 1)),
                    moment_at_selected_kappa=B.interval(selected), selected_kappa_excluded=selected[0] > 1,
                    moment_at_one_percent_target=B.interval(target_moment), one_percent_target_excluded=True)

    pairs = []
    for actual_idle in (False, True):
        before = scenario('coalesced_baseline', baseline, actual_idle)
        after = scenario('boundary_preserving_private_reuse', profile, actual_idle)
        B.require(Q(after['moment_at_selected_kappa']['upper']) <
                  Q(before['moment_at_selected_kappa']['lower']), 'strict moment improvement')
        B.require(Q(before['complex_saving_root_interval']['upper']) <
                  Q(after['complex_saving_root_interval']['lower']), 'strict root improvement')
        B.require(after['selected_kappa_excluded'] == actual_idle, 'screen versus actual owner outcome')
        pairs.append(dict(baseline=before, composed=after, strict_improvement_certified=True))
    return dict(status='PASS_STRICT_FINITE_PROFILE_IMPROVEMENT_WITH_HOSTED_THRESHOLD_REJECTION',
                selected_kappa=str(B.SELECTED_KAPPA), one_percent_target_kappa=str(target),
                combined_profile_delta={str(k): v for k, v in sorted(delta.items())},
                hypothetical_extra_gather_credit_used=False,
                source_scalar_operations_sha256=built['report']['source_scalar_operations_sha256'],
                priced_scalar_operations_sha256=built['report']['scalar_operation_word_sha256'],
                priced_transport_occurrences_sha256=built['report']['transport_occurrences_sha256'],
                owner_widths_sha256=hosted['actual_ordinary_widths_sha256'],
                owner_assignment_sha256=hosted['assignment_sha256'],
                global_remaining_idle_profile=hosted['remaining_idle_profile'],
                global_idle_mass=B.mass(idle_global), scenarios=pairs,
                global_emitter_admitted=False, new_kappa_gain_certified=False)
