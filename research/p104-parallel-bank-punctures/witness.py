"""Check each scalar identity, the cost of its transfers, and the full transposed map."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from construction import (HERE, build, digest, grouped_puncture, main_roles, need,
                          paid_split, puncture, read, receipt, relay)
from linear import dot, entrance_form, pulse_response, reverse_columns
from network import add_scaled, coefficients


def coupled_example(net, event):
    """Recover each receiver's observable plane directly from all its entrance forms."""
    lanes = {lane["remove"]: lane for lane in event["lanes"]}
    pivots = (101324, 99605)
    order = net.schedule()
    sources = [coefficients(lanes[k]["old_source_form"]) for k in pivots]
    pulses = [pulse_response(net, order, coefficients(lanes[k]["receive_direction"])) for k in pivots]
    result = []
    for chart, expected in ((144, (1, 0, "-1/2", "-1/2")), (177, (0, 1, "-1/2", "1/2"))):
        banks = [~r for r, a in enumerate(net.initial) if a == chart]
        banks.extend(k for k, (_, b) in net.moves.items() if b == chart)
        # Each column of this linear system is a local bank or a negative source equation.
        columns = [entrance_form(net, order, {k: Fraction(1)}) for k in banks]
        columns += [{j: -q for j, q in row.items()} for row in sources]
        basis, relations = {}, []
        for i, column in enumerate(columns):
            row, relation = column.copy(), {i: Fraction(1)}
            while row:
                j = max(row)
                factor = row[j]
                if j not in basis:
                    basis[j] = ({k: v/factor for k, v in row.items()},
                                {k: v/factor for k, v in relation.items()})
                    break
                saved, expression = basis[j]
                add_scaled(row, saved, -factor)
                add_scaled(relation, expression, -factor)
            else:
                local = {k: relation[i] for i, k in enumerate(banks) if i in relation}
                source = [relation.get(len(banks) + i, 0) for i in range(2)]
                observed = [dot(local, pulse) for pulse in pulses]
                values = source + observed
                if any(values):
                    first = next(v for v in values if v)
                    relations.append(tuple(Fraction(v, first) for v in values))
        want = tuple(map(Fraction, expected))
        need(set(relations) == {want}, "complete local observation and two impulse responses")
        affected = [(r, [pulse.get(net.first_output + r, 0) for pulse in pulses])
                    for r, b in enumerate(net.final) if b == chart and
                    any(pulse.get(net.first_output + r) for pulse in pulses)]
        need(len(affected) == 1 and affected[0][1][0] and affected[0][1][1],
             "both impulses reach the surviving receiver")
        r, response = affected[0]
        need(response[0] * want[3] == response[1] * want[2], "jointly repairable response")
        result.append(dict(chart=chart, banks=len(banks), public_terminal=r,
                           available_source_and_pulse=[str(q) for q in want],
                           terminal_response=[str(q) for q in response]))
    return dict(pivots=list(pivots), receivers=result)


def verify():
    layout = read(HERE / "data/BASE-INTERFACE.json")
    base = read(HERE / "data/BASE-GRAPH.json.gz")
    mains = main_roles(layout)
    ranks = list(map(len, base["frames"]))

    def grade(a, b):
        return abs(ranks[a] - ranks[b])

    def owners(entrances, exits):
        return Counter(grade(a, b) for i, (a, b) in enumerate(zip(entrances, exits, strict=True))
                       if i not in mains)

    paid = Counter(grade(a, b) for _, a, b in base["moves"])
    targets = owners(base["initial"], base["final"])
    record, faults, coupled = [], {}, {}

    def inspect(index, net, event):
        kind = event["type"]
        delta, credit = Counter(), Counter()
        if kind == "parallel_relay":
            key, lead = event["remove"], event["pivot"]
            delta[grade(*net.moves[key])] -= 1
            delta[grade(*net.moves[lead])] -= 1
            delta[grade(event["source_chart"], net.moves[lead][1])] += 1
        elif kind == "paid_side_split":
            a, b, c, sender, z = (event[j] for j in ("A", "B", "D", "E", "Z"))
            delta[grade(sender, b)] += 1
            credit[grade(a, z)] -= 1
            credit.update((grade(a, b), grade(c, z)))
        else:
            for lane in event["lanes"] if kind == "grouped_puncture" else [event]:
                k, r = lane["remove"], lane["role"]
                delta[grade(*net.moves[k])] -= 1
                old = net.final[r]
                credit[grade(net.initial[r], old)] -= 1
                credit[grade(net.moves[k][1], lane.get("return_chart", old))] += 1
        paid.update(delta)
        targets.update(credit)
        record.append(dict(step=index + 1, operation=kind, paid=sorted(delta.items()),
                           productive=sorted(credit.items())))
        if kind == "grouped_puncture" and {101324, 99605} <= {v["remove"] for v in event["lanes"]}:
            coupled.update(coupled_example(net, event))
        if kind in faults:
            return
        bad = deepcopy(event)
        if kind == "parallel_relay":
            fn, reason = relay, "relay observation at both charts"
            bad["sender"][0][1] = str(2 * Fraction(bad["sender"][0][1]))
        elif kind == "paid_side_split":
            fn, reason = paid_split, "split terminal response"
            bad["inj"] = []
        elif kind == "grouped_puncture":
            fn, reason = lambda n, e, v: grouped_puncture(n, e, mains, v), (
                "group return on the constrained source and every pulse")
            lane = bad["lanes"][0]
            lane["response"] = str(2 * Fraction(lane["response"]))
        else:
            fn, reason = puncture, "readout response"
            bad["response"] = str(2 * Fraction(bad["response"]))
        try:
            fn(net, bad, True)
        except ValueError as error:
            need(str(error) == reason, "wrong edit control rejection")
        else:
            raise ValueError("altered edit accepted")
        faults[kind] = dict(step=index + 1, reason=reason)

    graph, layout, net = build(verify=True, observer=inspect)
    need(coupled, "joint readout example")
    actual_paid = Counter(grade(a, b) for a, b in net.moves.values())
    actual_targets = owners(net.initial, net.final)
    need(paid == actual_paid and targets == actual_targets, "independent journal invoice")
    old_paid = Counter(grade(a, b) for _, a, b in base["moves"])
    old_targets = owners(base["initial"], base["final"])
    net_change = {r: actual_targets[r] - old_targets[r] - actual_paid[r] + old_paid[r]
                  for r in range(1, 10)}
    first_moment = sum(r * n for r, n in net_change.items())
    tails = [sum((r-k)*n for r, n in net_change.items() if r > k) for k in range(1, 9)]
    need(first_moment == 0 and all(value < 0 for value in tails), "strict concave native advantage")
    return dict(graph_sha256=digest(graph), edits=record, altered_controls=faults,
                productive_minus_paid_change=net_change, rank_mass_change=first_moment, tails=tails,
                paid=sorted(actual_paid.items()), productive=sorted(actual_targets.items()),
                coupled_example=coupled, reverse=reverse_columns(net, layout))


if __name__ == "__main__":
    result = verify()
    receipt("witness", result)
    print("PASS_PARALLEL_BANK_WITNESS", len(result["edits"]), result["reverse"]["columns"])
