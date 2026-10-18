#!/usr/bin/env python3
"""Exact R439 semantic-D and cost checks independent of the row search.

Prepared for Gareth Davidson (@bitplane), with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
import copy
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile

C = runpy.run_path(str(Path(__file__).resolve().with_name("common.py")))
need = C["need"]


def same(a, b, message):
    need(C["canonical"](a) == C["canonical"](b), message)


def guards(forward, reverse):
    need(forward <= 49347, "forward guard")
    need(64 * forward ** 3 * reverse ** 2 < 1 << 104, "local payload guard")
    need((1 << 18) * forward ** 5 * reverse ** 4 < 1 << 192, "nine-stage guard")


def d_atoms(word):
    v, n = word["v"], 2 * word["v"] + word["R"]
    result = []
    for frame, d, sources in word["D"]:
        need(frame == 0, "D frame zero")
        need(v <= d < 2 * v, "D only writes targets")
        need(all(v <= s < n and s != d for s in sources), "D legal donor")
        result.extend((d, s) for s in sources)
    return result


def stream(word):
    # Simple opcode interpreter; no imports from the builder or owning exporter.
    v, temp = word["v"], 2 * word["v"] + word["R"]
    instructions = []
    for section in ("D", "A"):
        for _, d, sources in word[section]:
            instructions.extend((1, d, s) for s in sources)
    for j, center in enumerate(word["ret"]):
        instructions.append((2, temp, center))
        for target, coefficients in enumerate(word["scatter"]):
            if j in coefficients:
                instructions.append((1, v + target, temp))
        instructions.append((3, temp, center))
    for section in ("B", "C"):
        for _, d, sources in word[section]:
            instructions.extend((1, d, s) for s in sources)
    return instructions


def positive(instructions, size, reverse):
    values, largest = [1] * size, 1
    for kind, d, s in (instructions[::-1] if reverse else instructions):
        if reverse and kind != 1:
            kind = 5 - kind
        if kind == 1:
            values[d] += values[s]
        elif kind == 2:
            values[d] = values[s]
        else:
            values[d] = 0
        largest = max(largest, values[d])
    return largest


def boundary_columns(word, reverse=False):
    """661 separate Boolean input columns, not the search's row bitsets."""
    n = 2 * word["v"] + word["R"]
    operations = d_atoms(word)
    if reverse:
        operations = operations[::-1]
    output = []
    for column in range(n):
        values = bytearray(n)
        values[column] = 1
        for d, s in operations:
            values[d] ^= values[s]
        output.append(bytes(values))
    return output


def assemble(original, supports, entrance):
    result = copy.deepcopy(original)
    v = original["v"]
    injections = [[0, v + i, sorted(row)] for i, row in enumerate(supports)]
    result["D"] = copy.deepcopy(entrance) + injections + copy.deepcopy(entrance[::-1])
    return result


def outside_d(original, candidate):
    same({k: v for k, v in original.items() if k != "D"},
         {k: v for k, v in candidate.items() if k != "D"}, "non-D field changed")


def check_bill(candidate, certificate):
    same(certificate["D_adds"], len(d_atoms(candidate)), "literal D cost")
    literal = stream(candidate)
    same(certificate["native_ADDs"], sum(kind == 1 for kind, _, _ in literal), "literal total cost")
    size = 2 * candidate["v"] + candidate["R"] + 1
    forward, reverse = (positive(literal, size, direction) for direction in (False, True))
    for key, value in {"F": forward, "B": reverse,
                       "payload_bits": (64 * forward ** 3 * reverse ** 2).bit_length(),
                       "nine_stage_prefix_bits": ((1 << 18) * forward ** 5 * reverse ** 4).bit_length()}.items():
        same(certificate[key], value, "literal bound: " + key)


def recipe_check(original, candidate, certificate):
    need(certificate["format"] == "r439-compensation/1" and type(certificate["seed"]) is int
         and certificate["seed"] == 10, "certificate format/seed")
    need(C["digest"](original) == certificate["baseline_sha256"], "baseline hash")
    need(C["digest"](candidate) == certificate["candidate_sha256"], "candidate hash")
    outside_d(original, candidate)
    need(len(certificate["steps"]) == 306, "step count")
    v, size = original["v"], 2 * original["v"] + original["R"] + 1
    supports = [set() for _ in range(v)]
    for _, destination, sources in original["D"]:
        for source in sources:
            supports[destination - v].symmetric_difference_update({source})
    baseline_cost = len(d_atoms(original))
    entrance, history = [], []
    prefix_instructions = 0
    for index, step in enumerate(certificate["steps"]):
        need(all(type(step[k]) is int for k in ("destination", "source", "gain", "F", "B",
                                               "delta_forward", "delta_reverse")), "noninteger step")
        d, s = step["destination"], step["source"]
        need(0 <= d < v and 0 <= s < v and d != s, "target transvection")
        replacement = supports[d].symmetric_difference(supports[s])
        gain = len(supports[d]) - len(replacement) - 2
        need(gain > 0 and gain == step["gain"], "fully paid strict gain")
        supports[d] = replacement
        entrance.append([0, v + d, [v + s]])
        partial = assemble(original, supports, entrance)
        literal = stream(partial)
        forward, reverse = (positive(literal, size, direction) for direction in (False, True))
        need((forward, reverse) == (step["F"], step["B"]), "literal/incremental step prefix")
        guards(forward, reverse)
        prefix_instructions += 2 * len(literal)
        history.append(dict(step=index + 1, D_adds=len(d_atoms(partial)), F=forward, B=reverse))
    reconstructed = assemble(original, supports, entrance)
    same(reconstructed, candidate, "candidate differs from complete paid recipe")
    check_bill(candidate, certificate)
    savings = sum(x["gain"] for x in certificate["steps"])
    need(baseline_cost == 18085 and len(d_atoms(candidate)) == 6988 and savings == 11097,
         "complete D bill")
    terminal = [len(supports[d]) - len(supports[d] ^ supports[s]) - 2
                for d in range(v) for s in range(v) if d != s]
    need(max(terminal) <= 0, "terminal single-shear improvement remains")
    return {"steps": len(entrance), "helper_injections": sum(map(len, supports)),
            "entrance_adds": len(entrance), "restoration_adds": len(entrance),
            "D_adds_before": baseline_cost, "D_adds_after": len(d_atoms(candidate)),
            "saving": savings, "literal_prefix_instructions_checked": prefix_instructions,
            "prefix_history": history, "terminal_pairs_checked": len(terminal),
            "terminal_max_gain": max(terminal)}


def source_checks(root, original, candidate):
    owner = C["module"]("pinned_r439", Path(root) / C["CHECKER"])
    receipts = {}
    for name, word in (("baseline", original), ("candidate", candidate)):
        _, labels, full, hypotheses, conclusions, info = owner.check(word)
        wanted_h = {key: True for key in hypotheses}
        wanted_c = {key: True for key in conclusions}
        if name == "candidate":
            wanted_h["H2_D_frame0_targets_from_helpers"] = False
            wanted_c["K_equals_D"] = False
        same(hypotheses, wanted_h, "unexpected source interface predicates")
        same(conclusions, wanted_c, "unexpected source conclusion predicates")
        receipts[name] = dict(labels=labels, full=full, hypotheses=hypotheses, conclusions=conclusions, info=info)
    return owner, receipts


def nine_stage_bound(root, native):
    source_path = ("research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/"
                   "vendor/e8-r715-eleven-stage-whole/code/global_k.py")
    syntax = ast.parse((Path(root) / source_path).read_text())
    formulas = [node.value for node in ast.walk(syntax) if isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "prefix" for t in node.targets)]
    expected = ast.parse("(1 << nb) * cf ** (K + 1) * cb ** K", mode="eval").body
    need(len(formulas) == 1 and ast.dump(formulas[0]) == ast.dump(expected), "source prefix formula")
    bridge_equality = ast.parse("nb == 6 * (K - 1)", mode="eval").body
    need(any(isinstance(node, ast.Compare) and ast.dump(node) == ast.dump(bridge_equality)
             for node in ast.walk(syntax)), "source bridge exponent")
    admitted = C["load"](Path(root) / "research/e8-bit-p111-tuned/tune/EXPECTED.json")["nine"]["bit"]
    need(admitted["charged_prefix_bits"] == 192, "source nine-stage charge")
    output = {"formula": "2^18 * F^5 * B^4", "source_charge_bits": 192}
    for name in ("baseline", "candidate"):
        bounds = native[name]["staged"]["9"]["signed_lift_prefix"]
        forward, reverse = [int(x["cancellation_free_signed_row_l1_upper"]) for x in bounds]
        value = (1 << 18) * forward ** 5 * reverse ** 4
        need(value < 1 << 192, "nine-stage invoice bound")
        output[name] = {"bound": str(value), "bits": value.bit_length()}
    need(output["baseline"]["bits"] == admitted["prefix_bits"] == 177, "source baseline prefix")
    need(output["candidate"]["bits"] == 189, "candidate nine-stage prefix")
    return output


def controls(original, candidate, certificate, baseline_columns):
    rejected = []

    def reject(name, action, message):
        try:
            action()
        except ValueError as error:
            need(message in str(error), "unexpected control failure: " + name + ": " + str(error))
            rejected.append(name)
        else:
            raise ValueError("control accepted: " + name)

    def boundary(word):
        need(boundary_columns(word) == baseline_columns, "D boundary mismatch")

    count, v = len(certificate["steps"]), original["v"]
    changed = copy.deepcopy(candidate)
    del changed["D"][:count]
    columns = boundary_columns(changed)
    need(columns[2 * v:] == baseline_columns[2 * v:], "zero-target control premise")
    need(columns[v:2 * v] != baseline_columns[v:2 * v], "arbitrary targets are necessary")
    reject("missing entrance passes helper-only checking", lambda: boundary(changed), "D boundary")
    changed = copy.deepcopy(candidate)
    changed["D"].pop()
    reject("missing target restoration", lambda: boundary(changed), "D boundary")
    changed = copy.deepcopy(candidate)
    changed["D"][count][2].pop()
    reject("missing recoded helper injection", lambda: boundary(changed), "D boundary")
    changed = copy.deepcopy(candidate)
    changed["D"][-count:] = copy.deepcopy(changed["D"][:count])
    reject("undo in forward order", lambda: boundary(changed), "D boundary")
    changed = copy.deepcopy(candidate)
    changed["D"][0][0] = 1
    reject("nonzero D frame", lambda: d_atoms(changed), "D frame")
    changed = copy.deepcopy(candidate)
    changed["D"][0][1] = 2 * v
    reject("temporary helper write", lambda: d_atoms(changed), "only writes targets")
    changed = copy.deepcopy(candidate)
    changed["D"][0][2] = [0]
    reject("source read at frame zero", lambda: d_atoms(changed), "D legal donor")
    underpriced = copy.deepcopy(certificate)
    underpriced["D_adds"] -= count
    reject("undercharged restoration", lambda: check_bill(candidate, underpriced), "literal D cost")
    reject("local payload overrun", lambda: guards(49347, 1 << 30), "local payload")
    reject("nine-stage overrun below local cap", lambda: guards(49347, 16913321), "nine-stage")
    reject("forward guard overrun", lambda: guards(49348, 1), "forward guard")
    reject("boolean masquerading as count", lambda: same({"count": 1}, {"count": True}, "typed receipt"), "typed")
    changed = copy.deepcopy(candidate)
    changed["C"].pop()
    reject("unrelated cleanup change", lambda: outside_d(original, changed), "non-D")
    changed_recipe = copy.deepcopy(certificate)
    changed_recipe["steps"][0]["destination"] = True
    reject("boolean target index", lambda: recipe_check(original, candidate, changed_recipe), "noninteger")
    # A positive control: cancelling target operations are legal and cost two ADDs.
    neutral = copy.deepcopy(candidate)
    neutral["D"][:0] = [[0, v, [v + 1]], [0, v, [v + 1]]]
    need(boundary_columns(neutral) == baseline_columns, "neutral pair endpoint")
    need(len(d_atoms(neutral)) == len(d_atoms(candidate)) + 2, "neutral pair must be paid")
    return {"rejected": rejected, "paid_neutral_pair": 2}


def run(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    manifest = C["pins"](root)
    output.mkdir(parents=True, exist_ok=False)
    original = C["load"](root / C["WORD"])
    candidate = C["load"](C["HERE"] / "candidate.json.gz")
    certificate = C["load"](C["HERE"] / "CERTIFICATE.json")
    print("reproduce complete seed-10 nomination", flush=True)
    generated = output / "regenerated"
    subprocess.run([sys.executable, "-I", "-B", C["HERE"] / "build.py", "--source-root", root,
                    "--output", generated], check=True)
    same(C["load"](generated / "CERTIFICATE.json"), certificate, "certificate regeneration")
    same(C["load"](generated / "candidate.json.gz"), candidate, "candidate regeneration")
    print("independent set-valued recipe; literal bounds for every accepted step", flush=True)
    recipe = recipe_check(original, candidate, certificate)
    print("661 separate input columns in both D directions; unchanged full source checks", flush=True)
    baseline_columns = boundary_columns(original)
    for word in (original, candidate):
        for reverse in (False, True):
            need(boundary_columns(word, reverse) == baseline_columns, "arbitrary-input D boundary")
    _, source = source_checks(root, original, candidate)
    negative = controls(original, candidate, certificate, baseline_columns)
    print("unchanged native legality and 5/9/11-stage checks for both complete words", flush=True)
    native = C["module"]("r439_native", C["HERE"] / "native.py").run(
        root, root / C["WORD"], C["HERE"] / "candidate.json.gz", output / "native")
    return {"status": "PASS_R439_TARGET_COMPENSATION", "source_files": manifest["files"],
            "predecessor_files": manifest["local_files"], "recipe": recipe, "boundary_columns": 661,
            "boundary_words_and_directions": 4, "baseline_sha256": C["digest"](original),
            "candidate_sha256": C["digest"](candidate), "certificate_sha256": C["digest"](certificate),
            "source_checks": source, "controls": negative, "native": native,
            "nine_stage_prefix_bound": nine_stage_bound(root, native)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=C["ROOT"])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--expected", type=Path, default=C["HERE"] / "EXPECTED.json")
    args = parser.parse_args()
    if args.output:
        need(not args.output.exists(), "output already exists")
    if args.receipt:
        need(not args.receipt.exists(), "receipt already exists")
    expected = C["load"](args.expected)
    with tempfile.TemporaryDirectory(prefix="r439-target-") as temp:
        report = run(args.source_root, args.output or Path(temp) / "run")
        same(report, expected, "receipt differs from EXPECTED.json")
        if args.receipt:
            C["write"](args.receipt, report)
    print("PASS_R439_TARGET_COMPENSATION: D=18085->6988 ADDs=24305->13208 steps=306 nine_bits=189; semantic D; no new kappa")
