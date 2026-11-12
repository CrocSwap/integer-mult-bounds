"""Pinned rational chart capacities and monotone support check."""
from collections import Counter
from fractions import Fraction
import gzip
import json


def rational_rank(matrix):
    rows = [list(map(Fraction, row)) for row in matrix]
    rank = 0
    for column in range(8):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [x / scale for x in rows[rank]]
        for i in range(rank + 1, len(rows)):
            scale = rows[i][column]
            if scale:
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[rank], strict=True)]
        rank += 1
    return rank


def scan(path):
    # The package's read_rows authenticates the same live input before this scan.
    word = json.loads(gzip.decompress(path.read_bytes()))
    frames = {int(i): frame for i, frame in word["frames"].items()}
    lines = [tuple(map(Fraction, frames[i]["B"][0])) for i in word["start"][:111]]
    masks = {}
    capacities = Counter()
    for index, frame in frames.items():
        basis = frame["B"]
        annihilator = [tuple(map(Fraction, row)) for row in frame["A"]]
        rank = frame["dim"]
        assert len(basis) == rational_rank(basis) == rank
        assert len(annihilator) == rational_rank(annihilator) == 8 - rank
        assert all(sum(x*y for x,y in zip(a,b,strict=True)) == 0
                   for a in annihilator for b in basis)
        support = sum(1 << i for i, line in enumerate(lines)
                      if all(not sum(x*y for x,y in zip(line, row, strict=True)) for row in annihilator))
        masks[index] = support
        capacities[rank] = max(capacities[rank], support.bit_count())

    cur = word["start"] + [None] * word["owned_fields"]
    public = 0
    for op, r, *args in word["program"]:
        if op == "MOVE":
            a, b = args
            assert cur[r] == a
            if r < word["public"]:
                assert frames[a]["dim"] < frames[b]["dim"] and masks[a] & ~masks[b] == 0
                public += 1
            else:
                assert frames[a]["dim"] == 7 and b == 0
            cur[r] = b
        elif op == "ADD":
            assert cur[r] == cur[args[0]] == args[1]
        elif op == "INIT":
            assert cur[r] is None
            cur[r] = args[0]
        elif op == "CLEAR":
            assert cur[r] == args[0]
            cur[r] = None
        else:
            assert op == "SWAP"
            other = args[0]
            cur[r], cur[other] = cur[other], cur[r]
    assert public == 2862 and cur == word["final"] + [None] * word["owned_fields"]
    return dict(capacities), sorted({masks[i] for i, frame in frames.items() if frame["dim"] == 6})
