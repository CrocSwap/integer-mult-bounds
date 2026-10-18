#!/usr/bin/env python3
"""Independent closed-form and dirty-register checks for one center shear.

Copyright 2026 Curtis Dransfield. Apache-2.0.
Prepared with substantial OpenAI Codex assistance. Original dyadic central
factor and transparent schedule: Douglas R. Colkitt, with retained Codex
assistance disclosure. This module imports no repository implementation.

Only the central commutator is checked here; this is not a full scalar
network, frame, recursive-interface, or multiplication-exponent certificate.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from math import comb


def require(condition, message):
    if not condition:
        raise ValueError(message)


def factor_entries(h, changed=False):
    """Own dense formulas; h<8 is used only for small algebra controls.

    U_rows[S] is a scatter numerator row. V_columns[T] is a gather column.
    The changed entries are V[1,T]=t1-t2 and U[S,2]=s1+s2-2s0.
    """
    require(type(h) is int and h >= 3, 'Use integer h >= 3')
    triples = tuple(combinations(range(h), 3))
    gather, scatter = [], []
    for triple in triples:
        indicator = tuple(int(i in triple) for i in range(h))
        s0, s1, s2 = indicator[:3]
        v = [1, s1-s2 if changed else s1-1, s2-1] + list(indicator[3:])
        u = [s0+s1+s2-1, s1-s0,
             s1+s2-2*s0 if changed else s2-s0]
        u += [x-s0 for x in indicator[3:]]
        gather.append(tuple(v))
        scatter.append(tuple(u))
    return dict(h=h, triples=triples, U_rows=tuple(scatter), V_columns=tuple(gather))


def weighted_cost(factor):
    gather = sum(x != 0 for column in factor['V_columns'] for x in column)
    scatter = sum(1 if abs(x) == 2 else 2 for row in factor['U_rows'] for x in row if x)
    return dict(gather=gather, scatter=scatter, total=gather+scatter)


def closed_cost_formula(h):
    def choose(n, k):
        return comb(n, k) if n >= k >= 0 else 0
    n = comb(h, 3)
    old_gather = n + 2*choose(h-1, 3) + (h-3)*choose(h-1, 2)
    old_scatter = 2*choose(h-3, 3) + 6*(h-3) + 1 + 4*(h-1)*choose(h-2, 2)
    gather_change = 2*choose(h-2, 2) - choose(h-1, 3)
    scatter_change = choose(h-2, 2)
    numerator = (h-10)*(h-2)*(h-3)
    require(numerator % 6 == 0, 'Nonintegral closed saving')
    saving = numerator // 6
    require(saving == -(gather_change + scatter_change), 'Saving formulas disagree')
    return dict(h=h, original_gather=old_gather, original_scatter=old_scatter,
                changed_gather=old_gather+gather_change,
                changed_scatter=old_scatter+scatter_change,
                gather_change=gather_change, scatter_change=scatter_change,
                saving_gather_plus_scatter=saving,
                complete_three_stage_scalar_bound_saving=6*n*n*saving)


def orbit_census(h=26):
    """Check 16 coordinate-type/sign orbits instead of individual moves.

    The stabilizer of coordinate zero and the base triple permutes B={1,2}
    and C={3,...,h-1}. Simultaneously permuting triples and these coordinates
    preserves every factor entry and charge. Distinct ordered indices have
    eight type pairs (AA is impossible), each with two signs.
    """
    require(type(h) is int and h >= 8 and h % 2 == 0, 'Use even h >= 8')
    factor = factor_entries(h)
    classes = {'A': (0,), 'B': (1, 2), 'C': tuple(range(3, h))}
    records = []
    histogram = Counter()
    admissible = total = 0
    for i_type, i_members in classes.items():
        for j_type, j_members in classes.items():
            if i_type == j_type and len(i_members) == 1:
                continue
            i = i_members[0]
            j = j_members[1] if i_type == j_type else j_members[0]
            multiplicity = len(i_members)*(len(j_members)-int(i_type == j_type))
            original_v = tuple(column[i] for column in factor['V_columns'])
            other_v = tuple(column[j] for column in factor['V_columns'])
            original_u = tuple(row[j] for row in factor['U_rows'])
            other_u = tuple(row[i] for row in factor['U_rows'])
            for sign in (-1, 1):
                changed_v = tuple(a + sign*b for a, b in zip(original_v, other_v))
                changed_u = tuple(a - sign*b for a, b in zip(original_u, other_u))
                gather_ok = all(x in (-1, 0, 1) for x in changed_v)
                scatter_ok = all(x in (-2, -1, 0, 1, 2) for x in changed_u)
                result = dict(i_type=i_type, j_type=j_type, sign=sign,
                              representative=[i, j, sign], multiplicity=multiplicity,
                              gather_admissible=gather_ok, scatter_admissible=scatter_ok)
                total += multiplicity
                if gather_ok and scatter_ok:
                    # Independent literal prices; only the affected row and
                    # column enter the difference because every other entry
                    # is identical under an elementary shear.
                    prices = {0: 0, -1: 2, 1: 2, -2: 1, 2: 1}
                    delta_g = sum(x != 0 for x in changed_v) - sum(x != 0 for x in original_v)
                    delta_h = sum(prices[x] for x in changed_u) - sum(prices[x] for x in original_u)
                    result.update(delta_G=delta_g, delta_H=delta_h, delta=delta_g+delta_h)
                    histogram[delta_g+delta_h] += multiplicity
                    admissible += multiplicity
                records.append(result)
    require(len(records) == 16 and total == 2*h*(h-1), 'Incomplete coordinate-type orbit cover')
    minimum = min(histogram)
    return dict(h=h, orbits=len(records), candidate_moves=total,
                admissible_moves=admissible, rejected_moves=total-admissible,
                delta_histogram={str(delta): count for delta, count in sorted(histogram.items())},
                minimum_delta=minimum,
                minimizing_move_categories=[row for row in records if row.get('delta') == minimum],
                orbit_records=records,
                method='Dense closed factor entries; 16 coordinate-type/sign representatives with exact orbit multiplicities',
                symmetry='Fix coordinate0; permute {1,2} and {3,...,h-1}, simultaneously permuting triple labels',
                stopping_rule='All eight ordered coordinate-type pairs times both signs; AA excluded')


def coefficient_check(h=26):
    """Check every coefficient by contracting the unchanged tail in closed form.

    The tail dot product is |S_tail intersect T_tail|-s0*|T_tail|.
    This avoids both sparse-factor multiplication and imported producer code.
    """
    triples = tuple(combinations(range(h), 3))
    masks = [sum(1 << i for i in triple) for triple in triples]
    source_features = []
    target_features = []
    for mask in masks:
        a, b, c = (mask >> i & 1 for i in range(3))
        source_features.append((mask, mask & ~7, a, a+b+c-1, b-a, c-a, b+c-2*a))
        target_features.append((mask, mask & ~7, b-1, c-1, b-c, 3-a-b-c))
    histogram = [0, 0, 0, 0]
    digest = sha256()
    checked = 0
    for source_mask, source_tail, s0, u0, u1, old_u2, new_u2 in source_features:
        row = bytearray()
        for target_mask, target_tail, old_v1, v2, new_v1, tail_size in target_features:
            common_tail = (source_tail & target_tail).bit_count() - s0*tail_size
            old_value = u0 + u1*old_v1 + old_u2*v2 + common_tail
            new_value = u0 + u1*new_v1 + new_u2*v2 + common_tail
            expected = (source_mask & target_mask).bit_count() - 1
            if old_value != expected or new_value != expected:
                raise ValueError('Closed coefficient mismatch for masks ' +
                                 str((source_mask, target_mask)))
            histogram[expected+1] += 1
            row.append(new_value+1)
            checked += 1
        digest.update(row)
    require(checked == len(triples)**2, 'Incomplete coefficient coverage')
    return dict(h=h, triples=len(triples), coefficients_checked=checked,
                coefficient_histogram={str(i-1): count for i, count in enumerate(histogram)},
                coefficient_sha256=digest.hexdigest(),
                digest_encoding='Row-major lexicographic triples; one byte per coefficient plus one',
                method='Two closed-form head contractions and exact tail-intersection cardinality')


def _central_run(factor, x, doubled_y, center, inverse=False, omit_step=None):
    """Simulate integer coordinates (x,2y,c), so scatter uses U, not U/2."""
    x, doubled_y, center = list(x), list(doubled_y), list(center)
    operations = (('scatter', -1), ('gather', 1), ('scatter', 1), ('gather', -1))
    if inverse:
        operations = tuple((name, -sign) for name, sign in reversed(operations))
    for step, (name, sign) in enumerate(operations):
        if step == omit_step:
            continue
        if name == 'gather':
            for coefficient, column in zip(x, factor['V_columns']):
                if coefficient:
                    for i, value in enumerate(column):
                        center[i] += sign*coefficient*value
        else:
            for i, row in enumerate(factor['U_rows']):
                doubled_y[i] += sign*sum(a*b for a, b in zip(row, center))
    return x, doubled_y, center


def dirty_basis_check(h):
    factor = factor_entries(h, changed=True)
    n = len(factor['triples'])
    masks = [sum(1 << i for i in triple) for triple in factor['triples']]
    checked = 0
    for inverse in (False, True):
        for basis in range(2*n+h):
            x, y2, center = [0]*n, [0]*n, [0]*h
            if basis < n:
                x[basis] = 1
            elif basis < 2*n:
                y2[basis-n] = 2
            else:
                center[basis-2*n] = 1
            expected_y2 = list(y2)
            if basis < n:
                for i, mask in enumerate(masks):
                    expected_y2[i] += (-1 if inverse else 1)*((mask & masks[basis]).bit_count()-1)
            actual = _central_run(factor, x, y2, center, inverse)
            require(actual == (x, expected_y2, center), 'Dirty central basis state failed')
            checked += 1
    return dict(h=h, triples=n, basis_inputs=2*n+h, orientations=2,
                invocations_checked=checked, all_dirty_center_inputs_restored=True,
                x_unchanged=True, arbitrary_y_preserved=True,
                coordinates='Exact integer representation (x,2y,c); linearity extends to rational inputs')


def mutation_controls():
    old, changed = factor_entries(6), factor_entries(6, changed=True)
    n = len(changed['triples'])
    x, y2, center = [0]*n, [0]*n, [0]*6
    x[0] = 1
    omitted_restore = _central_run(changed, x, y2, center, omit_step=3)
    require(omitted_restore[2] != center, 'Missing restore mutation went undetected')
    x = [0]*n
    center[0] = 1
    omitted_dirty_cancel = _central_run(changed, x, y2, center, omit_step=0)
    require(omitted_dirty_cancel[1] != y2, 'Missing dirty cancellation went undetected')

    def first_mismatch(rows, columns):
        for i, row in enumerate(rows):
            for j, column in enumerate(columns):
                actual = sum(a*b for a, b in zip(row, column))
                expected = len(set(changed['triples'][i]) & set(changed['triples'][j]))-1
                if actual != expected:
                    return dict(S=changed['triples'][i], T=changed['triples'][j],
                                actual_numerator=actual, expected_numerator=expected)
        raise ValueError('Factor mutation went undetected')

    gather_only = first_mismatch(old['U_rows'], changed['V_columns'])
    wrong_rows = [list(row) for row in changed['U_rows']]
    mutated_row = next(i for i, row in enumerate(wrong_rows) if row[2] == -2)
    wrong_rows[mutated_row][2] = 2
    wrong_sign = first_mismatch(wrong_rows, changed['V_columns'])
    return dict(omitted_inverse_gather_rejected=True,
                omitted_initial_dirty_scatter_rejected=True,
                gather_changed_without_inverse_scatter_change=gather_only,
                negative_two_numerator_flipped_positive=wrong_sign)


def independent_check():
    old, changed = factor_entries(26), factor_entries(26, changed=True)
    before, after = weighted_cost(old), weighted_cost(changed)
    closed = closed_cost_formula(26)
    require(before == dict(gather=14100, scatter=31281, total=45381), 'Original cost changed')
    require(after == dict(gather=12352, scatter=31557, total=43909), 'Changed cost changed')
    require(before['total'] - after['total'] == 1472, 'Wrong exact scalar saving')
    require(all(x in (-1, 0, 1) for col in changed['V_columns'] for x in col),
            'Changed gather alphabet failed')
    scatter_alphabet = sorted({x for row in changed['U_rows'] for x in row})
    require(scatter_alphabet == [-2, -1, 0, 1, 2], 'Changed scatter alphabet failed')
    formula_cases = []
    for h in (4, 6, 8, 10, 12, 14, 20, 26, 30):
        original, altered = weighted_cost(factor_entries(h)), weighted_cost(factor_entries(h, True))
        formula = closed_cost_formula(h)
        require(original['gather'] == formula['original_gather'] and
                original['scatter'] == formula['original_scatter'] and
                altered['gather'] == formula['changed_gather'] and
                altered['scatter'] == formula['changed_scatter'], 'Closed cost formula mismatch')
        formula_cases.append(formula)
    return dict(
        status='PASS_INDEPENDENT_DYADIC_CENTER_SHEAR',
        shear=dict(i=1, j=2, sign=-1, changed_gather='V_1 = t_1 - t_2',
                   changed_scatter='U_2 = s_1 + s_2 - 2*s_0'),
        coefficients=coefficient_check(26), orbit_census=orbit_census(26),
        original_cost=before, changed_cost=after,
        closed_saving_at_26=closed, closed_formula_controls=formula_cases,
        changed_scatter_numerator_alphabet=scatter_alphabet,
        dirty_central_controls=[dirty_basis_check(h) for h in (4, 6, 8)],
        negative_controls=mutation_controls(),
        scope='One fixed shear; full coefficient coverage at h=26; central commutator only; '
              'h<8 controls assert algebra only; no new multiplication exponent')


if __name__ == '__main__':
    print(json.dumps(independent_check(), indent=2, sort_keys=True))
