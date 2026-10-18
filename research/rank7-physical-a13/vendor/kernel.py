# SPDX-License-Identifier: Apache-2.0
"""Literal reversible bit gates for a guarded signed dyadic ADD."""

from dataclasses import dataclass

MAX_WIDTH = 256
MAX_SHIFT = 3
MAX_GATES = 8192
Gate = tuple[int, ...]  # CX(control, target), CCX(control, control, target)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Circuit:
    width: int
    shift: int
    sign: int
    policy: str
    gates: tuple[Gate, ...]

    @property
    def wires(self) -> int:
        return (3 if self.policy == "scratch" else 2) * self.width + 1


def swap(a: int, b: int) -> list[Gate]:
    return [(a, b), (b, a), (a, b)]


def signed_half(bits: tuple[int, ...]) -> list[Gate]:
    """Arithmetic right shift on the subspace with a zero low bit."""
    gates: list[Gate] = []
    for i in range(len(bits) - 1):
        gates.extend(swap(bits[i], bits[i + 1]))
    gates.append((bits[-2], bits[-1]))
    return gates


def adder(source: tuple[int, ...], target: tuple[int, ...], carry: int) -> list[Gate]:
    """Cuccaro-style MAJ/UMA, modulo 2**width, with one restored carry."""
    width = len(source)
    require(2 <= width <= MAX_WIDTH and len(target) == width, "adder widths")
    require(len({*source, *target, carry}) == 2 * width + 1, "disjoint wires")
    gates: list[Gate] = []
    for i in range(width - 1):
        a, b, c = source[i], target[i], carry if i == 0 else source[i - 1]
        gates.extend(((a, c), (a, b), (b, c, a)))
    gates.extend(((source[-1], target[-1]), (source[-2], target[-1])))
    for i in reversed(range(width - 1)):
        a, b, c = source[i], target[i], carry if i == 0 else source[i - 1]
        gates.extend(((b, c, a), (a, c), (c, b)))
    return gates


def validate(circuit: Circuit) -> None:
    require(type(circuit.width) is int and 4 <= circuit.width <= MAX_WIDTH, "width")
    require(type(circuit.shift) is int and 1 <= circuit.shift <= MAX_SHIFT, "shift")
    require(circuit.shift < circuit.width, "shift below width")
    require(type(circuit.sign) is int and circuit.sign in (-1, 1), "sign")
    require(circuit.policy in ("source", "scratch", "wired"), "policy")
    require(len(circuit.gates) <= MAX_GATES, "gate budget")
    for gate in circuit.gates:
        require(len(gate) in (2, 3), "CX or CCX")
        require(all(type(i) is int and 0 <= i < circuit.wires for i in gate), "wire")
        require(len(set(gate)) == len(gate), "distinct gate wires")


def build(width: int, shift: int, sign: int, policy: str) -> Circuit:
    validate(Circuit(width, shift, sign, policy, ()))
    source = tuple(range(width))
    target = tuple(range(width, 2 * width))
    active = tuple(range(2 * width, 3 * width)) if policy == "scratch" else source
    carry = (3 if policy == "scratch" else 2) * width
    copying = (
        [(s, a) for s, a in zip(source, active, strict=True)]
        if policy == "scratch"
        else []
    )
    shifting = signed_half(active) * shift
    if policy == "wired":
        # Guard bits become explicit sign-extension wires, then return to zero.
        active = source[shift:] + source[:shift]
        shifting = [(source[-1], source[i]) for i in range(shift)]
    adding = adder(active, target, carry)
    if sign == -1:
        adding.reverse()
    gates = copying + shifting + adding + list(reversed(shifting)) + copying
    result = Circuit(width, shift, sign, policy, tuple(gates))
    validate(result)
    return result


def signed(value: int, width: int) -> int:
    return value - (1 << width) if value >> (width - 1) else value


def pack(circuit: Circuit, source: int, target: int) -> int:
    """Checked caller boundary. Values are encoded integers on one common grid."""
    validate(circuit)
    low, high = -(1 << (circuit.width - 1)), 1 << (circuit.width - 1)
    require(type(source) is int and low <= source < high, "signed source range")
    require(type(target) is int and low <= target < high, "signed target range")
    require(source % (1 << circuit.shift) == 0, "fractional guard zeros")
    require(
        low <= target + circuit.sign * (source >> circuit.shift) < high,
        "signed result overflow",
    )
    mask = (1 << circuit.width) - 1
    return (source & mask) | ((target & mask) << circuit.width)


def execute(circuit: Circuit, state: int) -> int:
    """Bit-packed gate interpreter; deliberately has no arithmetic ADD operation."""
    validate(circuit)
    require(type(state) is int and 0 <= state < (1 << circuit.wires), "state range")
    for gate in circuit.gates:
        control = (state >> gate[0]) & 1
        if len(gate) == 3:
            control &= (state >> gate[1]) & 1
        state ^= control << gate[-1]
    return state


def check(circuit: Circuit, source: int, target: int) -> int:
    before = pack(circuit, source, target)
    after = execute(circuit, before)
    mask = (1 << circuit.width) - 1
    require(signed(after & mask, circuit.width) == source, "source restoration")
    result = signed((after >> circuit.width) & mask, circuit.width)
    require(result == target + circuit.sign * (source >> circuit.shift), "signed ADD")
    require(after >> (2 * circuit.width) == 0, "carry and scratch return")
    return after


def coarse_call(circuit: Circuit, source: int, target: int) -> int:
    """Append k owned zero fractional bits to each P-bit input, W=P+k.

    The source's k new bits return to zero. The target's k new bits are
    retained output data, not erased or silently rounded back to P bits.
    """
    validate(circuit)
    precision = circuit.width - circuit.shift
    low, high = -(1 << (precision - 1)), 1 << (precision - 1)
    require(type(source) is int and low <= source < high, "coarse source range")
    require(type(target) is int and low <= target < high, "coarse target range")
    return check(circuit, source << circuit.shift, target << circuit.shift)


def invoice(circuit: Circuit) -> dict[str, int]:
    validate(circuit)
    cx = sum(len(gate) == 2 for gate in circuit.gates)
    ccx = sum(len(gate) == 3 for gate in circuit.gates)
    width, shift = circuit.width, circuit.shift
    expected = 4 * width - 2 + 2 * shift * (3 * width - 2)
    if circuit.policy == "wired":
        expected = 4 * width - 2 + 2 * shift
    if circuit.policy == "scratch":
        expected += 2 * width
    require(cx == expected and ccx == 2 * width - 2, "literal full gate count")
    return {
        "cx": cx,
        "ccx": ccx,
        "clean_bits": circuit.wires - 2 * width,
        "total_bits": circuit.wires,
        "fractional_guard_zeros": shift,
        "coarse_input_bits": 2 * (width - shift),
        "coarse_new_zero_bits": circuit.wires - 2 * (width - shift),
        "coarse_returned_zero_bits": circuit.wires - 2 * width + shift,
        "coarse_retained_new_target_bits": shift,
    }
