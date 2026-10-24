"""Exact BW16 insertion thresholds around DaysSky's fixed 72-line clique."""

import argparse
from collections import Counter
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys
import time


HERE = Path(__file__).resolve().parent
SOURCE_SHA256 = "c16f23f68fd3e840216032df458dbd8f281822fbe1e829aeb06710e4372d0d99"
EXPECTED_PAIRS = {
    30: 11340, 34: 30240, 35: 30240, 40: 127008, 42: 56700,
    43: 75600, 44: 15120, 46: 117180, 47: 120960, 48: 105840,
    49: 98280, 50: 211680, 51: 181440, 52: 7560, 53: 7560,
    54: 21420, 56: 90720, 58: 8100,
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dot(left, right):
    return sum(x * y for x, y in zip(left, right, strict=True))


def member(vector):
    """Test Construction D directly, separately from shell enumeration."""
    if len(vector) != 16 or any(type(x) is not int for x in vector):
        return False
    low = tuple(x % 2 for x in vector)
    constant = low[0]
    coefficients = tuple(low[1 << j] ^ constant for j in range(4))
    for point in range(16):
        value = constant
        for j in range(4):
            value ^= coefficients[j] * ((point >> j) & 1)
        if value != low[point]:
            return False
    return sum((x - c) // 2 for x, c in zip(vector, low, strict=True)) % 2 == 0


def shell():
    """Canonical norm-eight lines, using the two cited shell shapes."""
    vectors = []
    for i, j in combinations(range(16), 2):
        for sign in (-2, 2):
            vector = [0] * 16
            vector[i], vector[j] = 2, sign
            vectors.append(tuple(vector))
    for normal in range(1, 16):
        for constant in range(2):
            support = tuple(i for i in range(16)
                            if ((normal & i).bit_count() + constant) % 2)
            need(len(support) == 8, "affine hyperplane size")
            for signs in range(128):
                if signs.bit_count() % 2:
                    continue
                vector = [0] * 16
                vector[support[0]] = 1
                for j in range(1, 8):
                    vector[support[j]] = -1 if signs >> (j - 1) & 1 else 1
                vectors.append(tuple(vector))
    result = tuple(sorted(vectors))
    need(len(result) == len(set(result)) == 2160, "shell size/distinctness")
    need(all(member(v) and dot(v, v) == 8 for v in result), "shell membership")
    return result


def load_clique():
    path = HERE / "CLIQUE72.json"
    need(path.stat().st_size < 30000, "source size cap")
    raw = path.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, "source bytes")
    data = json.loads(raw)
    need(isinstance(data, list) and len(data) == 72, "clique shape")
    need(all(isinstance(v, list) and len(v) == 16 for v in data), "vector shape")
    clique = tuple(tuple(v) for v in data)
    need(len(set(clique)) == 72, "distinct source lines")
    need(all(member(v) and dot(v, v) == 8 for v in clique), "source membership")
    need(all(dot(v, w) != 0 for v, w in combinations(clique, 2)), "source premise")
    return clique


def signed_bits(vector):
    positive = sum(1 << i for i, x in enumerate(vector) if x > 0)
    negative = sum(1 << i for i, x in enumerate(vector) if x < 0)
    scale = max(map(abs, vector))
    need(all(x == 0 or abs(x) == scale for x in vector), "constant nonzero scale")
    return positive, negative, scale


def bit_dot(left, right):
    lp, ln, ls = left
    rp, rn, rs = right
    return ls * rs * ((lp & rp).bit_count() + (ln & rn).bit_count()
                      - (lp & rn).bit_count() - (ln & rp).bit_count())


def missing_sets(outside, clique):
    result = tuple(sum(1 << j for j, old in enumerate(clique) if dot(v, old) == 0)
                   for v in outside)
    histogram = Counter(bits.bit_count() for bits in result)
    need(histogram == {20: 378, 29: 1080, 36: 630}, "single insertion histogram")
    return result, histogram


def pair_census(outside, missing, literal):
    encoded = tuple(signed_bits(v) for v in outside)
    counts = Counter()
    witness = None
    for i in range(2088):
        for j in range(i):
            product = (dot(outside[i], outside[j]) if literal
                       else bit_dot(encoded[i], encoded[j]))
            if product == 0:
                continue
            deleted = (missing[i] | missing[j]).bit_count()
            need(deleted >= 30, "two compatible new lines delete at least thirty")
            counts[deleted] += 1
            if deleted == 30 and witness is None:
                witness = i, j
    need(dict(counts) == EXPECTED_PAIRS, "complete compatible-pair histogram")
    need(sum(counts.values()) == 1316988, "compatible pair total")
    need(witness is not None, "two-insertion bound is attained")
    return counts, witness


def attainments(outside, missing, pair, clique):
    one = next(i for i in range(2088) if missing[i].bit_count() == 20)
    for deleted in range(20, 30):
        mask = missing[one]
        extras = tuple(j for j in range(72) if not (mask >> j & 1))
        for j in extras[:deleted - 20]:
            mask |= 1 << j
        kept = tuple(v for j, v in enumerate(clique) if not (mask >> j & 1))
        need(len(kept) + 1 == 73 - deleted, "exact deletion-size attainment")
        need(all(dot(outside[one], v) != 0 for v in kept), "one-line attainment")
    i, j = pair
    mask = missing[i] | missing[j]
    kept = tuple(v for k, v in enumerate(clique) if not (mask >> k & 1))
    need(len(kept) == 42 and dot(outside[i], outside[j]) != 0, "two-line attainment")
    need(all(dot(v, w) != 0 for v in kept for w in (outside[i], outside[j])),
         "two-line retained contacts")
    return {"one": outside[one], "two": (outside[i], outside[j])}


def controls(clique, outside):
    bad = list(outside[0])
    bad[0] += 1
    need(not member(tuple(bad)), "nonaffine-residue control")
    bad_sign = list(next(v for v in outside if max(map(abs, v)) == 1))
    first = next(i for i, x in enumerate(bad_sign) if x)
    bad_sign[first] *= -1
    need(not member(tuple(bad_sign)), "odd sign parity control")
    need(dot(clique[0], clique[0]) == 8, "nonzero self contact")
    need(sum(dot(clique[0], v) == 0 for v in clique) == 0,
         "old-line admission would give zero deletions")
    for v in outside:
        encoded = signed_bits(v)
        need(bit_dot(encoded, encoded) == dot(v, v) == 8, "encoded scale")
        negated = tuple(-x for x in v)
        need(bit_dot(encoded, signed_bits(negated)) == -8, "signed-dot control")
    return 4 + 2 * len(outside)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--literal", action="store_true", help="use direct integer dot products")
    args = parser.parse_args()
    started = time.monotonic()
    clique = load_clique()
    vectors = shell()
    old = set(clique)
    need(old <= set(vectors), "source clique belongs to enumerated shell")
    outside = tuple(v for v in vectors if v not in old)
    need(len(outside) == 2088, "outside domain")
    missing, singles = missing_sets(outside, clique)
    pairs, witness = pair_census(outside, missing, args.literal)
    attaining = attainments(outside, missing, witness, clique)
    control_count = controls(clique, outside)
    paths = tuple(sorted(p for p in HERE.iterdir() if p.is_file()))
    receipt = {
        "claim_type": "finite certificate and scoped combinatorial proof",
        "shell_lines": len(vectors), "outside_lines": len(outside),
        "single_histogram": dict(singles), "pair_histogram": dict(pairs),
        "compatible_pairs": sum(pairs.values()), "one_threshold": 20,
        "two_threshold": 30, "attainments": attaining, "controls": control_count,
        "literal": args.literal, "python": sys.version.split()[0],
        "package_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
    }
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_BW16_CLIQUE_EXCHANGE_BARRIER", "one=20", "two=30",
          "outside=2088", "compatible_pairs=1316988", f"seconds={time.monotonic()-started:.3f}")


if __name__ == "__main__":
    main()
