#!/usr/bin/env python3
"""Source-bound comparison with the concurrent published six-field caller.

Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The concurrent source is parsed as data; its implementation is not executed.
Event counts are literal counts, not a physical cost or minimality theorem.
"""
import ast
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
SOURCE_SHA = "9fb33c8902a2ef8c603c342cc9c32da8d0aad3108df85bf536d77194a6513296"
C = runpy.run_path(str(HERE / "verify_caller.py"))
need = C["need"]


def predecessor_word():
    raw = (HERE / "frozen/concurrent-construct.py").read_bytes()
    need(sha256(raw).hexdigest() == SOURCE_SHA, "Concurrent source SHA256")
    need(C["SOURCE_SHA256"].encode() in raw, "Same retained #6726 interface")
    tree = ast.parse(raw)
    functions = [n for n in tree.body
                 if isinstance(n, ast.FunctionDef) and n.name == "construct"]
    need(len(functions) == 1 and len(functions[0].body) == 1,
         "Unique literal concurrent constructor")
    ret = functions[0].body[0]
    need(isinstance(ret, ast.Return), "Concurrent constructor is literal data")
    normalized = ast.literal_eval(ret.value)
    need(len(normalized) == 13, "Complete concurrent gate inventory")
    events = []
    for gate in normalized:
        if gate[0] in ("QUERY", "NATIVE"):
            dst, src = gate[-2:]
            events.append(["LAMBDA", dst, -1])
            events.append(["QUERY", dst, src, -1] if gate[0] == "QUERY"
                          else ["LOCAL", gate[1], src, dst])
            events.append(["LAMBDA", dst, 1])
        elif gate[0] == "IDLE":
            events.append(["IDLE_ONE", gate[1], gate[2]])
        else:
            need(gate[0] in ("ADD", "SCALE"), "Concurrent ordinary alphabet")
            events.append(list(gate))
    return events


def replay(events, size):
    # Compose elementary maps in the full Gaussian q^4=1 coefficient ring.
    # ADD is the only opcode absent from the new word's smaller interpreter.
    result = C["eye"](size)
    for event in events:
        if event[0] == "ADD":
            _, dst, src, coefficient = event
            elementary = C["eye"](size)
            C["accumulate"](elementary[dst], elementary[src],
                            (Fraction(coefficient), Fraction(0)))
        else:
            elementary = C["execute"]([event], size)
        result = C["compose"](elementary, result)
    return result


def main():
    C["source_binding"]((HERE / "frozen/caller6726.py").read_bytes())
    old = predecessor_word()
    new = C["word"](6)
    four = C["word"](4)
    old_counts = {"LAMBDA": 8, "LOCAL": 2, "QUERY": 2,
                  "ADD": 3, "SCALE": 2, "IDLE_ONE": 4}
    new_counts = {"LAMBDA": 8, "LOCAL": 2, "QUERY": 2,
                  "SCALE": 3, "SWAP": 1, "IDLE_ONE": 4}
    need(dict(Counter(x[0] for x in old)) == old_counts,
         "Concurrent 21-event exact count")
    need(dict(Counter(x[0] for x in new)) == new_counts,
         "New 20-event exact count")
    need(len(old) == 21 and len(new) == 20 and len(four) == 18,
         "Literal event totals")
    old_map, new_map = replay(old, 6), replay(new, 6)
    need(old_map == new_map == C["endpoint"](6),
         "All 36 six-field entries agree in the full q^4 ring")
    need(C["bit_specialization"](old_map) == C["direct_bit_word"](6),
         "Concurrent characteristic-two specialization")
    need(replay(four, 4) == C["endpoint"](4),
         "Explicit four-register variant")

    normalizers = [["LAMBDA", 2, -1], ["LAMBDA", 3, -1]]
    normalized_target = C["endpoint"](6)
    for port in (2, 3):
        normalized_target[port] = C["shifted"](C["eye"](6)[port], q=-1, l=1)
    need(replay(old + normalizers, 6) == normalized_target,
         "Concurrent 23-event auxiliary target normalization")
    need(replay(new + normalizers, 6) == normalized_target,
         "New 22-event auxiliary target normalization")
    normalized_four = C["endpoint"](4)
    for port in (2, 3):
        normalized_four[port] = C["shifted"](C["eye"](4)[port], q=-1, l=1)
    need(replay(four + normalizers, 4) == normalized_four,
         "Four-register 20-event auxiliary target normalization")

    for events in (old, new):
        for omitted in range(2):
            need(replay(events + [normalizers[1 - omitted]], 6)
                 != normalized_target, "Missing auxiliary normalizer rejected")
        phase_fault = [list(e) for e in events]
        next(e for e in phase_fault if e[0] == "QUERY")[-1] = 1
        wrong = replay(phase_fault, 6)
        need(wrong != C["endpoint"](6), "Wrong q exponent rejected")
        need(C["specialize_q_one"](wrong)
             == C["specialize_q_one"](C["endpoint"](6)),
             "The phase negative control would escape q=1 testing")

    print(json.dumps({
        "concurrent_commit": "d87e4a38890f6962162d00a68031ab2476f58f6e",
        "concurrent_source_sha256": SOURCE_SHA,
        "same_source_interface_sha256": C["SOURCE_SHA256"],
        "six_field_events": {"concurrent": len(old), "this_word": len(new)},
        "six_field_normalized_events": {"concurrent": len(old) + 2,
                                         "this_word": len(new) + 2},
        "four_field_events": len(four),
        "four_field_normalized_events": len(four) + 2,
        "concurrent_opcodes": old_counts,
        "this_word_opcodes": new_counts,
        "scope": "Literal event comparison; no physical cost or new kappa"
    }, sort_keys=True))
    print("PASS_SOURCE_BOUND_CONCURRENT_CALLER_COMPARISON")


if __name__ == "__main__":
    main()
