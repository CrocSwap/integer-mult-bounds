"""Exact bounded-accumulator lowering of the selected complex scalar words.

Prepared for Seb (@ZK-Snarky) with substantial OpenAI Codex assistance.
Apache-2.0. The primitive vocabulary is from icekylinx's PR425/433/531
lineage. Copy-Horner/unit lowering and the sparse replay structure follow
Sagar Thakrar's PR696 (5a3f983715027c4fd83f50bc9001d4b18463bed1).
The two target-accumulation circuits and their prefix check are new here.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVIDERS = ROOT / "research/community-k492-audit/pr626/replay/mixed-global/base/providers"
WORK = ("W", 0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def power_two(n):
    return n > 0 and n & (n - 1) == 0


def shifts(register, exponent):
    return [("double" if exponent > 0 else "halve", register)] * abs(exponent)


@lru_cache(maxsize=None)
def addition(q):
    """Choose the shortest of three explicit circuits, keeping Horner on ties.

    Abstract registers T/S/W are target/source/private coefficient work.
    Every candidate has exact endpoint T += q*S, S unchanged, W = 0.
    """
    a, b = abs(q.numerator), q.denominator
    require(a and power_two(b), "addition requires a nonzero dyadic")
    accumulate = "add" if q > 0 else "subtract"
    if a == b:
        return "unit", ((accumulate, "T", "S"), ("clear", "W"))
    k, d = a.bit_length() - 1, b.bit_length() - 1
    horner = [("copy", "W", "S")]
    for bit in bin(a)[3:]:
        horner.append(("double", "W"))
        if bit == "1":
            horner.append(("add", "W", "S"))
    horner += shifts("W", -d) + [(accumulate, "T", "W"), ("clear", "W")]

    # Descending positive binary summands: every target prefix lies in [0,q]
    # (or [q,0]) and the work never exceeds the leading power of two.
    binary = [("copy", "W", "S")] + shifts("W", k - d)
    for i in range(k, -1, -1):
        if a >> i & 1:
            binary.append((accumulate, "T", "W"))
        if i:
            binary.append(("halve", "W"))
    binary.append(("clear", "W"))

    # Non-adjacent signed digits. Split a too-large leading work value into
    # two visits to its half; this matters for integral coefficients only.
    digits, n = [], a
    while n:
        digit = 2 - n % 4 if n & 1 else 0
        digits.append(digit)
        n = (n - digit) // 2
    if 1 << (len(digits) - 1) > a * b:
        top = digits.pop()
        digits[-1] += 2 * top
    signed = [("copy", "W", "S")] + shifts("W", -d)
    for i, digit in enumerate(digits):
        operation = "add" if (digit > 0) == (q > 0) else "subtract"
        signed += [(operation, "T", "W")] * abs(digit)
        if i + 1 < len(digits):
            signed.append(("double", "W"))
    signed.append(("clear", "W"))
    candidates = (("horner", horner), ("binary_descending", binary),
                  ("signed_ascending", signed))
    method, word = min(candidates, key=lambda item: len(item[1]))
    return method, tuple(word)


def lower(op, work=WORK):
    """Lower one scalar macro; caller executes all primitives at its frame."""
    tag, target = op[0], tuple(op[1])
    require(target != work, "work aliases target")
    if tag == "clear":
        return "clear", [("clear", target)]
    if tag == "scale":
        q = Q(op[2], op[3])
        require(power_two(abs(q.numerator)) and power_two(q.denominator),
                "scale requires a signed power of two")
        word = shifts(target, abs(q.numerator).bit_length() - q.denominator.bit_length())
        return "scale", word + ([("negate", target)] if q < 0 else [])
    require(tag in ("add", "copy"), "unknown macro")
    source = tuple(op[2])
    require(source not in (target, work), "source aliases target or work")
    if tag == "copy":
        return "copy", [("copy", target, source)]
    method, word = addition(Q(op[3], op[4]))
    registers = {"T": target, "S": source, "W": work}
    return method, [(p[0], *(registers[r] for r in p[1:])) for p in word]


def step(rows, op):
    """Exact sparse row interpreter; executes primitives, not scalar macros."""
    tag, target = op[:2]
    if tag == "clear":
        rows[target] = {}
    elif tag == "copy":
        rows[target] = rows[op[2]].copy()
    elif tag in ("double", "halve", "negate"):
        q = {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag]
        rows[target] = {j: q * x for j, x in rows[target].items()}
    elif tag in ("add", "subtract"):
        for j, x in list(rows[op[2]].items()):
            value = rows[target].get(j, Q(0)) + (x if tag == "add" else -x)
            if value:
                rows[target][j] = value
            else:
                rows[target].pop(j, None)
    else:
        raise ValueError("unknown primitive")


def check_addition(q, word):
    """Independently check arbitrary T,S,W and the reference prefix envelope."""
    rows = {r: {r: Q(1)} for r in ("T", "S", "W")}
    for primitive in word:
        step(rows, primitive)
        require(rows["S"] == {"S": Q(1)}, "source changed")
        t, w = rows["T"], rows["W"]
        require(t.get("T") == 1 and set(t) <= {"T", "S"}
                and abs(t.get("S", 0)) <= abs(q), "target prefix envelope")
        require(w == {"W": Q(1)} or
                (set(w) <= {"S"} and abs(w.get("S", 0)) <= abs(q.numerator)),
                "work prefix envelope")
    require(rows == {"T": {"T": Q(1), "S": q}, "S": {"S": Q(1)}, "W": {}},
            "endpoint or dirty-work cleanup")


def baseline_count(op):
    if op[0] in ("clear", "copy"):
        return 1
    q = Q(op[3], op[4]) if op[0] == "add" else Q(op[2], op[3])
    a, b = abs(q.numerator), q.denominator
    if op[0] == "scale":
        return abs(a.bit_length() - b.bit_length()) + int(q < 0)
    return 3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def controls():
    q = Q(63, 8)
    _, word = addition(q)
    word = list(word)
    mutations = {
        "missing_cleanup": word[:-1],
        "dirty_source_copy_omitted": word[1:],
        "wrong_accumulation_sign": [
            ("add", *p[1:]) if p[0] == "subtract" else p for p in word],
        "endpoint_neutral_source_growth": [("double", "S"), ("halve", "S")] + word,
        "endpoint_neutral_target_growth": [("add", "T", "S")] * 8
            + [("subtract", "T", "S")] * 8 + word,
        "endpoint_neutral_work_growth": [("copy", "W", "S")]
            + [("double", "W")] * 6 + [("halve", "W")] * 6 + word,
    }
    rejected = []
    for name, mutant in mutations.items():
        try:
            check_addition(q, mutant)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("accepted mutation: " + name)
    for name, op in {
        "nondyadic": ["add", ["T", 0], ["S", 0], 1, 3],
        "zero_coefficient": ["add", ["T", 0], ["S", 0], 0, 1],
        "source_alias": ["add", ["T", 0], ["T", 0], 1, 1],
        "work_alias": ["add", ["T", 0], list(WORK), 1, 1],
    }.items():
        try:
            lower(op)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("accepted invalid macro: " + name)
    return rejected


def replay(events, checks, inherited, orientation):
    n, v = 716, 112
    rows = {("L", r): {r: Q(1)} for r in range(n)}
    rows[WORK] = {n: Q(1)}
    paid, methods, primitives, coefficients = Counter(), Counter(), Counter(), set()
    original = predecessor = macro_count = 0
    circuit_hash = hashlib.sha256()
    for event in events:
        if event[0] == "climb":
            paid[event[5]] += 1
        elif event[0] == "center":
            paid[event[4]] += 1
        elif event[0] == "scalar":
            op, frame = event[1:]
            method, word = lower(op)
            methods[method] += 1
            macro_count += 1
            old = baseline_count(op)
            original += 2 * old
            predecessor += 2 * old
            if op[0] == "add":
                q = Q(op[3], op[4])
                coefficients.add(q)
                predecessor -= 2 * (1 + (abs(q) == 1))
            rows.setdefault(tuple(op[1]), {})
            for primitive in word:
                step(rows, primitive)
                primitives[primitive[0]] += 2
                circuit_hash.update(json.dumps([frame, primitive], separators=(",", ":")).encode() + b"\n")
            if op[0] == "add":
                require(not rows[WORK], "private coefficient work survived")
        else:
            require(event[0] in ("phase", "adapter", "residual_adapter"), "unknown event")
    for r in range(n):
        expected = {r: Q(1)}
        if orientation == "forward" and v <= r < 2 * v:
            expected[r - v] = Q(1)
        if orientation == "backward" and r < v:
            expected[r + v] = Q(-1)
        require(rows[("L", r)] == expected, "full arbitrary-input endpoint at " + str(r))
    require(all(not row for r, row in rows.items() if r[0] != "L"), "private work not zero")
    require(original == checks["real_component_primitive_bound"], "original primitive count")
    require(macro_count == checks["scalar_macros"], "scalar count")
    require(dict(paid) == {int(k): v for k, v in checks["paid_profile"].items()}, "paid profile")
    total = sum(primitives.values())
    return {
        "original_real_primitives": original,
        "pr696_real_primitives": predecessor,
        "new_real_primitives": total,
        "saved_vs_pr696": predecessor - total,
        "saved_vs_original": original - total,
        "all_input_columns": n,
        "extra_dirty_work_column": 1,
        "scalar_macros": macro_count,
        "methods": dict(sorted(methods.items())),
        "primitives": dict(sorted(primitives.items())),
        "primitive_word_sha256": circuit_hash.hexdigest(),
        "paid_profile": {str(k): v for k, v in sorted(paid.items())},
        "inherited_prefix_l1_upper": inherited["prefix_l1_upper"],
        "charged_payload_bits": inherited["charged_payload_bits"],
    }, coefficients


def certificate():
    pins = read(HERE / "SOURCES.json")
    for name, expected in pins["files"].items():
        path = ROOT / name
        data = path.read_bytes()
        if path.suffix == ".gz":
            data = gzip.decompress(data)
        require(digest(data) == expected, "source pin: " + name)
    results, coefficients = {}, set()
    for provider in ("ck", "jp8"):
        directory = PROVIDERS / provider
        programs = read(directory / "LOCAL-PROGRAMS.json.gz")
        checks = read(directory / "LOCAL-CHECKS.json")
        inherited = read(directory / "INDEPENDENT-LOCAL-REPLAY.json")
        for orientation in ("forward", "backward"):
            events = programs[orientation]
            require(digest(json.dumps(events, sort_keys=True, separators=(",", ":")).encode())
                    == checks[orientation]["sha256"], "program semantic hash")
            key = provider + "/" + orientation
            results[key], used = replay(events, checks[orientation],
                                       inherited["local"][orientation], orientation)
            coefficients.update(used)
    for q in sorted(coefficients):
        _, word = addition(q)
        check_addition(q, word)
    return {"status": "PASS_COMPLEX_COEFFICIENT_ACCUMULATION", "programs": results,
            "distinct_coefficients": len(coefficients), "controls": controls()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", type=Path, help="write to a NEW file instead of checking EXPECTED.json")
    args = parser.parse_args()
    result = certificate()
    if args.write_certificate:
        with args.write_certificate.open("x") as out:
            out.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(result == read(HERE / "EXPECTED.json"), "expected certificate differs")
    savings = ",".join(str(p["saved_vs_pr696"]) for p in result["programs"].values())
    print(f"PASS_COMPLEX_COEFFICIENT_ACCUMULATION programs=4 columns=716 extra_savings={savings} controls={len(result['controls'])}")
