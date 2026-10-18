#!/usr/bin/env python3
"""Assertion-enabled source replay for the historical center-basis experiment.

Copyright 2026 Curtis Dransfield. Apache-2.0; substantial OpenAI Codex assistance.
"""
from fractions import Fraction as F
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from circuit import census, charge, closed_saving, require, serializable, shear, verify_product
require(__debug__, 'Inherited constructors must run with assertions enabled')
sys.path.insert(0, str(ROOT / 'scripts'))
from experiments.complex_centers import factor, invoke, counts, verify_factor
from experiments.disjoint_tensor import DisjointTensor, scalar_program
from general_network_guard import guard


class Form:
    """Sparse rational row for simultaneous, independent dirty input columns."""
    def __init__(self, row):
        self.row = {i: F(c) for i, c in row.items() if c}
    def __add__(self, other):
        row = dict(self.row)
        for i, c in other.row.items():
            row[i] = row.get(i, F(0)) + c
        return Form(row)
    def __mul__(self, c):
        return Form({i: c*x for i, x in self.row.items()})
    __rmul__ = __mul__
    def __sub__(self, other):
        return self + (-1)*other
    def __eq__(self, other):
        return isinstance(other, Form) and self.row == other.row


def invocation_control(h):
    f = shear(factor(h), 1, 2, -1)
    code = scalar_program(DisjointTensor(h))
    n, R = len(f['triples']), code['roles']
    total = 2*n + R + h
    for inverse in (False, True):
        values = [Form({i: 1}) for i in range(total)]
        x, y = values[:n], values[n:2*n]
        side, center = values[2*n:2*n+R], values[2*n+R:]
        before = [list(bank) for bank in (x, y, side, center)]
        invoke(x, y, side, center, code, f, inverse=inverse)
        sign = -1 if inverse else 1
        require(x == before[0] and side == before[2] and center == before[3],
                'Dirty inputs not restored')
        require(y == [b + sign*a for a, b in zip(before[0], before[1])],
                'Full signed invocation is not target += sign*source')
    return dict(h=h, source_roles=n, target_roles=n, side_roles=R, center_roles=h,
                independent_columns_per_direction=total, directions=2,
                sources_unchanged=True, arbitrary_side_and_center_inputs_restored=True)


def replay():
    h = 26
    old = factor(h)
    new = shear(old, 1, 2, -1)
    search = census(old, seed=20)
    require((search['selected']['i'], search['selected']['j'], search['selected']['sign']) == (1, 2, -1),
            'Selected one-shear minimum changed')
    product_checks = verify_product(new)
    region = []
    for ground_size in range(8, 41, 2):
        b = factor(ground_size)
        a = shear(b, 1, 2, -1)
        saving = charge(b)['G_plus_H'] - charge(a)['G_plus_H']
        require(saving == closed_saving(ground_size), 'Closed saving formula failed')
        region.append(dict(h=ground_size, old=charge(b), new=charge(a), saving=saving))
    baseline = json.loads((ROOT / 'certificates/dyadic-central-factor.json').read_text())
    before, after = charge(old), charge(new)
    require(before == dict(G=14100, H=31281, G_plus_H=45381), 'Baseline scalar bill changed')
    side = DisjointTensor(h)
    code = scalar_program(side)
    disjoint_roles = side.compile()['roles']
    n = counts(h, disjoint_roles)
    require(serializable(n) == baseline['counts'], 'Historical rank ledger changed')
    M = sum(len(ins)+len(outs)-2 for ins, outs in code['gates'])
    C, J = len(code['sources']), len(code['outputs'])
    require((M, C, J) == tuple(baseline['scalar_charge'][k] for k in ('M', 'C', 'J')),
            'Fresh complete side scalar counts changed')
    fixed = 4*M + 2*C + 4*J
    old_steps = 3*n['v']**2*(fixed + 2*before['G_plus_H'])
    new_steps = 3*n['v']**2*(fixed + 2*after['G_plus_H'])
    require(old_steps == baseline['scalar_charge']['steps'] and new_steps < old_steps,
            'Full scalar bill does not improve')
    E = 64*(n['W']+n['m']+1)**3
    slack = E-(4*new_steps + 8*n['s'] + 8*n['W'] + 8*n['m'])
    require(slack > 0 and E == baseline['scalar_charge']['E'], 'Node-charge guard failed')
    g = guard(n['m'], n['s'], E, F(1,100), F(1,1000), F(5))
    require(serializable(g) == baseline['scalar_charge']['guard'], 'Retained conditional recurrence changed')
    # The original checker rejects the broadened numerator alphabet; the
    # optional adapter explicitly prices -2 as a signed unit update instead.
    try:
        verify_factor(shear(factor(8), 1, 2, -1))
    except ValueError as exc:
        require('dyadic weights' in str(exc), 'Wrong historical-alphabet rejection')
        original_rejection = str(exc)
    else:
        raise ValueError('Historical alphabet guard unexpectedly accepted -2')
    result = dict(primary_h=h, central_coefficients_checked=product_checks['coefficients_checked'],
                central_coefficient_sha256=product_checks['coefficient_sha256'], one_shear_census=search,
                chosen_shear_parameter_controls=region,
                before=before, after=after, counts=n,
                full_scalar_charge=dict(M=M, C=C, J=J, old_steps=old_steps, new_steps=new_steps,
                    saved_steps=old_steps-new_steps, per_invocation_saved=2*(before['G_plus_H']-after['G_plus_H']),
                    fixed_side_steps_per_invocation=fixed, E=E, new_slack=slack,
                    additional_helper_roles=0, center_basis_adapter_operations=0,
                    frame_changes=0, child_profile_changes=0, guard=g),
                source_reuse='Fresh side topology/counts; unchanged h26 side coefficient and phase proofs inherited, not replayed',
                historical_alphabet_rejection=original_rejection,
                complete_dirty_invocations=[invocation_control(h) for h in (8, 10)])
    result['inherited_python_imports'] = sorted({
        Path(module.__file__).resolve().relative_to(ROOT).as_posix()
        for module in tuple(sys.modules.values())
        if getattr(module, '__file__', None) and Path(module.__file__).is_file()
        and Path(module.__file__).resolve().is_relative_to(ROOT)
        and not Path(module.__file__).resolve().is_relative_to(HERE)})
    return result


if __name__ == '__main__':
    print(json.dumps(serializable(replay()), sort_keys=True))
