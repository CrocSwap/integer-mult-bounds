"""Recover the nine-coordinate separator from eight independent observed rows."""
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path

COORDINATES = (663, 770, 780, 825, 1055, 1225, 1238, 1239, 1288)
PIVOT_ROWS = (88878, 88896, 90590, 90592, 94158, 95493, 95884, 103651)
TERMINAL = 155442


def normalized_kernel(rows):
    """Solve the eight homogeneous constraints and the unit output constraint."""
    size = len(rows)
    augmented = [list(v) + [int(i == size-1)] for i,v in enumerate(rows)]
    for i in range(size):
        pivot = next((j for j in range(i, size) if augmented[j][i]), None)
        if pivot is None:
            raise ValueError("Chosen witnesses do not single out a ray on these coordinates")
        augmented[i], augmented[pivot] = augmented[pivot], augmented[i]
        scale = augmented[i][i]
        augmented[i] = [Fraction(x, scale) for x in augmented[i]]
        for j in range(size):
            if j != i and augmented[j][i]:
                scale = augmented[j][i]
                augmented[j] = [x-scale*y for x,y in zip(augmented[j], augmented[i], strict=True)]
    return tuple(v[-1] for v in augmented)


def main():
    path = Path(__file__).parent / "retained" / "WORD.json.gz"
    data = gzip.decompress(path.read_bytes())
    if sha256(data).hexdigest() != "c447b6d5ba956fbe40834fe3c1bc69af2f225736f1b97ecd84b57bab9dd283cb":
        raise ValueError("Unexpected rational word")
    word = json.loads(data)
    forms = {k: [(j,Fraction(a)) for j,a in row] for k,row in word["forms"]}

    @cache
    def restriction(k):
        if k < 0:
            return tuple(int(~k == j) for j in COORDINATES)
        out = [0]*len(COORDINATES)
        for source, a in forms[k]:
            for i, coeff in enumerate(restriction(source)):
                if coeff:
                    out[i] += a*coeff
        return tuple(out)

    local = [~j for j,c in enumerate(word["initial"]) if c in (11,58)]
    receiver = []
    for k, a, b in word["moves"]:
        if b in (11,58) or (a,b) == (3,278):
            local.append(k)
        elif b == 127 and k != 88:
            receiver.append(k)
    stocks = local + receiver
    if (len(local),len(receiver)) != (18,901) or not set(PIVOT_ROWS) <= set(stocks):
        raise ValueError("Unexpected observed row set")
    ray = normalized_kernel([restriction(k) for k in (*PIVOT_ROWS, TERMINAL)])
    observed = lambda k: sum(a*b for a,b in zip(restriction(k), ray, strict=True))
    if not all(ray) or any(observed(k) for k in stocks) or observed(TERMINAL) != 1:
        raise ValueError("Incomplete observation nullspace or incorrect normalization")
    print("PASS 919 projected stock rows, rank eight on the chosen nine coordinates.")
    print("Unique separator with unit output on this support:", *ray)


if __name__ == "__main__":
    main()
