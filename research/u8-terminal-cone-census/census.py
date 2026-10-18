"""Exact necessary terminal cones for the frozen U8 scalar prefix.

Standalone diagnostic; no supplier construction or exponent certificate.
Credits icekylinx's arbitrary-dirt auditor and the PR591/604/635 cold-end
criterion retained by Jeremy Kothe's PR869/870 U8. Apache-2.0.
Prepared for ToikY with substantial OpenAI Codex assistance.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import time

WORD_SHA = "090fd574747fbf9628e70cb9beb792732914cfa52e1df147579fe4dbccc68c5a"
FULL = (256, 128, 64, 32, 16, 8, 4, 2, 1)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def span(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            bit = vector.bit_length() - 1
            if bit in pivots:
                vector ^= pivots[bit]
            else:
                pivots[bit] = vector
                break
    for bit in sorted(pivots):
        for high in pivots:
            if high > bit and (pivots[high] >> bit) & 1:
                pivots[high] ^= pivots[bit]
    return tuple(pivots[bit] for bit in sorted(pivots, reverse=True))


def included(small, large):
    return span(small + large) == large


def touched(gate):
    return gate[1:3] if gate[0] == "add" else gate[1:2]


def execute(gates, rows, inverse=False):
    sequence = reversed(gates) if inverse else gates
    for gate in sequence:
        kind = gate[0]
        if kind == "add":
            target, source = gate[1:3]
            require(target != source, "self addition")
            coefficient = Fraction(gate[3], gate[4]) * (-1 if inverse else 1)
            for column, value in list(rows[source].items()):
                total = rows[target].get(column, 0) + coefficient * value
                if total:
                    rows[target][column] = total
                else:
                    rows[target].pop(column, None)
        elif kind == "scale":
            coefficient = Fraction(gate[2], gate[3])
            require(coefficient != 0, "zero scale")
            if inverse:
                coefficient = 1 / coefficient
            rows[gate[1]] = {k: coefficient * v for k, v in rows[gate[1]].items()}
        else:
            raise ValueError("unknown primitive")
    return rows


def identity(size):
    return [{i: Fraction(1)} for i in range(size)]


def compute(word):
    v, h, helpers = (word["report"][k] for k in ("v", "h", "R"))
    require((v, h, helpers) == (112, 9, 504), "wrong U8 geometry")
    size = 2 * v + helpers
    core = word["A"] + word["cut"] + word["B"]
    raw = execute(core, identity(size))
    response = [{} for _ in range(size)]
    for target in range(v, 2 * v):
        response[target] = {k: a for k, a in raw[target].items() if k >= 2 * v}
    execute(word["precondition"], response)
    compensation = [
        ["add", target, helper, -value.numerator, value.denominator, []]
        for target in range(v, 2 * v)
        for helper, value in sorted(response[target].items())
    ]
    prefix = word["precondition"] + compensation + core
    forward = execute(prefix, identity(size))
    inverse = execute(prefix, identity(size), inverse=True)
    # Replaying the inverse on the actual forward state checks all columns.
    require(execute(prefix, [dict(row) for row in forward], inverse=True) == identity(size),
            "prefix inverse does not restore every arbitrary input")
    start = [(port,) for port in word["ports"]] + [()] * (v + helpers)
    for q, frame in word.get("start_extra", {}).items():
        start[int(q)] = span(frame)
    end = [FULL] * v + [
        span(x for x in range(1, 512) if (x & port).bit_count() % 2 == 0)
        for port in word["ports"]
    ] + [FULL] * helpers
    for q, frame in word.get("helper_final", {}).items():
        end[int(q)] = span(frame)
    current = list(start)
    paid = Counter()

    def climb(q, frame):
        frame = span(frame)
        require(included(current[q], frame), "nonmonotone frame")
        delta = len(frame) - len(current[q])
        if delta:
            paid[delta] += 1
        current[q] = frame

    for section in ("A", "B"):
        if section == "B":
            levels = {int(q): span(frame) for q, frame in word.get("target_levels", {}).items()}
            require(all(current[v + q] == levels.get(q, ()) for q in range(v)), "target boundary")
            for carrier, frame in zip(word["centers"], word["center_frames"]):
                frame = span(frame)
                require(current[carrier] == frame, "center boundary")
                served = {levels.get(g[1] - v, ()) for g in word["cut"] if g[2] == carrier}
                for target_frame in sorted(served, key=lambda f: -len(f)):
                    require(included(target_frame, frame), "center nesting")
                    if frame != target_frame:
                        paid[len(frame) - len(target_frame)] += 1
                    frame = target_frame
        for gate in word[section]:
            for q in touched(gate):
                climb(q, gate[-1])
    end_b = list(current)
    prefix_paid = paid.copy()
    early = word.get("early_cleanup", [])
    early_indices = {i for i, _ in early}
    require(len(early_indices) == len(early), "duplicate early cleanup")
    tail = [word["cleanup"][i][:-1] + [frame] for i, frame in early]
    cleanup = [g for i, g in enumerate(word["cleanup"]) if i not in early_indices]
    for gate in tail:
        for q in touched(gate):
            climb(q, gate[-1])
    for q, frame in enumerate(end):
        climb(q, frame)
    require(dict(paid) == {int(k): n for k, n in word["report"]["local_profile"].items()}, "paid profile")
    require(all(end[q] == FULL for g in cleanup for q in touched(g)), "FULL cleanup access")
    complete = execute(tail + cleanup, [dict(row) for row in forward])
    expected = identity(size)
    for q in range(v):
        expected[v + q][q] = Fraction(1)
    require(complete == expected, "complete arbitrary-dirt endpoint")
    records = []
    dirt_rows = {q: [] for q in range(2 * v, size)}
    for row, coefficients in enumerate(forward):
        for q in coefficients:
            if q >= 2 * v and row != q:
                dirt_rows[q].append(row)
    for q in range(2 * v, size):
        required = sorted(set(inverse[q]) | set(dirt_rows[q]) | {q})
        row_frame = span(vector for k in set(inverse[q]) | {q} for vector in end_b[k])
        minimal = span(vector for k in required for vector in end_b[k])
        require(included(minimal, end[q]), "current endpoint violates necessary cones")
        records.append({
            "helper": q - 2 * v, "register": q,
            "start_frame": list(start[q]), "end_b_frame": list(end_b[q]),
            "current_terminal_frame": list(end[q]), "minimal_necessary_terminal_frame": list(minimal),
            "row_and_monotonicity_minimum": list(row_frame),
            "row_only_dimension_slack": len(end[q]) - len(row_frame),
            "inverse_row_support": sorted(inverse[q]), "dirt_column_support": dirt_rows[q],
            "current_width": len(end[q]) - len(start[q]),
            "minimal_necessary_width": len(minimal) - len(start[q]),
            "terminal_dimension_slack": len(end[q]) - len(minimal),
            "full_cleanup_incidence": sum(q in touched(g) for g in cleanup),
            "column_blockers_for_row_minimum": [k for k in dirt_rows[q] if not included(end_b[k], row_frame)],
        })
    return {
        "status": "PASS_EXACT_NECESSARY_U8_TERMINAL_CONE_CENSUS",
        "helper_count": helpers, "arbitrary_input_columns": size,
        "compensation_gates": len(compensation), "prefix_gates": len(prefix),
        "local_profile": dict(sorted(paid.items())),
        "fixed_prefix_paid_profile": dict(sorted(prefix_paid.items())),
        "actual_old_suffix_paid_profile": dict(sorted((paid - prefix_paid).items())),
        "all_register_minimal_one_jump_suffix_profile": dict(sorted(Counter(
            len(end[q]) - len(end_b[q]) for q in range(size) if end[q] != end_b[q]
        ).items())),
        "current_width_inventory": dict(sorted(Counter(r["current_width"] for r in records).items())),
        "necessary_width_inventory": dict(sorted(Counter(r["minimal_necessary_width"] for r in records).items())),
        "dimension_slack_histogram": dict(sorted(Counter(r["terminal_dimension_slack"] for r in records).items())),
        "row_only_dimension_slack_histogram": dict(sorted(Counter(r["row_only_dimension_slack"] for r in records).items())),
        "row_only_candidates": [r["helper"] for r in records if r["row_only_dimension_slack"]],
        "candidates": [r["helper"] for r in records if r["terminal_dimension_slack"]],
        "records": records,
        "scope": "Necessary cones for the fixed compensated scalar prefix and end-B frames under monotone equal-common-frame invertible ADD/nonzero SCALE cleanup on the same arbitrary dirty registers. No added COPY/ERASE/clean scratch or frame reset. This excludes smaller helper endpoints; it does not exclude cheaper tails at unchanged endpoints, changed prefix/end-B or other interfaces. No new exponent or full theorem claim.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), "refusing to overwrite output")
    start = time.monotonic()
    raw = gzip.decompress(args.word.read_bytes())
    require(hashlib.sha256(raw).hexdigest() == WORD_SHA, "frozen word pin")
    result = compute(json.loads(raw))
    result["word_content_sha256"] = WORD_SHA
    result["seconds"] = time.monotonic() - start
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "records"}, indent=2))


if __name__ == "__main__":
    main()
