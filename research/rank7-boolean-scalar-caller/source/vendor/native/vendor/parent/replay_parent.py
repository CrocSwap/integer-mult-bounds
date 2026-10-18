# SPDX-License-Identifier: Apache-2.0
"""Source-bound native replay of both providers, with an explicit edit proof."""

import argparse
import gzip
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from contractions import produce
from frames import require
from tariff import price
from tariff import produce as tariff_parent

PACKAGE = Path(__file__).resolve().parent
LOCAL = {1: 2433, 2: 712, 3: 232, 4: 108, 5: 18, 8: 8}
FROZEN = {
    "contract.py",
    "frames.py",
    "tariff.py",
    "vendor/WORD-base.json.gz",
    "vendor/WORD-extra.json.gz",
    "vendor/PROFILE.json",
    "vendor/CREDITS.md",
    "vendor/NOTICE",
    "vendor/native/bw_transport.py",
    "vendor/native/bw_emit.py",
    "vendor/native/NOTICE-PR2226.md",
    "vendor/native/PR2226-NOTICE.md",
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read(path):
    require(path.is_file() and path.stat().st_size <= 8_000_000, "bounded input")
    raw = path.read_bytes()
    if path.suffix == ".gz":
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(8_000_001)
    require(len(raw) <= 8_000_000, "bounded decoded input")
    return json.loads(raw)


def check_pins(package=PACKAGE):
    records = read(package / "VENDOR.json")["files"]
    require(
        len(records) == len(FROZEN) and {r["path"] for r in records} == FROZEN,
        "complete frozen inventory",
    )
    for record in records:
        path = package / record["path"]
        require(
            path.is_file()
            and not path.is_symlink()
            and path.resolve().is_relative_to(package),
            "contained regular input",
        )
        require(path.stat().st_size <= 8_000_000, "bounded frozen source")
        require(
            hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"],
            "frozen source bytes: " + record["path"],
        )
    return len(records)


def compile_word(word, work):
    require(not work.exists(), "fresh native output directory")
    work.mkdir()
    source = work / "WORD.json"
    payload = canonical(word)
    require(source.write_bytes(payload) == len(payload), "complete source export")
    output = work / "native"
    env = dict(
        os.environ,
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONPYCACHEPREFIX=str(work / "bytecode"),
    )
    for key in ("PYTHONOPTIMIZE", "PYTHONPATH"):
        env.pop(key, None)
    for script, args in (
        ("bw_transport.py", [source, output]),
        ("bw_emit.py", [output]),
    ):
        command = [
            sys.executable,
            "-W",
            "error",
            "-B",
            str(PACKAGE / "vendor/native" / script),
            *map(str, args),
        ]
        with (work / (script + ".log")).open("w") as stream:
            subprocess.run(
                command,
                cwd=work,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=stream,
                stderr=subprocess.STDOUT,
                check=True,
                timeout=90,
            )
    programs = read(output / "LOCAL-PROGRAMS.json.gz")
    checks = read(output / "LOCAL-CHECKS.json")
    for direction in ("forward", "backward"):
        check_ledger(programs[direction], checks[direction])
    return programs, checks


def check_ledger(events, check):
    require(len(events) <= 30_000, "bounded native stream")
    scalars = [event[1] for event in events if event[0] == "scalar"]
    paid = {}
    for event in events:
        if event[0] in ("climb", "center"):
            rank = event[5] if event[0] == "climb" else event[4]
            paid[rank] = paid.get(rank, 0) + 1
    require(paid == LOCAL, "literal paid-child recount")
    require(check["sha256"] == digest(events), "literal native program hash")
    require(
        check["real_component_primitive_bound"] == 2 * sum(map(price, scalars)),
        "independent complete native tariff",
    )
    require(
        check["events"] == len(events) and check["scalar_macros"] == len(scalars),
        "complete event and macro counts",
    )
    require(
        {int(r): n for r, n in check["paid_profile"].items()} == LOCAL,
        "native paid profile",
    )
    require(
        check["all_columns"] == 632 and check["warp_events"] == 240,
        "all live inputs and warps",
    )
    require(
        check["zero_buffers_returned_to_zero"] == 91
        and check["private_centers_cleared"]
        and check["private_coefficient_stream_cleared_after_each_macro"],
        "all private erasure obligations",
    )


def compare(before, after, old_checks, new_checks, base_bound, saving):
    for direction, expected in (("forward", base_bound), ("backward", base_bound + 48)):
        old, new = old_checks[direction], new_checks[direction]
        require(
            old["real_component_primitive_bound"] == expected
            and new["real_component_primitive_bound"] == expected - saving,
            "complete bound saving",
        )
        require(
            old["events"] - new["events"] == 54
            and old["scalar_macros"] - new["scalar_macros"] == 54,
            "54 emitted scalar events removed",
        )
        require(
            [e for e in before[direction] if e[0] != "scalar"]
            == [e for e in after[direction] if e[0] != "scalar"],
            "identical complete non-scalar stream",
        )


def run(work):
    pin_count = check_pins()
    edits = read(PACKAGE / "EDITS.json")
    require(not work.exists(), "fresh replay root")
    work.mkdir(parents=True)
    result = {}
    for provider in ("base", "extra"):
        original = read(PACKAGE / f"vendor/WORD-{provider}.json.gz")
        baseline = tariff_parent(original)
        candidate = produce(baseline, edits)
        original_candidate = produce(original, edits)
        require(
            tariff_parent(original_candidate) == candidate,
            "commutes with PR3060's disjoint restore improvement",
        )
        programs, checks = {}, {}
        for name, word in (
            ("pr3042", original),
            ("pr3060", baseline),
            ("candidate", candidate),
        ):
            programs[name], checks[name] = compile_word(
                word, work / f"{provider}-{name}"
            )
        compare(
            programs["pr3060"],
            programs["candidate"],
            checks["pr3060"],
            checks["candidate"],
            158124,
            340,
        )
        compare(
            programs["pr3042"],
            programs["candidate"],
            checks["pr3042"],
            checks["candidate"],
            158148,
            364,
        )
        result[provider] = {
            "parent_sha256": digest(baseline),
            "word_sha256": digest(candidate),
            "native": checks,
        }
    return {
        "status": "PASS_COMMUTING_CONTRACTIONS_NO_NEW_KAPPA",
        "frozen_inputs": pin_count,
        "edits": 24,
        "A_gates": [4079, 4052],
        "cleanup_gates": [5216, 5189],
        "single_component_A_saving": 85,
        "complete_saving_over_pr3060": 340,
        "complete_saving_over_pr3042": 364,
        "providers": result,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--work", type=Path, help="fresh external directory; retain diagnostics"
    )
    parser.add_argument("--emit-word", choices=("base", "extra"))
    args = parser.parse_args()
    if args.work:
        work = args.work.expanduser().resolve()
        require(not work.is_relative_to(PACKAGE.parents[1]), "output outside checkout")
        result = run(work)
    else:
        with tempfile.TemporaryDirectory(prefix="rank7-contractions-") as directory:
            result = run(Path(directory) / "replay")
    require(result == read(PACKAGE / "RESULT.json"), "committed deterministic receipt")
    if args.emit_word:
        parent = tariff_parent(read(PACKAGE / f"vendor/WORD-{args.emit_word}.json.gz"))
        result = produce(parent, read(PACKAGE / "EDITS.json"))
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
