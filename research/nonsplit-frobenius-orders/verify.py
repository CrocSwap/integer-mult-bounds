"""Check the new counts, never predecessor verifiers. Apache-2.0.

Produced by Nick Petalas.
"""

import hashlib
import json
from pathlib import Path
import platform

from oracle import (Pair, Ring, enumerate_local, enumerate_pair, field_mul,
                    mixed_histogram, odd_count, validate_map)
from orders import local_order, product_orders, require


def reject(label, function, *arguments):
    try:
        function(*arguments)
    except ValueError:
        return label
    raise ValueError("control accepted: " + label)


def field_controls():
    results = []
    for degree, modulus in ((1, 3), (3, 11), (4, 19), (6, 67)):
        size = 1 << degree
        products = tuple(tuple(field_mul(a, b, degree, modulus) for b in range(size))
                         for a in range(size))
        for a in range(1, size):
            require(set(products[a]) == set(range(size)), "field not a field")
        results.append({"degree": degree, "products": size*size})
    return results


def local_fixtures():
    f8 = Ring(3, 11, (1,))
    maps8, data8 = enumerate_local(f8, (0, 1), 2, (1, 1, 0, 1), 3)
    require(len(maps8) == 3*local_order(8, 2, (1,)), "F8 local count")
    f16 = Ring(4, 19, (1,))
    alpha = next(a for a in range(2, 16) if f16.mul(a, a) ^ a ^ 1 == 0)
    base = (0, 1, alpha, alpha ^ 1)
    theta = next(a for a in range(16) if f16.mul(a, a) ^ a ^ alpha == 0)
    maps16, data16 = enumerate_local(f16, base, theta, (alpha, 1, 1), 2)
    require(len(maps16) == 2*local_order(16, 2, (1,)), "F16/F4 local count")
    maps16_absolute, data16_absolute = enumerate_local(f16, (0, 1), 2, (1, 1, 0, 0, 1), 4)
    require(len(maps16_absolute) == 4*local_order(16, 2, (1,)), "F16/F2 local count")
    field64 = Ring(6, 67, ())
    maps64, data64 = enumerate_local(field64, (0, 1), 2, (1, 1, 0, 0, 0, 0, 1), 6)
    require(len(maps64) == product_orders(2, 2, ((6, (), 1),))["automorphisms"],
            "pure residue count")
    return ((f8, maps8, f16, maps16, field64, maps64, alpha),
            [data8, data16, data16_absolute, data64])


def controls(fixtures, repeated, equal):
    f8, maps8, f16, maps16, field64, _, alpha = fixtures
    rows = [reject("wrong_characteristic", local_order, 8, 3, (1,)),
            reject("composite_characteristic", local_order, 4, 4, (1,)),
            reject("zero_height", local_order, 2, 2, (0,)),
            reject("large_dimension", local_order, 2, 2, (3, 3)),
            reject("uncombined_types", product_orders, 2, 2, ((3, (1,), 1), (3, (1,), 1)))]
    require(equal["automorphisms_factorized"] != 168, "nonlinear freedom discriminator")
    require(len(maps16) != local_order(16, 2, (1,)), "missing coefficient Frobenius")
    require(len(maps16) != 4*local_order(16, 2, (1,)), "p/q Frobenius discriminator")
    require(repeated["automorphisms"] != len(maps8)**2, "missing factorial discriminator")
    rows += ["nonlinear_freedom", "coefficient_frobenius", "base_q_not_p", "repeat_factorial"]
    singular = (0,)*f8.dimension
    rows.append(reject("singular_substitution", validate_map, f8, singular))
    changed = list(maps8[0])
    changed[0] ^= 1 << 3
    rows.append(reject("changed_unit", validate_map, f8, tuple(changed)))
    p_frobenius = tuple(f16.power(1 << i, 2) if i < 4 else f16.power(1 << (i-4), 2) << 4
                       for i in range(f16.dimension))
    rows.append(reject("moving_base_field", validate_map, f16, p_frobenius, (alpha,)))
    pair = Pair(f8, field64)
    swap = tuple(1 << (i+6) for i in range(6)) + tuple(1 << i for i in range(6))
    rows.append(reject("same_dimension_different_type", validate_map, pair, swap))
    return rows


def receipt():
    root = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "orders.py", "oracle.py", "verify.py")
    hashes = {}
    for name in names:
        with (root / name).open("rb") as stream:
            data = stream.read(1024*1024+1)
        require(len(data) <= 1024*1024, "receipt file limit")
        hashes[name] = hashlib.sha256(data).hexdigest()
    return hashes


def main():
    fields = field_controls()
    fixtures, locals_report = local_fixtures()
    f8, maps8, _, _, field64, maps64, _ = fixtures
    _, repeated = enumerate_pair(f8, f8, maps8, maps8, True)
    _, distinct = enumerate_pair(f8, field64, maps8, maps64, False)
    repeated_formula = product_orders(2, 2, ((3, (1,), 2),))
    distinct_formula = product_orders(2, 2, ((3, (1,), 1), (6, (), 1)))
    require(repeated["automorphisms"] == repeated_formula["automorphisms"], "repeat count")
    require(distinct["automorphisms"] == distinct_formula["automorphisms"], "distinct count")
    mixed = mixed_histogram(Ring(1, 3, (1, 3)), (1, 3))
    require(mixed["automorphisms_factorized"] == local_order(2, 2, (1, 3)), "mixed count")
    equal = mixed_histogram(Ring(1, 3, (1, 1, 1)), (1, 1, 1), 1)
    require(equal["automorphisms_factorized"] == local_order(2, 2, (1, 1, 1)), "equal count")
    odd = odd_count()
    require(odd["automorphisms"] == local_order(3, 3, (1,)), "odd count")
    report = {"status": "PASS_NONSPLIT_FROBENIUS_ORDERS", "python": platform.python_version(),
              "fields": fields, "locals": locals_report, "repeated": repeated,
              "distinct": distinct, "mixed": mixed, "equal": equal, "odd": odd,
              "repeated_formula": repeated_formula, "distinct_formula": distinct_formula,
              "controls": controls(fixtures, repeated, equal), "sha256": receipt(),
              "scope": "scoped proof with finite corroboration; no new kappa"}
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
