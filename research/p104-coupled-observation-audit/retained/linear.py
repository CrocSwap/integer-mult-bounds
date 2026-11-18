"""Verify local forms and all input columns. Adapted from PR 7726."""
from math import lcm
from network import add_scaled, main_roles, need
import physical


def entrance_form(net, order, weights):
    """Expand a local observation into independent public input coordinates."""
    row = dict(weights)
    for key in reversed(order):
        factor = row.pop(key, 0)
        if factor:
            add_scaled(row, net.forms[key], factor)
    need(all(i < 0 for i in row), "unresolved bank")
    return {~i: v for i, v in row.items()}


def pulse_response(net, order, pulse):
    values = {}
    for key in order:
        output = sum(c * values[j] for j, c in net.forms[key].items() if j in values)
        output += pulse.get(key, 0)
        if output:
            values[key] = output
    return values


def dot(left, right):
    return sum(left[k] * right[k] for k in left.keys() & right.keys())


def reverse_columns(net, layout):
    """Accumulate the coefficient of each output back to every public input."""
    first, size = net.first_output, len(net.initial)
    order = net.schedule()[::-1]
    grids = dict.fromkeys(net.forms, 1)
    grids.update({~i: 1 for i in range(size)})
    for k in order:
        for j, c in net.forms[k].items():
            grids[j] = lcm(grids[j], grids[k] * c.denominator)
    unit = lcm(*grids.values())
    columns = {k: {} for k in grids}
    for r in range(size):
        columns[first + r] = {r: unit}
    products = 0
    for k in order:
        output = columns.pop(k)
        for j, c in net.forms[k].items():
            bank = columns[j]
            for r, x in output.items():
                value, remainder = divmod(c.numerator * x, c.denominator)
                need(remainder == 0, "inexact reverse product")
                new = bank.get(r, 0) + value
                if new:
                    bank[r] = new
                else:
                    bank.pop(r, None)
                products += 1
    h = layout["hosted"]
    interface = main_roles(layout), set(h["Dports"]), list(zip(h["X2"], h["Y2"], strict=True))
    expected = physical.expected_rows(size, layout, interface, unit)
    target = {~r: {} for r in range(size)}
    for i, row in enumerate(expected):
        for j, coefficient in row.items():
            target[~j][i] = coefficient
    need(columns == target, "reverse public operator")
    return dict(columns=size, exact_products=products, scale=unit)
