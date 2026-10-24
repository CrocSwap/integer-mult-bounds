"""Check the weighted raw controller with formal ordered operators."""

from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ONE = {(): F(1)}


def need(value, label):
    if not value:
        raise ValueError(label)


def word_product(left, right):
    word = list(left + right)
    changed = True
    while changed:
        changed = False
        for i in range(len(word)-1):
            a, b = word[i:i+2]
            inverse = (a, b) in (("Q", "q"), ("q", "Q"))
            inverse |= a[0] in "HK" and b == ("K" if a[0] == "H" else "H") + a[1:]
            if inverse:
                del word[i:i+2]
                changed = True
                break
    return tuple(word)


def plus(a, b, scale=1):
    out = dict(a)
    for word, value in b.items():
        out[word] = out.get(word, F(0)) + scale*value
        if not out[word]:
            del out[word]
    return out


def product(a, b):
    out = {}
    for left, x in a.items():
        for right, y in b.items():
            out = plus(out, {word_product(left, right): x*y})
    return out


def operator(*names):
    out = ONE
    for name in names:
        out = product(out, {(name,): F(1)})
    return out


def row_add(a, b, scale=1):
    return [plus(x, y, scale) for x, y in zip(a, b)]


def row_map(op, row):
    return [product(op, value) for value in row]


def basis(n, j):
    return [ONE if i == j else {} for i in range(n)]


def zero(n):
    return [{} for _ in range(n)]


def replay(m, upper, mutation=None):
    n = 4*m
    state = [basis(n, j) for j in range(n)]
    for i in range(m-2, -1, -1):
        state[4*i+1] = row_add(state[4*i+1], state[4*i+5], -1)
    state[2], state[3] = row_add(state[2], state[0]), row_add(state[3], state[1])
    cuts = []
    for i in range(m):
        j, s, t = 4*i, 2*i+1, 2*i+2
        a, u, b, v = state[j:j+4]
        d = row_map(operator("Q"), a)
        h = row_add(row_add(row_map(operator("q"), b), row_map(operator(f"R{s}"), d), -1), row_map(operator(f"L{s}"), v), -1)
        w = row_map(operator(f"K{s}"), row_add(row_add(u, row_map(operator(f"C{s}"), d), -1), row_map(operator(f"H{s}"), v), -1))
        if upper:
            h = row_add(h, row_map(operator(f"L{s}"), w), -1)
        state[j:j+4] = [h, w, d, v]
        if i+1 < m:
            state[j+5] = row_map(operator(f"K{s}"), state[j+5])
            state[j+1] = row_add(state[j+1], state[j+5])
            state[j+7] = row_add(state[j+7], state[j+3], -1)
        cuts.append({"active_X_U": state[j+1], "input_Y_U": state[j+3]})
        state[j+3] = row_map(operator(f"H{t}"), state[j+3])
        h, k, d, v = state[j:j+4]
        h = row_add(h, row_map(operator("q", f"R{t}", "q"), d))
        h = row_add(h, row_map(operator("q", f"L{t}"), k))
        v = row_add(row_add(v, row_map(operator(f"C{t}", "q"), d)), row_map(operator(f"H{t}"), k))
        if mutation == "omit_selected_self_term":
            h = row_add(h, row_map(operator("q", f"R{t}", "q"), d), -1)
        state[j:j+4] = [h, k, d, v]
        if i+1 < m:
            if mutation == "early_idle_reset":
                state[j+5] = row_map(operator(f"H{s}"), state[j+5])
            state[j+1] = row_add(state[j+1], state[j+5], -1)
            state[j+7] = row_add(state[j+7], state[j+3])
            if mutation != "early_idle_reset":
                state[j+5] = row_map(operator(f"H{s}"), state[j+5])
    for i in range(m-1, 0, -1):
        state[4*i+1] = row_add(state[4*i+1], state[4*i-3])
    return state, cuts


def formulas(m, upper):
    n = 4*m
    original = [basis(n, j) for j in range(n)]
    z = [zero(n) for _ in range(m+1)]
    for i in range(m-1, -1, -1):
        z[i] = row_add(original[4*i+1], z[i+1], -1)
    eta = row_add(original[3], z[0])
    out, cuts, ws = [], [], []
    rprev, cprev = zero(n), zero(n)
    for i in range(m):
        j, s, t = 4*i, 2*i+1, 2*i+2
        a, x = original[j:j+2]
        b = row_add(original[j+2], a) if not i else original[j+2]
        ca = row_map(operator(f"K{s}", f"C{s}", "Q"), a)
        w = row_add(row_add(row_map(operator(f"K{s}"), z[i]), eta, -1), ca, -1)
        k = row_add(w, row_map(operator(f"K{s}"), z[i+1]))
        retired = row_add(row_map(operator(f"H{t}", f"K{s}"), x), row_map(operator(f"C{t}"), a))
        retired = row_add(retired, row_map(operator(f"H{t}"), ca), -1)
        if upper:
            h = row_add(row_map(operator("q"), b), row_map(operator(f"L{s}", f"K{s}"), z[i]), -1)
            h = row_add(h, row_map(operator(f"R{s}", "Q"), a), -1)
            h = row_add(h, row_map(operator(f"L{s}"), ca))
        else:
            h = row_add(row_map(operator("q"), b), row_map(operator(f"R{s}", "Q"), a), -1)
            h = row_add(h, row_map(operator(f"L{s}"), eta), -1)
        h = row_add(row_add(h, row_map(operator("q", f"R{t}"), a)), row_map(operator("q", f"L{t}"), k))
        completed = row_add(row_map(operator(f"K{s}"), z[i]), original[j+3], -1)
        completed = row_add(completed, ca, -1)
        if i:
            completed = row_add(completed, row_map(operator(f"K{s-2}"), z[i-1]))
            completed = row_add(row_add(completed, cprev, -1), rprev, -1)
        else:
            completed = row_add(completed, z[0], -1)
        out += [h, completed, row_map(operator("Q"), a), retired]
        cuts.append({"active_X_U": k, "input_Y_U": eta})
        ws.append(w)
        if i+1 < m:
            eta = row_add(row_add(original[j+7], eta, -1), retired)
        rprev, cprev = retired, ca
    return out, cuts, ws, z


def selected_normalization(m, endpoint, ws, z):
    n = 4*m
    for i in range(m):
        j, s, t = 4*i, 2*i+1, 2*i+2
        actual = row_add(row_map(operator("Q"), endpoint[j]), row_map(operator(f"L{t}"), ws[i]), -1)
        a = basis(n, j)
        b = row_add(basis(n, j+2), a) if not i else basis(n, j+2)
        expected = row_add(b, row_map(operator("Q", f"L{s}", f"K{s}"), z[i]), -1)
        expected = row_add(expected, row_map(operator("Q", f"R{s}", "Q"), a), -1)
        expected = row_add(expected, row_map(operator("Q", f"L{s}", f"K{s}", f"C{s}", "Q"), a))
        expected = row_add(expected, row_map(operator(f"R{t}"), a))
        expected = row_add(expected, row_map(operator(f"L{t}", f"K{s}"), z[i+1]))
        need(actual == expected, "Selected normalization and pure input response")


def main():
    tests = []
    for upper in (False, True):
        for m in range(1, 7):
            actual, cuts = replay(m, upper)
            expected, expected_cuts, ws, z = formulas(m, upper)
            need(actual == expected, "Every weighted endpoint operator block")
            need(cuts == expected_cuts, "Every weighted active cut")
            if upper:
                selected_normalization(m, actual, ws, z)
            need(replay(m, upper, "omit_selected_self_term")[0] != actual, "Selected self-block control")
            if m > 1:
                need(replay(m, upper, "early_idle_reset")[0] != actual, "Early idle reset control")
            tests.append({"pairs": m, "B_postupper": upper, "endpoint_blocks": (4*m)**2, "active_cuts": 2*m})
    result = {
        "status": "PASS_WEIGHTED_RAW_CONTROLLER",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "proof_sha256": sha256((HERE / "WEIGHTED-RAW-CONTROLLER.md").read_bytes()).hexdigest(),
        "tests": tests,
        "relations": ["Q q = q Q = I", "H_j K_j = K_j H_j = I"],
        "method": "Formal ordered words. Direct event replay and an independent endpoint recurrence. No producer imports or scalar specialization.",
        "controls": ["Omitted selected self-block term in F", "Early idle-X reset"],
        "scope": "Ordered algebra. Native local replay, idle-X access, inter-call views, and a full paid decoder are separate obligations."
    }
    (HERE / "WEIGHTED-RAW-CHECKS.json").write_text(json.dumps(result, indent=2) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
