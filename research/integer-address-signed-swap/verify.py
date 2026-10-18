#!/usr/bin/env python3
"""Exact finite checks accompanying PROOF.md; standard library, no source imports."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
from fractions import Fraction

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
I = (1, 0, 0, 1)
LABELS = {"a+": (1, 1, 0, 1), "a-": (1, -1, 0, 1),
          "b+": (1, 0, 1, 1), "b-": (1, 0, -1, 1),
          "nx": (-1, 0, 0, 1), "ny": (1, 0, 0, -1)}
TARGETS = {"S": (0, 1, 1, 0), "-S": (0, -1, -1, 0),
           "J": (0, 1, -1, 0), "-J": (0, -1, 1, 0)}
VECTORS = ((1, 0), (1, 1), (0, 1))
PAIRS = ((0, 1), (0, 2), (1, 2), (1, 0), (2, 0), (2, 1))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def mul(x, y):
    a, b, c, d = x
    e, f, g, h = y
    return a*e+b*g, a*f+b*h, c*e+d*g, c*f+d*h


def det(g):
    a, b, c, d = g
    return a*d-b*c


def identity(r):
    return [[{I} if i == j else set() for j in range(r)] for i in range(r)]


def paid(matrix, name, u, v):
    """Right multiply by I+([g]+1)uv^T, with exact F2 group supports."""
    r = len(matrix)
    require(0 < u < 1 << r and 0 < v < 1 << r and (u & v).bit_count() % 2 == 1,
            "not a rank-one idempotent")
    g = LABELS[name]
    result = [[set(entry) for entry in row] for row in matrix]
    for i in range(r):
        p = set()
        for k in range(r):
            if u >> k & 1:
                p ^= matrix[i][k]
        change = p ^ {mul(h, g) for h in p}
        for j in range(r):
            if v >> j & 1:
                result[i][j] ^= change
    return result


def scalar_cnot(matrix, source, target):
    require(source != target, "noninvertible scalar operation")
    result = [[set(entry) for entry in row] for row in matrix]
    for row in result:
        row[target] ^= row[source]
    return result


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length()-1
            if p in pivots:
                row ^= pivots[p]
            else:
                pivots[p] = row
                break
    return len(pivots)


def rep(g, kind):
    a, b, c, d = g
    if kind == "natural":
        return ((a & 1) | ((b & 1) << 1), (c & 1) | ((d & 1) << 1))
    if kind == "sign":
        return (1, 2) if det(g) == 1 else (2, 1)
    permutation = [VECTORS.index(((a*x+b*y) % 2, (c*x+d*y) % 2))
                   for x, y in VECTORS]
    rows = [0]*6
    for j, (x, y) in enumerate(PAIRS):
        i = PAIRS.index((permutation[x], permutation[y]))
        rows[i] ^= 1 << j
    return tuple(rows)


def lift(matrix, kind):
    r = len(matrix)
    dim = 6 if kind == "pairs" else 2
    rows = [0]*(r*dim)
    for i in range(r):
        for j in range(r):
            for g in matrix[i][j]:
                for a, bits in enumerate(rep(g, kind)):
                    for b in range(dim):
                        if bits >> b & 1:
                            rows[a*r+i] ^= 1 << (b*r+j)
    return rows


def cuts(matrix):
    r = len(matrix)
    natural = lift(matrix, "natural")
    pairs = lift(matrix, "pairs")
    sign = lift(matrix, "sign")
    return (rank([row >> r for row in natural[:r]]),
            rank([row & ((1 << r)-1) for row in natural[r:]]),
            rank([row >> (3*r) for row in pairs[:3*r]]),
            rank([row >> r for row in sign[:r]]))


def expected(names, r):
    matrix = identity(r)
    for j, name in enumerate(names):
        matrix[j][j] = {TARGETS[name]}
    return matrix


def words(target, orientation):
    if target == "-J":
        word = ["a-", "b+", "a-"] if orientation == "aba" else ["b+", "a-", "b+"]
    else:
        word = ["a+", "b-", "a+"] if orientation == "aba" else ["b-", "a+", "b-"]
    if target == "S":
        word.append("nx")
    elif target == "-S":
        word.append("ny")
    return word


def counts(word):
    return tuple(sum(name.startswith(prefix) for name in word) for prefix in ("a", "b", "n"))


def sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    retained = json.loads((HERE / "PREDECESSORS.json").read_text(encoding="utf-8"))
    checked = 0
    for item in manifest["files"] + retained["files"]:
        if item["usage"] == "provenance":
            continue
        path = ROOT / item["path"]
        raw = path.read_bytes()
        # Git checkout LF/CRLF conversion is not scientific content drift.
        raw = raw.replace(b"\r\n", b"\n")
        require(hashlib.sha256(raw).hexdigest() == item["sha256"], "source SHA mismatch: " + item["path"])
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == item["git_blob"], "source blob mismatch: " + item["path"])
        checked += 1
    return checked


def run():
    source_count = sources()
    projector_cases = 0
    free_cases = 0
    for r in range(1, 5):
        for u in range(1, 1 << r):
            for v in range(1, 1 << r):
                if (u & v).bit_count() % 2 != 1:
                    continue
                for name in LABELS:
                    want = (1, 0, 1, 0) if name[0] == "a" else ((0, 1, 1, 0) if name[0] == "b" else (0, 0, 0, 1))
                    require(cuts(paid(identity(r), name, u, v)) == want, "projector cut")
                    projector_cases += 1
        for i in range(r):
            for j in range(r):
                if i != j:
                    require(cuts(scalar_cnot(identity(r), i, j)) == (0, 0, 0, 0), "free cut")
                    free_cases += 1

    endpoint_cases = 0
    price_cases = 0
    prices = [Fraction(0), Fraction(1, 3), Fraction(1), Fraction(2), Fraction(7, 2)]
    for n in range(5):
        for names in itertools.product(TARGETS, repeat=n):
            t = sum(det(TARGETS[name]) == -1 for name in names)
            for r in (n, n+1):
                for orientation in ("aba", "bab"):
                    matrix = identity(r)
                    all_words = []
                    for j, target in enumerate(names):
                        for name in words(target, orientation):
                            matrix = paid(matrix, name, 1 << j, 1 << j)
                            all_words.append(name)
                    require(matrix == expected(names, r), "formal endpoint")
                    require(cuts(matrix) == (n, n, 3*n, t), "target cuts")
                    require(counts(all_words) == ((2*n, n, t) if orientation == "aba" else (n, 2*n, t)), "attainer count")
                    endpoint_cases += 1
            for a, b, c in itertools.product(prices, repeat=3):
                count = (2*n, n, t) if a <= b else (n, 2*n, t)
                require(a*count[0]+b*count[1]+c*count[2] == n*(2*min(a,b)+max(a,b))+t*c, "price attainer")
                price_cases += 1

    rng = random.Random(82026)
    prefix_cases = 0
    for r in range(1, 6):
        for _ in range(16):
            matrix = identity(r)
            budget = [0, 0, 0, 0]
            for _ in range(9):
                if r > 1 and rng.randrange(3) == 0:
                    i, j = rng.sample(range(r), 2)
                    matrix = scalar_cnot(matrix, i, j)
                else:
                    while True:
                        u, v = rng.randrange(1, 1 << r), rng.randrange(1, 1 << r)
                        if (u & v).bit_count() % 2:
                            break
                    name = rng.choice(tuple(LABELS))
                    matrix = paid(matrix, name, u, v)
                    charge = (1, 0, 1, 0) if name[0] == "a" else ((0, 1, 1, 0) if name[0] == "b" else (0, 0, 0, 1))
                    budget = [x+y for x,y in zip(budget, charge)]
                require(all(x <= y for x,y in zip(cuts(matrix), budget)), "mixed-prefix rank bound")
                prefix_cases += 1

    controls = {}
    j_matrix = expected(("J",), 2)
    s_matrix = expected(("S",), 2)
    require(j_matrix != s_matrix and cuts(j_matrix)[:3] == cuts(s_matrix)[:3] and cuts(j_matrix)[3] == 0 and cuts(s_matrix)[3] == 1,
            "omitted sign control")
    controls["omitted_neg_detected_only_by_sign_cut"] = True
    perturbed = expected(("S",), 2)
    perturbed[1][0] ^= {I, mul(LABELS["a+"], LABELS["a+"])}
    require(perturbed != s_matrix and all(lift(perturbed, k) == lift(s_matrix, k) for k in ("natural", "pairs", "sign")), "quotient blind spot")
    controls["all_quotients_miss_nonzero_formal_perturbation"] = True
    require(tuple(x % 2 for x in TARGETS["J"]) == tuple(x % 2 for x in TARGETS["S"]), "mod2 control")
    require(all(tuple(x % m for x in TARGETS["J"]) != tuple(x % m for x in TARGETS["S"]) for m in (3,5,7)), "odd moduli control")
    controls["finite_modulus_two_breaks_formal_lower_bound"] = True
    inverses = {"a+":"a-", "a-":"a+", "b+":"b-", "b-":"b+", "nx":"nx", "ny":"ny"}
    for name, inverse in inverses.items():
        require(paid(paid(identity(2), name, 3, 1), inverse, 3, 1) == identity(2), "negative-price identity loop")
    controls["six_negative_price_identity_loops"] = True
    for target in TARGETS:
        word = words(target, "aba")
        for omitted in range(len(word)):
            matrix = identity(1)
            for i, name in enumerate(word):
                if i != omitted:
                    matrix = paid(matrix, name, 1, 1)
            require(matrix != expected((target,), 1), "deleted call")
    controls["fourteen_deleted_attainer_calls_rejected"] = True
    try:
        paid(identity(2), "a+", 1, 2)
    except ValueError:
        controls["nonidempotent_projector_rejected"] = True
    else:
        raise ValueError("accepted nonidempotent")
    rank_two = expected(("S", "S"), 2)
    require(cuts(rank_two)[0] == 2, "higher rank label control")
    controls["higher_rank_unit_would_change_model"] = True
    return {"schema_version": 1, "claim_kind": "finite_checks_for_scoped_proof",
            "source_files": source_count, "rank_one_paid_factor_cases": projector_cases,
            "free_scalar_factor_cases": free_cases, "full_formal_endpoint_cases": endpoint_cases,
            "exact_rational_price_cases": price_cases, "mixed_word_prefix_cases": prefix_cases,
            "controls": controls, "formula": "r*(2*min(A,B)+max(A,B))+t*C",
            "all_register_proof": "PROOF.md", "new_selected_exponent": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path, help="write a NEW receipt path; never replace committed evidence")
    args = parser.parse_args()
    result = run()
    rendered = json.dumps(result, indent=2, sort_keys=True)+"\n"
    if args.write_result:
        with args.write_result.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(rendered)
    else:
        recorded = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
        require(json.dumps(recorded, sort_keys=True) == json.dumps(result, sort_keys=True), "receipt mismatch")
    print(rendered, end="")


if __name__ == "__main__":
    main()
