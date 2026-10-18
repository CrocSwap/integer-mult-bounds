"""Exact boundary checks for sign normalization of the selected PR1042 word.

Scratch-net, with substantial OpenAI Codex assistance. Apache-2.0.
Construction: Ross Richardson's retained lazy-sign compiler.
Primitive lowering: Sagar Thakrar's retained PR696 implementation.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVIDER = "slots/local/"
INPUTS = (
    "research/complex-dyadic-lowering/lower.py",
    "research/ck-sign-normalization-seed22/compile.py",
    "research/community-frontier1042-audit/selected-replay.tar.gz",
    "research/community-frontier1042-audit/RESULT.json",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def source_check(root=ROOT):
    pins = read(HERE / "SOURCE-PINS.json")
    context = pins["selected_context"]
    context_path = HERE / context["path"]
    require(digest(context_path.read_bytes()) == context["sha256"], "selected context pin differs")
    selected = read(context_path)
    require(selected["kappa"] == context["kappa"] and
            selected["audited_source_head"] == context["audited_source_head"], "selected context differs")
    require(set(pins["files"]) == set(INPUTS), "source inventory differs")
    for name in INPUTS:
        data = (root / name).read_bytes()
        pin = pins["files"][name]
        require(pin["representation"] == "file bytes",
                "source representation differs: " + name)
        require(digest(data) == pin["sha256"], "source pin differs: " + name)
    return pins


def selected_word_check(word, pins):
    require(digest(canonical(word)) == pins["selected_word_content_sha256"],
            "selected word content differs")


def selected_inputs(root=ROOT):
    """Read exact named members, never the retained R492 evidence directory."""
    pins = read(HERE / "SOURCE-PINS.json")
    receipt = read(root / INPUTS[3])
    selected = read(HERE / "BASE-SELECTED.json")
    require(receipt["selected_assembly_sha256"] == selected["certificate_sha256"],
            "selected assembly binding differs")
    values = {}
    with tarfile.open(root / INPUTS[2], "r:gz") as archive:
        for name, pin in pins["members"].items():
            members = [m for m in archive.getmembers() if m.name == name]
            require(len(members) == 1 and members[0].isfile(), "archive member missing or duplicated")
            data = archive.extractfile(members[0]).read()
            if name != "RESULT.json":
                require(digest(data) == receipt["artifacts"][name], "replay artifact binding differs")
            payload = gzip.decompress(data) if name.endswith(".gz") else data
            require(digest(payload) == pin["sha256"], "archive member payload differs: " + name)
            values[name] = json.loads(payload)
    require(canonical(values["RESULT.json"]) == canonical(receipt), "archive replay receipt differs")
    selected_word_check(values[PROVIDER + "FULL-WORD.json.gz"], pins)
    native = values[PROVIDER + "INDEPENDENT-LOCAL-REPLAY.json"]
    require(native["helpers"] == 480 and native["v"] == 112, "wrong ancestor helper count")
    require(native["local_programs_sha256"] == receipt["artifacts"][PROVIDER + "LOCAL-PROGRAMS.json.gz"],
            "native program binding differs")
    return values[PROVIDER + "LOCAL-PROGRAMS.json.gz"], values[PROVIDER + "LOCAL-CHECKS.json"]


def segments(events):
    """No sign state crosses a non-scalar event or a literal frame change."""
    start, frame, run = None, None, []
    for index, event in enumerate(events):
        if event[0] != "scalar" or event[2] != frame:
            if run:
                yield start, frame, run
                run = []
        if event[0] == "scalar":
            if not run:
                start, frame = index, event[2]
            run.append(event)
    if run:
        yield start, frame, run


def step(rows, instruction):
    tag, target = instruction[:2]
    if tag == "clear":
        rows[target] = {}
    elif tag == "copy":
        rows[target] = dict(rows[instruction[2]])
    elif tag in ("double", "halve", "negate"):
        factor = {"double": Fraction(2), "halve": Fraction(1, 2),
                  "negate": Fraction(-1)}[tag]
        rows[target] = {column: value * factor for column, value in rows[target].items()}
    elif tag in ("add", "subtract"):
        sign = 1 if tag == "add" else -1
        for column, value in list(rows[instruction[2]].items()):
            result = rows[target].get(column, Fraction(0)) + sign * value
            if result:
                rows[target][column] = result
            else:
                rows[target].pop(column, None)
    else:
        raise ValueError("unknown primitive: " + tag)


def identity(registers):
    return {reg: {reg: Fraction(1)} for reg in registers}


def endpoint_digest(rows):
    serialized = [[reg, [[col, value.numerator, value.denominator]
                         for col, value in sorted(row.items())]]
                  for reg, row in sorted(rows.items())]
    return digest(canonical(serialized))


def register_inventory(programs, lower):
    registers = set()
    for events in programs.values():
        for event in events:
            if event[0] == "scalar":
                for instruction in lower(event[1]):
                    registers.update(instruction[1:])
    logical = {("L", i) for i in range(704)}
    private = {("C", i) for i in range(8)} | {("W", 0)}
    require(registers == logical | private, "unexpected register inventory")
    return registers


def replay(events, checks, lower, optimize, registers):
    require(len(events) == checks["events"], "event count differs")
    require(digest(canonical(events)) == checks["sha256"], "event payload differs")
    totals = [Counter(), Counter()]
    streams = [hashlib.sha256(), hashlib.sha256()]
    full_rows = [identity(registers), identity(registers)]
    full_peaks, full_depths = [Fraction(1), Fraction(1)], [0, 0]
    boundary_hash = hashlib.sha256()
    access_hash = hashlib.sha256()
    gains, changed = Counter(), []
    macro_count, run_count = 0, 0
    for start, frame, run in segments(events):
        original = [p for event in run for p in lower(event[1])]
        candidate = optimize(original)
        def accesses(word):
            return [("update" if p[0] in ("add", "subtract") else p[0], *p[1:])
                    for p in word if p[0] != "negate"]
        require(accesses(original) == accesses(candidate), "non-negation access sequence differs")
        access_hash.update(canonical([start, frame, accesses(candidate)]) + b"\n")
        touched = {reg for instruction in original for reg in instruction[1:]}
        require(all(reg in touched for p in candidate for reg in p[1:]),
                "candidate added a register")
        # A fresh basis at EVERY run establishes substitution across opaque events.
        local_rows = [identity(touched), identity(touched)]
        local_peaks, local_depths = {}, {}
        for version, word in enumerate((original, candidate)):
            peaks = {reg: Fraction(1) for reg in touched}
            depths = {reg: 0 for reg in touched}
            for instruction in word:
                step(local_rows[version], instruction)
                step(full_rows[version], instruction)
                target = instruction[1]
                row = local_rows[version][target]
                peaks[target] = max(peaks[target], sum(map(abs, row.values()), Fraction(0)))
                depths[target] = max(depths[target], max(
                    (value.denominator.bit_length() - 1 for value in row.values()), default=0))
                row = full_rows[version][target]
                full_peaks[version] = max(full_peaks[version],
                                         sum(map(abs, row.values()), Fraction(0)))
                full_depths[version] = max(full_depths[version], max(
                    (value.denominator.bit_length() - 1 for value in row.values()), default=0))
                totals[version][instruction[0]] += 1
                streams[version].update(canonical([frame, instruction]) + b"\n")
            local_peaks[version], local_depths[version] = peaks, depths
        require(local_rows[0] == local_rows[1], "arbitrary-input run endpoint differs: " + str(start))
        require(local_peaks[0] == local_peaks[1], "run magnitude envelope differs: " + str(start))
        require(local_depths[0] == local_depths[1], "run denominator envelope differs: " + str(start))
        require(full_rows[0] == full_rows[1], "scalar projection boundary differs: " + str(start))
        endpoint = endpoint_digest(local_rows[1])
        boundary_hash.update(canonical([start, frame, len(run), endpoint]) + b"\n")
        saving = 2 * (len(original) - len(candidate))
        require(saving >= 0, "this word has a cost-increasing run: " + str(start))
        gains[saving] += 1
        if saving:
            changed.append({"start_event": start, "frame": frame, "scalar_macros": len(run),
                            "baseline_real_primitives": 2 * len(original),
                            "candidate_real_primitives": 2 * len(candidate),
                            "real_saved": saving, "endpoint_sha256": endpoint})
        macro_count += len(run)
        run_count += 1
    require(macro_count == checks["scalar_macros"], "scalar coverage differs")
    require(full_peaks[0] == full_peaks[1] and full_depths[0] == full_depths[1],
            "scalar projection envelope differs")
    for reg, row in full_rows[1].items():
        if reg[0] != "L":
            require(not row, "private work not erased in scalar projection")
    non_scalar = [[i, e] for i, e in enumerate(events) if e[0] != "scalar"]
    paid = Counter()
    for _, event in non_scalar:
        if event[0] == "climb":
            paid[event[5]] += 1
        elif event[0] == "center":
            paid[event[4]] += 1
    require({str(k): v for k, v in paid.items()} == checks["paid_profile"],
            "paid profile differs")
    # Negations alone disappear. Operand reads, shifts, clears and copies are identical in number.
    for tag in ("copy", "clear", "double", "halve"):
        require(totals[0][tag] == totals[1][tag], "non-sign primitive count differs")
    require(totals[0]["add"] + totals[0]["subtract"] ==
            totals[1]["add"] + totals[1]["subtract"], "source access count differs")
    return {
        "formal_input_columns": len(registers), "logical_columns": 704,
        "private_input_columns": 9, "events": len(events), "scalar_macros": macro_count,
        "runs": run_count, "boundary_maps_sha256": boundary_hash.hexdigest(),
        "non_negation_accesses_sha256": access_hash.hexdigest(),
        "non_scalar_events": len(non_scalar), "indexed_non_scalar_sha256": digest(canonical(non_scalar)),
        "baseline_real_primitives": 2 * sum(totals[0].values()),
        "candidate_real_primitives": 2 * sum(totals[1].values()),
        "real_saved": 2 * (sum(totals[0].values()) - sum(totals[1].values())),
        "baseline_tags_per_component": dict(sorted(totals[0].items())),
        "candidate_tags_per_component": dict(sorted(totals[1].items())),
        "baseline_primitive_sha256": streams[0].hexdigest(),
        "candidate_primitive_sha256": streams[1].hexdigest(),
        "scalar_projection_row_l1_max": [str(x) for x in full_peaks],
        "scalar_projection_fractional_bits_max": full_depths,
        "scalar_projection_endpoint_sha256": endpoint_digest(full_rows[1]),
        "paid_profile": dict(sorted(checks["paid_profile"].items())),
        "run_savings_census": {str(k): v for k, v in sorted(gains.items())},
        "changed_runs": changed,
    }


def verify():
    pins = source_check()
    lower = module("selected_sign_lower", ROOT / INPUTS[0]).lower
    optimize = module("selected_sign_compiler", ROOT / INPUTS[1]).optimize_run
    programs, checks = selected_inputs()
    require(set(programs) == {"forward", "backward"}, "orientation coverage differs")
    registers = register_inventory(programs, lower)
    results = {direction: replay(programs[direction], checks[direction], lower, optimize, registers)
               for direction in ("backward", "forward")}
    return {"status": "PASS_SELECTED_K8_SIGN_NORMALIZATION", "base_commit": pins["base_commit"],
            "assignment_seed": 38, "source_pr": 1042, "kappa": "unchanged", "programs": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new receipt; refuse an existing file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.write:
        with args.write.open("x") as file:
            file.write(json.dumps(result, sort_keys=True, indent=2) + "\n")
    else:
        require(canonical(result) == canonical(read(HERE / "EXPECTED.json")), "receipt differs")
    if args.json:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        p = result["programs"]
        print("PASS_SELECTED_K8_SIGN_NORMALIZATION runs=" + "+".join(str(p[d]["runs"]) for d in ("forward", "backward"))
              + " columns=713 saved=" + "/".join(str(p[d]["real_saved"]) for d in ("forward", "backward"))
              + " no_new_kappa")


if __name__ == "__main__":
    main()
