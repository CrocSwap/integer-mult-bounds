"""Exact fixed-chart suffix column span for the funded role 1355 lift."""
from argparse import ArgumentParser
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
from time import monotonic

HEAD = "9d0119eb12fbd9fa534b48cd37b68e7099757b91"
WORD_SHA = "c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9"
PRICE_SHA = "25205ad2cf4230bd2b2b704eec9f96ec4a5486fd575b5599861b28ffdd15b00b"
FIRST, TARGET, LAST = 37765, 48184, 76460
FRAME, DONOR, CACHE = 240, 1355, 1568
PROTECTED = {863, DONOR}


def pinned(path, digest):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != digest:
        raise ValueError(f"changed pinned input: {path.name}")
    return raw


def accumulate(row, other, multiplier):
    for r, x in other.items():
        v = row.get(r, 0) + multiplier * x
        if v:
            row[r] = v
        else:
            row.pop(r, None)


def echelon(columns, target):
    basis = {}

    def reduce(column, terms):
        while column:
            p = min(column)
            if p not in basis:
                break
            old, coef = basis[p]
            multiple = -column[p] / old[p]
            accumulate(column, old, multiple)
            accumulate(terms, coef, multiple)

    for key, column in columns.items():
        row, terms = dict(column), {key: Q(1)}
        reduce(row, terms)
        if row:
            basis[min(row)] = row, terms
    residue, terms = target.copy(), {}
    for pivot, (row, coefficients) in sorted(basis.items()):
        if pivot in residue:
            multiple = -residue[pivot] / row[pivot]
            accumulate(residue, row, multiple)
            accumulate(terms, coefficients, multiple)
    return basis, residue, {k: -q for k, q in terms.items()}


def certificate(basis, residue, columns, target):
    witnesses = []
    for coordinate in sorted(residue, key=lambda i: (i != 1109, i)):
        dual = {coordinate: Q(1)}
        for pivot in sorted(basis, reverse=True):
            row = basis[pivot][0]
            value = -sum(x * dual.get(i, 0) for i, x in row.items() if i != pivot) / row[pivot]
            if value:
                dual[pivot] = value
        def value(column):
            return sum(q * dual.get(i, 0) for i, q in column)
        assert all(not value(column) for column in columns.values())
        result = value(target.items())
        assert result == residue[coordinate]
        witnesses.append((dual, result))
    dual, result = min(witnesses, key=lambda item: len(item[0]))
    return dict(dual={i:str(x) for i,x in dual.items()}, target_value=str(result))


def controls():
    a, b = (3, 1), (2, 1)
    cols = {a: ((1, Q(1)), (2, Q(2))), b: ((2, Q(-1)),)}
    _, miss, expr = echelon(cols, {1: Q(3), 2: Q(2)})
    assert not miss and expr == {a: Q(3), b: Q(4)}
    _, miss, _ = echelon(cols, {1: Q(3), 2: Q(2), 9: Q(1)})
    assert miss == {9: Q(1)}
    return ["signed spanning combination", "missing exterior coordinate"]


def screen(word, cap, seconds):
    check = controls()
    deadline = monotonic() + seconds
    n, owned = word["public"], word["owned_fields"]
    tape = word["program"]
    assert tape[TARGET-2:TARGET+1] == [
        ["MOVE", DONOR, 739, FRAME, False],
        ["ADD", DONOR, CACHE, "-2", FRAME],
        ["MOVE", DONOR, FRAME, 127, False],
    ]
    assert tape[FIRST-1] == ["COPY", CACHE, 863, "1", FRAME] or tape[FIRST-1] == ["ADD", CACHE, 863, "1", FRAME]
    assert tape[LAST] == ["CLEAR", CACHE, FRAME]
    charts = word["final"] + [None] * owned
    bank = {i for i, f in enumerate(charts[:n]) if f == FRAME}
    columns = {}
    seen = {}
    adjoint = [{i: Q(1)} for i in range(n)] + [{} for _ in range(owned)]
    target = None
    cut_count = visits = zeros = duplicates = 0
    omitted = None
    stop = "exhausted"
    for cut in range(len(tape), FIRST-1, -1):
        if monotonic() >= deadline:
            stop = "runner cap"
            omitted = [cut, None]
            break
        if cut == TARGET:
            target = {i: -2*x for i, x in adjoint[DONOR].items()}
            assert target
        op, dst, *args = tape[cut-1]
        touched = args[:2] if op == "MOVE" else [args[-1]]
        if FIRST <= cut <= LAST and (cut in (FIRST, LAST) or FRAME in touched):
            assert charts[CACHE] == FRAME
            cut_count += 1
            for r in sorted(bank - PROTECTED):
                visits += 1
                vector = tuple(sorted(adjoint[r].items()))
                if not vector:
                    zeros += 1
                    continue
                if vector in seen:
                    duplicates += 1
                    continue
                if len(columns) == cap:
                    stop = "case cap"
                    omitted = [cut, r]
                    break
                seen[vector] = (cut, r)
                columns[cut, r] = vector
            if omitted:
                break
        if cut == FIRST:
            break
        if op == "MOVE":
            old, new, flag = args
            assert charts[dst] == new and flag == (dst >= n)
            charts[dst] = old
            if not flag:
                if new == FRAME:
                    bank.remove(dst)
                if old == FRAME:
                    bank.add(dst)
        elif op in ("INIT", "CLEAR"):
            f, = args
            assert charts[dst] == (f if op == "INIT" else None)
            charts[dst] = None if op == "INIT" else f
            adjoint[dst] = {}
            if dst == CACHE:
                assert cut == LAST+1 and op == "CLEAR"
        else:
            coef, f = Q(args[-2]), args[-1]
            src = dst if op == "SCALE" else args[0]
            assert charts[src] == charts[dst] == f and dst != CACHE
            if op == "SCALE":
                adjoint[dst] = {j: coef*v for j, v in adjoint[dst].items()}
            else:
                assert op in ("ADD", "COPY") and src != dst
                accumulate(adjoint[src], adjoint[dst], coef)
                if op == "COPY":
                    adjoint[dst] = {}
    outcome = dict(stage=stop, omitted=omitted, cut_count=cut_count, visits=visits,
                   zeros=zeros, duplicates=duplicates, distinct=len(columns),
                   keys=list(columns), controls=check, cap=cap, seconds=seconds)
    if target is not None:
        basis, residue, terms = echelon(columns, target)
        if not residue:
            total = {}
            for key, q in terms.items():
                accumulate(total, dict(columns[key]), q)
            assert total == target
        outcome.update(rank=len(basis), target={i:str(q) for i,q in target.items()},
                       residual={i:str(q) for i,q in residue.items()},
                       witness=[] if residue else [[*key,str(q)] for key,q in terms.items()])
        if residue:
            outcome["separator"] = certificate(basis, residue, columns, target)
    return outcome


def main():
    p = ArgumentParser()
    p.add_argument("price", type=Path)
    p.add_argument("word", type=Path)
    p.add_argument("--cap", type=int, default=512, choices=range(1,513), metavar="[1,512]")
    p.add_argument("--seconds", type=int, default=27, choices=range(1,28), metavar="[1,27]")
    a = p.parse_args()
    price = json.loads(pinned(a.price, PRICE_SHA))
    assert price["head"] == HEAD
    word = json.loads(gzip.decompress(pinned(a.word, WORD_SHA)))
    result = screen(word, a.cap, a.seconds)
    result.update(head=HEAD, price_sha256=PRICE_SHA, word_sha256=WORD_SHA)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
