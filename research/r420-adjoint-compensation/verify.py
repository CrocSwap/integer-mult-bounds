#!/usr/bin/env python3
"""Exact backward-covector certificate for the selected R420 compensation.

Prepared for Sagar Thakrar with substantial OpenAI Codex assistance.
Apache-2.0. No supplier implementation is imported or executed.
"""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 81
WORD = "research/e8-bit-r420/data/bitE8mut-r420.json.gz"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_word():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for path, pin in pins["files"].items():
        raw = (ROOT / path).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pin["sha256"], "source pin: " + path)
    selected = json.loads((ROOT / "certificates/selected-result.json").read_text())
    need(selected["reviewed_dependency_heads"]["543"] == pins["pr543_head"], "PR543 binding")
    manifest = json.loads((ROOT / selected["source_manifest"]).read_text())
    need(manifest["files"][WORD] == pins["files"][WORD]["sha256"], "selected word binding")
    payload = gzip.decompress((ROOT / WORD).read_bytes())
    need(hashlib.sha256(payload).hexdigest() == pins["word_payload_sha256"], "payload pin")
    return json.loads(payload)


def validate(w):
    need((w["v"], w["R"]) == (120, 420), "dimensions")
    n = 660
    for section in ("D", "A", "B", "C"):
        for f, d, sources in w[section]:
            need(type(f) is int and 0 <= f < len(w["frames"]), "frame index")
            need(type(d) is int and 0 <= d < n, "destination index")
            need(all(type(s) is int and 0 <= s < n and s != d for s in sources), "operand index or alias")
    need(len(w["scatter"]) == 120 and all(240 <= h < n for h in w["ret"]), "scatter shape")
    need(all(type(k) is int and 0 <= k < len(w["ret"]) for row in w["scatter"] for k in row), "scatter index")
    need(all(120 <= d < 240 and all(s >= 240 for s in src) for _, d, src in w["D"]), "D must correct targets from helpers")
    need(all(not 120 <= d < 240 for _, d, _ in w["C"]), "C changes a target")


def pullback(q, gates):
    """For x[d] ^= sum(x[s]), transpose sends q[s] ^= old q[d]."""
    for _, d, sources in reversed(gates):
        if q & (1 << d):
            for s in sources:
                q ^= 1 << s
    return q


def raw_covectors(w):
    rows = []
    for target in range(120):
        q = pullback(1 << (120 + target), w["B"])
        for t, indices in enumerate(w["scatter"]):
            if q & (1 << (120 + t)):
                for k in indices:
                    q ^= 1 << w["ret"][k]
        rows.append(pullback(q, w["A"]))
    return rows


def compensation_rows(w):
    rows = [0] * 120
    for _, d, sources in w["D"]:
        for s in sources:
            rows[d - 120] ^= 1 << (s - 240)
    return rows


def check_identity(w):
    validate(w)
    raw = raw_covectors(w)
    correction = compensation_rows(w)
    for t, q in enumerate(raw):
        wanted = (1 << t) | (1 << (120 + t))
        need(q & ((1 << 240) - 1) == wanted, "J/V identity: target " + str(t))
        need(q >> 240 == correction[t], "D parity: target " + str(t))
        need(pullback(q, w["D"]) == wanted, "complete target map: " + str(t))
    return [q >> 240 for q in raw]


def scalar_tests(w, labels):
    """Bit k of each value is the execution under dirty assignment k."""
    values = [0] * 240 + list(labels)
    for section in ("D", "A", "scatter", "B", "C"):
        if section == "scatter":
            gates = [(0, 120 + t, [w["ret"][i] for i in row])
                     for t, row in enumerate(w["scatter"])]
        else:
            gates = w[section]
        for _, d, sources in gates:
            delta = 0
            for s in sources:
                delta ^= values[s]
            values[d] ^= delta
    return values[120:240]


def suite_certificate(w):
    labels = [1 | (j << 1) for j in range(420)]
    patterns = [sum(1 << j for j, label in enumerate(labels) if label & (1 << k)) for k in range(10)]
    need(all(labels) and len(set(labels)) == 420, "zero or duplicate syndrome column")
    need(all(label & 1 for label in labels), "odd-error parity row")
    pairs = [(i, j) for i in range(420) for j in range(i + 1, 420)]
    need(all(labels[i] ^ labels[j] for i, j in pairs), "undetected two-coefficient fault")
    need(scalar_tests(w, labels) == [0] * 120, "baseline ten-test replay")
    for weight in (1, 2, 3):
        bad = copy.deepcopy(w)
        expected = []
        for t in range(120):
            support = [(SEED + t + k) % 420 for k in range(weight)]
            bad["D"][t][2] = sorted(set(bad["D"][t][2]) ^ {240 + j for j in support})
            syndrome = 0
            for j in support:
                syndrome ^= labels[j]
            expected.append(syndrome)
        need(all(expected) and scalar_tests(bad, labels) == expected, "bounded D fault replay")
    # Outside the promised radius, all ten tests can miss an actual scalar fault.
    blind = copy.deepcopy(w)
    blind["D"][SEED][2] = sorted(set(blind["D"][SEED][2]) ^ {240, 241, 242, 243})
    need(scalar_tests(blind, labels) == [0] * 120, "four-coefficient blind control")
    try:
        check_identity(blind)
    except ValueError as error:
        need(str(error).startswith("D parity:"), "blind control failed for another reason")
    else:
        raise ValueError("full check missed four-coefficient fault")
    need(scalar_tests(blind, [1] + [0] * 419)[SEED] == 1, "blind control basis witness")
    return {
        "test_count": 10,
        "pattern_hex": [format(pattern, "0105x") for pattern in patterns],
        "column_rule": "1 | (helper_relative_index << 1)",
        "fault_radius_per_target": 3,
        "single_supports": 420,
        "pair_supports": len(pairs),
        "triple_supports": 420 * 419 * 418 // 6,
        "optimality_bound": "420 <= 2^(q-1), hence q >= 10",
        "blind_four_support": [240, 241, 242, 243],
        "blind_target": 120 + SEED,
        "blind_witness_dirty_helper": 240,
    }


def negative_controls(w):
    rejected = []

    def reject(name, mutant):
        try:
            check_identity(mutant)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("control accepted: " + name)

    # One selected omission in every D row, with all covectors recomputed.
    for t in range(120):
        bad = copy.deepcopy(w)
        del bad["D"][t][2][(SEED + t) % len(bad["D"][t][2])]
        reject("omit_D_operand_" + str(t), bad)
    bad = copy.deepcopy(w)
    bad["D"] = []
    reject("omit_D", bad)
    bad = copy.deepcopy(w)
    bad["D"][SEED][2].append(bad["D"][SEED][2][0])
    reject("duplicate_D_operand", bad)
    bad = copy.deepcopy(w)
    bad["D"][SEED][1], bad["D"][SEED + 1][1] = bad["D"][SEED + 1][1], bad["D"][SEED][1]
    reject("swap_D_targets", bad)
    bad = copy.deepcopy(w)
    bad["A"].reverse()
    reject("wrong_A_order", bad)
    bad = copy.deepcopy(w)
    bad["B"].reverse()
    reject("wrong_B_order", bad)
    bad = copy.deepcopy(w)
    bad["ret"] = [240 + k for k in range(len(w["ret"]))]
    reject("wrong_scatter_helpers", bad)
    bad = copy.deepcopy(w)
    bad["scatter"][SEED].pop()
    reject("omit_scatter_operand", bad)
    bad = copy.deepcopy(w)
    bad["D"][SEED][2][0] = SEED
    reject("D_reads_source", bad)
    bad = copy.deepcopy(w)
    bad["A"][SEED][2].append(bad["A"][SEED][1])
    reject("self_alias", bad)
    # Even duplicate occurrences cancel; lists must retain XOR multiplicity.
    same = copy.deepcopy(w)
    operand = same["D"][SEED][2][0]
    same["D"][SEED][2].extend([operand, operand])
    need(check_identity(same) == check_identity(w), "duplicate-pair positive control")
    # Distinguish reverse transpose from simply running the gates backward.
    toy = [[0, 1, [0]], [0, 2, [1]]]
    need(pullback(1 << 2, toy) == 7, "two-gate transpose control")
    need(pullback(1 << 2, list(reversed(toy))) == 6, "order-sensitive toy control")
    return rejected


def evidence(w):
    rows = check_identity(w)
    binary = bytes((row >> col) & 1 for row in rows for col in range(420))
    controls = negative_controls(w)
    return {
        "format": "r420-compensation-optimal-test-suite-v1",
        "assignment_seed": SEED,
        "domain": {"targets": 120, "helpers": 420, "original_inputs": 660},
        "raw_sections": ["A", "scatter", "B"],
        "gate_counts": {s: len(w[s]) for s in ("D", "A", "B", "C")},
        "nonzero_entries": sum(bin(row).count("1") for row in rows),
        "zero_columns": [c for c in range(420) if all(not row & (1 << c) for row in rows)],
        "row_weight_range": [min(bin(r).count("1") for r in rows), max(bin(r).count("1") for r in rows)],
        "matrix_binary_sha256": hashlib.sha256(binary).hexdigest(),
        "suite": suite_certificate(w),
        "negative_controls": controls,
        "positive_controls": ["duplicate_D_pair", "two_gate_transpose", "two_gate_wrong_order"],
    }


def main():
    need(sys.argv[1:] in ([], ["--emit"]), "usage: verify.py [--emit]")
    result = evidence(load_word())
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = json.loads((HERE / "EXPECTED.json").read_text())
        need(result == expected, "committed certificate mismatch")
        print("PASS_R420_COMPENSATION_SUITE tests=10 optimal=10 radius=3 targets=120 blind_weight=4 controls=" + str(len(result["negative_controls"])))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise SystemExit("FAIL_R420_ADJOINT: " + str(error))
