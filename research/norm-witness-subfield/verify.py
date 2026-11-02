"""Exact finite corroboration of the new subfield criterion. Apache-2.0."""

import hashlib
import json
from collections import Counter
from math import gcd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from witness import Field, minimal_degree, norm_witness, require


FIXTURES = (
    (2, (1, 1), 1),
    (2, (1, 1, 1), 2),
    (2, (1, 0, 1, 1), 2),
    (2, (1, 0, 0, 1, 1), 2),
    (2, (1, 0, 0, 0, 0, 1, 1), 2),
    (2, (1, 0, 0, 0, 1, 1, 1, 0, 1), 2),
    (3, (1, 1), 2),
    (3, (2, 1, 1), 3),
    (3, (1, 0, 2, 1), 3),
    (3, (2, 0, 0, 1, 1), 3),
    (3, (2, 0, 0, 0, 0, 1, 1), 3),
    (5, (1, 1), 2),
    (5, (2, 1, 1), 5),
    (5, (2, 0, 1, 1), 5),
    (5, (2, 0, 2, 1, 1), 5),
    (7, (1, 1), 3),
    (7, (3, 1, 1), 7),
    (7, (2, 1, 1, 1), 7),
)

SOURCE_FILES = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json",
                "VERIFY.json", "verify.py", "witness.py")


def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def norm_product(field, value, q, d):
    result, conjugate = 1, value
    for _ in range(d):
        result = field.multiply(result, conjugate)
        conjugate = field.power(conjugate, q)
    return result


def arithmetic_cases():
    orders = sorted({p**f for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31)
                     for f in range(1, 7) if p**f <= 64})
    cases, images = 0, 0
    for q in orders:
        for d in range(1, 129):
            e_min = minimal_degree(q, d)
            sufficient = []
            for e in divisors(d):
                image = {(k * (d // e)) % (q - 1) for k in range(q - 1)}
                require(len(image) == (q - 1) // gcd(d // e, q - 1),
                        "cyclic image size")
                require((len(image) == q - 1) == (e % e_min == 0),
                        "minimal degree disagrees with enumerated image")
                if len(image) == q - 1:
                    sufficient.append(e)
                images += 1
            require(min(sufficient) == e_min, "wrong least sufficient degree")
            cases += 1
    return {"orders": orders, "degree_pairs": cases, "cyclic_images": images}


def field_cases(field, generator):
    field.certify_generator(generator)
    report = {"base_domains": 0, "subfields": 0, "norm_values": 0, "witnesses": 0}
    for f in divisors(field.n):
        q, d = field.p**f, field.n // f
        base = {x for x in range(1, field.order) if field.power(x, q) == x}
        require(len(base) == q - 1, "wrong base fixed field")
        sufficient = []
        for e in divisors(d):
            elements = [x for x in range(1, field.order) if field.power(x, q**e) == x]
            counts = Counter(norm_product(field, x, q, d) for x in elements)
            expected = {field.power(x, d // e) for x in base}
            require(len(elements) == q**e - 1 and set(counts) == expected,
                    "literal norm restriction disagrees with power image")
            require(set(counts.values()) == {(q**e - 1) // len(expected)},
                    "literal norm fibers have wrong size")
            if set(counts) == base:
                sufficient.append(e)
            report["subfields"] += 1
            report["norm_values"] += len(elements)
        require(min(sufficient) == minimal_degree(q, d), "wrong literal minimum")
        for desired in sorted(base):
            result = norm_witness(field, f, generator, desired)
            require(norm_product(field, result["element"], q, d) == desired,
                    "constructor failed independent conjugate-product check")
            require(result["degree"] == min(sufficient), "constructor overstates minimum")
            report["witnesses"] += 1
        report["base_domains"] += 1
    return report


def determinant_mod_prime(matrix, p):
    a, result = [row[:] for row in matrix], 1
    for j in range(len(a)):
        pivot = next((i for i in range(j, len(a)) if a[i][j] % p), None)
        if pivot is None:
            return 0
        if pivot != j:
            a[j], a[pivot] = a[pivot], a[j]
            result = -result
        value = a[j][j] % p
        result = result * value % p
        for i in range(j + 1, len(a)):
            scale = a[i][j] * pow(value, -1, p) % p
            for k in range(j, len(a)):
                a[i][k] = (a[i][k] - scale * a[j][k]) % p
    return result % p


def determinant_application():
    field = Field(3, (2, 0, 0, 0, 0, 1, 1))
    field.certify_generator(3)
    result = norm_witness(field, 1, 3, 2)
    columns = [field.digits(field.multiply(result["element"], 3**j))
               for j in range(6)]
    matrix = [list(row) for row in zip(*columns)]
    determinant = determinant_mod_prime(matrix, 3)
    local_matrix = [[matrix[i % 6][j % 6] if i // 6 == j // 6 else 0
                     for j in range(18)] for i in range(18)]
    local_determinant = determinant_mod_prime(local_matrix, 3)
    require(determinant == 2 and local_determinant == 2,
            "literal residue/local-unit determinant")
    scalar_norms = {norm_product(field, x, 3, 6) for x in (1, 2)}
    require(scalar_norms == {1}, "scalar obstruction disappeared")
    require(field.power(result["element"], 9) == result["element"]
            and field.power(result["element"], 3) != result["element"],
            "witness must have exact intermediate degree two")
    return {"q": 3, "d": 6, "minimal_degree": 2, "desired_determinant": 2,
            "witness": result, "multiplication_matrix": matrix,
            "residue_determinant": determinant, "local_dimension_over_residue": 3,
            "local_unit_determinant": local_determinant,
            "full_nonzero_elements": 728, "subfield_nonzero_elements": 8}


def expect_rejection(operation):
    try:
        operation()
    except ValueError:
        return 1
    raise ValueError("invalid control was accepted")


def controls():
    rejected = 0
    for q, d in ((1, 2), (3, 0), (True, 2), (3, False), (3, 2**32 + 1)):
        rejected += expect_rejection(lambda: minimal_degree(q, d))
    for p, modulus in ((4, (1, 1)), (3, (1, 2)), (2, (1, 1) * 5),
                       (31, (1, 0, 0, 1))):
        rejected += expect_rejection(lambda: Field(p, modulus))
    field = Field(3, (2, 1, 1))
    rejected += expect_rejection(lambda: field.certify_generator(1))
    rejected += expect_rejection(lambda: Field(3, (2, 0, 1)).certify_generator(3))
    for f, g, desired in ((0, 3, 1), (3, 3, 1), (1, 3, 0), (1, 3, 3),
                           (1, 1, 2), (1, 3, 9)):
        rejected += expect_rejection(lambda: norm_witness(field, f, g, desired))
    require(minimal_degree(3, 12) == 4, "radical-only mutant escaped")
    require(minimal_degree(2, 6) == 1, "characteristic-prime mutant escaped")
    require(minimal_degree(9, 6) == 2, "extension-base mutant escaped")
    require(minimal_degree(5, 6) == 2, "full-degree mutant escaped")
    return {"invalid_inputs_rejected": rejected, "semantic_obstructions": 4}


def main():
    require(len(sys.argv) == 1, "this verifier accepts no arguments")
    totals = Counter()
    for p, modulus, generator in FIXTURES:
        totals.update(field_cases(Field(p, modulus), generator))
    result = {"status": "PASS_NORM_WITNESS_SUBFIELD", "arithmetic": arithmetic_cases(),
              "field_presentations": len(FIXTURES), "literal_fields": dict(totals),
              "application": determinant_application(), "controls": controls()}
    here = Path(__file__).resolve().parent
    result["source_sha256"] = {name: hashlib.sha256((here / name).read_bytes()).hexdigest()
                               for name in SOURCE_FILES}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
