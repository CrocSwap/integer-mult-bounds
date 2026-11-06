"""Independent finite review; no edits to the package under review.

@CubeJerry, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import json
import random
import types
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
kernel_bytes = (PACKAGE / 'compress.py').read_bytes()
kernel = types.ModuleType('independent_review_kernel')
exec(compile(kernel_bytes, str(PACKAGE / 'compress.py'), 'exec'), kernel.__dict__)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def dot(a, b, width):
    return sum(((a >> i) & 1) * ((b >> i) & 1) for i in range(width)) % 2


def rank(columns, rows):
    table = [[(c >> i) & 1 for c in columns] for i in range(rows)]
    pivot = 0
    for j in range(len(columns)):
        found = next((i for i in range(pivot, rows) if table[i][j]), None)
        if found is None:
            continue
        table[pivot], table[found] = table[found], table[pivot]
        for i in range(rows):
            if i != pivot and table[i][j]:
                table[i] = [a ^ b for a, b in zip(table[i], table[pivot])]
        pivot += 1
    return pivot


ZERO, ONE = frozenset(), frozenset({0})


def pmul(a, b):
    result = set()
    for x in a:
        for y in b:
            if x + y in result:
                result.remove(x + y)
            else:
                result.add(x + y)
    return frozenset(result)


def identity(n):
    return tuple(tuple(ONE if i == j else ZERO for j in range(n)) for i in range(n))


def product(a, b):
    n = len(a)
    output = [[ZERO for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                output[i][j] ^= pmul(a[i][k], b[k][j])
    return tuple(tuple(row) for row in output)


def endpoint(calls, n):
    answer = identity(n)
    for exponent, x, y in calls:
        factor = [list(row) for row in identity(n)]
        scalar = frozenset({exponent}) ^ ONE
        for i in range(n):
            for j in range(n):
                if (x >> i) & (y >> j) & 1:
                    factor[i][j] ^= scalar
        answer = product(answer, factor)
    return answer


def desired(t, r, exponent):
    answer = [list(row) for row in identity(t + r)]
    for i in range(t):
        answer[i][i] = frozenset({exponent})
    return tuple(tuple(row) for row in answer)


def binary_inverse(rows):
    n = len(rows)
    left = rows[:]
    right = [1 << i for i in range(n)]
    for j in range(n):
        i = next(i for i in range(j, n) if (left[i] >> j) & 1)
        left[i], left[j] = left[j], left[i]
        right[i], right[j] = right[j], right[i]
        for i in range(n):
            if i != j and (left[i] >> j) & 1:
                left[i] ^= left[j]
                right[i] ^= right[j]
    need(left == [1 << i for i in range(n)], 'binary inverse')
    return right


def random_basis(n, rng):
    rows = [1 << i for i in range(n)]
    if n > 1:
        for _ in range(5 * n):
            i, j = rng.sample(range(n), 2)
            rows[i] ^= rows[j]
    return rows, binary_inverse(rows)


def all_pairings(calls, n):
    return [[dot(y, x, n) for _, x, _ in calls] for _, _, y in calls]


def check_word(calls, t, r, target):
    compressed, w = kernel.compress_calls(calls, t, t + r)
    need(endpoint(calls, t + r) == target, 'original full endpoint')
    need(endpoint(compressed, t + w) == tuple(tuple(target[i][j]
         if i < t and j < t else (ONE if i == j else ZERO)
         for j in range(t + w)) for i in range(t + w)), 'compressed full endpoint')
    need(all_pairings(calls, t + r) == all_pairings(compressed, t + w), 'all call pairings')
    mask = (1 << t) - 1
    need([(a, x & mask, y & mask) for a, x, y in calls] ==
         [(a, x & mask, y & mask) for a, x, y in compressed], 'frames and data components')
    left, right = [x >> t for _, x, _ in calls], [y >> t for _, _, y in calls]
    u, v = rank(left, r), rank(right, r)
    gram = [sum(dot(x, y, r) << i for i, y in enumerate(right)) for x in left]
    need(w == rank(gram, len(calls)), 'paired rank width')
    need(u + v <= len(calls) - t, 'helper surplus rank')
    need(w <= (len(calls) - t) // 2, 'surplus width')
    return w


def main():
    rng = random.Random(2026110655)
    count = {'arbitrary_helper_factorizations': 0, 'full_endpoint_words': 0,
             'strict_dimension_reductions': 0, 'overbroad_claim_counterexamples': 0}
    for r in (0, 1, 2, 3, 5, 9, 17, 65):
        for k in (0, 1, 2, 3, 5, 8, 13):
            for _ in range(8):
                left = [rng.getrandbits(r) for _ in range(k)]
                right = [rng.getrandbits(r) for _ in range(k)]
                ul, vl, w = kernel.factor_helpers(left, right)
                need(len(ul) == len(vl) == k, 'column counts')
                need(all(0 <= z < 1 << w for z in ul + vl), 'compressed bit widths')
                for i in range(k):
                    for j in range(k):
                        need(dot(right[i], left[j], r) == dot(vl[i], ul[j], w), 'pairing factor')
                gram = [sum(dot(y, x, r) << i for i, y in enumerate(right)) for x in left]
                need(w == rank(gram, k), 'independent Gram rank')
                count['arbitrary_helper_factorizations'] += 1

    # A mixed scalar basis resolves z I into rank-one calls. Coordinate
    # helper inverses restore the helpers. Idle dimensions are then mixed
    # by an independently generated helper-only basis change.
    for t in (1, 2, 3):
        for r in range(5):
            for core in range(r + 1):
                for _ in range(4):
                    n = t + core
                    basis, inverse = random_basis(n, rng)
                    exponent = rng.choice((-3, -2, -1, 1, 2, 3))
                    calls = [(exponent, sum(((basis[i] >> j) & 1) << i for i in range(n)), inverse[j])
                             for j in range(n)]
                    calls += [(-exponent, 1 << i, 1 << i) for i in range(t, n)]
                    change, reverse = random_basis(r, rng)
                    changed = []
                    mask = (1 << t) - 1
                    for a, x, y in calls:
                        hx, hy = x >> t, y >> t
                        ux = sum(dot(row, hx, r) << i for i, row in enumerate(change))
                        vy = sum(dot(sum(((reverse[j] >> i) & 1) << j for j in range(r)), hy, r) << i
                                 for i in range(r))
                        changed.append((a, (x & mask) | (ux << t), (y & mask) | (vy << t)))
                    w = check_word(changed, t, r, desired(t, r, exponent))
                    need(w == core, 'sharp mixed-basis paired width')
                    count['full_endpoint_words'] += 1
                    count['strict_dimension_reductions'] += w < r

    # Both individual helper spans are nonzero, yet the paired width is zero.
    calls = [(3, 1, 1), (1, 3, 5), (-1, 3, 5)]
    need(check_word(calls, 1, 2, desired(1, 2, 3)) == 0, 'zero paired rank')
    count['full_endpoint_words'] += 1
    count['strict_dimension_reductions'] += 1

    # Nonidentity helpers: exact diagonal endpoint, but the surplus bound fails.
    calls = [(1, 1, 1), (1, 2, 2)]
    _, w = kernel.compress_calls(calls, 1, 2)
    need(endpoint(calls, 2) == desired(2, 0, 1) and w == 1 and w > (len(calls)-1)//2,
         'nonidentity-helper counterexample')
    count['overbroad_claim_counterexamples'] += 1

    # Correct on zero helper input, including its return to zero; full
    # matrix restoration is absent. Even the u+v surplus statement fails.
    calls = [(1, 1, 3)]
    need(endpoint(calls, 2) == ((frozenset({1}), frozenset({0, 1})), (ZERO, ONE)),
         'zero-input-only endpoint')
    need(rank([0], 1) + rank([1], 1) > len(calls)-1, 'zero-input-only rank violation')
    count['overbroad_claim_counterexamples'] += 1

    # Counting an identity target as nonidentity makes the claimed width false.
    calls = [(1, 2, 2), (-1, 2, 2)]
    _, w = kernel.compress_calls(calls, 1, 2)
    need(endpoint(calls, 2) == identity(2) and w == 1 and w > (len(calls)-1)//2,
         'identity-target counterexample')
    count['overbroad_claim_counterexamples'] += 1

    # A zero address frame is an identity call but still carries scalar
    # pairing rank. It is excluded by the theorem, not by the constructor.
    calls = [(2, 1, 1), (0, 2, 2)]
    _, w = kernel.compress_calls(calls, 1, 2)
    need(endpoint(calls, 2) == desired(1, 1, 2) and w == 1 and w > (len(calls)-1)//2,
         'zero-frame counterexample')
    count['overbroad_claim_counterexamples'] += 1

    # Pairings and data components alone do not force a new endpoint when
    # unrestricted, nonminimal helper factorizations are substituted.
    original = [(3, 1, 1), (1, 2, 2), (-1, 2, 2)]
    replaced = [(3, 1, 1), (1, 2, 2), (-1, 6, 2)]
    need(all_pairings(original, 2) == all_pairings(replaced, 3), 'replacement pairings')
    need(endpoint(original, 2) == desired(1, 1, 3), 'replacement original restored')
    changed = [list(row) for row in desired(1, 2, 3)]
    changed[2][1] = frozenset({-1, 0})
    need(endpoint(replaced, 3) == tuple(tuple(row) for row in changed),
         'pairings-only endpoint counterexample')
    count['overbroad_claim_counterexamples'] += 1

    # The paired rank is optimal only under the stated preservation
    # contract. Moving an adjacent cancelling pair onto the data wire
    # keeps frames and the endpoint, but changes the scalar components.
    replacement = [(a, 1, 1) for a, _, _ in original]
    need(kernel.compress_calls(original, 1, 2)[1] == 1 and
         endpoint(replacement, 1) == desired(1, 0, 3),
         'paired rank mistaken for an unrestricted helper lower bound')
    count['overbroad_claim_counterexamples'] += 1

    source_hashes = {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
                     for name in ('PROOF.md', 'compress.py')}
    need((PACKAGE / 'compress.py').read_bytes() == kernel_bytes, 'kernel changed during review')
    return {'marker': 'PASS_C_INDEPENDENT_COMPRESSION_REVIEW', 'seed': 2026110655,
            'counts': count, 'reviewed_sha256': source_hashes,
            'scope': 'Independent finite evidence; universal proof separately reviewed.'}


if __name__ == '__main__':
    print(json.dumps(main(), indent=2, sort_keys=True))
