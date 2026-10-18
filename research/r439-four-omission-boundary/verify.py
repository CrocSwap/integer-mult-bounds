#!/usr/bin/env python3
"""Exact chronological four-omission census. Apache-2.0.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
Transported-transvection reduction: woklerx, PR1446/PR1017.
"""
from bisect import bisect_left
from collections import defaultdict
import argparse
import gzip
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/r439-helper-stars-seed19/candidate.json.gz"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parity(x):
    return x.bit_count() & 1


def replay(gates, width, omitted=()):
    rows = [1 << i for i in range(width)]
    omitted = set(omitted)
    for i, (dst, src) in enumerate(gates):
        if i not in omitted:
            rows[dst] ^= rows[src]
    return rows


def row_times(vector, rows):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= rows[bit.bit_length() - 1]
        vector ^= bit
    return result


def compose(left, right):
    return [row_times(row, right) for row in left]


def transvection_rows(factor, width):
    u, v = factor
    return [(1 << i) ^ (v if (u >> i) & 1 else 0)
            for i in range(width)]


def factors_from_suffixes(gates, width):
    """u=B e_dst, v=e_src^T B^-1, using exact baseline suffixes B."""
    columns = [1 << i for i in range(width)]
    inverse_rows = columns.copy()
    factors = [None] * len(gates)
    for i in range(len(gates) - 1, -1, -1):
        dst, src = gates[i]
        require(0 <= dst < width and 0 <= src < width and dst != src,
                "invalid elementary ADD")
        factors[i] = (columns[dst], inverse_rows[src])
        columns[src] ^= columns[dst]
        inverse_rows[dst] ^= inverse_rows[src]
    return factors


def check_factors(gates, width, factors, literal_singles=False):
    """Separate forward-prefix construction; optionally every literal omission."""
    baseline = replay(gates, width)
    inverse = replay(gates[::-1], width)
    require(compose(baseline, inverse) == [1 << i for i in range(width)],
            "baseline inverse")
    prefixes = [1 << i for i in range(width)]
    for i, (dst, src) in enumerate(gates):
        u, v = factors[i]
        incoming = prefixes[src]
        require(v == row_times(incoming, inverse), "incoming factor transport")
        if literal_singles:
            changed = replay(gates, width, (i,))
            require(all((changed[j] ^ baseline[j]) ==
                        (incoming if (u >> j) & 1 else 0)
                        for j in range(width)), "literal single omission")
        prefixes[dst] ^= prefixes[src]
    require(prefixes == baseline, "forward prefix boundary")


def ordered_matches(forward, backward):
    """Count (a,b),(c,d) with b<c and equal exact product keys."""
    endings = {}
    first_pair = {}
    for key, pairs in forward.items():
        ordered = sorted(pairs, key=lambda pair: (pair[1], pair[0]))
        endings[key] = [b for a, b in ordered]
        first_pair[key] = ordered[0]
    count = 0
    witness = None
    for key, c, d in backward:
        ends = endings.get(key)
        if ends is not None:
            matched = bisect_left(ends, c)
            count += matched
            if matched:
                a, b = first_pair[key]
                candidate = (a, b, c, d)
                witness = candidate if witness is None else min(witness, candidate)
    return count, witness


def four_census(factors):
    """Partition all pairs by rank, then by the image of their product-I.

    Distinct nontrivial F2 transvections are required. A rank-two product's
    image is span(u_a,u_b), containing at most three nonzero image vectors.
    """
    require(len(set(factors)) == len(factors), "duplicate transported factor")
    require(all(u > 0 and v > 0 and not parity(u & v) for u, v in factors),
            "nontrivial transvection premise")
    by_u, by_v = defaultdict(list), defaultdict(list)
    for i, (u, v) in enumerate(factors):
        by_u[u].append((i, v))
        by_v[v].append((i, u))

    rank_one = defaultdict(list)
    rank_one_pairs = 0
    for side, groups in enumerate((by_u, by_v)):
        for common, members in groups.items():
            for (a, x), (b, y) in combinations(members, 2):
                key = (common, x ^ y) if side == 0 else (x ^ y, common)
                rank_one[key].append((a, b))
                rank_one_pairs += 1
    count_one, witness_one = ordered_matches(
        rank_one, ((key, c, d) for key, pairs in rank_one.items() for c, d in pairs))
    triple_set = set()
    index = {factor: i for i, factor in enumerate(factors)}
    for key, pairs in rank_one.items():
        if key in index:
            for a, b in pairs:
                triple_set.add(tuple(sorted((a, b, index[key]))))

    us = sorted(by_u)
    position = {u: i for i, u in enumerate(us)}
    count_two = rank_two_pairs = plane_count = three_member_planes = 0
    peak_plane_pairs = 0
    witness_two = None
    for ia, x in enumerate(us):
        for ib in range(ia + 1, len(us)):
            y = us[ib]
            ic = position.get(x ^ y)
            if ic is not None and ic < ib:
                continue  # visit a three-member plane at its two smallest u's
            plane_count += 1
            groups = [(x, 1, by_u[x]), (y, 2, by_u[y])]
            if ic is not None:
                three_member_planes += 1
                groups.append((x ^ y, 3, by_u[x ^ y]))
            forward = defaultdict(list)
            backward = []
            for (ug, cg, group_g), (uh, ch, group_h) in combinations(groups, 2):
                for i, vg in group_g:
                    for j, vh in group_h:
                        if vg == vh:
                            continue  # already covered by the rank-one by_v bucket
                        if i < j:
                            a, b, ua, ub, va, vb, ca, cb = i, j, ug, uh, vg, vh, cg, ch
                        else:
                            a, b, ua, ub, va, vb, ca, cb = j, i, uh, ug, vh, vg, ch, cg
                        # T_b T_a-I = ua va + ub (vb + (vb.ua) va).
                        q = vb ^ (va if parity(vb & ua) else 0)
                        f0 = (va if ca & 1 else 0) ^ (q if cb & 1 else 0)
                        f1 = (va if ca & 2 else 0) ^ (q if cb & 2 else 0)
                        # The inverse is T_a T_b, with the other cross term.
                        p = va ^ (vb if parity(va & ub) else 0)
                        g0 = (p if ca & 1 else 0) ^ (vb if cb & 1 else 0)
                        g1 = (p if ca & 2 else 0) ^ (vb if cb & 2 else 0)
                        forward[(f0, f1)].append((a, b))
                        backward.append(((g0, g1), a, b))
            plane_pairs = len(backward)
            peak_plane_pairs = max(peak_plane_pairs, plane_pairs)
            rank_two_pairs += plane_pairs
            matches, witness = ordered_matches(forward, backward)
            count_two += matches
            if witness is not None:
                witness_two = witness if witness_two is None else min(witness_two, witness)
    require(rank_one_pairs + rank_two_pairs == math.comb(len(factors), 2),
            "pair partition coverage")
    witnesses = [w for w in (witness_one, witness_two) if w is not None]
    return {
        "factors": len(factors),
        "distinct_image_vectors": len(by_u),
        "distinct_covectors": len(by_v),
        "pair_count": rank_one_pairs + rank_two_pairs,
        "rank_one_pairs": rank_one_pairs,
        "rank_two_pairs": rank_two_pairs,
        "image_planes": plane_count,
        "three_member_image_planes": three_member_planes,
        "peak_rank_two_plane_pairs": peak_plane_pairs,
        "neutral_triples": len(triple_set),
        "neutral_four_rank_one": count_one,
        "neutral_four_rank_two": count_two,
        "neutral_four_total": count_one + count_two,
        "witness": list(min(witnesses)) if witnesses else None,
    }


def dense_oracle(factors, width):
    """Small-domain oracle: literal dense matrices, no pair-bucket logic."""
    identity = [1 << i for i in range(width)]
    matrices = [transvection_rows(factor, width) for factor in factors]
    neutral = []
    for indices in combinations(range(len(factors)), 4):
        product = identity
        for i in indices:
            product = compose(matrices[i], product)
        if product == identity:
            neutral.append(indices)
    return neutral


def controls():
    # Every 3D transvection and several complete chronological orderings.
    small = [(u, v) for u in range(1, 8) for v in range(1, 8)
             if not parity(u & v)]
    require(len(small) == 21, "small transvection domain")
    orders = [[small[(k * j) % 21] for j in range(21)] for k in (1, 2, 4, 5)]
    orders += [order[::-1] for order in orders.copy()]
    counts = []
    for ordered in orders:
        expected = dense_oracle(ordered, 3)
        observed = four_census(ordered)
        require(observed["neutral_four_total"] == len(expected), "dense quartet oracle")
        require(observed["witness"] is None or tuple(observed["witness"]) in expected,
                "dense quartet witness")
        counts.append(len(expected))

    # Both rank strata contain positive examples. The second is noncommuting.
    one = [(1, 2), (1, 4), (6, 6), (7, 6)]
    two = [(1, 2), (2, 4), (3, 4), (1, 6)]
    require(four_census(one)["neutral_four_rank_one"] == 1, "rank-one positive")
    require(four_census(two)["neutral_four_rank_two"] == 1, "rank-two positive")
    left = compose(transvection_rows(two[1], 3), transvection_rows(two[0], 3))
    wrong_right = compose(transvection_rows(two[3], 3), transvection_rows(two[2], 3))
    require(left != wrong_right, "same-orientation mutant must fail")
    wrong_order = [two[i] for i in (1, 0, 2, 3)]
    require(not dense_oracle(wrong_order, 3) and
            four_census(wrong_order)["neutral_four_total"] == 0,
            "chronology mutant must fail")
    require(ordered_matches({0: [(0, 2)]}, [(0, 1, 3)])[0] == 0,
            "interleaved pairs are not chronological splits")
    require(ordered_matches({0: [(0, 2)]}, [(0, 2, 3)])[0] == 0,
            "shared-position pairs are not disjoint")
    require(ordered_matches({0: [(0, 1), (0, 2), (1, 2)]}, [(0, 3, 4)])[0] == 3,
            "all compatible earlier pairs must be counted")
    rejected = 0
    for bad in [[(1, 2), (1, 2)], [(1, 1)], [(0, 2)], [(1, 0)]]:
        try:
            four_census(bad)
        except ValueError:
            rejected += 1
    require(rejected == 4, "malformed factor controls")
    # Restored zero helpers would hide this change; arbitrary dirt does not.
    dirty_rows = replay([(0, 2)], 3)
    require([r & 3 for r in dirty_rows[:2]] == [1, 2] and dirty_rows != [1, 2, 4],
            "clean-input-only counterexample")
    # Check the deletion formula for every subset (not just size four) of
    # a literal word with noncommuting gates, using original baseline suffixes.
    gates = [(0, 1), (1, 2), (2, 0), (0, 2), (1, 0), (2, 1), (0, 1)]
    factors = factors_from_suffixes(gates, 3)
    check_factors(gates, 3, factors, literal_singles=True)
    baseline = replay(gates, 3)
    inverse = replay(gates[::-1], 3)
    for mask in range(1 << len(gates)):
        omitted = [i for i in range(len(gates)) if (mask >> i) & 1]
        product = [1, 2, 4]
        for i in omitted:
            product = compose(transvection_rows(factors[i], 3), product)
        require(compose(replay(gates, 3, omitted), inverse) == product,
                "literal deletion transport formula")
    require(baseline != [1, 2, 4], "nontrivial literal positive word")
    return {"dense_orderings": len(orders), "dense_quartets": len(orders) * math.comb(21, 4),
            "dense_neutral_counts": counts, "literal_deletion_subsets": 1 << len(gates),
            "positive_rank_strata": 2, "malformed_factor_rejections": rejected,
            "orientation_chronology_dirty_controls": 5}


def load_bound_word():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for source in manifest["files"]:
        if source["usage"] == "input":
            data = (ROOT / source["path"]).read_bytes()
            require(hashlib.sha256(data).hexdigest() == source["sha256"],
                    "source digest: " + source["path"])
    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    require((word["v"], word["R"]) == (111, 439), "source dimensions")
    require(all(frame == 0 for frame, dst, srcs in word["D"]), "zero-frame D")
    gates = [(dst, src) for frame, dst, srcs in word["D"] for src in srcs]
    require(len(gates) == 5563, "elementary gate count")
    return gates, 661


def check_certificate(result, expected):
    require(result == expected, "certificate mismatch")


def run():
    gates, width = load_bound_word()
    factors = factors_from_suffixes(gates, width)
    check_factors(gates, width, factors, literal_singles=True)
    digest = hashlib.sha256(json.dumps([[str(u), str(v)] for u, v in factors],
                                      separators=(",", ":")).encode()).hexdigest()
    predecessor = json.loads((ROOT / "research/r439-three-omission-distance/CERTIFICATE.json").read_text())
    require(digest == predecessor["factor_sha256"], "PR1446 factor corroboration")
    result = four_census(factors)
    # Same full finite domain, partitioned independently by covector planes.
    # Transpose reverses products; reversing four involutions preserves I.
    dual = four_census([(v, u) for u, v in factors])
    for key in ("pair_count", "rank_one_pairs", "rank_two_pairs", "neutral_triples",
                "neutral_four_rank_one", "neutral_four_rank_two", "neutral_four_total"):
        require(result[key] == dual[key], "dual-plane corroboration: " + key)
    witness = result["witness"]
    if witness is not None:
        require(replay(gates, width, witness) == replay(gates, width),
                "literal four-omission witness")
    result.update({"columns": width, "four_subsets_covered": math.comb(len(gates), 4),
                   "factor_sha256": digest, "literal_single_replays": len(gates),
                   "dual_partition": dual, "controls": controls(), "new_kappa": False})
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the deterministic receipt")
    args = parser.parse_args()
    result = run()
    certificate = HERE / "CERTIFICATE.json"
    if args.write:
        certificate.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        check_certificate(result, json.loads(certificate.read_text()))
    print("PASS_FOUR_OMISSION_CENSUS"
          f" gates={result['factors']} pairs={result['pair_count']}"
          f" four_subsets={result['four_subsets_covered']}"
          f" neutral={result['neutral_four_total']} columns={result['columns']}"
          f" dual_neutral={result['dual_partition']['neutral_four_total']}"
          f" dense_controls={result['controls']['dense_quartets']} no_new_kappa")
