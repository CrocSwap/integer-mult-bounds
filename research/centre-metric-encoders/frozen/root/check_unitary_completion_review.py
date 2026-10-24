#!/usr/bin/env python3
"""Check the unitary centre code with an independent real matrix engine."""

import argparse
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / (
    "lanes/new-core-transfer-20261017/low-displacement-20261020/"
    "metric-completion-20261020/unitary-v2-normal/UNITARY-COMPLETION.json.gz"
)
SOURCE_PIN = "fd3b442caa13104cef4b7c046e1c2781f2ffa216d8d098b4e2a4e51e6063f428"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(size):
    return [{j: Fraction(1)} for j in range(size)]


def product(left, right):
    result = []
    for row in left:
        out = {}
        for j, a in row.items():
            for k, b in right[j].items():
                out[k] = out.get(k, Fraction(0)) + a * b
        result.append({k: v for k, v in out.items() if v})
    return result


def transpose(matrix, columns):
    result = [{} for _ in range(columns)]
    for j, row in enumerate(matrix):
        for k, value in row.items():
            result[k][j] = value
    return result


def real_matrix(rows):
    result = [{} for _ in range(2 * len(rows))]
    for p, row in enumerate(rows):
        for raw_q, pair in row.items():
            q = int(raw_q)
            a, b = map(Fraction, pair)
            for i, j, v in ((2*p, 2*q, a), (2*p, 2*q+1, -b),
                            (2*p+1, 2*q, b), (2*p+1, 2*q+1, a)):
                if v:
                    result[i][j] = v
    return result


def rank_mod_three(matrix):
    pivots = {}
    for row in matrix:
        current = {j: (v.numerator * pow(v.denominator, -1, 3)) % 3
                   for j, v in row.items()}
        current = {j: v for j, v in current.items() if v}
        while current:
            j = min(current)
            if j not in pivots:
                inverse = pow(current[j], -1, 3)
                pivots[j] = {k: v * inverse % 3 for k, v in current.items()}
                break
            multiple = current[j]
            for k, value in pivots[j].items():
                current[k] = (current.get(k, 0) - multiple * value) % 3
                if not current[k]:
                    del current[k]
    return len(pivots)


def replay(word):
    state = identity(1280)
    maximum, height, price = Fraction(1), 0, 0
    for operation, target, source, raw in word:
        coefficient = Fraction(raw)
        require(0 <= target < 224, "A component instruction leaves the code.")
        if operation == "add":
            require(0 <= source < 224 and source != target,
                    "An ADD source is invalid.")
            for j, value in state[source].items():
                state[target][j] = state[target].get(j, Fraction(0)) + coefficient * value
            state[target] = {j: value for j, value in state[target].items() if value}
            a, b = abs(coefficient.numerator), coefficient.denominator
            price += 1 + a.bit_length() + a.bit_count() + b.bit_length()
        else:
            require(operation == "scale" and coefficient, "A SCALE is invalid.")
            numerator, denominator = abs(coefficient.numerator), coefficient.denominator
            require(numerator & (numerator-1) == denominator & (denominator-1) == 0,
                    "A SCALE is not a signed power of two.")
            state[target] = {j: coefficient * value for j, value in state[target].items()}
            price += abs(numerator.bit_length() - denominator.bit_length()) + (coefficient < 0)
        maximum = max(maximum, sum(map(abs, state[target].values())))
        for value in state[target].values():
            d = value.denominator
            require(d & (d-1) == 0, "A component value is not dyadic.")
            height = max(height, d.bit_length()-1)
    return state, {"price": price, "prefix_one_norm": str(maximum), "binary_height": height}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    raw = gzip.decompress(SOURCE.read_bytes())
    require(hashlib.sha256(raw).hexdigest() == SOURCE_PIN, "The code source pin differs.")
    data = json.loads(raw)
    checked_pins = {}
    native = None
    for name, pin in data["source_pins"].items():
        if not isinstance(pin, dict):
            continue
        path = Path(pin["path"])
        content = path.read_bytes()
        if path.suffix == ".gz":
            content = gzip.decompress(content)
        digest = hashlib.sha256(content).hexdigest()
        require(digest == pin["sha256"], "A direct source pin differs: " + name)
        checked_pins[name] = digest
        if name == "native":
            native = json.loads(content)["model"]
    code = real_matrix(data["code"])
    inverse = real_matrix(data["inverse_and_adjoint"])
    response = real_matrix(data["response"])
    coded_response = real_matrix(data["coded_response"])
    mode = real_matrix(data["mode_code"])
    mode_response = real_matrix(data["mode_response"])
    mode_coded = real_matrix(data["mode_coded_response"])
    readers = real_matrix(data["original_centre_readers"])
    decoder = real_matrix(data["full_carrier_centre_decoder"])
    eye = identity(224)
    require(inverse == transpose(code, 224), "The code inverse is not its real adjoint.")
    require(product(code, inverse) == product(inverse, code) == eye,
            "A unitary product differs from the identity.")
    require(product(mode, transpose(mode, 224)) == eye, "The mode code is not unitary.")
    require(product(code, response) == coded_response, "The physical response differs.")
    require(product(mode, mode_response) == mode_coded, "The mode response differs.")
    require(all(j not in row and (j ^ 1) not in row for j, row in enumerate(code)),
            "A physical complex diagonal is nonzero.")
    require(all(j not in row and (j ^ 1) not in row for j, row in enumerate(mode)),
            "A mode complex diagonal is nonzero.")
    selected = set(data["selected_full_ports"])
    ordinary = set(data["ordinary_ports"])
    require(len(selected) == 32 and len(ordinary) == 80
            and selected.isdisjoint(ordinary) and selected | ordinary == set(range(112)),
            "The selected partition differs.")
    require(all(coded_response[2*p+i] == code[2*p+i]
                for p in ordinary for i in (0, 1)), "An ordinary row changed.")
    require(all(j // 2 in selected for row in decoder for j in row),
            "A centre reader uses an ordinary output.")
    require(product(decoder, code) == readers, "The centre decoder is incorrect.")
    gram = product(readers, transpose(readers, 224))
    require(gram == [{j: Fraction(12 if j < 16 else 8)} for j in range(32)],
            "The exact real centre Gram matrix differs.")
    reader_rank = rank_mod_three(readers)
    gram_rank = rank_mod_three(gram)
    require(reader_rank == 32 and gram_rank == 16, "A finite-field rank differs.")
    minimum_real_coordinates = 2 * reader_rank - gram_rank
    code24 = [dict(row) for row in code]
    require(native is not None, "The native model is absent.")
    for clique in native["small_cliques"]:
        require(len(clique) == 8, "An eight-port clique is absent.")
        for i, p in enumerate(clique):
            code24[2*p], code24[2*p+1] = {}, {}
            for j, q in enumerate(clique):
                coefficient = Fraction((-1) ** ((i & j).bit_count()), 4)
                code24[2*p][2*q] = code24[2*p+1][2*q+1] = coefficient
                code24[2*p][2*q+1] = -coefficient
                code24[2*p+1][2*q] = coefficient
    inverse24 = transpose(code24, 224)
    require(product(code24, inverse24) == product(inverse24, code24) == eye,
            "The abstract 24-coordinate code is not unitary.")
    decoder24 = product(readers, inverse24)
    support24 = sorted({j // 2 for row in decoder24 for j in row})
    require(len(support24) == 24 and product(decoder24, code24) == readers,
            "The abstract 24-coordinate code does not attain the bound.")
    bad_ordinary_diagonals = [
        p for p in range(112) if p not in support24
        and any(2*p+i in code24[2*p] for i in (0, 1))
    ]
    require(len(bad_ordinary_diagonals) == 56,
            "The abstract code native-support limit differs.")
    checks = {}
    for name, wanted in (("code", code), ("inverse_and_adjoint", inverse)):
        actual, receipt = replay(data["component_words"][name])
        require(actual == wanted + identity(1280)[224:],
                "The complete real component word is incorrect: " + name)
        require(receipt["price"] == 5460, "The literal component price differs.")
        changed = list(data["component_words"][name])
        deletion = next(i for i, gate in enumerate(changed) if gate[0] == "add")
        del changed[deletion]
        require(replay(changed)[0] != actual, "The missing ADD control was not rejected.")
        checks[name] = receipt
    wrong_adjoint = [dict(row) for row in inverse]
    p = next(p for p, row in enumerate(wrong_adjoint) if row)
    j = next(iter(wrong_adjoint[p]))
    wrong_adjoint[p][j] *= -1
    require(product(code, wrong_adjoint) != eye, "The wrong adjoint control was not rejected.")
    output = {
        "source_sha256_decompressed": SOURCE_PIN,
        "direct_source_pins_checked": checked_pins,
        "independent_engine": "Real sparse matrices over Fraction; no producer code imports.",
        "physical_complex_columns": 112,
        "arbitrary_real_columns_per_component_word": 1280,
        "unchanged_real_columns_per_component_word": 1056,
        "centre_readers": 16,
        "selected_full_ports": 32,
        "ordinary_ports": 80,
        "component_words": checks,
        "unitary_coordinate_bound": {
            "prime": 3, "real_reader_rank": reader_rank, "real_gram_rank": gram_rank,
            "minimum_real_coordinates": minimum_real_coordinates,
            "minimum_complex_coordinates": minimum_real_coordinates // 2,
            "abstract_attainment_ports": support24,
            "abstract_attainment_failed_ordinary_native_diagonals": bad_ordinary_diagonals,
        },
        "negative_controls": ["one deleted ADD in each word", "one wrong adjoint entry"],
        "scope": "Scalar code and response algebra only. No native service or routed caller.",
    }
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"pass": True, "source": SOURCE_PIN, "output": str(args.out)}))


if __name__ == "__main__":
    main()
