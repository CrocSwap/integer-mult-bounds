"""Verify the local equations on independent inputs and the full transposed operator."""
from collections import Counter
from math import lcm
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from construction import HERE, add_scaled, apply_edits, build, coefficients, digest, main_roles, need, read, receipt
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


def record_job_changes(net, edit, ranks, paid, targets):
    kind = edit["event"]
    if kind == "restrict":
        role = edit["role"]
        targets[ranks(net.initial[role], net.final[role])] -= 1
        for bank in edit["banks"]:
            paid[ranks(*net.moves[bank["remove"]])] -= 1
    elif kind == "split":
        a, c, z = (edit[k] for k in ("source_chart", "split_chart", "return_chart"))
        targets[ranks(a, z)] -= 1
        targets.update([ranks(a, c), ranks(c, z)])
    elif kind == "pivot":
        removed, pivot = net.moves[edit["remove"]], net.moves[edit["pivot"]]
        paid.subtract([ranks(*removed), ranks(*pivot)])
        paid[ranks(edit["source_chart"], pivot[1])] += 1
    else:
        need(kind == "hub", "priced graph edit")
        incoming, outgoing = net.moves[edit["incoming"]], net.moves[edit["outgoing"]]
        paid.subtract([ranks(*incoming), ranks(*outgoing)])
        paid.update([ranks(incoming[0], edit["hub"]), ranks(edit["hub"], outgoing[1])])


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


def alternate_restrictions(journal):
    result = []
    for case in read(HERE / "data/RESTRICTION-CONTROLS.json"):
        prior = case["alternative"]
        index, = [i for i, e in enumerate(journal) if e.get("role") == prior["role"]]
        last, = [i for i, e in enumerate(journal) if e["event"] == "split" and
                 (e["role"], e["split_chart"], e["direction"]) ==
                 (case["split_role"], case["split_chart"], case["direction"])]
        edits = list(journal[:last])
        need(edits[index]["banks"][0]["remove"] == prior["banks"][0]["remove"],
             "the control retires the same paid instruction")
        edits[index] = prior
        net, _ = apply_edits(edits)
        split = journal[last]
        if split["direction"] == "transpose":
            net = net.transpose()
        order = net.schedule()
        effect = pulse_response(net, order, coefficients(split["pulse"]))
        actual = entrance_form(net, order, coefficients(split["readout"]))
        required = coefficients(split["source_covector"])
        old_outputs = {net.first_output + i: v for i, v in coefficients(split["return_covector"]).items()}
        observed = entrance_form(net, order, coefficients(split["calibration"]))
        terminal = {i - net.first_output: v for i, v in effect.items() if i >= net.first_output}
        equations = {"readout": (actual, required), "calibration": (observed, entrance_form(net, order, old_outputs)),
                     "response": (terminal, coefficients(split["return_direction"]))}
        failures = {}
        for name, (left, right) in equations.items():
            indices = sorted(i for i in left.keys() | right.keys() if left.get(i, 0) != right.get(i, 0))
            if indices:
                i = indices[0]
                failures[name] = dict(coordinates=len(indices), first_coordinate=i,
                                      actual=str(left.get(i, 0)), required=str(right.get(i, 0)))
        need(failures, "the alternative restriction must invalidate this split")
        result.append(dict(restriction=prior["role"], split=split["role"], failures=failures))
    return result


def verify():
    counts = Counter()
    controls = set()
    # The frame table belongs to the parent graph. All edits use its chart IDs.
    dims = list(map(len, read(HERE / "data/BASE-GRAPH.json.gz")["frames"]))
    paid, targets = Counter(), Counter()
    def rank(a, b):
        return abs(dims[a] - dims[b])
    def audit(net, edit):
        kind = edit["event"]
        counts[kind] += 1
        record_job_changes(net, edit, rank, paid, targets)
        if kind not in ("split", "restrict"):
            return
        order = net.schedule()
        if kind == "restrict":
            source = entrance_form(net, order, coefficients(edit["source"]))
            need(source.get(edit["role"]), "the surrendered input has no effect on the constraint")
            for bank in edit["banks"]:
                row = coefficients(bank["relation"])
                survived = entrance_form(net, order, row)
                need(survived == source, "false receiver restriction")
                counts["receiver_equations"] += 1
                if edit["direction"] not in controls:
                    row[bank["remove"]] += 1
                    need(entrance_form(net, order, row) != source, "altered restriction accepted")
                    controls.add(edit["direction"])
            return
        source = coefficients(edit["source_covector"])
        steering = coefficients(edit["source_direction"])
        decoder = coefficients(edit["return_covector"])
        response = coefficients(edit["return_direction"])
        readout = coefficients(edit["readout"])
        calibration = coefficients(edit["calibration"])
        pulse = coefficients(edit["pulse"])
        for k in pulse:
            need(k in net.moves or net.first_output <= k < net.first_output + len(net.final),
                 "pulse must reach a paid instruction or a terminal")
            chart = net.moves[k][0] if k in net.moves else net.final[k - net.first_output]
            need(chart == edit["split_chart"], "pulse at the wrong source chart")
        need(entrance_form(net, order, readout) == source, "split readout")
        old_outputs = {net.first_output + i: v for i, v in decoder.items()}
        need(entrance_form(net, order, old_outputs) == entrance_form(net, order, calibration),
             "split calibration and decoder")
        effect = pulse_response(net, order, pulse)
        terminal = {k - net.first_output: v for k, v in effect.items() if k >= net.first_output}
        need(terminal == response, "split output response")
        input_effect = pulse_response(net, order, {k: sum(v * steering.get(~j, 0) for j, v in row.items() if j < 0)
                                                    for k, row in net.forms.items()})
        need({k - net.first_output: v for k, v in input_effect.items() if k >= net.first_output} == response,
             "source and pulse must give the same output direction")
        need(dot(source, steering) != 0 and dot(decoder, response) != 0 and
             dot(readout, effect) == dot(calibration, effect) == 0, "causal split")
        key = next(iter(pulse))
        pulse[key] += 1
        wrong = pulse_response(net, order, pulse)
        need(any(wrong.get(net.first_output + i, 0) != response.get(i, 0) for i in range(len(net.initial))),
             "altered pulse accepted")
        counts["rejected_pulse_mutations"] += 1
        controls.add("pulse")
    graph, layout, net = build(audit)
    need(controls == {"forward", "transpose", "pulse"}, "checked fault controls")
    parent = read(HERE / "data/QUOTIENT-APPLICATION.json")["invoice"]
    candidate = read(HERE / "results/application.json")["invoice"]
    for side, delta in (("paid", paid), ("targets", targets)):
        before = Counter({int(k): v for k, v in parent[side].items()})
        before.update({grade: 16 * change for grade, change in delta.items()})
        need({str(k): v for k, v in before.items() if v} == candidate[side], "journal invoice for " + side)
    journal = read(HERE / "EDITS.json")
    return dict(events=dict(counts), graph_sha256=digest(graph), reverse=reverse_columns(net, layout),
                native_change_from_7713=dict(paid=dict(sorted(paid.items())), targets=dict(sorted(targets.items()))),
                alternate_restrictions=alternate_restrictions(journal), rejected=sorted(controls),
                chronological_edits=len(journal))


if __name__ == "__main__":
    result = verify()
    receipt("witness", result)
    print("PASS_INTERLEAVED_WITNESSES", result["chronological_edits"], result["reverse"]["columns"])
