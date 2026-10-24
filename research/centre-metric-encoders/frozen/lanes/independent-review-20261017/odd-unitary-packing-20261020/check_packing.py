"""Construct the actual sixteen-coordinate unitary code with odd divisor three."""

import argparse
from fractions import Fraction as F
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
HELPER = HERE.parent / "unitary-footprint-review-20261020/check_review.py"
HELPER_PIN = "a834f297f9cc82de9b29f4cd17ac762ed371d9a0b13bbac25b3430d2f87de25e"
SOURCE = HERE.parents[1] / "new-core-transfer-20261017/low-displacement-20261020/metric-completion-20261020"
PLACEMENT_PIN = "88a9f75fa87b1a258d6465e309785c1aaec1be6393d46e51bc0a469e62f09e5e"
CODE_PIN = "9be7deb70acfc20d98408c84d59a24dbd6e2eddaea408958ec64b6003eb75f8c"


def need(value, label):
    if not value:
        raise ValueError(label)


def serialize(matrix):
    return [{str(j): [str(x), str(y)] for j, (x, y) in sorted(row.items())}
            for row in matrix]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    need(sha256(HELPER.read_bytes()).hexdigest() == HELPER_PIN, "Independent arithmetic pin")
    spec = importlib.util.spec_from_file_location("packing_arithmetic", HELPER)
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    placement = json.loads(g.read_pinned(
        SOURCE / "signed-probe/METRIC-COMPLETION.json.gz", PLACEMENT_PIN))
    source = json.loads(g.read_pinned(
        SOURCE / "twenty-four-v2-normal/UNITARY-24.json.gz", CODE_PIN))
    h = g.rows(placement["pair_code"], True)
    v, e = g.rows(source["original_centre_readers"]), g.rows(source["response"])
    large = [block for block in placement["mode_blocks"] if block["kind"] == "large6"]
    small = [block for block in placement["mode_blocks"] if block["kind"] == "small8"]
    large_ports = {p for block in large for p in block["ports"]}
    alpha, beta = (F(1,2), F(1,2)), (F(1,4), F(1,4))
    normalized_pair = [{j: g.times(alpha, x) if i in large_ports else x for j, x in row.items()}
                       for i, row in enumerate(h)]
    need(g.product(normalized_pair, g.adjoint(normalized_pair, 112)) == g.eye(112),
         "Actual Gaussian dyadic unitary pair encoder")
    mode = g.eye(112)
    word = []

    def cadd(target, source_field, value):
        for component in (0, 1):
            word.append(["add", 2*target+component, 2*source_field+component, str(value)])

    def cscale(target, value):
        for component in (0, 1):
            word.append(["scale", 2*target+component, None, str(value)])

    def c_alpha(target):
        x, y = 2*target, 2*target+1
        word.extend([["add", x, y, "-1"], ["scale", y, None, "2"],
                     ["add", y, x, "1"], ["scale", x, None, "1/2"],
                     ["scale", y, None, "1/2"]])

    def raw_hadamard(a, b):
        cadd(a, b, 1)
        cscale(b, -2)
        cadd(b, a, 1)

    def walsh(ports):
        bit = 1
        while bit < len(ports):
            for j in range(len(ports)):
                if not j & bit:
                    raw_hadamard(ports[j], ports[j | bit])
            bit *= 2

    pairs = sorted({tuple(sorted(h[p])) for p in large_ports})
    need(len(pairs) == 24 and all(len(pair) == 2 for pair in pairs), "Actual24 physical pairs")
    for a, b in pairs:
        aa, bb, cc, dd = [h[x][y][0] for x, y in ((a,a),(a,b),(b,a),(b,b))]
        need(all(x in (-1, 1) for x in (aa,bb,cc,dd)), "Signed Hadamard pair")
        sign = cc / aa
        need(dd == -bb*sign, "Pair sign factor")
        if aa < 0:
            cscale(a, -1)
        if bb < 0:
            cscale(b, -1)
        raw_hadamard(a, b)
        if sign < 0:
            cscale(b, -1)
        c_alpha(a)
        c_alpha(b)
    large_carriers = []
    for block in large:
        ports, signs = block["ports"], block["signs"]
        for port, sign in zip(ports, signs):
            if sign < 0:
                cscale(port, -1)
        for i in range(4):
            mode[ports[i]] = {
                ports[j]: (F(signs[j] * (-1 if (i & j).bit_count() % 2 else 1), 2), F(0))
                for j in range(4)}
        for i in range(2):
            mode[ports[4+i]] = {
                ports[4+j]: g.times(alpha, (F(signs[4+j] * (-1 if i*j else 1)), F(0)))
                for j in range(2)}
        walsh(ports[:4])
        for port in ports[:4]:
            cscale(port, F(1,2))
        raw_hadamard(ports[4], ports[5])
        c_alpha(ports[4])
        c_alpha(ports[5])
        large_carriers.append([ports[0], ports[4]])
    small_carriers = []
    for block in small:
        ports = block["ports"]
        for i, port in enumerate(ports):
            mode[port] = {
                ports[j]: g.times(beta, (F(-1 if (i & j).bit_count() % 2 else 1), F(0)))
                for j in range(8)}
        walsh(ports)
        for port in ports:
            c_alpha(port)
            cscale(port, F(1,2))
        small_carriers.append(ports[0])
    cpre = g.product(mode, normalized_pair)
    cprei = g.adjoint(cpre, 112)
    need(g.product(cpre, cprei) == g.product(cprei, cpre) == g.eye(112), "Precode unitary orders")
    decoder_pre = g.product(v, cprei)
    wanted_pre = [{ports[0]: (F(2),F(-2)), ports[1]: (F(0),F(-2))}
                  for ports in large_carriers]
    wanted_pre += [{port: (F(2),F(-2))} for port in small_carriers]
    need(decoder_pre == wanted_pre, "Actual preliminary centre coefficients")
    inverse_word = [[op, target, source_field, str(-F(value) if op == "add" else 1/F(value))]
                    for op, target, source_field, value in reversed(word)]
    reports = {}
    for name, instructions, matrix in (("precode", word, cpre), ("precode_adjoint", inverse_word, cprei)):
        need(all(0 <= x[1] < 224 and (x[0] == "scale" or 0 <= x[2] < 224) for x in instructions),
             "Arbitrary528 outside complex fields stay fixed")
        expected = g.realify(matrix, 112)
        need(g.pullback(instructions) == expected, "All1280 precode real input columns")
        forward, bounds = g.prefix_bounds(instructions)
        need(forward == expected, "Precode prefix replay")
        reports[name] = {"instructions": len(instructions),
                         "scalar": sum(map(g.tariff, instructions)), **bounds}

    a = [{0:(F(1),F(0)),1:(F(1),F(1))},
         {0:(F(-1),F(1)),1:(F(1),F(0))}]
    b = [{0:(F(1),F(-1)),1:(F(0),F(-1))},
         {0:(F(0),F(-1)),1:(F(1),F(1))}]
    three = [{j:(F(3),F(0))} for j in range(2)]
    need(g.product(a,g.adjoint(a,2)) == g.product(b,g.adjoint(b,2)) == three,
         "Two integer Gaussian norm-three factors")

    def doubled(matrix):
        return [{j+2*block:x for j,x in row.items()} for block in range(2) for row in matrix]

    permutation = [{j:g.ONE} for j in (0,2,1,3)]
    numerator = g.product(g.product(doubled(g.adjoint(a,2)), permutation), doubled(b))
    packing = [{j:g.times((F(1,3),F(0)),x) for j,x in row.items()} for row in numerator]
    packing_inverse = g.adjoint(packing,4)
    need(g.product(packing,packing_inverse) == g.product(packing_inverse,packing) == g.eye(4),
         "Packing unitary products")
    target = [{j:g.times((F(2),F(0)),x) for j,x in row.items()} for row in a]
    old_readers = [{j+2*i:g.times((F(2),F(0)),x) for j,x in b[0].items()} for i in range(2)]
    need(g.product(target,packing) == old_readers, "Exact four-to-two packing equation")
    global_packing = g.eye(112)
    pack_ports, selected = [], list(small_carriers)
    for i in range(0,8,2):
        ports = large_carriers[i]+large_carriers[i+1]
        pack_ports.append(ports)
        selected.extend(ports[:2])
        for row, port in zip(packing, ports):
            global_packing[port] = {ports[j]:x for j,x in row.items()}
    c = g.product(global_packing,cpre)
    ci = g.adjoint(c,112)
    decoder = g.product(v,ci)
    need(g.product(c,ci) == g.product(ci,c) == g.eye(112), "Complete sixteen-output unitary")
    need(set().union(*(set(row) for row in decoder)) == set(selected) and len(set(selected)) == 16,
         "Exact sixteen-coordinate footprint")
    need(g.product(decoder,c) == v, "Actual complete reader recovery")
    ce = g.product(c,e)
    ordinary = set(range(112))-set(selected)
    need(all(c[p] == ce[p] for p in ordinary), "All96 ordinary response rows")
    odd_height = binary_height = 0
    for matrix in (c,ci):
        for row in matrix:
            for z in row.values():
                for coefficient in z:
                    denominator = coefficient.denominator
                    two = three_power = 0
                    while denominator % 2 == 0:
                        two += 1
                        denominator //= 2
                    while denominator % 3 == 0:
                        three_power += 1
                        denominator //= 3
                    need(denominator == 1 and three_power <= 1, "Only one factor three in endpoint entries")
                    binary_height, odd_height = max(binary_height,two), max(odd_height,three_power)
    need(odd_height == 1, "The odd factor is present")
    payload = {
        "schema":"actual-sixteen-coordinate-odd-unitary-v1",
        "selected_ports":sorted(selected), "ordinary_ports":sorted(ordinary),
        "large_precode_carriers":large_carriers, "small_precode_carriers":small_carriers,
        "packing_ports":pack_ports, "packing_order":"diag(B,B), P, diag(A*,A*), scalar1/3",
        "packing_integer_A":serialize(a), "packing_integer_B":serialize(b),
        "packing_numerator":serialize(numerator), "packing":serialize(packing),
        "packing_adjoint":serialize(packing_inverse), "packing_target_decoder":serialize(target),
        "precode":serialize(cpre), "precode_adjoint":serialize(cprei),
        "precode_words":{"precode":word,"precode_adjoint":inverse_word},
        "code":serialize(c), "code_adjoint":serialize(ci),
        "original_readers":serialize(v), "decoder":serialize(decoder),
        "coded_response":serialize(ce),
        "source_pins":{"independent_arithmetic":HELPER_PIN,"actual_24_code":CODE_PIN,
                       "actual_placement":PLACEMENT_PIN},
        "scope":"Actual common-frame matrices and paid dyadic precode only. Packing component word, grid admission, native support and caller are separate.",
    }
    encoded = (json.dumps(payload,sort_keys=True,separators=(",",":"))+"\n").encode()
    (args.out/"PACKING.json.gz").write_bytes(gzip.compress(encoded,mtime=0))
    receipt = {
        "status":"PASS_ACTUAL_ODD_UNITARY_PACKING",
        "payload_decompressed_sha256":sha256(encoded).hexdigest(),
        "source_pins":payload["source_pins"], "arbitrary_real_precode_columns":1280,
        "unchanged_outside_complex_fields":528, "precode_words":reports,
        "complete_code_selected_fields":16, "ordinary_response_equal_rows":96,
        "complete_code_maximum_binary_denominator_height":binary_height,
        "complete_code_maximum_three_denominator_height":odd_height,
        "ordinary_code_nonzero_diagonals":sum(p in c[p] for p in ordinary),
        "packing_component_word_emitted":False, "complete_native_service":False,
        "recursive_grid_contract_admitted":False, "new_owned_fields":0,
    }
    (args.out/"CHECKS.json").write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    print(receipt["status"])
    print(json.dumps(reports,sort_keys=True))


if __name__ == "__main__":
    main()
