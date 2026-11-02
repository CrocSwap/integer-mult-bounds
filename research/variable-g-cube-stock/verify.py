#!/usr/bin/env python3
"""Exact finite evidence for the new variable-g stock schedule."""

import hashlib
import json
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENGINE = "research/typed-actual-width-physical-h/physical_h.py"
ENGINE_SHA = "f032251b60c3d3a4eca84bb6697f5cf032980089b891e1dc8248c297e99ecd2a"


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def module_at(name, path, expected=None):
    raw = path.read_bytes()
    need(len(raw) <= 65536, "module size")
    if expected is not None:
        need(hashlib.sha256(raw).hexdigest() == expected, "source hash")
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


def load():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    rows = [row for row in sources["files"] if row["path"] == ENGINE]
    need(len(rows) == 1 and rows[0]["usage"] == "input", "source declaration")
    need(rows[0]["sha256"] == ENGINE_SHA, "source pin")
    return module_at("variable_stock", HERE / "stock.py"), module_at(
        "physical_h", ROOT / ENGINE, ENGINE_SHA)


def cube_for(machine, salt):
    bound = 1 << machine.p
    return [[(((17 * x + 5 * j + salt) % (2 * bound + 1)) - bound,
              ((11 * x + 7 * j + 3 * salt) % (2 * bound + 1)) - bound)
             for j in range(1 << machine.ell)]
            for x in range(1 << len(machine.physical))]


def check_case(stock, engine, ell, flags, k, p, heights, salt):
    machine = engine.TypedActualWidthH(ell, flags, k, p)
    rounds = [(h, cube_for(machine, salt + index)) for index, h in enumerate(heights)]
    expected = []
    for h, cube in rounds:
        call = engine.TypedActualWidthH(ell, flags, k, p)
        expected.append(call.run(cube, h, source_order="physical"))
    tape_class = engine.Tape
    report = stock.run_schedule(engine, ell, flags, k, p, rounds)
    need(engine.Tape is tape_class, "successful binding restoration")
    need(len(report["rounds"]) == len(rounds), "round count")
    summaries = []
    for index, row in enumerate(report["rounds"]):
        decoded, ledger, info = expected[index]
        need((row["decoded"], row["ledger"], row["info"]) ==
             (decoded, ledger, info), "fresh-call equivalence")
        need(row["source"] == tuple(engine._presented_cells(rounds[index][1], p + 2)),
             "source preservation")
        packet = [bit for record in decoded for pair in record for value in pair
                  for bit in engine.bits_from_int(value, p + 2)]
        root = [bit for start in range(0, len(packet), p + 2)
                for bit in reversed(packet[start:start + p + 2])]
        need(row["consumer"] == tuple(packet) and row["root"] == tuple(root),
             "physical output packets")
        g = len(info["selected_bits"])
        need(len(row["requests"]) == 4 + 3 * g, "per-bit reuse count")
        if index:
            for name in ("root", "consumer"):
                n = report["lengths"][name]
                need(row["reset"][name] == (0, n, 2 * (n - 1)), "charged reset")
        else:
            need(row["reset"] is None, "first round reset")
        summaries.append({"h": row["h"], "g": g, "ledger": ledger,
                          "reset": row["reset"], "allocations": len(row["requests"])})
    return {"ell": ell, "flags": flags, "k": k, "p": p,
            "cells": report["cells"], "lengths": report["lengths"], "rounds": summaries}


def rejects(call, reason):
    try:
        call()
    except ValueError as error:
        need(str(error) == reason, "wrong rejection: " + str(error))
        return
    raise ValueError("missing rejection: " + reason)


def controls(stock, engine):
    view = stock.Prefix([0] * 4)
    view.activate(2)
    rejects(lambda: view.__getitem__(2), "prefix index")
    rejects(lambda: view.__setitem__(-1, 0), "prefix index")
    rejects(lambda: view.__setitem__(0, True), "prefix bit")
    rejects(lambda: view.activate(5), "prefix capacity")
    view.backing[3] = 1
    rejects(lambda: view.activate(2), "dirty inactive tail")
    machine, lengths = stock.geometry(engine, 3, (True, False), 1, 4)
    inv = stock.Inventory(engine, lengths)
    inv.begin(1)
    rejects(lambda: inv.allocate(lengths["source"] + 1), "prefix capacity")
    inv.tapes["source"].head = 1
    rejects(lambda: inv.allocate(lengths["source"]), "allocation head")
    inv.tapes["source"].head = 0
    inv.allocate(lengths["source"])
    inv.views["scratch"].backing[0] = 1
    rejects(lambda: inv.allocate(lengths["scratch"]), "allocation dirt")
    rejects(lambda: stock.run_schedule(engine, 3, (True, False), 1, 4, []), "schedule bound")
    rejects(lambda: stock.geometry(engine, 5, (True,), 1, 4), "layout bound")
    cube = cube_for(machine, 0)
    cube[0][0] = (17, 0)
    original = engine.Tape
    rejects(lambda: stock.run_schedule(engine, 3, (True, False), 1, 4, [(2, cube)]),
            "unit disk")
    need(engine.Tape is original, "failed binding restoration")
    return 11


def main():
    stock, engine = load()
    cases = [(3, (True, False), 1, 4, (2, 1), 0),
             (3, (True, False), 1, 4, (1, 2), 7),
             (3, (True, False), 1, 1, (2, 1, 0, 2), 3),
             (3, (True, False), 2, 4, (2, 0, 1), 11),
             (2, (True, False, False), 1, 4, (1, 0, 1), 2)]
    results = [check_case(stock, engine, *case) for case in cases]
    need(results[0]["cells"] == 21504, "discriminating stock")
    need([row["g"] for row in results[0]["rounds"]] == [1, 2], "changing g witness")
    count = controls(stock, engine)
    receipt = {"claim_type": "scoped stock construction with finite certificate",
               "cases": results, "controls": count,
               "sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in sorted(HERE.iterdir()) if path.is_file()}}
    print("PASS_VARIABLE_G_CUBE_STOCK")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
