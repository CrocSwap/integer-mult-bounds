#!/usr/bin/env python3
"""Exact matching bound, bounded precision alternatives and complete R439 replay.

Circuit I/O, boundary, positive and owning-checker routines adapted from PR926.
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


def validate_pairs(pairs, count):
    used = set()
    for pair in pairs:
        need(isinstance(pair, (list, tuple)) and len(pair) == 2, "pair shape")
        a, b = pair
        need(type(a) is int and type(b) is int, "noninteger helper index")
        need(0 <= a < count and 0 <= b < count and a != b, "helper pair range")
        need(a not in used and b not in used, "overlapping helper pair")
        used.update((a, b))


def matching_gain(columns, pairs):
    validate_pairs(pairs, len(columns))
    return sum(len(columns[b]) - len(columns[b].symmetric_difference(columns[a])) - 2 for a, b in pairs)


def dual_check(columns, dual, witness):
    """Elementary integer upper bound: each vertex once, each odd set at most floor(size/2)."""
    q, sets = dual["vertex_prices_2"], dual["odd_sets"]
    count = len(columns)
    need(len(q) == count and all(type(x) is int and x >= 0 for x in q), "nonnegative integer vertex prices")
    priced_sets = []
    for row in sets:
        vertices, price = row["vertices"], row["price_2"]
        need(type(price) is int and price > 0, "positive integer odd-set price")
        need(len(vertices) >= 3 and len(vertices) % 2 == 1, "odd-set size")
        need(all(type(v) is int and 0 <= v < count for v in vertices)
             and len(set(vertices)) == len(vertices), "odd-set vertices")
        priced_sets.append((set(vertices), price))
    census, positive, tight = [], 0, 0
    for a in range(count):
        for b in range(a + 1, count):
            distance = len(columns[a].symmetric_difference(columns[b]))
            ab, ba = len(columns[b]) - distance - 2, len(columns[a]) - distance - 2
            weight = max(ab, ba)
            price = q[a] + q[b] + sum(z for vertices, z in priced_sets if a in vertices and b in vertices)
            need(price >= 2 * weight, "dual edge inequality")
            census.append([a, b, ab, ba])
            positive += weight > 0
            tight += price == 2 * weight
    objective_2 = sum(q) + sum(z * (len(vertices) // 2) for vertices, z in priced_sets)
    gain = matching_gain(columns, witness)
    need(objective_2 == 2 * gain, "primal/dual equality")
    need(gain == 1260, "fixed-class saving")
    return dict(unordered_pairs=len(census), oriented_pair_scores=2 * len(census),
                positive_edges=positive, tight_edges=tight, vertex_prices=len(q), odd_sets=len(sets),
                largest_odd_set=max(len(s) for s, _ in priced_sets), doubled_objective=objective_2,
                exact_maximum_saving=gain, complete_ADD_floor=13208 - gain,
                census_sha256=C["digest"](census))


def proxy_check(parent, nomination):
    """Independent literal suffix columns for the optional discovery objective."""
    v, n = parent["v"], 2 * parent["v"] + parent["R"]
    blank = copy.deepcopy(parent)
    blank["D"] = []
    instructions = stream(blank)

    def final(values):
        values = list(values) + [0]
        for kind, d, s in instructions:
            if kind == 1:
                values[d] += values[s]
            elif kind == 2:
                values[d] = values[s]
            else:
                values[d] = 0
        return values

    ordinary = final([1] * n)
    pivot = max(list(range(v)) + list(range(2 * v, n)), key=lambda j: ordinary[j])
    costs = []
    for j in range(parent["R"]):
        values = [0] * n
        values[2 * v + j] = 1
        costs.append(final(values)[pivot])
    same(pivot, nomination["proxy_pivot"], "proxy pivot")
    same(costs, nomination["proxy_cost"], "all helper proxy columns")
    same(1 + sum(costs), nomination["lexicographic_multiplier"], "lexicographic multiplier")
    return dict(pivot=pivot, helper_columns=len(costs), maximum_cost=max(costs),
                lexicographic_multiplier=1 + sum(costs))


def compact_bill(word):
    full = bill(word)
    forward, backward = full["F"], full["B"]
    admitted = (64 * forward ** 3 * backward ** 2 < 1 << 104
                and (1 << 18) * forward ** 5 * backward ** 4 < 1 << 192)
    return dict(ADDs=full["native_ADDs"], gain=13208 - full["native_ADDs"], F=forward, B=backward,
                payload_bits=full["payload_bits"], nine_bits=full["nine_stage_prefix_bits"], admitted=admitted)


def bounded_family(parent, rows, target, nomination, columns):
    need(type(nomination["seed"]) is int and nomination["seed"] == 4, "nomination seed")
    nominations = nomination["nominations"]
    same([r["variant"] for r in nominations], ["lexicographic", "seed4", "forward_proxy"], "three nomination policies")
    trials, best, instructions_checked = [], None, 0
    for ni, nominated in enumerate(nominations):
        need(matching_gain(columns, nominated["pairs"]) == 1260, "each nomination attains arithmetic floor")
        for removed in range(-1, len(nominated["pairs"])):
            pairs = [pair for i, pair in enumerate(nominated["pairs"]) if i != removed]
            word, _ = reconstruct(parent, rows, target, pairs)
            charge = compact_bill(word)
            instructions_checked += 2 * len(stream(word))
            if removed == -1:
                same(charge, {k: value for k, value in nominated.items() if k not in ("variant", "pairs")},
                     "full optimum word bill")
                need(charge["admitted"] is False and charge["nine_bits"] == 193, "nominated optimum fails nine-stage cap")
            row = dict(nomination=ni, removed_index=removed, **charge)
            trials.append(row)
            key = (charge["ADDs"], charge["nine_bits"], charge["F"], charge["B"], ni, removed)
            if charge["admitted"] and (best is None or key < best[0]):
                best = key, pairs, row
    same(trials, nomination["trials"], "all bounded-family charges")
    need(best is not None, "bounded family has no admitted word")
    same(best[1], nomination["selected_pairs"], "selected matching")
    same(best[2], nomination["selected"], "selected full cost and bounds")
    return dict(nominations=len(nominations), single_pair_deletions=len(trials) - len(nominations),
                complete_words_priced=len(trials), admitted_words=sum(r["admitted"] for r in trials),
                literal_prefix_instructions_checked=instructions_checked, selected=best[2])


def matrix_check(original, e_rows, pairs, middle):
    v, helpers = original["v"], original["R"]
    rows = original_rows(original)
    k = [[int(j in rows[i]) for j in range(helpers)] for i in range(v)]
    a_rows = [row.symmetric_difference({i}) for i, row in enumerate(e_rows)]
    predecessor = {b: a for a, b in pairs}
    mixed = [set() for _ in range(v)]
    for i in range(v):
        for j in range(helpers):
            base = k[i][j]
            left = sum(k[t][j] for t in a_rows[i]) % 2
            right = k[i][predecessor[j]] if j in predecessor else 0
            cross = sum(k[t][predecessor[j]] for t in a_rows[i]) % 2 if j in predecessor else 0
            need((base + left + right + cross) % 2 == int(j in middle[i]), "four-term coefficient")
            if cross:
                mixed[i].add(j)
    return dict(coefficients=v * helpers, mixed_term_nonzeros=sum(map(len, mixed))), mixed


def nine_stage_bound(root, native):
    source = ("research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/"
              "vendor/e8-r715-eleven-stage-whole/code/global_k.py")
    tree = ast.parse((Path(root) / source).read_text())
    formulas = [node.value for node in ast.walk(tree) if isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "prefix" for t in node.targets)]
    expected = ast.parse("(1 << nb) * cf ** (K + 1) * cb ** K", mode="eval").body
    need(len(formulas) == 1 and ast.dump(formulas[0]) == ast.dump(expected), "source prefix formula")
    bridge = ast.parse("nb == 6 * (K - 1)", mode="eval").body
    need(any(isinstance(node, ast.Compare) and ast.dump(node) == ast.dump(bridge)
             for node in ast.walk(tree)), "source bridge exponent")
    admitted = C["load"](Path(root) / "research/e8-bit-p111-tuned/tune/EXPECTED.json")["nine"]["bit"]
    need(admitted["charged_prefix_bits"] == 192, "source nine-stage charge")
    output = {"formula": "2^18 * F^5 * B^4", "source_charge_bits": 192}
    for name in ("baseline", "parent", "greedy", "floor", "candidate"):
        bounds = native[name]["staged"]["9"]["signed_lift_prefix"]
        forward, backward = [int(x["cancellation_free_signed_row_l1_upper"]) for x in bounds]
        value = (1 << 18) * forward ** 5 * backward ** 4
        fits = value < 1 << 192
        need(fits == (name != "floor"), "nine-stage admission for " + name)
        output[name] = {"bound": str(value), "bits": value.bit_length(), "admitted": fits}
    need(output["baseline"]["bits"] == admitted["prefix_bits"] == 177, "source baseline prefix")
    return output


def controls(original, candidate, floor_word, certificate, nomination, columns, baseline_columns, middle, mixed):
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

    dual, witness = nomination["primary_dual"], nomination["nominations"][0]["pairs"]
    wrong = copy.deepcopy(dual)
    wrong["odd_sets"] = []
    reject("omitted odd-set prices", lambda: dual_check(columns, wrong, witness), "dual edge inequality")
    wrong = copy.deepcopy(dual)
    index = next(i for i, value in enumerate(wrong["vertex_prices_2"]) if value)
    wrong["vertex_prices_2"][index] -= 1
    reject("underpriced vertex", lambda: dual_check(columns, wrong, witness), "dual edge inequality")
    wrong = copy.deepcopy(dual)
    wrong["odd_sets"][0]["vertices"].pop()
    reject("even set charged as odd", lambda: dual_check(columns, wrong, witness), "odd-set size")
    wrong = copy.deepcopy(dual)
    wrong["vertex_prices_2"][0] = True
    reject("boolean dual price", lambda: dual_check(columns, wrong, witness), "integer vertex prices")
    pairs = copy.deepcopy(nomination["selected_pairs"])
    pairs[1][0] = pairs[0][0]
    reject("overlapping matching", lambda: validate_pairs(pairs, original["R"]), "overlapping")
    pairs = copy.deepcopy(nomination["selected_pairs"])
    pairs[0][0] = True
    reject("boolean helper index", lambda: validate_pairs(pairs, original["R"]), "noninteger")
    h, m, v = certificate["helper_pairs"], certificate["target_shears"], original["v"]
    changed = copy.deepcopy(candidate)
    del changed["D"][h:h + m]
    actual = boundary_columns(changed)
    need(actual[2 * v:] == baseline_columns[2 * v:], "helper-only target-preparation control premise")
    reject("missing target preparation", lambda: boundary(changed), "D boundary")
    changed = copy.deepcopy(candidate)
    del changed["D"][:h]
    actual = boundary_columns(changed)
    need(actual[:2 * v] == baseline_columns[:2 * v], "clean-helper preparation control premise")
    reject("missing helper preparation", lambda: boundary(changed), "D boundary")
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
    changed["D"][0][0] = 1
    reject("nonzero D frame", lambda: d_atoms(changed), "D frame")
    changed = copy.deepcopy(candidate)
    changed["D"][0][2] = [0]
    reject("D source access", lambda: d_atoms(changed), "D legal donor")
    changed = copy.deepcopy(certificate)
    changed["D_adds"] -= h
    reject("unpaid helper restoration", lambda: check_bill(candidate, changed), "literal bill: D_adds")
    changed = copy.deepcopy(certificate)
    changed["F"] = 49347
    reject("inherited parent forward bound", lambda: check_bill(candidate, changed), "literal bill: F")
    floor_bill = bill(floor_word)
    reject("arithmetic optimum falsely admitted", lambda: guards(floor_bill["F"], floor_bill["B"]), "nine-stage")
    reject("strict local ceiling equality", lambda: guards(1, 1 << 49), "local payload")
    reject("strict nine-stage ceiling equality", lambda: guards(1 << 2, 1 << 41), "nine-stage")
    changed = copy.deepcopy(candidate)
    changed["C"].pop()
    reject("unrelated cleanup change", lambda: outside_d(original, changed), "non-D")
    neutral = copy.deepcopy(candidate)
    neutral["D"][:0] = [[0, 2 * v, [2 * v + 1]], [0, 2 * v, [2 * v + 1]]]
    need(boundary_columns(neutral) == baseline_columns, "neutral helper pair endpoint")
    need(len(d_atoms(neutral)) == len(d_atoms(candidate)) + 2, "neutral helper pair cost")
    return {"rejected": rejected, "paid_neutral_helper_pair": 2}


def run(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    manifest = C["pins"](root)
    output.mkdir(parents=True, exist_ok=False)
    original = C["load"](root / C["WORD"])
    parent = C["load"](C["HERE"] / "vendor/pr915/candidate.json.gz")
    greedy = C["load"](C["HERE"] / "vendor/pr926/candidate.json.gz")
    candidate = C["load"](C["HERE"] / "candidate.json.gz")
    floor_word = C["load"](C["HERE"] / "floor-word.json.gz")
    certificate = C["load"](C["HERE"] / "CERTIFICATE.json")
    nomination = C["load"](C["HERE"] / "NOMINATION.json")
    need(certificate["format"] == "r439-helper-matching/1" and type(certificate["seed"]) is int
         and certificate["seed"] == 4, "certificate format/seed")
    for label, word in (("baseline", original), ("parent", parent), ("greedy", greedy), ("candidate", candidate),
                        ("floor_word", floor_word)):
        same(C["digest"](word), certificate[label + "_sha256"], label + " digest")
        outside_d(original, word)
    same(C["digest"](parent), manifest["parent"]["canonical_word_sha256"], "manifest parent digest")
    same(C["digest"](greedy), manifest["greedy_comparator"]["canonical_word_sha256"], "manifest comparator digest")
    same(C["digest"](nomination), certificate["nomination_sha256"], "nomination digest")
    rows, e_rows, target = frozen_parent(original, parent)
    columns = [{i for i, row in enumerate(rows) if j in row} for j in range(original["R"])]
    print("independent 96,141-edge integer vertex/odd-set certificate", flush=True)
    dual = dual_check(columns, nomination["primary_dual"], nomination["nominations"][0]["pairs"])
    same(dual["positive_edges"], nomination["positive_edges"], "positive edge census")
    print("all 601 complete bounded-family words; literal positive instructions", flush=True)
    family = bounded_family(parent, rows, target, nomination, columns)
    proxy = proxy_check(parent, nomination)
    selected_pairs = nomination["selected_pairs"]
    rebuilt, middle = reconstruct(parent, rows, target, selected_pairs)
    same(rebuilt, candidate, "candidate literal recipe")
    same(reconstruct(parent, rows, target, nomination["nominations"][0]["pairs"])[0], floor_word, "floor word recipe")
    greedy_certificate = C["load"](C["HERE"] / "vendor/pr926/CERTIFICATE.json")
    greedy_pairs = [[step["a"], step["b"]] for step in greedy_certificate["steps"]]
    validate_pairs(greedy_pairs, original["R"])
    same(reconstruct(parent, rows, target, greedy_pairs)[0], greedy, "greedy comparator recipe")
    check_bill(greedy, greedy_certificate)
    check_bill(candidate, certificate)
    need(certificate["helper_pairs"] == len(selected_pairs) == 199 and certificate["target_shears"] == 306,
         "complete basis operation counts")
    need(certificate["middle_weight"] == sum(map(len, middle)) == 4719, "middle weight")
    need(certificate["saved_beyond_parent"] == 1259 and certificate["saved_beyond_greedy"] == 31, "complete savings")
    matrix, mixed = matrix_check(original, e_rows, selected_pairs, middle)
    print("rebuild both artifacts; all five D words on 661 columns in both directions", flush=True)
    generated = output / "regenerated"
    subprocess.run([sys.executable, "-I", "-B", C["HERE"] / "build.py", "--source-root", root,
                    "--output", generated], check=True)
    for name in ("candidate.json.gz", "floor-word.json.gz", "CERTIFICATE.json"):
        same(C["load"](generated / name), C["load"](C["HERE"] / name), "regeneration: " + name)
    words = dict(baseline=original, parent=parent, greedy=greedy, floor=floor_word, candidate=candidate)
    baseline_columns = boundary_columns(original)
    for word in words.values():
        for reverse in (False, True):
            need(boundary_columns(word, reverse) == baseline_columns, "arbitrary-input D boundary")
    source = source_checks(root, words)
    negative = controls(original, candidate, floor_word, certificate, nomination, columns, baseline_columns, middle, mixed)
    print("unchanged native legality and 5/9/11-stage replay: five complete words", flush=True)
    paths = {"baseline": root / C["WORD"], "parent": C["HERE"] / "vendor/pr915/candidate.json.gz",
             "greedy": C["HERE"] / "vendor/pr926/candidate.json.gz", "floor": C["HERE"] / "floor-word.json.gz",
             "candidate": C["HERE"] / "candidate.json.gz"}
    native = C["module"]("r439_matching_native", C["HERE"] / "native.py").run(root, paths, output / "native")
    bills = {name: bill(word) for name, word in words.items()}
    for name in words:
        need(bills[name]["native_ADDs"] == native[name]["common_frame_ADDs"], "literal/native ADD cost")
        bounds = native[name]["staged"]["9"]["signed_lift_prefix"]
        same([bills[name]["F"], bills[name]["B"]],
             [int(x["cancellation_free_signed_row_l1_upper"]) for x in bounds], "literal/native positive bounds")
    need(bills["candidate"]["F"] < bills["greedy"]["F"] and bills["candidate"]["B"] < bills["greedy"]["B"],
         "both prefix maxima improve beyond comparator")
    return dict(status="PASS_R439_HELPER_MATCHING", source_files=manifest["files"], predecessor_files=manifest["local_files"],
                dual=dual, bounded_family=family, discovery_proxy=proxy, matrix=matrix,
                boundary_columns=661, boundary_words_and_directions=10, bills=bills,
                candidate_sha256=C["digest"](candidate), certificate_sha256=C["digest"](certificate),
                nomination_sha256=C["digest"](nomination), source_checks=source, controls=negative, native=native,
                nine_stage_prefix_bound=nine_stage_bound(root, native),
                precision_constrained_ADD_interval=[dual["complete_ADD_floor"], bills["candidate"]["native_ADDs"]])


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
    with tempfile.TemporaryDirectory(prefix="r439-matching-") as temp:
        report = run(args.source_root, args.output or Path(temp) / "run")
        same(report, expected, "receipt differs from EXPECTED.json")
        if args.receipt:
            C["write"](args.receipt, report)
    print("PASS_R439_HELPER_MATCHING: ADDs 11,980 -> 11,949; fixed-class floor 11,948; "
          "601 budgeted words; one-ADD gap; no new kappa")
