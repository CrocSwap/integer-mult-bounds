"""Exact symmetry counts for a declared width-two universal search family.

Produced by Nick Petalas. Apache-2.0.
No predecessor executable, external dependency, Git or network access is used.
"""

from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

Matrix = tuple[int, int, int, int]
IDENTITY: Matrix = (1, 0, 0, 1)
ZERO: Matrix = (0, 0, 0, 0)
E00: Matrix = (1, 0, 0, 0)
E11: Matrix = (0, 0, 0, 1)
SPECS = {2: (2, (0, 1)), 3: (3, (0, 1)), 4: (2, (1, 1, 1)),
         5: (5, (0, 1)), 7: (7, (0, 1)), 8: (2, (1, 1, 0, 1)),
         9: (3, (1, 0, 1))}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def raw_product(a: int, b: int, p: int, modulus: tuple[int, ...]) -> int:
    degree = len(modulus) - 1
    aa = tuple((a // p**i) % p for i in range(degree))
    bb = tuple((b // p**i) % p for i in range(degree))
    coeff = [0] * (2 * degree - 1)
    for i in range(degree):
        for j in range(degree):
            coeff[i + j] = (coeff[i + j] + aa[i] * bb[j]) % p
    for i in range(2 * degree - 2, degree - 1, -1):
        lead = coeff[i]
        for j in range(degree + 1):
            coeff[i - degree + j] = (
                coeff[i - degree + j] - lead * modulus[j]) % p
    return sum(coeff[i] * p**i for i in range(degree))


class Field:
    __slots__ = ("q", "p", "add", "mul", "neg", "inverse")

    def __init__(self, q: int, p: int, add: tuple[tuple[int, ...], ...],
                 mul: tuple[tuple[int, ...], ...], neg: tuple[int, ...],
                 inverse: tuple[int, ...]) -> None:
        self.q = q
        self.p = p
        self.add = add
        self.mul = mul
        self.neg = neg
        self.inverse = inverse


def field(q: int) -> Field:
    require(type(q) is int and q in SPECS, "unsupported finite replay field")
    p, modulus = SPECS[q]
    degree = len(modulus) - 1
    require(p**degree == q and modulus[-1] == 1, "field specification")
    add = tuple(tuple(sum((((a // p**i) % p + (b // p**i) % p) % p)
                          * p**i for i in range(degree))
                      for b in range(q)) for a in range(q))
    mul = tuple(tuple(raw_product(a, b, p, modulus) for b in range(q))
                for a in range(q))
    neg = tuple(next(b for b in range(q) if add[a][b] == 0) for a in range(q))
    inverses = [0]
    for a in range(1, q):
        candidates = tuple(b for b in range(1, q) if mul[a][b] == 1)
        require(len(candidates) == 1, "nonfield modulus")
        inverses.append(candidates[0])
    return Field(q, p, add, mul, neg, tuple(inverses))


def mm(f: Field, a: Matrix, b: Matrix) -> Matrix:
    s, t = f.add, f.mul
    return (s[t[a[0]][b[0]]][t[a[1]][b[2]]],
            s[t[a[0]][b[1]]][t[a[1]][b[3]]],
            s[t[a[2]][b[0]]][t[a[3]][b[2]]],
            s[t[a[2]][b[1]]][t[a[3]][b[3]]])


def transpose(a: Matrix) -> Matrix:
    return (a[0], a[2], a[1], a[3])


def subtract(f: Field, a: Matrix, b: Matrix) -> Matrix:
    return tuple(f.add[x][f.neg[y]] for x, y in zip(a, b, strict=True))


def plus(f: Field, a: Matrix, b: Matrix) -> Matrix:
    return tuple(f.add[x][y] for x, y in zip(a, b, strict=True))


def invert(f: Field, a: Matrix) -> Matrix:
    det = f.add[f.mul[a[0]][a[3]]][f.neg[f.mul[a[1]][a[2]]]]
    require(det != 0, "singular scalar adapter")
    d = f.inverse[det]
    return tuple(f.mul[d][x] for x in (a[3], f.neg[a[1]], f.neg[a[2]], a[0]))


def conjugate(f: Field, s: Matrix, a: Matrix) -> Matrix:
    return mm(f, mm(f, s, a), invert(f, s))


def is_projector(f: Field, a: Matrix) -> bool:
    return mm(f, a, a) == a and f.add[a[0]][a[3]] == 1


def projectors(f: Field) -> tuple[Matrix, ...]:
    direct = tuple(a for a in product(range(f.q), repeat=4) if is_projector(f, a))
    outer: set[Matrix] = set()
    vectors = tuple(product(range(f.q), repeat=2))
    for u in vectors:
        for v in vectors:
            if f.add[f.mul[u[0]][v[0]]][f.mul[u[1]][v[1]]] == 1:
                outer.add(tuple(f.mul[x][y] for x in u for y in v))
    require(set(direct) == outer, "independent projector inventory")
    require(len(direct) == f.q * (f.q + 1), "projector cardinality")
    return direct


def symmetries(f: Field) -> tuple[Matrix, ...]:
    return (tuple((t, 0, 0, 1) for t in range(1, f.q))
            + tuple((0, t, 1, 0) for t in range(1, f.q)))


def permutations(f: Field, items: tuple[Matrix, ...]) -> tuple[tuple[int, ...], ...]:
    indices = {a: i for i, a in enumerate(items)}
    normal = tuple(tuple(indices[conjugate(f, s, a)] for a in items)
                   for s in symmetries(f))
    reverse_maps = tuple(tuple(indices[conjugate(f, s, transpose(a))] for a in items)
                         for s in symmetries(f))
    return normal + reverse_maps


def orbit_formula(f: Field, length: int) -> int:
    require(type(length) is int and length in (1, 3, 5), "odd replay length")
    q, n, odd = f.q, f.q * (f.q + 1), int(f.p != 2)
    numerator = (n**length + 2**length * (q - 2 + odd * ((q - 1) // 2))
                 + (q - 1) * (q + odd) * n**(length // 2))
    denominator = 4 * (q - 1)
    require(numerator % denominator == 0, "nonintegral Burnside quotient")
    return numerator // denominator


def field_checks(f: Field) -> int:
    for a, b, c in product(range(f.q), repeat=3):
        require(f.add[f.add[a][b]][c] == f.add[a][f.add[b][c]], "add associativity")
        require(f.mul[f.mul[a][b]][c] == f.mul[a][f.mul[b][c]], "mul associativity")
        require(f.mul[a][f.add[b][c]] == f.add[f.mul[a][b]][f.mul[a][c]],
                "distributivity")
    for a in range(f.q):
        require(f.add[0][a] == a and f.mul[1][a] == a, "field identities")
        require(f.mul[a][0] == 0, "field zero")
    return f.q**3


def fixed_counts(f: Field, items: tuple[Matrix, ...]) -> dict[str, object]:
    n, half = len(items), 2 * (f.q - 1)
    maps = permutations(f, items)
    require(len(maps) == 2 * half and len(set(maps)) == 2 * half, "action order")
    require(all(set(p) == set(range(n)) for p in maps), "action bijections")
    rows = []
    for s, p, r in zip(symmetries(f), maps[:half], maps[half:], strict=True):
        c = sum(p[i] == i for i in range(n))
        h = sum(r[i] == i for i in range(n))
        a = mm(f, s, transpose(invert(f, s)))
        pair = sum(conjugate(f, a, x) == x for x in items)
        require(h == 0 or pair == n, "middle fixed point forces paired freedom")
        rows.append((c, h, pair))
    counts = {}
    for length in (1, 3, 5):
        fixed_sum = sum(c**length + h * pair**(length // 2) for c, h, pair in rows)
        require(fixed_sum % (2 * half) == 0, "Burnside divisibility")
        count = fixed_sum // (2 * half)
        require(count == orbit_formula(f, length), "literal fixed-count formula")
        counts[str(length)] = count
    return {"field": f.q, "projectors": n, "fixed_rows": rows, "orbits": counts}


def image_index(digits: tuple[int, ...], perm: tuple[int, ...],
                reverse: bool, n: int) -> int:
    result = 0
    for i in range(len(digits)):
        digit = digits[-1 - i] if reverse else digits[i]
        result = result * n + perm[digit]
    return result


def decode(index: int, n: int, length: int) -> tuple[int, ...]:
    digits = [0] * length
    for i in range(length - 1, -1, -1):
        index, digits[i] = divmod(index, n)
    require(index == 0, "tuple index range")
    return tuple(digits)


def canonical(digits: tuple[int, ...], maps: tuple[tuple[int, ...], ...], n: int) -> int:
    require(len(digits) in (1, 3, 5), "canonical length")
    require(all(type(x) is int and 0 <= x < n for x in digits), "projector index")
    require(len(maps) > 0 and len(maps) % 2 == 0, "canonical action size")
    require(all(len(p) == n and set(p) == set(range(n)) for p in maps),
            "canonical permutations")
    return min(image_index(digits, p, j >= len(maps) // 2, n)
               for j, p in enumerate(maps))


def census(f: Field, length: int) -> dict[str, object]:
    items = projectors(f)
    maps, n = permutations(f, items), len(items)
    total = n**length
    require(length in (1, 3, 5) and total <= 24_300_000, "census capacity")
    seen = bytearray(total)
    histogram: dict[int, int] = {}
    digest, count, covered = sha256(), 0, 0
    for index in range(total):
        if seen[index]:
            continue
        digits = decode(index, n, length)
        orbit = {image_index(digits, p, j >= len(maps) // 2, n)
                 for j, p in enumerate(maps)}
        require(min(orbit) == index, "canonical enumeration")
        require(all(not seen[i] for i in orbit), "overlapping orbits")
        require(len(maps) % len(orbit) == 0, "orbit stabilizer divisor")
        for i in orbit:
            seen[i] = 1
        covered += len(orbit)
        count += 1
        histogram[len(orbit)] = histogram.get(len(orbit), 0) + 1
        digest.update(index.to_bytes(8, "big"))
    require(covered == total and all(seen), "complete tuple coverage")
    require(count == orbit_formula(f, length), "enumerated orbit formula")
    return {"field": f.q, "length": length, "tuples": total, "orbits": count,
            "orbit_size_histogram": histogram, "representatives_sha256": digest.hexdigest()}


def expand(f: Field, word: tuple[Matrix, ...]) -> dict[tuple[int, ...], Matrix]:
    result = {(): IDENTITY}
    for label, projector in enumerate(word):
        following: dict[tuple[int, ...], Matrix] = {}
        for w, coefficient in result.items():
            for suffix, factor in (((), subtract(f, IDENTITY, projector)),
                                   ((label,), projector)):
                key = w + suffix
                following[key] = plus(f, following.get(key, ZERO), mm(f, coefficient, factor))
        result = {w: a for w, a in following.items() if a != ZERO}
    return result


def covariance_checks(f: Field, items: tuple[Matrix, ...]) -> int:
    fixtures = 0
    for offset in range(min(10, len(items))):
        word = tuple(items[(offset + i * i + 1) % len(items)] for i in range(5))
        original = expand(f, word)
        for s in symmetries(f):
            got = expand(f, tuple(conjugate(f, s, a) for a in word))
            expected = {w: conjugate(f, s, a) for w, a in original.items()}
            require(got == expected, "formal conjugation covariance")
            reverse_word = tuple(conjugate(f, s, transpose(a)) for a in reversed(word))
            got = expand(f, reverse_word)
            expected = {tuple(4 - i for i in reversed(w)):
                        conjugate(f, s, transpose(a)) for w, a in original.items()}
            require(got == expected, "reversal and opposite-group covariance")
            require({conjugate(f, s, E00), conjugate(f, s, E11)} == {E00, E11},
                    "target normalizer")
            fixtures += 1
    return fixtures


def controls() -> int:
    rejected = 0
    for q in (0, 1, 6, 10, True):
        try:
            field(q)
        except ValueError:
            rejected += 1
    f = field(3)
    for length in (0, 2, 4, 7, True):
        try:
            orbit_formula(f, length)
        except ValueError:
            rejected += 1
    items = projectors(f)
    maps = permutations(f, items)
    for digits in ((-1,), (len(items),), (True,), (0, 1)):
        try:
            canonical(digits, maps, len(items))
        except ValueError:
            rejected += 1
    try:
        invert(f, ZERO)
    except ValueError:
        rejected += 1
    require(rejected == 15, "rejection controls")
    require(not is_projector(f, ZERO) and not is_projector(f, IDENTITY), "rank condition")
    word = (E00, (1, 1, 0, 0))
    wrong = expand(f, tuple(transpose(a) for a in word))
    intended = {tuple(1 - i for i in reversed(w)): transpose(a)
                for w, a in expand(f, word).items()}
    require(wrong != intended, "transpose without reversal is not the claimed operation")
    require(conjugate(f, (1, 1, 0, 1), E11) not in (E00, E11),
            "arbitrary scalar conjugation does not preserve the target pattern")
    return rejected


def main() -> None:
    require(len(sys.argv) == 1, "this bounded verifier accepts no arguments")
    fixed, field_triples, covariance = [], 0, 0
    for q in SPECS:
        f = field(q)
        field_triples += field_checks(f)
        items = projectors(f)
        fixed.append(fixed_counts(f, items))
        covariance += covariance_checks(f, items)
        maps = permutations(f, items)
        for i in range(len(items)):
            index = canonical((i,), maps, len(items))
            require(canonical(decode(index, len(items), 1), maps, len(items)) == index,
                    "canonical idempotence")
    censuses = [census(field(q), 5) for q in (2, 3, 4, 5)]
    rejection_count = controls()
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: sha256((package / name).read_bytes()).hexdigest() for name in names}
    print(json.dumps({"status": "PASS_PROJECTOR_WORD_SYMMETRY", "fields": fixed,
                      "field_triples": field_triples, "formal_covariance_fixtures": covariance,
                      "censuses": censuses, "rejections": rejection_count,
                      "sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
