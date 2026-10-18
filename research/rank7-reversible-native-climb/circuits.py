# SPDX-License-Identifier: Apache-2.0
"""Literal, bounded Boolean execution of one in-place Gaussian C lift."""

from collections import Counter
from fractions import Fraction as Q

import caller

MAX_WIDTH = 256
MAX_FIELDS = 2048
MAX_MACROS = 12_000
MAX_GATES = 8_000_000
MAX_TRUTH_COLUMNS = 262_144


def require(condition, message):
    if not condition:
        raise ValueError(message)


def lift(sign=1, control=False):
    """Four real fields a,b,c,d, with even a-c and b-d on the input grid."""
    require(type(sign) is int and sign in (-1, 1), "C sign")
    program = [("add", 0, 2, -1, 1), ("add", 1, 3, -1, 1)]
    if control:
        program += [("half", 0), ("half", 1)]
    denominator = 1 if control else 2
    program += [("add", 2, 0, 1, denominator), ("add", 3, 1, 1, denominator)]
    program += [("swap", 0, 1), ("neg", 0 if sign == 1 else 1)]
    program += [("add", 2, 0, -1, denominator), ("add", 3, 1, -1, denominator)]
    if control:
        program += [("double", 0), ("double", 1)]
    return program + [("add", 0, 2, 1, 1), ("add", 1, 3, 1, 1)]


def primitive(width, instruction):
    """Return local wires (target=0, source=1, carry=2) and their global banks."""
    require(type(width) is int and 3 <= width <= MAX_WIDTH, "bounded width")
    banks = instruction_banks(instruction)
    kind, target = instruction[:2]
    if kind == "add":
        _, _, source, a, b = instruction
        require(a in (-1, 1) and b in (1, 2), "unit or half-unit ADD")
        gates = caller.add(width, 0, 1, a, b)
    elif kind == "neg":
        gates = caller.negate(width, 0)
    elif kind in ("half", "double"):
        gates = caller.shift(width, 0, kind == "half")
    else:
        require(kind == "swap" and len(instruction) == 3, "scalar SWAP")
        gates = [g for i in range(width) for g in caller.swap((0, i), (1, i))]
    remapped = []
    for gate in gates:
        ports = tuple((2 if b == 3 else b, i) for b, i in gate[1:])
        require(all(b in (0, 1, 2) for b, _ in ports), "local wire banks")
        require(len(set(ports)) == len(ports), "distinct Boolean ports")
        remapped.append((gate[0], *ports))
    return remapped, banks


def semantic(values, instruction, width):
    """Check every arithmetic cut; source divisibility is checked before ADD."""
    kind, target = instruction[:2]
    limit = 1 << (width - 1)
    touched = [target]
    if kind == "swap":
        source = instruction[2]
        values[target], values[source] = values[source], values[target]
        touched.append(source)
    elif kind == "add":
        source, a, b = instruction[2:]
        require(values[source] % b == 0, "half-source alignment")
        values[target] += a * (values[source] // b)
        touched.append(source)
    elif kind == "neg":
        values[target] = -values[target]
    elif kind == "half":
        require(values[target] % 2 == 0, "physical HALF alignment")
        values[target] //= 2
    else:
        require(kind == "double", "supported arithmetic instruction")
        values[target] *= 2
    require(all(-limit <= values[b] < limit for b in touched), "signed microstate")


def apply_words(gates, words, width):
    """A second-level Boolean interpreter, independent of rational semantics."""
    state = list(words)
    require(len(state) == 3 and state[2] == 0, "owned clean carry bank")
    for gate in gates:
        bank, bit = gate[1]
        control = (state[bank] >> bit) & 1
        if gate[0] == "ccx":
            bank, bit = gate[2]
            control &= (state[bank] >> bit) & 1
        bank, bit = gate[-1]
        state[bank] ^= control << bit
    require(state[2] == 0, "carry return")
    require(all(0 <= v < 1 << width for v in state[:2]), "Boolean word range")
    return state


def run(values, program, width, *, bits=True):
    require(type(width) is int and 3 <= width <= MAX_WIDTH, "bounded width")
    require(1 <= len(values) <= MAX_FIELDS, "bounded field inventory")
    require(len(program) <= MAX_MACROS, "bounded macro program")
    require(all(type(v) is int for v in values), "encoded integer fields")
    limit, mask = 1 << (width - 1), (1 << width) - 1
    require(all(-limit <= v < limit for v in values), "signed entrance")
    state, cache, total = list(values), {}, 0
    for instruction in program:
        banks = instruction_banks(instruction)
        key = (instruction[0], *instruction[3:])
        if key not in cache:
            cache[key] = primitive(width, instruction)[0]
        gates = cache[key]
        require(all(b < len(state) for b in banks), "owned program field")
        words = [state[b] & mask for b in banks]
        words += [0] * (3 - len(words))
        semantic(state, instruction, width)
        total += len(gates)
        require(total <= MAX_GATES, "bounded executed gate count")
        if bits:
            observed = apply_words(gates, words, width)
            require(
                all(observed[i] == state[b] & mask for i, b in enumerate(banks)),
                "literal arithmetic endpoint",
            )
    return state


def instruction_banks(instruction):
    require(
        isinstance(instruction, (tuple, list)) and 2 <= len(instruction) <= 5,
        "bounded instruction shape",
    )
    kind, target = instruction[:2]
    require(kind in ("add", "swap", "neg", "half", "double"), "supported instruction")
    require(
        len(instruction) == (5 if kind == "add" else 3 if kind == "swap" else 2),
        "instruction arity",
    )
    banks = (target, instruction[2]) if kind in ("add", "swap") else (target,)
    require(all(type(b) is int and 0 <= b < MAX_FIELDS for b in banks), "field index")
    require(len(set(banks)) == len(banks), "distinct owned fields")
    if kind == "add":
        require(
            all(type(q) is int for q in instruction[3:])
            and instruction[3] in (-1, 1)
            and instruction[4] in (1, 2),
            "unit or half-unit ADD",
        )
    return banks


def pair_gates(width, sign=1, control=False):
    gates = []
    for instruction in lift(sign, control):
        local, banks = primitive(width, instruction)
        for gate in local:
            ports = tuple(
                ((4 if b == 2 else banks[b]) * width + i) for b, i in gate[1:]
            )
            gates.append((gate[0], *ports))
    require(len(gates) <= 100_000, "bounded C-pair circuit")
    return gates


def packed(gates, columns, width):
    require(type(width) is int and 3 <= width <= MAX_WIDTH, "bounded width")
    require(len(columns) == 5 * width - 1, "complete packed field/carry inventory")
    require(len(gates) <= 100_000, "bounded packed circuit")
    require(
        all(
            type(c) is int and c >= 0 and c.bit_length() <= MAX_TRUTH_COLUMNS
            for c in columns
        ),
        "bounded packed truth columns",
    )
    state = list(columns)
    for gate in gates:
        require(
            gate[0] in ("cx", "ccx") and len(gate) == (3 if gate[0] == "cx" else 4),
            "packed gate arity",
        )
        require(
            len(set(gate[1:])) == len(gate) - 1
            and all(type(i) is int and 0 <= i < len(state) for i in gate[1:]),
            "owned distinct packed ports",
        )
        control = state[gate[1]]
        if gate[0] == "ccx":
            control &= state[gate[2]]
        state[gate[-1]] ^= control
    return state


def tariff(program, width):
    require(len(program) <= MAX_MACROS, "bounded tariff program")
    count, cache = Counter(), {}
    for instruction in program:
        instruction_banks(instruction)
        key = (instruction[0], *instruction[3:])
        if key not in cache:
            cache[key] = Counter(g[0] for g in primitive(width, instruction)[0])
        count.update(cache[key])
    require(sum(count.values()) <= MAX_GATES, "bounded literal tariff")
    return dict(sorted(count.items()))


def rational_lift(sign, control=False):
    """Exact four-column microstate rows, without using the bit interpreter."""
    rows = [[Q(i == j) for j in range(4)] for i in range(4)]
    trace = []
    for instruction in lift(sign, control):
        kind, target = instruction[:2]
        if kind == "add":
            source, a, b = instruction[2:]
            rows[target] = [
                x + Q(a, b) * y for x, y in zip(rows[target], rows[source], strict=True)
            ]
        elif kind == "swap":
            source = instruction[2]
            rows[target], rows[source] = rows[source], rows[target]
        else:
            factor = {"neg": -1, "half": Q(1, 2), "double": 2}[kind]
            rows[target] = [factor * x for x in rows[target]]
        trace.append([list(row) for row in rows])
    return rows, trace
