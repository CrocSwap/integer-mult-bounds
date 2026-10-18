#!/usr/bin/env python3
"""Set-valued independent census and full dirty-input verification.

No search.py imports. Source geometry and physical records use unchanged,
source-pinned eumemic/Dylan Crow checkers, with their notices retained.
Predecessor-recipe and literal-evaluator patterns follow @woklerx's PR1040
research/r439-target-retune-seed14/verify.py (Apache-2.0, Codex assistance).
Hanson Sun (@bbMisk), substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
from collections import Counter
import copy
import gzip
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "cd91ac8e2652bfee6bf09da3b8724253bcf78f5f"
ORIGINAL = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
PARENT = "research/r439-helper-stars-seed19/candidate.json.gz"
HCERT = "research/r439-helper-stars-seed19/CERTIFICATE.json"
TCERT = "research/r439-target-compensation/CERTIFICATE.json"
OWNER = "research/e8-bit-p111-tuned/code/xcheck_p.py"
EXPORT = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
FORMULA = "research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py"
CHARGE = "research/e8-bit-p111-tuned/tune/EXPECTED.json"
INPUTS = {ORIGINAL, PARENT, HCERT, TCERT, OWNER, EXPORT, FORMULA, CHARGE}
PROVENANCE = {"docs/research/agent-task-catalog.json", "certificates/selected-result.json"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def parse(raw):
    return json.loads(raw, object_pairs_hook=unique_pairs,
                      parse_constant=lambda _: require(False, "nonfinite JSON"))


def read(path):
    raw = Path(path).read_bytes()
    return parse(gzip.decompress(raw) if str(path).endswith(".gz") else raw)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def same(actual, expected, label):
    require(canonical(actual) == canonical(expected), label)


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def source_pins(manifest):
    require(manifest["schema_version"] == 1 and manifest["base_commit"] == BASE, "source base")
    entries = manifest["files"]
    require(len(entries) == len(INPUTS | PROVENANCE), "source inventory length")
    require({r["path"] for r in entries if r["usage"] == "input"} == INPUTS, "exact live input inventory")
    require({r["path"] for r in entries if r["usage"] == "provenance"} == PROVENANCE, "provenance inventory")
    for row in entries:
        if row["usage"] == "input":
            raw = (ROOT / row["path"]).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source digest: " + row["path"])
            git_blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            require(git_blob == row["git_blob"], "source blob: " + row["path"])


def recipe(original, parent):
    helpers = [[0, 222 + p["a"], [222 + p["b"]]] for p in read(ROOT / HCERT)["steps"]]
    targets = [[0, 111 + p["destination"], [111 + p["source"]]] for p in read(ROOT / TCERT)["steps"]]
    require(len(helpers) == 221 and len(targets) == 306, "predecessor lengths")
    rows = [set() for _ in range(111)]
    for f, d, sources in original["D"]:
        require(f == 0 and 111 <= d < 222 and all(222 <= s < 661 for s in sources), "original D contract")
        rows[d - 111].symmetric_difference_update(s - 222 for s in sources)
    for _, d, sources in targets:
        rows[d - 111].symmetric_difference_update(rows[sources[0] - 111])
    for _, d, sources in reversed(helpers):
        for row in rows:
            if d - 222 in row:
                row.symmetric_difference_update({sources[0] - 222})
    core = [[0, 111 + i, [222 + s for s in sorted(row)]] for i, row in enumerate(rows)]
    same(helpers + targets + core + targets[::-1] + helpers[::-1], parent["D"], "rederive complete PR967 D")
    same({k: v for k, v in parent.items() if k != "D"},
         {k: v for k, v in original.items() if k != "D"}, "unchanged non-D source")
    return helpers, targets, rows


def interaction_table():
    table = []
    for x, y, z, t in itertools.product((0, 1), repeat=4):
        m = [[x, z], [y, t]]
        weight = lambda a: sum(sum(row) for row in a)
        def row_step(a):
            return [[a[0][j] ^ a[1][j] for j in range(2)], a[1][:]]
        def col_step(a):
            return [[row[0] ^ row[1], row[1]] for row in a]
        joint = weight(m) - weight(col_step(row_step(m)))
        separate = (weight(m) - weight(row_step(m))) + (weight(m) - weight(col_step(m)))
        table.append([x, y, z, t, joint - separate])
    require(max(row[-1] for row in table) == 2 and min(row[-1] for row in table) == -2, "interaction bound")
    return table


def tie(case):
    return hashlib.sha256(("13:" + ":".join(map(str, case[:4]))).encode("ascii")).hexdigest()


def independent_census(rows):
    columns = [{i for i, row in enumerate(rows) if j in row} for j in range(439)]
    target_hist, helper_hist = Counter(), Counter()
    near_t, near_h = [], []
    for a in range(111):
        for b in range(111):
            if a != b:
                gain = len(rows[a]) - len(rows[a].symmetric_difference(rows[b])) - 2
                target_hist[gain] += 1
                if gain in (-1, 0):
                    near_t.append((a, b, gain))
    for d in range(439):
        for s in range(439):
            if d != s:
                gain = len(columns[s]) - len(columns[s].symmetric_difference(columns[d])) - 2
                helper_hist[gain] += 1
                if gain in (-1, 0):
                    near_h.append((d, s, gain))
    cases, explicit_hist = [], Counter()
    for a, b, gt in near_t:
        for d, s, gh in near_h:
            if gt + gh <= -2:
                continue
            cs, cd = set(columns[s]), set(columns[d])
            if b in cs:
                cs.symmetric_difference_update({a})
            if b in cd:
                cd.symmetric_difference_update({a})
            gain = gt + len(cs) - len(cs.symmetric_difference(cd)) - 2
            explicit_hist[gain] += 1
            if gain > 0:
                cases.append([a, b, d, s, gt, gh, gain])
    cases.sort(key=lambda c: (-c[6], tie(c), c[:4]))
    domain = sum(n for g, n in target_hist.items() if g <= 0) * sum(n for g, n in helper_hist.items() if g <= 0)
    explicit = sum(explicit_hist.values())
    return {"all_target_pairs": sum(target_hist.values()), "all_helper_pairs": sum(helper_hist.values()),
            "target_gain_histogram": {str(k): v for k, v in sorted(target_hist.items())},
            "helper_gain_histogram": {str(k): v for k, v in sorted(helper_hist.items())},
            "nonpositive_unilateral_domain": domain,
            "excluded_by_interaction_upper_bound": domain - explicit,
            "explicit_interaction_cases": explicit,
            "explicit_gain_histogram": {str(k): v for k, v in sorted(explicit_hist.items())},
            "positive_cases": cases, "positive_count": len(cases),
            "positive_cases_sha256": digest(cases), "interaction_table": interaction_table()}


def construct(parent, helpers, targets, rows, case, use_target=True, use_helper=True):
    a, b, d, s = case[:4]
    transformed = [set(row) for row in rows]
    if use_helper:
        for row in transformed:
            if d in row:
                row.symmetric_difference_update({s})
    if use_target:
        transformed[a].symmetric_difference_update(transformed[b])
    h = [[0, 222 + d, [222 + s]]] if use_helper else []
    t = [[0, 111 + a, [111 + b]]] if use_target else []
    core = [[0, 111 + i, [222 + j for j in sorted(row)]] for i, row in enumerate(transformed)]
    word = copy.deepcopy(parent)
    word["D"] = helpers + targets + h + t + core + t + h + targets[::-1] + helpers[::-1]
    return word


def instructions(word, only_d=False):
    result = []
    for section in ("D",) if only_d else ("D", "A"):
        for _, d, sources in word[section]:
            result += [("add", d, s) for s in sources]
    if only_d:
        return result
    for j, source in enumerate(word["ret"]):
        result.append(("copy", 661, source))
        for i, sources in enumerate(word["scatter"]):
            if j in sources:
                result.append(("add", 111 + i, 661))
        result.append(("erase", 661, source))
    for section in ("B", "C"):
        for _, d, sources in word[section]:
            result += [("add", d, s) for s in sources]
    return result


def evaluate(word, reverse=False, only_d=False, positive=False):
    values = [1] * 661 + [0] if positive else [{i} for i in range(661)] + [set()]
    stream = instructions(word, only_d)
    maximum = 1
    for kind, d, s in reversed(stream) if reverse else stream:
        if reverse and kind != "add":
            kind = "erase" if kind == "copy" else "copy"
        if kind == "add":
            if positive:
                values[d] += values[s]
            else:
                values[d].symmetric_difference_update(values[s])
        elif kind == "copy":
            require(not values[d], "copy destination must be clean")
            values[d] = values[s] if positive else set(values[s])
        else:
            if not positive:
                require(values[d] == values[s], "erase must match live copied value")
            values[d] = 0 if positive else set()
        if positive:
            maximum = max(maximum, values[d])
    require(not values[661], "scratch restored")
    return maximum if positive else [sorted(v) for v in values[:661]]


def admitted(local, nine):
    return local < (1 << 104) and nine < (1 << 192)


def invoice(word):
    f = evaluate(word, positive=True)
    b = evaluate(word, reverse=True, positive=True)
    local, nine = 64 * f**3 * b**2, (1 << 18) * f**5 * b**4
    return {"ADDs": len([r for r in instructions(word) if r[0] == "add"]),
            "D_ADDs": len(instructions(word, only_d=True)), "F": f, "B": b,
            "local_bound": str(local), "nine_stage_bound": str(nine),
            "admitted": admitted(local, nine)}


def formula_check():
    syntax = ast.parse((ROOT / FORMULA).read_text())
    assignments = [n.value for n in ast.walk(syntax) if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "prefix" for t in n.targets)]
    expected = ast.parse("(1 << nb) * cf ** (K + 1) * cb ** K", mode="eval").body
    require(len(assignments) == 1 and ast.dump(assignments[0]) == ast.dump(expected), "nine-stage source formula")
    bridge = ast.dump(ast.parse("nb == 6 * (K - 1)", mode="eval").body)
    require(any(isinstance(n, ast.Compare) and ast.dump(n) == bridge for n in ast.walk(syntax)), "bridge exponent")
    require(read(ROOT / CHARGE)["nine"]["bit"]["charged_prefix_bits"] == 192, "retained nine-stage charge")


def geometry_and_records(parent, candidate):
    spec = importlib.util.spec_from_file_location("retained_r439_owner", ROOT / OWNER)
    owner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(owner)
    _, labels, full, hypotheses, conclusions, info = owner.check(candidate)
    require({k for k, v in hypotheses.items() if not v} == {"H2_D_frame0_targets_from_helpers"}, "inherited H2 failure only")
    require({k for k, v in conclusions.items() if not v} == {"K_equals_D"}, "inherited literal K failure only")
    exported = {}
    with tempfile.TemporaryDirectory(prefix="r439-mixed-") as directory:
        folder = Path(directory)
        for name, word in (("parent", parent), ("candidate", candidate)):
            source = folder / (name + ".json")
            source.write_bytes(canonical(word))
            output = folder / name
            done = subprocess.run([sys.executable, "-I", "-B", str(ROOT / EXPORT), str(source), str(output)],
                                  capture_output=True, text=True, timeout=90)
            require(done.returncode == 0, "unchanged exporter: " + done.stderr)
            records = list(struct.iter_unpack("<6i", (output / "249-records.bin").read_bytes()))
            exported[name] = {"records": records, "states": read(output / "249-states.json"),
                              "frames": read(output / "frames.json")}
    p, c = exported["parent"], exported["candidate"]
    same(p["states"], c["states"], "all role endpoints")
    same(p["frames"], c["frames"], "all rational frames")
    same([r for r in p["records"] if r[0] != 1], [r for r in c["records"] if r[0] != 1], "ordered MOVE/COPY/ERASE stream")
    summary = {}
    for name, data in exported.items():
        records = data["records"]
        hist = Counter(r[4] if r[0] == 0 else r[5] for r in records if r[0] in (0, 2))
        summary[name] = {"records": len(records), "ADDs": sum(r[0] == 1 for r in records),
                         "MOVE": sum(r[0] == 0 for r in records), "COPY": sum(r[0] == 2 for r in records),
                         "ERASE": sum(r[0] == 3 for r in records),
                         "paid_histogram": {str(k): v for k, v in sorted(hist.items())},
                         "rank_mass": sum(k * v for k, v in hist.items())}
        require(summary[name]["ADDs"] == invoice(parent if name == "parent" else candidate)["ADDs"], "export ADD price")
        require(summary[name]["rank_mass"] == 5129 and summary[name]["COPY"] == 9, "retained paid profile")
    return {"hypotheses": hypotheses, "conclusions": conclusions, "labels": labels,
            "full_frame": full, "geometry_info": info, "exports": summary}


def expect_rejection(label, fn):
    try:
        fn()
    except (ValueError, KeyError):
        return label
    raise ValueError("negative control unexpectedly accepted: " + label)


def controls(parent, candidate, chosen, manifest, certificate):
    rejected = []
    expected_d = evaluate(parent, only_d=True)
    for index, label in ((527, "omit_helper_preparation"), (528, "omit_target_preparation"),
                         (640, "omit_target_restoration"), (641, "omit_helper_restoration")):
        bad = copy.deepcopy(candidate)
        del bad["D"][index]
        rejected.append(expect_rejection(label, lambda b=bad: same(evaluate(b, only_d=True), expected_d, label)))
    for index, label in ((527, "reverse_helper_direction"), (528, "reverse_target_direction")):
        bad = copy.deepcopy(candidate)
        f, d, ss = bad["D"][index]
        bad["D"][index] = [f, ss[0], [d]]
        rejected.append(expect_rejection(label, lambda b=bad: same(evaluate(b, only_d=True), expected_d, label)))
    bad = copy.deepcopy(candidate)
    bad["D"][529:640] = copy.deepcopy(parent["D"][527:638])
    rejected.append(expect_rejection("omit_middle_substitution", lambda: same(evaluate(bad, only_d=True), expected_d, "uncorrected middle")))
    false_bill = invoice(candidate)
    false_bill["ADDs"] -= 4
    rejected.append(expect_rejection("free_preparation_restoration", lambda: same(invoice(candidate), false_bill, "four unpaid gates")))
    rejected.append(expect_rejection("add_unilateral_savings_without_interaction",
                    lambda: same(chosen[4] + chosen[5], chosen[6], "missing mixed interaction")))
    wrong_table = [[x, y, z, t, (x ^ y) + (x ^ z) - (x ^ y ^ z) - x]
                   for x, y, z, t in itertools.product((0, 1), repeat=4)]
    rejected.append(expect_rejection("omit_cross_entry_in_interaction",
                    lambda: same(wrong_table, interaction_table(), "missing fourth matrix entry")))
    require(not admitted(1 << 104, 0) and not admitted(0, 1 << 192), "strict precision boundary")
    rejected += ["local_cap_equality", "nine_stage_cap_equality"]
    require(not certificate["trials"][0]["bill"]["admitted"], "precision-overflow fixture")
    rejected.append("endpoint_valid_first_nominee_exceeds_precision")
    altered = copy.deepcopy(manifest)
    altered["files"] = [r for r in altered["files"] if r["path"] != PARENT]
    rejected.append(expect_rejection("missing_source_pin", lambda: source_pins(altered)))
    altered = copy.deepcopy(manifest)
    next(r for r in altered["files"] if r["path"] == PARENT)["sha256"] = "0" * 64
    rejected.append(expect_rejection("source_digest_drift", lambda: source_pins(altered)))
    rejected.append(expect_rejection("duplicate_JSON_key", lambda: parse('{"seed":13,"seed":13}')))
    rejected.append(expect_rejection("nonfinite_JSON", lambda: parse('{"value":NaN}')))
    rejected.append(expect_rejection("boolean_as_integer", lambda: same(True, 1, "typed receipt equality")))
    neutral = copy.deepcopy(candidate)
    gate = [0, 222, [223]]
    neutral["D"] = [gate, copy.deepcopy(gate)] + neutral["D"]
    same(evaluate(neutral, only_d=True), evaluate(candidate, only_d=True), "neutral pair endpoint")
    require(invoice(neutral)["ADDs"] == invoice(candidate)["ADDs"] + 2, "neutral pair charge")
    return {"rejected": rejected, "paid_neutral_pair": True}


def run():
    manifest, certificate = read(HERE / "SOURCES.json"), read(HERE / "CERTIFICATE.json")
    source_pins(manifest)
    require(certificate["format"] == "r439-neutral-mixed-shears/1" and certificate["base_commit"] == BASE
            and type(certificate["seed"]) is int and certificate["seed"] == 13, "certificate identity")
    require(certificate["no_new_kappa"] is True, "finite scope label")
    require(certificate["stopping_rule"] == "complete support census using proved exclusions; price exactly first min(32,positive_count); first admitted; no descent or restart",
            "stopping rule")
    formula_check()
    original, parent = read(ROOT / ORIGINAL), read(ROOT / PARENT)
    helpers, targets, rows = recipe(original, parent)
    census = independent_census(rows)
    same(census, certificate["census"], "independent full census")
    same(invoice(parent), certificate["baseline"], "parent invoice")
    expected = [[i] if not 111 <= i < 222 else [i - 111, i] for i in range(661)]
    expected_d = evaluate(original, only_d=True)
    for reverse in (False, True):
        same(evaluate(parent, reverse), expected, "parent full dirty boundary")
        same(evaluate(parent, reverse, only_d=True), expected_d, "parent semantic D")
    nominees = census["positive_cases"][:32]
    require(len(certificate["trials"]) == len(nominees), "nomination cap coverage")
    admitted_indices, checked = [], []
    for i, case in enumerate(nominees):
        word = construct(parent, helpers, targets, rows, case)
        bill = invoice(word)
        trial = {"case": case, "tie_sha256": tie(case), "bill": bill, "word_sha256": digest(word)}
        same(trial, certificate["trials"][i], "independent literal trial and full invoice")
        require(certificate["baseline"]["ADDs"] - bill["ADDs"] == case[6], "complete saving")
        for reverse in (False, True):
            same(evaluate(word, reverse), expected, "all trial dirty columns and lifecycles")
            same(evaluate(word, reverse, only_d=True), expected_d, "all trial semantic D")
        if bill["admitted"]:
            admitted_indices.append(i)
        checked.append(word)
    require(admitted_indices and certificate["winner_index"] == admitted_indices[0], "first admitted selection")
    winner = admitted_indices[0]
    candidate, chosen = checked[winner], nominees[winner]
    same(candidate, read(HERE / "candidate.json.gz"), "entire decoded candidate")
    require(digest(candidate) == certificate["candidate_sha256"], "candidate canonical digest")
    for label, flags in (("target", {"use_helper": False}), ("helper", {"use_target": False})):
        single = construct(parent, helpers, targets, rows, chosen, **flags)
        same(invoice(single), certificate["winner_single_" + label], "unilateral complete invoice")
        require(invoice(single)["ADDs"] == invoice(parent)["ADDs"], "chosen unilateral move is exactly neutral")
        for reverse in (False, True):
            same(evaluate(single, reverse), expected, "unilateral full dirty boundary")
    require(chosen[6] == 2 and chosen[4:6] == [0, 0], "attained sharp two-ADD interaction bound")
    geometry = geometry_and_records(parent, candidate)
    negative = controls(parent, candidate, chosen, manifest, certificate)
    return {"status": "PASS_R439_NEUTRAL_MIXED_SHEARS", "base_commit": BASE,
            "candidate_sha256": digest(candidate), "census_domain": census["nonpositive_unilateral_domain"],
            "explicit_cases": census["explicit_interaction_cases"], "positive_cases": census["positive_count"],
            "trials": len(nominees), "admitted_trial_indices": admitted_indices,
            "winner": chosen, "bill": invoice(candidate), "geometry_and_records": geometry,
            "dirty_input_columns": 661, "orientations": 2, "controls": negative,
            "scope": "sharp fixed one-target/one-helper nonpositive-unilateral neighborhood; no arbitrary-word or supplier theorem",
            "no_new_kappa": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    receipt = run()
    if args.write_receipt:
        (HERE / "VALIDATION.json").write_text(json.dumps(receipt, indent=2) + "\n")
    else:
        same(receipt, read(HERE / "VALIDATION.json"), "complete verification receipt")
    print(receipt["status"], "ADDs=11783->11781 positive=91 trials=32 admitted=8 columns=661",
          "controls=" + str(len(receipt["controls"]["rejected"])), "no_new_kappa")


if __name__ == "__main__":
    main()
