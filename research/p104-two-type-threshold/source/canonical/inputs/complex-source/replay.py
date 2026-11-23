"""Rebuild seven chart splits, one new helper and three removed transfers. Use Python 3.10 or later."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from math import gcd, lcm
from pathlib import Path
import gzip
import json
import sys


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def expected(layout, count, grid):
    out = [{r: grid} for r in range(count)]
    hosted = layout["hosted"]
    for p, x in enumerate(layout["live"]):
        y = x + 112
        if p in hosted["Dports"]:
            out[y][x] = grid
        else:
            require(grid % 2 == 0, "odd main grid")
            out[x][y] = -grid
            out[y] = {x: grid // 2, y: grid // 2}
    for x, y in zip(hosted["X2"], hosted["Y2"], strict=True):
        out[x][y] = -grid
    return out


def verify_integer_grid(net, graph, layout):
    n = len(net.initial)
    divisors = {~r: 1 for r in range(n)}
    grid = 1
    peak_literal = 0
    for k in graph["schedule"]:
        row_grid = 1
        for j, q in net.forms[k].items():
            peak_literal = max(peak_literal, q.numerator.bit_length(), q.denominator.bit_length())
            row_grid = lcm(row_grid, divisors[j] * q.denominator)
        divisors[k] = row_grid
        grid = lcm(grid, row_grid)

    ends = expected(layout, n, grid)
    scalar = {~r: {r: grid} for r in range(n)}
    checked = Counter()
    common = grid
    for k in graph["schedule"]:
        row = {}
        for j, q in net.forms[k].items():
            for c, value in scalar[j].items():
                term, remainder = divmod(q.numerator * value, q.denominator)
                require(remainder == 0, f"inexact division at row {k}, donor {j}, column {c}")
                common = gcd(common, term)
                result = row.get(c, 0) + term
                if result:
                    row[c] = result
                else:
                    row.pop(c, None)
                checked[q.denominator] += 1
        if k in net.moves:
            scalar[k] = row
        else:
            require(row == ends[k-net.first_output], f"public output {k-net.first_output}")
    return dict(path_grid=grid, minimum_product_grid=grid // common, literal_peak_bits=peak_literal,
                products=sum(checked.values()), nontrivial_divisions=sum(checked.values())-checked[1],
                by_denominator=dict(sorted(checked.items())), public_rows=n)


def add(row, donor, factor):
    for index, value in donor.items():
        new = row.get(index, 0) + value * factor
        if new:
            row[index] = new
        else:
            row.pop(index, None)


def input_forms(net, labels):
    needed = set(labels)
    stack = list(needed)
    while stack:
        node = stack.pop()
        for donor in net.forms[node]:
            if donor >= 0 and donor not in needed:
                needed.add(donor)
                stack.append(donor)
    signals = {}
    for node in net.schedule():
        if node in needed:
            row = {}
            for donor, factor in net.forms[node].items():
                add(row, {donor: 1} if donor < 0 else signals[donor], factor)
            signals[node] = row
    return signals


def erase_return(net, event):
    from network import Network

    move = event["move"]
    calibration = event["calibration"]
    pivot = event["pivot"]
    receiver = event["receiver"]
    sender = event["sender"]
    initial = event["source"]
    first = net.first_output
    require(net.moves[move] == (sender, receiver), "erased move")
    require(net.moves[calibration][1] == sender, "calibration receipt")
    consumers = {k - first: row[move] for k, row in net.forms.items() if move in row}
    require(consumers == {int(k): Fraction(v) for k, v in event["responses"].items()},
            "erased consumers")
    require(all(net.initial[r] == initial and net.final[r] == receiver for r in consumers),
         "helper endpoints")
    form = input_forms(net, [calibration])[calibration]
    require(all(net.initial[~i] == initial for i in form), "one calibration source")
    pairing = sum(form.get(~r, 0) * value for r, value in consumers.items())
    require(pairing == 1, "calibration pairing")
    lift = {i: -q / pairing for i, q in form.items() if i != ~pivot}
    lift[~pivot] = 1 / pairing
    rows = {}
    for node, old in net.forms.items():
        if node == move:
            continue
        r = node - first
        if r == pivot:
            row = {calibration: 1}
        else:
            row = dict(old)
            if r in consumers:
                add(row, net.forms[first + pivot], -consumers[r] / consumers[pivot])
                require(move not in row, "erasure cancellation")
        factor = sum(row.get(~r, 0) * q for r, q in consumers.items())
        row.pop(~pivot, None)
        add(row, lift, factor)
        rows[node] = row
    moves = dict(net.moves)
    del moves[move]
    final = list(net.final)
    final[pivot] = sender
    return Network(first, list(net.initial), final, moves, rows)


def restrict_source(net, layout, event):
    from network import Network

    first = net.first_output
    pivot = event["pivot"]
    last = len(net.initial) - 1
    require(last == 1289 and net.initial[pivot] == event["initial"] and net.final[pivot] == event["final"],
         "old helper stock")
    first_leg, second_leg = (entry["move"] for entry in event["receipts"])
    require(net.moves[first_leg] == (event["initial"], event["via"]) and
            net.moves[second_leg] == (event["via"], event["final"]), "paid chain")
    local = {entry["move"]: {i: Fraction(q) for i, q in entry["donors"]}
             for entry in event["receipts"]}
    values = input_forms(net, set(local) | {i for row in local.values() for i in row})
    relations = {}
    for node, replacement in local.items():
        row = dict(values[node])
        for donor, amount in replacement.items():
            add(row, values[donor], -amount)
        relations[node] = row
    source = relations[first_leg]
    require(source == {j: Fraction(event["proportion"]) * value for j, value in relations[second_leg].items()},
         "proportional source relations")
    require(len(source) == event["support"] and all(net.initial[~j] == event["initial"] for j in source),
         "one source chart")
    divisor = source[~pivot]
    require(divisor == Fraction(event["pivot_coefficient"]), "source pivot")
    rewrites = dict(local)
    rewrites[~pivot] = {j: -v / divisor for j, v in source.items() if j != ~pivot}
    rows = {}
    for node, row in net.forms.items():
        if node in local or node == first + pivot:
            continue
        out = {j: v for j, v in row.items() if j not in rewrites}
        for donor in row.keys() & rewrites.keys():
            add(out, rewrites[donor], row[donor])
        if ~last in out:
            out[~pivot] = out.pop(~last)
        rows[first + pivot if node == first + last else node] = out

    def pack(sequence):
        result = list(sequence[:-1])
        result[pivot] = sequence[last]
        return result

    moves = {k: chart for k, chart in net.moves.items() if k not in local}
    require(layout["public"] == last + 1 and layout["source_labels"][last] == 1542,
         "public layout")
    updated = dict(layout, public=last, source_labels=pack(layout["source_labels"]))
    return Network(first, pack(net.initial), pack(net.final), moves, rows), updated


def replay(source, layout, journal, engines):
    require(sha256(encoded(source)).hexdigest() == journal["source"], "source word pin")
    require(sha256(encoded(layout)).hexdigest() == journal["layout"], "source layout pin")
    for name, digest in journal["semantic_modules"].items():
        require(sha256((engines / name).read_bytes()).hexdigest() == digest, name)
    sys.path[:0] = [str(engines), str(engines / "retained" / "vendor")]
    from network import Network
    from public_split import split
    from birth_event import apply_split

    net = Network(source["first_output"], source["initial"], source["final"],
                  {k: (a, b) for k, a, b in source["moves"]},
                  {k: {i: Fraction(v) for i, v in row} for k, row in source["forms"]})
    for e in journal["splits"]:
        net = split(net, e)
        net.schedule()
    e = journal["subdivide"]
    k, j, chart = e["move"], e["new"], e["through"]
    a, b = net.moves[k]
    require([a, b] == e["original"] and j not in net.moves, "carrier preimage")
    moves = dict(net.moves)
    forms = dict(net.forms)
    moves[j], moves[k] = (a, chart), (chart, b)
    forms[j], forms[k] = forms[k], {j: Fraction(1)}
    net = apply_split(Network(net.first_output, net.initial, net.final, moves, forms), journal["birth"])
    layout = dict(layout, public=len(net.initial),
                  source_labels=[*layout["source_labels"], journal["birth_source_label"]])
    net = erase_return(net, journal["erasure"])
    net, layout = restrict_source(net, layout, journal["quotient"])
    require(sha256(encoded(layout)).hexdigest() == journal["child_layout_sha256"], "child layout pin")
    graph = dict(first_output=net.first_output, initial=net.initial, final=net.final, frames=source["frames"],
                 moves=[[k, *pair] for k, pair in sorted(net.moves.items())],
                 forms=[[k, [[i, str(q)] for i, q in sorted(row.items())]] for k, row in sorted(net.forms.items())],
                 schedule=net.schedule())
    digest = sha256(encoded(graph)).hexdigest()
    require(digest == journal["canonical_sha256"], "child word pin")
    audit = verify_integer_grid(net, graph, layout)
    return graph, dict(word_sha256=digest, **audit)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--layout", required=True, type=Path)
    parser.add_argument("--engines", required=True, type=Path)
    parser.add_argument("--journal", type=Path, default=Path(__file__).with_name("EVENTS.json"))
    parser.add_argument("--write-word", type=Path)
    parser.add_argument("--write-audit", type=Path)
    args = parser.parse_args()
    require(sys.flags.optimize == 0, "the source engines use assertions")
    graph, audit = replay(read(args.source), read(args.layout), read(args.journal), args.engines)
    if args.write_word:
        args.write_word.write_bytes(gzip.compress(encoded(graph), mtime=0))
    if args.write_audit:
        args.write_audit.write_text(json.dumps(audit, sort_keys=True, indent=2)+"\n")
    print(json.dumps(audit, sort_keys=True))


if __name__ == "__main__":
    main()
