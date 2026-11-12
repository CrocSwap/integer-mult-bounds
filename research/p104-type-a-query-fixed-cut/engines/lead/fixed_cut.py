"""Direct exact fixed-cut compensator action on all 36 basis columns."""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys
from time import monotonic

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
PRICE = "52e05b80069ce01cad3b8e5f3cf9123e930de36987bd398dd43f103953a4674a"
CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
CLOCKS = (1516, 1580, 1659, 1721)
N = 36


def checked(path, expected):
    value = path.read_bytes()
    if sha256(value).hexdigest() != expected:
        raise ValueError(f"changed dependency {path.name}")
    return json.loads(value)


def trace(caller, first, second, q, even):
    factors = []
    assert Q(caller["types"]["A"]["alpha2"]) == -1
    for clock in range(first, second + 1):
        kind, op, *args = caller["events"][clock]
        if kind == "J":
            x, y, u, v = args[0]
            assert len({x, y, u, v}) == 4
            factors.extend([("ADD", y, x, Q(q)), ("ADD", u, v, Q(-q))])
        elif kind == "A":
            d, *tail = args
            if op in ("ADD", "QUERY"):
                s, k = tail
                if op == "QUERY":
                    if clock in (first, second):
                        assert (d, s, k) == (0, 1, -1)
                    k = Q(1 if even and clock in (first, second) else q) ** k
                factors.append(("ADD", d, s, Q(k)))
            elif op == "SCALE":
                k = Q(tail[0])
                assert k
                factors.append((op, d, d, k))
            elif op == "SWAP":
                factors.append((op, d, tail[0], Q(0)))
            elif op == "LAMBDA":
                assert q*q == 1
            elif op == "IDLE_ODD":
                factors.append(("SCALE", d, d, Q(q) ** tail[1]))
            elif op != "IDLE_ONE":
                raise ValueError(op)
        elif kind != "B":
            raise ValueError(kind)
    return factors


def apply(factors, vector, inverse=False):
    for op, d, s, k in reversed(factors) if inverse else factors:
        if op == "ADD":
            vector[d] += (-k if inverse else k) * vector[s]
        elif op == "SCALE":
            vector[d] *= 1/k if inverse else k
        elif op == "SWAP":
            vector[d], vector[s] = vector[s], vector[d]
        else:
            raise ValueError(op)
    return vector


def defect(original, even, dimension=N):
    columns = []
    for i in range(dimension):
        vector = [Q(j == i) for j in range(dimension)]
        changed = apply(even, apply(original, vector.copy()), inverse=True)
        assert apply(even, changed.copy()) == apply(original, vector.copy())
        columns.append([b-a for a, b in zip(vector, changed)])
    return columns


def square_entry(columns):
    n = len(columns)
    for j, col in enumerate(columns):
        for i in range(n):
            value = sum(columns[k][i]*a for k, a in enumerate(col) if a)
            if value:
                return [i, j, str(value)]
    return None


def rank(columns):
    basis = {}
    for column in columns:
        v = column.copy()
        for i, row in sorted(basis.items()):
            if v[i]:
                v = [a-v[i]*b for a,b in zip(v,row)]
        i = next((i for i,x in enumerate(v) if x), None)
        if i is not None:
            basis[i] = [x/v[i] for x in v]
    return len(basis)


def controls():
    disjoint = [("ADD", 0, 1, Q(-2)), ("ADD", 2, 3, Q(-2))]
    shared = [("ADD", 0, 1, Q(-2)), ("ADD", 1, 0, Q(-2))]
    assert rank(defect(disjoint, [], 4)) == 2
    assert square_entry(defect(disjoint, [], 4)) is None
    assert square_entry(defect(shared, [], 4)) is not None
    assert defect(disjoint, disjoint, 4) == [[0]*4 for _ in range(4)]
    return ["commuting disjoint rank two", "cross-acting rank two", "exact predecessor cancellation"]


def main():
    root = Path(sys.argv[1])
    price = checked(root / "price/PRICE.json", PRICE)
    caller = checked(root / "price/inputs/7113-CALLER.json", CALLER)
    assert (caller["stages"], len(caller["types"]["A"]["ports"])) == (17, 96)
    keys = list(combinations(CLOCKS, 2))
    checks = controls()
    deadline = monotonic() + 18
    records = []
    for first, second in keys:
        if monotonic() >= deadline:
            break
        even_plus, orig_plus = (trace(caller, first, second, 1, flag) for flag in (True, False))
        assert even_plus == orig_plus and rank(defect(orig_plus, even_plus)) == 0
        even_minus, orig_minus = (trace(caller, first, second, -1, flag) for flag in (True, False))
        columns = defect(orig_minus, even_minus)
        r, square = rank(columns), square_entry(columns)
        records.append(dict(key=[first, second], rank=r, square_witness=square,
                            decision="excluded" if square is not None or r > 2 else "provisional",
                            defect_columns=[{i:str(x) for i,x in enumerate(col) if x} for col in columns]))
    print(json.dumps(dict(head=HEAD, caller_sha256=CALLER, price_sha256=PRICE, scope="fixed first cut, commuting mutually annihilating rank-one axes", body_values="all one",
                          controls=checks, cap_cases=6, cap_runner_seconds=18, decisions=records, unvisited=keys[len(records):]), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
