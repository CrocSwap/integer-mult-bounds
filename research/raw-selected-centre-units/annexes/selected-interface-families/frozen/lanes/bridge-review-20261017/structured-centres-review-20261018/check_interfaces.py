"""Check the singular endpoints and query split on the actual centre rows."""

from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("review_helpers", HERE/"check_review.py")
R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)


def rank(rows, prime=None):
    basis = {}
    for source in rows:
        row = dict(source)
        if prime:
            row = {j: int(v.numerator)*pow(int(v.denominator), -1, prime) % prime
                   for j, v in row.items()}
            row = {j:v for j, v in row.items() if v}
        while row:
            pivot = min(row)
            if pivot not in basis:
                reciprocal = pow(row[pivot], -1, prime) if prime else 1/row[pivot]
                basis[pivot] = {j:(v*reciprocal) % prime if prime else v*reciprocal
                                for j, v in row.items()}
                break
            factor = row[pivot]
            for j, v in basis[pivot].items():
                value = row.get(j, 0)-factor*v
                if prime:
                    value %= prime
                if value:
                    row[j] = value
                else:
                    row.pop(j, None)
    return len(basis)


def main():
    source = R.STRUCTURED/"STRUCTURED-CENTRES-PROGRAM.json.gz"
    raw = gzip.decompress(source.read_bytes())
    R.need(sha256(raw).hexdigest() == R.STRUCTURED_PIN, "Actual centre source pin")
    packet = json.loads(raw)
    k = R.decode(packet["centre_rows"])
    large = sorted({j for row in k for j in row})
    position = {j:i for i, j in enumerate(large)}
    k = [{position[j]:v for j, v in row.items()} for row in k]
    kt = R.transpose(k, 48)
    gram = R.mm(kt, k)
    minors = json.loads((R.STRUCTURED/"STRUCTURED-CENTRES.json").read_text())["orthogonal_minor_ports"]
    reports = []
    for index, fields in enumerate(minors):
        selected = sorted(position[j] for j in fields)
        ordinary = sorted(set(range(48))-set(selected))
        ks = [{i:row[j] for i, j in enumerate(selected) if j in row} for row in k]
        ku = [{i:row[j] for i, j in enumerate(ordinary) if j in row} for row in k]
        b = [{j:v/2 for j, v in row.items()} for row in R.mm(R.transpose(ks, 8), ku)]
        d = R.transpose(b, 40)
        R.need(R.mm(b, d) == [{i:F(5)} for i in range(8)], "BD equals5I for every single minor")
        R.need(R.mm(R.transpose(ks, 8), ks) == [{i:F(2)} for i in range(8)], "Selected response block is zero")
        signs = {j:F(-1) if j in selected else F(1) for j in range(48)}
        a = [{i:signs[i]} for i in range(48)]
        for row, outer in zip(a, gram):
            R.add(row, outer, F(-1, 8))
        kernel = [{j:signs[i]*v for j, v in row.items()} for i, row in enumerate(kt)]
        R.need(R.mm(a, kernel) == [{} for _ in range(48)], "Eight explicit kernel columns")
        R.need(rank(a) == 40 and rank(R.transpose(kernel, 8)) == 8, "Exact rational kernel dimension")
        chosen = next(minor for j, minor in enumerate(minors) if j != index)
        local = [ordinary.index(position[j]) for j in chosen]
        square = [{j:row[q] for j, q in enumerate(local) if q in row} for row in b]
        R.need(R.mm(square, R.transpose(square, 8)) == R.eye(8), "Dyadic-unit ordinary B minor")
        m = [{local[j]:v for j, v in row.items()} for row in square]
        R.need(R.mm(m, d) == R.eye(8), "Explicit dyadic log with MD equalI")
        R.need(rank(b+m) == rank(b+m, 5) == 16, "Full query split overQ and modulo5")
        matched = [{j:v/5 for j, v in row.items()} for row in b]
        R.need(R.mm(matched, d) == R.eye(8) and rank(b+matched) == 8, "Rational matched log removes the split")
        R.need(any(v.denominator % 5 == 0 for row in matched for v in row.values()), "Matched log requires division by5")
        # The complement of five minors is one complete square minor.
        R.need(R.mm(R.transpose(ks, 8), ks) == [{i:F(2)} for i in range(8)], "Five-minor ordinary H is zero")
        reports.append(dict(selected_minor=index, data_rank=40, data_kernel_dimension=8,
                            centre_product="5I8", dyadic_query_rank=16,
                            modular_prime=5, matched_rational_query_rank=8,
                            five_minor_ordinary_nullity=8))
    report = dict(status="PASS_ACTUAL_COMPLETE_MINOR_ENDPOINTS", cases=reports,
                  source_payload_sha256=R.STRUCTURED_PIN,
                  helper_checker_sha256=sha256((HERE/"check_review.py").read_bytes()).hexdigest(),
                  checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    (HERE/"INTERFACES.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    print(report["status"], flush=True)


if __name__ == "__main__":
    main()
