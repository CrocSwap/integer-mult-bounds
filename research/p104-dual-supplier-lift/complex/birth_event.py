"""Apply one helper split to an oriented scalar communication network."""

from fractions import Fraction


def linear_combination(destination, source, scale):
    for index, coefficient in source.items():
        value = destination.get(index, 0) + scale * coefficient
        if value:
            destination[index] = value
        else:
            destination.pop(index, None)


def read_row(items):
    row = {index: Fraction(text) for index, text in items}
    if [[index, str(row[index])] for index in sorted(row)] != items or not all(row.values()):
        raise ValueError("noncanonical split row")
    return row


def apply_split(net, event):
    """Use the direction specified in the event before this call."""
    first = net.first_output
    role = event["role"]
    chart = event["split_chart"]
    if (net.initial[role], net.final[role]) != (event["source_chart"], event["return_chart"]):
        raise ValueError("helper split boundary")
    direction = read_row(event["source_direction"])
    probe = read_row(event["source_covector"])
    readout = read_row(event["readout"])
    response = read_row(event["return_direction"])
    decode = read_row(event["return_covector"])
    calibration = read_row(event["calibration"])
    pulse = read_row(event["pulse"])
    input_scale = sum(probe.get(i, 0) * v for i, v in direction.items())
    output_scale = sum(decode.get(i, 0) * v for i, v in response.items())
    if not input_scale or not output_scale or not response.get(role):
        raise ValueError("zero helper split pivot")
    if not all(net.initial[i] == net.initial[role] for i in direction.keys() | probe.keys()):
        raise ValueError("source vectors use different charts")
    if not all(net.final[i] == net.final[role] for i in response.keys() | decode.keys()):
        raise ValueError("return vectors use different charts")
    fresh = len(net.initial)
    # The old input value has coordinate role set to zero before it receives the source direction.
    multiplier = {~i: -v / input_scale for i, v in probe.items() if i != role}
    multiplier[~role] = 1 / input_scale

    def change_inputs(row):
        coefficient = sum(row.get(~i, 0) * value for i, value in direction.items())
        if not coefficient and ~role not in row:
            return row
        changed = dict(row)
        changed.pop(~role, None)
        linear_combination(changed, multiplier, coefficient)
        return changed

    rows = {k: change_inputs(a) for k, a in net.forms.items()}
    observed = change_inputs(readout)
    excitation = {~fresh: 1 / output_scale}
    linear_combination(excitation, change_inputs(calibration), -1 / output_scale)
    for k, coefficient in pulse.items():
        row = dict(rows[k])
        linear_combination(row, excitation, coefficient)
        rows[k] = row
    returned = {}
    for i, coefficient in decode.items():
        linear_combination(returned, rows[first + i], coefficient)
    pivot = rows[first + role]
    for i, coefficient in response.items():
        if i != role:
            row = dict(rows[first + i])
            linear_combination(row, pivot, -coefficient / response[role])
            rows[first + i] = row
    rows[first + role] = observed
    rows[first + fresh] = returned
    final = net.final + [net.final[role]]
    final[role] = chart
    return type(net)(first, net.initial + [chart], final, dict(net.moves), rows)
