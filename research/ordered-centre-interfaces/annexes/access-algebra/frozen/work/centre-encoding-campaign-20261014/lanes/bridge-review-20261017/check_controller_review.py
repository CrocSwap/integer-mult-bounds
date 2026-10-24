"""Check the matched controller with free operator words."""

from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parent
PINS = {
    "controller-followthrough-20261017/GENERAL-BRIDGES.md": "1871ff4f98ccc23e31221146f4be0012229ba2af64847353d42f0329842b59bf",
    "controller-followthrough-20261017/CHECKS.json": "6d35a2b2e92d0775874e50cd89a071dc5a02f575e8d58d04880a31167bf94af7",
    "controller-followthrough-20261017/check_general_bridges.py": "c4e2a92865a92deaa06bf70ef1d0aa4b717571e2ced49a5575cd1346b2490837",
}
ONE, ZERO = {(): 1}, {}


def require(condition, label):
    if not condition:
        raise ValueError(label)


def symbol(name, index=0, inverse=0):
    return {((name, index, inverse),): 1}


def plus(a, b, scale=1):
    result = dict(a)
    for word, coefficient in b.items():
        value = result.get(word, 0) + scale * coefficient
        if value:
            result[word] = value
        else:
            result.pop(word, None)
    return result


def normalize(word, projections):
    stack, scalar = [], 1
    for token in word:
        if stack and token[:2] == stack[-1][:2] and token[2] and token[2] == -stack[-1][2]:
            stack.pop()
        elif projections and stack and token == stack[-1] and token[0] == "P":
            continue
        elif stack and stack[-1][0] == "B" and token[0] == "D" and stack[-1][1] == token[1]:
            stack.pop()
            scalar *= 13
        else:
            stack.append(token)
    return tuple(stack), scalar


def times(a, b, projections=False):
    result = {}
    for left, c in a.items():
        for right, d in b.items():
            word, scale = normalize(left + right, projections)
            value = result.get(word, 0) + c * d * scale
            if value:
                result[word] = value
            else:
                result.pop(word, None)
    return result


def replay(m, policy, mutation=None):
    p = [symbol("P", i) for i in range(m)]
    a = [symbol("A", i, 1) for i in range(m)]
    ai = [symbol("A", i, -1) for i in range(m)]
    g = [symbol("G", i, 1) for i in range(m)]
    u = [plus(ONE, x, -1) for x in p]
    w = [symbol("W", i) if policy == "arbitrary" else u[i + 1] for i in range(m - 1)]
    t = [symbol("T", i) if policy == "arbitrary" else (ZERO if policy == "future_zero" else u[i + 1])
         for i in range(m - 1)]
    projections = policy != "arbitrary"
    mul = lambda x, y: times(x, y, projections)
    c, ci, v = symbol("C", inverse=1), symbol("C", inverse=-1), symbol("V")
    original_x, original_y = [symbol("x", i) for i in range(m)], [symbol("y", i) for i in range(m)]
    x, y = list(original_x), list(original_y)
    for i in range(m - 2, -1, -1):
        x[i] = plus(x[i], x[i + 1], -1)
    z = list(x)
    y[0] = plus(mul(c, y[0]), mul(v, x[0]))
    for i in range(m):
        ax, old_y = mul(a[i], x[i]), y[i]
        x[i], y[i] = plus(mul(u[i], ax), old_y, -1), plus(old_y, mul(p[i], ax))
        if i + 1 < m:
            x[i + 1] = mul(a[i], x[i + 1])
            x[i] = plus(x[i], x[i + 1])
            y[i + 1] = plus(y[i + 1], mul(w[i], y[i]), -1)
        y[i] = mul(g[i], plus(x[i], y[i]))
        if i + 1 < m:
            if mutation == "early_reset":
                x[i + 1] = mul(ai[i], x[i + 1])
            x[i] = plus(x[i], x[i + 1], -1)
            y[i + 1] = plus(y[i + 1], mul(t[i], y[i]))
            if mutation != "early_reset":
                x[i + 1] = mul(ai[i], x[i + 1])
    for i in range(m - 1, 0, -1):
        x[i] = plus(x[i], mul(u[i - 1] if mutation == "wrong_tail" else w[i - 1], x[i - 1]))
    x[0] = mul(ci, x[0])
    e = [mul(g[i], a[i]) for i in range(m)]
    h = [mul(ci, mul(plus(mul(u[0], a[0]), v, -1), z[0]))]
    for i in range(1, m):
        response = plus(mul(mul(u[i], a[i]), z[i]), mul(mul(w[i - 1], a[i - 1]), z[i - 1]))
        response = plus(response, mul(mul(t[i - 1], e[i - 1]), original_x[i - 1]), -1)
        h.append(response)
    expected_x = [plus(h[i], original_y[i], -1) for i in range(m)]
    expected_y = [mul(e[i], original_x[i]) for i in range(m)]
    if mutation:
        require((x, y) != (expected_x, expected_y), "Mutation must fail: " + mutation)
    else:
        require(x == expected_x and y == expected_y, "Free noncommuting endpoint identity")
        if projections:
            require(all(mul(p[i], h[i]) == ZERO for i in range(1, m)), "Every later query is preserved")
            require(mul(p[0], h[0]) != ZERO, "First response is a separate condition")
    return {"pairs": m, "policy": policy, "endpoint_words": sum(map(len, x + y))}


def matrix_add(a, b, scale=1):
    return [[plus(x, y, scale) for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def matrix_mul(a, b):
    rows = []
    for row in a:
        out = []
        for col in zip(*b):
            value = ZERO
            for left, right in zip(row, col):
                value = plus(value, times(left, right))
            out.append(value)
        rows.append(out)
    return rows


def signed_kernel_review():
    identity = [[ONE, ZERO], [ZERO, ONE]]
    pi = [[ONE, ZERO], [ZERO, ZERO]]
    s, a, p, u = {}, {}, {}, {}
    for stage in [1, 2, 3]:
        b, d = symbol("B", stage), symbol("D", stage)
        nb, nd = plus(ZERO, b, -1), plus(ZERO, d, -1)
        s[stage] = [[plus(ZERO, ONE, -1), nb], [nd, plus(ONE, times(d, b), -1)]]
        a[stage] = [[plus(ZERO, ONE, 12), nb], [nd, ONE]]
        p[stage] = [[ONE, b], [ZERO, ZERO]]
        u[stage] = matrix_add(identity, p[stage], -1)
        require(matrix_mul(s[stage], a[stage]) == matrix_mul(a[stage], s[stage]) == identity, "Both signed inverses")
        require(matrix_mul(p[stage], a[stage]) == matrix_add([[ZERO, ZERO], [ZERO, ZERO]], pi, -1), "Original selected return")
        require(matrix_mul(u[stage], a[stage]) == matrix_add(a[stage], pi), "Return factor")
    previous_x = [[symbol("xpA")], [symbol("xpU")]]
    next_z = [[symbol("ziA")], [symbol("ziU")]]
    previous_z = matrix_add(previous_x, next_z, -1)
    r = matrix_mul(matrix_mul(s[2], a[1]), previous_x)
    h = matrix_add(matrix_mul(matrix_mul(u[3], a[3]), next_z), matrix_mul(matrix_mul(u[3], a[1]), previous_z))
    h = matrix_add(h, matrix_mul(u[3], r), -1)
    ordinary = plus(times(plus(symbol("D", 1), symbol("D", 3), -1), next_z[0][0]), times(symbol("D", 2), r[0][0]), -1)
    require(h[1][0] == ordinary, "Exact signed ordinary response")
    require(h[0][0] == plus(ZERO, times(symbol("B", 3), ordinary), -1), "Exact signed selected response")
    require(matrix_mul(p[3], h) == [[ZERO], [ZERO]], "Actual oblique query preservation")
    return {"stages": 3, "relations_used": ["B_s D_s = 13 I"], "cross_stage_commutations": 0}


def main():
    for path, pin in PINS.items():
        require(sha256((LANES / path).read_bytes()).hexdigest() == pin, path)
    cases = [replay(m, policy) for policy in ["arbitrary", "future_zero", "future_matched"] for m in range(1, 9)]
    for policy in ["arbitrary", "future_zero", "future_matched"]:
        for m in range(2, 9):
            replay(m, policy, "early_reset")
            replay(m, policy, "wrong_tail")
    signed = signed_kernel_review()
    receipt = dict(status="PASS_INDEPENDENT_MATCHED_CONTROLLER", source_pins=PINS,
        checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(), cases=cases,
        controls={"early_idle_X_reset": 21, "wrong_tail_coefficient": 21,
                  "first_response_not_automatic": 16}, signed_kernel=signed,
        method="Free noncommutative words; only adjacent unit cancellations, specified idempotence, and B_s D_s = 13 I.",
        proof_scope="The induction proves all positive pair counts. The executable word checks cover m=1 through 8.",
        open_obligations=["Native local maps and idle-X code changes", "First response", "Complete decoder", "Finite maps, precision, stock and recursion"])
    (HERE / "CONTROLLER-REVIEW.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])
    print(json.dumps({"free_word_cases": len(cases), "mutation_controls": 42, "signed_kernel": signed}, sort_keys=True))


if __name__ == "__main__":
    main()
