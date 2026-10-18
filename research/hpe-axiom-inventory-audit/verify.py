#!/usr/bin/env python3
"""Reproduce HPE axiom-coverage failures and check a proposed repair.

Apache-2.0. Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance.
The driver experiments substitute subprocess results. They do not build Lean.
"""
import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TARGET = "research/hyperplane-end-lean/verify.py"
PROBES = "research/hyperplane-end-lean/PrintAxioms.lean"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pinned_inputs():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    files = {}
    for item in manifest["files"]:
        if item["usage"] != "input":
            continue
        name = item["path"]
        path = (ROOT / name).resolve()
        require(path.is_relative_to(ROOT), "input outside repository")
        data = path.read_bytes()
        require(sha(data) == item["sha256"], "source drift: " + name)
        blob = sha_git_blob(data)
        require(blob == item["git_blob"], "Git blob drift: " + name)
        files[name] = data
    require(TARGET in files and PROBES in files, "missing audited inputs")
    return files


def sha_git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def run_driver(implementation, directory, queries, transcript):
    """Execute the real main(), stubbing only its expensive run() boundary."""
    (directory / PROBES).write_text(queries, encoding="utf-8")
    namespace = {"__name__": "audited_hpe_driver", "__file__": str(directory / TARGET)}
    exec(compile(implementation, str(directory / TARGET), "exec"), namespace)
    calls = []

    def captured_run(command, timeout):
        calls.append(command)
        if command == ["lake", "build"]:
            require(timeout == 3600, "unexpected build timeout")
            return "Build completed successfully.\n"
        require(command == ["lake", "env", "lean", "PrintAxioms.lean"],
                "unexpected subprocess: " + repr(command))
        require(timeout == 1200, "unexpected probe timeout")
        return transcript

    namespace["run"] = captured_run
    previous = sys.argv
    sys.argv = ["verify.py", "--no-cache"]
    output = io.StringIO()
    code = 0
    try:
        with contextlib.redirect_stdout(output):
            try:
                namespace["main"]()
            except SystemExit as error:
                code = error.code
    finally:
        sys.argv = previous
    text = output.getvalue()
    reported = re.findall(r"^axioms: (\d+) results,", text, flags=re.M)
    return {
        "accepted": code == 0 and text.rstrip().endswith("\nPASS"),
        "exit_code": code,
        "reported_results": int(reported[0]) if reported else None,
        "subprocess_calls": len(calls),
        "stdout_sha256": sha(text.encode()),
    }


def report(name, axioms=()):
    if not axioms:
        return f"'{name}' does not depend on any axioms\n"
    return f"'{name}' depends on axioms: [{', '.join(axioms)}]\n"


def audit():
    inputs = pinned_inputs()
    original = inputs[TARGET].decode()
    queries = inputs[PROBES].decode()
    # This is the immutable source inventory, independently read from the pin.
    lines = queries.splitlines(keepends=True)
    names = [line.split()[2] for line in lines if line.startswith("#print axioms ")]
    require(len(names) == len(set(names)) == 42, "unexpected source inventory")
    healthy = "".join(report(name, ("propext", "Classical.choice", "Quot.sound"))
                      for name in names)
    cases = []

    def case(label, source, output, old_accept, new_accept, old_count=None):
        cases.append((label, source, output, old_accept, new_accept, old_count))

    case("complete_allowed_inventory", queries, healthy, True, True, 42)
    case("complete_axiom_free_inventory", queries,
         "".join(report(name) for name in names), True, True, 42)
    case("reordered_queries_and_reports", "import HyperplaneEnd\n" + "".join(
        f"#print axioms {name}\n" for name in reversed(names)),
        "".join(report(name) for name in reversed(names)), True, True, 42)
    case("wrapped_allowed_axiom_lists", queries,
         healthy.replace("propext, Classical.choice, Quot.sound",
                         "propext,\n Classical.choice,\n Quot.sound"), True, True, 42)
    case("empty_inventory", "import HyperplaneEnd\n", "", True, False, 0)
    for name in names:
        reduced_queries = "".join(line for line in lines if line != f"#print axioms {name}\n")
        reduced_reports = "".join(report(other) for other in names if other != name)
        case("omit_query:" + name, reduced_queries, reduced_reports, True, False, 41)
        # Existing rejection is retained when only compiler output disappears.
        case("omit_report:" + name, queries, reduced_reports, False, False)
    indented = "".join("  " + line if line.startswith("#print axioms") else line
                       for line in lines)
    case("indented_complete_inventory", indented, healthy, True, True, 0)
    forbidden = "".join(report(name, ("sorryAx",)) if name == names[0] else report(name)
                        for name in names)
    case("indented_forbidden_dependency", indented, forbidden, True, False, 0)
    case("ordinary_forbidden_dependency", queries, forbidden, False, False)
    first = names[0]
    case("substitute_unrelated_theorem", queries.replace(first, "Nat.add_comm"),
         healthy.replace(first, "Nat.add_comm"), True, False, 42)
    case("duplicate_query", queries + f"#print axioms {first}\n",
         healthy + report(first), True, False, 43)
    case("comment_out_one_query", queries.replace(f"#print axioms {first}",
         f"-- #print axioms {first}"), "".join(report(n) for n in names[1:]), True, False, 41)
    case("unexpected_report", queries, healthy + report("Nat.add_comm"), True, False, 42)
    case("duplicate_report", queries, healthy + report(first), True, False, 42)
    case("conflicting_duplicate_report", queries, forbidden + report(first), True, False, 42)
    case("conflicting_duplicate_report_reversed", queries, report(first) + forbidden,
         True, False, 42)
    case("malformed_report", queries, healthy.replace(f"'{first}'", "malformed", 1),
         False, False)

    with tempfile.TemporaryDirectory(prefix="hpe-inventory-audit-") as temporary:
        directory = Path(temporary)
        for name, data in inputs.items():
            target = directory / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        patch = HERE / "repair.patch"
        for args in (["--check"], []):
            subprocess.run(["git", "apply", *args, str(patch)], cwd=directory,
                           check=True, capture_output=True, timeout=30)
        repaired = (directory / TARGET).read_text()
        rows = []
        for label, source, output, old_accept, new_accept, old_count in cases:
            old = run_driver(original, directory, source, output)
            new = run_driver(repaired, directory, source, output)
            require(old["accepted"] == old_accept, "original behavior differs: " + label)
            require(new["accepted"] == new_accept, "repair behavior differs: " + label)
            if old_count is not None:
                require(old["reported_results"] == old_count, "original count differs: " + label)
            if new_accept:
                require(new["reported_results"] == 42, "repair failed full coverage: " + label)
            # Query inventory changes must stop before either expensive subprocess.
            if label.startswith("omit_query:") or label in {
                "empty_inventory", "substitute_unrelated_theorem", "duplicate_query",
                "comment_out_one_query",
            }:
                require(new["subprocess_calls"] == 0, "late inventory rejection: " + label)
            rows.append({"case": label, "original": old, "repaired": new})

        # A real, retained Lean 4.21 transcript checks the grammar separately.
        fixture = (HERE / "fixtures/ProbeSyntax.lean").read_bytes()
        transcript = (HERE / "fixtures/lean421.txt").read_text()
        fixture_meta = json.loads((HERE / "fixtures/LEAN.json").read_text())
        require(sha(fixture) == fixture_meta["source_sha256"], "Lean fixture source drift")
        require(sha(transcript.encode()) == fixture_meta["stdout_sha256"], "Lean transcript drift")
        require(fixture_meta["version"].startswith("Lean (version 4.21.0,"), "wrong fixture Lean version")
        parsed = re.findall(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[[^\]]*\])",
                            transcript)
        require([name for name, _ in parsed] == ["HPEInventoryFixture.clean",
                "HPEInventoryFixture.ext", "HPEInventoryFixture.bad"], "real probe names differ")
        ns = {"__name__": "repaired_probe_parser", "__file__": str(directory / TARGET)}
        exec(compile(repaired, str(directory / TARGET), "exec"), ns)
        for index, allowed in ((0, True), (1, True), (2, False)):
            name, suffix = parsed[index]
            rejected = False
            with contextlib.redirect_stdout(io.StringIO()):
                try:
                    ns["check_axiom_reports"](f"'{name}' {suffix}\n", [name])
                except SystemExit:
                    rejected = True
            require(rejected != allowed, "real transcript classification differs: " + name)

    return {
        "status": "PASS_HPE_AXIOM_INVENTORY_AUDIT",
        "scope": "Python control-flow audit using substituted subprocess results; real Lean 4.21 syntax fixture only, not an HPE build or theorem audit.",
        "source_driver_sha256": sha(inputs[TARGET]),
        "source_queries_sha256": sha(inputs[PROBES]),
        "repair_patch_sha256": sha((HERE / "repair.patch").read_bytes()),
        "repaired_driver_sha256": sha(repaired.encode()),
        "required_probes": names,
        "driver_cases": len(rows),
        "omitted_queries_rejected_before_build": len(names),
        "existing_missing_report_rejections_preserved": len(names),
        "real_lean_syntax_cases": 3,
        "cases": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path, help="write a new receipt; refuse to overwrite")
    args = parser.parse_args()
    result = audit()
    rendered = json.dumps(result, indent=2) + "\n"
    if args.write_receipt:
        with args.write_receipt.open("x", encoding="utf-8") as stream:
            stream.write(rendered)
    else:
        require(json.loads((HERE / "RESULT.json").read_text()) == result, "committed receipt differs")
    print(f"{result['status']} probes=42 driver_cases={result['driver_cases']} real_lean_syntax_cases=3 no_HPE_build")


if __name__ == "__main__":
    main()
