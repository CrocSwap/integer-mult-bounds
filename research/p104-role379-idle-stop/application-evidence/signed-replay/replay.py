#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay the signed #7113 application on the pinned #7658 role-379 word."""

import argparse
from copy import deepcopy
import gzip
from hashlib import sha1, sha256
from io import BytesIO
import json
import os
from pathlib import Path, PurePosixPath
import runpy
import subprocess
import sys
import tarfile
import tempfile


HERE = Path(__file__).resolve().parent
PRIORDIR = "kappa-7641-successor-20261118"
HEAD = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
FREEZE = "ac57680f5a9c2ba97840b3b5bd10f1b7b77db1fe20d54e6197a1e18c08842045"
DRIVERS = {"engines.py", "guard.py", "native_ingredient.py", "run.py"}
SPEC_INPUTS = {
    "clear_result", "grid", "independent_pair", "native_adapter", "native_launcher",
    "native_physical", "native_receipt", "native_result", "native_start", "native_stderr",
    "native_stdout", "native_time", "ordinary", "source_invoice", "source_word", "word",
}
SHORT_CALLER = "caller/replay/supplier7112/short-caller"
VENDOR_SHORT_CALLER = ("interval_gate.py", "check_odd_fixed_tape_counts.py")
PRICING = {
    "evaluate_recursive_power.py": "52b20f41fd0bb55fa88dccd6015af2ce358917817b9506720f3e60ce681cc3ad",
    "compare_recursive_invoices.py": "3930c22c11da7bc6042cfeb6e459ecb06e4478430037bee3469d034353855fc6",
}
NATIVE_WORD = "f0753b6614b2d351723dddc307a39b6ecd748a43008c6fdb9335b01feeec9669"
NATIVE_TRANSPORT = "4e9cd9cc70a5423db44f870b35d8d6da9ac5746aa352f3af1420443f6dda350e"


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(raw):
    return sha256(raw).hexdigest()


def git_blob(raw):
    return sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def read(path, pin=None):
    raw = path.read_bytes()
    require(pin is None or digest(raw) == pin, f"byte pin {path.name}")
    return raw


def load(path, pin=None):
    return json.loads(read(path, pin))


def write(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as out:
        out.write(raw)


def write_json(path, obj):
    write(path, (json.dumps(obj, sort_keys=True, indent=2) + "\n").encode())


def relative(name):
    p = PurePosixPath(name)
    require(not p.is_absolute() and ".." not in p.parts and p.parts and p.as_posix() == name,
            f"invalid relative input {name!r}")
    return p


def bound_path(root, name):
    p = root / relative(name)
    require(p.is_file() and p.resolve() == p, f"missing or aliased input {name}")
    return p


def materialize(root, core):
    """Authenticate the exact source inventory and restore the driver's relative layout."""
    sources = load(HERE / "data/SOURCE-CLOSURE.json")
    members = sources["members"]
    require(sources["schema_version"] == 1 and sources["caller_pr"] == 7113
            and sources["caller_head"] == HEAD and sources["prior_freeze_sha256"] == FREEZE,
            "source manifest and caller head")
    archive = read(HERE / "data/caller-closure.tar.gz", sources["archive_sha256"])
    validated = {}
    with tarfile.open(fileobj=BytesIO(archive), mode="r:gz") as packed:
        for entry in packed:
            name = entry.name
            relative(name)
            require(entry.isfile() and name in members and name not in validated,
                    f"unexpected archive entry {name}")
            record = members[name]
            require(entry.size == record["bytes"], f"archive size {name}")
            raw = packed.extractfile(entry).read()
            require(digest(raw) == record["sha256"], f"archive byte pin {name}")
            if "git_blob" in record:
                require(git_blob(raw) == record["git_blob"], f"Git blob pin {name}")
            validated[name] = raw
    require(set(validated) == set(members), "archive member omission")
    require(digest(validated["caller/FREEZE.json"]) == FREEZE, "prior scientific source freeze")
    frozen = json.loads(validated["caller/FREEZE.json"])["files"]
    require(len(frozen) == 68, "prior source denominator")
    require(set(validated) == {"caller/" + name for name in frozen}
            | {"caller/FREEZE.json", "caller/LICENSE", "resources/fixed/controls.py"}, "archive closure shape")
    for local, pin in frozen.items():
        name = "caller/" + local
        record = members[name]
        require(digest(validated[name]) == pin, f"signed driver historical freeze {local}")
        if local == "run_caller.py":
            require(record["origin"] == "retained_local_inert", "local wrapper provenance")
        else:
            require(record["origin"] == "github" and record["commit"] == HEAD
                    and record["source_path"] == f"research/signed-caller-8x9/{local}"
                    and "git_blob" in record, f"#7113 source binding {local}")
    prior = root / PRIORDIR
    for name, raw in validated.items():
        write(prior / name, raw)
    for name in VENDOR_SHORT_CALLER:
        write(prior / "resources/vendor" / name, validated[SHORT_CALLER + "/" + name])
    for name, pin in PRICING.items():
        path = bound_path(core, f"retained/pricing/{name}")
        write(prior / "resources/vendor" / name, read(path, pin))

    run = load(HERE / "data/OBSERVED.json")
    require(set(run["driver_files"]) == DRIVERS, "original driver file set")
    driver = root / "current/signed"
    for name, pin in run["driver_files"].items():
        write(driver / name, read(HERE / "driver" / name, pin))
    return driver, run


def match_rebuilt(packed, historical_decoded):
    require(gzip.decompress(packed) == historical_decoded, "rebuilt candidate decoded bytes differ")


def transport_controls(decoded):
    def alternate(raw):
        out = BytesIO()
        with gzip.GzipFile(filename="rebuilt-role379.json", fileobj=out, mode="wb",
                           mtime=37, compresslevel=1) as zipped:
            zipped.write(raw)
        return out.getvalue()

    equivalent = alternate(decoded)
    require(digest(equivalent) != NATIVE_TRANSPORT, "alternate transport control changed no bytes")
    match_rebuilt(equivalent, decoded)
    marker = b'"owned_fields":68'
    require(decoded.count(marker) == 1, "decoded mutation control anchor")
    different = decoded.replace(marker, b'"owned_fields":69', 1)
    try:
        match_rebuilt(alternate(different), decoded)
    except ValueError as exc:
        require(str(exc) == "rebuilt candidate decoded bytes differ", "wrong decoded mutation refusal")
    else:
        raise ValueError("one-byte decoded word mutation accepted")
    return {"alternate_gzip": "accepted", "different_decoded_byte": "rejected"}


def portable_spec(core, evidence):
    """Restore runtime paths and authenticate the exact historical signed inputs."""
    spec = load(HERE / "data/SPEC.json")
    require(set(spec["inputs"]) == SPEC_INPUTS and spec["source_pr"] == 7658
            and spec["candidate_canonical_sha256"] == spec["candidate_raw_sha256"] == NATIVE_WORD,
            "exact signed input set and candidate")
    inputs = {}
    for name, ref in spec["inputs"].items():
        if name == "word":
            require(ref["origin"] == "retained-signed-transport" and ref["path"] == "WORD.json.gz"
                    and ref["sha256"] == NATIVE_TRANSPORT, "historical signed transport pin")
            p = bound_path(HERE / "data", ref["path"])
        elif ref["origin"] == "core":
            p = bound_path(core, ref["path"])
        else:
            require(ref["origin"] == "application-evidence", f"unknown input provenance {name}")
            p = bound_path(evidence, ref["path"])
        raw = read(p, ref["sha256"])
        if name == "word":
            decoded = gzip.decompress(raw)
            require(digest(decoded) == NATIVE_WORD, "historical signed word pin")
        inputs[name] = {"path": str(p), "sha256": digest(raw)}
    return {**spec, "inputs": inputs}, decoded


def check_driver(driver):
    # Import the unchanged driver and call its independent source guard.
    entry = (
        "import runpy,sys\n"
        "ns=runpy.run_path(sys.argv[1])\n"
        "assert len(ns['verify_sources']())==68\n"
    )
    subprocess.run([sys.executable, "-I", "-B", "-c", entry, str(driver / "run.py")],
                   cwd=driver, check=True)


def regenerate(core, work):
    entry = runpy.run_path(str(bound_path(core, "verify.py")))
    work.mkdir()
    result, raw, _ = entry["run_mutation"](7658, work, core / "evidence/pr7658", entry["pinned_sources"]())
    require(raw == NATIVE_WORD, "core candidate word hash")
    return result


def normalize_result(obj):
    """Leave only reproducible scientific fields and control outcomes."""
    data = deepcopy(obj)
    del data["seconds"]
    for case in data["controls"]["fixed_tape"]["cases"]:
        # A rejected control's traceback carries relocated filesystem paths.
        case.pop("stderr_sha256")
    return data


def run_application(args, core, evidence):
    output = args.out.resolve()
    output.mkdir(exist_ok=False)
    driver, observed = materialize(output, core)
    spec, historical_decoded = portable_spec(core, evidence)
    transport = transport_controls(historical_decoded)
    rebuilt = read(regenerate(core, output / "candidate"))
    match_rebuilt(rebuilt, historical_decoded)
    path = output / "SPEC.json"
    write_json(path, spec)
    available = os.sched_getaffinity(0)
    cpu = min(available) if args.cpu is None else args.cpu
    require(cpu in available and 150 <= args.wall <= 900, "one available Linux CPU and bounded wall")
    # The command is the reviewer's authorization for this local run. Its
    # self-contained receipt is separate from the original ledger event.
    local_receipt = {
        "mode": "independent_checkout_replay", "spec_sha256": digest(read(path)),
        "candidate_canonical_sha256": NATIVE_WORD, "cpu": cpu, "wall_seconds": args.wall,
        "source_head": spec["source_head"], "driver_files": observed["driver_files"],
    }
    receipt_path = output / "REPLAY-REQUEST.json"
    write_json(receipt_path, local_receipt)
    go = {**local_receipt, "status": "GO", "scope": "fresh-signed-caller-outer",
          "event_id": "independent-checkout-replay",
          "receipt_id": "sha256:" + digest(read(receipt_path))}
    write_json(output / "GO.json", go)
    work = driver / "application"
    subprocess.run([sys.executable, "-I", "-B", str(driver / "run.py"),
                    "--spec", str(path), "--go", str(output / "GO.json"), "--work", str(work)],
                   cwd=driver, check=True)
    result = read(work / "RESULT.json")
    exit_receipt = load(work / "EXIT.json")
    require(exit_receipt["status"] == "COMPLETE"
            and exit_receipt["result_sha256"] == digest(result), "portable signed completion custody")
    expected = load(HERE / "data/EXPECTED.json", observed["normalized_result_sha256"])
    actual = normalize_result(json.loads(result))
    changed = sorted(k for k in actual.keys() | expected.keys() if actual.get(k) != expected.get(k))
    require(not changed, "relocated result differs: " + ", ".join(changed))
    write_json(output / "REPLAY-RESULT.json", {
        "status": "PASS_PORTABLE_7658_SIGNED_APPLICATION",
        "result_sha256": digest(result), "candidate": NATIVE_WORD,
        "claim": spec["claim"], "catalogue_size": actual["catalogue_size"],
        "normalized_result_sha256": observed["normalized_result_sha256"],
        "retained_native_launch_verified": True,
        "transport": {"historical_gzip_sha256": NATIVE_TRANSPORT,
                      "rebuilt_gzip_sha256": digest(rebuilt),
                      "decoded_sha256": NATIVE_WORD, "controls": transport},
        "raw_result": work.relative_to(output).as_posix() + "/RESULT.json",
    })
    print(f"PASS_PORTABLE_7658_SIGNED_APPLICATION {NATIVE_WORD} "
          f"kappa={spec['claim']} catalogue_maps={actual['catalogue_size']}", flush=True)


def main():
    require(sys.version_info[:2] == (3, 12) and sys.flags.isolated
            and sys.dont_write_bytecode and __debug__, "use Linux Python 3.12 -I -B with assertions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core", required=True, type=Path)
    parser.add_argument("--application-evidence", type=Path)
    command = parser.add_subparsers(dest="mode", required=True)
    check = command.add_parser("check", help="validate bindings and relocated input closure")
    check.add_argument("--candidate", type=Path, help="optionally check a previously generated candidate")
    run = command.add_parser("run", help="rebuild candidate and execute the complete signed application")
    run.add_argument("--out", type=Path, help="retain outputs in a fresh directory")
    run.add_argument("--cpu", type=int)
    run.add_argument("--wall", type=int, default=900)
    args = parser.parse_args()
    core = args.core.resolve()
    evidence = (args.application_evidence or (core / "application-evidence")).resolve()
    if args.mode == "run":
        if args.out is not None:
            run_application(args, core, evidence)
        else:
            with tempfile.TemporaryDirectory(prefix="role379-signed-replay-") as tmp:
                args.out = Path(tmp) / "run"
                run_application(args, core, evidence)
        return
    spec, historical_decoded = portable_spec(core, evidence)
    transport_controls(historical_decoded)
    if args.candidate:
        match_rebuilt(read(args.candidate), historical_decoded)
    with tempfile.TemporaryDirectory(prefix="role379-signed-source-check-") as tmp:
        driver, observed = materialize(Path(tmp), core)
        expected = load(HERE / "data/EXPECTED.json", observed["normalized_result_sha256"])
        require(expected["status"] == "PASS_FRESH_SIGNED_CALLER_CONDITIONAL_COMPONENTS"
                and expected["candidate_canonical_sha256"] == NATIVE_WORD, "observed signed result")
        check_driver(driver)
    print(f"PASS_PORTABLE_SIGNED_INPUTS_ONLY {len(spec['inputs'])}/{len(SPEC_INPUTS)}", flush=True)
    print("PASS_PORTABLE_SIGNED_TRANSPORT_CONTROLS alternate_gzip=accepted different_decoded_byte=rejected",
          flush=True)


if __name__ == "__main__":
    main()
