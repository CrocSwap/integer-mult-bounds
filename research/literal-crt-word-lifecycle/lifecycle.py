"""Fixed-graph lifecycle for the exact 64-Word current CRT inventory.

Only R/W/M/J/H survive offline compilation. The ordered free stack is an
actual tape; Python lists/sets never select a runtime owner in this graph.
Apache-2.0. Prepared for Jerry Chen / @CubeJerry with OpenAI assistance.
"""
from hashlib import sha256
import json

ALPHABET = ("0", "1", "L", "R", "_")
TEMPLATE, STACK, SOURCE, OUTPUT = 64, 65, 66, 67
TAPES, STACK_EXTENT, SELECTOR_EXTENT = 68, 338, 8


class Builder:
    def __init__(self):
        self.code, self.labels, self.serial = [], {}, 0

    def fresh(self, prefix="q"):
        self.serial += 1
        return f"{prefix}_{self.serial}"

    def mark(self, name):
        if name in self.labels:
            raise ValueError("duplicate state label")
        self.labels[name] = len(self.code)

    def op(self, *instruction):
        self.code.append(instruction)

    def jump(self, target):
        self.op("J", target)

    def read(self, tape, branches, numeric=False):
        self.op("NR" if numeric else "R", tape,
                {s: branches.get(s, "FAIL") for s in ALPHABET})

    def expect(self, tape, symbol, numeric=False):
        done = self.fresh("expected")
        self.read(tape, {symbol: done}, numeric)
        self.mark(done)

    def move(self, tape, direction, numeric=False):
        self.op("NM" if numeric else "M", tape, direction)

    def write(self, tape, symbol, numeric=False):
        self.op("NW" if numeric else "W", tape, symbol)

    def rewind(self, tape, numeric=False, word=False):
        if word:
            self.move(tape, -1, numeric)
        loop, back, done = (self.fresh(x) for x in ("rewind", "back", "origin"))
        self.mark(loop)
        self.read(tape, {s: done if s == "L" else back for s in ALPHABET}, numeric)
        self.mark(back)
        self.move(tape, -1, numeric)
        self.jump(loop)
        self.mark(done)
        if word:
            self.move(tape, 1, numeric)

    def finish(self):
        result = []
        for op, *args in self.code:
            if op in ("R", "NR"):
                result.append((op, args[0], {s: self.labels[t] for s, t in args[1].items()}))
            elif op == "J":
                result.append((op, self.labels[args[0]]))
            else:
                result.append((op, *args))
        return tuple(result), dict(self.labels)


def blank_selector(b, tape):
    for i in range(8):
        b.expect(tape, "_")
        if i != 7:
            b.move(tape, 1)
    for _ in range(7):
        b.move(tape, -1)


def set_selector(b, tape, slot):
    for i, symbol in enumerate(("L", *(str((slot >> j) & 1) for j in range(6)), "R")):
        b.expect(tape, "_")
        b.write(tape, symbol)
        if i != 7:
            b.move(tape, 1)
    for _ in range(7):
        b.move(tape, -1)


def clear_selector(b, tape):
    b.expect(tape, "L")
    b.write(tape, "_")
    b.move(tape, 1)
    for _ in range(6):
        digit = b.fresh("selector_digit")
        b.read(tape, {"0": digit, "1": digit})
        b.mark(digit)
        b.write(tape, "_")
        b.move(tape, 1)
    b.expect(tape, "R")
    b.write(tape, "_")
    for _ in range(7):
        b.move(tape, -1)


def decode(b, tape, prefix, destinations):
    b.expect(tape, "L")
    b.move(tape, 1)
    b.jump(prefix + "_0_0")
    for depth in range(6):
        for value in range(1 << depth):
            b.mark(f"{prefix}_{depth}_{value}")
            targets = {str(bit): b.fresh("decode_bit") for bit in (0, 1)}
            b.read(tape, targets)
            for bit in (0, 1):
                b.mark(targets[str(bit)])
                b.move(tape, 1)
                b.jump(f"{prefix}_{depth + 1}_{value + (bit << depth)}")
    for slot in range(64):
        b.mark(f"{prefix}_6_{slot}")
        b.expect(tape, "R")
        for _ in range(7):
            b.move(tape, -1)
        b.jump(destinations[slot])


def membership(b, prefix, found, absent):
    """Compare every six-bit stack entry to SOURCE, leaving STACK at match/end."""
    loop = prefix + "_next"
    b.expect(STACK, "L")
    b.move(STACK, 1)
    b.mark(loop)
    start = b.fresh("record")
    b.read(STACK, {"0": start, "1": start, "R": absent})
    b.mark(start)
    b.expect(SOURCE, "L")
    b.move(SOURCE, 1)
    b.jump(prefix + "_0_1")
    for j in range(6):
        for equal in (0, 1):
            b.mark(f"{prefix}_{j}_{equal}")
            left = {str(x): b.fresh("stack_bit") for x in (0, 1)}
            b.read(STACK, left)
            for x in (0, 1):
                b.mark(left[str(x)])
                right = {str(y): b.fresh("request_bit") for y in (0, 1)}
                b.read(SOURCE, right)
                for y in (0, 1):
                    b.mark(right[str(y)])
                    b.move(STACK, 1)
                    b.move(SOURCE, 1)
                    b.jump(f"{prefix}_{j + 1}_{int(equal and x == y)}")
    for equal in (0, 1):
        b.mark(f"{prefix}_6_{equal}")
        b.expect(SOURCE, "R")
        for _ in range(7):
            b.move(SOURCE, -1)
        b.jump(found if equal else loop)


def pop(b, prefix, continuation):
    """Pop exact top slot and encode it in OUTPUT. Initial STACK head is zero."""
    scan, step, end, nonempty = (b.fresh(x) for x in ("scan", "step", "end", "nonempty"))
    b.expect(STACK, "L")
    b.move(STACK, 1)
    b.mark(scan)
    b.read(STACK, {"0": step, "1": step, "R": end})
    b.mark(step)
    b.move(STACK, 1)
    b.jump(scan)
    b.mark(end)
    b.move(STACK, -1)
    b.read(STACK, {"0": nonempty, "1": nonempty, "L": "EMPTY"})
    b.mark(nonempty)
    b.move(STACK, 1)
    b.write(STACK, "_")
    b.move(STACK, -1)
    b.jump(prefix + "_0_0")
    for depth in range(6):
        for value in range(1 << depth):
            b.mark(f"{prefix}_{depth}_{value}")
            targets = {str(bit): b.fresh("top_bit") for bit in (0, 1)}
            b.read(STACK, targets)
            for bit in (0, 1):
                b.mark(targets[str(bit)])
                b.write(STACK, "_")
                if depth != 5:
                    b.move(STACK, -1)
                b.jump(f"{prefix}_{depth + 1}_{2 * value + bit}")
    for slot in range(64):
        b.mark(f"{prefix}_6_{slot}")
        if slot < 8:
            b.jump("FAIL")
            continue
        b.write(STACK, "R")
        b.rewind(STACK)
        set_selector(b, OUTPUT, slot)
        b.jump(continuation)


def left_guard(b, role, numeric=False):
    b.move(role, -1, numeric)
    b.expect(role, "L", numeric)
    b.move(role, 1, numeric)


def logical_graph():
    b = Builder()
    entries = ("INIT", "TAKE", "ZERO", "COPY", "FREE", "IS_LIVE", "CLOSE")
    b.mark("INIT")
    for tape, extent in ((STACK, 338), (SOURCE, 8), (OUTPUT, 8)):
        for i in range(extent):
            b.write(tape, "_")
            if i + 1 < extent:
                b.move(tape, 1)
        for _ in range(extent - 1):
            b.move(tape, -1)
    b.write(STACK, "L")
    b.move(STACK, 1)
    for slot in reversed(range(8, 64)):
        for j in range(6):
            b.write(STACK, str((slot >> j) & 1))
            b.move(STACK, 1)
    b.write(STACK, "R")
    b.rewind(STACK)
    b.op("H", "READY")
    for slot in range(64):
        b.mark(f"SET_{slot}")
        set_selector(b, SOURCE, slot)
        b.op("H", "BOUND")

    b.mark("CLOSE")
    blank_selector(b, SOURCE)
    blank_selector(b, OUTPUT)
    b.expect(STACK, "L")
    b.write(STACK, "_")
    b.move(STACK, 1)
    for _ in range(336):
        digit = b.fresh("close_digit")
        b.read(STACK, {"0": digit, "1": digit})
        b.mark(digit)
        b.write(STACK, "_")
        b.move(STACK, 1)
    b.expect(STACK, "R")
    b.write(STACK, "_")
    for _ in range(337):
        b.move(STACK, -1)
    b.op("H", "RETIRED")

    for entry, body in (("TAKE", "RETURN_PLAIN"), ("ZERO", "ZERO_BODY")):
        b.mark(entry)
        blank_selector(b, SOURCE)
        blank_selector(b, OUTPUT)
        pop(b, entry + "_POP", body)

    b.mark("ZERO_BODY")
    left_guard(b, TEMPLATE)
    left_guard(b, 1, True)
    b.jump("ZERO_0")
    for progress in range(5):
        b.mark(f"ZERO_{progress}")
        digit = b.fresh("zero_digit")
        b.read(TEMPLATE, {"0": digit, **({"R": "ZERO_END"} if progress == 4 else {})})
        b.mark(digit)
        b.expect(1, "_", True)
        b.write(1, "0", True)
        b.move(1, 1, True)
        b.move(TEMPLATE, 1)
        b.jump(f"ZERO_{min(4, progress + 1)}")
    b.mark("ZERO_END")
    b.expect(1, "_", True)
    b.write(1, "R", True)
    b.rewind(1, True, True)
    b.rewind(TEMPLATE, False, True)
    b.jump("RETURN_PLAIN")

    b.mark("COPY")
    blank_selector(b, OUTPUT)
    decode(b, SOURCE, "COPY_HANDLE", ["COPY_MEMBERSHIP"] * 64)
    b.mark("COPY_MEMBERSHIP")
    membership(b, "COPY_MEMBER", "FAIL", "COPY_ABSENT")
    b.mark("COPY_ABSENT")
    b.rewind(STACK)
    pop(b, "COPY_POP", "COPY_BODY")
    b.mark("COPY_BODY")
    left_guard(b, 0, True)
    left_guard(b, 1, True)
    b.jump("COPY_0")
    for progress in range(5):
        b.mark(f"COPY_{progress}")
        digits = {str(x): b.fresh("copy_digit") for x in (0, 1)}
        b.read(0, {**digits, **({"R": "COPY_END"} if progress == 4 else {})}, True)
        for x in (0, 1):
            b.mark(digits[str(x)])
            b.expect(1, "_", True)
            b.write(1, str(x), True)
            b.move(0, 1, True)
            b.move(1, 1, True)
            b.jump(f"COPY_{min(4, progress + 1)}")
    b.mark("COPY_END")
    b.expect(1, "_", True)
    b.write(1, "R", True)
    b.rewind(0, True, True)
    b.rewind(1, True, True)
    b.jump("RETURN_COPY")

    b.mark("FREE")
    blank_selector(b, OUTPUT)
    decode(b, SOURCE, "FREE_HANDLE", ["FAIL"] * 8 + ["FREE_MEMBERSHIP"] * 56)
    b.mark("FREE_MEMBERSHIP")
    membership(b, "FREE_MEMBER", "FAIL", "FREE_BODY")
    b.mark("FREE_BODY")
    left_guard(b, 0, True)
    b.jump("FREE_0")
    for progress in range(5):
        b.mark(f"FREE_{progress}")
        digit = b.fresh("erase_digit")
        b.read(0, {"0": digit, "1": digit, **({"R": "FREE_END"} if progress == 4 else {})}, True)
        b.mark(digit)
        b.write(0, "_", True)
        b.move(0, 1, True)
        b.jump(f"FREE_{min(4, progress + 1)}")
    b.mark("FREE_END")
    b.write(0, "_", True)
    b.rewind(0, True, True)
    b.expect(SOURCE, "L")
    b.move(SOURCE, 1)
    for j in range(6):
        if j:
            b.expect(STACK, "_")
        bits = {str(x): b.fresh("push_bit") for x in (0, 1)}
        after = b.fresh("pushed_bit")
        b.read(SOURCE, bits)
        for x in (0, 1):
            b.mark(bits[str(x)])
            b.write(STACK, str(x))
            b.jump(after)
        b.mark(after)
        b.move(STACK, 1)
        b.move(SOURCE, 1)
    b.expect(STACK, "_")
    b.write(STACK, "R")
    b.expect(SOURCE, "R")
    for _ in range(7):
        b.move(SOURCE, -1)
    b.rewind(STACK)
    clear_selector(b, SOURCE)
    b.op("H", "FREED")

    b.mark("IS_LIVE")
    blank_selector(b, OUTPUT)
    decode(b, SOURCE, "LIVE_HANDLE", ["LIVE_MEMBERSHIP"] * 64)
    b.mark("LIVE_MEMBERSHIP")
    membership(b, "LIVE_MEMBER", "IS_FREE", "IS_PRESENT")
    for label, result in (("IS_FREE", "FREE"), ("IS_PRESENT", "LIVE")):
        b.mark(label)
        b.rewind(STACK)
        clear_selector(b, SOURCE)
        b.op("H", result)

    for entry, with_source in (("RETURN_PLAIN", False), ("RETURN_COPY", True)):
        b.mark(entry)
        targets = [b.fresh("allocated") for _ in range(64)]
        decode(b, OUTPUT, entry + "_HANDLE", targets)
        for slot, target in enumerate(targets):
            b.mark(target)
            if slot < 8:
                b.jump("FAIL")
                continue
            clear_selector(b, OUTPUT)
            if with_source:
                clear_selector(b, SOURCE)
            b.op("H", f"ALLOC_{slot}")
    b.mark("EMPTY")
    b.op("H", "EXHAUSTED")
    b.mark("FAIL")
    b.op("H", "MALFORMED")
    code, labels = b.finish()
    return code, labels, entries


def dispatch(b, row, pc):
    op, role, value = row
    selector = SOURCE if role == 0 else OUTPUT
    destinations = [b.fresh("selected_port") for _ in range(64)]
    decode(b, selector, b.fresh("dispatch"), destinations)
    for slot, label in enumerate(destinations):
        b.mark(label)
        if op == "NR":
            b.read(slot, {s: f"CORE_{target}" for s, target in value.items()})
        else:
            b.op(op[1:], slot, value)
            b.jump(f"CORE_{pc + 1}")


def compile_program():
    logical, logical_labels, entry_names = logical_graph()
    b = Builder()
    for pc, row in enumerate(logical):
        b.mark(f"CORE_{pc}")
        op, *args = row
        if op in ("NR", "NW", "NM"):
            dispatch(b, row, pc)
        elif op == "R":
            b.read(args[0], {s: f"CORE_{target}" for s, target in args[1].items()})
        elif op == "J":
            b.jump(f"CORE_{args[0]}")
        else:
            b.op(op, *args)
    b.mark("FAIL")
    b.op("H", "MALFORMED")
    code, labels = b.finish()
    entries = {name: labels[f"CORE_{logical_labels[name]}"] for name in entry_names}
    setters = [labels[f"CORE_{logical_labels[f'SET_{slot}']}"] for slot in range(64)]
    metadata = {
        "tapes": TAPES, "stack_extent": STACK_EXTENT, "selector_extent": SELECTOR_EXTENT,
        "locations": len(code), "logical_locations": len(logical),
        "entries": entries, "setters": setters,
        "logical_to_physical": [labels[f"CORE_{i}"] for i in range(len(logical))],
    }
    return code, metadata


def digest(code):
    return sha256(json.dumps(code, separators=(",", ":"), sort_keys=True).encode()).hexdigest()
