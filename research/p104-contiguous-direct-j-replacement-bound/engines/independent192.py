"""Replay the exact opposite-sign difference of the first three Type A J calls."""
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/GRAPH.json": "4b861a36472639caed5402eab19089c475a11e9eee96d14949001ed990c9ebb9",
    "inputs/PRICE.json": "1ad9852ecff0b3780770cbf4e500731e65214a9c438f8b1ed2c0cbe484d9b36b",
}
N = 36


def unique(items):
    result = dict(items)
    assert len(result) == len(items)
    return result


def read(name):
    raw = (ROOT / name).read_bytes()
    assert sha256(raw).hexdigest() == PINS[name], name
    return loads(raw, object_pairs_hook=unique)


def forward(events, index, q):
    column = [Fraction(k == index) for k in range(N)]
    for _, e in events:
        if e[0] == "J":
            x, y, u, v = e[2]
            assert len({x, y, u, v}) == 4
            column[y] += column[x] / q
            column[u] -= q * column[v]
        else:
            assert e[0] == "A"
            op, r = e[1:3]
            if op == "ADD":
                column[r] += Fraction(e[4]) * column[e[3]]
            elif op == "SCALE":
                column[r] *= Fraction(e[3])
            else:
                assert op in ("IDLE_ONE", "LAMBDA")
                # Bodies are set to identity and the normalized LAMBDA is q-even.
    return column


def rank_and_pivots(rows):
    work = [row.copy() for row in rows]
    order = list(range(len(rows)))
    selected = []
    for col in range(len(work[0])):
        row = len(selected)
        p = next((j for j in range(row, len(work)) if work[j][col]), None)
        if p is None:
            continue
        work[row], work[p] = work[p], work[row]
        order[row], order[p] = order[p], order[row]
        for j in range(row+1, len(work)):
            if work[j][col]:
                z = work[j][col] / work[row][col]
                work[j] = [b-z*a for a,b in zip(work[row], work[j], strict=True)]
        selected.append((order[row], col, work[row][col]))
    return selected


def stop(*_):
    raise TimeoutError("20-second exact rank gate")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(20)
    caller = read("inputs/CALLER.json")
    graph = read("inputs/GRAPH.json")
    price = read("inputs/PRICE.json")
    assert len(caller["events"]) == 4783 and caller["types"]["A"]["roles"] == N
    lo, hi = graph["window_inclusive"]
    assert (lo, hi) == (43,268)
    source = [[i,e] for i,e in enumerate(caller["events"][lo:hi+1],lo) if e[0] in ("J","A")]
    assert source == graph["typed_events"] and len(source) == 43
    assert [i for i,e in source if e[0]=="J"] == price["clocks"] == [43,137,268]
    assert not any(e[:2] in (["A","SWAP"],["A","QUERY"]) for _,e in source)
    assert Fraction(price["price_by_type_a_rank1_per_port"]["4"]["raw_gross"][0]) > 0
    assert Fraction(price["price_by_type_a_rank1_per_port"]["5"]["raw_gross"][1]) < 0
    results = {q:[forward(source, i, q) for i in range(N)] for q in (1,-1)}
    difference = [[results[1][j][i] - results[-1][j][i] for j in range(N)] for i in range(N)]
    pivots = rank_and_pivots(difference)
    r = len(pivots)
    rows = [i for i,_,_ in pivots]
    cols = [j for _,j,_ in pivots]
    minor = [[difference[i][j] for j in cols] for i in rows]
    minor_pivots = rank_and_pivots(minor)
    assert len(minor_pivots) == r
    determinant = Fraction(1)
    order = [i for i,_,_ in minor_pivots]
    inversions = sum(x>y for j,x in enumerate(order) for y in order[j+1:])
    for _,_,value in minor_pivots:
        determinant *= value
    determinant *= (-1)**inversions
    assert determinant
    assert len(rank_and_pivots([[Fraction(1),Fraction(2)],[Fraction(2),Fraction(4)]])) == 1
    alarm(0)
    print(dumps({"pins":PINS,"window":[lo,hi],"phases":[1,-1],"columns_per_sign":N,
                 "typed_events":len(source),"rank":r,"pivot_rows":rows,"pivot_columns":cols,
                 "nonzero_minor_determinant":str(determinant),"minor":minor,
                 "four_query_gate_survives":r<=4,"cap_seconds":20}, default=str,sort_keys=True,indent=2))


if __name__ == "__main__":
    main()
