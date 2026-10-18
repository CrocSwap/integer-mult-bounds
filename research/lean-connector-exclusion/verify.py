#!/usr/bin/env python3
"""Check the source binding, independent census, Lean proof and controls.

SPDX-License-Identifier: Apache-2.0
Hanson Sun, with substantial OpenAI Codex assistance.
No predecessor executable is imported. No third-party Python dependency.
"""

import argparse
from collections import Counter
from hashlib import sha1, sha256
from itertools import product
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
TOOLCHAIN = "leanprover/lean4:v4.28.0"
LEAN_COMMIT = "7e01a1bf5c70fc6167d49c345d3bf80596e9a79b"
ALLOWED_AXIOMS = {"propext", "Quot.sound"}
THEOREMS = (
    "covered_iff", "missing_certificate", "code_exclusion",
    "pairing_five_has_code", "five_source_exclusion", "code_is_pairing",
    "code_shape", "four_source_attainment", "near_word_exact",
    "twelve_toggle_attainment", "repair_shape",
)
TABLE_PATTERN = re.compile(
    r"(-- BEGIN MISSING WITNESSES\n"
    r"def witnesses : List \(List \(List \(List Nat\)\)\) := )(.*?)(\n-- END MISSING WITNESSES)",
    re.S,
)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sources(root, manifest):
    for relative, pins in manifest["files"].items():
        content = (root / relative).read_bytes()
        need(sha256(content).hexdigest() == pins["sha256"], f"source SHA256: {relative}")
        blob = sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
        need(blob == pins["git_blob"], f"source Git blob: {relative}")


def insertion_word(code):
    # Reconstruct a pairing by removing the first endpoint's mate recursively.
    # This uses neither restricted-growth DFS nor endpoint-matching generation.
    result = [0, 0]
    for slot in reversed(code):
        shifted = [label + 1 for label in result]
        result = [0] + shifted[:slot] + [0] + shifted[slot:]
    return result


def interval_masks(word):
    # A difference of prefixes is the odd-occurrence mask of a contiguous
    # interval. Recount intervals directly, rather than sharing Lean's XOR scan.
    return {
        sum(1 << label for label, count in Counter(word[start:stop]).items() if count % 2)
        for start in range(len(word) + 1)
        for stop in range(start, len(word) + 1)
    }


def census(n):
    domains = [range(2 * k - 1) for k in range(n, 1, -1)]
    entries = []
    witnesses = {}
    for code in product(*domains):
        word = insertion_word(code)
        need(Counter(word) == Counter({j: 2 for j in range(n)}), "illegal insertion word")
        masks = interval_masks(word)
        entries.append((word, sum(1 << mask for mask in masks)))
        if n == 5:
            absent = sorted(set(range(32)) - masks)
            need(bool(absent), "five-source universal word found")
            witnesses[code] = absent[0]
    need(len({tuple(w) for w, _ in entries}) == len(entries), "duplicate pairing code")
    entries.sort()
    histogram = Counter(mask.bit_count() for _, mask in entries)
    return {
        "sources": n,
        "pairings": len(entries),
        "histogram": {str(k): v for k, v in sorted(histogram.items())},
        "canonical_entries_sha256": sha256(json.dumps(entries, separators=(",", ":")).encode()).hexdigest(),
        "max_coverage": max(histogram),
    }, witnesses


def witness_table(source):
    match = TABLE_PATTERN.search(source)
    need(match is not None, "missing Lean witness table")
    return json.loads(match.group(2))


def replace_table(source, table):
    match = TABLE_PATTERN.search(source)
    need(match is not None, "missing Lean witness table")
    return source[:match.start(2)] + json.dumps(table) + source[match.end(2):]


def audit_axioms(output, names):
    found = {}
    pattern = re.compile(
        r"^'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)$", re.M
    )
    for name, body in pattern.findall(output):
        axioms = sorted(part.strip() for part in body.split(",") if part.strip())
        need(set(axioms) <= ALLOWED_AXIOMS, f"unapproved axioms for {name}: {axioms}")
        need(name not in found, f"duplicate axiom report: {name}")
        found[name] = axioms
    need(set(found) == set(names), f"incomplete axiom reports: {sorted(found)}")
    return found


def lean_command(explicit):
    if explicit:
        resolved = shutil.which(explicit)
        need(resolved is not None, f"Lean executable unavailable: {explicit}")
        return str(Path(resolved).resolve())
    elan = shutil.which("elan")
    need(elan is not None, "Install Lean 4.28.0, or pass --lean /absolute/path/to/lean")
    env = os.environ.copy()
    env["ELAN_TOOLCHAIN"] = TOOLCHAIN
    result = subprocess.run(
        [elan, "which", "lean"],
        env=env, text=True, capture_output=True, timeout=30,
    )
    need(result.returncode == 0, f"Lean 4.28.0 must already be installed: {result.stderr.strip()}")
    return result.stdout.strip()


def run_lean(lean, directory, filename, *, object_file=False, warning_errors=True):
    env = os.environ.copy()
    for key in ("LEAN_PATH", "LEAN_SRC_PATH", "LEAN_OPTS", "LEAN_SYSROOT"):
        env.pop(key, None)
    env["LEAN_PATH"] = str(directory)
    command = [lean, f"-DwarningAsError={'true' if warning_errors else 'false'}"]
    if object_file:
        command += ["-o", str(Path(filename).with_suffix(".olean"))]
    command.append(filename)
    result = subprocess.run(command, cwd=directory, env=env, text=True,
                            capture_output=True, timeout=240)
    return result.returncode, result.stdout + result.stderr


def rejection_controls(lean, directory, source, manifest):
    controls = []
    for name, value in (("covered_mask_zero", 0), ("out_of_range_mask", 32)):
        table = witness_table(source)
        table[0][0][0][0] = value
        filename = name + ".lean"
        (directory / filename).write_text(replace_table(source, table), encoding="utf-8")
        status, output = run_lean(lean, directory, filename)
        need(status != 0 and "decide" in output and "error:" in output,
             f"corrupted witness not rejected mathematically: {name}\n{output[-2000:]}")
        controls.append(name)

    for name, statement in (
        ("false_ten_toggle_universality", "ConnectorBoundary.Universal 5 ConnectorBoundary.nearWord"),
        ("false_twelve_toggle_exclusion", "¬ ConnectorBoundary.Universal 5 ConnectorBoundary.repairWord"),
    ):
        filename = name + ".lean"
        (directory / filename).write_text(
            f"import Boundary\nexample : {statement} := by decide\n", encoding="utf-8"
        )
        status, output = run_lean(lean, directory, filename)
        need(status != 0 and "decide" in output and "error:" in output,
             f"false claim not rejected: {name}\n{output[-2000:]}")
        controls.append(name)

    # These controls must compile, then fail the compiled dependency audit.
    for name, text in (
        ("custom_axiom", "axiom injected : False\ntheorem bad : False := injected"),
        ("sorry_axiom", "theorem bad : False := sorryAx _ true"),
        ("native_decide_axiom", "theorem bad : (1 : Nat) = 1 := by native_decide"),
    ):
        filename = name + ".lean"
        (directory / filename).write_text(
            "import Std\n" + text + "\n#print axioms bad\n", encoding="utf-8"
        )
        # Only deliberately invalid assumption controls allow warnings, so a
        # compiled sorryAx report reaches the dependency audit being tested.
        status, output = run_lean(lean, directory, filename, warning_errors=False)
        need(status == 0, f"axiom control did not reach dependency audit: {name}\n{output}")
        try:
            audit_axioms(output, ["bad"])
        except ValueError as error:
            need("unapproved axioms" in str(error), f"wrong axiom rejection: {name}")
        else:
            raise ValueError(f"axiom control accepted: {name}")
        controls.append(name)

    # Real on-disk source corruption, with no edits to the checkout.
    source_copy = directory / "source-control"
    for relative in manifest["files"]:
        destination = source_copy / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / relative, destination)
    altered = source_copy / "research/universal-connector-boundary/CERTIFICATE.json"
    altered.write_bytes(altered.read_bytes() + b"\n")
    try:
        sources(source_copy, manifest)
    except ValueError as error:
        need("source SHA256:" in str(error), "wrong source corruption rejection")
    else:
        raise ValueError("changed predecessor certificate accepted")
    controls.append("predecessor_source_corruption")
    return controls


def verify(lean):
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    sources(REPO, manifest)
    predecessor = json.loads(
        (REPO / "research/universal-connector-boundary/CERTIFICATE.json").read_text(encoding="utf-8")
    )
    source = (HERE / "Boundary.lean").read_text(encoding="utf-8")
    need(not re.search(r"\b(sorry|admit|axiom|native_decide)\b", source), "forbidden proof escape")
    censuses = []
    for n in (4, 5):
        result, missing = census(n)
        need(result == predecessor["censuses"][n - 4], f"PR943 census differs for n={n}")
        censuses.append(result)
        if n == 5:
            expected_table = [[[[missing[a, b, c, d] for d in range(3)] for c in range(5)]
                               for b in range(7)] for a in range(9)]
            need(witness_table(source) == expected_table, "Lean witness data differ from interval recount")
    four = predecessor["schedules"]["four_all"]["source_word"]
    near = predecessor["schedules"]["five_extra_output"]["source_word"]
    repair = predecessor["schedules"]["five_extra_source"]["source_word"]
    for name, word in (("fourWord", four), ("nearWord", near), ("repairWord", repair)):
        match = re.search(rf"def {name} : List Nat := (\[[^\n]+\])", source)
        need(match is not None and json.loads(match.group(1)) == word, f"changed literal witness {name}")
    need(interval_masks(four) == set(range(16)), "four-source positive control")
    need(set(range(32)) - interval_masks(near) == {21}, "31-mask sharpness witness")
    need(interval_masks(repair) == set(range(32)), "twelve-toggle positive control")
    version = subprocess.run([lean, "--version"], text=True, capture_output=True,
                             check=True, timeout=30).stdout.strip()
    need(re.fullmatch(rf"Lean \(version 4\.28\.0, [^,]+, commit {LEAN_COMMIT}, Release\)", version),
         f"wrong compiler version/commit: {version}")
    print("Census and source pins match; compiling 11 audited Lean statements.", flush=True)
    with tempfile.TemporaryDirectory(prefix="lean-connector-exclusion-") as temporary:
        directory = Path(temporary)
        (directory / "Boundary.lean").write_text(source, encoding="utf-8")
        status, output = run_lean(lean, directory, "Boundary.lean", object_file=True)
        need(status == 0, f"Lean proof failed:\n{output}")
        axioms = audit_axioms(output, [f"ConnectorBoundary.{name}" for name in THEOREMS])
        print("Kernel build and all 11 axiom audits pass; checking rejection controls.", flush=True)
        controls = rejection_controls(lean, directory, source, manifest)
    return {
        "schema": "lean-connector-exclusion-v1",
        "status": "PASS_SCOPED_FORMALIZATION",
        "base_commit": manifest["base_commit"],
        "subject_pr": manifest["subject_pr"],
        "subject_head": manifest["subject_head"],
        "lean_version": "4.28.0", "lean_commit": LEAN_COMMIT,
        "formal_source_sha256": sha256(source.encode()).hexdigest(),
        "censuses": censuses, "compiled_theorems": len(THEOREMS),
        "axioms": axioms, "negative_controls": controls,
        "source_pins_checked": len(manifest["files"]),
        "scope": "Pairing grammar and finite prefix-mask coverage only; no full query-cost or multiplication theorem.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lean", help="Lean 4.28.0 binary; default uses the installed Elan toolchain")
    parser.add_argument("--write", type=Path, help="write a new receipt; never overwrite")
    args = parser.parse_args()
    result = verify(lean_command(args.lean))
    expected = HERE / "EXPECTED.json"
    need(expected.exists(), "missing EXPECTED.json")
    need(result == json.loads(expected.read_text(encoding="utf-8")), "receipt differs from EXPECTED.json")
    if args.write:
        with args.write.open("x", encoding="utf-8") as output:
            json.dump(result, output, indent=2, sort_keys=True)
            output.write("\n")
    print(f"PASS_LEAN_CONNECTOR_EXCLUSION pairings=945 theorems={len(THEOREMS)} controls={len(result['negative_controls'])}")


if __name__ == "__main__":
    main()
