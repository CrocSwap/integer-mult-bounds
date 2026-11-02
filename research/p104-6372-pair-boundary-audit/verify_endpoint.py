#!/usr/bin/env python3
"""Full forward rational endpoint and literal dual-block audit of frozen PR6372.

No author, local-round checker, native engine or oracle is imported. The scalar
transpose schema retains PR6355 and round1 credit. Frame labels are tracked;
MOVE acts as identity only in the rational projection, without native claims.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import gzip
from hashlib import sha1, sha256
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
PUBLIC, OWNED, ZERO, FULL = 770, 29, 3, 127
PREP_LENGTH = 4759
PREP_SHA256 = "dfa58d2c83ba427714a7c0a62e40b05b9f3a561f055f44cac6104800bea01782"
PINNED = {
    "sources/OUTPUT-WORD.json.gz": [
        "e3b6f1c25d672b8c85433be97ebad77ae6a6972352ce2ff63507d30835fcb491",
        "0af79e58172f85c302c35b193205c0b185b09393"
    ],
    "sources/BASIS.json": [
        "28d01a60c1780dc61373a13ac70654c140fa20519abdac0dd78f24c8343a002f",
        "efa2be3e34cab2d15ceaf33ff43eab70ff4c12e6"
    ],
    "sources/constructor-source.py": [
        "e18f0221827628e38674dc71198a95ccebc401476328e3db7569b84e4b7be969",
        "d92f1f92e705eafdda770ec19b958084584420a8"
    ],
    "sources/upstream-PROOF.md": [
        "4d02ec61147085ed88c11340b369729c943b954a0cc41a9995ffc07d24f1a285",
        "3a670ce4c0ae727b4d3cd3604d67d45b189da3c7"
    ],
    "sources/NOTICE": [
        "f13f42a39d4614b26d9871f5bc8fcb76e60cb44b4df8762cd51e505b43723e46",
        "9af7effd3a0ff5218d94331567022fd179a1e8fa"
    ],
    "sources/INPUT-WORD.json.gz": [
        "0c83c1f1dee8c9442558719510a61b89f38c2dbfc8fb565ba035660d2a68d928",
        "03ea7690285d4cda72815f962d5710ab96e08490"
    ]
}
START = time.monotonic()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return sha256((canonical(value) + "\n").encode()).hexdigest()


def encoded(row):
    return [[coordinate, str(value)] for coordinate, value in sorted(row.items())]


def matrix_digest(rows):
    return digest([encoded(row) for row in rows])


def authenticate():
    inventory = json.loads((HERE / "SOURCE-PINS.json").read_bytes())
    require(type(inventory) is list and len(inventory) == len(PINNED) and
            {r["file"]: [r["sha256"], r["git_blob"]] for r in inventory} == PINNED,
            "six independently pinned source files")
    data = {}
    for name, (expected_sha, expected_blob) in PINNED.items():
        raw = (HERE / name).read_bytes()
        require(sha256(raw).hexdigest() == expected_sha, "source SHA256: " + name)
        require(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == expected_blob,
                "source Git blob: " + name)
        if name.endswith(".json.gz"):
            data[Path(name).name] = json.loads(gzip.decompress(raw))
        elif name.endswith(".json"):
            data[Path(name).name] = json.loads(raw)
    return data


def integer(value, lower, upper, label):
    require(type(value) is int and lower <= value < upper, label)


def rational(value):
    require(type(value) is str, "rational coefficient string")
    result = Fraction(value)
    require(result and str(result) == value and result.denominator & (result.denominator - 1) == 0,
            "canonical nonzero dyadic coefficient")
    return result


def plus(destination, source, coefficient):
    result = dict(destination)
    for coordinate, value in source.items():
        updated = result.get(coordinate, 0) + coefficient * value
        if updated:
            result[coordinate] = updated
        else:
            result.pop(coordinate, None)
    return result


def forward(word, retain_clears=True):
    require(type(word["public"]) is int and word["public"] == PUBLIC and
            type(word["owned_fields"]) is int and word["owned_fields"] == OWNED, "770 public and29 owned labels")
    frames = word["frames"]
    require(type(frames) is list and len(frames) == 1095, "literal frame inventory")
    require(len(word["initial"]) == len(word["final"]) == PUBLIC, "public frame boundaries")
    require(type(word["program"]) is list and len(word["program"]) < 26000, "bounded literal word")
    for frame in word["initial"] + word["final"]:
        integer(frame, 0, len(frames), "public frame label")
    rows = [{r: Fraction(1)} if r < PUBLIC else {} for r in range(PUBLIC + OWNED)]
    current = dict(enumerate(word["initial"]))
    lifetime = {}
    counts, clears = Counter(), []
    initialized, peak, copy_checks = 0, 0, 0
    for index, event in enumerate(word["program"]):
        require(type(event) is list and event, "literal instruction")
        op, role = event[:2]
        integer(role, 0, PUBLIC + OWNED, "literal role")
        counts[op] += 1
        if op == "MOVE":
            require(len(event) == 5, "MOVE shape")
            _, _, start, end, private = event
            integer(start, 0, len(frames), "MOVE source frame")
            integer(end, 0, len(frames), "MOVE target frame")
            require(type(private) is bool and private == (role >= PUBLIC) and current.get(role) == start,
                    "MOVE frame and ownership chronology")
            current[role] = end
        elif op == "INIT":
            require(len(event) == 3 and role >= PUBLIC and role not in current, "owned INIT lifetime")
            integer(event[2], 0, len(frames), "INIT frame")
            rows[role] = {}
            current[role] = event[2]
            initialized += 1
            lifetime[role] = (initialized, index)
            peak = max(peak, len(lifetime))
        elif op == "CLEAR":
            require(len(event) == 3, "CLEAR shape")
            integer(event[2], 0, len(frames), "CLEAR frame")
            require(len(event) == 3 and role >= PUBLIC and role in lifetime and current.get(role) == event[2],
                    "owned CLEAR lifetime and frame")
            sequence, birth = lifetime.pop(role)
            if retain_clears:
                row = encoded(rows[role])
                clears.append({"role": role, "lifetime": sequence, "init_index": birth, "clear_index": index,
                               "frame": event[2], "public_support": len(row),
                               "row_sha256": digest(row), "row": row})
            # A forward CLEAR may discard a nonzero functional. Recording it
            # does not grant physical erasure permission.
            rows[role] = {}
            del current[role]
        elif op == "SCALE":
            require(len(event) == 4, "SCALE shape")
            integer(event[3], 0, len(frames), "SCALE frame")
            require(len(event) == 4 and current.get(role) == event[3], "active SCALE frame")
            coefficient = rational(event[2])
            rows[role] = {coordinate: coefficient * value for coordinate, value in rows[role].items()}
        else:
            require(op in ("ADD", "COPY") and len(event) == 5, "known scalar opcode and shape")
            source = event[2]
            integer(source, 0, PUBLIC + OWNED, "scalar source role")
            integer(event[4], 0, len(frames), "scalar common frame")
            require(source != role and role in current and source in current and
                    current[role] == current[source] == event[4], "active common-frame scalar operands")
            coefficient = rational(event[3])
            if op == "COPY":
                require(role >= PUBLIC and role in lifetime and not rows[role], "COPY into zero owned destination")
                copy_checks += 1
                rows[role] = {coordinate: coefficient * value for coordinate, value in rows[source].items()}
            else:
                rows[role] = plus(rows[role], rows[source], coefficient)
        if index % 256 == 0:
            require(time.monotonic() - START < 60 and sum(map(len, rows)) <= 250000,
                    "bounded full rational replay resources")
    require(not lifetime and current == dict(enumerate(word["final"])), "complete public frame exits and owned retirement")
    require(all(not row for row in rows[PUBLIC:]), "owned coordinate rows reset at exit")
    return rows[:PUBLIC], {"events": len(word["program"]), "opcode_counts": dict(sorted(counts.items())),
                           "owned_lifetimes": initialized, "peak_active_owned": peak,
                           "zero_destination_COPY_checks": copy_checks,
                           "forward_CLEAR_functionals": clears}


def expected_interface(word):
    live = word["live"]
    require(type(live) is list and len(live) == len(set(live)) == len(word["ports"]) == 104, "104 main pairs")
    require(not (set(live) & {r + 112 for r in live}), "disjoint main pairs")
    rows = [{r: Fraction(1)} for r in range(PUBLIC)]
    for role in live:
        integer(role, 0, PUBLIC - 112, "main source role")
        rows[role + 112][role] = Fraction(1)
    return rows


def first_difference(actual, expected):
    for output, (left, right) in enumerate(zip(actual, expected)):
        for coordinate in sorted(left.keys() | right.keys()):
            if left.get(coordinate, 0) != right.get(coordinate, 0):
                return {"output": output, "input": coordinate, "actual": str(left.get(coordinate, 0)),
                        "expected": str(right.get(coordinate, 0))}
    return None


def bounded_local_rank_delta(source, candidate):
    """A four-frame source property, conditional on the retained native tariff."""
    old_moves, new_moves = [Counter(tuple(e) for e in word["program"] if e[0] == "MOVE")
                            for word in (source, candidate)]
    removed, added = old_moves - new_moves, new_moves - old_moves
    require(removed == Counter({("MOVE", r, 1091, 127, False): 1 for r in (224, 227)}) and
            added == Counter({("MOVE", r, 1091, 245, False): 1 for r in (224, 227)}),
            "exactly two changed MOVE records; all other transports cancel")
    spans = {}
    for label in (3, 1091, 245, 127):
        space = {0}
        for vector in source["frames"][label]:
            integer(vector, 1, 512, "nonzero binary nine-axis basis vector")
            require(vector not in space, "independent changed-frame basis")
            space |= {point ^ vector for point in tuple(space)}
        spans[label] = space
    dimensions = {label: len(space).bit_length() - 1 for label, space in spans.items()}
    require(dimensions == {3: 0, 1091: 4, 245: 8, 127: 9} and
            spans[3] < spans[1091] < spans[245] < spans[127], "four exact nested changed-frame subspaces")
    paid, productive = Counter(), Counter()
    for records, sign in ((added, 1), (removed, -1)):
        for event, count in records.items():
            paid[abs(dimensions[event[3]] - dimensions[event[2]])] += sign * count
    mains = set(source["live"]) | {r + 112 for r in source["live"]}
    for role in (224, 227):
        require(role not in mains and source["initial"][role] == candidate["initial"][role] == 3,
                "two changed productive helper boundaries")
        productive[dimensions[candidate["final"][role]] - dimensions[3]] += 1
        productive[dimensions[source["final"][role]] - dimensions[3]] -= 1
    require(dict(paid) == {4: 2, 5: -2} and dict(productive) == {8: 2, 9: -2},
            "conditional local declared-tariff coefficient deltas")
    return {"frame_dimensions": {str(k): v for k, v in dimensions.items()},
            "strict_nesting": [3, 1091, 245, 127],
            "removed_MOVE_records": [list(event) for event in sorted(removed)],
            "added_MOVE_records": [list(event) for event in sorted(added)],
            "local_paid_delta": {str(k): v for k, v in sorted(paid.items())},
            "local_productive_delta": {str(k): v for k, v in sorted(productive.items())},
            "qualification": "Conditional on retained native implementation and frame-rank tariff semantics; not a phase proof or complete invoice."}


def dual_program(word):
    permutation = list(range(PUBLIC + OWNED))
    for role in word["live"]:
        permutation[role], permutation[role + 112] = role + 112, role
    require(len(set(permutation)) == PUBLIC + OWNED, "scalar dual role permutation")
    flip = lambda frame: FULL if frame == ZERO else ZERO if frame == FULL else frame
    out = []
    for event in reversed(word["program"]):
        op, role = event[:2]
        if op == "MOVE":
            out.append(["MOVE", permutation[role], flip(event[3]), flip(event[2]), event[4]])
        elif op in ("INIT", "CLEAR"):
            out.append(["CLEAR" if op == "INIT" else "INIT", permutation[role], flip(event[2])])
        elif op in ("ADD", "COPY"):
            out.append(["ADD", permutation[event[2]], permutation[role], event[3], flip(event[4])])
        else:
            require(op == "SCALE", "scalar dual opcode")
            out.append(["SCALE", permutation[role], event[2], flip(event[3])])
    return out


def inverse(operations):
    result = []
    for event in reversed(operations):
        op = event[0]
        if op == "ADD":
            result.append([op, event[1], event[2], str(-rational(event[3]))])
        elif op == "SCALE":
            result.append([op, event[1], str(1 / rational(event[2]))])
        else:
            require(op == "SWAP", "basis inverse opcode")
            result.append(list(event))
    return result


def emit(operations, frame):
    result = []
    for event in operations:
        if event[0] == "SWAP":
            a, b = event[1:]
            entries = [["ADD", a, b, "1"], ["ADD", b, a, "-1"],
                       ["ADD", a, b, "1"], ["SCALE", b, "-1"]]
        else:
            entries = [event]
        for row in entries:
            result.append(list(row) + [frame])
    return result


def bind_dual_blocks(source, candidate, basis):
    old, new = dual_program(source), dual_program(candidate)
    prefix = new[:PREP_LENGTH]
    require(digest(prefix) == PREP_SHA256, "immutable round1 literal preparation certificate")
    first, groups = {}, {}
    for index, event in enumerate(old):
        if event[0] != "MOVE":
            continue
        role, start, end = event[1:4]
        if role >= PUBLIC:
            require(ZERO not in (start, end), "no owned transport through dual ZERO")
        else:
            require(end != ZERO, "no public return to dual ZERO")
            if start == ZERO:
                require(role not in first, "one source first departure")
                first[role] = (index, end)
                groups.setdefault(end, []).append(role)
    anchors = basis["anchors"]
    require(anchors == [224, 227] and basis["entries"] == {"224": 245, "227": 245}, "two literal anchor entrances")
    early, moved = [], set()
    for text_role, responses in basis["responses"].items():
        role = int(text_role)
        if role in anchors:
            continue
        require(first[role][1] == 245, "nonprimary response destination")
        early.append(["MOVE", role, ZERO, 245, False])
        moved.add(role)
        for anchor, coefficient in responses.items():
            early.append(["ADD", role, int(anchor), str(rational(coefficient)), 245])
    for role in anchors:
        require(first[role][1] == 1091, "anchor first departure block")
        early.append(["MOVE", role, 245, 1091, False])
        moved.add(role)
    for role in groups[1091]:
        if role not in moved:
            early.append(["MOVE", role, ZERO, 1091, False])
            moved.add(role)
    early += emit(inverse(basis["C"]), 1091)
    require(len(early) == 30 and sorted(moved) == basis["moved"] and len(moved) == 14,
            "derived thirty-event bridge and fourteen moved public roles")
    remainder, removed, zero_count = [], [], 0
    for index, event in enumerate(old):
        if event[0] in ("ADD", "COPY", "SCALE", "INIT", "CLEAR") and event[-1] == ZERO:
            zero_count += 1
            continue
        if event[0] == "MOVE" and event[1] in moved and event[2] == ZERO:
            require(first[event[1]][0] == index, "removed exact first departure")
            removed.append({"role": event[1], "source_dual_index": index, "source_event": event})
            continue
        remainder.append(event)
    require(zero_count == 4709 and len(remainder) == 12934 and
            len(removed) == 14 and {row["role"] for row in removed} == moved, "retained source complement")
    suffix_B0 = emit(inverse(basis["B0"]), FULL)
    suffix_B2 = emit(inverse(basis["B2"]), FULL)
    require(len(suffix_B0) == 11 and len(suffix_B2) == 23, "ordered inverse suffix lengths")
    expected = prefix + early + remainder + suffix_B0 + suffix_B2
    require(canonical(new) == canonical(expected), "every literal candidate dual instruction and block order")
    return {"round1_prefix_events": PREP_LENGTH, "round1_prefix_sha256": PREP_SHA256,
            "bridge_events": len(early), "bridge_sha256": digest(early), "bridge": early,
            "replaced_departures": removed, "retained_source_events": len(remainder),
            "retained_source_sha256": digest(remainder), "B0_inverse_suffix_events": len(suffix_B0),
            "B2_inverse_suffix_events": len(suffix_B2), "ordered_suffix_sha256": digest(suffix_B0 + suffix_B2),
            "candidate_dual_events": len(new)}


def controls(candidate, basis, expected):
    result = {}
    cases = [("omitted_input_correction", "input_correction", "omit"),
             ("wrong_response_sign", "response", "sign"),
             ("omitted_departure_inverse", "departure_inverse", "omit"),
             ("wrong_output_basis_sign", "output_basis", "sign")]
    for label, site, action in cases:
        bad = deepcopy(candidate)
        index = basis["control_indices"][site]
        original = deepcopy(bad["program"][index])
        require(original[0] in ("ADD", "SCALE"), "full-word scalar control site")
        if action == "omit":
            del bad["program"][index]
            replacement = None
        else:
            bad["program"][index][-2] = str(-rational(original[-2]))
            replacement = bad["program"][index]
        matrix, _ = forward(bad, retain_clears=False)
        witness = first_difference(matrix, expected)
        require(witness is not None, "full-word fault must yield public coefficient difference")
        result[label] = {"event_index": index, "original_event": original, "replacement": replacement,
                         "public_coefficient_witness": witness}
    return result


def run():
    data = authenticate()
    source, candidate, basis = data["INPUT-WORD.json.gz"], data["OUTPUT-WORD.json.gz"], data["BASIS.json"]
    require(set(source) == set(candidate), "same word schema")
    for key in source:
        if key not in ("program", "final"):
            require(canonical(source[key]) == canonical(candidate[key]), "unchanged shared header: " + key)
    changed_initial = {str(r): [a, b] for r, (a, b) in enumerate(zip(source["initial"], candidate["initial"])) if a != b}
    changed_final = {str(r): [a, b] for r, (a, b) in enumerate(zip(source["final"], candidate["final"])) if a != b}
    require(not changed_initial and changed_final == {"224": [127, 245], "227": [127, 245]},
            "exact changed native frame labels, without native operator admission")
    before, source_info = forward(source)
    after, candidate_info = forward(candidate)
    require(first_difference(after, before) is None, "all770x770 source/candidate scalar coefficients")
    target = expected_interface(source)
    require(first_difference(before, target) is None and first_difference(after, target) is None,
            "derived scalar transfer equals identity plus104 declared main shears")
    require(source_info["owned_lifetimes"] == 41 and candidate_info["owned_lifetimes"] == 43 and
            source_info["peak_active_owned"] == candidate_info["peak_active_owned"] == 13,
            "exact source/candidate owned lifetime census")
    require(candidate["program"][-2:] == [["CLEAR", 780, 127], ["CLEAR", 779, 127]], "two actual candidate tail CLEARs")
    added = candidate_info["forward_CLEAR_functionals"][-2:]
    require([row["role"] for row in added] == [780, 779] and
            [row["clear_index"] for row in added] == [len(candidate["program"]) - 2, len(candidate["program"]) - 1],
            "added tail lifetimes bound to tracked actual INITs")
    blocks = bind_dual_blocks(source, candidate, basis)
    local_rank_delta = bounded_local_rank_delta(source, candidate)
    return {"schema_version": 1, "scope": "full rational public endpoint and literal dual bridge/suffix only",
            "public_input_columns": PUBLIC, "public_output_rows": PUBLIC,
            "coefficient_slots_compared": PUBLIC * PUBLIC,
            "source_transfer_sha256": matrix_digest(before), "candidate_transfer_sha256": matrix_digest(after),
            "nonzero_public_coefficients": sum(map(len, after)),
            "declared_main_shears": len(source["live"]), "changed_initial_frame_labels": changed_initial,
            "changed_final_frame_labels": changed_final,
            "source_census_and_CLEARs": source_info, "candidate_census_and_CLEARs": candidate_info,
            "added_tail_lifetime_bindings": [{key: row[key] for key in
                ("role", "lifetime", "init_index", "clear_index", "frame", "public_support", "row_sha256")} for row in added],
            "dual_literal_blocks": blocks, "controls": controls(candidate, basis, target),
            "bounded_local_declared_tariff": local_rank_delta,
            "limits": ["Scalar transfer equality does not equate the changed native helper operators.",
                       "MOVE is identity only in this rational projection; frame/complement/native-phase correctness is not proved.",
                       "Forward CLEAR functionals are recorded, not required zero; physical erasure remains a separate obligation.",
                       "No native, physical caller, invoice, all-width, funding or new kappa admission follows."]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit fresh JSON without retained endpoint-result comparison")
    options = parser.parse_args()
    result = run()
    if not options.emit:
        retained = HERE / "ENDPOINT-RESULT.json"
        require(retained.is_file(), "retained ENDPOINT-RESULT.json receipt must exist")
        require(canonical(json.loads(retained.read_bytes())) == canonical(result),
                "exact typed retained ENDPOINT-RESULT.json receipt")
        print("PASS complete rational endpoint and literal dual blocks")
    else:
        print(json.dumps(result, sort_keys=True, indent=2))
