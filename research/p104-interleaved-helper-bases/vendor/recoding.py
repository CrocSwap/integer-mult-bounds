"""Rebuild the exact source graph and apply the ordered rational cut certificate."""
from fractions import Fraction
from hashlib import sha1, sha256
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))
import construct
from network import Network, add_scaled, coefficients, encoded, need, pivot, read


def sources():
    for item in read(HERE / "SOURCE-PINS.json"):
        raw = (HERE / item["path"]).read_bytes()
        git_blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        need(sha256(raw).hexdigest() == item["sha256"] and
             sha1(git_blob).hexdigest() == item["git_blob"], f"source pin {item['path']}")
    word = read(HERE / "data/WORD.json.gz")
    certs = read(HERE / "data/CERTS.json")
    raw, clears, moves = construct.raw_fold(word, certs["clear_event_index"])
    graph, relay = construct.contract(raw, word["frames"], clears, moves)
    parent = construct.serialized(graph, word["frames"], "candidate",
                                  source_banked_graph_sha256=construct.PARENT, paid_relay=relay)
    need(sha256(parent).hexdigest() == construct.CHILD, "published role-1256 parent")
    net = Network(graph.first, graph.initial, graph.final, graph.moves, graph.forms)
    return word, net, read(HERE / "CUTS.json")


def combine(weights, forms):
    result = {}
    for token, weight in weights.items():
        add_scaled(result, forms[token], weight)
    return result


def check_bank(net, row, chart):
    for key in row:
        if key < 0:
            need(~key < len(net.initial) and net.initial[~key] == chart, "public bank chart")
        else:
            need(key in net.moves and net.moves[key][1] == chart, "paid bank chart")


def dot(row, direction):
    return sum(row[k] * direction[k] for k in row.keys() & direction.keys())


def hub(net, edit):
    t, j, hub_chart = edit["incoming"], edit["outgoing"], edit["hub"]
    source, middle = net.moves[t]
    start, target = net.moves[j]
    need(start == middle and len({source, middle, hub_chart, target}) >= 3
         and hub_chart not in (source, middle, target), "hub route")
    direction = coefficients(edit["innovation"])
    receiver = coefficients(edit["receiver"])
    group = {k for k, pair in net.moves.items() if pair == (source, middle)}
    need(direction.get(t) == 1 and direction.keys() <= group, "normalized cut direction")

    feedback = edit["kind"] == "feedback"
    if feedback:
        local = net.forms[j]
        sent = coefficients(edit["sender"])
    else:
        local = coefficients(edit["group"])
        need(local.keys() <= group, "local signal group")
        sent = combine(local, net.forms)
    check_bank(net, sent, source)
    check_bank(net, receiver, hub_chart)
    response = dot(local, direction)
    need(response != 0, "zero response")
    moves = dict(net.moves)
    moves[t], moves[j] = (source, hub_chart), (hub_chart, target)
    forms = dict(net.forms)
    forms[t] = sent
    for k, weight in direction.items():
        if k != t:
            forms[k] = dict(net.forms[k])
            add_scaled(forms[k], net.forms[t], -weight)

    # Remove the transmitted direction from each row at its old receiver.
    corrections = {}
    for k, row in net.forms.items():
        if k in (t, j) or row.keys().isdisjoint(direction):
            continue
        ratio = Fraction(dot(row, direction), response)
        if ratio:
            need(net.moves.get(k) == (middle, hub_chart), "lost receiver component")
            corrections[k] = ratio
        residual = dict(row)
        add_scaled(residual, local, -ratio)
        need(dot(residual, direction) == 0, "cut did not cancel")
        residual.pop(t, None)
        forms[k] = residual

    if feedback:
        determinant = 1 - dot(receiver, corrections)
        need(determinant != 0, "singular receiver recovery")
        recovered = {k: weight / determinant for k, weight in receiver.items()}
        add_scaled(recovered, {t: 1}, Fraction(1, determinant))
    else:
        recovered = {t: 1}
        forms[j] = dict(receiver)
        add_scaled(forms[j], recovered, 1)
    for k, row in list(forms.items()):
        if feedback and k == j:
            continue
        factor = dot(row, corrections)
        if factor:
            forms[k] = dict(row)
            add_scaled(forms[k], recovered, factor)
    if feedback:
        forms[j] = recovered
    return Network(net.first_output, net.initial, net.final, moves, forms)


def apply(net, edits, frames, observer=None):
    spans = [construct.span(basis) for basis in frames]
    for i, edit in enumerate(edits):
        need(edit["direction"] in ("forward", "transpose")
             and edit["kind"] in ("pivot", "group", "feedback"), "cut type")
        dual = edit["direction"] == "transpose"
        before = net.transpose() if dual else net
        if edit["kind"] == "pivot":
            check_bank(before, coefficients(edit["sender"]), edit["source_chart"])
            check_bank(before, coefficients(edit["receiver"]), before.moves[edit["pivot"]][1])
        if observer:
            observer(i, before, edit)
        after = pivot(before, edit) if edit["kind"] == "pivot" else hub(before, edit)
        changed = [edit["pivot"]] if edit["kind"] == "pivot" else [edit["incoming"], edit["outgoing"]]
        for key in changed:
            a, b = after.moves[key]
            need(spans[a] < spans[b] or spans[b] < spans[a], "strictly nested cut transfer")
        after.schedule()
        net = after.transpose() if dual else after
    return net


def layout(word, net):
    return dict(frames=word["frames"], initial=net.initial, final=net.final,
                first_output=net.first_output, moves=[[k, *ab] for k, ab in sorted(net.moves.items())],
                forms=[[k, [[j, str(c)] for j, c in sorted(row.items())]]
                       for k, row in sorted(net.forms.items())], schedule=net.schedule())


def receipt(name, result):
    stored = read(HERE / "results" / (name + ".json"))
    need(json.loads(json.dumps(result)) == stored, "receipt mismatch: " + name)


if __name__ == "__main__":
    word, parent, cuts = sources()
    net = apply(parent, cuts, word["frames"])
    sys.stdout.buffer.write(encoded(layout(word, net)))
