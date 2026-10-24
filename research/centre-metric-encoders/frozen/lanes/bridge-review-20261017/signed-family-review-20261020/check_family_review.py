"""Check the general scalar word and the diagonal-metric classification."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
ROOT = LANES.parent / "root"
PREVIOUS = HERE.parent / "signed-metric-review-20261020"
MODEL = LANES / "oblique-native-20261017/signed-metric-reciprocal-20261020"
PINS = {
    "SIGNED-METRIC-DYADIC-FAMILY-20261020.md": "c19042d37e37921de9a67fbdaf262305811190f7e886f199b89a09f2c044667a",
    "check_signed_metric_family.py": "9daacf3e3f5683477235824a18afb92b09aad42c5ac297862aa1d2c7c5dea9fa",
    "signed-metric-family-normal.json": "3a4e4e27835be8431a68051e9c58a64cb22ec53e89beaac6f58fba4a945a0d37",
    "signed-metric-family-optimized.json": "3a4e4e27835be8431a68051e9c58a64cb22ec53e89beaac6f58fba4a945a0d37",
}
PRIOR_PIN = "b44b5a95c1fa8372bbd979f360fde743df10c16bd07ac4d5015c048982539762"
FAMILY_PIN = "a6088c38e984e7c4f15fb462d0cb89ac2c73cb2b6bbba0501513c236b32107b1"


def need(test, reason):
    if not test:
        raise ValueError(reason)


def freeze(path, pin):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == pin, "Freeze pin")
    for name, value in json.loads(raw)["files"].items():
        need(sha256((path.parent / name).read_bytes()).hexdigest() == value, "Frozen file")


freeze(PREVIOUS / "FREEZE.json", PRIOR_PIN)
spec = importlib.util.spec_from_file_location("own_signed_review", PREVIOUS / "check_review.py")
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
r = old.r


def replay(word, n):
    rows = r.eye(n)
    cost, height, peak = 0, 0, F(1)
    for op, target, source, value in word:
        if op == "add":
            for j, c in rows[source].items():
                r.put(rows[target], j, value * c)
            a, b = abs(value.numerator), value.denominator
            cost += 2 * (1 + a.bit_length() + a.bit_count() + b.bit_length())
        else:
            need(op == "scale", "Scalar grammar")
            rows[target] = {j: value * c for j, c in rows[target].items()}
            cost += 2 * (abs(old.dyadic_exponent(value)) + (value < 0))
        peak = max(peak, sum(map(abs, rows[target].values())))
        for c in rows[target].values():
            d = c.denominator
            need(d & (d - 1) == 0, "Odd prefix denominator")
            height = max(height, d.bit_length() - 1)
    return rows, dict(cost=cost, height=height, peak=str(peak), instructions=len(word))


def build_word(k):
    gates = []
    def h(a, b):
        gates.extend((("add", a, b, F(1)), ("scale", b, None, F(-2)),
                      ("add", b, a, F(1))))
    for bit in range(k.bit_length() - 1):
        mask = 1 << bit
        for left in range(k):
            if not left & mask:
                h(left, left | mask)
    h(k, k + 1)
    gates.extend((("add", 0, k + 2, F(-1)), ("add", k, 0, F(1)),
                  ("scale", k, None, F(-1)), ("add", k + 2, k, F(k, 2)),
                  ("add", k + 2, 0, F(k + 2, 4)), ("scale", k + 2, None, F(-1))))
    h(0, k + 2)
    return gates


def closed(k):
    n = k + 4
    a = [{} for _ in range(n)]
    for i in range(1, k):
        a[i] = {j: F(1 if (i & j).bit_count() % 2 == 0 else -1) for j in range(k)}
    s = {j: F(1) for j in range(k)}
    v = dict(s)
    r.put(v, k + 2, F(-1))
    w = {k: F(k, 2), k + 1: F(k, 2), k + 2: F(-1)}
    for j, value in v.items():
        r.put(w, j, F(k - 2, 4) * value)
    for j in set(v) | set(w):
        r.put(a[0], j, v.get(j, 0) + w.get(j, 0))
        r.put(a[k + 2], j, v.get(j, 0) - w.get(j, 0))
    a[k] = {j: F(-1) for j in range(k + 2)}
    a[k][k + 2] = F(1)
    a[k + 1] = {k: F(1), k + 1: F(-1)}
    a[-1] = {n - 1: F(1)}
    return a


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "normal.json")
    args = parser.parse_args()
    for name, pin in PINS.items():
        need(sha256((ROOT / name).read_bytes()).hexdigest() == pin, "Root source pin")
    freeze(MODEL / "FAMILY-FREEZE.json", FAMILY_PIN)
    samples = []
    for power in range(7):
        k, n = 2**power, 2**power + 4
        word = build_word(k)
        fw, fb = replay(word, n + 5)
        inverse = [(op, t, s, -c if op == "add" else 1 / c) for op, t, s, c in reversed(word)]
        bw, bb = replay(inverse, n + 5)
        c = closed(k)
        need(fw[:n] == c and fw[n:] == bw[n:] == r.eye(n + 5)[n:], "All arbitrary inputs")
        need(r.matmul(fw, bw) == r.matmul(bw, fw) == r.eye(n + 5), "Both inverse orders")
        g = old.diagonal([-2 * k] + [k] * (k - 1) + [2, 2, 2 * k, -k])
        metric = old.diagonal([1] * (k + 2) + [-k, -k])
        need(r.matmul(c, r.matmul(metric, old.transpose(c, n))) == g, "Signed Gram")
        _, determinant = r.invert(c)
        need(determinant**2 == 16 * k**k, "Determinant square")
        bill = 86 if power == 0 else 96 if power == 1 else 10 * k * power + 76 + 4 * power
        need(fb["cost"] == bb["cost"] == bill, "Closed exact price")
        need(fb["instructions"] == bb["instructions"] == 3 * k * power // 2 + 12, "Instruction count")
        need(F(fb["peak"]) <= 4 * (k + 1) * max(k, 2) and F(bb["peak"]) <= 2 * (k + 5),
             "General prefix norm bounds")
        need(fb["height"] <= 2 and bb["height"] <= max(power, 1) + 3, "General height bounds")
        need(replay(word[1:], n + 5)[0] != fw, "Deleted gate control")
        samples.append(dict(k=k, forward=fb, inverse=bb))
    metric_samples = []
    for n in range(5, 25):
        model = old.local_model(n)
        e = model["E"]
        equations = []
        for a in range(n):
            for b in range(a, n):
                eq = {i: e[i].get(a, 0) * e[i].get(b, 0) for i in range(n)}
                eq = {i: value for i, value in eq.items() if value}
                if a == b:
                    r.put(eq, a, F(-1))
                if eq:
                    equations.append(eq)
        need(old.rank(equations, n) == n - 1, "Exact diagonal-metric nullity one")
        need(old.rank(old.difference(e, r.eye(n)), n) == 2
             and old.rank(old.difference(e, model["P"]), n) == 1, "Both displacement ranks")
        need(all(not matrix[i].get(i) for matrix in (e, model["inverse_E"]) for i in range(n)),
             "Reciprocal zero diagonals")
        metric_samples.append(dict(n=n, diagonal_metric_dimension=1, identity_rank=2, P_rank=1))
    output = dict(
        status="PASS_SIGNED_FAMILY_WORD_AND_METRIC_CLASSIFICATION",
        checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        root_source_pins=PINS, family_freeze_sha256=FAMILY_PIN, prior_review_freeze_sha256=PRIOR_PIN,
        word_samples=samples, metric_samples=metric_samples,
        scope="Independent word/cost and family classification review. This lane supplied the underlying basis.",
        native_geometry_or_supplier_claim=False,
    )
    raw = (json.dumps(output, sort_keys=True, indent=2) + "\n").encode()
    args.output.write_bytes(raw)
    print(output["status"])
    print(sha256(raw).hexdigest())


if __name__ == "__main__":
    main()
