"""Independent exact restricted-update check. Apache-2.0.

Reads no executable predecessor or primary implementation. The literal Gaussian
word is credited to Tekalign/PR3025/3033 and Nick Petalas/PR3035/3037; the present
independent enumeration and closed coefficient construction are by Ross
Richardson with OpenAI Codex assistance.
"""
from collections import Counter
from functools import lru_cache
from itertools import product
import hashlib
import json
import math


def require(condition, message):
    if not condition:
        raise ValueError(message)


def gaussian_multiply(z, w):
    return z[0] * w[0] - z[1] * w[1], z[0] * w[1] + z[1] * w[0]


def gaussian_power(z, n):
    w = (1, 0)
    for _ in range(n):
        w = gaussian_multiply(w, z)
    return w


def literal(x, r, mutation=False):
    """Use Gaussian pairs, with two floors at their literal locations."""
    require(r >= 1 and len(x) == 2 << r, "dimension")
    require(all(type(v) is int for v in x), "integer source")
    z = list(zip(x[::2], x[1::2]))
    for k in range(r):
        step = 1 << k
        for base in range(0, 1 << r, 2 * step):
            for offset in range(step):
                i, j = base + offset, base + offset + step
                a, b = z[i], z[j]
                d = a[0] - b[0], a[1] - b[1]
                s = b[0] + d[0] // 2, b[1] + d[1] // 2
                e = d[1] if mutation else -d[1], d[0]
                lower = s[0] - e[0] // 2, s[1] - e[1] // 2
                upper = lower[0] + e[0], lower[1] + e[1]
                z[i], z[j] = upper, lower
    return tuple(t for pair in z for t in pair)


@lru_cache(None)
def matrix(r, stages=None):
    """Numerator 2^k U_k from the unique path, not a stage evaluator."""
    k = r if stages is None else stages
    n = 1 << r
    rows = [[0] * (2 * n) for _ in range(2 * n)]
    for i in range(n):
        for j in range(n):
            if i >> k != j >> k:
                continue
            h = (i ^ j).bit_count()
            a, b = gaussian_multiply(gaussian_power((1, 1), k - h),
                                     gaussian_power((1, -1), h))
            rows[2*i][2*j], rows[2*i][2*j+1] = a, -b
            rows[2*i+1][2*j], rows[2*i+1][2*j+1] = b, a
    return tuple(map(tuple, rows))


def defect(x, r):
    a = matrix(r)
    return tuple((1 << r) * y - sum(c * v for c, v in zip(row, x))
                 for row, y in zip(a, literal(x, r)))


def character_columns(r):
    """Independent quotient: joint prefix-parity characters in Q/Z.

    Row (U_k[a]-U_k[b])/2 has common denominator q. Its character
    vanishes exactly when the next input difference is an even integer.
    The simultaneous kernel is the sufficient prefix lattice.
    """
    q = 1 << (r // 2 + 1)
    d = 2 << r
    rows = []
    for k in range(r):
        a = matrix(r, k)
        for i in range(1 << r):
            if i & (1 << k):
                continue
            j = i + (1 << k)
            for c in range(2):
                nums = [q * (u - v) for u, v in zip(a[2*i+c], a[2*j+c])]
                den = 1 << (k + 1)
                require(all(v % den == 0 for v in nums), "character denominator")
                rows.append(tuple((v // den) % q for v in nums))
    return q, tuple(tuple(row[j] for row in rows) for j in range(d))


def quotient_representatives(r, include_characters=False):
    """Adjoin standard-basis characters, enumerating each new image coset.

    This enumerates the finite character image, rather than using a lattice
    basis, Hermite form or the predecessor's index-two transversal algorithm.
    """
    q, cols = character_columns(r)
    m, d = len(cols[0]), len(cols)
    states = {(0,) * m: (0,) * d}
    orders = []
    for j, col in enumerate(cols):
        order = next(k for k in range(1, q + 1)
                     if tuple(k * a % q for a in col) in states)
        require(q % order == 0, "extension order")
        old = list(states.items())
        for k in range(1, order):
            for char, rep in old:
                new = tuple((a + k*b) % q for a, b in zip(char, col))
                require(new not in states, "character collision")
                x = list(rep)
                x[j] = (x[j] + k) % q
                states[new] = tuple(x)
        orders.append(order)
    require(len(states) == math.prod(orders), "quotient order")
    return q, tuple(states.items()) if include_characters else tuple(states.values()), orders


def family_counts(r, reps=None):
    q = 1 << (r // 2 + 1)
    d = 2 << r
    values = tuple(product(range(q), repeat=d)) if reps is None else tuple(reps)
    local_defect = lru_cache(None)(lambda x: defect(x, r))
    counts, histograms, digests = {}, {}, {}
    for step in (1, 2, 4):
        row, hist, hashes = [], [], []
        for j in range(d):
            sigs = Counter()
            for x in values:
                sig = []
                for k in range(q // math.gcd(q, step)):
                    y = list(x)
                    y[j] = (y[j] + k*step) % q
                    sig.append(local_defect(tuple(y)))
                sigs[tuple(sig)] += 1
            row.append(len(sigs))
            hist.append({str(a): b for a, b in sorted(Counter(sigs.values()).items())})
            stream = json.dumps(sorted(sigs.items()), separators=(",", ":")).encode()
            hashes.append(hashlib.sha256(stream).hexdigest())
            keys = set(sigs)
            rotated = {s[1:] + s[:1] for s in keys}
            inverse = {s[-1:] + s[:-1] for s in keys}
            require(rotated == keys == inverse, "signature update permutation")
        counts[str(step)], histograms[str(step)], digests[str(step)] = row, hist, hashes
    return {"rank": r, "q": q, "dimension": d, "inputs": len(values),
            "counts_by_step_all_coordinates": counts,
            "fiber_histograms": histograms,
            "signature_fiber_sha256": digests}


def character_quotient_counts(r):
    q, pairs, orders = quotient_representatives(r, include_characters=True)
    _, columns = character_columns(r)
    values = {char: defect(rep, r) for char, rep in pairs}
    d = 2 << r
    counts, histograms, digests = {}, {}, {}
    for step in (1, 2, 4):
        row, hist, hashes = [], [], []
        for j, col in enumerate(columns):
            sigs = Counter()
            for char in values:
                sig = tuple(values[tuple((a + k*step*b) % q
                                         for a, b in zip(char, col))]
                            for k in range(q // math.gcd(q, step)))
                sigs[sig] += 1
            row.append(len(sigs))
            hist.append({str(a): b for a, b in sorted(Counter(sigs.values()).items())})
            stream = json.dumps(sorted(sigs.items()), separators=(",", ":")).encode()
            hashes.append(hashlib.sha256(stream).hexdigest())
            keys = set(sigs)
            require({s[1:] + s[:1] for s in keys} == keys, "forward quotient action")
            require({s[-1:] + s[:-1] for s in keys} == keys, "inverse quotient action")
        counts[str(step)], histograms[str(step)], digests[str(step)] = row, hist, hashes
    return {"rank": r, "q": q, "dimension": d, "inputs": len(values),
            "counts_by_step_all_coordinates": counts,
            "fiber_histograms": histograms, "signature_fiber_sha256": digests,
            "quotient_extension_orders": orders,
            "quotient_representative_sha256": hashlib.sha256(
                json.dumps(pairs, separators=(",", ":")).encode()).hexdigest()}


def controls():
    local = signed = 0
    for x in product(range(-3, 4), repeat=4):
        p, q = (x[0] - x[2]) % 2, (x[1] - x[3]) % 2
        require(defect(x, 1) == (q-p, p-q, q-p, p-q), "signed pair identity")
        local += 1
    for r in (1, 2, 3):
        d, q = 2 << r, 1 << (r//2 + 1)
        for seed in range(7):
            x = tuple((-1 if i % 2 else 1) * (seed+1) * (i*i+3) for i in range(d))
            z = tuple((i%3)-1 for i in range(d))
            y = tuple(a + q*b for a, b in zip(x, z))
            require(defect(x, r) == defect(y, r), "signed scalar period")
            signed += 1
    witness = (1, 0, 0, 1)
    require(literal(witness, 1, mutation=True) != literal(witness, 1), "sign mutation survived")
    require(defect((0, 0, 0, 0), 1) == defect((0, 0, 1, 1), 1), "pointwise collision")
    require(defect((1, 0, 0, 0), 1) != defect((1, 0, 1, 1), 1), "update witness")
    require(any(defect(x, 2) != defect(tuple(v + (2 if i == 0 else 0)
                for i, v in enumerate(x)), 2)
                for x in product(range(2), repeat=8)), "bad period not detected")
    return {"signed_pair_cases": local, "signed_scalar_period_fixtures": signed,
            "rejected": ["literal_rotation_sign", "pointwise_update", "rank2_scalar_period2"]}


def run(include_rank3=False):
    receipt = {"controls": controls(), "raw_boxes": [family_counts(1), family_counts(2)]}
    if include_rank3:
        receipt["rank3_independent_character_quotient"] = character_quotient_counts(3)
    return receipt


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--rank3", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args.rank3), indent=2, sort_keys=True))
