#!/usr/bin/env python3
"""Independent full rational reverse-functional endpoint oracle.

The reverse-functional method follows our earlier ToikY/OpenAI Codex PR6376
oracle, adapted here to the frozen6375 word and literal prefix. No author,
primary, predecessor or preparation engine is imported or executed.
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
PUBLIC, OWNED, PREFIX_CUT = 770, 29, 17752
FROZEN = {
    "SOURCE-PINS.json": "06514df0ebb826b6561b3fb8f349021240dbd76d0b249f86bf8a7ec5a16cc348",
    "verify_preparation.py": "b025336c2929281ff773fc07631bc00561fd0feddbe202a4e801666bae513bff",
    "oracle_preparation.py": "9ef5a448a1337ded7e9e1e9b18bf4caba2670b7433cb10858a391676d89f35d1",
    "PREP-RESULT.json": "3fe48cc86074cff29d7f98e793fc91f28021f8b1d9f901996f0daf44f4c28ee9",
    "PREP-ORACLE.json": "f308e045f563e10602e78ce23320f592b9748883541c815141da4aed042d3057",
    "PROOF.md": "49175bd7d784d4b6b7b67b83e23dd2080b351b7c50291d62c61ed4d11ba0e212",
    "sources/LIFTS.json": "38960b70a074888a2aeaf3b543629a7ae747c0c5d4f5c853371a6e7c483766c5",
    "sources/NEW-WORD.json.gz": "9e31463a785c18a70f6ae6ef3d04a6560dbb965517109390fe820f9fac3371b3",
    "sources/NOTICE": "91f24d68004688bc0a56303a48edcb5ddabd66bfc2326950603bf98dec245bbe",
    "sources/OLD-WORD.json.gz": "e3b6f1c25d672b8c85433be97ebad77ae6a6972352ce2ff63507d30835fcb491",
    "sources/author-VALIDATION.md": "cf33fe7acd32b1912bde7bf67abe1386eb042c6d269a9540cd28cdd076a7cac3",
    "sources/constructor-source.py": "fe7dc1d9aa55da393465388ee90faaa687b1e5be48dfa816a421069fa3d2de08",
    "sources/upstream-PROOF.md": "769e0f87e6b85c557b48135d2d898bb485cf77ce9925540e0a3740e6283f41af",
}
BLOBS = {
    "NEW-WORD.json.gz": "b1cfd03abe9128cf5a3908fbd82652e5e8a2e292",
    "OLD-WORD.json.gz": "0af79e58172f85c302c35b193205c0b185b09393",
    "LIFTS.json": "2ee8cb78fd149f9aca8dd953c650b92495a56266",
    "constructor-source.py": "c099995bef0e224cbb0ec61c06ed3d0b4d478b33",
    "upstream-PROOF.md": "bd20fcaf2078691d914d6afbc5cb06a75f47770d",
    "NOTICE": "638a187d1417bda8976e945a2aeaed116a090e37",
    "author-VALIDATION.md": "0be8e7f1052628c34e24dfae6777cb3749b224a9",
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def decode(raw):
    def pairs(items):
        answer = {}
        for key, value in items:
            require(key not in answer, "Duplicate JSON member")
            answer[key] = value
        return answer
    def bad(value):
        raise ValueError("Nonfinite JSON value " + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad)


def inputs():
    data = {}
    for name, sha in FROZEN.items():
        raw = (ROOT / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == sha, "Frozen scientific sha256 mismatch: " + name)
        if name.startswith("sources/"):
            short = name[len("sources/"):]
            require(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == BLOBS[short],
                    "Source Git blob mismatch: " + short)
            if short.endswith(".json") or short.endswith(".json.gz"):
                data[short] = decode(gzip.decompress(raw) if short.endswith(".gz") else raw)
    return data


def integer(value, low=0):
    require(type(value) is int and value >= low, "Strict integer required")
    return value


def fraction(value):
    require(type(value) in (str, int), "Exact rational string/integer required")
    return F(value)


def coefficient_add(row, role, value):
    if value:
        total = row.get(role, F(0)) + value
        if total:
            row[role] = total
        else:
            row.pop(role, None)


def encoded(row):
    return [[r, str(c)] for r, c in sorted(row.items()) if c]


def digest(value):
    return hashlib.sha256((canonical(value)+"\n").encode()).hexdigest()


def compile_word(word):
    require(type(word) is dict and set(word) == {"schema", "public", "frames", "initial", "final", "owned_fields", "ports", "live", "program"}, "Word object schema")
    require(type(word["public"]) is int and word["public"] == PUBLIC
            and type(word["owned_fields"]) is int and word["owned_fields"] == OWNED,
            "Frozen public/owned dimensions")
    initial, final, frames, program = (word[k] for k in ("initial", "final", "frames", "program"))
    require(type(initial) is list and type(final) is list and len(initial) == len(final) == PUBLIC,
            "Public headers")
    require(type(frames) is list and all(type(frame) is list and all(type(v) is int and 0 <= v < 512 for v in frame) for frame in frames), "Binary frame data typing")
    def frame(value):
        require(type(value) is int and 0 <= value < len(frames), "Frame identifier")
    for value in initial+final:
        frame(value)
    require(type(word["live"]) is list and len(word["live"]) == len(set(word["live"])) == len(word["ports"]) == 104
            and all(type(r) is int and 0 <= r < 112 for r in word["live"]), "Actual live-port source set")
    state = initial[:] + [None]*OWNED
    active, births = set(), {}
    per_role = Counter()
    lifetimes, copies, ops = [], [], []
    maximum = 0
    for index, event in enumerate(program):
        require(type(event) is list and event and type(event[0]) is str, "Instruction list/opcode")
        op = event[0]
        require(op in ("ADD", "SCALE", "COPY", "MOVE", "INIT", "CLEAR"), "Instruction opcode")
        require(len(event) == {"ADD": 5, "SCALE": 4, "COPY": 5, "MOVE": 5, "INIT": 3, "CLEAR": 3}[op], "Instruction arity")
        d = integer(event[1])
        require(d < PUBLIC+OWNED, "Destination role range")
        if op == "INIT":
            frame(event[2])
            require(d >= PUBLIC and state[d] is None and d not in active, "Blank inactive owned INIT")
            per_role[d] += 1
            births[d] = {"lifetime_ordinal": len(lifetimes)+len(active)+1,
                         "role_lifetime_ordinal": per_role[d], "role": d,
                         "INIT_event_index": index, "INIT_frame": event[2]}
            active.add(d)
            maximum = max(maximum, len(active))
            state[d] = event[2]
            ops.append((op, d, -1, F(0)))
        elif op == "CLEAR":
            frame(event[2])
            require(d >= PUBLIC and d in active and state[d] == event[2], "Active owned CLEAR exact frame")
            record = births.pop(d)
            record.update({"CLEAR_event_index": index, "CLEAR_frame": event[2]})
            lifetimes.append(record)
            active.remove(d)
            state[d] = None
            ops.append((op, d, -1, F(0)))
        elif op == "MOVE":
            frame(event[2]); frame(event[3])
            require(type(event[4]) is bool and event[4] == (d >= PUBLIC), "Strict MOVE ownership flag")
            require(state[d] == event[2], "MOVE current source header")
            state[d] = event[3]
            ops.append((op, d, -1, F(0)))
        else:
            f = event[-1]
            frame(f)
            require(state[d] == f, "Scalar active destination/current frame")
            if op == "SCALE":
                c = fraction(event[2])
                require(c != 0, "Invertible scalar SCALE")
                ops.append((op, d, -1, c))
            else:
                s = integer(event[2])
                require(s < PUBLIC+OWNED and s != d and state[s] == f, "Distinct active same-frame scalar source")
                c = fraction(event[3])
                ops.append((op, d, s, c))
                if op == "COPY":
                    copies.append({"event_index": index, "destination": d, "source": s, "frame": f})
    require(state == final+[None]*OWNED and not active and not births, "Final exact headers/inactive owned lifetimes")
    require(len(lifetimes) == 43 and len(per_role) == 29 and maximum == 13, "Actual43 lifetimes/29 roles/peak13")
    lifetimes.sort(key=lambda r: r["INIT_event_index"])
    for ordinal, record in enumerate(lifetimes, 1):
        record["lifetime_ordinal"] = ordinal
    return tuple(ops), lifetimes, copies, {"instructions": len(program), "public": PUBLIC, "owned_roles": len(per_role),
                                           "owned_lifetimes": len(lifetimes), "peak_owned": maximum,
                                           "COPY_instructions": len(copies)}


def pullback(reverse_ops, output_role):
    """One full exact functional over all799 formal entrance coordinates."""
    row = {output_role: F(1)}
    for op, d, s, c in reverse_ops:
        if op == "ADD":
            value = row.get(d)
            if value:
                coefficient_add(row, s, c*value)
        elif op == "SCALE":
            if d in row:
                row[d] *= c
        elif op == "COPY":
            value = row.pop(d, F(0))
            coefficient_add(row, s, c*value)
        elif op == "INIT":
            row.pop(d, None)  # Blank birth kills any prior scratch coordinate.
        elif op == "CLEAR":
            # A valid future functional cannot read an inactive slot. This is
            # not a statement about the payload immediately BEFORE CLEAR.
            require(not row.get(d, 0), "Backward inactive owned slot coefficient")
            row.pop(d, None)
        # MOVE is the identity ONLY in this declared normalized scalar model.
    require(all(r < PUBLIC for r in row), "No surviving initial inactive-owned coefficient")
    return row


def public_map(ops, cutoff):
    reversed_prefix = tuple(reversed(ops[:cutoff]))
    return [pullback(reversed_prefix, output) for output in range(PUBLIC)]


def clear_functions(ops, lifetimes):
    answer = []
    for record in lifetimes:
        row = pullback(tuple(reversed(ops[:record["CLEAR_event_index"]])), record["role"])
        payload = encoded(row)
        answer.append(dict(record, public_coefficients=payload, public_support=len(payload),
                           public_row_sha256=digest(payload)))
    return answer


def copy_blank_checks(ops, copies):
    for copy in copies:
        row = pullback(tuple(reversed(ops[:copy["event_index"]])), copy["destination"])
        require(not row, "COPY pre-destination must be blank on all public inputs")
    return {"literal_COPY_count": len(copies), "all_public_pre_destination_functions_zero": True,
            "qualification": "COPY is interpreted as overwrite; these sources have no literal COPY instructions."}


def expected_maps(old, specification):
    M = [{r: F(1)} for r in range(PUBLIC)]
    for r in old["live"]:
        coefficient_add(M[r+112], r, F(1))
    N = [{} for _ in range(PUBLIC)]
    anchors = []
    tail = []
    require(type(specification) is dict and set(specification) == {"schema_version", "rounds"}, "Lift specification schema")
    for rd in specification["rounds"]:
        for cluster in rd["clusters"]:
            for text, payload in cluster["anchors"].items():
                require(type(text) is str and text.isascii() and text.isdigit(), "Anchor identifier")
                q = int(text)
                require(0 <= q < PUBLIC and q not in anchors, "Distinct public anchor")
                anchors.append(q)
                require(type(payload) is dict and set(payload) == {"h"}, "Direction object")
                for role, value in payload["h"].items():
                    require(type(role) is str and role.isascii() and role.isdigit(), "Direction role identifier")
                    r, c = int(role), fraction(value)
                    require(0 <= r < PUBLIC, "Direction public input role")
                    coefficient_add(N[r], q, c)
                    if r != q:
                        tail.append(["ADD", r, q, str(-c), 127])
                coefficient_add(N[q], q, F(-1))
    require(sorted(anchors) == [472, 520, 544, 624, 655, 671] and len(tail) == 16, "Six directions/sixteen literal restorations")
    P = [dict(row) for row in M]
    for r, row in enumerate(N):
        for q, c in row.items():
            coefficient_add(P[r], q, c)
    require(sum(map(len, M)) == 874 and sum(map(len, N)) == 16 and sum(map(len, P)) == 890,
            "Expected M/N/M+N counts")
    return M, N, P, tail


def compare_maps(actual, expected, label):
    require(len(actual) == len(expected) == PUBLIC, label + " full output count")
    for output, (row, want) in enumerate(zip(actual, expected)):
        for source in sorted(row.keys() | want.keys()):
            require(row.get(source, F(0)) == want.get(source, F(0)),
                    label + " coefficient mismatch at output" + str(output) + ",input" + str(source))
    payload = [encoded(row) for row in actual]
    return {"rows": PUBLIC, "input_columns": PUBLIC, "coefficients_compared": PUBLIC*PUBLIC,
            "nonzero_coefficients": sum(map(len, actual)), "public_matrix_sha256": digest(payload)}


def first_difference(actual, expected, output):
    for source in sorted(actual.keys() | expected.keys()):
        if actual.get(source, F(0)) != expected.get(source, F(0)):
            return {"output": output, "input": source, "actual": str(actual.get(source, F(0))),
                    "expected": str(expected.get(source, F(0)))}
    return None


def word_controls(new, ops, baseline):
    probes = [
        ("drop_carrier130_h624_response", ["ADD", 130, 624, "-1/2", 105], 112),
        ("drop_postponed_h624_write", ["ADD", 624, 623, "1", 117], 624),
        ("drop_tail205_restoration", ["ADD", 205, 624, "-1", 127], 205),
        ("drop_tail732_half_restoration", ["ADD", 732, 624, "-1/2", 127], 732),
    ]
    answer = []
    for label, event, output in probes:
        indices = [i for i, actual in enumerate(new["program"]) if actual == event]
        require(len(indices) == 1, "One actual literal control event")
        index = indices[0]
        modified = ops[:index]+ops[index+1:]
        row = pullback(tuple(reversed(modified)), output)
        witness = first_difference(row, baseline[output], output)
        require(witness is not None, "Actual full-word omission must change a public coefficient: " + label)
        answer.append({"control": label, "NEW_event_index": index, "omitted_event": event,
                       "actual_modified_full_word_output_function": encoded(row), "coefficient_witness": witness,
                       "qualification": "Full modified word is pulled back for the named output; the omitted ADD does not change the literal frame/lifetime sequence."})
    return answer


def compute():
    data = inputs()
    old, new = data["OLD-WORD.json.gz"], data["NEW-WORD.json.gz"]
    require(all(canonical(old[k]) == canonical(new[k]) for k in old if k not in ("initial", "program")), "Unchanged interface/frame/final data")
    oldops, oldlife, oldcopy, oldstats = compile_word(old)
    newops, newlife, newcopy, newstats = compile_word(new)
    require(len(oldops) == 17757 and len(newops) == 17768 and len(newops)-PREFIX_CUT == 16,
            "Literal source/full/prefix lengths")
    M, N, P, tail = expected_maps(old, data["LIFTS.json"])
    require(new["program"][PREFIX_CUT:] == tail, "Actual final16 restoration instructions")
    require(all(record["CLEAR_event_index"] < PREFIX_CUT for record in newlife), "Prefix has closed every owned lifetime")
    oldmap = public_map(oldops, len(oldops))
    prefixmap = public_map(newops, PREFIX_CUT)
    newmap = public_map(newops, len(newops))
    maps = {"OLD": compare_maps(oldmap, M, "OLD=M"),
            "NEW_prefix_before16restores": compare_maps(prefixmap, P, "ActualNEWprefix=M+N"),
            "NEW": compare_maps(newmap, M, "NEW=M")}
    require(all(a == b for a, b in zip(oldmap, newmap)), "Actual OLD/NEW public matrices coincide")
    oldclears, newclears = clear_functions(oldops, oldlife), clear_functions(newops, newlife)
    # These are independently derived functions, not presumed equal across
    # different formal helper input presentations.
    clear_differences = []
    for a, b in zip(oldclears, newclears):
        require((a["role"], a["role_lifetime_ordinal"]) == (b["role"], b["role_lifetime_ordinal"]), "Paired declared lifetime roles/order")
        if a["public_coefficients"] != b["public_coefficients"]:
            clear_differences.append({"lifetime_ordinal": a["lifetime_ordinal"], "role": a["role"],
                                      "OLD_row_sha256": a["public_row_sha256"], "NEW_row_sha256": b["public_row_sha256"]})
    return {"schema_version": 1, "status": "PASS_INDEPENDENT_FULL_RATIONAL_ENDPOINT",
            "frozen_scientific_sha256": FROZEN, "source_git_blobs": BLOBS,
            "method": "Exact reverse output functionals, independently adapted from our6376 oracle; no author/primary scientific execution or imports.",
            "formal_domain": "All770 public entrance coordinates arbitrary;29owned slots initially inactive;INIT is blank activation and CLEAR is owned projection/deactivation. Every backwards row is checked to have zero initial inactive-owned coefficients.",
            "prefix_cut_t": PREFIX_CUT, "word_stats": {"OLD": oldstats, "NEW": newstats},
            "actual_public_maps": maps, "N_rows": [encoded(row) for row in N],
            "all_public_rows_compared_directly_before_hashing": True,
            "COPY_blank_checks": {"OLD": copy_blank_checks(oldops, oldcopy), "NEW": copy_blank_checks(newops, newcopy)},
            "pre_CLEAR_functions": {"OLD": oldclears, "NEW": newclears},
            "OLD_NEW_pre_CLEAR_function_differences": clear_differences,
            "nonzero_pre_CLEAR_counts": {"OLD": sum(bool(row["public_coefficients"]) for row in oldclears),
                                         "NEW": sum(bool(row["public_coefficients"]) for row in newclears)},
            "controls": word_controls(new, newops, newmap),
            "limits": ["These are normalized scalar maps under changed literal initial headers, not equality of physical input embeddings or native operators.",
                       "P=M+N and finalNEW=M close actual global scalar delivery; actual intermediate round2 preparation equality and an independent constructor regeneration are not asserted.",
                       "Nonzero pre-CLEAR values are measured honestly. Formal projection is not physical erasure permission or owned_erasure admission.",
                       "No native phase/allcolumns/allwidths, productive tariff, ordinary funding, compiler/outer admission, newkappa or frontier change is supplied.",
                       "The16restoration ADDs commute; reversing their order is not used as a failure control."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(canonical(result))
    else:
        path = ROOT / "ENDPOINT-ORACLE.json"
        require(path.is_file(), "Retained endpoint receipt ENDPOINT-ORACLE.json required")
        require(canonical(decode(path.read_bytes())) == canonical(result), "Retained endpoint receipt mismatch")
        print("PASS independent full rational endpoint receipt")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        sys.exit(1)
