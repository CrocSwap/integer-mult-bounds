#!/usr/bin/env python3
"""Independent literal replay and complete billing of an eight-word composition.

Set-valued streams and source-binding patterns follow PR926/967/980.
Gareth Davidson (@bitplane), with substantial OpenAI Codex assistance.
Apache-2.0. No assertion is needed for rejection in this verifier.
"""
import argparse
import ast
import copy
from pathlib import Path
import runpy
import tempfile

C = runpy.run_path(str(Path(__file__).with_name("common.py")))
need, same, load = C["need"], C["same"], C["load"]


def instructions(word):
    n = 2 * word["v"] + word["R"]
    out = []
    for phase in ("D", "A", "scatter", "B", "C"):
        if phase == "scatter":
            for j, center in enumerate(word["ret"]):
                out.append(("copy", n, center))
                for i, uses in enumerate(word["scatter"]):
                    if j in uses:
                        out.append(("add", word["v"] + i, n))
                out.append(("erase", n, center))
        else:
            for frame, d, donors in word[phase]:
                need(type(frame) is int and 0 <= frame < len(word["frames"]), "frame domain")
                need(type(d) is int and 0 <= d < n, "destination domain")
                need(type(donors) is list and len(set(donors)) == len(donors), "distinct donors")
                need(all(type(s) is int and 0 <= s < n and s != d for s in donors), "donor domain")
                out.extend(("add", d, s) for s in donors)
    return out


def execute(word, reverse=False, stream=None):
    """Sets of formal columns plus integer positive bounds; COPY work starts empty."""
    n = 2 * word["v"] + word["R"]
    symbolic = [{i} for i in range(n)] + [set()]
    positive = [1] * n + [0]
    stream = instructions(word) if stream is None else stream
    opened, peak, adds, copies, erasures = False, 1, 0, 0, 0
    for kind, d, s in reversed(stream) if reverse else stream:
        if reverse and kind != "add":
            kind = "erase" if kind == "copy" else "copy"
        if kind == "add":
            need(d < n, "private COPY target cannot be ADD destination")
            need(s != n or opened, "private COPY read outside lifetime")
            symbolic[d].symmetric_difference_update(symbolic[s])
            positive[d] += positive[s]
            adds += 1
        elif kind == "copy":
            need(d == n and not opened and not symbolic[n] and positive[n] == 0, "COPY destination not empty")
            symbolic[n] = set(symbolic[s])
            positive[n] = positive[s]
            opened = True
            copies += 1
        elif kind == "erase":
            need(d == n and opened and symbolic[n] == symbolic[s], "ERASE original changed or missing COPY")
            symbolic[n] = set()
            positive[n] = 0
            opened = False
            erasures += 1
        else:
            raise ValueError("unknown instruction")
        peak = max(peak, positive[d])
    need(not opened and not symbolic[n] and positive[n] == 0, "unclosed private COPY")
    expected = [{i} for i in range(n)]
    for i in range(word["v"]):
        expected[word["v"] + i].add(i)
    need(symbolic[:-1] == expected, "dirty full-word boundary")
    need(copies == erasures == 9, "complete COPY bill")
    return dict(ADDs=adds, bound=peak, copies=copies, erasures=erasures,
                columns=n, instructions=len(stream))


def phase_rows(word, phase, reverse=False):
    n = 2 * word["v"] + word["R"]
    rows = [{i} for i in range(n)]
    for _, d, donors in reversed(word[phase]) if reverse else word[phase]:
        for s in donors:
            rows[d].symmetric_difference_update(rows[s])
    return rows


def literal_cleanup(word):
    fulls = [i for i, f in enumerate(word["frames"]) if sorted(f) == list(range(word["v"]))]
    need(len(fulls) == 1, "one full frame")
    reverse = []
    for phase in ("B", "A"):
        for gate in word[phase][::-1]:
            if not word["v"] <= gate[1] < 2 * word["v"]:
                reverse.append([fulls[0], gate[1], list(gate[2])])
    same(reverse, word["C"], "literal cleanup")


def literal_price(word):
    forward, reverse = execute(word), execute(word, True)
    same(forward["ADDs"], reverse["ADDs"], "reverse ADD bill")
    f, b = forward["bound"], reverse["bound"]
    local, nine = 2**6 * f * f * f * b * b, 2**18 * f**5 * b**4
    return dict(ADDs=forward["ADDs"], F=f, B=b, local_upper=str(local), nine_upper=str(nine),
                local_bits=local.bit_length(), nine_bits=nine.bit_length(),
                admitted=local < 2**104 and nine < 2**192)


def require_admission(price):
    need(int(price["local_upper"]) < 2**104, "local precision cap")
    need(int(price["nine_upper"]) < 2**192, "nine-stage precision cap")


def recipe(baseline, source_a, source_bd, word, mask):
    need(type(mask) is int and 0 <= mask <= 7, "mask domain")
    for key in baseline:
        if key not in ("A", "B", "C", "D"):
            same(word[key], baseline[key], "unchanged field " + key)
            same(source_a[key], baseline[key], "PR980 immutable geometry " + key)
            same(source_bd[key], baseline[key], "PR1062 immutable geometry " + key)
    same(sorted(word), sorted(baseline), "complete payload keys")
    for phase, flag, source in (("A", 1, source_a), ("B", 2, source_bd), ("D", 4, source_bd)):
        same(word[phase], (source if mask & flag else baseline)[phase], "exact phase splice " + phase)
        for reverse in (False, True):
            need(phase_rows(word, phase, reverse) == phase_rows(baseline, phase, reverse),
                 "phase semantic boundary " + phase)
    literal_cleanup(word)


def source_formula(root):
    name = ("research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/"
            "vendor/e8-r715-eleven-stage-whole/code/global_k.py")
    syntax = ast.parse((root / name).read_text())
    formulas = [node.value for node in ast.walk(syntax) if isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "prefix" for t in node.targets)]
    formula = ast.parse("(1 << nb) * cf ** (K + 1) * cb ** K", mode="eval").body
    need(len(formulas) == 1 and ast.dump(formulas[0]) == ast.dump(formula), "nine-stage formula binding")
    bridge = ast.parse("nb == 6 * (K - 1)", mode="eval").body
    need(any(isinstance(node, ast.Compare) and ast.dump(node) == ast.dump(bridge)
             for node in ast.walk(syntax)), "bridge exponent binding")
    need(load(root / "research/e8-bit-p111-tuned/tune/EXPECTED.json")["nine"]["bit"]
         ["charged_prefix_bits"] == 192, "retained nine-stage charge")
    return dict(K=4, bridge_exponent=18, local_cap=104, nine_cap=192)


def owner_checks(root, words):
    owner = C["module"]("composition_owner", root / C["CHECKER"])
    original = owner.Word(words["0"])
    labels = original.labels()
    result = {}
    for label, word in words.items():
        # recipe() has checked every geometry field; only scalar sections differ.
        current = copy.copy(original)
        current.w = word
        full = current.full()
        totals = current.totals()
        hypotheses, conclusions, _ = current.interface()
        d_changed = bool(int(label) & 4)
        for key, value in hypotheses.items():
            need(value is (not d_changed if key == "H2_D_frame0_targets_from_helpers" else True),
                 "unchanged owning hypothesis " + key)
        for key, value in conclusions.items():
            need(value is (not d_changed if key == "K_equals_D" else True), "owning conclusion " + key)
        need(full["columns"] == 661 and [x["rank"] for x in totals] == [7] * 9, "owning coverage")
        need(all(x["hyperplane_of_punctured_line"] for x in totals), "punctured total geometry")
        result[label] = dict(hypotheses=hypotheses, conclusions=conclusions,
                             full=full, totals=totals)
    return original, dict(labels=labels, words=result)


def controls(words, prices, owner):
    rejected = []

    def reject(label, action, reason):
        try:
            action()
        except ValueError as exc:
            need(reason in str(exc), "wrong rejection for " + label + ": " + str(exc))
            rejected.append(label)
        else:
            raise ValueError("negative control accepted: " + label)

    candidate = words["7"]
    for phase, index, label in (("A", 0, "omitted A gate"), ("B", 0, "omitted B gate"),
                                 ("D", 0, "omitted helper preparation"), ("D", -1, "omitted helper restoration")):
        bad = copy.deepcopy(candidate)
        del bad[phase][index]
        reject(label, lambda w=bad: execute(w), "boundary")
    stale = copy.deepcopy(candidate)
    stale["C"] = copy.deepcopy(words["0"]["C"])
    execute(stale)  # Same F2 inverse, but no longer the declared literal cleanup.
    reject("semantically valid stale cleanup", lambda: literal_cleanup(stale), "literal cleanup")
    altered = instructions(candidate)
    at = next(i for i, x in enumerate(altered) if x[0] == "copy")
    missing_copy = altered[:at] + altered[at + 1:]
    reject("omitted private COPY", lambda: execute(candidate, stream=missing_copy), "outside lifetime")
    er = next(i for i, x in enumerate(altered) if x[0] == "erase")
    missing_erase = altered[:er] + altered[er + 1:]
    reject("omitted private ERASE", lambda: execute(candidate, stream=missing_erase), "not empty")
    wrong_original = list(altered)
    kind, d, s = wrong_original[er]
    wrong_original[er] = kind, d, s + 1
    reject("wrong ERASE original", lambda: execute(candidate, stream=wrong_original), "original changed")
    bad = copy.deepcopy(candidate)
    bad["A"][0][0] = True
    reject("boolean frame id", lambda: execute(bad), "frame domain")
    bad = copy.deepcopy(candidate)
    bad["A"][0][2] = [bad["A"][0][1]]
    reject("self ADD", lambda: execute(bad), "donor domain")
    for field, value, label in (("ADDs", 10628, "double-counted inherited B saving"),
                               ("F", 1, "stale forward bound"), ("nine_upper", "1", "underpriced bridges")):
        bad_price = dict(prices["7"], **{field: value})
        reject(label, lambda p=bad_price: same(p, literal_price(candidate), "literal price"), "literal price")
    reject("D-only semantic success exceeds precision", lambda: require_admission(prices["4"]), "nine-stage")
    for key, cap in (("local_upper", 104), ("nine_upper", 192)):
        bad_price = dict(prices["7"], **{key: str(1 << cap)})
        reject("strict equality at " + key, lambda p=bad_price: require_admission(p), "precision cap")
    wrong_frame = copy.deepcopy(candidate)
    wrong_frame["A"][0][0] = 0
    current = copy.copy(owner)
    current.w = wrong_frame
    try:
        current.full()
    except Exception as exc:
        need(type(exc).__name__ == "Reject" and "climb not nested" in str(exc), "wrong frame rejection")
        rejected.append("non-nested physical frame")
    else:
        raise ValueError("physical frame control accepted")
    return dict(rejected=rejected, positive_controls=["stale cleanup still F2 exact",
                "D-only corner remains F2 exact while admission fails"])


def artifacts(root):
    root = Path(root).resolve()
    manifest = C["pins"](root)
    builder = C["module"]("composition_builder", C["HERE"] / "build.py")
    words, certificate = builder.build(root)
    same(certificate, load(C["HERE"] / "CERTIFICATE.json"), "complete certificate regeneration")
    same(words["7"], load(C["HERE"] / "candidate.json.gz"), "complete decoded candidate regeneration")
    return manifest, words, certificate


def run(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    manifest, words, certificate = artifacts(root)
    output.mkdir(parents=True, exist_ok=False)
    (output / "regenerated").mkdir()
    for name, word in words.items():
        C["write"](output / "regenerated" / (name + ".json.gz"), word)
    C["write"](output / "regenerated" / "CERTIFICATE.json", certificate)
    baseline, source_a, source_bd = (load(root / C["WORD"]), load(root / C["A_WORD"]),
                                     load(C["HERE"] / C["BD_WORD"]))
    same(words["0"], baseline, "baseline identity")
    same(words["6"], source_bd, "PR1062 identity")
    need((baseline["v"], baseline["R"]) == (111, 439), "fixed dimensions")
    print("eight compositions: phase maps, arbitrary dirty columns, explicit COPY/ERASE and full bounds", flush=True)
    prices = {}
    for label, word in words.items():
        recipe(baseline, source_a, source_bd, word, int(label))
        price = literal_price(word)
        recorded = certificate["corners"][label]
        same(price, {k: recorded[k] for k in price}, "macro/literal complete price")
        prices[label] = price
    need([int(k) for k, v in prices.items() if not v["admitted"]] == [4], "exact failed corner")
    need(prices["7"]["ADDs"] == 10652 and prices["6"]["ADDs"] - prices["7"]["ADDs"] == 848,
         "composition complete saving")
    prefix = source_formula(root)
    print("owning E8/frame checker, semantic D exception and rejection controls", flush=True)
    owner, checked = owner_checks(root, words)
    negatives = controls(words, prices, owner)
    native = C["module"]("composition_native", C["HERE"] / "native.py").run(
        root, output / "regenerated", prices, output / "native")
    return dict(status="PASS_R439_ABC_STAR_COMPOSITION", sources=manifest,
                certificate_sha256=C["digest"](certificate), prices=prices,
                prefix=prefix, source_checks=checked, native=native, controls=negatives,
                exact_phase_maps=dict(phases=3, directions=2, columns=661, words=8),
                literal_streams=dict(directions=2, columns=661, words=8,
                                     instructions=sum(len(instructions(w)) for w in words.values())),
                no_new_kappa=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=C["ROOT"])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--write-expected", action="store_true",
                        help="initial artifact production only; refuses to replace EXPECTED.json")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="r439-composition-") as temporary:
        receipt = run(args.source_root, args.output or Path(temporary) / "run")
        if args.write_expected:
            C["write"](C["HERE"] / "EXPECTED.json", receipt)
        else:
            same(receipt, load(C["HERE"] / "EXPECTED.json"), "complete deterministic receipt")
        if args.receipt:
            C["write"](args.receipt, receipt)
    print("PASS_R439_ABC_STAR_COMPOSITION: 8 corners; ADDs 11500 -> 10652; "
          "661 dirty columns; 5/9/11 stages; 384 bridge controls; 92/176 bits; no new kappa")


if __name__ == "__main__":
    main()
