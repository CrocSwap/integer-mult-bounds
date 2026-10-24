#!/usr/bin/env python3
"""Build a dyadic unitary code with distributed centre rows."""

import argparse
from fractions import Fraction as F
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
HELPER = HERE / "check_completion.py"
HELPER_PIN = "854d8be88966bfdd279f9e208927f21c34d4e3fe09a19be2b7d180334f178084"
GAUSSIAN = HERE.parents[3] / "root/check_sign_metric_involutions_20261020.py"
GAUSSIAN_PIN = "4c053a9fbc5da82ec1ef39c6740256f3fc0f6d5784df630130b1110a7efae863"
SOURCE = HERE / "signed-probe/METRIC-COMPLETION.json.gz"
SOURCE_PIN = "88a9f75fa87b1a258d6465e309785c1aaec1be6393d46e51bc0a469e62f09e5e"


def load(path, pin, name):
    if sha256(path.read_bytes()).hexdigest() != pin:
        raise ValueError("Pinned helper " + name)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


b = load(HELPER, HELPER_PIN, "unitary_real_code")
g = load(GAUSSIAN, GAUSSIAN_PIN, "unitary_gaussian_arithmetic")
need = b.need


def gaussian(real_rows):
    return [{j: g.real(v) for j, v in row.items()} for row in real_rows]


def realify(matrix, n=640):
    out = b.r.identity(2 * n)
    for p, row in enumerate(matrix):
        out[2 * p], out[2 * p + 1] = {}, {}
        for j, (x, y) in row.items():
            for target, source, coefficient in (
                    (2 * p, 2 * j, x), (2 * p, 2 * j + 1, -y),
                    (2 * p + 1, 2 * j, y), (2 * p + 1, 2 * j + 1, x)):
                if coefficient:
                    out[target][source] = coefficient
    return out


def components(word):
    out = []
    for op, target, source, coefficient in word:
        for bit in (0, 1):
            out.append([op, 2 * target + bit,
                        None if source is None else 2 * source + bit, coefficient])
    return out


def component_scale(port, norm):
    x, y = 2 * port, 2 * port + 1
    if norm == 4:
        return [["scale", x, None, "1/2"], ["scale", y, None, "1/2"]]
    need(norm == 2, "A pair or four-field Haar row")
    return [["add", x, y, "-1"], ["scale", y, None, "2"],
            ["add", y, x, "1"], ["scale", x, None, "1/2"],
            ["scale", y, None, "1/2"]]


def replay(word):
    result, report = b.replay(word, 1280)
    need(report["scalar"] % 2 == 0, "The real-component tariff is integral")
    report["scalar"] //= 2
    return result, report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    raw = gzip.decompress(SOURCE.read_bytes())
    need(sha256(raw).hexdigest() == SOURCE_PIN, "The exact block placement")
    source = json.loads(raw)
    native = json.loads(b.read("native"))
    cyclic = json.loads(b.read("cyclic"))
    H, Hi = gaussian(b.rows(source["pair_code"])), gaussian(b.rows(source["pair_code_inverse"]))
    real_mode = b.r.identity(112)
    mode = g.eye(112)
    modes, normalization = [], []
    for block in source["mode_blocks"]:
        pp = block["ports"]
        rotation = []
        if block["kind"] == "large6":
            v = block["roles"]
            p, c, n, t, a, z = [v[k] for k in
                                ("centre", "contrast", "negative", "negative_difference",
                                 "pair_difference_a", "pair_difference_b")]
            template = {
                p: {c: 1, t: 1, a: 1, z: 1},
                c: {p: 1, n: 1},
                n: {z: 1, c: 1, a: -1, t: -1},
                t: {p: 1, n: -1},
                a: {z: 1, c: -1},
                z: {a: 1, t: -1},
            }
            norms = {p: 4, c: 2, n: 4, t: 2, a: 2, z: 2}
            sign = dict(zip(pp, block["signs"]))
        else:
            p, c = block["centre"], block["contrast"]
            left, right = pp[:4], pp[4:]
            template = {p: {j: 1 for j in left}, c: {j: 1 for j in right}}
            norms = {p: 4, c: 4}
            for group, outputs in ((left, right[1:]), (right, left[1:])):
                x0, x1, x2, x3 = group
                patterns = [{x0: 1, x1: -1}, {x2: 1, x3: -1},
                            {x0: 1, x1: 1, x2: -1, x3: -1}]
                for output, row, norm in zip(outputs, patterns, (2, 2, 4)):
                    template[output], norms[output] = row, norm
            sign = {j: 1 for j in pp}
            rotation = [["add", c, p, "1"], ["add", p, c, "-1"], ["add", c, p, "1"]]
        for port in pp:
            real_mode[port] = {j: F(value * sign[j]) for j, value in template[port].items()}
            coefficient = (F(1, 2), F(1, 2) if norms[port] == 2 else F(0))
            mode[port] = {j: g.times(g.real(value), coefficient)
                          for j, value in real_mode[port].items()}
            normalization += component_scale(port, norms[port])
        local = [{pp.index(j): value for j, value in real_mode[port].items()} for port in pp]
        modes += b.factor(local, pp) + rotation
        if rotation:
            real_mode[p], real_mode[c] = b.scale_row(real_mode[c], F(-1)), real_mode[p]
            mode[p], mode[c] = {j: g.neg(value) for j, value in mode[c].items()}, mode[p]
    need(g.multiply(mode, g.adjoint(mode, 112)) == g.multiply(g.adjoint(mode, 112), mode) == g.eye(112),
         "Both exact mode unitary identities")
    C = g.multiply(g.multiply(Hi, mode), H)
    Ci = g.adjoint(C, 112)
    need(g.multiply(C, Ci) == g.multiply(Ci, C) == g.eye(112), "Both physical unitary orders")
    E = gaussian(b.rows(native["model"]["response"]))
    CE = g.multiply(C, E)
    Em = g.multiply(g.multiply(H, E), Hi)
    CEm = g.multiply(mode, Em)
    selected = set(source["exceptional_ports"])
    ordinary = set(range(112)) - selected
    need(all(C[p] == CE[p] for p in ordinary), "All80 ordinary response rows are unchanged")
    need(all(p not in mode[p] and p not in CEm[p] for p in ordinary), "Ordinary mode diagonals vanish")
    need(all(p not in C[p] and p not in CE[p] for p in ordinary), "Ordinary physical diagonals vanish")
    need(all(p not in mode[p] and p not in C[p] for p in range(112)),
         "The full code has zero mode and physical diagonal")
    need({p for p in range(112) if p in CEm[p]} <= selected, "Response exceptions are selected")
    V = gaussian(b.rows(native["model"]["correction_V"]))
    decoder = g.multiply(V, Ci)
    need(all(set(row) <= selected for row in decoder), "All old centre readers use only32 FULL outputs")
    need(g.multiply(decoder, C) == V, "The exact original centre information")
    hword = []
    for pair in cyclic["pair_codes"]:
        local = [{j: F(c) for j, c in enumerate(row) if c} for row in pair["matrix"]]
        hword += b.factor(local, pair["ports"])
    word = components(hword) + components(modes) + normalization + components(b.r.inverse_word(hword))
    inverse = b.r.inverse_word(word)
    words = {"code": word, "inverse_and_adjoint": inverse}
    reports = {}
    for name, instructions in words.items():
        expected = C if name == "code" else Ci
        actual, report = replay(instructions)
        need(actual == realify(expected), "All1280 real columns and1056 outside components")
        wrong = list(instructions)
        del wrong[next(i for i, event in enumerate(wrong) if event[0] == "add")]
        need(replay(wrong)[0] != realify(expected), "A missing component ADD is rejected")
        reports[name] = report
    for value in (C, Ci, CE, decoder):
        for row in value:
            for z in row.values():
                for x in z:
                    need(x.denominator & (x.denominator - 1) == 0, "Every matrix entry is Gaussian dyadic")
    payload = {
        "schema": "physical-unitary-distributed-centre-code-v1",
        "source_pins": {"real_helper": HELPER_PIN, "gaussian_helper": GAUSSIAN_PIN,
                        "placement_payload_decompressed": SOURCE_PIN, **source["source_pins"]},
        "ports": source["ports"], "selected_full_ports": sorted(selected), "ordinary_ports": sorted(ordinary),
        "code": g.serialize(C), "inverse_and_adjoint": g.serialize(Ci),
        "mode_code": g.serialize(mode), "response": g.serialize(E), "coded_response": g.serialize(CE),
        "mode_response": g.serialize(Em), "mode_coded_response": g.serialize(CEm),
        "original_centre_readers": g.serialize(V), "full_carrier_centre_decoder": g.serialize(decoder),
        "component_words": words, "component_index": "2*p is real;2*p+1 is imaginary.",
        "identity": "C*=C^-1 and C^-*=C. Every ordinary row of C E equals the same row of C.",
        "scope": "Exact unitary scalar code,32-carrier centre decoding and zero mode diagonal. Changed native typed service and routed caller remain open.",
    }
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    saved = json.loads(raw)
    for name, instructions in saved["component_words"].items():
        need(replay(instructions)[1] == reports[name], "Serialized component word")
    (args.out / "UNITARY-COMPLETION.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    receipt = {
        "status": "PASS_PHYSICAL_UNITARY_CENTRE_COMPLETION",
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_decompressed_sha256": sha256(raw).hexdigest(),
        "all_complex_columns": 640, "all_real_columns": 1280, "unchanged_other_complex_fields": 528,
        "selected_full_rows": len(selected), "ordinary_rows": len(ordinary),
        "centre_decoder_row_supports": [len(row) for row in decoder],
        "code_diagonal_exceptions": sorted(p for p in range(112) if p in C[p]),
        "coded_response_diagonal_exceptions": sorted(p for p in range(112) if p in CE[p]),
        "reports": reports, "scope": payload["scope"],
    }
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
