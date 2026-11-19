"""Reproduce the parallel-bank replacement from PR 7756. See retained/CREDITS.md."""

from fractions import Fraction
from network import Network, add_scaled, coefficients, need


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


def check_bank(net, weights, chart):
    for donor in weights:
        if donor < 0:
            need(~donor < len(net.initial) and net.initial[~donor] == chart, "public bank chart")
        else:
            need(donor in net.moves and net.moves[donor][1] == chart, "paid bank chart")


def substitute(row, key, replacement):
    if key not in row:
        return row
    result = row.copy()
    add_scaled(result, replacement, result.pop(key))
    return result


def in_parallel_basis(net, key, weights):
    """Change the receiver basis and apply its inverse at the common sender."""
    need(weights[key] == 1 and all(net.moves[j] == net.moves[key] for j in weights),
         "same directed paid endpoints and unit pivot")
    others = {j: v for j, v in weights.items() if j != key}
    rows = {}
    for j, row in net.forms.items():
        correction = dot(row, others)
        if correction:
            row = row.copy()
            add_scaled(row, {key: correction}, 1)
        rows[j] = row
    pivot = rows[key]
    for j, factor in others.items():
        rows[j] = rows[j].copy()
        add_scaled(rows[j], pivot, -factor)
    return Network(net.first_output, net.initial, net.final, net.moves, rows)


def puncture(net, event):
    """Replace one paid arrival with an independent helper input."""
    first, key, role = net.first_output, event["remove"], event["role"]
    sender, receiver = net.moves[key]
    destination = event["return_chart"]
    need(role >= 0 and role < len(net.initial) and sender != receiver, "puncture domain")
    source, response, calibration, readout = (coefficients(event[k]) for k in
        ("old_source_form", "old_terminal_response", "calibration", "new_readout"))
    gain = Fraction(event["response"])
    need(gain and source.get(role) and all(net.initial[j] == net.initial[role] for j in source),
         "source pivot and return gain")
    check_bank(net, calibration, receiver)
    check_bank(net, readout, destination)
    repairs = {r: (coefficients(row), Fraction(scale)) for r, row, scale in event["repairs"]}
    need(len(repairs) == len(event["repairs"]) and repairs.keys() >= response.keys() - {role},
         "complete terminal repairs")
    for r, (row, scale) in repairs.items():
        need(scale, "repair scale")
        check_bank(net, row, net.final[r])
    order = net.schedule()
    pulse = pulse_response(net, order, {key: 1})
    terminal = {j - first: v for j, v in pulse.items() if j >= first}
    need(terminal == response, "paid impulse at every terminal")
    need(dot(calibration, pulse) == 0 and dot(readout, pulse) == gain, "readout response")
    remainder = entrance_form(net, order, readout)
    add_scaled(remainder, entrance_form(net, order, {key: 1}), -gain)
    add_scaled(remainder, entrance_form(net, order, calibration), -1)
    add_scaled(remainder, source, -remainder.get(role, 0) / source[role])
    need(not remainder, "return equation modulo the source constraint")
    for row, scale in repairs.values():
        need(entrance_form(net, order, row) == source and dot(row, pulse) == scale,
             "local repair equation")
    old_input = {~r: -value / source[role] for r, value in source.items() if r != role}
    packet = {~role: Fraction(1)}
    add_scaled(packet, substitute(calibration, ~role, old_input), -1 / gain)

    def new_row(row):
        return substitute(substitute(row, ~role, old_input), key, packet)

    moves = net.moves.copy()
    del moves[key]
    rows = {j: new_row(row) for j, row in net.forms.items() if j != key}
    for r, value in response.items():
        if r != role:
            row, scale = repairs[r]
            rows[first + r] = rows[first + r].copy()
            add_scaled(rows[first + r], new_row(row), -value / scale)
    rows[first + role] = {j: value / gain for j, value in new_row(readout).items()}
    initial, final = net.initial.copy(), net.final.copy()
    initial[role], final[role] = receiver, destination
    return Network(first, initial, final, moves, rows)
