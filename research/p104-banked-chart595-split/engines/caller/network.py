"""Construct the communication circuit and apply the rational pivots."""
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from graphlib import TopologicalSorter
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
PARENT = "ee251f6005d2a92b887c5b804bd7aac05989d278b2c9ccb3c3091b50d533b08d"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def source_word():
    for pin in read(HERE / "SOURCE-PINS.json"):
        raw = (HERE / pin["file"]).read_bytes()
        need(sha256(raw).hexdigest() == pin["sha256"], "source SHA-256")
        need(sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == pin["git_blob"], "source Git blob")
    base = read(HERE / "source/K372-2-WORD.json.gz")
    patch = read(HERE / "source/source-edits.json")
    need(sha256(encoded(base)).hexdigest() == patch["source"], "source edit origin")
    result = []
    cursor = 0
    for edit in patch["edits"]:
        start, stop = edit["start"], edit["stop"]
        need(cursor <= start <= stop <= len(base["program"]), "source edit range")
        need(base["program"][start:stop] == edit["before"], "source edit preimage")
        result.extend(base["program"][cursor:start])
        result.extend(edit["after"])
        cursor = stop
    result.extend(base["program"][cursor:])
    word = dict(base, program=result)
    need(sha256(encoded(word)).hexdigest() == patch["candidate"] == PARENT, "parent word")
    return word


def main_roles(word):
    h = word["hosted"]
    return set(word["live"]) | {i + 112 for i in word["live"]} | set(h["X2"]) | set(h["Y2"])


@cache
def rational(literal):
    return Fraction(literal)


def add_scaled(row, donor, factor):
    for index, value in donor.items():
        new = row.get(index, 0) + factor * value
        if new:
            row[index] = new
        else:
            row.pop(index, None)


@dataclass
class Network:
    first_output: int
    initial: list
    final: list
    moves: dict
    forms: dict

    def schedule(self):
        for node, form in self.forms.items():
            chart = self.moves[node][0] if node < self.first_output else self.final[node - self.first_output]
            for donor in form:
                if donor < 0:
                    need(0 <= ~donor < len(self.initial), "input owner")
                    donor_chart = self.initial[~donor]
                else:
                    need(donor in self.moves, "missing donor")
                    donor_chart = self.moves[donor][1]
                need(donor_chart == chart, "nonlocal scalar")
        need(set(self.forms) == self.moves.keys() | set(range(self.first_output, self.first_output + len(self.final))),
             "output inventory")
        dependencies = {node: sorted(i for i in self.forms[node] if i >= 0) for node in sorted(self.forms)}
        return list(TopologicalSorter(dependencies).static_order())

    def transpose(self):
        def reverse(node):
            if node < 0:
                return self.first_output + ~node
            if node >= self.first_output:
                return ~(node - self.first_output)
            return node

        edges = {k: {} for k in self.moves}
        edges.update({self.first_output + r: {} for r in range(len(self.initial))})
        for node, form in self.forms.items():
            for donor, coefficient in form.items():
                edges[reverse(donor)][reverse(node)] = coefficient
        moves = {k: (b, a) for k, (a, b) in self.moves.items()}
        return Network(self.first_output, self.final, self.initial, moves, edges)


def fold(word):
    n = word["public"]
    rows = [{~r: 1} for r in range(n)] + [None] * word["owned_fields"]
    charts = word["initial"][:] + [None] * word["owned_fields"]
    forms, moves = {}, {}
    for clock, event in enumerate(word["program"]):
        op, r = event[:2]
        if op == "INIT":
            need(r >= n and rows[r] is None, "private birth")
            rows[r], charts[r] = {}, event[2]
            continue
        need(rows[r] is not None, "inactive register")
        if op == "MOVE":
            _, _, a, b, owned = event
            need(charts[r] == a and owned == (r >= n), "original transfer")
            moves[clock], forms[clock] = (a, b), rows[r]
            rows[r], charts[r] = {clock: 1}, b
        else:
            need(charts[r] == event[-1], "original scalar chart")
            if op == "CLEAR":
                need(r >= n, "public retirement")
                rows[r], charts[r] = None, None
            elif op == "SCALE":
                rows[r] = {k: v * rational(event[2]) for k, v in rows[r].items()}
            else:
                need(op == "ADD" and event[2] != r and charts[event[2]] == charts[r], "original donor")
                add_scaled(rows[r], rows[event[2]], rational(event[3]))
    need(charts[:n] == word["final"] and all(f is None for f in charts[n:]), "original exit")
    first = len(word["program"])
    forms.update({first + r: rows[r] for r in range(n)})
    return Network(first, word["initial"], word["final"], moves, forms)


def coefficients(entries):
    result = {k: rational(v) for k, v in entries}
    need(len(entries) == len(result) and all(result.values()), "sparse coefficient list")
    return result


def pivot(net, edit):
    drop, lead = edit["remove"], edit["pivot"]
    combination = coefficients(edit["combination"])
    sender = coefficients(edit["sender"])
    side = coefficients(edit["receiver"])
    need(lead in combination and drop in net.moves and lead in net.moves, "pivot slots")
    _, middle = net.moves[drop]
    old, destination = net.moves[lead]
    uses = {m: row[drop] for m, row in net.forms.items() if drop in row}
    need(old == middle and combination.keys() <= uses.keys(), "pivot combination")
    need(all(net.moves.get(m) == (middle, destination) for m in uses), "shared destination")
    aggregate = {}
    for m, weight in combination.items():
        add_scaled(aggregate, net.forms[m], weight)
    response = aggregate.get(drop, 0)
    need(response, "zero pivot response")

    forms = net.forms.copy()
    del forms[drop]
    forms[lead] = sender
    for m, weight in uses.items():
        if m != lead:
            residual = net.forms[m].copy()
            add_scaled(residual, aggregate, -Fraction(weight, response))
            need(drop not in residual, "uncancelled transfer")
            forms[m] = residual

    combined = {lead: 1}
    add_scaled(combined, side, -1)
    recovered = {}
    for m, weight in uses.items():
        if m == lead:
            row = {k: -v / combination[lead] for k, v in combination.items() if k != lead}
        else:
            row = {m: 1}
        add_scaled(row, combined, Fraction(weight, response))
        recovered[m] = row
    for k, row in list(forms.items()):
        affected = row.keys() & recovered.keys()
        if affected:
            new = {i: v for i, v in row.items() if i not in affected}
            for i in affected:
                add_scaled(new, recovered[i], row[i])
            forms[k] = new
    moves = net.moves.copy()
    del moves[drop]
    moves[lead] = (edit["source_chart"], destination)
    return Network(net.first_output, net.initial, net.final, moves, forms)


def networks(word):
    parent = fold(word)
    net = parent
    receipts = []
    for edit in read(HERE / "PIVOTS.json"):
        direction = edit["direction"]
        need(direction in ("forward", "transpose"), "pivot direction")
        if direction == "transpose":
            net = net.transpose()
        before = len(net.moves)
        net = pivot(net, edit)
        if direction == "transpose":
            net = net.transpose()
        net.schedule()
        need(len(net.moves) == before - 1, "paid slot count")
        receipts.append([direction, edit["remove"], edit["pivot"], len(net.moves)])
    return parent, net, receipts
