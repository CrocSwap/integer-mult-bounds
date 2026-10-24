#!/usr/bin/env python3
"""Check the signed centre family and its exact reciprocal parameters."""

from collections import defaultdict
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
from pathlib import Path
import gzip
import json


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "bipartite-eight-20261018/BIPARTITE-EIGHT-PROGRAM.json.gz"
PIN = "0c832994c1d06562a8db0b9b3d940f6f6143c37beed983f874a69f2bf6ecfdee"


def need(value, message):
    if not value:
        raise RuntimeError(message)


def clean(row):
    return {p: v for p, v in row.items() if v}


def mul(a, b):
    result = []
    for row in a:
        out = defaultdict(F)
        for middle, left in row.items():
            for column, right in b[middle].items():
                out[column] += left * right
        result.append(clean(out))
    return result


def transpose(a, columns):
    out = [{} for _ in range(columns)]
    for i, row in enumerate(a):
        for j, value in row.items():
            out[j][i] = value
    return out


def restrict(a, ports):
    index = {p: i for i, p in enumerate(ports)}
    return [{index[p]: v for p, v in a[row].items() if p in index} for row in ports]


def determinant(a):
    n = len(a)
    rows = [[a[i].get(j, F(0)) for j in range(n)] for i in range(n)]
    result = F(1)
    for i in range(n):
        pivot = next((j for j in range(i, n) if rows[j][i]), None)
        if pivot is None:
            return F(0)
        if pivot != i:
            rows[i], rows[pivot] = rows[pivot], rows[i]
            result = -result
        value = rows[i][i]
        result *= value
        for j in range(i + 1, n):
            if rows[j][i]:
                ratio = rows[j][i] / value
                rows[j] = [a - ratio * b for a, b in zip(rows[j], rows[i])]
    return result


def unit(value):
    numerator, denominator = abs(value.numerator), value.denominator
    return bool(numerator) and numerator & (numerator - 1) == 0 and denominator & (denominator - 1) == 0


def dyadic(value):
    return value.denominator & (value.denominator - 1) == 0


def multiply(values):
    out = F(1)
    for value in values:
        out *= value
    return out


def main():
    raw = gzip.decompress(SOURCE.read_bytes())
    need(sha256(raw).hexdigest() == PIN, "Pinned source changed")
    source = json.loads(raw)
    decode = lambda rows: [{int(p): F(v) for p, v in row.items()} for row in rows]
    base, g, k = decode(source["response"]), decode(source["signed_monomial"]), decode(source["centre_rows"])
    large, small, selected = source["large_ports"], source["small_ports"], source["selected_ports"]
    partners = source["partner_ports"]
    ordinary = sorted(set(large) - set(selected))
    alpha = [F(v) for v in source["component_signs"]]
    kt = transpose(k, 112)
    need(mul(k, kt) == [{i: F(12)} for i in range(8)], "Actual K K transpose is 12I")
    expected_gk = [{j: value * alpha[j] for j, value in row.items()} for row in kt]
    need(mul(g, kt) == expected_gk, "Actual G K transpose is K transpose Lambda")
    need(mul(g, g) == [{p: F(1)} if p in large else {} for p in range(112)], "G is an involution on48")
    need(not any(restrict(g, selected)), "Selected G block is zero")
    need(determinant([kt[p] for p in selected]) == F(-4), "Selected centre minor has determinant -4")

    def response(beta, reciprocal_small=False):
        out = [dict(row) for row in g]
        for v, centre in enumerate(k):
            for p, left in centre.items():
                for q, right in centre.items():
                    out[p][q] = out[p].get(q, F(0)) - beta[v] * alpha[v] * left * right
        for p in small:
            out[p] = {q: value / (4 if reciprocal_small else 1) for q, value in base[p].items()}
        return [clean(row) for row in out]

    identity = [{p: F(1)} for p in range(112)]
    allowed = [F(1, 4), F(1, 8), F(-1, 4), F(1, 16)]
    cases = [(f"uniform_{value}", [value] * 8) for value in allowed]
    cases += [("mixed_four_parameters", allowed * 2),
              ("mixed_reverse_parameters", list(reversed(allowed)) * 2)]
    reports = []
    for name, beta in cases:
        spectral = [1 - 12 * value for value in beta]
        reciprocal = [-value / s for value, s in zip(beta, spectral)]
        e, ei = response(beta), response(reciprocal, reciprocal_small=True)
        need(mul(e, ei) == identity and mul(ei, e) == identity, "Both full112 reciprocal orders")
        dl = determinant(restrict(e, selected))
        dh = determinant(restrict(e, ordinary))
        expected = 16 * multiply(beta)
        need(dl == dh == expected and unit(dl), "Both actual principal determinants")
        need(determinant(restrict(e, large)) == multiply(spectral), "Actual48 response determinant")
        reports.append({"case": name, "beta": [str(v) for v in beta],
                        "reciprocal_beta": [str(v) for v in reciprocal],
                        "selected_determinant": str(dl), "ordinary40_determinant": str(dh),
                        "response48_determinant": str(multiply(spectral)),
                        "both_full112_inverse_orders": True})

    parameters = []
    for exponent in range(-64, 65):
        spectral = F(-2) ** exponent
        beta = (1 - spectral) / 12
        need(dyadic(beta), "Every sampled integral exponent gives a dyadic coefficient")
        need(unit(beta) == (exponent in (-2, -1, 1, 2)), "Only the four nonzero principal-unit parameters")
        parameters.append({"n": exponent, "beta": str(beta), "s": str(spectral), "beta_is_unit": unit(beta)})

    count = 0
    determinant_histogram = defaultdict(int)
    for beta in product(allowed, repeat=8):
        spectral = [1 - 12 * value for value in beta]
        reciprocal = [-value / s for value, s in zip(beta, spectral)]
        need(all(v in allowed for v in reciprocal), "The four-parameter family is closed under inversion")
        value = 16 * multiply(beta)
        need(unit(value) and all(unit(s) for s in spectral), "All component choices give full and principal units")
        determinant_histogram[str(value)] += 1
        count += 1
    need(count == 65536, "The independent eight-component count is4^8")
    receipt = {"status": "PASS_RECIPROCAL_SIGNED_CENTRE_FAMILY",
               "scope": "Exact coefficient family and actual source matrix checks; independently adjustable centre scatter and full native composition remain implementation premises",
               "source_payload_decompressed_sha256": PIN,
               "selected_ports": selected, "partner_ports": partners,
               "full112_matrix_cases": reports, "component_choice_count": count,
               "principal_determinant_histogram": dict(sorted(determinant_histogram.items())),
               "exponent_spot_check_range": [-64, 64],
               "exponent_classification_basis": "The proof uses reduction modulo3 and the exact dyadic-unit equations, not a bounded search",
               "parameters_with_both_units": [v for v in parameters if v["beta_is_unit"]],
               "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "RECIPROCAL-CENTRES.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
