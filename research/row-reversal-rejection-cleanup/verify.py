"""Replay the new retirement graph, including rejected-then-valid reuse.

Produced by Nick Petalas. Apache-2.0. Uses only the standard library.
"""
from pathlib import Path
import hashlib
import importlib.util
import itertools
import json
import sys

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("tidy_program", HERE / "program.py")
if SPEC is None or SPEC.loader is None:
    raise ValueError("missing program loader")
p = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(p)
r = p.load_source()
CODE, ALPHABET = r.compile_reverse()
GRAPH, _, HALTS = p.compile_tidy(r, CODE, ALPHABET)
LIMIT = 2_000_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def packet(descriptors, payload, count=26):
    origins = tuple(7 * i - 51 for i in range(count))
    tapes = [r.Tape({o - 20: "1", o + 10000: "|"}, o) for o in origins]
    for tape, word in enumerate((*descriptors, payload)):
        tapes[tape].cells.update({origins[tape] + j: s for j, s in enumerate(word)
                                  if s != "_"})
    return tapes, origins


def execute(code, tapes, budget=LIMIT):
    cpu = r.Machine(code, tapes)
    for tape in tapes:
        tape.local_low = tape.local_high = tape.head
    rejected, last_pc = False, None
    for _ in range(budget):
        last_pc = cpu.pc
        instruction = code[cpu.pc]
        try:
            cpu.step()
        except ValueError as error:
            require(str(error) == "invalid scanned symbol", "unexpected machine error")
            rejected = True
            break
        if instruction[0] == "move":
            tape = tapes[instruction[1]]
            tape.local_low = min(tape.local_low, tape.head)
            tape.local_high = max(tape.local_high, tape.head)
        if cpu.halted:
            break
    else:
        raise ValueError("bounded replay exhausted")
    return cpu.steps, last_pc, rejected


def check_run(descriptors, payload, expected, *, tapes=None, origins=None, graph=GRAPH):
    if tapes is None:
        tapes, origins = packet(descriptors, payload)
    before = [dict(t.cells) for t in tapes]
    owners = tuple(map(id, tapes))
    shadow = [r.Tape(dict(t.cells), t.head) for t in tapes[:13]]
    old_steps, _, old_rejected = execute(CODE, shadow)
    steps, last_pc, invalid = execute(graph, tapes)
    require(not invalid, "new graph fell through a symbol branch")
    status = "reject" if old_rejected else "accept"
    require(last_pc == HALTS[status], "wrong terminal status")
    require(tuple(map(id, tapes)) == owners, "replaced physical tape owner")
    require(all(t.head == o for t, o in zip(tapes, origins)), "head was not restored")
    for tape in range(3):
        require(tapes[tape].cells == before[tape], "descriptor was modified")
    for tape in range(4, 26):
        require(tapes[tape].cells == before[tape], "private or monitor was not erased")
    want = dict(before[3])
    if expected is not None:
        for j, symbol in enumerate(expected):
            want[origins[3] + j] = symbol
    require(tapes[3].cells == want, "public data or exterior changed incorrectly")
    span = sum(t.local_high - t.local_low + 1 for t in shadow)
    require(steps <= 5 * old_steps + 16 * span + 6 * 13, "simulation time bound")
    require(steps <= 21 * old_steps + 22 * 13, "linear time corollary")
    for i in range(13):
        require(tapes[i].local_low >= shadow[i].local_low - 1, "left cleanup excursion")
        require(tapes[i].local_high <= shadow[i].local_high + 1, "right cleanup excursion")
    return {"status": status, "steps": steps, "source_steps": old_steps,
            "source_span": span}, tapes, origins


def successful_fixtures():
    rows, calls, transitions = [], 0, 0
    for prefix, count, width in itertools.product(range(1, 5), repeat=3):
        volume = prefix * count * width
        if volume > 6:
            continue
        for bits in itertools.product("01", repeat=volume):
            word = "".join(bits)
            expected = "".join(word[(group * count + row) * width + j]
                               for group in range(prefix)
                               for row in reversed(range(count))
                               for j in range(width))
            evidence, _, _ = check_run(tuple(bin(n)[2:] for n in (prefix, count, width)),
                                       word, expected)
            require(evidence["status"] == "accept", "valid packet rejected")
            rows.append(evidence)
            calls += 1
            transitions += evidence["steps"]
    return {"calls": calls, "transitions": transitions,
            "evidence_sha256": digest(rows)}


def malformed_fixtures():
    cases = []
    for tape in range(3):
        for bad in ("", "0", "|", "1|", "10|", "01"):
            descriptors = ["10", "11", "10"]
            descriptors[tape] = bad
            cases.append((tuple(descriptors), "010101010101"))
    for payload in ("", "0", "01010101010", "0101010101010",
                    "|10101010101", "01010|010101", "01010101010|"):
        cases.append((("10", "11", "10"), payload))
    records = []
    for descriptors, payload in cases:
        evidence, _, _ = check_run(descriptors, payload, None)
        require(evidence["status"] == "reject", "malformed packet accepted")
        records.append(evidence)
    return {"calls": len(records), "transitions": sum(x["steps"] for x in records),
            "evidence_sha256": digest(records)}


def reuse_fixture():
    evidence, tapes, origins = check_run(("100", "11", "10"), "0101", None)
    require(evidence["status"] == "reject", "reuse setup must reject")
    prior_history = sum(t.high - t.low + 1 for t in tapes)
    # A caller supplies the next public packet. No private cell or head is reset.
    for i, word in enumerate(("1", "10", "10", "0011")):
        for j in range(32):
            tapes[i].cells.pop(origins[i] + j, None)
        tapes[i].cells.update({origins[i] + j: s for j, s in enumerate(word)})
    after, _, _ = check_run(("1", "10", "10"), "0011", "1100",
                            tapes=tapes, origins=origins)
    require(after["status"] == "accept", "valid call after rejection failed")
    require(sum(t.high - t.low + 1 for t in tapes) >= prior_history,
            "cleanup reset retained history")
    return {"first": evidence, "second": after, "prior_history": prior_history,
            "final_history": sum(t.high - t.low + 1 for t in tapes)}


def generic_fixtures():
    records = []
    for count in range(1, 5):
        for direction in (-1, 1):
            for reject in (False, True):
                code = []
                for tape in range(count):
                    code.extend((("move", tape, direction), ("write", tape, "1"),
                                 ("move", tape, direction), ("write", tape, "0")))
                code.extend((("read", 0, {"1" if reject else "0": len(code) + 1}),
                             ("halt",)))
                private = tuple(range(1, count))
                graph, _, halts = p.compile_tidy(r, tuple(code), ALPHABET, count, private)
                tapes, origins = packet((), "", 2 * count)
                shadow = [r.Tape(dict(t.cells), t.head) for t in tapes[:count]]
                old, _, old_reject = execute(tuple(code), shadow)
                steps, pc, invalid = execute(graph, tapes)
                require(not invalid and old_reject == reject, "generic terminal mismatch")
                require(pc == halts["reject" if reject else "accept"], "generic halt")
                require(tapes[0].cells == shadow[0].cells, "public final state changed")
                for i in range(1, 2 * count):
                    require(tapes[i].cells == {origins[i]-20: "1", origins[i]+10000: "|"},
                            "generic private cleanup")
                require(all(t.head == o for t, o in zip(tapes, origins)), "generic head")
                span = sum(t.high-t.low+1 for t in shadow)
                require(steps <= 5*old + 16*span + 6*count, "generic time bound")
                records.append({"tapes": count, "direction": direction,
                                "rejected": reject, "steps": steps})
    return {"calls": len(records), "evidence_sha256": digest(records)}


def controls():
    caught = []
    # These mutations target the added contract, not predecessor mathematics.
    for name, message, change in (
        ("private_erasure", "private or monitor was not erased", lambda i, op: ("goto", i + 1)
         if op == ("write", 4, "_") and i > HALTS["accept"] else op),
        ("origin_retirement", "private or monitor was not erased", lambda i, op: ("goto", i + 1)
         if op == ("write", 13, "_") and i > HALTS["accept"]
         and GRAPH[i+1][0:2] == ("read", 14) else op),
    ):
        mutant = tuple(change(i, op) for i, op in enumerate(GRAPH))
        try:
            check_run(("10", "11", "10"), "01010", None, graph=mutant)
        except ValueError as error:
            require(str(error) == message, "mutation failed for an unexpected reason")
            caught.append(name)
    for name, code in (
        ("bad_jump", (("goto", 4),)),
        ("long_move", (("move", 0, 2), ("halt",))),
        ("unknown_write", (("write", 0, "x"), ("halt",))),
        ("fallthrough", (("write", 0, "1"),)),
        ("missing_operand", (("read",),)),
        ("nonlocal_opcode", (("callback",),)),
    ):
        try:
            p.compile_tidy(r, code, ALPHABET)
        except ValueError:
            caught.append(name)
    require(len(caught) == 8, "a control survived")
    return caught


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def main():
    if sys.argv[1:] not in ([], ["--record"]):
        raise ValueError("usage: verify.py [--record]")
    result = {"status": "PASS_ROW_REVERSAL_REJECTION_CLEANUP", "tapes": 26,
              "locations": len(GRAPH), "source_locations": len(CODE),
              "success": successful_fixtures(), "rejection": malformed_fixtures(),
              "reuse": reuse_fixture(), "generic": generic_fixtures(),
              "controls": controls(), "pins": p.PINS}
    result["bindings"] = {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                          for name in ("program.py", "verify.py", "PROOF.md", "SOURCES.json")}
    receipt = HERE / "RESULT.json"
    if sys.argv[1:]:
        receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(json.loads(receipt.read_text()) == result, "receipt differs")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
