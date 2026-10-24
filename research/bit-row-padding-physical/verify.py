#!/usr/bin/env python3
"""Independent byte oracle and source-bound finite calibration; not callee admission."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

from machine import (Machine, Tape, PROGRAM, TAPES, BLANK, LEFT, SOURCE, PD, RD,
                     SD, BD, P, R, S, B, D, TEMP, ROWS, PAD, RETURN, OUTPUT, need)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def binary(value):
    return bin(value)[2:][::-1]


def word(tape, origin):
    # Test observation only, never called by the finite controller.
    result = []
    position = origin + 1
    while tape.cells.get(position, BLANK) != BLANK:
        result.append(tape.cells[position])
        position += 1
    return "".join(result)


def snapshot(tape):
    return dict(tape.cells), tape.head


def fixture(p, r, s, b, payload, origins=None):
    origins = origins or [0] * TAPES
    tapes = [Tape.fixture(origin=origin) for origin in origins]
    tapes[SOURCE] = Tape.fixture(payload, origins[SOURCE])
    for index, value in zip((PD, RD, SD, BD), (p, r, s, b)):
        tapes[index] = Tape.fixture(binary(value), origins[index])
    return tapes, origins


def oracle_pad(payload, p, r, s, b):
    padded_rows = (r + s - 1) // s * s
    return "".join(payload[i*r*b:(i+1)*r*b] + "0"*((padded_rows-r)*b)
                   for i in range(p)), padded_rows


def oracle_callee(payload, b):
    # Explicit synthetic completed row-pointwise callback, not a native body.
    return "".join(payload[i:i+b][::-1] for i in range(0, len(payload), b))


def trial(p, r, s, b, payload, origins=None):
    tapes, origins = fixture(p, r, s, b, payload, origins)
    borrowed = [snapshot(tapes[i]) for i in range(5)]
    machine = Machine(tapes)
    need(machine.run() == "call", "one completed-row call boundary")
    padded, padded_rows = oracle_pad(payload, p, r, s, b)
    need(word(tapes[PAD], origins[PAD]) == padded, "all padded fibres")
    need(word(tapes[ROWS], origins[ROWS]) == binary(padded_rows), "paid binary row count")
    before_call = machine.steps
    # The theorem retains this callee premise. Its semantic check here is
    # an oracle observation, not a hidden instruction or runtime admission.
    tapes[RETURN] = Tape.fixture(oracle_callee(padded, b), origins[RETURN])
    need(machine.run() == "done" and machine.calls == 1, "one complete return")
    need(word(tapes[OUTPUT], origins[OUTPUT]) == oracle_callee(payload, b),
         "genuine rows and spectators through restriction")
    need([snapshot(tapes[i]) for i in range(5)] == borrowed, "borrowed bytes and heads")
    for index in (P, R, S, B, D, TEMP, ROWS, PAD, RETURN):
        tape = tapes[index]
        need(tape.head == origins[index] + 1 and
             all(symbol == BLANK or (position == origins[index] and symbol == LEFT)
                 for position, symbol in tape.cells.items()), "owned visited backing erased")
    need(tapes[OUTPUT].head == origins[OUTPUT] + 1, "owned output boundary")
    volume = p*r*b
    visited = sum(t.high-t.low+1 for t in tapes)
    need(machine.steps <= 2048*volume + 2048, "proved transition envelope")
    need(visited <= 64*volume + 64, "proved visited-space envelope")
    return [p, r, s, b, before_call, machine.steps, visited]


def rejects(label, operation):
    try:
        operation()
    except ValueError as error:
        expected={"aliased-physical-port":"distinct physical tape ports",
                  "aliased-return-port":"distinct physical tape ports",
                  "wrong-return-head":"quarantined",
                  "wrong-borrowed-head":"quarantined"}.get(label,"rejected")
        if label=="nonbinary-descriptor":
            if not str(error).startswith("local guard rejected at state "):
                raise RuntimeError("wrong nonbinary rejection") from error
        elif str(error)!=expected:
            raise RuntimeError("wrong rejection for "+label+": "+str(error)) from error
        return label
    raise ValueError("invalid case accepted: " + label)


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def checked_rejection(machine, recover=True):
    tapes=machine.tapes
    before=[dict(t.cells) for t in tapes[:5]]
    origins=[next(k for k,v in t.cells.items() if v==LEFT) for t in tapes]
    try:
        machine.run()
    except ValueError as error:
        if recover:
            check(str(error)=="rejected", "fixed cleanup rejection")
            check([dict(t.cells) for t in tapes[:5]]==before, "reject preserves borrowed bytes")
            check(all(t.head==origins[i]+1 for i,t in enumerate(tapes)), "reject rewinds all heads")
            check(all(all(v==BLANK or (k==origins[i] and v==LEFT) for k,v in t.cells.items())
                     for i,t in enumerate(tapes) if i>=5), "reject erases all owned backing")
        raise
    raise RuntimeError("expected failure did not occur")


def failure_controls():
    rejected = []
    def aliased():
        tapes, _ = fixture(2,5,3,6,"1"*60)
        tapes[PAD] = tapes[SOURCE]
        Machine(tapes)
    rejected.append(rejects("aliased-physical-port", aliased))
    def return_alias():
        tapes,_=fixture(2,5,3,6,"1"*60)
        machine=Machine(tapes)
        check(machine.run()=="call", "return alias reaches call")
        tapes[RETURN]=tapes[SOURCE]
        machine.run()
    rejected.append(rejects("aliased-return-port", return_alias))
    for label, descriptor in (("zero", "0"), ("noncanonical", "10"),
                              ("empty", ""), ("nonbinary", "x")):
        def bad(value=descriptor):
            tapes, _ = fixture(2, 5, 3, 6, "1"*60)
            tapes[PD] = Tape.fixture(value)
            checked_rejection(Machine(tapes), value!="x")
        rejected.append(rejects(label + "-descriptor", bad))
    rejected.append(rejects("stock-exceeds-rows",
                            lambda: checked_rejection(Machine(fixture(1, 2, 3, 2, "1010")[0]))))
    for label, payload in (("short-source", "1"*59), ("long-source", "1"*61)):
        rejected.append(rejects(label, lambda data=payload:
                               checked_rejection(Machine(fixture(2, 5, 3, 6, data)[0]))))
    for label in ("short-return", "long-return", "dirty-added-fibre",
                  "wrong-return-head", "wrong-borrowed-head"):
        def bad(kind=label):
            tapes, origins = fixture(2, 5, 3, 6, "1"*60)
            machine = Machine(tapes)
            check(machine.run() == "call", "failure control call")
            data = oracle_callee(word(tapes[PAD], 0), 6)
            if kind == "short-return":
                data = data[:-1]
            elif kind == "long-return":
                data += "0"
            elif kind == "dirty-added-fibre":
                data = data[:30] + "1" + data[31:]
            tapes[RETURN] = Tape.fixture(data)
            if kind == "wrong-return-head":
                tapes[RETURN].head += 1
            if kind == "wrong-borrowed-head":
                tapes[RD].head += 1
            checked_rejection(machine, kind not in ("wrong-return-head", "wrong-borrowed-head"))
        rejected.append(rejects(label, bad))
    # Complete-return ownership and semantics are NOT runtime oracle checks.
    # A mutation violating the semantic premise can preserve padding zeros.
    tapes, _ = fixture(2, 5, 3, 6, "1"*60)
    machine = Machine(tapes)
    check(machine.run() == "call", "premise separation call")
    tapes[RETURN] = Tape.fixture("0"*72)
    check(machine.run() == "done" and word(tapes[OUTPUT], 0) == "0"*60,
         "zero checks do not certify the completed-callee semantic premise")
    # A faulty cleanup assertion must escape the expected-rejection catcher.
    class BadCleanup:
        def __init__(self):
            self.tapes=fixture(2,5,3,6,"1"*60)[0]
            self.tapes[P]=Tape.fixture("1")
        def run(self):
            raise ValueError("rejected")
    try:
        rejects("zero-descriptor", lambda: checked_rejection(BadCleanup()))
    except RuntimeError as error:
        check(str(error)=="reject erases all owned backing", "precise checker mutation")
    else:
        raise RuntimeError("negative-control checker swallowed bad cleanup")
    return rejected


def source_binding():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    for row in rows:
        need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
             "exact input " + row["path"])
    source = ROOT / "research/bit-row-route-generator"
    generator = (source / "generator.py").read_text()
    interpreter = (source / "interpreter.py").read_text()
    need("if 2*borrowed_digits<e:" in generator and
         "emit('inner_return',a,b);emit('row_unpad',a,b)" in generator,
         "actual source borrowed and completed-return boundary")
    need("'zeros':[0]*(total-size)" in interpreter, "addressed model row metadata")
    specification = json.loads(gzip.decompress((source / "PROGRAM.json.gz").read_bytes()))
    need(specification["owners"] == [462, 461] and len(specification["matcher"]) == 8,
         "actual helper and other owner")
    need([specification[k] for k in ("f","q","w","borrowed_digits","reserve")] == [1,5,4,1,3],
         "actual committed borrowed-branch fixture")
    operations=[step["op"] for step in specification["steps"]]
    need(operations.count("row_pad")==operations.count("row_unpad")==80,
         "all eighty actual source padding lifetimes")
    sequence=["inner_borrow","row_pad","body_sub","raw_reverse_swap","body_add",
              "raw_reverse_swap","body_rsub","inner_return","row_unpad","older_high_swap"]
    need(all(operations[i-1:i+9]==sequence for i,op in enumerate(operations) if op=="row_pad"),
         "actual complete source body and return chronology")
    with tarfile.open(ROOT / "research/physical-ordinary-interchange/inputs/pr2808.tar") as archive:
        retained = archive.extractfile("vendor/pr2786/padding.py").read()
    need(b"row-pointwise" in retained and b"callee must leave added rows zero" in retained,
         "retained padding and callee premise")
    return dict(inputs=len(rows), retained_padding_sha256=hashlib.sha256(retained).hexdigest(),
                source_owners=[462, 461], source_padding_lifetimes=80, actual_fixture=dict(f=1,q=5,w=4,k=1,S=3,
                    high_width=3,borrowed=True,prefixes=2,rows=5,body=6,
                    genuine_bits=60,padded_bits=72,added_bits=12))


def run():
    source = source_binding()
    rows = []
    for p in (1, 2):
        for r in range(1, 5):
            for s in range(1, r+1):
                for b in (1, 2, 3):
                    payload = "".join(str((i*7+i//3+p+r+s+b)%2) for i in range(p*r*b))
                    rows.append(trial(p,r,s,b,payload))
    for i in range(60):
        rows.append(trial(2,5,3,6,"0"*i+"1"+"0"*(59-i)))
    rows.append(trial(2,5,3,6,"1"*60,[7*i-41 for i in range(TAPES)]))
    for shape in ((1,31,16,1),(1,32,17,1),(1,33,32,1),(2,1,1,33),(7,9,5,4)):
        p,r,s,b=shape
        rows.append(trial(p,r,s,b,"10"*(p*r*b//2)+"1"*(p*r*b%2)))
    controls = failure_controls()
    need(all(row[0] in ("read","write","move","goto","call","done","rejected","quarantined") for row in PROGRAM),
         "only local finite opcodes")
    return dict(status="PASS_COMPLETE_FIBRE_ROW_PADDING",source=source,
                tapes=TAPES,instructions=len(PROGRAM),
                program_sha256=hashlib.sha256(json.dumps(PROGRAM,sort_keys=True).encode()).hexdigest(),
                successful_cases=len(rows),basis_columns=60,
                cases_sha256=hashlib.sha256(json.dumps(rows).encode()).hexdigest(),
                actual_fixture=rows[60],translated_fixture=rows[120],
                max_steps=max(row[5] for row in rows),
                rejected=controls,negative_checker_rejects_bad_cleanup=True,
                callee_semantics_remain_conditional=True,
                bounds=dict(transitions="2048*V+2048 excluding callee",
                            visited_cells="64*V+64 including endpoints and callee return"),
                scope="All-width written local-controller proof; finite source-bound adapter calibration, no native supplier admission")


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--emit",action="store_true")
    args=parser.parse_args()
    result=run()
    if not args.emit:
        expected=json.loads((HERE/"RESULT.json").read_text())
        need(json.dumps(result,sort_keys=True)==json.dumps(expected,sort_keys=True),
             "exact typed receipt")
    print(json.dumps(result,sort_keys=True,indent=2))
