#!/usr/bin/env python3
"""Independent set/matrix replay and unchanged native checks of the two-sided word.

Prepared for Gareth Davidson (@bitplane), with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
import copy
from pathlib import Path
import random
import runpy
import subprocess
import sys
import tempfile

C = runpy.run_path(str(Path(__file__).resolve().with_name("common.py")))
need = C["need"]


def same(a, b, message):
    need(C["canonical"](a) == C["canonical"](b), message)


def guards(forward, backward):
    need(64 * forward ** 3 * backward ** 2 < 1 << 104, "local payload guard")
    need((1 << 18) * forward ** 5 * backward ** 4 < 1 << 192, "nine-stage guard")


def d_atoms(word):
    v, n = word["v"], 2 * word["v"] + word["R"]
    result = []
    for frame, d, sources in word["D"]:
        need(type(frame) is int and frame == 0, "D frame zero")
        need(type(d) is int and v <= d < n, "D may not write sources")
        need(sources and len(set(sources)) == len(sources), "D nonempty distinct donors")
        need(all(type(s) is int and v <= s < n and s != d for s in sources), "D legal donor")
        need(d < 2 * v or all(s >= 2 * v for s in sources), "D helper may not read target")
        result.extend((d, s) for s in sources)
    return result


def stream(word):
    """Literal ADD/COPY/ERASE instructions, independent of builder macro evaluation."""
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


def positive(instructions, size, reverse=False):
    values, largest = [1] * size, 1
    for kind, d, s in (reversed(instructions) if reverse else instructions):
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


def bill(word):
    literal = stream(word)
    size = 2 * word["v"] + word["R"] + 1
    forward, backward = positive(literal, size), positive(literal, size, True)
    return dict(D_adds=len(d_atoms(word)), native_ADDs=sum(k == 1 for k, _, _ in literal),
                F=forward, B=backward, payload_bits=(64 * forward ** 3 * backward ** 2).bit_length(),
                nine_stage_prefix_bits=((1 << 18) * forward ** 5 * backward ** 4).bit_length())


def check_bill(word, certificate):
    for key, value in bill(word).items():
        same(value, certificate[key], "literal bill: " + key)


def boundary_columns(word, reverse=False):
    """One byte-valued replay for each of the 661 separate input columns."""
    n = 2 * word["v"] + word["R"]
    operations = d_atoms(word)
    if reverse:
        operations.reverse()
    output = []
    for column in range(n):
        values = bytearray(n)
        values[column] = 1
        for d, s in operations:
            values[d] ^= values[s]
        output.append(bytes(values))
    return output


def outside_d(original, candidate):
    same({k: v for k, v in original.items() if k != "D"},
         {k: v for k, v in candidate.items() if k != "D"}, "non-D field changed")


def original_rows(original):
    v = original["v"]
    rows = [set() for _ in range(v)]
    for frame, d, sources in original["D"]:
        need(frame == 0 and v <= d < 2 * v and all(s >= 2 * v for s in sources), "old D shape")
        for s in sources:
            rows[d - v].symmetric_difference_update({s - 2 * v})
    return rows


def frozen_parent(original, parent):
    """Derive E and EK from the pinned target recipe, without accepting search claims."""
    certificate = C["load"](C["HERE"] / "vendor/pr915/CERTIFICATE.json")
    same(C["digest"](parent), certificate["candidate_sha256"], "parent digest")
    outside_d(original, parent)
    v = original["v"]
    rows, e_rows, target = original_rows(original), [{i} for i in range(v)], []
    for step in certificate["steps"]:
        d, s = step["destination"], step["source"]
        need(type(d) is int and type(s) is int and 0 <= d < v and 0 <= s < v and d != s,
             "parent target shear")
        rows[d].symmetric_difference_update(rows[s])
        e_rows[d].symmetric_difference_update(e_rows[s])
        target.append([0, v + d, [v + s]])
    middle = [[0, v + i, [2 * v + j for j in sorted(row)]] for i, row in enumerate(rows)]
    same(target + middle + target[::-1], parent["D"], "frozen parent reconstruction")
    check_bill(parent, certificate)
    need(len(target) == 306, "parent target count")
    return rows, e_rows, target


def helper_pairs(certificate, count):
    pairs, used = [], set()
    for step in certificate["steps"]:
        a, b = step["a"], step["b"]
        need(type(a) is int and type(b) is int, "noninteger helper index")
        need(0 <= a < count and 0 <= b < count and a != b, "helper pair range")
        need(a not in used and b not in used, "overlapping helper pair")
        pairs.append((a, b))
        used.update((a, b))
    return pairs


def reconstruct(parent, rows, target, pairs):
    v = parent["v"]
    transformed = [set(row) for row in rows]
    for a, b in pairs:
        for row in transformed:
            if a in row:
                row.symmetric_difference_update({b})
    helpers = [[0, 2 * v + a, [2 * v + b]] for a, b in pairs]
    middle = [[0, v + i, [2 * v + j for j in sorted(row)]] for i, row in enumerate(transformed)]
    result = copy.deepcopy(parent)
    result["D"] = helpers + target + middle + target[::-1] + helpers[::-1]
    return result, transformed


def recipe_check(original, parent, candidate, certificate):
    need(certificate["format"] == "r439-two-sided/1" and type(certificate["seed"]) is int
         and certificate["seed"] == 5, "certificate format/seed")
    for label, word in (("baseline", original), ("parent", parent), ("candidate", candidate)):
        same(C["digest"](word), certificate[label + "_sha256"], label + " digest")
    outside_d(original, candidate)
    rows, e_rows, target = frozen_parent(original, parent)
    v, helpers = original["v"], original["R"]
    expected_pairs = helper_pairs(certificate, helpers)
    # Set cardinalities, not the builder's packed column XOR/popcount implementation.
    columns = [{i for i in range(v) if j in rows[i]} for j in range(helpers)]
    rng, census, choices = random.Random(5), [], []
    for a in range(helpers):
        for b in range(helpers):
            if a == b:
                continue
            gain = len(columns[b]) - len(columns[b].symmetric_difference(columns[a])) - 2
            tie = rng.getrandbits(64)
            census.append([a, b, gain, tie])
            if gain > 0:
                choices.append((-gain, tie, a, b))
    same(C["digest"](census), certificate["census_sha256"], "all pair scores and ties")
    same(len(census), certificate["pair_scores"], "pair census size")
    same(len(choices), certificate["positive_pairs"], "positive pair count")
    same(max(-p[0] for p in choices), certificate["max_pair_gain"], "maximum pair gain")
    accepted, used, history, rejected, skipped, instructions_checked = [], set(), [], [], 0, 0
    for neg_gain, tie, a, b in sorted(choices):
        if a in used or b in used:
            skipped += 1
            continue
        trial, supports = reconstruct(parent, rows, target, accepted + [(a, b)])
        charges = bill(trial)
        forward, backward = charges["F"], charges["B"]
        instructions_checked += 2 * len(stream(trial))
        try:
            guards(forward, backward)
        except ValueError:
            rejected.append(dict(a=a, b=b, gain=-neg_gain, F=forward, B=backward))
            continue
        accepted.append((a, b))
        used.update((a, b))
        history.append(dict(a=a, b=b, gain=-neg_gain, F=forward, B=backward,
                            middle_weight=sum(map(len, supports))))
    same(accepted, expected_pairs, "guarded greedy pairs")
    same(history, certificate["steps"], "literal prefix history")
    same(rejected, certificate["guard_rejections"], "guard rejection history")
    same(skipped, certificate["overlap_skips"], "overlap count")
    reconstructed, supports = reconstruct(parent, rows, target, accepted)
    same(reconstructed, candidate, "entire candidate recipe")
    check_bill(candidate, certificate)
    need(len(accepted) == certificate["helper_pairs"] == 192, "accepted pair count")
    need(certificate["target_shears"] == len(target), "fixed target count")
    need(sum(map(len, supports)) == certificate["middle_weight"] == 4764, "middle matrix weight")
    saving = sum(step["gain"] for step in history)
    need(saving == certificate["saved_beyond_parent"] == 1228, "fully paid savings")
    need(certificate["D_adds"] == 2 * len(target) + 2 * len(accepted) + sum(map(len, supports)) == 5760,
         "all preparation and restoration charged")
    return dict(pair_scores=len(census), positive_pairs=len(choices), max_pair_gain=max(-p[0] for p in choices),
                overlap_skips=skipped, guard_rejections=len(rejected), helper_pairs=len(accepted),
                target_shears=len(target), middle_weight=sum(map(len, supports)),
                saved_beyond_parent=saving, literal_prefix_instructions_checked=instructions_checked), e_rows, supports


def matrix_check(original, e_rows, pairs, middle):
    """Every coefficient by K + (E-I)K + K(H-I) + (E-I)K(H-I)."""
    v, helpers = original["v"], original["R"]
    k_rows = original_rows(original)
    k = [[int(j in k_rows[i]) for j in range(helpers)] for i in range(v)]
    a_rows = [row.symmetric_difference({i}) for i, row in enumerate(e_rows)]
    predecessor = {b: a for a, b in pairs}
    mixed, coefficients, helper_only_weight = [set() for _ in range(v)], 0, 0
    for i in range(v):
        for j in range(helpers):
            base = k[i][j]
            left = sum(k[t][j] for t in a_rows[i]) % 2
            right = k[i][predecessor[j]] if j in predecessor else 0
            cross = sum(k[t][predecessor[j]] for t in a_rows[i]) % 2 if j in predecessor else 0
            need(((base + left + right + cross) % 2) == int(j in middle[i]), "four-term matrix coefficient")
            if cross:
                mixed[i].add(j)
            helper_only_weight += (base + right) % 2
            coefficients += 1
    need(sum(map(len, mixed)) == 7031, "nonzero mixed-term support")
    return dict(coefficients_checked=coefficients, mixed_term_nonzeros=sum(map(len, mixed)),
                helper_only_middle_weight_for_same_pairs=helper_only_weight,
                helper_only_D_cost_for_same_pairs=helper_only_weight + 2 * len(pairs)), mixed


def source_checks(root, words):
    owner = C["module"]("pinned_r439", Path(root) / C["CHECKER"])
    receipts = {}
    for name, word in words.items():
        _, labels, full, hypotheses, conclusions, info = owner.check(word)
        wanted_h = {key: True for key in hypotheses}
        wanted_c = {key: True for key in conclusions}
        if name != "baseline":
            wanted_h["H2_D_frame0_targets_from_helpers"] = False
            wanted_c["K_equals_D"] = False
        same(hypotheses, wanted_h, "unexpected source interface predicates")
        same(conclusions, wanted_c, "unexpected source conclusion predicates")
        receipts[name] = dict(labels=labels, full=full, hypotheses=hypotheses, conclusions=conclusions, info=info)
    return receipts


def nine_stage_bound(root, native):
    path = ("research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/"
            "vendor/e8-r715-eleven-stage-whole/code/global_k.py")
    syntax = ast.parse((Path(root) / path).read_text())
    formulas = [node.value for node in ast.walk(syntax) if isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "prefix" for t in node.targets)]
    expected = ast.parse("(1 << nb) * cf ** (K + 1) * cb ** K", mode="eval").body
    need(len(formulas) == 1 and ast.dump(formulas[0]) == ast.dump(expected), "source prefix formula")
    bridge = ast.parse("nb == 6 * (K - 1)", mode="eval").body
    need(any(isinstance(node, ast.Compare) and ast.dump(node) == ast.dump(bridge)
             for node in ast.walk(syntax)), "source bridge exponent")
    admitted = C["load"](Path(root) / "research/e8-bit-p111-tuned/tune/EXPECTED.json")["nine"]["bit"]
    need(admitted["charged_prefix_bits"] == 192, "source nine-stage charge")
    output = {"formula": "2^18 * F^5 * B^4", "source_charge_bits": 192}
    for name in ("baseline", "parent", "candidate"):
        bounds = native[name]["staged"]["9"]["signed_lift_prefix"]
        forward, backward = [int(x["cancellation_free_signed_row_l1_upper"]) for x in bounds]
        value = (1 << 18) * forward ** 5 * backward ** 4
        need(value < 1 << 192, "nine-stage invoice bound")
        output[name] = {"bound": str(value), "bits": value.bit_length()}
    need(output["baseline"]["bits"] == admitted["prefix_bits"] == 177, "source baseline prefix")
    need(output["parent"]["bits"] == 189 and output["candidate"]["bits"] == 192, "changed prefix charges")
    return output


def controls(original, parent, candidate, certificate, baseline_columns, mixed, middle):
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

    h, m, v = certificate["helper_pairs"], certificate["target_shears"], original["v"]
    changed = copy.deepcopy(candidate)
    del changed["D"][h:h + m]
    columns = boundary_columns(changed)
    need(columns[2 * v:] == baseline_columns[2 * v:], "missing-target-entrance control premise")
    need(columns[v:2 * v] != baseline_columns[v:2 * v], "arbitrary target inputs are necessary")
    reject("missing target preparation passes helper-only columns", lambda: boundary(changed), "D boundary")
    changed = copy.deepcopy(candidate)
    del changed["D"][:h]
    columns = boundary_columns(changed)
    need(columns[:2 * v] == baseline_columns[:2 * v], "missing-helper-preparation control premise")
    reject("missing helper preparation passes clean-helper inputs", lambda: boundary(changed), "D boundary")
    changed = copy.deepcopy(candidate)
    changed["D"].pop()
    reject("missing helper restoration", lambda: boundary(changed), "D boundary")
    changed = copy.deepcopy(candidate)
    changed["D"].pop(-h - 1)
    reject("missing target restoration", lambda: boundary(changed), "D boundary")
    changed = copy.deepcopy(candidate)
    for i, row in enumerate(middle):
        changed["D"][h + m + i][2] = [2 * v + j for j in sorted(row.symmetric_difference(mixed[i]))]
    reject("omitted mixed term", lambda: boundary(changed), "D boundary")
    changed = copy.deepcopy(candidate)
    changed["D"][h + m:h + m + v] = copy.deepcopy(parent["D"][m:m + v])
    reject("stale one-sided middle matrix", lambda: boundary(changed), "D boundary")
    changed = copy.deepcopy(candidate)
    for i, (_, _, row) in enumerate(parent["D"][m:m + v]):
        support = set(row)
        for a, b in helper_pairs(certificate, original["R"]):
            if 2 * v + b in support:
                support.symmetric_difference_update({2 * v + a})
        changed["D"][h + m + i][2] = sorted(support)
    reject("wrong direction of helper-column change", lambda: boundary(changed), "D boundary")
    changed = copy.deepcopy(candidate)
    changed["D"][-h - m:-h] = copy.deepcopy(parent["D"][:m])
    reject("target restoration in forward order", lambda: boundary(changed), "D boundary")
    changed = copy.deepcopy(candidate)
    changed["D"][0][0] = 1
    reject("nonzero D frame", lambda: d_atoms(changed), "D frame")
    changed = copy.deepcopy(candidate)
    changed["D"][0][1] = 0
    reject("D writes source", lambda: d_atoms(changed), "may not write sources")
    changed = copy.deepcopy(candidate)
    changed["D"][0][2] = [0]
    reject("D reads source", lambda: d_atoms(changed), "D legal donor")
    changed = copy.deepcopy(candidate)
    changed["D"][0][2] = [v]
    reject("helper reads target", lambda: d_atoms(changed), "may not read target")
    wrong = copy.deepcopy(certificate)
    wrong["D_adds"] -= h
    reject("unpaid helper restoration", lambda: check_bill(candidate, wrong), "literal bill: D_adds")
    wrong = copy.deepcopy(certificate)
    wrong["F"] = 49347
    reject("inherited parent forward bound", lambda: check_bill(candidate, wrong), "literal bill: F")
    reject("local payload ceiling equality", lambda: guards(1, 1 << 49), "local payload")
    reject("nine-stage overrun below local cap", lambda: guards(71907, 14000000), "nine-stage")
    wrong = copy.deepcopy(certificate)
    wrong["steps"][1]["a"] = wrong["steps"][0]["a"]
    reject("overlapping helper pairs", lambda: helper_pairs(wrong, original["R"]), "overlapping")
    wrong = copy.deepcopy(certificate)
    wrong["steps"][0]["a"] = True
    reject("boolean helper index", lambda: helper_pairs(wrong, original["R"]), "noninteger")
    changed = copy.deepcopy(candidate)
    changed["C"].pop()
    reject("unrelated cleanup change", lambda: outside_d(original, changed), "non-D")
    neutral = copy.deepcopy(candidate)
    neutral["D"][:0] = [[0, 2 * v, [2 * v + 1]], [0, 2 * v, [2 * v + 1]]]
    need(boundary_columns(neutral) == baseline_columns, "neutral helper pair endpoint")
    need(len(d_atoms(neutral)) == len(d_atoms(candidate)) + 2, "neutral pair must be paid")
    return {"rejected": rejected, "paid_neutral_helper_pair": 2}


def run(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    manifest = C["pins"](root)
    output.mkdir(parents=True, exist_ok=False)
    original = C["load"](root / C["WORD"])
    parent = C["load"](C["HERE"] / "vendor/pr915/candidate.json.gz")
    candidate = C["load"](C["HERE"] / "candidate.json.gz")
    certificate = C["load"](C["HERE"] / "CERTIFICATE.json")
    same(C["digest"](parent), manifest["parent"]["canonical_word_sha256"], "manifest parent digest")
    print("reproduce complete seed-5 pair census and guarded greedy pass", flush=True)
    generated = output / "regenerated"
    subprocess.run([sys.executable, "-I", "-B", C["HERE"] / "build.py", "--source-root", root,
                    "--output", generated], check=True)
    same(C["load"](generated / "CERTIFICATE.json"), certificate, "certificate regeneration")
    same(C["load"](generated / "candidate.json.gz"), candidate, "candidate regeneration")
    print("independent set-valued search replay and literal prefix bounds", flush=True)
    recipe, e_rows, middle = recipe_check(original, parent, candidate, certificate)
    pairs = helper_pairs(certificate, original["R"])
    matrix, mixed = matrix_check(original, e_rows, pairs, middle)
    print("48,729 four-term coefficients; 661 separate columns, three words, both D directions", flush=True)
    baseline_columns = boundary_columns(original)
    words = {"baseline": original, "parent": parent, "candidate": candidate}
    bills = {name: bill(word) for name, word in words.items()}
    for word in words.values():
        for reverse in (False, True):
            need(boundary_columns(word, reverse) == baseline_columns, "arbitrary-input D boundary")
    source = source_checks(root, words)
    negative = controls(original, parent, candidate, certificate, baseline_columns, mixed, middle)
    print("unchanged native legality and 5/9/11-stage checks for all three complete words", flush=True)
    native = C["module"]("r439_native", C["HERE"] / "native.py").run(
        root, root / C["WORD"], C["HERE"] / "vendor/pr915/candidate.json.gz",
        C["HERE"] / "candidate.json.gz", output / "native")
    for name in words:
        need(bills[name]["native_ADDs"] == native[name]["common_frame_ADDs"], "native/literal cost")
        bounds = native[name]["staged"]["9"]["signed_lift_prefix"]
        same([bills[name]["F"], bills[name]["B"]],
             [int(x["cancellation_free_signed_row_l1_upper"]) for x in bounds], "native/literal bounds")
    return {"status": "PASS_R439_TWO_SIDED_COMPENSATION", "source_files": manifest["files"],
            "predecessor_files": manifest["local_files"], "recipe": recipe, "matrix": matrix,
            "boundary_columns": 661, "boundary_words_and_directions": 6, "bills": bills,
            "baseline_sha256": C["digest"](original), "parent_sha256": C["digest"](parent),
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
    with tempfile.TemporaryDirectory(prefix="r439-two-sided-") as temp:
        report = run(args.source_root, args.output or Path(temp) / "run")
        same(report, expected, "receipt differs from EXPECTED.json")
        if args.receipt:
            C["write"](args.receipt, report)
    print("PASS_R439_TWO_SIDED_COMPENSATION: ADDs 24,305 -> 13,208 -> 11,980; "
          "192 helper pairs; nine-stage prefix 192 bits; semantic D; no new kappa")
