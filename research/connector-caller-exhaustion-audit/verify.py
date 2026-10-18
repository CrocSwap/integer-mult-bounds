#!/usr/bin/env python3
"""Source-bound gap enumeration audit, not a full word census. Apache-2.0."""

import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SUBJECT = "research/connector-covering-code/cycle_search.cpp"
CALLER = "research/connector-covering-code/verify_cycles.py"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticated_sources(root=ROOT):
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    contents = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        raw = (root / row["path"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash mismatch")
        need(
            hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            == row["git_blob"],
            "source Git blob mismatch",
        )
        contents[row["path"]] = raw.decode()
    return contents


def replace_once(source, old, new):
    need(source.count(old) == 1, f"adapter site changed: {old}")
    return source.replace(old, new)


def adapted_source(source):
    # These are the only production statements substituted. Gap traversal,
    # deadlines, counters and early-exit/result logic execute unchanged.
    source = replace_once(
        source,
        "++stats.compositions;",
        "++stats.compositions; audit_gap(gaps, blocks);",
    )
    source = replace_once(
        source, "if (!capacity(gaps)) return;", "if (!audit_capacity(gaps)) return;"
    )
    return replace_once(
        source, "search(domains_for(gaps), true);", "audit_search(*this);"
    )


def compile_run(source, directory, compiler):
    path = Path(directory)
    (path / "subject.cpp").write_text(adapted_source(source))
    shutil.copyfile(PACKAGE / "enumerate_harness.cpp", path / "harness.cpp")
    binary = path / "audit"
    command = [
        *compiler,
        "-std=c++17",
        "-O2",
        "-Wall",
        "-Wextra",
        "-Wpedantic",
        "-Werror",
        str(path / "harness.cpp"),
        "-o",
        str(binary),
    ]
    subprocess.run(command, check=True, timeout=60, capture_output=True, text=True)
    return subprocess.run(
        [str(binary)], check=False, timeout=120, capture_output=True, text=True
    )


def native_audit(source, compiler, controls):
    with tempfile.TemporaryDirectory(prefix="connector-caller-audit-") as directory:
        actual = compile_run(source, directory, compiler)
        need(actual.returncode == 0, actual.stderr)
        receipt = json.loads(actual.stdout)
        need(receipt["rank_checked_gaps"] == 45189640, "native coverage changed")
        mutations = [
            (
                "missing maximum gap",
                "length <= std::min(7, remaining)",
                "length < std::min(7, remaining)",
                "gap count does not equal independent coefficient count",
            ),
            (
                "duplicate leaf",
                "++stats.compositions;",
                "++stats.compositions; stats.compositions += 1;",
                "gap count does not equal independent coefficient count",
            ),
            (
                "incomplete reported exhausted",
                "return !timed_out && !found;",
                "return true;",
                "found/timeout did not stop the entire traversal",
            ),
            (
                "wrong-sum leaf",
                "if (remaining) return;",
                "if (remaining == 1) return;",
                "gap rank is not next lexicographic rank",
            ),
        ]
        if controls:
            for name, old, new, failure in mutations:
                mutant = replace_once(source, old, new)
                result = compile_run(mutant, directory, compiler)
                need(
                    result.returncode == 1 and f"FAIL {failure}" in result.stderr,
                    f"semantic mutant did not fail the intended predicate: {name}: {result.stderr}",
                )
        return receipt, len(mutations) if controls else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controls", action="store_true")
    args = parser.parse_args()
    sources = authenticated_sources()
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    need(compiler and shutil.which(compiler[0]), "installed C++17 compiler required")
    receipt, count = native_audit(sources[SUBJECT], compiler, args.controls)
    receipt["semantic_native_mutants_rejected"] = count
    expected = json.loads((PACKAGE / "RESULT.json").read_text())["enumeration"]
    if not args.controls:
        expected["semantic_native_mutants_rejected"] = 0
    need(receipt == expected, "complete enumeration receipt changed")
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_CONNECTOR_ENUMERATION_AUDIT")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        raise SystemExit(f"FAIL {error}") from error
