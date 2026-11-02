#!/usr/bin/env python3
"""Verify the new 22-ADD, 232-unit handoff; write no files.

This contribution was produced by Nick Petalas. Apache-2.0.
Predecessor executables are authenticated and used only on the new word.
"""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from types import ModuleType
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/p104-coupled-helper-bases/"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path, name):
    """Execute source bytes directly, without reading a bytecode cache."""
    module = ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def sources():
    metadata = json.loads((HERE / "SOURCES.json").read_bytes())
    rows = [r for r in metadata["files"] if r["usage"] == "input"]
    require(len(rows) == 4, "exact live dependency closure")
    hashes = {}
    for row in rows:
        raw = (ROOT / row["path"]).read_bytes()
        digest = sha256(raw).hexdigest()
        require(digest == row["sha256"], "source bytes: " + row["path"])
        hashes[row["path"]] = digest
    return hashes


def matrix(events, keys):
    require(len(keys) <= 5 and len(events) <= 12, "small boundary domain")
    index = {r: i for i, r in enumerate(keys)}
    value = [[Q(i == j) for j in keys] for i in keys]
    for op, r, s, q, frame in events:
        require(op == "ADD" and r != s, "boundary ADD")
        i, j = index[r], index[s]
        value[i] = [x + Q(q) * y for x, y in zip(value[i], value[j], strict=True)]
    return value


def boundary(c, a, b, events):
    keys = sorted(set(a) | set(b))
    value = matrix(events, keys)
    p = keys.index(596)
    require([sum(a.get(r, 0) * value[i][j] for i, r in enumerate(keys))
             for j in range(len(keys))] == [Q(j == p) for j in range(len(keys))],
            "row boundary")
    require([value[i][p] for i in range(len(keys))] == [b.get(r, 0) for r in keys],
            "column boundary")
    require(matrix(events + c.inverse(events), keys)
            == [[Q(i == j) for j in keys] for i in keys], "dirty inverse")


def rejection(function):
    try:
        function()
    except ValueError as error:
        return str(error)
    raise ValueError("control accepted")


def boundary_checks(c):
    results, controls = [], []
    for a, b, frame, cost in [(c.V, c.B, 3, 62), (c.V, c.U, 1053, 54)]:
        events = c.basis(a, b, 596, frame)
        boundary(c, a, b, events)
        require(c.allowance(events) == c.allowance(c.inverse(events)) == cost,
                "boundary and inverse tariff")
        for i in range(len(events)):
            mutant = events[:i] + events[i + 1:]
            controls.append(rejection(lambda m=mutant: boundary(c, a, b, m)))
        mutant = deepcopy(events)
        # These two inverse preconditioners do not commute.
        mutant[-1], mutant[-2] = mutant[-2], mutant[-1]
        controls.append(rejection(lambda: boundary(c, a, b, mutant)))
        results.append({"events": events, "allowance": cost})
    require(len(controls) == 13, "complete boundary omission/order controls")
    require(2 * sum(r["allowance"] for r in results) == 232, "four-boundary tariff")
    return results, controls


def construct(c):
    local = load(ROOT / SOURCE / "local.py", "local")
    builder = load(ROOT / SOURCE / "construct.py", "_ordered_handoff_builder")
    word = json.loads(gzip.decompress((ROOT / SOURCE / "inputs/pr5580-WORD.json.gz").read_bytes()))
    pairs = lambda values: [[r, str(q)] for r, q in sorted(values.items())]
    step = {"kind": "coupled_handoff", "cut": 13762, "frame": 1053,
            "group": [3, 127], "pivot": 596, "v": pairs(c.V), "u": pairs(c.U),
            "source_functional": pairs(c.V), "output_direction": pairs(c.B)}
    builder.basis = c.basis
    candidate = builder.handoff(word, step)
    require(len(candidate["program"]) == 25162, "22 inserted ADDs")
    require(candidate["frames"] == word["frames"] and candidate["ports"] == word["ports"],
            "retained geometry")
    return candidate, local


def word_checks(candidate, local):
    primary = local.replay(candidate)
    other = load(ROOT / "research/p104-unit-column-handoff/independent.py",
                 "_ordered_handoff_integer_replay")
    independent, snapshot = other.replay(candidate)
    require(snapshot is None, "no unrequested checkpoint")
    paid = {1: 2211, 2: 459, 3: 494, 4: 94, 5: 164, 6: 18, 7: 14}
    helpers = {4: 84, 5: 6, 8: 15, 9: 423}
    require(primary["paid"] == independent["paid"] == paid, "complete paid profile")
    require(primary["helpers"] == independent["helpers"] == helpers, "complete target profile")
    require(primary["real_scalar_allowance"] == independent["allowance"] == 217660,
            "new complete scalar allowance")
    require(independent["input_columns"] == 744 and independent["endpoint_coefficients"] == 553536,
            "all independent coefficients")
    require(independent["initialized"] == independent["cleared"] == 8
            and independent["peak_owned"] == 1, "owned lifetimes")
    return primary, independent, other


def word_controls(candidate, engine):
    results = []
    for kind in range(8):
        mutant = deepcopy(candidate)
        if kind == 0:
            mutant["program"][0][-2] = "5/8"
        elif kind == 1:
            del mutant["program"][0]
        elif kind == 2:
            mutant["program"][0][-1] = 1053
        elif kind == 3:
            mutant["initial"][735] = 3
        elif kind == 4:
            mutant["final"][596] = 127
        elif kind == 5:
            i = next(i for i, e in enumerate(mutant["program"]) if e[0] == "CLEAR")
            del mutant["program"][i]
        elif kind == 6:
            mutant["program"].insert(0, ["INIT", 735, 1053])
        else:
            mutant["program"][0][-2] = "1/3"
        results.append({"case": kind, "rejection": rejection(lambda: engine.replay(mutant))})
    require(len(results) == 8, "whole-word semantic controls")
    return results


def main():
    require(len(sys.argv) == 1, "no arguments; verifier writes nothing")
    inputs = sources()
    c = load(HERE / "completion.py", "_ordered_completion")
    boundaries, omissions = boundary_checks(c)
    candidate, local = construct(c)
    primary, independent, engine = word_checks(candidate, local)
    result = {"claim_type": "scoped construction with exact finite certificate",
              "inserted_events": 22, "inserted_allowance": 232,
              "boundaries": boundaries, "boundary_controls": omissions,
              "primary": primary, "second_representation": independent,
              "word_controls": word_controls(candidate, engine), "inputs_sha256": inputs,
              "word_sha256": sha256(json.dumps(candidate, sort_keys=True,
                                               separators=(",", ":")).encode()).hexdigest(),
              "package_sha256": {p.name: sha256(p.read_bytes()).hexdigest()
                                 for p in sorted(HERE.iterdir()) if p.is_file()}}
    print(json.dumps(result, sort_keys=True))
    print("PASS_P104_ORDERED_HANDOFF inserted_events=22 inserted_allowance=232")


if __name__ == "__main__":
    main()
