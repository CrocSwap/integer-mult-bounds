#!/usr/bin/env python3
"""Check the exact group-algebra paired-line identity at small widths."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


ZERO = (F(0), F(0))
ONE = (F(1), F(0))
ID = {0: ONE}


def need(value, message):
    if not value:
        raise ValueError(message)


def zadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def zmul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def add(a, b):
    out = dict(a)
    for j, value in b.items():
        out[j] = zadd(out.get(j, ZERO), value)
        if out[j] == ZERO:
            del out[j]
    return out


def multiply(a, b):
    out = {}
    for i, x in a.items():
        for j, y in b.items():
            k = i ^ j
            out[k] = zadd(out.get(k, ZERO), zmul(x, y))
            if out[k] == ZERO:
                del out[k]
    return out


def negative(a):
    return {j: (-x, -y) for j, (x, y) in a.items()}


def product(a, b):
    return [[add(multiply(a[i][0], b[0][j]), multiply(a[i][1], b[1][j]))
             for j in range(2)] for i in range(2)]


def determinant(a):
    return add(multiply(a[0][0], a[1][1]), negative(multiply(a[0][1], a[1][0])))


def line(f, sign):
    out = dict(ID)
    for j in range(f):
        out = multiply(out, {0: (F(1, 2), F(sign, 2)),
                             1 << j: (F(1, 2), F(-sign, 2))})
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    need(not args.out.exists(), "Use a new output path")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    checks = []
    for f in range(1, 7):
        qpos, qneg = line(f, 1), line(f, -1)
        need(multiply(qpos, qneg) == ID, "The exact line inverse")
        need(len(qpos) == len(qneg) == 2 ** f, "The complete tensor support")
        upper = [[ID, qpos], [{}, ID]]
        lower = [[ID, {}], [negative(qneg), ID]]
        rotation = [[{}, negative(ID)], [ID, {}]]
        target = [[qpos, {}], [{}, qneg]]
        need(product(product(product(upper, lower), upper), rotation) == target,
             "The exact paired-line factor")
        need(determinant(target) == ID, "The target determinant")
        need(determinant([[qpos, {}], [{}, ID]]) == qpos
             and determinant([[qneg, {}], [{}, ID]]) == qneg,
             "The one-call determinant factors")
        shortcut = {0: (F(1, 2), F(1, 2)),
                    (1 << f) - 1: (F(1, 2), F(-1, 2))}
        need((shortcut == qpos) == (f == 1), "The one-position shortcut fails above width one")
        wrong = [[ID, {}], [qneg, ID]]
        need(product(product(product(upper, wrong), upper), rotation) != target,
             "The wrong lower sign is rejected")
        checks.append({"tensor_width": f, "line_support": len(qpos),
                       "paired_identity": True, "inverse": True,
                       "shortcut_rejected": f > 1})
    receipt = {
        "status": "PASS_PAIRED_LINE_SCOPE",
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "checks": checks,
        "scope": "Exact finite examples support the algebraic proof. The general support and translation-only determinant arguments are in PAIRED-LINE-TENSOR-SCOPE.md.",
    }
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
