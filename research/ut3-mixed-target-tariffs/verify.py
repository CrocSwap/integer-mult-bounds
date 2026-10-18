#!/usr/bin/env python3
"""Exact finite corroboration of the mixed UT3 target theorem in README.md.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor implementation is imported. The unbounded theorem is written,
not inferred from the finite fixtures below. Default operation is read-only.
"""

import argparse
from collections import deque
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
A, B, C = 1, 2, 4  # x + 2*y + 4*z


def require(ok, message):
    if not ok:
        raise ValueError(message)


def group_mul(g, h):
    x, y, z = g & 1, (g >> 1) & 1, g >> 2
    X, Y, Z = h & 1, (h >> 1) & 1, h >> 2
    return (x ^ X) | ((y ^ Y) << 1) | ((z ^ Z ^ (x & Y)) << 2)


TABLE = tuple(tuple(group_mul(g, h) for h in range(8)) for g in range(8))


def algebra_mul(a, b):
    out = 0
    for g in range(8):
        if a >> g & 1:
            for h in range(8):
                if b >> h & 1:
                    out ^= 1 << TABLE[g][h]
    return out


def quotient(a):
    # Coefficients in 1, X, Y, XY, YX, packed into five bits.
    out = 0
    for g in range(8):
        if a >> g & 1:
            x, y, z = g & 1, (g >> 1) & 1, g >> 2
            out ^= 1 | (x << 1) | (y << 2) | (z << 3) | ((z ^ (x & y)) << 4)
    return out


def quotient_mul(a, b):
    out = 0
    for i in range(5):
        for j in range(5):
            if not (a >> i & 1 and b >> j & 1):
                continue
            k = j if i == 0 else i if j == 0 else 3 if (i, j) == (1, 2) else 4 if (i, j) == (2, 1) else None
            if k is not None:
                out ^= 1 << k
    return out


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row.bit_length() - 1
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
    return len(pivots)


def bmul(left, right):
    out = []
    for row in left:
        value = 0
        for j, rr in enumerate(right):
            if row >> j & 1:
                value ^= rr
        out.append(value)
    return tuple(out)


def outer(u, v, r):
    return tuple(v if u >> i & 1 else 0 for i in range(r))


def ident(r):
    return tuple(1 << i for i in range(r))


def formal_identity(r):
    return tuple(tuple(int(i == j) for j in range(r)) for i in range(r))


def append_paid(state, gate):
    # Right multiplication by I + ([g]+1) u v^T.
    g, u, v = gate
    r = len(state)
    out = []
    for row in state:
        col = 0
        for j in range(r):
            if u >> j & 1:
                col ^= row[j]
        delta = algebra_mul(col, 1 ^ (1 << g))
        out.append(tuple(row[j] ^ (delta if v >> j & 1 else 0) for j in range(r)))
    return tuple(out)


def legal(gate, r):
    g, u, v = gate
    return g in (A, B) and 0 < u < 1 << r and 0 < v < 1 << r


def replay(r, word):
    state = formal_identity(r)
    for gate in word:
        require(legal(gate, r), "illegal paid factor")
        state = append_paid(state, gate)
    return state


def target(labels, r):
    return tuple(tuple((1 << (labels[i] if i < len(labels) else 0)) if i == j else 0 for j in range(r)) for i in range(r))


def direct_words():
    words = {0: ()}
    queue = deque([0])
    while queue:
        g = queue.popleft()
        for letter in (A, B):
            h = TABLE[g][letter]
            if h not in words:
                words[h] = words[g] + (letter,)
                queue.append(h)
    require(len(words) == 8, "address alphabet coverage")
    return words


WORDS = direct_words()


def counts(labels):
    a = b = 0
    for g in labels:
        x, y, z = g & 1, (g >> 1) & 1, g >> 2
        a += x + 2 * (1 - x) * z
        b += y + 2 * (1 - y) * z
    return a, b


def witness(labels):
    return tuple((g, 1 << i, 1 << i) for i, label in enumerate(labels) for g in WORDS[label])


def coefficients(state):
    r = len(state)
    return tuple(tuple(sum(((quotient(state[i][j]) >> k) & 1) << j for j in range(r)) for i in range(r)) for k in (1, 2, 3, 4))


def concatenate_rank(left, right):
    r = len(left)
    return rank(tuple(x | (y << r) for x, y in zip(left, right)))


def lower_bounds(state):
    a, b, ab, ba = coefficients(state)
    # Sylvester, without assuming a or b vanishes.
    return (concatenate_rank(a, ab) + rank(a + ba) - rank(a),
            concatenate_rank(b, ba) + rank(b + ab) - rank(b))


def scalar_conjugate(state, f, inv):
    r = len(state)
    left = []
    for row in f:
        dst = [0] * r
        for i in range(r):
            if row >> i & 1:
                dst = [x ^ y for x, y in zip(dst, state[i])]
        left.append(dst)
    return tuple(tuple(xor_values(row[k] for k in range(r) if inv[k] >> j & 1) for j in range(r)) for row in left)


def xor_values(values):
    out = 0
    for v in values:
        out ^= v
    return out


def scalar_basis(r):
    f = ident(r)
    ops = []
    for i in range(r - 1):
        gate = list(ident(r))
        gate[i] ^= 1 << (i + 1)
        f = bmul(f, tuple(gate))
        ops.append(tuple(gate))
    inv = ident(r)
    for gate in reversed(ops):
        inv = bmul(inv, gate)
    require(bmul(f, inv) == ident(r), "scalar basis inverse")
    return f, inv


def conjugate_word(word, f, inv):
    r = len(f)
    out = []
    for g, u, v in word:
        uu = sum(((row & u).bit_count() & 1) << i for i, row in enumerate(f))
        vv = bmul((v,), inv)[0]
        require(rank(bmul(bmul(f, outer(u, v, r)), inv)) == 1, "conjugated factor rank")
        out.append((g, uu, vv))
    return tuple(out)


def regular_rows(state):
    # Expand formal coefficients in the left regular representation.
    r = len(state)
    rows = [0] * (8 * r)
    for i in range(r):
        for j in range(r):
            for g in range(8):
                if state[i][j] >> g & 1:
                    for h in range(8):
                        rows[8 * i + TABLE[g][h]] ^= 1 << (8 * j + h)
    return rows


def update_digest(digest, rows):
    digest.update(json.dumps(rows, separators=(",", ":")).encode() + b"\n")


def check_algebra():
    for g, h in product(range(8), repeat=2):
        require(quotient(1 << TABLE[g][h]) == quotient_mul(quotient(1 << g), quotient(1 << h)), "quotient homomorphism")
    for a, b, c in product(range(32), repeat=3):
        require(quotient_mul(quotient_mul(a, b), c) == quotient_mul(a, quotient_mul(b, c)), "quotient associativity")
    for g in range(8):
        require(counts((g,)) == (WORDS[g].count(A), WORDS[g].count(B)), "direct word fails separate minima")
    # Exact shortest paths independently reprice the eight address endpoints.
    tariffs = ((1, 1), (1, 7), (7, 1), (Fraction(2, 3), Fraction(5, 7)))
    for alpha, beta in tariffs:
        dist = {0: Fraction(0)}
        done = set()
        while len(done) < 8:
            g = min((x for x in dist if x not in done), key=dist.get)
            done.add(g)
            for label, price in ((A, alpha), (B, beta)):
                h = TABLE[g][label]
                cost = dist[g] + price
                if h not in dist or cost < dist[h]:
                    dist[h] = cost
        for g in range(8):
            p, q = counts((g,))
            require(dist[g] == alpha * p + beta * q, "weighted address bound")
    return {"group_products": 64, "quotient_associativity_triples": 32768, "exact_tariff_endpoints": 32}


def check_sylvester():
    checked = nonzero = 0
    for n in range(4):
        for x in product(range(1 << n), repeat=2):
            for y in product(range(4), repeat=n):
                z = bmul(x, y)
                require(rank(x) + rank(y) - rank(z) <= n, "Sylvester bound")
                checked += 1
                nonzero += bool(rank(z))
    return {"sylvester_pairs": checked, "sylvester_nonzero_products": nonzero}


def check_witnesses():
    digest = hashlib.sha256()
    fixtures = columns = controls = 0
    for t in range(1, 4):
        for labels in product(range(8), repeat=t):
            for extra in (0, 1):
                r = t + extra
                word = witness(labels)
                expected = target(labels, r)
                state = replay(r, word)
                require(state == expected, "full formal dirty boundary")
                require(lower_bounds(state) == counts(labels), "mixed endpoint rank formula")
                for conjugated in (False, True):
                    if conjugated:
                        f, inv = scalar_basis(r)
                        state = replay(r, conjugate_word(word, f, inv))
                        require(state == scalar_conjugate(expected, f, inv), "scalar-conjugated dirty boundary")
                        require(lower_bounds(state) == counts(labels), "basis-invariant lower bound")
                    update_digest(digest, regular_rows(state))
                    fixtures += 1
                    columns += 8 * r
                if extra and word:
                    bad = word + ((A, 1 << t, 1 << t),)
                    require(replay(r, bad) != expected, "unrestored dirty role must reject")
                    controls += 1
            if any(labels):
                word = witness(labels)
                for i in range(len(word)):
                    require(replay(t, word[:i] + word[i + 1:]) != target(labels, t), "deleted paid call must reject")
                    controls += 1
    # All eight labels together, including two arbitrary restored dirty roles.
    labels = tuple(range(8))
    word = witness(labels)
    require(replay(10, word) == target(labels, 10), "all-label boundary")
    require(lower_bounds(target(labels, 10)) == (8, 8), "all-label cost")
    return {"witness_fixtures": fixtures, "faithful_columns": columns, "witness_digest": digest.hexdigest(), "all_eight_labels_bill": [8, 8], "boundary_mutation_controls": controls}


def check_all_short_words():
    # Every r=2 expanded-alphabet word of length <=4, including nilpotents.
    alphabet = tuple((g, u, v) for g in (A, B) for u in range(1, 4) for v in range(1, 4))
    identity = formal_identity(2)
    checked = endpoints = 0
    pair_digest = hashlib.sha256()

    def visit(state, depth, na, nb):
        nonlocal checked, endpoints
        bound_a, bound_b = lower_bounds(state)
        require(bound_a <= na and bound_b <= nb, "short-word coefficient-rank inequality")
        checked += 1
        if state[0][1] == state[1][0] == 0 and all(v > 0 and v & (v - 1) == 0 for v in (state[0][0], state[1][1])):
            labels = (state[0][0].bit_length() - 1, state[1][1].bit_length() - 1)
            need_a, need_b = counts(labels)
            require(need_a <= na and need_b <= nb, "short formal endpoint violates proposed tariff")
            endpoints += 1
        if depth == 2:
            update_digest(pair_digest, regular_rows(state))
        if depth == 4:
            return
        for gate in alphabet:
            visit(append_paid(state, gate), depth + 1, na + (gate[0] == A), nb + (gate[0] == B))

    visit(identity, 0, 0, 0)
    return {"expanded_r2_alphabet": len(alphabet), "words_through_length_four": checked, "diagonal_endpoint_words": endpoints, "two_factor_digest": pair_digest.hexdigest()}


def check_controls():
    # The quotient is deliberately not a formal endpoint acceptance test.
    kernel = algebra_mul(1 ^ (1 << A), 1 ^ (1 << C))
    require(kernel != 0 and quotient(kernel) == 0, "nonfaithful quotient control")
    good = target((C,), 2)
    bad = ((good[0][0], kernel), good[1])
    require(coefficients(bad) == coefficients(good), "kernel perturbation invisible to rank proof")
    require(bad != good and regular_rows(bad) != regular_rows(good), "formal and faithful controls reject kernel")
    # It is invisible on all clean-extra inputs but changes a dirty-extra column.
    differences = [x ^ y for x, y in zip(regular_rows(bad), regular_rows(good))]
    require(all(d & 255 == 0 for d in differences) and any(d >> 8 for d in differences), "clean-only false acceptance control")
    # The central-only proof cannot be copied verbatim for a noncentral target.
    state = replay(1, ((A, 1, 1),))
    require(lower_bounds(state) == (1, 0), "rank(A) correction is essential")
    require(2 * rank(coefficients(state)[0]) > 1, "zero-sum shortcut would be false")
    # Simply exchanging x and y misses the xy term in the quotient.
    wrong = lambda g: ((g >> 1) & 1) | ((g & 1) << 1) | (g & 4)
    require(wrong(TABLE[A][B]) != TABLE[wrong(A)][wrong(B)], "missing xy correction must fail")
    require(not legal((C, 1, 1), 1), "central address primitive outside alphabet")
    require(not legal((A, 0, 1), 1), "zero scalar factor outside alphabet")
    # Four full-rank coordinatewise macros attain two central targets. Each
    # macro is rank two, so charging it once would change the legal alphabet.
    require(rank(ident(2)) == 2, "higher-rank control")
    state = formal_identity(2)
    for label in WORDS[C]:
        state = tuple(tuple(algebra_mul(entry, 1 << label) for entry in row) for row in state)
    require(state == target((C, C), 2), "rank-two macro witness")
    require(len(WORDS[C]) < sum(lower_bounds(state)), "unit-priced rank-two macros violate the intended bill")
    nilpotent = (A, 1, 2)
    require(replay(2, (nilpotent, nilpotent)) == formal_identity(2), "nilpotent paid factor remains reversible")
    return {"model_controls": ["nonfaithful_quotient_kernel", "formal_kernel_rejection",
            "faithful_kernel_rejection", "clean_extra_blind_spot", "nonzero_first_order_correction",
            "missing_xy_correction", "central_label_restriction", "nonzero_factor_restriction",
            "unit_priced_rank_two_escape", "nilpotent_reversibility"],
            "nonfaithful_kernel_support": [g for g in range(8) if kernel >> g & 1]}


def run():
    result = {"schema_version": 1, "scope": "Finite evidence for the written all-register mixed UT3 tariff theorem; no new kappa."}
    for check in (check_algebra, check_sylvester, check_witnesses, check_all_short_words, check_controls):
        result.update(check())
    independent = json.loads(subprocess.check_output([sys.executable, "-I", "-B", str(HERE / "independent.py")], text=True, timeout=120))
    for field in ("witness_fixtures", "faithful_columns", "witness_digest", "two_factor_digest"):
        require(independent[field] == result[field], "separate regular implementation disagrees: " + field)
    result["independent"] = independent
    return result


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print freshly computed finite evidence without modifying files")
    args = parser.parse_args()
    try:
        result = run()
        if args.emit:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            expected = json.loads((HERE / "CERTIFICATE.json").read_text())
            require(canonical(result) == canonical(expected), "committed certificate differs from exact replay")
            print("PASS_UT3_MIXED_TARGET_TARIFFS words=" + str(result["words_through_length_four"]) + " witnesses=" + str(result["witness_fixtures"]) + " no_new_kappa")
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        parser.exit(1, "FAIL_UT3_MIXED_TARGET_TARIFFS: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
