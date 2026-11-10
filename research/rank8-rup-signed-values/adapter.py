#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Opt-in, byte-bound literal-table adapter for PR1212's complete CLI."""
from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/complex-rank8-decoder-rigidity/verify.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def authenticated_source(root: Path = ROOT) -> tuple[Path, str]:
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    source_path = root / SOURCE
    for entry in manifest["files"]:
        if entry["usage"] == "input":
            path = root / entry["path"]
            require(path.is_file() and not path.is_symlink(), f"missing input: {path}")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            require(digest == entry["sha256"], f"input hash mismatch: {entry['path']}")
    return source_path, source_path.read_text()


def signed_source(source: str) -> str:
    """Change only the bounded, authenticated RUP function."""
    functions = [node for node in ast.parse(source).body
                 if isinstance(node, ast.FunctionDef) and node.name == "rup_check"]
    require(len(functions) == 1, "expected exactly one RUP function")
    function = functions[0]
    lines = source.splitlines(keepends=True)
    original = "".join(lines[function.lineno - 1:function.end_lineno])
    changed = original
    replacements = (
        ("assign = [0] * (nvars + 1)", "assign = [0] * (2 * nvars + 1)", 1),
        ("    def value(lit):\n        return assign[abs(lit)] * (1 if lit > 0 else -1)\n\n", "", 1),
        ("v = value(lit)", "v = assign[lit]", 1),
        ("v = value(l)", "v = assign[l]", 1),
        ("assign[abs(l)] = 0", "assign[l] = assign[-l] = 0", 3),
        ("assign[abs(lit)] = 1 if lit > 0 else -1", "assign[lit], assign[-lit] = 1, -1", 1),
        ("assign[abs(unassigned)] = 1 if unassigned > 0 else -1", "assign[unassigned], assign[-unassigned] = 1, -1", 1),
    )
    for before, after, count in replacements:
        require(changed.count(before) == count, f"adapter replacement mismatch: {before}")
        changed = changed.replace(before, after)
    require("value(" not in changed and "assign[abs(" not in changed,
            "unconverted literal access")
    return "".join(lines[:function.lineno - 1]) + changed + "".join(lines[function.end_lineno:])


def load_source(optimized: bool = True, root: Path = ROOT) -> dict:
    path, source = authenticated_source(root)
    if optimized:
        source = signed_source(source)
    namespace = {"__name__": "rank8_replay_source", "__file__": str(path)}
    exec(compile(source, str(path), "exec"), namespace)
    return namespace


def main() -> int:
    try:
        namespace = load_source()
        return namespace["main"]()
    except (OSError, ValueError, SyntaxError) as error:
        print(f"FAIL_RANK8_SIGNED_VALUES: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
