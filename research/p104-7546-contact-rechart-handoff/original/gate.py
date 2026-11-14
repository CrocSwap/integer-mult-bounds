#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""One frozen current-word nomination gate, never a kappa/supplier admission.

Reuses the fresh-helper-boundary cut method and Rohan Arun's #7122/#7124
return contract. Source notices and exact pins are in SOURCES.json.
Prepared for Clear1nsight with substantial OpenAI Pro/Codex assistance.
"""
import time
START = time.monotonic()
import argparse
import ast
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import resource
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
OUT = None
RECEIPT = {"status": "RUNNING", "completed": [], "new_kappa": False,
           "full_qualification_completed": False,
           "full_supplier_executed": False, "source_cases": 1}


def emit(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def checkpoint(name):
    RECEIPT["completed"].append(name)
    emit("RECEIPT.json", RECEIPT)
    print(name, time.monotonic() - START, flush=True)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def authenticate():
    if not __debug__:
        raise ValueError("assertions must remain active")
    frozen = json.loads((ROOT / "FREEZE.json").read_text())
    if sha256((ROOT / "FREEZE.json").read_bytes()).hexdigest() != EXPECTED_FREEZE:
        raise ValueError("external frozen manifest digest")
    for item in frozen["files"]:
        data = (ROOT / item["path"]).read_bytes()
        if (len(data), sha256(data).hexdigest()) != (item["bytes"], item["sha256"]):
            raise ValueError("frozen file mismatch: " + item["path"])
    spec = json.loads((ROOT / "SPEC.json").read_text())
    if {item["path"] for item in frozen["files"]} != set(spec["mandatory_paths"]):
        raise ValueError("mandatory frozen path set")
    sources = json.loads((ROOT / "SOURCES.json").read_text())
    for item in sources["current_public_inputs"]:
        if sha256((ROOT / item["path"]).read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("independent upstream source pin")
    raw = gzip.decompress((ROOT / "sources/WORD.json.gz").read_bytes())
    if sha256(raw).hexdigest() != spec["word_canonical_sha256"]:
        raise ValueError("current word hash")
    word = json.loads(raw)
    if raw != json.dumps(word, sort_keys=True, separators=(",", ":")).encode():
        raise ValueError("current word canonical bytes")
    emit("AUTHENTICATION.json", {"freeze_sha256": sha256((ROOT / "FREEZE.json").read_bytes()).hexdigest(),
         "files": frozen["files"], "canonical_word_sha256": spec["word_canonical_sha256"]})
    return spec, word


def invoice_primitive():
    path = ROOT / "sources/check_role902_grid.py"
    tree = ast.parse(path.read_text())
    definitions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "invoice"]
    if len(definitions) != 1:
        raise ValueError("unique source invoice primitive")
    namespace = {"Counter": Counter}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(path), "exec"), namespace)
    return namespace["invoice"]


def plain(value):
    return json.loads(json.dumps(value, sort_keys=True))


def rejected(name, action, results):
    try:
        action()
    except ValueError as error:
        results[name] = str(error)
        return
    raise ValueError("control accepted: " + name)


def controls(core):
    toy = {"public": 1, "owned_fields": 0, "live": [], "hosted": {"X2": [], "Y2": []},
           "frames": [[], [1], [1, 2]], "initial": [0], "final": [2],
           "program": [["MOVE", 0, 0, 1, False], ["MOVE", 0, 1, 2, False]]}
    spaces = list(map(core.span, toy["frames"]))
    graph = core.build_graph(toy, set())
    labels = [n["before"] for n in graph["nodes"]]
    rebuilt, bindings = core.reconstruct(toy, graph, labels, set(), spaces)
    obs = core.validate_reconstruction(toy, rebuilt, bindings, set(), spaces)
    core.need(obs["paid"] == {2: 1} and core.inventory(toy, spaces)["paid"] == {1: 2}, "baseline fusion control")
    result = {"baseline_fusion": {"before": {1: 2}, "after": {2: 1}}}
    protected = core.build_graph(toy, {0})
    labels = [n["before"] for n in protected["nodes"]]
    retained, anchors = core.reconstruct(toy, protected, labels, {0}, spaces)
    core.need(retained == toy, "protected source-clock anchors")
    result["protected_anchors_retained"] = True
    bad = list(labels); bad[0] = 1
    rejected("protected_boundary", lambda: core.validate_labels(toy, protected, bad, "entry", {0}, spaces), result)
    wrong = deepcopy(toy); wrong["program"][0][-1] = True
    rejected("false_owned_flag", lambda: core.inventory(wrong, spaces), result)
    duplicate = list(spaces) + [spaces[1]]
    core.need(not core.ascend(duplicate, 1, 3), "distinct equal-span IDs")
    result["equal_span_different_ID_refused"] = True
    copy = deepcopy(toy); copy["owned_fields"] = 1
    copy["program"] = [["INIT", 1, 0], ["COPY", 1, 0, "1", 0], ["CLEAR", 1, 0], ["MOVE", 0, 0, 2, False]]
    core.need(len(core.inventory(copy, spaces)["copies"]) == 1, "INIT COPY guard")
    dirty = deepcopy(copy); dirty["program"].insert(1, ["ADD", 1, 0, "1", 0])
    rejected("dirty_COPY_not_hidden_by_CLEAR", lambda: core.inventory(dirty, spaces), result)
    return result


def graph_file(word, graph, spaces):
    path = OUT / "GRAPH.txt"
    with path.open("x") as f:
        print(len(spaces), len(graph["nodes"]), len(graph["edges"]), len(graph["helpers"]), file=f)
        for frame, values in zip(word["frames"], spaces):
            chunks = [sum(1 << (v % 64) for v in values if v // 64 == b) for b in range(8)]
            print(len(frame), *chunks, file=f)
        for node in graph["nodes"]:
            print(int(node["entry"]), int(node["exit"]), node["before"], node["after"], file=f)
        for a, b, _r in graph["edges"]:
            print(a, b, file=f)
        for r in graph["helpers"]:
            print(graph["initial"][r], graph["final"][r], file=f)
    return path


def command(argv, stdout_name):
    remaining = min(116., 118. - (time.monotonic() - START))
    if remaining <= 0:
        raise TimeoutError("frozen wall cap")
    with (OUT / stdout_name).open("x") as out, (OUT / (stdout_name + ".stderr")).open("x") as err:
        result = subprocess.run(argv, stdout=out, stderr=err, timeout=remaining, cwd=ROOT)
    if result.returncode:
        raise ValueError("command failed: " + stdout_name + " exit " + str(result.returncode))


def exact_price(word, paid, invoice, caller, interval, upper):
    inv = invoice(word, caller, paid)
    signed = {"T": dict(inv["signed_productive"]), "P": dict(inv["signed_paid"])}
    value = interval.sub(interval.moment(signed["T"], upper), interval.moment(signed["P"], upper))
    return inv, {"comparison_kappa_upper": upper, "moment_integer_bounds": list(value),
                 "fixed_denominator": str(interval.B), "strictly_positive_lower": value[0] > 0,
                 "invoice": plain(inv)}


def assess(core, word, graph, labels, mode, protected, spaces, invoice, caller, interval, spec, prefix):
    core.validate_labels(word, graph, labels, mode, protected, spaces)
    new, bindings = core.reconstruct(word, graph, labels, protected, spaces)
    inv = core.validate_reconstruction(word, new, bindings, protected, spaces)
    if mode == "baseline":
        expected = Counter()
        for a, b, _r in graph["edges"]:
            fa, fb = graph["nodes"][a]["after"], graph["nodes"][b]["before"]
            if fa != fb:
                expected[len(word["frames"][fb])-len(word["frames"][fa])] += 1
        for e in word["program"]:
            if e[0] == "MOVE" and (e[1] >= word["public"] or e[1] in protected):
                expected[abs(len(word["frames"][e[3]])-len(word["frames"][e[2]]))] += 1
        core.need(expected == inv["paid"], "graph edges and immutable charges match causal reconstruction")
    profile, price = exact_price(new, inv["paid"], invoice, caller, interval, spec["comparison_raw_upper"])
    core.need(profile["native_productive"] == inv["targets"], "independent native target recount")
    change = core.changes(word, new, bindings)
    retained = module("retained_protected_constructor", ROOT / "construct7124_protected.py")
    core.need(retained.construct(word, change, protected) == new,
              "existing protected #7124 constructor agrees with clock-instrumented emitter")
    emit(prefix + "-PRICE.json", price)
    emit(prefix + "-CHANGES.json", change)
    emit(prefix + "-INVENTORY.json", plain(inv))
    if price["strictly_positive_lower"]:
        (OUT / "NOMINEE-WORD.json.gz").write_bytes(gzip.compress(core.canonical(new), mtime=0))
        emit("NOMINEE-BINDINGS.json", bindings)
        emit("NOMINEE-ASSIGNMENT.json", {"mode": mode, "labels": labels})
        emit("NOMINEE.json", {"mode": mode, "changes": change, "price": price,
             "canonical_word_sha256": sha256(core.canonical(new)).hexdigest(),
             "source_sha256": spec["word_canonical_sha256"],
             "status": "NOMINATION_ONLY_FULL_QUALIFICATION_UNRUN", "new_kappa": False,
             "unrun": spec["full_qualification_obligations"]})
        return True
    return False


def main():
    spec, word = authenticate()
    core = module("contact_rechart_core", ROOT / "core.py")
    interval = module("contact_rechart_intervals", ROOT / "sources/interval_gate.py")
    invoice = invoice_primitive()
    caller = json.loads((ROOT / "sources/CALLER.json").read_text())
    checkpoint("authenticated_code_inputs_and_invoice_primitive")
    ctl = controls(core)
    binary = OUT / "discover"
    command(["g++", "-O2", "-std=c++20", "-Wall", "-Wextra", "-Werror",
             str(ROOT / "discover.cpp"), "-o", str(binary)], "COMPILE.txt")
    exponent = str(1. - float(spec["comparison_raw_upper"]))
    command([str(binary), exponent, "--selftest"], "CUT-CONTROLS.txt")
    core.need("PASS_CUT_CONTROLS 20" in (OUT / "CUT-CONTROLS.txt").read_text(), "cut control marker")
    ctl["cut_bruteforce_controls"] = (OUT / "CUT-CONTROLS.txt").read_text()
    emit("CONTROLS.json", ctl)
    checkpoint("frozen_controls_and_compilation")
    protected = set(spec["unavailable"])
    spaces = list(map(core.span, word["frames"]))
    before = core.inventory(word, spaces)
    original, price = exact_price(word, before["paid"], invoice, caller, interval, spec["comparison_raw_upper"])
    whole = json.loads((ROOT / "sources/WHOLE.json").read_text())
    core.need(plain(original) == whole["signed_profile"], "literal original17invoice")
    core.need(price["moment_integer_bounds"][1] < 0, "original invoice rejects comparison upper")
    core.need((len(before["lifetimes"]), len(before["owned_moves"]), before["peak"]) == (74, 47, 50), "original ownership inventory")
    changed = Counter(before["paid"]); changed[1] += 1
    mutant = invoice(word, caller, changed)
    core.need(mutant["signed_paid"][1] - original["signed_paid"][1] == 17, "omitted17fold charge control")
    emit("ORIGINAL-PRICE.json", price)
    emit("ORIGINAL-INVENTORY.json", plain(before))
    graph = core.build_graph(word, protected)
    emit("FORCED-CORRIDORS.json", core.narrow_forced_spaces(graph, spaces))
    emit("GRAPH-INDEX.json", graph)
    RECEIPT["graph"] = {"nodes": len(graph["nodes"]), "edges": len(graph["edges"]),
                        "frames": len(spaces), "mutable_helpers": len(graph["helpers"])}
    checkpoint("literal_graph_original_invoice_and_owned_anchors")
    labels = [n["before"] for n in graph["nodes"]]
    if assess(core, word, graph, labels, "baseline", protected, spaces, invoice, caller, interval, spec, "BASELINE-REBUILD"):
        RECEIPT["status"] = "EXACT_NOMINEE_ONLY_FROM_BASELINE_RECONSTRUCTION"
        return
    checkpoint("no_edit_causal_reconstruction_exact_price")
    data = graph_file(word, graph, spaces)
    proposal = OUT / "FLOAT-ASSIGNMENT.txt"
    command([str(binary), exponent, str(data), str(proposal)], "SEARCH.txt")
    if not proposal.exists():
        RECEIPT["status"] = "NO_NOMINEE_IN_ONE_INPUT_THEN_OUTPUT_SWEEP"
        return
    lines = proposal.read_text().splitlines()
    mode, label = lines[0].split(); label = int(label)
    for line in lines[1:]:
        labels[int(line)] = label
    checkpoint("one_floating_assignment_returned")
    accepted = assess(core, word, graph, labels, mode, protected, spaces, invoice, caller, interval, spec, "EXPANSION")
    RECEIPT["status"] = "EXACT_NOMINEE_ONLY" if accepted else "FLOAT_NOMINEE_FAILED_COMPLETE_EXACT_PRICE"


def terminate(signum, _frame):
    raise TimeoutError("resource signal " + str(signum))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--freeze-sha", required=True)
    args = parser.parse_args()
    OUT = args.out.resolve()
    EXPECTED_FREEZE = args.freeze_sha
    if not OUT.is_dir():
        raise ValueError("supervisor must create fresh output")
    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGXCPU, terminate)
    code = 0
    try:
        main()
    except (TimeoutError, subprocess.TimeoutExpired, MemoryError) as error:
        RECEIPT.update(status="FROZEN_RESOURCE_STOP", error=repr(error))
        code = 124
    except BaseException as error:
        RECEIPT.update(status="UNRESOLVED_IMPLEMENTATION_OR_RUNTIME", error=repr(error))
        code = 1
    finally:
        log = OUT / "SEARCH.txt"
        visits = [line.split()[1:3] for line in log.read_text().splitlines() if line.startswith("VISIT ")] if log.exists() else []
        frames = RECEIPT.get("graph", {}).get("frames")
        population = [[mode, str(f)] for mode in ("entry", "exit") for f in range(frames)] if frames is not None else None
        observed = {tuple(key) for key in visits}
        emit("VISITED.json", {"keys": visits, "population": len(population) if population is not None else None,
             "coverage_initialized": population is not None,
             "unvisited": [key for key in population if tuple(key) not in observed] if population is not None else None})
        own, children = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
        RECEIPT.update(seconds=time.monotonic() - START, visited_expansions=len(visits),
            self_cpu_seconds=own.ru_utime+own.ru_stime,
            children_cpu_seconds=children.ru_utime+children.ru_stime,
            self_peak_rss_KiB=own.ru_maxrss, children_peak_rss_KiB=children.ru_maxrss,
            conservative_sum_peak_rss_KiB=own.ru_maxrss+children.ru_maxrss,
            nominee_word_emitted=(OUT / "NOMINEE-WORD.json.gz").exists())
        emit("RECEIPT.json", RECEIPT)
        print(json.dumps(RECEIPT, sort_keys=True), flush=True)
    sys.exit(code)
