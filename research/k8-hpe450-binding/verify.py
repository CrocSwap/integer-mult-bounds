#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance.
"""Finite scalar/chronology/recipe binding for k8 helper 450; no Lean build.

Pinned producers reconstruct the published event streams. This checker does
not import their replay functions: it pulls one output row backwards and
pushes one input column forwards using exact rational arithmetic.
"""
import argparse
import ast
import copy
from fractions import Fraction
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HELPER = 450
RAW = "research/t16-owner-audit-seed67/inputs/k8-seven-slot-word.json.gz"
PINS = "research/gauge44-slots/construction/slots/SLOT-PINS-k8.json"
LEAN = "research/hyperplane-end-lean/HyperplaneEnd/Exact.lean"
SOURCE = "research/complex-sw4-frame8/vendor/pr635/research/complex-571-cold14-st2/code"
VENDOR = "research/complex-k492-owner-repair/vendor/multicold"
ROUTING = VENDOR + "/vendor/pr558/vendor/pr552/complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz"
CLIFFORD = VENDOR + "/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford/clifford_exact.py"
PHASES = ["zero_frame_precondition", "entry_adapters", "A", "centers", "B",
          "cleanup_tail", "final", "exit_adapters", "full_frame_cleanup", "done"]


class Reject(ValueError):
    def __init__(self, code, detail=""):
        self.code = code
        super().__init__(code + (": " + detail if detail else ""))


def need(ok, code, detail=""):
    if not ok:
        raise Reject(code, detail)


def unique_object(items):
    out = {}
    for key, value in items:
        need(key not in out, "duplicate_json_key", key)
        out[key] = value
    return out


def read(path):
    data = path.read_bytes()
    if path.suffix == ".gz":
        data = gzip.decompress(data)
    return json.loads(data, object_pairs_hook=unique_object)


def encoded(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source_check(root=ROOT):
    manifest = read(HERE / "SOURCES.json")
    rows = [r for r in manifest["files"] if r["usage"] == "input"]
    for row in rows:
        path = (root / row["path"]).resolve()
        need(path.is_relative_to(root.resolve()), "source_path")
        need(path.is_file() and sha(path.read_bytes()) == row["sha256"],
             "source_hash", row["path"])
    return {row["path"]: row["sha256"] for row in rows}


def literal_pair3(text):
    # Source pins fix this deliberately narrow parser's language and theorem.
    matches = re.findall(r"^def pair3 : Pair := (.*?)\n\n", text, re.S | re.M)
    need(len(matches) == 1, "lean_pair_literal")
    data = ast.literal_eval(matches[0].replace("⟨", "[").replace("⟩", "]"))
    need(isinstance(data, list) and len(data) == 4, "lean_pair_shape")
    fields = ("quadratic_rows", "linear_Z4", "matrix_rows", "offset", "phase")
    entrance, terminal, left, right = data
    return entrance, terminal, dict(zip(fields, left, strict=True)), dict(zip(fields, right, strict=True))


def span(rows):
    points = {0}
    for row in rows:
        need(type(row) is int and 0 < row < 512, "frame_vector")
        points |= {p ^ row for p in points}
    need(len(points) == 2 ** len(rows), "dependent_frame_basis")
    return frozenset(points)


def fraction(a, b):
    # Inverse scales may serialize a negative denominator; Fraction normalizes it.
    need(type(a) is int and type(b) is int and b != 0, "scalar_coefficient")
    return Fraction(a, b)


def register(value):
    need(isinstance(value, list) and len(value) == 2 and
         value[0] in ("L", "C") and type(value[1]) is int and
         0 <= value[1] < (704 if value[0] == "L" else 8), "register")
    return tuple(value)


def scalar(op):
    need(isinstance(op, list) and op, "scalar_shape")
    tag = op[0]
    sizes = {"clear": 2, "copy": 3, "scale": 4, "add": 5}
    need(tag in sizes and len(op) == sizes[tag], "scalar_shape")
    target = register(op[1])
    source = register(op[2]) if tag in ("add", "copy") else None
    need(source != target, "scalar_alias")
    q = fraction(*op[3:5]) if tag == "add" else fraction(*op[2:4]) if tag == "scale" else None
    return tag, target, source, q


def add_value(values, key, amount):
    value = values.get(key, Fraction(0)) + amount
    if value:
        values[key] = value
    else:
        values.pop(key, None)


def scalar_row_column(ops, helper=HELPER):
    """Compute e_h^T M and M e_h, including COPY and CLEAR exactly.

    Reverse row propagation multiplies a covector by each gate; it is not
    inverse execution. CLEAR drops a coefficient; COPY transfers it to the
    source and drops the previous target coefficient.
    """
    column = {("L", helper): Fraction(1)}
    for tag, target, source, q in ops:
        if tag == "clear":
            column.pop(target, None)
        elif tag == "copy":
            column.pop(target, None)
            add_value(column, target, column.get(source, Fraction(0)))
        elif tag == "scale":
            value = column.pop(target, Fraction(0))
            add_value(column, target, q * value)
        else:
            add_value(column, target, q * column.get(source, Fraction(0)))
    row = {("L", helper): Fraction(1)}
    for tag, target, source, q in reversed(ops):
        if tag == "clear":
            row.pop(target, None)
        elif tag == "copy":
            value = row.pop(target, Fraction(0))
            add_value(row, source, value)
        elif tag == "scale":
            value = row.pop(target, Fraction(0))
            add_value(row, target, q * value)
        else:
            add_value(row, source, q * row.get(target, Fraction(0)))
    return row, column


def sparse(values):
    return [[list(key), str(value)] for key, value in sorted(values.items())]


def audit(canonical, events, recipe, pair):
    """Semantic checks only: no source or event hashes gate the mutations."""
    c = canonical
    need(c["v"] == 112 and c["R"] == 480 and c["h"] == 9 and
         len(c["start"]) == len(c["final"]) == 704, "local_domain")
    frames = c["frames"]
    spaces = [span(rows) for rows in frames]
    def frame(f):
        need(type(f) is int and 0 <= f < len(frames), "frame_index")
        return f
    for f in c["start"] + c["final"]:
        frame(f)
    entrance, terminal = c["start"][HELPER], c["final"][HELPER]
    E, U, left, right = pair
    need(frames[entrance] == E and frames[terminal] == U, "lean_frame_binding")
    need(len(spaces[entrance]) == 2 and len(spaces[terminal]) == 256 and
         spaces[entrance] <= spaces[terminal], "helper_width")
    for key, value in {"frame": entrance, "terminal": terminal, "vectors": E,
                       "terminal_vectors": U, "entrance_rank": 1, "terminal_rank": 8,
                       "rank": 7, "left": left, "right": right}.items():
        need(key in recipe and encoded(recipe[key]) == encoded(value), "lean_recipe_binding", key)
    current = {("L", r): f for r, f in enumerate(c["start"])}
    wrapped = {r for r in range(224, 704) if c["start"][r] != 0 or c["final"][r] != 1}
    pre, post, phases, touches, climbs, ops = {}, {}, [], [], [], []
    for index, event in enumerate(events):
        need(isinstance(event, list) and event, "event_shape")
        tag = event[0]
        if tag == "phase":
            need(len(event) == 2 and len(phases) < len(PHASES) and
                 event[1] == PHASES[len(phases)], "phase_order")
            phases.append(event[1])
            continue
        need(phases and phases[-1] != "done", "event_outside_program")
        phase = phases[-1]
        if tag == "residual_adapter":
            need(len(event) in (4, 5), "wrapper_shape")
            kind, r, e = event[1:4]
            need(type(r) is int and r in wrapped and e == c["start"][r], "wrapper_entrance")
            end = c["final"][r]
            need(event[4:] == ([end] if end != 1 else []), "wrapper_terminal")
            if kind == "pre":
                need(phase == "entry_adapters" and r not in pre and r not in post, "pre_wrapper_order")
                pre[r] = index
            else:
                need(kind == "post" and phase == "full_frame_cleanup" and r in pre and
                     r not in post and current["L", r] == end, "post_wrapper_order")
                post[r] = index
        elif tag == "adapter":
            need(len(event) == 4, "adapter_shape")
            _, direction, r, f = event
            need(type(r) is int and 0 <= r < 704 and current["L", r] == frame(f), "adapter_frame")
            need((direction == "old_to_new" and phase == "entry_adapters" and r not in wrapped) or
                 (direction == "new_to_old" and phase == "exit_adapters" and
                  not (r >= 224 and c["final"][r] != 1)), "adapter_kind")
        elif tag == "climb":
            need(len(event) == 6, "climb_shape")
            _, part, r, old, new, rank = event
            need(type(r) is int and 0 <= r < 704 and part == phase and
                 current["L", r] == frame(old), "climb_old_frame")
            frame(new)
            need(spaces[old] < spaces[new] and type(rank) is int and
                 rank == len(frames[new]) - len(frames[old]), "climb_rank")
            if r in wrapped:
                need(r in pre and r not in post, "wrapper_enclosure")
            current["L", r] = new
            if r == HELPER:
                climbs.append({"index": index, "phase": phase, "from": old, "to": new, "rank": rank})
        elif tag == "center":
            need(len(event) == 5 and phase == "centers", "center_shape")
            _, k, old, new, rank = event
            need(type(k) is int and 0 <= k < 8 and current.get(("C", k)) == frame(old), "center_frame")
            frame(new)
            need((spaces[old] < spaces[new] or spaces[new] < spaces[old]) and
                 type(rank) is int and rank == abs(len(frames[new]) - len(frames[old])), "center_rank")
            current["C", k] = new
        elif tag == "scalar":
            need(len(event) == 3, "scalar_event_shape")
            f = frame(event[2])
            operation = scalar(event[1])
            op, target, source, _ = operation
            if op == "clear":
                need(target[0] == "C", "clear_local")
                current[target] = f
            operands = [target] + ([source] if source is not None else [])
            for reg in operands:
                if reg[0] == "L" and reg[1] in wrapped:
                    need(reg[1] in pre and reg[1] not in post, "wrapper_enclosure")
            for reg in operands:
                need(current.get(reg) == f, "scalar_frame", str(index))
            ops.append(operation)
            if ("L", HELPER) in (target, source):
                touches.append({"index": index, "phase": phase, "event": event})
        else:
            raise Reject("unknown_event", str(tag))
    need(phases == PHASES and set(pre) == set(post) == wrapped, "wrapper_inventory")
    need([current["L", r] for r in range(704)] == c["final"], "final_frames")
    need(touches and pre[HELPER] < touches[0]["index"] < touches[-1]["index"] < post[HELPER],
         "helper_wrapper_order")
    need(touches[-1]["phase"] == "cleanup_tail" and
         not any(t["phase"] == "full_frame_cleanup" for t in touches), "helper_last_tail")
    row, column = scalar_row_column(ops)
    unit = {("L", HELPER): Fraction(1)}
    need(row == unit, "helper_unit_row", str(sparse(row)))
    need(column == unit, "helper_isolated_column", str(sparse(column)))
    return {"events": len(events), "scalar_operations": len(ops), "local_registers": 704,
            "private_registers": 8, "pre_wrapper_index": pre[HELPER],
            "post_wrapper_index": post[HELPER], "helper_climbs": climbs,
            "helper_scalar_touches": touches, "unit_row": sparse(row),
            "isolated_column": sparse(column), "all_scalar_frame_tags_consistent": True}


def controls(c, events, recipe, pair):
    """All mutations reach the semantic checker; checksums are not consulted."""
    positive = audit(c, events, recipe, pair)
    first = positive["helper_scalar_touches"][0]["index"]
    last = positive["helper_scalar_touches"][-1]["index"]
    pre = positive["pre_wrapper_index"]
    post = positive["post_wrapper_index"]
    climb = positive["helper_climbs"][0]["index"]
    last_failure = "helper_unit_row" if events[last][1][1] == ["L", HELPER] else "helper_isolated_column"
    cases = []
    def event_case(name, code, mutate):
        bad = copy.deepcopy(events)
        mutate(bad)
        cases.append((name, code, c, bad, recipe))
    event_case("missing_pre_wrapper", "wrapper_enclosure", lambda es: es.pop(pre))
    event_case("pre_names_full_terminal", "wrapper_terminal", lambda es: es[pre].__setitem__(4, 1))
    event_case("missing_post_wrapper", "wrapper_inventory", lambda es: es.pop(post))
    event_case("post_before_last_touch", "post_wrapper_order", lambda es: es.insert(last, es.pop(post)))
    event_case("wrong_old_climb_frame", "climb_old_frame", lambda es: es[climb].__setitem__(3, 0))
    event_case("wrong_scalar_frame", "scalar_frame", lambda es: es[first].__setitem__(2, 1))
    event_case("drop_final_tail_touch", last_failure, lambda es: es.pop(last))
    event_case("wrong_final_tail_sign", last_failure, lambda es: es[last][1].__setitem__(3, -es[last][1][3]))
    # After the last touch h's row cannot change again. A new read of its dirty
    # value tests the COLUMN obligation independently of the row.
    extra = ["scalar", ["add", ["L", 230], ["L", HELPER], 1, 1], c["final"][HELPER]]
    event_case("restored_row_but_dirt_leak", "helper_isolated_column", lambda es: es.insert(last + 1, extra))
    event_case("read_after_post_wrapper", "wrapper_enclosure", lambda es: es.insert(post + 1, extra))
    for side in ("left", "right"):
        bad = copy.deepcopy(recipe)
        bad[side]["phase"] = (bad[side]["phase"] + 1) % 4
        cases.append((side + "_global_phase", "lean_recipe_binding", c, events, bad))
    bad = copy.deepcopy(recipe)
    bad["left"], bad["right"] = bad["right"], bad["left"]
    cases.append(("swapped_wrappers", "lean_recipe_binding", c, events, bad))
    bad = copy.deepcopy(recipe)
    bad["right"]["offset"] ^= 1
    cases.append(("wrong_wrapper_translation", "lean_recipe_binding", c, events, bad))
    rejected = []
    for name, code, word, program, rec in cases:
        try:
            audit(word, program, rec, pair)
        except Reject as exc:
            need(exc.code == code, "wrong_control_rejection", name + ": " + str(exc))
            record = {"name": name, "rejected_by": code}
            if name == "restored_row_but_dirt_leak":
                row, column = scalar_row_column([scalar(e[1]) for e in program if e[0] == "scalar"])
                need(row == {("L", HELPER): Fraction(1)}, "leak_control_row")
                leaked = [(r, q) for r, q in sorted(column.items()) if r != ("L", HELPER)]
                need(leaked, "leak_control_column")
                record.update(unit_row_preserved=True, leaked_register=list(leaked[0][0]),
                              exact_coefficient=str(leaked[0][1]))
            rejected.append(record)
        else:
            raise Reject("accepted_mutant", name)
    return rejected


def rebuild(out, root=ROOT):
    """Execute pinned producers sequentially, with assertions in fresh temp output."""
    env = dict(os.environ, MULTICOLD_SOURCE=str(root / VENDOR))
    for key in ("PYTHONOPTIMIZE", "PYTHONPATH", "PYTHONHOME"):
        env.pop(key, None)
    commands = [
        [root / SOURCE / "hpe_audit_and_transport.py", "--raw", root / RAW,
         "--routing", root / ROUTING, "--out", out],
        [root / SOURCE / "hpe_emit_local.py", out],
        [root / SOURCE / "hpe_adapters_local.py", out / "CANONICAL-WORD.json.gz",
         out / "RESIDUAL-ADAPTERS.json", out / "WRAPPER-CHECKS.json"],
    ]
    for command in commands:
        result = subprocess.run([sys.executable, "-I", "-B", *map(str, command)],
                                cwd=root, env=env, capture_output=True, text=True, timeout=120)
        need(result.returncode == 0, "producer_failed", str(command[0]) + "\n" + result.stdout[-1000:] + result.stderr[-1000:])
    cdata = gzip.decompress((out / "CANONICAL-WORD.json.gz").read_bytes())
    c = read(out / "CANONICAL-WORD.json.gz")
    programs = read(out / "LOCAL-PROGRAMS.json.gz")
    recipes = read(out / "RESIDUAL-ADAPTERS.json")
    pins = read(root / PINS)
    need(sha(gzip.decompress((root / RAW).read_bytes())) == pins["word_sha256"], "raw_word_pin")
    need(sha(cdata) == pins["canonical_sha256"], "canonical_pin")
    need(set(programs) == {"forward", "backward"}, "orientations")
    for name in programs:
        need(sha(encoded(programs[name])) == pins["program_sha256"][name], "program_pin", name)
    return c, programs, recipes, pins


def compute():
    inputs = source_check()
    selected_source = read(ROOT / "research/community-frontier1094-audit/SELECTED-SOURCE.json")
    need(selected_source["files"][PINS] == inputs[PINS], "selected_slot_pin_binding")
    with tempfile.TemporaryDirectory(prefix="k8-hpe450-") as tmp:
        c, programs, recipes, pins = rebuild(Path(tmp) / "local")
        pair = literal_pair3((ROOT / LEAN).read_text())
        key = f"{c['start'][HELPER]}:{c['final'][HELPER]}"
        need(key in recipes["recipes"], "recipe_key")
        recipe = recipes["recipes"][key]
        results = {}
        for name in ("forward", "backward"):
            results[name] = audit(c, programs[name], recipe, pair)
            results[name]["controls"] = controls(c, programs[name], recipe, pair)
        need(source_check() == inputs, "sources_changed_during_replay")
    return {"status": "PASS_K8_HPE450_FINITE_BINDING", "helper": HELPER,
            "lean_pair": "HyperplaneEnd.Exact.pair3", "recipe_key": key,
            "raw_word_content_sha256": pins["word_sha256"],
            "canonical_content_sha256": pins["canonical_sha256"],
            "program_sha256": pins["program_sha256"], "input_sha256": inputs,
            "recipe": recipe, "orientations": results,
            "scope": "Finite scalar row/column, emitted frame tags, wrapper placement and literal recipe binding. "
                     "No fresh Lean build or general JSON-to-Lean translation proof; exact lowering of other "
                     "events, physical hosting, all-size compilation, costs and analytic transfer remain separate."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path, help="write a new receipt without overwriting an existing file")
    args = parser.parse_args()
    result = compute()
    if args.write_result:
        with args.write_result.open("x") as out:
            out.write(json.dumps(result, indent=2) + "\n")
    else:
        need(encoded(result) == encoded(read(HERE / "RESULT.json")), "receipt_mismatch")
    print(result["status"] + " helper=450 orientations=2 scalar_row_and_column=exact controls=28 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (Reject, OSError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        raise SystemExit("FAIL: " + str(exc))
