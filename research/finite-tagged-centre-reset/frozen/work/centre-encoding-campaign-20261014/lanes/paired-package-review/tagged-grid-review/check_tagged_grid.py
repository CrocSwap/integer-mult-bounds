"""Check the tagged grid word without importing a research producer."""

import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
ROOT = LANES.parents[2]
PINS = {
    "core": (LANES / "history-encoding/FULL-MODE-PROGRAMS.json.gz", "f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205", True),
    "interface": (LANES / "circuit-interface/INTERFACE.json", "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3", False),
    "canonical": (ROOT / "work/five-pr-sprint-20261013/lanes/centre-sharing/CANONICAL-WORD.json.gz", "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219", False),
    "word": (LANES / "schur-selection/finite-grid/REDUNDANT-GRID-WORD.json.gz", "26247471aaca9c8b80f365c0f012fa93000c8bd10db0e4ff74d0cdace9e85e87", False),
    "receipt": (LANES / "schur-selection/finite-grid/REDUNDANT-GRID-CHECK.json", "fd7b11c4d6ea5855b1901445fd219b14dbcc94de511c4ff003bafdd5ef6752eb", False),
    "producer": (LANES / "schur-selection/finite-grid/check_redundant_grid.py", "90c7b4fdeac34f6a04c39da323c082e45ce7385e76afd6003b997d7acce683ba", False),
    "proof_v2": (LANES / "schur-selection/finite-grid/GRID-RESET-PROOF-V2.md", "40fa4d2cbd2a6cfa3a7ec6facd81e04af727b18d77bed11643b13f19e38428e7", False),
    "carrier_addendum": (LANES / "schur-selection/finite-grid/CARRIER-RESOLUTION.md", "1dd7b6bcb4e38b576abb549fe92283c762a20d435733768dceea69adbd0ed754", False),
    "precision_contract": (LANES / "temporal-reuse/HETEROGENEOUS-PRECISION-CONTRACT.md", "4c47389d756d61fea7a672e03494e5219d83bbd7d1b2f7526a62cf411edc6607", False),
    "physical_review": (HERE.parent / "centre-reset-review/REVIEW-V2.json", "b2086bd9bb0e62c6fb8120f011c0ec307f20d7e084db6b5074c9bf75bb3cd7cc", False),
    "native_review": (LANES / "interface-proof/FULL-MODE-PORT-REVIEW.json", "ff123b08b3ac58f20d12d4fbec575472086ace1708d3242519884dbffe534372", False),
}
CENTRES = [92, 57, 81, 224, 11, 240, 9, 256]
MODES = [225, 226, 229, 232, 241, 242, 257, 258]
CUT, RESUME = 12995, 13004


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def add(target, source, scalar):
    for key, value in source.items():
        result = target.get(key, 0) + scalar * value
        if result:
            target[key] = result
        else:
            target.pop(key, None)


def scalar(event):
    gate = event[1]
    return gate[0], gate[1][1], gate[2][1] if gate[0] == "add" else None, Q(*gate[-2:])


def step(rows, event):
    if event[0] == "scalar":
        kind, target, source, value = scalar(event)
        if kind == "add":
            add(rows[target], rows[source], value)
        else:
            rows[target] = {key: value * entry for key, entry in rows[target].items()}


def round_grid(value, grid):
    numerator = (value / grid + Q(1, 2))
    return grid * (numerator.numerator // numerator.denominator)


def decode_literal(word, value, grid, delta):
    state = {"L": value, "C0": Q(0)}
    for operation in word:
        op, target = operation[:2]
        if op == "COPY":
            need(state[operation[2]] == 0, "COPY uses a zero private target")
            state[operation[2]] = state[target]
        elif op == "ROUND":
            state[target] = round_grid(state[target], grid)
        elif op == "ADD":
            state[target] += operation[3] * state[operation[2]]
        elif op == "SCALE":
            factor = 1 / delta if operation[2] == "delta^-1" else Q(operation[2])
            state[target] *= factor
        elif op == "CLEAR":
            state[target] = Q(0)
        else:
            raise ValueError("Unknown decoder instruction")
    need(state["C0"] == 0, "The decoder clears its owned field")
    return state["L"]


def main(args):
    data = {}
    for name, (path, pin, decompressed) in PINS.items():
        raw = path.read_bytes()
        payload = gzip.decompress(raw) if decompressed else raw
        need(sha256(payload).hexdigest() == pin, "Source pin: " + name)
        if path.suffix in (".json", ".gz"):
            data[name] = json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)
    events, canonical, word, reference = data["core"]["backward"], data["canonical"], data["word"], data["receipt"]
    need(len(events) == 25457, "Complete source event count")
    need(word["prefix_source_events"] == [0, CUT] and word["suffix_source_events"] == [RESUME, len(events)], "Exact source chronology")
    need(word["cut_centre_fields"] == CENTRES, "Exact centre order")
    need(word["cut_coarse_round_fields"] == [j for j in range(704) if j not in CENTRES], "Every other cut field is rounded")
    need(word["exit_round_fields"] == list(range(704)), "Every output field is rounded")
    need(word["entry"][0] == ["CLEAR", "C0"] and word["entry"][1][:2] == ["FOR_EACH", list(range(224))], "Both data banks are tagged")
    tag = word["entry"][1][2]
    need(tag == [["COPY", "L", "C0"], ["SCALE", "C0", "delta"], ["ADD", "L", "C0", 1], ["CLEAR", "C0"]], "The tag uses only legal unit scales")
    counts = Counter({"CLEAR": 1, "ROUND": 696 + 704})
    for op in tag:
        counts[op[0]] += 224
    for op in word["cut_centre_word"]:
        counts[op[0]] += 8
    need(dict(counts) == {"CLEAR": 233, "ROUND": 1416, "COPY": 232, "SCALE": 240, "ADD": 240}, "Complete added field pass invoice")
    need(sum(counts.values()) == 2361, "Total added passes")

    rows = [{j: Q(1)} for j in range(704)]
    frames = canonical["start"][:]
    inputs = {}
    denominator = growth = 0
    rank_profile = Counter()
    for index, event in enumerate(events):
        if event[0] == "scalar":
            kind, target, source, value = scalar(event)
            need(frames[target] == event[2] and (source is None or frames[source] == event[2]), "Actual scalar frame")
            denominator += value.denominator.bit_length() - 1
            growth += (abs(value.numerator) + value.denominator).bit_length()
        elif event[0] == "climb":
            need(frames[event[2]] == event[3], "Actual native input frame")
            frames[event[2]] = event[4]
            rank_profile[event[5]] += 1
            if index < CUT:
                inputs[index] = rows[event[2]].copy()
        if index == CUT:
            cut_rows = [row.copy() for row in rows]
            cut_frames = frames[:]
            for field, mode in zip(CENTRES, MODES):
                rows[field] = {mode: Q(1)}
        elif CUT < index < RESUME:
            need(event == ["scalar", ["scale", ["L", CENTRES[index-CUT-1]], -1, 1], 415+index-CUT-1], "Only the eight signs are omitted")
        else:
            step(rows, event)
    expected = [{j: Q(1), 112+j: Q(-1)} if j < 112 else {j: Q(1)} for j in range(704)]
    need(rows == expected, "All 704 output rows give unit backward data and all 480 helpers")
    need(frames == canonical["final"], "All inherited physical endpoints")
    need([cut_frames[j] for j in CENTRES] == list(range(415, 423)), "All centre decoder frames")
    need(denominator == 16339 and growth == 49012, "Exact conservative scalar bounds")
    need(sum(rank*count for rank, count in rank_profile.items()) == 5522 and sum(rank_profile.values()) == 3486, "Complete native census")
    r = [{int(j): Q(value) for j, value in row.items()} for row in data["interface"]["R"]]
    for k, field in enumerate(CENTRES):
        row = {MODES[k]: Q(1)}
        add(row, {112+j: value for j, value in r[k].items()}, Q(1, 4))
        need(cut_rows[field] == row, "Exact full centre input row")

    response = [{CENTRES.index(j): Q(1)} if j in CENTRES else {} for j in range(704)]
    sensitive = {}
    for index in range(CUT-1, -1, -1):
        event = events[index]
        if event[0] == "climb" and response[event[2]]:
            sensitive[index] = response[event[2]].copy()
            need(any(j < 224 for j in inputs[index]) and any(j >= 224 for j in inputs[index]), "Each fine native input is mixed")
        elif event[0] == "scalar":
            kind, target, source, value = scalar(event)
            if kind == "add":
                add(response[source], response[target], value)
            else:
                response[target] = {j: value * entry for j, entry in response[target].items()}
    published = {item["source_event"]: item for item in reference["active_native_events"]}
    need(set(sensitive) == set(published), "The complete fine native set")
    for index, column in sensitive.items():
        need(column == {j: Q(v) for j, v in published[index]["centre_response"]}, "Each exact native response")
        need(inputs[index] == {j: Q(v) for j, v in published[index]["input"]}, "Each complete native input")
    fine_profile = Counter(events[index][5] for index in sensitive)
    need(fine_profile == {1: 124, 4: 8}, "Fine rank profile")
    # Direct impulses use forward scalar propagation, not the reverse equations.
    for index, target_column in sensitive.items():
        pulse = [Q(0)] * 704
        pulse[events[index][2]] = Q(1)
        for event in events[index+1:CUT]:
            if event[0] == "scalar":
                kind, target, source, value = scalar(event)
                if kind == "add":
                    pulse[target] += value * pulse[source]
                else:
                    pulse[target] *= value
        need({k: pulse[field] for k, field in enumerate(CENTRES) if pulse[field]} == target_column, "Direct native impulse at all eight physical centres")

    decoder_cases = 0
    for exponent in (2, 5, 9):
        grid, delta = Q(1, 2**exponent), Q(1, 4096)
        for h in range(-17, 18):
            for q in range(-17, 18):
                for error in (-delta*grid/16, Q(0), delta*grid/16):
                    z = (h+q)*grid + delta*q*grid + error
                    need(decode_literal(word["cut_centre_word"], z, grid, delta) == h*grid, "Literal signed finite decoder")
                    decoder_cases += 1
    grid, delta = Q(1, 16), Q(1, 1024)
    need(decode_literal(word["cut_centre_word"], (1+delta)*grid+grid/32, grid, delta) != 0, "Coarse accuracy alone must fail")
    need(round_grid((1+delta)*grid+grid/32, grid) == grid, "First coarse snap remains exact in the control")
    # A native C1 half-grid output cannot meet a small relative return error.
    parent_quantum = Q(1, 2**24)
    small_native_component = parent_quantum/2
    relative_error = abs(round_grid(small_native_component, parent_quantum)-small_native_component)/parent_quantum
    need(relative_error == Q(1, 2), "Parent return rounding needs an absolute error budget")

    margin_cases = 0
    for t in (0, 1, 7, 31):
        for e in (1, 2, 11, 73):
            for b in (0, 1, 9):
                for width in (1, e):
                    h, g_bound = 5522*width+16339, 5522*width+49012
                    p, g = 2*b*e+2*h+4*g_bound+32, t+b*e
                    need((g+h+4)-(2*g+2*h+g_bound+8) == -g-h-g_bound-4, "Delta and delta exponents")
                    coarse_slack = t+p-18-2*g_bound-g-h-4
                    fine_slack = 2*t+p-18-2*g_bound-2*g-2*h-g_bound-8
                    suffix_slack = t+p-18-3*g_bound-g-2*h-4
                    need((coarse_slack, fine_slack, suffix_slack) == (b*e+h+2*g_bound+10, g_bound+6, b*e+g_bound+10), "Three exact exponent margins")
                    need(2*g+h+g_bound+4 <= 2*t+p and g+2*h <= 2*t+p, "Exact tags and output grids fit the parent format")
                    margin_cases += 1
    insertion_sites = len(events) + sum(rank_profile.values()) + sum(counts.values())
    need(insertion_sites == 31304 and insertion_sites < 2**16, "Complete local error insertion budget")

    minor = [0, 7, 20, 27, 36, 46, 57, 111]
    a = [[row.get(j, Q(0)) for j in minor] for row in r]
    need(all(sum(a[i][k]*a[j][k] for k in range(8)) == 4*int(i == j) for i in range(8) for j in range(8)), "Actual full rank carrier minor")
    carrier_cases = 0
    for g in (4, 9, 17):
        for delta in (Q(1, 2), Q(1, 32), Q(1, 2**20)):
            for s in (Q(-1, 8), Q(0), Q(1, 8)-Q(1, 2**g)):
                first, second = Q(1, 8)+delta*s, Q(1, 8)+delta*(s+Q(1, 2**g))
                difference = second-first
                need(Q(1, 16) <= first <= second <= Q(3, 16), "Fixed nonzero carrier size")
                need(Q(16, 3)*delta*Q(1, 2**g) <= difference/first <= 16*delta*Q(1, 2**g), "Exact relative separation")
                threshold = difference/(first+second)
                shared = 2*first*second/(first+second)
                need(abs(shared-first)/first == abs(shared-second)/second == threshold, "Two relative error balls have a common point")
                carrier_cases += 1
    result = {"status": "PASS_INDEPENDENT_TAGGED_GRID_LOCAL_CONTRACT", "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
              "source_pins": {name: pin for name, (_, pin, _) in PINS.items()},
              "complete_input_columns": 704, "restored_helper_contents": 480,
              "fine_native_count": len(sensitive), "fine_native_profile": dict(sorted(fine_profile.items())), "fine_native_mass": 156,
              "direct_native_impulses": len(sensitive), "native_rank_mass": 5522,
              "scalar_denominator_sum": denominator, "scalar_growth_upper_sum": growth,
              "added_field_operations": dict(sorted(counts.items())), "added_field_passes": sum(counts.values()),
              "local_error_insertion_sites": insertion_sites, "exact_decoder_cases": decoder_cases,
              "exact_margin_cases": margin_cases, "relative_carrier_cases": carrier_cases,
              "controls": {"coarse_accuracy_fails_fine_decoder": True, "relative_parent_conversion_minimum_error": str(relative_error)},
              "scope": "Local exact finite-grid reset with a relative child computation error and a separate absolute parent return error. Actual native recipes are inherited. Caller input-grid conversion, complete node endpoint, full tape invoice and kappa remain outside this review."}
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2)+"\n")
    print(result["status"])
    print(sha256(args.out.read_bytes()).hexdigest())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=HERE / "CHECKS.json")
    main(parser.parse_args())
