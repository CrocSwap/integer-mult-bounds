#!/usr/bin/env python3
"""Independent, read-only finite checks; literature completeness is external."""
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rejected(operation):
    try:
        operation()
    except ValueError:
        return True
    raise ValueError("negative control was accepted")


def histogram(values):
    return {str(k): v for k, v in sorted(Counter(values).items())}


def transform(values):
    """Unnormalized Walsh transform, using only integer butterflies."""
    values = list(values)
    stride = 1
    while stride < len(values):
        for start in range(0, len(values), 2 * stride):
            for offset in range(stride):
                i, j = start + offset, start + offset + stride
                values[i], values[j] = values[i] + values[j], values[i] - values[j]
        stride *= 2
    return values


def coverage(points, dimension):
    size = 1 << dimension
    indicator = [int(x in points) for x in range(size)]
    convolution = transform([x * x for x in transform(indicator)])
    require(all(x >= 0 and x % size == 0 for x in convolution), "bad convolution")
    return sum(x != 0 for x in convolution)


def rowspace(points, dimension):
    rows = [sum(((point >> j) & 1) << i for i, point in enumerate(points))
            for j in range(dimension)]
    words = [0]
    for row in rows:
        words += [word ^ row for word in words]
    rank = len(set(words)).bit_length() - 1
    return rank, histogram(bin(word).count("1") for word in words[1:])


def direct_weights(points, dimension):
    weights = []
    for character in range(1, 1 << dimension):
        weight = 0
        for point in points:
            parity = 0
            for coordinate in range(dimension):
                if (character >> coordinate) & 1:
                    parity ^= (point >> coordinate) & 1
            weight += parity
        weights.append(weight)
    return histogram(weights)


def columns_of(representative, size=19):
    columns = representative["columns"]
    require(len(columns) == size, "wrong number of representative columns")
    require(all(type(x) is int and 0 < x < 128 for x in columns), "invalid column")
    require(len(set(columns)) == len(columns), "duplicate column")
    return columns


def span_rank(directions):
    span = {0}
    for direction in directions:
        span |= {point ^ direction for point in span}
    return len(span).bit_length() - 1


def affine_rank(points):
    require(bool(points), "affine rank needs a nonempty set")
    origin = min(points)
    return span_rank(point ^ origin for point in points)


def coordinate_parity(point, normal, dimension):
    parity = 0
    for coordinate in range(dimension):
        if (normal >> coordinate) & 1:
            parity ^= (point >> coordinate) & 1
    return parity


def partition_geometry(points, normal):
    sides = [[p for p in points if coordinate_parity(p, normal, 7) == side]
             for side in range(2)]
    minority, majority = sorted(sides, key=len)
    require(len(minority) == 4 and len(majority) == 16, "cut is not four/sixteen")
    small_rank, large_rank = affine_rank(minority), affine_rank(majority)
    require(small_rank == 2 and large_rank == 6, "wrong affine geometry")
    small_sums = {a ^ b for a, b in combinations(minority, 2)}
    large_sums = {a ^ b for a, b in combinations(majority, 2)}
    intersection = small_sums & large_sums
    require(not intersection and len(small_sums | large_sums) == 63, "internal supports overlap")
    cross = Counter(a ^ b for a in minority for b in majority)
    require(len(cross) == 64 and set(cross.values()) == {1}, "cross sums are not unique")
    require(set(cross) == {x for x in range(128) if coordinate_parity(x, normal, 7)},
            "cross sums do not equal the opposite hyperplane coset")
    return {"normal": normal, "minority_points": sorted(minority),
            "minority_affine_rank": small_rank, "majority_affine_rank": large_rank,
            "internal_support_intersection": sorted(intersection), "cross_count": len(cross),
            "component_bound": small_rank + large_rank + 2 - 7}


def minimum_cover_geometry(points):
    normals = [normal for normal in range(1, 128)
               if sum(coordinate_parity(p, normal, 7) for p in points) in (4, 16)]
    require(len(normals) == 1, "four/sixteen hyperplane is not unique")
    return partition_geometry(points, normals[0])


def component_rank_check():
    """Within-component differences use edge directions; roots add at most c-1 ranks."""
    alphabets = [[d for d in range(1, 8) if (mask >> (d - 1)) & 1] for mask in range(128)]
    ranks = [span_rank(directions) for directions in alphabets]
    cases = 0
    for subset in range(1, 256):
        points = {x for x in range(8) if (subset >> x) & 1}
        point_rank = affine_rank(points)
        for directions in alphabets:
            unseen = set(points)
            components = 0
            used = 0
            while unseen:
                components += 1
                stack = [unseen.pop()]
                while stack:
                    point = stack.pop()
                    for direction in directions:
                        other = point ^ direction
                        if other in points:
                            used |= 1 << (direction - 1)
                        if other in unseen:
                            unseen.remove(other)
                            stack.append(other)
            require(components >= point_rank + 1 - ranks[used], "component-rank lemma failed")
            cases += 1
    require(cases == 32640, "incomplete component-rank enumeration")
    return {"dimension": 3, "nonempty_sets": 255, "direction_alphabets": 128, "cases": cases}


def union_find_sizes(vertices, edges):
    parent = {vertex: vertex for vertex in vertices}

    def root(vertex):
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    for left, right in edges:
        left_root, right_root = root(left), root(right)
        if left_root != right_root:
            parent[left_root] = right_root
    return sorted(Counter(root(vertex) for vertex in parent).values(), reverse=True)


def size21_screen(representatives):
    require(len(representatives) == 36 and
            [rep["id"] for rep in representatives] == list(range(1, 37)),
            "expected thirty-six ordered size-twenty projective classes")
    receipts = []
    for representative in representatives:
        points = [0] + columns_of(representative, 20)
        require(coverage(set(points), 7) == 128, "size-twenty-one class is not a cover")
        removable = [point for point in points if coverage(set(points) - {point}, 7) == 128]
        require(set(removable) <= {0}, "projective class has a removable column")
        pairs = list(combinations(points, 2))
        multiplicities = Counter(left ^ right for left, right in pairs)
        characters = []
        for normal in range(1, 128):
            if sum(coordinate_parity(point, normal, 7) for point in points) != 11:
                continue
            eligible = {direction for direction, count in multiplicities.items()
                        if count >= 2 and coordinate_parity(direction, normal, 7)}
            sizes = union_find_sizes(points, ((left, right) for left, right in pairs
                                             if left ^ right in eligible))
            characters.append({"normal": normal, "eligible_directions": len(eligible),
                               "component_sizes": sizes, "excluded": sizes[0] < 20})
        receipts.append({"id": representative["id"], "coverage": 128,
                         "removable_points": removable, "characters": characters,
                         "excluded": bool(removable) or all(item["excluded"] for item in characters)})
    excluded = [item["id"] for item in receipts if item["excluded"]]
    remaining = [item["id"] for item in receipts if not item["excluded"]]
    remaining_pairs = sum(len(item["characters"]) for item in receipts if not item["excluded"])
    total_pairs = sum(len(item["characters"]) for item in receipts)
    require(total_pairs == 402, "size-twenty-one character census changed")
    require(excluded == [4, 12, 15, 17, 19, 20, 22, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
            "size-twenty-one exclusion receipt changed")
    require(remaining == [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 13, 14, 16, 18, 21, 23]
            and remaining_pairs == 234, "size-twenty-one survivor receipt changed")
    return {"classes": 36, "excluded_classes": excluded, "remaining_classes": remaining,
            "total_character_pairs": total_pairs, "remaining_character_pairs": remaining_pairs,
            "representatives": receipts}


def support_rank(values):
    """Binary Gaussian elimination, independent of the span-closure oracle."""
    rows = [0] * 7
    rank = 0
    for value in values:
        for bit in range(6, -1, -1):
            if not (value >> bit) & 1:
                continue
            if rows[bit]:
                value ^= rows[bit]
            else:
                rows[bit] = value
                rank += 1
                break
    return rank


def support_basis(points, normal, leaf=None):
    """Find any independent seven-direction set meeting necessary support degrees.

    A leaf branch removes that vertex from the ordinary cycle and forces its
    direction. No connectedness or exact graph-factor constraints are used.
    """
    require(len(points) == len(set(points)) == 21 and points[0] == 0,
            "support search needs twenty-one distinct points rooted at zero")
    require(all(type(point) is int and 0 <= point < 128 for point in points)
            and support_rank(points) == 7, "invalid support-search points")
    require(type(normal) is int and 0 < normal < 128 and
            sum((point & normal).bit_count() % 2 for point in points) == 11,
            "support search needs a weight-eleven character")
    require(leaf is None or type(leaf) is int and 0 < leaf < 21 and
            (points[leaf] & normal).bit_count() % 2 == 1, "invalid pendant leaf")
    active = [point for index, point in enumerate(points) if index != leaf]
    active_set = set(active)
    multiplicities = Counter(left ^ right for left, right in combinations(active, 2))
    mandatory = points[leaf] if leaf is not None else None
    directions = tuple(direction for direction in range(1, 128)
                       if (direction & normal).bit_count() % 2 and
                       (multiplicities[direction] >= 2 or direction == mandatory))
    incident = [frozenset(direction for direction in directions
                          if index != leaf and point ^ direction in active_set)
                for index, point in enumerate(points)]
    targets = tuple(0 if index == leaf else 4 if leaf is None and index == 0 else 2
                    for index in range(21))
    nodes = 0

    def search(selected, allowed):
        nonlocal nodes
        nodes += 1
        slots = 7 - len(selected)
        if slots < 0 or len(allowed) < slots or support_rank(selected + allowed) < 7:
            return None
        allowed = tuple(direction for direction in allowed
                        if support_rank(selected + (direction,)) > len(selected))
        if len(allowed) < slots:
            return None
        selected_set, allowed_set = frozenset(selected), frozenset(allowed)
        obligation, score = None, None
        for neighbors, target in zip(incident, targets):
            deficit = target - len(neighbors & selected_set)
            if deficit <= 0:
                continue
            choices = tuple(sorted(neighbors & allowed_set))
            if deficit > slots or len(choices) < deficit:
                return None
            count = 1
            for index in range(1, deficit + 1):
                count = count * (len(choices) - index + 1) // index
            if score is None or count < score:
                score, obligation = count, (choices, deficit)
        if obligation is None:
            # Degree bounds survive additions; matroid augmentation completes
            # an independent basis whenever the available span has rank seven.
            completion = list(selected)
            for direction in allowed:
                if support_rank(completion + [direction]) > len(completion):
                    completion.append(direction)
                if len(completion) == 7:
                    break
            require(len(completion) == support_rank(completion) == 7,
                    "support basis augmentation failed")
            require(all(len(set(completion) & neighbors) >= target
                        for neighbors, target in zip(incident, targets)),
                    "support basis misses a degree bound")
            return completion
        choices, deficit = obligation
        # Partition completions by their first required incident directions.
        # Larger incident directions remain free, so extra neighbors are kept.
        for added in combinations(choices, deficit):
            next_selected = selected + added
            if support_rank(next_selected) != len(next_selected):
                continue
            excluded = frozenset(direction for direction in choices if direction <= added[-1])
            answer = search(next_selected, tuple(direction for direction in allowed
                                                 if direction not in excluded))
            if answer is not None:
                return answer
        return None

    selected = () if mandatory is None else (mandatory,)
    answer = search(selected, tuple(direction for direction in directions if direction not in selected))
    return answer, nodes


def size21_support_exclusion(representatives, screen):
    retained = [item for item in screen["representatives"] if not item["excluded"]]
    require([item["id"] for item in retained] == screen["remaining_classes"],
            "support cases disagree with computed component screen")
    by_id = {representative["id"]: representative for representative in representatives}
    cases = []
    for item in retained:
        points = [0] + columns_of(by_id[item["id"]], 20)
        for character in item["characters"]:
            normal = character["normal"]
            leaves = [None] + [index for index in range(1, 21)
                               if (points[index] & normal).bit_count() % 2]
            require(len(leaves) == 12, "incomplete simple/pendant support branches")
            nodes = 0
            for leaf in leaves:
                answer, branch_nodes = support_basis(points, normal, leaf)
                nodes += branch_nodes
                require(answer is None,
                        f"support basis survived class {item['id']}, character {normal}, leaf {leaf}")
            cases.append({"id": item["id"], "normal": normal, "excluded": True,
                          "branches": len(leaves), "nodes": nodes, "solutions": 0})
    require(len(cases) == screen["remaining_character_pairs"], "support character census changed")
    return {"classes": len(retained), "character_cases": len(cases),
            "branches": sum(item["branches"] for item in cases),
            "nodes": sum(item["nodes"] for item in cases), "solutions": 0, "cases": cases}


def representative_receipt(representative):
    points = [0] + columns_of(representative)
    rank, weights = rowspace(points, 7)
    require(rank == 7, "representative does not have rank seven")
    require(weights == direct_weights(points, 7), "character oracles disagree")
    require(sum(weights.values()) == 127 and "10" not in weights, "balanced character")
    covered = coverage(set(points), 7)
    require(covered == 128, "representative is not a cover")
    pair_counts = Counter(a ^ b for a, b in combinations(points, 2))
    span = {0}
    for direction, count in pair_counts.items():
        if count >= 2:
            span |= {x ^ direction for x in span}
    repeated_rank = len(span).bit_length() - 1
    require(repeated_rank == 6, "unexpected repeated-direction rank")
    return {"id": representative["id"], "size": len(points), "rank": rank,
            "coverage": covered, "character_weights": weights,
            "pair_multiplicities": histogram(pair_counts.values()),
            "repeated_direction_rank": repeated_rank,
            "minimum_cover_geometry": minimum_cover_geometry(points)}


def small_correspondence():
    origins = covers = 0
    for subset in range(256):
        points = {x for x in range(8) if (subset >> x) & 1}
        is_cover = all(any((target ^ x) in points for x in points) for target in range(8))
        covers += is_cover
        for origin in points:
            origins += 1
            columns = [x ^ origin for x in sorted(points) if x != origin]
            syndromes = [0]
            for column in columns:
                syndromes += [s ^ column for s in syndromes]
            kernel = [word for word, syndrome in enumerate(syndromes) if syndrome == 0]
            coset_distances = {}
            for word, syndrome in enumerate(syndromes):
                distance = min(bin(word ^ codeword).count("1") for codeword in kernel)
                previous = coset_distances.setdefault(syndrome, distance)
                require(previous == distance, "distance varies inside a kernel coset")
            code_condition = len(coset_distances) == 8 and max(coset_distances.values()) <= 2
            require(code_condition == is_cover, "cover/kernel-coset correspondence failed")
    require(origins == 1024, "incomplete origin enumeration")
    return {"dimension": 3, "subsets": 256, "origins": origins, "covers": covers}


def prefix_states(word, dimension):
    state, points = 0, set()
    for coordinate in word:
        require(type(coordinate) is int and 0 <= coordinate < dimension, "bad singleton")
        points.add(state)
        state ^= 1 << coordinate
    require(state == 0, "word is not restored")
    return points


def gray_cycle(dimension, offset):
    vertices = [i ^ (i >> 1) for i in range(1 << dimension)]
    return [(vertices[i] ^ vertices[(i + 1) % len(vertices)]).bit_length() - 1 + offset
            for i in range(len(vertices))]


def linear_image(value, basis):
    image = 0
    for j, column in enumerate(basis):
        if (value >> j) & 1:
            image ^= column
    return image


def controls(representatives):
    first = representatives[0]
    columns = columns_of(first)
    duplicate = {"columns": columns[:-1] + columns[:1]}
    out_of_range = {"columns": columns[:-1] + [128]}
    shortened = {"columns": columns[:-1]}
    require(rejected(lambda: columns_of(duplicate)), "duplicate control")
    require(rejected(lambda: columns_of(out_of_range)), "range control")
    require(rejected(lambda: columns_of(shortened)), "removal control")
    points = [0] + columns
    correct_normal = minimum_cover_geometry(points)["normal"]
    wrong_normal = next(normal for normal in range(1, 128) if normal != correct_normal)
    require(rejected(lambda: partition_geometry(points, wrong_normal)), "wrong-cut control")
    cube_rank = affine_rank(set(range(16)))
    require(cube_rank == 4, "linear sixteen-point fixture rank changed")
    require(rejected(lambda: require(cube_rank == 6, "not rank six")), "affine-rank control")
    cycle_edges = [(point, (point + 1) % 20) for point in range(20)]
    leaf_sizes = union_find_sizes(range(21), cycle_edges)
    require(leaf_sizes == [20, 1] and not leaf_sizes[0] < 20, "pendant positive control")
    require(union_find_sizes(range(21), cycle_edges + [(0, 20)]) == [21], "leaf attachment control")
    disconnected_edges = [(point, point + 1) for point in range(20) if point != 5]
    disconnected_sizes = union_find_sizes(range(21), disconnected_edges)
    require(disconnected_sizes == [15, 6] and disconnected_sizes[0] < 20,
            "disconnected rejection control")
    simple_support = [0, 1, 3, 7, 6, 4] + [(index ^ (index >> 1)) << 3
                                         for index in range(1, 16)]
    simple_basis, _ = support_basis(simple_support, 127)
    require(simple_basis is not None, "planted two-cycle support basis was rejected")
    cycle_support = [0, 16, 17, 1, 33, 35, 3] + [index ^ (index >> 1)
                                                for index in range(3, 16)]
    pendant_support = cycle_support + [64]
    require(not any(left ^ right == 64 for left, right in combinations(cycle_support, 2)),
            "pendant fixture unexpectedly uses its direction on the cycle")
    pendant_basis, _ = support_basis(pendant_support, 127, 20)
    require(pendant_basis is not None and 64 in pendant_basis,
            "planted pendant support basis was rejected")
    losses = sum(coverage(set([0] + rep["columns"][:-1]), 7) < 128 for rep in representatives)
    require(losses == 5, "removed-column cover unexpectedly survives")
    balanced = list(range(10)) + list(range(64, 74))
    weights = direct_weights(balanced, 7)
    require("10" in weights, "balanced fixture was missed")
    basis = [(1 << j) ^ ((1 << (j + 1)) if j < 6 else 0) for j in range(7)]
    require(len({linear_image(x, basis) for x in range(128)}) == 128, "singular fixture")
    image = [linear_image(x, basis) ^ 53 for x in balanced]
    require(direct_weights(image, 7).get("10") == weights["10"], "affine balance changed")
    word = gray_cycle(3, 0) + gray_cycle(4, 3)
    require(rejected(lambda: prefix_states(word[:-1], 7)), "restoration control")
    points = prefix_states(word, 7)
    require(coverage(points, 7) == 128 and len(points) == 23, "positive word failed")
    p = {0, 1, 2, 3, 4, 8, 12}
    basis = [5, 6, 9, 11]
    require(len({linear_image(x, basis) for x in range(16)}) == 16, "singular GL map")
    q = {x for x in range(16) if linear_image(x, basis) in p}
    require(q == {0, 3, 5, 11, 12, 14, 15}, "GL fixture changed")
    require(prefix_states([0, 1, 0, 1, 2, 3, 2, 3], 4) == p, "original walk failed")
    zero_degree = sum((1 << j) in q for j in range(4))
    require(coverage(p, 4) == coverage(q, 4) == 16 and zero_degree == 0, "GL control failed")
    require(direct_weights(sorted(p), 4) == direct_weights(sorted(q), 4), "GL spectrum changed")
    return ({"steps": len(word), "distinct_prefixes": len(points), "coverage": 128,
             "restored": True},
            {"duplicates_rejected": True, "out_of_range_rejected": True,
             "removed_point_rejected": True, "removed_points_lose_coverage": losses,
             "balanced_character_detected": True, "affine_balance_preserved": True,
             "nonrestored_rejected": True, "wrong_cut_rejected": True,
             "linear_sixteen_point_rank": cube_rank, "pendant_component_retained": True,
             "disconnected_six_fifteen_rejected": True,
             "simple_support_basis_retained": True, "pendant_support_basis_retained": True,
             "pendant_direction_without_cycle_edge_retained": True},
            {"dimension": 4, "original_coverage": 16, "transformed_coverage": 16,
             "zero_degree": zero_degree, "same_character_weights": True})


def run(data_path=None):
    path = Path(data_path) if data_path is not None else Path(__file__).with_name("table6.json")
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() ==
            "fbf0f123bb6c037ce990c0a527f1aafbb30a70da0a941ac1eec894ea6166f88c",
            "Table 6 transcription digest changed")
    data = json.loads(raw)
    require(data["dimension"] == 7, "wrong ambient dimension")
    representatives = data["representatives"]
    require(len(representatives) == 5 and [rep["id"] for rep in representatives] == list(range(1, 6)),
            "expected five ordered Table 6 classes")
    receipts = [representative_receipt(rep) for rep in representatives]
    positive_word, negative_controls, gl_counterexample = controls(representatives)
    screen = size21_screen(data["size20_representatives"])
    return {"dimension": 7, "representatives": receipts,
            "correspondence": small_correspondence(), "positive_word": positive_word,
            "controls": negative_controls, "gl_counterexample": gl_counterexample,
            "component_rank_lemma": component_rank_check(),
            "size21_screen": screen,
            "support_exclusion": size21_support_exclusion(data["size20_representatives"], screen)}


if __name__ == "__main__":
    import sys
    print(json.dumps(run(sys.argv[1] if len(sys.argv) > 1 else None), indent=2, sort_keys=True))
    print("PASS independent covering-code checks")
