#!/usr/bin/env python3
"""Exact finite corroboration of PROOF.md; standard library, Apache-2.0.

Prepared for Ross Richardson with substantial OpenAI Codex assistance.
No predecessor implementation is imported. Verification never generates evidence.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def reject(fn, message):
    try:
        fn()
    except ValueError:
        return
    raise ValueError("negative control accepted: " + message)


def strict_json(path):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, "duplicate JSON key: " + key)
            out[key] = value
        return out
    return json.loads(path.read_text(), object_pairs_hook=pairs)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def verify_receipt(actual, expected):
    require(canonical(actual) == canonical(expected), "receipt differs from exact recomputation")


def mul(a, b, n):
    k, e = divmod(a, 2)
    l, f = divmod(b, 2)
    return 2 * ((k + (-l if e else l)) % n) + (e ^ f)


def cmul(a, b, n):
    out = 0
    while a:
        low = a & -a
        x = low.bit_length() - 1
        a ^= low
        q = b
        while q:
            low = q & -q
            y = low.bit_length() - 1
            q ^= low
            out ^= 1 << mul(x, y, n)
    return out


def identity(roles):
    return tuple(1 if i == j else 0 for i in range(roles) for j in range(roles))


def projectors(roles):
    return [(u, v) for u in range(1, 1 << roles)
            for v in range(1, 1 << roles) if (u & v).bit_count() % 2]


def validate_factor(factor, n, roles):
    g, u, v = factor
    require(g in (1, 2 * (n - 1) + 1), "illegal paid label")
    require(type(u) is int and type(v) is int and 0 < u < 1 << roles
            and 0 < v < 1 << roles and (u & v).bit_count() % 2 == 1,
            "not a legal rank-one idempotent")


def append_factor(state, factor, n, roles):
    """Right multiply the full formal matrix by I + ([g]+1) u v^T."""
    validate_factor(factor, n, roles)
    g, u, v = factor
    out = list(state)
    for a in range(roles):
        aggregate = 0
        for s in range(roles):
            if u >> s & 1:
                aggregate ^= state[a * roles + s]
        delta = aggregate ^ cmul(aggregate, 1 << g, n)
        for b in range(roles):
            if v >> b & 1:
                out[a * roles + b] ^= delta
    return tuple(out)


def formal(word, n, roles):
    state = identity(roles)
    for f in word:
        state = append_factor(state, f, n, roles)
    return state


def target_matrix(targets, roles):
    require(len(targets) <= roles, "too many targets")
    t = tuple(targets) + (0,) * (roles - len(targets))
    return tuple(1 << t[i] if i == j else 0
                 for i in range(roles) for j in range(roles))


def endpoint(state, targets, roles):
    require(state == target_matrix(targets, roles), "formal endpoint mismatch")


def distance(t, n):
    t %= n
    return min(t, n - t)


def budget(targets, n):
    require(type(n) is int and n >= 3 and n % 2 == 1, "odd period >=3 required")
    m = n // 2
    pairs = [divmod(g, 2) for g in targets]
    require(all(0 <= k < n and e in (0, 1) for k, e in pairs), "invalid target")
    return (sum(distance(k + e, n) for k, e in pairs),
            sum(distance(k, n) for k, e in pairs),
            sum((k, e) == (m, 1) for k, e in pairs))


def tariff(targets, n, alpha, beta):
    require(alpha >= 0 and beta >= 0, "negative price")
    a, b, t = budget(targets, n)
    return alpha * a + beta * b + t * min(alpha, beta)


def letters(g, n, extra_x=True):
    """An attaining alternating word; group products are displayed left to right."""
    k, e = divmod(g, 2)
    m = n // 2
    if k > m or (k == m and e and not extra_x):
        k -= n
    x, y = 1, 2 * (n - 1) + 1
    word = [x, y] * k if k >= 0 else [y, x] * (-k)
    if e:
        word.append(x)
    reduced = []
    for h in word:
        if reduced and reduced[-1] == h:
            reduced.pop()
        else:
            reduced.append(h)
    return reduced


def direct_word(targets, n, j=0):
    """j of the exceptional roles receive the extra x; the rest an extra y."""
    _, _, t = budget(targets, n)
    require(type(j) is int and 0 <= j <= t, "invalid exceptional split")
    seen = 0
    word = []
    for role, g in enumerate(targets):
        exceptional = g == n  # index 2m+1 of (m,1)
        extra_x = not exceptional or seen < j
        seen += exceptional
        word.extend((h, 1 << role, 1 << role) for h in letters(g, n, extra_x))
    return word


def compose(p, q):
    return tuple(p[q[a]] for a in range(len(p)))


class RegularOracle:
    """Independent group construction from literal permutations on n vertices.

    Matrices are binary rows; calls execute on all 2n group-basis addresses.
    This uses neither mul/cmul nor append_factor to build the operator.
    """
    def __init__(self, n):
        self.n = n
        one = tuple(range(n))
        x = tuple((-a) % n for a in range(n))
        y = tuple((-a - 1) % n for a in range(n))
        found = {one}
        queue = deque([one])
        self.bfs_distance = {one: 0}
        while queue:
            p = queue.popleft()
            for q in (x, y):
                r = compose(q, p)
                if r not in found:
                    found.add(r)
                    queue.append(r)
                    self.bfs_distance[r] = self.bfs_distance[p] + 1
        self.perms = sorted(found)
        require(len(self.perms) == 2 * n, "wrong group order")
        index = {p: i for i, p in enumerate(self.perms)}
        self.normal = [index[tuple((k + (-a if e else a)) % n for a in range(n))]
                       for k in range(n) for e in range(2)]
        self.actions = [[index[compose(p, q)] for q in self.perms] for p in self.perms]

    def matrix(self, word, roles):
        width = 2 * self.n
        rows = [1 << i for i in range(width * roles)]
        for label, u, v in reversed(word):
            action = self.actions[self.normal[label]]
            old = rows[:]
            for address in range(width):
                delta = 0
                for role in range(roles):
                    if v >> role & 1:
                        delta ^= old[role * width + address] ^ old[role * width + action[address]]
                for role in range(roles):
                    if u >> role & 1:
                        rows[role * width + address] ^= delta
        return rows

    def from_formal(self, state, roles):
        width = 2 * self.n
        rows = [0] * (width * roles)
        for i in range(roles):
            for j in range(roles):
                coeffs = state[i * roles + j]
                for normal in range(width):
                    if coeffs >> normal & 1:
                        for source, dest in enumerate(self.actions[self.normal[normal]]):
                            rows[i * width + dest] ^= 1 << (j * width + source)
        return rows


def rank(rows):
    pivots = {}
    for x in rows:
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                break
    return len(pivots)


def crossing(rows, half, width, roles):
    """Rank of the output-K/input-H block, matching PROOF.md."""
    k = [i * width + a for i in range(roles) for a in range(width) if a not in half]
    mask = sum(1 << (i * width + a) for i in range(roles) for a in half)
    return rank([rows[i] & mask for i in k])


def regular_half(oracle):
    n = oracle.n
    m = n // 2
    return {oracle.normal[2 * (a % n)] for a in range(-m, 1)} | {
        oracle.normal[2 * b + 1] for b in range(m)}


def small_action(g, n, c):
    k, e = divmod(g, 2)
    return tuple((k + (c - a if e else a)) % n for a in range(n))


def represented(state, n, roles, c):
    rows = [0] * (n * roles)
    for i in range(roles):
        for j in range(roles):
            for g in range(2 * n):
                if state[i * roles + j] >> g & 1:
                    for a, b in enumerate(small_action(g, n, c)):
                        rows[i * n + b] ^= 1 << (j * n + a)
    return rows


def count_bound(targets, n, roles, nx, ny):
    """Reject bills below actual operator cut ranks, not a substituted formula.

    Passing this necessary-condition test is not endpoint/circuit certification.
    """
    require(type(nx) is int and type(ny) is int and nx >= 0 and ny >= 0, "invalid bill")
    budget(targets, n)
    state = target_matrix(targets, roles)
    m = n // 2
    qx = crossing(represented(state, n, roles, m), set(range(m)), n, roles)
    qy = crossing(represented(state, n, roles, m-1), set(range(m)), n, roles)
    oracle = RegularOracle(n)
    qjoint = crossing(oracle.from_formal(state, roles), regular_half(oracle), 2*n, roles)
    require(nx >= qx, "x cut invoice")
    require(ny >= qy, "y cut invoice")
    require(nx + ny >= qjoint, "joint cut invoice")
    return qx, qy, qjoint


def verify_sources():
    source = strict_json(HERE / "SOURCES.json")
    root = HERE.parents[1]
    for item in source["files"]:
        if item["usage"] == "input":
            require(hashlib.sha256((root / item["path"]).read_bytes()).hexdigest()
                    == item["sha256"], "source hash mismatch: " + item["path"])


def compute():
    counts = Counter()
    digest = hashlib.sha256()
    for n in range(3, 32, 2):
        oracle = RegularOracle(n)
        half = regular_half(oracle)
        require(len(half) == n, "regular half size")
        m = n // 2
        for g in range(2 * n):
            a, b, t = budget([g], n)
            rows = oracle.from_formal((1 << g,), 1)
            q = crossing(rows, half, 2 * n, 1)
            shortest = oracle.bfs_distance[oracle.perms[oracle.normal[g]]]
            require(q == shortest == a + b + t, "joint cut / shortest distance")
            require(crossing(represented((1 << g,), n, 1, m), set(range(m)), n, 1) == a,
                    "x cut formula")
            require(crossing(represented((1 << g,), n, 1, m - 1), set(range(m)), n, 1) == b,
                    "y cut formula")
            for j in range(t + 1):
                word = direct_word([g], n, j)
                endpoint(formal(word, n, 1), [g], 1)
                require(oracle.matrix(word, 1) == rows, "single formal/regular disagreement")
                counts["single_attaining_words"] += 1
            digest.update(canonical([n, g, a, b, t, q]).encode())
            counts["complete_single_targets"] += 1
        if n <= 15:
            for g, h in itertools.product(range(2 * n), repeat=2):
                product = mul(g, h, n)
                require(oracle.normal[product] == oracle.actions[oracle.normal[g]][oracle.normal[h]],
                        "independent group multiplication")
                for c in (m, m - 1):
                    require(small_action(product, n, c) == compose(small_action(g, n, c),
                                                                small_action(h, n, c)), "representation law")
                counts["complete_group_pairs"] += 1
        if n <= 11:
            for roles in range(1, 5):
                ps = projectors(roles)
                require(len(ps) == (1 << (roles - 1)) * ((1 << roles) - 1), "projector count")
                for u, v in ps:
                    for letter, label in enumerate((1, 2 * (n - 1) + 1)):
                        state = formal([(label, u, v)], n, roles)
                        rows = oracle.matrix([(label, u, v)], roles)
                        require(rows == oracle.from_formal(state, roles), "factor oracle")
                        cuts = (crossing(represented(state, n, roles, m), set(range(m)), n, roles),
                                crossing(represented(state, n, roles, m - 1), set(range(m)), n, roles),
                                crossing(rows, half, 2 * n, roles))
                        require(cuts == ((1, 0, 1) if letter == 0 else (0, 1, 1)), "rank-one cut charges")
                        counts["all_projector_factor_checks"] += 1
                        counts["factor_regular_basis_columns"] += 2 * n * roles
    for n in (3, 5):
        oracle = RegularOracle(n)
        half = regular_half(oracle)
        alphabet = [(g, u, v) for g in (1, 2 * (n - 1) + 1) for u, v in projectors(2)]
        for length in range(4):
            for word in itertools.product(alphabet, repeat=length):
                state = formal(word, n, 2)
                rows = oracle.matrix(word, 2)
                require(rows == oracle.from_formal(state, 2), "mixed full operator disagreement")
                nx = sum(g == 1 for g, _, _ in word)
                qx = crossing(represented(state, n, 2, n // 2), set(range(n // 2)), n, 2)
                qy = crossing(represented(state, n, 2, n // 2 - 1), set(range(n // 2)), n, 2)
                qr = crossing(rows, half, 2 * n, 2)
                require(qx <= nx and qy <= length - nx and qr <= length, "mixed cut subadditivity")
                counts["complete_short_words"] += 1
                counts["short_word_regular_basis_columns"] += 4 * n
                digest.update(canonical([n, list(word), state]).encode())
    prices = (Fraction(0), Fraction(1, 3), Fraction(1), Fraction(2), Fraction(7))
    for n in (3, 5, 7):
        oracle = RegularOracle(n)
        for targets in itertools.product(range(2 * n), repeat=2):
            a, b, t = budget(targets, n)
            costs = []
            for j in range(t + 1):
                word = direct_word(targets, n, j)
                state = formal(word, n, 3)
                endpoint(state, targets, 3)
                regular = oracle.matrix(word, 3)
                require(regular == oracle.from_formal(target_matrix(targets, 3), 3), "dirty regular boundary")
                nx = sum(g == 1 for g, _, _ in word)
                require((nx, len(word) - nx) == (a + j, b + t - j), "joint count split")
                costs.append((nx, len(word) - nx))
                inverse_targets = [2*(-(g//2) % n) if g % 2 == 0 else g for g in targets]
                inverse = formal(list(reversed(word)), n, 3)
                endpoint(inverse, inverse_targets, 3)
                require(oracle.matrix(list(reversed(word)), 3) == oracle.from_formal(inverse, 3),
                        "inverse regular boundary")
                counts["pair_inverse_words"] += 1
                for cut in range(len(word)):
                    reject(lambda cut=cut: endpoint(formal(word[:cut] + word[cut+1:], n, 3), targets, 3),
                           "single-call omission")
                    counts["single_call_omissions"] += 1
                counts["complete_pair_attaining_words"] += 1
                counts["pair_regular_basis_columns"] += 6 * n
                digest.update(canonical([n, targets, j, state]).encode())
            for alpha, beta in itertools.product(prices, repeat=2):
                require(min(alpha*x + beta*y for x, y in costs) == tariff(targets, n, alpha, beta),
                        "nonnegative rational tariff")
                counts["rational_price_checks"] += 1
    # Beyond pair endpoints: every exceptional split, with varied ordinary targets
    # and one arbitrary spectator, for t=0..5 (up to eight scalar roles).
    for n in (3, 5, 9, 15):
        oracle = RegularOracle(n)
        for t in range(6):
            targets = [n] * t + [1, 2*n-2]
            roles = len(targets) + 1
            a, b, actual_t = budget(targets, n)
            require(actual_t == t, "larger tuple setup")
            for j in range(t+1):
                word = direct_word(targets, n, j)
                state = formal(word, n, roles)
                endpoint(state, targets, roles)
                require(oracle.matrix(word, roles) == oracle.from_formal(state, roles), "larger tuple regular boundary")
                require(count_bound(targets, n, roles, a+j, b+t-j) == (a,b,a+b+t), "joint operator bill")
                counts["larger_mixed_tuple_words"] += 1
                counts["larger_tuple_regular_basis_columns"] += roles * 2*n
    # All scalar invertible maps through three roles have zero crossing rank,
    # and conjugation permutes the full rank-one-idempotent alphabet.
    for roles in range(1,4):
        ps = projectors(roles)
        for scalar in itertools.product(range(1 << roles), repeat=roles):
            if rank(scalar) != roles:
                continue
            images = [sum(((row & v).bit_count() % 2) << i for i, row in enumerate(scalar))
                      for v in range(1 << roles)]
            inverse = {image: v for v, image in enumerate(images)}
            for u, v in ps:
                covector = sum(((v & inverse[1 << i]).bit_count() % 2) << i for i in range(roles))
                require((images[u], covector) in ps, "scalar conjugation closure")
                counts["scalar_projector_conjugations"] += 1
            for n in (3,5):
                rows = [sum(1 << (j*2*n+a) for j in range(roles) if scalar[i] >> j & 1)
                        for i in range(roles) for a in range(2*n)]
                oracle = RegularOracle(n)
                require(crossing(rows, regular_half(oracle), 2*n, roles) == 0, "free scalar charge")
                counts["free_scalar_cut_checks"] += 1
    controls = semantic_controls()
    return {"schema_version": 1, "scope": "finite corroboration; universal theorem is PROOF.md; no_new_kappa",
            "domains": {"odd_periods_all_targets": list(range(3, 32, 2)),
                        "all_group_pairs_periods": list(range(3, 16, 2)),
                        "all_projectors_roles": [1, 2, 3, 4], "all_projectors_periods": [3, 5, 7, 9, 11],
                        "complete_short_words": {"periods": [3, 5], "roles": 2, "lengths": [0, 1, 2, 3]},
                        "all_ordered_target_pairs": {"periods": [3, 5, 7], "roles": 3},
                        "larger_mixed_tuples": {"periods": [3,5,9,15], "exceptional_counts": list(range(6)),
                                                 "ordinary_targets": ["x", "r^-1"], "dirty_spectators": 1},
                        "all_scalar_GL_roles": [1,2,3]},
            "counts": dict(sorted(counts.items())), "semantic_controls": controls,
            "mathematical_digest_sha256": digest.hexdigest()}


def semantic_controls():
    names = []
    def bad(name, fn):
        reject(fn, name)
        names.append(name)
    bad("even-period misuse", lambda: budget([0], 4))
    bad("negative tariff", lambda: tariff([1], 3, Fraction(-1), Fraction(1)))
    bad("illegal rotation label", lambda: formal([(2, 1, 1)], 3, 2))
    bad("non-idempotent scalar factor", lambda: formal([(1, 1, 2)], 3, 2))
    bad("foreign scalar role", lambda: formal([(1, 4, 4)], 3, 2))
    for n in (3, 5):
        a, b, t = budget([n, n], n)
        require((a+b) % 2 == 0 and t == 2, "joint-gap fixture setup")
        bad(f"joint deficit n={n}", lambda n=n, a=a, b=b: count_bound([n,n], n, 3, a, b))
        bad(f"wrong noncommuting order n={n}", lambda n=n: endpoint(formal([(1,1,1),(2*n-1,1,1)], n, 1), [2*n-2], 1))
        require(len(direct_word([n], n, 0)) == n, "longest reflection length")
    n, roles = 5, 3
    bad("x bill hidden by large y bill", lambda: count_bound([1], 5, 2, 0, 100))
    bad("y bill hidden by large x bill", lambda: count_bound([9], 5, 2, 100, 0))
    word = direct_word([n, 2], n, 1)
    baseline = formal(word, n, roles)
    dirty = list(baseline)
    dirty[2] ^= 1
    require(dirty[0] == baseline[0] and dirty[1] == baseline[1], "clean control setup")
    bad("dirty spectator leaks into target", lambda: endpoint(tuple(dirty), [n,2], roles))
    dirty = list(baseline)
    dirty[8] = 1 << 1
    bad("spectator not restored", lambda: endpoint(tuple(dirty), [n,2], roles))
    hidden = list(identity(2)); hidden[1] = (1 << (2*n)) - 1
    for c in (n//2, n//2-1):
        require(represented(tuple(hidden), n, 2, c) == represented(identity(2), n, 2, c), "common kernel setup")
    bad("proof-representation false endpoint", lambda: endpoint(tuple(hidden), [], 2))
    oracle = RegularOracle(n)
    require(oracle.from_formal(tuple(hidden), 2) != oracle.from_formal(identity(2), 2), "faithful kernel detector")
    extra = [(1, 3, 1), (1, 3, 1)]
    require(formal(extra, n, 2) == identity(2), "equivalent cancelling presentation")
    require(oracle.matrix(extra, 2) == oracle.from_formal(identity(2), 2), "oracle equivalent presentation")
    names.append("positive noncoordinate cancelling presentation")
    return names


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print recomputation without writing evidence")
    args = parser.parse_args()
    verify_sources()
    actual = compute()
    if args.emit:
        print(json.dumps(actual, indent=2, sort_keys=True))
        return
    expected = strict_json(HERE / "RECEIPT.json")
    verify_receipt(actual, expected)
    print("PASS_ODD_DIHEDRAL_JOINT_TARIFF " + canonical(actual["counts"]) + " no_new_kappa")


if __name__ == "__main__":
    main()
