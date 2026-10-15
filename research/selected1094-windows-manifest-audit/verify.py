#!/usr/bin/env python3
"""Audit two frozen PR1094 manifest guards; never modify the supplier.

Prepared for josecarlosgonzalezroque-design with substantial OpenAI Codex
assistance. Apache-2.0. The evaluated guards belong to Rohan Arun's PR1094;
the archived source is Jeremy Kothe's PR1087 with its retained notices.
"""
import argparse
import ast
import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = "research/complex-t16-rare-pattern-exchanges"
SELECTED = "research/community-frontier1094-audit/SELECTED-SOURCE.json"
SUBMISSION = "Submission file inventory or hash changed"
ARCHIVE = "Upstream archive mismatch"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical_name(name):
    path = PurePosixPath(name)
    require(name and not path.is_absolute() and ".." not in path.parts
            and "\\" not in name and ":" not in name
            and path.as_posix() == name, "noncanonical input name: " + name)


def authenticate(root):
    sources = json.loads((HERE / "SOURCES.json").read_bytes())
    rows = [row for row in sources["files"] if row["usage"] == "input"]
    require({row["path"] for row in rows} == {
        SELECTED, *[PACKAGE + "/" + name for name in (
            "CANDIDATE.json", "MANIFEST.json", "MOVES.json", "OWNERS.json.gz",
            "PRICE.json", "PROFILE.json", "README.md", "SOURCE.json",
            "upstream1087.tar.gz", "VALIDATION.json", "verify.py",
            "data/OWNERS.json.gz", "data/PLAN.json", "data/SPEC.json")]},
        "audit input inventory changed")
    for row in rows:
        canonical_name(row["path"])
        require(sha((root / row["path"]).read_bytes()) == row["sha256"],
                "immutable input changed: " + row["path"])
    selected = json.loads((root / SELECTED).read_bytes())["files"]
    for row in rows:
        if row["path"].startswith(PACKAGE + "/"):
            require(selected[row["path"]] == row["sha256"],
                    "input is not the selected source: " + row["path"])
    return rows


def guards(source):
    """Extract the actual two assertions and the first guard's assignments."""
    body = ast.parse(source).body

    def assignment(name):
        matches = [n for n in body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)]
        require(len(matches) == 1, "source assignment changed: " + name)
        return matches[0]

    def assertion(message):
        matches = [n for n in body if isinstance(n, ast.Assert)
                   and isinstance(n.msg, ast.Constant) and n.msg.value == message]
        require(len(matches) == 1, "source guard changed: " + message)
        return matches[0]

    return {
        "submission": (SUBMISSION, [assignment("sha"), assignment("manifest"),
                                    assignment("actual"), assertion(SUBMISSION)]),
        "upstream": (ARCHIVE, [assignment("sha"), assertion(ARCHIVE)]),
    }


class PosixKeys(ast.NodeTransformer):
    """Change only str(f.relative_to(...)) into (...).as_posix() in memory."""
    def __init__(self):
        self.changed = 0

    def visit_Call(self, node):
        if (isinstance(node.func, ast.Name) and node.func.id == "str"
                and len(node.args) == 1 and not node.keywords
                and isinstance(node.args[0], ast.Call)
                and isinstance(node.args[0].func, ast.Attribute)
                and node.args[0].func.attr == "relative_to"):
            self.changed += 1
            return ast.copy_location(ast.Call(
                func=ast.Attribute(value=node.args[0], attr="as_posix", ctx=ast.Load()),
                args=[], keywords=[]), node)
        return self.generic_visit(node)


def guard_code(nodes, corrected=False):
    tree = ast.Module(body=copy.deepcopy(nodes), type_ignores=[])
    if corrected:
        transformer = PosixKeys()
        tree = transformer.visit(tree)
        require(transformer.changed == 1, "expected exactly one path-key change")
    # The frozen assertions must execute even when this audit uses -O.
    return compile(ast.fix_missing_locations(tree), "<pinned PR1094 inventory guard>",
                   "exec", optimize=0)


def accepts(code, directory, spelling, message):
    namespace = {"P": directory, "source": directory, "json": json,
                 "hashlib": hashlib,
                 "pins": json.loads((directory / "MANIFEST.json").read_bytes())}
    # Only relative-path serialization is modeled; enumeration and file bytes
    # remain actual filesystem operations. This is not full OS emulation.
    if spelling == "windows":
        namespace["str"] = lambda p: str(PureWindowsPath(p.as_posix()))
    elif spelling == "posix":
        namespace["str"] = lambda p: PurePosixPath(p.as_posix()).as_posix()
    try:
        exec(code, namespace)
    except AssertionError as exc:
        require(str(exc) == message, "unexpected guard assertion")
        return False
    return True


def archive_files(path):
    files = {}
    with tarfile.open(path) as archive:
        for member in archive:
            canonical_name(member.name)
            require(member.isfile() and member.name not in files,
                    "nonregular or duplicate archive member")
            files[member.name] = archive.extractfile(member).read()
    return files


def exercise(name, nodes, message, files, directory):
    for relative, data in files.items():
        canonical_name(relative)
        path = directory / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    expected = json.loads(files["MANIFEST.json"])
    for relative in expected:
        canonical_name(relative)
    actual = {relative: sha(data) for relative, data in files.items()
              if relative != "MANIFEST.json"}
    require(actual == expected, name + ": actual bytes differ from immutable manifest")
    nested = sorted(relative for relative in expected if "/" in relative)
    require(nested, "fixture must exercise nested paths")
    windows_names = {str(PureWindowsPath(relative)) for relative in expected}
    require(len(windows_names) == len(expected), "Windows path alias in fixture")

    original, corrected = guard_code(nodes), guard_code(nodes, corrected=True)
    require(accepts(original, directory, "posix", message), "POSIX original rejected")
    require(not accepts(original, directory, "windows", message), "Windows original accepted")
    require(accepts(original, directory, "native", message) == (os.name != "nt"),
            "native result disagrees with the path model")
    for spelling in ("posix", "windows", "native"):
        require(accepts(corrected, directory, spelling, message), "corrected guard rejected")

    # Each payload is actually changed and omitted on disk, with the original
    # manifest untouched. All hashes, names, and inventory equality stay active.
    for relative in sorted(expected):
        path, old = directory / relative, files[relative]
        path.write_bytes(old + b"\x00")
        require(not accepts(corrected, directory, "native", message),
                "changed bytes accepted: " + relative)
        path.unlink()
        require(not accepts(corrected, directory, "native", message),
                "omitted file accepted: " + relative)
        path.write_bytes(old)
    extra = directory / "unexpected-audit-file"
    extra.write_bytes(b"extra")
    require(not accepts(corrected, directory, "native", message), "extra file accepted")
    extra.unlink()
    old_name = nested[0]
    renamed = directory / "renamed-audit-file"
    (directory / old_name).unlink()
    renamed.write_bytes(files[old_name])
    require(not accepts(corrected, directory, "native", message), "renamed file accepted")
    renamed.unlink()
    (directory / old_name).write_bytes(files[old_name])
    require(accepts(corrected, directory, "native", message), "restored positive rejected")
    return {"files": len(expected), "nested_keys": nested,
            "digest_mismatches": 0, "original_posix_accepts": True,
            "original_windows_accepts": False, "corrected_accepts": True,
            "changed_file_rejections": len(expected),
            "omitted_file_rejections": len(expected), "extra_file_rejections": 1,
            "rename_rejections": 1}


def audit(root, work):
    rows = authenticate(root)
    package = root / PACKAGE
    parsed = guards((package / "verify.py").read_bytes())
    outer = {p.relative_to(package).as_posix(): p.read_bytes()
             for p in package.rglob("*") if p.is_file()}
    inner = archive_files(package / "upstream1087.tar.gz")
    source = json.loads(outer["SOURCE.json"])
    require(sha(inner["MANIFEST.json"]) == source["manifest_sha256"],
            "archived manifest differs from PR1087 source pin")
    require(json.loads(inner["MANIFEST.json"]) == source["files"],
            "archived manifest differs from PR1087 source inventory")
    results = {}
    for name, files in (("submission", outer), ("upstream", inner)):
        message, nodes = parsed[name]
        results[name] = exercise(name, nodes, message, files, work / name)

    # Check immutable-source pins before code evaluation; a changed manifest
    # or container header must not become a portability waiver.
    export = work / "pin-controls"
    for row in rows:
        dest = export / row["path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / row["path"], dest)
    for relative in ("verify.py", "MANIFEST.json", "upstream1087.tar.gz"):
        path = export / PACKAGE / relative
        old = path.read_bytes()
        path.write_bytes(old + b"\x00")
        try:
            authenticate(export)
        except ValueError as exc:
            require(str(exc) == "immutable input changed: " + PACKAGE + "/" + relative,
                    "unexpected immutable-source failure")
        else:
            raise ValueError("corrupt immutable source accepted")
        path.write_bytes(old)
    authenticate(export)

    native = "not run (non-Windows host); guard models checked"
    if os.name == "nt":
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        env.pop("PYTHONOPTIMIZE", None)
        output = work / "must-not-be-created"
        run = subprocess.run([sys.executable, "-B", str(package / "verify.py"),
                              "--main", str(root), "--local", str(work / "unused-local"),
                              "--work", str(output)], capture_output=True, env=env, timeout=30)
        require(run.returncode != 0 and ("AssertionError: " + SUBMISSION).encode() in run.stderr,
                "native unmodified entry point did not reproduce the first-guard failure")
        require(not output.exists(), "failed submission guard reached output creation")
        native = "unmodified entry point rejects at submission guard before output creation"
    authenticate(root)
    result = {"status": "PASS_SELECTED1094_WINDOWS_MANIFEST_AUDIT", "guards": results,
              "immutable_source_rejections": 3,
              "total_corruption_rejections": sum(2*r["files"] + 2 for r in results.values()) + 3,
              "scope": "Two inventory guards only; no supplier replay or new kappa"}
    return result, native


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write", action="store_true", help="write deterministic audit receipt")
    parser.add_argument("--report", type=Path, help="write environment-specific execution report")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="pr1094-manifest-") as temporary:
        work = Path(temporary).resolve()
        require(work.is_relative_to(Path(tempfile.gettempdir()).resolve()), "unexpected temporary root")
        result, native = audit(args.root.resolve(), work)
    receipt = HERE / "RESULT.json"
    if args.write:
        receipt.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    else:
        require(result == json.loads(receipt.read_bytes()), "audit receipt differs")
    if args.report:
        args.report.write_text(json.dumps({"python": sys.version, "platform": platform.platform(),
            "native_entry_point": native, "result": result}, indent=2) + "\n",
            encoding="utf-8", newline="\n")
    print(result["status"], "guards=2 files=192 controls=" + str(result["total_corruption_rejections"]),
          "no_new_kappa")
    print("Native observation:", native)


if __name__ == "__main__":
    main()
