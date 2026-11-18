"""Execute the local two-head reset graph and bind each use to its allocation."""
from fractions import Fraction
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from word import encoded, need
from hashlib import sha256

LEFT, RIGHT = "<", ">"
BLANK = "_"
ALPHABET = "01_:|#<>"
# The two control markers use a separate guide tag. A literal marker inside data is a payload symbol.
ALLOWED = frozenset(ALPHABET)


def bits(value):
    need(value > 0, "positive shape count")
    return [(value >> i) & 1 for i in range(value.bit_length())]


def repetitions(low_first):
    """Read a binary counter from its low end on each decrement."""
    digits = low_first.copy()
    while True:
        i = 0
        while i < len(digits) and digits[i] == 0:
            digits[i] = 1
            i += 1
        if i == len(digits):
            return
        digits[i] = 0
        yield None


def make_guide(rows, axes, width):
    """Emit the complete zero layout using shape parameters alone."""
    need(axes >= 0, "selected axis count")
    component = [("cell", "0") for _ in repetitions(bits(width))]
    record = component + [("cell", ":")] + component + [("cell", "|"), ("cell", BLANK)]
    guide = [("left", None)]
    address_count = [0] * axes + bits(rows)
    for _ in repetitions(address_count):
        guide.extend(record)
    guide.append(("right", None))
    return guide


def graph(action):
    need(action in ("INIT", "CLEAR"), "reset operation")
    table = {("start", "left", None): ("out", None, 1),
             ("out", "right", None): ("back", None, -1),
             ("back", "left", None): ("done", None, 0)}
    for symbol in ALLOWED:
        table["out", "cell", symbol] = ("out", symbol if action == "INIT" else BLANK, 1)
        table["back", "cell", symbol] = ("back", None, -1)
    return table


def run_reset(action, guide, private):
    table = graph(action)
    need(guide is not private, "aliased reset bank")
    gpos = ppos = 0
    state, steps = "start", 0
    while state != "done":
        tag, symbol = guide[gpos]
        state, write, move = table[state, tag, symbol]
        if write is not None:
            private[ppos] = write
        gpos += move
        ppos += move
        steps += 1
    need(gpos == ppos == 0, "reset head return")
    return steps


def plan(word):
    live = {}
    sites = []
    for t, evt in enumerate(word["program"]):
        op, role = evt[:2]
        if op == "INIT":
            need(role >= word["public"] and role not in live, "private lifetime alias")
            ordinal = len(sites)
            sites.append([role, t, evt[2], None, None])
            live[role] = ordinal
        elif op == "CLEAR":
            need(role in live, "unknown private lifetime")
            row = sites[live.pop(role)]
            row[3:] = [t, evt[2]]
    need(not live and all(a[3] is not None for a in sites), "private lifetime not closed")
    return sites


def scaled_bits(value, coefficient):
    a = abs(coefficient.numerator)
    b = coefficient.denominator
    carry = 0
    product_bits = []
    mag = abs(value)
    for j in range(max(1, mag.bit_length()) + a.bit_length() + 1):
        total = carry + a * ((mag >> j) & 1)
        product_bits.append(total & 1)
        carry = total >> 1
    need(carry == 0, "constant product drain")
    remainder = result = 0
    for bit in reversed(product_bits):
        trial = 2 * remainder + bit
        output = int(trial >= b)
        remainder = trial - output * b
        result = 2 * result + output
    need(not remainder, "nonintegral physical division")
    return -result if (value < 0) ^ (coefficient < 0) else result


def verify(word, caller, calls):
    sites = plan(word)
    tags = {(call, ordinal) for call in range(calls) for ordinal in range(len(sites))}
    need(len(tags) == calls * len(sites), "cross-call lifetime alias")
    steps = count = 0
    template = "00:00_00|00#00"
    for body in (template, "", "0", ALPHABET, template * 23):
        guide = [("left", None)] + [("cell", c) for c in body] + [("right", None)]
        for old in ALPHABET:
            private = [LEFT] + [old] * len(body) + [RIGHT]
            for op, expected in (("INIT", list(body)), ("CLEAR", [BLANK] * len(body))):
                number = run_reset(op, guide, private)
                need(private == [LEFT] + expected + [RIGHT] and number == 2 * len(body) + 3, "complete extent")
                steps += number
                count += 1
    # Run every lifetime on a common flat format with a distinct parked ancestor.
    shapes = 0
    for rows in (1, 2, 3):
        for axes in (0, 1, 4):
            for width in (1, 2, 17):
                scientific = "0" * width + ":" + "0" * width + "|_"
                actual = make_guide(rows, axes, width)
                need(actual == [("left", None)] + [("cell", c) for c in scientific * (rows * 2**axes)] + [("right", None)], "shape producer")
                shapes += 1
    guide = make_guide(1, 1, 3)
    payload = "".join(c for _, c in guide[1:-1])
    ancestor = [LEFT] + ["#"] * len(payload) + [RIGHT]
    parked = ancestor.copy()
    homes = {tag: [LEFT] + [ALPHABET[(sum(tag) + j) % len(ALPHABET)] for j in range(len(payload))] + [RIGHT] for tag in tags}
    for stage in range(calls):
        for ordinal, _ in enumerate(sites):
            target = homes[stage, ordinal]
            run_reset("INIT", guide, target)
            need(target[1:-1] == list(payload), "formatted owned zero")
            target[1:-1] = list("1" * len(payload))
            run_reset("CLEAR", guide, target)
    need(all(body == [LEFT] + [BLANK] * len(payload) + [RIGHT] for body in homes.values()) and ancestor == parked, "bank completion")
    short = [LEFT] + ["1"] * len(payload) + [RIGHT]
    run_reset("CLEAR", guide[:-2] + guide[-1:], short)
    need(short[-2] == "1", "short-guide control must leave the last old cell")
    try:
        run_reset("INIT", guide, guide)
    except ValueError:
        pass
    else:
        raise ValueError("alias control escaped")
    scalars = {Fraction(e[-2]) for e in word["program"] if e[0] in ("ADD", "COPY", "SCALE")}
    scalars.update(Fraction(e[-1]) for e in caller["events"] if e[0] != "J" and e[1] in ("ADD", "SCALE"))
    scalars.update(map(Fraction, (225, "1/225", 675, "1/675", "1/2", "-1/2")))
    cases = 0
    for q in sorted(scalars):
        for multiple in (0, -127, -1, 1, 19, 2**67 + 1):
            x = multiple * q.denominator
            need(scaled_bits(x, q) == x * q, "physical signed scalar")
            cases += 1
    try:
        scaled_bits(1, Fraction(-1, 2))
    except ValueError as exc:
        need(str(exc) == "nonintegral physical division", "last-tick countercontrol")
    else:
        raise ValueError("odd half-tick escaped")
    return dict(lifetimes=len(sites), physical_native_homes=len(tags), physical_native_resets=2 * len(tags),
                plan_sha256=sha256(encoded(sites)).hexdigest(), reset_graph_runs=count, shape_cases=shapes,
                reset_steps=steps, signed_scalar_cases=cases, distinct_scalars=len(scalars),
                numerator_bits=max(abs(q.numerator).bit_length() for q in scalars),
                odd_half_tick_rejected=True, extent_control_rejected=True, alias_control_rejected=True)
