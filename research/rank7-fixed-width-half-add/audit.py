# SPDX-License-Identifier: Apache-2.0
"""Separate bit-array interpreter. Does not import the circuit producer."""

from dataclasses import dataclass


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Program:
    width: int
    shift: int
    sign: int
    policy: str
    wires: int
    gates: tuple[tuple[int, ...], ...]


def parse(document: dict) -> Program:
    need(type(document) is dict, "program object")
    need(
        set(document) == {"width", "shift", "sign", "policy", "wires", "gates"},
        "program fields",
    )
    w, k = document["width"], document["shift"]
    need(type(w) is int and 4 <= w <= 256, "width")
    need(type(k) is int and 1 <= k <= 3 and k < w, "shift")
    need(type(document["sign"]) is int and document["sign"] in (-1, 1), "sign")
    policy = document["policy"]
    need(policy in ("source", "scratch", "wired"), "policy")
    wires = (3 if policy == "scratch" else 2) * w + 1
    need(type(document["wires"]) is int and document["wires"] == wires, "wire count")
    gates = document["gates"]
    need(type(gates) is list and len(gates) <= 8192, "gate budget")
    for gate in gates:
        need(type(gate) is list and len(gate) in (2, 3), "gate shape")
        need(all(type(i) is int and 0 <= i < wires for i in gate), "wire range")
        need(len(set(gate)) == len(gate), "aliased gate")
    return Program(w, k, document["sign"], policy, wires, tuple(map(tuple, gates)))


def observe(program: Program, source: int, target: int) -> tuple[int, int, int]:
    """Evaluate literal gates using mutable bits, not packed-state gate updates."""
    w = program.width
    encoded = (source % (2**w)) + (target % (2**w)) * (2**w)
    bits = [(encoded // (2**i)) % 2 for i in range(program.wires)]
    for gate in program.gates:
        if all(bits[control] == 1 for control in gate[:-1]):
            bits[gate[-1]] = 1 - bits[gate[-1]]
    values = []
    for offset in (0, w):
        value = sum(bits[offset + i] * (2**i) for i in range(w))
        if bits[offset + w - 1]:
            value -= 2**w
        values.append(value)
    dirty = sum(bits[i] for i in range(2 * w, program.wires))
    return values[0], values[1], dirty


def check(program: Program, source: int, target: int) -> None:
    w, k = program.width, program.shift
    need(type(source) is int and type(target) is int, "integer inputs")
    need(-(2 ** (w - 1)) <= source < 2 ** (w - 1), "source range")
    need(-(2 ** (w - 1)) <= target < 2 ** (w - 1), "target range")
    need(source % (2**k) == 0, "source grid")
    expected = target + program.sign * (source // (2**k))
    need(-(2 ** (w - 1)) <= expected < 2 ** (w - 1), "result range")
    need(
        observe(program, source, target) == (source, expected, 0),
        "bit-array caller identity and clean return",
    )
