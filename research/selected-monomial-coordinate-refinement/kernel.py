"""Explicit fresh Lean build; no default or source-only kernel-success mode.

The invocation needs --lake, --work-dir, --packages and --out.  Existing Mathlib
compiled objects are reused, while all package proof modules are rebuilt in a
new directory.  The receipt distinguishes these two trust boundaries.

The fresh-workdir/axiom-report pattern follows Gareth Davidson's PR2341
``verify.py`` (commit f448ce821ba32001bf1ec13f7088450d2edcd112).
Prepared for AAAmirinu with substantial OpenAI Codex assistance. Apache-2.0.
"""

from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
VERSION = "4.33.0-rc1"
COMMIT = "62eed1db4d67327ec8120be05f1a1b0847d74561"
TOOLCHAIN = "leanprover/lean4:v4.33.0-rc1"
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
SOURCE_FILES = (
    "LemmaG/Stream.lean", "TensorLift.lean", "SelectedRecipe.lean",
    "MonomialRefinement.lean", "PhaseWords.lean", "lakefile.toml",
    "lake-manifest.json", "lean-toolchain",
)
MODULES = ("SelectedRecipe", "MonomialRefinement", "PhaseWords")
TARGETS = (
    "SelectedMonomial.word_affine",
    "SelectedMonomial.reverse_forward",
    "SelectedMonomial.forward_reverse",
    "SelectedMonomial.strict_upper_phase",
    "SelectedMonomial.phase_must_use_recovered_input",
    "SelectedMonomial.single_constant_is_wrong",
    "SelectedMonomial.primitive_word",
    "SelectedMonomial.selected_word",
    "SelectedMonomial.selected_inverse_word",
    "SelectedMonomial.spectator_fixed",
    "SelectedMonomial.selected_physical_roundtrip",
    "SelectedMonomial.selected_physical_reverse_roundtrip",
    "SelectedMonomial.tensor_coordinates",
    "SelectedMonomial.tensor_coordinates_with_spectators",
    "SelectedMonomial.backward_forward",
    "SelectedMonomial.forward_backward",
    "SelectedMonomial.selected_phase_product",
    "SelectedMonomial.selected_phase_mod_four",
    "SelectedMonomial.selected_full_array",
    "SelectedMonomial.physical_backward_forward",
    "SelectedMonomial.physical_forward_backward",
    "SelectedMonomial.physical_tensor_refinement",
    "SelectedPhaseWords.carryLoop_conservation",
    "SelectedPhaseWords.negate_unsigned_mod",
    "SelectedPhaseWords.negate_signed",
    "SelectedPhaseWords.negate_signed_headroom",
    "SelectedPhaseWords.rotateWords_refines",
    "SelectedPhaseWords.phase_pass_coefficient",
    "SelectedPhaseWords.mostNegative_negate",
    "SelectedPhaseWords.mostNegative_signed",
    "SelectedPhaseWords.mostNegative_not_signed_negation",
)
DEPENDENCY_REVISIONS = {
    "mathlib": "55b7917b472489c7c56a0fa6393af05cfd536599",
    "plausible": "b1c4a69a7e247ab7df20460212001673d74f08c0",
    "LeanSearchClient": "0498c7c070c143a3bf7379f4d99a2c63bb9d9715",
    "importGraph": "18a90119a5d316358fde6c86e0ca24e59212e32c",
    "proofwidgets": "b1436dc749e722c9920036b52cdc43b3451d0b69",
    "aesop": "57d3325be72a842920813bcb40f96a6f7393c185",
    "Qq": "ee41917ae11d38479fb8fb24745f7ca4bf0a784d",
    "batteries": "2c810760f0a0c4536b397dbe30ca9b2f2f467366",
    "Cli": "da07ca808b6718cb2aed14dba154e5a08b8f8ecf",
}
NEGATIVE_PROBES = {
    "single_constant_for_two_columns": """import MonomialRefinement
example : (2 + SelectedMonomial.q 0 + SelectedMonomial.q 0) % 4 = 0 := by
  rw [SelectedMonomial.single_constant_is_wrong]
  norm_num
""",
    "phase_on_output_address": """import MonomialRefinement
set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
example : SelectedMonomial.q (SelectedMonomial.sigma 0) = SelectedMonomial.q 0 := by
  decide
""",
    "signed_negation_without_headroom": """import PhaseWords
example : SelectedPhaseWords.signed
    (SelectedPhaseWords.negate (SelectedPhaseWords.mostNegative 3)) =
    -SelectedPhaseWords.signed (SelectedPhaseWords.mostNegative 3) := by
  rw [SelectedPhaseWords.mostNegative_negate, SelectedPhaseWords.mostNegative_signed]
  norm_num
""",
}


class KernelError(ValueError):
    """A check failed; no kernel-success receipt may be produced."""


def need(condition, message):
    if not condition:
        raise KernelError(message)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def unique_pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(path):
    def reject_constant(value):
        raise KernelError("nonfinite JSON value: " + value)
    return json.loads(path.read_bytes(), object_pairs_hook=unique_pairs,
                      parse_constant=reject_constant)


def lean_code(source):
    """Strip nested/block/line comments before the conservative escape scan."""
    output, depth, index = [], 0, 0
    while index < len(source):
        if source.startswith("/-", index):
            depth += 1
            output.append(" ")
            index += 2
        elif depth and source.startswith("-/", index):
            depth -= 1
            output.append(" ")
            index += 2
        elif not depth and source.startswith("--", index):
            end = source.find("\n", index)
            index = len(source) if end < 0 else end
        else:
            output.append(source[index] if not depth or source[index] == "\n" else " ")
            index += 1
    need(depth == 0, "unterminated Lean comment")
    return "".join(output)


def source_snapshot():
    raw_files = {}
    for name in SOURCE_FILES:
        path = HERE / "lean" / name
        need(path.is_file() and not path.is_symlink(), "missing/nonregular source: " + name)
        raw_files[name] = path.read_bytes()
        if path.suffix == ".lean":
            code = lean_code(raw_files[name].decode("utf-8"))
            need(not re.search(r"\b(axiom|sorry|admit|native_decide|unsafe|run_tac|elab|macro|syntax)\b",
                               code), "unapproved proof escape: " + name)
    need(raw_files["lean-toolchain"].decode("utf-8").strip() == TOOLCHAIN,
         "wrong source toolchain")
    manifest = read_json(HERE / "lean/lake-manifest.json")
    need(manifest.get("packagesDir") == ".lake/packages", "unexpected packages directory")
    dependencies = {}
    for dependency in manifest["packages"]:
        name = dependency["name"]
        need(name not in dependencies, "duplicate dependency: " + name)
        need(dependency["type"] == "git" and dependency.get("subDir") is None,
             "nonstandard dependency: " + name)
        dependencies[name] = {"rev": dependency["rev"], "url": dependency["url"]}
    need({name: data["rev"] for name, data in dependencies.items()} == DEPENDENCY_REVISIONS,
         "the exact nine dependency revisions are required")
    # Keep inherited proof bytes and predecessor notices source-authenticated.
    for entry in read_json(HERE / "SOURCES.json")["vendored_sources"]:
        relative = Path(entry["path"])
        need(not relative.is_absolute() and ".." not in relative.parts, "unsafe vendored path")
        need(sha256((HERE / relative).read_bytes()) == entry["sha256"],
             "vendored bytes changed: " + entry["path"])
    return raw_files, dependencies


def parse_axioms(output, targets=TARGETS):
    found = {}
    for name, raw in re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]", output):
        need(name not in found, "duplicate axiom report: " + name)
        axioms = sorted(item.strip() for item in raw.split(",") if item.strip())
        need(set(axioms) <= ALLOWED_AXIOMS, "unexpected axiom for " + name)
        found[name] = axioms
    for name in re.findall(r"'([^']+)' does not depend on any axioms", output):
        need(name not in found, "duplicate axiom report: " + name)
        found[name] = []
    need(set(found) == set(targets), "missing or extra target axiom report")
    need("sorryAx" not in output, "unchecked proof in axiom output")
    return found


def dependency_snapshot(packages, expected):
    result = {}
    for name, dependency in sorted(expected.items()):
        path = packages / name
        need(path.is_dir(), "missing dependency: " + name)
        head = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
        need(head == dependency["rev"], "dependency head: " + name)
        status = subprocess.run(["git", "-C", str(path), "diff", "--quiet", "HEAD", "--"],
                                capture_output=True)
        need(status.returncode == 0, "modified tracked dependency source: " + name)
        result[name] = dict(dependency, head=head, tracked_clean=True)
    return result


def run_kernel(args, receipt):
    sources, dependencies = source_snapshot()
    receipt["source_sha256"] = {"lean/" + name: sha256(raw) for name, raw in sources.items()}
    receipt["harness_sha256"] = sha256(Path(__file__).read_bytes())
    lake = args.lake.resolve(strict=True)
    lean = lake.with_name("lean.exe" if lake.suffix == ".exe" else "lean")
    need(lake.is_file() and lean.is_file(), "Lake and sibling Lean executables are required")
    version = subprocess.run([str(lean), "--version"], capture_output=True,
                             text=True, check=True, timeout=30).stdout.strip()
    need(re.search(r"\bversion " + re.escape(VERSION) + r"(?:,|\))", version) is not None
         and re.search(r"\bcommit " + COMMIT + r"(?:,|\))", version) is not None,
         "wrong Lean version or commit: " + version)
    receipt["toolchain"] = {"requested": TOOLCHAIN, "version_output": version,
                            "lean_commit": COMMIT, "lake_path": str(lake),
                            "lean_executable_sha256": sha256(lean.read_bytes()),
                            "lake_executable_sha256": sha256(lake.read_bytes())}
    packages = args.packages.resolve(strict=True)
    need(packages.is_dir(), "package cache missing")
    receipt["dependencies_before"] = dependency_snapshot(packages, dependencies)
    receipt["scope"]["dependency_source_pins_checked"] = True
    work = args.work_dir.resolve()
    need(not work.exists() and not args.work_dir.is_symlink(), "build directory already exists")
    need(not work.is_relative_to(HERE), "build directory must be outside the source package")
    work.mkdir(parents=True)
    for name, raw in sources.items():
        dest = work / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
    (work / ".lake").mkdir()
    (work / ".lake/packages").symlink_to(packages, target_is_directory=True)
    receipt["scope"]["dependency_compiled_cache_reused"] = True
    receipt["work_directory"] = str(work)
    receipt["package_cache"] = str(packages)
    env = dict(os.environ)
    env["PATH"] = str(lake.parent) + os.pathsep + env.get("PATH", "")
    env["LEAN_NUM_THREADS"] = "4"
    # Avoid accidentally importing package objects from another project.
    for name in ("LEAN_PATH", "LEAN_SRC_PATH", "LEAN_SYSROOT", "LAKE_HOME"):
        env.pop(name, None)

    def run(command, label, timeout):
        start = time.monotonic()
        process = subprocess.run(command, cwd=work, env=env, capture_output=True,
                                 text=True, encoding="utf-8", errors="replace", timeout=timeout)
        output = process.stdout + process.stderr
        log = work / (label + ".log")
        log.write_text(output, encoding="utf-8")
        record = {"command": command, "exit_code": process.returncode,
                  "elapsed_seconds": round(time.monotonic() - start, 3),
                  "log_path": str(log), "log_sha256": sha256(output.encode("utf-8"))}
        return record, output

    build, output = run([str(lake), "build", *MODULES], "kernel-build", args.timeout)
    receipt["positive_build"] = build
    need(build["exit_code"] == 0, "kernel build failed; inspect " + build["log_path"])
    need("sorry" not in output, "unexpected incomplete-proof warning in build output")
    probe = "\n".join("import " + name for name in MODULES) + "\n"
    probe += "\n".join("#print axioms " + target for target in TARGETS) + "\n"
    (work / "AxiomProbe.lean").write_text(probe, encoding="utf-8")
    axiom_run, output = run([str(lake), "env", "lean", "AxiomProbe.lean"], "axioms", 180)
    receipt["axiom_probe"] = dict(axiom_run, source_sha256=sha256(probe.encode("utf-8")))
    need(axiom_run["exit_code"] == 0, "axiom probe failed; inspect " + axiom_run["log_path"])
    receipt["axioms"] = parse_axioms(output)
    receipt["negative_probes"] = {}
    for name, code in NEGATIVE_PROBES.items():
        path = work / ("Reject_" + name + ".lean")
        path.write_text(code, encoding="utf-8")
        record, output = run([str(lake), "env", "lean", path.name], "reject_" + name, 180)
        mathematical_failure = any(term in output for term in (
            "unsolved goals", "Type mismatch", "type mismatch",
            "Tactic `decide` proved that the proposition", "tactic 'decide' proved that"))
        infrastructure_failure = any(term in output.lower() for term in (
            "unknown", "object file", "failed to synthesize", "maximum recursion",
            "maximum number of heartbeats", "unexpected token", "invalid import"))
        record.update(source_sha256=sha256(code.encode("utf-8")),
                      output_excerpt=output[-4000:],
                      rejected_false_theorem=record["exit_code"] != 0 and "error:" in output
                      and mathematical_failure and not infrastructure_failure)
        receipt["negative_probes"][name] = record
        need(record["rejected_false_theorem"], "invalid negative probe: " + name)
    receipt["dependencies_after"] = dependency_snapshot(packages, dependencies)
    need(receipt["dependencies_before"] == receipt["dependencies_after"], "dependency state changed")
    current, _ = source_snapshot()
    need(current == sources, "package sources changed during build; rerun the final bytes")
    for name, raw in sources.items():
        need((work / name).read_bytes() == raw, "staged source changed: " + name)
    receipt["kernel_checked"] = True
    receipt["status"] = "pass"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lake", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--packages", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=1800, help="positive build timeout in seconds")
    args = parser.parse_args(argv)
    need(args.timeout > 0, "positive timeout required")
    need(not args.out.exists() and not args.out.is_symlink(), "receipt path already exists")
    need(args.out.parent.is_dir(), "receipt parent directory must already exist")
    receipt = {"schema": "selected-monomial-coordinate-kernel/1", "status": "failed",
               "kernel_checked": False,
               "python_version": sys.version,
               "platform": sys.platform,
               "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "scope": {"fresh_local_modules": list(MODULES),
                         "dependency_source_pins_checked": False,
                         "dependency_compiled_cache_reused": False,
                         "dependency_compiled_cache_independently_rebuilt": False,
                         "python_or_tape_implementation_formalized": False,
                         "full_multiplication_theorem_verified": False}}
    failure = None
    try:
        run_kernel(args, receipt)
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as error:
        failure = error
        receipt["error"] = str(error)
    receipt["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with args.out.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(receipt, handle, sort_keys=True, indent=2)
        handle.write("\n")
    if failure:
        print("FAIL_SELECTED_MONOMIAL_KERNEL:", failure, file=sys.stderr)
        return 1
    print("PASS_SELECTED_MONOMIAL_KERNEL", "kernel_checked=true",
          "axiom_targets=" + str(len(TARGETS)), "false_theorems_rejected=" + str(len(NEGATIVE_PROBES)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
