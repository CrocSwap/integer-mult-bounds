# SPDX-License-Identifier: Apache-2.0
"""One guarded source, four signed half-ADDs, one restored carry."""

from dataclasses import dataclass

from vendor.kernel import adder

MAX_WIDTH = 256
MAX_GATES = 8192


def need(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Circuit:
    width: int
    shared: bool
    gates: tuple[tuple[int, ...], ...]

    @property
    def wires(self):
        return 5 * self.width + 1


def validate(circuit):
    need(type(circuit.width) is int and 4 <= circuit.width <= MAX_WIDTH, "width")
    need(type(circuit.shared) is bool, "guard policy")
    need(len(circuit.gates) <= MAX_GATES, "gate budget")
    for gate in circuit.gates:
        need(len(gate) in (2, 3), "CX or CCX")
        need(all(type(i) is int and 0 <= i < circuit.wires for i in gate), "wire")
        need(len(set(gate)) == len(gate), "distinct gate wires")


def build(width, shared):
    validate(Circuit(width, shared, ()))
    source = tuple(range(width))
    active = source[1:] + source[:1]
    fill = [(width - 1, 0)]
    gates = list(fill) if shared else []
    for j in range(4):
        target = tuple(range((j + 1) * width, (j + 2) * width))
        adding = list(reversed(adder(active, target, 5 * width)))
        gates.extend(adding if shared else fill + adding + fill)
    if shared:
        gates.extend(fill)
    result = Circuit(width, shared, tuple(gates))
    validate(result)
    return result


def pack(circuit, source, targets):
    validate(circuit)
    need(type(targets) is tuple and len(targets) == 4, "four targets")
    low, high = -(1 << (circuit.width - 1)), 1 << (circuit.width - 1)
    need(type(source) is int and low <= source < high, "source range")
    need(source % 2 == 0, "source guard zero")
    state = source % (1 << circuit.width)
    for j, target in enumerate(targets):
        need(type(target) is int and low <= target < high, "target range")
        need(low <= target - source // 2 < high, "result overflow")
        state |= (target % (1 << circuit.width)) << ((j + 1) * circuit.width)
    return state


def execute(circuit, state):
    validate(circuit)
    need(type(state) is int and 0 <= state < 1 << circuit.wires, "state range")
    for gate in circuit.gates:
        control = (state >> gate[0]) & 1
        if len(gate) == 3:
            control &= (state >> gate[1]) & 1
        state ^= control << gate[-1]
    return state


def observe(circuit, state):
    mask = (1 << circuit.width) - 1
    words = []
    for j in range(5):
        word = (state >> (j * circuit.width)) & mask
        words.append(
            word - (1 << circuit.width) if word >> (circuit.width - 1) else word
        )
    return tuple(words), state >> (5 * circuit.width)


def check(circuit, source, targets):
    after = execute(circuit, pack(circuit, source, targets))
    expected = (source, *(t - source // 2 for t in targets))
    need(
        observe(circuit, after) == (expected, 0),
        "fanout identity and complete clean return",
    )
    return after


def invoice(circuit):
    validate(circuit)
    cx = sum(len(g) == 2 for g in circuit.gates)
    ccx = sum(len(g) == 3 for g in circuit.gates)
    need(cx == 16 * circuit.width - (6 if circuit.shared else 0), "full CNOT count")
    need(ccx == 8 * circuit.width - 8, "full Toffoli count")
    return {"cx": cx, "ccx": ccx, "wires": circuit.wires, "returned_carry_bits": 1}
