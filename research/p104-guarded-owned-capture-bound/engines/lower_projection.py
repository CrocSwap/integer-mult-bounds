"""Direct exact coordinate separators for the six lower-chart first reads."""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from time import monotonic
import gzip
import json
import sys

WORD = "c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9"
PRICE = "d7da1459dda5b5a33fa1a022d74ba16081e3215c1a37b50112f3597b6033b9ef"
HEAD = "9d0119eb12fbd9fa534b48cd37b68e7099757b91"
CASES = {33134: (1514, 260, 2), 34520: (1518, 431, 2), 35435: (1519, 600, 2),
         36320: (1516, 394, 1), 36328: (1517, 598, 1), 39845: (1515, 599, 0)}


def read(path, digest):
    raw = Path(path).read_bytes()
    if sha256(raw).hexdigest() != digest:
        raise ValueError(f"changed pinned input: {Path(path).name}")
    return raw


def separated(value, donors):
    return bool(value) and not any(donors)


def project(word):
    assert separated(Fraction(-2), [0, 0])
    assert not separated(Fraction(-2), [Fraction(1, 7), 0])
    assert not separated(Fraction(0), [0, 0])
    deadline = monotonic() + 10
    public = word["public"]
    charts = list(word["initial"]) + [None] * word["owned_fields"]
    rows = [{i: Fraction(1)} if i < 3 else {} for i in range(len(charts))]
    results = []
    tape = word["program"]
    for t, (op, dst, *args) in enumerate(tape):
        if t % 128 == 0 and monotonic() >= deadline:
            break
        if t in CASES:
            role, chart, coord = CASES[t]
            move, mover, old, new, owned = tape[t-1]
            assert (move, mover, new, owned) == ("MOVE", role, chart, True)
            assert len(word["frames"][old]) > len(word["frames"][new])
            assert op == "ADD" and args[0] == role and args[-1] == chart
            donors = [r for r, f in enumerate(charts) if f == chart and r != role]
            target = rows[role].get(coord, 0)
            assert separated(target, (rows[r].get(coord, 0) for r in donors))
            results.append(dict(role=role, read=t, move=t-1, chart=chart,
                                coordinate=coord, target=str(target), donor_roles=donors,
                                public_donors=sum(r < public for r in donors)))
        if op == "MOVE":
            assert charts[dst] == args[0]
            charts[dst] = args[1]
        elif op in ("INIT", "CLEAR"):
            assert charts[dst] == (None if op == "INIT" else args[0])
            charts[dst], rows[dst] = (args[0] if op == "INIT" else None), {}
        else:
            source = dst if op == "SCALE" else args[0]
            assert charts[source] == charts[dst] == args[-1]
            q = Fraction(args[-2])
            scaled = {j: q * v for j, v in rows[source].items()}
            if op == "ADD":
                for j, x in scaled.items():
                    value = rows[dst].get(j, 0) + x
                    if value:
                        rows[dst][j] = value
                    else:
                        rows[dst].pop(j, None)
            else:
                assert op in ("SCALE", "COPY")
                rows[dst] = scaled
        if t == max(CASES):
            break
    unvisited = sorted(CASES.keys() - {r["read"] for r in results})
    return dict(head=HEAD, price_sha256=PRICE, word_sha256=WORD,
                cases=results, unresolved=unvisited, complete=not unvisited,
                controls=["signed separation", "nonzero donor rejected", "zero target rejected"])


def main():
    price, word = sys.argv[1:]
    assert json.loads(read(price, PRICE))["head"] == HEAD
    result = project(json.loads(gzip.decompress(read(word, WORD))))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
