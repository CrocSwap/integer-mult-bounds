# SPDX-License-Identifier: Apache-2.0
"""Bit-array evaluator for serialized fanout gates; imports no gate producer."""


def need(condition, message):
    if not condition:
        raise ValueError(message)


def parse(document):
    need(type(document) is dict, "program object")
    need(set(document) == {"width", "shared", "wires", "gates"}, "program fields")
    w = document["width"]
    need(type(w) is int and 4 <= w <= 256, "width")
    need(type(document["shared"]) is bool, "policy")
    need(type(document["wires"]) is int and document["wires"] == 5 * w + 1, "wires")
    gates = document["gates"]
    need(type(gates) is list and len(gates) <= 8192, "gate budget")
    for gate in gates:
        need(type(gate) is list and len(gate) in (2, 3), "gate shape")
        need(all(type(i) is int and 0 <= i < 5 * w + 1 for i in gate), "wire range")
        need(len(set(gate)) == len(gate), "wire alias")
    return w, tuple(tuple(g) for g in gates)


def check(program, source, targets):
    w, gates = program
    need(type(targets) is tuple and len(targets) == 4, "four targets")
    values = (source, *targets)
    need(
        all(type(x) is int and -(2 ** (w - 1)) <= x < 2 ** (w - 1) for x in values),
        "signed inputs",
    )
    need(source % 2 == 0, "guard")
    expected = (source, *(x - source // 2 for x in targets))
    need(all(-(2 ** (w - 1)) <= x < 2 ** (w - 1) for x in expected), "signed result")
    bits = []
    for value in values:
        bits.extend((value % (2**w) // (2**i)) % 2 for i in range(w))
    bits.append(0)
    for gate in gates:
        if all(bits[i] == 1 for i in gate[:-1]):
            bits[gate[-1]] = 1 - bits[gate[-1]]
    actual = []
    for j in range(5):
        value = sum(bits[j * w + i] * 2**i for i in range(w))
        if bits[(j + 1) * w - 1]:
            value -= 2**w
        actual.append(value)
    need(
        tuple(actual) == expected and bits[-1] == 0, "array fanout result/source/carry"
    )
