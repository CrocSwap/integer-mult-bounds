"""Charge the two separately supplied eight-axis bodies of a B-to-A port."""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}


def read(name):
    raw = (ROOT / name).read_bytes()
    assert sha256(raw).hexdigest() == PINS[name]
    return raw


def stop(*_):
    raise TimeoutError("15-second exact cap")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(15)
    source = loads(read("inputs/CALLER.json"))
    quote = loads((ROOT/"R170-PRICE.json").read_bytes())
    base = loads(read("inputs/R92-PRICE.json"))
    read("inputs/pricing.py")
    cost = run_path(str(ROOT / "inputs/pricing.py"))["cost"]
    assert quote["head"] == base["head"] and quote["caller"] == base["caller_head"]
    assert len(quote["type_b_ports"]) == 8
    stages = [e for e in source["events"] if e[0]=="J"]
    assert [e[1] for e in stages] == list(range(1,18))
    dimensions = []
    for _, s, a, b in stages:
        axes = tuple(1 << i for i in range(9+8*(s-1), 9+8*s))
        assert len(axes) == len(set(axes)) == 8 and all(x.bit_count()==1 for x in axes)
        assert len(set(a)) == 4 and len(set(b[:2])) == 2
        dimensions.extend([len(axes)] * (len(a)-len(b[:2])))
    assert dimensions == [8] * 34
    p = quote["per_port"]
    assert p["A_targets"] == p["B_targets"]
    credit = Counter({int(r): n for r, n in p["B_paid"].items()})
    credit.subtract({int(r): n for r, n in p["A_paid"].items()})
    assert {r:n for r,n in credit.items() if n} == {1:-4,8:30,9:4}
    credit.subtract(dimensions)
    signed = {r:n for r,n in credit.items() if n}
    assert signed == {1:-4,8:-4,9:4}
    crossing = Q(base["old_crossing_upper"])
    gain = cost(signed, crossing)
    assert gain[1] < 0
    alarm(0)
    print(dumps({"head": base["head"], "caller": base["caller_head"], "pins": PINS,
                 "stage_body_dimensions": dimensions, "charged_signed_delta_per_port": signed,
                 "gain_interval_per_port": gain, "compatible_ports_upper": 8,
                 "eight_port_delta_interval": [8*x for x in gain],
                 "scope": "two independent body completions per J, support paid or retired, signed repairs granted free",
                 "stop": "exact price exclusion, no native build", "hard_cap_seconds": 15},
                sort_keys=True, indent=2, default=str))


if __name__ == "__main__":
    main()
