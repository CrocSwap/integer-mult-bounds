#!/usr/bin/env python3
"""Independent six-direction preparation oracle; no full NEW endpoint replay.

Only exact direction columns through OLD zero-frame preparation are propagated.
Author and peer code are authenticated as data, never imported or executed.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
Z, FULL = 3, 127
PINS = {
    "NEW-WORD.json.gz": ("9e31463a785c18a70f6ae6ef3d04a6560dbb965517109390fe820f9fac3371b3", "b1cfd03abe9128cf5a3908fbd82652e5e8a2e292"),
    "OLD-WORD.json.gz": ("e3b6f1c25d672b8c85433be97ebad77ae6a6972352ce2ff63507d30835fcb491", "0af79e58172f85c302c35b193205c0b185b09393"),
    "LIFTS.json": ("38960b70a074888a2aeaf3b543629a7ae747c0c5d4f5c853371a6e7c483766c5", "2ee8cb78fd149f9aca8dd953c650b92495a56266"),
    "constructor-source.py": ("fe7dc1d9aa55da393465388ee90faaa687b1e5be48dfa816a421069fa3d2de08", "c099995bef0e224cbb0ec61c06ed3d0b4d478b33"),
    "upstream-PROOF.md": ("769e0f87e6b85c557b48135d2d898bb485cf77ce9925540e0a3740e6283f41af", "bd20fcaf2078691d914d6afbc5cb06a75f47770d"),
    "NOTICE": ("91f24d68004688bc0a56303a48edcb5ddabd66bfc2326950603bf98dec245bbe", "638a187d1417bda8976e945a2aeaed116a090e37"),
    "author-VALIDATION.md": ("cf33fe7acd32b1912bde7bf67abe1386eb042c6d269a9540cd28cdd076a7cac3", "0be8e7f1052628c34e24dfae6777cb3749b224a9"),
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def decode(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, "Duplicate JSON member")
            out[key] = value
        return out
    def bad(value):
        raise ValueError("Nonfinite JSON value " + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad)


def inputs():
    result = {}
    for name, (sha, blob) in PINS.items():
        raw = (ROOT / "sources" / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == sha, "Source sha256 mismatch: " + name)
        require(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == blob,
                "Source Git blob mismatch: " + name)
        if name.endswith(".json") or name.endswith(".json.gz"):
            result[name] = decode(gzip.decompress(raw) if name.endswith(".gz") else raw)
    return result


def integer(value, lower=0):
    require(type(value) is int and value >= lower, "Strict integer required")
    return value


def fraction(value):
    require(type(value) in (int, str), "Exact rational string/integer required")
    return F(value)


def sparse_json(vector):
    return [[r, str(c)] for r, c in sorted(vector.items()) if c]


def directions(spec):
    require(type(spec) is dict and set(spec) == {"schema_version", "rounds"}
            and type(spec["schema_version"]) is int and spec["schema_version"] == 1,
            "Lift specification schema")
    answer, clusters = {}, []
    for round_index, rd in enumerate(spec["rounds"], 1):
        require(type(rd) is dict and set(rd) == {"clusters"}, "Round schema")
        for cluster in rd["clusters"]:
            require(type(cluster) is dict and set(cluster) == {"F", "anchors", "carriers"}, "Cluster schema")
            entrance = integer(cluster["F"])
            carriers = cluster["carriers"]
            require(type(carriers) is list and carriers and all(type(c) is int and c >= 0 for c in carriers)
                    and len(carriers) == len(set(carriers)), "Carrier roles")
            anchors = []
            for text, payload in cluster["anchors"].items():
                require(type(text) is str and text.isascii() and text.isdigit(), "Anchor identifier")
                q = int(text)
                require(q not in answer and type(payload) is dict and set(payload) == {"h"}, "Distinct anchor schema")
                h = {}
                for role, value in payload["h"].items():
                    require(type(role) is str and role.isascii() and role.isdigit() and str(int(role)) == role,
                            "Direction role identifier")
                    c = fraction(value)
                    require(c != 0, "Sparse direction has no explicit zero")
                    h[int(role)] = c
                answer[q] = h
                anchors.append(q)
            clusters.append({"round": round_index, "F": entrance, "anchors": anchors, "carriers": carriers})
    require(sorted(answer) == [472, 520, 544, 624, 655, 671], "Exactly six frozen anchors")
    return answer, clusters


def word_schema(word):
    require(type(word) is dict and set(word) == {"schema", "public", "frames", "initial", "final", "owned_fields", "ports", "live", "program"}, "Word object schema")
    public, owned = integer(word["public"], 1), integer(word["owned_fields"])
    require(public == 770 and owned == 29 and len(word["initial"]) == len(word["final"]) == public,
            "Frozen public/owned dimensions")
    frames = word["frames"]
    require(type(frames) is list and all(type(frame) is list and all(type(v) is int and 0 <= v < 512 for v in frame) for frame in frames), "Binary frame data typing")
    def frame(value):
        require(type(value) is int and 0 <= value < len(frames), "Frame identifier")
    for values in (word["initial"], word["final"]):
        require(type(values) is list, "Header list")
        for value in values:
            if value is not None:
                frame(value)
    require(all(type(r) is int and 0 <= r < public for r in word["live"])
            and len(word["live"]) == len(set(word["live"])) == len(word["ports"]) == 104,
            "Actual live-port inventory")
    for event in word["program"]:
        require(type(event) is list and event and type(event[0]) is str, "Instruction list")
        op = event[0]
        require(op in ("ADD", "SCALE", "COPY", "MOVE", "INIT", "CLEAR"), "Instruction opcode")
        require(len(event) == {"ADD": 5, "SCALE": 4, "COPY": 5, "MOVE": 5, "INIT": 3, "CLEAR": 3}[op], "Instruction arity")
        require(integer(event[1]) < public+owned, "Destination role")
        if op in ("ADD", "COPY"):
            require(integer(event[2]) < public+owned and event[1] != event[2], "Distinct scalar source")
            fraction(event[3]); frame(event[4])
        elif op == "SCALE":
            require(fraction(event[2]) != 0, "Invertible scalar SCALE")
            frame(event[3])
        elif op == "MOVE":
            frame(event[2]); frame(event[3])
            require(type(event[4]) is bool and event[4] == (event[1] >= public), "Strict MOVE ownership flag")
        else:
            require(event[1] >= public, "Owned INIT/CLEAR role")
            frame(event[2])
    return public, public+owned


def trace_preparation(word, h=None):
    """Selected direction columns only while a role is at the zero frame.

    Values outside Z are deliberately not propagated. No full NEW endpoint or
    arbitrary dirty-owned coefficient conclusion can be drawn from this trace.
    """
    public, count = word_schema(word)
    anchors = sorted(h) if h is not None else []
    state = list(word["initial"]) + [None]*(count-public)
    values = {r: [h[q].get(r, F(0)) for q in anchors] for r in range(public) if state[r] == Z} if h is not None else {}
    if h is not None:
        require(all(0 <= r < public and word["initial"][r] == Z for d in h.values() for r in d), "Every selected direction starts in public Z preparation")
    departures, terminal, births = {}, [], {}
    initial_Z = [r for r in range(public) if state[r] == Z]
    for index, event in enumerate(word["program"]):
        op, d = event[:2]
        if op == "INIT":
            require(state[d] is None, "Inactive owned INIT lifetime")
            state[d] = event[2]
            if state[d] == Z and h is not None:
                values[d] = [F(0) for _ in anchors]
                births[d] = index
        elif op == "CLEAR":
            require(state[d] == event[2], "CLEAR exact local frame")
            if state[d] == Z and h is not None:
                column_values = values.pop(d)
                terminal.append({"role": d, "INIT_index": births.pop(d), "CLEAR_index": index,
                                 "six_direction_values": [str(c) for c in column_values]})
            state[d] = None
        elif op == "MOVE":
            require(state[d] == event[2], "MOVE source exact local frame")
            require(event[3] != Z, "Frozen preparation has no reentry into Z")
            if event[2] == Z and h is not None:
                require(d not in departures, "Unique first Z departure")
                departures[d] = {"event_index": index, "destination": event[3], "values": values.pop(d)}
            state[d] = event[3]
        else:
            frame = event[-1]
            require(state[d] == frame, "Scalar destination exact local frame")
            if op in ("ADD", "COPY"):
                s, c = event[2], fraction(event[3])
                require(state[s] == frame, "Scalar source exact local frame")
                if frame == Z and h is not None:
                    old = values[d]
                    source = values[s]
                    values[d] = [a+c*b for a, b in zip(old, source)] if op == "ADD" else [c*b for b in source]
            elif frame == Z and h is not None:
                c = fraction(event[2])
                values[d] = [c*a for a in values[d]]
    require(state == word["final"] + [None]*(count-public), "Literal final header/type closure")
    if h is not None:
        require(sorted(departures) == initial_Z and not values, "Every actual Z-born public departure and owned terminal accounted")
        require(all(not F(c) for row in terminal for c in row["six_direction_values"]), "Selected direction values zero at owned Z terminal")
    return anchors, departures, terminal


def response_contract(anchors, departures, clusters):
    index = {q: i for i, q in enumerate(anchors)}
    reports, forbidden = {}, []
    for cl in clusters:
        for q in cl["anchors"]:
            j, destination = index[q], departures[q]["destination"]
            rows = []
            for r, row in sorted(departures.items()):
                value = row["values"][j]
                if not value:
                    continue
                kind = "anchor" if r == q else "carrier" if r in cl["carriers"] else "recipient"
                if (r == q and value != 1) or (r != q and kind != "carrier" and row["destination"] != destination):
                    forbidden.append({"anchor": q, "row": r, "coefficient": str(value),
                                      "actual_first_destination": row["destination"], "allowed_recipient_destination": destination})
                rows.append({"row": r, "coefficient": str(value), "kind": kind, "first_destination": row["destination"],
                             "departure_event_index": row["event_index"]})
            reports[str(q)] = {"entrance": cl["F"], "anchor_first_destination": destination, "responses": rows}
    require(not forbidden, "Preparation response support/unit violation: " + canonical(forbidden[0]) if forbidden else "")
    unit = [[str(departures[r]["values"][index[q]]) for q in anchors] for r in anchors]
    require(unit == [[str(int(r == q)) for q in anchors] for r in anchors], "Full six-by-six prepared anchor unit matrix")
    return reports, unit


def add_vectors(a, b, factor=F(1)):
    out = dict(a)
    for r, value in b.items():
        total = out.get(r, F(0))+factor*value
        if total:
            out[r] = total
        else:
            out.pop(r, None)
    return out


def basis_checks(word, h):
    anchors = sorted(h)
    require(all(h[q].get(r, F(0)) == int(q == r) for q in anchors for r in anchors), "Input direction cross-anchor unit coordinates")
    u = {q: add_vectors(h[q], {q: F(1)}, F(-1)) for q in anchors}
    def N(v):
        out = {}
        for q in anchors:
            if v.get(q, 0):
                out = add_vectors(out, u[q], v[q])
        return out
    def E(v):
        return {r+112: v[r] for r in word["live"] if v.get(r, 0)}
    def U(v, sign=1):
        return add_vectors(v, N(v), F(sign))
    def M(v):
        return add_vectors(v, E(v))
    for j in range(word["public"]):
        e = {j: F(1)}
        require(not N(N(e)), "N squared is zero on every public column")
        require(U(U(e), -1) == U(U(e, -1)) == e, "Two-sided U inverse on every public column")
        require(U(M(e)) == M(U(e)), "U commutes with declared old M on every public column")
    return u, {"public_columns": word["public"], "N_squared_zero": True,
               "two_sided_inverse": "U=I+N, U_inverse=I-N", "commutes_with_declared_M": True,
               "declared_M": "row[r+112] += input[r] for every literal live r; all other public rows identity",
               "U_minus_I_columns": {str(q): sparse_json(u[q]) for q in anchors}}


def literal_bindings(old, new, h, clusters, reports, u):
    oldP, newP = old["program"], new["program"]
    oldcount = Counter(canonical(e) for e in oldP)
    newcount = Counter(canonical(e) for e in newP)
    carrier_deliveries, recipient_deliveries, postponed = [], [], []
    tail = []
    for cl in clusters:
        for q in cl["anchors"]:
            report = reports[str(q)]
            G = report["anchor_first_destination"]
            require(old["initial"][q] == Z and old["final"][q] == FULL and new["initial"][q] == cl["F"], "Literal lifted anchor headers")
            require(sum(e == ["MOVE", q, cl["F"], G, False] for e in newP) == 1, "Actual anchor first-destination move")
            for row in report["responses"]:
                r, coefficient = row["row"], F(row["coefficient"])
                if r == q:
                    continue
                frame = cl["F"] if row["kind"] == "carrier" else G
                event = ["ADD", r, q, str(coefficient), frame]
                require(newcount[canonical(event)]-oldcount[canonical(event)] == 1, "Literal response delivery delta")
                locations = [i for i, e in enumerate(newP) if e == event]
                record = {"anchor": q, "row": r, "coefficient": str(coefficient), "frame": frame,
                          "matching_NEW_indices": locations}
                (carrier_deliveries if row["kind"] == "carrier" else recipient_deliveries).append(record)
            writes = [(i, e) for i, e in enumerate(oldP) if e[0] == "ADD" and e[1] == q and e[-1] == Z]
            require(not any(e[0] == "SCALE" and e[1] == q and e[-1] == Z for e in oldP), "No old anchor Z SCALE")
            for i, event in writes:
                source, coefficient = event[2:4]
                require(not any(e[-1] == Z and e[0] in ("ADD", "SCALE", "COPY") and e[1] == source for e in oldP[i+1:]), "Postponed donor unchanged at Z after old write")
                require(not any(e[0] == "ADD" and e[-1] == Z and e[2] == q for e in oldP[i+1:]), "No old outgoing anchor read after postponed write")
                replacement = ["ADD", q, source, coefficient, G]
                require(newcount[canonical(replacement)]-oldcount[canonical(replacement)] == 1
                        and newcount[canonical(event)] == 0, "Exact postponed-write replacement")
                postponed.append({"anchor": q, "donor": source, "coefficient": coefficient,
                                  "OLD_index": i, "NEW_indices": [j for j, e in enumerate(newP) if e == replacement], "frame": G})
            for r, coefficient in h[q].items():
                if r != q:
                    tail.append(["ADD", r, q, str(-coefficient), FULL])
    require(len(carrier_deliveries) == 6, "All six carrier deliveries")
    require(len(tail) == 16 and newP[-len(tail):] == tail, "Actual sixteen-event restoration suffix")
    require(all(e[1] not in h and e[2] in h for e in tail), "Restoration transvections commute")
    for j in range(old["public"]):
        v = {j: F(1)}
        for _, dest, source, coefficient, _frame in tail:
            if v.get(source, 0):
                v = add_vectors(v, {dest: F(coefficient)*v[source]})
        expected = add_vectors({j: F(1)}, u.get(j, {}), F(-1))
        require(v == expected, "Literal restoration suffix equals U inverse on every public column")
    return {"carrier_deliveries": carrier_deliveries, "recipient_deliveries": recipient_deliveries,
            "postponed_writes": postponed, "restoration_suffix": tail,
            "restoration_suffix_public_columns": old["public"], "restore_order_commutes": True}


def controls(old, h, clusters, baseline_departures):
    variants = []
    omission = {q: dict(v) for q, v in h.items()}
    require(omission[624].pop(732) == F(1, 2), "Real h624 omitted term")
    variants.append(("h624_omit_732_over2", omission))
    shorthand = {q: dict(v) for q, v in h.items()}
    shorthand[624] = {624: F(1), 625: F(-1)}
    variants.append(("h624_false_two_term_shorthand", shorthand))
    result = []
    for name, changed in variants:
        anchors, departures, _terminal = trace_preparation(old, changed)
        index = anchors.index(624)
        mismatches = [{"row": r, "expected": str(baseline_departures[r]["values"][index]),
                       "actual": str(row["values"][index]), "first_destination": row["destination"]}
                      for r, row in sorted(departures.items()) if row["values"][index] != baseline_departures[r]["values"][index]]
        require(mismatches, "Control changes actual propagated preparation response")
        observed = None
        try:
            response_contract(anchors, departures, clusters)
        except ValueError as error:
            observed = str(error)
        require(observed is not None, "Bad h624 response support/unit must reject")
        _, basis = basis_checks(old, changed)
        result.append({"control": name, "observed_error": observed, "coefficient_witness": mismatches[0],
                       "changed_response_rows": len(mismatches), "input_basis_inverse_and_M_commutation_still_pass": basis["commutes_with_declared_M"]})
    return result


def compute():
    data = inputs()
    old, new = data["OLD-WORD.json.gz"], data["NEW-WORD.json.gz"]
    h, clusters = directions(data["LIFTS.json"])
    require(len(h[624]) == 15 and h[624].get(732) == F(1, 2), "Literal fifteen-term h624 direction")
    require(all(canonical(old[k]) == canonical(new[k]) for k in old if k not in ("initial", "program")), "Unchanged interface/frame/final data")
    require([i for i, (a, b) in enumerate(zip(old["initial"], new["initial"])) if a != b] == sorted(h), "Exactly six changed initial headers")
    anchors, departures, terminal = trace_preparation(old, h)
    trace_preparation(new)  # Header/lifetime typing only; no NEW value replay.
    reports, unit = response_contract(anchors, departures, clusters)
    u, basis = basis_checks(old, h)
    bindings = literal_bindings(old, new, h, clusters, reports, u)
    main = set(old["live"]) | {r+112 for r in old["live"]}
    return {"schema_version": 1, "status": "PASS_INDEPENDENT_SIX_DIRECTION_PREPARATION",
            "source_sha256": {name: pin[0] for name, pin in PINS.items()},
            "source_git_blobs": {name: pin[1] for name, pin in PINS.items()},
            "anchor_order": anchors, "directions": {str(q): sparse_json(h[q]) for q in anchors},
            "direction_main_role_support": {str(q): sorted(set(h[q]) & main) for q in anchors},
            "old_Z_public_first_departures": len(departures), "owned_Z_terminal_direction_checks": terminal,
            "first_departure_responses": reports, "prepared_cross_anchor_unit_matrix": unit,
            "input_basis": basis, "literal_local_bindings": bindings,
            "controls": controls(old, h, clusters, departures),
            "limits": ["Exactly six public direction columns through OLD zero-frame preparation, with zero-owned births; no arbitrary dirty-owned/fullNEW scalar endpoint is replayed.",
                       "The OLD first-departure response table is not itself a proof of the actual round2 modified preparation chronology.",
                       "NEW is checked for literal header/lifetime typing and local delivery/postponement/restoration records; wholeNEW endpoint/restoration is reserved forR8.",
                       "U commutation concerns the explicitly declared OLD public shear M; it does not prove NEW implements U_inverse M U.",
                       "No native phase/operator, physical erasure permission, tariff, ordinary/compiler/outer admission or frontier change is supplied."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(canonical(result))
    else:
        path = ROOT / "PREP-ORACLE.json"
        require(path.is_file(), "Retained preparation receipt PREP-ORACLE.json required")
        require(canonical(decode(path.read_bytes())) == canonical(result), "Retained preparation receipt mismatch")
        print("PASS independent six-direction preparation receipt")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        sys.exit(1)
