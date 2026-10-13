#!/usr/bin/env python3
"""Exact, set-valued verification of the frozen restored-helper-star circuit.

Literal-stream and source-check patterns follow Gareth Davidson's PR926.
Prepared for @theon199 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
import copy
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile

C = runpy.run_path(str(Path(__file__).with_name("common.py")))
need, load, digest = C["need"], C["load"], C["digest"]
HERE, ROOT = C["HERE"], C["ROOT"]
PARENT = "research/r439-target-compensation/"
PAIRS = "research/r439-two-sided-compensation/"


def same(a, b, message):
    need(C["canonical"](a) == C["canonical"](b), message)


def stream(word):
    out = []
    for section in ("D", "A"):
        for _, d, sources in word[section]:
            out.extend(("add", d, s) for s in sources)
    temp = 2 * word["v"] + word["R"]
    for j, center in enumerate(word["ret"]):
        out.append(("copy", temp, center))
        for i, sources in enumerate(word["scatter"]):
            if j in sources:
                out.append(("add", word["v"] + i, temp))
        out.append(("erase", temp, center))
    for section in ("B", "C"):
        for _, d, sources in word[section]:
            out.extend(("add", d, s) for s in sources)
    return out


def positive(word, reverse=False):
    values = [1] * (2 * word["v"] + word["R"] + 1)
    peak = 1
    instructions = stream(word)
    for kind, d, s in reversed(instructions) if reverse else instructions:
        if reverse and kind != "add":
            kind = "erase" if kind == "copy" else "copy"
        if kind == "add":
            values[d] += values[s]
        elif kind == "copy":
            values[d] = values[s]
        else:
            values[d] = 0
        peak = max(peak, values[d])
    return peak


def bill(word):
    f, b = positive(word), positive(word, True)
    return dict(native_ADDs=sum(k == "add" for k, _, _ in stream(word)),
                D_adds=sum(len(g[2]) for g in word["D"]), F=f, B=b,
                local_bound=str(64 * f**3 * b**2),
                nine_stage_bound=str((1 << 18) * f**5 * b**4))


def guard(receipt):
    need(int(receipt["local_bound"]) < 1 << 104, "local precision guard")
    need(int(receipt["nine_stage_bound"]) < 1 << 192, "nine-stage precision guard")


def d_rows(word, reverse=False):
    """Sets of formal input columns; arbitrary targets and helpers remain distinct."""
    v, n = word["v"], 2 * word["v"] + word["R"]
    rows = [{i} for i in range(n)]
    for frame, d, sources in reversed(word["D"]) if reverse else word["D"]:
        need(type(frame) is int and frame == 0, "D frame zero")
        need(type(d) is int and v <= d < n, "D destination")
        need(type(sources) is list and len(sources) == len(set(sources)), "D donors distinct")
        need(all(type(s) is int and v <= s < n and s != d for s in sources), "D donors")
        need(d < 2 * v or all(s >= 2 * v for s in sources), "helper reads target")
        for s in sources:
            rows[d].symmetric_difference_update(rows[s])
    return rows


def full_rows(word, reverse=False):
    n = 2 * word["v"] + word["R"]
    rows = [{i} for i in range(n)] + [set()]
    instructions = stream(word)
    for kind, d, s in reversed(instructions) if reverse else instructions:
        if reverse and kind != "add":
            kind = "erase" if kind == "copy" else "copy"
        if kind == "add":
            rows[d].symmetric_difference_update(rows[s])
        elif kind == "copy":
            need(not rows[d], "copy target not empty")
            rows[d] = set(rows[s])
        else:
            need(rows[d] == rows[s], "erase lost copied value")
            rows[d] = set()
    need(not rows[-1], "private copy not erased")
    return rows[:-1]


def recipe(original, parent, candidate, certificate, parent_certificate):
    """Derive E K and E K H using sets, without builder functions or bit packing."""
    v, r = original["v"], original["R"]
    k = [set() for _ in range(v)]
    for frame, d, sources in original["D"]:
        need(frame == 0 and v <= d < 2 * v, "original compensation shape")
        k[d - v].symmetric_difference_update(s - 2 * v for s in sources)
    rows = copy.deepcopy(k)
    target = []
    for step in parent_certificate["steps"]:
        d, s = step["destination"], step["source"]
        need(type(d) is int and type(s) is int and 0 <= d < v and 0 <= s < v and d != s,
             "target recipe index")
        rows[d].symmetric_difference_update(rows[s])
        target.append([0, v + d, [v + s]])
    def middle(supports):
        return [[0, v + i, [2 * v + s for s in sorted(row)]] for i, row in enumerate(supports)]
    same(target + middle(rows) + target[::-1], parent["D"], "parent E K reconstruction")
    need(len(target) == 306, "target count")
    centers, leaves, edges = {}, set(), []
    base_columns = [{i for i, row in enumerate(rows) if j in row} for j in range(r)]
    saved = 0
    for step in certificate["steps"]:
        a, b = step["a"], step["b"]
        need(type(a) is int and type(b) is int and 0 <= a < r and 0 <= b < r and a != b,
             "helper index")
        need(a not in leaves and b not in leaves and b not in centers
             and len(centers.get(a, [])) < certificate["max_leaves"], "star geometry")
        centers.setdefault(a, []).append(b)
        leaves.add(b)
        edges.append([0, 2 * v + a, [2 * v + b]])
        gain = len(base_columns[b]) - len(base_columns[b] ^ base_columns[a]) - 2
        need(gain == step["gain"] and gain > 0, "fully paid edge gain")
        saved += gain
        for row in rows:
            if a in row:
                row.symmetric_difference_update({b})
    same(edges + target + middle(rows) + target[::-1] + edges[::-1], candidate["D"],
         "candidate E K H reconstruction")
    need(saved == certificate["saved_beyond_PR915"], "additive complete saving")
    need(sum(map(len, rows)) == certificate["middle_weight"], "middle weight")
    need(len(edges) == certificate["helper_edges"], "edge count")
    need(len(centers) == certificate["helper_components"], "component count")
    need(sum(len(x) == 2 for x in centers.values()) == certificate["two_leaf_stars"], "star count")
    for word in (parent, candidate):
        same({k: x for k, x in original.items() if k != "D"},
             {k: x for k, x in word.items() if k != "D"}, "non-D change")
    return {"matrix_entries": v * r, "helpers_used": len(centers) + len(leaves),
            "unused_helpers": r - len(centers) - len(leaves), "fully_paid_saving": saved}


def source_formula(root):
    path = ("research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/"
            "vendor/e8-r715-eleven-stage-whole/code/global_k.py")
    syntax = ast.parse((root / path).read_text())
    formulas = [node.value for node in ast.walk(syntax) if isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "prefix" for t in node.targets)]
    expected = ast.parse("(1 << nb) * cf ** (K + 1) * cb ** K", mode="eval").body
    need(len(formulas) == 1 and ast.dump(formulas[0]) == ast.dump(expected), "nine-stage formula")
    bridge = ast.parse("nb == 6 * (K - 1)", mode="eval").body
    need(any(isinstance(node, ast.Compare) and ast.dump(node) == ast.dump(bridge)
             for node in ast.walk(syntax)), "nine-stage bridge exponent")
    need(load(root / "research/e8-bit-p111-tuned/tune/EXPECTED.json")["nine"]["bit"]
         ["charged_prefix_bits"] == 192, "nine-stage charge")


def controls(original, parent, candidate, cert, parent_cert):
    failures = []
    wanted = d_rows(original)
    def reject(label, action):
        try:
            action()
        except ValueError:
            failures.append(label)
        else:
            raise ValueError("negative control accepted: " + label)
    def boundary(word):
        need(d_rows(word) == wanted, "dirty boundary mismatch")
    h, m, v = cert["helper_edges"], 306, 111
    for name, index in (("helper preparation", 0), ("helper restoration", -1),
                        ("target preparation", h), ("target restoration", -h - 1)):
        changed = copy.deepcopy(candidate)
        changed["D"].pop(index)
        reject("omit " + name, lambda: boundary(changed))
    changed = copy.deepcopy(candidate)
    changed["D"][h + m:h + m + v] = copy.deepcopy(parent["D"][m:m + v])
    reject("omit helper column transformation", lambda: boundary(changed))
    changed = copy.deepcopy(candidate)
    del changed["D"][:h]
    bad = d_rows(changed)
    need(all((x & set(range(222))) == (y & set(range(222))) for x, y in zip(bad, wanted)),
         "clean-helper negative-control premise")
    reject("clean helpers hide omitted preparation", lambda: boundary(changed))
    changed = copy.deepcopy(candidate)
    del changed["D"][h:h + m]
    bad = d_rows(changed)
    need(all({j for j in x if j >= 222} == {j for j in y if j >= 222}
             for x, y in zip(bad, wanted)), "helper-only negative-control premise")
    reject("helper-only inputs hide target preparation", lambda: boundary(changed))
    changed = copy.deepcopy(candidate)
    changed["D"][-h - m:-h] = copy.deepcopy(parent["D"][:m])
    reject("target inverse in forward order", lambda: boundary(changed))
    changed = copy.deepcopy(candidate)
    changed["D"][0][0] = 1
    reject("wrong D frame", lambda: boundary(changed))
    changed = copy.deepcopy(cert)
    changed["steps"][0]["a"] = True
    reject("boolean helper index", lambda: recipe(original, parent, candidate, changed, parent_cert))
    changed = copy.deepcopy(cert)
    changed["max_leaves"] = 1
    reject("shared center outside pair class", lambda: recipe(original, parent, candidate, changed, parent_cert))
    changed = copy.deepcopy(cert)
    changed["saved_beyond_PR915"] += h
    reject("omit restoration charge", lambda: recipe(original, parent, candidate, changed, parent_cert))
    reject("strict precision equality", lambda: guard(dict(local_bound=str(1 << 104), nine_stage_bound="1")))
    reject("nine-stage overrun below local cap", lambda: guard(dict(local_bound="1", nine_stage_bound=str(1 << 192))))
    changed = copy.deepcopy(candidate)
    changed["D"][-h:] = list(reversed(changed["D"][-h:]))
    need(d_rows(changed) == wanted, "commuting helper restoration positive control")
    neutral = copy.deepcopy(candidate)
    neutral["D"][:0] = [[0, 222, [223]], [0, 222, [223]]]
    need(d_rows(neutral) == wanted, "paid neutral-pair boundary")
    need(bill(neutral)["native_ADDs"] == bill(candidate)["native_ADDs"] + 2, "neutral pair bill")
    return dict(rejected=failures, positive=["commuting helper restoration", "neutral pair charged two ADDs"])


def run(root, work, native=False, check_expected=True):
    manifest = C["pins"](root)
    work.mkdir(parents=True, exist_ok=False)
    subprocess.run([sys.executable, "-I", "-B", HERE / "build.py", "--source-root", root,
                    "--output", work / "rebuilt"], check=True)
    cert, pair_cert = load(HERE / "CERTIFICATE.json"), load(HERE / "PAIR-CONTROL.json")
    candidate = load(HERE / "candidate.json.gz")
    same(load(work / "rebuilt/candidate-certificate.json"), cert, "candidate search receipt")
    same(load(work / "rebuilt/pair-control-certificate.json"), pair_cert, "pair-control search receipt")
    same(load(work / "rebuilt/candidate.json.gz"), candidate, "candidate payload")
    original, parent = load(root / C["WORD"]), load(root / (PARENT + "candidate.json.gz"))
    words = dict(baseline=original, parent=parent, predecessor_pairs=load(root / (PAIRS + "candidate.json.gz")),
                 pair_control=load(work / "rebuilt/pair-control.json.gz"), candidate=candidate)
    parent_cert = load(root / (PARENT + "CERTIFICATE.json"))
    matrix = recipe(original, parent, candidate, cert, parent_cert)
    recipe(original, parent, words["pair_control"], pair_cert, parent_cert)
    source_formula(root)
    bills, source = {}, {}
    owner = C["module"]("r439_source_checker", root / C["CHECKER"])
    expected_full = [{i, i - 111} if 111 <= i < 222 else {i} for i in range(661)]
    for name, word in words.items():
        bills[name] = bill(word)
        guard(bills[name])
        for reverse in (False, True):
            need(d_rows(word, reverse) == d_rows(original), name + " D boundary")
            need(full_rows(word, reverse) == expected_full, name + " complete boundary")
        if name in ("baseline", "candidate"):
            _, labels, full, hypotheses, conclusions, info = owner.check(word)
            h, c = dict.fromkeys(hypotheses, True), dict.fromkeys(conclusions, True)
            if name == "candidate":
                h["H2_D_frame0_targets_from_helpers"] = False
                c["K_equals_D"] = False
            same(hypotheses, h, "source hypotheses")
            same(conclusions, c, "source conclusions")
            source[name] = dict(labels=labels, full=full, hypotheses=hypotheses, conclusions=conclusions, info=info)
    for name, receipt in (("candidate", cert), ("pair_control", pair_cert)):
        same(bills[name], {k: receipt[k] for k in bills[name]}, "complete literal invoice")
    need(bills["candidate"]["native_ADDs"] == 11783, "candidate bill")
    need(bills["predecessor_pairs"]["native_ADDs"] == 11980, "PR926 bill")
    report = dict(status="PASS_R439_HELPER_STARS", sources=manifest["files"], matrix=matrix, bills=bills,
                  source_checks=source, input_columns=661, words=5, directions=2,
                  controls=controls(original, parent, candidate, cert, parent_cert),
                  certificate_sha256=digest(cert), candidate_sha256=digest(candidate))
    if native:
        runner = C["module"]("helper_stars_native", HERE / "native.py")
        native_report = runner.run(root, root / C["WORD"], root / (PARENT + "candidate.json.gz"),
                                   HERE / "candidate.json.gz", work / "native")
        if check_expected:
            same(native_report, load(HERE / "NATIVE.json"), "native receipt")
    if check_expected:
        same(report, load(HERE / "EXPECTED.json"), "complete verification receipt")
    return report


if __name__ == "__main__":
    # The inherited owning checker uses assertions. Preserve them under python -O.
    if not __debug__:
        raise SystemExit(subprocess.call([sys.executable, "-I", "-B", __file__, *sys.argv[1:]]))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--native", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="r439-stars-verify-") as temp:
        run(args.source_root.resolve(), args.output or Path(temp) / "run", args.native)
    print("PASS_R439_HELPER_STARS: 64 three-helper stars; ADDs 11980 -> 11783; "
          "200 beyond same-seed pairs; 661 columns; 14 controls; no new kappa")
