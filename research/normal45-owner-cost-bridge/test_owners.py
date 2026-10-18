# SPDX-License-Identifier: Apache-2.0
"""Defect-sensitive whole-owner controls, active with Python -O."""
from collections import defaultdict
import copy

from owners import invoice, need


def run_controls(order, fill, dispatch, plan, template, providers, profile):
    reference = invoice(order, fill, dispatch, plan, template, providers, profile, 66808)
    rejected = {}

    def check(name, reason, **changes):
        arguments = dict(order=order, fill=fill, dispatch_rows=dispatch, plan=plan,
                         template=template, providers=providers,
                         claimed_profile=profile, claimed_physical=66808)
        arguments.update(changes)
        try:
            invoice(**arguments)
        except ValueError as error:
            need(str(error) == reason, 'wrong control rejection: ' + name + ': ' + str(error))
            rejected[name] = reason
        else:
            raise ValueError('accepted defective owner input: ' + name)

    def rows_at(index, replacement):
        rows = list(fill['rows'])
        rows[index] = replacement
        return {**fill, 'rows': rows}

    check('missing_helper_role', 'complete helper role count',
          fill={**fill, 'rows': fill['rows'][:-1]})
    row = list(fill['rows'][1])
    row[1] = fill['rows'][0][1]
    check('duplicate_helper_identity', 'unique helper at call', fill=rows_at(1, row))
    row = list(fill['rows'][1])
    row[2:5] = fill['rows'][0][2:5]
    check('same_call_family_alias', 'distinct physical family at call', fill=rows_at(1, row))

    from owners import event_windows
    _, windows = event_windows(order, template, plan)
    i, row = next((i, r) for i, r in enumerate(fill['rows'])
                  if windows[tuple(r[2:4])][1] >= 0)
    row = list(row)
    row[0] = windows[tuple(row[2:4])][1]
    check('loan_at_last_source_touch', 'source-event window', fill=rows_at(i, row))
    i, row = next((i, r) for i, r in enumerate(fill['rows'])
                  if windows[tuple(r[2:4])][2] < len(order) - 1)
    row = list(row)
    row[0] = windows[tuple(row[2:4])][2] + 1
    check('loan_after_consumer', 'source-event window', fill=rows_at(i, row))
    row = list(fill['rows'][0])
    row[5] = windows[tuple(row[2:4])][0]
    check('width_spills_capacity', 'owner capacity', fill=rows_at(0, row))

    bins = defaultdict(list)
    by_call = {(s, r): p for s, r, p in dispatch}
    for index, row in enumerate(fill['rows']):
        width = providers[by_call[tuple(order[row[0]])]]['widths'][row[1]]
        bins[tuple(row[2:5])].append((row[5], row[5] + width, index))
    segments = next(v for v in bins.values() if len(v) >= 2)
    first, second = sorted(segments)[:2]
    row = list(fill['rows'][second[2]])
    row[5] = first[0]
    check('overlapping_helpers_across_calls', 'disjoint owner intervals',
          fill=rows_at(second[2], row))
    key, final = next((key, max(v)) for key, v in bins.items()
                      if max(v)[1] < windows[key[:2]][0])
    row = list(fill['rows'][final[2]])
    row[5] += 1
    check('unpaid_gap_before_residual', 'compact owner prefix', fill=rows_at(final[2], row))

    wrong = dict(profile)
    rank14_key = '14' if '14' in wrong else 14
    need(wrong[rank14_key] == 1, 'literal rank14 omission fixture')
    del wrong[rank14_key]
    check('omit_unique_rank14_residual', 'complete profile equality', claimed_profile=wrong)
    check('retain_old_82_buffer_stock', 'private stock equality', claimed_physical=66804)
    wrong_dispatch = [list(x) for x in dispatch]
    wrong_dispatch[0][2] = 'unbound'
    check('unknown_provider', 'dispatch provider', dispatch_rows=wrong_dispatch)
    wrong_template = copy.deepcopy(template)
    i = next(i for i, e in enumerate(wrong_template['execution_schedule']) if e['kind'] == 'bridge')
    del wrong_template['execution_schedule'][i]
    check('omit_actual_bridge_source_touch', 'source graph binding', template=wrong_template)
    wrong_plan = copy.deepcopy(plan)
    wrong_plan['sides']['3'] = wrong_plan['sides']['1']
    check('overlapping_child_names_on_one_family', 'disjoint physical-family loan lifetimes',
          plan=wrong_plan)
    wrong_order = [list(x) for x in order]
    first = next(i for i, (s, r) in enumerate(order) if r == 0 and s == 0)
    second = next(i for i, (s, r) in enumerate(order) if r == 0 and s == 1)
    wrong_order[first], wrong_order[second] = wrong_order[second], wrong_order[first]
    check('reverse_replica_progression', 'replica chronology', order=wrong_order)
    wrong_fill = rows_at(0, [True] + fill['rows'][0][1:])
    check('boolean_time_alias', 'integer helper role', fill=wrong_fill)

    # Positive controls are equivalent presentations, not new candidates.
    reversed_rows = {**fill, 'rows': list(reversed(fill['rows']))}
    need(invoice(order, reversed_rows, dispatch, plan, template, providers, profile, 66808)
         == reference, 'row-order invariance')
    cached = copy.deepcopy(plan)
    cached['windows'] = {}
    cached['T'], cached['live'], cached['profile'] = 1, 1, {}
    historical = copy.deepcopy(template)
    historical['calls'], historical['live'], historical['physical'] = 1, 1, 1
    need(invoice(order, fill, dispatch, cached, historical, providers, profile, 66808)
         == reference, 'cached historical totals are not actual invoice')
    return dict(rejecting=rejected, positive=['row permutation', 'ignore historical cached totals'])
