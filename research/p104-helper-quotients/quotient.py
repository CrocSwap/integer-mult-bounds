"""Rebuild the parent, impose the supplied relations, and remove the private coordinates."""
from fractions import Fraction
from hashlib import sha1, sha256
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))
from network import Network, add_scaled, encoded, main_roles, need, read
import construct
import recoding

PARENT = "db10e4ca7154b454f86bf404bc34b3a16d02de6cc008d5227e4eef2654cb0778"


def parent():
    for item in read(HERE / "SOURCE-PINS.json"):
        data = (HERE / item["path"]).read_bytes()
        blob = f"blob {len(data)}\0".encode() + data
        need(sha256(data).hexdigest() == item["sha256"] and sha1(blob).hexdigest() == item["git_blob"],
             "source identity " + item["path"])
    word = read(HERE / "data/WORD.json.gz")
    certs = read(HERE / "data/CERTS.json")
    raw, clears, moves = construct.raw_fold(word, certs["clear_event_index"])
    relay, proof = construct.contract(raw, word["frames"], clears, moves)
    frozen = construct.serialized(relay, word["frames"], "candidate",
                                  source_banked_graph_sha256=construct.PARENT, paid_relay=proof)
    need(sha256(frozen).hexdigest() == construct.CHILD, "role-1256 graph")
    net = Network(relay.first, relay.initial, relay.final, relay.moves, relay.forms)
    net = recoding.apply(net, read(HERE / "data/PARENT-CUTS.json"), word["frames"])
    need(digest(recoding.layout(word, net)) == PARENT, "exact parent graph")
    return word, net


def digest(value):
    return sha256(encoded(value)).hexdigest()


def sparse(items):
    row = {key: Fraction(text) for key, text in items}
    need(items == [[key, str(row[key])] for key in sorted(row)] and
         all(type(k) is int for k in row) and all(row.values()), "canonical sparse relation")
    return row


def substitute(forms, key, relation):
    """Solve a homogeneous relation for one bank and replace every read of it."""
    need(key in relation, "missing pivot in relation")
    scale = -1 / relation[key]
    replacement = {i: scale * v for i, v in relation.items() if i != key}
    result = {}
    for j, row in forms.items():
        if j == key:
            continue
        if key not in row:
            result[j] = row
            continue
        residual = dict(row)
        add_scaled(residual, replacement, residual.pop(key))
        result[j] = residual
    return result


def restrict(net, edit, mains, retired, observer=None):
    need(edit["direction"] in ("forward", "transpose"), "certificate direction")
    is_transpose = edit["direction"] == "transpose"
    before = net.transpose() if is_transpose else net
    r = edit["role"]
    forms, moves = before.forms, dict(before.moves)
    n = len(before.initial)
    need(0 <= r < n and r not in retired | mains and before.initial[r] != before.final[r],
         "retired coordinate must be a positive helper")
    entrance = {~i: v for i, v in sparse(edit["entrance"]).items()}
    need(~r in entrance and all(0 <= ~i < n and ~i not in retired and
         before.initial[~i] == before.initial[r] for i in entrance), "helper entrance chart")
    local = []
    for bank in edit["banks"]:
        key, chart = bank["remove"], bank["chart"]
        need(key in moves and moves[key][1] == chart, "receiver chart of removed bank")
        relation = sparse(bank["relation"])
        recoding.check_bank(before, relation, chart)
        need(key in relation, "missing paid pivot")
        local.append((key, chart, relation))
    need(len(local) >= 2 and len(local) == len({c for _, c, _ in local}), "distinct receiver charts")
    if observer:
        observer(before, entrance, local)
    forms = substitute(forms, ~r, entrance)
    for key, _, relation in local:
        forms = substitute(forms, key, relation)
        del moves[key]
    # Keep the label for later witnesses. The final circuit omits this row and column.
    final = list(before.final)
    final[r] = before.initial[r]
    forms[before.first_output + r] = {~r: Fraction(1)}
    after = Network(before.first_output, before.initial, final, moves, forms)
    after.schedule()
    return after.transpose() if is_transpose else after


def compact(net, word, retired):
    keep = [r for r in range(len(net.initial)) if r not in retired]
    index = {old: new for new, old in enumerate(keep)}
    need(main_roles(word) <= index.keys(), "every main must survive")
    need(all(index[x + 112] == index[x] + 112 for x in word["live"]), "first-plane partners")
    for r in retired:
        need(net.initial[r] == net.final[r] and net.forms[net.first_output + r] == {~r: 1},
             "isolated retired terminal")
    forms = {}
    for key, row in net.forms.items():
        if key >= net.first_output:
            public = key - net.first_output
            if public in retired:
                continue
            key = net.first_output + index[public]
        need(all(d >= 0 or ~d in index for d in row), "a retired entrance still has a reader")
        forms[key] = {d if d >= 0 else ~index[~d]: v for d, v in row.items()}
    compacted = Network(net.first_output, [net.initial[r] for r in keep],
                        [net.final[r] for r in keep], net.moves, forms)
    compacted.schedule()
    hosted = dict(word["hosted"])
    for key in ("X2", "Y2"):
        hosted[key] = [index[r] for r in hosted[key]]
    layout = dict(public=len(keep), live=[index[r] for r in word["live"]], hosted=hosted,
                  frames=word["frames"], ports=word["ports"])
    return compacted, layout, keep


def construct_candidate(word, source, observer=None):
    net = source
    mains, retired = main_roles(word), set()
    for position, edit in enumerate(read(HERE / "QUOTIENTS.json")):
        def check(before, entrance, banks):
            if observer:
                observer(position, before, entrance, banks)
        net = restrict(net, edit, mains, retired, check if observer else None)
        retired.add(edit["role"])
    return compact(net, word, retired)


def receipt(name, result):
    need(json.loads(json.dumps(result)) == read(HERE / "results" / (name + ".json")),
         "receipt mismatch " + name)


if __name__ == "__main__":
    source_word, network = parent()
    candidate, metadata, _ = construct_candidate(source_word, network)
    sys.stdout.buffer.write(encoded(recoding.layout(metadata, candidate)))
