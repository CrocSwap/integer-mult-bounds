#!/usr/bin/env python3
"""Read-only source/census/transport checks; NOT a Lean parser or proof checker.
SPDX-License-Identifier: Apache-2.0. Python 3.12+, standard library only.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any
from generate import ROOT, check_generated, require
from check_numeric import read_emitted_values
from check_axioms import QUERY


def strip_comments(text: str) -> str:
    """Retain line positions while excluding nested Lean comments and strings."""
    out: list[str] = []
    i, depth, in_string = 0, 0, False
    while i < len(text):
        pair, char = text[i:i+2], text[i]
        if depth:
            if pair == "/-":
                depth += 1; out.extend("  "); i += 2; continue
            if pair == "-/":
                depth -= 1; out.extend("  "); i += 2; continue
            out.append("\n" if char == "\n" else " "); i += 1; continue
        if in_string:
            if char == "\\" and i + 1 < len(text):
                out.extend("  "); i += 2; continue
            if char == '"':
                in_string = False
            out.append("\n" if char == "\n" else " "); i += 1; continue
        if pair == "/-":
            depth = 1; out.extend("  "); i += 2; continue
        if pair == "--":
            end = text.find("\n", i)
            if end == -1: end = len(text)
            out.extend(" " * (end-i)); i = end; continue
        if char == '"':
            in_string = True; out.append(" "); i += 1; continue
        out.append(char); i += 1
    require(depth == 0 and not in_string, "Unclosed source comment/string")
    return "".join(out)


def declaration_rows(root: Path) -> list[tuple[str, int, str, str, str]]:
    result: list[tuple[str, int, str, str, str]] = []
    for path in sorted(root.rglob("*.lean")):
        rel = path.relative_to(root).as_posix()
        stack: list[str] = []
        code = strip_comments(path.read_text(encoding="utf-8"))
        for lineno, line in enumerate(code.splitlines(), 1):
            ns = re.fullmatch(r"namespace\s+(\w+(?:\.\w+)*)\s*", line)
            if ns:
                stack.append(ns.group(1)); continue
            if re.fullmatch(r"end(?:\s+[\w.]+)?\s*", line):
                require(bool(stack), f"Unexpected end in {rel}:{lineno}")
                stack.pop(); continue
            decl = re.match(r"^(def|theorem|structure|abbrev)\s+([A-Za-z_][\w]*)\b", line)
            if decl:
                kind, name = decl.groups()
                qualified = ".".join([*stack, name])
                origin = "inherited" if rel == "PR1497Bridge.lean" else "new"
                result.append((rel, lineno, kind, qualified, origin))
        require(not stack, f"Unclosed namespace in {rel}")
    return result


def census_bytes(root: Path) -> bytes:
    rows = declaration_rows(root)
    text = "file\tline\tkind\tdeclaration\torigin\n"
    text += "".join(f"{p}\t{line}\t{kind}\t{name}\t{origin}\n"
                    for p, line, kind, name, origin in rows)
    return text.encode("utf-8")


def audit(root: Path = ROOT, check_census: bool = True) -> dict[str, Any]:
    binding = check_generated(root)
    original = json.loads((root / "P112.json").read_text(encoding="utf-8"))
    recovered = read_emitted_values((root / "P112Data.lean").read_text(encoding="utf-8"))
    require(recovered == original, "Inverse literal parser found a value mismatch")
    declarations = declaration_rows(root)
    all_names = [row[3] for row in declarations]
    require(len(all_names) == len(set(all_names)), "Duplicate named declaration")
    by_file: dict[str, list[str]] = {}
    for rel, _, _, name, _ in declarations:
        by_file.setdefault(rel, []).append(name)
    plan = json.loads((root / "REPLAY_PLAN.json").read_text(encoding="utf-8"))
    require(plan["per_unit_seconds"] == 120 and plan["successor_total_seconds"] == 600,
            "Resource limits changed")
    positive = plan["positive_units"]
    negative = plan["negative_units"]
    actual_files = {p.relative_to(root).as_posix() for p in root.rglob("*.lean")}
    require(actual_files == set(positive + negative), "Replay plan is not the full Lean file set")
    forbidden = re.compile(r"\b(?:axiom|sorry|admit|unsafe|native_decide|macro|elab|syntax|run_tac)\b|#(?:eval|reduce|compile)\b")
    compiled_modules: set[str] = set()
    for rel in positive + negative:
        text = (root / rel).read_text(encoding="utf-8")
        code = strip_comments(text)
        require(not forbidden.search(code), f"Forbidden executable token in {rel}")
        for module in re.findall(r"^import\s+([\w.]+)\s*$", code, re.M):
            require(module == "Std" or module in compiled_modules,
                    f"Unresolved/out-of-order import in {rel}: {module}")
        compiled_modules.add(rel[:-5].replace("/", "."))
        if rel != "PR1497Bridge.lean":
            require(re.findall(r"^set_option maxRecDepth\s+(\d+)\s*$", code, re.M) == ["4096"],
                    f"Unexpected recursion bound in {rel}")
            require(re.findall(r"^set_option maxHeartbeats\s+(\d+)\s*$", code, re.M) == ["1000000"],
                    f"Unexpected heartbeat bound in {rel}")
        queries = QUERY.findall(text)
        require(len(queries) == len(set(queries)), f"Duplicate query in {rel}")
        require(set(queries) == set(by_file.get(rel, [])), f"Incomplete axiom queries in {rel}")
        if rel in positive:
            require(bool(queries), f"No axiom queries in positive unit {rel}")
    if check_census:
        require((root / "DECLARATIONS.tsv").read_bytes() == census_bytes(root), "Stale declaration census")
    return {"status": "SOURCE_AUDIT_ONLY_NOT_KERNEL_EVIDENCE",
            "binding": binding,
            "inherited_named_queries": sum(r[4] == "inherited" for r in declarations),
            "new_named_queries": sum(r[4] == "new" for r in declarations),
            "new_theorems": sum(r[4] == "new" and r[2] == "theorem" for r in declarations),
            "positive_units_including_dependency": len(positive),
            "negative_units": len(negative),
            "new_lean_executed": False}


def verify_manifest(root: Path) -> None:
    lines = (root / "MANIFEST.tsv").read_text(encoding="utf-8").splitlines()
    require(lines[0] == "path\tutf8_bytes\tsha256", "Bad manifest header")
    seen: set[str] = set()
    for line in lines[1:]:
        name, count, digest = line.split("\t")
        require(name not in seen, f"Duplicate manifest entry {name}")
        require(not Path(name).is_absolute() and ".." not in Path(name).parts, "Unsafe manifest path")
        seen.add(name)
        raw = (root / name).read_bytes()
        raw.decode("utf-8")
        require(len(raw) == int(count), f"Byte count mismatch: {name}")
        require(hashlib.sha256(raw).hexdigest() == digest, f"SHA256 mismatch: {name}")
    expected = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()
                and "__pycache__" not in p.parts
                and p.name not in {"MANIFEST.tsv", "SHA256SUMS"}}
    require(seen == expected, "Manifest payload set mismatch")
    sums = (root / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
    checksum_names: set[str] = set()
    for line in sums:
        digest, name = line.split("  ", 1)
        require(name not in checksum_names, "Duplicate SHA256SUMS entry")
        checksum_names.add(name)
        require(name in seen | {"MANIFEST.tsv"}, "Unexpected SHA256SUMS path")
        require(hashlib.sha256((root / name).read_bytes()).hexdigest() == digest,
                f"SHA256SUMS mismatch: {name}")
    require(checksum_names == seen | {"MANIFEST.tsv"}, "SHA256SUMS inventory mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--manifest", action="store_true")
    args = parser.parse_args()
    report = audit(args.root.resolve())
    if args.manifest:
        verify_manifest(args.root.resolve())
        report["manifest_verified"] = True
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
