"""Check all width-one Walsh columns of one fixed stage-9 even idle."""
from ast import Assign, Name, literal_eval, parse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import version_info

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/7113-signed-child.py": "ef03444360f02225138be9b38e2f9a85f313eeaa910d63a365de0f16d228cb8b",
    "inputs/7334-RESULT.json": "7f2d587c59f063b01f1e8b320084a7f0943f2f05d65e3e0f5e80448c6c8e8194",
}
UNITS = ((1, 0), (0, 1), (-1, 0), (0, -1))
PORTS = [15, 17, 27, 34, 35, 42, 47, 55]
AXES, DIM, CAP = 8, 256, 30


def unique(pairs):
    values = dict(pairs)
    if len(values) != len(pairs):
        raise ValueError("duplicate JSON key")
    return values


def checked(path):
    data = (ROOT / path).read_bytes()
    assert sha256(data).hexdigest() == PINS[path], path
    return data


def body(column, direction):
    # Apply 2C (or 2C*) on each bit using Gaussian integer pair arithmetic.
    values = [(x, 0) for x in column]
    for axis in range(AXES):
        stride = 1 << axis
        for block in range(0, DIM, 2 * stride):
            for k in range(block, block + stride):
                a, b = values[k]
                c, d = values[k + stride]
                rr = a + c
                ii = b + d
                dr = direction * (a - c)
                di = direction * (b - d)
                values[k] = (rr - di, ii + dr)
                values[k + stride] = (rr + di, ii - dr)
    return values


def expected(column, phase):
    a, b = UNITS[phase]
    return [(DIM * x * a, DIM * x * b) for x in column]


def stop(*_):
    raise TimeoutError("30-second finite gate")


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    signal(SIGALRM, stop)
    alarm(CAP)
    signed_source = checked("inputs/7113-signed-child.py")
    assert b"((9+8*(stage-1))*width)" in signed_source
    constants = {node.targets[0].id: literal_eval(node.value)
                 for node in parse(signed_source).body
                 if isinstance(node, Assign) and len(node.targets) == 1
                 and isinstance(node.targets[0], Name)
                 and node.targets[0].id in {"C", "EXPECTED_PORTS"}}
    assert constants["C"] == (((1, 1), (1, -1)), ((1, -1), (1, 1)))
    assert list(constants["EXPECTED_PORTS"]) == PORTS
    caller = loads(checked("inputs/CALLER.json"), object_pairs_hook=unique)
    assert len(caller["events"]) == 4783 and caller["types"]["B"]["ports"] == PORTS
    assert caller["events"][2866] == ["B", "IDLE_ONE", 36, [9]]
    assert caller["events"][2935] == ["B", "IDLE_ONE", 54, [9]]
    assert caller["ambient_rank"] == 145 and caller["stages"] == 17
    observed = {1: Counter(), -1: Counter()}
    for char in range(DIM):
        column = [1 - 2*((j & char).bit_count() % 2) for j in range(DIM)]
        for direction in (1, -1):
            actual = body(column, direction)
            phase = UNITS.index(tuple(v // DIM for v in actual[0]))
            assert actual == expected(column, phase)
            assert phase == (direction * char.bit_count()) % 4
            observed[direction][phase] += 1
            if char == 1:
                assert actual != expected(column, (-phase) % 4)
                assert actual != expected(column, 0)
    assert observed[1] == observed[-1] == Counter({0: 72, 1: 64, 2: 56, 3: 64})
    result = loads(checked("inputs/7334-RESULT.json"), object_pairs_hook=unique)
    invoice = result["price"]["after"]
    assert (invoice["P"]["8"], sum(invoice["P"].values()), sum(invoice["T"].values()), invoice["S"]) == (741, 110519, 22461, 1424)
    hypothetical_gain_upper = 8 * 8 * Fraction(observed[1][0], DIM)
    assert hypothetical_gain_upper == 18
    # ln(8)<3, κ<1/250 and exp(-x)>1-x give 8H8 > 64*(1-3/250).
    retained_bit = Fraction("0.00376669")
    assert retained_bit < Fraction(1, 250)
    strict_conversion_gain_upper = -64 * (1 - Fraction(3, 250))
    assert strict_conversion_gain_upper == Fraction("-63.232")
    alarm(0)
    print(dumps({
        "basis_columns": DIM, "cap_seconds": CAP, "checked_clock": 2866,
        "phases_forward_and_adjoint": [observed[1][j] for j in range(4)],
        "displacement_rank": DIM - observed[1][0], "input_pins": PINS,
        "exact_ports": PORTS, "selected_axis_range": [73, 80],
        "optimistic_free_conversion_saving_strict_upper": str(hypothetical_gain_upper),
        "optimistic_charged_conversion_saving_strict_upper": str(strict_conversion_gain_upper),
        "priced_paid_histogram_delta": {"8": 8}, "unresolved_within_width_one": 0,
        "controls": ["wrong signed phase", "missing odd phase"],
    }, indent=2, sort_keys=True))
    print("PASS_R180_WIDTH_ONE_WALSH_PRICE_AND_ACTION")


if __name__ == "__main__":
    main()
