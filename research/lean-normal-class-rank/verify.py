"""Source/finite replay, or an explicitly requested fresh Lean kernel build.

The default command never claims Lean ran. Kernel mode requires --lake,
--work-dir and either --packages (an existing pinned cache) or --fetch-cache.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from finite import replay


def need(ok, message):
    if not ok:
        raise ValueError(message)


def unique(items):
    out = {}
    for key, value in items:
        need(key not in out, "duplicate JSON key")
        out[key] = value
    return out


def read(path):
    def reject(value):
        raise ValueError("nonfinite JSON: " + value)
    return json.loads(Path(path).read_bytes(), object_pairs_hook=unique, parse_constant=reject)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def lean_code(source):
    """Remove nested Lean comments; retain newlines and actual code tokens."""
    output, depth, i = [], 0, 0
    while i < len(source):
        if source.startswith("/-", i):
            depth += 1
            i += 2
        elif depth and source.startswith("-/", i):
            depth -= 1
            i += 2
        elif not depth and source.startswith("--", i):
            end = source.find("\n", i)
            i = len(source) if end < 0 else end
        else:
            output.append(source[i] if not depth or source[i] == "\n" else " ")
            i += 1
    need(depth == 0, "unterminated Lean comment")
    return "".join(output)


def check_sources(root=HERE):
    pins = read(root / "PROOF-SOURCES.json")
    need(pins["schema"] == "normal-class-rank-proof-sources/1", "source schema")
    inventory = {str(p.relative_to(root)) for folder in (root / "lean", root / "sources")
                 for p in folder.rglob("*") if p.is_file()}
    need(inventory == set(pins["files"]), "incomplete proof source inventory")
    need({"lean/NormalClassRank.lean", "lean/Counterexamples.lean",
          "sources/PR2338-README.md", "sources/PR2338-NOTICE.md"} <= inventory,
         "required proof inputs missing")
    for name, expected in pins["files"].items():
        path = Path(name)
        need(not path.is_absolute() and ".." not in path.parts, "relative source path")
        raw = (root / path).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == expected, "source bytes changed: " + name)
        if path.suffix == ".lean":
            code = lean_code(raw.decode())
            need(not re.search(r"\b(axiom|sorry|admit|native_decide|unsafe|run_tac|elab|macro|syntax)\b", code),
                 "unapproved proof escape in " + name)
    manifest = read(root / "lean/lake-manifest.json")
    actual = {p["name"]: {"rev": p["rev"], "url": p["url"]} for p in manifest["packages"]}
    need(encoded(actual) == encoded(pins["dependencies"]), "dependency pins")
    need((root / "lean/lean-toolchain").read_text().strip() == pins["toolchain"], "toolchain pin")
    need(len(pins["axiom_targets"]) == len(set(pins["axiom_targets"])), "distinct theorem targets")
    for item in read(root / "SOURCES.json")["files"]:
        if item["usage"] == "input":
            path = Path(item["path"])
            need(not path.is_absolute() and ".." not in path.parts, "relative live input")
            need(hashlib.sha256((root.parents[1] / path).read_bytes()).hexdigest() == item["sha256"],
                 "live source bytes changed: " + str(path))
    return pins


def parse_axioms(output, targets):
    found = {}
    for name, raw in re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]", output):
        need(name not in found, "duplicate axiom report")
        axioms = sorted(x.strip() for x in raw.split(",") if x.strip())
        need(set(axioms) <= {"propext", "Classical.choice", "Quot.sound"},
             "unexpected axiom: " + name)
        found[name] = axioms
    for name in re.findall(r"'([^']+)' does not depend on any axioms", output):
        need(name not in found, "duplicate axiom report")
        found[name] = []
    need(set(found) == set(targets), "missing or extra theorem axiom report")
    need("sorryAx" not in output, "unchecked proof reported")
    return found


def kernel_build(args, pins):
    lake = args.lake.resolve()
    need(lake.is_file(), "Lake executable missing")
    lean = lake.with_name("lean")
    version = subprocess.check_output([str(lean), "--version"], text=True)
    need(pins["lean_version"] in version and pins["lean_commit"] in version, "wrong Lean version")
    work = args.work_dir.resolve()
    need(not work.exists(), "build directory already exists")
    # The package may itself be a read-only export. Only the newly created
    # build copy is made writable; source permissions are never changed.
    shutil.copytree(HERE / "lean", work, copy_function=shutil.copyfile)
    work.chmod(0o755)
    for directory in work.rglob("*"):
        if directory.is_dir():
            directory.chmod(0o755)
    env = dict(os.environ, PATH=str(lake.parent) + os.pathsep + os.environ.get("PATH", ""),
               LEAN_NUM_THREADS="4")
    # No previously built local proof objects are copied; only library packages
    # may be reused, and every Git dependency is checked below.
    def run(command, label, timeout=180):
        result = subprocess.run(command, cwd=work, env=env, capture_output=True, text=True, timeout=timeout)
        output = result.stdout + result.stderr
        (work / (label + ".log")).write_text(output)
        need(result.returncode == 0, label + " failed; inspect " + str(work / (label + ".log")))
        return output

    if args.packages:
        packages = args.packages.resolve()
        need(packages.is_dir(), "package cache missing")
        (work / ".lake").mkdir()
        (work / ".lake/packages").symlink_to(packages, target_is_directory=True)
    else:
        run([str(lake), "exe", "cache", "get"], "cache", timeout=600)
        packages = work / ".lake/packages"
    for name, dependency in pins["dependencies"].items():
        path = packages / name
        actual = subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
        need(actual == dependency["rev"], "dependency head: " + name)
        need(subprocess.run(["git", "-C", str(path), "diff", "--quiet", "HEAD", "--"],
                            capture_output=True).returncode == 0, "modified dependency source: " + name)
    run([str(lake), "build"], "kernel-build")
    probe = "import Counterexamples\n" + "\n".join("#print axioms " + n for n in pins["axiom_targets"]) + "\n"
    probe += "\n".join("#check " + n for n in pins["type_targets"]) + "\n"
    (work / "AxiomProbe.lean").write_text(probe)
    output = run([str(lake), "env", "lean", "AxiomProbe.lean"], "axioms")
    axioms = parse_axioms(output, pins["axiom_targets"])
    # False conclusions reach Lean's arithmetic/type checker after valid imports.
    controls = {
        "equal_classes": "import Counterexamples\nopen NormalClassRank.Controls\nexample : Fintype.card (Fin 1) ≤ 2 * (1-equalClass).rank := by\n  norm_num [equalClass]\n",
        "zero_diagonal_only": "import Counterexamples\nopen NormalClassRank.Controls\nexample : Fintype.card (Fin 3) ≤ 2 * (1-incompatible).rank := by\n  exfalso\n  have h := incompatible_violates_rank\n  norm_num at h\n",
        "one_third_kernel": "import Counterexamples\nopen NormalClassRank.Controls Module\nexample : 3 * finrank ℚ (LinearMap.ker (1-cycle).mulVecLin) ≤ Fintype.card (Fin 2) := by\n  norm_num [cycle_kernel]\n",
    }
    rejected = []
    for key, source in controls.items():
        path = work / ("Reject_" + key + ".lean")
        path.write_text(source)
        result = subprocess.run([str(lake), "env", "lean", path.name], cwd=work, env=env,
                                capture_output=True, text=True, timeout=90)
        output = result.stdout + result.stderr
        (work / ("reject_" + key + ".log")).write_text(output)
        need(result.returncode != 0 and "error:" in output
             and any(term in output for term in ("unsolved goals", "Type mismatch", "Application type mismatch"))
             and not any(term in output for term in ("Unknown", "unknown", "object file", "failed to synthesize")),
             "invalid negative control: " + key)
        rejected.append(key)
    return {"kernel_checked": True, "lean_version": version.strip(),
            "axioms": axioms, "rejected_invalid_proofs": rejected,
            "dependencies": pins["dependencies"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lake", type=Path)
    parser.add_argument("--work-dir", type=Path)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--packages", type=Path)
    group.add_argument("--fetch-cache", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    need(args.out is None or not args.out.exists(), "output already exists")
    need(bool(args.lake) == bool(args.work_dir), "--lake and --work-dir are paired")
    need(not args.lake or args.packages or args.fetch_cache, "kernel mode needs --packages or --fetch-cache")
    need(args.lake or not (args.packages or args.fetch_cache), "cache options require kernel mode")
    pins = check_sources()
    finite = replay()
    need(encoded(finite) == encoded(read(HERE / "FINITE.json")), "finite receipt differs")
    historical = read(HERE / "KERNEL.json")
    need(historical.get("kernel_checked") is True, "historical kernel receipt mode")
    need(encoded(historical["finite"]) == encoded(finite), "historical finite binding")
    need(encoded(historical["proof_source_hashes"]) == encoded(pins["files"]), "historical proof source binding")
    need(encoded(historical["dependencies"]) == encoded(pins["dependencies"]), "historical dependency binding")
    need(set(historical["axioms"]) == set(pins["axiom_targets"]), "historical theorem coverage")
    need(all(set(v) <= {"propext", "Classical.choice", "Quot.sound"} for v in historical["axioms"].values()),
         "historical unexpected axiom")
    need(pins["lean_version"] in historical["lean_version"] and
         pins["lean_commit"] in historical["lean_version"], "historical Lean version")
    need(historical["rejected_invalid_proofs"] ==
         ["equal_classes", "zero_diagonal_only", "one_third_kernel"],
         "historical rejection coverage")
    result = {"finite": finite, "proof_source_hashes": pins["files"], "kernel_checked": False}
    if args.lake:
        result.update(kernel_build(args, pins))
    if args.out:
        with args.out.open("x") as handle:
            json.dump(result, handle, sort_keys=True, indent=2)
            handle.write("\n")
    print("PASS_NORMAL_CLASS_RANK_KERNEL" if result["kernel_checked"] else
          "PASS_NORMAL_CLASS_RANK_SOURCES_AND_FINITE_ONLY", "theorems=" + str(len(pins["axiom_targets"])),
          "kernel_checked=" + str(result["kernel_checked"]).lower())


if __name__ == "__main__":
    main()
