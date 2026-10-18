#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reassemble the finite programs and replay the sparse physical implementation.

Default is read-only. --write explicitly regenerates TABLE.json and RESULT.json.
Prepared for David Arias with substantial OpenAI Codex assistance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from machine import Machine, binary, marked, ZERO, ONE, need
from shear import build_program, INPUT_TAPES, SCRATCH_TAPES, TAPE_COUNT


def serialize(value):
    return json.dumps(value, indent=2) + "\n"


def serialize_table(table):
    """One instruction per line makes the complete finite bank reviewable."""
    programs = []
    for name, program in table.items():
        rows = ",\n".join("      " + json.dumps(row) for row in program["instructions"])
        programs.append(f'  "{name}": {{\n    "tapes": {program["tapes"]},\n'
                        f'    "entry": {program["entry"]},\n    "instructions": [\n'
                        + rows + "\n    ]\n  }")
    return "{\n" + ",\n".join(programs) + "\n}\n"


def authenticate_inputs():
    entries = json.loads((HERE / "SOURCES.json").read_text())["files"]
    inputs = [entry for entry in entries if entry["usage"] == "input"]
    need([entry["path"] for entry in inputs] == ["research/selected-bit-stream-routes/qadic_streams.py"],
         "exact declared live input")
    for entry in inputs:
        raw = (ROOT / entry["path"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == entry["sha256"], "input SHA256: " + entry["path"])
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == entry["git_blob"], "input Git blob: " + entry["path"])


def ledger(p, q, g, s):
    v = p*q*q*g*s
    conversion = sum(24*n-7*n.bit_count()+15*n.bit_length()+12 for n in (p,q,g,s))
    return conversion+36*v+20*p*q*q*g+28*p*q*g+50*p*q+19*p+7*q+g+s+104


def span(p, q, g, s):
    lengths = [n.bit_length() for n in (p,q,g,s)]
    return 3*p*q*q*g*s+p+g+s+2*q+max(lengths)+sum(lengths)+28


def run_checks(programs):
    count = total = max_volume = 0
    # Exercise each descriptor independently near binary shrink boundaries,
    # then shapes with simultaneously nontrivial prefix, gap and suffix.
    shapes = {(1,1,1,1), (2,3,4,5), (3,5,2,4), (2,8,3,2), (3,7,2,3)}
    for n in (2,3,4,7,8,15,16,31,32,63,64):
        for axis in range(4):
            shape = [1,1,1,1]; shape[axis] = n
            shapes.add(tuple(shape))
    for p,q,g,s in sorted(shapes):
        v = p*q*q*g*s
        bits = [((i*17 + i//7 + 3) % 11) % 2 for i in range(v)]
        for inverse, direction in ((False,"forward"),(True,"inverse")):
            m = Machine(programs[direction], {0:marked(ONE if b else ZERO for b in bits),
                        **{i:binary(n) for i,n in zip((4,5,6,7),(p,q,g,s))}})
            original = {i:dict(m.tapes[i].cells) for i in INPUT_TAPES}
            m.run(max_steps=442*v)
            expected = [None]*v
            for a in range(p):
                for x in range(q):
                    for h in range(g):
                        for y in range(q):
                            old = (((a*q+x)*g+h)*q+y)*s
                            new_y = (y-x if inverse else y+x) % q
                            new = (((a*q+x)*g+h)*q+new_y)*s
                            expected[new:new+s] = bits[old:old+s]
            out = marked(ONE if b else ZERO for b in expected)
            need(m.tapes[1].cells == out.cells and m.tapes[1].head == 1, "complete owned output")
            for i in INPUT_TAPES:
                need(m.tapes[i].cells == original[i] and m.tapes[i].head == 1, "preserved input and head")
                need(not m.write_positions[i], "input tape never written")
            for i in SCRATCH_TAPES:
                need(not m.tapes[i].cells and m.tapes[i].head == 0, "complete scratch erasure and origin")
            need(m.steps == ledger(p,q,g,s), "exact microinstruction ledger")
            visited = sum(len(cells) for cells in m.visits)
            need(visited == span(p,q,g,s) and visited <= 41*v, "visited-cell span ledger")
            need(all(min(cells) == 0 for cells in m.visits), "no head crosses its own origin")
            count += 1; total += m.steps; max_volume = max(max_volume,v)
    return {"cases":count,"shapes":len(shapes),"maximum_payload_bits":max_volume,
            "total_transitions":total,"exact_transition_and_span_ledgers":"pass",
            "source_preservation_output_ownership_scratch_erasure_head_contract":"pass"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write",action="store_true")
    args = parser.parse_args()
    authenticate_inputs()
    programs = {name:build_program(inverse) for name,inverse in (("forward",False),("inverse",True))}
    table = {name:{"tapes":p.tapes,"entry":p.entry,"instructions":p.instructions} for name,p in programs.items()}
    raw = serialize_table(table)
    if args.write:
        (HERE/"TABLE.json").write_text(raw)
    else:
        need((HERE/"TABLE.json").read_text() == raw,"TABLE.json must exactly match finite assembly")
    need(all(p.tapes == TAPE_COUNT == 14 and len(p.instructions) == 531 for p in programs.values()),
         "fixed fourteen-tape, 531-instruction programs")
    need(all(row[1] not in INPUT_TAPES for p in programs.values() for row in p.instructions if row[0] == "write"),
         "static input immutability")
    result = {"schema_version":1,"status":"PASS_FIXED_TAPE_ORDERED_SHEAR",
              "table_sha256":hashlib.sha256(raw.encode()).hexdigest(),
              "physical_tapes":14,"instructions_per_direction":531,"alphabet_symbols":7,
              "uniform_transition_bound":"442 P Q^2 G S",
              "uniform_visited_cell_bound":"41 P Q^2 G S",
              "sparse_replay":run_checks(programs),
              "scope":"all-size unit ordered-shear proof plus finite physical implementation checks; no full caller or kappa change"}
    text = serialize(result)
    if args.write:
        (HERE/"RESULT.json").write_text(text)
    else:
        need((HERE/"RESULT.json").read_text() == text,"RESULT.json must match read-only replay")
    print(text,end="")


if __name__ == "__main__":
    main()
