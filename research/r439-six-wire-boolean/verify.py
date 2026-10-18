#!/usr/bin/env python3
"""Exact independent local checks and unchanged full/native replay. Apache-2.0.

Prepared for Gareth Davidson (@bitplane), with OpenAI Codex assistance.
This checker does not import the Gaussian synthesis implementation.
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


def validate_ops(ops):
    need(type(ops) is list and ops, "nonempty operation list")
    for op in ops:
        need(type(op) is list and len(op) == 2, "operation pair")
        d, s = op
        need(type(d) is int and type(s) is int and 0 <= d < 6 and 0 <= s < 6 and d != s,
             "elementary transvection")


def act(ops, value, positive=False):
    result = list(value)
    for d, s in ops:
        if positive:
            result[d] += result[s]
        else:
            result[d] ^= result[s]
    return result


def local_check(old, new):
    validate_ops(old)
    validate_ops(new)
    strict = [0, 0]
    # Entire Boolean truth tables, independently from builder's packed rows.
    for x in range(64):
        values = [(x >> i) & 1 for i in range(6)]
        need(act(old, values) == act(new, values), "local Boolean map")
    # Column images, including the reverse positive map, not just row sums.
    for reverse in (False, True):
        a, b = (old[::-1], new[::-1]) if reverse else (old, new)
        for col in range(6):
            values = [int(i == col) for i in range(6)]
            before, after = act(a, values, True), act(b, values, True)
            need(all(y <= x for x, y in zip(before, after)), "positive entrywise guard")
            strict[int(reverse)] += sum(y < x for x, y in zip(before, after))
    return strict


def check_certificate(parent, candidate, cert):
    need(cert["format"] == "r439-six-wire-boolean/1" and type(cert["seed"]) is int and cert["seed"] == 19,
         "certificate version/seed")
    need(cert["parent_sha256"] == C["digest"](parent), "parent digest")
    need(cert["candidate_sha256"] == C["digest"](candidate), "candidate digest")
    need(len(cert["blocks"]) == 60, "sixty-block domain")
    need([r["frame"] for r in cert["blocks"]] == list(range(266, 326)), "frame domain")
    total, selected, strict_maps, reports = 0, 0, 0, []
    candidate_a, cursor = [], 0
    for item in cert["blocks"]:
        frame, start, end = (item[x] for x in ("frame", "start", "end"))
        need(all(type(i) is int for i in (frame, start, end)), "integer frame/range")
        indices = [i for i, g in enumerate(parent["A"]) if g[0] == frame]
        need(indices == list(range(start, end)) and cursor <= start < end, "complete source block")
        old_gates = parent["A"][start:end]
        wires = sorted({x for _, d, ss in old_gates for x in [d, *ss]})
        same(wires, item["wires"], "physical wires")
        need(len(wires) == 6 and all(r < parent["v"] or r >= 2 * parent["v"] for r in wires), "six z wires")
        old = [[wires.index(d), wires.index(s)] for _, d, ss in old_gates for s in ss]
        same(old, item["old"], "source operations")
        candidate_a.extend(copy.deepcopy(parent["A"][cursor:start]))
        new = item["new"]
        if new is None:
            need(item["saved_A"] == 0 and type(item["saved_A"]) is int, "unselected saving")
            candidate_a.extend(copy.deepcopy(old_gates))
        else:
            strict = local_check(old, new)
            need({r for op in new for r in op} == set(range(6)), "all six frame paths retained")
            need(len(new) < len(old) and type(item["saved_A"]) is int and
                 item["saved_A"] == len(old) - len(new), "shorter cost")
            candidate_a.extend([[frame, wires[d], [wires[s]]] for d, s in new])
            total += len(old) - len(new)
            selected += 1
            strict_maps += strict[0] > 0
            reports.append({"frame": frame, "before": len(old), "after": len(new),
                            "strict_positive_entries": strict})
        cursor = end
    candidate_a.extend(copy.deepcopy(parent["A"][cursor:]))
    expected = copy.deepcopy(parent)
    expected["A"] = candidate_a
    v = parent["v"]
    z = [g for phase in ("A", "B") for g in expected[phase] if not v <= g[1] < 2 * v]
    expected["C"] = [[1, d, list(ss)] for _, d, ss in z[::-1]]
    same(expected, candidate, "exact splice with literal cleanup")
    same(cert["summary"], {"trials": 172800, "selected": selected, "saved_A": total}, "summary accounting")
    need(selected == 7 and total == 19 and strict_maps == 5, "new construction summary")
    return {"selected": selected, "saved_A": total, "saved_complete": 2 * total,
            "changed_positive_maps": strict_maps, "Boolean_inputs": 64 * selected,
            "positive_column_pairs": 12 * selected, "blocks": reports}


def instructions(word):
    n, v = 2 * word["v"] + word["R"], word["v"]
    result = []
    for phase in ("D", "A", "scatter", "B", "C"):
        if phase == "scatter":
            for j, q in enumerate(word["ret"]):
                result.append(("copy", n, q))
                for i, row in enumerate(word["scatter"]):
                    if j in row:
                        result.append(("add", v + i, n))
                result.append(("erase", n, q))
        else:
            for _, d, sources in word[phase]:
                result.extend(("add", d, s) for s in sources)
    return result


def word_checks(word):
    n, v = 2 * word["v"] + word["R"], word["v"]
    program = instructions(word)
    summaries = []
    for reverse in (False, True):
        ops = [("erase" if k == "copy" else "copy" if k == "erase" else k, d, s)
               for k, d, s in program[::-1]] if reverse else program
        # A separate set-valued arbitrary-dirt interpreter plus positive ADDs.
        values = [{r} for r in range(n)] + [set()]
        positive = [1] * n + [0]
        bound = 1
        for kind, d, s in ops:
            if kind == "add":
                values[d] ^= values[s]
                positive[d] += positive[s]
            elif kind == "copy":
                need(not values[d], "fresh COPY temporary")
                values[d] = set(values[s])
                positive[d] = positive[s]
            else:
                need(values[d] == values[s], "ERASE restoration")
                values[d] = set()
                positive[d] = 0
            bound = max(bound, positive[d])
        expected = [{r} if not v <= r < 2 * v else {r, r - v} for r in range(n)] + [set()]
        need(values == expected, "complete arbitrary-dirt endpoint")
        summaries.append(bound)
    forward, backward = summaries
    local = 64 * forward ** 3 * backward ** 2
    nine = (1 << 18) * forward ** 5 * backward ** 4
    need(local < 1 << 104 and nine < 1 << 192, "precision cap")
    return {"F": forward, "B": backward, "local_payload_bits": local.bit_length(),
            "nine_stage_prefix_bits": nine.bit_length(), "nine_stage_bound": str(nine),
            "ADDs": sum(k == "add" for k, _, _ in program), "columns_each_order": n,
            "instructions_both_orders": 2 * len(program)}


def prefix_binding(root):
    path = next(p for p in C["load"](C["HERE"] / "SOURCES.json")["files"] if p.endswith("/global_k.py"))
    tree = ast.parse((Path(root) / path).read_text())
    expressions = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ("nb", "prefix"):
                    expressions[target.id] = node.value
    expected = {"prefix": "(1<<nb)*cf**(K+1)*cb**K"}
    for name, expr in expected.items():
        same(ast.dump(expressions[name]), ast.dump(ast.parse(expr, mode="eval").body), "prefix source expression")
    bridge_assertion = ast.dump(ast.parse("nb == 6*(K-1)", mode="eval").body)
    need(any(ast.dump(term) == bridge_assertion for node in ast.walk(tree) if isinstance(node, ast.Assert)
             for term in ast.walk(node.test)), "source bridge assertion")
    return {"stages": 9, "K": 4, "bridges": 18, "formula": "2^18 * F^5 * B^4", "source": path}


def source_checks(root, words):
    checker = C["module"]("pinned_xcheck", Path(root) / C["CHECKER"])
    results = {}
    for name, word in words.items():
        _, labels, full, h, c, info = checker.check(word)
        need(all(x is True for x in h.values()), "all original H1-H5")
        need(all(x is True for x in c.values()), "all original conclusions")
        need(full["columns"] == 661, "source symbolic column coverage")
        results[name] = {"labels": labels, "full": full, "hypotheses": h, "conclusions": c, "info": info}
    return checker, results


def controls(parent, candidate, cert, checker):
    rejected = []

    def reject(name, function, reason):
        try:
            function()
        except (ValueError, checker.Reject) as error:
            need(reason in str(error), "unexpected rejection: " + name + ": " + str(error))
            rejected.append(name)
        else:
            raise ValueError("accepted negative control: " + name)

    selected = next(i for i, r in enumerate(cert["blocks"]) if r["new"] is not None)
    def changed(name, edit, reason):
        item = copy.deepcopy(cert)
        edit(item["blocks"][selected])
        reject(name, lambda: check_certificate(parent, candidate, item), reason)

    changed("dropped Boolean gate", lambda r: r["new"].pop(), "local Boolean map")
    changed("target or wrong physical participant", lambda r: r["wires"].__setitem__(0, 111), "physical wires")
    changed("partial block boundary", lambda r: r.__setitem__("end", r["end"] - 1), "complete source block")
    changed("boolean gate coordinate", lambda r: r["new"][0].__setitem__(0, True), "elementary transvection")
    changed("unpaid saving", lambda r: r.__setitem__("saved_A", r["saved_A"] + 1), "shorter cost")
    changed("self addition", lambda r: r["new"][0].__setitem__(0, r["new"][0][1]), "elementary transvection")
    old = [[0, 1]]
    bloated = [[0, 1], [2, 3], [2, 3]]
    reject("Boolean equality hides positive growth", lambda: local_check(old, bloated), "positive entrywise guard")
    stale = copy.deepcopy(candidate)
    stale["C"] = copy.deepcopy(parent["C"])
    w = checker.Word(stale)
    w.full()
    h, conclusions, _ = w.interface()
    need(h["H4_C_literal_reverse_at_full"] is False and all(conclusions.values()), "stale cleanup control premise")
    rejected.append("semantically equal but unpaired literal cleanup")
    reject("stale cleanup exact splice", lambda: check_certificate(parent, stale, dict(cert, candidate_sha256=C["digest"](stale))),
           "exact splice")
    broken = copy.deepcopy(candidate)
    del broken["A"][0]
    reject("dropped physical gate", lambda: word_checks(broken), "endpoint")
    altered = copy.deepcopy(candidate)
    altered["stats"]["junk_wires"] += 1
    reject("unrelated payload edit with rebound digest",
           lambda: check_certificate(parent, altered, dict(cert, candidate_sha256=C["digest"](altered))), "exact splice")
    reject("boolean receipt field", lambda: same({"n": 1}, {"n": True}, "strict receipt"), "strict receipt")
    return rejected


def run(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    manifest = C["pins"](root)
    output.mkdir(parents=True, exist_ok=False)
    baseline = C["load"](root / C["WORD"])
    parent = C["load"](C["HERE"] / "vendor/pr936/candidate.json.gz")
    candidate = C["load"](C["HERE"] / "candidate.json.gz")
    cert = C["load"](C["HERE"] / "CERTIFICATE.json")
    regenerated = output / "regenerated"
    print("reproduce all 172,800 bounded nominations", flush=True)
    with (output / "search.log").open("x") as log:
        subprocess.run([sys.executable, "-I", "-B", C["HERE"] / "build.py", "--out", regenerated],
                       check=True, stdout=log, stderr=subprocess.STDOUT)
    same(C["load"](regenerated / "candidate.json.gz"), candidate, "candidate regeneration")
    same(C["load"](regenerated / "CERTIFICATE.json"), cert, "complete search certificate regeneration")
    print("independent truth tables, positive columns, full arbitrary-dirt words", flush=True)
    local = check_certificate(parent, candidate, cert)
    words = {"baseline": baseline, "parent936": parent, "candidate": candidate}
    scalar = {name: word_checks(word) for name, word in words.items()}
    need([scalar[k]["ADDs"] for k in words] == [24305, 23711, 23673], "full independent ADD accounting")
    for k in ("F", "B"):
        need(scalar["candidate"][k] <= scalar["parent936"][k] <= scalar["baseline"][k], "full prefix domination")
    source_prefix = prefix_binding(root)
    print("unchanged E8 geometry, 661 symbolic columns and original H1-H5", flush=True)
    checker, source = source_checks(root, words)
    negatives = controls(parent, candidate, cert, checker)
    print("fresh native legality and 5/9/11 stages on all three words", flush=True)
    native = C["module"]("six_wire_native", C["HERE"] / "native.py").run(
        root, root / C["WORD"], C["HERE"] / "vendor/pr936/candidate.json.gz",
        C["HERE"] / "candidate.json.gz", output / "native")
    for label in words:
        need(native[label]["common_frame_ADDs"] == scalar[label]["ADDs"], "independent/native ADD agreement")
        staged = native[label]["staged"]["5"]
        need(staged["payload_prefix_bits"] == scalar[label]["local_payload_bits"], "independent/native payload agreement")
        need([int(row["cancellation_free_signed_row_l1_upper"]) for row in staged["signed_lift_prefix"]]
             == [scalar[label]["F"], scalar[label]["B"]], "independent/native positive bound agreement")
        need(int(staged["payload_prefix_upper"]) == 64 * scalar[label]["F"] ** 3 * scalar[label]["B"] ** 2,
             "independent/native exact payload agreement")
    return {"status": "PASS_R439_SIX_WIRE_BOOLEAN", "sources": manifest,
            "word_sha256": {name: C["digest"](word) for name, word in words.items()},
            "certificate_sha256": C["digest"](cert), "local": local, "scalar": scalar,
            "prefix_source": source_prefix, "source_checks": source, "native": native,
            "controls_rejected": negatives}


def main():
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
    with tempfile.TemporaryDirectory(prefix="r439-six-wire-") as tmp:
        result = run(args.source_root, args.output or Path(tmp) / "run")
        same(result, expected, "receipt differs from EXPECTED.json")
        if args.receipt:
            C["write"](args.receipt, result)
    print("PASS_R439_SIX_WIRE_BOOLEAN: 7 blocks; 38 further ADDs; 632 versus PR589; "
          "H1-H5; 5/9/11 stages; 12 controls; no new kappa")


if __name__ == "__main__":
    main()
