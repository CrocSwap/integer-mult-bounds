# SPDX-License-Identifier: Apache-2.0
"""Rebuild source-bound native streams and bind their scalar bit contracts."""

import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

import caller
from source.vendor.lowering import lower
from source.vendor.native import format as native

PACKAGE = Path(__file__).resolve().parent


def authenticate():
    records = json.loads((PACKAGE / "FROZEN.json").read_text())["files"]
    actual = {
        p.relative_to(PACKAGE).as_posix()
        for p in (PACKAGE / "source").rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    } | {"bitadder.py"}
    caller.require(
        len(records) <= 32 and actual == {r["path"] for r in records},
        "complete frozen inventory",
    )
    for record in records:
        path = PACKAGE / record["path"]
        caller.require(
            not path.is_symlink() and path.stat().st_size <= 8_000_000,
            "bounded regular frozen source",
        )
        caller.require(
            hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"],
            "frozen source hash",
        )
    return len(records)


def templates(width, alphabet):
    caller.require(len(alphabet) <= 32, "bounded scalar alphabet")
    result = {}
    for kind, a, b in alphabet:
        recipe = lower.certify(kind, a, b, policy="target_walk")
        direct = caller.circuit(width, kind, a, b, recipe)
        control = caller.control(width, recipe)
        key = f"{kind}:{a}:{b}"
        result[key] = {"direct": direct, "control": control}
    return result


def trace_for(kind, a, b):
    rows = ((Q(1), Q(0)), (Q(0), Q(1)), (Q(0), Q(0)))
    trace = []
    for instruction in lower.certify(kind, a, b, policy="target_walk"):
        rows = lower.execute([instruction], rows)
        trace.append(rows[instruction[1]])
    return trace


def observe(ledger, record, source, rank, index, trace):
    for label, row in (
        ("source", source),
        ("target input", record[2]),
        ("increment", record[3]),
        ("target output", record[4]),
    ):
        ledger.field(row, rank, index, label)
    for weights in trace:
        row = {
            atom: value * weights[0]
            for atom, value in record[2].items()
            if value * weights[0]
        }
        row = native.add(row, source, weights[1])
        ledger.field(row, rank, index, "control/scale prefix")


def bind(events, word):
    caller.require(1 <= len(events) <= 30_000, "bounded native stream")
    state = {("L", r): {(r, ()): Q(1)} for r in range(632)}
    current = {("L", r): f for r, f in enumerate(word["start"])}
    histogram, digest = Counter(), hashlib.sha256()
    ledger = native.Ledger(True, correlated=True)
    traces = {}
    active = ended = False
    for index, event in enumerate(events):
        if event[0] == "phase":
            if event[1] == "A":
                active = True
            elif active:
                caller.require(event[1] == "centers", "complete A endpoint")
                ended = True
                break
            continue
        if event[0] in ("adapter", "residual_adapter"):
            caller.require(not active, "inherited adapter endpoint premise")
            continue
        source = (
            state[tuple(event[1][2])]
            if event[0] == "scalar" and event[1][0] == "add"
            else {}
        )
        record = native.apply_event(event, state, current, word["frames"], active)
        if event[0] != "scalar":
            continue
        rank = len(word["frames"][record[5]]) if active else 0
        kind, a, b = event[1][0], *event[1][-2:]
        key = kind, a, b
        if key not in traces:
            caller.require(len(traces) < 32, "bounded guard templates")
            traces[key] = trace_for(kind, a, b)
        observe(ledger, record, source, rank, index, traces[key])
        histogram[key] += 1
        digest.update(native.canonical([index, event]))
    caller.require(
        ended and sum(histogram.values()) == 9992 and len(histogram) == 29,
        "complete scalar binding",
    )
    report = ledger.result(64)
    for precision in (3, 64, 128):
        native.capacity(report, precision, 7, precision + 20)
    return histogram, digest.hexdigest(), report


def aggregate(histogram, circuits):
    caller.require(
        len(histogram) <= 32 and sum(histogram.values()) == 9992,
        "bounded complete scalar histogram",
    )
    result = {p: dict.fromkeys(("cx", "ccx"), 0) for p in ("direct", "control")}
    for (kind, a, b), multiplicity in histogram.items():
        for policy, gates in circuits[f"{kind}:{a}:{b}"].items():
            for gate, count in caller.counts(gates).items():
                result[policy][gate] += 2 * multiplicity * count
    result["saving"] = {
        g: result["control"][g] - result["direct"][g] for g in ("cx", "ccx")
    }
    caller.require(sum(result["saving"].values()) > 0, "strict local Boolean saving")
    return result


def run(work):
    frozen = authenticate()
    sys.path.insert(0, str(PACKAGE / "source"))
    from source import verify as inherited

    inherited_result = inherited.run(work)
    caller.require(
        inherited_result == json.loads((PACKAGE / "source/RESULT.json").read_text()),
        "complete inherited coefficient-capacity replay",
    )
    results = {}
    for provider in ("base", "extra"):
        path = work / provider / "native"
        # The inherited compiler authenticates and bounds both compressed inputs.
        import replay_parent as parent

        programs = parent.read(path / "LOCAL-PROGRAMS.json.gz")
        word = parent.read(path / "CANONICAL-WORD.json.gz")
        streams = {}
        for direction in ("forward", "backward"):
            histogram, dispatch, guard_report = bind(programs[direction], word)
            circuits = templates(84, sorted(histogram))
            payload = native.canonical(circuits)
            export = work / f"{provider}-{direction}-circuits.json"
            caller.require(
                export.write_bytes(payload) == len(payload), "complete template export"
            )
            observed = json.loads(export.read_bytes())
            caller.require(
                native.canonical(observed) == payload, "literal template roundtrip"
            )
            streams[direction] = {
                "macros": sum(histogram.values()),
                "templates": len(histogram),
                "dispatch_sha256": dispatch,
                "scalar_guard_ledger": guard_report,
                "circuits_sha256": hashlib.sha256(payload).hexdigest(),
                "histogram": {
                    f"{k}:{a}:{b}": n for (k, a, b), n in sorted(histogram.items())
                },
                "both_components_at_84_bits": aggregate(histogram, observed),
                "width_checks": {
                    str(w): aggregate(histogram, templates(w, sorted(histogram)))
                    for w in (23, 64, 148, 256)
                },
            }
        results[provider] = streams
    return {
        "status": "PASS_BOOLEAN_SCALAR_CALLER_NO_NEW_KAPPA",
        "frozen_files": frozen,
        "input_precision": 64,
        "fractional_bits": 7,
        "data_width": 84,
        "carry_bits": 83,
        "coefficient_scratch_bits": 0,
        "providers": results,
    }
