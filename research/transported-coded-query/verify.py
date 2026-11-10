"""Exact ordered-ring identity and separate finite-vector corroboration.

No predecessor executable is imported. All domains are fixed below.
"""

import hashlib
import itertools
import json
import platform
from pathlib import Path

Word = tuple[int, ...]
Poly = dict[Word, int]
Matrix = list[list[Poly]]
Pair = tuple[int, int]
Small = tuple[int, int, int, int]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def constant(n: int) -> Poly:
    return {(): n} if n else {}


def letter(n: int) -> Poly:
    require(1 <= abs(n) <= 4, "unknown free-group generator")
    return {(n,): 1}


def reduced(word: Word) -> Word:
    require(len(word) <= 64, "word capacity")
    stack: list[int] = []
    for token in word:
        if stack and stack[-1] == -token:
            stack.pop()
        else:
            stack.append(token)
    return tuple(stack)


def plus(a: Poly, b: Poly) -> Poly:
    require(len(a) <= 128 and len(b) <= 128, "polynomial input capacity")
    out = a.copy()
    for word, coefficient in b.items():
        out[word] = out.get(word, 0) + coefficient
    out = {word: coefficient for word, coefficient in out.items() if coefficient}
    require(len(out) <= 128, "polynomial output capacity")
    return out


def negative(a: Poly) -> Poly:
    return {word: -coefficient for word, coefficient in a.items()}


def times(a: Poly, b: Poly) -> Poly:
    require(len(a) <= 128 and len(b) <= 128, "product input capacity")
    out: Poly = {}
    for first, c in a.items():
        for second, d in b.items():
            word = reduced(first + second)
            out[word] = out.get(word, 0) + c * d
    out = {word: coefficient for word, coefficient in out.items() if coefficient}
    require(len(out) <= 128, "product output capacity")
    return out


def scalar_matrix(rows: list[list[int]]) -> Matrix:
    require(len(rows) == 4 and all(len(row) == 4 for row in rows), "matrix shape")
    return [[constant(n) for n in row] for row in rows]


def identity() -> Matrix:
    return scalar_matrix([[int(i == j) for j in range(4)] for i in range(4)])


def product(a: Matrix, b: Matrix) -> Matrix:
    out = identity()
    for i in range(4):
        for j in range(4):
            value: Poly = {}
            for k in range(4):
                value = plus(value, times(a[i][k], b[k][j]))
            out[i][j] = value
    return out


def operations(c: Poly, variant: str = "correct") -> list[Matrix]:
    a, b, q, qi = letter(1), letter(2), letter(3), letter(-3)
    h = times(a, b)
    r = scalar_matrix([[1, 0, 0, 1], [0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]])
    s = identity()
    s[0][2] = constant(1)
    si = identity()
    si[0][2] = constant(-1)
    ell = scalar_matrix([[1, 0, 0, 0], [0, 0, 0, 1], [1, 0, -1, 0], [0, -1, 0, 1]])
    thin = identity()
    thin[2][1], thin[2][3] = negative(q), q
    idle = identity()
    idle[2][2], idle[3][3] = h, h
    if variant == "missing_idle":
        idle[2][2] = constant(1)
    if variant == "reversed_idle":
        idle[2][2] = idle[3][3] = times(b, a)
    child_b = identity()
    child_b[0][0] = child_b[1][1] = b
    child_b[1][0] = negative(times(b, q if variant == "wrong_lower" else qi))
    child_a = identity()
    child_a[0][0] = child_a[1][1] = a
    child_a[0][1] = times(a, c)
    children = [child_b, child_a]
    if variant == "reversed_children":
        children = [child_a, child_b]
    return [r, thin, si, idle, *children, s, ell]


def chronological(ops: list[Matrix]) -> Matrix:
    require(len(ops) == 8, "fixed eight-operation scaffold")
    out = identity()
    for operation in ops:
        out = product(operation, out)
    return out


def target() -> Matrix:
    h = times(letter(1), letter(2))
    out = identity()
    for i in range(4):
        out[i][i] = h
    out[0][1] = out[2][2] = times(h, letter(3))
    out[3][3] = times(h, letter(-3))
    return out


def formal_checks() -> dict[str, int]:
    a, b, q, bi = letter(1), letter(2), letter(3), letter(-2)
    transported = times(times(b, q), bi)
    expected = target()
    require(chronological(operations(transported)) == expected, "transported endpoint")
    arbitrary = letter(4)
    actual = chronological(operations(arbitrary))
    defect = plus(times(times(a, arbitrary), b), negative(times(times(a, b), q)))
    residual = scalar_matrix([[0] * 4 for _ in range(4)])
    for row in (0, 2):
        residual[row][1] = defect
        residual[row][3] = negative(times(defect, letter(-3)))
    for i in range(4):
        for j in range(4):
            require(plus(actual[i][j], negative(expected[i][j])) == residual[i][j],
                    "complete residual formula")
    variants = ("missing_idle", "reversed_idle", "wrong_lower", "reversed_children")
    for variant in variants:
        require(chronological(operations(transported, variant)) != expected, variant)
    require(chronological(operations(q)) != expected, "untransported query control")
    backwards = times(times(bi, q), b)
    require(chronological(operations(backwards)) != expected, "conjugation direction")
    for left, right in ((a, b), (a, q), (b, q)):
        require(times(left, right) != times(right, left), "free noncommutation retained")
    return {"symbolic_endpoint_entries": 16, "symbolic_residual_entries": 16,
            "symbolic_rejecting_mutants": 6, "retained_commutators": 3}


def lowered_bridge(recipe: list[tuple[str, int, int]]) -> Matrix:
    require(len(recipe) <= 5, "bridge recipe capacity")
    out = identity()
    for kind, destination, source in recipe:
        require(0 <= destination < 4 and 0 <= source < 4, "bridge field")
        operation = identity()
        if kind == "swap":
            operation[destination], operation[source] = operation[source], operation[destination]
        elif kind == "negate":
            operation[destination][destination] = constant(-1)
        else:
            require(destination != source, "bridge addition fields")
            require(kind in ("add", "subtract", "query"), "bridge operation")
            operation[destination][source] = letter(3) if kind == "query" else constant(
                -1 if kind == "subtract" else 1)
        out = product(operation, out)
    return out


def bridge_checks() -> dict[str, int]:
    recipes = [
        [("add", 3, 0), ("swap", 0, 3), ("swap", 1, 2), ("swap", 2, 3)],
        [("subtract", 3, 1), ("query", 2, 3), ("add", 3, 1)],
        [("subtract", 0, 2)],
        [("add", 0, 2)],
        [("negate", 2, 2), ("add", 2, 0), ("negate", 1, 1),
         ("add", 1, 3), ("swap", 1, 3)],
    ]
    abstract = operations(letter(3))
    for recipe, index in zip(recipes, (0, 1, 2, 6, 7), strict=True):
        require(lowered_bridge(recipe) == abstract[index], "in-place bridge lowering")
    counts = {kind: 0 for kind in ("add", "subtract", "swap", "negate", "query")}
    for recipe in recipes:
        for kind, _, _ in recipe:
            counts[kind] += 1
    require(counts == {"add": 5, "subtract": 2, "swap": 4, "negate": 2, "query": 1},
            "literal ordinary-operation census")
    rejected = 0
    for n in (0, 5):
        try:
            letter(n)
        except ValueError:
            rejected += 1
    try:
        reduced((1,) * 65)
    except ValueError:
        rejected += 1
    require(rejected == 3, "symbolic domain/capacity controls")
    return {"ordinary_additions_subtractions": 7, "ordinary_swaps": 4,
            "ordinary_negations": 2, "thin_queries": 1, "symbolic_domain_rejections": rejected}


def smul(a: Small, b: Small, p: int) -> Small:
    return tuple(sum(a[2 * i + k] * b[2 * k + j] for k in range(2)) % p
                 for i in range(2) for j in range(2))


def inverse(a: Small, p: int) -> Small:
    require(p in (2, 3), "prime field domain")
    determinant = (a[0] * a[3] - a[1] * a[2]) % p
    require(determinant != 0, "singular operator")
    d = pow(determinant, -1, p)
    return tuple(d * x % p for x in (a[3], -a[1], -a[2], a[0]))


def apply(a: Small, v: Pair, p: int) -> Pair:
    return ((a[0] * v[0] + a[1] * v[1]) % p,
            (a[2] * v[0] + a[3] * v[1]) % p)


def vadd(v: Pair, w: Pair, p: int) -> Pair:
    return ((v[0] + w[0]) % p, (v[1] + w[1]) % p)


def vsub(v: Pair, w: Pair, p: int) -> Pair:
    return ((v[0] - w[0]) % p, (v[1] - w[1]) % p)


def literal(a: Small, b: Small, q: Small, c: Small, p: int,
            state: tuple[Pair, ...]) -> tuple[Pair, ...]:
    """Direct vector operations, with no polynomial or 4-by-4 matrix engine."""
    x, y, u, v = state
    h, qi = smul(a, b, p), inverse(q, p)
    x, y, u, v = vadd(x, v, p), u, x, y
    u = vadd(u, apply(q, vsub(v, y, p), p), p)
    x = vsub(x, u, p)
    u, v = apply(h, u, p), apply(h, v, p)
    x, y = apply(b, x, p), apply(b, vsub(y, apply(qi, x, p), p), p)
    x, y = apply(a, vadd(x, apply(c, y, p), p), p), apply(a, y, p)
    x = vadd(x, u, p)
    return x, v, vsub(x, u, p), vsub(v, y, p)


def expected_vectors(a: Small, b: Small, q: Small, p: int,
                     state: tuple[Pair, ...]) -> tuple[Pair, ...]:
    x, y, u, v = state
    h = smul(a, b, p)
    return (apply(h, vadd(x, apply(q, y, p), p), p), apply(h, y, p),
            apply(h, apply(q, u, p), p), apply(h, apply(inverse(q, p), v, p), p))


def gl2(p: int) -> list[Small]:
    require(p in (2, 3), "bounded matrix domain")
    return [entries for entries in itertools.product(range(p), repeat=4)
            if (entries[0] * entries[3] - entries[1] * entries[2]) % p]


def finite_checks() -> dict[str, int]:
    cases = noncommuting = columns = 0
    for p in (2, 3):
        group = gl2(p)
        require(len(group) == (6 if p == 2 else 48), "complete GL2 domain")
        first = group if p == 2 else [(1, 1, 0, 1)]
        for a, b, q in itertools.product(first, group, group):
            c = smul(smul(b, q, p), inverse(b, p), p)
            commute = smul(q, b, p) == smul(b, q, p)
            wrong_matches = True
            for column in range(8):
                state = tuple(tuple(int(2 * row + k == column) for k in range(2))
                              for row in range(4))
                wanted = expected_vectors(a, b, q, p, state)
                require(literal(a, b, q, c, p, state) == wanted, "finite transported column")
                wrong_matches &= literal(a, b, q, q, p, state) == wanted
                columns += 1
            require(wrong_matches == commute, "exact commutator criterion")
            noncommuting += not commute
            cases += 1
    require(cases == 2520 and columns == 20160, "fixed finite coverage")
    singular_rejections = 0
    for p in (2, 3):
        try:
            inverse((1, 1, 1, 1), p)
        except ValueError:
            singular_rejections += 1
    require(singular_rejections == 2, "nonunit input rejection")
    return {"finite_operator_triples": cases, "arbitrary_input_basis_columns": columns,
            "noncommuting_untransported_rejections": noncommuting,
            "singular_operator_rejections": singular_rejections}


def package_hashes() -> dict[str, str]:
    root = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    result = {}
    for name in names:
        with (root / name).open("rb") as stream:
            payload = stream.read(1_048_577)
        require(len(payload) <= 1_048_576, "package file capacity")
        result[name] = hashlib.sha256(payload).hexdigest()
    return result


def main() -> None:
    result = {**formal_checks(), **bridge_checks(), **finite_checks()}
    result["python"] = platform.python_version()
    result["package_sha256"] = package_hashes()
    print(json.dumps(result, sort_keys=True))
    print("PASS_TRANSPORTED_CODED_QUERY")


if __name__ == "__main__":
    main()
