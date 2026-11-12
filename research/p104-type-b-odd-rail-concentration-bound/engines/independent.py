"""Check the fixed-fibre signed rank requirement for two Type B odd rails."""
from ast import Assign, Name, literal_eval, parse
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/7113-signed-child.py": "ef03444360f02225138be9b38e2f9a85f313eeaa910d63a365de0f16d228cb8b",
    "inputs/7334-RESULT.json": "7f2d587c59f063b01f1e8b320084a7f0943f2f05d65e3e0f5e80448c6c8e8194",
}
CLOCKS = {68: 1339, 70: 2970}
PORTS = [15, 17, 27, 34, 35, 42, 47, 55]


def unique(items):
    result = dict(items)
    assert len(items) == len(result)
    return result


def checked(path):
    raw = (ROOT / path).read_bytes()
    assert sha256(raw).hexdigest() == PINS[path], path
    return raw


def stop(*_):
    raise TimeoutError("20-second exact gate")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(20)
    caller = loads(checked("inputs/CALLER.json"), object_pairs_hook=unique)
    assert caller["types"]["B"]["ports"] == PORTS
    events = caller["events"]
    assert len(events) == 4783
    contacts = {role: [] for role in CLOCKS}
    for index, event in enumerate(events):
        if event[0] == "J":
            used = event[3][:2]
        elif event[0] == "B":
            assert event[1] in {"ADD", "SCALE", "SWAP", "IDLE_ONE", "IDLE_ODD", "LAMBDA"}
            used = event[2:4] if event[1] in {"ADD", "SWAP"} else event[2:3]
        else:
            assert event[0] == "A"
            continue
        for role in CLOCKS.keys() & set(used):
            contacts[role].append(index)
    assert contacts == {role: [clock] for role, clock in CLOCKS.items()}
    assert events[1339] == ["B", "IDLE_ODD", 68, [8], -1]
    assert events[2970] == ["B", "IDLE_ODD", 70, [9], -1]
    node = next(n for n in parse(checked("inputs/7113-signed-child.py")).body
                if isinstance(n, Assign) and isinstance(n.targets[0], Name)
                and n.targets[0].id == "C")
    gate = literal_eval(node.value)
    plus, minus = (1, 1), (1, -1)
    def twice_action(v):
        return [tuple(sum(gate[row][j][k] * v[j] for j in range(2)) for k in range(2))
                for row in range(2)]
    assert twice_action(plus) == [(2, 0), (2, 0)]
    assert twice_action(minus) == [(0, 2), (0, -2)]
    # The two minus lines contribute i*i=-1. All body axes are on plus lines.
    signs = tuple(events[clock][-1] for clock in CLOCKS.values())
    columns = {}
    for q in (1, -1):
        phase = [int(Fraction(q)**sign) for sign in signs]
        columns[q] = [[phase[0], 0], [0, phase[1]]]
    delta = [[columns[1][j][i] - columns[-1][j][i] for i in range(2)] for j in range(2)]
    determinant = delta[0][0]*delta[1][1] - delta[0][1]*delta[1][0]
    assert determinant == 4
    invoice = loads(checked("inputs/7334-RESULT.json"), object_pairs_hook=unique)["price"]["after"]
    assert (invoice["P"]["8"], invoice["P"]["9"], invoice["P"].get("10", 0)) == (741, 32, 0)
    assert (sum(invoice["P"].values()), sum(invoice["T"].values()), invoice["S"]) == (110519, 22461, 1424)
    assert sum({8:8, 9:-16, 10:8}.values()) == 0
    assert 8*8 - 9*16 + 10*8 == 0
    cap = Fraction("0.00376669")
    assert 0 < cap < 1
    alarm(0)
    print(dumps({"pins": PINS, "contacts": contacts, "ports": PORTS, "phase_columns": columns,
                 "determinant_required": determinant, "replacement_difference_rank_upper": 1,
                 "paid_delta": {8:8, 9:-16, 10:8}, "gross_strict_upper": str(cap),
                 "columns_checked": 4, "runner_cap_seconds": 20}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
