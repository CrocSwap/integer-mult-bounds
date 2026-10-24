"""Check the actual unitary code and the coordinate bound without producer code."""

import argparse
from fractions import Fraction as F
import gzip
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parents[2]
SOURCE = CAMPAIGN / "lanes/new-core-transfer-20261017/low-displacement-20261020/metric-completion-20261020"
PINS = {
    "root/UNITARY-FOOTPRINT-FREEZE-20261020.json":
        "9ec2cb0f38210cf95246991f9637c036c7e5489cfc9ad78b7075213d9ca3ba75",
    "root/UNITARY-CENTRE-FOOTPRINT-20261020.md":
        "464628f0966138a9f95c34d26abeed214ab38720916fb1214820dd62e998f0a0",
}
LOCAL_PINS = {
    "TWENTY-FOUR-FREEZE.json": "3fda436c0390fb8ef2ee72b4d9fe6ccbfc0ea994208f4d962bb9f43960af7a82",
    "UNITARY-24.md": "420e5d4eb13c43bfbd41614c7a686db49e1091bf06ed26039f231323208461a6",
    "twenty-four-v2-normal/UNITARY-24.json.gz":
        "9be7deb70acfc20d98408c84d59a24dbd6e2eddaea408958ec64b6003eb75f8c",
    "unitary-v2-normal/UNITARY-COMPLETION.json.gz":
        "fd3b442caa13104cef4b7c046e1c2781f2ffa216d8d098b4e2a4e51e6063f428",
    "signed-probe/METRIC-COMPLETION.json.gz":
        "88a9f75fa87b1a258d6465e309785c1aaec1be6393d46e51bc0a469e62f09e5e",
}
ZERO = (F(0), F(0))
ONE = (F(1), F(0))


def need(test, label):
    if not test:
        raise ValueError(label)


def plus(a, b):
    return a[0] + b[0], a[1] + b[1]


def times(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def conjugate(a):
    return a[0], -a[1]


def put(row, j, value):
    result = plus(row.get(j, ZERO), value)
    if result == ZERO:
        row.pop(j, None)
    else:
        row[j] = result


def rows(raw, real=False):
    return [{int(j): (F(v), F(0)) if real else tuple(map(F, v))
             for j, v in row.items()} for row in raw]


def eye(n):
    return [{j: ONE} for j in range(n)]


def adjoint(a, columns):
    out = [{} for _ in range(columns)]
    for i, row in enumerate(a):
        for j, x in row.items():
            out[j][i] = conjugate(x)
    return out


def product(a, b):
    out = []
    for row in a:
        result = {}
        for j, x in row.items():
            for k, y in b[j].items():
                put(result, k, times(x, y))
        out.append(result)
    return out


def realify(a, columns):
    out = [{} for _ in range(2 * len(a))]
    for i, row in enumerate(a):
        for j, (x, y) in row.items():
            for target, source, value in (
                    (2*i, 2*j, x), (2*i, 2*j+1, -y),
                    (2*i+1, 2*j, y), (2*i+1, 2*j+1, x)):
                if value:
                    out[target][source] = value
    need(all(j < 2 * columns for row in out for j in row), "Real column range")
    return out


def rank_mod_three(a, columns):
    a = [[int(row.get(j, 0).numerator) * pow(int(row.get(j, F(0)).denominator), -1, 3) % 3
          for j in range(columns)] for row in a]
    pivot = 0
    for j in range(columns):
        found = next((k for k in range(pivot, len(a)) if a[k][j]), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        a[pivot] = [(x * pow(a[pivot][j], -1, 3)) % 3 for x in a[pivot]]
        for k in range(pivot + 1, len(a)):
            value = a[k][j]
            if value:
                a[k] = [(x - value*y) % 3 for x, y in zip(a[k], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def tariff(event):
    op, _, _, raw = event
    value = F(raw)
    a, b = abs(value.numerator), value.denominator
    need(b & (b - 1) == 0, "Dyadic component coefficient")
    if op == "add":
        return 3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1
    need(op == "scale" and a and a & (a - 1) == 0, "Binary component scale")
    return abs(a.bit_length() - b.bit_length()) + int(value < 0)


def pullback(word):
    """Propagate each output covector backwards through the literal word."""
    out = []
    for output in range(224):
        row = {output: F(1)}
        for op, target, source, raw in reversed(word):
            coefficient = F(raw)
            if target not in row:
                continue
            if op == "scale":
                row[target] *= coefficient
            else:
                need(op == "add" and source != target, "A distinct ADD source")
                value = row.get(source, F(0)) + coefficient * row[target]
                if value:
                    row[source] = value
                else:
                    row.pop(source, None)
        out.append(row)
    return out


def prefix_bounds(word):
    a = [{j: F(1)} for j in range(224)]
    norm, height = F(1), 0
    for op, target, source, raw in word:
        coefficient = F(raw)
        if op == "scale":
            a[target] = {j: coefficient*x for j, x in a[target].items()}
        else:
            row = dict(a[target])
            for j, x in a[source].items():
                value = row.get(j, F(0)) + coefficient*x
                if value:
                    row[j] = value
                else:
                    row.pop(j, None)
            a[target] = row
        norm = max(norm, sum(map(abs, a[target].values()), F(0)))
        height = max(height, max((x.denominator.bit_length()-1 for x in a[target].values()), default=0))
    return a, {"prefix_one_norm": str(norm), "binary_height": height}


def read_pinned(path, pin):
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Source digest: " + str(path))
    return raw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    need(not args.out.exists(), "New output file")
    for name, pin in PINS.items():
        read_pinned(CAMPAIGN / name, pin)
    raw = {name: read_pinned(SOURCE / name, pin) for name, pin in LOCAL_PINS.items()}
    source = json.loads(raw["twenty-four-v2-normal/UNITARY-24.json.gz"])
    old = json.loads(raw["unitary-v2-normal/UNITARY-COMPLETION.json.gz"])
    placement = json.loads(raw["signed-probe/METRIC-COMPLETION.json.gz"])
    c, ci = rows(source["code"]), rows(source["inverse_and_adjoint"])
    v, e = rows(source["original_centre_readers"]), rows(source["response"])
    h, hi = rows(placement["pair_code"], True), rows(placement["pair_code_inverse"], True)
    need(product(h, hi) == product(hi, h) == eye(112), "Actual pair inverse")
    need(ci == adjoint(c, 112), "Literal adjoint")
    need(product(c, ci) == product(ci, c) == eye(112), "Both unitary products")
    need(v == rows(old["original_centre_readers"]), "Unchanged actual readers")
    need(e == rows(old["response"]), "Unchanged actual response")

    rebuilt_v, owner = [], {}
    for index, block in enumerate(placement["mode_blocks"]):
        ports = block["ports"]
        for port in ports:
            need(port not in owner, "Disjoint native mode blocks")
            owner[port] = index
        if block["kind"] == "large6":
            local = [{p: (F(s), F(0)) for p, s in zip(ports, block["signs"])}]
            rebuilt_v += product(local, h)
        else:
            rebuilt_v.append({p: ONE for p in ports})
    need(rebuilt_v == v, "Readers derived from actual block and pair geometry")
    gram = product(v, adjoint(v, 112))
    desired = [{j: (F(12 if j < 8 else 8), F(0))} for j in range(16)]
    need(gram == desired, "Actual reader Gram")
    rv, rg = realify(v, 112), realify(gram, 16)
    real_rank, real_gram_rank = rank_mod_three(rv, 224), rank_mod_three(rg, 32)
    need((real_rank, real_gram_rank) == (32, 16), "Actual real modulo-three ranks")
    need(rank_mod_three([{j: x for j, (x, _) in row.items()} for row in v], 112) == 16,
         "Actual complex modulo-three row rank")

    rebuilt_c = rows(old["code"])
    reflection_vector = [1, 1, -1, 0, -1, 0, 0, 0]
    reflection = [{j: (F(i == j)-F(reflection_vector[i]*reflection_vector[j], 2), F(0))
                   for j in range(8) if F(i == j)-F(reflection_vector[i]*reflection_vector[j], 2)}
                  for i in range(8)]
    need(product(reflection, reflection) == eye(8), "Small reflection involution")
    need(product([{j: ONE for j in range(8)}], reflection) == [{j: ONE for j in range(8)}],
         "Reflection fixes the centre")
    haar = [[1,1,1,1,1,1,1,1], [1,1,1,1,-1,-1,-1,-1],
            [1,1,-1,-1,0,0,0,0], [0,0,0,0,1,1,-1,-1],
            [1,-1,0,0,0,0,0,0], [0,0,1,-1,0,0,0,0],
            [0,0,0,0,1,-1,0,0], [0,0,0,0,0,0,1,-1]]
    normalizers = [(F(1,4),F(1,4))]*2 + [(F(1,2),F(0))]*2 + [(F(1,2),F(1,2))]*4
    normalized = [{j: times((F(x), F(0)), normalizers[i]) for j, x in enumerate(row) if x}
                  for i, row in enumerate(haar)]
    local = product(normalized, reflection)
    assignment = [0,1,5,3,2,7,6,4]
    small = [b for b in placement["mode_blocks"] if b["kind"] == "small8"]
    small_ports = {p for block in small for p in block["ports"]}
    selected = set(old["selected_full_ports"]) - small_ports
    for block in small:
        ports = block["ports"]
        selected.add(ports[0])
        for row, target in zip(local, assignment):
            rebuilt_c[ports[target]] = {ports[j]: x for j, x in row.items()}
    need(rebuilt_c == c, "Independent Haar/reflection construction on actual ports")
    need(selected == set(source["selected_full_ports"]) and len(selected) == 24,
         "Actual selected coordinate set")
    ordinary = set(range(112))-selected
    need(ordinary == set(source["ordinary_ports"]) and len(ordinary) == 88,
         "Actual ordinary coordinate set")
    ce = product(c, e)
    mode, mode_ce = product(product(h, c), hi), product(product(h, ce), hi)
    need(ce == rows(source["coded_response"]), "Complete coded response")
    need(mode == rows(source["mode_code"]) and mode_ce == rows(source["mode_coded_response"]),
         "Actual mode conjugations")
    need(all(ce[p] == c[p] for p in ordinary), "All88 ordinary rows")
    for matrix in (c, ce, mode, mode_ce):
        need(all(p not in matrix[p] for p in ordinary), "Every ordinary diagonal")
    need(sum(p in c[p] for p in range(112)) == 8, "Eight selected diagonal exceptions")
    need(all(owner[i] == owner[j] for matrix in (mode, mode_ce)
             for i, row in enumerate(matrix) for j in row), "Native block support")
    decoder = product(v, ci)
    need(decoder == rows(source["centre_decoder"]), "Exact saved decoder")
    need(set().union(*(set(row) for row in decoder)) == selected, "Exact24 coordinate support")
    need(product(decoder, c) == v, "Complete centre recovery")
    need(all(x.denominator & (x.denominator-1) == 0
             for matrix in (c, ci, ce, decoder) for row in matrix for z in row.values() for x in z),
         "Every coefficient is Gaussian dyadic")

    reports = {}
    words = source["component_words"]
    for name, matrix in (("code", c), ("inverse_and_adjoint", ci)):
        word = words[name]
        need(all(0 <= event[1] < 224 and
                 (event[0] == "scale" or 0 <= event[2] < 224) for event in word),
             "All528 outside complex fields are untouched")
        expected = realify(matrix, 112)
        backward = pullback(word)
        need(backward == expected, "Every real output covector")
        forward, bounds = prefix_bounds(word)
        need(forward == backward, "Distinct forward prefix computation")
        cost = sum(map(tariff, word))
        need(cost == 8052 and len(word) == 2418, "Full real scalar invoice")
        mutation = list(word)
        del mutation[next(i for i, event in enumerate(mutation) if event[0] == "add")]
        need(pullback(mutation) != expected, "Deleted component ADD rejected")
        reports[name] = {"instructions": len(word), "scalar": cost, **bounds}
    reverse = [[op, target, source_field, str(-F(value) if op == "add" else 1/F(value))]
               for op, target, source_field, value in reversed(words["code"])]
    need(words["inverse_and_adjoint"] == reverse, "Literal inverse instruction order")
    need(reports["code"]["prefix_one_norm"] == "16" and reports["code"]["binary_height"] == 3,
         "Code prefix bounds")
    need(reports["inverse_and_adjoint"]["prefix_one_norm"] == "28" and
         reports["inverse_and_adjoint"]["binary_height"] == 2, "Adjoint prefix bounds")
    for name, pin in PINS.items():
        read_pinned(CAMPAIGN / name, pin)
    for name, pin in LOCAL_PINS.items():
        read_pinned(SOURCE / name, pin)
    receipt = {
        "status": "PASS_UNITARY_FOOTPRINT_AND_24_CODE_REVIEW",
        "root_source_pins": PINS, "producer_source_pins": LOCAL_PINS,
        "imports_producer_or_root_checker": False,
        "reader_Gram": ["12"]*8+["8"]*8,
        "real_mod_three_row_rank": real_rank, "real_mod_three_Gram_rank": real_gram_rank,
        "lower_bound_real_coordinates": 2*real_rank-real_gram_rank,
        "lower_bound_complex_fields": (2*real_rank-real_gram_rank)//2,
        "attained_selected_fields": len(selected), "ordinary_equal_rows": len(ordinary),
        "arbitrary_real_input_columns": 1280, "unchanged_outside_complex_fields": 528,
        "component_words": reports, "new_owned_fields": 0,
        "native_target_path_census_reviewed": False,
        "native_phases_or_complete_service_reviewed": False,
        "recursive_caller_admitted": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, sort_keys=True, indent=2)+"\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
