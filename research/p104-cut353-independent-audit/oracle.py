#!/usr/bin/env python3
"""Reverse-covector/forward-vector exact oracle for the PR6716 cut.

The first monomial coordinate is source Q (not the proof's q=Q^-1).
LOCAL is an explicit conditional contract, not native supplier admission.
"""
import argparse
from fractions import Fraction as F
from hashlib import sha256, sha1
import json
from pathlib import Path

N = 18
UNIT = (0, (0,) * N)
ONE = {UNIT: (F(1), F(0))}
MAX_TERMS = 100000
INPUT_PINS = {
    "inputs/PROOF.md": "bdf2a3e379d0aaf8ae42a49b09ee6f9d21c5c1a8ec8653fab75efac0c5c93099",
    "inputs/README.md": "68f52f2e0fa916cbf98e18896f0f6026469d3e45474e6d4314f95e0959cef6cb",
    "inputs/WITNESS.json": "4c820b99eb1ebebd7cd527f07b0aa86a355865072acace8bfc9fddd998086331",
    "inputs/CONTROLLER-UNRETIRED.json": "8c58adc35a7055dde1eda8f2547492dda9f558a73262fc17f439819c39d2555e",
    "inputs/CONTROLLER.json": "2a0fb1c11fccfcc4dacbc7c82cf439969caa295dba4fc1a21a83e01b4ab8affc",
    "inputs/caller.py.txt": "ad0dd4aa97ae19f687defc8690e0ffb5f8ada551720aba4b48b8d307c776b5ba",
}
META_PINS = {
    "SOURCE-PINS.json": "0de615eb3eac51539567c56e85e177c91c0d3e5c2c69b8cd64abff46f68fc902",
    "CASES.json": "7a7e961a1971c31653770af43b0097ba55d1eb980795a050c74786e8f5c7d6c0",
    "SCHEMA.json": "3936e155a437939af360d5b2c4be83036984e56c7d04665c5eca2dc7f09ba50d",
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def pairs(items):
    out = {}
    for k, v in items:
        need(k not in out, "duplicate JSON key")
        out[k] = v
    return out


def decode_json(raw):
    def bad(value):
        raise ValueError("nonfinite JSON: " + value)
    need(len(raw) <= 16777216, "bounded JSON input bytes")
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad)


def load(path):
    return decode_json(path.read_bytes())


def rational(text):
    need(type(text) is str and len(text) <= 128, "bounded rational string")
    value = F(text)
    need(str(value) == text and value.denominator & (value.denominator - 1) == 0, "canonical dyadic")
    need(value.numerator.bit_length() <= 256 and value.denominator.bit_length() <= 256, "rational height")
    return value


def add(a, b):
    out = a.copy()
    for m, (r, i) in b.items():
        x, y = out.get(m, (F(0), F(0)))
        value = (x + r, y + i)
        if value == (0, 0):
            out.pop(m, None)
        else:
            out[m] = value
    need(len(out) <= MAX_TERMS, "polynomial term budget")
    return out


def scale(poly, real, imag=0):
    if real == 0 and imag == 0:
        return {}
    return {m: (r * real - i * imag, r * imag + i * real) for m, (r, i) in poly.items()}


def shift(poly, power=0, stages=()):
    exponents = [0] * N
    for stage in stages:
        exponents[stage - 1] += 1
    return {((q + power) % 4, tuple(a + b for a, b in zip(d, exponents))): value
            for (q, d), value in poly.items()}


def times(a, b):
    out = {}
    for (q, d), (r, i) in b.items():
        temp = {((p + q) % 4, tuple(x + y for x, y in zip(c, d))): (x * r - y * i, x * i + y * r)
                for (p, c), (x, y) in a.items()}
        out = add(out, temp)
    return out


def lambda_action(poly, sign):
    return add(scale(poly, F(1, 2), F(sign, 2)),
               scale(shift(poly, 2), F(1, 2), F(-sign, 2)))


def serialize(poly):
    return [[q, list(d), [r.numerator, r.denominator, i.numerator, i.denominator]]
            for (q, d), (r, i) in sorted(poly.items())]


def vector(sparse, size):
    out = [{} for unused in range(size)]
    for key, text in sparse.items():
        need(key.isdecimal() and str(int(key)) == key and int(key) < size, "sparse vector role")
        out[int(key)] = scale(ONE, rational(text))
    return out


def roles(event):
    op = event[0]
    if op == "LOCAL":
        return event[2:4]
    if op in ("ADD", "SWAP", "QUERY", "IDLE"):
        return event[1:3]
    return event[1:2]


def check_events(events, size):
    need(type(events) is list and len(events) <= 1024, "bounded event list")
    for event in events:
        need(type(event) is list and event, "instruction list")
        op = event[0]
        lengths = {"ADD": 4, "SWAP": 3, "SCALE": 3, "LAMBDA": 3,
                   "QUERY": 4, "LOCAL": 4, "IDLE": 4, "IDLE_ONE": 3}
        need(op in lengths and len(event) == lengths[op], "typed opcode")
        indices = roles(event)
        need(all(type(x) is int and 0 <= x < size for x in indices), "typed role indices")
        need(len(set(indices)) == len(indices), "distinct two-field operands")
        if op in ("ADD", "SCALE"):
            value = rational(event[-1])
            need(op != "SCALE" or value != 0, "invertible ordinary scale")
        elif op in ("QUERY", "LAMBDA"):
            need(type(event[-1]) is int and event[-1] in (-1, 1), "signed phase exponent")
        elif op == "LOCAL":
            need(type(event[1]) is int and 1 <= event[1] <= N, "typed LOCAL stage")
        elif op in ("IDLE", "IDLE_ONE"):
            stages = event[-1]
            need(type(stages) is list and stages and all(type(x) is int and 1 <= x <= N for x in stages),
                 "typed idle stage list")
            need(stages == sorted(set(stages)), "distinct ascending idle stages")


def reverse(row, events):
    """Pull one output covector through M_last ... M_first."""
    row = row.copy()
    for event in reversed(events):
        op = event[0]
        if op == "ADD":
            dst, src, text = event[1:]
            row[src] = add(row[src], scale(row[dst], rational(text)))
        elif op == "SWAP":
            a, b = event[1:]
            row[a], row[b] = row[b], row[a]
        elif op == "SCALE":
            row[event[1]] = scale(row[event[1]], rational(event[2]))
        elif op == "LAMBDA":
            row[event[1]] = lambda_action(row[event[1]], event[2])
        elif op == "QUERY":
            dst, src, exponent = event[1:]
            row[src] = add(row[src], shift(row[dst], exponent))
        elif op == "LOCAL":
            stage, src, dst = event[1:]
            old_src, old_dst = row[src], row[dst]
            row[src] = shift(add(old_src, shift(old_dst, -1)), stages=(stage,))
            row[dst] = shift(old_dst, stages=(stage,))
        else:
            for role in roles(event):
                row[role] = shift(row[role], stages=event[-1])
        need(sum(len(x) for x in row) <= MAX_TERMS, "reverse live term budget")
    return row


def forward(column, events):
    """Push one independent column through chronological instructions."""
    column = column.copy()
    for event in events:
        op = event[0]
        if op == "ADD":
            dst, src, text = event[1:]
            column[dst] = add(column[dst], scale(column[src], rational(text)))
        elif op == "SWAP":
            a, b = event[1:]
            column[a], column[b] = column[b], column[a]
        elif op == "SCALE":
            column[event[1]] = scale(column[event[1]], rational(event[2]))
        elif op == "LAMBDA":
            column[event[1]] = lambda_action(column[event[1]], event[2])
        elif op == "QUERY":
            dst, src, exponent = event[1:]
            column[dst] = add(column[dst], shift(column[src], exponent))
        elif op == "LOCAL":
            stage, src, dst = event[1:]
            old_src, old_dst = column[src], column[dst]
            column[dst] = shift(add(old_dst, shift(old_src, -1)), stages=(stage,))
            column[src] = shift(old_src, stages=(stage,))
        else:
            for role in roles(event):
                column[role] = shift(column[role], stages=event[-1])
        need(sum(len(x) for x in column) <= MAX_TERMS, "forward live term budget")
    return column


def basis(index, size):
    out = [{} for unused in range(size)]
    out[index] = ONE.copy()
    return out


def expected_target(declaration):
    need(type(declaration) is list and len(declaration) == 20 and
         all(type(x) is int for x in declaration) and declaration[1] == 0,
         "20-coordinate source diagonal, dummy coordinate zero")
    return {(declaration[0] % 4, tuple(declaration[2:])): (F(1), F(0))}


def dot(left, right):
    out = {}
    for a, b in zip(left, right):
        out = add(out, times(a, b))
    return out


def inverse_ordinary(events):
    out = []
    for event in reversed(events):
        if event[0] == "SWAP":
            out.append(event.copy())
        elif event[0] == "ADD":
            out.append(event[:-1] + [str(-rational(event[-1]))])
        else:
            need(event[0] == "SCALE", "ordinary inverse opcode")
            out.append(event[:-1] + [str(1 / rational(event[-1]))])
    return out


def compute(unretired, final, witness):
    need(unretired["roles"] == 34 and final["roles"] == 35, "independent role counts")
    need(unretired["stages"] == final["stages"] == N, "18 independent Laurent stages")
    old_events, new_events = unretired["events"], final["events"]
    need(len(old_events) == 562 and len(new_events) == 586, "literal event counts")
    check_events(old_events, 34)
    check_events(new_events, 35)
    need([witness[x] for x in ("cut_after", "handoff_after", "pivot", "fresh")] == [353, 362, 4, 34],
         "literal cut and fresh handoff indices")
    first = next(index for index, event in enumerate(new_events) if 34 in roles(event))
    need(first == 363 and all(34 not in roles(e) for e in new_events[:363]), "fresh input untouched until handoff")
    a, b, c, d = [vector(witness[key], 34) for key in ("a", "b", "c", "d")]
    boundary, middle = witness["boundary"], witness["middle"]
    need(len(boundary) == 3 and len(middle) == 6, "ordinary witness word sizes")
    check_events(boundary, 34)
    check_events(middle, 34)
    need(all(e[0] in ("ADD", "SCALE", "SWAP") for e in boundary + middle), "ordinary witness coefficients")
    need(new_events[:3] == inverse_ordinary(boundary) and new_events[3:357] == old_events[:354]
         and new_events[357:363] == middle, "literal inverseG/prefix/J binding at handoff")
    pivot = basis(4, 34)
    identities = [dot(a, b) == ONE, dot(c, d) == ONE,
                  reverse(pivot, boundary) == c, forward(d, boundary) == pivot,
                  reverse(pivot, middle) == a, forward(b, middle) == pivot]
    need(all(identities), "six ordinary dual-pair/basis identities")
    S = lambda_action(shift(ONE, -1), 1)
    need(times(S, S) == ONE and shift(ONE, 4) == ONE, "S involution with Q^4=1")
    need(S != shift(ONE, -1) and shift(ONE, 2) != ONE, "retain central square and global lambda")
    prefix = old_events[:354]
    a_prefix, prefix_d = reverse(a, prefix), forward(d, prefix)
    need(a_prefix == [times(S, entry) for entry in c], "all34 exact aP=S*c positions")
    need(prefix_d == [times(S, entry) for entry in b], "all34 exact Pd=S*b positions")
    final_matrix = [reverse(basis(row, 35), new_events) for row in range(35)]
    need(len(unretired["diagonal"]) == 34 and len(final["diagonal"]) == 35, "declared diagonal lengths")
    targets = [expected_target(entry) for entry in unretired["diagonal"]]
    need(witness["group"] == [4, 20, 21] and targets[4] == targets[20] == targets[21],
         "G mixes equal complete old targets")
    need(all(set(roles(e)) <= {4, 20, 21} for e in boundary), "G support in equal-target group")
    targets[4] = shift(ONE, -1)
    targets.append(shift(ONE, stages=(10, 11, 12, 13)))
    need([expected_target(entry) for entry in final["diagonal"]] == targets, "fresh expected target contract")
    for row in range(35):
        for col in range(35):
            need(final_matrix[row][col] == (targets[row] if row == col else {}), "literal35x35 endpoint")
    artifact = {"schema_version": 1, "a_prefix": [serialize(x) for x in a_prefix],
                "prefix_d": [serialize(x) for x in prefix_d],
                "final_matrix": [[serialize(x) for x in row] for row in final_matrix]}
    need(len(canonical(artifact)) <= 4194304, "canonical artifact byte budget")
    return artifact, {"cut_after": 353, "handoff_after": 362, "pivot": 4, "fresh": 34,
                      "unretired_roles": 34, "unretired_events": 562, "final_roles": 35,
                      "final_events": 586, "stages": 18, "cut_cells": 68, "final_cells": 1225,
                      "ordinary_identities": 6, "fresh_first_contact": first}


def validate_poly(poly):
    need(type(poly) is list and len(poly) <= MAX_TERMS, "polynomial term list")
    previous = None
    for term in poly:
        need(type(term) is list and len(term) == 3, "term triple")
        q, stages, coefficient = term
        need(type(q) is int and 0 <= q < 4, "reduced central exponent")
        need(type(stages) is list and len(stages) == N and
             all(type(x) is int and -1024 <= x <= 1024 for x in stages), "typed Laurent exponents")
        need(type(coefficient) is list and len(coefficient) == 4 and
             all(type(x) is int and x.bit_length() <= 4096 for x in coefficient), "typed Gaussian rational")
        rn, rd, im, iden = coefficient
        need(rd > 0 and iden > 0, "positive denominators")
        r, i = F(rn, rd), F(im, iden)
        need([r.numerator, r.denominator, i.numerator, i.denominator] == coefficient and (r != 0 or i != 0),
             "normalized nonzero Gaussian coefficient")
        key = (q, tuple(stages))
        need(previous is None or previous < key, "strictly sorted unique monomials")
        previous = key


def validate_artifact(obj):
    need(type(obj) is dict and set(obj) == {"schema_version", "a_prefix", "prefix_d", "final_matrix"}, "artifact keys")
    need(type(obj["schema_version"]) is int and obj["schema_version"] == 1, "artifact schema")
    for key in ("a_prefix", "prefix_d"):
        need(type(obj[key]) is list and len(obj[key]) == 34, "34 cut positions")
        for poly in obj[key]:
            validate_poly(poly)
    need(type(obj["final_matrix"]) is list and len(obj["final_matrix"]) == 35, "35 endpoint rows")
    for row in obj["final_matrix"]:
        need(type(row) is list and len(row) == 35, "35 endpoint columns")
        for poly in row:
            validate_poly(poly)


def actual_controls(unretired, final, artifact):
    """Exercise the real reverse engine on valid mutated source instructions.

    These endpoint tests deliberately bypass the constructor-prefix equality
    gate. Expected targets come again from the unretired target declaration,
    not the source final packet or recomputed final matrix.
    """
    targets = [expected_target(x) for x in unretired["diagonal"]]
    targets[4] = shift(ONE, -1)
    targets.append(shift(ONE, stages=(10, 11, 12, 13)))
    events = final["events"]
    query_index = next(j for j, e in enumerate(events) if e[0] == "QUERY")
    need(events[query_index][-1] == -1 and events[0][0] == "ADD" and events[0][-1] == "-1",
         "control mutation sites")
    mutants = []
    changed_query = [e.copy() for e in events]
    changed_query[query_index][-1] = 1
    mutants.append(("first_QUERY_central_inverse", changed_query))
    changed_input_basis = [e.copy() for e in events]
    changed_input_basis[0][-1] = "-2"
    mutants.append(("first_input_G_ADD_coefficient", changed_input_basis))
    witnesses = []
    for name, instructions in mutants:
        check_events(instructions, 35)
        witness = None
        for row in range(35):
            actual = reverse(basis(row, 35), instructions)
            for col in range(35):
                expected = targets[row] if row == col else {}
                difference = add(actual[col], scale(expected, -1))
                if difference:
                    witness = {"name": name, "row": row, "column": col,
                               "nonzero_difference": serialize(difference)}
                    break
            if witness is not None:
                break
        need(witness is not None, "actual reverse engine failed to detect source-word mutant")
        witnesses.append(witness)

    def rejection(function, name):
        try:
            function()
        except ValueError:
            return name
        raise ValueError("strict malformed-artifact control accepted: " + name)

    def changed_artifact(mode):
        obj = json.loads(canonical(artifact))
        poly = next(poly for poly in obj["a_prefix"] if len(poly) >= 2)
        if mode == "boolean_denominator":
            poly[0][2][1] = True
        elif mode == "duplicate_monomial":
            poly.append(poly[0])
        else:
            poly.reverse()
        return obj

    strict = [rejection(lambda mode=mode: validate_artifact(changed_artifact(mode)), mode)
              for mode in ("boolean_denominator", "duplicate_monomial", "unsorted_monomials")]
    strict.append(rejection(lambda: decode_json(b'{"bad":NaN}'), "nonfinite_JSON"))
    strict.append(rejection(lambda: decode_json(b'{"key":1,"key":1}'), "duplicate_JSON_key"))
    return {"actual_source_word_mutations": witnesses, "strict_rejections": strict,
            "total_controls": len(witnesses) + len(strict)}


def authenticate(package):
    need(INPUT_PINS and META_PINS, "oracle not sealed with frozen input pins")
    for name, expected in META_PINS.items():
        need(sha256((package / name).read_bytes()).hexdigest() == expected, "frozen metadata: " + name)
    manifest = load(package / "SOURCE-PINS.json")
    need(manifest["schema_version"] == 1 and
         {entry["local_path"] for entry in manifest["sources"]} == set(INPUT_PINS), "six inert source manifest entries")
    for name, expected in INPUT_PINS.items():
        raw = (package / name).read_bytes()
        need(len(raw) <= 16777216 and sha256(raw).hexdigest() == expected, "frozen inert input: " + name)
        entry = next(x for x in manifest["sources"] if x["local_path"] == name)
        need(entry["sha256"] == expected and entry["git_commit"] == "a467457692bc9e11113d9b2e2e34ea8ffb553b58",
             "frozen source head and SHA")
        need(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == entry["git_blob"], "source Git blob")
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--package", type=Path, default=Path(__file__).resolve().parent)
    p.add_argument("--first", action="store_true")
    p.add_argument("--artifact", type=Path)
    p.add_argument("--expected", type=Path)
    p.add_argument("--write-actions", "--write-packet", dest="write_actions", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    authenticate(args.package)
    inputs = args.package / "inputs"
    unretired = load(inputs / "CONTROLLER-UNRETIRED.json")
    final = load(inputs / "CONTROLLER.json")
    artifact, counts = compute(unretired, final, load(inputs / "WITNESS.json"))
    validate_artifact(artifact)
    controls = actual_controls(unretired, final, artifact)
    common = {"schema_version": 1, "scope": "PR6716 cut353 fresh34 conditional LOCAL audit",
              "source_manifest_sha256": META_PINS["SOURCE-PINS.json"],
              "case_manifest_sha256": META_PINS["CASES.json"], **counts,
              "artifact_sha256": sha256(canonical(artifact)).hexdigest()}
    if not args.first:
        actual = load(args.artifact or args.package / "PACKET.json")
        validate_artifact(actual)
        need(canonical(actual) == canonical(artifact), "actual artifact differs from reverse-row oracle")
        expected = load(args.expected or args.package / "RESULT.json")
        need(canonical(expected) == canonical(common), "actual receipt differs from recomputation")
    if args.write_actions:
        args.write_actions.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    if args.output:
        args.output.write_text(json.dumps(common, indent=2, sort_keys=True) + "\n")
    print("PASS reverse-row cut oracle")
    print(json.dumps(common, sort_keys=True))
    print(json.dumps({"oracle_controls": controls}, sort_keys=True))


if __name__ == "__main__":
    main()
