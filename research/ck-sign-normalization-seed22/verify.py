"""Reproduce the complete historical CK sign-normalization census, offline.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVIDER = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck/"
INPUTS = (
    "research/complex-dyadic-lowering/lower.py",
    PROVIDER + "LOCAL-PROGRAMS.json.gz",
    PROVIDER + "LOCAL-CHECKS.json",
    PROVIDER + "INDEPENDENT-LOCAL-REPLAY.json",
)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def source_check():
    pins = read(HERE / "SOURCE-PINS.json")
    require(set(pins["files"]) == set(INPUTS), "source inventory differs")
    for name in INPUTS:
        data = (ROOT / name).read_bytes()
        if name.endswith(".gz"):
            data = gzip.decompress(data)
        require(digest(data) == pins["files"][name], "source pin: " + name)
    return pins


def segments(events):
    """Every scalar run is bounded by any event or any literal frame change."""
    run, start, frame = [], 0, None
    for index, event in enumerate(events):
        if event[0] != "scalar" or event[2] != frame:
            if run:
                yield start, frame, run
                run = []
            frame = None
        if event[0] == "scalar":
            if not run:
                start, frame = index, event[2]
            run.append(event)
    if run:
        yield start, frame, run


def step(rows, op):
    tag, target = op[:2]
    if tag == "clear":
        rows[target] = {}
    elif tag == "copy":
        rows[target] = dict(rows[op[2]])
    elif tag in ("double", "halve", "negate"):
        factor = {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag]
        rows[target] = {key: factor * value for key, value in rows[target].items()}
    elif tag in ("add", "subtract"):
        factor = 1 if tag == "add" else -1
        for key, value in list(rows[op[2]].items()):
            new = rows[target].get(key, Q(0)) + factor * value
            if new:
                rows[target][key] = new
            else:
                rows[target].pop(key, None)
    else:
        raise ValueError("unknown primitive: " + tag)


def replay(events, checks, lower, optimize, orientation):
    require(digest(canonical(events)) == checks["sha256"], "event semantic digest")
    runs = list(segments(events))
    registers = {("L", i) for i in range(716)} | {("W", 0)}
    for _, _, run in runs:
        for event in run:
            for primitive in lower(event[1]):
                registers.update(primitive[1:])
    rows = [{register: {register: Q(1)} for register in registers} for _ in range(2)]
    peaks, depths, counts = [Q(1), Q(1)], [0, 0], [Counter(), Counter()]
    streams = [hashlib.sha256(), hashlib.sha256()]
    changed, gains = [], Counter()
    macro_count = 0
    for start, frame, run in runs:
        original = [p for event in run for p in lower(event[1])]
        candidate = optimize(original)
        macro_count += len(run)
        touched = {reg for p in original for reg in p[1:]}
        for version, word in enumerate((original, candidate)):
            for primitive in word:
                step(rows[version], primitive)
                counts[version][primitive[0]] += 1
                streams[version].update(canonical([frame, primitive]) + b"\n")
                row = rows[version][primitive[1]]
                peaks[version] = max(peaks[version], sum(map(abs, row.values()), Q(0)))
                depths[version] = max(depths[version], max(
                    (x.denominator.bit_length() - 1 for x in row.values()), default=0))
        require(all(rows[0][reg] == rows[1][reg] for reg in touched),
                "boundary mismatch at event " + str(start))
        saving = 2 * (len(original) - len(candidate))
        gains[saving] += 1
        if saving:
            changed.append({"start_event": start, "scalar_macros": len(run), "frame": frame,
                            "baseline_real_primitives": 2 * len(original),
                            "candidate_real_primitives": 2 * len(candidate),
                            "real_saved": saving,
                            "baseline_negations_per_component": sum(p[0] == "negate" for p in original),
                            "boundary_negations_per_component": sum(p[0] == "negate" for p in candidate)})
    require(macro_count == checks["scalar_macros"], "incomplete scalar coverage")
    require(peaks[0] == peaks[1] and depths[0] == depths[1], "prefix envelope increased")
    require(rows[0] == rows[1], "whole scalar map differs")
    for r in range(716):
        expected = {("L", r): Q(1)}
        if orientation == "forward" and 112 <= r < 224:
            expected[("L", r - 112)] = Q(1)
        if orientation == "backward" and r < 112:
            expected[("L", r + 112)] = Q(-1)
        require(rows[1][("L", r)] == expected, "whole scalar shear or restoration differs")
    require(all(not row for reg, row in rows[1].items() if reg[0] != "L"), "private work not cleared")
    non_scalar = [e for e in events if e[0] != "scalar"]
    paid = Counter()
    for event in non_scalar:
        if event[0] == "climb":
            paid[event[5]] += 1
        elif event[0] == "center":
            paid[event[4]] += 1
    require({str(k): v for k, v in paid.items()} == checks["paid_profile"], "paid profile differs")
    return {
        "formal_input_columns": len(registers), "logical_columns": 716,
        "private_input_columns": len(registers) - 716,
        "events": len(events), "scalar_macros": macro_count, "runs": len(runs),
        "non_scalar_events": len(non_scalar), "non_scalar_sha256": digest(canonical(non_scalar)),
        "baseline_real_primitives": 2 * sum(counts[0].values()),
        "candidate_real_primitives": 2 * sum(counts[1].values()),
        "real_saved": 2 * (sum(counts[0].values()) - sum(counts[1].values())),
        "baseline_tags_per_component": dict(sorted(counts[0].items())),
        "candidate_tags_per_component": dict(sorted(counts[1].items())),
        "baseline_primitive_sha256": streams[0].hexdigest(),
        "candidate_primitive_sha256": streams[1].hexdigest(),
        "prefix_row_l1_max": [str(x) for x in peaks], "fractional_bits_max": depths,
        "paid_profile": checks["paid_profile"],
        "run_savings_census": {str(k): v for k, v in sorted(gains.items())},
        "changed_runs": changed,
    }


def verify():
    pins = source_check()
    lower = module("ck_sign_baseline", ROOT / INPUTS[0]).lower
    optimize = module("ck_sign_compiler", HERE / "compile.py").optimize_run
    programs = read(ROOT / INPUTS[1])
    checks = read(ROOT / INPUTS[2])
    require(set(programs) == {"forward", "backward"}, "orientation coverage")
    results = {direction: replay(programs[direction], checks[direction], lower, optimize, direction)
               for direction in ("forward", "backward")}
    return {"status": "PASS_CK_SIGN_NORMALIZATION", "base_commit": pins["base_commit"],
            "assignment_seed": 22, "kappa": "unchanged", "programs": results}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new receipt during development")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.write:
        with args.write.open("x") as file:
            file.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(canonical(result) == canonical(read(HERE / "EXPECTED.json")), "expected receipt mismatch")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        rows = [result["programs"][d] for d in ("forward", "backward")]
        print("PASS_CK_SIGN_NORMALIZATION runs=" + "+".join(str(r["runs"]) for r in rows)
              + " saved=" + "/".join(str(r["real_saved"]) for r in rows) + " kappa=unchanged")
