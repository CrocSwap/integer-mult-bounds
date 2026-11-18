#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run the 180-CLEAR verification from the bundled inputs and receipts."""

import argparse
from copy import deepcopy
import gzip
from hashlib import sha1, sha256
import json
import os
from pathlib import Path, PurePosixPath
from shutil import copy2, copytree
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic, sleep


ROOT = Path(__file__).resolve().parent
CLAIM = "https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19698656"
FILES = "INVENTORY.json"
SIDES = ("source", "candidate")
LOCAL_REPLAY = "independent-checkout-replay"


def require(test, reason):
    if not test:
        raise ValueError(reason)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def save(path, obj):
    with path.open("x", encoding="utf-8") as output:
        json.dump(obj, output, indent=2, sort_keys=True)
        output.write("\n")


def check_inventory():
    inventory = load(ROOT / FILES)
    pins = inventory["files"]
    require(inventory["schema_version"] == 1 and inventory["file_count"] == len(pins) and pins,
            "package inventory count")
    observed = set()
    for path in ROOT.rglob("*"):
        name = path.relative_to(ROOT).as_posix()
        require(not path.is_symlink(), f"package symlink {name}")
        if path.is_file() and name != FILES:
            observed.add(name)
    require(observed == pins.keys(), f"package inventory difference: {sorted(observed ^ pins.keys())}")
    for name, record in pins.items():
        rel = PurePosixPath(name)
        require(rel.parts and rel.as_posix() == name and not rel.is_absolute() and ".." not in rel.parts,
                "unsafe package path")
        raw = (ROOT / rel).read_bytes()
        require(len(raw) == record["bytes"] and sha256(raw).hexdigest() == record["sha256"],
                f"package byte difference: {name}")
        if record.get("origin") == "published Git blob":
            git_blob = sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
            require(git_blob == record["git_blob"], f"retained Git blob difference: {name}")
        if "decoded_sha256" in record:
            require(sha256(gzip.decompress(raw)).hexdigest() == record["decoded_sha256"],
                    f"retained decoded evidence difference: {name}")


def python_command(work, script, *args, import_siblings=False):
    argv = [sys.executable, "-I", "-B", "-X", f"pycache_prefix={work / 'new-cache'}"]
    path = ROOT / script
    if import_siblings:
        # Isolated Python omits the script directory. Add only the pinned native
        # adapter directory so its local build_low import works.
        argv.extend(["-c", "import pathlib,runpy,sys\n"
                     "script=pathlib.Path(sys.argv.pop(1))\n"
                     "sys.path.insert(0,str(script.parent))\n"
                     "runpy.run_path(str(script),run_name='__main__')", path])
    else:
        argv.append(path)
    return [*argv, *args]


def command(work, script, *args, timeout):
    subprocess.run(python_command(work, script, *args), cwd=work, check=True, timeout=timeout)


def build_pair(work):
    regenerated = work / "regenerated"
    command(work, "src/native/build_low.py", "--inputs", ROOT / "inputs/native", "--out", regenerated,
            "--authorization", ROOT / "evidence/core-authorization.json", timeout=15)
    brief = load(regenerated / "BINDING.json")
    pair = work / "pair"
    pair.mkdir()
    original = load(ROOT / "evidence/BINDING.json")
    for side in SIDES:
        saved = ROOT / "inputs/lowered" / side
        raw = gzip.decompress((regenerated / side / "WORD.json.gz").read_bytes())
        require(raw == gzip.decompress((saved / "WORD.json.gz").read_bytes())
                and sha256(raw).hexdigest() == brief[side]["raw_sha256"], f"rebuilt decoded bytes: {side}")
        require((regenerated / side / "CLEAR-CERTIFICATES.json").read_bytes() ==
                (saved / "CLEAR-CERTIFICATES.json").read_bytes(), f"rebuilt CLEAR certificates: {side}")
        # The retained grid binds the original gzip bytes. Establish decoded
        # equality before copying that immutable transport for signed replay.
        fields = original[side]
        require(fields["gzip_sha256"] == digest(saved / "WORD.json.gz")
                and fields["clear_sha256"] == digest(saved / "CLEAR-CERTIFICATES.json"),
                f"retained transport binding: {side}")
        copytree(saved, pair / side)
        brief[side]["gzip_sha256"] = fields["gzip_sha256"]
    require(brief == original, "retained build receipt differs from the cold rebuild")
    copy2(ROOT / "evidence/BINDING.json", pair / "BINDING.json")
    return pair


def exact(work):
    pair = build_pair(work)
    scalar = subprocess.check_output(python_command(
        work, "src/check_scalar.py", ROOT / "inputs/native/raw-combined.json.gz",
        pair / "candidate/WORD.json.gz"), cwd=work, timeout=20)
    require(json.loads(scalar) == load(ROOT / "evidence/SCALAR-DOMAIN.json"), "scalar residue evidence differs")
    result = work / "INDEPENDENT-RESULT.json"
    command(work, "src/independent/verify.py", "--spec", ROOT / "INDEPENDENT.json",
            "--out", result, timeout=230)
    actual, expected = load(result), load(ROOT / "evidence/INDEPENDENT-RESULT.json")
    for record in (actual, expected):
        del record["started_at"]
        del record["completed_at"]
    require(actual == expected, "portable independent evidence differs")


def native_science(record):
    data = deepcopy(record)
    for name in ("completed_at", "elapsed_ns", "artifacts"):
        del data[name]
    for report in data["finite_replays"]:
        del report["elapsed_ns"]
    for side in SIDES:
        # Gzip framing varies by Python and zlib. build_pair compares the exact
        # decoded payload and verifies each replay's own transport hash.
        del data[side]["gzip_sha256"]
    return data


def run_native(work, wall):
    """Produce a new native result and launch receipt for the signed input gate."""
    native = work / "native"
    copytree(ROOT / "src/native", native)
    pair = build_pair(native)
    inputs = native / "inputs"
    copytree(ROOT / "inputs/native", inputs)
    archive = inputs / "prior-pairs.json.gz"
    (inputs / "prior-pairs.json").write_bytes(gzip.decompress(archive.read_bytes()))
    out = native / "replay"
    log = native / "native-logs"
    release = native / "native-authorization.json"
    cpu = min(os.sched_getaffinity(0))
    argv = python_command(work, native / "run_guarded_low.py", "native", "--inputs", inputs,
                          "--out", out, "--log", log, "--authorization", release,
                          "--materialized", pair, "--cpu", str(cpu), "--wall", str(wall), import_siblings=True)
    with subprocess.Popen(argv, cwd=work) as process:
        try:
            start = log / "START.json"
            deadline = monotonic() + 10
            while not start.is_file():
                require(process.poll() is None and monotonic() < deadline, "native launcher did not arm")
                sleep(0.1)
            # The legacy gate expects the original event key. Record this
            # independent checkout with its own request hash and no graph ID.
            original = load(ROOT / "evidence/native-authorization.json")
            origin = {k: v for k, v in original.items() if k not in {"receipt_id", "receipt_sha256"}}
            request = native / "REPLAY-REQUEST.json"
            save(request, {**origin, "mode": LOCAL_REPLAY, "native_start_sha256": digest(start)})
            staged = native / "REPLAY-RELEASE.json"
            save(staged, {**load(request), "receipt_id": f"sha256:{digest(request)}"})
            staged.rename(release)
            require(process.wait(timeout=wall + 15) == 0, "native launcher failed")
        finally:
            if process.poll() is None:
                process.kill()
    actual, expected = load(out / "RESULT.json"), load(ROOT / "evidence/NATIVE-RESULT.json")
    require(native_science(actual) == native_science(expected), "portable native evidence differs")
    require(actual["artifacts"]["MOVE-PAIRS.json"] == expected["artifacts"]["MOVE-PAIRS.json"],
            "complete MOVE catalogue digest differs")
    return native


def native(work):
    run_native(work, 340)


def local_gate(work, scope, spec, fields):
    path = work / "GO.json"
    payload = {"mode": LOCAL_REPLAY, "status": "GO", "scope": scope, "spec_sha256": digest(spec),
               "public_claim": CLAIM, "event_id": LOCAL_REPLAY, **fields}
    receipt = work / "REPLAY-REQUEST.json"
    save(receipt, payload)
    save(path, {**payload, "receipt_id": f"sha256:{digest(receipt)}"})
    return path


def resources(work, case, wall):
    build_pair(work)
    spec = ROOT / "RESOURCE.json"
    cpu = min(os.sched_getaffinity(0))
    go = local_gate(work, "7636-lowered-paired-resource", spec,
                    {"bounds": {case: {"cpu": cpu, "cpu_seconds": wall - 10, "wall_seconds": wall}}})
    output = work / "resources"
    command(work, "src/application/resource_replay.py", "--evidence", ROOT / "application-evidence",
            "--spec", spec, "--go", go, "--case", case, "--out", output, timeout=wall + 10)
    result = load(output / "RESULT.json")
    originals = ROOT / "evidence/resources" / ("resource-" + case)
    original = load(originals / "RESULT.json")
    # This runner uses the immutable originally observed compressed input, so
    # proof-relevant receipts can be compared as canonical JSON objects.
    for name, expected_pin in original["receipts"].items():
        expected = originals / name
        require(digest(expected) == expected_pin and digest(output / name) == result["receipts"][name],
                f"resource receipt hash {case}/{name}")
        old, new = load(expected), load(output / name)
        for record in (old, new):
            if name == "GRID.json":
                del record["elapsed_seconds"]
            elif name == "ORDINARY.json":
                del record["adapted_ordinary_sha256"]  # contains the relocated input and output paths
        require(new == old, f"portable resource evidence differs: {case}/{name}")


def signed(work):
    started = monotonic()
    native_root = run_native(work, 260)
    spec = work / "SIGNED-SPEC.json"
    command(work, "src/application/freeze_signed.py", "--core", ROOT, "--native", native_root,
            "--independent", ROOT / "evidence/INDEPENDENT-RESULT.json", "--resources", ROOT / "evidence/resources",
            "--out", spec, timeout=15)
    remaining = 575 - int(monotonic() - started)
    require(remaining >= 155, "registered signed wall budget after fresh native proof")
    go = local_gate(work, "fresh-signed-7636-lowered-c", spec,
                    {"cpu": min(os.sched_getaffinity(0)), "wall_seconds": remaining - 5})
    command(work, "src/application/signed_replay.py", "--core", ROOT, "--spec", spec,
            "--go", go, "--out", work / "signed", "--expected", ROOT / "evidence/SIGNED-EXPECTED.json",
            timeout=remaining)


def main():
    require(sys.version_info[:2] == (3, 12) and sys.flags.isolated and sys.dont_write_bytecode and __debug__
            and sys.platform.startswith("linux"), "use Linux CPython 3.12 -I -B")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("integrity", "exact", "native", "resource-source", "resource-candidate", "signed"))
    parser.add_argument("--out", type=Path, help="keep the replay in this new directory outside the package")
    parser.add_argument("--resource-wall", type=int, default=420, help="wall cap for a resource replay")
    args = parser.parse_args()
    check_inventory()
    if args.stage != "integrity":
        stages = {"exact": exact, "native": native, "signed": signed}
        runner = stages.get(args.stage)
        if runner is None:
            case = args.stage.removeprefix("resource-")

            def runner(work):
                require(15 <= args.resource_wall <= 420, "finite resource wall limit")
                resources(work, case, args.resource_wall)

        if args.out is None:
            with TemporaryDirectory(prefix="p104-180-") as temporary:
                runner(Path(temporary).resolve())
        else:
            out = args.out.resolve()
            require(not out.is_relative_to(ROOT), "place replay output outside the frozen input package")
            out.mkdir(exist_ok=False)
            runner(out)
    print("PASS_180_CONTACT_APPLICATION_" + args.stage.upper().replace("-", "_"), flush=True)


if __name__ == "__main__":
    main()
