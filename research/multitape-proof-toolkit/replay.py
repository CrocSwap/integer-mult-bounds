"""Fresh serial Lean rebuild and complete defining-module axiom audit. Apache-2.0.

No download, model, solver, GPU, or persistent process is launched. Install the
pinned Lean/Mathlib environment separately. Every compiler output goes outside
the immutable source package, under a new explicitly supplied output folder.
"""
from __future__ import annotations
import argparse, importlib.util, json, os, re, shutil, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("toolkit_checks", P / "checks.py")
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)

def command(argv, *, cwd, env=None, timeout=180):
    result = subprocess.run(argv, cwd=cwd, env=env, text=True, encoding="utf-8",
                            errors="replace", stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=timeout)
    checks.need(result.returncode == 0, "command failed:\n" + result.stdout[-7000:])
    checks.need(not re.search(r"(?m)^.*\berror(?:\(|:)", result.stdout), "error-bearing compiler transcript")
    return result.stdout

def check_module_inventory(config):
    modules = config["modules"]
    checks.need(modules and len(modules) == len(set(modules)), "empty or duplicated module list")
    checks.need(all(re.fullmatch(r"MultitapeToolkit\.[A-Za-z][A-Za-z0-9]*", n) for n in modules), "invalid owned module name")
    files = {p.relative_to(P / "lean").as_posix() for p in (P / "lean").rglob("*.lean")
             if ".lake" not in p.relative_to(P / "lean").parts}
    expected = {n.replace(".", "/") + ".lean" for n in modules} | {"MultitapeToolkit.lean", "Check.lean"}
    checks.need(files == expected, "Lean source/module inventory mismatch")
    lines = [line.strip() for line in (P / "lean/MultitapeToolkit.lean").read_text().splitlines() if line.strip()]
    checks.need(lines == ["import " + n for n in modules], "aggregator import inventory mismatch")
    return modules

def dependency_paths(cache, pinned):
    package_root = cache / ".lake/packages"
    libraries = []
    for row in pinned["packages"]:
        package = package_root / row["name"]
        checks.need(package.is_dir(), "missing cached dependency: " + row["name"])
        actual = command(["git", "rev-parse", "HEAD"], cwd=package).strip()
        checks.need(actual == row["rev"], "dependency revision mismatch: " + row["name"])
        dirty = command(["git", "status", "--porcelain", "--untracked-files=no"], cwd=package).strip()
        checks.need(not dirty, "tracked dependency source drift: " + row["name"])
        lib = package / ".lake/build/lib/lean"
        if row["name"] == "mathlib":
            checks.need(lib.is_dir(), "missing compiled Mathlib cache")
        if lib.is_dir():
            libraries.append(lib)
    return libraries

def actual_lean_audit_controls(lean, out, lib, env, modules, timeout):
    """Real compiler fixtures; the rejected axioms never enter a positive build."""
    fixture = out / "fixtures/MultitapeToolkit"
    fixture.mkdir(parents=True)
    auditor = (P / "lean/Check.lean").read_text(encoding="utf-8-sig")
    passed = []
    for suffix, body, required_error in [
        ("CoverageFixture", "def globallyNamedToolkitHelper : Nat := 0\nprivate theorem privateCoverage : True := True.intro\n", None),
        ("UnusedPrivateAxiom", "private axiom unusedPrivateDependency : False\n", "Toolkit declares an axiom"),
        ("PublicAxiom", "axiom publicDependency : False\n", "Toolkit declares an axiom"),
        ("PrivateUnprovedTheorem", "private theorem missingProof : False := by sorry\n", "forbidden axiom")]:
        module = "MultitapeToolkit." + suffix
        source = fixture / (suffix + ".lean")
        source.write_text(body, encoding="utf-8")
        artifact = lib / "MultitapeToolkit" / (suffix + ".olean")
        command([str(lean), "-j1", "-R", str(out / "fixtures"), str(source), "-o", str(artifact)],
                cwd=out, env=env, timeout=timeout)
        driver = out / (suffix + "Audit.lean")
        driver.write_text(auditor.replace("import MultitapeToolkit\n", "import MultitapeToolkit\nimport " + module + "\n", 1), encoding="utf-8")
        report = out / (suffix + ".json")
        fixture_env = dict(env, MULTITAPE_TOOLKIT_AUDIT_PATH=str(report))
        result = subprocess.run([str(lean), "-j1", "-DmaxHeartbeats=4000000", str(driver)], cwd=out,
                                env=fixture_env, text=True, encoding="utf-8", errors="replace",
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
        (out / (suffix + ".log")).write_text(result.stdout, encoding="utf-8")
        if required_error:
            checks.need(result.returncode != 0 and required_error in result.stdout,
                        "real Lean negative fixture failed for wrong reason: " + suffix + "\n" + result.stdout[-4000:])
            checks.need(not report.exists(), "rejected Lean fixture emitted a success report")
        else:
            checks.need(result.returncode == 0 and report.is_file(), "real ownership coverage fixture failed")
            audit = json.loads(report.read_text())
            checks.validate_audit(audit["rows"], audit["declaration_names"], set(modules) | {module})
            owned = [r for r in audit["rows"] if r["module"] == module]
            checks.need(any(r["name"] == "globallyNamedToolkitHelper" for r in owned), "global helper omitted")
            checks.need(any(r["name"].startswith("_private.") and r["kind"] == "theorem" for r in owned), "private helper omitted")
        passed.append(suffix)
    return passed

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--lean", type=Path)
    parser.add_argument("--cache-project", type=Path, default=P / "lean")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    checks.need(1 <= args.timeout <= 600, "bounded compiler timeout required")
    initial_manifest_digest = checks.digest(P / "MANIFEST.json")
    before = checks.inventory(P)
    config = json.loads((P / "MODULES.json").read_text())
    modules = check_module_inventory(config)
    pinned = json.loads((P / "lean/lake-manifest.json").read_text())
    candidate = args.lean or shutil.which("lean")
    checks.need(candidate is not None, "Lean executable not found")
    lean = Path(candidate).resolve()
    checks.need(lean.is_file(), "Lean executable not found: " + str(lean))
    compiler_env = dict(os.environ)
    compiler_env.pop("LEAN_SYSROOT", None)
    version = command([str(lean), "--version"], cwd=P, env=compiler_env)
    checks.need("version " + config["lean_version"] + "," in version,
                "wrong Lean compiler; expected " + config["lean_version"])
    libraries = dependency_paths(args.cache_project.resolve(), pinned)
    out = args.out.resolve()
    checks.need(out != P and P not in out.parents, "outputs must be outside the package")
    checks.need(not out.exists(), "fresh compiler output directory required")
    out.mkdir(parents=True)
    lib = out / "olean"
    lib.mkdir()
    env = dict(compiler_env, LEAN_PATH=os.pathsep.join(str(p) for p in [lib, *libraries]))
    receipts = []
    for module in modules + ["MultitapeToolkit"]:
        relative = Path(*module.split(".")).with_suffix(".lean")
        source = P / "lean" / relative
        artifact = (lib / relative).with_suffix(".olean")
        artifact.parent.mkdir(parents=True, exist_ok=True)
        log = command([str(lean), "-j1", "-DmaxHeartbeats=2000000", "-R", str(P / "lean"),
                       str(source), "-o", str(artifact)], cwd=P / "lean", env=env, timeout=args.timeout)
        (out / (module + ".log")).write_text(log, encoding="utf-8")
        receipts.append({"module": module, "source_sha256": checks.digest(source),
                         "artifact_sha256": checks.digest(artifact)})
        print("PASS_KERNEL " + module, flush=True)
    report = out / "axioms.json"
    env["MULTITAPE_TOOLKIT_AUDIT_PATH"] = str(report)
    log = command([str(lean), "-j1", "-DmaxHeartbeats=4000000", str(P / "lean/Check.lean")],
                  cwd=P / "lean", env=env, timeout=args.timeout)
    (out / "audit.log").write_text(log, encoding="utf-8")
    checks.need(report.is_file(), "missing actual Lean declaration report")
    audit = json.loads(report.read_text())
    checks.need(set(audit["modules"]) == set(modules) | {"MultitapeToolkit"}, "imported-module audit coverage mismatch")
    checks.validate_audit(audit["rows"], audit["declaration_names"], set(modules))
    expected_audit = json.loads((P / "expected/AXIOMS.json").read_text())
    def normalize(rows):
        return sorted((r["name"], r["module"], r["kind"], tuple(sorted(r["axioms"]))) for r in rows)
    checks.need(normalize(audit["rows"]) == normalize(expected_audit["rows"]),
                "actual declaration/axiom inventory differs from the pinned golden report")
    checks.need(checks.inventory(P) == before and checks.digest(P / "MANIFEST.json") == initial_manifest_digest, "source changed during kernel audit")
    private_count = sum(r["name"].startswith("_private.") for r in audit["rows"])
    controls = actual_lean_audit_controls(lean, out, lib, env, modules, args.timeout)
    checks.need(checks.inventory(P) == before and checks.digest(P / "MANIFEST.json") == initial_manifest_digest, "source changed during audit controls")
    result = {"status": "PASS_FRESH_KERNEL_AND_COMPLETE_AXIOM_AUDIT",
              "lean_version": config["lean_version"], "dependency_revisions": {r["name"]: r["rev"] for r in pinned["packages"]},
              "modules": receipts, "declarations": len(audit["rows"]),
              "theorems": sum(r["kind"] == "theorem" for r in audit["rows"]),
              "private_declarations": private_count,
              "actual_lean_ownership_and_axiom_controls": controls,
              "allowed_axioms": sorted(checks.ALLOWED_AXIOMS),
              "actual_axiom_report_sha256": checks.digest(report),
              "manifest_sha256": checks.digest(P / "MANIFEST.json")}
    (out / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
