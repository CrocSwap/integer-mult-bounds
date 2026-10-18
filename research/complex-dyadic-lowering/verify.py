"""Replay four pinned PR626 scalar words with an explicit primitive lowering.

Sagar Thakrar, with substantial OpenAI Codex assistance. Apache-2.0.
Run from any directory with Python 3.11+; standard library only, no writes.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

from lower import lower

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVIDERS = ROOT / "research/community-k492-audit/pr626/replay/mixed-global/base/providers"
WORK = ("W", 0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def step(rows, op):
    """Sparse rational row interpreter, with no scalar-macro shortcut."""
    tag, target = op[:2]
    if tag == "clear":
        rows[target] = {}
    elif tag == "copy":
        rows[target] = rows[op[2]].copy()
    elif tag in ("double", "halve", "negate"):
        q = {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag]
        rows[target] = {j: q * x for j, x in rows[target].items()}
    elif tag in ("add", "subtract"):
        target_row = rows[target]
        for j, x in rows[op[2]].items():
            value = target_row.get(j, Q(0)) + (x if tag == "add" else -x)
            if value:
                target_row[j] = value
            else:
                target_row.pop(j, None)
    else:
        raise ValueError("unknown primitive")


def baseline_count(op):
    tag = op[0]
    if tag in ("clear", "copy"):
        return 1
    q = Q(op[3], op[4]) if tag == "add" else Q(op[2], op[3])
    a, b = abs(q.numerator), q.denominator
    if tag == "scale":
        return abs(a.bit_length() - b.bit_length()) + int(q < 0)
    return 3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1


def macro_check(q, circuit):
    """Arbitrary T,S,W columns and exact per-register prefix containment."""
    t, s = ("T", 0), ("S", 0)
    rows = {t: {0: Q(1)}, s: {1: Q(1)}, WORK: {2: Q(1)}}
    reference = [("clear", WORK)]
    for index, bit in enumerate(bin(abs(q.numerator))[2:]):
        if index:
            reference.append(("double", WORK))
        if bit == "1":
            reference.append(("add", WORK, s))
    reference.extend([("halve", WORK)] * (q.denominator.bit_length() - 1))
    reference.extend([("add" if q > 0 else "subtract", t, WORK), ("clear", WORK)])
    reference_rows = {register: row.copy() for register, row in rows.items()}
    seen = {register: {tuple(sorted(row.items()))} for register, row in rows.items()}
    for primitive in reference:
        step(reference_rows, primitive)
        for register, row in reference_rows.items():
            seen[register].add(tuple(sorted(row.items())))
    for primitive in circuit:
        step(rows, primitive)
        for register, row in rows.items():
            require(tuple(sorted(row.items())) in seen[register], "prefix row not in reference")
    require(rows == {t: {0: Q(1), 1: q}, s: {1: Q(1)}, WORK: {}},
            "macro endpoint or private clearing")
    expected = baseline_count(["add", list(t), list(s), q.numerator, q.denominator])
    expected -= 2 if abs(q) == 1 else 1
    require(len(circuit) == expected, "primitive count")


def negative_controls(coefficients):
    t, s = ["T", 0], ["S", 0]
    q = sorted(x for x in coefficients if abs(x) != 1)[22]
    op = ["add", t, s, q.numerator, q.denominator]
    word = lower(op)
    mutations = {
        "missing_cleanup": word[:-1],
        "missing_source_copy": word[1:],
        "wrong_sign": word[:-2] + [("subtract" if word[-2][0] == "add" else "add", *word[-2][1:])] + word[-1:],
        "redundant_work": [("clear", WORK)] + word,
    }
    # Grow a source beyond the allowed envelope, then restore it exactly.
    k = abs(q.numerator).bit_length() + 1
    mutations["endpoint_neutral_prefix_growth"] = (
        [("double", tuple(s))] * k + [("halve", tuple(s))] * k + word
    )
    unit = lower(["add", t, s, -1, 1])
    mutations["unit_dirty_work_not_cleared"] = unit[:-1]
    rejected = []
    for name, circuit in mutations.items():
        try:
            macro_check(Q(-1) if name.startswith("unit_") else q, circuit)
        except ValueError as error:
            if name == "endpoint_neutral_prefix_growth":
                require(str(error) == "prefix row not in reference", "prefix control failed for another reason")
            if name == "redundant_work":
                require(str(error) == "primitive count", "count control failed for another reason")
            rejected.append(name)
        else:
            raise ValueError("accepted negative control: " + name)
    for name, invalid in {
        "nondyadic": ["add", t, s, 1, 3],
        "zero_coefficient": ["add", t, s, 0, 1],
        "source_alias": ["add", t, t, 1, 1],
        "work_alias": ["add", t, list(WORK), 1, 1],
    }.items():
        try:
            lower(invalid)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("accepted invalid macro: " + name)
    return {"coefficient": str(q), "rejected": rejected}


def replay(provider, orientation, events, checks, inherited):
    n, v = 716, 112
    rows = {("L", r): {r: Q(1)} for r in range(n)}
    rows[WORK] = {n: Q(1)}
    env = {("L", r): Q(1) for r in range(n)}
    peak = Q(1)
    paid, primitive_tags = Counter(), Counter()
    baseline = macros = additions = units = 0
    coefficients = set()
    circuit_hash = hashlib.sha256()
    for event in events:
        if event[0] == "climb":
            paid[event[5]] += 1
        elif event[0] == "center":
            paid[event[4]] += 1
        elif event[0] != "scalar":
            require(event[0] in ("phase", "adapter", "residual_adapter"), "unknown event")
        else:
            op, frame = event[1:]
            tag, target = op[0], tuple(op[1])
            rows.setdefault(target, {})
            word = lower(op)
            baseline += 2 * baseline_count(op)
            macros += 1
            if tag == "add":
                source, q = tuple(op[2]), Q(op[3], op[4])
                coefficients.add(q)
                additions += 1
                units += abs(q) == 1
                # Old Horner attains this work bound. New work is a subsequence
                # of the old work states, or absent for a unit coefficient.
                peak = max(peak, abs(q.numerator) * env[source])
                env[target] = env.get(target, Q(0)) + abs(q) * env[source]
            elif tag == "scale":
                env[target] *= abs(Q(op[2], op[3]))
            elif tag == "clear":
                env[target] = Q(0)
            elif tag == "copy":
                env[target] = env[tuple(op[2])]
            peak = max(peak, env[target])
            for primitive in word:
                step(rows, primitive)
                primitive_tags[primitive[0]] += 2
                circuit_hash.update(json.dumps([frame, primitive], separators=(",", ":")).encode() + b"\n")
            if tag == "add":
                require(not rows[WORK], "coefficient work survived a macro")
    for r in range(n):
        expected = {r: Q(1)}
        if orientation == "forward" and v <= r < 2 * v:
            expected[r - v] = Q(1)
        if orientation == "backward" and r < v:
            expected[r + v] = Q(-1)
        require(rows[("L", r)] == expected, f"{provider}/{orientation} column map at {r}")
    require(all(not row for register, row in rows.items() if register[0] != "L"), "private registers not clear")
    require(baseline == checks["real_component_primitive_bound"], "baseline primitive receipt")
    require(macros == checks["scalar_macros"], "scalar macro count")
    require(dict(paid) == {int(k): value for k, value in checks["paid_profile"].items()}, "paid profile")
    require(peak == Q(inherited["prefix_l1_upper"]), "inherited prefix envelope")
    total = sum(primitive_tags.values())
    require(baseline - total == 2 * (additions + units), "closed-form savings")
    return {
        "all_input_columns": n,
        "dirty_helper_columns_restored": 492,
        "scalar_macros": macros,
        "additions": additions,
        "unit_additions": units,
        "baseline_real_primitives": baseline,
        "new_real_primitives": total,
        "saved_real_primitives": baseline - total,
        "primitive_tags": dict(sorted(primitive_tags.items())),
        "primitive_word_sha256": circuit_hash.hexdigest(),
        "paid_profile": {str(k): value for k, value in sorted(paid.items())},
        "retained_prefix_l1_upper": str(peak),
        "charged_payload_bits": inherited["charged_payload_bits"],
    }, coefficients


def verify():
    pins = read(HERE / "SOURCE-PINS.json")
    for name, expected in pins["files"].items():
        path = ROOT / name
        payload = gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_bytes()
        require(digest(payload) == expected, "source pin: " + name)
    results, coefficients = {}, set()
    for provider in ("ck", "jp8"):
        directory = PROVIDERS / provider
        programs = read(directory / "LOCAL-PROGRAMS.json.gz")
        checks = read(directory / "LOCAL-CHECKS.json")
        inherited = read(directory / "INDEPENDENT-LOCAL-REPLAY.json")
        require(set(programs) == {"forward", "backward"}, "program orientations")
        for orientation in ("forward", "backward"):
            events = programs[orientation]
            require(digest(json.dumps(events, sort_keys=True, separators=(",", ":")).encode()) == checks[orientation]["sha256"], "program semantic hash")
            key = provider + "/" + orientation
            results[key], used = replay(provider, orientation, events, checks[orientation], inherited["local"][orientation])
            coefficients.update(used)
    for q in coefficients:
        op = ["add", ["T", 0], ["S", 0], q.numerator, q.denominator]
        macro_check(q, lower(op))
    return {"status": "PASS_COMPLEX_DYADIC_LOWERING", "programs": results,
            "distinct_coefficients": len(coefficients), "controls": negative_controls(coefficients)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print the deterministic receipt")
    args = parser.parse_args()
    result = verify()
    require(result == read(HERE / "EXPECTED.json"), "expected receipt mismatch")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        savings = ",".join(str(x["saved_real_primitives"]) for x in result["programs"].values())
        print(f"PASS_COMPLEX_DYADIC_LOWERING programs=4 columns=716 savings={savings} controls={len(result['controls']['rejected'])}")
