#!/usr/bin/env python3
"""Mathematical faults rejected independently of provenance-hash failures."""
from __future__ import annotations

from copy import deepcopy

from gauss_trace import adjoint, equal, require
from native_check import check_native, frame, gaussian, lowered, monomial
from source_algebra import free_laurent, local_gauge, ownership_and_invoice
from caller_check import AXES, contact, orthogonal_base, phase, positive, route, stage_terms, terms, transformed_path


def lift(n, f, circuit, repeat_constant=True):
    """Small checked test witness, not a replacement for the universal proof."""
    dimension = n*f
    out = []
    for column in range(f):
        offset = n*column
        for gate in circuit:
            kind = gate[0]
            if kind == 'P':
                rows = [1 << j for j in range(dimension)]
                rows[offset:offset+n] = [row << offset for row in gate[1]]
                out.append(('P', tuple(rows)))
            elif kind == 'D':
                rows, linear = [0]*dimension, [0]*dimension
                rows[offset:offset+n] = [row << offset for row in gate[1]]
                linear[offset:offset+n] = gate[2]
                out.append(('D', tuple(rows), tuple(linear)))
            elif kind in ('X', 'C'):
                out.append((kind, gate[1] << offset)+gate[2:])
            else:
                require(kind == 'phase', 'witness native gate')
                if repeat_constant or column == 0:
                    out.append(gate)
    return tuple(out)


def run(word, result, candidates, controller, phase_source):
    rejected = {}

    def reject(name, action):
        try:
            action()
        except ValueError as error:
            rejected[name] = str(error)
            return
        raise ValueError('negative control accepted: '+name)

    records = {(a, b): recipe for a, b, recipe in candidates['pairs']}
    # These are actual source pairs, chosen once after locating nondegenerate
    # faults. They are fixed regression witnesses, not a continuing search.
    a, b = 0, 249
    recipe = records[a, b]
    expected = adjoint(frame(tuple(word['frames'][a])))+frame(tuple(word['frames'][b]))
    actual = lowered(recipe)
    equal(9, actual, expected, 'native control baseline')
    reject('native_global_i_preserving_conjugation_action',
           lambda: equal(9, actual+(('phase', 1),), expected, 'lost absolute phase'))
    reject('native_left_right_order',
           lambda: equal(9, monomial(recipe['left'])+gaussian(recipe['rank'])+monomial(recipe['right']),
                         expected, 'reversed native factors'))
    reject('native_missing_positive_child',
           lambda: equal(9, monomial(recipe['right'])+monomial(recipe['left']), expected, 'omitted native Gaussian'))
    equal(18, lift(9, 2, actual), lift(9, 2, expected), 'actual two-column native baseline')
    reject('native_constant_i_not_raised_to_column_width',
           lambda: equal(18, lift(9, 2, actual, repeat_constant=False), lift(9, 2, expected), 'wrong i^(p*f)'))
    require(any(event[0] == 'SIGNED_SWAP' for event in controller['physical_events']), 'actual exterior minus source')
    reject('exterior_minus_incorrectly_tensor_powered',
           lambda: equal(18, lift(9, 2, (('phase', 2),)), (('phase', 2),), 'exterior sign squared'))
    reject('tensor_of_sum_replaced_by_sum_of_tensors',
           lambda: equal(2, (('C', 3, 1),), (('C', 1, 1), ('C', 2, 1)), 'tensoring a Gaussian expansion termwise'))
    reject('zero_column_agrees_but_quadratic_operator_differs',
           lambda: equal(2, (), (('D', (2, 1), (0, 0)),), 'missing controlled sign'))

    a, b = 3, 117
    helper = records[a, b]
    helper_path = adjoint(frame(tuple(word['frames'][a])))+frame(tuple(word['frames'][b]))
    equal(9, adjoint(monomial(helper['right']))+helper_path+adjoint(monomial(helper['left'])),
          gaussian(helper['rank']), 'whole-helper control baseline')
    reject('whole_helper_pre_normalizer_not_inverted',
           lambda: equal(9, monomial(helper['right'])+helper_path+adjoint(monomial(helper['left'])),
                         gaussian(helper['rank']), 'wrong whole-helper entry'))

    changed = deepcopy(candidates)
    changed['pairs'][0][2]['left']['phase'] = (changed['pairs'][0][2]['left']['phase']+1) % 4
    reject('registered_recipe_payload_drift', lambda: check_native(word, result, changed))
    changed_word = deepcopy(word)
    scalar = next(event for event in changed_word['program'] if event[0] == 'ADD')
    scalar[-1] = (scalar[-1]+1) % len(word['frames'])
    reject('scalar_chart_mismatch', lambda: local_gauge(changed_word, result))
    changed_word = deepcopy(word)
    move = next(event for event in changed_word['program'] if event[0] == 'MOVE')
    move[2], move[3] = move[3], move[2]
    reject('MOVE_reversed_source_and_target', lambda: local_gauge(changed_word, result))
    changed_word = deepcopy(word)
    changed_word['live'][-1] = changed_word['live'][0]
    reject('aliased_local_public_role', lambda: ownership_and_invoice(changed_word, controller, result))

    changed_controller = deepcopy(controller)
    changed_controller['physical_events'].remove(next(event for event in changed_controller['physical_events'] if event[0] == 'Q_POWER'))
    reject('caller_missing_central_translation', lambda: free_laurent(changed_controller))
    changed_controller = deepcopy(controller)
    next(event for event in changed_controller['physical_events'] if event[0] == 'SIGNED_SWAP')[0] = 'SWAP'
    reject('caller_exterior_swap_sign_lost', lambda: free_laurent(changed_controller))
    changed_controller = deepcopy(controller)
    changed_controller['diagonal'][0][0] *= -1
    reject('caller_wrong_raw_diagonal_Q_exponent', lambda: free_laurent(changed_controller))

    q = word['ports'][0]
    reject('canonical_rank_one_chart_mistaken_for_C_q',
           lambda: equal(9, frame(tuple(word['frames'][word['initial'][word['live'][0]]])),
                         (('C', q, 1),), 'omitted nontrivial intrinsic main adapter'))
    port_recipe = next(item for item in phase_source['recipes'] if item['q'] == q)
    basis = orthogonal_base(q, port_recipe)
    stage = 1
    columns = route(stage, q, basis)
    spectators = positive(AXES[9:17])
    entry = contact(positive(AXES[:9]), terms(list(spectators)+[(q, 1)]), columns)
    exit_ = contact(terms(list(spectators)+[(axis, 1) for axis in AXES[:9]]), positive(AXES[:17]), columns)
    desired = phase(stage_terms(stage, q))
    require(transformed_path(stage_terms(0, q), entry, exit_, columns) == desired, 'actual contact control baseline')
    changed_exit = dict(exit_)
    changed_exit['translation'] ^= AXES[264]
    reject('contact_corrupts_arbitrary_spectator_row',
           lambda: require(transformed_path(stage_terms(0, q), entry, changed_exit, columns) == desired,
                           'nonidentity spectator action'))
    diagonal = next(term for term in controller['diagonal'] if term[0] == -1)
    raw = terms([(q, -1)]+[item for s, yes in enumerate(diagonal[1:]) if yes for item in stage_terms(s, q)])
    corrected = phase(terms(list(raw)+[(q, 2)]))
    reject('main_whole_job_final_translation_omitted',
           lambda: require(phase(raw) == corrected, 'omitted X_q final raw endpoint correction'))
    return rejected
