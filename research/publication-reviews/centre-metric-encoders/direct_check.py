"""Check the main matrix claims with a separate exact engine."""

import argparse
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path


def need(value, message):
    if not value:
        raise ValueError(message)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def mul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


ZERO = (F(0), F(0))
ONE = (F(1), F(0))


def rows(raw):
    return [{int(j): tuple(map(F, value)) if isinstance(value, list) else (F(value), F(0))
             for j, value in row.items()} for row in raw]


def star(a, size):
    out = [{} for _ in range(size)]
    for i, row in enumerate(a):
        for j, (x, y) in row.items():
            out[j][i] = (x, -y)
    return out


def product(a, b):
    out = []
    for row in a:
        result = {}
        for j, x in row.items():
            for k, y in b[j].items():
                value = add(result.get(k, ZERO), mul(x, y))
                if value == ZERO:
                    result.pop(k, None)
                else:
                    result[k] = value
        out.append(result)
    return out


def realify(a):
    out = [{} for _ in range(2 * len(a))]
    for i, row in enumerate(a):
        for j, (x, y) in row.items():
            for target, source, value in ((2*i, 2*j, x), (2*i, 2*j+1, -y),
                                          (2*i+1, 2*j, y), (2*i+1, 2*j+1, x)):
                if value:
                    out[target][source] = value
    return out


def rank_mod(a, prime):
    pivots = {}
    for raw in a:
        row = {j: value.numerator * pow(value.denominator, -1, prime) % prime
               for j, value in raw.items()}
        row = {j: value for j, value in row.items() if value}
        while row:
            j = min(row)
            value = row[j]
            if j not in pivots:
                inverse = pow(value, -1, prime)
                pivots[j] = {k: v * inverse % prime for k, v in row.items()}
                break
            for k, v in pivots[j].items():
                new = (row.get(k, 0) - value*v) % prime
                if new:
                    row[k] = new
                else:
                    row.pop(k, None)
    return len(pivots)


def diagonal(values):
    return [{i: (F(value), F(0))} for i, value in enumerate(values)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    frozen = args.package / "frozen"
    pins = {}

    def read(relative):
        raw = (frozen / relative).read_bytes()
        pins[relative] = hashlib.sha256(raw).hexdigest()
        return json.loads(gzip.decompress(raw))

    c24 = read("lanes/new-core-transfer-20261017/low-displacement-20261020/metric-completion-20261020/twenty-four-v2-normal/UNITARY-24.json.gz")
    response = read("lanes/oblique-native-20261017/signed-metric-reciprocal-20261020/model-normal-v2/RESPONSE.json.gz")
    rational = read("lanes/independent-review-20261017/odd-unitary-packing-20261020/run-normal/PACKING.json.gz")
    companion = read("lanes/new-core-transfer-20261017/low-displacement-20261020/signed-sixteen-20261020/paired-normal/PAIRED-SIGNED-SIXTEEN.json.gz")
    v = rows(c24["original_centre_readers"])
    vg = product(v, star(v, 112))
    need(vg == diagonal([12]*8 + [8]*8), "Original reader Gram")
    need((rank_mod(realify(v), 3), rank_mod(realify(vg), 3)) == (32, 16),
         "Original reader and Gram ranks")
    code = rows(c24["code"])
    cs = star(code, 112)
    need(product(code, cs) == product(cs, code) == diagonal([1]*112), "C24 is unitary")
    decoder = product(v, cs)
    need(len({j for row in decoder for j in row}) == 24, "C24 uses 24 coordinates")
    need(product(decoder, code) == v, "C24 recovers the original reader")

    ell = rows(response["reflection_L"])
    lg = product(ell, star(ell, 112))
    need(lg == diagonal([10]*8 + [7]*8), "Reciprocal reader Euclidean Gram")
    modular = {str(p): [rank_mod(realify(ell), p), rank_mod(realify(lg), p)] for p in (3, 5, 7)}
    need(modular == {"3": [32, 32], "5": [32, 16], "7": [32, 16]}, "Reciprocal modular ranks")
    k = rows(response["physical"]["inverse_J"])
    need(product(product(ell, k), star(ell, 112)) == diagonal([4]*8 + [2]*8),
         "Reciprocal weighted Gram")
    physical_p = rows(response["physical"]["P"])
    need(sum(len(row) for row in physical_p) == 160, "Physical P has 160 nonzero entries")
    need(sum(row != {i: ONE} for i, row in enumerate(physical_p)) == 32,
         "Physical P changes 32 ports")
    companion_decoder = product(ell, rows(companion["inverse"]))
    transpose_decoder = product(ell, rows(companion["inverse_transpose"]))
    companion_support = {j for row in companion_decoder for j in row}
    transpose_support = {j for row in transpose_decoder for j in row}
    need(companion_support == set(companion["centre_ports"]), "Cbar recovers L from its 16 selected outputs")
    need(len(transpose_support) == 96 and not transpose_support <= set(companion["centre_ports"]),
         "Cbar transpose is a companion interface, not a 16-coordinate L code")
    need(product(transpose_decoder, rows(companion["transpose"])) == ell,
         "The full transpose decoder is the unique exact L decoder")

    c16 = rows(rational["code"])
    c16star = star(c16, 112)
    need(product(c16, c16star) == product(c16star, c16) == diagonal([1]*112), "C16 is unitary")
    trace = ZERO
    for i, row in enumerate(c16):
        trace = add(trace, row.get(i, ZERO))
    need(trace == (F(11, 6), F(7, 6)), "Complete C16 trace")
    trace_residue = [(3*x).numerator * pow((3*x).denominator, -1, 3) % 3 for x in trace]
    need(trace_residue == [1, 2], "Nonzero residue trace proves non-nilpotence")
    residue = [{j: (3*a, 3*b) for j, (a, b) in row.items()} for row in c16]
    need(rank_mod(realify(residue), 3) == 8, "Complete residue has Gaussian rank four")
    decoder16 = product(v, c16star)
    need(len({j for row in decoder16 for j in row}) == 16, "Rational C16 uses 16 coordinates")
    need(product(decoder16, c16) == v, "C16 recovers the original reader")
    ordinary = rational["ordinary_ports"]
    need(len(ordinary) == 96 and all(c16[i].get(i, ZERO) != ZERO for i in ordinary),
         "All 96 ordinary C16 diagonals are nonzero")

    result = {"status": "PASS_DIRECT_ENCODER_MATRIX_CHECKS", "producer_imports": 0,
              "original_real_ranks_mod3": [32, 16], "original_complex_bound": 24,
              "reciprocal_real_ranks": modular, "reciprocal_complex_bound_mod5_or_mod7": 24,
              "original_gram": [12]*8 + [8]*8, "reciprocal_gram": [10]*8 + [7]*8,
              "reciprocal_weighted_gram": [4]*8 + [2]*8,
              "physical_P_changed_ports": 32, "physical_P_nonzero_entries": 160,
              "Cbar_L_decoder_support": len(companion_support),
              "Cbar_transpose_L_decoder_support": len(transpose_support),
              "C24_selected_support": 24, "C16_selected_support": 16,
              "C16_trace": list(map(str, trace)), "C16_scaled_trace_mod3": trace_residue,
              "C16_residue_real_rank_mod3": 8, "C16_nonzero_ordinary_diagonals": 96,
              "input_sha256": pins,
              "scope": "Independent exact matrix checks. The proof of all-power height uses the nonzero residue trace. No native or recursive theorem is inferred from these calculations."}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
