# SPDX-License-Identifier: Apache-2.0
"""Read-only source-bound local, literal-owner and exact-moment verification.

This establishes a finite candidate, not complete supplier/outer admission.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import hashlib
import json
import sys
import types

sys.dont_write_bytecode = True
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate import HERE, authenticate, build, need, read


def module(name, filename):
    result = types.ModuleType(name)
    result.__file__ = str(filename)
    exec(compile(filename.read_bytes(), str(filename), 'exec'), result.__dict__)
    return result


def main():
    need(__debug__, 'assertions required for retained independent frame engine')
    pins = authenticate()
    source = HERE / 'sources'
    local = module('independent_local', source / 'PR2839-independent_local.py')
    owner = module('independent_owners', source / 'PR2839-independent_owners.py')
    moment = module('exact_moment', source / 'PR2839-exact_moment.py')
    providers = read(source / 'PR2833-PROVIDERS.json')
    local_results = {}
    for tag, provider in [('base', 'gauge44'), ('extra', 'extra')]:
        word = read(source / ('PR2833-WORD-' + tag + '.json.gz'))
        report, start, end = local.check_frames(word)
        cleanup = local.check_cleanup(word)
        algebra = local.algebra(word)
        widths = [local.dm(end[r]) - local.dm(start[r])
                  for r in sorted(start) if r >= 224]
        need(widths == providers[provider]['widths'] and len(widths) == 408,
             'source-bound actual provider widths')
        paid = {int(k): v for k, v in providers[provider]['actual_paid_profile'].items()}
        need(paid == report['profile'], 'source-bound actual provider profile')
        providers[provider]['actual_paid_profile'] = paid
        local_results[tag] = {'profile': paid, 'cleanup_events': cleanup,
                              'operator_result': algebra}
    order, dispatch_rows, fill = build()
    need(order == read(HERE / 'ORDER.json'), 'literal regenerated order')
    need(dispatch_rows == read(HERE / 'DISPATCH.json'), 'literal regenerated dispatch')
    need(fill == read(HERE / 'FILL.json.gz'), 'literal regenerated allocation')
    plan = read(source / 'PR2833-PLAN.json')
    template = read(source / 'PR2833-T37-TEMPLATE.json.gz')
    dispatch = {(s, r): p for s, r, p in dispatch_rows}
    claimed = read(HERE / 'PROFILE.json')
    result, windows, _ = owner.check(248, order, fill, dispatch, claimed,
                                      plan, template, providers)
    need(windows[0, 0] == (16, -1, 18)
         and windows[124, 0] == (16, -1, 19), 'exact exceptional source windows')
    old_order = read(source / 'PR2843-ORDER.json')
    old_fill = read(source / 'PR2843-FILL.json.gz')
    old_dispatch = {(s, r): p for s, r, p in read(source / 'PR2843-DISPATCH.json')}
    baseline, _, _ = owner.check(124, old_order, old_fill, old_dispatch, None,
                                 plan, template, providers)
    delta = Counter(result['profile'])
    delta.subtract({rank: 2 * n for rank, n in baseline['profile'].items()})
    need({r: n for r, n in delta.items() if n} == {2: 1, 9: -2, 16: 1},
         'exact paid profile delta H2 + H16 - 2 H9')
    lower = Fraction(1718658508304930004819, 10**24)
    upper = lower + Fraction(1, 10**24)
    need(moment.moment(result['profile'], lower, 222208)[1] < 1,
         'strict candidate lower endpoint')
    need(moment.moment(result['profile'], upper, 222208)[0] > 1,
         'strict candidate upper endpoint')
    previous = Fraction(read(source / 'PR2843-CLAIM.json')['kappa'])
    target = lower - Fraction(1, 10**46) - Fraction(1, 10**70)
    need(target > previous, 'candidate target exceeds exact PR2843 headline')
    controls = []

    def reject(name, changed_fill, reason):
        try:
            owner.check(248, order, changed_fill, dispatch, claimed, plan, template, providers)
        except ValueError as error:
            need(str(error) == reason, 'wrong rejecting reason: ' + name + ': ' + str(error))
            controls.append(name)
        else:
            raise ValueError('accepted mutant: ' + name)

    def mutate(match, replacement):
        rows = list(fill['rows'])
        ids = [i for i, row in enumerate(rows) if row == match]
        need(len(ids) == 1, 'exact mutation preimage')
        rows[ids[0]] = replacement
        return {**fill, 'rows': rows}

    reject('missing_role', {**fill, 'rows': fill['rows'][:-1]}, 'complete role count')
    reject('overlapping_merged_roles', mutate([1, 224, 124, 0, 0, 7],
                                            [1, 224, 124, 0, 0, 6]), 'bin overlap')
    reject('unpaid_prefix_hole', mutate([1, 224, 124, 0, 0, 7],
                                      [1, 224, 124, 0, 0, 8]), 'compact bin prefix')
    reject('out_of_capacity', mutate([1, 224, 124, 0, 0, 7],
                                    [1, 224, 124, 0, 0, 10]), 'bin capacity')
    reject('undo_move_without_restoring_offset', mutate([0, 224, 124, 0, 0, 0],
                                                       [0, 224, 0, 0, 0, 0]),
           'compact bin prefix')
    need(authenticate() == pins, 'unchanged source inputs')
    print(json.dumps({'status': 'PASS_TWO_COPY_RESIDUE_FINITE_CANDIDATE',
                      'replicas': 248, 'roles': result['roles'],
                      'complex_lower': str(lower), 'complex_upper': str(upper),
                      'delta': {'2': 1, '9': -2, '16': 1}, 'controls': controls,
                      'scope': 'Independent local frame/free-operator replay, literal geometry, '
                               'complete paid profile and directed rational moment; '
                               'full native/global/outer admission is separate.'}, sort_keys=True))


if __name__ == '__main__':
    main()
