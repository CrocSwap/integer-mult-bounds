#!/usr/bin/env python3
"""Check the new rounded-read fiber; native zero preservation is a premise."""

import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = "research/p104-helper470-twin-rung-removal/WORD.json.gz"
SOURCE_SHA256 = "7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f"
COHORT = (
    118, 119, 120, 121, 122, 123, 126, 130, 134, 135, 137, 139,
    140, 141, 143, 150, 152, 156, 157, 158, 159, 160, 161, 162,
    163, 165, 167, 168, 172, 176, 177, 179, 180, 181, 182, 184,
    186, 188, 191, 194, 196, 200, 202, 204, 205, 207, 210, 211,
    214, 215, 216, 218, 219, 222, 223, 259, 289, 369, 506, 734,
)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_operations(raw):
    """Authenticate bytes before parsing the fixed, bounded source."""
    need(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, "source hash")
    word = json.loads(gzip.decompress(raw))
    need(word["public"] == 770 and word["owned_fields"] == 29, "field domain")
    need(len(word["program"]) == 22803, "event domain")
    operations = []
    for event in word["program"]:
        kind, dst = event[:2]
        need(kind in {"ADD", "SCALE", "COPY", "MOVE", "INIT", "CLEAR"}, "opcode")
        need(type(dst) is int and 0 <= dst < 799, "destination")
        src = event[2] if kind in {"ADD", "COPY"} else dst
        need(type(src) is int and 0 <= src < 799, "source")
        value = event[3] if kind == "ADD" else event[2] if kind == "SCALE" else "1"
        need(isinstance(value, str) and len(value) <= 32, "coefficient syntax")
        q = Fraction(value)
        need(0 < abs(q.numerator) <= 1024 and q.denominator <= 1024, "coefficient")
        operations.append((kind, dst, src, q.numerator, q.denominator))
    return operations


def find_cohort(operations):
    """Find fields with only silent fractional reads before a contraction."""
    cohort = []
    for field in range(770):
        for index, (kind, dst, src, p, d) in enumerate(operations):
            if kind == "SCALE" and dst == field:
                if abs(p) < d:
                    cohort.append((field, index))
                break
            if kind in {"COPY", "MOVE", "INIT", "CLEAR"} and dst == field:
                break
            if kind in {"ADD", "COPY"} and src == field and abs(p) >= d:
                break
    return cohort


def causal_certificate(operations, fields):
    """Check every event on all independent binary labels simultaneously."""
    need(len(fields) == len(set(fields)), "duplicate label")
    need(all(type(r) is int and 0 <= r < 770 for r in fields), "public labels")
    active = set(fields)
    kills, reads = [], []
    native_count = 0
    for index, (kind, dst, src, p, d) in enumerate(operations):
        if kind == "ADD" and src in active:
            need(abs(p) < d, "non-silent source read")
            reads.append((index, src, p, d))
        elif kind == "SCALE" and dst in active:
            need(abs(p) < d, "noncontracting scale")
            need(abs(p) == 1 and d == 2, "witness erasure is not a signed half")
            active.remove(dst)
            kills.append((dst, index))
        elif kind == "MOVE":
            need(dst not in active, "native sees a label")
            native_count += 1
        elif kind == "COPY":
            need(src not in active and dst not in active, "copy sees a label")
        elif kind in {"INIT", "CLEAR"}:
            need(dst not in active, "owned operation sees a label")
    need(not active, "surviving public label")
    return {"erasures": kills, "silent_reads": reads, "native_zero_calls": native_count}


def seed(p, denominator):
    """One fixed legal seed schedule, shared by every input and coordinate."""
    return denominator - 1 if p < 0 else 0


def run_data(operations, columns, masks):
    """Literal integer data replay. MOVE uses only the cited zero contract."""
    need(columns in {2, 8, 1024} and len(masks) == len(COHORT), "replay domain")
    need(all(type(m) is int and 0 <= m < 1 << columns for m in masks), "bit masks")
    data = [[0] * columns for _ in range(799)]
    for field, mask in zip(COHORT, masks):
        data[field] = [(mask >> c) & 1 for c in range(columns)]
    for kind, dst, src, p, d in operations:
        if kind in {"ADD", "SCALE"}:
            operand = data[src] if kind == "ADD" else data[dst]
            rounded = [(p * x + seed(p, d)) // d for x in operand]
            if kind == "ADD":
                data[dst] = [x + y for x, y in zip(data[dst], rounded)]
            else:
                data[dst] = rounded
        elif kind == "COPY":
            data[dst] = data[src].copy()
        elif kind in {"INIT", "CLEAR"}:
            data[dst] = [0] * columns
        else:
            need(not any(data[dst]), "nonzero native input")
    need(not any(any(row) for row in data), "nonzero complete output")


def replay_cases(operations):
    """Enumerate each one-bit generator and several simultaneous patterns."""
    cases = 0
    for label in range(120):
        masks = [0] * 60
        masks[label // 2] = 1 << (label % 2)
        run_data(operations, 2, masks)
        cases += 1
    for columns in (2, 8, 1024):
        limit = (1 << columns) - 1
        run_data(operations, columns, [0] * 60)
        run_data(operations, columns, [limit] * 60)
        run_data(operations, columns, [limit // 3 if i % 2 else 2 * (limit // 3)
                                       for i in range(60)])
        cases += 3
    return cases


def expect_rejection(action, expected):
    try:
        action()
    except ValueError as error:
        need(str(error) == expected, "unexpected rejection: " + str(error))
        return
    raise ValueError("missing rejection: " + expected)


def controls(operations, raw):
    """Reject changed bytes, leakage, native reads, copies and bad families."""
    expect_rejection(lambda: load_operations(raw + b"x"), "source hash")
    first = COHORT[0]
    bad_events = (
        (("ADD", 0, first, 1, 1), "non-silent source read"),
        (("MOVE", first, first, 1, 1), "native sees a label"),
        (("COPY", 0, first, 1, 1), "copy sees a label"),
        (("SCALE", first, first, -1, 1), "noncontracting scale"),
        (("CLEAR", first, first, 1, 1), "owned operation sees a label"),
    )
    for event, message in bad_events:
        expect_rejection(lambda: causal_certificate([event] + operations, COHORT), message)
    expect_rejection(lambda: causal_certificate([], COHORT), "surviving public label")
    expect_rejection(lambda: causal_certificate(operations, COHORT + (first,)), "duplicate label")
    expect_rejection(lambda: causal_certificate(operations, (799,)), "public labels")
    need((-1 + seed(-1, 2)) // 2 == 0 and (-1 + 0) // 2 == -1, "wrong-seed witness")
    need((2 + seed(1, 2)) // 2 == 1, "outside-binary witness")
    return {"actual_rejections": 9, "computed_boundary_controls": 2}


def main():
    raw = (ROOT / SOURCE).read_bytes()
    operations = load_operations(raw)
    cohort = find_cohort(operations)
    need(tuple(field for field, _ in cohort) == COHORT, "cohort differs")
    certificate = causal_certificate(operations, COHORT)
    need(sorted(certificate["erasures"]) == cohort, "independent erasure agreement")
    need(len(certificate["silent_reads"]) == 39, "silent-read count")
    need(len({row[1] for row in certificate["silent_reads"]}) == 17, "read-bearing fields")
    need(max(index for _, index in cohort) + 1 == 10448, "erasure cut")
    need(certificate["native_zero_calls"] == 3453, "native call count")
    need(all((p * b + seed(p, d)) // d == 0
             for _, _, p, d in certificate["silent_reads"] for b in (0, 1)), "silent endpoints")
    receipt = {
        "claim_type": "scoped proof with finite corroboration",
        "source_sha256": SOURCE_SHA256,
        "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "public_fields": list(COHORT), "fields": len(COHORT),
        "hidden_bits_per_complex_coordinate": 2 * len(COHORT),
        "width_one_bits": 2 * len(COHORT) * 512,
        "width_one_bytes": 2 * len(COHORT) * 512 // 8,
        "seed_scope": "the explicit sign-dependent scalar seed schedule only",
        "certificate": certificate, "data_replays": replay_cases(operations),
        "controls": controls(operations, raw),
        "native_implementation_executed": False,
    }
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    print("PASS_ROUNDED_READ_CALLER_FIBER")


if __name__ == "__main__":
    main()
