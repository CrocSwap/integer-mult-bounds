#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Authenticate sources and compare the proved literal recurrence to PR3182."""

import argparse
import ast
import hashlib
import json
from itertools import combinations, pairwise, product
from pathlib import Path

from memory import Model, bitmap, propagate, require, span

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = "research/p104-pooled-onehop-and-physical-consumer-bill/verify.py"
PREFIX = "research/p104-native-channel/inputs/"
CERT = "research/p104-joint-unit-flags/CERTIFICATE.json"
MATCH = "research/p104-coherent-support-witness/WITNESS.json"
INPUTS = (
    OLD,
    PREFIX + "LOWRANK-WITNESS.json",
    PREFIX + "P104-FIXTURE.json",
    CERT,
    MATCH,
)


def unique(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), "duplicate JSON key")
    return result


def read(path):
    with path.open("rb") as stream:
        raw = stream.read(2_000_001)
    require(len(raw) <= 2_000_000, "input byte capacity")
    return json.loads(raw, object_pairs_hook=unique)


def authenticate():
    manifest = read(HERE / "SOURCES.json")
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    require(
        sorted(row["path"] for row in rows) == sorted(INPUTS), "exact input inventory"
    )
    for row in rows:
        path = ROOT / row["path"]
        require(path.stat().st_size <= 2_000_000, "source byte capacity")
        require(
            hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
            "source changed: " + row["path"],
        )


def archived(write_all):
    """Execute only named, authenticated pure functions, bypassing .pyc imports."""
    tree = ast.parse((ROOT / OLD).read_bytes())
    names = {
        "require",
        "span",
        "bits",
        "dim",
        "intervals",
        "fits",
        "contact",
        "build_general_interval_layers",
        "propagate_with_subspace_memory_bitmap",
    }
    nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in names
    ]
    require({node.name for node in nodes} == names, "audited function inventory")
    memory = next(node for node in nodes if node.name.startswith("propagate_"))
    branches = [
        node
        for node in ast.walk(memory)
        if isinstance(node, ast.If)
        and node.body
        and isinstance(node.body[-1], ast.Break)
    ]
    require(len(branches) == 1 and len(branches[0].body) == 2, "one output break")
    require(
        ast.unparse(branches[0].body[0]) == "outputs[t] |= 1 << s", "break location"
    )
    if write_all:
        branches[0].body.pop()
    namespace = {}
    module = ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[]))
    exec(compile(module, "<authenticated-pr3182-functions>", "exec"), namespace)
    return namespace


def paths(word):
    result = {
        f"{kind}{i}": [span(word["initial_frames"][f"{kind}{i}"])]
        for kind in "XY"
        for i in range(104)
    }
    require(len(word["program"]) == 4058, "original word length")
    for event in word["program"]:
        if event[0] != "transport":
            require(event[0] in {"add", "copy", "zero", "erase"}, "original opcode")
            require(not event[1].startswith("X"), "immutable sources")
            if event[0] in {"add", "copy"}:
                require(not event[2].startswith("Y"), "unread targets")
        if event[0] == "transport" and event[1] in result:
            old, new = span(event[2]), span(event[3])
            chain = result[event[1]]
            require(chain[-1] == old and old < new, "monotone data path")
            require(len(new) == len(old) << event[4], "transport rank")
            chain.append(new)
    for name, chain in result.items():
        require(chain[-1] == span(word["final_frames"][name]), "final data frame")
    return result


def required_entry():
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            root = [0] * 8
            root[i], root[j] = 2, 2 * sign
            roots.append(tuple(root))
    roots += [
        (1, *signs) for signs in product((-1, 1), repeat=7) if signs.count(-1) % 2 == 0
    ]
    fixture = read(ROOT / (PREFIX + "P104-FIXTURE.json"))["section4_explicit_P104"]
    ports = sorted(set(roots) - {tuple(v) for v in fixture["F0"] + fixture["C"]})
    require(len(ports) == 104, "ordered root fixture")
    require(
        sum(a * b for a, b in zip(ports[98], ports[1], strict=True)) == 4,
        "C[98,1] = -1/2",
    )
    return "-1/2"


def p104_model():
    word = read(ROOT / (PREFIX + "LOWRANK-WITNESS.json"))
    cert = read(ROOT / CERT)
    pairing = read(ROOT / MATCH)["pairing"]
    data = paths(word)
    require(
        len(pairing) == 208 and set(pairing) == set(range(208)), "matching bijection"
    )
    lines = [data[f"X{s}"][0] for s in range(104)]
    caps = [data[f"Y{t}"][-1] for t in range(104)]
    departures, arrivals = [], []
    for i in range(104):
        for form in cert["forms"]["departure"][i]:
            departures.append(span(word["initial_frames"][f"X{i}"] + [form]))
        for form in cert["forms"]["arrival"][i]:
            arrivals.append(
                frozenset(v for v in caps[i] if (v & form).bit_count() % 2 == 0)
            )
    bounds = []
    for dimension in range(1, 9):
        layer = []
        for helper, arrival in enumerate(pairing):
            require(departures[helper] <= arrivals[arrival], "compatible endpoint pair")
            if dimension in (1, 2, 7, 8):
                fixed = {
                    1: lines[helper // 2],
                    2: departures[helper],
                    7: arrivals[arrival],
                    8: caps[arrival // 2],
                }[dimension]
                layer.append((fixed, fixed))
            else:
                layer.append((departures[helper], arrivals[arrival]))
        bounds.append(tuple(layer))
    model = Model(
        tuple(bounds),
        tuple(tuple(data[f"X{s}"]) for s in range(104)),
        tuple(tuple(data[f"Y{t}"]) for t in range(104)),
    )
    frames = (
        [bitmap(f) for f in lines],
        [bitmap(f) for f in departures],
        [bitmap(f) for f in arrivals],
        [bitmap(f) for f in caps],
        [],
    )
    return model, frames, list(enumerate(pairing)), word, data


def archived_outputs(namespace, model, frames, edges, full_memory):
    data = {
        f"{kind}{i}": [bitmap(f) for f in chain]
        for kind, chains in (("X", model.sources), ("Y", model.targets))
        for i, chain in enumerate(chains)
    }
    layers = namespace["build_general_interval_layers"](frames, edges, data)
    direct = [
        sum(
            1 << s for s, chain in enumerate(model.sources) if set(chain) & set(targets)
        )
        for targets in model.targets
    ]
    return namespace["propagate_with_subspace_memory_bitmap"](
        frames, edges, layers, data, direct, full_memory=full_memory
    )


def actual_path(model, edges, word, data, legacy, repaired):
    flag = [span([]), model.bounds[0][201][0], model.bounds[1][201][0]]
    for basis in (
        [3, 8, 480],
        [3, 8, 64, 416],
        [3, 5, 8, 64, 416],
        [3, 5, 8, 16, 64, 416],
    ):
        flag.append(span(basis))
    flag += [
        model.bounds[6][201][0],
        model.bounds[7][201][0],
        span([1 << i for i in range(9)]),
    ]
    require([len(f) for f in flag] == [1 << d for d in range(10)], "literal full flag")
    require(all(a < b for a, b in pairwise(flag)), "literal nested flag")
    source = span(word["initial_frames"]["X1"])
    for event in word["program"][:594]:
        if event[:2] == ["transport", "X1"]:
            require(span(event[2]) == source, "source cut induction")
            source = span(event[3])
    require(source == flag[4] and data["Y98"][-1] == flag[8], "read and write cuts")
    require(edges[201] == (201, 197), "pinned helper edge")
    require(legacy[98] & 2 == 0 and repaired[98] & 2 == 2, "literal path retained")
    return {
        "source": 1,
        "helper": 201,
        "target": 98,
        "read_cut": 594,
        "write_cut": 4058,
        "required_coefficient": required_entry(),
        "legacy_contains": False,
        "repaired_contains": True,
    }


def result():
    authenticate()
    model, frames, edges, word, data = p104_model()
    old, fixed = archived(False), archived(True)
    modes = {}
    for full in (False, True):
        output, peak = propagate(model, full)
        require(
            output == archived_outputs(fixed, model, frames, edges, full),
            "separate implementation agrees with one-break repair",
        )
        legacy = archived_outputs(old, model, frames, edges, full)
        modes[str(full)] = {
            "outputs": output,
            "max_antichain": peak,
            "path": actual_path(model, edges, word, data, legacy, output),
        }
    return {"schema_version": 1, "p104_pr3019": modes, "no_new_kappa": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    value = result()
    if args.emit:
        print(json.dumps(value, indent=2))
    else:
        require(
            json.dumps(value, sort_keys=True)
            == json.dumps(read(HERE / "RESULT.json"), sort_keys=True),
            "typed receipt mismatch",
        )
        print(
            "PASS_P104_MEMORY_RELAXATION_SOUNDNESS modes=2 "
            "actual_path=X1-H201-Y98 no_new_kappa"
        )


if __name__ == "__main__":
    main()
