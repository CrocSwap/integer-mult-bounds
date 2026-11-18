#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Authenticate and replay the matched role-230 banked construction."""

import argparse
import gzip
from hashlib import sha1, sha256
import json
from pathlib import Path, PurePosixPath
import resource
import subprocess
import sys
from tempfile import TemporaryDirectory
import time


ROOT = Path(__file__).resolve().parent
BASE = "e54523517d0f03e58352e647c403a5af3e525a57"
PEER_HEAD = "28b2af322a1fab01b3734365988930920f9dda48"
SCIENCE = "26b6c469aa6c4aa04322ce25a22150f90e5fb14e"
SOURCE = "ee251f6005d2a92b887c5b804bd7aac05989d278b2c9ccb3c3091b50d533b08d"
PEER_GRAPH = "d81ec9f47740852a4bf7bd83100feff5cb66b70e1973466e1609bbac8af75098"
CANDIDATE_GRAPH = "1f082936ada08b5138b7d13e33368bd21c6f46632c5319a348e2f2a8e0021150"
CALLER = "62d94fb992acab0a71c3d12f22be4ce63f4f65e5cbe3f420b93aa1393ffa8dcf"
PIVOTS = "fb22afc8aaf543e62709fa682f222577e6bdf4e1f1994d307784468314c3da85"
PEER_RESULT = "00340c699fd7e2895d31a41d1eb60aebf91d7ba2c1c193dc002f69315298cd38"
WIRE_RESULT = "cde8b602d182ece20f55616decab1bf5c2b64e877770c20106afca44ff08752d"
INDEPENDENT_PRICE_PLAN = "509c44b078561a8868b68dab9f50b0b7d87d0976361d927bc8cc6bfdf1239393"
PEER_GRAPH_FILE = "PEER-GRAPH.json.gz"
CANDIDATE_GRAPH_FILE = "CANDIDATE-GRAPH.json.gz"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return sha256(raw).hexdigest()


def file(root, relative):
    name = PurePosixPath(relative)
    require(name.parts and not name.is_absolute() and ".." not in name.parts
            and name.as_posix() == relative, f"invalid asset path: {relative}")
    original = root.joinpath(*name.parts)
    require(original.resolve() == original and original.is_file(), f"missing or aliased asset: {relative}")
    return original


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def authenticate(root):
    manifest = read(file(root, "ASSETS.json"))
    comparator = manifest["comparator"]
    require(manifest["schema_version"] == 1 and manifest["base_commit"] == BASE
            and (comparator["pr"], comparator["head"], comparator["science"]) == (7674, PEER_HEAD, SCIENCE)
            and comparator["source_word"] == SOURCE and comparator["caller_sha256"] == CALLER,
            "exact matched source and caller")
    verified = {}
    for row in manifest["files"]:
        name = row["path"]
        require(name not in verified, f"duplicate asset: {name}")
        raw = file(root, name).read_bytes()
        require(len(raw) == row["bytes"] and digest(raw) == row["sha256"], f"asset bytes: {name}")
        if "git_blob" in row:
            blob = sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
            require(blob == row["git_blob"], f"upstream Git blob: {name}")
        verified[name] = row["sha256"]
    require(verified["peer/PIVOTS.json"] == comparator["pivot_sha256"] == PIVOTS
            and verified["peer/RESULT.json"] == comparator["published_receipt_sha256"] == PEER_RESULT
            and verified["evidence/WIRE-RESULT.json"] == WIRE_RESULT,
            "frozen peer inputs and actual completed graph receipt")
    actual_caller = gzip.decompress(file(root, "peer/source/caller.json.gz").read_bytes())
    require(digest(actual_caller) == CALLER, "literal decoded 16-call caller")
    return verified


def invoke(root, scratch, script, args, seconds):
    command = [sys.executable, "-I", "-B", "-X", f"pycache_prefix={scratch / 'fresh-bytecode'}",
               str(file(root, script)), *(str(arg) for arg in args)]
    subprocess.run(command, check=True, cwd=root, timeout=seconds)


def compare_reports(fresh, recorded, observed_fields=()):
    require({key: value for key, value in fresh.items() if key not in observed_fields}
            == {key: value for key, value in recorded.items() if key not in observed_fields},
            "fresh result matches every reproducible field")


def graph(root, out, materialize=False):
    original = root / "evidence/WIRE-RESULT.json"
    args = ["--peer-package", root / "peer", "--contacts-file", root / "data/CONTACTS.json", "--out", out]
    if materialize:
        args += ["--materialize-only", original]
    invoke(root, out, "engines/graph.py", args, 80 if materialize else 105)
    expected = read(original)
    result_path = out / ("MATERIALIZATION.json" if materialize else "RESULT.json")
    result = read(result_path)
    require(result["graphs"] == expected["graphs"], "frozen canonical and packed graph identities")
    for name, raw_pin in ((PEER_GRAPH_FILE, PEER_GRAPH), (CANDIDATE_GRAPH_FILE, CANDIDATE_GRAPH)):
        require(digest(gzip.decompress((out / name).read_bytes())) == raw_pin, f"canonical graph bytes: {name}")
    if materialize:
        require(result["status"] == "PASS_BANK24_MATERIALIZATION_ONLY" and result["exact_result_sha256"] == WIRE_RESULT,
                "materialized exact replay identities")
    else:
        compare_reports(result, expected, ("started_at", "completed_at", "start_sha256", "binding_sha256", "resource"))
        require(result["status"] == "PASS_BANK24_WIRE_COMMUTATION" and len(result["pivot_checks"]) == 15
                and result["exact_whole_graph_both_orders"] is True, "paired exact wire and unchanged pivot proof")
    return result


def paired(root, out):
    out.mkdir(exist_ok=False)
    graph_out = out / "graphs"
    wire = graph(root, graph_out)
    app_out = out / "application"
    invoke(root, out, "engines/application/verify.py", (
        "--package", root / "peer", "--engine-dir", root / "engines/frozen",
        "--parent-graph", graph_out / PEER_GRAPH_FILE, "--candidate-graph", graph_out / CANDIDATE_GRAPH_FILE,
        "--graph-receipt", root / "evidence/WIRE-RESULT.json", "--out", app_out
    ), 120)
    application = read(app_out / "RESULT.json")
    compare_reports(application, read(file(root, "evidence/APPLICATION-RESULT.json")))
    require(application["status"] == "PASS_BANK24_ACTUAL16_APPLICATION_COMPONENT", "full signed application status")
    physical_path = out / "PHYSICAL.json"
    invoke(root, out, "engines/check_banked_provider_cost.py", (
        "--binding", graph_out / "GRAPH-BINDING.json", "--peer-result", root / "peer/RESULT.json",
        "--caller", root / "peer/source/caller.json.gz", "--application-dir", app_out, "--out", physical_path
    ), 20)
    physical = read(physical_path)
    compare_reports(physical, read(file(root, "evidence/PROVIDER-RESULT.json")))
    price_path = out / "INDEPENDENT-PRICE.json"
    invoke(root, out, "engines/check_price.py", (
        "--invoices", app_out / "INVOICES.json", "--outer", app_out / "PRICE-OUTER.json",
        "--application", app_out / "RESULT.json", "--peer-result", root / "peer/RESULT.json",
        "--plan-sha256", INDEPENDENT_PRICE_PLAN, "--out", price_path
    ), 10)
    price = read(price_path)
    compare_reports(price, read(file(root, "evidence/INDEPENDENT-PRICE.json")))
    require(price["status"] == "PASS_BANK24_REVIEW_INDEPENDENT_DIRECTED_PRICE", "bounded independent signed margins")
    result = {"status": "PASS_ROLE230_BANKED_PAIRED_APPLICATION", "source_graph": PEER_GRAPH,
              "candidate_graph": CANDIDATE_GRAPH, "caller_sha256": CALLER,
              "candidate_conditional_lower": application["candidate_directed_conditional_lower"],
              "paired_wire_exact": wire["exact_whole_graph_both_orders"],
              "artifacts": {str(path.relative_to(out)): digest(path.read_bytes()) for path in
                            (graph_out / "RESULT.json", app_out / "RESULT.json", physical_path, price_path)}}
    write(out / "RESULT.json", result)
    return result


def native(root, out):
    out.mkdir(exist_ok=False)
    deadline = time.monotonic() + 385
    graph_out = out / "graphs"
    graph(root, graph_out, materialize=True)

    def run(script, args, seconds):
        remaining = deadline - time.monotonic()
        require(remaining > 0, "paired native replay deadline")
        invoke(root, out, "engines/native/" + script + ".py", args, min(seconds, remaining))

    common = ("--peer-package", root / "peer", "--engine-dir", root / "engines/frozen", "--graphs", graph_out)
    phase_out = out / "phase"
    run("bank_phase", (*common, "--custody", root / "engines/native/MAP-CUSTODY.json.gz",
                       "--expect-peer", PEER_GRAPH, "--expect-child", CANDIDATE_GRAPH, "--out", phase_out), 85)
    phase_path = phase_out / "RESULT.json"
    phase = read(phase_path)
    compare_reports(phase, read(file(root, "evidence/PHASE-RESULT.json")), ("complete_at", "artifact_sha256"))
    require(phase["status"] == "PASS_PAIRED_BANK24_EXACT_NATIVE_MAPS", "complete paired native phase catalogue")
    for name, pin in phase["artifact_sha256"].items():
        require(digest(file(phase_out, name).read_bytes()) == pin, f"fresh phase artifact: {name}")
    records = {}
    for prime in (1000000009, 998244353):
        dense_out = out / f"dense-{prime}"
        run("bank_dense", (*common, "--field-engine", root / "engines/frozen/field_interpreter.py",
                           "--phase", phase_out, "--prime", prime, "--out", dense_out),
            115 if prime == 1000000009 else 85)
        path = dense_out / "RESULT.json"
        report = read(path)
        observed = ("observed_at", "completed_at", "phase_sha256")
        compare_reports(report, read(file(root, f"evidence/DENSE-{prime}.json")), observed)
        require(report["status"] == "PASS_PAIRED_BANK24_ACTUAL_HELD_ARRAYS"
                and report["phase_sha256"] == digest(phase_path.read_bytes()), "native dense result and fresh phase binding")
        controls = report["actual_negative_controls"]
        if prime == 1000000009:
            require(set(controls) == {"quarter phase", "same-price sign"}
                    and all(len(set(control["changed_public_roles"])) == 53 for control in controls.values()),
                    "both actual first-prime fault controls affect 53 distinct public roles")
        else:
            require(not controls, "second prime replays the unmodified graph")
        records[str(prime)] = digest(path.read_bytes())
    sealed_path = out / "NATIVE-COMPONENT.json"
    run("bank_complete", ("--phase", phase_out, "--dense-first", out / "dense-1000000009",
                           "--dense-second", out / "dense-998244353", "--out", sealed_path), 10)
    sealed = read(sealed_path)
    expected = read(file(root, "evidence/NATIVE-RESULT.json"))
    compare_reports(sealed, expected, ("phase_sha256", "dense"))
    require(sealed["status"] == "PASS_PAIRED_BANK24_NATIVE_QUALIFICATION_COMPONENT",
            "complete native exact and held-array comparison")
    result = {"status": "PASS_ROLE230_BANKED_PAIRED_NATIVE", "source_graph": PEER_GRAPH,
              "candidate_graph": CANDIDATE_GRAPH, "caller_sha256": CALLER,
              "phase_result_sha256": digest(phase_path.read_bytes()), "dense_result_sha256": records,
              "sealed_native_component_sha256": digest(sealed_path.read_bytes())}
    write(out / "RESULT.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("integrity", "graph", "paired", "native"))
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    require(sys.version_info[:2] == (3, 12) and sys.flags.isolated and sys.dont_write_bytecode and __debug__,
            "use Python 3.12 -I -B with assertions")
    authenticated = authenticate(ROOT)
    if args.stage == "integrity":
        require(args.out is None, "integrity uses read-only inputs")
        print(json.dumps({"status": "PASS_BANK24_CAPSULE_INTEGRITY", "assets": len(authenticated)}))
        return
    bound = 2 * 1024**3
    resource.setrlimit(resource.RLIMIT_AS, (bound, bound))
    stage = {"graph": graph, "paired": paired, "native": native}[args.stage]
    if args.out is None:
        with TemporaryDirectory(prefix="p104-banked-") as scratch:
            result = stage(ROOT, Path(scratch) / "replay")
    else:
        result = stage(ROOT, args.out.resolve())
    require(authenticated == authenticate(ROOT), "source bytes throughout replay")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
