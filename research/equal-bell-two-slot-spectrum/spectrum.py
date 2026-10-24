"""Exact equal-Bell spectrum; Ali Romman with OpenAI Codex, Apache-2.0."""
from collections import Counter
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import runpy

import numpy as np
from sympy import Matrix, Poly, Symbol, ZZ

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
X = Symbol("x")
SOURCE = "research/centre-polynomial-cache-limits/frozen/work/centre-encoding-campaign-20261014/lanes/circuit-interface/INTERFACE.json"
PREDECESSOR = "research/exact-one-slot-gram/"


def require(test, message):
    if not test:
        raise ValueError(message)


def authenticate():
    records = json.loads((PACKAGE / "SOURCES.json").read_text())["files"]
    for row in records:
        if row.get("usage") == "input":
            require(sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                    "source digest: " + row["path"])


def inputs():
    authenticate()
    raw = json.loads((ROOT / SOURCE).read_text())
    roots = np.array([[int(raw["R"][i].get(str(j), 0)) for i in range(8)]
                      for j in range(112)], dtype=np.int64)
    ports = tuple(raw["ports"])
    prior = runpy.run_path(str(ROOT / PREDECESSOR / "model.py"))
    checked, labels = prior["read_query"]()
    require(np.array_equal(roots, checked) and ports == labels, "independent query read")
    generators = prior["symmetries"](checked, labels)
    orbits = prior["label_orbits"](generators)
    require([(v[0], len(v)) for v in orbits] ==
            [(0, 2), (1, 224), (3, 224), (7, 16), (30, 14), (128, 32)],
            "complete equal-label symmetry cover")
    return roots, ports, orbits


def walsh_matrices(roots, ports):
    out = []
    for u in range(512):
        signs = np.array([1 - 2 * ((q & u).bit_count() % 2) for q in ports], dtype=np.int64)
        out.append(roots.T @ (roots * signs[:, None]))
    return np.array(out, dtype=np.int64)


def compressed_pairs(walsh, c):
    plus, minus = {}, {}
    for u in range(512):
        a, b = walsh[u] + walsh[u ^ c], walsh[u] - walsh[u ^ c]
        require(np.all(a % 2 == 0) and np.all(b % 2 == 0), "integral half sums")
        plus.setdefault(tuple((a // 2).flat), u)
        minus.setdefault(tuple((b // 2).flat), u)
    return plus, minus


def characteristic_batch(matrices):
    """Use exact Faddeev-LeVerrier arithmetic in its checked int64 domain."""
    require(matrices.ndim == 3 and matrices.shape[1:] == (8, 8), "eight-dimensional matrices")
    require(np.array_equal(matrices, matrices.transpose(0, 2, 1)), "symmetric matrices")
    require(int(np.max(np.sum(np.abs(matrices), axis=2))) <= 112, "row norm bound")
    require(max(64 * comb(7, k - 1) * 112**k for k in range(1, 9)) < 2**63,
            "integer intermediate bound")
    identity = np.eye(8, dtype=np.int64)
    work = np.broadcast_to(identity, matrices.shape).copy()
    coefficients = np.ones((len(matrices), 9), dtype=np.int64)
    for k in range(1, 9):
        product = matrices @ work
        trace = np.trace(product, axis1=1, axis2=2)
        require(np.all(trace % k == 0), "exact Newton trace division")
        coefficient = -(trace // k)
        coefficients[:, 8 - k] = coefficient
        work = product + coefficient[:, None, None] * identity
    require(np.all(work == 0), "complete characteristic polynomial action")
    return coefficients


def literal_matrix(roots, ports, c, u, v):
    output = [[0] * 8 for _ in range(8)]
    for q, root in zip(ports, roots):
        label = v if (q & c).bit_count() % 2 else u
        sign = 1 - 2 * ((q & label).bit_count() % 2)
        for i in range(8):
            for j in range(8):
                output[i][j] += sign * int(root[i]) * int(root[j])
    return output


def polynomial(coefficients):
    require(all(type(v) is int for v in coefficients) and coefficients[-1] == 1,
            "monic integer coefficients")
    return Poly.from_list(list(reversed(coefficients)), X, domain=ZZ)


def coefficient_list(poly):
    return [int(v) for v in reversed(poly.all_coeffs())]


def classify(roots, ports, walsh, c):
    plus, minus = compressed_pairs(walsh, c)
    b = np.array(list(minus), dtype=np.int64).reshape(-1, 8, 8)
    vvalues = list(minus.values())
    examples, counts = {}, Counter()
    for a, u in plus.items():
        matrices = np.array(a, dtype=np.int64).reshape(8, 8) + b
        coefficients = characteristic_batch(matrices)
        for index, row in enumerate(coefficients):
            key = tuple(int(z) for z in row)
            counts[key] += 1
            examples.setdefault(key, (u, vvalues[index]))
    total = Poly(1, X, domain=ZZ)
    for key, (u, v) in examples.items():
        matrix = Matrix(literal_matrix(roots, ports, c, u, v))
        exact = matrix.charpoly(X).as_poly()
        require(coefficient_list(exact) == list(key), "independent symbolic determinant")
        total = total.lcm(polynomial(list(key)).sqf_part())
    histogram = [[list(key), counts[key], list(examples[key])] for key in sorted(counts)]
    return total, {"c": c, "plus_classes": len(plus), "minus_classes": len(minus),
                   "matrix_pairs": len(plus) * len(minus), "characteristic_polynomials": len(counts),
                   "minimal_degree": total.degree(), "polynomial": coefficient_list(total),
                   "histogram_sha256": sha256(json.dumps(histogram, separators=(",", ":")).encode()).hexdigest()}


def bell_check(ports):
    # Check the second Bell state on every actual port and address.
    checks = 0
    for c, u, v in ((1, 0, 2), (3, 17, 138), (7, 511, 73), (30, 42, 109), (128, 345, 21)):
        for q in ports:
            shift = (q & c).bit_count() % 2
            expected = (q & (v if shift else u)).bit_count() % 2
            for a in range(512):
                b = a ^ u
                initial = (a & v).bit_count() % 2
                if shift:
                    aa, bb, sign = a ^ q, b ^ q, 0
                else:
                    aa, bb = a, b
                    sign = ((q & a).bit_count() + (q & b).bit_count()) % 2
                require(bb == aa ^ u and (initial + sign) % 2 ==
                        ((aa & v).bit_count() + expected) % 2, "literal joint Bell action")
                checks += 1
    return checks


def failure_controls(roots, ports, walsh, witness):
    def rejected(call):
        try:
            call()
        except ValueError:
            return
        raise ValueError("negative control accepted")
    rejected(lambda: polynomial([True, 1]))
    rejected(lambda: polynomial([0, 2]))
    rejected(lambda: characteristic_batch(np.ones((1, 7, 7), dtype=np.int64)))
    bad = np.eye(8, dtype=np.int64)[None, :, :] * 113
    rejected(lambda: characteristic_batch(bad))
    bad = np.zeros((1, 8, 8), dtype=np.int64); bad[0, 0, 1] = 1
    rejected(lambda: characteristic_batch(bad))
    wrong = literal_matrix(roots, ports, 1, 2, 0)
    require(wrong != witness, "Bell sign labels cannot be swapped")
    require(literal_matrix(roots, ports, 0, 0, 2) != witness, "outer label is essential")
    require((walsh[0] + walsh[2]).tolist() != witness, "half projections are essential")
    exact = Matrix(witness).charpoly(X).as_poly()
    require((exact + 1).eval(32) == 1, "changed annihilator constant rejects witness")
    return 9


def report():
    roots, ports, orbits = inputs()
    walsh = walsh_matrices(roots, ports)
    rows, equal = [], Poly(1, X, domain=ZZ)
    for orbit in orbits:
        poly, row = classify(roots, ports, walsh, orbit[0])
        rows.append(row); equal = equal.lcm(poly)
    prior = json.loads((ROOT / PREDECESSOR / "CERTIFICATE.json").read_text())
    one = Poly(1, X, domain=ZZ)
    for row in [prior["zero"]] + prior["sectors"]:
        one = one.lcm(polynomial(row["coefficients"]))
    one_hash = sha256(json.dumps(coefficient_list(one), separators=(",", ":")).encode()).hexdigest()
    require(one.degree() == 881 and one_hash == prior["polynomial_sha256"], "inherited one-slot polynomial")
    joint = equal.lcm(one)
    witness = literal_matrix(roots, ports, 1, 0, 2)
    require(all(witness[i][1] == (32 if i == 1 else 0) for i in range(8)), "explicit new eigenvector")
    require(one.eval(32) != 0, "new eigenvalue absent from one slot")
    require(equal.degree() == 255 and joint.degree() == 1093, "new exact equal-label and joint degrees")
    return {"status": "PASS_EQUAL_BELL_TWO_SLOT_SPECTRUM", "operator": "B_lambda=4*A_lambda",
            "orbits": [[a[0], len(a)] for a in orbits], "representatives": rows,
            "equal_label_degree": equal.degree(), "one_slot_degree_inherited": one.degree(),
            "new_spectral_degree": equal.exquo(equal.gcd(one)).degree(),
            "higher_width_degree_lower_bound": joint.degree(),
            "affine_inverse_degree_lower_bound": joint.degree() - 1,
            "equal_label_polynomial": coefficient_list(equal),
            "joint_polynomial_sha256": sha256(json.dumps(coefficient_list(joint), separators=(",", ":")).encode()).hexdigest(),
            "new_eigenvalue_B": 32, "new_eigenvalue_A": 8, "witness": {"c": 1, "u": 0, "v": 2, "root_coordinate": 1},
            "literal_Bell_port_columns": bell_check(ports), "negative_controls": failure_controls(roots, ports, walsh, witness)}
