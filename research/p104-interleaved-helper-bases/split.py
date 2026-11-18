"""Apply one helper split to an oriented scalar communication network."""


from network import add_scaled, coefficients


def apply_split(net, event):
    """Use the direction specified in the event before this call."""
    first = net.first_output
    role = event["role"]
    chart = event["split_chart"]
    if (net.initial[role], net.final[role]) != (event["source_chart"], event["return_chart"]):
        raise ValueError("helper split boundary")
    direction = coefficients(event["source_direction"])
    probe = coefficients(event["source_covector"])
    readout = coefficients(event["readout"])
    response = coefficients(event["return_direction"])
    decode = coefficients(event["return_covector"])
    calibration = coefficients(event["calibration"])
    pulse = coefficients(event["pulse"])
    input_scale = sum(probe.get(i, 0) * v for i, v in direction.items())
    output_scale = sum(decode.get(i, 0) * v for i, v in response.items())
    if not input_scale or not output_scale or not response.get(role):
        raise ValueError("zero helper split pivot")
    if not all(net.initial[i] == net.initial[role] for i in direction.keys() | probe.keys()):
        raise ValueError("source vectors use different charts")
    if not all(net.final[i] == net.final[role] for i in response.keys() | decode.keys()):
        raise ValueError("return vectors use different charts")
    fresh = len(net.initial)
    # Set the old pivot coordinate to zero. Add the source direction to encode the new input.
    multiplier = {~i: -v / input_scale for i, v in probe.items() if i != role}
    multiplier[~role] = 1 / input_scale

    def change_inputs(row):
        coefficient = sum(row.get(~i, 0) * value for i, value in direction.items())
        if not coefficient and ~role not in row:
            return row
        changed = dict(row)
        changed.pop(~role, None)
        add_scaled(changed, multiplier, coefficient)
        return changed

    rows = {k: change_inputs(a) for k, a in net.forms.items()}
    observed = change_inputs(readout)
    excitation = {~fresh: 1 / output_scale}
    add_scaled(excitation, change_inputs(calibration), -1 / output_scale)
    for k, coefficient in pulse.items():
        row = dict(rows[k])
        add_scaled(row, excitation, coefficient)
        rows[k] = row
    returned = {}
    for i, coefficient in decode.items():
        add_scaled(returned, rows[first + i], coefficient)
    pivot = rows[first + role]
    for i, coefficient in response.items():
        if i != role:
            row = dict(rows[first + i])
            add_scaled(row, pivot, -coefficient / response[role])
            rows[first + i] = row
    rows[first + role] = observed
    rows[first + fresh] = returned
    final = net.final + [net.final[role]]
    final[role] = chart
    return type(net)(first, net.initial + [chart], final, dict(net.moves), rows)
