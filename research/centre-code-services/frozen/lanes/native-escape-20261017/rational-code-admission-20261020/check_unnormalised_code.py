"""Check the actual dyadic rank-thirty capture and its reduced code tests."""

from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
PINS = {
    "section": (LANES / "coherent-port/section-entry-20261020/SECTION.json",
                "23568099ea426947015eca86f7d86742a4758f33327e725b047441daab7c8bd7"),
    "response": (LANES / "new-core-transfer-20261017/low-displacement-20261020/run-normal/RESPONSE-PROGRAM.json",
                 "5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c"),
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def dense(rows, columns):
    return [[F(row.get(str(j), 0)) for j in range(columns)] for row in rows]


def product(a, b):
    out = [[F(0)] * len(b[0]) for _ in a]
    for i, row in enumerate(a):
        for k, value in enumerate(row):
            if value:
                out[i] = [x + value * y for x, y in zip(out[i], b[k])]
    return out


def reduced(a, p):
    return [[x.numerator * pow(x.denominator, -1, p) % p for x in row] for row in a]


def rank(a, p):
    a = reduced(a, p)
    k = 0
    for j in range(len(a[0])):
        i = next((i for i in range(k, len(a)) if a[i][j]), None)
        if i is None:
            continue
        a[i], a[k] = a[k], a[i]
        scale = pow(a[k][j], -1, p)
        a[k] = [x * scale % p for x in a[k]]
        for i in range(k + 1, len(a)):
            scale = a[i][j]
            if scale:
                a[i] = [(x - scale * y) % p for x, y in zip(a[i], a[k])]
        k += 1
        if k == len(a):
            break
    return k


def dyadic(a):
    return all(x.denominator & (x.denominator - 1) == 0 for row in a for x in row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    sources, pins = {}, {}
    for name, (path, digest) in PINS.items():
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == digest, "Source pin " + name)
        sources[name] = json.loads(raw)
        pins[name] = {"path": str(path), "sha256": digest}
    s, model = sources["section"], sources["response"]
    a, ordinary = s["selected_carriers"], s["ordinary_carriers"]
    need(len(a) == 30 and sorted(a + ordinary) == list(range(112)), "Actual complete row partition")
    u, v = dense(model["correction_U"], 30), dense(model["correction_V"], 112)
    b, bi = dense(s["B0"], 30), dense(s["B0_inverse"], 30)
    expected_b = [[F(0)] * 30 for _ in range(30)]
    for i in range(0, 16, 2):
        expected_b[i][i:i + 2] = [F(-4), F(1)]
        expected_b[i + 1][i:i + 2] = [F(2), F(-2)]
    for i in range(16, 30):
        expected_b[i][i] = F(-3 if i in (25, 26, 27) else -5)
    need(b == expected_b, "Complete square-free odd Smith blocks")
    ua, uai = [u[p] for p in a], dense(s["minor_inverse"], 30)
    e = dense(model["response"], 112)
    need(product(v, u) == b and product(ua, uai) == product(uai, ua) == identity(30), "Actual factors and minor")
    need(dyadic(u) and dyadic(v) and dyadic(uai), "Actual dyadic input maps")
    capture = dense(s["C0"], 112)
    for i, p in enumerate(a):
        capture[p] = v[i][:]
    normalised = dense(s["C0"], 112)
    scale = identity(112)
    for i, p in enumerate(a):
        scale[p] = [F(0)] * 112
        for j, q in enumerate(a):
            scale[p][q] = b[i][j]
    need(capture == product(scale, normalised), "Unnormalised capture identity")
    need(dyadic(capture), "Every capture coefficient is dyadic")
    pre = [[F(0)] * 112 for _ in range(30)]
    for i, p in enumerate(a):
        pre[i][p] = 1
        for q in ordinary:
            pre[i][q] = -v[i][q]
    pivot = product(bi, pre)
    decode = product(u, pivot)
    for p in ordinary:
        decode[p][p] += 1
    need(product(capture, decode) == product(decode, capture) == identity(112), "Both full code inverse orders")
    original_pivot = product(uai, [[F(q == p) for q in range(112)] for p in a])
    need(product(pre, capture) == product(b, original_pivot), "Valid decoder receives a B0-code")
    h = dense(s["encoded_response"], 112)
    need(product(capture, product(e, decode)) == h, "Unchanged centre action")
    hi = identity(112)
    gi = dense(s["H_inverse"], 30)
    for i, p in enumerate(a):
        hi[p] = [F(0)] * 112
        for j, q in enumerate(a):
            hi[p][q] = gi[i][j]
    need(dyadic(h) and dyadic(hi) and product(h, hi) == product(hi, h) == identity(112),
         "Centre action and inverse are dyadic")
    ei = [[F(i == j) - x for j, x in enumerate(row)] for i, row in enumerate(product(u, product(gi, v)))]
    need(dyadic(ei) and product(e, ei) == product(ei, e) == identity(112), "Actual response inverse is dyadic")
    need(product(hi, capture) == product(capture, ei), "Inverse centre action preserves the actual code")
    checks = {}
    for p in (3, 5):
        left = []
        if p == 3:
            for i in range(0, 16, 2):
                row = [F(0)] * 30
                row[i], row[i + 1] = 1, -1
                left.append(row)
        for i in range(16, 30):
            if b[i][i].numerator % p == 0:
                row = [F(0)] * 30
                row[i] = 1
                left.append(row)
        need(len(left) == 11 and rank(left, p) == 11, "Eleven independent centre syndromes")
        need(not any(x for row in reduced(product(left, b), p) for x in row), "Left nullspace of B0")
        syndromes = product(left, pre)
        need(rank(syndromes, p) == 11 and rank(capture, p) == 101, "Actual code image codimension")
        need(not any(x for row in reduced(product(syndromes, capture), p) for x in row), "Code has zero syndrome")
        need(reduced(product(syndromes, h), p) == reduced(syndromes, p)
             and reduced(product(syndromes, hi), p) == reduced(syndromes, p),
             "Both centre actions are identity on the code quotient")
        checks[str(p)] = {"syndrome_rank": 11, "capture_rank": 101,
                          "rows": [[str(x) for x in row] for row in syndromes]}
    bad_middle = identity(112)
    bad_middle[a[0]][a[0]] = 2
    l3 = [[F(x) for x in row] for row in checks["3"]["rows"]]
    bad = reduced(product(l3, product(bad_middle, capture)), 3)
    witness = next(((i, j, x) for i, row in enumerate(bad)
                    for j, x in enumerate(row) if x), None)
    need(witness is not None, "A dyadic unit need not preserve the code")
    payload = {"source_pins": pins, "selected_carriers": a, "ordinary_carriers": ordinary,
               "capture": [[str(x) for x in row] for row in capture],
               "decode": [[str(x) for x in row] for row in decode],
               "syndromes": checks,
               "nonpreserving_dyadic_unit": {"scaled_physical_port": a[0],
                                           "scale": 2, "modulus": 3,
                                           "syndrome_row_input_column_value": witness}}
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    (args.out / "UNNORMALISED-CODE.json").write_bytes(raw)
    receipt = {"status": "PASS_ACTUAL_UNNORMALISED_RANK30_CODE", "source_pins": pins,
               "payload_sha256": sha256(raw).hexdigest(), "all_data_columns": 112,
               "forward_is_dyadic": True, "centre_action_and_inverse_are_dyadic": True,
               "valid_decode_input_is_B0_code": True, "syndrome_ranks": {"3": 11, "5": 11},
               "scope": "Exact code algebra and divisibility interface. No elementary capture invoice or physical native caller."}
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
