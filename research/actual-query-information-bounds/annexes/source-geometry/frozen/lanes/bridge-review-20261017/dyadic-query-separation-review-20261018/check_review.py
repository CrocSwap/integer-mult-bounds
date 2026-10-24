"""Review the residue-field query theorem on the actual centre matrices."""

from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parents[2]
PINS = {
    "root/DYADIC-QUERY-SEPARATION-20261018.md": "664f430efd099f35cbc7c2abc8025968c03020707027857d2882daa51a065a1a",
    "root/check_dyadic_query_separation_20261018.py": "b4ed000b5b600944f614b86ae7a88ac55af8eac3213e6827ed211a2630ccd342",
    "root/DYADIC-QUERY-SEPARATION-20261018.json": "e66d5c311490c06973bf604d207fb5cf7a9cd4800c0cea049623c3b5e2369732",
    "lanes/oblique-native-20261017/minor-input-log/UNIT-COMPLETION.md": "1a4d715e089773a9063fba88d5b83ec770bb5eb6ed501bc8f96b290c19b08401",
    "lanes/controller-followthrough-20261017/MINOR-LOG-SOURCE-ACCESS.md": "50ce523e083f70556cc62694219da94b684cc898f3d5e358767fcc40dd77e4bc",
}
CORE = "lanes/new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz"
CORE_RAW_PIN = "a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa"
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]
U = [p for p in range(112) if p not in A]
P = 13


def require(ok, label):
    if not ok:
        raise ValueError(label)


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def tr(a):
    return [list(c) for c in zip(*a)]


def mm(a, b):
    out = [[Q(0) for _ in b[0]] for _ in a]
    for i, row in enumerate(a):
        for k, value in enumerate(row):
            if value:
                for j, right in enumerate(b[k]):
                    if right:
                        out[i][j] += value * right
    return out


def inverse(a):
    n = len(a)
    rows = [list(row) + unit for row, unit in zip(a, eye(n))]
    for j in range(n):
        pivot = next((k for k in range(j, n) if rows[k][j]), None)
        require(pivot is not None, "Invertible exact minor")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        value = rows[j][j]
        rows[j] = [x / value for x in rows[j]]
        for k in range(n):
            if k != j:
                value = rows[k][j]
                rows[k] = [x - value * y for x, y in zip(rows[k], rows[j])]
    return [row[n:] for row in rows]


def dyadic(a):
    return all(x.denominator & (x.denominator - 1) == 0 for row in a for x in row)


def mod(a):
    out = []
    for row in a:
        values = []
        for x in row:
            x = Q(x)
            require(x.denominator % P != 0, "The coefficient has a defined residue")
            values.append(x.numerator * pow(x.denominator, -1, P) % P)
        out.append(values)
    return out


def pivots(a):
    # Build a column basis, instead of reducing the source matrix by rows.
    basis = {}
    chosen = []
    for j, col in enumerate(zip(*a)):
        v = list(col)
        for pivot, b in sorted(basis.items()):
            value = v[pivot]
            v = [(x - value * y) % P for x, y in zip(v, b)]
        pivot = next((k for k, value in enumerate(v) if value), None)
        if pivot is not None:
            inv = pow(v[pivot], -1, P)
            basis[pivot] = [x * inv % P for x in v]
            chosen.append(j)
    return chosen


def determinant(a):
    rows = [list(r) for r in a]
    det = Q(1)
    for j in range(len(rows)):
        pivot = next((k for k in range(j, len(rows)) if rows[k][j]), None)
        if pivot is None:
            return Q(0)
        if pivot != j:
            rows[j], rows[pivot] = rows[pivot], rows[j]
            det *= -1
        v = rows[j][j]
        det *= v
        for k in range(j + 1, len(rows)):
            c = rows[k][j] / v
            for col in range(j + 1, len(rows)):
                rows[k][col] -= c * rows[j][col]
    return det


def actual_matrices():
    for path, pin in PINS.items():
        require(sha256((CAMPAIGN / path).read_bytes()).hexdigest() == pin, path)
    raw = gzip.decompress((CAMPAIGN / CORE).read_bytes())
    require(sha256(raw).hexdigest() == CORE_RAW_PIN, "Actual clean-core payload pin")
    core = json.loads(raw)
    r = [[Q(row.get(str(p), 0)) for p in range(112)] for row in core["R"]]
    ra = [[row[p] for p in A] for row in r]
    ru = [[row[p] for p in U] for row in r]
    rai = inverse(ra)
    b = mm(rai, ru)
    d = mm(tr(ru), tr(rai))
    require(dyadic(b) and dyadic(d), "Actual graphs are dyadic")
    require(mm(b, d) == [[13 * x for x in row] for row in eye(8)], "Actual BD=13I")
    dt = [d[U.index(p)] for p in T]
    dti = inverse(dt)
    bt = [[row[U.index(p)] for p in T] for row in b]
    bti = inverse(bt)
    require(dyadic(dti) and dyadic(bti), "Actual source and query minors are dyadic units")
    require(mm(dt, dti) == mm(dti, dt) == eye(8), "Both ordinary inverse-minor orders")
    require(mm(bt, bti) == mm(bti, bt) == eye(8), "Both B inverse-minor orders")
    m = [[Q(0) for _ in U] for _ in A]
    for i in range(8):
        for j, p in enumerate(T):
            m[i][U.index(p)] = dti[i][j]
    require(mm(m, d) == eye(8), "Sparse starting section")
    return b, d, m


def log_checks(b, d, m):
    require(len(pivots(mod(b))) == 8, "B has full row rank modulo 13")
    cols = pivots(mod(b + m))
    require(len(cols) == 16, "Independent source stack modulo 13")
    minor = [[row[j] for j in cols] for row in b + m]
    det = determinant(minor)
    require(det and mod([[det]])[0][0], "Explicit minor lifts to a nonzero rational determinant")
    ker = eye(104)
    projection = mm(d, m)
    ker = [[x - y for x, y in zip(row, sub)] for row, sub in zip(ker, projection)]
    require(mm(ker, d) == [[0] * 8 for _ in U], "Exact kernel projector rows")
    cases = []
    last = None
    for case in range(24):
        unit = eye(8)
        a, j = case % 8, (case + 1) % 8
        unit[a][a] = Q(2) if case % 2 else Q(1, 2)
        unit[a][j] = Q((-1) ** case, 2 ** (case % 3))
        unit_inv = inverse(unit)
        require(unit != eye(8) and dyadic(unit_inv) and mm(unit, unit_inv) == mm(unit_inv, unit) == eye(8), "Nonidentity dyadic unit K")
        candidate = mm(unit, m)
        for row in range(8):
            krow = ker[(17 * case + 9 * row + 1) % 104]
            coefficient = Q(1 + case % 5, 2 ** (row % 3))
            candidate[row] = [x + coefficient * y for x, y in zip(candidate[row], krow)]
        require(mm(candidate, d) == unit, "MD can be a general unit, not only identity")
        require(len(pivots(mod(b + candidate))) == 16, "Every general-unit fixture has rank 16")
        cases.append({"case": case, "MD_is_identity": False, "stack_rank_mod_13": 16})
        last = candidate
    matched = [[x / 13 for x in row] for row in b]
    require(mm(matched, d) == eye(8) and all(13 * x == y for row, base in zip(matched, b) for x, y in zip(row, base)), "Matched exact section and row dependence")
    require(not dyadic(matched), "Matched section leaves the dyadic ring")
    try:
        mod(matched)
    except ValueError:
        pass
    else:
        raise ValueError("The matched coefficient must not have a mod-13 residue")
    require(len(pivots(mod(b + b))) == 8 and mm(b, d) != eye(8), "A rationally invertible MD alone is insufficient")
    require(len(pivots([[0], [1]])) == 1, "B=13,D=M=1 defeats the conclusion without full residue rank")
    require(len(pivots([[1], [1]])) == 1, "B=D=M=1 defeats the conclusion when c survives reduction")
    return last, {"B_rank_mod_13": 8, "stack_rank_mod_13": 16,
                  "explicit_minor_ports": [U[j] for j in cols], "explicit_minor_determinant": str(det),
                  "nonidentity_MD_cases": cases, "matched_rank_over_Q": 8,
                  "controls": ["M=B has MD=13I and rank-eight stack", "Missing B residue rank", "Missing zero residue of c", "Matched coefficients have no residue at 13"]}


def mm_mod(a, b):
    columns = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, col)) % P for col in columns] for row in a]


def route(index):
    # This is the residue of L(b) U(i*a), a Gaussian-dyadic unit.
    a, b = (index % 7) + 1, (index % 5) + 1
    ia = 5 * a % P
    forward = [[1, ia], [b, (1 + b * ia) % P]]
    back = [[(1 + b * ia) % P, -ia % P], [-b % P, 1]]
    require(mm_mod(forward, back) == mm_mod(back, forward) == [[1, 0], [0, 1]], "Gaussian unit route and its inverse")
    return forward, back


def lift(a, target_routes, source_routes):
    out = [[0] * (2 * len(a[0])) for _ in range(2 * len(a))]
    for i, row in enumerate(a):
        left = target_routes[i][1]
        for j, x in enumerate(row):
            block = mm_mod(left, source_routes[j][0])
            for s in range(2):
                for t in range(2):
                    out[2 * i + s][2 * j + t] = x * block[s][t] % P
    return out


def routed_check(b, d, m):
    require((5 * 5 + 1) % P == 0 and 2 * 7 % P == 1, "Gaussian dyadic residue i->5, 1/2->7")
    eroutes = [route(3 * j + 1) for j in range(8)]
    uroutes = [route(5 * j + 2) for j in range(104)]
    require(mm_mod(eroutes[0][0], uroutes[0][0]) != mm_mod(uroutes[0][0], eroutes[0][0]), "The fixture uses noncommuting routes")
    br = lift(mod(b), eroutes, uroutes)
    dr = lift(mod(d), uroutes, eroutes)
    mr = lift(mod(m), eroutes, uroutes)
    require(mm_mod(br, dr) == [[0] * 16 for _ in range(16)], "Routed BD reduces to zero with the exact order")
    require(len(pivots(mm_mod(mr, dr))) == 16, "Routed MD is a unit")
    require(len(pivots(br)) == 16 and len(pivots(br + mr)) == 32, "Routed two-coordinate stack has rank 32")
    return {"coordinates_per_field": 2, "query_rank_mod_13": 32, "noncommuting_routes": True,
            "scope": "An actual-B Gaussian-unit conjugation fixture; the general finite-operator version follows from the residue proof, not a new native route replay."}


def full_null_check():
    zero, v, beta = {}, {(): 1}, {("beta",): 1}

    def add(a, b, coefficient=1):
        out = dict(a)
        for word, value in b.items():
            out[word] = out.get(word, 0) + coefficient * value
            if not out[word]:
                del out[word]
        return out

    def apply(op, a):
        out = {}
        for word, value in a.items():
            term = (op,) + word
            if len(term) >= 2 and term[:2] in [("Q", "q"), ("q", "Q")]:
                term = term[2:]
            out[term] = out.get(term, 0) + value
        return {word: value for word, value in out.items() if value}

    bv, mv = apply("B", v), apply("M", v)
    dbv = apply("D", bv)
    original_u = add(v, dbv, -1)
    qa = add(zero, mv, -1)
    a = apply("q", qa)
    original_b = add(apply("Q", bv), apply("q", mv), -1)
    original_b = {word: -value for word, value in original_b.items()}
    incoming_v = add(dbv, original_u)
    incoming_b = add(original_b, a)
    d = add(qa, apply("M", incoming_v))
    h = add(apply("q", incoming_b), apply("B", incoming_v))
    w = add(add(original_u, incoming_v, -1), apply("D", add(d, apply("q", incoming_b), -1)))
    require(incoming_v == v and d == h == w == zero, "Full-null family without any MD or BD relation")
    require(add(add(zero, incoming_v, -1), v) == zero, "The next ordinary bridge cancels for every pair count")
    bad_b = add(zero, apply("Q", bv), -1)
    require(add(apply("q", add(bad_b, a)), bv) != zero, "The original-b qMv term is necessary")
    source_w = add(add(zero, apply("D", beta), -1), add(apply("D", mv), v, -1))
    source_d = mv
    f0 = add(add(zero, source_w, -1), apply("D", source_d))
    g = add(source_d, apply("M", f0), -1)
    require(f0 == add(v, apply("D", beta)) and g == add(zero, apply("M", apply("D", beta)), -1), "General MD unit-criterion factorization")
    return {"operator_relations": ["Qq=I", "qQ=I"], "uses_MD_identity": False,
            "uses_BD_identity_for_null_family": False, "unit_factorization": "diag(I,-MD)",
            "wrong_original_b_control": True, "all_pair_counts": "The future inputs and all visible outputs are zero; the only nonzero next-bank bridge is -v+v."}


def main():
    b, d, m = actual_matrices()
    candidate, actual = log_checks(b, d, m)
    routed = routed_check(b, d, candidate)
    full_null = full_null_check()
    out = {"status": "PASS_INDEPENDENT_DYADIC_QUERY_SEPARATION", "source_pins": PINS,
           "core_decompressed_sha256": CORE_RAW_PIN, "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
           "actual_source": actual, "routed_operator_fixture": routed, "formal_full_null": full_null,
           "universal_proof": "Residue row relation times D forces beta=0 because MD is a unit; full residue rank of B forces alpha=0. A nonzero residue minor lifts to the fraction field.",
           "scope": "Fixed linear observations on the full underlying field space, with arbitrary postprocessing. No native-child, bit-packing, arbitrary nonlinear-encoding or complete supplier lower bound."}
    (HERE / "REVIEW.json").write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print(out["status"])
    print(json.dumps({"rank": 16, "matched_rank": 8, "MD_nonidentity_cases": 24, "routed_rank": 32,
                      "null_family_uses_MD_identity": False}, sort_keys=True))


if __name__ == "__main__":
    main()
