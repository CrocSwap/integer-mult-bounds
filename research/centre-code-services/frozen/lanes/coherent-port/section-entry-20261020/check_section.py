"""Check the rank-thirty entry code and its exact phase contract."""

from fractions import Fraction as F
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
SOURCE = LANES / "new-core-transfer-20261017/low-displacement-20261020/run-normal/RESPONSE-PROGRAM.json"
SOURCE_PIN = "5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c"
PAIRS = LANES / "independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json"
PAIRS_PIN = "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585"
A = [0, 27, 9, 61, 11, 63, 20, 46, 37, 110, 41, 106, 76, 87, 78, 99,
     5, 3, 24, 23, 1, 8, 29, 26, 4, 18, 19, 39, 6, 31]
P = 1000003


def require(ok, text):
    if not ok:
        raise RuntimeError(text)


def read_pinned(path, pin):
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == pin, str(path))
    return json.loads(raw)


def rows(values):
    return [{int(j): F(c) for j, c in row.items() if F(c)} for row in values]


def identity(n):
    return [{i: F(1)} for i in range(n)]


def add(a, b, scale=F(1)):
    out = dict(a)
    for j, c in b.items():
        out[j] = out.get(j, F(0)) + scale * c
        if not out[j]:
            del out[j]
    return out


def product(a, b):
    out = []
    for row in a:
        result = {}
        for k, c in row.items():
            result = add(result, b[k], c)
        out.append(result)
    return out


def inverse(a, n):
    m = [[a[i].get(j, F(0)) for j in range(n)] +
         [F(i == j) for j in range(n)] for i in range(n)]
    determinant = F(1)
    for k in range(n):
        candidates = [i for i in range(k, n) if m[i][k]]
        require(bool(candidates), "singular matrix")
        j = candidates[0]
        if j != k:
            m[j], m[k] = m[k], m[j]
            determinant = -determinant
        pivot = m[k][k]
        determinant *= pivot
        m[k] = [c / pivot for c in m[k]]
        for i in range(n):
            if i != k and m[i][k]:
                c = m[i][k]
                m[i] = [x - c * y for x, y in zip(m[i], m[k])]
    result = [{j: m[i][n + j] for j in range(n) if m[i][n + j]}
              for i in range(n)]
    return result, determinant


def serialize(a):
    return [{str(j): str(c) for j, c in sorted(row.items())} for row in a]


def mod(c):
    return c.numerator * pow(c.denominator, -1, P) % P


def modular_minor(a, n):
    m = [[mod(row.get(j, F(0))) for j in range(n)] for row in a]
    pivots = []
    r = 0
    determinant = 1
    for c in range(n):
        candidates = [i for i in range(r, len(m)) if m[i][c]]
        if not candidates:
            continue
        k = candidates[0]
        if k != r:
            m[k], m[r] = m[r], m[k]
            determinant = -determinant
        pivot = m[r][c]
        determinant = determinant * pivot % P
        inv = pow(pivot, -1, P)
        m[r] = [x * inv % P for x in m[r]]
        for i in range(r + 1, len(m)):
            if m[i][c]:
                t = m[i][c]
                m[i] = [(x - t * y) % P for x, y in zip(m[i], m[r])]
        pivots.append(c)
        r += 1
        if r == len(m):
            break
    return pivots, determinant % P


def write(name, data):
    text = json.dumps(data, sort_keys=True, indent=2) + "\n"
    (HERE / name).write_text(text)
    return hashlib.sha256(text.encode()).hexdigest()


def main():
    src = read_pinned(SOURCE, SOURCE_PIN)
    pair_source = read_pinned(PAIRS, PAIRS_PIN)
    u = rows(src["correction_U"])
    v = rows(src["correction_V"])
    e = rows(src["response"])
    qs = src["ports"]
    require(len(set(A)) == 30, "minor rows")
    remaining = [p for p in range(112) if p not in A]
    ua = [u[p] for p in A]
    ua_inv, ua_det = inverse(ua, 30)
    require(ua_det == F(-1, 256), "minor determinant")
    require(all(c.denominator == 1 for row in ua_inv for c in row.values()),
            "integral minor inverse")
    require(product(ua, ua_inv) == identity(30), "minor right inverse")
    require(product(ua_inv, ua) == identity(30), "minor left inverse")

    b0 = product(v, u)
    expected_b0 = []
    for j in range(8):
        expected_b0.extend([{2*j: F(-4), 2*j+1: F(1)},
                            {2*j: F(2), 2*j+1: F(-2)}])
    expected_b0.extend([{16+j: F(-len(clique))}
                        for j, clique in enumerate(src["small_cliques"])])
    require(b0 == expected_b0, "constant cross Gram blocks")
    b0_inv, b0_det = inverse(b0, 30)
    d0 = product(b0_inv, v)
    require(product(d0, u) == identity(30), "left section inverse")
    h = [add(row, identity(30)[i]) for i, row in enumerate(b0)]
    h_inv, h_det = inverse(h, 30)
    require(product(h, h_inv) == identity(30), "centre right inverse")

    # Output rows remain in their physical carrier slots.
    c0 = [dict() for _ in range(112)]
    uua = product(u, ua_inv)
    for j, p in enumerate(A):
        c0[p] = d0[j]
    for p in remaining:
        c0[p] = add({p: F(1)},
                    {A[j]: -c for j, c in uua[p].items()})
    c0_inv = []
    for p in range(112):
        row = {A[j]: c for j, c in u[p].items()}
        if p in remaining:
            row[p] = row.get(p, F(0)) + 1
        for j, c in u[p].items():
            row = add(row, {r: value for r, value in d0[j].items()
                            if r in remaining}, -c)
        c0_inv.append(row)
    require(product(c0, c0_inv) == identity(112), "square code right inverse")
    require(product(c0_inv, c0) == identity(112), "square code left inverse")
    encoded_e = identity(112)
    for j, p in enumerate(A):
        encoded_e[p] = {A[k]: c for k, c in h[j].items()}
    require(product(c0, e) == product(encoded_e, c0),
            "complete unit response in code coordinates")

    # Replay the three block updates of C0 on all 112 arbitrary inputs.
    state = identity(112)
    old_selected = [state[p] for p in A]
    new_selected = product(ua_inv, old_selected)
    for j, p in enumerate(A):
        state[p] = new_selected[j]
    for p in remaining:
        for j, c in u[p].items():
            state[p] = add(state[p], state[A[j]], -c)
    for j, p in enumerate(A):
        for r, c in d0[j].items():
            if r in remaining:
                state[p] = add(state[p], state[r], c)
    require(state == c0, "ordered in-place square code")

    pair_set = {tuple(record["ports"]) for record in pair_source["pair_codes"]}
    carrier_pairs = [A[2*j:2*j+2] for j in range(8)]
    require(all(tuple(pair) in pair_set for pair in carrier_pairs),
            "actual complete physical pairs")
    require(all(qs[p] ^ qs[r] == 45 for p, r in carrier_pairs),
            "common pair direction")

    # A nonzero modular minor is an exact rational rank certificate.
    require(all(P % d for d in range(2, 1001)), "prime modulus")
    chi = 92
    signs = [(-1) ** ((chi & q).bit_count() % 2) for q in qs]
    vl = [{p: c * signs[p] for p, c in row.items()} for row in v]
    columns, determinant_mod = modular_minor(v + vl, 112)
    require(len(columns) == 60 and determinant_mod != 0,
            "full missing-reader rank")
    square = [{j: row.get(p, F(0)) for j, p in enumerate(columns)
               if row.get(p, F(0))} for row in v + vl]
    check_columns, check_det = modular_minor(square, 60)
    require(check_columns == list(range(60)) and check_det == determinant_mod,
            "serialized minor")

    data = {
        "source_sha256": {"response": SOURCE_PIN, "pair_flags": PAIRS_PIN},
        "selected_carriers": A,
        "ordinary_carriers": remaining,
        "selected_q": [qs[p] for p in A],
        "carrier_pairs": carrier_pairs,
        "minor_determinant": str(ua_det),
        "minor_inverse": serialize(ua_inv),
        "B0": serialize(b0),
        "B0_inverse": serialize(b0_inv),
        "B0_determinant": str(b0_det),
        "H": serialize(h),
        "H_inverse": serialize(h_inv),
        "H_determinant": str(h_det),
        "D0": serialize(d0),
        "C0": serialize(c0),
        "C0_inverse": serialize(c0_inv),
        "encoded_response": serialize(encoded_e),
        "old_reader_counterexample": {
            "character": chi,
            "prime": P,
            "minor_columns": columns,
            "minor_determinant_mod_prime": determinant_mod,
            "stacked_rank": 60,
            "restriction_rank": 30,
        },
        "block_program_C0": [
            "selected := U_A^-1 selected",
            "ordinary -= U_U selected",
            "selected += D0_U ordinary",
        ],
        "entry_code": "C_in = C0 Q^2",
        "transported_code": "C_out = Q^-1 C0 Q^-1",
        "transported_response": "diag(Q_A^-1 H Q_A,I_U)",
        "scope": "Exact square-code algebra and typed phase identities; no global caller or scalar/native invoice",
    }
    payload_pin = write("SECTION.json", data)
    receipt = {
        "status": "PASS_EXACT_RANK30_ENTRY_SECTION",
        "payload_sha256": payload_pin,
        "source_sha256": data["source_sha256"],
        "arbitrary_data_columns": 112,
        "new_data_fields": 0,
        "minor_determinant": str(ua_det),
        "minor_inverse_integral": True,
        "constant_centre_blocks": {"two_by_two": 8, "scalar": 14},
        "common_pair_direction": 45,
        "old_reader_restriction_rank_at_character_92": 30,
        "checked": [
            "both square-code inverse orders",
            "complete E conjugation",
            "ordered three-block code",
            "actual physical pair labels",
            "nonzero sixty-by-sixty modular minor",
        ],
        "not_checked": [
            "elementary scalar compiler and cost",
            "recursive child code admission",
            "routed interstage code transitions",
            "raw output decoding",
            "extra-centre productive ownership",
        ],
    }
    write("CHECKS.json", receipt)
    print("PASS_EXACT_RANK30_ENTRY_SECTION")


if __name__ == "__main__":
    main()
