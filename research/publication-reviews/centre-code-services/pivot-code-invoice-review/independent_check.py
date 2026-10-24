"""Check the original pivot invoice, grid, and input-side translation."""

import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
from hashlib import sha256
import json
from pathlib import Path


def need(value, label):
    if not value:
        raise ValueError(label)


def identity():
    return [{i: F(1)} for i in range(112)]


def multiply(a, b):
    out = []
    for row in a:
        result = {}
        for j, c in row.items():
            for i, v in b[j].items():
                result[i] = result.get(i, F(0)) + c * v
        out.append({i: v for i, v in result.items() if v})
    return out


def replay(word, start=None, require_valid_divisions=False):
    rows = identity() if start is None else [dict(row) for row in start]
    norm, binary, odd, division_rows = F(1), 0, 0, []
    for index, (op, target, source, literal) in enumerate(word):
        need(0 <= target < 112, "Data-only target")
        value = F(literal)
        if op == "add":
            need(0 <= source < 112 and source != target, "Data-only source")
            rows[target] = {
                i: rows[target].get(i, F(0)) + value * rows[source].get(i, F(0))
                for i in rows[target].keys() | rows[source].keys()
            }
        else:
            need(source is None and op in ("scale", "fixed_multiply", "fixed_divide"), "Scalar grammar")
            if op == "fixed_divide":
                need(value == 3, "Only fixed-three division")
                divisible = all(c.numerator % 3 == 0 and c.denominator % 3 != 0 for c in rows[target].values())
                division_rows.append({"event": index, "target": target, "dyadic_input_coefficients_divisible_by_three": divisible})
                if require_valid_divisions:
                    need(divisible, "Exact division on the forward image")
                value = 1 / value
            rows[target] = {i: value * c for i, c in rows[target].items()}
        rows[target] = {i: c for i, c in rows[target].items() if c}
        norm = max(norm, sum(map(abs, rows[target].values()), F(0)))
        for c in rows[target].values():
            d, b, o = c.denominator, 0, 0
            while d % 2 == 0:
                d //= 2
                b += 1
            while d % 3 == 0:
                d //= 3
                o += 1
            need(d == 1, "Only declared denominator primes")
            binary, odd = max(binary, b), max(odd, o)
    return rows, {"norm": str(norm), "binary_height": binary, "odd_three_height": odd, "division_rows": division_rows}


def invoice(word):
    tariff = {("add", "1"): 8, ("add", "-1"): 8,
              ("scale", "-1"): 2, ("scale", "2"): 2,
              ("scale", "-2"): 4, ("scale", "8"): 6,
              ("scale", "1/2"): 2, ("scale", "-1/2"): 4,
              ("scale", "1/8"): 6}
    census = Counter((g[0], g[3]) for g in word)
    units = 0
    for key, count in census.items():
        if key in (("fixed_multiply", "3"), ("fixed_divide", "3")):
            continue
        need(key in tariff, "Literal unit ADD and binary-scale tariff")
        units += tariff[key] * count
    return {"old_real_scalar_units": units,
            "real_multiply_three_scans": 2 * census[("fixed_multiply", "3")],
            "real_divide_three_scans": 2 * census[("fixed_divide", "3")],
            "census": {" ".join(key): value for key, value in sorted(census.items())}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    base = args.source_root / "lanes/new-core-transfer-20261017/low-displacement-20261020"
    raw = (base / "pivot-codes/final-normal/PIVOT-CODES.json").read_bytes()
    need(sha256(raw).hexdigest() == "49044ce1a2ef7a591084ba344e6d13d16e3e47ea56fd977c8c2218aed6b3a670", "Original pivot payload")
    packet = json.loads(raw)
    source_raw = gzip.decompress((base / "odd16-normal-v2/EXTENSION-PROGRAM.json.gz").read_bytes())
    need(sha256(source_raw).hexdigest() == "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4", "Actual response")
    model = json.loads(source_raw)["model"]
    word, inverse = (packet["scalar_words"][name] for name in ("code", "inverse_code"))
    code, forward_grid = replay(word)
    back, inverse_grid = replay(inverse)
    restored, valid_image_grid = replay(inverse, code, True)
    need(restored == replay(word, back)[0] == identity(), "Both full inverse orders")
    need(forward_grid == {"norm": "12", "binary_height": 0, "odd_three_height": 0, "division_rows": []}, "Forward prefix bounds")
    need((inverse_grid["norm"], inverse_grid["binary_height"], inverse_grid["odd_three_height"]) == ("8", 3, 1), "Inverse prefix bounds")
    need(len(valid_image_grid["division_rows"]) == 8 and valid_image_grid["odd_three_height"] == 0, "Valid image has no new odd denominator")
    need(any(not row["dyadic_input_coefficients_divisible_by_three"] for row in inverse_grid["division_rows"]), "Generic inverse is a distinct grid contract")
    forward_price, inverse_price = invoice(word), invoice(inverse)
    need(forward_price["old_real_scalar_units"] == inverse_price["old_real_scalar_units"] == 2078, "Exact old-unit invoice")
    need(forward_price["real_multiply_three_scans"] == inverse_price["real_divide_three_scans"] == 16, "Sixteen real scans")
    need(forward_price["real_divide_three_scans"] == inverse_price["real_multiply_three_scans"] == 0, "Correct scan direction")
    pair_raw = (args.source_root / "lanes/independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json").read_bytes()
    need(sha256(pair_raw).hexdigest() == "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585", "Actual pair geometry")
    pair_events = sum(3 + (g["matrix"][0][0] != 1) for g in json.loads(pair_raw)["pair_codes"])
    large_end = pair_events + sum(sum(s == -1 for s in g["signs"]) + 2 * len(g["signs"]) for g in model["vertex_assignments"])
    need(invoice(word[:pair_events])["old_real_scalar_units"] == 470, "Actual pair prefix invoice")
    need(invoice(word[pair_events:large_end])["old_real_scalar_units"] == 664, "Eight signed six-mode invoices")
    need(invoice(word[large_end:])["old_real_scalar_units"] == 944, "Eight eight-mode invoices")
    pivots = packet["pivots"]
    need(len(pivots) == len(set(pivots)) == 16, "Sixteen existing pivots")
    multipliers = {p: F(-5 if i < 8 else -7) for i, p in enumerate(pivots)}
    response = [{int(i): F(c) for i, c in row.items()} for row in model["response"]]
    need(multiply(code, response) == [{i: multipliers.get(p, F(1)) * c for i, c in row.items()} for p, row in enumerate(code)], "Actual diagonal response")
    translations = packet["entry_square_word"][:112]
    need(translations == [["translate", p, None, str(q)] for p, q in enumerate(model["ports"])], "One actual input translation per field")
    need(packet["entry_square_word"][112:] == word, "Input-side order C L")
    wrong_side = next((p, i, str(c), model["ports"][i], model["ports"][p]) for p, row in enumerate(code) for i, c in row.items() if model["ports"][i] != model["ports"][p])
    result = {"status": "PASS_INDEPENDENT_PIVOT_INVOICE_GRID", "pivot_payload_sha256": sha256(raw).hexdigest(), "response_decompressed_sha256": sha256(source_raw).hexdigest(), "forward_invoice": forward_price, "inverse_invoice": inverse_price, "forward_prefix": forward_grid, "inverse_prefix": inverse_grid, "valid_image_inverse_prefix": valid_image_grid, "scalar_inverse_orders": 2, "data_fields": 112, "untouched_roles_by_gate_bounds": 528, "actual_pivots": 16, "complement_fields": 96, "input_translation_maps": 112, "wrong_side_witness_target_input_coefficient_correct_wrong_label": wrong_side, "scope": "Original local scalar invoice and prefix grid. Valid-image division does not admit generic root streams. No native query, productive transport, or raw output decoder."}
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
