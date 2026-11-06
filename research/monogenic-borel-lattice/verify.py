"""Read-only exact corroboration; no predecessor executable is imported."""

import hashlib
import importlib.util
import itertools
import json
from fractions import Fraction as F
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_constructor():
    path = Path(__file__).with_name("lattice.py")
    spec = importlib.util.spec_from_file_location("monogenic_lattice", path)
    require(spec is not None and spec.loader is not None, "module loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def mul(a, b):
    return tuple(tuple(sum(x * y for x, y in zip(row, col, strict=True))
                       for col in zip(*b, strict=True)) for row in a)


def eye(n):
    return tuple(tuple(F(i == j) for j in range(n)) for i in range(n))


def inverse(a):
    n = len(a)
    rows = [list(row) + list(unit) for row, unit in zip(a, eye(n), strict=True)]
    for j in range(n):
        candidates = [i for i in range(j, n) if rows[i][j]]
        require(bool(candidates), "singular basis")
        i = candidates[0]
        rows[i], rows[j] = rows[j], rows[i]
        pivot = rows[j][j]
        rows[j] = [x / pivot for x in rows[j]]
        for i in range(n):
            if i != j:
                ratio = rows[i][j]
                rows[i] = [x - ratio * y for x, y in zip(rows[i], rows[j], strict=True)]
    result = tuple(tuple(row[n:]) for row in rows)
    require(mul(a, result) == eye(n), "inverse residual")
    return result


def det_characteristic(a):
    """Leibniz expansion of det(xI-A), independent of the trace recurrence."""
    n = len(a)
    result = [F(0)] * (n + 1)
    for permutation in itertools.permutations(range(n)):
        sign = (-1) ** sum(permutation[i] > permutation[j]
                           for i in range(n) for j in range(i + 1, n))
        term = [F(sign)]
        for i, j in enumerate(permutation):
            factor = [-a[i][j], F(i == j)]
            expanded = [F(0)] * (len(term) + 1)
            for k, x in enumerate(term):
                for ell, y in enumerate(factor):
                    expanded[k + ell] += x * y
            term = expanded
        result = [x + y for x, y in zip(result, term, strict=True)]
    return tuple(reversed(result))


def integral_matrix(a):
    return all(x.denominator % 2 for row in a for x in row)


def check(t, certificate):
    """Check certificates from original entries without importing the solver."""
    coefficients = det_characteristic(t)
    bad = [i for i, x in enumerate(coefficients) if x.denominator % 2 == 0]
    if certificate["kind"] == "obstruction":
        index = certificate["index"]
        require(index in bad, "false nonintegrality obstruction")
        require(certificate["coefficient"] == coefficients[index], "wrong coefficient")
        return False
    require(certificate["kind"] == "basis" and not bad, "invalid certificate kind")
    b = certificate["basis"]
    n = len(t)
    require(len(b) == n and all(len(row) == n for row in b), "basis shape")
    back = inverse(b)
    require(integral_matrix(mul(mul(back, t), b)), "basis is not stable")
    power = eye(n)
    for _ in range(n):
        require(integral_matrix(mul(back, power)), "missing lattice generator")
        power = mul(t, power)
    return True


def rejection(function, *args):
    try:
        function(*args)
    except (ValueError, ArithmeticError):
        return 1
    raise ValueError("a rejection control was accepted")


def finite_corpus(constructor):
    accepted = rejected = 0
    values = tuple(F(x, 2) for x in range(-2, 3))
    for entries in itertools.product(values, repeat=4):
        t = (entries[:2], entries[2:])
        require(constructor.characteristic(t) == det_characteristic(t), "charpoly disagreement")
        good = check(t, constructor.solve(t))
        accepted += good
        rejected += not good
    require(accepted + rejected == 625, "corpus coverage")
    return {"two_by_two": 625, "stable": accepted, "obstructed": rejected}


def nonsplit(s):
    q = 2 ** s
    return ((F(1, q), F(1, q), F(0)),
            (F(-q * q - 1, q), F(-1, q), F(0)),
            (F(0), F(0), F(0)))


def block(a, b, c, d):
    return tuple(tuple(x + y) for x, y in zip(a, b, strict=True)) + tuple(
        tuple(x + y) for x, y in zip(c, d, strict=True))


def add(a, b, coefficient=1):
    return tuple(tuple(x + coefficient * y for x, y in zip(row, other, strict=True))
                 for row, other in zip(a, b, strict=True))


def example_word(t):
    """Six local labels in application order, paid ranks 1 then 2."""
    n = len(t)
    one = eye(n)
    zero = tuple(tuple(F(0) for _ in range(n)) for _ in range(n))
    q = add(one, mul(t, t))
    require(q == ((F(0), F(0), F(0)), (F(0), F(0), F(0)),
                  (F(0), F(0), F(1))), "rank-one paid projector")
    require(t[0][0] * t[1][1] - t[0][1] * t[1][0] == 1
            and all(t[2][i] == t[i][2] == 0 for i in range(3)), "rank-two paid matrix")
    x = add(q, t, -1)
    x_back = add(q, t)
    require(mul(x, x_back) == one, "normalizer inverse")
    lower = block(one, zero, t, one)
    lower_back = block(one, zero, add(zero, t, -1), one)
    labels = (lower_back, block(x_back, zero, zero, one),
              block(one, q, zero, one), block(one, t, zero, one),
              block(x, zero, zero, one), lower)
    expected = mul(mul(lower, block(one, one, zero, one)), lower_back)
    actual = eye(2 * n)
    for label in labels:
        actual = mul(label, actual)
    require(actual == expected, "complete local endpoint")
    require(tuple(tuple(actual[i][j] for j in range(n, 2 * n))
                  for i in range(n)) == one, "target is not a unit")
    require(mul(lower, labels[3]) != mul(labels[3], lower), "labels became abelian")
    return labels, expected


def formal_endpoint(labels, expected):
    """Literal F2[group] replay: mix two data roles, leave a dirty role intact."""
    unit = eye(6)
    state = [[{unit} if i == j else set() for j in range(3)] for i in range(3)]
    for j in range(3):
        state[0][j] ^= state[1][j]
    for role in range(2):
        for label in labels:
            state[role] = [{mul(label, g) for g in entry} for entry in state[role]]
    for j in range(3):
        state[0][j] ^= state[1][j]
    wanted = [[{expected if i < 2 else unit} if i == j else set()
               for j in range(3)] for i in range(3)]
    require(state == wanted, "formal data/dirty endpoint")


def separating_family(constructor):
    for s in range(1, 9):
        t = nonsplit(s)
        require(det_characteristic(t) == (F(1), F(0), F(1), F(0)), "family polynomial")
        require(t[0][0].denominator == 2 ** s, "diagonal-gauge obstruction")
        check(t, constructor.solve(t))
        q = 2 ** s
        explicit = ((F(1), F(1, q), F(0)),
                    (F(0), F(-q * q - 1, q), F(0)),
                    (F(0), F(0), F(1)))
        companion = ((F(0), F(-1), F(0)), (F(1), F(0), F(0)),
                     (F(0), F(0), F(0)))
        require(mul(mul(inverse(explicit), t), explicit) == companion, "explicit chart")
        labels, expected = example_word(t)
        b = constructor.solve(t)["basis"]
        zero = tuple(tuple(F(0) for _ in range(3)) for _ in range(3))
        paired = block(b, zero, zero, b)
        back = inverse(paired)
        for label in labels:
            require(integral_matrix(mul(mul(back, label), paired)), "applied label is nonintegral")
        formal_endpoint(labels, expected)
    return {"family_parameters": 8, "formal_words": 8, "paid_rank_per_data_role": 3}


def controls(constructor):
    t = nonsplit(1)
    certificate = constructor.solve(t)
    count = rejection(check, t, {"kind": "basis", "basis": eye(3)})
    count += rejection(check, t, {"kind": "basis", "basis": ((F(0),) * 3,) * 3})
    count += rejection(check, t, {"kind": "obstruction", "index": 2, "coefficient": F(1)})
    bad = ((F(1, 2),),)
    count += rejection(check, bad, {"kind": "basis", "basis": eye(1)})
    count += rejection(check, bad, {"kind": "obstruction", "index": 1, "coefficient": F(1, 2)})
    for invalid in ([], [[0, 0]], [[0.5]], [[True]], [[2 ** 65]], [[0]] * 5):
        count += rejection(constructor.solve, invalid)
    b = certificate["basis"]
    check(t, certificate)
    # An applied inverse is additional input: 2I is stable, (2I)^-1 is not.
    require(integral_matrix(mul(mul(inverse(b), tuple(tuple(2 * x for x in row)
            for row in eye(3))), b)), "singular reduction control")
    require(not integral_matrix(tuple(tuple(x / 2 for x in row) for row in eye(3))),
            "applied inverse was silently admitted")
    require(not integral_matrix(mul(mul(inverse(b),
            tuple(tuple(x / 2 for x in row) for row in t)), b)),
            "nonintegral polynomial coefficient was silently admitted")
    one = eye(3)
    zero = tuple(tuple(F(0) for _ in range(3)) for _ in range(3))
    unpaired = block(one, zero, zero, add(one, one))
    target = mul(mul(inverse(unpaired), block(one, one, zero, one)), unpaired)
    hd = tuple(tuple(target[i][j] for j in range(3, 6)) for i in range(3))
    require(det_characteristic(hd)[-1].numerator % 2 == 0,
            "independent H/D scaling did not destroy the target unit")
    # If T is not applied, its bad characteristic coefficient proves nothing about I.
    require(not check(bad, constructor.solve(bad)) and check(eye(1), constructor.solve(eye(1))),
            "unapplied-generator control")
    labels, expected = example_word(t)
    count += rejection(formal_endpoint, labels[1:], expected)
    return {"rejections": count, "scope_controls": 5}


def main():
    constructor = load_constructor()
    results = finite_corpus(constructor)
    results.update(separating_family(constructor))
    results.update(controls(constructor))
    # Include dimensions 1 and 4, repeated factors and odd denominators.
    for t in (((F(2, 3),),), eye(4),
              ((F(0), F(1, 2)), (F(0), F(0))),
              tuple(tuple(F(1, 2) if j == i + 1 else F(0)
                          for j in range(4)) for i in range(4))):
        check(t, constructor.solve(t))
    results["extra_matrices"] = 4
    package = Path(__file__).resolve().parent
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(package.iterdir()) if p.is_file()}
    print(json.dumps({"status": "PASS_MONOGENIC_BOREL_LATTICE", "results": results,
                      "package_sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
