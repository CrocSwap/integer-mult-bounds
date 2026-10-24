#!/usr/bin/env python3
"""Build a unitary centre code with 24 output coordinates."""

import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
HELPER = HERE / "check_unitary.py"
HELPER_PIN = "45edfdf2a3e62557b1809ed6280b27d0afc411704fd1c572ab7295759d40127a"
SOURCE = HERE / "unitary-v2-normal/UNITARY-COMPLETION.json.gz"
SOURCE_PIN = "fd3b442caa13104cef4b7c046e1c2781f2ffa216d8d098b4e2a4e51e6063f428"


def need(value, message):
    if not value:
        raise ValueError(message)


need(sha256(HELPER.read_bytes()).hexdigest() == HELPER_PIN, "Pinned unitary helper")
spec = importlib.util.spec_from_file_location("unitary_twenty_four_source", HELPER)
u = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = u
spec.loader.exec_module(u)
b, g = u.b, u.g


def rows(value):
    return [{int(j): (F(x), F(y)) for j, (x, y) in row.items()} for row in value]


def small_block():
    vector = [1, 1, -1, 0, -1, 0, 0, 0]
    reflection = [{j: F(int(i == j)) - F(vector[i] * vector[j], 2)
                   for j in range(8)
                   if F(int(i == j)) - F(vector[i] * vector[j], 2)}
                  for i in range(8)]
    haar = [
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, -1, -1, -1, -1],
        [1, 1, -1, -1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, -1, -1],
        [1, -1, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, -1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, -1, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, -1],
    ]
    output = [0, 1, 5, 3, 2, 7, 6, 4]
    norm = [8, 8, 4, 4, 2, 2, 2, 2]
    ordered = [{} for _ in range(8)]
    factors, norms = {}, {}
    for row, target, squared_norm in zip(haar, output, norm):
        ordered[target] = {j: F(x) for j, x in enumerate(row) if x}
        factors[target] = ((F(1, 4), F(1, 4)) if squared_norm == 8 else
                           (F(1, 2), F(1, 2)) if squared_norm == 2 else
                           (F(1, 2), F(0)))
        norms[target] = squared_norm
    real_product = b.r.product(ordered, reflection)
    code = [{j: g.times(g.real(x), factors[i]) for j, x in row.items()}
            for i, row in enumerate(real_product)]
    need(sum(vector) == 0 and sum(x * x for x in vector) == 4, "The reflection fixes the centre")
    need(b.r.product(reflection, reflection) == b.r.identity(8), "The real reflection is an involution")
    need(g.multiply(code, g.adjoint(code, 8)) == g.multiply(g.adjoint(code, 8), code) == g.eye(8),
         "Both small-block unitary identities")
    need(all(i not in code[i] for i in range(1, 8)), "All seven ordinary diagonals vanish")
    need(code[0] == {j: (F(1, 4), F(1, 4)) for j in range(8)}, "The sole centre row")
    return code, reflection, ordered, norms, vector, output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    raw = gzip.decompress(SOURCE.read_bytes())
    need(sha256(raw).hexdigest() == SOURCE_PIN, "Pinned physical 32-coordinate code")
    source = json.loads(raw)
    placement = json.loads(gzip.decompress(u.SOURCE.read_bytes()))
    native = json.loads(b.read("native"))
    large = set(native["model"]["large_ports"])
    C, Cm = rows(source["code"]), rows(source["mode_code"])
    E = rows(source["response"])
    V = rows(source["original_centre_readers"])
    block, reflection, haar, norms, vector, output = small_block()
    selected = set(source["selected_full_ports"]) & large
    word = []
    for event in source["component_words"]["code"]:
        target = event[1] // 2
        if target in large:
            need(event[2] is None or event[2] // 2 in large, "The copied large word is closed")
            word.append(event)
    blocks = []
    for record in placement["mode_blocks"]:
        if record["kind"] == "large6":
            continue
        ports = record["ports"]
        selected.add(ports[0])
        for i, p in enumerate(ports):
            C[p] = {ports[j]: z for j, z in block[i].items()}
            Cm[p] = dict(C[p])
        local_word = u.components(b.factor(reflection, ports) + b.factor(haar, ports))
        for i, p in enumerate(ports):
            local_word += u.component_scale(p, 2 if norms[i] == 8 else norms[i])
            if norms[i] == 8:
                local_word += [["scale", 2 * p, None, "1/2"],
                               ["scale", 2 * p + 1, None, "1/2"]]
        word += local_word
        blocks.append({"ports": ports, "centre": ports[0], "component_word": local_word})
    Ci = g.adjoint(C, 112)
    ordinary = set(range(112)) - selected
    CE = g.multiply(C, E)
    decoder = g.multiply(V, Ci)
    need(len(selected) == 24, "Exactly 24 centre coordinates")
    need(g.multiply(C, Ci) == g.multiply(Ci, C) == g.eye(112), "Both physical unitary orders")
    need(all(C[p] == CE[p] and p not in C[p] for p in ordinary), "All88 ordinary rows and diagonals")
    need(all(set(row) <= selected for row in decoder) and g.multiply(decoder, C) == V,
         "All sixteen original readers use the 24 coordinates")
    for matrix in (C, Ci, CE, decoder):
        for row in matrix:
            for value in row.values():
                need(all(x.denominator & (x.denominator - 1) == 0 for x in value),
                     "Every coefficient is Gaussian dyadic")
    mode_response = rows(source["mode_response"])
    CEm = g.multiply(Cm, mode_response)
    need(all(p not in Cm[p] and p not in CEm[p] for p in ordinary), "All ordinary mode diagonals")
    allowed = {}
    for record in placement["mode_blocks"]:
        for p in record["ports"]:
            allowed[p] = set(record["ports"])
    need(all(set(row) <= allowed[p] for p, row in enumerate(Cm)), "The native block support")
    inverse = b.r.inverse_word(word)
    reports = {}
    for name, instructions, matrix in (("code", word, C), ("inverse_and_adjoint", inverse, Ci)):
        actual, report = u.replay(instructions)
        need(actual == u.realify(matrix), "All1280 real columns and528 external complex fields")
        damaged = list(instructions)
        del damaged[next(i for i, event in enumerate(damaged) if event[0] == "add")]
        need(u.replay(damaged)[0] != actual, "A missing component ADD is rejected")
        reports[name] = report
    need(b.r.product(u.realify(C), u.realify(Ci)) == b.r.identity(1280),
         "The full real-component inverse composition")
    path_census = {}
    for name, provider in native["providers"].items():
        events = provider["forward"]["events"]
        removed = []
        kept = []
        for event in events:
            target = event[1] if event[0] == "native" else event[1][1]
            (removed if target in {112 + p for p in selected} else kept).append(event)
        need(all(event[0] != "scalar" or event[1][2] not in {112 + p for p in selected}
                 for event in kept), "No retained event reads a removed target")
        profile = Counter(event[4] for event in removed if event[0] == "native")
        need(profile == Counter({1: 192}), "Exactly192 removed rank-one target advances")
        path_census[name] = {"removed_events": len(removed), "removed_native_profile": dict(profile),
                             "retained_reads_of_selected_target": 0}
    payload = {
        "schema": "physical-unitary-24-coordinate-centre-code-v1",
        "source_payload_decompressed_sha256": SOURCE_PIN,
        "helper_sha256": HELPER_PIN,
        "source_pins": source["source_pins"],
        "selected_full_ports": sorted(selected), "ordinary_ports": sorted(ordinary),
        "code": g.serialize(C), "inverse_and_adjoint": g.serialize(Ci),
        "mode_code": g.serialize(Cm), "response": g.serialize(E),
        "coded_response": g.serialize(CE), "mode_coded_response": g.serialize(CEm),
        "original_centre_readers": g.serialize(V), "centre_decoder": g.serialize(decoder),
        "small_reflection_vector": vector, "small_output_assignment": output,
        "small_blocks": blocks,
        "component_words": {"code": word, "inverse_and_adjoint": inverse},
        "scope": "Exact unitary code,24-coordinate centre recovery, scalar words and native path/support census. Complete native code and routed caller remain open.",
    }
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    (args.out / "UNITARY-24.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    receipt = {
        "status": "PASS_ACTUAL_UNITARY_24_COORDINATE_CODE",
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_decompressed_sha256": sha256(raw).hexdigest(),
        "all_real_columns": 1280, "all_complex_fields": 640, "unchanged_external_complex_fields": 528,
        "selected_full_rows": 24, "ordinary_rows": 88, "reports": reports,
        "centre_decoder_supports": [len(row) for row in decoder],
        "code_diagonal_exceptions": [p for p in range(112) if p in C[p]],
        "coded_response_diagonal_exceptions": [p for p in range(112) if p in CE[p]],
        "path_census": path_census, "scope": payload["scope"],
    }
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
