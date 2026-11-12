"""Directed complete B-to-A port price with charged main-owner substitutions."""
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


def read(path):
    raw = (ROOT / path).read_bytes()
    assert sha256(raw).hexdigest() == PINS[path]
    return raw


def profile(caller, name):
    info = caller["types"][name]
    assert all(row[:2] == [-1, 0] for row in info["diagonal"])
    targets = Counter(1 + 8 * sum(row[2:]) for row in info["diagonal"])
    paid = Counter()
    for event in caller["events"]:
        if event[0] != name:
            continue
        if event[1] == "QUERY":
            paid[1] += 1
        elif event[1] in ("IDLE_ONE", "IDLE_ODD"):
            paid[8 * len(event[3]) + (event[1] == "IDLE_ODD")] += 1
    return targets, paid, info["ports"]


def stop(*_):
    raise TimeoutError("15-second price cap")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(15)
    caller = loads(read("inputs/CALLER.json"))
    base = loads(read("inputs/R92-PRICE.json"))
    read("inputs/pricing.py")
    cost = run_path(str(ROOT / "inputs/pricing.py"))["cost"]
    a, pa, a_ports = profile(caller, "A")
    b, pb, b_ports = profile(caller, "B")
    assert len(a_ports) == 96 and len(b_ports) == 8
    assert sorted(a_ports + b_ports) == list(range(104))
    assert caller["stages"] == 17 and len(caller["events"]) == 4783
    assert all(len(e[2]) == 4 and len(e[3][:2]) == 2 for e in caller["events"] if e[0] == "J")
    assert sum(a.values()) == sum(b.values()) == 36
    delta = a.copy()
    delta.subtract(pa)
    delta.subtract(b)
    delta.update(pb)

    paid = Counter({int(r): n for r, n in base["old_paid"].items()})
    targets = Counter({int(r): n for r, n in base["old_targets"].items()})
    stock = targets.copy()
    stock.subtract(paid)
    assert (sum(paid.values()), sum(targets.values()), sum(r*n for r, n in stock.items())) == (110519, 22461, 1424)
    crossing = Q(base["old_crossing_upper"])
    min_lost = 2 * caller["stages"]
    owner_delta = delta.copy()
    owner_delta[1] -= min_lost
    cases = []
    for ports in range(1, len(b_ports) + 1):
        priced = {r: n * ports for r, n in owner_delta.items()}
        complete = stock.copy()
        complete.update(priced)
        cases.append({"ports": ports, "optimistic_delta": cost(priced, crossing),
                      "optimistic_full_margin": cost(complete, crossing),
                      "optimistic_rank_mass": sum(r*n for r, n in complete.items())})
    alarm(0)
    print(dumps({"head": base["head"], "caller": base["caller_head"], "pins": PINS,
                 "per_port": {"A_paid": pa, "A_targets": a, "B_paid": pb, "B_targets": b},
                 "type_b_ports": b_ports, "free_reclassification_margin": cost(delta, crossing),
                 "minimum_lost_rank_one_credits_per_port": min_lost,
                 "cases": cases, "hard_cap_seconds": 15}, sort_keys=True, indent=2, default=str))


if __name__ == "__main__":
    main()
