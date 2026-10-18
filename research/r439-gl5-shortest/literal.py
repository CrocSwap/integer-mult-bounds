#!/usr/bin/env python3
"""Literal COPY/ADD/ERASE interpreter, retained from PR1122 for independent replay.

Set-valued streams and source-binding patterns follow PR926/967/980.
Gareth Davidson (@bitplane), with substantial OpenAI Codex assistance.
Apache-2.0. No assertion is needed for rejection in this verifier.
"""
import argparse
import ast
import copy
from pathlib import Path
import runpy
import tempfile

C = runpy.run_path(str(Path(__file__).with_name("common.py")))
need, same, load = C["need"], C["same"], C["load"]


def instructions(word):
    n = 2 * word["v"] + word["R"]
    out = []
    for phase in ("D", "A", "scatter", "B", "C"):
        if phase == "scatter":
            for j, center in enumerate(word["ret"]):
                out.append(("copy", n, center))
                for i, uses in enumerate(word["scatter"]):
                    if j in uses:
                        out.append(("add", word["v"] + i, n))
                out.append(("erase", n, center))
        else:
            for frame, d, donors in word[phase]:
                need(type(frame) is int and 0 <= frame < len(word["frames"]), "frame domain")
                need(type(d) is int and 0 <= d < n, "destination domain")
                need(type(donors) is list and len(set(donors)) == len(donors), "distinct donors")
                need(all(type(s) is int and 0 <= s < n and s != d for s in donors), "donor domain")
                out.extend(("add", d, s) for s in donors)
    return out


def execute(word, reverse=False, stream=None):
    """Sets of formal columns plus integer positive bounds; COPY work starts empty."""
    n = 2 * word["v"] + word["R"]
    symbolic = [{i} for i in range(n)] + [set()]
    positive = [1] * n + [0]
    stream = instructions(word) if stream is None else stream
    opened, peak, adds, copies, erasures = False, 1, 0, 0, 0
    for kind, d, s in reversed(stream) if reverse else stream:
        if reverse and kind != "add":
            kind = "erase" if kind == "copy" else "copy"
        if kind == "add":
            need(d < n, "private COPY target cannot be ADD destination")
            need(s != n or opened, "private COPY read outside lifetime")
            symbolic[d].symmetric_difference_update(symbolic[s])
            positive[d] += positive[s]
            adds += 1
        elif kind == "copy":
            need(d == n and not opened and not symbolic[n] and positive[n] == 0, "COPY destination not empty")
            symbolic[n] = set(symbolic[s])
            positive[n] = positive[s]
            opened = True
            copies += 1
        elif kind == "erase":
            need(d == n and opened and symbolic[n] == symbolic[s], "ERASE original changed or missing COPY")
            symbolic[n] = set()
            positive[n] = 0
            opened = False
            erasures += 1
        else:
            raise ValueError("unknown instruction")
        peak = max(peak, positive[d])
    need(not opened and not symbolic[n] and positive[n] == 0, "unclosed private COPY")
    expected = [{i} for i in range(n)]
    for i in range(word["v"]):
        expected[word["v"] + i].add(i)
    need(symbolic[:-1] == expected, "dirty full-word boundary")
    need(copies == erasures == 9, "complete COPY bill")
    return dict(ADDs=adds, bound=peak, copies=copies, erasures=erasures,
                columns=n, instructions=len(stream))


def phase_rows(word, phase, reverse=False):
    n = 2 * word["v"] + word["R"]
    rows = [{i} for i in range(n)]
    for _, d, donors in reversed(word[phase]) if reverse else word[phase]:
        for s in donors:
            rows[d].symmetric_difference_update(rows[s])
    return rows


def literal_cleanup(word):
    fulls = [i for i, f in enumerate(word["frames"]) if sorted(f) == list(range(word["v"]))]
    need(len(fulls) == 1, "one full frame")
    reverse = []
    for phase in ("B", "A"):
        for gate in word[phase][::-1]:
            if not word["v"] <= gate[1] < 2 * word["v"]:
                reverse.append([fulls[0], gate[1], list(gate[2])])
    same(reverse, word["C"], "literal cleanup")


def literal_price(word):
    forward, reverse = execute(word), execute(word, True)
    same(forward["ADDs"], reverse["ADDs"], "reverse ADD bill")
    f, b = forward["bound"], reverse["bound"]
    local, nine = 2**6 * f * f * f * b * b, 2**18 * f**5 * b**4
    return dict(ADDs=forward["ADDs"], F=f, B=b, local_upper=str(local), nine_upper=str(nine),
                local_bits=local.bit_length(), nine_bits=nine.bit_length(),
                admitted=local < 2**104 and nine < 2**192)


def require_admission(price):
    need(int(price["local_upper"]) < 2**104, "local precision cap")
    need(int(price["nine_upper"]) < 2**192, "nine-stage precision cap")



def source_formula(root):
    name = ("research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/"
            "vendor/e8-r715-eleven-stage-whole/code/global_k.py")
    syntax = ast.parse((root / name).read_text())
    formulas = [node.value for node in ast.walk(syntax) if isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "prefix" for t in node.targets)]
    formula = ast.parse("(1 << nb) * cf ** (K + 1) * cb ** K", mode="eval").body
    need(len(formulas) == 1 and ast.dump(formulas[0]) == ast.dump(formula), "nine-stage formula binding")
    bridge = ast.parse("nb == 6 * (K - 1)", mode="eval").body
    need(any(isinstance(node, ast.Compare) and ast.dump(node) == ast.dump(bridge)
             for node in ast.walk(syntax)), "bridge exponent binding")
    need(load(root / "research/e8-bit-p111-tuned/tune/EXPECTED.json")["nine"]["bit"]
         ["charged_prefix_bits"] == 192, "retained nine-stage charge")
    return dict(K=4, bridge_exponent=18, local_cap=104, nine_cap=192)
