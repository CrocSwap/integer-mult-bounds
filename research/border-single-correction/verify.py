"""Exact witnesses for the fixed border's one-operation recovery obstruction."""

from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path


N = 4


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity():
    return tuple(tuple(Q(i == j) for j in range(N)) for i in range(N))


def diagonal(values):
    require(len(values) == N, "diagonal dimension")
    return tuple(tuple(Q(values[i]) if i == j else Q(0)
                       for j in range(N)) for i in range(N))


def multiply(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(N))
                       for j in range(N)) for i in range(N))


def inverse(a):
    rows = [list(a[i]) + list(identity()[i]) for i in range(N)]
    for col in range(N):
        pivot = next((i for i in range(col, N) if rows[i][col]), None)
        require(pivot is not None, "singular matrix")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scale = rows[col][col]
        rows[col] = [x / scale for x in rows[col]]
        for row in range(N):
            if row != col:
                scale = rows[row][col]
                rows[row] = [x - scale * y
                             for x, y in zip(rows[row], rows[col])]
    result = tuple(tuple(row[N:]) for row in rows)
    require(multiply(a, result) == identity(), "inverse postcondition")
    return result


def rank(a):
    rows = [list(row) for row in a]
    found = 0
    for col in range(N):
        pivot = next((i for i in range(found, N) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[found], rows[pivot] = rows[pivot], rows[found]
        scale = rows[found][col]
        rows[found] = [x / scale for x in rows[found]]
        for row in range(found + 1, N):
            scale = rows[row][col]
            rows[row] = [x - scale * y
                         for x, y in zip(rows[row], rows[found])]
        found += 1
    return found


def difference(a, b):
    return tuple(tuple(a[i][j] - b[i][j] for j in range(N))
                 for i in range(N))


def query(u, v, central):
    return tuple(tuple(Q(i == j) + (central - 1) * u[i] * v[j]
                       for j in range(N)) for i in range(N))


def factors(e, a, b, c, central=-1):
    e, a, b, c, central = map(Q, (e, a, b, c, central))
    require(all((e, a, b, c)), "zero parameter")
    require(central in (-1, 1), "central character")
    us = ((1, 0, 0, 0), (-1/e, 1, 0, 0), (-e, 0, 1, 0),
          (-e, 0, 1, -1), (1, 0, 0, 1/e))
    vs = ((0, 1/e, 0, 0), (0, 1, -e*e, 0), (-1/e, 0, -1, 0),
          (-1/e, 0, 0, 0), (-1, 0, 0, e))
    stages = ((a, a, 1, 1), (1, 1, 1, 1), (b, 1, b, 1),
              (1, 1, 1, 1), (c, 1, 1, c))
    return tuple(multiply(diagonal(d), query(u, v, central))
                 for u, v, d in zip(us, vs, stages))


def product(items):
    require(len(items) <= 7, "word length")
    value = identity()
    for item in items:
        value = multiply(item, value)
    return value


def target(a, b, c, central=-1):
    return diagonal((central*a*b*c, central*a, central*b, central*c))


def required_at_cut(word, goal, cut):
    require(0 <= cut <= 5 and len(word) == 5, "cut domain")
    prefix, suffix = product(word[:cut]), product(word[cut:])
    value = multiply(multiply(inverse(suffix), goal), inverse(prefix))
    require(multiply(multiply(suffix, value), prefix) == goal,
            "required correction identity")
    return value


def table(b):
    b = Q(b)
    require(b != 0, "zero middle stage")
    return (
        ((1, 0, 0, -2/b), (0, 1, 2, 0), (0, 0, 1, 0), (0, 0, 0, 1)),
        ((1, 0, -4, -2/b), (0, 1, 2, 0), (0, 0, 1, 0), (0, 0, 0, 1)),
        ((1, 0, 0, -2/b), (0, 1, -2, 0), (0, 0, 1, 0), (0, 0, 0, 1)),
        ((1, 0, 0, 2), (4/b, 1, 2/b, 0), (0, 0, 1, -4), (0, 0, 0, 1)),
        ((5, 0, 0, -2), (0, 1, 2/b, 0), (0, 0, 1, 0), (8, 0, 0, -3)),
        ((1, 0, 0, -2), (0, 1, 2/b, 0), (0, 0, 1, 0), (0, 0, 0, 1)),
    )


def check_cut(e, cut):
    corrections = []
    for b in (Q(1), Q(-1)):
        word = factors(e, 1, b, 1)
        correction = required_at_cut(word, target(1, b, 1), cut)
        gauge = diagonal((e, 1, e*e, e*e))
        expected = multiply(multiply(inverse(gauge), table(b)[cut]), gauge)
        require(correction == expected, "similarity/table mismatch")
        require(rank(difference(correction, identity())) == 2,
                "required correction must have rank-two displacement")
        corrections.append(correction)
    require(corrections[0] != corrections[1], "stage dependence missing")
    word = factors(e, 1, -1, 1)
    wrong = word[:cut] + (corrections[0],) + word[cut:]
    require(product(wrong) != target(1, -1, 1), "frozen correction accepted")
    return {"e": str(e), "cut": cut,
            "required_plus": [[str(x) for x in row] for row in corrections[0]],
            "required_minus": [[str(x) for x in row] for row in corrections[1]]}


def check_two_corrections(e, a, b, c, central):
    word = factors(e, a, b, c, central)
    first = query((0, e*e, 0, 0), (0, 0, 1, 0), central)
    last = query((e, 0, 0, 0), (0, 0, 0, 1), central)
    repaired = word[:2] + (first,) + word[2:] + (last,)
    require(product(repaired) == target(a, b, c, central),
            "cited two-correction attainment")


def rejection_controls():
    controls = (
        ("zero border", lambda: factors(0, 1, 1, 1)),
        ("zero stage", lambda: factors(1, 1, 0, 1)),
        ("central domain", lambda: factors(1, 1, 1, 1, 0)),
        ("cut domain", lambda: required_at_cut(factors(1, 1, 1, 1), identity(), 6)),
        ("singular inverse", lambda: inverse(diagonal((0, 1, 1, 1)))),
    )
    for name, action in controls:
        try:
            action()
        except ValueError:
            continue
        raise ValueError("control accepted: " + name)
    return [name for name, _ in controls]


def main():
    parameters = tuple(map(Q, (1, -1, "1/2", "-1/2", 2, 3)))
    witnesses = [check_cut(e, cut) for e in parameters for cut in range(6)]
    for b in map(Q, (1, -1, 2, -2, 3, -3)):
        word = factors(1, 1, b, 1)
        for cut in range(6):
            require(required_at_cut(word, target(1, b, 1), cut) == table(b)[cut],
                    "normalized table fixture")
    attainment = 0
    for e in parameters:
        for a, b, c in ((1, 1, 1), (2, 3, 5), (-1, 2, -3), (3, -1, 2)):
            for central in (-1, 1):
                check_two_corrections(e, Q(a), Q(b), Q(c), central)
                attainment += 1
    controls = rejection_controls()
    package = Path(__file__).resolve().parent
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(package.iterdir()) if p.is_file()}
    print(json.dumps({"status": "PASS_BORDER_SINGLE_CORRECTION",
                      "cut_parameter_witnesses": witnesses,
                      "normalized_table_checks": 36,
                      "two_correction_fixtures": attainment,
                      "rejection_controls": controls,
                      "package_sha256": hashes}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
