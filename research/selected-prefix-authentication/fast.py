#!/usr/bin/env python3
"""Opt-in path-prefix reuse for the frozen PR6030 baseline.

Produced by Nick Petalas. Apache-2.0.
Baseline/report: Mihir Srivastava / PR4463. Source checker: Douglas Colkitt
and retained contributors. Source files and scientific checks are unchanged.
"""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
from runpy import run_path


PACKAGE = Path(__file__).resolve().parent
MAX_INPUTS = 4096
MAX_DEPTH = 128


def require(condition, message):
    if not condition:
        raise ValueError(message)


class PrefixValidator:
    """Reuse directory facts only while one stable-tree check is running."""

    def __init__(self, root, fallback):
        self.root = root.resolve()
        self.fallback = fallback
        self.directories = {(): self.root}
        self.calls = 0
        self.directory_checks = 0
        self.file_checks = 0

    def __call__(self, root, relative):
        require(root == self.root, "Validator root changed")
        self.calls += 1
        require(self.calls <= MAX_INPUTS, "Explicit inventory exceeds capacity")
        if os.name == "nt":
            return self.fallback(root, relative)
        require(isinstance(relative, str), "Invalid explicit input name")
        name = PurePosixPath(relative)
        parts = name.parts
        require(bool(parts) and not name.is_absolute() and ".." not in parts
                and "\\" not in relative and name.as_posix() == relative,
                "Noncanonical explicit input: " + relative)
        require(len(parts) <= MAX_DEPTH, "Explicit input exceeds depth capacity")
        current = self.root
        for depth, part in enumerate(parts[:-1], 1):
            key = parts[:depth]
            if key not in self.directories:
                candidate = current / part
                self.directory_checks += 1
                require(not candidate.is_symlink() and candidate.is_dir(),
                        "Invalid explicit directory: " + relative)
                self.directories[key] = candidate
            current = self.directories[key]
        result = current / parts[-1]
        self.file_checks += 1
        require(not result.is_symlink() and result.is_file(),
                "Invalid explicit file: " + relative)
        return result


def load_baseline(root):
    """Execute the two pinned source files, with no imported bytecode cache."""
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    require(len(sources["files"]) <= MAX_INPUTS + 8, "Source inventory exceeds capacity")
    for item in sources["files"]:
        if item["usage"] == "input" and item["path"].startswith("scripts/"):
            raw = (root / item["path"]).read_bytes()
            require(sha256(raw).hexdigest() == item["sha256"],
                    "Baseline source changed: " + item["path"])
    return run_path(str(root / "scripts/research_selected_baseline.py"),
                    run_name="selected_baseline_source")


def report(root, reference=False):
    """Run the unchanged checker and summarizer on the captured selection."""
    baseline = load_baseline(root)
    raw = (PACKAGE / "selection.json").read_bytes()
    record = json.loads(raw)
    manifest = json.loads((root / record["source_manifest"]).read_bytes())
    require(manifest.get("format") == "repository-files-sha256-v1",
            "Adapter requires an explicit file inventory")
    require(len(manifest["files"]) <= MAX_INPUTS, "Explicit inventory exceeds capacity")
    checker = baseline["check"]
    globals_ = checker.__globals__
    validator = PrefixValidator(root, globals_["explicit_file"])
    if not reference:
        globals_["explicit_file"] = validator
    checker(record, root)
    certificate = json.loads((root / record["certificate"]).read_bytes())
    result = baseline["summarize"](record, certificate)
    result["selected_record_sha256"] = sha256(raw).hexdigest()
    return result, validator


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PACKAGE.parents[1])
    parser.add_argument("--reference", action="store_true")
    args = parser.parse_args()
    result, _ = report(args.root.resolve(), args.reference)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
