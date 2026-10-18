#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact full-boundary audit of the hosted scalar skeleton, not native semantics."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import sys
import tarfile
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
MEMBERS = {
    "template": (
        "candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz",
        "2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760",
    ),
    "programs": (
        "candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz",
        "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
    ),
}
KNOWN_TAGS = {"scalar", "center", "phase", "climb", "adapter", "residual_adapter"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_inputs() -> dict:
    root = HERE.parents[1]
    pins = json.loads((HERE / "SOURCES.json").read_text())
    pin = next(row for row in pins["files"] if row["path"] == ARCHIVE)
    path = root / ARCHIVE
    require(path.stat().st_size <= 8 * 1024**2, "archive size limit")
    require(
        hashlib.sha256(path.read_bytes()).hexdigest() == pin["sha256"], "archive hash"
    )
    result = {}
    with tarfile.open(path, "r:gz") as archive:
        for key, (name, digest) in MEMBERS.items():
            info = archive.getmember(name)
            require(info.isfile() and info.size <= 2 * 1024**2, "member type/size")
            stream = archive.extractfile(info)
            require(stream is not None, "member stream")
            with stream:
                raw = stream.read(info.size + 1)
            require(hashlib.sha256(raw).hexdigest() == digest, "member hash")
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as zipped:
                payload = zipped.read(16 * 1024**2 + 1)
            require(len(payload) <= 16 * 1024**2, "payload size limit")
            result[key] = json.loads(payload)
    template = result["template"]
    require(len(template["calls"]) == 144, "call domain")
    require(len(template["execution_schedule"]) == 482, "schedule domain")
    for call in template["calls"]:
        base = 896 * call["replica"] + 224 * call["pair"]
        require(
            [row[0] for row in call["owners"][:224]] == list(range(base, base + 224)),
            "data role ownership",
        )
    return result


def plus(dst: dict[int, F], src: dict[int, F], factor: F) -> None:
    for column, value in src.items():
        updated = dst.get(column, F(0)) + factor * value
        if updated:
            dst[column] = updated
        else:
            dst.pop(column, None)


def scalar(state: dict[tuple, dict[int, F]], operation: list) -> None:
    tag, destination = operation[0], tuple(operation[1])
    if tag == "add":
        source = tuple(operation[2])
        require(source != destination, "no aliased ADD")
        plus(state[destination], state[source], F(operation[3], operation[4]))
    elif tag == "scale":
        factor = F(operation[2], operation[3])
        state[destination] = {
            i: factor * x for i, x in state[destination].items() if factor * x
        }
    elif tag == "copy":
        state[destination] = dict(state[tuple(operation[2])])
    elif tag == "clear":
        state[destination] = {}
    else:
        raise ValueError("unknown scalar operation")


def local_matrices(program: list, orientation: str) -> tuple[list, list]:
    require(len(program) < 30000, "local event bound")
    state = {("L", i): {i: F(1)} for i in range(704)}
    state.update({("C", k): {} for k in range(8)})
    cuts = []
    for event in program:
        require(event[0] in KNOWN_TAGS, "unknown program event")
        if event[0] == "scalar":
            scalar(state, event[1])
        elif event[0] == "center":
            k = event[1]
            require(k == len(cuts) and k < 8, "centre order")
            cuts.append(dict(state[("C", k)]))
            state[("C", k)][704 + k] = F(1)
    require(len(cuts) == 8, "eight cuts")
    require(all(not state[("C", k)] for k in range(8)), "private scratch return")
    response = [{} for _ in range(8)]
    for i in range(704):
        row = state[("L", i)]
        ordinary = {j: x for j, x in row.items() if j < 704}
        expected = {i: F(1)}
        if orientation == "forward" and 112 <= i < 224:
            expected[i - 112] = F(1)
        if orientation == "backward" and i < 112:
            expected[i + 112] = F(-1)
        require(ordinary == expected, "ordinary scalar endpoint")
        for k in range(8):
            if row.get(704 + k):
                response[k][i] = row[704 + k]
    return cuts, response


def echelon(rows: list[dict[int, F]]) -> tuple[list[int], list[int]]:
    basis = {}
    selected = []
    for index, row in enumerate(rows):
        value = dict(row)
        for pivot, previous in sorted(basis.items()):
            if pivot in value:
                plus(value, previous, -value[pivot])
        if value:
            pivot = min(value)
            factor = value[pivot]
            basis[pivot] = {j: x / factor for j, x in value.items()}
            selected.append(index)
    return selected, sorted(basis)


def determinant(matrix: list[list[F]]) -> F:
    n = len(matrix)
    require(0 < n <= 16 and all(len(row) == n for row in matrix), "minor dimensions")
    a = [row[:] for row in matrix]
    result = F(1)
    for k in range(n):
        pivot = next((i for i in range(k, n) if a[i][k]), None)
        if pivot is None:
            return F(0)
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            result = -result
        diagonal = a[k][k]
        result *= diagonal
        for i in range(k + 1, n):
            factor = a[i][k] / diagonal
            for j in range(k, n):
                a[i][j] -= factor * a[k][j]
    return result


def minor_receipt(rows: list[dict[int, F]], allowed: range) -> dict:
    restricted = [{i: x for i, x in row.items() if i in allowed} for row in rows]
    selected, columns = echelon(restricted)
    minor = [[restricted[i].get(j, F(0)) for j in columns] for i in selected]
    det = determinant(minor)
    require(det != 0, "nonzero minor")
    return {
        "rank": len(selected),
        "rows": selected,
        "columns": columns,
        "determinant": str(det),
    }


def chronological_cuts(template: dict, cuts: dict) -> dict:
    state = [{i: F(1)} for i in range(14336)]
    calls = {call["time"]: call for call in template["calls"]}
    result = {}
    for event in template["execution_schedule"]:
        if event["kind"] == "local_cover_sweep":
            call = calls[event["time"]]
            owners = [row[0] for row in call["owners"]]
            require(
                len(owners) == 704 and len(set(owners)) == 704, "injective role map"
            )
            if call["time"] in (0, 4, 10):
                observed = []
                for row in cuts[call["orientation"]]:
                    out = {}
                    for role, factor in row.items():
                        plus(out, state[owners[role]], factor)
                    observed.append(out)
                result[call["time"]] = observed
            if call["time"] == 10:
                break
            for k in range(112):
                x, y = owners[k], owners[112 + k]
                if call["orientation"] == "forward":
                    plus(state[y], state[x], F(1))
                else:
                    plus(state[x], state[y], F(-1))
        elif event["kind"] == "bridge":
            base = 896 * event["replica"]
            source, destination = base + 224 * event["src"], base + 224 * event["dst"]
            factor = F(event["coefficient"])
            for k in range(112):
                plus(state[destination + k], state[source + k], factor)
                plus(state[source + 112 + k], state[destination + 112 + k], -factor)
    require(set(result) == {0, 4, 10}, "three chronological cuts")
    return result


def circle_receipt(template: dict, cuts: dict) -> dict:
    observed = chronological_cuts(template, cuts)
    require(
        all(not (set(row) & set(range(112))) for row in observed[10]), "D0 cancellation"
    )
    for before, after in zip(observed[0], observed[10], strict=True):
        require(
            not (set(before) & set(range(112, 224))), "no initial T0 in first demand"
        )
        require(
            all(after.get(112 + p, 0) == -before.get(p, 0) for p in range(112)),
            "surviving T0 demand",
        )
    joint = minor_receipt(observed[0] + observed[10], range(224))
    target = minor_receipt(observed[10], range(112, 224))
    require((joint["rank"], target["rank"]) == (16, 8), "full-input ranks")
    witness = next(
        p for p in range(112) if any(row.get(112 + p) for row in observed[10])
    )
    require(all(not row.get(112 + witness) for row in observed[0]), "zero first demand")
    return {
        "calls": [0, 4, 10],
        "f2_rank_on_D0": 0,
        "f2_on_T0": target,
        "f0_f2_on_D0_T0": joint,
        "target_only_input": 112 + witness,
        "f0_values": [str(row.get(112 + witness, F(0))) for row in observed[0]],
        "f2_values": [str(row.get(112 + witness, F(0))) for row in observed[10]],
    }


def late_responses(template: dict, response: list) -> tuple[list, list]:
    schedule = template["execution_schedule"]
    calls = sorted(
        (c for c in template["calls"] if c["stage"] == 8), key=lambda c: c["replica"]
    )
    require(len(calls) == 16 and all(c["pair"] == 3 for c in calls), "late call domain")
    blocks, records = [], []
    for call in calls:
        time, replica = call["time"], call["replica"]
        start = next(
            i
            for i, e in enumerate(schedule)
            if e["kind"] == "local_cover_sweep" and e["time"] == time
        )
        suffix = [
            (i, e)
            for i, e in enumerate(schedule)
            if i > start and e.get("replica") == replica
        ]
        bridges = [(i, e) for i, e in suffix if e["kind"] == "bridge"]
        require(
            [(e["src"], e["dst"], e["coefficient"]) for _, e in bridges]
            == [(2, 3, 1), (1, 2, 1), (0, 1, 1)],
            "late bridge chain",
        )
        require(
            not any(e["kind"] == "local_cover_sweep" for _, e in suffix),
            "no later local call",
        )
        owners = [row[0] for row in call["owners"]]
        rows = [{owners[role]: x for role, x in row.items()} for row in response]
        for _, event in bridges:
            base = 896 * replica
            for row in rows:
                for port in range(112):
                    source = base + 224 * event["dst"] + 112 + port
                    destination = base + 224 * event["src"] + 112 + port
                    plus(
                        row,
                        {destination: row[source]} if row.get(source) else {},
                        F(-1),
                    )
        for k, row in enumerate(rows):
            expected = {}
            for pair, sign in enumerate((-1, 1, -1, 1)):
                for role, value in response[k].items():
                    expected[896 * replica + 224 * pair + role] = sign * value
            require(row == expected, "complete late target response")
        blocks.extend(rows)
        records.append(
            {
                "replica": replica,
                "call_time": time,
                "schedule_index": start,
                "bridges": [i for i, _ in bridges],
            }
        )
    return blocks, records


def compute() -> dict:
    inputs = load_inputs()
    cuts, responses = {}, {}
    for orientation in ("forward", "backward"):
        cuts[orientation], responses[orientation] = local_matrices(
            inputs["programs"][orientation], orientation
        )
    require(
        all(set(row) <= set(range(112, 224)) for row in responses["forward"]),
        "target-only response",
    )
    local = minor_receipt(responses["forward"], range(112, 224))
    blocks, records = late_responses(inputs["template"], responses["forward"])
    ranks = [
        minor_receipt(blocks[8 * r : 8 * r + 8], range(896 * r, 896 * (r + 1)))
        for r in range(16)
    ]
    require(all(row["rank"] == 8 for row in ranks), "late response block ranks")
    for replica, receipt in enumerate(ranks):
        require(
            receipt["columns"] == [896 * replica + p for p in local["columns"]],
            "shifted minor",
        )
        require(
            receipt["determinant"] == local["determinant"], "equal block determinants"
        )
    require(
        all(
            set(row) <= set(range(896 * (i // 8), 896 * (i // 8 + 1)))
            for i, row in enumerate(blocks)
        ),
        "disjoint replica supports",
    )
    return {
        "schema_version": 1,
        "scope": (
            "Frozen scalar skeleton: nonscalar recursive events are identity; "
            "fresh centre increments are independent inputs."
        ),
        "circle": circle_receipt(inputs["template"], cuts),
        "late_stage": {
            "local_response": local,
            "calls": records,
            "bridge_count": sum(len(c["bridges"]) for c in records),
            "minor_column_shift_per_replica": 896,
            "direct_sum_rank": sum(r["rank"] for r in ranks),
            "target_panel_multipliers": [-1, 1, -1, 1],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--emit", action="store_true", help="print regenerated evidence without writing"
    )
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = json.loads((HERE / "RESULT.json").read_text())
        require(result == expected, "receipt differs")
        print(
            "PASS_CENTRE_CIRCLE_ENDPOINT_AUDIT joint_rank=16 "
            "late_rank=128 late_bridges=48 no_new_kappa"
        )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, KeyError, OSError, StopIteration) as error:
        sys.exit(f"FAIL_CENTRE_CIRCLE_ENDPOINT_AUDIT: {error}")
