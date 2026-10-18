#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Rebuild R2 and its R1 composition, audit actual words, certify full moments."""

import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

import frame_trace
import rewrite as rw

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PARENT = ROOT / "research/rank7-joint-endframes"
EXPECTED = {1: 1643016, 2: 471528, 3: 159468, 4: 71928, 5: 13716, 8: 5328, 48: 28190}


def read(path):
    raw = path.read_bytes()
    rw.need(len(raw) <= 2_000_000, "bounded input bytes")
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def canonical(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate():
    pins = read(PACKAGE / "SOURCES.json")["files"]
    rw.need(len(pins) <= 16, "bounded dependency inventory")
    for entry in pins:
        if entry["usage"] == "input":
            rw.need(
                digest(ROOT / entry["path"]) == entry["sha256"],
                "source pin: " + entry["path"],
            )
    vendor = read(PACKAGE / "VENDOR.json")
    rw.need(len(vendor) <= 4, "bounded retained sources")
    for entry in vendor:
        rw.need(digest(PACKAGE / entry["path"]) == entry["sha256"], "retained pin")


def load(path, name):
    # Callers authenticate every external module before loading it.
    spec = importlib.util.spec_from_file_location(name, path)
    rw.need(spec is not None and spec.loader is not None, "source module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def words(variant, frames):
    original = read(PARENT / f"data/WORD-{variant}.json.gz")
    r1 = rw.r1(original, read(PACKAGE / "vendor/R1.json"), variant)
    candidates = {
        "parent": copy.deepcopy(original),
        "R1": r1,
        "R2": rw.r2(original),
        "R1R2": rw.r2(r1),
    }
    expected = {
        "parent": {"1": 2445, "2": 706},
        "R1": {"1": 2443, "2": 707},
        "R2": {"1": 2443, "2": 707},
        "R1R2": {"1": 2441, "2": 708},
    }
    for name, word in candidates.items():
        rw.finish(word, original, frames)
        profile = {**rw.LOCAL, **expected[name]}
        rw.need(word["report"]["local_profile"] == profile, "exact local bill")
    return candidates


def scalar_identity():
    """Independent four-register Q matrix check, not a frame-engine result."""
    rows = [[Fraction(i == j) for j in range(4)] for i in range(4)]
    original = copy.deepcopy(rows)
    for target in (2, 3):
        original[target] = [
            a + b - 2 * c
            for a, b, c in zip(original[target], original[0], original[1], strict=True)
        ]
    for target, source, coefficient in ((0, 1, -2), (2, 0, 1), (3, 0, 1), (0, 1, 2)):
        rows[target] = [
            a + coefficient * b for a, b in zip(rows[target], rows[source], strict=True)
        ]
    rw.need(rows == original, "dirty-source/target matrix identity")
    rw.need(rows[:2] == [[1, 0, 0, 0], [0, 1, 0, 0]], "both sources restored")
    return [[str(x) for x in row] for row in rows]


def restore_matrix(word):
    """Exact scalar action of every literal restore gate on all 704 inputs."""
    rw.need(len(word["restore"]) <= 204, "bounded restore matrix")
    rows = [{i: Fraction(1)} for i in range(704)]
    for gate in word["restore"]:
        target = gate[1]
        rw.need(0 <= target < 704, "restore target")
        if gate[0] == "add":
            source, coefficient = gate[2], Fraction(gate[3], gate[4])
            rw.need(0 <= source < 704 and target != source, "restore source")
            for column, value in tuple(rows[source].items()):
                total = rows[target].get(column, 0) + coefficient * value
                if total:
                    rows[target][column] = total
                else:
                    rows[target].pop(column, None)
        else:
            rw.need(gate[0] == "scale", "restore scalar opcode")
            coefficient = Fraction(gate[2], gate[3])
            rw.need(coefficient != 0, "invertible restore scale")
            rows[target] = {c: coefficient * x for c, x in rows[target].items()}
    return rows


def audit(word, label, work, accepted=True, reason=None):
    path, output = work / (label + ".json.gz"), work / (label + ".audit.json")
    payload = json.dumps(word, sort_keys=True, separators=(",", ":")).encode()
    path.write_bytes(gzip.compress(payload, compresslevel=1, mtime=0))
    command = [
        sys.executable,
        "-I",
        "-B",
        "-X",
        "pycache_prefix=" + str(work / "audit-bytecode"),
        str(PARENT / "vendor/audit_local.py"),
        "--word",
        str(path),
        "--output",
        str(output),
    ]
    with (work / (label + ".log")).open("w") as log:
        result = subprocess.run(
            command, stdout=log, stderr=subprocess.STDOUT, timeout=30, check=False
        )
    if not accepted:
        rw.need(result.returncode != 0, "mutant accepted: " + label)
        text = (work / (label + ".log")).read_text()
        rw.need(
            reason is not None and reason in text, "actual mutation rejection reason"
        )
        return "rejected"
    rw.need(result.returncode == 0, "failed actual word audit: " + label)
    report = read(output)
    rw.need(report["status"] == "PASS_INDEPENDENT_EXACT_BORROWING_WORD", "audit status")
    rw.need(
        report["checked_columns"] == 632 and report["zero_buffers"] == 91,
        "all dirty columns and private buffers",
    )
    rw.need(
        report["orientations"] == {"forward": "PASS", "dual": "PASS"},
        "both orientations",
    )
    return {
        "canonical_sha256": canonical(word),
        "local_profile": report["local_profile"],
        "width_inventory": report["width_inventory"],
        "checked_columns": 632,
        "orientations": report["orientations"],
        "zero_buffers": 91,
    }


def controls(candidate, original, variant, work):
    labels = []
    for name in (
        "omit-aggregate",
        "wrong-aggregate",
        "omit-undo",
        "wrong-undo",
        "frame-too-small",
        "stale-cleanup",
        "stale-profile",
    ):
        mutant = copy.deepcopy(candidate)
        if name == "omit-aggregate":
            del mutant["restore"][162]
        elif name == "wrong-aggregate":
            mutant["restore"][162][3] = -1
        elif name == "omit-undo":
            mutant["restore"].pop()
        elif name == "wrong-undo":
            mutant["restore"][-1][3] = -2
        elif name == "frame-too-small":
            mutant["restore"][162][-1] = rw.LOW[:-1]
        elif name == "stale-cleanup":
            mutant["cleanup"] = copy.deepcopy(original["cleanup"])
        else:
            mutant["report"]["local_profile"] = copy.deepcopy(
                original["report"]["local_profile"]
            )
        rw.need(mutant != candidate, "effective rejection control")
        if name in ("omit-aggregate", "wrong-aggregate", "omit-undo", "wrong-undo"):
            rw.need(
                restore_matrix(mutant) != restore_matrix(candidate),
                "independent scalar-equivalence control",
            )
        reason = "explicit cleanup differs"
        if name == "frame-too-small":
            reason = "frame not monotone"
        elif name == "stale-profile":
            reason = "paid profile mismatch"
        audit(mutant, variant + "-" + name, work, accepted=False, reason=reason)
        labels.append(name)
    # A coefficient-preserving but semantically invalid intervening read must
    # fail the rewriter boundary, before any generated word is accepted.
    mutant = copy.deepcopy(original)
    mutant["restore"][164] = ["add", 18, 40, 1, 1, rw.FULL]
    try:
        rw.r2(mutant)
    except ValueError as error:
        rw.need("observer" in str(error), "contact guard rejects the actual obligation")
    else:
        raise ValueError("intervening source observer accepted")
    return labels + ["intervening-source-observer"]


def moment():
    root = load(PARENT / "tools/root.py", "source_bound_moment")
    parent = {int(k): n for k, n in read(PARENT / "allocation/PROFILE.json").items()}
    r1 = {**parent, 1: parent[1] - 1332, 2: parent[2] + 666}
    rw.need(
        {**parent, 1: parent[1] - 2664, 2: parent[2] + 1332} == EXPECTED,
        "complete bill",
    )
    lower, upper = root.kappa_from_profile(EXPECTED, 74)
    r1_lower, r1_upper = root.kappa_from_profile(r1, 74)
    previous = read(PACKAGE / "vendor/PR3030-FINITE.json")
    previous_profile = {int(k): n for k, n in previous["profile"].items()}
    previous_cap_lower, previous_cap_upper = root.kappa_from_profile(
        previous_profile, 740
    )
    rw.need(
        [str(previous_cap_lower), str(previous_cap_upper)]
        == previous["moment"]["root"],
        "pinned T740 comparison",
    )
    rw.need(
        lower > previous_cap_upper > r1_upper,
        "strict gain beyond current published T740 candidate",
    )
    rw.need(root.rank_mass(EXPECTED) == 74 * 65088, "complete rank mass")
    return {
        "T": 74,
        "calls": 666,
        "profile": EXPECTED,
        "rank_mass": 74 * 65088,
        "root": [str(lower), str(upper)],
        "R1_root": [str(r1_lower), str(r1_upper)],
        "PR3030_root": [str(previous_cap_lower), str(previous_cap_upper)],
        "gain_over_PR3030": [
            str(lower - previous_cap_upper),
            str(upper - previous_cap_lower),
        ],
        "packing_relaxation": packing_ceiling(root, lower, upper),
    }


def packing_ceiling(root, lower, upper):
    local = {int(r): n for r, n in rw.LOCAL.items()}
    idle_mass = 65088 - 9 * sum(r * n for r, n in local.items())
    rw.need(
        idle_mass == 18837 and 2 * 51**2 < 73**2 <= 2 * 52**2,
        "coverage and halving cap",
    )
    relaxed = {r: 9 * n for r, n in local.items()}
    relaxed[51] = Fraction(idle_mass, 51)
    cap_lower, cap_upper = root.kappa_from_profile(relaxed, 1)
    rw.need(upper < cap_lower, "favorable packing ceiling, not a feasible invoice")
    return {
        "maximum_idle_rank": 51,
        "idle_mass_per_call": "2093",
        "root": [str(cap_lower), str(cap_upper)],
        "fraction_realized": [str(lower / cap_upper), str(upper / cap_lower)],
        "scope": (
            "Coverage/halving relaxation in the moment variable; "
            "not a packing construction."
        ),
    }


def run(work):
    authenticate()
    sys.dont_write_bytecode = True
    sys.pycache_prefix = str(work / "module-bytecode")
    frames = load(PARENT / "vendor/preload_move.py", "source_bound_frames")
    reports = {}
    for variant in ("base", "extra"):
        candidates = words(variant, frames)
        expected_restore = restore_matrix(candidates["parent"])
        rw.need(
            all(
                restore_matrix(word) == expected_restore for word in candidates.values()
            ),
            "all literal restore operators agree on every scalar input",
        )
        reports[variant] = {
            name: audit(word, variant + "-" + name, work)
            for name, word in candidates.items()
        }
        reports[variant]["restore_matrix_sha256"] = canonical(
            [sorted((c, str(x)) for c, x in row.items()) for row in expected_restore]
        )
        reports[variant]["controls"] = controls(
            candidates["R1R2"], candidates["parent"], variant, work
        )
        before, entrance = frame_trace.census(candidates["R1"])
        after, new_entrance = frame_trace.census(candidates["R1R2"])
        delta = {
            r: after.get(r, 0) - before.get(r, 0) for r in set(before) | set(after)
        }
        rw.need(
            {r: n for r, n in delta.items() if n} == {"1": -2, "2": 1},
            "separate four-register set-span census",
        )
        rw.need(entrance == new_entrance, "same restore-entry frames")
        reports[variant]["frame_census"] = {
            "R1": before,
            "R1R2": after,
            "restore_entry": entrance,
        }
    return {
        "status": "PASS_SHARED_RESTORE_FANIN",
        "variants": reports,
        "scalar_matrix": scalar_identity(),
        "moment": moment(),
        "scope": (
            "Finite exact words and full fixed-allocation moment; "
            "native/admission release is separate."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--work", type=Path, help="fresh external directory; retained on failure"
    )
    parser.add_argument(
        "--record",
        action="store_true",
        help="write evidence/FINITE.json after validation",
    )
    args = parser.parse_args()
    if args.work:
        work = args.work.resolve()
        rw.need(
            not work.exists() and not work.is_relative_to(ROOT),
            "fresh external work directory",
        )
        work.mkdir(parents=True)
        result = run(work)
        save(work / "RESULT.json", result)
    else:
        with tempfile.TemporaryDirectory(prefix="shared-restore-") as directory:
            result = run(Path(directory))
    result = json.loads(json.dumps(result, sort_keys=True))
    if args.record:
        (PACKAGE / "evidence").mkdir(exist_ok=True)
        save(PACKAGE / "evidence/FINITE.json", result)
    else:
        rw.need(
            result == read(PACKAGE / "evidence/FINITE.json"),
            "published deterministic evidence",
        )
    print(result["status"], "local=2441,708,232,108,18,8 controls=16", flush=True)


if __name__ == "__main__":
    main()
