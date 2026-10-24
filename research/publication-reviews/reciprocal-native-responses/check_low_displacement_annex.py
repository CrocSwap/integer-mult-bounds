#!/usr/bin/env python3
"""Review the frozen supporting responses and changed exits."""

import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import time


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("publication_arithmetic", HERE/"check_publication_review.py")
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)
PINS = {
    "run-normal/RESPONSE-PROGRAM.json": "5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c",
    "native-normal-v2/NATIVE-PROGRAM.json.gz": "aca3b3364b73e3c2115ede3082088e7566d789273711031381e44406c0ae793c",
    "reciprocal-normal-v2/EXTENSION-PROGRAM.json.gz": "825f27e5b3705dace14c75ae53aa21ea94b9dc69284bbdbd3377591fbcce7439",
    "odd16-normal-v2/EXTENSION-PROGRAM.json.gz": "7160a8764f0b12131e30dd1ca90a28b781b9dd99e8eb2f1935b8592aaf48037b",
    "coded-normal/CODED-EXITS-PROGRAM.json.gz": "aad4decc178d7b9ac19ef4b97d3b77d56854c26714f063e1ff6fa762cf2b6b08",
}


def determinant(matrix):
    work = [dict(row) for row in matrix]
    result = F(1)
    for column in range(len(work)):
        pivot = next((i for i in range(column, len(work)) if work[i].get(column)), None)
        if pivot is None:
            return F(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        value = work[column][column]
        result *= value
        for i in range(column+1, len(work)):
            scale = work[i].get(column, 0)/value
            if scale:
                for j, entry in work[column].items():
                    a.put(work[i], j, -scale*entry)
    return result


def restrict(matrix, indices):
    return [{j: matrix[p][q] for j, q in enumerate(indices) if q in matrix[p]} for p in indices]


def expected_map(response, backward):
    result = a.eye(640)
    for i, row in enumerate(response):
        for j, value in row.items():
            a.put(result[j if backward else 112+i], 112+i if backward else j, -value if backward else value)
    return result


def physical_model(model, correction_rank):
    e, ei = a.rows(model["response"]), a.rows(model["response_inverse"])
    a.need(a.mul(e, ei) == a.mul(ei, e) == a.eye(112), "Supporting inverse orders")
    delta = a.plus(e, a.eye(112), -1)
    a.need(a.rank(delta) == correction_rank, "Supporting correction rank")
    if "correction_U" in model:
        u, v = a.rows(model["correction_U"]), a.rows(model["correction_V"])
        a.need(a.mul(u, v) == delta and a.rank(u) == a.rank(v) == correction_rank, "Supporting correction factor")
    ordinary = model["ordinary_ports"]
    principal = restrict(e, ordinary)
    inverse = a.rows(model["ordinary_inverse"])
    a.need(a.mul(principal, inverse) == a.mul(inverse, principal) == a.eye(104), "Ordinary inverse orders")
    selected = model["selected_ports"]
    l = a.rows(model["selected_block"])
    a.need(restrict(e, selected) == l and a.mul(l, l) == [{i: F(1, 2)} for i in range(8)], "Selected block")
    expected_det = 2**25 if correction_rank == 30 else 35**8
    expected_ordinary = F(2**21) if correction_rank == 30 else F(7**8*31**4, 16)
    a.need(determinant(e) == expected_det and determinant(principal) == expected_ordinary, "Supporting determinants")
    if correction_rank == 16:
        inverse_selected = a.plus([{i: F(4, 5)} for i in range(8)], l, F(1, 5))
        a.need(restrict(ei, selected) == inverse_selected, "Changed selected inverse")
        denominators = Counter(value.denominator for row in inverse for value in row.values())
        a.need(denominators == {7: 512, 31: 568, 62: 640}, "Prime 31 in ordinary inverse")
        a.need(a.transpose(e, 112) == e, "Rank16 symmetry")
    else:
        a.need(restrict(ei, selected) == l, "Rank30 inverse selected block")
    return {"rank": correction_rank, "determinant": str(expected_det), "ordinary_determinant": str(expected_ordinary)}


def as_tuple(value):
    return tuple(map(as_tuple, value)) if isinstance(value, list) else value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    start = time.monotonic()
    source_dir = args.source_root/"lanes/new-core-transfer-20261017/low-displacement-20261020"
    for name, digest in PINS.items():
        a.need(sha256((source_dir/name).read_bytes()).hexdigest() == digest, "Supporting input " + name)
    base = a.read(source_dir/"run-normal/RESPONSE-PROGRAM.json")
    raw = a.read(source_dir/"native-normal-v2/NATIVE-PROGRAM.json.gz")
    reciprocal = a.read(source_dir/"reciprocal-normal-v2/EXTENSION-PROGRAM.json.gz")
    odd = a.read(source_dir/"odd16-normal-v2/EXTENSION-PROGRAM.json.gz")
    coded = a.read(source_dir/"coded-normal/CODED-EXITS-PROGRAM.json.gz")
    reports = {"rank30": physical_model(base, 30), "reciprocal_large": physical_model(reciprocal["model"], 30),
               "rank16": physical_model(odd["model"], 16)}
    raw_reports = {}
    for name, model, packet, scalar, profile in (
        ("rank30", base, raw, 5288, {1: 1036, 3: 48, 4: 55, 5: 55, 6: 9, 7: 9}),
        ("reciprocal_large", reciprocal["model"], reciprocal, 5288, {1: 1036, 3: 48, 4: 55, 5: 55, 6: 9, 7: 9}),
        ("rank16", odd["model"], odd, 7384, {1: 1520, 2: 64, 3: 48}),
    ):
        for provider, directions in packet["providers"].items():
            for direction, word in directions.items():
                expected = expected_map(a.rows(model["response"]), direction == "backward")
                raw_reports[name+"/"+provider+"/"+direction] = a.word_check(word, expected, profile, scalar)
        for word_name, gates in model.get("common_frame_words", {}).items():
            state, cost, _, _ = a.scalar_replay(gates, 112)
            expected = a.rows(model["response_inverse"] if "inverse" in word_name else model["response"])
            if "transpose" in word_name:
                expected = a.transpose(expected, 112)
            a.need(state == expected and cost == 3210, "Supporting common-frame scalar code")

    model = odd["model"]
    u, v, q = a.rows(model["correction_U"]), a.rows(model["correction_V"]), model["ports"]
    histogram = Counter()
    for character in range(512):
        moved = [{j: value*(-1 if (q[p] & character).bit_count() % 2 else 1) for j, value in row.items()} for p, row in enumerate(u)]
        histogram[a.rank(a.mul(v, moved))] += 1
    a.need(histogram == {0: 32, 4: 96, 8: 12, 14: 256, 16: 116}, "Independent cross-Gram rank census")

    phase_path = args.source_root/"lanes/interface-proof/verify_native_lift.py"
    phase_spec = importlib.util.spec_from_file_location("supporting_phase_engine", phase_path)
    phase = importlib.util.module_from_spec(phase_spec)
    phase_spec.loader.exec_module(phase)
    changed = {}
    coded_reports = {}
    raw_packets = {"rank30": raw, "rank16": odd}
    a.need(base["ports"] == odd["model"]["ports"], "Same physical directions")
    fourier = [["C", 1 << i, 1] for i in range(9)]
    s0 = ["D", [1]+[0]*8, [1]+[0]*8]
    gauge = [s0, ["C", 45, 1], s0]
    profiles = {
        ("rank30", "W48_I64"): {1: 988, 2: 48, 4: 55, 5: 55, 6: 9, 7: 9},
        ("rank30", "W112"): {1: 988, 2: 48, 5: 55, 6: 55, 7: 9, 8: 9},
        ("rank16", "W48_I64"): {1: 1472, 2: 112},
        ("rank16", "W112"): {1: 1408, 2: 112, 3: 64},
    }
    for name, codes in coded["providers_by_response_and_code"].items():
        for code, providers in codes.items():
            for provider, directions in providers.items():
                for direction, word in directions.items():
                    raw_word = raw_packets[name]["providers"][provider][direction]
                    coded_ports = set(range(112)) if code == "W112" else set(base["large_ports"])
                    a.need(set(word["left_W_ports"]) == coded_ports and set(word["raw_output_ports"]) == set(range(112))-coded_ports, "Exact coded port set")
                    a.need(word["gauge_circuit"] == gauge, "Literal S_e0 C_45 S_e0 code")
                    a.need(word["start"] == raw_word["start"], "Unchanged input frame ids")
                    a.need(word["frames"][:len(raw_word["frames"])] == [{"kind": "canonical", "basis": f} for f in raw_word["frames"]], "Unchanged ordered canonical frames")
                    endpoints = [record for record in raw_word["endpoint_adapters"] if record["role"] == "source" or record["port"] not in coded_ports]
                    a.need(word["endpoint_adapters"] == endpoints, "Exact retained endpoint records")
                    for p in range(112):
                        if p in coded_ports:
                            for field, circuit in ((p, fourier+gauge), (112+p, [["C", base["ports"][p], -1]]+fourier+gauge)):
                                frame = word["frames"][word["final"][field]]
                                a.need(frame["kind"] == "literal" and frame["circuit"] == circuit, "Literal W F9 Q inverse output order")
                        else:
                            a.need(word["final"][p] == raw_word["final"][p] and word["final"][112+p] == raw_word["final"][112+p], "Unchanged uncoded exits")
                    current, census, monomials, gates = list(word["start"]), Counter(), 0, []
                    a.need(len(word["events"]) == len(raw_word["events"]), "One event per original position")
                    for event, raw_event in zip(word["events"], raw_word["events"]):
                        if event[0] == "scalar":
                            gate, frame = event[1:]
                            if gate[0] == "add":
                                _, target, source, num, den = gate
                                a.need(current[source] == frame and 0 <= source < 224, "Coded source access")
                            else:
                                _, target, num, den = gate
                                source = None
                            a.need(current[target] == frame and 0 <= target < 224, "Coded target access")
                            gates.append([gate[0], target, source, str(F(num, den))])
                            a.need(raw_event[:2] == ["scalar", gates[-1]], "Scalar operation and coefficient unchanged")
                            if raw_event[2] != frame:
                                fields = [target] if source is None else [target, source]
                                a.need(all(raw_event[2] == raw_word["final"][p] and frame == word["final"][p]
                                           and p % 112 in coded_ports for p in fields), "Scalar access changes only to its completed coded output frame")
                            continue
                        field, old, new, key = event[1], event[2], event[3], event[-1]
                        a.need(0 <= field < 224 and current[field] == old, "Coded transformation entry")
                        current[field] = new
                        record = word["native_recipes"][key]
                        if event[0] == "native":
                            a.need(event[4] == record["rank"] > 0, "Coded native rank")
                            census[event[4]] += 1
                        else:
                            a.need(event[0] == "monomial" and record["rank"] == 0, "Explicit rank-zero map")
                            monomials += 1
                        if key.startswith("coded:"):
                            a.need(raw_event[0] == "native" and raw_event[1:3] == event[1:3] and raw_event[3] == raw_word["final"][field], "Only the final physical exit changes")
                            objects = [word["frames"][old], word["frames"][new], record]
                            changed[json.dumps(objects, sort_keys=True)] = objects
                        else:
                            a.need(event == raw_event and record == raw_word["native_recipes"][key], "Exact inherited native occurrence and recipe")
                    state, scalar, peak, height = a.scalar_replay(gates, 640)
                    a.need(state == expected_map(a.rows(coded["responses"][name]), direction == "backward"), "Coded 640-column content")
                    a.need(current == word["final"] and current[224:] == word["start"][224:], "Coded final frames and outside restoration")
                    a.need(census == profiles[name, code] and monomials == 48, "Coded profile and monomial count")
                    a.need(scalar == (5288 if name == "rank30" else 7384), "Coded scalar invoice")
                    a.need(len(word["endpoint_adapters"]) == (112 if code == "W112" else 176), "Coded endpoint census")
                    coded_reports[name+"/"+code+"/"+provider+"/"+direction] = {
                        "profile": dict(census), "children": sum(census.values()), "mass": sum(k*v for k, v in census.items()),
                        "scalar": scalar, "inline_monomials": monomials, "endpoints": len(word["endpoint_adapters"]),
                        "prefix_one_norm": str(peak), "binary_height": height,
                    }
    a.need(len(changed) == 352, "Changed exit recipe count")
    for old, new, record in changed.values():
        def frame(value):
            return phase.frame(value["basis"], 9) if value["kind"] == "canonical" else as_tuple(value["circuit"])
        phase.equal(phase.recipe(record), phase.adjoint(frame(old))+frame(new), "Supporting changed exit")
    for name, digest in PINS.items():
        a.need(sha256((source_dir/name).read_bytes()).hexdigest() == digest, "Supporting input unchanged")
    result = {"status": "PASS_SUPPORTING_LOW_DISPLACEMENT_REVIEW", "python": sys.version,
              "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(), "input_sha256": PINS,
              "response_models": reports, "raw_native_words": raw_reports, "cross_gram_rank_census": dict(histogram),
              "coded_words": coded_reports, "changed_exit_exact_phase_checks": len(changed),
              "phase_engine_sha256": sha256(phase_path.read_bytes()).hexdigest(),
              "scope": "Independent rational maps, scalar prices, typed frame ledger, and 352 changed-exit phases with the existing compiler-independent engine. Inherited raw phases and physical endpoints retain the pinned predecessor reviews. No odd-grid admission or supplier replay.",
              "elapsed_seconds": round(time.monotonic()-start, 3)}
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(result["status"])


if __name__ == "__main__":
    main()
