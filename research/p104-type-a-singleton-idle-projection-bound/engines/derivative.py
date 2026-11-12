"""Reconstruct the fixed Type A stage-8 two-return derivative directly."""
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "PRICE.json": "fc02b956e172a6128c08a4774efd5c0bc99ad63cf9cf921c8624aa46213e5560",
}
PAIR = (1466, 1487)
ROLES = (7, 25)
STAGE = 8


def checked(path):
    raw = (ROOT / path).read_bytes()
    if sha256(raw).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return loads(raw)


def stop(*_):
    raise TimeoutError("10-second cap")


def apply(events, roles, seed, erased):
    value = [Q(i == seed) for i in range(roles)]
    slope = [Q(0)] * roles
    for clock, (kind, op, dest, *args) in events:
        if kind != "A":
            assert kind == "B"
            continue
        if op == "IDLE_ONE":
            if clock not in erased and STAGE in args[0]:
                slope[dest] += value[dest]
        elif op == "ADD":
            source, scalar = args
            factor = Q(scalar)
            value[dest] += factor * value[source]
            slope[dest] += factor * slope[source]
        elif op == "SCALE":
            factor = Q(args[0])
            value[dest] *= factor
            slope[dest] *= factor
        elif op == "SWAP":
            peer, = args
            value[dest], value[peer] = value[peer], value[dest]
            slope[dest], slope[peer] = slope[peer], slope[dest]
        else:
            # Type A lambda normalization specializes to identity at q=1.
            assert op == "LAMBDA" and args[0] in (-1, 1)
    return value, slope


def minor(events, roles, outputs, erased):
    matrix = []
    for seed in outputs:
        value, old = apply(events, roles, seed, set())
        control, new = apply(events, roles, seed, erased)
        assert value == control
        matrix.append([old[i] - new[i] for i in outputs])
    determinant = matrix[0][0] * matrix[1][1] - matrix[1][0] * matrix[0][1]
    return matrix, determinant


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(10)
    caller, quote = (checked(path) for path in PINS)
    assert len(caller["events"]) == 4783 and quote["pair"] == list(PAIR)
    tape = caller["events"]
    assert all(tape[clock] == ["A", "IDLE_ONE", role, [STAGE]] for clock, role in zip(PAIR, ROLES, strict=True))
    window = list(enumerate(tape[PAIR[0]:PAIR[1] + 1], PAIR[0]))
    assert len(window) == 22
    count = caller["types"]["A"]["roles"]
    matrix, det = minor(window, count, ROLES, set(PAIR))
    assert det
    _, single = minor(window, count, ROLES, {PAIR[0]})
    assert not single
    toy = [(0, ["A", "IDLE_ONE", 0, [8]]), (1, ["A", "IDLE_ONE", 0, [8]])]
    old, collapsed = minor(toy, 2, (0, 1), {0, 1})
    assert not collapsed and old[0][0] == 2
    alarm(0)
    print(dumps(dict(head=quote["head"], caller=quote["caller"], pins=PINS, pair=PAIR, roles=ROLES,
                     events=len(window), minor_columns=[list(map(str, col)) for col in matrix],
                     determinant=str(det), exact_rank=2, case_cap=1, runner_seconds=10,
                     controls=["omit only one call", "two copies on one role"]), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
