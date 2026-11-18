"""Construct the compact P104 network from its published parent and an edit journal."""
from fractions import Fraction
from functools import cache
from hashlib import sha256
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE / "vendor")]
from network import Network, add_scaled, coefficients, encoded, main_roles, need, pivot, read
from recoding import check_bank, hub, layout as serialize
from split import apply_split

BASE_HASH = "16e99893a2c669467ce74f214e8eb5150402f0267aaa8d67aad5d870aa4d5c18"


def digest(value):
    return sha256(encoded(value)).hexdigest()


def receipt(name, value):
    need(json.loads(json.dumps(value)) == read(HERE / "results" / (name + ".json")),
         "receipt mismatch for " + name)


def source():
    graph = read(HERE / "data/BASE-GRAPH.json.gz")
    interface = read(HERE / "data/BASE-INTERFACE.json")
    keep, first = interface["keep"], graph["first_output"]
    need(digest(graph) == BASE_HASH and len(keep) == len(set(keep)) == 1468, "PR 7713 graph")
    need(keep == sorted(keep) and keep[0] >= 0 and keep[-1] < 1501, "stable parent labels")
    # The published source uses compact labels. Restore the old labels for the edit journal.
    initial, final = [3] * 1501, [3] * 1501
    for i, old in enumerate(keep):
        initial[old], final[old] = graph["initial"][i], graph["final"][i]
    forms = {first + r: {~r: Fraction(1)} for r in set(range(1501)) - set(keep)}
    for key, row in graph["forms"]:
        node = key if key < first else first + keep[key - first]
        forms[node] = {j if j >= 0 else ~keep[~j]: value for j, value in coefficients(row).items()}
    moves = {k: (a, b) for k, a, b in graph["moves"]}
    live = [keep[i] for i in interface["live"]]
    hosted = dict(interface["hosted"])
    for axis in ("X2", "Y2"):
        hosted[axis] = [keep[i] for i in hosted[axis]]
    frames = graph["frames"]
    ports = [frames[initial[i]][0] for i in live]
    old_layout = dict(frames=frames, ports=ports, live=live, hosted=hosted)
    net = Network(first, initial, final, moves, forms)
    need(main_roles(old_layout) == {keep[i] for i in interface["main_roles"]}, "all original main labels")
    return net, old_layout


def restrict(net, edit):
    """Solve the entrance and receiver equations, then remove their pivots."""
    role = edit["role"]
    forms, moves = net.forms, dict(net.moves)
    need(net.initial[role] != net.final[role], "active helper")
    equations = [(~role, net.initial[role], coefficients(edit["source"]))]
    for bank in edit["banks"]:
        key, chart = bank["remove"], bank["chart"]
        need(moves[key][1] == chart, "receiver chart")
        equations.append((key, chart, coefficients(bank["relation"])))
    for key, chart, row in equations:
        check_bank(net, row, chart)
        scale = -1 / row[key]
        replacement = {k: scale * v for k, v in row.items() if k != key}
        updated = {}
        for node, form in forms.items():
            if node == key:
                continue
            if key in form:
                form = dict(form)
                add_scaled(form, replacement, form.pop(key))
            updated[node] = form
        forms = updated
        if key >= 0:
            del moves[key]
    final = list(net.final)
    final[role] = net.initial[role]
    forms[net.first_output + role] = {~role: Fraction(1)}
    return Network(net.first_output, net.initial, final, moves, forms)


def compact(net, template):
    first = net.first_output
    mains = main_roles(template)
    live = {r for r, (a, b) in enumerate(zip(net.initial, net.final, strict=True)) if a != b or r in mains}
    # Keep each first-plane pair exactly 112 labels apart in the public interface.
    spare = sorted(r for r in live - mains if r >= 224)
    prefix = [r if r in live else spare.pop() for r in range(224)]
    keep = prefix + sorted(live - set(prefix))
    index = {old: new for new, old in enumerate(keep)}
    need(len(keep) == len(index) and set(index) == live, "one label per physical owner")
    forms = {}
    for key, row in net.forms.items():
        if key >= first and key - first not in live:
            need(row == {~(key - first): 1}, "isolated retired terminal")
            continue
        need(all(j >= 0 or ~j in index for j in row), "retired input has a reader")
        node = key if key < first else first + index[key - first]
        forms[node] = {j if j >= 0 else ~index[~j]: v for j, v in row.items()}
    new = Network(first, [net.initial[i] for i in keep], [net.final[i] for i in keep], net.moves, forms)
    hosted = dict(template["hosted"])
    for axis in ("X2", "Y2"):
        hosted[axis] = [index[r] for r in hosted[axis]]
    layout = dict(template, hosted=hosted, public=len(keep), live=[index[r] for r in template["live"]],
                  source_labels=keep)
    need(all(index[x + 112] == index[x] + 112 for x in template["live"]), "preserved main partners")
    return new, layout


def apply_edits(events, observer=None):
    net, template = source()
    mains = main_roles(template)
    orientation = "forward"
    for edit in events:
        side, kind = edit["direction"], edit["event"]
        need(side in ("forward", "transpose"), "edit orientation")
        if side != orientation:
            net = net.transpose()
            orientation = side
        if observer is not None:
            observer(net, edit)
        if kind in ("restrict", "split"):
            need(0 <= edit["role"] < len(net.initial) and edit["role"] not in mains, "helper owner")
        if kind == "restrict":
            net = restrict(net, edit)
        elif kind == "split":
            check_bank(net, coefficients(edit["readout"]), edit["split_chart"])
            check_bank(net, coefficients(edit["calibration"]), edit["split_chart"])
            net = apply_split(net, edit)
        elif kind == "pivot":
            check_bank(net, coefficients(edit["sender"]), edit["source_chart"])
            check_bank(net, coefficients(edit["receiver"]), net.moves[edit["pivot"]][1])
            net = pivot(net, edit)
        else:
            need(kind == "hub", "known graph edit")
            net = hub(net, edit)
    if orientation == "transpose":
        net = net.transpose()
    return net, template


@cache
def build(observer=None):
    net, layout = compact(*apply_edits(read(HERE / "EDITS.json"), observer))
    return serialize(layout, net), layout, net


if __name__ == "__main__":
    sys.stdout.buffer.write(encoded(build()[0]))
