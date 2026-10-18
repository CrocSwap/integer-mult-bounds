#!/usr/bin/env python3
"""Independent finite equality-model verification; Python 3.10+, stdlib only.

Copyright 2026 Sam Sung. Apache-2.0. Substantial OpenAI Codex assistance.
No assertion statements: checks remain active with -I -O.
"""
import argparse
from collections import defaultdict
import hashlib
from itertools import combinations, product
import json
from math import comb
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def ports(p, degree):
    return [sum(1 << (2 * pair + sign) for pair, sign in zip(pairs, signs))
            for pairs in combinations(range(p), degree)
            for signs in product(range(2), repeat=degree)]


def coordinates(port):
    return [i for i in range(port.bit_length()) if port >> i & 1]


def row(star, family):
    return sum(1 << i for i, port in enumerate(family) if port & star == star)


def basis(rows):
    pivots = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return pivots


def residual(value, pivots):
    for pivot in sorted(pivots, reverse=True):
        if value >> pivot & 1:
            value ^= pivots[pivot]
    return value


def model(p, k):
    family = ports(p, k)
    stars = [s for degree in range(1, k) for s in ports(p, degree)]
    rows = [row(star, family) for star in stars]
    return family, stars, rows, basis(rows + [(1 << len(family)) - 1])


def cube_mask(dimensions, family):
    cube = [sum(1 << coordinate for coordinate in choice)
            for choice in product(*dimensions)]
    require(len(set(cube)) == 2 ** len(dimensions), "degenerate generalized cube")
    require(set(cube) <= set(family), "cube contains an inadmissible port")
    return sum(1 << i for i, port in enumerate(family) if port in set(cube))


def rigidity_cubes(k, family):
    """Two geometric parity families: constant signs within/between blocks."""
    within, between = [], []
    extras = list(range(k - 1, k + 2))
    for a in range(k - 1):
        other = [(2 * i, 2 * i + 1) for i in range(k - 1) if i != a]
        for b in extras:
            c = next(c for c in extras if c != b)
            within.append(cube_mask(other + [(2 * a, 2 * c), (2 * b, 2 * b + 1)], family))
        for b, c in combinations(extras, 2):
            d = next(d for d in extras if d not in (b, c))
            between.append(cube_mask(other + [(2 * a, 2 * d), (2 * b, 2 * c)], family))
    return within, between


def parity_valid(word, checks):
    return all((word & check).bit_count() % 2 == 0 for check in checks)


def census(k):
    p = k + 2
    family, stars, rows, pivots = model(p, k)
    index = {port: i for i, port in enumerate(family)}
    blocks = []
    for extra in range(k - 1, p):
        mask = sum(3 << (2 * pair) for pair in [*range(k - 1), extra])
        block = [port for port in family if port & mask == port]
        require(len(block) == 2 ** k, "block cardinality")
        syndromes = [residual(1 << index[port], pivots) for port in block]
        blocks.append([(syndromes[a] ^ syndromes[b], (block[a], block[b]))
                       for a, b in combinations(range(len(block)), 2)])
    pair_sums = defaultdict(list)
    for a, (sa, _) in enumerate(blocks[0]):
        for b, (sb, _) in enumerate(blocks[1]):
            pair_sums[sa ^ sb].append((a, b))
    within, between = rigidity_cubes(k, family)
    require(all(parity_valid(generator, within + between)
                for generator in rows + [(1 << len(family)) - 1]), "dual cube certificate")
    solutions = []
    for sc, pairc in blocks[2]:
        for a, b in pair_sums.get(sc, []):
            support = sorted((*blocks[0][a][1], *blocks[1][b][1], *pairc))
            word = sum(1 << index[port] for port in support)
            common = support[0]
            for port in support[1:]:
                common &= port
            require(common.bit_count() == k - 1, "non-star member of equality model")
            require(row(common, family) == word, "literal global-star evaluation")
            require(word.bit_count() == 6, "sharp star weight at q=2")
            require(parity_valid(word, within + between), "member violates geometric parity")
            solutions.append(support)
    require(len(solutions) == 2 ** (k - 1), "equality-model solution count")
    representative = solutions[0]
    word = sum(1 << index[port] for port in representative)
    corrupt = word ^ (1 << index[representative[0]])
    require(residual(corrupt, pivots) != 0, "corrupt-support control")
    # Flip one common sign in both ports of one block. Each block stays rigid,
    # but the altered block disagrees with the other two blocks.
    block_pair = [port for port in representative if port & (3 << (2 * (k - 1)))]
    altered_support = set(representative) - set(block_pair)
    altered_support.update(port ^ 3 for port in block_pair)
    altered = sum(1 << index[port] for port in altered_support)
    require(parity_valid(altered, within) and not parity_valid(altered, between),
            "missing cross-block parity control")
    require(residual(altered, pivots) != 0, "asymmetric-sign support control")
    return dict(k=k, p=p, ports=len(family), nonempty_star_rank=len(basis(rows)),
                rank_with_empty_star=len(pivots), pairs_per_block=comb(2 ** k, 2),
                logical_supports=comb(2 ** k, 2) ** 3,
                distinct_pair_sums=len(pair_sums), member_supports=len(solutions),
                all_members_are_literal_stars=True,
                generalized_cubes=len(within) + len(between),
                generator_rows_sha256=digest(rows), support_census_sha256=digest(solutions),
                representative_support=[coordinates(port) for port in representative])


def two_target_case(k, q, literal=False):
    p = k + q
    family = ports(p, k)
    index = {port: i for i, port in enumerate(family)}
    common_port = sum(1 << (2 * pair) for pair in range(k))
    stars = [common_port ^ (1 << coordinate) for coordinate in (0, 2)]
    words = [row(star, family) for star in stars]
    require(all(word.bit_count() == 2 * (q + 1) for word in words), "two-target star weights")
    require((words[0] & words[1]).bit_count() == 1, "two stars must meet once")
    targets = [index[star | (1 << (2 * k))] for star in stars]
    target_mask = sum(1 << i for i in targets)
    deleted = (words[0] | words[1]) ^ target_mask
    require(deleted.bit_count() == 4 * q + 1, "two-target deletion count")
    require(all(word & ~deleted == 1 << targets[a] for a, word in enumerate(words)),
            "two-target decoder identity on every surviving port")
    restored = [i for i in range(len(family)) if deleted >> i & 1]
    require(all(any(word & ~(deleted ^ (1 << i)) != 1 << targets[a]
                    for a, word in enumerate(words)) for i in restored), "restoration controls")
    result = dict(p=p, k=k, q=q, ports=len(family),
                  union_weight=(words[0] | words[1]).bit_count(), deletions=deleted.bit_count(),
                  restoration_failures=len(restored), deleted_mask_sha256=digest(hex(deleted)))
    if literal:
        result.update(stars=[coordinates(s) for s in stars],
                      targets=[coordinates(family[i]) for i in targets],
                      deleted_ports=[coordinates(family[i]) for i in restored])
    return result


def small_second_weights():
    results = []
    for p in range(4, 7):
        family, _, _, pivots = model(p, 2)
        words = [0]
        for generator in pivots.values():
            words += [word ^ generator for word in words]
        require(len(set(words)) == 2 ** len(pivots), "independent codeword enumeration")
        weights = [word.bit_count() for word in words]
        minimum, examined, attaining = len(family), 0, defaultdict(int)
        for a in range(1, len(words)):
            for b in range(a + 1, len(words)):
                c = a ^ b
                if b >= c:  # Exactly the two smallest labels of each 2D subspace.
                    continue
                examined += 1
                support_size = (words[a] | words[b]).bit_count()
                if support_size < minimum:
                    minimum, attaining = support_size, defaultdict(int)
                if support_size == minimum:
                    attaining[tuple(sorted((weights[a], weights[b], weights[c])))] += 1
        expected_count = (len(words) - 1) * (len(words) - 2) // 6
        require(examined == expected_count, "complete two-dimensional subcode count")
        require(minimum == 4 * (p - 2) + 3, "exhaustive second generalized weight")
        distance = 2 * (p - 1)
        require(min(weights[1:]) == distance, "exhaustive minimum word weight")
        require(attaining == {(distance, distance, 2 * distance - 2): len(family)},
                "optimal subcodes must be exactly the adjacent-star spans")
        results.append(dict(k=2, p=p, ports=len(family), code="C+ including empty star",
                            rank=len(pivots), codewords=len(words), subcodes=examined,
                            minimum_word_weight=min(weights[1:]), second_weight=minimum,
                            attaining_weight_triples={str(key): count for key, count in sorted(attaining.items())}))
    return results


def boundary_and_two_targets():
    family, _, _, pivots = model(5, 4)
    low_star, outside = (1 << 0) | (1 << 2), (8, 9)
    coefficient_stars = [low_star] + [low_star | (1 << c) for c in outside]
    exceptional = 0
    for star in coefficient_stars:
        exceptional ^= row(star, family)
    support = [port for i, port in enumerate(family) if exceptional >> i & 1]
    require(len(support) == 4 and residual(exceptional, pivots) == 0, "q=1 exception")
    require(all(row(star, family) != exceptional for star in ports(5, 3)),
            "q=1 exception must be non-star")
    exception = dict(p=5, k=4, coefficient_stars=[coordinates(s) for s in coefficient_stars],
                     support=[coordinates(port) for port in support],
                     role="q=1 counterexample to extending equality rigidity below q=2")
    family = ports(6, 4)
    # A nonzero coefficient vector can represent the zero function.
    singleton = 1 << 0
    redundant = [singleton] + [s for s in ports(6, 2) if s & singleton]
    zero_word = 0
    for star in redundant:
        zero_word ^= row(star, family)
    require(len(redundant) > 0 and zero_word == 0, "coefficients are not codewords")
    return exception, two_target_case(4, 2, literal=True), len(redundant)


def prescribed_pairs(k, q):
    p = k + q
    family = ports(p, k)
    size = len(family)
    star_rows = {star: row(star, family) for star in ports(p, k - 1)}
    covered, spans, evaluations = set(), set(), 0

    def indices(mask):
        result = []
        while mask:
            bit = mask & -mask
            result.append(bit.bit_length() - 1)
            mask ^= bit
        return result

    for port in family:
        for a, b in combinations(coordinates(port), 2):
            stars = tuple(sorted((port ^ (1 << a), port ^ (1 << b))))
            require(stars not in spans, "duplicate adjacent-star span")
            spans.add(stars)
            left, right = [star_rows[star] for star in stars]
            require((left & right).bit_count() == 1, "adjacent-star intersection")
            columns = {1: indices(left & ~right), 2: indices(right & ~left), 3: indices(left & right)}
            combinations_of_rows = {1: left, 2: right, 3: left ^ right}
            for first, second in combinations(columns, 2):
                decoder = [next(word for c, word in combinations_of_rows.items()
                                if (c & own).bit_count() % 2 == 1
                                and (c & other).bit_count() % 2 == 0)
                           for own, other in [(first, second), (second, first)]]
                for i, j in product(columns[first], columns[second]):
                    deleted = (left | right) ^ (1 << i) ^ (1 << j)
                    require(deleted.bit_count() == 4 * q + 1, "near-target deletion count")
                    require(decoder[0] & ~deleted == 1 << i and decoder[1] & ~deleted == 1 << j,
                            "near-target full-port unit identities")
                    covered.add(min(i, j) * size + max(i, j))
                    evaluations += 1
    require(len(spans) == size * comb(k, 2), "adjacent-span count")
    expected, distant, unsigned_control = set(), 0, None
    for i, j in combinations(range(size), 2):
        pair_id = i * size + j
        if (family[i] & family[j]).bit_count() >= k - 2:
            expected.add(pair_id)
            continue
        words = [star_rows[family[t] ^ (1 << (family[t].bit_length() - 1))] for t in (i, j)]
        require(words[0] & words[1] == 0, "distant stars must be disjoint")
        deleted = (words[0] | words[1]) ^ (1 << i) ^ (1 << j)
        require(deleted.bit_count() == 4 * q + 2, "distant-target deletion count")
        require(words[0] & ~deleted == 1 << i and words[1] & ~deleted == 1 << j,
                "distant-target full-port unit identities")
        distant += 1
        pair_sets = [{c // 2 for c in coordinates(family[t])} for t in (i, j)]
        if len(pair_sets[0] & pair_sets[1]) >= k - 2 and unsigned_control is None:
            require(pair_id not in covered, "unsigned intersection incorrectly accepted")
            unsigned_control = [coordinates(family[i]), coordinates(family[j])]
    require(covered == expected, "prescribed-pair signed-intersection criterion")
    require(k == 2 or unsigned_control is not None, "missing unsigned-intersection control")
    return dict(k=k, p=p, q=q, ports=size, adjacent_spans=len(spans), near_target_pairs=len(covered),
                distant_target_pairs=distant, near_decoder_checks=evaluations,
                near_deletions=4 * q + 1, distant_deletions=4 * q + 2,
                covered_pairs_sha256=digest(sorted(covered)),
                unsigned_intersection_counterexample=unsigned_control)


def verify():
    cases = [census(k) for k in range(2, 6)]
    exception, two_targets, relation_size = boundary_and_two_targets()
    witness_grid = [two_target_case(k, q) for k in range(2, 7) for q in range(2, 7)]
    return dict(status="PASS", arithmetic="exact F2 integer bitsets", cases=cases,
                scope="Equality census fixes k-1 common pairs at q=2; it is not a full codeword search. "
                      "Second-weight enumeration is complete for the listed k=2 codes. "
                      "General proofs are in MINIMUM-WORDS.md.",
                q1_nonstar_counterexample=exception, two_target_witness=two_targets,
                two_target_witness_grid=witness_grid, exhaustive_second_weights=small_second_weights(),
                two_target_scope="Grid entries verify attaining witnesses; uniform lower bounds are proved in MINIMUM-WORDS.md.",
                prescribed_pair_coverage=[prescribed_pairs(k, q) for k in range(2, 5) for q in (2, 3)],
                prescribed_pair_scope="All target pairs checked for proper-star observations in the listed cases; "
                                      "uniform classification is proved in EQUALITY-PAIR.md. "
                                      "Overlap corrections preserve these thresholds only at power-of-two k.",
                negative_controls=["corrupt support rejected in all four cases",
                                   "omitting between-block parity admits false supports in all four cases",
                                   "q=1 non-star minimum support invalidates a weakened hypothesis",
                                   f"nonzero {relation_size}-coefficient vector has zero evaluated function",
                                   "all 425 one-port restorations break the respective two-target witnesses",
                                   "unsigned pair-index overlap falsely predicts attainable nearby-target decoders"])


def self_test(result):
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        script = directory / "global_verify.py"
        script.write_bytes(Path(__file__).read_bytes())
        receipt = directory / "GLOBAL-RESULTS.json"
        receipt.write_text(json.dumps(result))
        command = [sys.executable, "-I", "-O", "-B", str(script)]
        run = subprocess.run(command, capture_output=True, text=True)
        require(run.returncode == 0, f"minimal relocated optimized replay: {run.stderr}")
        damaged = dict(result, status="CORRUPTED")
        receipt.write_text(json.dumps(damaged))
        protected = directory / "protected.json"
        protected.write_text("preserve this output\n")
        run = subprocess.run(command + ["--check", str(receipt), "--write", str(protected)],
                             capture_output=True, text=True)
        require(run.returncode != 0, "tampered receipt accepted")
        require(protected.read_text() == "preserve this output\n", "failed check overwrote output")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write receipt only after all requested checks pass")
    parser.add_argument("--check", type=Path, help="compare this receipt before any output write")
    parser.add_argument("--self-test", action="store_true", help="test relocation and failure preservation")
    args = parser.parse_args()
    result = verify()
    if args.check or not args.write:
        receipt = args.check or HERE / "GLOBAL-RESULTS.json"
        require(json.loads(receipt.read_text()) == result, f"receipt mismatch: {receipt}")
    if args.self_test:
        self_test(result)
    if args.write:
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS_GLOBAL_EQUALITY: 4 complete equality models; "
          f"{sum(case['logical_supports'] for case in result['cases'])} candidate supports; "
          "30 stars; 3 complete k=2 codes; 25 two-target witnesses; "
          f"{sum(case['near_target_pairs'] + case['distant_target_pairs'] for case in result['prescribed_pair_coverage'])} "
          "prescribed target pairs; 6 control categories")


if __name__ == "__main__":
    main()
