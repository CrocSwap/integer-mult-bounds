#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay exact rational paid projections with the pinned public #7776 helpers."""

import argparse
from collections import Counter
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha1, sha256
import json
from math import gcd, lcm
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ENGINE = Path("research/p104-dual-supplier-lift/complex")
ENGINE_HEAD = "4f7c67ae387cc91580f469aeda4d508b372b9ec1"
ENGINE_FILES = {
    "retained/vendor/network.py": (
        "a9169fd6ad0a13c69cf39bd32649d53256f6d6fa2ed2ceda854f848b64f4c546",
        "0ebc1925c40cc6c11af59e405221ea51801a6e92",
    ),
    "puncture.py": (
        "adee4c8212193854ada80ef385af1acf51486adb7def50566dcb7288b506934d",
        "5196457f5b5b72762f575e7f9e06e4e51c8771bd",
    ),
}
WORD = "03ef8f6cc9ebb7394b5c7f8da70d44df965659ae4ff361bbc8d32c7a12121445"
LAYOUT = "37c04b0a349c1b7f7ada22533d3e4e6bacb42e4c6549f4257f4cbcae189a0275"
CANDIDATE = "275fae189ec8869bae0b5d1daa59621792ac8e4d1605507ecc30c2008cd61cd1"


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def load(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw.startswith(b"\x1f\x8b") else raw)


def canonical(item):
    return json.dumps(item, sort_keys=True, separators=(",", ":")).encode()


def digest(item):
    return sha256(canonical(item)).hexdigest()


def engines(source_root):
    path = source_root.resolve() / ENGINE
    for relative, (expected, git_blob) in ENGINE_FILES.items():
        raw = (path / relative).read_bytes()
        payload = f"blob {len(raw)}\0".encode() + raw
        need((sha256(raw).hexdigest(), sha1(payload).hexdigest()) == (expected, git_blob),
             f"public engine {relative} from {ENGINE_HEAD}")
    sys.path[:0] = [str(path / "retained/vendor"), str(path)]
    import network
    import puncture

    need(Path(network.__file__).resolve() == path / "retained/vendor/network.py"
         and Path(puncture.__file__).resolve() == path / "puncture.py", "use verified module paths")
    return network, puncture


@cache
def span(axes):
    points = {0}
    for axis in axes:
        need(type(axis) is int and 0 < axis < 512 and axis not in points, "independent chart axes")
        points |= {current ^ axis for current in points}
    return frozenset(points)


def rank(frames, leg, productive=False):
    a, b = (span(tuple(frames[i])) for i in leg)
    need(a < b or (not productive and b < a), f"positive nested chart move {leg}")
    return abs(len(frames[leg[0]]) - len(frames[leg[1]]))


def encode(row):
    return [[t, str(q)] for t, q in sorted(row.items())]


def dump_graph(net, frames):
    return dict(
        frames=frames, initial=net.initial, final=net.final, first_output=net.first_output,
        moves=[[t, *leg] for t, leg in sorted(net.moves.items())],
        forms=[[t, encode(row)] for t, row in sorted(net.forms.items())],
        schedule=net.schedule(),
    )


def apply_projection(net, frames, entry, network, puncture):
    """Use V' = V - P g, quotient two vanishing observations, and restore P g."""
    orientation = entry["orientation"]
    need(orientation in ("forward", "transpose"), "projection orientation")
    oriented = net.transpose() if orientation == "transpose" else net
    order = oriented.schedule()
    source, receiver, terminal = entry["charts"]
    need(len({source, receiver, terminal}) == 3, "three distinct banks")
    g = network.coefficients(entry["source"])
    v = network.coefficients(entry["injection"])
    puncture.check_bank(oriented, g, source)
    need(v and all(t in oriented.moves and oriented.moves[t][0] == source for t in v),
         "source-local injection")
    need(len(entry["drops"]) == 2 and len(set(entry["drops"])) == 2,
         "distinct paid quotient pivots")
    pulse = puncture.pulse_response(oriented, order, v)
    g_in = puncture.entrance_form(oriented, order, g)
    need(g_in and puncture.dot(g, pulse) == 0, "nonzero source form invariant under pulse")
    substitution = {}
    for chart, token in zip((receiver, terminal), entry["drops"], strict=True):
        h = network.coefficients(entry["original_observation"][str(token)])
        need(token in h and token in oriented.moves and oriented.moves[token][1] == chart,
             "paid readout pivot at its declared bank")
        puncture.check_bank(oriented, h, chart)
        need(puncture.entrance_form(oriented, order, h) == g_in
             and puncture.dot(h, pulse) == 1, "common exact source and unit pulse observation")
        substitution[token] = {t: -q / h[token] for t, q in h.items() if t != token}
    need(all(substitution.keys().isdisjoint(row) for row in substitution.values()),
         "independent homogeneous substitutions")
    response = {t: q for t, q in pulse.items() if t >= net.first_output}
    need(response and response == network.coefficients(entry["terminal_repairs"])
         and all(oriented.final[t - net.first_output] == terminal for t in response),
         "complete exact terminal response on restoration chart")

    def quotient(row):
        for token, replacement in substitution.items():
            row = puncture.substitute(row, token, replacement)
        return row.copy()

    g_quotient = quotient(g)
    moves = {t: leg for t, leg in oriented.moves.items() if t not in substitution}
    forms = {t: quotient(row) for t, row in oriented.forms.items() if t not in substitution}
    for token, q in v.items():
        if token in forms:
            network.add_scaled(forms[token], g_quotient, -q)
    new = next(t for t in range(net.first_output) if t not in oriented.moves)
    leg = (source, terminal)
    new_rank = rank(frames, leg)
    need(entry["restoration_rank"] == new_rank, "declared paid restoration rank")
    moves[new], forms[new] = leg, g_quotient
    for token, q in response.items():
        network.add_scaled(forms[token], {new: q}, 1)
    candidate = network.Network(net.first_output, oriented.initial, oriented.final, moves, forms)
    candidate.schedule()

    omitted, response_coefficient = next(iter(sorted(response.items())))
    owner, source_coefficient = next(iter(sorted(g_in.items())))
    without = puncture.substitute(forms[omitted], new, {})
    lost = puncture.entrance_form(candidate, candidate.schedule(), without)
    old = puncture.entrance_form(oriented, order, {omitted: 1})
    network.add_scaled(lost, old, -1)
    need(lost == {column: -response_coefficient*q for column, q in g_in.items()},
         "omitting the restoration changes the prescribed terminal row")
    return (candidate.transpose() if orientation == "transpose" else candidate,
            dict(orientation=orientation, charts=entry["charts"], dropped=entry["drops"],
                 dropped_ranks=[rank(frames, oriented.moves[t]) for t in entry["drops"]],
                 added=[new, *leg, new_rank], terminal_support=len(response),
                 omission=dict(row=omitted, column=owner,
                               coefficient_difference=str(-response_coefficient*source_coefficient))))


def endpoints(net):
    """Value every terminal row over all independent columns using reduced integer rows."""
    values = {~r: (1, {r: 1}) for r in range(len(net.initial))}
    outputs = [{} for _ in net.final]
    for token in net.schedule():
        summands = []
        for donor, q in net.forms[token].items():
            denominator, coefficients = values[donor]
            if coefficients:
                summands.append((q.numerator, denominator*q.denominator, coefficients))
        denominator = lcm(*(d for _, d, _ in summands))
        row = {}
        for numerator, d, coefficients in summands:
            scale = numerator * (denominator // d)
            for column, coefficient in coefficients.items():
                row[column] = row.get(column, 0) + scale*coefficient
        row = {column: q for column, q in row.items() if q}
        if token in net.moves:
            common = gcd(denominator, *row.values())
            values[token] = denominator // common, {column: q // common for column, q in row.items()}
        else:
            outputs[token - net.first_output] = {column: Fraction(q, denominator) for column, q in row.items()}
    return outputs


def verify(source_root, word, layout_path, word_sha, layout_sha, journal, expected=None):
    graph, layout = load(word), load(layout_path)
    n = len(graph["initial"])
    need(digest(graph) == word_sha and digest(layout) == layout_sha, "canonical word and layout pins")
    need(n == len(graph["final"]) == layout["public"] == len(set(layout["source_labels"]))
         and graph["frames"] == layout["frames"], "complete caller layout and independent source owners")
    network, puncture = engines(source_root)
    frames = graph["frames"]
    original = network.Network(
        graph["first_output"], graph["initial"], graph["final"],
        {t: (a, b) for t, a, b in graph["moves"]},
        {t: network.coefficients(row) for t, row in graph["forms"]},
    )
    need(dump_graph(original, frames) == graph, "complete scheduled input graph")
    current, steps = original, []
    for entry in load(journal):
        current, step = apply_projection(current, frames, entry, network, puncture)
        steps.append(step)
    changed = dump_graph(current, frames)
    result_sha = digest(changed)
    if expected is None and (word_sha, layout_sha) == (WORD, LAYOUT) and journal == HERE / "PROJECTIONS.json":
        expected = CANDIDATE
    need(expected is None or result_sha == expected, "bound canonical result")
    need(len(original.moves) - len(current.moves) == len(steps)
         and all(changed[key] == graph[key] for key in ("first_output", "initial", "final", "frames")),
         "one paid removal per projection and all boundaries preserved")
    bits = max(max(abs(q.numerator).bit_length(), q.denominator.bit_length())
               for t, row in current.forms.items() if original.forms.get(t) != row for q in row.values())
    need(bits <= 24, "changed coefficient width")
    need(endpoints(original) == endpoints(current), "all exact forward endpoint rows")
    need(endpoints(original.transpose()) == endpoints(current.transpose()), "all exact adjoint endpoint rows")
    h = layout["hosted"]
    main = set(layout["live"]) | {t + 112 for t in layout["live"]} | set(h["X2"]) | set(h["Y2"])
    need(len(main) == 400, "retained main inventory")
    def inventory(net):
        paid = Counter(rank(frames, leg) for leg in net.moves.values())
        targets = Counter(rank(frames, (a, b), productive=True)
                          for i, (a, b) in enumerate(zip(net.initial, net.final, strict=True)) if i not in main)
        return dict(paid=dict(paid), targets=dict(targets))
    receipt = dict(source_sha256=word_sha, child_sha256=result_sha, layout_sha256=layout_sha,
                   cached_source_head=ENGINE_HEAD, steps=steps, all_forward_and_adjoint_rows_each=n,
                   changed_scalar_bits=bits, source_native_inventory=inventory(original),
                   child_native_inventory=inventory(current))
    return changed, layout, receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source-root", "word", "layout", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--word-sha", default=WORD)
    parser.add_argument("--layout-sha", default=LAYOUT)
    parser.add_argument("--expected")
    parser.add_argument("--journal", type=Path, default=HERE / "PROJECTIONS.json")
    args = parser.parse_args()
    graph, layout, receipt = verify(args.source_root, args.word, args.layout, args.word_sha,
                                    args.layout_sha, args.journal, args.expected)
    args.out.mkdir(parents=True, exist_ok=True)
    for name, value in (("WORD.json.gz", graph), ("LAYOUT.json.gz", layout)):
        (args.out / name).write_bytes(gzip.compress(canonical(value), mtime=0))
    (args.out / "PROJECTIONS-REPLAY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("PASS", receipt["child_sha256"], receipt["all_forward_and_adjoint_rows_each"])
