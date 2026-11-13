"""Exact new gauge/Max Cut reduction. Produced by Nick Petalas; Apache-2.0."""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def graph(n, edges):
    need(type(n) is int and 1 <= n <= 4, "vertex bound")
    need(type(edges) is tuple and len(edges) <= 6, "edge bound")
    for edge in edges:
        need(type(edge) is tuple and len(edge) == 2, "edge shape")
        i, j = edge
        need(type(i) is int and type(j) is int and 0 <= i < j < n, "edge endpoints")
    need(tuple(sorted(set(edges))) == edges, "simple ordered edges")
    delta = max(sum(i in edge for edge in edges) for i in range(n))
    return 2 * delta + 1, delta


def gauges(n, k):
    need(type(k) is tuple and len(k) == n, "gauge shape")
    need(all(type(x) is int and abs(x) <= 1024 for x in k), "gauge bound")


def f(z):
    return abs(z) - int(z == 0)


def unary(a, x):
    return 2 * abs(x) + a * f(x) + (a + 1) * f(x - 1)


def pair(d):
    return f(1 + d) + f(1 - d)


def objective(n, edges, k):
    a, _ = graph(n, edges)
    gauges(n, k)
    return sum(unary(a, x) for x in k) + sum(pair(k[i] - k[j]) for i, j in edges)


def word(n, edges):
    a, _ = graph(n, edges)
    result = []
    for i in range(n):
        result.extend([(i, n, 0)] * a)
        result.extend([(i, n, -1)] * (a + 1))
    for i, j in edges:
        result.extend(((i, j, 1), (j, i, 1)))
    need(len(result) <= 72, "word capacity")
    return tuple(result)


def invoice(events, k):
    g = k + (0,)
    return 2 * sum(abs(x) for x in k) + sum(3 + f(e + g[t] - g[s]) for t, s, e in events)


def primitives(events, k, wrong_ratio=False, omit_exit=False):
    g = k + (0,)
    work = len(g)
    result = []
    for i, x in enumerate(k):
        result.extend([("double" if x > 0 else "halve", i)] * abs(x))
    for t, s, e in events:
        z = e + (g[s] - g[t] if wrong_ratio else g[t] - g[s])
        if z:
            result.append(("copy", work, s))
            result.extend([("double" if z > 0 else "halve", work)] * abs(z))
            result.append(("add", t, work))
        else:
            result.append(("add", t, s))
        result.append(("clear", work))
    if not omit_exit:
        for i, x in enumerate(k):
            result.extend([("halve" if x > 0 else "double", i)] * abs(x))
    need(len(result) <= 1024, "primitive capacity")
    return tuple(result)


def execute(ops, initial):
    state = list(map(Fraction, initial))
    for op in ops:
        tag, t = op[:2]
        if tag == "copy":
            state[t] = state[op[2]]
        elif tag == "clear":
            state[t] = Fraction(0)
        elif tag == "add":
            state[t] += state[op[2]]
        elif tag == "double":
            state[t] *= 2
        elif tag == "halve":
            state[t] /= 2
        else:
            raise ValueError("unknown primitive")
    return tuple(state)


def exact_endpoint(events, initial):
    state = list(map(Fraction, initial))
    for t, s, e in events:
        state[t] += Fraction(2) ** e * state[s]
    state[-1] = Fraction(0)
    return tuple(state)


def graph_cases(max_n):
    need(1 <= max_n <= 4, "census bound")
    for n in range(1, max_n + 1):
        possible = tuple(combinations(range(n), 2))
        for mask in range(1 << len(possible)):
            yield n, tuple(e for j, e in enumerate(possible) if (mask >> j) & 1)


def algebra_checks():
    counts = {"graphs": 0, "binary_assignments": 0, "integer_assignments": 0, "thresholds": 0}
    complete_minima = {}
    for n, edges in graph_cases(4):
        counts["graphs"] += 1
        a, delta = graph(n, edges)
        events = word(n, edges)
        base = n * (6 * a + 4) + 8 * len(edges)
        cuts = [sum(k[i] != k[j] for i, j in edges) for k in product(range(2), repeat=n)]
        best = max(cuts)
        binary_min = min(invoice(events, k) for k in product(range(2), repeat=n))
        need(binary_min == base - best, "exact Max Cut minimum")
        for k, cut in zip(product(range(2), repeat=n), cuts):
            need(invoice(events, k) == base - cut, "literal binary tariff")
            counts["binary_assignments"] += 1
        for k in product(range(-2, 4), repeat=n):
            clipped = tuple(min(1, max(0, x)) for x in k)
            distance = sum(abs(x - y) for x, y in zip(k, clipped))
            value = objective(n, edges, k)
            need(invoice(events, k) == 3 * len(events) + value, "full invoice decomposition")
            need(value >= objective(n, edges, clipped) + (delta + 5) * distance, "quantitative clipping")
            need(invoice(events, k) >= binary_min, "integer optimum floor")
            counts["integer_assignments"] += 1
        for threshold in range(-1, len(edges) + 2):
            need((best >= threshold) == (binary_min <= base - threshold), "decision equivalence")
            counts["thresholds"] += 1
        if len(edges) == n * (n - 1) // 2:
            complete_minima[str(n)] = binary_min
    counts["complete_graph_minima"] = complete_minima
    return counts


def endpoint_checks():
    counts = {"gauge_words": 0, "dirty_endpoints": 0, "executed_primitives": 0}
    for n, edges in graph_cases(3):
        events = word(n, edges)
        for k in product(range(-1, 3), repeat=n):
            ops = primitives(events, k)
            need(len(ops) == invoice(events, k), "literal macro bill")
            counts["gauge_words"] += 1
            fixtures = [tuple(int(j == i) for j in range(n + 2)) for i in range(n + 2)]
            fixtures.extend(tuple(Fraction((i + 1) * sign, i + 2) for i in range(n + 2)) for sign in (-1, 1))
            for initial in fixtures:
                need(execute(ops, initial) == exact_endpoint(events, initial), "complete dirty endpoint")
                counts["dirty_endpoints"] += 1
                counts["executed_primitives"] += len(ops)
    return counts


def control_checks():
    events = word(2, ((0, 1),))
    k = (1, 0)
    initial = (Fraction(2), Fraction(-3), Fraction(5), Fraction(7))
    expected = exact_endpoint(events, initial)
    need(execute(primitives(events, k, wrong_ratio=True), initial) != expected, "wrong-ratio control")
    need(execute(primitives(events, k, omit_exit=True), initial) != expected, "missing-exit control")
    need(execute(primitives(events, k)[:-1], initial) != expected, "truncated-word control")
    need(invoice(events, k) - 2 * sum(map(abs, k)) != invoice(events, k), "boundary-price control")
    need(sum(3 + abs(e) for _, _, e in events) != invoice(events, (0, 0)), "unit-discount control")
    triangle = ((0, 1), (0, 2), (1, 2))
    need(max(sum(x[i] != x[j] for i, j in triangle) for x in product(range(2), repeat=3)) == 2, "frustrated triangle")
    rejections = 0
    for n, edges in ((0, ()), (5, ()), (2, ((0, 0),)), (2, ((1, 0),)), (2, ((0, 2),)), (2, ((0, 1), (0, 1))), (2, [[0, 1]]), (True, ())):
        try:
            graph(n, edges)
        except ValueError:
            rejections += 1
        else:
            raise ValueError("invalid graph accepted")
    need(rejections == 8, "all invalid controls rejected")
    return {"semantic_controls": 6, "invalid_graph_rejections": rejections}


def local_lemmas():
    count = 0
    for d in range(-128, 129):
        need(pair(d) == (2 if d == 0 else 1 if abs(d) == 1 else 2 * abs(d)), "pair formula")
        need(abs(pair(d + 1) - pair(d)) <= 3, "pair Lipschitz")
        for a in range(1, 8):
            clipped = min(1, max(0, d))
            need(unary(a, clipped) == 1, "binary unary value")
            need(unary(a, d) - 1 >= (2 * a + 3) * abs(d - clipped), "unary clipping")
            count += 1
    return count


def source_hashes():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    hashes = {}
    for pin in pins["files"]:
        if pin["usage"] == "input":
            path = HERE.parents[1] / pin["path"]
            raw = path.read_bytes()
            need(len(raw) <= 32768, "source capacity")
            digest = sha256(raw).hexdigest()
            need(digest == pin["sha256"], "source authentication")
            hashes[pin["path"]] = digest
    for name in FILES:
        raw = (HERE / name).read_bytes()
        need(len(raw) <= 65536, "package file capacity")
        hashes[name] = sha256(raw).hexdigest()
    return hashes


def main():
    hashes = source_hashes()
    result = {"status": "PASS_INTEGER_GAUGE_MAXCUT", "files_sha256": hashes}
    result["local_lemma_cases"] = local_lemmas()
    result["algebra"] = algebra_checks()
    result["endpoints"] = endpoint_checks()
    result["controls"] = control_checks()
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
