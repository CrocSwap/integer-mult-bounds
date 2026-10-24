#!/usr/bin/env python3
"""Emit an in-place centre code for the exact rank-sixteen response."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
LANES = PARENT.parents[1]
PINS = {
    PARENT / "check_response.py":
        "c6d92104e4345816e86163f6c1dea24fbd9b6e9b133ffd2e0c646dca17ca00a8",
    LANES / "independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json":
        "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585",
}
SOURCE = PARENT / "odd16-normal-v2/EXTENSION-PROGRAM.json.gz"
SOURCE_PIN = "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4"


def need(test, message):
    if not test:
        raise ValueError(message)


for path, pin in PINS.items():
    need(sha256(path.read_bytes()).hexdigest() == pin, "Source pin " + str(path))
spec = importlib.util.spec_from_file_location("response_helpers", PARENT / "check_response.py")
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def inverse(word):
    result = []
    for op, target, source, coefficient in reversed(word):
        if op == "fixed_multiply":
            result.append(["fixed_divide", target, source, coefficient])
        elif op == "fixed_divide":
            result.append(["fixed_multiply", target, source, coefficient])
        elif op == "translate":
            result.append([op, target, source, coefficient])
        else:
            value = F(coefficient)
            result.append([op, target, source, str(1 / value if op == "scale" else -value)])
    return result


def replay(word, spatial=False):
    state = [{(i, 0): F(1)} if spatial else {i: F(1)} for i in range(640)]
    norm, binary_height, odd_height = F(1), 0, 0
    for op, target, source, coefficient in word:
        need(0 <= target < 112, "Only data targets")
        if op == "translate":
            need(spatial, "Translation requires the spatial interpreter")
            state[target] = {(i, t ^ int(coefficient)): c for (i, t), c in state[target].items()}
        elif op == "add":
            need(0 <= source < 112 and source != target, "Only distinct data sources")
            r.add(state[target], state[source], F(coefficient))
        else:
            need(op in ("scale", "fixed_multiply", "fixed_divide"), "Literal scalar grammar")
            value = F(coefficient)
            if op == "fixed_divide":
                value = 1 / value
            state[target] = {i: c * value for i, c in state[target].items() if c * value}
        norm = max(norm, sum(abs(c) for c in state[target].values()))
        for coefficient in state[target].values():
            denominator = coefficient.denominator
            binary = odd = 0
            while denominator % 2 == 0:
                denominator //= 2
                binary += 1
            while denominator % 3 == 0:
                denominator //= 3
                odd += 1
            need(denominator == 1, "Only the declared binary and odd-three grid")
            binary_height, odd_height = max(binary_height, binary), max(odd_height, odd)
    for i in range(112, 640):
        need(state[i] == ({(i, 0): F(1)} if spatial else {i: F(1)}),
             "Every other arbitrary input stays unchanged")
    return state[:112], {
        "maximum_prefix_row_one_norm": str(norm),
        "additional_binary_height": binary_height,
        "additional_odd_three_height": odd_height,
    }


def price(word):
    old, odd_multiply, odd_divide, translations = 0, 0, 0, 0
    for gate in word:
        if gate[0] == "fixed_multiply":
            odd_multiply += 2
        elif gate[0] == "fixed_divide":
            odd_divide += 2
        elif gate[0] == "translate":
            translations += 1
        else:
            old += r.price([gate])
    return {
        "old_real_scalar_units": old,
        "real_fixed_three_multiplication_scans": odd_multiply,
        "real_fixed_three_division_scans": odd_divide,
        "explicit_translation_maps": translations,
        "native_children": 0,
        "owned_fields": 0,
    }


def make_code(model, cyclic):
    word = []
    pair_matrix = r.identity(112)
    for pair in cyclic["pair_codes"]:
        a, b = pair["ports"]
        aa, ab = pair["matrix"][0]
        ba, bb = pair["matrix"][1]
        pair_matrix[a], pair_matrix[b] = {a: F(aa), b: F(ab)}, {a: F(ba), b: F(bb)}
        if aa != 1:
            word.append(["scale", a, None, str(aa)])
        word.extend([["add", a, b, str(ab)], ["scale", b, None, str(2 * bb)],
                     ["add", b, a, str(ba * aa)]])
    groups = [
        {"ports": item["ordered_carriers_a_b_c"], "signs": item["signs"], "kind": "large"}
        for item in model["vertex_assignments"]
    ]
    groups += [{"ports": group, "signs": [1] * 8, "kind": "small"}
               for group in model["small_cliques"]]
    need(sorted(p for group in groups for p in group["ports"]) == list(range(112)),
         "The sixteen mode blocks partition all data fields")
    modes = r.identity(112)
    diagonal = r.identity(112)
    for group in groups:
        ports, signs = group["ports"], group["signs"]
        pivot, size = ports[0], len(ports)
        group["pivot"] = pivot
        group["centre_multiplier"] = 1 - size
        for p, sign in zip(ports, signs):
            if sign == -1:
                word.append(["scale", p, None, "-1"])
        for p in ports[1:]:
            word.append(["add", p, pivot, "-1"])
        if size == 6:
            word.extend([["scale", pivot, None, "2"],
                         ["fixed_multiply", pivot, None, "3"]])
        else:
            need(size == 8, "The exact rank-sixteen block sizes")
            word.append(["scale", pivot, None, "8"])
        for p in ports[1:]:
            word.append(["add", pivot, p, "1"])
        modes[pivot] = {p: F(sign) for p, sign in zip(ports, signs)}
        for p, sign in zip(ports[1:], signs[1:]):
            modes[p] = {p: F(sign), pivot: F(-signs[0])}
        diagonal[pivot] = {pivot: F(1 - size)}
    return word, groups, r.product(modes, pair_matrix), diagonal


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    raw = gzip.decompress(SOURCE.read_bytes())
    need(sha256(raw).hexdigest() == SOURCE_PIN, "Exact native response source")
    model = json.loads(raw)["model"]
    cyclic = json.loads(next(path.read_bytes() for path in PINS if path.name == "CYCLIC-FLAGS.json"))
    word, groups, expected, diagonal = make_code(model, cyclic)
    reverse = inverse(word)
    code, growth = replay(word)
    code_inverse, inverse_growth = replay(reverse)
    need(code == expected, "Literal centre sums and complement differences")
    need(replay(word + reverse)[0] == replay(reverse + word)[0] == r.identity(112),
         "Both literal inverse orders")
    response = [{int(p): F(c) for p, c in row.items()} for row in model["response"]]
    need(r.product(code, r.product(response, code_inverse)) == diagonal,
         "The exact response has sixteen scalar centre actions")
    entry = [["translate", p, None, str(q)] for p, q in enumerate(model["ports"])] + word
    entry_rows, entry_growth = replay(entry, spatial=True)
    want_entry = [{(p, model["ports"][p]): c for p, c in row.items()} for row in code]
    need(entry_rows == want_entry, "Each input line square is on the correct side of the code")
    need(replay(entry + inverse(entry), spatial=True)[0]
         == replay(inverse(entry) + entry, spatial=True)[0]
         == [{(p, 0): F(1)} for p in range(112)], "Both literal spatial inverse orders")
    wrong = word + entry[:112]
    need(replay(wrong, spatial=True)[0] != want_entry, "Wrong-side square control")
    need(price(word)["old_real_scalar_units"] == price(reverse)["old_real_scalar_units"] == 2078,
         "Literal complete scalar invoice")
    payload = {
        "source_decompressed_sha256": SOURCE_PIN,
        "groups": groups,
        "pivots": [group["pivot"] for group in groups],
        "code": r.encoded(code),
        "code_inverse": r.encoded(code_inverse),
        "diagonal_response": r.encoded(diagonal),
        "scalar_words": {"code": word, "inverse_code": reverse},
        "entry_square_word": entry,
        "entry_square_inverse_word": inverse(entry),
    }
    data = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    (args.out / "PIVOT-CODES.json").write_bytes(data)
    checks = {
        "status": "PASS_RANK16_EXISTING_PORT_PIVOT_CODE",
        "source_decompressed_sha256": SOURCE_PIN,
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_sha256": sha256(data).hexdigest(),
        "arbitrary_input_columns": 640,
        "unchanged_other_fields": 528,
        "new_fields": 0,
        "code_invoice": price(word),
        "inverse_invoice": price(reverse),
        "entry_square_invoice": price(entry),
        "code_prefix": growth,
        "inverse_prefix": inverse_growth,
        "entry_prefix": entry_growth,
        "both_scalar_inverse_orders": True,
        "both_spatial_inverse_orders": True,
        "wrong_side_square_rejected": True,
        "transport_scope": "The common-entry code is literal. The formal transported code q C q diagonalizes Q E q because its sixteen centre multipliers are scalar. No raw-output decoder or stage transition is supplied.",
    }
    (args.out / "CHECKS.json").write_text(json.dumps(checks, indent=2, sort_keys=True) + "\n")
    print(checks["status"], checks["code_invoice"], checks["code_prefix"], checks["inverse_prefix"])


if __name__ == "__main__":
    main()
