"""Exact bounded corroboration; no predecessor executable or external input."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


class Field:
    """Small prime fields, F4 = F2[t]/(t^2+t+1), F8 = F2[t]/(t^3+t+1)."""

    def __init__(self, q: int) -> None:
        if type(q) is not int or q not in (2, 3, 4, 5, 7, 8, 11, 13):
            raise ValueError("unsupported finite checker field")
        self.q = q
        self.p = 2 if q in (4, 8) else q
        self.sums = tuple(tuple(self._sum(a, b) for b in range(q)) for a in range(q))
        self.products = tuple(tuple(self._product(a, b) for b in range(q)) for a in range(q))
        self.negatives = tuple(next(b for b in range(q) if self.sums[a][b] == 0) for a in range(q))
        self.inverses = (0,) + tuple(
            next(b for b in range(1, q) if self.products[a][b] == 1)
            for a in range(1, q)
        )

    def _sum(self, a: int, b: int) -> int:
        return a ^ b if self.q in (4, 8) else (a + b) % self.q

    def _product(self, a: int, b: int) -> int:
        if self.q not in (4, 8):
            return a * b % self.q
        degree, modulus = (2, 0b111) if self.q == 4 else (3, 0b1011)
        result = 0
        for bit in range(degree):
            if (b >> bit) & 1:
                result ^= a << bit
        for bit in range(2 * degree - 2, degree - 1, -1):
            if (result >> bit) & 1:
                result ^= modulus << (bit - degree)
        return result

    def add(self, a: int, b: int) -> int:
        return self.sums[a][b]

    def mul(self, a: int, b: int) -> int:
        return self.products[a][b]

    def power(self, a: int, exponent: int) -> int:
        if not 0 <= exponent <= 1_000_000:
            raise ValueError("finite exponent bound")
        result = 1
        for bit in range(exponent.bit_length()):
            if (exponent >> bit) & 1:
                result = self.mul(result, a)
            a = self.mul(a, a)
        return result


def determinant(columns: tuple[tuple[int, ...], ...], field: Field) -> int:
    size = len(columns)
    require(1 <= size <= 36 and all(len(c) == size for c in columns), "matrix shape")
    rows = [[columns[j][i] for j in range(size)] for i in range(size)]
    result = 1
    for col in range(size):
        pivot = next((i for i in range(col, size) if rows[i][col]), None)
        if pivot is None:
            return 0
        if pivot != col:
            rows[pivot], rows[col] = rows[col], rows[pivot]
            result = field.negatives[result]
        value = rows[col][col]
        result = field.mul(result, value)
        inverse = field.inverses[value]
        for i in range(col + 1, size):
            scale = field.mul(rows[i][col], inverse)
            if scale:
                for j in range(col, size):
                    term = field.mul(scale, rows[col][j])
                    rows[i][j] = field.add(rows[i][j], field.negatives[term])
    return result


class Algebra:
    """The literal quotient algebra, with a bounded monomial table."""

    def __init__(self, field: Field, n: int, d: int) -> None:
        if type(n) is not int or type(d) is not int or not 2 <= n <= 6 or not 2 <= d <= 4:
            raise ValueError("finite algebra parameter bound")
        if n**d > 36:
            raise ValueError("finite algebra dimension bound")
        self.field, self.n, self.d = field, n, d
        self.exponents = tuple(itertools.product(range(n), repeat=d))
        self.size = len(self.exponents)
        self.index = {e: i for i, e in enumerate(self.exponents)}
        self.zero = (0,) * self.size
        self.one = (1,) + (0,) * (self.size - 1)
        self.variables = tuple(
            self.index[tuple(int(i == j) for i in range(d))] for j in range(d)
        )
        self.table = tuple(tuple(self._basis_product(a, b) for b in self.exponents) for a in self.exponents)

    def _basis_product(self, a: tuple[int, ...], b: tuple[int, ...]) -> int:
        exponent = tuple(x + y for x, y in zip(a, b, strict=True))
        return self.index[exponent] if max(exponent) < self.n else -1

    def basis(self, index: int) -> tuple[int, ...]:
        require(0 <= index < self.size, "basis index")
        return tuple(int(i == index) for i in range(self.size))

    def mul(self, a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
        require(len(a) == len(b) == self.size, "algebra input shape")
        result = [0] * self.size
        left = tuple((i, x) for i, x in enumerate(a) if x)
        right = tuple((j, y) for j, y in enumerate(b) if y)
        for i, x in left:
            for j, y in right:
                destination = self.table[i][j]
                if destination >= 0:
                    term = self.field.mul(x, y)
                    result[destination] = self.field.add(result[destination], term)
        return tuple(result)

    def powers(self, value: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
        result = [self.one]
        for _ in range(self.n):
            result.append(self.mul(result[-1], value))
        return tuple(result)

    def substitution(self, images: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
        require(len(images) == self.d and all(v[0] == 0 for v in images), "generator images")
        powers = tuple(self.powers(v) for v in images)
        require(all(p[-1] == self.zero for p in powers), "truncation relation")
        columns = []
        for exponent in self.exponents:
            value = self.one
            for i, power in enumerate(exponent):
                value = self.mul(value, powers[i][power])
            columns.append(value)
        return tuple(columns)


def is_characteristic_power(n: int, p: int) -> bool:
    remainder = n
    for _ in range(n.bit_length()):
        if remainder % p:
            break
        remainder //= p
    return remainder == 1


def character_data(field: Field, n: int, d: int) -> dict[str, int]:
    if type(n) is not int or type(d) is not int or not 2 <= n <= 1000 or not 2 <= d <= 8:
        raise ValueError("finite formula parameter bound")
    if is_characteristic_power(n, field.p):
        raise ValueError("the theorem excludes characteristic-power truncations")
    size = n**d
    exponent = size * (n - 1) // 2
    swap_exponent = n ** (d - 2) * n * (n - 1) // 2
    order = field.q - 1
    sign_generator = order // 2 if field.p != 2 and swap_exponent % 2 else 0
    g = math.gcd(order, size)
    h = math.gcd(order, exponent, sign_generator)
    return {"N": size, "E": exponent, "S": swap_exponent, "g": g, "h": h, "SL_orbits": g * g * h}


def power_subgroup(field: Field, exponent: int) -> set[int]:
    return {field.power(a, exponent) for a in range(1, field.q)}


def predicted_automorphism_image(field: Field, data: dict[str, int]) -> set[int]:
    return {a for a in range(1, field.q) if field.power(a, (field.q - 1) // data["h"]) == 1}


def tangent_is_monomial(algebra: Algebra, images: tuple[tuple[int, ...], ...]) -> bool:
    rows = tuple(tuple(v[j] for j in algebra.variables) for v in images)
    return all(sum(bool(x) for x in row) == 1 for row in rows) and all(
        sum(bool(rows[i][j]) for i in range(algebra.d)) == 1 for j in range(algebra.d)
    )


def check_homomorphism(algebra: Algebra, columns: tuple[tuple[int, ...], ...]) -> int:
    checked = 0
    for i in range(algebra.size):
        for j in range(algebra.size):
            destination = algebra.table[i][j]
            expected = algebra.zero if destination < 0 else columns[destination]
            require(algebra.mul(columns[i], columns[j]) == expected, "basis-product identity")
            checked += 1
    return checked


def linear_witnesses(algebra: Algebra) -> dict[str, object]:
    field = algebra.field
    data = character_data(field, algebra.n, algebra.d)
    observed: set[int] = set()
    products_checked = maps = 0
    for swap in (False, True):
        for scalar in range(1, field.q):
            images = [algebra.basis(j) for j in algebra.variables]
            images[0] = tuple(field.mul(scalar, a) for a in images[0])
            if swap:
                images[0], images[1] = images[1], images[0]
            columns = algebra.substitution(tuple(images))
            require(tangent_is_monomial(algebra, tuple(images)), "monomial attaining tangent")
            value = determinant(columns, field)
            expected = field.power(scalar, data["E"])
            if swap and data["S"] % 2:
                expected = field.negatives[expected]
            require(value == expected and value != 0, "literal monomial determinant")
            observed.add(value)
            products_checked += check_homomorphism(algebra, columns)
            maps += 1
    require(observed == predicted_automorphism_image(field, data), "automorphism image attainment")
    return {"q": field.q, "n": algebra.n, "d": algebra.d, **data,
            "maps": maps, "basis_products": products_checked, "determinants": sorted(observed)}


def complete_substitution_domain(q: int, n: int) -> dict[str, object]:
    algebra = Algebra(Field(q), n, 2)
    field = algebra.field
    require(q ** (2 * (algebra.size - 1)) <= 65536, "complete census capacity")
    values = tuple((0,) + tail for tail in itertools.product(range(q), repeat=algebra.size - 1))
    admissible = {v for v in values if algebra.powers(v)[-1] == algebra.zero}
    observed: set[int] = set()
    pairs = accepted = products_checked = 0
    for left in values:
        for right in values:
            pairs += 1
            if left not in admissible or right not in admissible:
                continue
            images = (left, right)
            tangent = tuple(tuple(v[j] for j in algebra.variables) for v in images)
            if determinant(tangent, field) == 0:
                continue
            columns = algebra.substitution(images)
            value = determinant(columns, field)
            require(value != 0, "invertible tangent lifts to an automorphism")
            require(tangent_is_monomial(algebra, images), "complete nonlinear tangent restriction")
            linear = tuple(tuple(c if sum(e) == 1 else 0 for c, e in zip(v, algebra.exponents, strict=True))
                           for v in images)
            require(value == determinant(algebra.substitution(linear), field), "every nonlinear lift determinant")
            products_checked += check_homomorphism(algebra, columns)
            observed.add(value)
            accepted += 1
    require(observed == predicted_automorphism_image(field, character_data(field, n, 2)), "complete automorphism image")
    return {"q": q, "n": n, "d": 2, "pairs": pairs, "automorphisms": accepted,
            "basis_products": products_checked, "determinants": sorted(observed)}


def complete_unit_domain(q: int, n: int) -> dict[str, object]:
    algebra = Algebra(Field(q), n, 2)
    field = algebra.field
    require(q**algebra.size <= 1024, "unit census capacity")
    observed: set[int] = set()
    units = 0
    for value in itertools.product(range(q), repeat=algebra.size):
        if value[0] == 0:
            continue
        columns = tuple(algebra.mul(value, algebra.basis(i)) for i in range(algebra.size))
        actual = determinant(columns, field)
        require(actual == field.power(value[0], algebra.size), "literal unit norm")
        observed.add(actual)
        units += 1
    require(observed == power_subgroup(field, algebra.size), "complete unit character")
    return {"q": q, "n": n, "units": units, "determinants": sorted(observed)}


def determinant_triples(field: Field, n: int, d: int) -> dict[str, int]:
    data = character_data(field, n, d)
    norms = power_subgroup(field, data["N"])
    automorphisms = predicted_automorphism_image(field, data)
    attained = set()
    for x, y, z in itertools.product(norms, norms, automorphisms):
        attained.add((field.inverses[field.mul(x, z)], field.inverses[field.mul(y, z)],
                      field.mul(field.mul(x, y), z)))
    tested = 0
    for u, v, w in itertools.product(range(1, field.q), repeat=3):
        vw, uw = field.mul(v, w), field.mul(u, w)
        uvw = field.mul(u, vw)
        subgroup_test = vw in norms and uw in norms and uvw in automorphisms
        equation_test = (field.power(vw, (field.q - 1) // data["g"]) == 1
                         and field.power(uw, (field.q - 1) // data["g"]) == 1
                         and field.power(uvw, (field.q - 1) // data["h"]) == 1)
        require(((u, v, w) in attained) == subgroup_test == equation_test, "three character equations")
        tested += 1
    require(len(attained) * data["SL_orbits"] == (field.q - 1) ** 3, "determinant index")
    return {"q": field.q, "n": n, "d": d, "tested": tested, "image_size": len(attained),
            "SL_orbits": data["SL_orbits"]}


def literal_covariant_control() -> dict[str, int]:
    """Transform every coefficient of one multiplication tensor directly."""
    algebra = Algebra(Field(7), 2, 2)
    field = algebra.field
    x, y = (algebra.basis(j) for j in algebra.variables)
    xy = algebra.mul(x, y)
    forward = tuple(field.add(a, b) for a, b in zip(x, xy, strict=True))
    backward = tuple(field.add(a, field.negatives[b]) for a, b in zip(x, xy, strict=True))
    sigma = algebra.substitution((forward, y))
    inverse = algebra.substitution((backward, y))
    # F=2 sigma, G=2 sigma, H=4 sigma; sigma(x)=x+xy, sigma(y)=y.
    f_inverse_transpose = tuple(tuple(field.mul(4, inverse[i][j]) for i in range(4)) for j in range(4))
    g_inverse_transpose = f_inverse_transpose
    h = tuple(tuple(field.mul(4, x) for x in column) for column in sigma)
    checked = 0
    wrong = missing_transpose = 0
    for i, j, k in itertools.product(range(4), repeat=3):
        actual = mistaken = untransposed = 0
        for a, b in itertools.product(range(4), repeat=2):
            c = algebra.table[a][b]
            if c >= 0:
                term = field.mul(f_inverse_transpose[a][i], g_inverse_transpose[b][j])
                actual = field.add(actual, field.mul(term, h[c][k]))
                raw = field.mul(field.mul(2, sigma[a][i]), field.mul(2, sigma[b][j]))
                mistaken = field.add(mistaken, field.mul(raw, h[c][k]))
                raw_inverse = field.mul(field.mul(4, inverse[a][i]), field.mul(4, inverse[b][j]))
                untransposed = field.add(untransposed, field.mul(raw_inverse, h[c][k]))
        expected = int(algebra.table[i][j] == k)
        require(actual == expected, "literal covariant tensor coefficient")
        wrong += int(mistaken != expected)
        missing_transpose += int(untransposed != expected)
        checked += 1
    require(wrong > 0, "raw autotopism must not act covariantly without inverse transposes")
    require(missing_transpose > 0, "inverse without transpose must reject")
    triple = tuple(determinant(matrix, field) for matrix in (f_inverse_transpose, g_inverse_transpose, h))
    require(triple == (4, 4, 4), "literal covariant determinant triple")
    return {"coefficients": checked, "wrong_convention_coefficients": wrong,
            "missing_transpose_coefficients": missing_transpose}


def controls() -> dict[str, object]:
    algebra = Algebra(Field(3), 2, 2)
    x, y = (algebra.basis(j) for j in algebra.variables)
    mixed = tuple(algebra.field.add(a, b) for a, b in zip(x, y, strict=True))
    require(algebra.powers(mixed)[-1] != algebra.zero, "non-Frobenius shear must fail")
    binary = Algebra(Field(2), 2, 2)
    bx, by = (binary.basis(j) for j in binary.variables)
    bmixed = tuple(a ^ b for a, b in zip(bx, by, strict=True))
    require(binary.powers(bmixed)[-1] == binary.zero, "Frobenius shear discriminator")
    rejected = 0
    for operation, args in ((Field, (True,)), (Field, (6,)), (Algebra, (Field(3), 6, 4)),
                            (character_data, (Field(3), 3, 2)),
                            (character_data, (Field(5), 2, 1))):
        try:
            operation(*args)
        except ValueError:
            rejected += 1
        else:
            raise AssertionError("invalid checker domain accepted")
    data = character_data(Field(3), 2, 2)
    require(predicted_automorphism_image(Field(3), data) == {1, 2}, "swap sign is indispensable")
    require(power_subgroup(Field(3), data["E"]) == {1}, "sign omission discriminator")
    require(determinant_triples(Field(3), 2, 2)["image_size"] == 2, "two ternary determinant triples")
    require(character_data(Field(7), 2, 3)["h"] == 2, "swap sign can disappear in higher dimension")
    return {"invalid_domains_rejected": rejected,
            "semantic_discriminators": ["Frobenius versus non-Frobenius shear",
                                        "indispensable variable-swap sign",
                                        "ternary covariant image size two",
                                        "higher-dimensional swap sign disappearance"]}


def main() -> None:
    contexts = ((3, 2, 2), (5, 2, 2), (7, 2, 2), (7, 2, 3), (3, 2, 4),
                (5, 3, 2), (7, 3, 2), (2, 3, 2), (4, 3, 2), (8, 3, 2),
                (3, 4, 2), (5, 4, 2), (5, 6, 2), (7, 6, 2), (13, 6, 2))
    witnesses = [linear_witnesses(Algebra(Field(q), n, d)) for q, n, d in contexts]
    census = [complete_substitution_domain(3, 2), complete_substitution_domain(2, 3)]
    units = [complete_unit_domain(3, 2), complete_unit_domain(2, 3)]
    triples = [determinant_triples(Field(q), n, d) for q, n, d in contexts]
    report = {"claim_type": "scoped proof with exact finite corroboration", "witnesses": witnesses,
              "complete_substitutions": census, "complete_units": units,
              "determinant_triples": triples, "literal_covariant": literal_covariant_control(),
              "controls": controls()}
    root = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    report["source_sha256"] = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in names}
    print(json.dumps(report, sort_keys=True, indent=2))
    print("PASS_NONFROBENIUS_RECTANGULAR_CHARACTERS no_new_kappa")


if __name__ == "__main__":
    main()
