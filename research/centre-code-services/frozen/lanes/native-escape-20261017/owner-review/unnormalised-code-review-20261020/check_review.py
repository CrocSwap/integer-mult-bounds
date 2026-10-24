"""Check the rank-thirty code from its pinned scalar factors."""

import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import shutil


HERE = Path(__file__).resolve().parent
LANE = HERE.parents[1]
LANES = LANE.parent
PRODUCER = LANE / "rational-code-admission-20261020"
PINS = {
    "section": (
        LANES / "coherent-port/section-entry-20261020/SECTION.json",
        "23568099ea426947015eca86f7d86742a4758f33327e725b047441daab7c8bd7",
    ),
    "response": (
        LANES / "new-core-transfer-20261017/low-displacement-20261020/run-normal/RESPONSE-PROGRAM.json",
        "5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c",
    ),
    "proof": (
        PRODUCER / "UNNORMALISED-CODE.md",
        "a89acbfead19cf4fdbeedafc8544f8910705fd27569f44301e1e8087746a719f",
    ),
    "checker": (
        PRODUCER / "check_unnormalised_code.py",
        "8f4dd74601bb40248bc642469256679361c4841aa496fe907682f3beb405c043",
    ),
    "payload": (
        PRODUCER / "unnormalised-final-normal/UNNORMALISED-CODE.json",
        "8dd0706ad41a843c9e74346b181389712a81ba6f354fdd019688e2d6b094908e",
    ),
    "receipt": (
        PRODUCER / "unnormalised-final-normal/CHECKS.json",
        "6058c99b814f26a061ad93ef2121c4a86578822f819c2f4fdc4fac5043932510",
    ),
    "constants": (
        PRODUCER / "centre-constants-normal/CENTRE-CONSTANTS.json",
        "9f45130ccde5bf1624bf051f4b10023411d6f35f0ac99bd6ab13572d4c530368",
    ),
    "constant_review": (
        HERE.parent / "centre-constants-review-20261020/FREEZE.json",
        "36195b052b3cf2e989b02070be09881de9cdf9d8e3f84ff325f3f3fd18710d00",
    ),
}


def need(ok, label):
    if not ok:
        raise ValueError(label)


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def dense(rows, width):
    return [[F(row.get(str(j), 0)) for j in range(width)] for row in rows]


def mm(a, b):
    columns = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, col) if x and y)
             for col in columns] for row in a]


def inverse_and_det(a):
    n = len(a)
    rows = [row[:] + unit for row, unit in zip(a, eye(n))]
    determinant = F(1)
    for j in range(n):
        k = next((k for k in range(j, n) if rows[k][j]), None)
        need(k is not None, "Nonsingular selected minor")
        if k != j:
            rows[j], rows[k] = rows[k], rows[j]
            determinant *= -1
        q = rows[j][j]
        determinant *= q
        rows[j] = [x / q for x in rows[j]]
        for k in range(n):
            if k != j and rows[k][j]:
                q = rows[k][j]
                rows[k] = [x - q * y for x, y in zip(rows[k], rows[j])]
    return [row[n:] for row in rows], determinant


def reduced(a, p):
    return [[x.numerator * pow(x.denominator, -1, p) % p
             for x in row] for row in a]


def rank(a, p):
    rows, k = reduced(a, p), 0
    for j in range(len(rows[0])):
        i = next((i for i in range(k, len(rows)) if rows[i][j]), None)
        if i is None:
            continue
        rows[k], rows[i] = rows[i], rows[k]
        q = pow(rows[k][j], -1, p)
        rows[k] = [q * x % p for x in rows[k]]
        for i in range(k + 1, len(rows)):
            q = rows[i][j]
            rows[i] = [(x - q * y) % p for x, y in zip(rows[i], rows[k])]
        k += 1
        if k == len(rows):
            break
    return k


def dyadic(a):
    return all(x.denominator & (x.denominator - 1) == 0 for row in a for x in row)


def height2(a):
    need(dyadic(a), "Dyadic coefficients")
    return max(x.denominator.bit_length() - 1 for row in a for x in row)


def embed(a, selected):
    result = eye(112)
    for i, p in enumerate(selected):
        result[p] = [F(0)] * 112
        for j, q in enumerate(selected):
            result[p][q] = a[i][j]
    return result


def replay_inverse(word, initial, expected):
    rows = [row[:] for row in initial]
    peak = max(sum(abs(x) for x in row) for row in rows)
    binary = height2(rows)
    scans = Counter()
    for gate in word:
        op, target = gate[:2]
        if op == "ADD":
            source, sign = gate[2:]
            need(source != target and sign in (-1, 1), "Unit source ADD")
            rows[target] = [x + sign * y for x, y in zip(rows[target], rows[source])]
        else:
            if op == "NEG":
                scale = F(-1)
            elif op == "SCALE2":
                scale = F(2) ** gate[2]
            else:
                need(op == "DIVIDE_ODD", "Known inverse gate")
                p = gate[2]
                need(all(x.numerator % p == 0 for x in rows[target]),
                     "Exact odd division on every dyadic input coefficient")
                scans[p] += 2
                scale = F(1, p)
            rows[target] = [scale * x for x in rows[target]]
        need(dyadic([rows[target]]), "Every valid-code prefix is dyadic")
        binary = max(binary, height2([rows[target]]))
        peak = max(peak, sum(abs(x) for x in rows[target]))
    need(rows == expected, "Literal inverse on all input columns")
    need(scans == {3: 22, 5: 22}, "Both exact real odd-scan counts")
    return {"stored_row_l1": str(peak), "binary_height": binary,
            "odd_height": 0, "real_divisions": dict(scans)}


def split_ring_check():
    def split(z):
        a, b = z
        return ((a + 2 * b) % 5, (a - 2 * b) % 5)

    values = [(a, b) for a in range(5) for b in range(5)]
    need(len({split(z) for z in values}) == 25, "Split residue map is bijective")
    for a, b in values:
        for c, d in values:
            x, y = split((a, b)), split((c, d))
            need(split(((a + c) % 5, (b + d) % 5)) ==
                 tuple((u + v) % 5 for u, v in zip(x, y)), "Split addition")
            need(split(((a * c - b * d) % 5, (a * d + b * c) % 5)) ==
                 tuple(u * v % 5 for u, v in zip(x, y)), "Split multiplication")
    return {"elements": 25, "operation_pairs": 625,
            "isomorphism": "a+ib -> (a+2b,a-2b) in F5 x F5"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    need(shutil.disk_usage(HERE).free >= 3 * 2**30, "Disk floor")
    objects, sources = {}, {}
    for name, (path, digest) in PINS.items():
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == digest, "Source pin " + name)
        sources[name] = {"path": str(path), "sha256": digest, "bytes": len(raw)}
        if path.suffix == ".json":
            objects[name] = json.loads(raw)
    for filename in ("CHECKS.json", "UNNORMALISED-CODE.json"):
        need((PRODUCER / "unnormalised-final-normal" / filename).read_bytes() ==
             (PRODUCER / "unnormalised-final-optimized" / filename).read_bytes(),
             "Producer normal and optimized bytes")
    model, section, payload = (objects[k] for k in ("response", "section", "payload"))
    selected = [0, 27, 9, 61, 11, 63, 20, 46, 37, 110, 41, 106, 76, 87, 78, 99,
                5, 3, 24, 23, 1, 8, 29, 26, 4, 18, 19, 39, 6, 31]
    ordinary = [p for p in range(112) if p not in selected]
    need(section["selected_carriers"] == payload["selected_carriers"] == selected and
         section["ordinary_carriers"] == payload["ordinary_carriers"] == ordinary,
         "Actual complete carrier partition")
    u, v = dense(model["correction_U"], 30), dense(model["correction_V"], 112)
    ua = [u[p] for p in selected]
    uai, determinant = inverse_and_det(ua)
    need(determinant == F(-1, 256) and all(x.denominator == 1 for row in uai for x in row),
         "Minor determinant and integral inverse")
    need(uai == dense(section["minor_inverse"], 30), "Source minor inverse")
    b = [[F(0)] * 30 for _ in range(30)]
    bi = [[F(0)] * 30 for _ in range(30)]
    for j in range(0, 16, 2):
        b[j][j:j + 2], b[j + 1][j:j + 2] = [F(-4), F(1)], [F(2), F(-2)]
        bi[j][j:j + 2], bi[j + 1][j:j + 2] = [F(-1, 3), F(-1, 6)], [F(-1, 3), F(-2, 3)]
    for j in range(16, 30):
        b[j][j] = F(-3 if j in (25, 26, 27) else -5)
        bi[j][j] = 1 / b[j][j]
    need(mm(v, u) == b == dense(section["B0"], 30), "Complete actual B0 block pattern")
    need(mm(b, bi) == mm(bi, b) == eye(30), "Both B0 inverse orders")
    need(bi == dense(section["B0_inverse"], 30), "Source B0 inverse")
    g = [[x + F(i == j) for j, x in enumerate(row)] for i, row in enumerate(b)]
    gi, _ = inverse_and_det(g)
    need(dyadic(gi) and gi == dense(section["H_inverse"], 30), "Actual dyadic G0 inverse")
    select = [eye(112)[p] for p in selected]
    t = mm(uai, select)
    projection = mm(u, t)
    capture = eye(112)
    for j, p in enumerate(selected):
        capture[p] = v[j][:]
    for p in ordinary:
        capture[p] = [F(p == q) - x for q, x in enumerate(projection[p])]
    pre = [row[:] for row in select]
    for j in range(30):
        for p in ordinary:
            pre[j][p] = -v[j][p]
    decode = mm(u, mm(bi, pre))
    for p in ordinary:
        decode[p][p] += 1
    need(capture == [[F(x) for x in row] for row in payload["capture"]] and
         decode == [[F(x) for x in row] for row in payload["decode"]],
         "Independent matrices equal the final payload")
    need(mm(capture, decode) == mm(decode, capture) == eye(112), "Both 112-column inverse orders")
    need(mm(pre, capture) == mm(b, t), "Valid decoder receives B0 times an integral pivot map")
    need(capture == mm(embed(b, selected), dense(section["C0"], 112)),
         "Relation to the source normalized code")
    uv = mm(u, v)
    e = [[F(i == j) + x for j, x in enumerate(row)] for i, row in enumerate(uv)]
    correction = mm(u, mm(gi, v))
    ei = [[F(i == j) - x for j, x in enumerate(row)] for i, row in enumerate(correction)]
    need(e == dense(model["response"], 112) and ei == dense(model["response_inverse"], 112),
         "Both actual response matrices")
    need(dyadic(e) and dyadic(ei) and mm(e, ei) == mm(ei, e) == eye(112),
         "Both response inverse orders")
    h, hi = embed(g, selected), embed(gi, selected)
    need(h == dense(section["encoded_response"], 112), "Source encoded response")
    need(mm(capture, mm(e, decode)) == h and mm(capture, mm(ei, decode)) == hi,
         "Both encoded response conjugacies")
    need(mm(h, hi) == mm(hi, h) == eye(112), "Both encoded response inverse orders")
    syndromes, syndrome_checks = {}, {}
    for p in (3, 5):
        n, pivots = [], []
        if p == 3:
            for j in range(0, 16, 2):
                row = [F(0)] * 30
                row[j], row[j + 1] = 1, -1
                n.append(row)
                pivots.append(j)
        for j in range(16, 30):
            if b[j][j].numerator % p == 0:
                n.append(eye(30)[j])
                pivots.append(j)
        need(len(n) == 11, "Eleven explicit syndrome rows")
        l = mm(n, pre)
        right = [[F(0)] * 11 for _ in range(112)]
        for j, pivot in enumerate(pivots):
            right[selected[pivot]][j] = 1
        need(mm(l, right) == eye(11), "Integral right inverse over the full scalar ring")
        need(l == [[F(x) for x in row] for row in payload["syndromes"][str(p)]["rows"]],
             "Exact published syndrome rows")
        need(not any(x for row in reduced(mm(n, b), p) for x in row) and
             not any(x for row in reduced(mm(l, capture), p) for x in row),
             "All actual capture columns have zero syndrome")
        need(rank(l, p) == 11 and rank(capture, p) == 101, "Finite real rank cross-check")
        need(reduced(mm(l, h), p) == reduced(l, p) == reduced(mm(l, hi), p),
             "Both encoded responses fix the quotient")
        syndromes[p] = l
        syndrome_checks[p] = {"rows": 11, "capture_rank_over_Fp": 101,
                              "right_inverse_ports": [selected[j] for j in pivots],
                              "integral_right_inverse": True,
                              "both_response_quotient_actions": "identity"}
    word = objects["constants"]["families"]["rank30"]["words"]["B0_inverse"]
    counts = Counter(gate[0] for gate in word)
    need(8 * counts["ADD"] + 2 * (counts["NEG"] + counts["SCALE2"]) == 204,
         "Exact scalar cost of the omitted inverse")
    valid_checks = {"B0_parameter": replay_inverse(word, b, eye(30))}
    for name, middle, raw_middle in (("identity", eye(112), eye(112)), ("H", h, e), ("H_inverse", hi, ei)):
        argument = mm(pre, mm(middle, capture))
        valid_checks[name] = replay_inverse(word, argument, mm(t, raw_middle))
    good = [[F(0)] for _ in range(112)]
    good[selected[0]][0] = good[selected[1]][0] = 1
    need(dyadic(mm(decode, good)), "Explicit valid code witness")
    bad = [row[:] for row in good]
    bad[selected[0]][0] += bad[selected[1]][0]
    need(reduced(mm(syndromes[3], bad), 3)[0][0] == 1 and not dyadic(mm(decode, bad)),
         "Unit ADD can leave the code")
    helper_target = selected[16]
    need(syndromes[5][0][helper_target] == 1,
         "An arbitrary helper can violate the full-role condition")
    helper_data = [[F(p == helper_target)] for p in range(112)]
    need(not dyadic(mm(decode, helper_data)), "Helper witness needs an odd denominator")
    for name, (path, digest) in PINS.items():
        need(sha256(path.read_bytes()).hexdigest() == digest, "Source unchanged " + name)
    receipt = {
        "status": "PASS_INDEPENDENT_UNNORMALISED_CODE_REVIEW",
        "source_pins": sources,
        "matrix_checks": {
            "data_columns": 112, "minor_determinant": str(determinant),
            "minor_inverse_integral": True, "both_capture_inverse_orders": True,
            "capture_binary_height": height2(capture),
            "both_response_conjugacies": True, "both_response_inverse_orders": True,
            "B0_blocks": {"two_by_two": 8, "minus_three": 3, "minus_five": 11},
        },
        "syndromes": syndrome_checks,
        "gaussian_mod5": split_ring_check(),
        "valid_constant_inverse_prefixes": valid_checks,
        "negative_controls": {
            "unit_add": {"target": selected[0], "source": selected[1],
                         "valid_centre_pair": [1, 1], "invalid_pair": [2, 1],
                         "mod3_syndrome": 1},
            "arbitrary_helper": {"target": helper_target, "helper_value": 1,
                                 "data_block": "identity", "mod5_syndrome": 1},
        },
        "producer_normal_optimized_equal": True,
        "preserved_source_bytes": True,
        "scope": "Exact scalar code and full-role dyadic image criterion. No elementary capture invoice or physical caller.",
    }
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    (args.out / "SOURCE-MANIFEST.json").write_text(json.dumps(sources, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
