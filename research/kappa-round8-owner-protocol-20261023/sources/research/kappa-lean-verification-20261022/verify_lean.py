"""Replay scoped Lean proofs and bind their inputs, logs and compiled outputs.

Default: fresh sequential compilation. Explicit evidence reuse is source-bound,
not an independent attestation. Apache-2.0; substantial OpenAI Codex assistance.
Prepared for Cao Yifan. Requires the repository's global Python 3.14.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import gzip
from hashlib import sha1, sha256
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MATHLIB = "308445d7985027f538e281e18df29ca16ede2ba3"
PAYLOAD = "4409d2d9328fffbd276bb03fb800f59a33ec3b2ab15f79a330a7af66e75110cc"
ALLOW = {"propext", "Classical.choice", "Quot.sound"}
ROOTS = ["Native", "AnalyticGain", "NumericalMoments", "CompilerCapacity",
         "ArithmeticCertificate", "KappaWarpVerification"]
GENERATORS = {
    "native_generate.py": None,
    "numerical_generate.py": {"NumericalMoments.lean"},
    "generate_arithmetic.py": {"ArithmeticCertificate.lean", "ARITHMETIC-TRANSCRIPTION.json"},
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith(".gz") else raw)


def relative(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def local_path(name):
    path = (HERE / name).resolve()
    need(path.is_relative_to(HERE), "Evidence path leaves the Lean package")
    return path


def capture(argv, *, cwd=HERE, env=None):
    result = subprocess.run(argv, cwd=cwd, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, check=False)
    need(result.returncode == 0, "Command failed: " + str(argv[0]) + "\n" +
         result.stdout.decode("utf-8", errors="replace")[:2000])
    return result.stdout.decode("utf-8").strip()


def strip_lean(text):
    """Remove nested comments and string contents, preserving line numbers."""
    out = []; i = 0; depth = 0; string = False
    while i < len(text):
        if depth:
            if text.startswith("/-", i): depth += 1; out.extend("  "); i += 2
            elif text.startswith("-/", i): depth -= 1; out.extend("  "); i += 2
            else: out.append("\n" if text[i] == "\n" else " "); i += 1
        elif string:
            if text[i] == "\\" and i + 1 < len(text): out.extend("  "); i += 2
            elif text[i] == '"': string = False; out.append(" "); i += 1
            else: out.append("\n" if text[i] == "\n" else " "); i += 1
        elif text.startswith("/-", i): depth = 1; out.extend("  "); i += 2
        elif text.startswith("--", i):
            end = text.find("\n", i)
            if end < 0: end = len(text)
            out.extend(" " * (end-i)); i = end
        elif text[i] == '"': string = True; out.append(" "); i += 1
        else: out.append(text[i]); i += 1
    need(depth == 0 and not string, "Unterminated Lean comment/string in source audit")
    return "".join(out)


def audit_source(path):
    code = strip_lean(path.read_text(encoding="utf-8"))
    forbidden = re.search(r"\b(?:sorry|admit|axiom|native_decide|ofReduceBool|skipKernelTC|trustCompiler)\b", code)
    need(forbidden is None, "Forbidden proof shortcut in " + path.name)
    return re.findall(r"(?m)^\s*#print\s+axioms\s+([A-Za-z0-9_.]+)\s*$", code)


def imports(module):
    path = local_path(module.replace(".", "/") + ".lean")
    need(path.is_file(), "Missing local module: " + module)
    code = strip_lean(path.read_text(encoding="utf-8"))
    result = []
    for line in code.splitlines():
        if line.strip().startswith("import "):
            for name in line.strip().split()[1:]:
                candidate = HERE / (name.replace(".", "/") + ".lean")
                if candidate.is_file(): result.append(name)
                else: need(name == "Std" or name.startswith(("Std.", "Mathlib.")),
                           "Unexpected external import: " + name)
    return result


def order(roots):
    result = []; visiting = set(); done = set()
    def visit(module):
        if module in done: return
        need(module not in visiting, "Cyclic local imports")
        visiting.add(module)
        for dependency in imports(module): visit(dependency)
        visiting.remove(module); done.add(module); result.append(module)
    for root in roots: visit(root)
    return result


def parse_axioms(log, expected):
    text = Path(log).read_text(encoding="utf-8-sig")
    need("sorryAx" not in text and "declaration uses 'sorry'" not in text,
         "Sorry dependency in " + Path(log).name)
    need(re.search(r"(?m)^.*:\d+:\d+: error:", text) is None,
         "Lean error diagnostic in " + Path(log).name)
    rows = []
    pattern = r"'([^']+)'\s+(?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)"
    for match in re.finditer(pattern, text):
        axioms = [a.strip() for a in (match.group(2) or "").split(",") if a.strip()]
        need(set(axioms) <= ALLOW, "Unexpected axioms for " + match.group(1))
        rows.append({"theorem": match.group(1), "axioms": axioms})
    need(len(rows) == len(expected), "Missing/extra axiom reports in " + Path(log).name)
    for declared, row in zip(expected, rows):
        actual = row["theorem"]
        need(actual == declared or actual.endswith("." + declared),
             "Axiom report names differ from source in " + Path(log).name)
    return rows


def numerical_binding(arithmetic, native):
    tested = Fraction(302153, 100000000)
    kappa = Fraction(37769, 12500000)
    need(Fraction(arithmetic["strictification"]["tested"]) == tested, "Exact tested saving drifted")
    need(Fraction(arithmetic["kappa"]) == kappa, "Exact claimed saving drifted")
    def module(path, name):
        spec = importlib.util.spec_from_file_location(name, path)
        result = importlib.util.module_from_spec(spec); sys.modules[name] = result
        spec.loader.exec_module(result)
        return result
    generator = module(HERE / "numerical_generate.py", "lean_checked_numerical_generator")
    need(generator.TEST == tested, "Numerical generator TEST differs from the admitted saving")
    price = module(ROOT / "research/kappa-interface-round2-20261022/price_profile.py", "lean_checked_price_profile")
    helpers, local_paid, targets, paid, _ = price.assemble(native)
    ints = lambda d: {int(k): int(v) for k, v in d.items()}
    need(dict(helpers) == ints(arithmetic["local_helpers"]), "Actual helper/controller binding")
    need(dict(local_paid) == ints(arithmetic["local_paid"]), "Actual local paid/controller binding")
    need(dict(targets) == ints(arithmetic["targets"]) and dict(paid) == ints(arithmetic["paid"]),
         "Complete target/paid JSON differs from freshly assembled native/controller ledger")
    code = strip_lean((HERE / "NumericalMoments.lean").read_text(encoding="utf-8"))
    term = re.compile(r"\s*(\d+)\s*\*\s*\((\d+)\s*:\s*ℝ\)\s*\^\s*t\s*")
    for name, actual in (("targetMoment", targets), ("paidMoment", paid)):
        definitions = re.findall(r"noncomputable\s+def\s+" + name +
            r"\s*\(t\s*:\s*ℝ\)\s*:\s*ℝ\s*:=\s*\n(.*?)(?=\n\s*\n)", code, re.S)
        need(len(definitions) == 1, "Expected one bounded literal numerical definition: " + name)
        coefficients = {}
        for piece in definitions[0].split("+"):
            match = term.fullmatch(piece)
            need(match is not None, "Unexpected numerical polynomial syntax: " + name)
            count, rank = map(int, match.groups())
            need(count > 0 and rank > 0 and rank not in coefficients, "Extra/duplicate numerical coefficient: " + name)
            coefficients[rank] = count
        need(coefficients == dict(actual), "Lean numerical coefficients differ from actual complete ledger: " + name)
    return {"tested": str(tested), "kappa": str(kappa),
            "targets": dict(targets), "paid": dict(paid), "assembled_from_actual_native_controller": True,
            "lean_literal_coefficients_equal": True, "generator_TEST_equal": True}


def authenticate_inputs():
    native = ROOT / "research/warp-interface-20261022"
    frozen = read(native / "ACTUAL-WORD-FREEZE.json")
    raw = (native / "ACTUAL-WORD.json.gz").read_bytes()
    need(sha256(gzip.decompress(raw)).hexdigest() == PAYLOAD == frozen["canonical_payload_sha256"],
         "Wrong frozen native canonical payload")
    need(sha256(raw).hexdigest() == frozen["compressed_sha256"], "Immutable input archive differs")
    paths = {native / n for n in ("ACTUAL-WORD.json.gz", "ACTUAL-WORD-FREEZE.json",
             "SOURCES.json", "NATIVE-VALIDATION.json", "PHASE-VALIDATION.json.gz")}
    for name, want in frozen["discovery_sha256"].items():
        path = native / name
        need(digest(path) == want, "Frozen discovery pin differs: " + name)
        paths.add(path)
    pins = read(native / "SOURCES.json")
    for row in pins["files"]:
        path = ROOT / row["path"]; b = path.read_bytes()
        need(sha256(b).hexdigest() == row["sha256"], "Inherited input pin differs: " + row["path"])
        if "git_blob" in row:
            blob = sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
            need(blob == row["git_blob"], "Inherited Git blob differs: " + row["path"])
        paths.add(path)
    arithmetic_path = ROOT / "research/kappa-interface-round2-20261022/ARITHMETIC.json"
    arithmetic = read(arithmetic_path); paths.add(arithmetic_path)
    for name, want in arithmetic["source_sha256"].items():
        path = ROOT / name
        need(digest(path) == want, "Arithmetic source pin differs: " + name)
        paths.add(path)
    receipt = read(native / "NATIVE-VALIDATION.json")
    phase = read(native / "PHASE-VALIDATION.json.gz")
    need(receipt["status"] == "PASS_CHANGED_G_NATIVE_BOTH_632_COLUMN_INTERPRETERS", "Native admission receipt")
    need(phase["status"] == "PASS_ALL_ACTUAL_WARP_AND_NEW_PAID_ABSOLUTE_PHASES", "Physical admission receipt")
    need(arithmetic["native_receipt_sha256"] == digest(native / "NATIVE-VALIDATION.json"), "Arithmetic/native receipt link")
    need(arithmetic["local_paid"] == receipt["paid"] and arithmetic["local_helpers"] == receipt["helpers"],
         "Actual native lists feed the arithmetic")
    need(phase["actual_word_canonical_sha256"] == PAYLOAD, "Phase receipt payload binding")
    need(phase["source_manifest_sha256"] == digest(native / "SOURCES.json"), "Phase receipt source-manifest binding")
    session_path = ROOT / "research/kappa-interface-round2-20261022/SESSION-VERIFICATION.json"
    session = read(session_path); paths.add(session_path)
    need(session["status"] == "PASS_CONDITIONAL_CHANGED_MAP_KAPPA_00302152", "Complete Python replay receipt")
    for name, want in session["outputs_sha256"].items():
        path = ROOT / name
        need(digest(path) == want, "Python replay output binding: " + name)
        paths.add(path)
    for row in session["gates"]:
        path = session_path.parent / row["log"]
        need(row["exit_code"] == 0 and digest(path) == row["sha256"], "Python replay gate log")
        paths.add(path)
    numerical = numerical_binding(arithmetic, receipt)
    return {relative(p): digest(p) for p in sorted(paths)}, numerical


def check_generators():
    base = HERE / ".lake/verification-transcriptions"
    base.mkdir(parents=True, exist_ok=True)
    runner = ("import importlib.util,sys;from pathlib import Path;"
              "s=importlib.util.spec_from_file_location('checked_generator',sys.argv[1]);"
              "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
              "m.HERE=Path(sys.argv[2]);m.main()")
    records = []
    for name, wanted in GENERATORS.items():
        generator = HERE / name
        with tempfile.TemporaryDirectory(prefix="transcription-", dir=base) as directory:
            temp = Path(directory).resolve()
            need(temp.is_relative_to(base.resolve()), "Temporary generator directory escaped workspace")
            result = subprocess.run([sys.executable, "-B", "-c", runner, str(generator), str(temp)],
                                    cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
            need(result.returncode == 0, "Generator failed: " + name + "\n" +
                 result.stdout.decode("utf-8", errors="replace")[:2000])
            outputs = sorted(p.name for p in temp.iterdir() if p.is_file())
            if wanted is not None: need(set(outputs) == wanted, "Generator output inventory: " + name)
            else: need(outputs and all(n.startswith("Native") and n.endswith(".lean") for n in outputs),
                       "Native generator output inventory")
            hashes = {}
            for output in outputs:
                actual = HERE / output
                need(actual.is_file() and actual.read_bytes() == (temp / output).read_bytes(),
                     "Regenerated source differs: " + output)
                hashes[output] = digest(actual)
            records.append({"generator": name, "source_sha256": digest(generator),
                            "exit_code": result.returncode, "outputs_sha256": hashes,
                            "stdout_sha256": sha256(result.stdout).hexdigest()})
    return records


def environment(lake):
    need((HERE / "lean-toolchain").read_text().strip() == "leanprover/lean4:v4.21.0", "Lean toolchain pin")
    config = tomllib.loads((HERE / "lakefile.toml").read_text())
    requirement = next(r for r in config["require"] if r["name"] == "mathlib")
    need(requirement["rev"] == MATHLIB, "Lake mathlib revision pin")
    manifest = read(HERE / "lake-manifest.json")
    packages = []
    for package in manifest["packages"]:
        path = HERE / manifest["packagesDir"] / package["name"]
        head = capture(["git", "-C", str(path), "rev-parse", "HEAD"])
        need(head == package["rev"], "Dependency checkout revision: " + package["name"])
        dirty = subprocess.run(["git", "-C", str(path), "diff", "HEAD", "--quiet"],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        need(dirty.returncode == 0, "Modified tracked dependency source: " + package["name"])
        packages.append({"name": package["name"], "revision": head})
    need(any(p == {"name": "mathlib", "revision": MATHLIB} for p in packages), "Mathlib checkout pin")
    probe = "import json,os;print(json.dumps({k:os.environ.get(k,'') for k in ['PATH','LEAN_PATH']}))"
    values = json.loads(capture([lake, "env", sys.executable, "-B", "-c", probe]))
    env = dict(os.environ); env.update(values)
    env["LEAN_PATH"] = str(HERE) + (os.pathsep + values["LEAN_PATH"] if values["LEAN_PATH"] else "")
    lean = shutil.which("lean", path=values["PATH"])
    need(lean is not None, "Lean executable unavailable through lake env")
    version = capture([lean, "--version"], env=env)
    need("version 4.21.0," in version and "6741444a63ee" in version, "Unexpected Lean release")
    return lean, env, {"lean_version": version, "lean_executable_sha256": digest(lean),
                       "mathlib_revision": MATHLIB, "dependencies": packages}


def load_evidence(names, runtime):
    found = {}; receipts = []
    for name in names:
        path = local_path(name); evidence = read(path)
        version = evidence.get("lean_version", evidence.get("lean", ""))
        if version == "4.21.0":
            need(evidence.get("lean_commit") == "6741444a63ee", "Evidence Lean commit")
        else: need(version == runtime["lean_version"], "Evidence Lean version")
        need(evidence.get("mathlib_revision", evidence.get("mathlib_commit")) == MATHLIB, "Evidence mathlib pin")
        if "canonical_payload_sha256" in evidence: need(evidence["canonical_payload_sha256"] == PAYLOAD, "Evidence payload pin")
        if "generation_source_sha256" in evidence:
            need(evidence["generation_source_sha256"] == digest(HERE / "native_generate.py"), "Evidence native generator pin")
        for row in evidence["modules"]:
            module = row["module"]
            need(re.fullmatch(r"[A-Za-z][A-Za-z0-9_.]*", module) is not None, "Invalid evidence module")
            row = dict(row)
            row.setdefault("source", module.replace(".", "/") + ".lean")
            row.setdefault("olean", module.replace(".", "/") + ".olean")
            need(row.get("exit_code") == 0, "Failed module cannot be reused: " + module)
            for kind in ("source", "olean", "log"):
                target = local_path(row[kind])
                need(target.is_file() and digest(target) == row[kind + "_sha256"],
                     "Reused " + kind + " hash differs: " + module)
            need(local_path(row["source"]) == local_path(module.replace(".", "/") + ".lean"), "Evidence source/module mismatch")
            need(local_path(row["olean"]) == local_path(module.replace(".", "/") + ".olean"), "Evidence output/module mismatch")
            argv = row.get("argv", row.get("command"))
            need(isinstance(argv, list) and "-o" in argv and any(str(a).endswith(row["source"]) for a in argv),
                 "Evidence lacks a source-to-olean compile command")
            need(not any(re.search(r"skipKernelTC|ofReduceBool|trustCompiler|native_decide", str(a)) for a in argv),
                 "Evidence uses a compiler/kernel trust bypass")
            need(str(argv[argv.index("-o") + 1]).endswith(row["olean"]), "Evidence compiled another output")
            row["axioms"] = parse_axioms(local_path(row["log"]), audit_source(local_path(row["source"])))
            row["evidence"] = path.name
            if module in found:
                need(all(found[module][k] == row[k] for k in ("source_sha256", "olean_sha256", "log_sha256")),
                     "Conflicting reused module receipts: " + module)
            found[module] = row
        receipts.append({"path": path.name, "sha256": digest(path)})
    return found, receipts


def write_receipt(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lake", default="lake", help="Lake command/path; version is independently checked")
    parser.add_argument("--reuse-evidence", action="append", default=[], metavar="RECEIPT.json",
                        help="Explicitly validate/reuse genuine module logs and oleans; repeatable")
    parser.add_argument("--reuse-only", action="store_true", help="Fail rather than compile any missing module")
    parser.add_argument("--only", nargs="+", metavar="MODULE", help="Partial dependency-closed replay; not full verification")
    parser.add_argument("--check-inputs", action="store_true", help="Authenticate/transcribe only; proves no Lean result")
    parser.add_argument("--timeout", type=int, default=1800, help="Seconds allowed per Lean module (default: 1800)")
    parser.add_argument("--stack-kb", type=int, default=65536, help="Lean worker stack size")
    parser.add_argument("--receipt", default="LEAN-VERIFICATION.json", help="Package-relative output receipt")
    args = parser.parse_args()
    need(sys.version_info[:2] == (3, 14), "Use the repository's global Python 3.14")
    need(args.timeout > 0 and args.stack_kb > 0, "Positive timeout and stack required")
    receipt_path = local_path(args.receipt)
    need(all(local_path(name) != receipt_path for name in args.reuse_evidence),
         "Choose a different --receipt when reusing that same receipt as evidence")
    if not args.check_inputs:
        write_receipt(receipt_path, {"schema_version": 1, "status": "CHECKING_INPUTS"})
    try:
        bindings, numerical = authenticate_inputs()
        generated = check_generators()
        source_files = sorted(HERE.glob("*.lean"))
        expected = {p.stem: audit_source(p) for p in source_files}
        sources = {p.name: digest(p) for p in source_files}
        lean, env, runtime = environment(args.lake)
        if args.check_inputs:
            print("PASS_INPUT_BINDINGS_ONLY", len(sources), "Lean sources", flush=True)
            return
        selected = args.only or ROOTS
        modules = order(selected)
        evidence, evidence_files = load_evidence(args.reuse_evidence, runtime)
        need(not args.reuse_only or set(modules) <= evidence.keys(), "Missing evidence for --reuse-only")
    except Exception as exc:
        if not args.check_inputs:
            write_receipt(receipt_path, {"schema_version": 1, "status": "FAIL_INPUT_BINDINGS", "error": str(exc)})
        raise
    data = {"schema_version": 1, "status": "RUNNING", "started_utc": datetime.now(timezone.utc).isoformat(),
            "mode": "explicit-evidence-reuse" if args.reuse_evidence else "fresh",
            "python_version": sys.version, "runtime": runtime, **runtime,
            "canonical_payload_sha256": PAYLOAD, "allowed_axioms": sorted(ALLOW),
            "input_sha256": bindings, "lean_source_sha256": sources,
            "numerical_profile_binding": numerical,
            "verification_script_sha256": digest(Path(__file__)),
            "configuration_sha256": {n: digest(HERE/n) for n in ("lean-toolchain", "lakefile.toml", "lake-manifest.json")},
            "transcriptions": generated, "reused_receipts": evidence_files, "module_order": modules, "modules": [],
            "scope": "Scoped native frame/invoice, real moment/tail/capacity and rational compiler/outer proofs. No amplitudes/phases/free-group endpoint or end-to-end multiplication theorem."}
    write_receipt(receipt_path, data)
    completed = {}
    try:
        for module in modules:
            source = local_path(module.replace(".", "/") + ".lean")
            dependencies = order(imports(module))
            dep_hashes = {d: completed[d]["olean_sha256"] for d in dependencies}
            if module in evidence:
                row = evidence[module]
                for dependency in dependencies:
                    need(dependency in evidence, "Reused module lacks imported-module evidence: " + dependency)
                    need(evidence[dependency]["olean_sha256"] == dep_hashes[dependency],
                         "Reused module's dependency changed: " + dependency)
                row = {"module": module, "source": source.name, "source_sha256": digest(source),
                       "olean": row["olean"], "olean_sha256": row["olean_sha256"],
                       "log": row["log"], "log_sha256": row["log_sha256"],
                       "argv": ["lean", "-o", row["olean"], source.name], "exit_code": 0,
                       "axioms": row["axioms"], "mode": "reused", "evidence": row["evidence"],
                       "dependency_olean_sha256": dep_hashes}
                print("REUSE_VALIDATED", module, flush=True)
            else:
                output = source.with_suffix(".olean"); log = source.with_suffix(".log")
                argv = [lean, "-s", str(args.stack_kb), "-o", output.name, source.name]
                print("COMPILE", module, flush=True); started = time.monotonic()
                with log.open("wb") as stream:
                    result = subprocess.run(argv, cwd=HERE, env=env, stdout=stream, stderr=subprocess.STDOUT,
                                            timeout=args.timeout, check=False)
                row = {"module": module, "source": source.name, "source_sha256": digest(source),
                       "olean": output.name, "log": log.name, "log_sha256": digest(log),
                       "argv": ["lean", *argv[1:]], "exit_code": result.returncode,
                       "seconds": time.monotonic()-started, "mode": "fresh",
                       "dependency_olean_sha256": dep_hashes}
                need(result.returncode == 0 and output.is_file(), "Lean compile failed: " + module + "; see " + log.name)
                row["olean_sha256"] = digest(output)
                row["axioms"] = parse_axioms(log, expected[module])
                print("PASS", module, "axiom_reports", len(row["axioms"]), flush=True)
            need(row["source_sha256"] == sources[source.name], "Source changed during replay: " + module)
            completed[module] = row; data["modules"].append(row); write_receipt(receipt_path, data)
        need({p.name: digest(p) for p in source_files} == sources, "Lean source changed during replay")
        need(authenticate_inputs() == (bindings, numerical), "External input changed during replay")
        for item in generated:
            need(digest(HERE/item["generator"]) == item["source_sha256"], "Generator changed during replay")
        data["status"] = "PASS_PARTIAL_LEAN_REPLAY" if args.only else "PASS_SCOPED_LEAN_REPLAY"
        data["completed_utc"] = datetime.now(timezone.utc).isoformat()
        write_receipt(receipt_path, data)
        print(data["status"], len(modules), "modules", flush=True)
    except Exception as exc:
        data["status"] = "FAIL_LEAN_REPLAY"; data["error"] = str(exc)
        write_receipt(receipt_path, data)
        raise


if __name__ == "__main__":
    main()
