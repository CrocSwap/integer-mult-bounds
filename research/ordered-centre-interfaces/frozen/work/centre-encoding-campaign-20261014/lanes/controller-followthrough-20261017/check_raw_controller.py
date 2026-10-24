"""Check the raw selected controller in an ordered operator algebra."""

from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def need(value, label):
    if not value:
        raise ValueError(label)


def word_product(left, right):
    word, factor = list(left + right), F(1)
    changed = True
    while changed:
        changed = False
        for i in range(len(word) - 1):
            a, b = word[i:i+2]
            if (a, b) in (("Q", "q"), ("q", "Q")):
                del word[i:i+2]
                changed = True
                break
            if a.startswith("B") and b == "D" + a[1:]:
                del word[i:i+2]
                factor *= 13
                changed = True
                break
    return tuple(word), factor


def plus(a, b, scale=1):
    out = dict(a)
    for word, coefficient in b.items():
        out[word] = out.get(word, F(0)) + scale * coefficient
        if not out[word]:
            del out[word]
    return out


def product(a, b):
    out = {}
    for left, x in a.items():
        for right, y in b.items():
            word, factor = word_product(left, right)
            out = plus(out, {word: factor * x * y})
    return out


ONE = {(): F(1)}


def op(name):
    return {(name,): F(1)}


def row_add(a, b, scale=1):
    return [plus(x, y, scale) for x, y in zip(a, b)]


def row_map(operator, row):
    return [product(operator, x) for x in row]


def basis(n, j):
    return [ONE if i == j else {} for i in range(n)]


def zero(n):
    return [{} for _ in range(n)]


def local_b(a, u, b, v, s, lower=1):
    r, c = row_map(op("q"), b), row_map(op("Q"), a)
    h = row_add(r, row_map(op(f"B{s}"), v))
    k = row_add(u, v, -1)
    k = row_add(k, row_map(product(op(f"D{s}"), op(f"B{s}")), v), 1-lower)
    k = row_add(k, row_map(op(f"D{s}"), r), -lower)
    k = row_add(k, row_map(op(f"D{s}"), c))
    return h, k, c, v


def local_f(a, u, b, v, t, corrected):
    query = row_map(op(f"B{t}"), u)
    h = row_add(a, row_map(op("q"), query), -1)
    r = row_add(row_add(v, u), row_map(op(f"D{t}"), query), -1)
    if not corrected:
        r = row_add(r, row_map(product(op(f"D{t}"), op("q")), b), -1)
    return h, u, b, r


def replay(m, corrected, mutation=None):
    n = 4*m
    state = [basis(n, j) for j in range(n)]
    for i in range(m-2, -1, -1):
        state[4*i+1] = row_add(state[4*i+1], state[4*i+5], -1)
    state[2] = row_add(state[2], state[0])
    state[3] = row_add(state[3], state[1])
    cuts = []
    for i in range(m):
        j, s, t = 4*i, 2*i+1, 2*i+2
        state[j:j+4] = local_b(*state[j:j+4], s)
        if i+1 < m:
            state[j+1] = row_add(state[j+1], state[j+5])
            state[j+7] = row_add(state[j+7], state[j+3], -1)
        cuts.append({"active_X_U": state[j+1], "input_Y_U": state[j+3]})
        state[j:j+4] = local_f(*state[j:j+4], t, corrected)
        if mutation == "omit_selected_X_query":
            state[j] = row_add(state[j], row_map(product(op("q"), op(f"B{t}")), state[j+1]))
        if i+1 < m:
            state[j+1] = row_add(state[j+1], state[j+5], -1)
            state[j+7] = row_add(state[j+7], state[j+3])
    tail = range(1, m) if mutation == "ascending_tail" else range(m-1, 0, -1)
    for i in tail:
        state[4*i+1] = row_add(state[4*i+1], state[4*i-3])
    return state, cuts


def formulas(m, corrected):
    n = 4*m
    original = [basis(n, j) for j in range(n)]
    z = [zero(n) for _ in range(m+1)]
    for i in range(m-1, -1, -1):
        z[i] = row_add(original[4*i+1], z[i+1], -1)
    v = row_add(original[3], z[0])
    previous_response, previous_k, previous_a = zero(n), zero(n), zero(n)
    out, cuts = [], []
    for i in range(m):
        j, s, t = 4*i, 2*i+1, 2*i+2
        a = original[j]
        b = row_add(original[j+2], a) if not i else original[j+2]
        c = row_add(row_map(op("Q"), a), row_map(op("q"), b), -1)
        w = row_add(row_add(z[i], v, -1), row_map(op(f"D{s}"), c))
        k = row_add(w, z[i+1])
        query = row_map(op(f"B{t}"), k)
        selected = row_add(row_add(row_map(op(f"B{s}"), v), row_map(op("q"), b)), row_map(op("q"), query), -1)
        response = query if corrected else row_add(query, a)
        retired = row_add(row_add(v, k), row_map(op(f"D{t}"), response), -1)
        completed = row_add(row_map(op(f"D{s}"), c), original[j+3], -1)
        if i:
            completed = row_add(completed, row_map(op(f"D{s-1}"), previous_response))
        out += [selected, completed, row_map(op("Q"), a), retired]
        cuts.append({"active_X_U": k, "input_Y_U": v})
        if i+1 < m:
            v = row_add(row_add(original[j+7], v, -1), retired)
        previous_response, previous_k, previous_a = response, k, a
    return out, cuts


def local_inverse_checks():
    rows = [basis(4, j) for j in range(4)]
    for lower in (0, 1, F(1, 2), -1):
        h, k, c, v = local_b(*rows, 1, lower)
        r = row_add(h, row_map(op("B1"), v), -1)
        u = row_add(k, v)
        u = row_add(u, row_map(product(op("D1"), op("B1")), v), lower-1)
        u = row_add(u, row_map(op("D1"), r), lower)
        u = row_add(u, row_map(op("D1"), c), -1)
        need([row_map(op("q"), c), u, row_map(op("Q"), r), v] == rows, "Backward inverse")
    for corrected in (False, True):
        h, u, b, r = local_f(*rows, 2, corrected)
        a = row_add(h, row_map(product(op("q"), op("B2")), u))
        v = row_add(row_add(r, u, -1), row_map(product(op("D2"), op("B2")), u))
        if not corrected:
            v = row_add(v, row_map(product(op("D2"), op("q")), b))
        need([a, u, b, v] == rows, "Forward inverse")


def borrowed_normal_form(m, corrected):
    n = 4*m
    endpoint = replay(m, corrected)[0]
    restricted = [[block if j % 4 >= 2 else {} for j, block in enumerate(row)] for row in endpoint]
    w = [restricted[4*i+1] for i in range(m)]
    for i in range(1, m):
        w[i] = row_add(w[i], w[i-1], -1)
    h = [row_add(restricted[4*i], row_map(product(op("q"), op(f"B{2*i+2}")), w[i])) for i in range(m)]
    for i in range(m):
        s = 2*i+1
        ordinary, selected = w[i], h[i]
        if i:
            previous = row_add(w[i-1], row_map(product(op(f"D{s-1}"), op(f"B{s-1}")), w[i-1]), -1)
            ordinary = row_add(ordinary, previous)
            selected = row_add(selected, row_map(op(f"B{s}"), previous), -1)
        b, y = basis(n, 4*i+2), basis(n, 4*i+3)
        expected_selected = row_add(row_map(op("q"), b), row_map(op(f"B{s}"), y))
        expected_ordinary = row_add(row_map(product(op(f"D{s}"), op("q")), b), y)
        expected_ordinary = row_map({(): F(-1)}, expected_ordinary)
        need(selected == expected_selected and ordinary == expected_ordinary, "Borrowed-state block diagonal form")


def main():
    local_inverse_checks()
    tests = []
    for corrected in (False, True):
        for m in range(1, 7):
            actual, cuts = replay(m, corrected)
            expected, expected_cuts = formulas(m, corrected)
            need(actual == expected, "Every endpoint operator block")
            need(cuts == expected_cuts, "Every active ordinary cut")
            borrowed_normal_form(m, corrected)
            need(replay(m, corrected, "omit_selected_X_query")[0] != actual, "Missing selected query control")
            if m > 2:
                need(replay(m, corrected, "ascending_tail")[0] != actual, "Wrong tail order control")
            tests.append({"pairs": m, "forward": "corrected" if corrected else "raw", "endpoint_blocks": (4*m)**2, "active_cuts": 2*m})
    sources = [HERE / "RAW-ORDINARY-CONTROLLER.md", HERE.parent / "native-escape-20261017/ZERO-LINE-BACKWARD.md", HERE.parent / "native-escape-20261017/RAW-SELECTED-FORWARD.md"]
    result = {
        "status": "PASS_RAW_ORDINARY_CONTROLLER",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_pins": {str(p.relative_to(HERE.parent)): sha256(p.read_bytes()).hexdigest() for p in sources},
        "tests": tests,
        "local_inverse_cases": 6,
        "borrowed_normal_form_cases": 12,
        "relations": ["Q q = q Q = I", "B_s D_s = 13 I"],
        "method": "Formal ordered operator words. Direct event replay and a separate endpoint recurrence. No scalar specialization and no producer imports.",
        "controls": ["Omitted selected X query", "Ascending final X tail"],
        "scope": "Content algebra only. This does not prove native inter-call views or a paid physical decoder."
    }
    (HERE / "RAW-CONTROLLER-CHECKS.json").write_text(json.dumps(result, indent=2) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
