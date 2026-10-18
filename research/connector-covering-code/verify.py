#!/usr/bin/env python3
"""Finite premises of the covering-code proof; classification is a cited theorem.

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
The calculation does not enumerate all covers or all singleton words.
"""

from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


TABLE_SHA256 = "fbf0f123bb6c037ce990c0a527f1aafbb30a70da0a941ac1eec894ea6166f88c"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def points_checked(points, dimension):
    need(type(dimension) is int and 1 <= dimension <= 10, "finite check dimension")
    points = tuple(points)
    need(all(type(x) is int and 0 <= x < 1 << dimension for x in points),
         "points must be binary vectors, without boolean aliases")
    need(len(set(points)) == len(points), "distinct point set")
    return points


def pair_sums(points):
    return {x ^ y for x in points for y in points}


def columns_from_points(points, dimension, origin):
    points = points_checked(points, dimension)
    need(type(origin) is int and origin in points, "origin must belong to the set")
    return tuple(x ^ origin for x in points if x != origin)


def ball_syndromes(columns):
    return {0, *columns, *(x ^ y for x, y in combinations(columns, 2))}


def binary_rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    return len(pivots)


def character_weights(points, dimension):
    return dict(sorted(Counter(
        sum((u & x).bit_count() & 1 for x in points)
        for u in range(1, 1 << dimension)
    ).items()))


def affine_rank(points):
    origin = min(points)
    return binary_rank(point ^ origin for point in points)


def minimum_cover_geometry(points):
    normals = [u for u in range(1, 128)
               if sum((u & x).bit_count() & 1 for x in points) in (4, 16)]
    need(len(normals) == 1, "one four/sixteen cut")
    normal = normals[0]
    sides = [tuple(x for x in points if ((normal & x).bit_count() & 1) == bit)
             for bit in (0, 1)]
    small, large = sorted(sides, key=len)
    need((len(small), len(large)) == (4, 16), "cut sizes")
    ranks = (affine_rank(small), affine_rank(large))
    need(ranks == (2, 6), "affine ranks for the component obstruction")
    intersection = (pair_sums(small) & pair_sums(large)) - {0}
    need(not intersection, "disjoint internal nonzero directions")
    cross = Counter(a ^ b for a in small for b in large)
    need(len(cross) == 64 and set(cross.values()) == {1}, "unique cross directions")
    need(set(cross) == {d for d in range(128) if (normal & d).bit_count() & 1},
         "the whole opposite hyperplane coset")
    return {"normal": normal, "minority_points": sorted(small),
            "minority_affine_rank": ranks[0], "majority_affine_rank": ranks[1],
            "internal_support_intersection": sorted(intersection),
            "cross_count": len(cross), "component_bound": sum(ranks) + 2 - 7}


def component_sizes(points, directions):
    parent = {point: point for point in points}

    def root(point):
        while parent[point] != point:
            point = parent[point]
        return point

    for point in points:
        for direction in directions:
            other = point ^ direction
            if other in parent:
                parent[root(point)] = root(other)
    return sorted(Counter(root(point) for point in points).values())


def check_component_rank():
    cases = 0
    for mask in range(1, 256):
        points = tuple(x for x in range(8) if mask >> x & 1)
        point_rank = affine_rank(points)
        available = pair_sums(points) - {0}
        for alphabet in range(128):
            directions = tuple(d for d in available if alphabet >> (d - 1) & 1)
            count = len(component_sizes(points, directions))
            need(point_rank <= binary_rank(directions) + count - 1,
                 "component-rank lemma on every small direction graph")
            cases += 1
    need(cases == 32640, "complete small component-rank check")
    return {"dimension": 3, "nonempty_sets": 255, "direction_alphabets": 128,
            "cases": cases}


def check_twenty_one_classes(rows):
    need(len(rows) == 36 and [row["id"] for row in rows] == list(range(1, 37)),
         "all thirty-six size-twenty source classes")
    receipts = []
    for row in rows:
        columns = points_checked(row["columns"], 7)
        need(len(columns) == 20 and 0 not in columns, "twenty projective points")
        points = (0, *columns)
        need(pair_sums(points) == set(range(128)), "source twenty-one-point cover")
        removable = [x for x in points if pair_sums([p for p in points if p != x]) == set(range(128))]
        need(set(removable) <= {0}, "source nonzero columns are minimal")
        pairs = Counter(a ^ b for a, b in combinations(points, 2))
        characters = []
        for normal in range(1, 128):
            if sum((normal & p).bit_count() & 1 for p in points) != 11:
                continue
            eligible = [d for d, count in pairs.items()
                        if count >= 2 and (normal & d).bit_count() & 1]
            characters.append({"normal": normal,
                               "component_sizes": component_sizes(points, eligible)})
        excluded = bool(removable) or not any(max(c["component_sizes"]) >= 20 for c in characters)
        receipts.append({"id": row["id"], "removable_points": removable,
                         "characters": characters, "excluded": excluded})
    remaining = [row["id"] for row in receipts if not row["excluded"]]
    need(remaining == [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 13, 14, 16, 18, 21, 23],
         "exact retained twenty-one-point cases")
    character_count = sum(len(row["characters"]) for row in receipts if not row["excluded"])
    need(character_count == 234, "retained weight-eleven character cases")
    return {"classes": receipts, "remaining": remaining,
            "remaining_character_cases": character_count}


def support_basis_binary(points, normal, leaf=None):
    """Binary include/exclude search for a necessary independent support basis.

    The ordinary graph has root degree four. Removing a doubled pendant
    leaves a twenty-cycle; its pendant direction is selected even if it
    supplies no ordinary edge. Each other direction needs two distinct pairs.
    """
    active = tuple(i for i in range(21) if i != leaf)
    pairs = Counter(points[i] ^ points[j] for i, j in combinations(active, 2))
    mandatory = None if leaf is None else points[leaf]
    directions = tuple(d for d in range(1, 128) if (d & normal).bit_count() & 1
                       and (pairs[d] >= 2 or d == mandatory))
    active_points = {points[i] for i in active}
    incident = tuple(sum(1 << k for k, d in enumerate(directions)
                         if i != leaf and (point ^ d) in active_points)
                     for i, point in enumerate(points))
    targets = tuple(0 if i == leaf else 4 if leaf is None and i == 0 else 2
                    for i in range(21))
    nodes = 0

    def include(selected, allowed, span, index):
        bit = 1 << index
        if not allowed & bit or directions[index] in span:
            return None
        enlarged = span | frozenset(x ^ directions[index] for x in span)
        remaining = sum(1 << k for k, d in enumerate(directions)
                        if allowed >> k & 1 and d not in enlarged)
        return selected | bit, remaining, enlarged

    def search(selected, allowed, span):
        nonlocal nodes
        nodes += 1
        while True:
            slots = 7 - selected.bit_count()
            if slots < 0 or allowed.bit_count() < slots:
                return None
            forced = 0
            best = None
            choice = None
            for incidence, target in zip(incident, targets):
                deficit = target - (incidence & selected).bit_count()
                if deficit <= 0:
                    continue
                available = incidence & allowed
                count = available.bit_count()
                if count < deficit or deficit > slots:
                    return None
                if count == deficit:
                    forced = available
                    break
                score = count - deficit, count
                if best is None or score < best:
                    best, choice = score, available
            if not forced:
                break
            while forced:
                bit = forced & -forced
                forced ^= bit
                following = include(selected, allowed, span, bit.bit_length() - 1)
                if following is None:
                    return None
                selected, allowed, span = following
        if not slots:
            return tuple(d for k, d in enumerate(directions) if selected >> k & 1)
        if choice is None:
            choice = allowed
        bit = choice & -choice
        need(bool(bit), "a remaining independent direction must be decided")
        following = include(selected, allowed, span, bit.bit_length() - 1)
        if following is not None:
            answer = search(*following)
            if answer is not None:
                return answer
        return search(selected, allowed ^ bit, span)

    initial = 0, (1 << len(directions)) - 1, frozenset({0})
    if mandatory is not None:
        need(mandatory in directions, "pendant direction retained")
        initial = include(*initial, directions.index(mandatory))
        need(initial is not None, "nonzero pendant direction is independent")
    return search(*initial), nodes


def check_twenty_one_support(rows, screen):
    by_id = {row["id"]: row for row in rows}
    records = []
    for item in screen["classes"]:
        if item["excluded"]:
            continue
        points = (0, *by_id[item["id"]]["columns"])
        for character in item["characters"]:
            normal = character["normal"]
            leaves = [None] + [i for i in range(1, 21) if (points[i] & normal).bit_count() & 1]
            nodes = 0
            for leaf in leaves:
                answer, visited = support_basis_binary(points, normal, leaf)
                need(answer is None, "no necessary support basis for a twenty-one-prefix word")
                nodes += visited
            records.append({"id": item["id"], "normal": normal, "excluded": True,
                            "branches": len(leaves), "nodes": nodes, "solutions": 0})
    need(len(records) == 234 and sum(row["branches"] for row in records) == 2808,
         "all retained characters and ordinary/pendant branches checked")
    return {"classes": len({row["id"] for row in records}), "character_cases": len(records),
            "branches": sum(row["branches"] for row in records),
            "nodes": sum(row["nodes"] for row in records), "solutions": 0, "cases": records}


def check_support_controls():
    simple = [0, 1, 3, 7, 6, 4] + [(k ^ (k >> 1)) << 3 for k in range(1, 16)]
    pendant = [0, 16, 17, 1, 33, 35, 3] + [k ^ (k >> 1) for k in range(3, 16)] + [64]
    for points, leaf in ((simple, None), (pendant, 20)):
        need(len(points) == len(set(points)) == 21, "planted graph has twenty-one vertices")
        answer, _ = support_basis_binary(points, 127, leaf)
        need(answer is not None and len(answer) == binary_rank(answer) == 7,
             "planted simple and doubled-pendant support bases are retained")
    return {"simple_root_degree_four": True, "pendant_with_no_ordinary_pendant_edge": True}


def parse_table(raw):
    need(sha256(raw).hexdigest() == TABLE_SHA256, "Table 6 source bytes changed")
    table = json.loads(raw)
    need(type(table["dimension"]) is int and table["dimension"] == 7, "dimension seven")
    rows = table["representatives"]
    need(len(rows) == 5 and [row["id"] for row in rows] == list(range(1, 6)),
         "all five source classes in source order")
    return rows


def check_representatives(rows):
    result = []
    for row in rows:
        columns = points_checked(row["columns"], 7)
        need(len(columns) == 19 and 0 not in columns, "nineteen projective points")
        points = (0, *columns)
        coverage = pair_sums(points)
        need(coverage == set(range(128)), "the sharp twenty-point cover witness")
        need(binary_rank(columns) == 7, "full syndrome rank")
        weights = character_weights(points, 7)
        need(sum(weights.values()) == 127 and 10 not in weights,
             "no balanced nonzero character")
        multiplicity = Counter(x ^ y for x, y in combinations(points, 2))
        repeat_rank = binary_rank(d for d, count in multiplicity.items() if count >= 2)
        need(repeat_rank == 6, "corroborating repeated-direction obstruction")
        result.append({"id": row["id"], "size": len(points), "rank": 7,
                       "coverage": len(coverage), "character_weights": weights,
                       "repeated_direction_rank": repeat_rank,
                       "minimum_cover_geometry": minimum_cover_geometry(points)})
    return result


def check_correspondence():
    origins = covers = 0
    for mask in range(256):
        points = tuple(x for x in range(8) if mask >> x & 1)
        sums = pair_sums(points)
        covers += sums == set(range(8))
        for origin in points:
            columns = columns_from_points(points, 3, origin)
            need(ball_syndromes(columns) == sums, "exact at-most-two syndrome image")
            if len(sums) == 8:
                need(binary_rank(columns) == 3, "coverage forces full row rank")
            origins += 1
    need(origins == 1024, "every member-origin of every small set")
    return {"subsets": 256, "origins": origins, "covers": covers}


def prefixes(word, dimension):
    result = [0]
    for label in word:
        need(type(label) is int and 0 <= label < dimension, "singleton label")
        result.append(result[-1] ^ (1 << label))
    return result


def gray_cycle(dimension, offset):
    vertices = [i ^ (i >> 1) for i in range(1 << dimension)] + [0]
    return [(a ^ b).bit_length() - 1 + offset
            for a, b in zip(vertices, vertices[1:])]


def check_positive_word():
    word = gray_cycle(3, 0) + gray_cycle(4, 3)
    path = prefixes(word, 7)
    need(path[-1] == 0 and len(word) == 24, "restored twenty-four-step word")
    need(pair_sums(set(path)) == set(range(128)), "universal positive word")
    need(all(count % 2 == 0 for count in Counter(word).values()), "restoration parity")
    return {"length": len(word), "states": len(set(path)),
            "coverage": 128, "restored": True}


def check_basis_counterexample():
    points = {0, 1, 2, 3, 4, 8, 12}
    basis = (5, 6, 9, 11)
    mapping = {}
    for x in range(16):
        image = 0
        for i, vector in enumerate(basis):
            if x >> i & 1:
                image ^= vector
        mapping[x] = image
    need(len(set(mapping.values())) == 16, "invertible basis change")
    changed = {x for x, image in mapping.items() if image in points}
    need(changed == {0, 3, 5, 11, 12, 14, 15}, "exact transformed cover")
    need(pair_sums(points) == pair_sums(changed) == set(range(16)), "coverage invariant")
    need(character_weights(points, 4) == character_weights(changed, 4),
         "character spectrum invariant under linear maps")
    need(set(prefixes([0, 1, 0, 1, 2, 3, 2, 3], 4)) == points, "spanning source walk")
    need(all(1 << i not in changed for i in range(4)), "transformed zero is isolated")
    return {"dimension": 4, "points": sorted(points), "changed": sorted(changed),
            "basis": list(basis), "changed_zero_isolated": True}


def check_failure_controls(raw):
    cases = [lambda: points_checked([0, 0], 3),
             lambda: points_checked([False, 1], 3),
             lambda: points_checked([0, 8], 3),
             lambda: points_checked([0], True),
             lambda: columns_from_points([0, 1], 3, 2),
             lambda: parse_table(raw + b" ")]
    for case in cases:
        try:
            case()
        except ValueError:
            continue
        raise ValueError("a malformed-input/source control was accepted")
    need(binary_rank([1]) == 1 and len(ball_syndromes([1])) == 2,
         "rank-deficient matrices do not cover a nominal two-dimensional space")
    need(2 in character_weights([0, 1, 2, 3], 2),
         "positive balanced-character control")
    return {"input_or_source_rejections": len(cases), "mathematical_controls": 2}


def run():
    raw = Path(__file__).with_name("table6.json").read_bytes()
    rows = parse_table(raw)
    size20_rows = json.loads(raw)["size20_representatives"]
    screen = check_twenty_one_classes(size20_rows)
    return {"representatives": check_representatives(rows),
            "correspondence": check_correspondence(),
            "component_rank_lemma": check_component_rank(),
            "twenty_one_classes": screen,
            "support_exclusion": check_twenty_one_support(size20_rows, screen),
            "support_controls": check_support_controls(),
            "positive_word": check_positive_word(),
            "basis_counterexample": check_basis_counterexample(),
            "controls": check_failure_controls(raw)}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
    print("PASS_CONNECTOR_COVERING_CODE finite_premises_only")
