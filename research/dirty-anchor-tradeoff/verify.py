#!/usr/bin/env python3
"""Exact affine checks for the dirty-output call/ADD tariff. Apache-2.0.

Ross Richardson, with substantial OpenAI Codex assistance.
No predecessor executable is imported. Integer masks represent independent
dirty inputs, common-product output, and private-product outputs over F2.
"""

import argparse
import hashlib
import heapq
import itertools
import json
from pathlib import Path


def require(ok, message):
    if not ok:
        raise ValueError(message)


def schedule(q, roots, private=False):
    require(type(q) is int and 1 <= q <= 112, "q outside checker domain")
    roots = tuple(roots)
    require(roots and len(set(roots)) == len(roots), "roots not distinct/nonempty")
    require(all(type(i) is int and 0 <= i < q for i in roots), "invalid root")
    nonroots = [i for i in range(q) if i not in roots]
    # Each extra root forms a singleton; all nonroots share the first root.
    root = roots[0]
    word = [("A", i, root) for i in nonroots]
    word += [("P", i, 0) for i in roots]
    word += [("A", i, root) for i in nonroots]
    if private:
        word += [("T", i, 0) for i in range(q)]
    return word


def execute(q, word, state=None):
    state = [1 << i for i in range(q)] if state is None else list(state)
    for kind, dst, src in word:
        require(0 <= dst < q, "invalid destination")
        if kind == "A":
            require(0 <= src < q and dst != src, "invalid ADD")
            state[dst] ^= state[src]
        elif kind == "P":
            state[dst] ^= 1 << q
        elif kind == "T":
            state[dst] ^= 1 << (q + 1 + dst)
        else:
            raise ValueError("unknown instruction")
    return state


def endpoint(q, word, private=False):
    want = [(1 << i) ^ (1 << q) ^ ((1 << (q + 1 + i)) if private else 0)
            for i in range(q)]
    return execute(q, word) == want


def weighted_formula(alpha, mu):
    require(len(alpha) == len(mu) and alpha, "tariff dimensions")
    require(all(type(x) is int and x > 0 for x in (*alpha, *mu)), "tariff domain")
    delta = [m - 2 * a for a, m in zip(alpha, mu)]
    roots = tuple(i for i, d in enumerate(delta) if d < 0)
    if not roots:
        roots = (min(range(len(delta)), key=delta.__getitem__),)
    cost = sum(mu[i] for i in roots) + 2 * sum(
        a for i, a in enumerate(alpha) if i not in roots)
    return cost, roots


def actual_cost(word, alpha, mu):
    require(all(k in ("A", "P") for k, _, _ in word), "private tariff is separate")
    return sum(alpha[d] if k == "A" else mu[d] for k, d, _ in word)


def mul_row(rows, dst, src):
    result = list(rows)
    result[dst] ^= result[src]
    return tuple(result)


def fixed_call_minima(q):
    """Exhaust full affine group with at most q P calls; ADD weight one.

    State: (dirt matrix rows, common coefficient mask, P-call count).
    Independent private terms are projected out, permitting interleaving.
    """
    ident = tuple(1 << i for i in range(q))
    start = (ident, 0, 0)
    distances = {start: 0}
    queue = [(0, start)]
    adds = tuple((i, j) for i in range(q) for j in range(q) if i != j)
    while queue:
        distance, state = heapq.heappop(queue)
        if distance != distances[state]:
            continue
        rows, mask, count = state
        successors = []
        for dst, src in adds:
            newmask = mask ^ (((mask >> src) & 1) << dst)
            successors.append(((mul_row(rows, dst, src), newmask, count), 1))
        if count < q:
            successors += [((rows, mask ^ (1 << i), count + 1), 0)
                           for i in range(q)]
        for newstate, price in successors:
            candidate = distance + price
            if candidate < distances.get(newstate, 10**9):
                distances[newstate] = candidate
                heapq.heappush(queue, (candidate, newstate))
    target = (1 << q) - 1
    return [distances.get((ident, target, r)) for r in range(1, q + 1)], len(distances)


def weighted_search(alpha, mu):
    """Unrestricted-multiplicity Dijkstra on the full finite affine group."""
    q = len(alpha)
    ident = tuple(1 << i for i in range(q))
    start = (ident, 0)
    goal = (ident, (1 << q) - 1)
    distances = {start: 0}
    queue = [(0, start)]
    while queue:
        distance, state = heapq.heappop(queue)
        if distance != distances[state]:
            continue
        if state == goal:
            return distance
        rows, mask = state
        successors = [((rows, mask ^ (1 << i)), mu[i]) for i in range(q)]
        for dst in range(q):
            for src in range(q):
                if dst != src:
                    newmask = mask ^ (((mask >> src) & 1) << dst)
                    successors.append(((mul_row(rows, dst, src), newmask), alpha[dst]))
        for newstate, price in successors:
            candidate = distance + price
            if candidate < distances.get(newstate, 10**9):
                distances[newstate] = candidate
                heapq.heappush(queue, (candidate, newstate))
    raise ValueError("unreachable endpoint")


def evaluate(q, word, bits):
    # Separate concrete oracle for exhaustive dirty states.
    rows = list(bits[:q])
    common = bits[q]
    for kind, dst, src in word:
        if kind == "A":
            rows[dst] ^= rows[src]
        elif kind == "P":
            rows[dst] ^= common
        else:
            rows[dst] ^= bits[q + 1 + dst]
    return rows


def checks():
    symbolic = 0
    digest = hashlib.sha256()
    for q in range(1, 113):
        for r in range(1, q + 1):
            word = schedule(q, range(r), private=True)
            require(endpoint(q, word, True), "symbolic endpoint")
            final = execute(q, word)
            require(execute(q, reversed(word), final) == [1 << i for i in range(q)],
                    "inverse endpoint")
            counts = [sum(k == kind for k, _, _ in word) for kind in ("A", "P", "T")]
            require(counts == [2 * (q - r), r, q], "literal invoice")
            digest.update(json.dumps([q, r, final, counts]).encode())
            symbolic += 1
    subsets = 0
    for q in range(1, 9):
        for mask in range(1, 1 << q):
            roots = [i for i in range(q) if mask >> i & 1]
            require(endpoint(q, schedule(q, roots, True), True), "root subset endpoint")
            subsets += 1
    concrete = 0
    for q in range(1, 6):
        for r in range(1, q + 1):
            word = schedule(q, range(r), True)
            for bits in itertools.product((0, 1), repeat=2 * q + 1):
                out = evaluate(q, word, bits)
                require(out == [bits[i] ^ bits[q] ^ bits[q + 1 + i] for i in range(q)],
                        "concrete arbitrary dirt")
                inverse_bits = tuple(out) + bits[q:]
                require(evaluate(q, list(reversed(word)), inverse_bits) == list(bits[:q]),
                        "concrete inverse")
                concrete += 1
    fixed = []
    for q in range(1, 4):
        minima, states = fixed_call_minima(q)
        require(minima == [2 * (q - r) for r in range(1, q + 1)], "complete call frontier")
        fixed.append({"q": q, "minimum_adds": minima, "reachable_states": states})
    weighted = 0
    tariffs = [(v[:2], v[2:]) for v in itertools.product(range(1, 4), repeat=4)]
    tariffs += [(a, m) for a in itertools.product((1, 4), repeat=3)
                for m in itertools.product((2, 5), repeat=3)]
    tariffs += [((10, 1, 10), (1, 5, 1))]
    for alpha, mu in tariffs:
        price, roots = weighted_formula(alpha, mu)
        word = schedule(len(alpha), roots)
        require(endpoint(len(alpha), word), "weighted witness endpoint")
        require(actual_cost(word, alpha, mu) == price, "weighted literal invoice")
        require(weighted_search(alpha, mu) == price, "full affine weighted optimum")
        weighted += 1
    alpha, mu = (10, 1, 10), (1, 5, 1)
    price, roots = weighted_formula(alpha, mu)
    require((price, roots) == (4, (0, 2)), "mixed roots calibration")
    word = schedule(4, [0], True)
    mutants = {
        "omit_old_dirt_wave_gate": word[1:],
        "omit_common_child": [g for g in word if g[0] != "P"],
        "wrong_common_destination": [(k, 1 if k == "P" else d, s) for k, d, s in word],
        "omit_private_child": word[:-1],
        "extra_common_child": word + [("P", 0, 0)],
    }
    for name, mutant in mutants.items():
        require(mutant != word and not endpoint(4, mutant, True), name + " escaped")
    clean_only = [("P", 0, 0), ("A", 1, 0), ("A", 2, 0)]
    require(not endpoint(3, clean_only), "clean-entry scope control")
    for common_price in (1, 2, 3):
        prices = [(3 + r) * common_price + 2 * (3 - r) for r in (1, 2, 3)]
        require(prices[1] >= min(prices[0], prices[2]), "uniform interior claim")
    return {"schema_version": 1, "symbolic_q_r_witnesses": symbolic,
            "all_root_subsets_q_le_8": subsets, "concrete_forward_inverse_cases": concrete,
            "fixed_call_full_affine_search": fixed, "weighted_full_affine_prices": weighted,
            "mixed_root_fixture": {"alpha": alpha, "mu": mu, "roots": roots, "cost": price},
            "mutation_controls": list(mutants) + ["clean_entry_scope", "uniform_interior_claim"],
            "symbolic_digest": digest.hexdigest(),
            "scope": "exact F2 affine interface only; no physical supplier or new kappa"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="create absent RESULT.json")
    args = parser.parse_args()
    result = checks()
    path = Path(__file__).with_name("RESULT.json")
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":"))
    if args.write:
        with path.open("x", encoding="utf-8") as output:
            output.write(json.dumps(result, indent=2) + "\n")
    else:
        observed = json.loads(path.read_text(encoding="utf-8"))
        require(json.dumps(observed, sort_keys=True, separators=(",", ":")) == encoded,
                "receipt mismatch")
    print("PASS_DIRTY_ANCHOR_TRADEOFF", encoded)


if __name__ == "__main__":
    main()
