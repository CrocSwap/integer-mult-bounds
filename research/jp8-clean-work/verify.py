"""Exact JP8 replay and complete finite local bill; standard library only.

faw01, with substantial OpenAI Codex assistance. Apache-2.0.
Primitive vocabulary and the comparator are Sagar Thakrar's PR696 work,
following icekylinx's scalar lineage and Jeremy Kothe's PR622 construction.
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
PROVIDER = ROOT / "research/community-k492-audit/pr626/replay/mixed-global/base/providers/jp8"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


optimizer = load_module("jp8_clean_work_lower", HERE / "lower.py")
WORK = optimizer.WORK


def require(condition, message):
    if not condition:
        raise ValueError(message)


def payload(path):
    data = path.read_bytes()
    return gzip.decompress(data) if path.suffix == ".gz" else data


def read(path):
    return json.loads(payload(path))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def normalize(shift, values):
    """Exact dyadic sparse row: integer numerators divided by 2**shift."""
    values = {column: value for column, value in values.items() if value}
    if not values:
        return 0, {}
    if shift:
        common = min(shift, min((abs(x) & -abs(x)).bit_length() - 1 for x in values.values()))
        if common:
            shift -= common
            values = {j: x >> common for j, x in values.items()}
    return shift, values


def execute(rows, primitive):
    """Literal primitive interpreter; never shortcuts a scalar macro."""
    tag, target = primitive[:2]
    shift, values = rows[target]
    if tag == "clear":
        result = (0, {})
    elif tag == "copy":
        source_shift, source = rows[primitive[2]]
        result = source_shift, source.copy()
    elif tag == "halve":
        result = normalize(shift + 1, values)
    elif tag == "double":
        result = normalize(shift - 1, values) if shift else (0, {j: 2*x for j, x in values.items()})
    elif tag == "negate":
        result = shift, {j: -x for j, x in values.items()}
    elif tag in {"add", "subtract"}:
        source_shift, source = rows[primitive[2]]
        denominator = max(shift, source_shift)
        combined = {j: x << (denominator - shift) for j, x in values.items()}
        sign = 1 if tag == "add" else -1
        for j, x in source.items():
            combined[j] = combined.get(j, 0) + sign * (x << (denominator - source_shift))
        result = normalize(denominator, combined)
    else:
        raise ValueError("unknown primitive")
    rows[target] = result
    return Q(sum(map(abs, result[1].values())), 1 << result[0])


def original_cost(op):
    if op[0] in {"clear", "copy"}:
        return 1
    q = Q(op[3], op[4]) if op[0] == "add" else Q(op[2], op[3])
    numerator, denominator = abs(q.numerator), q.denominator
    if op[0] == "scale":
        return abs(numerator.bit_length() - denominator.bit_length()) + (q < 0)
    return 3 + numerator.bit_length() - 1 + numerator.bit_count() + denominator.bit_length() - 1


def backward_witnesses(events):
    """Independent census: walk backward from each unit addition.

    Does not use the optimizer's forward state or its proposed witnesses.
    Non-scalar events, frame changes and W operands terminate an epoch.
    """
    result = []
    for i, event in enumerate(events):
        if event[0] != "scalar" or event[1][0] != "add":
            continue
        op, frame = event[1:]
        if abs(Q(op[3], op[4])) != 1:
            continue
        for j in range(i - 1, -1, -1):
            previous = events[j]
            if previous[0] != "scalar" or previous[2] != frame:
                break
            prior = previous[1]
            operands = [tuple(prior[1])]
            if prior[0] in {"add", "copy"}:
                operands.append(tuple(prior[2]))
            require(all(r[0] in {"L", "C"} for r in operands), "private operand in census")
            if prior[0] == "add":
                result.append([i, j])
                break
            require(prior[0] in {"scale", "copy", "clear"}, "unknown census macro")
    return result


def replay(orientation, events, checks, inherited, n, centers, macro_lower):
    rows = {("L", r): (0, {r: 1}) for r in range(n)}
    rows.update({("C", r): (0, {n+r: 1}) for r in range(centers)})
    rows[WORK] = (0, {n+centers: 1})
    env = {register: Q(1) for register in rows}
    positive_peak = actual_peak = Q(1)
    paid, tags, phase_savings = Counter(), Counter(), Counter()
    baseline = pr696 = count = macros = 0
    witnesses = []
    stream = hashlib.sha256()
    phase = "before_first_phase"
    for index, word, witness in optimizer.specialize(events, macro_lower):
        event = events[index]
        if event[0] != "scalar":
            stream.update((json.dumps(event, separators=(",", ":")) + "\n").encode())
            if event[0] == "phase":
                phase = event[1]
            elif event[0] == "climb":
                paid[event[5]] += 1
            elif event[0] == "center":
                paid[event[4]] += 1
            continue
        _, op, frame = event
        tag, target = op[0], tuple(op[1])
        reference = tuple(macro_lower(op, WORK))
        if witness is not None:
            require(rows[WORK] == (0, {}), "removed clear has dirty work")
            require(word == reference[:-1] and reference[-1] == ("clear", WORK), "changed more than a clear")
            witnesses.append([index, witness])
            phase_savings[phase] += 2
        else:
            require(word == reference, "unannounced primitive change")
        baseline += 2 * original_cost(op)
        pr696 += 2 * len(reference)
        macros += 1
        # Retain the original positive Horner envelope; deletion of an operation
        # on an already-zero register cannot increase any prefix value.
        if tag == "add":
            source, q = tuple(op[2]), Q(op[3], op[4])
            positive_peak = max(positive_peak, abs(q.numerator) * env[source])
            env[target] += abs(q) * env[source]
        elif tag == "scale":
            env[target] *= abs(Q(op[2], op[3]))
        elif tag == "clear":
            env[target] = Q(0)
        elif tag == "copy":
            env[target] = env[tuple(op[2])]
        positive_peak = max(positive_peak, env[target])
        for primitive in word:
            actual_peak = max(actual_peak, execute(rows, primitive))
            tags[primitive[0]] += 2
            count += 2
            stream.update((json.dumps(["primitive", frame, primitive], separators=(",", ":")) + "\n").encode())
        if tag == "add":
            require(rows[WORK] == (0, {}), "addition boundary work not zero")
    for r in range(n):
        expected = {r: 1}
        if orientation == "forward" and 112 <= r < 224:
            expected[r - 112] = 1
        elif orientation == "backward" and r < 112:
            expected[r + 112] = -1
        require(rows[("L", r)] == (0, expected), f"endpoint at logical register {r}")
    require(all(row == (0, {}) for reg, row in rows.items() if reg[0] != "L"), "private endpoint not zero")
    require(witnesses == backward_witnesses(events), "independent deletion census")
    require(baseline == checks["real_component_primitive_bound"], "original primitive count")
    require(macros == checks["scalar_macros"], "macro count")
    require(dict(paid) == {int(k): v for k, v in checks["paid_profile"].items()}, "paid profile")
    require(positive_peak == Q(inherited["prefix_l1_upper"]), "inherited positive prefix")
    require(actual_peak <= positive_peak < 2**inherited["charged_payload_bits"], "prefix allowance exceeded")
    require(pr696 - count == 2 * len(witnesses), "savings identity")
    return {
        "events": len(events), "scalar_macros": macros,
        "logical_columns": n, "arbitrary_private_columns": centers + 1,
        "original_real_primitives": baseline, "pr696_real_primitives": pr696,
        "new_real_primitives": count, "extra_saved_real_primitives": pr696 - count,
        "saved_vs_original": baseline - count, "removed_clears_per_real_component": len(witnesses),
        "omission_witness_sha256": digest(witnesses),
        "seed33_omission_sample": witnesses[33 % len(witnesses)],
        "emitted_stream_sha256": stream.hexdigest(), "primitive_tags": dict(sorted(tags.items())),
        "extra_savings_by_phase": dict(sorted(phase_savings.items())),
        "paid_profile": {str(k): v for k, v in sorted(paid.items())},
        "actual_prefix_l1_peak": str(actual_peak), "retained_positive_prefix_l1": str(positive_peak),
        "retained_prefix_bits": inherited["prefix_bits_upper"],
        "charged_payload_bits": inherited["charged_payload_bits"],
    }


def invoice(programs, canonical):
    m = 73
    n = 2 * canonical["v"] + canonical["R"]
    centers = len(canonical["centers"])
    values = list(programs.values())
    require(values[0]["paid_profile"] == values[1]["paid_profile"], "orientation profiles differ")
    children = sum(values[0]["paid_profile"].values())
    macros = max(p["scalar_macros"] for p in values)
    compiler = 64 * (m+1)**3
    adapters = 16 * (macros + children + n + centers) + 64*m
    reserve = adapters * compiler
    return {
        "m": m, "helpers": canonical["R"], "centers": centers,
        "native_columns": n, "paid_children": children, "maximum_scalar_macros": macros,
        "compiler": compiler, "local_adapters": adapters, "adapter_primitive_reserve": reserve,
        "original_local_primitive_bound": reserve + max(p["original_real_primitives"] for p in values),
        "pr696_local_primitive_bound": reserve + max(p["pr696_real_primitives"] for p in values),
        "new_local_primitive_bound": reserve + max(p["new_real_primitives"] for p in values),
        "scope": "Finite JP8 local invoice only; no regenerated global binding or exponent claim.",
    }


def verify():
    for name, expected in read(HERE / "SOURCE-PINS.json")["files"].items():
        require(hashlib.sha256(payload(ROOT / name)).hexdigest() == expected, "source pin: " + name)
    comparator = load_module("pr696_lower", ROOT / "research/complex-dyadic-lowering/lower.py")
    source, checks = read(PROVIDER / "LOCAL-PROGRAMS.json.gz"), read(PROVIDER / "LOCAL-CHECKS.json")
    inherited = read(PROVIDER / "INDEPENDENT-LOCAL-REPLAY.json")
    canonical = read(PROVIDER / "CANONICAL-WORD.json.gz")
    require((canonical["v"], canonical["R"], canonical["h"]) == (112, 492, 9), "provider geometry")
    require(set(source) == {"forward", "backward"}, "orientations")
    predecessor = read(ROOT / "research/complex-dyadic-lowering/EXPECTED.json")
    programs = {}
    for orientation in ("forward", "backward"):
        events = source[orientation]
        require(digest(events) == checks[orientation]["sha256"], "program identity")
        programs[orientation] = replay(orientation, events, checks[orientation], inherited["local"][orientation], 716, 8, comparator.lower)
        require(programs[orientation]["pr696_real_primitives"] == predecessor["programs"]["jp8/"+orientation]["new_real_primitives"], "PR696 comparator")
    coefficients = {Q(e[1][3], e[1][4]) for events in source.values()
                    for e in events if e[0] == "scalar" and e[1][0] == "add"}
    controls = load_module("jp8_clean_work_controls", HERE / "controls.py").run(optimizer, comparator, execute, require, coefficients)
    return {"status": "PASS_JP8_CLEAN_WORK", "programs": programs,
            "local_invoice": invoice(programs, canonical), "controls": controls}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print the checked deterministic receipt")
    args = parser.parse_args()
    result = verify()
    require(result == read(HERE / "EXPECTED.json"), "expected receipt mismatch")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        savings = ",".join(str(p["extra_saved_real_primitives"]) for p in result["programs"].values())
        print(f"PASS_JP8_CLEAN_WORK orientations=2 columns=716+9 extra_saved={savings} controls={len(result['controls']['rejected'])}")
