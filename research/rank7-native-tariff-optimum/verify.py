# SPDX-License-Identifier: Apache-2.0
"""Compile both provider words and compare the exact native tariff ledgers."""

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

from contract import NEW, OLD, START, expected_cleanup, operator
from contract import produce as contract_three
from frames import require, trace
from tariff import (
    INVERSE,
    OPTIMAL,
    TARGET,
    bounded_exclusions,
    lower_bound,
    matrix,
    price,
    produce,
)

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
LOCAL = {1: 2433, 2: 712, 3: 232, 4: 108, 5: 18, 8: 8}
VENDORED = {
    "contract.py",
    "frames.py",
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
    require(path.is_file() and path.stat().st_size <= 8_000_000, "bounded input file")
    raw = path.read_bytes()
    if path.suffix == ".gz":
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(8_000_001)
    require(len(raw) <= 8_000_000, "bounded decoded input")
    return json.loads(raw)


def check_pins():
    records = read(PACKAGE / "VENDOR.json")["files"]
    require(
        len(records) == len(VENDORED) and {r["path"] for r in records} == VENDORED,
        "complete frozen input inventory",
    )
    for record in records:
        path = PACKAGE / record["path"]
        require(path.resolve().is_relative_to(PACKAGE), "contained frozen input")
        require(
            hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"],
            "frozen input hash: " + record["path"],
        )
    sources = read(PACKAGE / "SOURCES.json")["files"]
    require(len(sources) <= 8, "bounded live inputs")
    for record in sources:
        if record["usage"] == "input":
            path = ROOT / record["path"]
            require(path.resolve().is_relative_to(ROOT), "contained live input")
            require(
                hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"],
                "live source hash: " + record["path"],
            )
    return len(records)


def validate_word(word):
    limits = {
        "A": 20000,
        "B": 20000,
        "restore": 1000,
        "cleanup": 60000,
        "warps": 704,
        "initial_corrections": 20000,
        "precondition": 20000,
        "compensation": 20000,
        "cut": 20000,
    }
    for section, maximum in limits.items():
        require(
            isinstance(word[section], list) and len(word[section]) <= maximum,
            "bounded word section: " + section,
        )
    require(
        word["report"]["h"] == 9
        and word["report"]["v"] == 112
        and word["report"]["R"] == 480,
        "literal dimensions",
    )
    require(
        type(word["prelude_events"]) is int
        and 0 <= word["prelude_events"] <= len(word["A"]),
        "prelude range",
    )
    require(len(word["helper_final"]) == 91, "91 private buffers")


def check_words(parent, candidate):
    validate_word(parent)
    validate_word(candidate)
    require(parent["cleanup"] == expected_cleanup(parent), "source cleanup")
    require(candidate["cleanup"] == expected_cleanup(candidate), "candidate cleanup")
    require(
        candidate["restore"]
        == parent["restore"][:START] + OPTIMAL + parent["restore"][START + 4 :],
        "one literal tariff replacement",
    )
    require(
        operator(parent["restore"], range(704))
        == operator(candidate["restore"], range(704)),
        "arbitrary-dirty restore",
    )
    require(
        parent["cleanup"][:33] == candidate["cleanup"][:33]
        and parent["cleanup"][37:] == candidate["cleanup"][37:]
        and operator(parent["cleanup"][33:37], (22, 934))
        == operator(candidate["cleanup"][33:37], (22, 934))
        == {22: {22: -1, 934: 1}, 934: {22: -1}},
        "one exact inverse block on arbitrary dirty private-buffer values",
    )
    before, after = trace(parent), trace(candidate)
    require(
        before["profile"] == after["profile"] == LOCAL, "unchanged recursive children"
    )
    require(before["widths"] == after["widths"], "unchanged ordered helper widths")
    require(before["histories"] == after["histories"], "unchanged frame chronology")
    require(
        {k for k in parent if parent[k] != candidate[k]} == {"restore", "cleanup"},
        "no changed state, frame or other word section",
    )
    return {
        "word_sha256": digest(candidate),
        "local_profile": LOCAL,
        "helper_count": len(after["widths"]),
        "private_buffers": 91,
    }


def compile_word(word, work):
    source = work / "WORD.json"
    require(not work.exists(), "fresh compiler workspace")
    work.mkdir()
    payload = canonical(word)
    require(source.write_bytes(payload) == len(payload), "complete word export")
    output = work / "native"
    env = dict(
        os.environ,
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONPYCACHEPREFIX=str(work / "bytecode"),
    )
    for name in ("PYTHONOPTIMIZE", "PYTHONPATH"):
        env.pop(name, None)
    for script, arguments in (
        ("bw_transport.py", [source, output]),
        ("bw_emit.py", [output]),
    ):
        command = [
            sys.executable,
            "-W",
            "error",
            "-B",
            str(PACKAGE / "vendor/native" / script),
            *map(str, arguments),
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
    checks = read(output / "LOCAL-CHECKS.json")
    programs = read(output / "LOCAL-PROGRAMS.json.gz")
    for orientation in ("forward", "backward"):
        check_ledger(checks[orientation], programs[orientation])
    return {
        "canonical": read(output / "CANONICAL-WORD.json.gz"),
        "programs": programs,
        "checks": checks,
    }


def check_ledger(checks, events):
    require(len(events) <= 60000, "bounded emitted stream")
    scalars = [event[1] for event in events if event[0] == "scalar"]
    paid = {}
    for event in events:
        if event[0] in ("climb", "center"):
            rank = event[5] if event[0] == "climb" else event[4]
            paid[rank] = paid.get(rank, 0) + 1
    require(paid == LOCAL, "independent emitted child recount")
    require(checks["sha256"] == digest(events), "literal emitted program digest")
    require(
        checks["real_component_primitive_bound"] == 2 * sum(map(price, scalars)),
        "independent real-component tariff recount",
    )
    require(
        checks["events"] == len(events) and checks["scalar_macros"] == len(scalars),
        "event and macro count",
    )
    require(
        {int(r): n for r, n in checks["paid_profile"].items()} == LOCAL,
        "native paid ledger",
    )
    require(
        checks["all_columns"] == 632
        and checks["zero_buffers_returned_to_zero"] == 91
        and checks["private_centers_cleared"]
        and checks["private_coefficient_stream_cleared_after_each_macro"],
        "native arbitrary-input endpoint and private erasure",
    )


def phases(events):
    result = {}
    phase = None
    for event in events:
        if event[0] == "phase":
            phase = event[1]
            require(phase not in result, "unique phase")
            result[phase] = []
        if event[0] == "scalar":
            require(phase is not None, "scalar has phase")
            result[phase].append(event)
    return result


def compare_programs(parent, candidate, saving, removed_macros):
    require(
        {k: v for k, v in parent["canonical"].items() if k not in ("tail", "cleanup")}
        == {
            k: v
            for k, v in candidate["canonical"].items()
            if k not in ("tail", "cleanup")
        },
        "unchanged native frames, wrappers, warp table, ABI and recursive invoice",
    )
    for orientation in ("forward", "backward"):
        old, new = parent["programs"][orientation], candidate["programs"][orientation]
        require(
            [e for e in old if e[0] != "scalar"]
            == [e for e in new if e[0] != "scalar"],
            "unchanged non-scalar emitted events",
        )
        old_phases, new_phases = phases(old), phases(new)
        require(set(old_phases) == set(new_phases), "same phases")
        for phase in old_phases:
            delta = sum(price(e[1]) for e in old_phases[phase])
            delta -= sum(price(e[1]) for e in new_phases[phase])
            if phase in ("cleanup_tail", "full_frame_cleanup"):
                require(delta == saving // 4, "equal forward/inverse tariff saving")
            else:
                require(
                    old_phases[phase] == new_phases[phase], "unchanged other scalars"
                )
        a, b = parent["checks"][orientation], candidate["checks"][orientation]
        require(
            a["real_component_primitive_bound"] - b["real_component_primitive_bound"]
            == saving,
            "complete primitive-bound improvement",
        )
        require(
            a["scalar_macros"] - b["scalar_macros"] == removed_macros,
            "macro count is a different objective",
        )


def whole_bill():
    original = {
        int(r): n
        for r, n in read(
            ROOT / "research/rank7-joint-endframes/allocation/PROFILE.json"
        ).items()
    }
    source = {int(r): n for r, n in read(PACKAGE / "vendor/PROFILE.json").items()}
    require(
        source == {r: n + 666 * {1: -12, 2: 6}.get(r, 0) for r, n in original.items()},
        "PR3042 complete bill binding",
    )
    require(
        sum(r * n for r, n in source.items()) == 4816512, "unchanged complete rank mass"
    )
    return {
        "profile": source,
        "rank_mass": 4816512,
        "calls": 666,
        "physical_families": 66813,
        "private_buffers": 91,
        "profile_delta": {},
        "kappa_improvement_claimed": False,
    }


def audit(work):
    pins = check_pins()
    require(
        matrix(OPTIMAL) == TARGET and lower_bound(TARGET) == lower_bound(INVERSE) == 10,
        "optimal block and inverse",
    )
    require(
        [sum(map(price, gates)) for gates in (OLD, NEW, OPTIMAL)] == [16, 13, 10],
        "three distinct native block tariffs",
    )
    exclusions = bounded_exclusions()
    variants = {}
    for variant in ("base", "extra"):
        parent = read(PACKAGE / f"vendor/WORD-{variant}.json.gz")
        validate_word(parent)
        optimal = produce(parent)
        semantic = check_words(parent, optimal)
        words = {
            "parent": parent,
            "three_add": contract_three(parent),
            "optimal": optimal,
        }
        compiled = {
            name: compile_word(word, work / f"{variant}-{name}")
            for name, word in words.items()
        }
        compare_programs(compiled["parent"], compiled["three_add"], 12, 2)
        compare_programs(compiled["parent"], compiled["optimal"], 24, 0)
        variants[variant] = {
            "semantic": semantic,
            "native": {name: item["checks"] for name, item in compiled.items()},
        }
    return {
        "status": "PASS_RANK7_NATIVE_TARIFF_OPTIMUM",
        "vendor_pins": pins,
        "block_tariffs": {"parent": 16, "three_add": 13, "optimal": 10},
        "minimum_component_tariff": 10,
        "cheap_core_exclusions": exclusions,
        "variants": variants,
        "bill": whole_bill(),
        "scope": "Exact native transport/emitter and conservative coefficient tariff. "
        "No materialized instruction count, runtime, fresh physical warp/wrapper "
        "verification, precision, all-size, supplier admission or outer release.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--work", type=Path, help="fresh external path; retain compiler diagnostics"
    )
    parser.add_argument("--emit-word", choices=("base", "extra"))
    args = parser.parse_args()
    require(not sys.flags.optimize, "inherited native validators require assertions")
    if args.work:
        work = args.work.resolve()
        require(
            not work.exists()
            and not work.is_relative_to(ROOT)
            and not ROOT.is_relative_to(work),
            "fresh external compiler work path",
        )
        work.mkdir(parents=True)
        result = audit(work)
    else:
        with tempfile.TemporaryDirectory(prefix="rank7-native-tariff-") as directory:
            result = audit(Path(directory))
    if args.emit_word:
        result = produce(read(PACKAGE / f"vendor/WORD-{args.emit_word}.json.gz"))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
