"""Independent free-module, commit-boundary and finite-state checks."""

from collections import Counter
from copy import deepcopy
from fractions import Fraction
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("capacity_schedule", HERE / "schedule.py")
SCHED = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCHED)
PINS = {
    "sources/PR889-README.md": "0ef1c0a7dd98c0270822e6f78d222a3888083794502b132543038827c783c706",
    "sources/PR889-NOTICE.md": "e0ea74eed5957ed62f6c3eb5dadd6f51fd61d6c5ba546d29fb96adf4dda50e4b",
    "sources/PR938-PROOF.md": "9df4f8c6c40627054f512608b3ff423b61d453209ca3741eca1caa450ccd7b2b",
    "sources/PR938-NOTICE.md": "a50dd4719c3481db0179f9983da4d7c10ef32fd1ac081e5417d86c5b0095c251",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def identity(rows):
    return [{((), i): 1} for i in range(rows)]


def step(state, item, allowed):
    name, source, target, sign = item
    need(name in allowed and type(sign) is int and sign in (-1, 1), "invalid primitive")
    need(type(source) is int and type(target) is int and
         0 <= source < len(state) and 0 <= target < len(state) and source != target,
         "invalid or aliased ports")
    for (chain, origin), coefficient in state[source].items():
        term = chain + (name,), origin
        value = state[target].get(term, 0) + sign * coefficient
        if value:
            state[target][term] = value
        else:
            state[target].pop(term, None)


def target_map(k, rows, factors):
    result = identity(rows)
    for i in range(k):
        result[i + 1][(tuple(factors["B"] + factors[f"A{i}"]), 0)] = 1
    return result


def root_leaves(word, k):
    result = []
    names = {"B", *(f"A{i}" for i in range(k))}
    for name, sign in word:
        need(name in names, "unknown query")
        src, dst = (0, k + 1) if name == "B" else (k + 1, int(name[1:]) + 1)
        result.append([name, src, dst, sign])
    return result


def replay(leaves, commits, k, rows, factors, capacity):
    need(type(capacity) is int and capacity > 0, "invalid capacity")
    need(len(commits) == k and all(type(t) is int and 0 <= t < len(leaves) for t in commits),
         "invalid commit table")
    initial, expected = identity(rows), target_map(k, rows, factors)
    state = deepcopy(initial)
    pending, finished, peak = set(), set(), 0
    allowed = set(itertools.chain.from_iterable(factors.values()))
    events = {}
    for i, t in enumerate(commits):
        events.setdefault(t, []).append(i)
    for t, item in enumerate(leaves):
        need(item[1] - 1 not in finished, "committed output read again")
        dst = item[2]
        need(dst != 0, "source mutated")
        if 1 <= dst <= k:
            i = dst - 1
            need(i not in finished, "committed output touched again")
            pending.add(i)
            peak = max(peak, len(pending))
            need(peak <= capacity, "unfinished-output capacity exceeded")
        step(state, item, allowed)
        for i in events.get(t, []):
            need(i in pending and state[i + 1] == expected[i + 1], "incorrect early commit")
            pending.remove(i)
            finished.add(i)
    need(state == expected and not pending and len(finished) == k, "wrong endpoint or restoration")
    for name, src, dst, sign in reversed(leaves):
        step(state, [name, src, dst, -sign], allowed)
    need(state == initial, "literal inverse failed")
    return peak


def root_check(plan, k, capacity):
    factors = {name: [name] for name in ["B", *(f"A{i}" for i in range(k))]}
    return replay(root_leaves(plan["word"], k), plan["commit_after"], k, k + 2, factors, capacity)


def child_boundary_check(plan, factors, k, rows):
    state = identity(rows)
    allowed = set(itertools.chain.from_iterable(factors.values()))
    offset, ends = 0, []
    for name, src, dst, sign in root_leaves(plan["word"], k):
        expected = deepcopy(state)
        for (chain, origin), coefficient in state[src].items():
            term = chain + tuple(factors[name]), origin
            value = expected[dst].get(term, 0) + sign * coefficient
            if value:
                expected[dst][term] = value
            else:
                expected[dst].pop(term, None)
        n = len(factors[name])
        power = 1 << (n.bit_length() - 1)
        size = power * (3 * n - 2 * power)
        permitted = {src, dst, *range(k + 2, rows)}
        for item in plan["leaves"][offset:offset + size]:
            need(item[1] in permitted and item[2] in permitted and item[2] != src,
                 "child uses a reserved port")
            step(state, item, allowed)
        need(state == expected, "child did not restore its complete boundary")
        offset += size
        ends.append(offset - 1)
    need(offset == len(plan["leaves"]), "unpaid child instructions")
    need(plan["leaf_commit_after"] == [ends[t] for t in plan["commit_after"]],
         "commit is not at a complete child return")
    return len(ends)


def minimum_search(k, capacity, limit):
    # Output-label symmetry preserves reachability, not labelled word counts.
    states = {(0, k, (), 0)}
    sizes = []
    for depth in range(limit + 1):
        sizes.append(len(states))
        if (0, 0, (), k) in states:
            return depth, sizes
        following = set()
        for q, unopened, active, done in states:
            for sign in (-1, 1):
                following.add((q + sign, unopened, active, done))
            for j, (a, b) in enumerate(active):
                for sign in (-1, 1):
                    aa, bb = a + sign, b + sign * q
                    changed = list(active)
                    changed[j] = aa, bb
                    following.add((q, unopened, tuple(sorted(changed)), done))
                    if (aa, bb) == (0, 1):
                        following.add((q, unopened, active[:j] + active[j + 1:], done + 1))
            if unopened and len(active) < capacity:
                for sign in (-1, 1):
                    following.add((q, unopened - 1, tuple(sorted(active + ((sign, sign * q),))), done))
        states = following
    return None, sizes


def dense_check(plan, factors, k, rows):
    names = sorted(itertools.chain.from_iterable(factors.values()))
    cases = 0
    for dimension in (1, 2, 3):
        matrices = {name: [[((j + 2) * (r + 1) + (j + 1) * (c + 2) + r * c) % 5 - 2
                            for c in range(dimension)] for r in range(dimension)]
                    for j, name in enumerate(names)}
        def apply(matrix, vector):
            return [sum(x * y for x, y in zip(row, vector)) for row in matrix]
        def product(labels, vector):
            for label in labels:
                vector = apply(matrices[label], vector)
            return vector
        inputs = []
        for j in range(rows * dimension):
            vector = [0] * (rows * dimension)
            vector[j] = 1
            inputs.append(vector)
        inputs.append([((j + 53) % 11) - 5 for j in range(rows * dimension)])
        for flat in inputs:
            initial = [flat[i * dimension:(i + 1) * dimension] for i in range(rows)]
            state, expected = deepcopy(initial), deepcopy(initial)
            for i in range(k):
                delta = product(factors["B"] + factors[f"A{i}"], initial[0])
                expected[i + 1] = [a + b for a, b in zip(initial[i + 1], delta)]
            for t, (name, src, dst, sign) in enumerate(plan["leaves"]):
                delta = apply(matrices[name], state[src])
                state[dst] = [a + sign * b for a, b in zip(state[dst], delta)]
                for i, when in enumerate(plan["leaf_commit_after"]):
                    if t == when:
                        need(state[i + 1] == expected[i + 1], "dense commit failed")
            need(state == expected, "dense endpoint failed")
            for name, src, dst, sign in reversed(plan["leaves"]):
                delta = apply(matrices[name], state[src])
                state[dst] = [a - sign * b for a, b in zip(state[dst], delta)]
            need(state == initial, "dense inverse failed")
            cases += 1
    return cases


def reject(call):
    try:
        call()
    except (ValueError, KeyError, IndexError):
        return 1
    raise ValueError("negative control was accepted")


def verify(data):
    need(data == SCHED.fixture(), "certificate differs from literal regeneration")
    k, cap, factors = data["outputs"], data["capacity"], data["factors"]
    need((k, cap) == (5, 2), "fixture scope changed")
    counts, peaks, dense, boundaries = {}, {}, 0, 0
    for name, plan in data["plans"].items():
        allowed_cap = 3 if name == "unrestricted" else 2
        rows = k + 1 + plan["dirty_rows"]
        need(plan["dirty_rows"] == 4, "unpaid scratch")
        root_check(plan, k, allowed_cap)
        boundaries += child_boundary_check(plan, factors, k, rows)
        peaks[name] = replay(plan["leaves"], plan["leaf_commit_after"], k, rows, factors, allowed_cap)
        counts[name] = len(plan["leaves"])
        dense += dense_check(plan, factors, k, rows)
    need(counts == {"bounded": 404, "unrestricted": 300, "separate": 716}, "wrong complete leaf prices")
    need(peaks == {"bounded": 2, "unrestricted": 3, "separate": 1}, "wrong peak pending count")
    family = 0
    for outputs in range(33):
        for capacity in range(1, max(2, outputs + 1)):
            plan = SCHED.schedule(outputs, capacity)
            root_check(plan, outputs, capacity)
            counts_by_name = Counter(name for name, sign in plan["word"])
            expected_b = 2 * ((outputs + 2 * capacity - 1) // (2 * capacity))
            need(counts_by_name["B"] == expected_b and
                 all(counts_by_name[f"A{i}"] == 2 for i in range(outputs)), "family multiplicity")
            prices = {name: Fraction(1 + ((j + 53) % 17), 1 + j % 5)
                      for j, name in enumerate(["B", *(f"A{i}" for i in range(outputs))])}
            actual = sum(prices[name] for name, sign in plan["word"])
            target = expected_b * prices["B"] + 2 * sum(v for name, v in prices.items() if name != "B")
            need(actual == target, "weighted bill mismatch")
            family += 1
    minima = {}
    for outputs, capacity, bound in [(1, 1, 4), (2, 1, 6), (2, 2, 6), (3, 1, 10), (3, 2, 8)]:
        actual, sizes = minimum_search(outputs, capacity, bound)
        need(actual == bound, "independent finite minimum differs")
        minima[f"{outputs},{capacity}"] = {"minimum": actual, "states_by_depth": sizes}
    controls = 0
    for outputs, capacity in [(True, 1), (-1, 1), (1, 0), (1, True), (1, Fraction(1))]:
        controls += reject(lambda o=outputs, c=capacity: SCHED.schedule(o, c))
    bounded = data["plans"]["bounded"]
    controls += reject(lambda: root_check(data["plans"]["unrestricted"], k, cap))
    bad = deepcopy(bounded)
    bad["commit_after"][0] = 0
    controls += reject(lambda: root_check(bad, k, cap))
    bad = deepcopy(bounded)
    bad["word"] = bad["word"][:-1]
    controls += reject(lambda: root_check(bad, k, cap))
    bad = deepcopy(bounded)
    bad["word"][2][-1] *= -1
    controls += reject(lambda: root_check(bad, k, cap))
    for mode in ("omit", "factor", "alias", "commit"):
        bad = deepcopy(bounded)
        if mode == "omit":
            del bad["leaves"][-1]
        elif mode == "factor":
            bad["leaves"][0][0] = factors["B"][0]
        elif mode == "alias":
            bad["leaves"][0][1] = bad["leaves"][0][2]
        else:
            bad["leaf_commit_after"][0] = 0
        controls += reject(lambda: replay(bad["leaves"], bad["leaf_commit_after"], k, 10, factors, cap))
    bad = deepcopy(bounded)
    bad["leaves"][79], bad["leaves"][80] = bad["leaves"][80], bad["leaves"][79]
    replay(bad["leaves"], bad["leaf_commit_after"], k, 10, factors, cap)
    controls += reject(lambda: child_boundary_check(bad, factors, k, 10))
    need((3 + 1) ** 2 - 3 ** 2 == 7 and 7 != 1, "nonlinear boundary control")
    return {"status": "PASS_BOUNDED_PENDING_FANOUT", "family_cases": family,
            "leaf_calls": counts, "peak_pending": peaks, "dense_cases": dense,
            "controls_rejected": controls, "nonlinear_counterexamples": 1,
            "complete_child_boundaries": boundaries,
            "finite_minima": minima, "no_new_kappa": True}


def main():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    need({item["retained"]: item["sha256"] for item in manifest["files"]} == PINS, "source inventory differs")
    for item in manifest["files"]:
        payload = (HERE / item["retained"]).read_bytes()
        need(hashlib.sha256(payload).hexdigest() == item["sha256"], "source SHA256 differs")
        blob = b"blob " + str(len(payload)).encode() + b"\0" + payload
        need(hashlib.sha1(blob).hexdigest() == item["git_blob"], "source Git blob differs")
    result = verify(json.loads((HERE / "CERTIFICATE.json").read_text()))
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
