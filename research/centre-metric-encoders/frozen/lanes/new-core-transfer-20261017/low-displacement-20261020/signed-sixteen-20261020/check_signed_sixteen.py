#!/usr/bin/env python3
"""Check a complete code with one signed-metric carrier per centre."""

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
LANES = HERE.parents[2]
PINS = {
    "arithmetic": (
        HERE.parent / "metric-completion-20261020/check_completion.py",
        "854d8be88966bfdd279f9e208927f21c34d4e3fe09a19be2b7d180334f178084"),
    "response": (
        LANES / "oblique-native-20261017/signed-metric-reciprocal-20261020/model-normal-v2/RESPONSE.json.gz",
        "df2d2028c99028db3c645b3311d7f31ff96efe72f6f9257f99157ce030ff43d0"),
}


def need(value, message):
    if not value:
        raise ValueError(message)


def read(name):
    path, pin = PINS[name]
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Pinned source " + name)
    return raw


read("arithmetic")
spec = importlib.util.spec_from_file_location("signed_sixteen_arithmetic", PINS["arithmetic"][0])
b = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = b
spec.loader.exec_module(b)
r = b.r


def local_code(n):
    if n == 6:
        dense = [
            [-1, -1, -1, -1, 1, 0],
            [0, 0, 1, -1, 0, 0],
            [1, -1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1],
            [1, 1, -1, -1, 0, 0],
            [1, 1, 1, 1, -2, 0],
        ]
        gram = [2, 2, 2, -2, 4, -4]
    else:
        need(n == 8, "The actual six-mode and eight-mode blocks")
        dense = [
            [-1, -1, -1, -1, -1, -1, 1, 0],
            [0, 0, 0, 0, 1, 1, F(-1, 2), 0],
            [0, 0, 0, 0, 1, -1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1],
            [1, -1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, -1, 0, 0, 0, 0],
            [1, 1, -1, -1, 0, 0, 0, 0],
            [1, 1, 1, 1, 2, 2, -2, 0],
        ]
        gram = [2, 1, 2, -4, 2, 2, 4, -4]
    matrix = [{j: F(c) for j, c in enumerate(row) if c} for row in dense]
    return matrix, [{i: F(c)} for i, c in enumerate(gram)]


def diagonal_word(matrix, offset=0):
    return [["scale", offset + i, None, str(row[i])]
            for i, row in enumerate(matrix) if row[i] != 1]


def clean_map(code, centres):
    selected = set(centres)
    matrix = r.identity(224)
    for p in range(112):
        if p in selected:
            matrix[p] = {112 + p: F(-1)}
            matrix[112 + p] = dict(code[p])
        else:
            matrix[p] = dict(code[p])
            matrix[112 + p] = {112 + p: F(1)}
            r.add(matrix[112 + p], code[p], 1)
    return matrix


def literal_clean_word(code_word, centres):
    word = list(code_word)
    selected = set(centres)
    for p in range(112):
        if p not in selected:
            word.append(["add", 112 + p, p, "1"])
    for p in centres:
        word.extend([["add", 112 + p, p, "1"],
                     ["add", p, 112 + p, "-1"],
                     ["add", 112 + p, p, "1"]])
    return word


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    source = json.loads(read("response"))
    centres = source["centre_ports"]
    selected = set(centres)
    need(len(selected) == 16, "Sixteen actual centre fields")
    H = b.rows(source["pair_code"])
    Hi = b.rows(source["pair_code_inverse"])
    K = b.rows(source["physical"]["inverse_J"])
    J = b.rows(source["physical"]["J"])
    R = b.rows(source["physical"]["R"])
    E = b.rows(source["physical"]["E"])
    P = b.rows(source["physical"]["P"])
    Km = b.rows(source["mode"]["inverse_J"])
    Cm, Gm = r.identity(112), r.identity(112)
    mode_word, blocks = [], []
    for block in source["blocks"]:
        ports = block["ports"]
        local, gram = local_code(len(ports))
        local_k = r.restrict(Km, ports)
        need(r.product(r.product(local, local_k), r.transpose(local, len(ports))) == gram,
             "The exact local diagonal metric")
        u = [F(v) for v in block["u"]]
        need(all(sum(c * u[j] for j, c in row.items()) == (F(-2) if i == 0 else F(0))
                 for i, row in enumerate(local)), "The centre and ordinary actions on u")
        need(all(not local[i].get(i, 0) for i in range(1, len(ports))),
             "Every ordinary local diagonal is zero")
        for i, p in enumerate(ports):
            Cm[p] = {ports[j]: c for j, c in local[i].items()}
            Gm[p] = {p: gram[i][i]}
        word = b.factor(local, ports)
        mode_word += word
        blocks.append({
            **block, "code": r.encoded(local), "metric": r.encoded(gram),
            "determinant": str(r.determinant(local)),
            "scalar_word": word, "scalar_price": r.price(word),
        })
    hword, ordinary_hword = [], []
    for pair in source["pair_codes"]:
        ports = pair["ports"]
        matrix = [{j: F(c) for j, c in enumerate(row) if c}
                  for row in pair["matrix"]]
        word = b.factor(matrix, ports)
        hword += word
        need(not set(ports) & selected or set(ports) <= selected,
             "Selected physical pairs are complete")
        if not set(ports) & selected:
            ordinary_hword += word
    Horinv = r.identity(112)
    for p in range(112):
        if p not in selected:
            Horinv[p] = dict(Hi[p])
    C = r.product(r.product(Horinv, Cm), H)
    Ct = r.transpose(C, 112)
    G = r.product(r.product(C, K), Ct)
    need(all(set(row) == {p} and b.unit(row[p]) for p, row in enumerate(G)),
         "The physical output metric is diagonal with dyadic units")
    need(all(set(row) == {p} and b.unit(row[p]) for p, row in enumerate(K)),
         "The physical input metric is diagonal with dyadic units")
    Gi = [{p: 1 / row[p]} for p, row in enumerate(G)]
    Ci = r.product(r.product(K, Ct), Gi)
    Cd = r.product(r.product(Gi, C), K)
    need(r.product(C, Ci) == r.product(Ci, C) == r.identity(112),
         "Both full physical inverse orders")
    need(Cd == r.transpose(Ci, 112), "The exact inverse-adjoint identity")
    L = b.rows(source["reflection_L"])
    need([C[p] for p in centres] == L, "The sixteen stored centre readers")
    need(r.rank(L, 112) == 16, "All sixteen independent centre readers")
    CR = r.product(C, R)
    ZC = [b.scale_row(row, -1 if p in selected else 1) for p, row in enumerate(C)]
    need(CR == ZC, "The completed code diagonalizes the reflection")
    need(r.product(r.product(C, P), E) == CR, "The ordered C P E identity")
    Cnative = r.product(r.product(H, C), Hi)
    CRnative = r.product(r.product(H, CR), Hi)
    need(all(not C[p].get(p, 0) and not CR[p].get(p, 0)
             and not Cnative[p].get(p, 0) and not CRnative[p].get(p, 0)
             for p in range(112) if p not in selected), "Every ordinary native and physical diagonal is zero")
    mode_groups = [set(block["ports"]) for block in source["blocks"]]
    need(all(any(p in group and set(Cnative[p]) <= group for group in mode_groups)
             for p in range(112) if p not in selected), "All ordinary transfers use their admitted mode block")
    code_word = hword + mode_word + r.inverse_word(ordinary_hword)
    inverse_word = r.inverse_word(code_word)
    literal_dual = r.transpose_word(r.inverse_word(code_word))
    wrapped_dual = diagonal_word(K) + code_word + diagonal_word(Gi)
    words = {
        "code": code_word, "inverse": inverse_word,
        "literal_inverse_adjoint": literal_dual,
        "diagonal_inverse_adjoint": wrapped_dual,
    }
    expected = {"code": C, "inverse": Ci, "literal_inverse_adjoint": Cd,
                "diagonal_inverse_adjoint": Cd}
    reports = {}
    for name, word in words.items():
        actual, report = b.replay(word, 640)
        need(actual[:112] == expected[name] and actual[112:] == r.identity(640)[112:],
             "All640 input columns and528 unchanged outside fields")
        reports[name] = report
    fm = clean_map(C, centres)
    fw = literal_clean_word(code_word, centres)
    need(b.replay(fw, 640)[0][:224] == fm, "The complete scalar clean map")
    fd = r.transpose_word(r.inverse_word(fw))
    pre = diagonal_word(J) + diagonal_word(Gi, 112)
    post = diagonal_word(G) + diagonal_word(G, 112)
    converted = pre + fd + post
    converted_map = r.identity(224)
    for p in range(112):
        if p in selected:
            converted_map[p] = {112 + p: F(-1)}
            converted_map[112 + p] = dict(C[p])
        else:
            converted_map[p] = dict(C[p])
            r.add(converted_map[p], {112 + p: F(1)}, -1)
            converted_map[112 + p] = {112 + p: F(1)}
    need(b.replay(converted, 640)[0][:224] == converted_map,
         "The complete diagonal-converted clean inverse-adjoint")
    swap = {p: 112 + p for p in selected}
    swap.update({112 + p: p for p in selected})
    conjugated = [[op, swap.get(t, t), swap.get(s, s) if s is not None else None, c]
                  for op, t, s, c in converted]
    bmap = r.identity(224)
    mixed = [{(112 + p if p in selected else p): F(1)} for p in range(112)]
    w = r.product(C, mixed)
    for p in range(112):
        bmap[p] = dict(w[p])
        if p in selected:
            bmap[112 + p] = {p: F(-1)}
        else:
            r.add(bmap[p], {112 + p: F(1)}, -1)
    need(b.replay(conjugated, 640)[0][:224] == bmap,
         "The complete selected-bank conjugate with diagonal metric conversion")
    payload = {
        "schema": "signed-sixteen-complete-centre-code-v1",
        "source_pins": {name: {"path": str(path), "sha256": pin} for name, (path, pin) in PINS.items()},
        "centre_ports": centres, "ordinary_ports": sorted(set(range(112)) - selected),
        "blocks": blocks, "pair_code": source["pair_code"],
        "pair_code_inverse": source["pair_code_inverse"],
        "mode_code": r.encoded(Cm), "code": r.encoded(C), "inverse": r.encoded(Ci),
        "inverse_adjoint": r.encoded(Cd), "native_code": r.encoded(Cnative),
        "coded_reflection": r.encoded(CR), "native_coded_reflection": r.encoded(CRnative),
        "input_metric": r.encoded(K), "input_metric_inverse": r.encoded(J),
        "output_metric": r.encoded(G), "output_metric_inverse": r.encoded(Gi),
        "reflection_readers": source["reflection_L"],
        "scalar_words": words,
        "clean_metric_wrappers": {"pre": pre, "post": post},
        "clean_maps": {"forward": r.encoded(fm), "converted_inverse_adjoint": r.encoded(converted_map),
                       "selected_conjugate": r.encoded(bmap)},
        "scope": "Complete scalar code and exact native support. Native service, routed caller, recursive precision and hosting remain separate.",
    }
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    saved = json.loads(raw)
    need(b.replay(saved["scalar_words"]["code"], 640)[0][:112] == C, "Serialized code replay")
    (args.out / "SIGNED-SIXTEEN.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    receipt = {
        "status": "PASS_SIGNED_SIXTEEN_COMPLETION",
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_decompressed_sha256": sha256(raw).hexdigest(),
        "centre_count": 16, "ordinary_count": 96, "all_matrix_columns": 112,
        "all_scalar_columns": 640, "all_clean_columns": 640,
        "reports": reports, "metric_wrapper_price": r.price(pre + post),
        "input_metric_counts": dict(Counter(str(row[p]) for p, row in enumerate(K))),
        "output_metric_counts": dict(Counter(str(row[p]) for p, row in enumerate(G))),
        "local_determinants": dict(Counter(block["determinant"] for block in blocks)),
        "scope": payload["scope"],
    }
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
