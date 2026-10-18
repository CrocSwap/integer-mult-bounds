"""Forward error columns; no reverse-row engine or recurrence implementation import."""
from collections import Counter
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def forward_word(height, sign=1, x=0, y=1, depth=2, offset=0):
    if height == 0:
        return [(x, y, offset, sign)]
    half = 2 ** (height - 1)
    u = forward_word(height - 1, 1, x, depth, depth + 1, offset)
    v = forward_word(height - 1, 1, depth, y, depth + 1, offset + half)
    inverse = lambda word: [(a, b, f, -s) for a, b, f, s in reversed(word)]
    result = u + v + inverse(u) + inverse(v)
    return result if sign == 1 else inverse(result)


def step(state, event):
    x, y, factor, sign = event
    for term, coefficient in list(state[x].items()):
        key = (factor,) + term
        value = state[y].get(key, 0) + sign * coefficient
        if value:
            state[y][key] = value
        else:
            state[y].pop(key, None)


def columns(word, count, registers):
    for start in range(count):
        state = [{} for _ in range(registers)]
        state[word[start][1]][()] = 1
        for event in word[start + 1:count]:
            step(state, event)
        yield state


def l1(poly):
    return sum(abs(value) for value in poly.values())


def counts(values):
    values = Counter(value for value in values if value)
    return [values[i] for i in range(max(values, default=0) + 1)]


def binomial(n, k):
    if not 0 <= k <= n:
        return 0
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


def exit_formula(h):
    # Closed coefficient sum obtained by unrolling G; no primary recurrence.
    result = [0] * (h + 2)
    result[1] = 4 ** h
    for k in range(h):
        for degree in range(k + 1):
            value = 4 ** (h - 1 - k) * binomial(k, degree) * 2 ** (k - degree)
            result[degree + 2] += value
            result[degree + 1] -= value
    return result


def main():
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    for item in sources["files"]:
        if item["usage"] != "input":
            continue
        need(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"], "independent source hash")
    receipt = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    exit_count = cut_count = 0
    for h in range(5):
        for sign in (1, -1):
            word = forward_word(h, sign)
            gs, hs = [], []
            for state in columns(word, len(word), h + 2):
                need(not state[0], "source pollution")
                need(all(len(poly) <= 1 and all(abs(c) == 1 for c in poly.values()) for poly in state), "exit monomial lemma")
                support = sum(bool(poly) for poly in state)
                gs.append(support)
                if state[1]:
                    hs.append(support)
                exit_count += 1
            need(counts(gs) == exit_formula(h), "closed G coefficients")
            need(counts(hs) == [0] + [binomial(h, i) * 2 ** (h - i) for i in range(h + 1)], "closed H coefficients")
        if h == 0:
            continue
        record = receipt["observations"][h - 1]
        specifications = [("A", 1, (4 ** h + 2) // 3),
                          ("B", -1, (2 * 4 ** h - 2) // 3)]
        if h >= 2:
            specifications.append(("Omega", 1, 3 * 4 ** (h - 1) + (2 * 4 ** (h - 1) - 2) // 3))
        for name, sign, count in specifications:
            word = forward_word(h, sign)
            masses = [l1(state[h + 1]) for state in columns(word, count, h + 2)]
            need(counts(masses) == record[name], "forward cut " + name + str(h))
            cut_count += count

    # Correlated injections cannot be silently substituted for independent symbols.
    h = 3
    word = forward_word(h)
    count = 3 * 4 ** (h - 1) + (2 * 4 ** (h - 1) - 2) // 3
    channels = [state[h + 1] for state in columns(word, count, h + 2)]
    pair = next((i, 3 * 4 ** (h - 1) - 1 - i)
                for i in range(4 ** (h - 1)) if channels[i])
    left, right = pair
    need(channels[left] == channels[right], "matched inverse channel identity")
    state = [{} for _ in range(h + 2)]
    for i, event in enumerate(word[:count]):
        step(state, event)
        injection = 1 if i == left else -1 if i == right else 0
        dst = state[event[1]]
        dst[()] = dst.get((), 0) + injection
        if not dst[()]:
            del dst[()]
    independent_mass = l1(channels[left]) + l1(channels[right])
    need(independent_mass > 0 and not state[h + 1], "opposite shared errors did not cancel")
    print(f"PASS_FORWARD_COLUMNS: {exit_count} complete exit columns, {cut_count} cut columns, opposite shared-error control ({left},{right}; independent mass {independent_mass})")


if __name__ == "__main__":
    main()
