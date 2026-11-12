"""One full-J1 extension of the lexicographic Type A circuit."""
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINS = {
    "lead/RESULT.json": "ab74c834d4b94c63cda667338055889667e8e7a98c022ba6ed23afa35ff0acfe",
    "lead/dependency.py": "82959a8be9c332698e402fc963e0c3af8dfac6522128100851dd96c767e162d5",
    "lead/inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "lead/inputs/forward.py": "75d94780f9db49a4b08bb0e7fb4bd7fc04adb8cabbf73d83a809179c04c3d439",
}


def stop(*_):
    raise TimeoutError("20-second one-case plane gate")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(20)
    for name, digest in PINS.items():
        assert sha256((ROOT / name).read_bytes()).hexdigest() == digest
    lead = run_path(str(ROOT / "lead/dependency.py"))
    source = run_path(str(ROOT / "lead/inputs/forward.py"))
    unit, apply = source["unit"], source["apply"]
    old = loads((ROOT / "lead/RESULT.json").read_bytes())
    tape = loads((ROOT / "lead/inputs/CALLER.json").read_bytes())["events"]
    factors, keys = lead["source_factors"](unit, apply, tape)
    assert keys == old["factor_keys"] and keys[0][0] == keys[1][0] == 43
    assert 1 not in old["chosen"]
    chosen = sorted(old["chosen"] + [1])
    units = [unit(i) for i in range(36)]
    assert all(lead["product"](factors, e) == [-x for x in e] for e in units)
    cols, piv = lead["target"](chosen, factors, lead["suffix_transport"](factors), units)
    assert len(chosen) == 20 and len(piv) == 19
    off_block = [[row, col, str(x)] for col, entries in enumerate(cols)
                 for row, x in enumerate(entries) if x and col // 18 != row // 18]
    add, dot, rref = lead["add"], lead["dot"], lead["rref"]
    planes = []
    for first in () if off_block else (0, 18):
        field = slice(first, first + 18)
        block = [col[field] for col in cols[field]]
        basis = [e[field] for e in units[field]]
        delta = [add(col, e, -1) for col, e in zip(block, basis, strict=True)]
        rank = len(rref(zip(*delta, strict=True))[1])
        square = [[dot(row, col) for row in zip(*block, strict=True)] for col in block]
        involution = square == basis
        planes.append({"roles": list(range(first, first + 18)), "rank": rank, "involution": involution,
                       "length": rank + int(involution and rank > 0)})
    if not off_block:
        assert sum(p["rank"] for p in planes) == len(piv)
    alarm(0)
    print(dumps({"pins": PINS, "chosen": chosen, "added": 1, "rank": len(piv), "planes": planes,
                 "fixed_partition_off_block": off_block,
                 "plane_preserving_length": None if off_block else sum(p["length"] for p in planes),
                 "case_cap": 1,
                 "runner_cap_seconds": 20,
                 "target_columns": [[str(x) for x in col] for col in cols]}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
