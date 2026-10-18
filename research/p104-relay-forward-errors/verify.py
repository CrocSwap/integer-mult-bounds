#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact forward growth and final-output defect certificate for one P104 word."""

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction as Q
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
CORE_PATH = "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
CORE_HASH = "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e"
WORD_HASH = "10d47696ed9b42992f8518512c7007ce39774c66d95bfe6de3d964d419058a73"
PORTS, HELPERS, CORE_EVENTS, RELAY_EVENTS = 104, 1031, 4058, 17625
NAMES = ([f"X{i}" for i in range(PORTS)] + [f"Y{i}" for i in range(PORTS)]
         + [f"Q{i}" for i in range(8)] + [f"G{i}" for i in range(32)]
         + [f"D{i}" for i in range(32)] + [f"B{i}" for i in range(HELPERS)])
N = len(NAMES)
PRIVATE = N
INDEX = {name: i for i, name in enumerate(NAMES + ["C"])}
FULL = tuple(1 << i for i in range(8, -1, -1))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_inputs():
    core_bytes = (ROOT / CORE_PATH).read_bytes()
    word_bytes = (PACKAGE / "inputs/WORD.json").read_bytes()
    need(hashlib.sha256(core_bytes).hexdigest() == CORE_HASH, "core source pin")
    need(hashlib.sha256(word_bytes).hexdigest() == WORD_HASH, "relay source pin")
    return json.loads(core_bytes), json.loads(word_bytes)


def frame(values):
    """Canonical binary row space; independent of supplied basis order."""
    need(isinstance(values, list) and len(values) <= 9, "frame size")
    basis = {}
    for x in values:
        need(type(x) is int and 0 < x < 512, "frame label")
        while x:
            bit = x.bit_length() - 1
            if bit in basis:
                x ^= basis[bit]
            else:
                basis[bit] = x
                break
    for bit in sorted(basis):
        for larger in sorted(basis):
            if larger > bit and basis[larger] & (1 << bit):
                basis[larger] ^= basis[bit]
    return tuple(basis[bit] for bit in sorted(basis, reverse=True))


def subset(a, b):
    return all(reduce_vector(x, b) == 0 for x in a)


def reduce_vector(x, basis):
    for y in basis:
        x = min(x, x ^ y)
    return x


@dataclass(frozen=True)
class Gate:
    kind: str
    dst: int
    src: int = -1
    coefficient: Q = Q(0)
    section: str = "fixture"
    event: int = -1
    rank: int = 0

    def location(self):
        return {"section": self.section, "event": self.event,
                "register": (NAMES + ["C"])[self.dst]}


def compile_word(core, word):
    """Bind the literal chronological schedule, including COPY ownership."""
    need(len(core["program"]) == CORE_EVENTS, "core event count")
    need(word["lifetimes"] == HELPERS and len(word["ops"]) == RELAY_EVENTS,
         "relay size")
    need(word["ops"][0] == ["move_zero_all", HELPERS], "relay initialization")
    need(set(core["initial_frames"]) == set(NAMES[:280]), "core initial names")
    need(set(core["final_frames"]) == set(NAMES[:280]), "core final names")
    frames = {name: frame(b) for name, b in core["initial_frames"].items()}
    frames.update({f"B{i}": () for i in range(HELPERS)})
    gates, histogram, counts = [], Counter(), Counter()
    inserted = False
    split = None

    def emit(kind, dst, src=None, coefficient=0, section="core", event=-1, rank=0):
        need(dst in INDEX and (src is None or src in INDEX), "register name")
        q = Q(coefficient)
        need(q.denominator in (1, 2, 4) and abs(q) <= 4, "coefficient alphabet")
        need(kind != "add" or dst != src, "distinct ADD operands")
        gates.append(Gate(kind, INDEX[dst], INDEX[src] if src else -1,
                          q, section, event, rank))
        counts[f"{section}_{kind}"] += 1
        if rank:
            histogram[rank] += 1

    def insert_core():
        for i, op in enumerate(core["program"]):
            kind, dst = op[:2]
            if kind == "zero":
                need(dst == "C" and dst not in frames, "private allocation ownership")
                frames[dst] = frame(op[2])
                emit("zero", dst, event=i)
            elif kind == "erase":
                need(dst == "C" and frames.get(dst) == frame(op[2]), "private erase frame")
                del frames[dst]
                emit("erase", dst, event=i)
            elif kind in ("add", "copy"):
                src = op[2]
                claimed = frame(op[4] if kind == "add" else op[3])
                need(dst in frames and src in frames and frames[dst] == frames[src] == claimed,
                     "core common frame")
                if kind == "copy":
                    need(dst == "C", "private COPY destination")
                emit(kind, dst, src, op[3] if kind == "add" else 1, event=i)
            elif kind == "transport":
                old, new = frame(op[2]), frame(op[3])
                rank = abs(len(old) - len(new))
                need(frames.get(dst) == old and rank == op[4] and rank > 0,
                     "core transport rank/entry")
                need(subset(old, new) or subset(new, old), "core nested transport")
                frames[dst] = new
                emit(kind, dst, event=i, rank=rank)
            else:
                raise ValueError("unknown core operation")
        need("C" not in frames, "private lifetime remains live")
        need(all(frames[name] == frame(b) for name, b in core["final_frames"].items()),
             "core final frames")

    for i, op in enumerate(word["ops"][1:], 1):
        kind = op[0]
        if kind in ("read", "write"):
            need(op[4] in (0, CORE_EVENTS), "relay contact cut")
            if op[4] == CORE_EVENTS and not inserted:
                split = len(gates)
                insert_core()
                inserted = True
            need(op[4] == (CORE_EVENTS if inserted else 0), "relay cut order")
        if kind == "move":
            dst = f"B{op[1]}"
            new = frame(op[2])
            need(dst in frames, "relay helper index")
            old = frames[dst]
            need(subset(old, new) and len(old) < len(new), "relay monotone move")
            frames[dst] = new
            emit("transport", dst, section="relay", event=i, rank=len(new) - len(old))
        elif kind in ("read", "write", "shear"):
            if kind == "read":
                dst, src = f"B{op[1]}", f"X{op[2]}"
            elif kind == "write":
                dst, src = f"Y{op[1]}", f"B{op[2]}"
            else:
                dst, src = f"B{op[1]}", f"B{op[2]}"
            need(dst in frames and src in frames and frames[dst] == frames[src],
                 "relay common frame")
            emit("add", dst, src, op[3], section="relay", event=i)
        else:
            raise ValueError("unknown relay operation")
    need(inserted and all(frames[f"B{i}"] == FULL for i in range(HELPERS)),
         "relay terminal frames")
    return gates, {"core_inserted_after_combined_events": split,
                   "combined_events": len(gates), "counts": dict(sorted(counts.items())),
                   "profile": {str(k): v for k, v in sorted(histogram.items())},
                   "rank_mass": sum(k * v for k, v in histogram.items())}


def axpy(dst, src, coefficient):
    result = dst.copy()
    for key, value in src.items():
        updated = result.get(key, Q(0)) + coefficient * value
        if updated:
            result[key] = updated
        else:
            result.pop(key, None)
    return result


def expected_row(i):
    result = {i: Q(1)}
    if PORTS <= i < 2 * PORTS:
        result[i - PORTS] = Q(1)
    return result


def is_defective(gate):
    return gate.kind in ("add", "transport", "copy")


def scalar_replay(gates, initial, errors=None, stop=None):
    """Separate scalar evaluator used for attained-bound witnesses."""
    values = list(map(Q, initial)) + [Q(0)]
    for k, gate in enumerate(gates):
        d, s, c = gate.dst, gate.src, gate.coefficient
        if gate.kind == "add":
            values[d] += c * values[s]
        elif gate.kind == "copy":
            values[d] = values[s]
        elif gate.kind in ("zero", "erase"):
            values[d] = Q(0)
        elif gate.kind != "transport":
            raise ValueError("scalar operation")
        if errors and k in errors:
            need(is_defective(gate), "defect at exact operation")
            values[d] += errors[k]
        if stop == k:
            break
    return values


def prefix_certificate(gates):
    rows = [{i: Q(1)} for i in range(N)] + [{}]
    errors = [Q(0)] * (N + 1)
    maximum, denominator, envelope = Q(1), 1, Q(0)
    witness = {"combined_event": -1, "register": "X0"}
    norm_inputs, norm_stop, norm_dst = {0: Q(1)}, -1, 0
    denominator_witness = witness.copy()
    error_witness = witness.copy()
    for k, gate in enumerate(gates):
        d, s, c = gate.dst, gate.src, gate.coefficient
        if gate.kind == "add":
            rows[d] = axpy(rows[d], rows[s], c)
            errors[d] += abs(c) * errors[s]
        elif gate.kind == "copy":
            need(not rows[d], "COPY requires ideal zero destination")
            rows[d] = rows[s].copy()
            errors[d] = errors[s]
        elif gate.kind in ("zero", "erase"):
            rows[d] = {}
            errors[d] = Q(0)
        if is_defective(gate):
            errors[d] += 1
        norm = sum(map(abs, rows[d].values()), Q(0))
        den = max((value.denominator for value in rows[d].values()), default=1)
        need(den & (den - 1) == 0 and den <= 2**32, "dyadic capacity")
        need(all(abs(v.numerator).bit_length() <= 128 for v in rows[d].values()),
             "numerator capacity")
        location = {"combined_event": k, **gate.location()}
        if norm > maximum:
            maximum, witness = norm, location
            norm_inputs = {i: Q(1 if value > 0 else -1) for i, value in rows[d].items()}
            norm_stop, norm_dst = k, d
        if den > denominator:
            denominator, denominator_witness = den, location
        if errors[d] > envelope:
            envelope, error_witness = errors[d], location
    need(all(rows[i] == expected_row(i) for i in range(N)), "complete forward endpoint")
    need(not rows[PRIVATE], "private final discard")
    initial = [norm_inputs.get(i, Q(0)) for i in range(N)]
    attained = scalar_replay(gates, initial, stop=norm_stop)[norm_dst]
    need(attained == maximum, "prefix attainment replay")
    return {"max_row_l1": str(maximum), "norm_witness": witness,
            "largest_denominator": denominator, "denominator_witness": denominator_witness,
            "all_cut_unit_defect_envelope": str(envelope), "envelope_witness": error_witness,
            "endpoint_coefficients": N * N, "prefix_attainment_checked": True}


def pullback(columns, gate):
    d, s, c = gate.dst, gate.src, gate.coefficient
    if gate.kind == "add":
        columns[s] = axpy(columns[s], columns[d], c)
    elif gate.kind == "copy":
        columns[s] = axpy(columns[s], columns[d], Q(1))
        columns[d] = {}
    elif gate.kind in ("zero", "erase"):
        columns[d] = {}


def defect_witness(gates, output):
    """One signed output covector, independent of the all-output column scan."""
    covector = {output: Q(1)}
    signs = {}
    total = Q(0)
    for k in range(len(gates) - 1, -1, -1):
        gate = gates[k]
        d, s, c = gate.dst, gate.src, gate.coefficient
        value = covector.get(d, Q(0))
        if is_defective(gate) and value:
            signs[k] = Q(1 if value > 0 else -1)
            total += abs(value)
        if gate.kind in ("add", "copy"):
            value = covector.get(s, Q(0)) + (c if gate.kind == "add" else 1) * value
            if value:
                covector[s] = value
            else:
                covector.pop(s, None)
        if gate.kind in ("copy", "zero", "erase"):
            covector.pop(d, None)
    values = scalar_replay(gates, [0] * N, signs)
    need(values[output] == total, "signed defect attainment replay")
    return total, {"nonzero_defects": len(signs),
                   "signs_sha256": digest([[k, int(v)] for k, v in sorted(signs.items())]),
                   "scalar_replay_checked": True}


def suffix_certificate(gates, with_budgets=False):
    columns = [{i: Q(1)} for i in range(N)] + [{}]
    classes = sorted({g.section + "_" + g.kind for g in gates if is_defective(g)})
    budgets = {name: [Q(0)] * N for name in classes}
    single, single_witness = Q(0), {}
    for k in range(len(gates) - 1, -1, -1):
        gate = gates[k]
        if is_defective(gate):
            budget = budgets[gate.section + "_" + gate.kind]
            for output, value in columns[gate.dst].items():
                budget[output] += abs(value)
                if abs(value) > single:
                    single = abs(value)
                    single_witness = {"combined_event": k, **gate.location(),
                                      "output": NAMES[output]}
        pullback(columns, gate)
    for i in range(N):
        expected = {i: Q(1)}
        if i < PORTS:
            expected[i + PORTS] = Q(1)
        need(columns[i] == expected, "backward endpoint transpose")
    need(not columns[PRIVATE], "private initial sensitivity")
    totals = [sum((budgets[name][i] for name in classes), Q(0)) for i in range(N)]
    output = max(range(N), key=totals.__getitem__)
    attained, signs = defect_witness(gates, output)
    need(attained == totals[output], "two suffix implementations disagree")
    vector = [[NAMES[i]] + [str(budgets[name][i]) for name in classes] for i in range(N)]
    receipt = {"unit_defect_final_bound": str(totals[output]), "maximizing_output": NAMES[output],
            "classes": classes,
            "contributions_at_maximizer": {name: str(budgets[name][output]) for name in classes},
            "class_maxima": {name: str(max(budgets[name])) for name in classes},
            "all_output_budgets_sha256": digest(vector),
            "max_single_defect_gain": str(single), "single_defect_witness": single_witness,
            "attainment": signs}
    return (receipt, vector) if with_budgets else receipt


def error_certificate(gates, with_budgets=False):
    """Forward exact propagation of one fresh independent variable per defect.

    This uses signed error rows, not the triangle-inequality recurrence in the
    input-prefix pass. It independently checks every final budget from the
    reverse suffix scan, and covers intermediate private-copy states too.
    """
    rows = [{} for _ in range(N + 1)]
    classes = sorted({g.section + "_" + g.kind for g in gates if is_defective(g)})
    maximum, peak_size, size, defects = Q(0), 0, 0, 0
    witness, signs, at, dst = {}, {}, -1, 0
    for k, gate in enumerate(gates):
        d, s, c = gate.dst, gate.src, gate.coefficient
        size -= len(rows[d])
        if gate.kind == "add":
            rows[d] = axpy(rows[d], rows[s], c)
        elif gate.kind == "copy":
            rows[d] = rows[s].copy()
        elif gate.kind in ("zero", "erase"):
            rows[d] = {}
        if is_defective(gate):
            rows[d][k] = Q(1)
            defects += 1
        size += len(rows[d])
        peak_size = max(peak_size, size)
        need(size <= 2_000_000, "error-row sparse capacity")
        norm = sum(map(abs, rows[d].values()), Q(0))
        if norm > maximum:
            maximum, at, dst = norm, k, d
            witness = {"combined_event": k, **gate.location()}
            signs = {j: Q(1 if value > 0 else -1) for j, value in rows[d].items()}
    attained = scalar_replay(gates, [0] * N, signs, stop=at)[dst]
    need(attained == maximum, "all-cut defect attainment replay")
    vector = []
    for i in range(N):
        budgets = {name: Q(0) for name in classes}
        for j, value in rows[i].items():
            source = gates[j]
            budgets[source.section + "_" + source.kind] += abs(value)
        vector.append([NAMES[i]] + [str(budgets[name]) for name in classes])
    receipt = {"max_error_l1": str(maximum), "witness": witness,
            "independent_local_defects": defects, "peak_sparse_coefficients": peak_size,
            "all_output_budgets_sha256": digest(vector),
            "attainment": {"nonzero_defects": len(signs),
                            "signs_sha256": digest([[k, int(v)] for k, v in sorted(signs.items())]),
                            "scalar_replay_checked": True}}
    return (receipt, vector) if with_budgets else receipt


def audit(core, word):
    gates, schedule = compile_word(core, word)
    need(len(gates) <= CORE_EVENTS + RELAY_EVENTS, "combined event bound")
    prefix = prefix_certificate(gates)
    suffix, reverse_budgets = suffix_certificate(gates, with_budgets=True)
    errors, forward_budgets = error_certificate(gates, with_budgets=True)
    need(forward_budgets == reverse_budgets,
         "forward/reverse defect budgets disagree")
    return {"status": "PASS_P104_RELAY_FORWARD_ERRORS", "independent_inputs": N,
            "private_slots": 1, "private_lifetimes": 8, "schedule": schedule,
            "prefix": prefix, "suffix": suffix, "all_cut_errors": errors,
            "fixed_template_local_only_moment_at_zero": str(Q(9 * schedule["rank_mass"], 73 * 832))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write receipt exclusively to a new file")
    args = parser.parse_args()
    result = audit(*load_inputs())
    expected = json.loads((PACKAGE / "EXPECTED.json").read_text())
    need(result == expected, "receipt drift")
    if args.out:
        with args.out.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    print(result["status"], "inputs=" + str(N),
          "growth=" + result["prefix"]["max_row_l1"],
          "final_error=" + result["suffix"]["unit_defect_final_bound"], "no_new_kappa")


if __name__ == "__main__":
    main()
