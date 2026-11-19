"""Rebuild the P104 graph from the PR 7726 export and local bank changes."""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE / "vendor")]

from network import Network, add_scaled, coefficients, encoded, main_roles, need, pivot, read
from linear import dot, entrance_form, pulse_response

BASE = "ba59d5db17c40185c8608a734ced10135d8c041e432c3840e9034868781c31a2"


def digest(value):
    return sha256(encoded(value)).hexdigest()


def receipt(name, value):
    need(json.loads(json.dumps(value)) == read(HERE / "results" / (name + ".json")),
         "receipt mismatch for " + name)


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


def puncture(net, event, verify):
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
    if verify:
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


def paid_split(net, event, verify):
    """Send the missing part of a readout and install two independent returns."""
    first, role = net.first_output, event["r"]
    a, b, c, sender, z = (event[j] for j in ("A", "B", "D", "E", "Z"))
    need((net.initial[role], net.final[role]) == (a, z), "parent split interface")
    sent, local, source, direction, calibration, decoder, response, injection = (
        coefficients(event[j]) for j in ("send", "received", "s", "w", "cal", "y", "t", "inj"))
    check_bank(net, sent, sender)
    check_bank(net, local, b)
    check_bank(net, calibration, c)
    need(all(net.initial[i] == a for i in source.keys() | direction.keys()), "split source charts")
    need(all(net.final[i] == z for i in decoder.keys() | response.keys()), "split return charts")
    for k in injection:
        need((net.moves[k][0] if k in net.moves else net.final[k - first]) == c, "injection chart")
    key = next(k for k in range(first) if k not in net.moves)
    moves, rows = dict(net.moves), dict(net.forms)
    moves[key], rows[key] = (sender, b), sent
    observed = dict(local)
    observed[key] = Fraction(1)
    source_scale, return_scale = dot(source, direction), dot(decoder, response)
    need(source_scale and return_scale and response.get(role), "split normalization")
    if verify:
        extended = Network(first, net.initial, net.final, moves, rows)
        order = extended.schedule()
        need(entrance_form(extended, order, observed) == source, "split source observation")
        expected = entrance_form(extended, order, {first + r: v for r, v in decoder.items()})
        need(entrance_form(extended, order, calibration) == expected, "split calibration")
        pulse = pulse_response(extended, order, injection)
        source_pulse = {j: sum(v * direction.get(~i, 0) for i, v in row.items() if i < 0)
                        for j, row in rows.items()}
        for values in (pulse, pulse_response(extended, order, source_pulse)):
            need({j - first: v for j, v in values.items() if j >= first} == response,
                 "split terminal response")
        need(not dot(observed, pulse) and not dot(calibration, pulse), "split pulse isolation")
    steering = {~r: -v / source_scale for r, v in source.items() if r != role}
    steering[~role] = 1 / source_scale

    def rescale(row):
        factor = sum(row.get(~r, 0) * v for r, v in direction.items())
        if not factor and ~role not in row:
            return row
        result = row.copy()
        result.pop(~role, None)
        add_scaled(result, steering, factor)
        return result

    rows = {j: rescale(row) for j, row in rows.items()}
    fresh = len(net.initial)
    amplitude = {~fresh: 1 / return_scale}
    add_scaled(amplitude, rescale(calibration), -1 / return_scale)
    for j, v in injection.items():
        rows[j] = rows[j].copy()
        add_scaled(rows[j], amplitude, v)
    returned = {}
    for r, v in decoder.items():
        add_scaled(returned, rows[first + r], v)
    pivot = rows[first + role]
    for r, v in response.items():
        if r != role:
            rows[first + r] = rows[first + r].copy()
            add_scaled(rows[first + r], pivot, -v / response[role])
    rows[first + role], rows[first + fresh] = rescale(observed), returned
    final = net.final + [z]
    final[role] = b
    return Network(first, net.initial + [c], final, moves, rows)


def relay(net, event, verify):
    """Move a paid transfer directly to its receiver."""
    key, lead = event["remove"], event["pivot"]
    combination = coefficients(event["combination"])
    side = coefficients(event["receiver"])
    sender = coefficients(event["sender"])
    middle = net.moves[key][1]
    old, destination = net.moves[lead]
    need(old == middle and all(net.moves.get(j) == (middle, destination) for j in combination),
         "relay block")
    check_bank(net, sender, event["source_chart"])
    check_bank(net, side, destination)
    if verify:
        order = net.schedule()
        observed = combination.copy()
        add_scaled(observed, side, 1)
        need(entrance_form(net, order, sender) == entrance_form(net, order, observed),
             "relay observation at both charts")
    return pivot(net, event)


def replace_many(row, replacements):
    used = row.keys() & replacements.keys()
    if not used:
        return row
    result = {i: v for i, v in row.items() if i not in used}
    for i in used:
        add_scaled(result, replacements[i], row[i])
    return result


def grouped_puncture(net, event, mains, verify):
    """Use one local repair to remove the pulses from several new entrances."""
    order = net.schedule() if verify else None
    first = net.first_output
    lanes = event["lanes"]
    roles, pivots = set(), set()
    gauges, sources, packets, readouts = {}, {}, {}, {}
    terminal_repairs = {r: coefficients(row) for r, row in event["repairs"]}
    initial, final = net.initial.copy(), net.final.copy()
    for lane in lanes:
        k, r, gain = lane["remove"], lane["role"], Fraction(lane["response"])
        sender, receiver = net.moves[k]
        need(gain and 0 <= r < len(initial) and r not in roles | mains and k not in pivots and initial[r] == sender
             and initial[r] != final[r], "disjoint helper and paid pivots")
        direction = coefficients(lane["receive_direction"])
        need(direction.get(k) == 1 and all(net.moves[j] == (sender, receiver) for j in direction)
             and direction.keys().isdisjoint(gauges), "disjoint parallel directions")
        gauges.update({j: (k, v) for j, v in direction.items()})
        replacement = coefficients(lane["old_input"])
        need(all(j < 0 for j in replacement), "source replacement uses only public inputs")
        check_bank(net, replacement, sender)
        calibration, returned = (coefficients(lane[j]) for j in ("calibration", "new_readout"))
        check_bank(net, calibration, receiver)
        check_bank(net, returned, final[r])
        sources[~r] = replacement
        packets[k] = r, gain, calibration
        readouts[first + r] = returned
        initial[r] = receiver
        roles.add(r)
        pivots.add(k)
    need(all(row.keys().isdisjoint(sources) for row in sources.values()), "no recursive source replacement")
    need(terminal_repairs.keys().isdisjoint(roles), "separate returned and repaired roles")
    for r, row in terminal_repairs.items():
        check_bank(net, row, final[r])

    def gauge(row):
        result = row.copy()
        for j in row.keys() & gauges.keys():
            k, v = gauges[j]
            if k != j:
                add_scaled(result, {k: row[j]}, v)
        return result

    if verify:
        pulses = [pulse_response(net, order, coefficients(l["receive_direction"])) for l in lanes]
        def on_constraint(row):
            expansion = {~j: q for j, q in entrance_form(net, order, row).items()}
            return replace_many(expansion, sources)
        pivots_by_role = {}
        for lane in lanes:
            source = {~j: q for j, q in coefficients(lane["old_source_form"]).items()}
            check_bank(net, source, net.initial[lane["role"]])
            need(not replace_many(source, sources), "source equations after substitution")
            minor = {j: source[j] for j in source.keys() & sources.keys()}
            while minor:
                j = max(minor)
                if j not in pivots_by_role:
                    pivots_by_role[j] = {i: q / minor[j] for i, q in minor.items()}
                    break
                add_scaled(minor, pivots_by_role[j], -minor[j])
            else:
                raise ValueError("singular minor on the surrendered source inputs")
            k, r = lane["remove"], lane["role"]
            _, gain, calibration = packets[k]
            diff = readouts[first + r].copy()
            add_scaled(diff, calibration, -1)
            add_scaled(diff, {k: gain}, -1)
            need(not on_constraint(diff) and all(dot(diff, pulse) == 0 for pulse in pulses),
                 "group return on the constrained source and every pulse")
        for r in range(len(initial)):
            if r in roles:
                continue
            row = terminal_repairs.get(r, {})
            need(not on_constraint(row) and all(dot(row, pulse) == pulse.get(first + r, 0)
                 for pulse in pulses), "group repair on all old inputs and every pulse")

    rows = {j: gauge(row) for j, row in net.forms.items()}
    for j, (k, factor) in gauges.items():
        if j != k:
            add_scaled(rows[j], rows[k], -factor)
    injection = {}
    for k, (r, gain, calibration) in packets.items():
        packet = {~r: 1 / gain}
        add_scaled(packet, replace_many(gauge(calibration), sources), -1 / gain)
        need(packet.keys().isdisjoint(pivots), "calibration availability")
        injection[k] = packet

    def adjust(row):
        return replace_many(replace_many(row, sources), injection)

    rows = {j: adjust(row) for j, row in rows.items() if j not in pivots}
    for r, row in terminal_repairs.items():
        rows[first + r] = rows[first + r].copy()
        add_scaled(rows[first + r], adjust(gauge(row)), -1)
    rows.update({j: adjust(gauge(row)) for j, row in readouts.items()})
    return Network(first, initial, final, {k: ab for k, ab in net.moves.items() if k not in pivots}, rows)


def serialize(net, frames):
    return dict(frames=frames, initial=net.initial, final=net.final, first_output=net.first_output,
                moves=[[k, *v] for k, v in sorted(net.moves.items())],
                forms=[[k, [[i, str(v)] for i, v in sorted(row.items())]]
                       for k, row in sorted(net.forms.items())], schedule=net.schedule())


def build(verify=False, observer=None):
    source = read(HERE / "data/BASE-GRAPH.json.gz")
    layout = read(HERE / "data/BASE-INTERFACE.json")
    journal = read(HERE / "EDITS.json")
    need(digest(source) == journal["source_sha256"] == BASE, "PR 7726 source graph")
    moves = {k: (a, b) for k, a, b in source["moves"]}
    rows = {k: coefficients(row) for k, row in source["forms"]}
    net = Network(source["first_output"], source["initial"], source["final"], moves, rows)
    need(source["schedule"] == net.schedule() and layout["public"] == len(net.initial) == 1260,
         "published schedule and independent fields")
    labels = list(layout["source_labels"])
    mains = main_roles(layout)
    for index, event in enumerate(journal["events"]):
        split = event["type"] == "paid_side_split"
        reverse = event["d"] if split else event["orientation"]
        need(reverse in (0, 1), "edit orientation")
        oriented = net.transpose() if reverse else net
        if event["type"] in ("parallel_bank_puncture", "puncture_and_rehost", "paid_side_split"):
            role = event["r"] if split else event["role"]
            need(role not in mains and oriented.initial[role] != oriented.final[role], "independent helper")
        if event["type"] in ("parallel_bank_puncture", "parallel_relay"):
            oriented = in_parallel_basis(oriented, event["remove"], coefficients(event["receive_direction"]))
        if observer is not None:
            observer(index, oriented, event)
        if event["type"] == "parallel_relay":
            out = relay(oriented, event, verify)
        elif event["type"] == "grouped_puncture":
            out = grouped_puncture(oriented, event, mains, verify)
        elif split:
            out = paid_split(oriented, event, verify)
            labels.append(max(labels) + 1)
        else:
            need(event["type"] in ("parallel_bank_puncture", "puncture_and_rehost"), "edit type")
            out = puncture(oriented, event, verify)
        if verify:
            out.schedule()
        net = out.transpose() if reverse else out
    layout.update(public=len(net.initial), frames=source["frames"], source_labels=labels)
    return serialize(net, layout["frames"]), layout, net


if __name__ == "__main__":
    sys.stdout.buffer.write(encoded(build()[0]))
