"""Replay the one-clock Type B Walsh packing price and support gate."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from math import comb
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

HERE = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/7113-signed-child.py": "ef03444360f02225138be9b38e2f9a85f313eeaa910d63a365de0f16d228cb8b",
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
CLOCK = 2866
PORTS = (15, 17, 27, 34, 35, 42, 47, 55)


def stop(*_):
    raise TimeoutError("30-second clock-2866 gate")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(30)
    for name, digest in PINS.items():
        assert sha256((HERE / name).read_bytes()).hexdigest() == digest
    caller = loads((HERE / "inputs/CALLER.json").read_bytes())
    tape = caller["events"]
    assert len(tape) == 4783 and tape[CLOCK] == ["B", "IDLE_ONE", 36, [9]]
    assert tuple(caller["types"]["B"]["ports"]) == PORTS
    assert all(tape[i][:3] == ["B", "ADD", 36] for i in (CLOCK-1, CLOCK+1))
    child = run_path(str(HERE / "inputs/7113-signed-child.py"))
    c = child["C"]
    multiply = child["multiply"]
    for u, eigen in ((0, (1, 0)), (1, (0, 1))):
        for row in range(2):
            left = [sum((-1)**(u*j)*c[row][j][k] for j in range(2)) for k in range(2)]
            right = [2*(-1)**(u*row)*x for x in eigen]
            assert left == right
    # S=diag(1,i); S C S / ((1+i)/2) is the two-point Walsh matrix.
    for i in range(2):
        for j in range(2):
            left = multiply(multiply((1-i, i), c[i][j]), (1-j, j))
            assert left == ((1, 1) if not i*j else (-1, -1))
    counts = [sum(comb(8, j) for j in range(k, 9, 4)) for k in range(4)]
    assert counts == [72, 64, 56, 64]
    active = sum(counts[1:])
    assert active == 184 and active > 2**7
    # At width f, (1+i)^(8f)=16^f. The residue-zero count is
    # 2^(8f-2)+2^(4f-1), so active fraction grows from 23/32.
    assert multiply(multiply((1, 1), (1, 1)), multiply((1, 1), (1, 1))) == (-4, 0)
    assert multiply((-4, 0), (-4, 0)) == (16, 0)
    old = loads((HERE / "inputs/R92-PRICE.json").read_bytes())
    k = Fraction(old["old_crossing_upper"])
    assert 0 < k < Fraction(1, 250)
    cost = run_path(str(HERE / "inputs/pricing.py"))["cost"]
    directed = cost(Counter({8: -8}), k)
    assert directed[1] < -Fraction(63232, 1000)
    alarm(0)
    print(dumps({"pins": PINS, "head": old["head"], "caller": old["caller_head"],
                 "clock": CLOCK, "ports": PORTS, "counts_f1": counts,
                 "active_f1": active, "capacity_f1_rank7": 128,
                 "displacement_fraction": "3/4 - 2^(-4f-1)",
                 "standalone_known_walsh_delta": [str(x) for x in directed],
                 "width": "all integers f >= 1", "ordinary_cost_floor": 0,
                 "build_admitted": False, "runner_cap_seconds": 30}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
