#!/usr/bin/env python3
"""Build the scoped Lean prefix-norm proofs and audit their exact source/axiom boundary.

Gareth Davidson, with substantial OpenAI Codex assistance. Apache-2.0.
Requires Lean/Lake 4.21.0. --source-only needs only Python and proves no theorem.
The default build fetches the pinned Mathlib cache; --no-cache is for prepared
dependencies. --work uses a dedicated marked workspace, never frozen sources.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = "research/e8-lemma-g-lean/LemmaG/Stream.lean"
INPUTS = {SOURCE, "research/e8-lemma-g-lean/PROOF.md",
          "research/e8-lemma-g-lean/lake-manifest.json",
          "research/e8-lemma-g-lean/lean-toolchain", "research/hyperplane-end-lean/PROOF.md"}
LEAN_FILES = {"PrefixNorm.lean", "PrefixNorm/Examples.lean", "PrintAxioms.lean"}
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}
FORBIDDEN = re.compile(r"\b(sorry|admit|axiom|native_decide|implemented_by|extern|unsafe|opaque|set_option)\b")
MARKER = ".unitary-prefix-norm-workspace.json"
OWNER = {"package": "lean-unitary-prefix-norm", "version": 1}
CACHE_MODULES = ["Mathlib.Algebra.Module.Equiv.Defs", "Mathlib.Algebra.Module.Pi",
                 "Mathlib.Algebra.BigOperators.Pi", "Mathlib.Algebra.Module.LinearMap.Basic",
                 "Mathlib.LinearAlgebra.Span.Basic", "Mathlib.Analysis.InnerProductSpace.PiL2",
                 "Mathlib.Tactic.Linarith", "Mathlib.Tactic.NormNum", "Mathlib.Tactic.FinCases"]


class VerificationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def strip_comments(source):
    """Handle nested Lean block comments and line comments without swallowing code."""
    out, i, depth = [], 0, 0
    while i < len(source):
        if source.startswith("/-", i):
            depth += 1
            i += 2
        elif depth and source.startswith("-/", i):
            depth -= 1
            i += 2
            out.append(" ")
        elif depth:
            i += 1
        elif source.startswith("--", i):
            end = source.find("\n", i)
            i = len(source) if end < 0 else end
        else:
            out.append(source[i])
            i += 1
    require(depth == 0, "unclosed Lean comment")
    return "".join(out)


def scan(source, name):
    match = FORBIDDEN.search(strip_comments(source))
    require(match is None, "forbidden Lean token in " + name + (": " + match[0] if match else ""))


def source_check(root=ROOT, package=HERE):
    pins = json.loads((package / "SOURCES.json").read_text())
    live = [x for x in pins["files"] if x["usage"] == "input"]
    require(len(live) == len(INPUTS) and {x["path"] for x in live} == INPUTS, "mandatory input inventory")
    for row in live:
        require(sha((root / row["path"]).read_bytes()) == row["sha256"], "source hash: " + row["path"])
    actual = {str(p.relative_to(package)) for p in package.rglob("*.lean") if ".lake" not in p.parts}
    require(actual == LEAN_FILES, "Lean source inventory")
    for name in sorted(LEAN_FILES):
        scan((package / name).read_text(), name)
    scan((root / SOURCE).read_text(), SOURCE)
    index = json.loads((package / "THEOREMS.json").read_text())
    names = index["core"] + index["examples"]
    require(len(names) == len(set(names)) == 33, "theorem inventory")
    for group, file, prefix in [("core", "PrefixNorm.lean", "PrefixNorm."),
                                 ("examples", "PrefixNorm/Examples.lean", "PrefixNorm.Examples.")]:
        parsed = [prefix + n for n in re.findall(r"^theorem (\w+)",
                  strip_comments((package / file).read_text()), re.M)]
        require(parsed == index[group], "declared theorem coverage: " + group)
    printed = re.findall(r"^#print axioms (\S+)$", (package / "PrintAxioms.lean").read_text(), re.M)
    require(printed == names, "complete axiom audit requests")
    original = json.loads((root / "research/e8-lemma-g-lean/lake-manifest.json").read_text())
    staged = json.loads((package / "lake-manifest.json").read_text())
    original["name"] = "UnitaryPrefixNorm"
    require(original == staged, "unchanged dependency resolution")
    require((package / "lean-toolchain").read_bytes()
            == (root / "research/e8-lemma-g-lean/lean-toolchain").read_bytes(), "toolchain pin")
    require((package / "lean-toolchain").read_text().strip() == "leanprover/lean4:v4.21.0", "Lean version pin")
    return dict(status="PASS_PREFIX_NORM_SOURCE_BINDINGS_ONLY", core_theorems=len(index["core"]),
                example_theorems=len(index["examples"]), source_sha256={x["path"]: x["sha256"] for x in live},
                lean_source_sha256={n: sha((package / n).read_bytes()) for n in sorted(LEAN_FILES)})


def parse_axioms(output, names):
    found = {}
    for name, body in re.findall(r"'([\w.']+)' depends on axioms: \[([^\]]*)\]", output):
        require(name not in found, "duplicate axiom report")
        found[name] = sorted(a.strip() for a in body.split(",") if a.strip())
    for name in re.findall(r"'([\w.']+)' does not depend on any axioms", output):
        require(name not in found, "duplicate axiom report")
        found[name] = []
    require(set(found) == set(names), "incomplete/unexpected axiom reports")
    for name, axioms in found.items():
        require(set(axioms) <= ALLOWED, "unapproved theorem axiom: " + name)
    return found


def parse_lean_version(output):
    # A fresh Lake workspace emits dependency-download messages before the
    # version line. Require exactly one exact-version report, not quiet setup.
    versions = [line.strip() for line in output.splitlines() if line.startswith("Lean (version ")]
    require(len(versions) == 1 and
            re.fullmatch(r"Lean \(version 4\.21\.0, [^\r\n]+\)", versions[0]) is not None,
            "actual Lean version: " + output[-2000:])
    return versions[0]


def run(argv, work, timeout=300, expected_success=True):
    process = subprocess.run(argv, cwd=work, text=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, timeout=timeout)
    if expected_success:
        require(process.returncode == 0, "command failed: " + " ".join(map(str, argv)) + "\n" + process.stdout[-8000:])
    return process


def prepare(work, packages=None):
    require(work.resolve() != ROOT.resolve() and work.resolve() != HERE.resolve(), "dedicated build workspace")
    if work.exists() and any(work.iterdir()):
        marker = work / MARKER
        require(marker.is_file() and json.loads(marker.read_text()) == OWNER, "unrecognized nonempty workspace")
    work.mkdir(parents=True, exist_ok=True)
    (work / MARKER).write_text(json.dumps(OWNER) + "\n")
    if packages is not None:
        target = work / ".lake/packages"
        target.parent.mkdir(parents=True, exist_ok=True)
        require(not target.exists(), "dependency directory already exists")
        require(packages.is_dir(), "shared dependency directory")
        target.symlink_to(packages.resolve(), target_is_directory=True)
    for name in LEAN_FILES | {"lakefile.toml", "lake-manifest.json", "lean-toolchain"}:
        target = work / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(HERE / name, target)
    (work / "LemmaG").mkdir(exist_ok=True)
    shutil.copyfile(ROOT / SOURCE, work / "LemmaG/Stream.lean")
    (work / "LemmaG.lean").write_text("import LemmaG.Stream\n")
    # Only this marked workspace's own compiled outputs are removed. Cached
    # dependency libraries are retained; all new/imported local proofs rebuild.
    output = work / ".lake/build"
    if output.exists():
        require(not output.is_symlink(), "local build output must not be a symlink")
        shutil.rmtree(output)


def dependency_check(work):
    manifest = json.loads((HERE / "lake-manifest.json").read_text())
    heads = {}
    for package in manifest["packages"]:
        path = work / ".lake/packages" / package["name"]
        head = run(["git", "rev-parse", "HEAD"], path).stdout.strip()
        require(head == package["rev"], "dependency commit: " + package["name"])
        require(run(["git", "status", "--porcelain", "--untracked-files=no"], path).stdout == "",
                "modified dependency source: " + package["name"])
        heads[package["name"]] = head
    return heads


def full_check(work, no_cache, packages):
    source = source_check()
    prepare(work, packages)
    version_output = run(["lake", "env", "lean", "--version"], work, timeout=600).stdout
    (work / "TOOLCHAIN.log").write_text(version_output)
    version = parse_lean_version(version_output)
    if not no_cache:
        run(["lake", "exe", "cache", "get", *CACHE_MODULES], work, timeout=900)
    heads = dependency_check(work)
    build = run(["lake", "build", "PrefixNorm", "PrefixNorm.Examples"], work, timeout=600)
    require("warning:" not in build.stdout and "error:" not in build.stdout, "Lean build diagnostics")
    (work / "BUILD.log").write_text(build.stdout)
    require((work / "LemmaG/Stream.lean").read_bytes() == (ROOT / SOURCE).read_bytes(), "unchanged compiled Stream")
    axioms = run(["lake", "env", "lean", "PrintAxioms.lean"], work, timeout=120).stdout
    (work / "AXIOMS.log").write_text(axioms)
    names = sum(json.loads((HERE / "THEOREMS.json").read_text()).values(), [])
    checked = parse_axioms(axioms, names)
    require(checked == json.loads((HERE / "AXIOMS.json").read_text()), "axiom dependency receipt")
    # A semantically false strengthening of the partial-component theorem:
    # replace 2*L^2 by L^2. Its proof must fail, as the 41/25 fixture predicts.
    text = (HERE / "PrefixNorm.lean").read_text()
    original = "‖components realDone imagDone old new‖ ^ 2 ≤ 2 * L ^ 2 := by"
    require(text.count(original) == 1, "precision mutation target")
    mutant = text.replace(original, "‖components realDone imagDone old new‖ ^ 2 ≤ L ^ 2 := by")
    path = work / "Undercharged.lean"
    path.write_text(mutant)
    failure = run(["lake", "env", "lean", str(path)], work, timeout=120, expected_success=False)
    require(failure.returncode != 0 and "linarith failed" in failure.stdout,
            "undercharged partial-store theorem was not rejected for its proof")
    (work / "CONTROL.log").write_text(failure.stdout)
    path.unlink()
    require(source_check() == source, "source changed during proof check")
    require(dependency_check(work) == heads, "dependency changed during proof check")
    receipt = dict(status="PASS_LEAN_UNITARY_PREFIX_NORM", lean_version=version,
                   dependency_commits=heads, source=source, axioms=checked,
                   undercharged_partial_store_rejected=True,
                   freshly_built=["LemmaG.Stream", "PrefixNorm", "PrefixNorm.Examples"],
                   scope="Quantified prefix and component-store lemmas on imported semantics; "
                         "concrete selected event/row bindings and full physical/roundoff transfer remain open.")
    (work / "RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], "core=13 examples=20 axioms=33 semantic_mutation=rejected")
    print("axioms_sha256=" + sha(encoded(checked)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-only", action="store_true", help="bindings/policy only; does not run Lean")
    parser.add_argument("--work", type=Path, help="dedicated persistent build directory")
    parser.add_argument("--no-cache", action="store_true", help="reuse already available pinned dependencies")
    parser.add_argument("--packages", type=Path, help="explicitly share an existing pinned dependency directory")
    args = parser.parse_args()
    if args.source_only:
        print(source_check()["status"], "not_a_Lean_proof_check")
    elif args.work:
        full_check(args.work.resolve(), args.no_cache, args.packages)
    else:
        with tempfile.TemporaryDirectory(prefix="lean-prefix-norm-") as path:
            full_check(Path(path), args.no_cache, args.packages)


if __name__ == "__main__":
    main()
