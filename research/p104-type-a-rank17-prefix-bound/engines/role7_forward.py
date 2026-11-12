"""Classify the exact role-7 prefix for both sign allocations."""
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/PRICE.json": "e076ac34017cc3c86c185a3f5982857dd70325012e196a2dcdd8d2d85a3957dc",
    "inputs/forward.py": "1043c6cb86af5c3fe348e62e5e7f89c2148e1273f1456382907a1a77a739b0df",
}
ROLE, START, END = 7, 1139, 1466


def checked(path):
    raw = (ROOT / path).read_bytes()
    if sha256(raw).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return raw


def stop(*_):
    raise TimeoutError("25-second exact cap")


def sample(rows, cut):
    cells = [[r, q, [body.count(s) for s in range(1, 18)], str(a), str(b)]
             for r, row in enumerate(rows) for (q, body), (a, b) in sorted(row.items())]
    cells.sort(key=lambda x: (x[0], x[1], x[2]))
    assert cells
    factors = [int(s == 7) for s in range(1, 18)]
    foreign = next((cell for cell in cells if cell[2] != factors), None)
    parity = sorted({cell[1] % 2 for cell in cells})
    digest = sha256((dumps(cells, separators=(",", ":")) + "\n").encode()).hexdigest()
    witness = [next(cell for cell in cells if cell[1] % 2 == p) for p in parity]
    result = dict(cut=cut, terms=len(cells), sha256=digest, first_foreign_body=foreign,
                  parity=parity, parity_witnesses=witness)
    if foreign is None and len(parity) == 1:
        result["surviving_column"] = cells
    return result


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(25)
    caller, price = (loads(checked(p)) for p in ("inputs/CALLER.json", "inputs/PRICE.json"))
    checked("inputs/forward.py")
    alg = run_path(str(ROOT / "inputs/forward.py"))
    assert ROLE in price["roles"] and caller["events"][START - 1][:3] == ["J", 7, [7, 0, 18, 25]]
    assert caller["events"][END] == ["A", "IDLE_ONE", ROLE, [8]]
    assert len(caller["events"]) == 4783
    kind = caller["types"]["A"]
    rows = [{} for _ in range(kind["roles"])]
    rows[ROLE] = {(0, ()): alg["ONE"]}
    alpha = Fraction(kind["alpha2"])
    receipt = []
    for clock, event in enumerate(caller["events"], 1):
        alg["propagate"](rows, event, alpha)
        if START <= clock <= END:
            receipt.append(sample(rows, clock))
    assert len(receipt) == END - START + 1 == 328
    assert rows[ROLE] == {(3, (7, 8)): alg["ONE"]}
    assert all(not row for r, row in enumerate(rows) if r != ROLE)
    assert "surviving_column" in sample([{(1, (7,)): alg["ONE"]}], 0)
    assert "surviving_column" in sample([{(2, (7,)): alg["ONE"]}], 0)
    assert "surviving_column" not in sample([{(1, (7,)): alg["ONE"], (2, (7,)): alg["ONE"]}], 0)
    alarm(0)
    survivors = [row["cut"] for row in receipt if "surviving_column" in row]
    print(dumps(dict(head=price["head"], caller=price["caller"], pins=PINS, role=ROLE,
                     caps=dict(cuts=328, seconds=25), rows=receipt, survivors=survivors),
                indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
