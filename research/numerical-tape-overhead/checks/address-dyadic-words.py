#!/usr/bin/env python3
"""Fixed multitape arithmetic on arbitrary equally padded binary magnitudes."""
import argparse
from math import isqrt
from pathlib import Path
from random import Random
from runpy import run_path

tm = run_path(str(Path(__file__).with_name("node-tapes.py")))
Builder, Action = tm["Builder"], tm["Action"]
BLANK, HOME, HALT = tm["BLANK"], tm["HOME"], tm["HALT"]
END = "$"
DIGITS = ("0", "1")


def compile_word(operation):
    b = Builder()

    def home(tape, target):
        state = b.label("return to left delimiter")
        return b.sel(state, tape, {HOME: Action(target)},
                     Action(state, moves=((tape, -1),)))

    def reset(tapes, target):
        for tape in reversed(tapes):
            target = b.rewind(tape, target)
        return target

    def clear(tape, target):
        back, out = b.label("erase right to left"), b.label("seek current end")
        b.sel(back, tape, {HOME: Action(target, ((tape, BLANK),))},
              Action(back, ((tape, BLANK),), ((tape, -1),)))
        return b.sel(out, tape, {END: Action(back, ((tape, BLANK),), ((tape, -1),))},
                     Action(out, moves=((tape, 1),)))

    def shift(tape, incoming, target):
        states = [b.label("shift left and insert low bit") for _ in range(2)]
        done = b.rewind(tape, target)
        for carry, state in enumerate(states):
            cases = {END: Action(done)}
            for old, symbol in enumerate(DIGITS):
                cases[symbol] = Action(states[old], ((tape, str(carry)),), ((tape, 1),))
            b.sel(state, tape, cases)
        return states[incoming]

    def copy(src, dst, target):
        state = b.label("copy equally padded word")
        done = reset((src, dst), target)
        cases = {END: Action(done)}
        for symbol in DIGITS:
            cases[symbol] = Action(state, ((dst, symbol),), ((src, 1), (dst, 1)))
        return b.sel(state, src, cases)

    def accumulate(src, dst, subtract, target):
        states = [b.label("read source of add/subtract") for _ in range(2)]
        done = reset((src, dst), target)
        for carry, state in enumerate(states):
            cases = {END: Action(done)}
            for a, first in enumerate(DIGITS):
                joint = b.label("ripple destination bit")
                cases[first] = Action(joint)
                branches = {}
                for v, old in enumerate(DIGITS):
                    raw = v-a-carry if subtract else v+a+carry
                    next_carry = int(raw < 0) if subtract else raw//2
                    branches[old] = Action(states[next_carry], ((dst, str(raw % 2)),),
                                           ((src, 1), (dst, 1)))
                b.sel(joint, dst, branches)
            b.sel(state, src, cases)
        return states[0]

    def compare(x, y, ge, lt):
        states = {r: b.label("read first comparison bit") for r in (-1, 0, 1)}
        done_ge, done_lt = reset((x, y), ge), reset((x, y), lt)
        for relation, state in states.items():
            cases = {END: Action(done_ge if relation >= 0 else done_lt)}
            for a, symbol in enumerate(DIGITS):
                joint = b.label("higher differing bit controls comparison")
                cases[symbol] = Action(joint)
                branches = {}
                for v, second in enumerate(DIGITS):
                    next_relation = relation if a == v else (1 if a > v else -1)
                    branches[second] = Action(states[next_relation], moves=((x, 1), (y, 1)))
                b.sel(joint, y, branches)
            b.sel(state, x, cases)
        return states[0]

    uses_b = operation != "sqrt"
    tapes = ("A", "B", "O", "R", "T") if uses_b else ("A", "O", "R", "T")
    finish = clear("R", clear("T", home("O", HALT)))
    if uses_b:
        finish = home("B", finish)
    finish = home("A", finish)
    outer = b.label("read next multiplier, dividend or radicand digit")
    odd_start = outer

    if operation == "multiply":
        doubler = shift("T", 0, outer)
        add = accumulate("T", "O", False, doubler)
        b.sel(outer, "B", {END: Action(finish), "0": Action(doubler, moves=(("B", 1),)),
                           "1": Action(add, moves=(("B", 1),))})
    elif operation == "divide":
        yes = accumulate("B", "R", True, shift("O", 1, outer))
        no = shift("O", 0, outer)
        trial = compare("R", "B", yes, no)
        b.sel(outer, "A", {HOME: Action(finish),
                           **{s: Action(shift("R", a, trial), moves=(("A", -1),))
                              for a, s in enumerate(DIGITS)}})
    elif operation == "sqrt":
        yes = accumulate("T", "R", True, shift("O", 1, outer))
        no = shift("O", 0, outer)
        test = compare("R", "T", yes, no)
        trial = copy("O", "T", shift("T", 0, shift("T", 1, test)))
        second = [b.label("second radix-four digit bit") for _ in range(2)]
        for u, state in enumerate(second):
            cases = {}
            for v, symbol in enumerate(DIGITS):
                start = shift("R", u, shift("R", v, trial))
                cases[symbol] = Action(start, moves=(("A", -1),))
            b.sel(state, "A", cases)
        b.sel(outer, "A", {HOME: Action(finish),
                           **{s: Action(second[a], moves=(("A", -1),))
                              for a, s in enumerate(DIGITS)}})
        odd_start = second[0]
    else:
        raise ValueError(operation)

    # Allocate the three writable words in parallel, tracking input width parity.
    init = [b.label("allocate common operand width") for _ in range(2)]
    for parity, state in enumerate(init):
        first = odd_start if parity else outer
        if operation != "multiply":
            first = b.op(first, moves=(("A", -1),), name="start at most significant bit")
        first = reset(("O", "R", "T"), first)
        cases = {END: Action(first, tuple((t, END) for t in ("O", "R", "T")))}
        for symbol in DIGITS:
            writes = (("O", "0"), ("R", "0"), ("T", symbol if operation == "multiply" else "0"))
            cases[symbol] = Action(init[1-parity], writes, tuple((t, 1) for t in "AORT"))
        b.sel(state, "A", cases)
    start = b.op(init[0], tuple((t, HOME) for t in "ORT"), tuple((t, 1) for t in tapes),
                 "enter immutable inputs and make scratch left delimiters")
    return b, tapes, start


def encode(value, width):
    return HOME + format(value, f"0{width}b")[::-1] + END


def exercise(machine, operation, w, a, b=1):
    init = {"A": encode(a, w)}
    if operation != "sqrt":
        init["B"] = encode(b, w)
    sim = tm["Simulation"](machine, init).execute(256*(w+2)**2)
    if operation == "multiply":
        expected = a*b % (1<<w)
    elif operation == "divide":
        expected = a//b
    else:
        expected = isqrt(a)
    assert sim.tape["O"] == dict(enumerate(encode(expected, w)))
    for c, s in init.items():
        assert sim.tape[c] == dict(enumerate(s))
    assert not sim.tape["T"] and not sim.tape["R"]
    assert all(pos == 0 for pos in sim.head.values())
    assert sim.visited <= len(machine[1])*(w+2)
    return sim.steps


def main(extended):
    rng = Random(11939)
    for operation in ("multiply", "divide", "sqrt"):
        compiled = compile_word(operation)
        checked = maximum = 0
        for w in range(1, 6 if extended else 5):
            for a in range(1<<w):
                bs = (1,) if operation == "sqrt" else range(1 if operation == "divide" else 0, 1<<w)
                for b in bs:
                    maximum = max(maximum, exercise(compiled, operation, w, a, b))
                    checked += 1
        widths = (6, 7, 9, 16, 31, 32, 63, 64) if extended else (6, 7, 9, 16)
        for w in widths:
            for _ in range(12 if extended else 3):
                a = rng.getrandbits(w)
                b = max(1, rng.getrandbits(w))
                maximum = max(maximum, exercise(compiled, operation, w, a, b))
                checked += 1
        print(operation, "states", len(compiled[0].rules), "tapes", len(compiled[1]),
              "cases", checked, "maximum transitions", maximum)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--extended", action="store_true")
    main(parser.parse_args().extended)
