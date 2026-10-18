#!/usr/bin/env python3
"""Exact composition of pinned PR922 contractions and PR924 rescaling.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The fusion admission follows PR922; arbitrary-input primitive replay and the
source-bound native pipeline reuse PR924/PR681/PR696, with attribution in
COMPOSITION.md. No solver, Git checkout, or network is needed for verification.
"""
import argparse
import copy
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
PINNED_FILES = {"verify.py", "CERTIFICATE.json", "EXPECTED.json",
                "SOURCE-PINS.json", "PR922-CIRCUIT.json"}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load():
    cert = json.loads((HERE / "COMPOSITION.json").read_text())
    need(cert["format"] == "complex-factory-pr922-pr924-composition-v1", "certificate format")
    need(set(cert["pins"]) == PINNED_FILES, "incomplete composition source pins")
    for name, expected in cert["pins"].items():
        need(hashlib.sha256((HERE / name).read_bytes()).hexdigest() == expected,
             "composition source pin: " + name)
    need(cert["pr922_head"] == "efd5643c0016b6c6dac26e9ed7dee8a75295ff2a"
         and cert["pr924_head"] == cert["followup_base"] ==
         "e6f3cb8ca813dfc54c77738c9acd74a536b607fd", "predecessor heads")
    need(cert["common_base"] == "f567884aeb8851b6e794af1184119a3bfbe1e631"
         and cert["new_kappa"] is False, "scope changed")
    spec = importlib.util.spec_from_file_location("composition_pr924", HERE / "verify.py")
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    pins = v.source_check()
    return v, cert, pins


def gates(word):
    for op in word:
        need(isinstance(op, list) and op and op[0] in ("add", "scale"), "invalid gate")
        need(len(op) == (6 if op[0] == "add" else 5), "gate arity")
        need(all(type(x) is int for x in op[1:-1]), "integer gate fields required")
        need(isinstance(op[-1], list) and all(type(x) is int for x in op[-1]), "frame fields")


def commute(a, b):
    if a[0] == b[0] == "add":
        return a[1] != b[2] and b[1] != a[2]
    if a[0] == b[0] == "scale":
        return True
    scale, add = (a, b) if a[0] == "scale" else (b, a)
    return scale[1] not in add[1:3]


def fuse(tagged, recipes, old):
    word = copy.deepcopy(tagged)
    for recipe in recipes:
        labels, order = recipe["labels"], recipe["order"]
        need(len(labels) == 3 and len(set(labels)) == 3
             and all(type(x) is int for x in labels), "fusion labels")
        need(len(order) == 2 and len(set(order)) == 2
             and all(type(x) is int and 0 <= x < 3 for x in order), "fusion order")
        indices = [next(i for i, (label, _) in enumerate(word) if label == value)
                   for value in labels]
        i, j, k = indices
        need(i < j < k, "fusion chronology")
        triple = [word[x] for x in indices]
        need(all(op[0] == "add" for _, op in triple), "fusion must contain additions")
        need(all(commute(word[j][1], word[x][1]) for x in range(i + 1, j)),
             "fusion crosses second-gate dependency")
        need(all(commute(word[k][1], word[x][1]) for x in range(i + 1, k) if x != j),
             "fusion crosses third-gate dependency")
        pair = [triple[x] for x in order]
        need(old.columns([op for _, op in triple]) == old.columns([op for _, op in pair]),
             "fusion changes map")
        word = word[:i] + pair + [entry for index, entry in enumerate(word[i + 1:], i + 1)
                                  if index not in (j, k)]
    return word


def rescale(tagged):
    word = copy.deepcopy(tagged)
    for label, before, register in ((16, 31, 0), (22, 32, 1)):
        index = next(i for i, (tag, _) in enumerate(word) if tag == label)
        entry = word.pop(index)
        need(entry[1][:-1] == ["scale", register, 2, 1], "doubling precondition")
        index = next(i for i, (tag, _) in enumerate(word) if tag == before)
        word.insert(index, entry)
    for label, expected, replacement in ((26, ["add", 1, 6, 2, 1], [1, 1]),
                                          (30, ["add", 3, 0, -1, 2], [-1, 1])):
        op = next(op for tag, op in word if tag == label)
        need(op[:-1] == expected, "coefficient precondition")
        op[3:5] = replacement
    return word


def reconstruct(v, cert, src, old):
    predecessor = v.read(HERE / "PR922-CIRCUIT.json")
    gauge = v.read(HERE / "CERTIFICATE.json")
    tagged = list(enumerate(copy.deepcopy(src["replacement"])))
    current, recipes = copy.deepcopy(tagged), []
    for step in predecessor["fusions"]:
        indices = step["indices"]
        need(len(indices) == 3 and all(type(x) is int for x in indices)
             and 0 <= indices[0] < indices[1] < indices[2] < len(current), "PR922 indices")
        recipe = {"labels": [current[x][0] for x in indices], "order": step["pair_order"]}
        recipes.append(recipe)
        current = fuse(current, [recipe], old)
        word = [op for _, op in current]
        need(len(word) == step["gates"] and len(old.lowering(word)) == step["primitive_cost"],
             "PR922 step cost")
    need(recipes == cert["recipes"], "label recipe differs from PR922")
    fused = [op for _, op in current]
    need(fused == predecessor["replacement"], "PR922 witness differs")
    scaled = rescale(tagged)
    need([op for _, op in scaled] == gauge["budget_replacement"], "PR924 witness differs")
    first_fused = rescale(current)
    first_scaled = fuse(scaled, recipes, old)
    need(first_fused == first_scaled, "application orders differ")
    need([label for label, _ in first_fused] == cert["combined_labels"], "combined labels differ")
    need([op for _, op in first_fused] == cert["replacement"], "combined witness differs")
    versions = {"baseline": src["replacement"], "pr922": fused,
                "pr924": gauge["budget_replacement"], "combined": cert["replacement"]}
    for word in versions.values():
        gates(word)
    return versions


def local(v, old, lower, src, versions):
    variants = {"main": lambda x: x, "cleanup": old.inverse,
                "dual_main": old.dual, "dual_cleanup": lambda x: old.dual(old.inverse(x))}
    prices = {"baseline": (34, 128, 81), "pr922": (32, 120, 77),
              "pr924": (34, 126, 77), "combined": (32, 118, 73)}
    result = {}
    for name, word in versions.items():
        macros, horner, copied = prices[name]
        need(len(word) == macros, "local macro cost")
        admitted = {} if name == "baseline" else old.validate(
            versions["baseline"], word, src["frame"], src["entry_frames"])
        metrics = {}
        for direction, transform in variants.items():
            original, candidate = transform(versions["baseline"]), transform(word)
            rows, stats = v.primitive_replay(v.circuit_primitives(lower, candidate), 8)
            expected, baseline = v.primitive_replay(v.circuit_primitives(lower, original), 8)
            need(rows == expected, "local primitive map differs")
            need(len(old.lowering(candidate)) == horner and
                 stats["primitive_count_one_component"] == copied, "local primitive cost")
            need(stats["fractional_bits"] <= baseline["fractional_bits"] and
                 v.Q(stats["exact_prefix_row_l1"]) <= v.Q(baseline["exact_prefix_row_l1"]),
                 "local primitive precision grew")
            metrics[direction] = stats
        result[name] = {"macros": macros, "horner": horner, "pr696": copied,
                        "native_admission": admitted, "primitive_replay": metrics}
    # Stronger admission: rescaling also preserves the already-fused envelopes.
    result["combined_relative_to_pr922"] = old.validate(
        versions["pr922"], versions["combined"], src["frame"], src["entry_frames"])
    return result


def negative_controls(v, old, lower, src, cert, versions):
    controls = []

    def reject(name, reason, function):
        try:
            function()
        except ValueError as error:
            need(reason in str(error), name + ": unexpected rejection: " + str(error))
            controls.append({"name": name, "reason": reason})
        else:
            raise ValueError("negative control accepted: " + name)

    def check(word):
        gates(word)
        old.validate(src["replacement"], word, src["frame"], src["entry_frames"])
        need(len(v.circuit_primitives(lower, word)) == 73, "combined primitive cost")

    good = versions["combined"]
    for i in range(len(good)):
        reject("delete_combined_gate_" + str(i), "exact local map differs",
               lambda i=i: check(good[:i] + good[i + 1:]))
    bad = copy.deepcopy(good)
    bad[0][3] = True
    reject("boolean_coefficient", "integer gate fields required", lambda: check(bad))
    bad = copy.deepcopy(good)
    bad[0][-1][0] ^= 1
    reject("wrong_frame", "changed frame path", lambda: check(bad))
    bad = copy.deepcopy(good)
    bad[cert["combined_labels"].index(30)][3] = 1
    reject("wrong_rescaled_sign", "exact local map differs", lambda: check(bad))
    recipes = copy.deepcopy(cert["recipes"])
    recipes[0]["order"] = [1, 2]
    reject("wrong_fusion_order", "fusion changes map",
           lambda: fuse(list(enumerate(src["replacement"])), recipes, old))
    bad = copy.deepcopy(good) + [["scale", 0, -1, 1, src["frame"]]] * 2
    reject("endpoint_neutral_extra_cost", "combined primitive cost", lambda: check(bad))
    stream = v.circuit_primitives(lower, good)
    dirty = [op for op in stream if tuple(op) != ("clear", ("W", 0))]
    reject("uncleared_private_work", "private dirt not cleared",
           lambda: v.primitive_replay(dirty, 8))
    return controls


def make_raw(v, old, raw, src, blocks, template):
    word = copy.deepcopy(raw)
    for block in reversed(blocks):
        regs = [r - 16 if r >= 240 else r - 8
                for r in block["registers_before_112_port_restriction"]]

        def relocate(events):
            result = copy.deepcopy(events)
            for e in result:
                e[1] = regs[e[1]]
                if e[0] == "add":
                    e[2] = regs[e[2]]
                e[-1] = block["frame"]
            return result

        start, end = block["A_window_zero_based"]
        need(raw["A"][start:end] == relocate(src["original"]), "raw window differs")
        word["A"][start:end] = relocate(template)
    word["cleanup"] = old.inverse([e for e in word["A"] + word["B"] if not 112 <= e[1] < 224])
    for e in word["cleanup"]:
        e[-1] = [256, 128, 64, 32, 16, 8, 4, 2, 1]
    return word


def full(v, old, lower, src, versions, out):
    blocks = v.read(v.FACTORY / "BLOCKS.json")
    old.run(v.FACTORY / "extract.py", [out / "original"], out / "constructor.log")
    old.bind_blocks(blocks, v.read(out / "original/WINDOWS.json"), src)
    raw = v.read(out / "original/FULL-WORD.json.gz")
    results, native_words = {}, {}
    for name, template in versions.items():
        for block in blocks:
            a, b = copy.deepcopy(src["replacement"]), copy.deepcopy(template)
            for op in a + b:
                op[-1] = block["frame"]
            if name != "baseline":
                old.validate(a, b, block["frame"], block["entry_frames"])
        word = make_raw(v, old, raw, src, blocks, template)
        path = out / (name + "-raw.json.gz")
        path.write_bytes(gzip.compress(v.canonical(word), mtime=0))
        record, native_word = old.native(path, out / name, out)
        native_words[name] = native_word
        lowered = {}
        for direction, events in v.read(out / name / "LOCAL-PROGRAMS.json.gz").items():
            stream, tags, h = [], Counter(), hashlib.sha256()
            for event in events:
                if event[0] == "scalar":
                    for primitive in lower.lower(event[1]):
                        stream.append(primitive)
                        tags[primitive[0]] += 2
                        h.update(v.canonical([event[2], primitive]) + b"\n")
            rows, metrics = v.primitive_replay(stream, 716, 8)
            for r in range(716):
                expected = {r: v.Q(1)}
                if direction == "forward" and 112 <= r < 224:
                    expected[r - 112] = v.Q(1)
                elif direction == "backward" and r < 112:
                    expected[r + 112] = v.Q(-1)
                need(rows["L", r] == expected, "full primitive map differs")
            lowered[direction] = {**metrics, "real_primitives": 2 * len(stream),
                                  "primitive_tags": dict(sorted(tags.items())),
                                  "primitive_stream_sha256": h.hexdigest()}
        results[name] = {"native": record, "pr696": lowered}
    retained = v.read(HERE / "EXPECTED.json")["full"]
    need(results["baseline"] == retained["baseline"], "retained baseline differs")
    need(results["pr924"] == retained["candidate"], "retained PR924 differs")
    for name in ("pr922", "pr924", "combined"):
        for key in ("local_profile", "start", "final", "compensation", "ports", "centers",
                    "center_frames", "frames", "edges"):
            need(native_words["baseline"][key] == native_words[name][key], "native invariant: " + key)
    accounting = {}
    for name, record in results.items():
        macros = max(x["scalar_macros"] for x in record["native"]["emitted"].values())
        children = sum(record["native"]["emitted"]["forward"]["paid_profile"].values())
        adapters = 16 * (macros + children + 716 + 8) + 64 * 73
        accounting[name] = {"macros": macros, "children": children,
                            "adapter_allowance": adapters,
                            "pr696_local_bound": adapters * (64 * 74**3) + max(
                                x["real_primitives"] for x in record["pr696"].values())}
    for direction in ("forward", "backward"):
        base, fusion, gauge, both = (results[n] for n in ("baseline", "pr922", "pr924", "combined"))
        for value, saved in ((fusion, 224), (gauge, 224), (both, 448)):
            need(base["pr696"][direction]["real_primitives"] - value["pr696"][direction]["real_primitives"] == saved,
                 "full PR696 saving")
            need(value["native"]["emitted"][direction]["paid_profile"] ==
                 base["native"]["emitted"][direction]["paid_profile"], "paid profile changed")
        need(base["native"]["emitted"][direction]["scalar_macros"] -
             both["native"]["emitted"][direction]["scalar_macros"] == 56, "full macro saving")
        need(base["native"]["emitted"][direction]["real_component_primitive_bound"] -
             both["native"]["emitted"][direction]["real_component_primitive_bound"] == 560,
             "original Horner saving")
        need(both["native"]["local"]["local"][direction]["prefix_l1_upper"] ==
             fusion["native"]["local"]["local"][direction]["prefix_l1_upper"], "fused positive prefix changed")
        need(both["pr696"][direction]["fractional_bits"] <= base["pr696"][direction]["fractional_bits"]
             and v.Q(both["pr696"][direction]["exact_prefix_row_l1"]) <=
             v.Q(base["pr696"][direction]["exact_prefix_row_l1"]), "full scalar precision grew")
    need(accounting["combined"]["pr696_local_bound"] - accounting["pr922"]["pr696_local_bound"] == -224,
         "combined versus PR922 local bill")
    need(accounting["combined"]["pr696_local_bound"] - accounting["baseline"]["pr696_local_bound"] == -23237165504,
         "combined versus baseline local bill")
    bad = make_raw(v, old, raw, src, blocks, versions["combined"])
    bad["cleanup"].pop()
    path = out / "missing-cleanup.json.gz"
    path.write_bytes(gzip.compress(v.canonical(bad), mtime=0))
    try:
        old.native(path, out / "bad-cleanup", out)
    except ValueError:
        need("cleanup is not the literal reversed inverse" in
             (out / "bad-cleanup-native.log").read_text(), "unexpected cleanup rejection")
    else:
        raise ValueError("missing cleanup accepted")
    return {"versions": results, "accounting": accounting, "blocks": len(blocks),
            "physical_negative_control": "missing cleanup rejected by unchanged native auditor",
            "invoice_scope": "Retained local formula only; not a global invoice or runtime measurement."}


def verify(out, local_only=False):
    v, cert, pins = load()
    old = v.module("composition_factory", v.FACTORY / "verify.py")
    lower = v.module("composition_lowering", v.ROOT / "research/complex-dyadic-lowering/lower.py")
    src = v.read(v.FACTORY / "CIRCUIT.json")
    versions = reconstruct(v, cert, src, old)
    result = {"status": "PASS_FACTORY_PR922_PR924_COMPOSITION", "pr922_head": cert["pr922_head"],
              "pr924_head": cert["pr924_head"], "common_source_files": len(pins["files"]),
              "both_application_orders_identical": True, "new_kappa": False,
              "local": local(v, old, lower, src, versions),
              "controls": negative_controls(v, old, lower, src, cert, versions)}
    if not local_only:
        result["full"] = full(v, old, lower, src, versions, out)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="retain artifacts in a new directory")
    parser.add_argument("--write", type=Path, help="write a new development receipt")
    parser.add_argument("--local-only", action="store_true", help="skip the full raw replay")
    args = parser.parse_args()
    if args.write:
        need(not args.write.exists(), "receipt output already exists")
    if args.out:
        args.out.mkdir(parents=True, exist_ok=False)
        result = verify(args.out.resolve(), args.local_only)
    else:
        with tempfile.TemporaryDirectory(prefix="factory-pr922-pr924-") as directory:
            result = verify(Path(directory), args.local_only)
    if args.write:
        with args.write.open("x") as handle:
            handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((HERE / "COMPOSITION-RESULT.json").read_text())
        if args.local_only:
            expected.pop("full")
        need(result == expected, "composition receipt differs")
    suffix = "local_only=True" if args.local_only else "blocks=14 saved=448,448 extra_vs_each=224,224"
    print("PASS_FACTORY_PR922_PR924_COMPOSITION macros=32 primitives=73 " + suffix
          + " controls=" + str(len(result["controls"])) + " no_new_kappa")


if __name__ == "__main__":
    main()
