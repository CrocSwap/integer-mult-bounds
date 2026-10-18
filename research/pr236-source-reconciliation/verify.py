#!/usr/bin/env python3
"""Reconcile PR236 sources with preserved receipts; never invoke Lean or Git.

Prepared by Will Richards with substantial OpenAI Codex assistance.
Apache-2.0. The pinned original parser is reused for source commands and logs.
"""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = "research/lean-paired-cube-d1d6"
AUDIT = "research/community-round9-audit"
ALLOWED = ["Classical.choice", "Quot.sound", "propext"]
POLICY = "maintainer-darwin-uncapped-subset-v1"


class ReconciliationError(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise ReconciliationError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def canonical(value):
    # Matches the original driver's summary binding, including its separators.
    return json.dumps(value, sort_keys=True).encode()


def same(actual, expected, message):
    # In particular, do not equate JSON false with 0 or true with 1.
    need(canonical(actual) == canonical(expected), message)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique_pairs)


def safe_name(name):
    path = PurePosixPath(name)
    need(name and name != "." and not path.is_absolute() and ".." not in path.parts
         and "\\" not in name and path.as_posix() == name,
         "Unsafe or noncanonical path: " + name)
    return name


def read_archive(raw):
    """Inspect bytes in memory: no extraction, links, duplicate names or execution."""
    result = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        for member in archive:
            name = safe_name(member.name)
            need(member.isfile() and name not in result,
                 "Non-file or duplicate archive member: " + name)
            result[name] = archive.extractfile(member).read()
    return result


def pinned_files(pins):
    result = {}
    for name, pin in pins["files"].items():
        path = ROOT / safe_name(name)
        need(path.resolve().is_relative_to(ROOT) and path.is_file(), "Missing pinned file: " + name)
        raw = path.read_bytes()
        same({"sha256": digest(raw), "git_blob": blob(raw), "bytes": len(raw)},
             {k: pin[k] for k in ("sha256", "git_blob", "bytes")}, "Pinned bytes changed: " + name)
        result[name] = raw
    actual = {p.relative_to(ROOT).as_posix() for p in (ROOT / PACKAGE).rglob("*")
              if p.is_file()}
    expected = {name for name in result if name.startswith(PACKAGE + "/")}
    same(sorted(actual), sorted(expected), "Standalone package inventory differs")
    return result


def load_parser(files):
    # Execute the exact bytes already pinned, without rereading or writing pyc files.
    name = PACKAGE + "/offline_check.py"
    parser = ModuleType("pr236_original_parser")
    parser.__file__ = str(ROOT / name)
    exec(compile(files[name], parser.__file__, "exec"), parser.__dict__)
    return parser


def check_sources(plan, sources, pins, files, parser):
    modules = {}
    expected = {}
    for record in plan["modules"]:
        name, source = record["module"], safe_name(record["source"])
        need(parser.NAME.fullmatch(name) and name not in modules and source not in expected,
             "Duplicate or invalid module/source: " + name)
        need(type(record["timeout_seconds"]) is int and record["timeout_seconds"] in (60, 120, 300),
             "Unexpected timeout: " + name)
        modules[name] = record
        expected[source] = record["source_sha256"]
    for item in plan["scientific_inputs"]:
        name = safe_name(item["path"])
        need(name not in expected, "Duplicate scientific path: " + name)
        expected[name] = item["sha256"]
    same(sorted(sources), sorted(expected), "Source archive coverage differs")
    for name, raw in sources.items():
        same(digest(raw), expected[name], "Source archive bytes differ: " + name)
    same(plan["target_commit"], pins["scientific_commit"], "Scientific commit differs")
    same(plan["axiom_policy"], ALLOWED, "Axiom policy differs")
    same(plan["compiler"], {"version": "4.21.0", "commit": "6741444a63ee"}, "Compiler contract differs")
    same(len(modules), plan["accepted_module_count"], "Module count differs")
    same(sum(m["declarations"] for m in modules.values()), plan["accepted_declarations"],
         "Declaration count differs")
    external = set(plan["external_imports"])
    need(all(n in ("Lean", "Init") or n.startswith(("Lean.", "Init.")) for n in external),
         "Non-core external dependency")
    seen = set()
    all_audits = set()
    same(sorted(plan["ordered_modules"]), sorted(modules), "Ordered module coverage differs")
    for name in plan["ordered_modules"]:
        m = modules[name]
        imports, prints = parser.source_commands(sources[m["source"]].decode("utf-8"))
        same(imports, m["imports"], "Source imports differ: " + name)
        same(prints, m["expected_axiom_commands"], "Source audit commands differ: " + name)
        need(len(prints) == len(set(prints)) == m["declarations"] and not all_audits.intersection(prints),
             "Duplicate or missing declaration: " + name)
        need(set(imports) <= seen | external, "Missing or out-of-order dependency: " + name)
        all_audits.update(prints)
        seen.add(name)
    same(sorted(pins["scientific_inputs"]), sorted(i["path"] for i in plan["scientific_inputs"]),
         "Scientific input pin coverage differs")
    for name, pin in pins["scientific_inputs"].items():
        same(blob(sources[name]), pin["git_blob"], "Scientific Git blob differs: " + name)
    mirrors = [name for name in files if name.startswith(PACKAGE + "/key_theorems/")]
    need(len(mirrors) == 6, "Principal theorem coverage differs")
    for name in mirrors:
        same(digest(files[name]), digest(sources["src/" + Path(name).name]), "Theorem mirror differs: " + name)
    sums = {}
    for line in files[PACKAGE + "/SHA256SUMS"].decode().splitlines():
        sha, name = line.split()
        need(name not in sums, "Duplicate checksum entry")
        sums[name] = sha
    same(sorted(sums), sorted(n[len(PACKAGE) + 1:] for n in files
                             if n.startswith(PACKAGE + "/") and not n.endswith("/SHA256SUMS")),
         "Original checksum coverage differs")
    for name, sha in sums.items():
        same(digest(files[PACKAGE + "/" + name]), sha, "Original checksum differs: " + name)
    return modules


def check_receipts(plan, evidence, parser):
    """Check relationships after archive pins, so mutants can exercise each link."""
    modules = {m["module"]: m for m in plan["modules"]}
    wanted = {"INPUT_MAP.json", "SUMMARY.json", "darwin-driver.py"}
    wanted.update("receipts/" + n + ".json" for n in modules)
    wanted.update("logs/" + n + ".log" for n in modules)
    same(sorted(evidence), sorted(wanted), "Evidence member coverage differs")
    same(decode(evidence["INPUT_MAP.json"]), plan, "Archived map differs")
    map_hash = digest(evidence["INPUT_MAP.json"])
    summary = decode(evidence["SUMMARY.json"])
    same(summary["status"], "FULL_ACCEPTED_SET_COMPILED", "Incomplete historical build")
    same([summary["kernel_compiled"], summary["full_accepted_set"]], [True, True], "Partial historical build")
    same(summary["source_commit"], plan["target_commit"], "Summary scientific commit differs")
    same(summary["map_sha256"], map_hash, "Summary map hash differs")
    same([summary["accepted_modules"], summary["selected_modules"], summary["selected_declarations"]],
         [len(modules), len(modules), plan["accepted_declarations"]], "Summary coverage differs")
    same(sorted(summary["rebuilt"] + summary["reused"]), sorted(modules), "Rebuilt/reused coverage differs")
    same(sorted(summary["receipts"]), sorted(modules), "Summary receipt coverage differs")
    done = {}
    declarations = axiom_free = edges = zero_audits = 0
    axioms = set()
    for name in plan["ordered_modules"]:
        m = modules[name]
        receipt = decode(evidence["receipts/" + name + ".json"])
        same([receipt["status"], receipt["compiler_exit"], receipt["module"], receipt["map_sha256_when_built"]],
             ["PASS", 0, name, map_hash], "Receipt identity/status differs: " + name)
        dependencies = {n: done[n]["object_sha256"] for n in m["imports"] if n in modules}
        key = dict(policy=POLICY, compiler=summary["compiler"], source_sha256=m["source_sha256"],
                   imports=m["imports"], expected_axiom_commands=m["expected_axiom_commands"],
                   dependencies=dependencies, timeout_seconds=m["timeout_seconds"],
                   address_space_bytes=None, lean_jobs=1, lean_stack_kib=65536, allowed_axioms=ALLOWED)
        same(receipt["build_key"], key, "Receipt source/dependency/policy differs: " + name)
        log = evidence["logs/" + name + ".log"]
        same(digest(log), receipt["log_sha256"], "Receipt log hash differs: " + name)
        audit = parser.audit_output(log.decode("utf-8"), m["expected_axiom_commands"])
        same(receipt["audit"], audit, "Receipt axiom audit differs: " + name)
        same(digest(canonical(receipt)), summary["receipts"][name], "Summary receipt binding differs: " + name)
        need(isinstance(receipt["object_sha256"], str) and len(receipt["object_sha256"]) == 64
             and all(c in "0123456789abcdef" for c in receipt["object_sha256"]), "Invalid recorded object hash")
        declarations += audit["declarations"]
        axiom_free += audit["axiom_free"]
        zero_audits += audit["declarations"] == 0
        edges += len(dependencies)
        axioms.update(audit["axioms"])
        done[name] = receipt
    same(declarations, plan["accepted_declarations"], "Total audit coverage differs")
    return dict(modules=len(modules), audited_declarations=declarations, axiom_free_declarations=axiom_free,
                modules_without_audit_commands=zero_audits, internal_dependency_edges=edges,
                observed_axioms=sorted(axioms), historical_rebuilt=len(summary["rebuilt"]),
                historical_reused=summary["reused"], compiler=summary["compiler"])


def rejection_controls(plan, evidence, parser):
    """Mutate in-memory evidence after outer pin checks; no fixture files written."""
    chosen = next(m for m in plan["modules"] if m["expected_axiom_commands"]
                  and any(n in plan["ordered_modules"] for n in m["imports"]))
    name = chosen["module"]
    key = "receipts/" + name + ".json"

    def receipt_mutant(change):
        mutant = dict(evidence)
        r = decode(mutant[key])
        change(r)
        mutant[key] = canonical(r)
        # Repair the outer summary binding to test the actual relationship.
        summary = decode(mutant["SUMMARY.json"])
        summary["receipts"][name] = digest(canonical(r))
        mutant["SUMMARY.json"] = canonical(summary)
        return mutant

    cases = {}
    cases["missing_receipt"] = {k: v for k, v in evidence.items() if k != key}
    cases["unexpected_receipt"] = dict(evidence, **{"receipts/Unaccepted.json": evidence[key]})
    changes = {
        "wrong_module": lambda r: r.update(module="Unaccepted"),
        "wrong_map": lambda r: r.update(map_sha256_when_built="0" * 64),
        "false_compiler_exit": lambda r: r.update(compiler_exit=False),
        "failed_compiler": lambda r: r.update(compiler_exit=1),
        "wrong_source": lambda r: r["build_key"].update(source_sha256="0" * 64),
        "invented_memory_cap": lambda r: r["build_key"].update(address_space_bytes=4 * 1024**3),
        "missing_dependency": lambda r: r["build_key"].update(dependencies={}),
        "wrong_dependency_object": lambda r: r["build_key"]["dependencies"].update(
            {next(iter(r["build_key"]["dependencies"])): "0" * 64}),
        "wrong_audit_total": lambda r: r["audit"].update(declarations=r["audit"]["declarations"] + 1),
    }
    cases.update({label: receipt_mutant(change) for label, change in changes.items()})
    for label, change in {
        "duplicate_rebuilt": lambda s: s["rebuilt"].append(s["rebuilt"][0]),
        "missing_rebuilt": lambda s: s["rebuilt"].pop(),
        "partial_build": lambda s: s.update(full_accepted_set=False),
    }.items():
        mutant = dict(evidence)
        summary = decode(mutant["SUMMARY.json"])
        change(summary)
        mutant["SUMMARY.json"] = canonical(summary)
        cases[label] = mutant
    for label, text in {
        "missing_audit": "",
        "duplicate_audit": evidence["logs/" + name + ".log"].decode() * 2,
        "unapproved_axiom": "\n".join("'" + n + "' depends on axioms: [sorryAx]"
                                      for n in chosen["expected_axiom_commands"]),
    }.items():
        raw = text.encode()
        mutant = receipt_mutant(lambda r: r.update(log_sha256=digest(raw)))
        mutant["logs/" + name + ".log"] = raw
        cases[label] = mutant
    rejected = []
    for label, mutant in sorted(cases.items()):
        try:
            check_receipts(plan, mutant, parser)
        except (ReconciliationError, parser.CheckError):
            rejected.append(label)
        else:
            raise ReconciliationError("Mutation accepted: " + label)
    return rejected


def verify():
    pins = decode((HERE / "SOURCE-PINS.json").read_bytes())
    files = pinned_files(pins)
    parser = load_parser(files)
    plan_raw = files[PACKAGE + "/INPUT_MAP.json"]
    plan = decode(plan_raw)
    sources = read_archive(files[PACKAGE + "/scientific_sources.tar.gz"])
    check_sources(plan, sources, pins, files, parser)
    archive_raw = files[AUDIT + "/pr236-kernel-evidence.tar.gz"]
    evidence = read_archive(archive_raw)
    manifest = decode(files[AUDIT + "/pr236-evidence-manifest.json"])
    same([len(archive_raw), digest(archive_raw), len(evidence), manifest["source_head"]],
         [manifest["archive_bytes"], manifest["archive_sha256"], manifest["files"], pins["source_head"]],
         "Evidence archive manifest differs")
    same({k: digest(v) for k, v in evidence.items()}, manifest["member_sha256"], "Evidence member hashes differ")
    same(evidence["INPUT_MAP.json"].decode(), plan_raw.decode(), "Archived source map bytes differ")
    for member, filename in [("SUMMARY.json", "pr236-full-summary.json"),
                             ("darwin-driver.py", "pr236-darwin-driver.py")]:
        same(digest(evidence[member]), digest(files[AUDIT + "/" + filename]), "Published evidence differs: " + member)
    driver = files[PACKAGE + "/offline_check.py"].decode()
    for before, after in [
        ('POLICY = "offline-lean-check-v1"', 'POLICY = "' + POLICY + '"'),
        ("address_space_bytes=4 * 1024**3", "address_space_bytes=None"),
        ("timeout=timeout, preexec_fn=lambda: resource.setrlimit(\n"
         "                                        resource.RLIMIT_AS, (4 * 1024**3, 4 * 1024**3)))", "timeout=timeout)"),
    ]:
        need(driver.count(before) == 1, "Unexpected Darwin adapter input")
        driver = driver.replace(before, after)
    same(digest(driver.encode()), digest(evidence["darwin-driver.py"]), "Darwin adapter has additional changes")
    stats = check_receipts(plan, evidence, parser)
    integrity = decode(files[AUDIT + "/pr236-final-integrity.json"])
    same([stats["modules"], stats["audited_declarations"], stats["axiom_free_declarations"],
          stats["observed_axioms"], stats["historical_rebuilt"], stats["historical_reused"], stats["compiler"]],
         [integrity["accepted_modules"], integrity["audited_declarations"], integrity["axiom_free_declarations"],
          integrity["observed_axioms"], integrity["rebuilt_modules"], integrity["reused_modules"], integrity["compiler"]],
         "Final integrity totals differ")
    same([integrity["map_sha256"], integrity["summary_sha256"], integrity["driver_sha256"], integrity["source_commit"]],
         [digest(plan_raw), digest(evidence["SUMMARY.json"]), digest(evidence["darwin-driver.py"]), plan["target_commit"]],
         "Final integrity pins differ")
    controls = rejection_controls(plan, evidence, parser)
    return dict(status="PASS_PR236_SOURCE_RECEIPT_RECONCILIATION", base_commit=pins["base_commit"],
                source_head=pins["source_head"], scientific_commit=pins["scientific_commit"],
                source_files=14, source_archive_members=len(sources), scientific_inputs=len(plan["scientific_inputs"]),
                principal_theorem_mirrors=6, evidence_archive_members=len(evidence),
                **stats, rejected_controls=controls, fresh_lean_compilation=False,
                compiled_object_bytes_available=False, compiler_binary_bytes_available=False,
                original_acceptance_manifest_available=False, recorded_object_hash_links_checked=True,
                recorded_address_space_bytes=None, selected_record_changed=False)


def main():
    result = verify()
    same(result, decode((HERE / "RESULT.json").read_bytes()), "Result differs from recorded reconciliation")
    print(result["status"], f"{result['modules']} modules, {result['audited_declarations']} audits, "
          f"{result['scientific_inputs']} scientific inputs, {len(result['rejected_controls'])} rejected controls")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, KeyError, OSError, tarfile.TarError) as exc:
        print("FAIL_PR236_SOURCE_RECEIPT_RECONCILIATION:", exc, file=sys.stderr)
        raise SystemExit(1)
