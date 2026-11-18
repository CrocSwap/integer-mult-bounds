"""Check each cut identity and compare all public columns in reverse order."""
from copy import deepcopy
from math import lcm
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recoding import HERE, Network, apply, coefficients, combine, construct, dot, need, read, receipt, sources
from native import evaluate, verify_pivot
from network import add_scaled


def identity(before, edit):
    if edit["kind"] == "pivot":
        verify_pivot(before, edit)
        return
    incoming = coefficients(edit["sender" if edit["kind"] == "feedback" else "group"])
    receiver = coefficients(edit["receiver"])
    j = edit["outgoing"]
    _, values, _, _ = evaluate(before, incoming.keys() | receiver.keys() | {j})
    predicted = combine(incoming, values)
    add_scaled(predicted, combine(receiver, values), 1)
    need(predicted == values[j], "saved hub signal")


def reverse_columns(net):
    order = net.schedule()[::-1]
    grid = {i: 1 for i in net.forms}
    grid.update({~i: 1 for i in range(len(net.initial))})
    for i in order:
        for donor, q in net.forms[i].items():
            grid[donor] = lcm(grid[donor], grid[i] * q.denominator)
    unit = lcm(*grid.values())
    sums = {i: {} for i in grid}
    for role in range(len(net.final)):
        sums[net.first_output + role] = {role: unit}
    products = 0
    for i in order:
        row = sums.pop(i)
        for donor, q in net.forms[i].items():
            output = sums[donor]
            for j, value in row.items():
                term, rem = divmod(q.numerator * value, q.denominator)
                need(rem == 0, "reverse pre-product division")
                result = output.get(j, 0) + term
                if result:
                    output[j] = result
                else:
                    output.pop(j, None)
            products += len(row)
    return sums, unit, products


def source_clears(word):
    entries = read(HERE / "data/CERTS.json")["clear_event_index"]
    raw, clears, _ = construct.raw_fold(word, entries)
    wanted = {i for clear in clears for row in (clear.left, clear.right) for i in row}
    raw_net = Network(raw.first, raw.initial, raw.final, raw.moves, raw.forms)
    _, values, _, _ = evaluate(raw_net, wanted)
    zeros = 0
    for clear in clears:
        left = combine(clear.left, values)
        need(left == combine(clear.right, values), f"source CLEAR at {clear.clock}")
        zeros += not left
    need((len(clears), zeros) == (235, 42), "all source retirements")
    return dict(total=len(clears), zero=zeros, nonzero=len(clears)-zeros)


def cut_record(index, net, edit, frames):
    def rank(a, b):
        return abs(len(frames[a]) - len(frames[b]))

    if edit["kind"] == "pivot":
        first, second = edit["remove"], edit["pivot"]
        source, middle = net.moves[first]
        _, target = net.moves[second]
        return dict(step=index + 1, kind="pivot", direction=edit["direction"], keys=[first, second],
                    old_ranks=[rank(source, middle), rank(middle, target)],
                    new_ranks=[rank(edit["source_chart"], target)])
    first, second, hub = edit["incoming"], edit["outgoing"], edit["hub"]
    source, middle = net.moves[first]
    _, target = net.moves[second]
    record = dict(step=index + 1, kind=edit["kind"], direction=edit["direction"], keys=[first, second],
                  charts=[source, middle, target, hub], old_ranks=[rank(source, middle), rank(middle, target)],
                  new_ranks=[rank(source, hub), rank(hub, target)])
    if edit["kind"] == "feedback":
        v = coefficients(edit["innovation"])
        response = dot(net.forms[second], v)
        side = coefficients(edit["receiver"])
        feedback = sum(weight * dot(net.forms[k], v) / response for k, weight in side.items() if k >= 0)
        record.update(determinant=str(1-feedback), prior_edge_to_hub=(middle, hub) in net.moves.values())
    return record


def check(shard):
    word, parent, edits = sources()
    checks = []
    mutated = set()

    def observe(i, net, edit):
        if i % 2 != shard:
            return
        identity(net, edit)
        checks.append(cut_record(i, net, edit, word["frames"]))
        if edit["kind"] not in mutated:
            altered = deepcopy(edit)
            field = "group" if edit["kind"] == "group" else "sender"
            if not altered[field]:
                return
            token, v = altered[field][0]
            altered[field][0] = [token, str(-coefficients([[token, v]])[token])]
            try:
                identity(net, altered)
            except ValueError as exc:
                need(str(exc) in ("saved hub signal", "saved signal identity"), "mutation rejection")
                mutated.add(edit["kind"])
            else:
                raise ValueError("wrong signal sign accepted")

    net = apply(parent, edits, word["frames"], observe)
    need(mutated == {row["kind"] for row in checks}, "signal mutation coverage")
    result = dict(checks=checks, rejected_signs=sorted(mutated))
    if shard == 0:
        old, a, old_work = reverse_columns(parent)
        new, b, new_work = reverse_columns(net)
        need(old.keys() == new.keys() == {~i for i in range(len(net.initial))}, "reverse owners")
        for i, row in old.items():
            need(row.keys() == new[i].keys() and all(v*b == new[i][j]*a for j,v in row.items()),
                 f"reverse public column {~i}")
        result["reverse"] = dict(columns=len(old), parent_grid=a, final_grid=b,
                                 parent_products=old_work, final_products=new_work)
    else:
        result["raw_clears"] = source_clears(word)
    return result


if __name__ == "__main__":
    shard = int(sys.argv[1])
    need(sys.flags.optimize == 0 and shard in (0, 1), "witness slice")
    result = check(shard)
    receipt(f"witness-{shard}", result)
    print("PASS_CUT_IDENTITIES", shard, len(result["checks"]), result["rejected_signs"])
