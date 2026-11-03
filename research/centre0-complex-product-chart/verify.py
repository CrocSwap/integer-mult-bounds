#!/usr/bin/env python3
"""Check the new common chart; never execute a predecessor verifier."""

import hashlib
import importlib.util
import json
from fractions import Fraction as F
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
spec = importlib.util.spec_from_file_location("centre0_chart", PACKAGE / "chart.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load chart")
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


def check(value, message):
    if not value:
        raise RuntimeError(message)


def load_sources():
    path = PACKAGE / "SOURCES.json"
    check(path.stat().st_size <= 1024*1024, "manifest too large")
    manifest = json.loads(path.read_text())
    check(len(manifest["files"]) <= 16, "too many sources")
    data = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        path = ROOT / row["path"]
        check(path.stat().st_size <= 1024*1024, "source too large")
        raw = path.read_bytes()
        check(hashlib.sha256(raw).hexdigest() == row["sha256"], "source drift")
        if path.suffix == ".json":
            data[path.name] = json.loads(raw)
    return data


def quadratic_checks():
    check(78**2 < c.D < 79**2, "radicand is not between consecutive squares")
    check(c.mul(c.LAM, c.RECIP) == c.ONE, "wrong reciprocal")
    check(c.add(c.LAM, c.RECIP) == c.q(1874), "wrong trace")
    # A separate polynomial reduction uses X^2=6097.
    count = 0
    for a in range(-3, 4):
        for b in range(-3, 4):
            x = (F(a), F(b))
            for d in range(-3, 4):
                for e in range(-3, 4):
                    coefficients = [a*d, a*e+b*d, b*e]
                    expected = (F(coefficients[0]+6097*coefficients[2]),
                                F(coefficients[1]))
                    check(c.mul(x, (F(d), F(e))) == expected, "quadratic product")
                    count += 1
            if x != c.ZERO:
                check(c.mul(x, c.inverse(x)) == c.ONE, "quadratic inverse")
    return count


def chart_checks(data):
    r = [[F(x) for x in row] for row in data["R.json"]]
    source = data["CORRECTED-DERIVATION.json"]
    a = [[c.q(x) for x in row] for row in source["F_actual"]]
    b = [list(row) for row in zip(*a)]
    w, inverse = c.common_coordinates(r, source["selected_ports_J"])
    permutation, weights = c.split_maps(112)
    columns = [list(row) for row in zip(*w)]
    inverse_columns = [list(row) for row in zip(*inverse)]
    for j, column in enumerate(columns):
        expected = [c.q(i == j) for i in range(112)]
        check(c.apply(inverse, column) == expected, "Q W is not identity")
        check(c.apply(w, inverse_columns[j]) == expected, "W Q is not identity")
        check(c.apply(a, column) == columns[permutation[j]], "G chart endpoint")
        wanted = [c.mul(weights[permutation[j]], x) for x in columns[permutation[j]]]
        check(c.apply(b, column) == wanted, "transpose chart endpoint")
    products = 0
    for j in range(112):
        for k in range(112):
            left_slot, right_slot = permutation[j], permutation[k]
            left = {} if left_slot != right_slot else {left_slot: weights[right_slot]}
            right = {} if j != k else {permutation[j]: weights[permutation[j]]}
            check(left == right, "split product tensor")
            products += 1
    return w, inverse, {"inverse_columns": 224, "endpoint_columns": 224,
                        "split_basis_products": products}


def mod_fraction(x, prime):
    return x.numerator * pow(x.denominator, -1, prime) % prime


def mod_quadratic(x, root, prime):
    return (mod_fraction(x[0], prime) + root*mod_fraction(x[1], prime)) % prime


def evaluate(vector, roots, prime):
    values = []
    for root in roots:
        value = 0
        for x in reversed(vector):
            value = (value*root+x) % prime
        values.append(value)
    return values


def interpolate(values, roots, prime):
    n = len(values)
    result = [0]*n
    inv_n = pow(n, -1, prime)
    for value, root in zip(values, roots):
        power = value*inv_n % prime
        step = pow(root, -1, prime)
        for i in range(n):
            result[i] = (result[i]+power) % prime
            power = power*step % prime
    return result


def convolution(a, b, prime):
    n = len(a)
    result = [0]*n
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            k = i+j
            result[k % n] = (result[k % n] + (1 if k < n else -1)*x*y) % prime
    return result


def field_fixture(width):
    for prime in (7681, 12289, 40961, 65537):
        check(all(prime % d for d in range(2, 257) if d*d <= prime),
              "fixture modulus is not prime")
        if (prime-1) % (2*width):
            continue
        roots_d = [a for a in range(prime) if a*a % prime == c.D % prime]
        if not roots_d:
            continue
        for a in range(2, prime):
            zeta = pow(a, (prime-1)//(2*width), prime)
            if pow(zeta, width, prime) == prime-1:
                return prime, roots_d[0], zeta
    raise RuntimeError("no finite-field fixture")


def negacyclic_checks():
    count = 0
    fields = []
    for n in (128, 256, 512):
        prime, root_d, zeta = field_fixture(n)
        roots = [pow(zeta, 2*j+1, prime) for j in range(n)]
        permutation, weights_q = c.split_maps(n)
        weights = [mod_quadratic(x, root_d, prime) for x in weights_q]
        check(len(set(roots)) == n, "evaluation roots collide")
        for seed in range(6):
            x = [(i*i+seed*i+3*seed+1) % prime for i in range(n)]
            y = [(i**3+2*seed*i+seed+2) % prime for i in range(n)]
            ex, ey = evaluate(x, roots, prime), evaluate(y, roots, prime)
            check(interpolate(ex, roots, prime) == x, "evaluation inverse")
            ax = interpolate([ex[permutation[j]] for j in range(n)], roots, prime)
            by = interpolate([weights[j]*ey[permutation[j]] % prime
                              for j in range(n)], roots, prime)
            product = convolution(x, y, prime)
            ep = evaluate(product, roots, prime)
            wanted = interpolate([weights[j]*ep[permutation[j]] % prime
                                  for j in range(n)], roots, prime)
            check(convolution(ax, by, prime) == wanted, "negacyclic product identity")
            count += 1
        fields.append({"width": n, "prime": prime, "sqrt_6097": root_d,
                       "primitive_root": zeta})
    return count, fields


def controls(data, w, inverse):
    failures = 0
    tests = [lambda: c.inverse(c.ZERO), lambda: c.rref([[F(0)]], 112),
             lambda: c.split_maps(111), lambda: c.split_maps(513),
             lambda: c.source_vectors([], []),
             lambda: c.apply([[c.ONE]], [c.ONE, c.ONE])]
    for test in tests:
        try:
            test()
        except ValueError:
            failures += 1
        else:
            raise RuntimeError("invalid argument accepted")
    first = [row[0] for row in w]
    bad_inverse = [row[:] for row in inverse]
    bad_inverse[0][0] = c.add(bad_inverse[0][0], c.ONE)
    check(c.apply(bad_inverse, first) != [c.q(i == 0) for i in range(112)],
          "changed inverse not detected")
    source = [[c.q(x) for x in row] for row in data["CORRECTED-DERIVATION.json"]["F_actual"]]
    check(c.apply(source, first) != first, "false common diagonal model")
    permutation, weights = c.split_maps(112)
    check(weights[0] != c.ONE and weights[0] != weights[1], "weights collapsed")
    check(convolution([0, 1], [0, 1], 17) == [16, 0], "negacyclic wrap control")
    p, root, zeta = field_fixture(128)
    roots = [pow(zeta, 2*j+1, p) for j in range(128)]
    ex = evaluate([1]+[0]*127, roots, p)
    weighted = [mod_quadratic(weights[j], root, p)*ex[permutation[j]] % p
                for j in range(112)] + [1]*16
    check(interpolate(weighted, roots, p) != [1]+[0]*127,
          "identity output-map control")
    return failures+5


def receipt(result):
    names = ["README.md", "PROOF.md", "TASK.json", "VERIFY.json", "SOURCES.json",
             "chart.py", "verify.py"]
    hashes = {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
              for name in names}
    return {"claim_type": "scoped algebraic construction with finite corroboration",
            "result": result, "package_sha256": hashes}


def main():
    check(sys.argv[1:] in ([], ["--emit-receipt"]), "unknown arguments")
    data = load_sources()
    field_products = quadratic_checks()
    w, inverse, result = chart_checks(data)
    products, fields = negacyclic_checks()
    result.update({"quadratic_products": field_products, "negacyclic_pairs": products,
                   "finite_fields": fields, "controls": controls(data, w, inverse),
                   "active_planes": 7, "fixed_dimension": 98,
                   "lambda": [937, 12], "radicand": 6097})
    generated = receipt(result)
    if sys.argv[1:]:
        print(json.dumps(generated, indent=2, sort_keys=True))
    else:
        path = PACKAGE / "RESULT.json"
        check(path.stat().st_size <= 1024*1024, "receipt too large")
        expected = json.loads(path.read_text())
        check(json.dumps(generated, sort_keys=True) == json.dumps(expected, sort_keys=True),
              "receipt differs")
        print("PASS_CENTRE0_COMPLEX_PRODUCT_CHART")
        print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
