#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Dense one-input replay without primary or predecessor implementation imports."""

import gzip
import hashlib
import json
import sys
import tarfile
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
COLUMNS = (0, 1, 2, 3, 4, 5, 6, 12)


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def inputs() -> tuple[dict, dict]:
    pins = json.loads((HERE / "SOURCES.json").read_text())
    digest = next(x["sha256"] for x in pins["files"] if x["path"] == ARCHIVE)
    path = HERE.parents[1] / ARCHIVE
    check(path.stat().st_size <= 8 * 1024**2, "archive bound")
    check(hashlib.sha256(path.read_bytes()).hexdigest() == digest, "archive digest")
    with tarfile.open(path, "r:gz") as archive:
        result = []
        for member in (
            "candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz",
            "candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz",
        ):
            stream = archive.extractfile(member)
            check(stream is not None, "member missing")
            with stream:
                raw = stream.read(2 * 1024**2 + 1)
            check(len(raw) <= 2 * 1024**2, "compressed input bound")
            result.append(json.loads(gzip.decompress(raw)))
    return result[0], result[1]


def address(role: list) -> int:
    check(role[0] in ("L", "C"), "unknown role kind")
    bound = 704 if role[0] == "L" else 8
    check(0 <= role[1] < bound, "role range")
    return role[1] + (704 if role[0] == "C" else 0)


def execute(
    program: list, initial: list[Q], impulse: int | None = None
) -> tuple[list[Q], list[Q]]:
    check(len(initial) == 704 and len(program) < 30000, "execution domain")
    state = list(initial) + [Q(0)] * 8
    cuts = []
    for event in program:
        tag = event[0]
        if tag == "scalar":
            op = event[1]
            dst = address(op[1])
            if op[0] == "add":
                state[dst] += Q(op[3], op[4]) * state[address(op[2])]
            elif op[0] == "scale":
                state[dst] *= Q(op[2], op[3])
            elif op[0] == "copy":
                state[dst] = state[address(op[2])]
            elif op[0] == "clear":
                state[dst] = Q(0)
            else:
                raise ValueError("unknown scalar opcode")
        elif tag == "center":
            check(event[1] == len(cuts), "centre order")
            cuts.append(state[704 + event[1]])
            if impulse == event[1]:
                state[704 + event[1]] += 1
        else:
            check(tag in ("phase", "climb", "adapter", "residual_adapter"), "event tag")
    check(len(cuts) == 8 and state[704:] == [0] * 8, "private scratch restoration")
    return state[:704], cuts


def prefix(template: dict, programs: dict, column: int) -> dict[int, list[Q]]:
    state = [Q(0)] * 14336
    state[column] = Q(1)
    calls = {c["time"]: c for c in template["calls"]}
    observed = {}
    for event in template["execution_schedule"]:
        if event["kind"] == "local_cover_sweep":
            call = calls[event["time"]]
            owners = [x[0] for x in call["owners"]]
            endpoint, cuts = execute(
                programs[call["orientation"]], [state[i] for i in owners]
            )
            if call["time"] in (0, 4, 10):
                observed[call["time"]] = cuts
            if call["time"] == 10:
                break
            for index, value in zip(owners, endpoint, strict=True):
                state[index] = value
        elif event["kind"] == "bridge":
            base = 896 * event["replica"]
            a, b = base + 224 * event["src"], base + 224 * event["dst"]
            for port in range(112):
                state[b + port] += Q(event["coefficient"]) * state[a + port]
                state[a + 112 + port] -= Q(event["coefficient"]) * state[b + 112 + port]
    check(set(observed) == {0, 4, 10}, "prefix observation domain")
    return observed


def integer_determinant(matrix: list[list[int]]) -> int:
    n = len(matrix)
    check(0 < n <= 16 and all(len(r) == n for r in matrix), "determinant domain")
    a = [r[:] for r in matrix]
    previous, sign = 1, 1
    for k in range(n - 1):
        pivot = next((i for i in range(k, n) if a[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[i][j] * a[k][k] - a[i][k] * a[k][j]
                check(numerator % previous == 0, "exact Bareiss division")
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = a[k][k]
    return sign * a[-1][-1]


def check_circle(template: dict, programs: dict) -> None:
    columns = list(COLUMNS) + [112 + p for p in COLUMNS]
    observed = [prefix(template, programs, column) for column in columns]
    matrix = [[x[t][k] for x in observed] for t in (0, 10) for k in range(8)]
    check(all(x.denominator == 1 for row in matrix for x in row), "integer cut minor")
    integer = [[int(x) for x in row] for row in matrix]
    check(integer_determinant(integer) == 1024, "joint demand determinant")
    check(
        integer_determinant([r[8:] for r in integer[8:]]) == 32,
        "target demand determinant",
    )
    check(observed[8][0] == [0] * 8, "target witness first cut")
    check(observed[8][10] == [-1, -1, -1, -1, 0, 0, 0, 0], "target witness last cut")


def check_late(template: dict, programs: dict) -> None:
    responses = [execute(programs["forward"], [Q(0)] * 704, k)[0] for k in range(8)]
    minor = [[4 * row[112 + p] for p in COLUMNS] for row in responses]
    check(
        all(x.denominator == 1 for row in minor for x in row), "integer response minor"
    )
    check(
        integer_determinant([[int(x) for x in row] for row in minor]) == 32,
        "response determinant",
    )
    calls = [c for c in template["calls"] if c["stage"] == 8]
    check(len(calls) == 16, "late call count")
    for call in calls:
        owners, replica = [x[0] for x in call["owners"]], call["replica"]
        schedule = template["execution_schedule"]
        start = next(
            i
            for i, e in enumerate(schedule)
            if e["kind"] == "local_cover_sweep" and e["time"] == call["time"]
        )
        bridges = [
            e
            for e in schedule[start + 1 :]
            if e["kind"] == "bridge" and e["replica"] == replica
        ]
        check(len(bridges) == 3, "three later bridges")
        for response in responses:
            state = [Q(0)] * 896
            for role, value in enumerate(response):
                if value:
                    state[owners[role] - 896 * replica] = value
            for event in bridges:
                a, b = 224 * event["src"], 224 * event["dst"]
                for port in range(112):
                    state[a + 112 + port] -= (
                        Q(event["coefficient"]) * state[b + 112 + port]
                    )
            for pair, sign in enumerate((-1, 1, -1, 1)):
                check(
                    state[224 * pair : 224 * pair + 112] == [0] * 112, "no D response"
                )
                check(
                    state[224 * pair + 112 : 224 * pair + 224]
                    == [sign * x for x in response[112:224]],
                    "late endpoint response",
                )


def main() -> None:
    template, programs = inputs()
    check_circle(template, programs)
    check_late(template, programs)
    print(
        "PASS_INDEPENDENT_CENTRE_CIRCLE_ENDPOINT joint_determinant=1024 "
        "response_determinant=1/2048 late_rank=128"
    )


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, StopIteration) as error:
        sys.exit(f"FAIL_INDEPENDENT_CENTRE_CIRCLE_ENDPOINT: {error}")
