#!/usr/bin/env python3
"""Second checker: sparse block matrices and rightmost whole-word reduction.

Copyright 2026 Sricharan Vagvala (@theon199). Apache-2.0.
Substantial OpenAI Codex assistance. Does not import verify.py or PR1998 code.
"""
from hashlib import sha256
from pathlib import Path
import gzip
import json

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
RECIPE = "research/community-reconciliation-third100-audit/regenerated/pr377-outputs/work/odd-stages/RECIPE-9.json.gz"
RECIPE_HASH = "910fffd7b8980f1130d8bbec56d5ac34f92986c2a2c480b6aea40754b4b832ac"
SPACES = ["V"] * 8 + ["L"] * 9
N = 17


def ensure(ok, message):
    if not ok:
        raise ValueError(message)


def operator_type(name):
    ensure(type(name) is str and len(name) == 2 and name[0] in "RPZ"
           and name[1] in "012345678", "invalid operator")
    return ("V", "L") if name[0] == "R" else ("L", "V")


def reduce_right(word):
    # Repeatedly scan the whole word from the right; no stack or encoded tokens.
    symbols = list(word)
    while True:
        for i in range(len(symbols) - 2, -1, -1):
            first, second = symbols[i:i + 2]
            if first[0] == "R" and second[0] in "PZ" and first[1] == second[1]:
                symbols[i:i + 2] = []
                break
        else:
            return tuple(symbols)


def poly_sum(left, right):
    out = dict(left)
    for word, value in right.items():
        out[word] = out.get(word, 0) + value
        if out[word] == 0:
            del out[word]
    return out


def poly_product(left, right):
    out = {}
    for first, x in left.items():
        for second, y in right.items():
            word = reduce_right(first + second)
            out[word] = out.get(word, 0) + x * y
            if out[word] == 0:
                del out[word]
    return out


def eye():
    return [{i: {(): 1}} for i in range(N)]


def matrix_product(left, right):
    out = [{} for _ in range(N)]
    for i, row in enumerate(left):
        for k, first in row.items():
            for j, second in right[k].items():
                value = poly_sum(out[i].get(j, {}), poly_product(first, second))
                if value:
                    out[i][j] = value
                elif j in out[i]:
                    del out[i][j]
    return out


def read_matrix(rows):
    ensure(type(rows) is list and len(rows) == N, "invalid block matrix")
    out = [{} for _ in range(N)]
    for i, row in enumerate(rows):
        ensure(row["codomain"] == SPACES[i], "wrong output module")
        for j, coefficient, symbols in row["terms"]:
            ensure(type(j) is int and 0 <= j < N, "invalid input index")
            ensure(type(coefficient) is int and coefficient != 0, "invalid coefficient")
            ensure(type(symbols) is list, "invalid word")
            space = SPACES[j]
            for name in reversed(symbols):
                source, target = operator_type(name)
                ensure(space == source, "ill-typed certificate word")
                space = target
            ensure(space == SPACES[i], "wrong word endpoint")
            word = tuple(symbols)
            ensure(reduce_right(word) == word, "certificate word is not reduced")
            ensure(word not in out[i].get(j, {}), "duplicate certificate monomial")
            out[i].setdefault(j, {})[word] = coefficient
    return out


def elementary(event):
    # Assemble the entire elementary block matrix before multiplying it into W.
    out = eye()
    if event["kind"] == "bridge":
        d, s, c = event["dst"], event["src"], event["coefficient"]
        out[d][s] = {(): c}
        out[4 + s][4 + d] = {(): -c}
    else:
        ensure(event["kind"] == "local", "unknown controller event")
        s, x = event["stage"], event["pair"]
        y, log = 4 + x, 8 + s
        r, p, z = (kind + str(s) for kind in "RPZ")
        if event["reverse"]:
            out[x][y] = {(): -1}
            out[y] = {y: {(): 1, (p, r): -1}, log: {(z,): 1}}
            out[log] = {y: {(r,): 1}}
        else:
            source = {(): 1, (z, r): -1}
            out[x] = {x: source, log: {(p,): 1}}
            out[y] = {y: {(): 1}, x: source, log: {(p,): 1}}
            out[log] = {x: {(r,): 1}}
    return out


def audit(certificate, recipe):
    word = read_matrix(certificate["forward"])
    decoder = read_matrix(certificate["decoder"])
    rebuilt = eye()
    for event in recipe:
        if event["kind"] != "terminal":
            rebuilt = matrix_product(elementary(event), rebuilt)
    ensure(word == rebuilt, "forward certificate disagrees with elementary matrices")
    ensure(matrix_product(decoder, word) == eye(), "left inverse certificate failed")
    ensure(matrix_product(word, decoder) == eye(), "right inverse certificate failed")
    hidden = {9, 11, 13, 15}
    ensure(all(not (set(word[i]) & hidden) for i in [0, 1, 2, 3, *range(8, 17)]),
           "hidden-log certificate failed")
    return {"two_sided_block_identities": 578,
            "forward_monomials": sum(len(p) for row in word for p in row.values()),
            "decoder_monomials": sum(len(p) for row in decoder for p in row.values()),
            "maximum_word_length": max(len(w) for matrix in (word, decoder)
                                       for row in matrix for p in row.values() for w in p)}


def main():
    raw = (ROOT / RECIPE).read_bytes()
    ensure(sha256(raw).hexdigest() == RECIPE_HASH, "controller source drift")
    payload = gzip.decompress((PACKAGE / "CERTIFICATE.json.gz").read_bytes())
    result = audit(json.loads(payload), json.loads(gzip.decompress(raw)))
    print("PASS_PAIRED_LOG_BLOCK_CERTIFICATE " + " ".join(
        name + "=" + str(value) for name, value in result.items()))


if __name__ == "__main__":
    main()
