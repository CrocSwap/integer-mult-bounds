"""Exact canonical cuts for cyclic readers. Produced by Nick Petalas.

Apache-2.0. The child contract and rotation tariffs are inherited from
Ross Richardson's cyclic-output-restoration, PR1287. No predecessor code runs.
"""

import argparse
import hashlib
import json
from fractions import Fraction
from itertools import product
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parameters(k, a, b):
    require(type(k) is int and 1 <= k <= 4096, "child count outside 1..4096")
    for price in (a, b):
        require(type(price) in (int, Fraction), "exact price required")
        require(0 < price <= 4096, "price outside (0,4096]")
        require(Fraction(price).denominator <= 4096, "price denominator too large")


def boundary_cost(k, a, b):
    parameters(k, a, b)
    if a <= b:
        return k * a
    r = k % 3
    correction = (0, a - b, min(2 * (a - b), a))[r]
    return k * b + correction


def increments(k, a, b):
    """One attaining sequence of aligned-phase differences."""
    parameters(k, a, b)
    if a <= b:
        return (0,) * k
    r = k % 3
    if r == 2 and a >= 2 * b:
        return (2,) + (1,) * (k - 1)
    return (0,) * r + (1,) * (k - r)


def checked_lengths(lengths):
    require(type(lengths) is tuple and 1 <= len(lengths) <= 64, "invalid segments")
    require(all(type(k) is int and 1 <= k <= 256 for k in lengths), "invalid length")
    require(sum(lengths) <= 256, "schedule exceeds 256 children")


def schedule(lengths, a, b):
    """Post-child workspace/output powers, with zero entrance powers."""
    checked_lengths(lengths)
    result = []
    for k in lengths:
        result.extend(((d - 1) % 3, d) for d in increments(k, a, b))
    assert len(result) == sum(lengths)
    return tuple(result)


def composition(k, mask):
    """Every ordered positive composition of k, indexed by its cut mask."""
    require(1 <= k <= 8 and 0 <= mask < 1 << (k - 1), "invalid cut mask")
    cuts = [0] + [i for i in range(1, k) if mask & (1 << (i - 1))] + [k]
    return tuple(y - x for x, y in zip(cuts, cuts[1:]))


def oracle_cost(lengths, a, b):
    """Nine physical phase states; permit every entrance and gap power."""
    checked_lengths(lengths)
    cuts = set()
    end = 0
    for k in lengths:
        end += k
        cuts.add(end)
    states = {(p, q): a * (p != 0) + b * (q != 0)
              for p, q in product(range(3), repeat=2)}
    for child in range(1, end + 1):
        following = {}
        for t in range(3):
            if (t, t) not in states:
                continue
            start = states[t, t]
            for p, q in product(range(3), repeat=2):
                value = start + a * (p != (t + 1) % 3) + b * (q != t)
                key = (p, q)
                if key not in following or value < following[key]:
                    following[key] = value
        states = {(0, 0): following[0, 0]} if child in cuts else following
    return states[0, 0]


def check_prices():
    cases = penalty_cases = 0
    for a, b in product(range(1, 9), repeat=2):
        bound = 0 if a <= b else a - b + min(2 * (a - b), a)
        penalties = []
        for k in range(1, 9):
            for mask in range(1 << (k - 1)):
                lengths = composition(k, mask)
                expected = sum(boundary_cost(n, a, b) for n in lengths)
                require(oracle_cost(lengths, a, b) == expected, "checkpoint optimum")
                word = schedule(lengths, a, b)
                actual = sum(a * (u != 0) + b * (v != 0) for u, v in word)
                require(actual == expected, "attaining schedule price")
                cases += 1
        for left, right in product(range(1, 13), repeat=2):
            delta = (boundary_cost(left, a, b) + boundary_cost(right, a, b)
                     - boundary_cost(left + right, a, b))
            require(0 <= delta <= bound, "one-cut surcharge bound")
            penalties.append(delta)
            penalty_cases += 1
        require(max(penalties) == bound, "sharp one-cut surcharge")
    rational_cases = 0
    for a, b in product((Fraction(1, 3), Fraction(3, 4), Fraction(5, 2)), repeat=2):
        for k in range(1, 9):
            require(boundary_cost(k, a, b) == oracle_cost((k,), a, b), "rational price")
            rational_cases += 1
    return dict(checkpoint_optima=cases, one_cut_pairs=penalty_cases,
                rational_price_cases=rational_cases)


def rotate(values, power):
    require(power in (0, 1, 2), "invalid power")
    require(len(values) % 3 == 0 and len(values) <= 12, "invalid bank width")
    result = [0] * len(values)
    for i, value in enumerate(values):
        result[3 * (i // 3) + (i + power) % 3] = value
    return result


def reader(child, m, n):
    return [[((child + 1) * (r // 3 + 1) + 2 * (c // 3) + (r - c) % 3) % 5 - 2
             for c in range(3 * m)] for r in range(3 * n)]


def image(matrix, vector):
    return [sum(x * y for x, y in zip(row, vector)) for row in matrix]


def run_batch(lengths, m, n, source, output, word):
    """Literal rotations and periodic circulant readers, including each cut."""
    checked_lengths(lengths)
    require(1 <= m <= 4 and 1 <= n <= 3, "invalid literal dimensions")
    require(len(source) == 3 * m and len(output) == 3 * n, "invalid input shape")
    require(len(word) == sum(lengths), "invalid word length")
    original = source[:]
    expected = output[:]
    cuts = set()
    end = 0
    for k in lengths:
        end += k
        cuts.add(end)
    for j, (u, v) in enumerate(word):
        matrix = reader(j, m, n)
        output = [x + y for x, y in zip(output, image(matrix, source))]
        source = rotate(source, 1)
        source, output = rotate(source, u), rotate(output, v)
        expected = [x + y for x, y in zip(expected, image(matrix, original))]
        if j + 1 in cuts:
            require(source == original, "source noncanonical at cut")
            require(output == expected, "wrong output at canonical cut")
    return source, output


def check_literal():
    fixtures = probes = 0
    for m, n in product(range(1, 5), range(1, 4)):
        width = 3 * (m + n)
        for k in range(1, 7):
            for mask in range(1 << (k - 1)):
                lengths = composition(k, mask)
                word = schedule(lengths, m, n)
                for column in range(width + 1):
                    probe = ([int(i == column) for i in range(width)] if column < width
                             else [Fraction((-1) ** i * (i + 1), 7) for i in range(width)])
                    run_batch(lengths, m, n, probe[:3 * m], probe[3 * m:], word)
                    probes += 1
                fixtures += 1
    return dict(literal_fixtures=fixtures, arbitrary_dirty_basis_and_rational_probes=probes)


def check_controls():
    rejected = 0
    invalid = ((0, 1, 1), (True, 1, 1), (4097, 1, 1), (2, 0, 1),
               (2, 1.0, 1), (2, True, 1), (2, 1, Fraction(1, 4097)))
    for args in invalid:
        try:
            boundary_cost(*args)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid parameter accepted")
    for lengths in ((), (0,), (257,), (1,) * 65, (128, 129), [2, 1]):
        try:
            schedule(lengths, 3, 1)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid schedule accepted")
    require(boundary_cost(2, 3, 1) == 5 != 6, "residue-two alternate essential")
    require(boundary_cost(2, 3, 2) == 6 != 7, "two workspace restores essential")
    require(oracle_cost((1, 2), 3, 1) == 8 != boundary_cost(3, 3, 1),
            "ignoring checkpoint must change optimum")
    try:
        run_batch((1, 2), 3, 1, list(range(9)), [3, 4, 5], schedule((3,), 3, 1))
    except ValueError:
        rejected += 1
    else:
        raise ValueError("noncanonical mutant accepted")
    require(len(schedule((256,), 3, 1)) == 256, "maximum schedule capacity")
    require(len(schedule((1,) * 64, 3, 1)) == 64, "maximum segment capacity")
    require(boundary_cost(4096, 4096, 4096) == 4096 ** 2, "maximum formula capacity")
    return dict(rejected_inputs_and_word_mutants=rejected, formula_mutant_controls=3)


def result():
    counts = check_prices()
    counts.update(check_literal())
    counts.update(check_controls())
    package = Path(__file__).resolve().parent
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
              for name in ("verify.py", "README.md", "TASK.json", "SOURCES.json", "VERIFY.json")}
    return dict(schema_version=1, claim_type="scoped proof with finite corroboration",
                source_sha256=hashes, counts=counts,
                five_children_A3_B1=dict(
                    no_cut=boundary_cost(5, 3, 1),
                    cut_after_2=oracle_cost((2, 3), 3, 1),
                    cut_after_1=oracle_cost((1, 4), 3, 1), eager=5 * 3,
                    one_cut_maximum=max(boundary_cost(u, 3, 1) + boundary_cost(v, 3, 1)
                                        - boundary_cost(u + v, 3, 1)
                                        for u, v in product(range(1, 4), repeat=2))),
                status="PASS_CYCLIC_CHECKPOINT_COST", no_new_kappa=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path, help="write a new receipt; never overwrite")
    args = parser.parse_args()
    payload = result()
    encoded = json.dumps(payload, sort_keys=True, indent=2) + "\n"
    if args.write_result is not None:
        with args.write_result.open("x", encoding="utf-8") as handle:
            require(handle.write(encoded) == len(encoded), "short receipt write")
    else:
        receipt = Path(__file__).resolve().with_name("RESULT.json")
        actual = json.dumps(json.loads(receipt.read_text()), sort_keys=True, indent=2) + "\n"
        require(actual == encoded, "receipt or source hash mismatch")
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
