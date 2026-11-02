#!/usr/bin/env python3
"""Independent bounded checkpoint oracle for normalized G20 pairing excess.

This is not a second census, physical route implementation, typed continuation,
or target/profit certificate. Source code is authenticated as data, never run.
"""
import argparse
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PINS = {
    "WORD.json.gz": ("8dd441fdb9c8923df06eb5ebfda37d03e4539f2305763e688d8c7025d196c4b1", "3877a72d8a15adb03f6492f7d2fd8fa902ecb639"),
    "PATHS.json": ("f4dd58b78121040b1f054c0f7a626b25f6ef8d39f3de044d3456ea7dea8a6a5e", "efbdf632746a971f9a593f57ccbb7d2cc67a6760"),
    "FRAMES.json": ("0d99fc6b8f45c03dfba5252a03dd9e7fe23be3a7593dfe15368e34da6629a654", "9edf8d95b45a9c9c766a956bfcd3c19cf07bc13c"),
    "gap-source.py": ("91e201fd3c96267c878863abba794a16025070c98145ae598ee0ed7383c7f9c6", "93bf7baf7c01de63a57a8ad1e4653ca48047eaae"),
    "gap-PROOF.md": ("121649b47271f45e18a1053ca5615c94e1cc81cc42136d8ccf3b2dca7d93f706", "26f776a79accbb8a6378e5ad5ebefc3693a26501"),
    "prior-source.py": ("a9aea8b108ebbeae8041770cefecfdabdfaf91b72ba7b5cfa2ff13408f1d16dd", "13326f590033f6633bc91f919c802b6ddaf576bc"),
    "prior-PROOF.md": ("af88b44f1c61fb91d63ace7a2ece8d798bf6378864b2c4e1d44e01070fd485db", "c6d2f2c7626a7c42da025ef360ce1673f6a116dc"),
    "NOTICE.md": ("a4fdb5e2dfeeb216f3f58417891fc0a084c218d9a75228fb977e3cb82973be72", "accbc28384515af7b94b33e5f4eb57a150e0d9a1"),
    "source-README.md": ("e443b2fd7b988316953bfc7d21045690ea0d3ce9069ce1a06880f6ccfc7ec054", "b1655b59134ae7a5734628ba1efef6611b2dcd31"),
}
# Parent will freeze only source checkpoint identifiers here, not peer kernels.
CHECKPOINTS = [
    {"cut_t": 7670, "field": 323, "edge": [339, 507, 2],
     "bank": [0, 3, 11, 62, 63, 68, 69, 72, 464, 659, 663, 674, 676]},
    {"cut_t": 0, "field": 222, "edge": [1, 635, 1], "bank": [221]},
]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def unique_pairs(rows):
    result = {}
    for key, value in rows:
        require(key not in result, "Duplicate JSON member")
        result[key] = value
    return result


def decode(raw):
    def bad(value):
        raise ValueError("Nonfinite JSON constant " + value)
    return json.loads(raw, object_pairs_hook=unique_pairs, parse_constant=bad)


def source_inputs():
    data = {}
    for name, (sha, blob) in PINS.items():
        raw = (ROOT / "sources" / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == sha, "Source sha256 mismatch: " + name)
        digest = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(digest == blob, "Source Git blob mismatch: " + name)
        if name in ("WORD.json.gz", "PATHS.json", "FRAMES.json"):
            data[name] = decode(gzip.decompress(raw) if name.endswith(".gz") else raw)
    return data


def integer(value, minimum=0):
    require(type(value) is int and value >= minimum, "Strict integer required")
    return value


def rational(value):
    require(type(value) in (str, int, Fraction), "Exact rational coordinate required")
    return Fraction(value)


def rational_space(rows):
    """Unique reduced rational row space, with greatest-coordinate pivots."""
    require(type(rows) is list, "Frame basis list")
    basis = {}
    for source in rows:
        require(type(source) is list and len(source) == 8, "Frame coordinate width")
        row = list(map(rational, source))
        for pivot in sorted(basis, reverse=True):
            scale = row[pivot]
            if scale:
                row = [a-scale*b for a, b in zip(row, basis[pivot])]
        pivot = next((i for i in reversed(range(8)) if row[i]), None)
        if pivot is None:
            continue
        scale = row[pivot]
        row = [a/scale for a in row]
        for previous in basis:
            scale = basis[previous][pivot]
            if scale:
                basis[previous] = [a-scale*b for a, b in zip(basis[previous], row)]
        basis[pivot] = row
    return tuple(tuple(basis[p]) for p in sorted(basis, reverse=True))


def contains(outer, inner):
    return rational_space([list(row) for row in outer+inner]) == outer


def frame_geometry(payload):
    require(type(payload) is dict and set(payload) == {"frames"}, "Frame table schema")
    frames = payload["frames"]
    require(type(frames) is dict, "Frame table object")
    spaces = {}
    for key, entry in frames.items():
        require(type(key) is str and key.isascii() and key.isdigit() and str(int(key)) == key,
                "Canonical frame identifier")
        require(type(entry) is dict and set(entry) in ({"A", "B", "dim"}, {"A", "B", "dim", "origin"}), "Frame entry schema")
        if "origin" in entry:
            require(type(entry["origin"]) is str, "Frame origin metadata")
        shape = rational_space(entry["B"])
        require(integer(entry["dim"]) == len(shape), "Frame dimension")
        spaces[int(key)] = shape
    return spaces


def word_contract(word, spaces):
    require(type(word) is dict and set(word) == {"records", "start", "final", "owned"}, "Word schema")
    start, final, owned, records = (word[k] for k in ("start", "final", "owned", "records"))
    require(all(type(v) is list for v in (start, final, owned, records)), "Word lists")
    require(len(start) == len(final) == 685 and len(records) == 14794, "Frozen word dimensions")
    for value in start+final:
        require(value is None or (type(value) is int and value in spaces), "Declared frame identifier")
    for role in owned:
        require(integer(role) < len(start), "Owned role range")
    require(owned == sorted(set(owned)) and len(owned) == 48, "Owned inventory")
    for event in records:
        require(type(event) is list and event and type(event[0]) is str, "Event list/opcode")
        op = event[0]
        require(op in ("ADD", "ERASE", "INIT", "Q", "ZERO_Q"), "Event opcode")
        require(len(event) == {"ADD": 4, "ERASE": 3, "INIT": 3, "Q": 5, "ZERO_Q": 5}[op], "Event arity")
        require(integer(event[1]) < len(start), "Destination role")
        if op == "ADD":
            require(integer(event[2]) < len(start) and event[1] != event[2], "Distinct ADD source")
            require(type(event[3]) is int and event[3] in spaces, "ADD frame")
        elif op in ("ERASE", "INIT"):
            require(event[1] in owned, "Only owned ERASE/INIT")
            require(event[2] is None or (type(event[2]) is int and event[2] in spaces), "Owned header")
        else:
            require(all(type(x) is int and x in spaces for x in event[2:4]), "Query frame identifiers")
            integer(event[4], 1)
    return start, final, set(owned), records


def route_edges(payload, spaces):
    require(type(payload) is dict, "Route catalogue object")
    edges = set()
    for key, path in payload.items():
        require(type(key) is str and type(path) is list and path, "Nonempty route path")
        parts = key.split(":")
        require(len(parts) == 2 and all(p.isascii() and p.isdigit() for p in parts), "Route key")
        current = int(parts[0])
        for edge in path:
            require(type(edge) is list and len(edge) == 3, "Route edge schema")
            source, target, rank = edge
            require(all(type(v) is int for v in edge) and source in spaces and target in spaces,
                    "Route edge integer identifiers")
            require(current == source, "Route continuity")
            require(len(spaces[source])-len(spaces[target]) == rank > 0,
                    "Published strict dimension drop")
            require(contains(spaces[source], spaces[target]), "Published rational nesting")
            current = target
            edges.add(tuple(edge))
        require(current == int(parts[1]), "Route endpoint")
    return edges


def traces(word, spaces, cuts):
    start, final, owned, records = word_contract(word, spaces)
    require(all(type(t) is int and 0 <= t <= len(records) for t in cuts), "Cut number of applied records")
    wanted = set(cuts)
    n = len(start)
    rows = [1 << i for i in range(n)]
    state = start[:]
    before, after, headers = {}, {}, {}
    if 0 in wanted:
        before[0], headers[0] = rows[:], state[:]
    for t, event in enumerate(records, 1):
        op, d = event[:2]
        if op == "ADD":
            s, frame = event[2:]
            require(state[d] == state[s] == frame, "Literal ADD exact common frame")
            rows[d] ^= rows[s]
        elif op == "ERASE":
            rows[d] = 0
            state[d] = event[2]
        elif op == "INIT":
            require(rows[d] == 0, "Owned INIT whole normalized zero")
            state[d] = event[2]
        else:
            a, b, rank = event[2:]
            require(state[d] == a, "Literal query source header")
            require(len(spaces[a])-len(spaces[b]) == rank and contains(spaces[a], spaces[b]),
                    "Literal query geometry")
            if op == "ZERO_Q":
                require(rows[d] == 0, "ZERO_Q whole normalized zero")
            state[d] = b
        if t in wanted:
            before[t], headers[t] = rows[:], state[:]
    require(state == final, "Literal final frame contract")
    require(all(rows[i] == 0 for i in owned), "Final owned normalized zero rows")
    # B's columns are rebuilt directly from the final identity, independently
    # of the forward sweep or the predecessor's erased-column restoration.
    columns = [1 << i for i in range(n)]
    if len(records) in wanted:
        after[len(records)] = columns[:]
    for index in reversed(range(len(records))):
        event = records[index]
        op, d = event[:2]
        if op == "ADD":
            columns[event[2]] ^= columns[d]
        elif op == "ERASE":
            columns[d] = 0
        if index in wanted:
            after[index] = columns[:]
    require(set(before) == set(after) == set(headers) == wanted, "Direct checkpoint coverage")
    return before, after, headers


def xor_combine(rows, coefficients):
    require(type(coefficients) is int and coefficients >= 0 and coefficients.bit_length() <= len(rows), "Binary coefficient width")
    result = 0
    while coefficients:
        bit = coefficients & -coefficients
        result ^= rows[bit.bit_length()-1]
        coefficients ^= bit
    return result


def rank(rows):
    pivots = {}
    for source in rows:
        value = source
        while value:
            pivot = value.bit_length()-1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return len(pivots)


def kernels(rows):
    # Lowest pivots, opposite to the predecessor's highest-pivot dependencies.
    pivots, nullspace = {}, []
    for index, source in enumerate(rows):
        value, coefficients = source, 1 << index
        while value:
            pivot = (value & -value).bit_length()-1
            if pivot not in pivots:
                pivots[pivot] = (value, coefficients)
                break
            old, combination = pivots[pivot]
            value ^= old
            coefficients ^= combination
        if value == 0:
            nullspace.append(coefficients)
    require(len(nullspace) + rank(rows) == len(rows), "Complete eligible kernel dimension")
    require(rank(nullspace) == len(nullspace), "Eligible kernel independence")
    require(all(xor_combine(rows, c) == 0 for c in nullspace), "Eligible kernel defining equations")
    return nullspace


def independent_basis(rows):
    pivots = {}
    for value in rows:
        while value:
            pivot = (value & -value).bit_length()-1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return list(pivots.values())


def support(value):
    result = []
    while value:
        bit = value & -value
        result.append(bit.bit_length()-1)
        value ^= bit
    return result


def dot(a, b):
    return (a & b).bit_count() & 1


def matrices(left, right, prefix, suffix):
    inputs = [xor_combine(prefix, a) for a in left]
    outputs = [xor_combine(suffix, b) for b in right]
    boundary = [sum(dot(c, d) << j for j, d in enumerate(outputs)) for c in inputs]
    internal = [sum(dot(a, b) << j for j, b in enumerate(right)) for a in left]
    return inputs, outputs, boundary, internal


def validate_unit_pair(a, b, prefix, suffix, outside):
    c, d = xor_combine(prefix, a), xor_combine(suffix, b)
    require((c & outside) == (d & outside) == 0, "Full boundary support eligibility")
    require(dot(a, b) == dot(c, d) == 1, "Simultaneous internal and boundary unit equations")
    return c, d


def simultaneous_pair(left, right, prefix, suffix, slots, outside):
    inputs, outputs, boundary, internal = matrices(left, right, prefix, suffix)
    if not rank(boundary) or not rank(internal):
        return None
    ci = next(i for i, row in enumerate(boundary) if row)
    di = next(i for i, row in enumerate(internal) if row)
    if internal[ci]:
        lc = 1 << ci
    elif boundary[di]:
        lc = 1 << di
    else:
        lc = (1 << ci) ^ (1 << di)
    cfunctional = xor_combine(boundary, lc)
    dfunctional = xor_combine(internal, lc)
    require(cfunctional and dfunctional, "Simultaneous functional construction")
    overlap = cfunctional & dfunctional
    if overlap:
        rc = overlap & -overlap
    else:
        rc = (cfunctional & -cfunctional) ^ (dfunctional & -dfunctional)
    a, b = xor_combine(left, lc), xor_combine(right, rc)
    c, d = validate_unit_pair(a, b, prefix, suffix, outside)
    return {"a_roles": [slots[i] for i in support(a)], "b_roles": [slots[i] for i in support(b)],
            "c_input_support": support(c), "d_output_support": support(d),
            "internal_pairing": 1, "boundary_pairing": 1}


def bank_view(prefix, suffix, slots, outside):
    p, s = [prefix[i] for i in slots], [suffix[i] for i in slots]
    left, right = kernels([v & outside for v in p]), kernels([v & outside for v in s])
    inputs, outputs, boundary, internal = matrices(left, right, p, s)
    require(all(v & outside == 0 for v in inputs+outputs), "Kernel images full support")
    result = {"slots": slots, "left_kernel_dimension": len(left), "right_kernel_dimension": len(right),
              "boundary_rank": rank(boundary), "internal_rank": rank(internal),
              "left_kernel_role_supports": [[slots[i] for i in support(a)] for a in left],
              "right_kernel_role_supports": [[slots[i] for i in support(b)] for b in right],
              "eligible_input_supports": [support(v) for v in inputs],
              "eligible_output_supports": [support(v) for v in outputs],
              "boundary_matrix_rows": [support(v) for v in boundary],
              "internal_matrix_rows": [support(v) for v in internal],
              "simultaneous_unit_pair": simultaneous_pair(left, right, p, s, slots, outside)}
    return result, left, right, p, s


def inherited_quotient(left, right, p, s, slots, member, outside):
    position = slots.index(member)
    pivot = 1 << position
    if (p[position] & outside) or (s[position] & outside) or not dot(p[position], s[position]):
        return {"available": False, "reason": "The literal singleton is not an eligible boundary-unit pivot."}
    lzero = independent_basis([a ^ (pivot if a & pivot else 0) for a in left])
    rzero = independent_basis([b ^ (pivot if b & pivot else 0) for b in right])
    require(len(lzero)+1 == len(left) and len(rzero)+1 == len(right), "Inherited pivot eligible kernel decomposition")
    # Clear the boundary pivot using actual row/column basis changes. Internal
    # pairings are recomputed on these changed bases rather than assumed equal.
    newleft = [a ^ (pivot if dot(xor_combine(p, a), s[position]) else 0) for a in lzero]
    newright = [b ^ (pivot if dot(p[position], xor_combine(s, b)) else 0) for b in rzero]
    _, _, oldboundary, _ = matrices(left, right, p, s)
    inputs, outputs, boundary, internal = matrices(newleft, newright, p, s)
    require(all(dot(c, s[position]) == 0 for c in inputs) and all(dot(p[position], d) == 0 for d in outputs),
            "Inherited boundary pivot orthogonalization")
    require(rank(boundary)+1 == rank(oldboundary), "Exact inherited boundary rank debit")
    require(rank(newleft) == len(newleft) and rank(newright) == len(newright), "Inherited quotient basis independence")
    return {"available": True, "pivot_role": member, "boundary_rank": rank(boundary),
            "internal_rank_on_actual_changed_bases": rank(internal),
            "boundary_matrix_rows": [support(v) for v in boundary],
            "internal_matrix_rows": [support(v) for v in internal],
            "simultaneous_unit_pair": simultaneous_pair(newleft, newright, p, s, slots, outside)}


def checkpoint(spec, word, spaces, edges, prefix, suffix, state):
    member, edge = spec["field"], tuple(spec["edge"])
    require(type(member) is int and 222 <= member < len(state) and member not in word["owned"], "Public helper member")
    require(len(edge) == 3 and all(type(v) is int for v in edge) and edge in edges, "Published edge membership")
    source, target, paid_rank = edge
    require(state[member] == source, "Literal member source frame")
    entrance, exit_space = spaces[word["start"][member]], spaces[word["final"][member]]
    require(len(exit_space) < len(spaces[target]) < len(entrance), "Strict intermediate target dimension")
    require(contains(entrance, spaces[target]) and contains(spaces[target], exit_space), "Rational target compatibility")
    members = [i for i in range(222, len(state)) if i not in word["owned"]
               and spaces[word["start"][i]] == entrance and spaces[word["final"][i]] == exit_space]
    slots = [i for i, frame in enumerate(state) if frame is not None and spaces[frame] == spaces[target]]
    require(member in members and member not in slots and slots, "Member move into occupied different bank")
    if "group_members" in spec:
        require(members == spec["group_members"], "Frozen full group identification")
    if "bank" in spec:
        require(slots == spec["bank"], "Frozen entire occupied bank identification")
    outside = ((1 << len(state))-1) ^ sum(1 << h for h in members)
    base, _, _, _, _ = bank_view(prefix, suffix, slots, outside)
    singleton, _, _, _, _ = bank_view(prefix, suffix, [member], outside)
    augmented_slots = sorted(slots+[member])
    augmented, left, right, p, s = bank_view(prefix, suffix, augmented_slots, outside)
    boundary_excess = augmented["boundary_rank"]-max(base["boundary_rank"], singleton["boundary_rank"])
    internal_excess = augmented["internal_rank"]-max(base["internal_rank"], singleton["internal_rank"])
    return {"cut_t": spec["cut_t"], "field": member, "edge": list(edge), "group_members": members,
            "group_dimensions": [len(entrance), len(exit_space)], "target_dimension": len(spaces[target]),
            "paid_edge_rank": paid_rank, "base": base, "singleton": singleton, "augmented": augmented,
            "boundary_excess_over_both": boundary_excess, "internal_excess_over_both": internal_excess,
            "inherited_pivot_quotient": inherited_quotient(left, right, p, s, augmented_slots, member, outside),
            "qualification": "Necessary normalized pairing evidence only; no extra independent target, typed continuation or profit follows."}


def synthetic_controls():
    # Two projections each have rank1, while their joint bank has rank2.
    # These are explicit synthetic algebra controls, not a G20 source witness.
    prefix, suffix = [1, 2], [1, 2]
    base = bank_view(prefix, suffix, [0], 0)[0]
    single = bank_view(prefix, suffix, [1], 0)[0]
    both = bank_view(prefix, suffix, [0, 1], 0)[0]
    require(base["boundary_rank"] == single["boundary_rank"] == 1 and both["boundary_rank"] == 2,
            "Synthetic genuine augmentation excess")
    require(both["simultaneous_unit_pair"] is not None, "Synthetic simultaneous unit pair")
    # Boundary and internal tests must both be applied: this has internal1,
    # but disjoint images and hence boundary0.
    no_boundary = bank_view([1], [2], [0], 0)[0]
    require(no_boundary["boundary_rank"] == 0 and no_boundary["internal_rank"] == 1
            and no_boundary["simultaneous_unit_pair"] is None, "Synthetic internal-only rejection")
    foreign = bank_view([1], [1], [0], 1)[0]
    require(foreign["left_kernel_dimension"] == foreign["right_kernel_dimension"] == 0,
            "Foreign-coordinate eligibility rejection")
    return {"augmentation_ranks": [1, 1, 2], "internal_only_rejected": True,
            "foreign_coordinate_rejected": True, "synthetic_not_source_evidence": True}


def compute():
    data = source_inputs()
    spaces = frame_geometry(data["FRAMES.json"])
    edges = route_edges(data["PATHS.json"], spaces)
    word = data["WORD.json.gz"]
    require(CHECKPOINTS, "No frozen bounded checkpoints configured")
    cuts = [spec["cut_t"] for spec in CHECKPOINTS]
    prefix, suffix, states = traces(word, spaces, cuts)
    views = [checkpoint(spec, word, spaces, edges, prefix[spec["cut_t"]], suffix[spec["cut_t"]], states[spec["cut_t"]])
             for spec in CHECKPOINTS]
    candidate, control = views
    require(candidate["boundary_excess_over_both"] > 0 and candidate["augmented"]["simultaneous_unit_pair"] is not None,
            "Source-bound necessary excess and simultaneous unit witness")
    require([control[k]["boundary_rank"] for k in ("base", "singleton", "augmented")] == [0, 1, 1]
            and control["boundary_excess_over_both"] == 0
            and control["inherited_pivot_quotient"]["boundary_rank"] == 0,
            "Opening inherited-only positive is not excess")
    # Removing the transported member from the actual right witness must fail
    # the same complete-support guard used to certify the unmodified pair.
    slots = candidate["augmented"]["slots"]
    pair = candidate["augmented"]["simultaneous_unit_pair"]
    a = sum(1 << slots.index(i) for i in pair["a_roles"])
    b = sum(1 << slots.index(i) for i in pair["b_roles"])
    require(candidate["field"] in pair["b_roles"], "Actual witness uses transported member")
    outside = ((1 << len(word["start"]))-1) ^ sum(1 << h for h in candidate["group_members"])
    bad_b = b ^ (1 << slots.index(candidate["field"]))
    p = [prefix[candidate["cut_t"]][i] for i in slots]
    s = [suffix[candidate["cut_t"]][i] for i in slots]
    foreign_outputs = support(xor_combine(s, bad_b) & outside)
    require(foreign_outputs, "Omitted member has concrete foreign output support")
    rejection = None
    try:
        validate_unit_pair(a, bad_b, p, s, outside)
    except ValueError as exc:
        rejection = str(exc)
    require(rejection == "Full boundary support eligibility", "Omitted-member witness control must reject")
    return {"schema_version": 1, "status": "PASS_BOUNDED_NECESSARY_PAIRING_CHECKPOINTS",
            "source_sha256": {name: pins[0] for name, pins in PINS.items()},
            "source_git_blobs": {name: pins[1] for name, pins in PINS.items()},
            "cut_convention": "cut_t is the number of literal source records already applied; prefix[:t],suffix[t:]",
            "normalized_convention": "All685 entrance coordinates, including dirty owned coordinates, start as independent formal variables; ERASE is an owned projection, INIT requires a zero row, and queries are normalized identity maps.",
            "checkpoints": views, "controls": synthetic_controls(),
            "actual_witness_control": {"mutation": "Remove transported member323 from b's role support",
                                       "observed_error": rejection, "foreign_output_support": foreign_outputs},
            "limits": ["This is a bounded direct-cut oracle, not an independent complete-census exclusion.",
                       "Published edges and frame compatibility are exact rational geometry inQ^8; normalized scalar pairing is overF2.",
                       "A positive excess or simultaneous unit pair is only a necessary algebraic gate; no extra productive target or profitable split is certified.",
                       "No retargeted chronological continuation, native phase/all columns, physical erasure, complete paid/target invoice, ordinary admission or selected frontier change is supplied."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(canonical(result))
    else:
        path = ROOT / "ORACLE.json"
        require(path.is_file(), "Retained receipt ORACLE.json required")
        require(canonical(decode(path.read_bytes())) == canonical(result), "Retained receipt mismatch")
        print("PASS independent bounded G20 pairing receipt")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        sys.exit(1)
