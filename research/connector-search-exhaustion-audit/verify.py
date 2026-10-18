#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compare authenticated native search with a literal Cartesian word oracle."""

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/connector-covering-code/cycle_search.cpp"
MUTANTS = (
    (
        "first_branch_only",
        "if (success || timed_out) return;",
        "if (success || timed_out || id != domains[chosen].first()) return;",
    ),
    (
        "shared_child_domains",
        "Domains child = domains; child[chosen] = Bits{}; child[chosen].add(id);",
        "Domains& child = domains; child[chosen] = Bits{}; child[chosen].add(id);",
    ),
    (
        "ignore_child_timeout",
        "if (success || timed_out) return;",
        "if (success) return;",
    ),
    (
        "timeout_is_exhaustion",
        "return !timed_out && !found;",
        "return !found;",
    ),
)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticated_source(root=ROOT, inventory=None):
    inventory = HERE / "SOURCES.json" if inventory is None else inventory
    need(inventory.stat().st_size <= 16_384, "bounded source manifest")
    rows = json.loads(inventory.read_bytes())["files"]
    need(isinstance(rows, list) and len(rows) == 4, "four source bindings")
    need(len({row["path"] for row in rows}) == 4, "distinct source paths")
    inputs = [row for row in rows if row["usage"] == "input"]
    need(
        {row["path"] for row in inputs}
        == {SOURCE, "research/connector-covering-code/README.md"},
        "exact scientific input closure",
    )
    payloads = {}
    for row in inputs:
        path = root / row["path"]
        need(
            path.is_file()
            and not path.is_symlink()
            and path.resolve().is_relative_to(root.resolve())
            and path.stat().st_size <= 131_072,
            "bounded regular source",
        )
        payload = path.read_bytes()
        need(hashlib.sha256(payload).hexdigest() == row["sha256"], "source SHA256")
        blob = hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()
        need(blob == row["git_blob"], "source Git blob")
        payloads[row["path"]] = payload
    return payloads[SOURCE].decode("utf-8")


def command(argv, timeout):
    result = subprocess.run(
        argv, capture_output=True, text=True, timeout=timeout, check=False
    )
    need(len(result.stdout) + len(result.stderr) <= 65_536, "bounded diagnostics")
    return result


def compiled_run(directory, source, compiler, sanitize):
    written = (directory / "subject.cpp").write_text(source)
    need(written == len(source), "complete authenticated source write")
    binary = directory / "audit"
    flags = ["-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Werror"]
    flags += (
        ["-O1", "-g", "-fsanitize=address,undefined", "-fno-omit-frame-pointer"]
        if sanitize
        else ["-O2"]
    )
    build = command(
        [
            compiler,
            *flags,
            "-I",
            str(directory),
            str(HERE / "audit.cpp"),
            "-o",
            str(binary),
        ],
        60,
    )
    need(build.returncode == 0, "native compilation failed: " + build.stderr)
    return command([str(binary)], 90)


def replay(compiler, sanitize, mutants):
    source = authenticated_source()
    with tempfile.TemporaryDirectory(prefix="connector-search-") as temporary:
        directory = Path(temporary)
        actual = compiled_run(directory, source, compiler, sanitize)
        need(actual.returncode == 0, "native search audit failed: " + actual.stderr)
        need(not actual.stderr, "unexpected native diagnostics: " + actual.stderr)
        result = json.loads(actual.stdout)
        need(
            isinstance(result, dict)
            and len(result) == 14
            and all(type(value) is int and value >= 0 for value in result.values()),
            "bounded counter schema",
        )
        rejected = []
        if mutants:
            for name, before, after in MUTANTS:
                need(source.count(before) == 1, "unique mutation anchor: " + name)
                mutant = compiled_run(
                    directory, source.replace(before, after), compiler, False
                )
                need(mutant.returncode == 1, "semantic mutant survived: " + name)
                need(mutant.stderr.strip(), "mutant failed without diagnostic: " + name)
                rejected.append(name)
        return {"native": result, "semantic_mutants_rejected": rejected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", default="g++")
    parser.add_argument("--sanitize", action="store_true")
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--no-mutants", action="store_true")
    args = parser.parse_args()
    result = replay(args.compiler, args.sanitize, not args.no_mutants)
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    expected = json.loads((HERE / "RESULT.json").read_bytes())
    need(result["native"] == expected["native"], "exact native counter receipt")
    if not args.no_mutants:
        need(result == expected, "exact semantic mutant receipt")
    print("PASS_CONNECTOR_SEARCH_AUDIT roots=914 branching_sat=50 branching_unsat=22")


if __name__ == "__main__":
    main()
