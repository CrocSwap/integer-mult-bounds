"""Independent rational audit of the frozen PR6353 joint output basis.

No supplier constructor, retained replay, native-phase checker or price engine
is imported.  MOVE is the identity in this scalar projection.  A scalar CLEAR
discards its row; this audit does not infer the permission to erase that row.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
ZERO, FULL, PUBLIC, OWNED = 3, 127, 770, 29
ANCHORS = (703, 393, 707, 484, 297, 485, 226, 361, 451)
PINS = {
    "INPUT-WORD.json.gz": ("1415a62059ed62d0b4657db91f7ec01b23c117f5f2744746d93c880bd777be92", "f21f7ac451c3f2e1ae8d5ca1dcad839a0b0d844f"),
    "OUTPUT-WORD.json.gz": ("0c83c1f1dee8c9442558719510a61b89f38c2dbfc8fb565ba035660d2a68d928", "03ea7690285d4cda72815f962d5710ab96e08490"),
    "BASIS.json": ("e7bd061436c5fdbd1b968f9252cc79efda04320cf3c027a6fdcdf14ff4c9d2d3", "b35a19d4ec44aa365501ef0299a4b11f9cba3e00"),
    "PROOF.md": ("cd400ad5d82d316e469bd5df81e4fc26faf1ba0aaa385a5f9964ec4786a9de5d", "d27ef41f57d7d75293515e56dc5c21c3e6cff0d7"),
    "NOTICE": ("6c5f4a452f7d65ef8ca0980992dce279938b0a1139f6c067f91de78bf8ecb7bd", "e6cae17f778e8e31b7c294ff2890c545978931c0"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, lower, upper, label):
    require(type(value) is int and lower <= value < upper, label)
    return value


def rational(value):
    require(type(value) is str and value and value.strip() == value,
            "A coefficient must be a rational string")
    result = Fraction(value)
    require(str(result) == value, "Canonical rational coefficient")
    return result


def load_inputs():
    out = {}
    for name, (expected_sha, expected_blob) in PINS.items():
        raw = (HERE / "sources" / name).read_bytes()
        require(sha256(raw).hexdigest() == expected_sha, "SHA256 pin: " + name)
        require(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
                == expected_blob, "Git blob pin: " + name)
        if name.endswith(".json.gz"):
            out[name] = json.loads(gzip.decompress(raw))
        elif name.endswith(".json"):
            out[name] = json.loads(raw)
    return out


def validate_word(word):
    require(type(word) is dict, "Word is an object")
    require(type(word["public"]) is int and word["public"] == PUBLIC,
            "Exactly 770 independent public inputs")
    require(type(word["owned_fields"]) is int and word["owned_fields"] == OWNED,
            "Exactly 29 owned labels")
    require(type(word["frames"]) is list and len(word["frames"]) in (1094, 1095),
            "Frozen frame inventory")
    for frame in word["frames"]:
        require(type(frame) is list, "Frame is a basis list")
        for value in frame:
            integer(value, 1, 512, "GF(2)^9 frame vector")
    for key in ("initial", "final"):
        require(type(word[key]) is list and len(word[key]) == PUBLIC, key)
        for frame in word[key]:
            integer(frame, 0, len(word["frames"]), "Boundary frame")
    require(type(word["live"]) is list and len(word["live"]) == 104,
            "104 main pairs")
    require(len(set(word["live"])) == 104, "Distinct main pairs")
    for role in word["live"]:
        integer(role, 0, PUBLIC - 112, "Main left role")
    main = set(word["live"]) | {r + 112 for r in word["live"]}
    require(len(main) == 208, "Disjoint main pair roles")
    require(type(word["program"]) is list, "Literal program")
    for event in word["program"]:
        require(type(event) is list and event, "Event is a list")
        op = event[0]
        require(op in ("MOVE", "ADD", "COPY", "SCALE", "INIT", "CLEAR"),
                "Known event")
        require(len(event) == {"MOVE": 5, "ADD": 5, "COPY": 5,
                               "SCALE": 4, "INIT": 3, "CLEAR": 3}[op],
                "Event arity")
        integer(event[1], 0, PUBLIC + OWNED, "Event role")
        if op == "MOVE":
            integer(event[2], 0, len(word["frames"]), "MOVE source frame")
            integer(event[3], 0, len(word["frames"]), "MOVE target frame")
            require(type(event[4]) is bool, "Boolean MOVE flag")
        else:
            integer(event[-1], 0, len(word["frames"]), "Scalar/lifetime frame")
            if op in ("ADD", "COPY"):
                integer(event[2], 0, PUBLIC + OWNED, "Scalar source role")
                rational(event[3])
            elif op == "SCALE":
                require(rational(event[2]) != 0, "Invertible SCALE")
            else:
                require(event[1] >= PUBLIC, "Owned lifetime label")


def units(count=PUBLIC):
    return [{i: Fraction(1)} for i in range(count)]


def add_row(destination, source, coefficient):
    # Read the old source before modifying destination, including a self-ADD.
    for column, value in tuple(source.items()):
        value = destination.get(column, 0) + coefficient * value
        if value:
            destination[column] = value
        else:
            destination.pop(column, None)


def basis_apply(rows, operations):
    for event in operations:
        require(type(event) in (list, tuple) and event, "Basis event")
        op = event[0]
        require(op in ("ADD", "SCALE", "SWAP"), "Basis opcode")
        require(len(event) == (4 if op == "ADD" else 3), "Basis arity")
        r = integer(event[1], 0, PUBLIC, "Basis destination")
        if op == "ADD":
            s = integer(event[2], 0, PUBLIC, "Basis source")
            add_row(rows[r], rows[s], rational(event[3]))
        elif op == "SWAP":
            s = integer(event[2], 0, PUBLIC, "Basis swap role")
            rows[r], rows[s] = rows[s], rows[r]
        else:
            coefficient = rational(event[2])
            require(coefficient != 0, "Basis SCALE nonzero")
            rows[r] = {c: coefficient * v for c, v in rows[r].items()}
    return rows


def inverse(operations):
    out = []
    for event in reversed(operations):
        if event[0] == "SWAP":
            out.append(list(event))
        elif event[0] == "ADD":
            out.append(["ADD", event[1], event[2], str(-rational(event[3]))])
        else:
            out.append(["SCALE", event[1], str(1 / rational(event[2]))])
    return out


def dual_program(word):
    """Scalar transpose schema, without constructing orthogonal native bases.

    Non-extreme frame labels are retained only as labels.  This is sufficient
    for ZERO extraction, literal ordering and common-frame comparisons; no
    native phase or complemented-basis assertion follows from this function.
    """
    roles = list(range(PUBLIC + OWNED))
    for r in word["live"]:
        roles[r], roles[r + 112] = r + 112, r
    require(len(set(roles)) == PUBLIC + OWNED, "Transpose role permutation")

    def frame(f):
        return FULL if f == ZERO else ZERO if f == FULL else f

    out = []
    for event in reversed(word["program"]):
        op, r = event[:2]
        r = roles[r]
        if op == "MOVE":
            out.append([op, r, frame(event[3]), frame(event[2]), event[4]])
        elif op in ("INIT", "CLEAR"):
            out.append(["CLEAR" if op == "INIT" else "INIT", r, frame(event[2])])
        elif op in ("ADD", "COPY"):
            out.append(["ADD", roles[event[2]], r, event[3], frame(event[4])])
        else:
            out.append([op, r, event[2], frame(event[3])])
    return out


def preparation(source, witness):
    program = dual_program(source)
    first, zero_gates = {}, []
    for index, event in enumerate(program):
        if event[0] == "MOVE" and event[1] < PUBLIC:
            if event[2] == ZERO:
                require(event[1] not in first, "One public departure from ZERO")
                first[event[1]] = (index, event[3])
            require(event[3] != ZERO, "No public return to ZERO")
        if event[0] in ("ADD", "COPY", "SCALE") and event[-1] == ZERO:
            require(event[0] in ("ADD", "SCALE") and event[1] < PUBLIC
                    and (event[0] == "SCALE" or event[2] < PUBLIC),
                    "ZERO preparation touches only public scalar roles")
            zero_gates.append(event[:-1])
    blocks = witness["C"]
    require(type(blocks) is dict and set(blocks) == {"234", "242", "244"},
            "Three departure blocks")
    for destination, operations in blocks.items():
        used = {e[1] for e in operations} | {
            e[2] for e in operations if e[0] in ("ADD", "SWAP")}
        require(all(r in first and first[r][1] == int(destination) for r in used),
                "Each C block has one actual first destination")
    A = basis_apply(units(), zero_gates)
    CA = deepcopy(A)
    for operations in blocks.values():
        basis_apply(CA, operations)
    return A, CA, zero_gates, first


def compose_rows(left, right):
    result = []
    for row in left:
        value = {}
        for k, coefficient in row.items():
            add_row(value, right[k], coefficient)
        result.append(value)
    return result


def encoded(rows):
    return {str(r): {str(c): str(v) for c, v in sorted(row.items())}
            for r, row in sorted(rows.items())}


def basis_checks(source, witness):
    A, CA, gates, first = preparation(source, witness)
    B0, B2 = witness["B0"], witness["B2"]
    require(len(B0) == 17 and len(B2) == 37, "Frozen basis gate counts")
    M0, M2 = basis_apply(units(), B0), basis_apply(units(), B2)
    pairing = compose_rows(CA, M0)
    combined = compose_rows(pairing, M2)
    require(all(combined[a] == {a: Fraction(1)} for a in ANCHORS),
            "All nine CA B0 B2 anchor rows are exact units")
    require(all({b: pairing[a].get(b, 0) for b in ANCHORS}
                == {b: Fraction(int(a == b)) for b in ANCHORS} for a in ANCHORS),
            "CA B0 has unit anchor pairing before off-anchor correction")
    expected_B2 = units()
    for a in ANCHORS:
        for r, coefficient in pairing[a].items():
            if r != a:
                require(r not in ANCHORS, "Off-anchor correction support")
                expected_B2[a][r] = -coefficient
    require(M2 == expected_B2, "B2 is exactly the off-anchor nilpotent correction")
    main = set(source["live"]) | {r + 112 for r in source["live"]}
    # A full helper has ZERO input and FULL output in both this source and
    # its complemented transpose; contracted source helpers are excluded.
    # Determine that interface from the frozen source, not from author labels.
    helpers = {r for r in range(PUBLIC) if r not in main
               and source["initial"][r] == ZERO and source["final"][r] == FULL}
    require(PUBLIC - len(main) == 562 and set(ANCHORS) <= helpers,
            "Nine independent full helpers among 562 source helper roles")
    for operations in (B0, B2):
        used = {e[1] for e in operations} | {
            e[2] for e in operations if e[0] in ("ADD", "SWAP")}
        require(used <= helpers, "Input bases act only on full helper channels")
    require(all(set(CA[a]) <= helpers for a in ANCHORS),
            "Anchor preparation has helper-only support")
    responses = {r: {a: row[a] for a in ANCHORS if a in row}
                 for r, row in enumerate(pairing) if any(a in row for a in ANCHORS)}
    require(encoded(responses) == witness["responses"],
            "All serialized response coefficients derive from the actual source")
    directions = {a: {r: row[a] for r, row in enumerate(M0) if a in row}
                  for a in ANCHORS}
    require(encoded(directions) == witness["directions"], "All nine B0 directions")
    require(all(M2[r].get(a, 0) == int(r == a)
                for r in range(PUBLIC) for a in ANCHORS), "B2 fixes every anchor input")
    shadow = units()
    for a in ANCHORS:
        shadow[a] = {}
    for operations in (B2, B0, gates, *witness["C"].values()):
        basis_apply(shadow, operations)
    require(all(not shadow[a] for a in ANCHORS),
            "All nine dual temporary rows are zero at their CLEAR")
    for label, operations in (("B0", B0), ("B2", B2), *witness["C"].items()):
        require(basis_apply(basis_apply(units(), operations), inverse(operations))
                == units(), "Exact basis inverse: " + label)
    endpoint = basis_apply(basis_apply(units(), B2), B0)
    basis_apply(endpoint, inverse(B0))
    basis_apply(endpoint, inverse(B2))
    require(endpoint == units(), "Ordered full endpoint basis restoration")
    return {"anchors": list(ANCHORS), "independent_public_columns": PUBLIC,
            "full_helper_channels": len(helpers),
            "zero_frame_preparation_gates": len(gates), "B0_gates": len(B0),
            "B2_gates": len(B2), "departure_blocks": len(witness["C"]),
            "response_rows": len(responses), "dual_zero_temporaries": len(ANCHORS),
            "first_departures": len(first)}, (CA, gates)


def literal_replay(word):
    """Exact scalar projection with arbitrary public data and owned resets."""
    rows = units() + [None for _ in range(OWNED)]
    frames = list(word["initial"]) + [None for _ in range(OWNED)]
    counts, active, peak, clear_nonzero, copies_nonzero = Counter(), 0, 0, 0, 0
    for index, event in enumerate(word["program"]):
        op, r = event[:2]
        counts[op] += 1
        if op == "INIT":
            require(rows[r] is None and frames[r] is None, "INIT inactive label")
            rows[r], frames[r] = {}, event[2]
            active += 1
            peak = max(peak, active)
            continue
        require(rows[r] is not None, "Active event role at " + str(index))
        if op == "MOVE":
            require(frames[r] == event[2], "Literal MOVE source frame")
            frames[r] = event[3]
        elif op == "CLEAR":
            require(frames[r] == event[2], "Literal CLEAR frame")
            clear_nonzero += bool(rows[r])
            rows[r], frames[r] = None, None
            active -= 1
        else:
            require(frames[r] == event[-1], "Literal scalar destination frame")
            if op == "SCALE":
                rows[r] = {c: rational(event[2]) * v for c, v in rows[r].items()}
            else:
                s = event[2]
                require(rows[s] is not None and frames[s] == event[-1],
                        "Literal scalar source frame")
                if op == "COPY":
                    copies_nonzero += bool(rows[r])
                    rows[r] = {c: rational(event[3]) * v for c, v in rows[s].items()}
                else:
                    add_row(rows[r], rows[s], rational(event[3]))
    require(active == 0 and all(r is None for r in rows[PUBLIC:]),
            "Every owned lifetime ends")
    require(frames[:PUBLIC] == word["final"], "All final public frame declarations")
    return rows[:PUBLIC], {"events": len(word["program"]), "opcodes": dict(sorted(counts.items())),
                          "owned_lifetimes": counts["INIT"], "peak_owned_labels": peak,
                          "scalar_nonzero_clear_rows": clear_nonzero,
                          "scalar_nonzero_copy_destinations": copies_nonzero}


def span(vectors):
    result = {0}
    for vector in vectors:
        result |= {x ^ vector for x in tuple(result)}
    return result


def interface_checks(source, output, witness):
    require(all(output[key] == value for key, value in source.items()
                if key not in ("program", "frames", "final")),
            "All original input and metadata fields are unchanged")
    require(len(source["frames"]) == 1094 and len(output["frames"]) == 1095,
            "Exactly one new frame")
    require(output["frames"][:1094] == source["frames"], "All original frame bytes unchanged")
    require(output["frames"][1094] == [7, 9, 35, 66, 400], "Declared new forward frame")
    expected = {703: 1094, 393: 246, 707: 246, 484: 246, 297: 246,
                485: 246, 226: 246, 361: 245, 451: 245}
    actual = {r: output["final"][r] for r in range(PUBLIC)
              if source["final"][r] != output["final"][r]}
    require(actual == expected, "Exactly nine declared output frame changes")
    require({str(r): f for r, f in expected.items()} == witness["entries"], "Basis entrance witness")
    ranks = {str(r): (len(source["frames"][source["final"][r]]),
                     len(output["frames"][output["final"][r]])) for r in ANCHORS}
    for r in ANCHORS:
        old = span(source["frames"][source["final"][r]])
        new = span(output["frames"][output["final"][r]])
        require(new < old, "Each changed forward output is a strict subspace")
        require(len(old) == 2 ** ranks[str(r)][0], "Independent source output-frame basis")
        require(len(new) == 2 ** ranks[str(r)][1], "Independent changed-frame basis")
    return {"changed_output_frames": {str(r): f for r, f in sorted(actual.items())},
            "output_rank_changes": ranks, "unchanged_original_frames": 1094}


def literal_dual_bridge(source, output, witness):
    """Bind the basis algebra to the emitted dual prefix, bridge and suffix."""
    A, CA, gates, first = preparation(source, witness)
    dual = dual_program(output)
    prefix_end = next(i for i, e in enumerate(dual) if e[0] == "MOVE")
    early_count = integer(witness["early_events"], 1, len(dual), "Early event count")
    B0, B2 = witness["B0"], witness["B2"]
    b0_tail_count = sum(4 if e[0] == "SWAP" else 1 for e in B0)
    tail_count = b0_tail_count + len(B2)
    require(encoded({a: {PUBLIC + i: Fraction(1)} for i, a in enumerate(ANCHORS)})
            == {a: {str(s): "1"} for a, s in witness["shadow_roles"].items()},
            "The nine frozen shadow roles")
    rows = units() + [None for _ in range(OWNED)]
    roles = list(range(PUBLIC))
    for r in source["live"]:
        roles[r], roles[r + 112] = r + 112, r
    flip = lambda f: FULL if f == ZERO else ZERO if f == FULL else f
    frames = [None] * (PUBLIC + OWNED)
    source_frames = [None] * PUBLIC
    for r in range(PUBLIC):
        frames[roles[r]] = flip(output["final"][r])
        source_frames[roles[r]] = flip(source["final"][r])
    cleared = []

    def fragment(events, require_zero_clear=False):
        for event in events:
            op, r = event[:2]
            if op == "INIT":
                require(rows[r] is None, "Dual INIT starts an inactive shadow")
                rows[r], frames[r] = {}, event[2]
            elif op == "CLEAR":
                require(rows[r] is not None and frames[r] == event[2], "Dual CLEAR active frame")
                if require_zero_clear:
                    require(not rows[r], "Actual emitted dual temporary is zero at CLEAR")
                cleared.append(r)
                rows[r], frames[r] = None, None
            elif op == "MOVE":
                require(rows[r] is not None and frames[r] == event[2], "Dual MOVE source label")
                frames[r] = event[3]
            else:
                require(op in ("ADD", "SCALE") and rows[r] is not None
                        and frames[r] == event[-1], "Dual scalar destination label")
                if op == "SCALE":
                    rows[r] = {c: rational(event[2]) * v for c, v in rows[r].items()}
                else:
                    s = event[2]
                    require(rows[s] is not None and frames[s] == event[-1], "Dual scalar source label")
                    add_row(rows[r], rows[s], rational(event[3]))

    fragment(dual[:prefix_end], require_zero_clear=True)
    require(sorted(cleared) == list(range(PUBLIC, PUBLIC + 9)), "Exactly nine emitted dual shadow CLEARs")
    require(all(row is None for row in rows[PUBLIC:]), "No dual shadow survives preparation")
    expected_prefix = units()
    for a in ANCHORS:
        expected_prefix[a] = {}
    for operations in (B2, B0, gates, *witness["C"].values()):
        basis_apply(expected_prefix, operations)
    for a in ANCHORS:
        expected_prefix[a] = {a: Fraction(1)}
    require(rows[:PUBLIC] == expected_prefix, "Actual emitted dual preparation equals the independent basis product")
    fragment(dual[prefix_end:prefix_end + early_count])
    input_basis = basis_apply(basis_apply(units(), B2), B0)
    require(rows[:PUBLIC] == compose_rows(A, input_basis),
            "Actual response insertion restores every arbitrary prepared public row")
    moved = witness["replaced_departures"]
    require(type(moved) is list and len(moved) == 24 and len(set(moved)) == 24,
            "24 distinct replaced first departures")
    for r in moved:
        integer(r, 0, PUBLIC, "Replaced public departure")
        require(r in first, "Replaced departure exists in actual source")
        source_frames[r] = first[r][1]
    require(frames[:PUBLIC] == source_frames, "Response bridge reaches the exact source departure frames")
    retained = [e for i, e in enumerate(dual_program(source))
                if not (e[0] in ("ADD", "COPY", "SCALE") and e[-1] == ZERO)
                and not (e[0] == "MOVE" and e[2] == ZERO and e[1] in moved
                         and i == first[e[1]][0])]
    require(dual[prefix_end + early_count:-tail_count] == retained,
            "All retained source events remain in literal order")
    tail = dual[-tail_count:]
    require(all(e[0] in ("ADD", "SCALE") and e[-1] == FULL for e in tail),
            "Both emitted inverse bases operate at FULL")
    first_inverse = basis_apply(units(), [e[:-1] for e in tail[:b0_tail_count]])
    second_inverse = basis_apply(units(), [e[:-1] for e in tail[b0_tail_count:]])
    require(first_inverse == basis_apply(units(), inverse(B0)), "Actual first endpoint inverse is B0^-1")
    require(second_inverse == basis_apply(units(), inverse(B2)), "Actual second endpoint inverse is B2^-1")
    return {"dual_preparation_events": prefix_end, "response_bridge_events": early_count,
            "actual_dual_zero_shadow_clears": sorted(cleared), "replaced_first_departures": len(moved),
            "retained_source_events": len(retained), "inverse_B0_events": b0_tail_count,
            "inverse_B2_events": len(B2)}


def rejection(label, action):
    try:
        action()
    except (ValueError, KeyError, IndexError, ZeroDivisionError):
        return {"control": label, "rejected": True}
    raise ValueError("Control did not reject: " + label)


def controls(source, output, witness):
    results = []
    altered = deepcopy(witness)
    altered["B0"][0][2] = altered["B0"][0][1]
    results.append(rejection("identity_replacement_for_B0_swap", lambda: basis_checks(source, altered)))
    altered = deepcopy(witness)
    altered["B2"][0][3] = str(-rational(altered["B2"][0][3]))
    results.append(rejection("wrong_B2_correction_sign", lambda: basis_checks(source, altered)))
    altered = deepcopy(witness)
    altered["responses"]["704"]["703"] = "1"
    results.append(rejection("wrong_missing_response_sign", lambda: basis_checks(source, altered)))
    altered = deepcopy(witness)
    altered["C"]["244"][0][2] = "1"
    results.append(rejection("wrong_departure_basis_sign", lambda: basis_checks(source, altered)))
    altered_word = deepcopy(output)
    altered_word["final"][703] = FULL
    results.append(rejection("omitted_output_contraction", lambda: interface_checks(source, altered_word, witness)))
    altered_word = deepcopy(output)
    altered_word["program"].pop(witness["control_indices"]["dirty_carrier_subtraction"])
    baseline, _ = literal_replay(source)

    def wrong_literal():
        rows, _ = literal_replay(altered_word)
        require(rows == baseline, "Dirty-carrier control endpoint mismatch")

    results.append(rejection("omitted_literal_dirty_carrier_subtraction", wrong_literal))
    return results


def run():
    data = load_inputs()
    source, output, witness = (data["INPUT-WORD.json.gz"], data["OUTPUT-WORD.json.gz"], data["BASIS.json"])
    validate_word(source)
    validate_word(output)
    basis_result, _ = basis_checks(source, witness)
    interface_result = interface_checks(source, output, witness)
    dual_result = literal_dual_bridge(source, output, witness)
    source_rows, source_result = literal_replay(source)
    output_rows, output_result = literal_replay(output)
    require(source_result["scalar_nonzero_copy_destinations"] == 0,
            "Every original COPY destination is zero in the scalar projection")
    require(source_rows == output_rows, "Complete 770-by-770 scalar public endpoint equality")
    matrix = json.dumps(encoded(dict(enumerate(output_rows))), sort_keys=True, separators=(",", ":")).encode()
    return {"schema": "p104-joint-output-basis-audit/1", "status": "PASS",
            "scope": "frozen rational scalar projection and nine joint-basis interfaces",
            "basis": basis_result, "interface": interface_result, "literal_dual_bridge": dual_result,
            "literal_source": source_result, "literal_output": output_result,
            "public_endpoint_coefficients": sum(map(len, output_rows)),
            "public_endpoint_sha256": sha256(matrix).hexdigest(),
            "controls": controls(source, output, witness),
            "not_certified": ["native absolute phases or all native columns", "erasure permission",
                              "complete invoice or caller", "kappa", "uniform compiler or rounded multiplication"]}


if __name__ == "__main__":
    require(sys.argv[1:] in ([], ["--emit"]), "Usage: verify.py [--emit]")
    result = run()
    rendered = json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False)
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        retained = json.loads((HERE / "RESULT.json").read_bytes())
        require(rendered == json.dumps(retained, sort_keys=True, separators=(",", ":"), allow_nan=False),
                "Retained RESULT.json receipt matches the computed typed JSON result")
        print("PASS independent rational basis audit and retained RESULT.json")
