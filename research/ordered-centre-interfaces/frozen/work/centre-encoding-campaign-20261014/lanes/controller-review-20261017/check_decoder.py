"""Check the separate content decoder reductions."""

from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("independent_controller_review", HERE/"check_review.py")
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
add, neg, apply = review.add, review.neg, review.apply


def decode(m, family, option):
    endpoint = review.make_tape(m, family, option).rows()
    w = [endpoint[4*i+1] for i in range(m)]
    for i in range(1, m):
        w[i] = add(w[i], neg(w[i-1]))
    a = [apply("q", endpoint[4*i+2]) for i in range(m)]
    retired = [endpoint[4*i+3] for i in range(m)]
    suffix = [{} for _ in range(m+1)]
    incoming, selected = [{} for _ in range(m)], [{} for _ in range(m)]
    if family == "weighted":
        original = []
        for i in range(m):
            s, t = 2*i+1, 2*i+2
            value = add(retired[i], neg(apply(f"C{t}", a[i])))
            original.append(add(apply(f"H{s} K{t}", value), apply(f"C{s} Q", a[i])))
        for i in range(m-1, -1, -1):
            suffix[i] = add(original[i], neg(suffix[i+1]))
    for i in range(m-1, -1, -1):
        s, t = 2*i+1, 2*i+2
        f = endpoint[4*i]
        if family == "raw":
            k = add(w[i], suffix[i+1])
            echo_t = apply(f"B{t}", k)
            response = echo_t if option else add(echo_t, a[i])
            fresh_query = apply(f"B{s}", retired[i])
            echo_s = add(fresh_query, neg(apply(f"B{s}", k)), apply(f"B{s} D{t}", response))
            beta = add(f, apply("q", echo_t), neg(echo_s))
            selected[i] = apply("Q", beta)
            incoming[i] = add(retired[i], neg(k), apply(f"D{t}", response))
            suffix[i] = add(w[i], incoming[i], apply(f"D{s}", beta), neg(apply(f"D{s} Q", a[i])))
        else:
            incoming[i] = add(apply(f"K{s}", suffix[i]), neg(apply(f"K{s} C{s} Q", a[i])), neg(w[i]))
            k = add(w[i], apply(f"K{s}", suffix[i+1]))
            if option:
                g = add(apply("Q", f), neg(apply(f"L{t}", w[i])))
                selected[i] = add(g, apply(f"Q L{s} K{s}", suffix[i]), apply(f"Q R{s} Q", a[i]), neg(apply(f"Q L{s} K{s} C{s} Q", a[i])), neg(apply(f"R{t}", a[i])), neg(apply(f"L{t} K{s}", suffix[i+1])))
            else:
                selected[i] = add(apply("Q", f), apply(f"Q R{s} Q", a[i]), apply(f"Q L{s}", incoming[i]), neg(apply(f"R{t}", a[i])), neg(apply(f"L{t}", k)))
    recovered = []
    for i in range(m):
        y = add(incoming[i], incoming[i-1], neg(retired[i-1])) if i else add(incoming[0], neg(suffix[0]))
        b = selected[i] if i else add(selected[i], neg(a[0]))
        recovered.extend((a[i], add(suffix[i], suffix[i+1]), b, y))
    review.require(recovered == [review.input_value(j) for j in range(4*m)], "Complete content inverse")


def actual_five_minor():
    path = HERE.parent/"new-core-transfer-20261017/INTERFACE.json"
    pins = json.loads((HERE/"INPUTS.json").read_text())
    review.require(sha256(path.read_bytes()).hexdigest() == pins[str(path.relative_to(HERE.parent))], "Frozen actual source matrix")
    source = json.loads(path.read_text())
    r = [[int(row.get(str(j), "0")) for j in range(112)] for row in source["R"]]
    selected = [0,7,20,27,36,46,57,111,21,37,47,76,81,87,92,110,1,6,22,28,33,49,58,109,2,9,14,19,88,95,101,106,3,8,15,18,89,94,102,105]
    review.require(len(set(selected)) == 40, "Disjoint selected minors")
    for start in range(0, 40, 8):
        minor = selected[start:start+8]
        gram = [[sum(r[i][p]*r[j][p] for p in minor) for j in range(8)] for i in range(8)]
        review.require(gram == [[4*int(i==j) for j in range(8)] for i in range(8)], "Each selected minor Gram equals 4 I")
    ordinary = [j for j in range(112) if j not in selected]
    gram = [[sum(r[i][p]*r[j][p] for p in ordinary) for j in range(8)] for i in range(8)]
    review.require(gram == [[36*int(i==j) for j in range(8)] for i in range(8)], "Actual ordinary Gram equals 36 I")
    matrix = [[sum(r[k][i]*r[k][j] for k in range(8)) for j in ordinary] for i in ordinary]
    h = [[4*int(i==j)-matrix[i][j] for j in range(72)] for i in range(72)]
    inverse = [[32*int(i==j)-matrix[i][j] for j in range(72)] for i in range(72)]
    identity = [[128*int(i==j) for j in range(72)] for i in range(72)]
    review.require(review.matrix_multiply(h, inverse) == identity, "Actual H times inverse")
    review.require(review.matrix_multiply(inverse, h) == identity, "Actual inverse times H")
    return {"source": str(path.relative_to(HERE.parent)), "sha256": sha256(path.read_bytes()).hexdigest(), "selected_count": 40, "ordinary_count": 72, "gram": "36 I", "both_inverse_orders": True}


def main():
    cases = []
    for family in ("raw", "weighted"):
        for option in (False, True):
            for m in range(1, 9):
                decode(m, family, option)
                cases.append([family, option, m])
    result = {
        "status": "PASS_CONTENT_DECODER_REDUCTIONS_ONLY",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "review_engine_sha256": sha256((HERE/"check_review.py").read_bytes()).hexdigest(),
        "cases": cases,
        "actual_five_minor": actual_five_minor(),
        "scope": "Exact content inverse and query decomposition. No native access, storage schedule, or cost is supplied.",
    }
    (HERE/"DECODER-CHECKS.json").write_text(json.dumps(result, indent=2)+"\n")
    print(result["status"])


if __name__ == "__main__":
    main()
