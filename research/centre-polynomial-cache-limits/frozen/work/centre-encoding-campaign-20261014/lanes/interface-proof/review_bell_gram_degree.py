"""Review one exact Bell Gram degree certificate by a separate sparse map."""

from hashlib import sha256, shake_256
from pathlib import Path
import gzip
import importlib.util
import json
import numpy as np


P = 65537
N = 4096


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def pauli_product(first, second):
    x, z = first
    y, w = second
    return (x ^ y, z ^ w), 1-2*((z & y).bit_count() % 2)


def bareiss_mod(matrix):
    """Use fraction-free elimination, with division in the prime field."""
    a = matrix.copy()
    previous = 1
    sign = 1
    for k in range(len(a)-1):
        if a[k, k] == 0:
            rows = np.flatnonzero(a[k+1:, k])
            if not len(rows):
                return 0
            row = k+1+int(rows[0])
            a[[k, row]] = a[[row, k]]
            sign = -sign
        pivot = int(a[k, k])
        a[k+1:, k+1:] = ((pivot*a[k+1:, k+1:]
                         - a[k+1:, k, None]*a[None, k, k+1:]) % P
                        * pow(previous, -1, P)) % P
        a[k+1:, k] = 0
        previous = pivot
    return sign*int(a[-1, -1]) % P


def main():
    here = Path(__file__).resolve().parent
    lanes = here.parent
    workspace = here.parents[3]
    history = lanes/"history-encoding"
    certificate_raw = (history/"BELL-GRAM-DEGREE.json").read_bytes()
    certificate = json.loads(certificate_raw)
    interface_raw = (lanes/"circuit-interface/INTERFACE.json").read_bytes()
    require(sha256(interface_raw).hexdigest() == certificate["source_sha256"],
            "The exact interface source is pinned")
    interface = json.loads(interface_raw)
    frozen = workspace/"work/five-pr-sprint-20261013/lanes/centre-sharing"
    pinned = {
        "CANONICAL-WORD.json.gz": "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
        "LOCAL-PROGRAMS.json.gz": "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
    }
    source = {}
    for name, pin in pinned.items():
        raw = (frozen/name).read_bytes()
        require(sha256(raw).hexdigest() == pin, "The original word is pinned")
        source[name] = json.loads(gzip.decompress(raw))
    spec = importlib.util.spec_from_file_location(
        "independent_transpose", lanes/"bounds-review/review_centre_free.py")
    scalar = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scalar)
    word = source["CANONICAL-WORD.json.gz"]
    rows = scalar.clean_rows(source["LOCAL-PROGRAMS.json.gz"]["forward"], word)
    R = np.asarray(rows, dtype=np.int64)
    labels = word["ports"]
    require(labels == interface["ports"], "The label order matches the original word")
    given = np.asarray([[int(row.get(str(p), 0)) for p in range(112)]
                        for row in interface["R"]], dtype=np.int64)
    require(np.array_equal(R, given), "The original word gives the recorded R")
    require(np.array_equal(R@R.T, 56*np.eye(8, dtype=np.int64)), "R R^T=56 I")
    require(all(P % d for d in range(2, 257)), "65537 is prime")
    require(certificate["field_prime"] == P and certificate["bell_constant"] == 11,
            "The selected field and Bell block are fixed")
    c = 11
    # Expand H P H as four Pauli products. Its scalar is one half.
    for q in labels:
        require(q.bit_count() % 2 == 1, "Every source line is odd")
        identity_image = {}
        for left in ((q, 0), (0, q)):
            for right in ((q, 0), (0, q)):
                target, sign = pauli_product(left, right)
                identity_image[target] = identity_image.get(target, 0)+sign
        identity_image = {key: value for key, value in identity_image.items() if value}
        require(identity_image == {(0, 0): 2}, "The Pauli identity is fixed by every port")
        for a in range(512):
            b = a ^ c
            output = {}
            for left in ((q, 0), (0, q)):
                middle, first_sign = pauli_product(left, (b, a))
                for right in ((q, 0), (0, q)):
                    target, second_sign = pauli_product(middle, right)
                    output[target] = output.get(target, 0)+first_sign*second_sign
            output = {key: value for key, value in output.items() if value}
            odd = (q & c).bit_count() % 2
            target = (b ^ q, a ^ q) if odd else (b, a)
            sign = 1 if odd else 1-2*((q & a).bit_count() % 2)
            require(output == {target: 2*sign}, "The exact Bell action and sign")

    # Build the integer matrix 4 A from its coordinate entries, then
    # combine equal entries. This does not use the producer's R-factor map.
    addresses = np.arange(512, dtype=np.int64)
    keys = np.empty(112*16*512, dtype=np.int64)
    coefficients = np.empty(len(keys), dtype=np.int64)
    offset = 0
    for port, q in enumerate(labels):
        support = np.flatnonzero(R[:, port])
        require(len(support) == 4 and all(abs(int(R[k, port])) == 1 for k in support),
                "Every R column has four signed unit entries")
        odd = (q & c).bit_count() % 2
        targets = addresses ^ (q if odd else 0)
        signs = np.ones(512, dtype=np.int64) if odd else np.asarray(
            [1-2*((q & int(a)).bit_count() % 2) for a in addresses], dtype=np.int64)
        for i in support:
            for j in support:
                keys[offset:offset+512] = (512*i+targets)*N+512*j+addresses
                coefficients[offset:offset+512] = int(R[i, port]*R[j, port])*signs
                offset += 512
    order = np.argsort(keys)
    keys = keys[order]
    coefficients = coefficients[order]
    starts = np.flatnonzero(np.r_[True, keys[1:] != keys[:-1]])
    coefficients = np.add.reduceat(coefficients, starts)
    keys = keys[starts]
    keep = coefficients != 0
    keys, coefficients = keys[keep], coefficients[keep]
    row, column = keys//N, keys % N
    row_starts = np.flatnonzero(np.r_[True, row[1:] != row[:-1]])
    require(np.array_equal(row[row_starts], np.arange(N)), "All output rows are present")
    max_row_sum = int(np.max(np.add.reduceat(abs(coefficients), row_starts)))
    require(max_row_sum <= 224, "Each integer row has absolute sum at most224")
    inverse4 = pow(4, -1, P)

    def seed_vector(seed):
        data = shake_256(seed.encode()).digest(8192)
        return np.asarray([int.from_bytes(data[k:k+2], "little")
                           for k in range(0, 8192, 2)], dtype=np.int64)

    initial = seed_vector(certificate["initial_seed"])
    observer = seed_vector(certificate["observer_seed"])
    value = initial.copy()
    moments = []
    degree = certificate["hankel_size"]
    require(degree == 409, "The claimed minor has order409")
    for _ in range(2*degree-1):
        moments.append(int(np.dot(observer, value) % P))
        value = (np.add.reduceat(coefficients*value[column], row_starts) % P)*inverse4 % P
    require(moments == certificate["moments"], "All817 independent sparse moments agree")
    moments_pin = sha256(json.dumps(moments).encode()).hexdigest()
    require(moments_pin == certificate["moments_sha256"], "The moment digest agrees")
    hankel = np.asarray([[moments[i+j] for j in range(degree)]
                         for i in range(degree)], dtype=np.int64)
    determinant = bareiss_mod(hankel)
    require(determinant == 2984 == certificate["hankel_determinant_mod_prime"],
            "A separate fraction-free determinant agrees and is nonzero")
    dependent = hankel.copy()
    dependent[:, -1] = dependent[:, 0]
    require(bareiss_mod(dependent) == 0, "The duplicated-column control is singular")
    report = {
        "status": "PASS_INDEPENDENT_EXACT_BELL_GRAM_DEGREE_CERTIFICATE",
        "certificate_sha256": sha256(certificate_raw).hexdigest(),
        "original_source_pins": pinned,
        "interface_sha256": sha256(interface_raw).hexdigest(),
        "independent_operator": "Sparse coordinate matrix4A, built from original-word R",
        "integer_operator_nonzero_entries": len(keys),
        "integer_operator_maximum_absolute_row_sum": max_row_sum,
        "exact_Bell_Pauli_columns": 112*512,
        "field_prime": P, "bell_constant": c, "tensor_size": 1,
        "moments_count": len(moments), "moments_sha256": moments_pin,
        "hankel_size": degree, "hankel_determinant_mod_prime": determinant,
        "determinant_method": "Fraction-free Bareiss elimination in the prime field",
        "duplicated_column_control_rejected": True,
        "arithmetic": "Signed int64 only; row sums below2^24, moment sums below2^44, elimination products below2^33",
        "proved_minimal_polynomial_degree_lower_bound_over_Q": degree,
        "proof": "A rational annihilator of degree below409 makes the rational Hankel minor singular. Its entries lie in Z[1/2], so its nonzero reduction modulo65537 proves it is nonzero overQ.",
        "all_positive_tensor_sizes": "Tensor the certified block with the common fixed Pauli-identity Bell vector in every remaining tensor block. The resulting invariant subspace carries the same4096-dimensional operator.",
        "scope": "The actual112-port weighted operator at every positive tensor size; the certificate uses its invariant k1 Bell blockc11",
        "not_claimed": ["An exact minimal polynomial", "A lower bound for general scalar ADD circuits",
                        "A native decoder cost bound", "A lower bound for matrix-valued or multiple-state encodings"],
    }
    (here/"BELL-GRAM-DEGREE-REVIEW.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    print(report["status"])
    print(json.dumps({key: report[key] for key in ("integer_operator_nonzero_entries", "hankel_determinant_mod_prime")}, sort_keys=True))


if __name__ == "__main__":
    main()
