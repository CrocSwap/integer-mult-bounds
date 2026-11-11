#!/usr/bin/env python3
"""Weight-3 cover when exactly one of (10, 14) and (11, 13) is weight 3.

Hypothesis, inherited from the one-index exchange and not re-proved here: the
only failed diagonal index in 4..22 is the centre, so s=4..21 are free-type
states in the layered graph rebuilt below. This program exhausts the finite
subfamily on which those two pairs share different diagonal masks and exactly
one of the two sums is weight 3.

On that subfamily the weight-3 end is a (10, 14) shape. The (11, 13) shape
cannot be the weight-3 end, because its s=13 usage is already 3 on the mask
and every successor keeps that mask. Each of the 180 shapes has four states
at the other pair and three routes through s=12. The cover is 3, or 4 when
(9, 15) is the complement pair. Both values are attained by explicit words.

Evidence class: exhaustive finite census of a finite free-type graph, plus the
slot bounds rechecked on the same graph. Not a heuristic search, and not an
unrestricted c=7 theorem. No kappa change.
"""

import itertools

K = 6
SOURCES = tuple(range(K))
ALLOWED = (0, 1, 7, 8, 14)
MASK_VALUES = (1, 8)
LAYER_SIZES = (
    120, 420, 1120, 2400, 4320, 6720, 9120, 10920, 11600,
    10920, 9120, 6720, 4320, 2400, 1120, 420, 120, 20,
)
OFF_SUMS = (10, 17, 24, 31, 38, 52, 59, 66, 73, 80)
# Canonical shape M={0,1,2}, anchor 0, pair {3,4}, remainder 5.
# N removes 1 and adds 3. The two witness routes share this N.
CANON_MASK = frozenset((0, 1, 2))
CANON_N = frozenset((0, 2, 3))
CANON_R = frozenset((0, 3, 4))
CANON_COMPLEMENT = frozenset((3, 4, 5))
# Non-complement endpoints, s=12 carries N and is not a block. Cover 3.
PLAIN_WORD = "012221000134213555443345344555332411000122"
# Complement endpoints, s=12 carries R and (33, 33) repeats M. Cover 4.
SHARP_WORD = "012221100034215554433345334455534210001122"


def fail(message):
    raise SystemExit("FAIL: " + message)


def masks():
    return [frozenset(choice) for choice in itertools.combinations(SOURCES, 3)]


def weight3_mask(vector):
    support = []
    for source, value in enumerate(vector):
        if value not in ALLOWED:
            return None
        if value in MASK_VALUES:
            support.append(source)
    if len(support) != 3:
        return None
    return frozenset(support)


def middle(usage, mask):
    return tuple(7 - 2 * usage[source] - (1 if source in mask else 0) for source in SOURCES)


def prefix_of(usage, mask):
    return tuple(usage[source] + (1 if source in mask else 0) for source in SOURCES)


def letter_moves(usage, mask):
    counts = middle(usage, mask)
    if min(counts) < 0:
        return []
    found = []
    for source in SOURCES:
        if usage[source] >= 3 or counts[source] < 2:
            continue
        updated = list(usage)
        updated[source] += 1
        found.append((tuple(updated), mask))
    for removed in mask:
        if usage[removed] >= 3 or counts[removed] < 1:
            continue
        for added in SOURCES:
            if added in mask or counts[added] < 1:
                continue
            updated = list(usage)
            updated[removed] += 1
            moved = frozenset((set(mask) - {removed}) | {added})
            found.append((tuple(updated), moved))
    return found


def johnson_moves(usage, mask):
    counts = middle(usage, mask)
    if min(counts) < 0:
        return []
    found = []
    current = list(usage)
    for removed in mask:
        if usage[removed] >= 3 or counts[removed] < 1:
            continue
        for added in SOURCES:
            if added in mask or counts[added] < 1:
                continue
            current[removed] += 1
            moved = frozenset((set(mask) - {removed}) | {added})
            found.append((tuple(current), moved))
            current[removed] -= 1
    for source in SOURCES:
        if usage[source] >= 3 or counts[source] < 2:
            continue
        current[source] += 1
        found.append((tuple(current), mask))
        current[source] -= 1
    return found


def start_states():
    found = []
    seen = set()
    for last in SOURCES:
        for counts in itertools.product(range(5), repeat=K):
            if sum(counts) != 4:
                continue
            suffix = tuple(6 if source == last else 7 for source in SOURCES)
            summed = tuple(counts[source] + suffix[source] for source in SOURCES)
            mask = weight3_mask(summed)
            if mask is None:
                continue
            if sorted(summed) != [7, 7, 7, 8, 8, 8]:
                fail("s=4 weight-3 vector is not free type")
            usage = tuple(1 if source == last else 0 for source in SOURCES)
            if prefix_of(usage, mask) != counts:
                fail("s=4 prefix formula missed a state")
            state = (usage, mask)
            if state in seen:
                fail("duplicate s=4 state")
            seen.add(state)
            found.append(state)
    if len(found) != 120:
        fail("expected 120 states at s=4, found %s" % len(found))
    return found


def build_layers():
    layers = [start_states()]
    successors = []
    for _ in range(17):
        index = {}
        states = []
        edges = []
        for usage, mask in layers[-1]:
            letter = letter_moves(usage, mask)
            johnson = johnson_moves(usage, mask)
            if set(letter) != set(johnson) or len(letter) != len(set(letter)):
                fail("move generators diverged")
            targets = []
            for new_usage, new_mask in letter:
                delta = [new_usage[source] - usage[source] for source in SOURCES]
                increased = [source for source, value in enumerate(delta) if value == 1]
                if any(value < 0 for value in delta) or len(increased) != 1 or sum(delta) != 1:
                    fail("a free-type step does not add exactly one suffix letter")
                key = (new_usage, new_mask)
                if key not in index:
                    index[key] = len(states)
                    states.append(key)
                targets.append(index[key])
            edges.append(targets)
        layers.append(states)
        successors.append(edges)
    sizes = tuple(len(layer) for layer in layers)
    if sizes != LAYER_SIZES:
        fail("free-type layer sizes changed: " + str(sizes))
    return layers, successors


def state_index(layers):
    return [{state: position for position, state in enumerate(layer)} for layer in layers]


def reverse_edges(successors):
    reverse = []
    for edges in successors:
        width = max((max(targets) for targets in edges if targets), default=-1) + 1
        bucket = [[] for _ in range(width)]
        for source, targets in enumerate(edges):
            for target in targets:
                bucket[target].append(source)
        reverse.append(bucket)
    return reverse


def check_terminal_and_centre(layers):
    seen = []
    for usage, mask in layers[-1]:
        if usage != (3, 3, 3, 3, 3, 3):
            fail("s=21 usage is not saturated")
        if letter_moves(usage, mask):
            fail("s=21 still has an in-type step")
        seen.append(mask)
        off = [source for source in SOURCES if source not in mask]
        if len(off) != 3:
            fail("centre complement is not a triple")
        for order in itertools.permutations(off):
            q22 = [4 if source in mask else 3 for source in SOURCES]
            q22[order[0]] += 1
            q23 = q22[:]
            q23[order[1]] += 1
            centre = [q22[source] + q23[source] for source in SOURCES]
            if 6 not in centre or weight3_mask(tuple(centre)) is not None:
                fail("centre sum became weight 3: " + str(centre))
    if len(seen) != 20 or len(set(seen)) != 20:
        fail("s=21 is not one state per mask")


def check_prefix_bounds(layers):
    for layer, states in enumerate(layers):
        for usage, mask in states:
            prefix = prefix_of(usage, mask)
            if any(value < 0 or value > 4 for value in prefix):
                fail("free-type prefix left 0..4 at s=%s" % (layer + 4))
            if layer == 0 and any(value > 2 for value in prefix):
                fail("s=4 prefix has a coordinate above 2")


def q_low_high(index):
    if index <= 3:
        return 0, 2
    if index <= 21:
        return 0, 4
    if index <= 23:
        return 3, 4
    return 4, 7


def bound_reason(left, right, sigma):
    if 4 <= left and right <= 21:
        return None
    if (left, right) == (33, 33):
        return None
    low = q_low_high(left)[0] + q_low_high(right)[0]
    high = q_low_high(left)[1] + q_low_high(right)[1]
    possible = {value for value in ALLOWED if low <= value <= high}
    if not possible:
        return "empty"
    if possible <= {0, 1} and sigma != 3:
        return "small"
    if possible <= {7, 8} and sigma != 45:
        return "mid"
    if possible <= {8, 14} and sigma != 66:
        return "high"
    if left >= 24 and sigma == 66 and left < right:
        return "gap"
    return None


def classify_slots():
    blocked = graph = block = 0
    uncovered = []
    for sigma in OFF_SUMS:
        for left in range(0, sigma // 2 + 1):
            right = sigma - left
            if right > 41:
                continue
            reason = bound_reason(left, right, sigma)
            if reason is None and (left, right) == (33, 33):
                block += 1
            elif reason is None:
                graph += 1
            else:
                blocked += 1
            if reason is None and not (4 <= left and right <= 21) and (left, right) != (33, 33):
                uncovered.append((left, right, sigma))
    if uncovered:
        fail("slots without an obstruction: " + str(uncovered))
    if (blocked, graph, block) != (82, 25, 1):
        fail("slot census changed: %s %s %s" % (blocked, graph, block))
    return blocked


def marginal_hit(left_prefixes, right_prefixes, sigma):
    shapes = []
    for mask in itertools.combinations(SOURCES, 3):
        others = [source for source in SOURCES if source not in mask]
        for mask_values in itertools.product(MASK_VALUES, repeat=3):
            for other_values in itertools.product((0, 7), repeat=3):
                vector = [0] * K
                for position, source in enumerate(mask):
                    vector[source] = mask_values[position]
                for position, source in enumerate(others):
                    vector[source] = other_values[position]
                if sum(vector) == sigma and weight3_mask(tuple(vector)) is not None:
                    shapes.append(tuple(vector))
    right_set = set(right_prefixes)
    for start in left_prefixes:
        for vector in shapes:
            needed = tuple(vector[source] - start[source] for source in SOURCES)
            if min(needed) < 0:
                continue
            if needed in right_set:
                return True
    return False


def joint_hits(layers, successors, left_index, right_index):
    current = [1 << position for position in range(len(layers[left_index]))]
    for layer in range(left_index, right_index):
        nxt = [0] * len(layers[layer + 1])
        for position, bits in enumerate(current):
            if not bits:
                continue
            for target in successors[layer][position]:
                nxt[target] |= bits
        current = nxt
    hits = []
    for target, bits in enumerate(current):
        if not bits:
            continue
        right_usage, right_mask = layers[right_index][target]
        right_prefix = prefix_of(right_usage, right_mask)
        remaining = bits
        while remaining:
            bit = remaining & -remaining
            source_state = bit.bit_length() - 1
            remaining ^= bit
            left_usage, left_mask = layers[left_index][source_state]
            left_prefix = prefix_of(left_usage, left_mask)
            vector = tuple(left_prefix[source] + right_prefix[source] for source in SOURCES)
            realized = weight3_mask(vector)
            if realized is not None:
                hits.append((left_mask, right_mask, realized, left_usage, right_usage))
    return hits


def classify_graph(layers, successors):
    prefixes = [[prefix_of(usage, mask) for usage, mask in layer] for layer in layers]
    census = {}
    slots = 0
    shaped = []
    for sigma in OFF_SUMS:
        for left in range(4, 22):
            right = sigma - left
            if right < left or right > 21:
                continue
            slots += 1
            if not marginal_hit(prefixes[left - 4], prefixes[right - 4], sigma):
                continue
            for left_mask, right_mask, realized, left_usage, right_usage in joint_hits(
                layers, successors, left - 4, right - 4
            ):
                if realized == left_mask or realized == right_mask:
                    kind = "internal"
                elif left != right and left_mask == right_mask:
                    kind = "novel"
                else:
                    fail("unclassified joint pair s=%s t=%s" % (left, right))
                census[(left, right, kind)] = census.get((left, right, kind), 0) + 1
                if (left, right) in ((10, 14), (11, 13)):
                    shaped.append((left, right, left_mask, right_mask, realized, left_usage, right_usage))
    if slots != 25:
        fail("expected 25 graph slots, found %s" % slots)
    expected = {
        (12, 12, "internal"): 20,
        (11, 13, "novel"): 180,
        (10, 14, "novel"): 180,
        (9, 15, "novel"): 20,
    }
    if census != expected:
        fail("joint census changed: " + str(sorted(census.items())))
    return shaped


def shapes_1014():
    found = []
    for mask in masks():
        off = [source for source in SOURCES if source not in mask]
        for anchor in mask:
            usage = tuple(3 if source == anchor else (2 if source in mask else 0) for source in SOURCES)
            for pair in itertools.combinations(off, 2):
                realized = frozenset((anchor,) + pair)
                right = tuple(usage[source] + (0 if source == anchor else (1 if source in mask or source in pair else 0)) for source in SOURCES)
                found.append((usage, right, mask, realized))
    return found


def shapes_1113():
    found = []
    for mask in masks():
        off = [source for source in SOURCES if source not in mask]
        for pivot in mask:
            usage = tuple(2 if source == pivot else (3 if source in mask else 0) for source in SOURCES)
            for extra in off:
                right = list(usage)
                right[pivot] += 1
                right[extra] += 1
                realized = frozenset((set(mask) - {pivot}) | {extra})
                found.append((usage, tuple(right), mask, realized))
    return found


def check_hits_are_shapes(layers, successors, index, shaped):
    """Every weight-3 hit is a shape, and an (11, 13) shape cannot change mask."""
    expected = {10: set(), 14: set()}
    for usage, right, mask, realized in shapes_1014():
        vector = tuple(prefix_of(usage, mask)[source] + prefix_of(right, mask)[source] for source in SOURCES)
        if weight3_mask(vector) != realized or realized == mask:
            fail("(10, 14) shape is not a new weight-3 mask")
        expected[10].add((mask, mask, realized, usage, right))
    for usage, right, mask, realized in shapes_1113():
        vector = tuple(prefix_of(usage, mask)[source] + prefix_of(right, mask)[source] for source in SOURCES)
        if weight3_mask(vector) != realized or realized == mask:
            fail("(11, 13) shape is not a new weight-3 mask")
        expected[14].add((mask, mask, realized, usage, right))
        state = index[9][(right, mask)]
        successor_masks = {layers[10][target][1] for target in successors[9][state]}
        if successor_masks != {mask}:
            fail("an (11, 13) shape has a mask-changing successor")
        if any(value != 3 for source, value in enumerate(right) if source in mask):
            fail("an (11, 13) shape is not saturated on its mask")
    got = {10: set(), 14: set()}
    for left, right, left_mask, right_mask, realized, left_usage, right_usage in shaped:
        key = 10 if (left, right) == (10, 14) else 14
        got[key].add((left_mask, right_mask, realized, left_usage, right_usage))
    if got[10] != expected[10] or len(got[10]) != 180:
        fail("(10, 14) hits are not the 180 shapes")
    if got[14] != expected[14] or len(got[14]) != 180:
        fail("(11, 13) hits are not the 180 shapes")


def pair33(usage):
    """2 q_33, with q_33 = 7 - (suffix usage on [33, 42))."""
    return weight3_mask(tuple(14 - 2 * usage[source] for source in SOURCES))


def route_kind(shape_mask, nmask, realized, m12, block):
    if m12 == nmask:
        where = "N"
    elif m12 == realized:
        where = "R"
    else:
        where = "other"
    if block is None:
        support = "none"
    elif block == shape_mask:
        support = "M"
    else:
        support = "other"
    return (where, support)


def prefix_paths(successors, reverse, state10):
    cone = {6: {state10}}
    for layer in range(6, 0, -1):
        previous = set()
        for state in cone[layer]:
            previous.update(reverse[layer - 1][state])
        cone[layer - 1] = previous
    ways = {state: 1 for state in cone[0]}
    at_parents = None
    for layer in range(0, 6):
        nxt = {}
        for state, count in ways.items():
            for target in successors[layer][state]:
                if target in cone[layer + 1]:
                    nxt[target] = nxt.get(target, 0) + count
        ways = nxt
        if layer == 4:
            at_parents = dict(ways)
    return cone, ways.get(state10, 0), at_parents


def early_mask_is_diagonal(usage, mask):
    final = [source for source in SOURCES if usage[source] == 1]
    if sum(usage) != 1 or len(final) != 1 or final[0] not in mask:
        fail("s=4 final letter left the diagonal mask")
    prefix = list(prefix_of(usage, mask))
    realized = []
    for source in SOURCES:
        if prefix[source] == 0:
            continue
        trial = prefix[:]
        trial[source] -= 1
        mask_of = weight3_mask(tuple(trial))
        if mask_of is not None:
            realized.append(mask_of)
    if realized != [mask]:
        fail("(0, 3) can leave the s=4 mask: " + str(realized))


def check_prefix(layers, successors, reverse, state10, mask, usage10):
    cone, paths, at_parents = prefix_paths(successors, reverse, state10)
    if paths != 210:
        fail("expected 210 prefix paths, found %s" % paths)
    signature = tuple(len(cone[layer]) for layer in range(7))
    if signature != (3, 6, 8, 8, 6, 3, 1):
        fail("prefix cone signature changed: %s" % (signature,))
    for layer, states in cone.items():
        for state in states:
            if layers[layer][state][1] != mask:
                fail("prefix cone carries a mask other than M")
            usage = layers[layer][state][0]
            if any(usage[source] for source in SOURCES if source not in mask):
                fail("prefix usage leaves M")
    for state in cone[0]:
        early_mask_is_diagonal(*layers[0][state])
    parents = reverse[5][state10]
    if len(parents) != 3:
        fail("s=10 shape does not have three s=9 parents")
    parent_usages = {layers[5][state][0] for state in parents}
    expect = set()
    for source in mask:
        reduced = list(usage10)
        reduced[source] -= 1
        expect.add(tuple(reduced))
    if parent_usages != expect:
        fail("s=9 parents are not the three stays inside the mask")
    complement = tuple(2 if source in mask else 0 for source in SOURCES)
    if complement not in parent_usages:
        fail("complement s=9 usage is missing")
    for state in parents:
        if at_parents.get(state, 0) <= 0:
            fail("an s=9 parent has no path from s=4")
    return parents


def check_tail(layers, successors, state14, mask, usage14):
    children = successors[10][state14]
    if len(children) != 3:
        fail("s=14 shape does not have three s=15 children")
    child_usages = {layers[11][state][0] for state in children}
    off = [source for source in SOURCES if source not in mask]
    expect = set()
    for source in off:
        grown = list(usage14)
        grown[source] += 1
        expect.add(tuple(grown))
    if child_usages != expect:
        fail("s=15 children are not the three off-mask stays")
    complement = tuple(3 if source in mask else 1 for source in SOURCES)
    if complement not in child_usages:
        fail("complement s=15 usage is missing")
    frontier = {state14}
    for layer in range(10, 17):
        nxt = set()
        for state in frontier:
            targets = successors[layer][state]
            if not targets:
                fail("tail died before s=21")
            for target in targets:
                if layers[layer + 1][target][1] != mask:
                    fail("tail mask left M")
                grown = layers[layer + 1][target][0]
                start = layers[layer][state][0]
                increased = [source for source in SOURCES if grown[source] != start[source]]
                if len(increased) != 1 or increased[0] in mask:
                    fail("tail step is not a stay off M")
                nxt.add(target)
        frontier = nxt
    if len(frontier) != 1:
        fail("tail does not end at one s=21 state")
    usage, state_mask = layers[17][next(iter(frontier))]
    if usage != (3, 3, 3, 3, 3, 3) or state_mask != mask:
        fail("tail does not saturate on M")
    return children


def check_pair_sums(layers, parents, children, mask):
    complement_left = tuple(2 if source in mask else 0 for source in SOURCES)
    complement_right = tuple(3 if source in mask else 1 for source in SOURCES)
    hits = []
    for left in parents:
        for right in children:
            vector = tuple(
                prefix_of(layers[5][left][0], mask)[source]
                + prefix_of(layers[11][right][0], mask)[source]
                for source in SOURCES
            )
            realized = weight3_mask(vector)
            is_complement = (
                layers[5][left][0] == complement_left and layers[11][right][0] == complement_right
            )
            if is_complement:
                if realized != frozenset(SOURCES) - mask:
                    fail("complement endpoints do not realize M^c")
                hits.append(realized)
            elif realized is not None:
                fail("non-complement (9, 15) sum is weight 3: " + str(vector))
    if hits != [frozenset(SOURCES) - mask]:
        fail("expected one complement (9, 15) sum, found %s" % len(hits))


def enumerate_middles(layers, successors, index):
    """Every different-mask continuation of a (10, 14) shape.

    Returns the canonical route states used by the two witness words.
    """
    shapes = 0
    routes = 0
    canonical = None
    for mask in masks():
        off = [source for source in SOURCES if source not in mask]
        complement = frozenset(off)
        for anchor in mask:
            usage10 = tuple(3 if source == anchor else (2 if source in mask else 0) for source in SOURCES)
            state10 = index[6][(usage10, mask)]
            for pair in itertools.combinations(off, 2):
                usage14 = tuple(3 if source in mask else (1 if source in pair else 0) for source in SOURCES)
                state14 = index[10][(usage14, mask)]
                realized = frozenset((anchor,) + pair)
                vector = tuple(
                    prefix_of(usage10, mask)[source] + prefix_of(usage14, mask)[source]
                    for source in SOURCES
                )
                if weight3_mask(vector) != realized:
                    fail("(10, 14) endpoints do not realize R")
                if realized == mask or realized == complement or anchor not in realized:
                    fail("R collapsed into M or M^c")
                groups = {}
                for state11 in successors[6][state10]:
                    nmask = layers[7][state11][1]
                    if nmask == mask:
                        continue
                    for state12 in successors[7][state11]:
                        for state13 in successors[8][state12]:
                            if layers[9][state13][1] != nmask:
                                continue
                            if state14 not in successors[9][state13]:
                                continue
                            m12 = layers[8][state12][1]
                            block = pair33(layers[8][state12][0])
                            bucket = groups.setdefault(
                                nmask,
                                {"s11": set(), "s13": set(), "kinds": []},
                            )
                            bucket["s11"].add(state11)
                            bucket["s13"].add(state13)
                            bucket["kinds"].append(route_kind(mask, nmask, realized, m12, block))
                            added = nmask - mask
                            removed = mask - nmask
                            if len(added) != 1 or len(removed) != 1:
                                fail("a different mask is not a single transposition")
                            if next(iter(removed)) == anchor or next(iter(added)) not in pair:
                                fail("the transposition is not a non-anchor for a pair source")
                            if nmask == realized or nmask == complement or realized == complement:
                                fail("N, R and M^c are not distinct from the image")
                            routes += 1
                if len(groups) != 4:
                    fail("expected 4 different masks at (11, 13), found %s" % len(groups))
                expect_kinds = [("N", "M"), ("N", "none"), ("R", "M")]
                for nmask, bucket in groups.items():
                    if len(bucket["s11"]) != 1 or len(bucket["s13"]) != 1:
                        fail("a different mask does not determine unique endpoint states")
                    if sorted(bucket["kinds"]) != expect_kinds:
                        fail("s=12 routes are not the three kinds: " + str(bucket["kinds"]))
                    state11 = next(iter(bucket["s11"]))
                    state13 = next(iter(bucket["s13"]))
                    summed = tuple(
                        prefix_of(layers[7][state11][0], nmask)[source]
                        + prefix_of(layers[9][state13][0], nmask)[source]
                        for source in SOURCES
                    )
                    if weight3_mask(summed) is not None:
                        fail("different-mask (11, 13) sum is weight 3: " + str(summed))
                    if mask == CANON_MASK and nmask == CANON_N and realized == CANON_R:
                        canonical = (state10, state11, state13, state14, bucket["kinds"])
                shapes += 1
    if shapes != 180 or routes != 2160:
        fail("expected 180 shapes and 2160 routes, found %s %s" % (shapes, routes))
    if canonical is None:
        fail("canonical shape was not reached")
    return shapes, routes, canonical


def check_frozen_ends(layers, successors, reverse, index):
    seen10 = set()
    seen14 = set()
    endpoint_checks = 0
    for mask in masks():
        off = [source for source in SOURCES if source not in mask]
        for anchor in mask:
            usage10 = tuple(3 if source == anchor else (2 if source in mask else 0) for source in SOURCES)
            state10 = index[6][(usage10, mask)]
            if state10 not in seen10:
                parents = check_prefix(layers, successors, reverse, state10, mask, usage10)
                seen10.add(state10)
            else:
                parents = reverse[5][state10]
            for pair in itertools.combinations(off, 2):
                usage14 = tuple(3 if source in mask else (1 if source in pair else 0) for source in SOURCES)
                state14 = index[10][(usage14, mask)]
                if state14 not in seen14:
                    children = check_tail(layers, successors, state14, mask, usage14)
                    seen14.add(state14)
                else:
                    children = successors[10][state14]
                check_pair_sums(layers, parents, children, mask)
                endpoint_checks += 1
    if len(seen10) != 60 or len(seen14) != 60 or endpoint_checks != 180:
        fail("frozen-end census is not 60/60/180")


def extend_path(layers, successors, reverse, fixed):
    path = dict(fixed)
    state = path[min(path)]
    for layer in range(min(path), 0, -1):
        preds = reverse[layer - 1][state]
        if not preds:
            fail("canonical ancestor died at s=%s" % (layer + 3))
        state = min(preds, key=lambda item: layers[layer - 1][item][0])
        path[layer - 1] = state
    state = path[max(fixed)]
    for layer in range(max(fixed), 17):
        targets = successors[layer][state]
        if not targets:
            fail("canonical descendant died at s=%s" % (layer + 4))
        state = min(
            targets,
            key=lambda item: (tuple(sorted(layers[layer + 1][item][1])), layers[layer + 1][item][0]),
        )
        path[layer + 1] = state
    if sorted(path) != list(range(18)):
        fail("witness path missed a layer")
    return path


def assemble_word(layers, path):
    letters = [None] * 42
    prefixes = []
    for layer in range(18):
        usage, mask = layers[layer][path[layer]]
        prefixes.append(prefix_of(usage, mask))
    for layer in range(17):
        delta = [prefixes[layer + 1][source] - prefixes[layer][source] for source in SOURCES]
        increased = [source for source, value in enumerate(delta) if value == 1]
        if any(value < 0 for value in delta) or len(increased) != 1:
            fail("witness prefix does not add one letter")
        letters[layer + 4] = increased[0]
    counts = list(prefixes[0])
    twos = [source for source, value in enumerate(counts) if value == 2]
    if len(twos) != 1:
        fail("s=4 prefix does not have one coordinate 2")
    letters[3] = twos[0]
    counts[twos[0]] -= 1
    rest = [source for source, value in enumerate(counts) for _ in range(value)]
    if len(rest) != 3 or sorted(rest) != sorted(CANON_MASK):
        fail("s=4 remainder is not one copy of M")
    letters[0], letters[1], letters[2] = rest
    usage4 = layers[0][path[0]][0]
    finals = [source for source, value in enumerate(usage4) if value == 1]
    if len(finals) != 1:
        fail("s=4 suffix is not one letter")
    letters[41] = finals[0]
    for layer in range(17):
        before = layers[layer][path[layer]][0]
        after = layers[layer + 1][path[layer + 1]][0]
        delta = [after[source] - before[source] for source in SOURCES]
        increased = [source for source, value in enumerate(delta) if value == 1]
        if any(value < 0 for value in delta) or len(increased) != 1:
            fail("witness suffix does not add one letter")
        # Stepping from s=layer+4 to s=layer+5 adds the letter at index 40-layer.
        letters[40 - layer] = increased[0]
    mask21 = layers[17][path[17]][1]
    off = [source for source in SOURCES if source not in mask21]
    if len(off) != 3:
        fail("s=21 complement is not a triple")
    letters[21], letters[22], letters[23] = off
    if any(letter is None for letter in letters):
        fail("witness word has an empty position")
    word = "".join(str(letter) for letter in letters)
    # The suffix window and the prefix counts have to describe the same states.
    running = [0] * K
    for index, letter in enumerate(letters):
        running[letter] += 1
        if 4 <= index + 1 <= 21 and tuple(running) != prefixes[index + 1 - 4]:
            fail("witness prefix drifted at s=%s" % (index + 1))
        if 4 <= index + 1 <= 21:
            usage = layers[index + 1 - 4][path[index + 1 - 4]][0]
            suffix = tuple(
                sum(1 for position in range(45 - (index + 1), 42) if letters[position] == source)
                for source in SOURCES
            )
            if suffix != usage:
                fail("witness suffix drifted at s=%s" % (index + 1))
    return word


def inventory(word):
    if len(word) != 42 or any(character not in "012345" for character in word):
        fail("word is not a length-42 word on six sources")
    letters = [int(character) for character in word]
    if any(letters.count(source) != 7 for source in SOURCES):
        fail("word does not call every source seven times")
    running = [0] * K
    found = [tuple(running)]
    for letter in letters:
        running[letter] += 1
        found.append(tuple(running))
    realized = {}
    for left in range(42):
        for right in range(left, 42):
            if (left + right - 3) % 7:
                continue
            mask = weight3_mask(tuple(found[left][source] + found[right][source] for source in SOURCES))
            if mask is not None:
                realized.setdefault(mask, []).append((left, right))
    diagonal = [
        weight3_mask(tuple(found[index][source] + found[45 - index][source] for source in SOURCES))
        for index in range(4, 23)
    ]
    return found, realized, diagonal


def audit_word(word, expect):
    _found, realized, diagonal = inventory(word)
    if any(mask is None for mask in diagonal[:18]) or diagonal[18] is not None:
        fail("witness is not centre-only")
    if set(realized) != expect:
        fail("witness cover is not " + str(sorted(tuple(sorted(mask)) for mask in expect)))
    if (10, 14) not in realized[CANON_R]:
        fail("witness does not realize R at (10, 14)")
    if CANON_N in realized and (11, 13) in realized[CANON_N]:
        fail("witness realizes a weight-3 mask at (11, 13) on N")
    # (11, 13) itself must not be weight 3, whatever mask it would have had.
    pair = weight3_mask(
        tuple(
            inventory_prefix(word, 11)[source] + inventory_prefix(word, 13)[source]
            for source in SOURCES
        )
    )
    if pair is not None:
        fail("witness (11, 13) is weight 3")
    return len(realized)


def inventory_prefix(word, index):
    letters = [int(character) for character in word]
    return tuple(sum(1 for position in range(index) if letters[position] == source) for source in SOURCES)


def build_witnesses(layers, successors, reverse, index, canonical):
    state10, state11, state13, state14, _kinds = canonical
    if layers[6][state10] != ((3, 2, 2, 0, 0, 0), CANON_MASK):
        fail("canonical s=10 state drifted")
    if layers[7][state11][1] != CANON_N or layers[9][state13][1] != CANON_N:
        fail("canonical (11, 13) states are not on N")
    plain12 = index[8][((3, 3, 2, 0, 1, 0), CANON_N)]
    sharp12 = index[8][((3, 3, 3, 0, 0, 0), CANON_R)]
    if plain12 not in successors[7][state11] or state13 not in successors[8][plain12]:
        fail("plain s=12 route is not an edge")
    if sharp12 not in successors[7][state11] or state13 not in successors[8][sharp12]:
        fail("sharp s=12 route is not an edge")
    if state14 not in successors[9][state13] or state11 not in successors[6][state10]:
        fail("canonical shape edges are missing")
    parent_plain = index[5][((3, 1, 2, 0, 0, 0), CANON_MASK)]
    parent_complement = index[5][((2, 2, 2, 0, 0, 0), CANON_MASK)]
    child_plain = index[11][((3, 3, 3, 2, 1, 0), CANON_MASK)]
    child_complement = index[11][((3, 3, 3, 1, 1, 1), CANON_MASK)]
    for parent in (parent_plain, parent_complement):
        if parent not in reverse[5][state10]:
            fail("canonical s=9 parent is not attached")
    for child in (child_plain, child_complement):
        if child not in successors[10][state14]:
            fail("canonical s=15 child is not attached")
    plain = extend_path(
        layers,
        successors,
        reverse,
        {5: parent_plain, 6: state10, 7: state11, 8: plain12, 9: state13, 10: state14, 11: child_plain},
    )
    sharp = extend_path(
        layers,
        successors,
        reverse,
        {
            5: parent_complement,
            6: state10,
            7: state11,
            8: sharp12,
            9: state13,
            10: state14,
            11: child_complement,
        },
    )
    plain_word = assemble_word(layers, plain)
    sharp_word = assemble_word(layers, sharp)
    if plain_word != PLAIN_WORD or sharp_word != SHARP_WORD:
        fail("canonical witness words changed")
    plain_cover = audit_word(plain_word, {CANON_MASK, CANON_N, CANON_R})
    sharp_cover = audit_word(sharp_word, {CANON_MASK, CANON_N, CANON_R, CANON_COMPLEMENT})
    if plain_cover != 3 or sharp_cover != 4:
        fail("witness covers are not 3 and 4")
    mutated = list(plain_word)
    mutated[0], mutated[21] = mutated[21], mutated[0]
    if mutated[0] == plain_word[0]:
        fail("count-preserving swap did not move a letter")
    try:
        audit_word("".join(mutated), {CANON_MASK, CANON_N, CANON_R})
    except SystemExit as error:
        if not str(error).startswith("FAIL:"):
            raise
    else:
        fail("count-preserving swap was accepted as the cover-3 word")
    return plain_word, sharp_word


def main():
    layers, successors = build_layers()
    check_terminal_and_centre(layers)
    check_prefix_bounds(layers)
    blocked = classify_slots()
    index = state_index(layers)
    reverse = reverse_edges(successors)
    shaped = classify_graph(layers, successors)
    check_hits_are_shapes(layers, successors, index, shaped)
    check_frozen_ends(layers, successors, reverse, index)
    shapes, routes, canonical = enumerate_middles(layers, successors, index)
    plain_word, sharp_word = build_witnesses(layers, successors, reverse, index, canonical)
    if blocked != 82 or shapes != 180 or routes != 2160:
        fail("census floor failed")
    print(
        "PASS_SIX_SOURCE_C7_ONE_NEW_PAIR_COVER "
        "shapes=180/180 routes=2160 states_per_shape=4 routes_per_state=3 "
        "case_b_mask_changes=0 different_mask_weight3_other=0 "
        "cover_without_complement=3 cover_with_complement=4 "
        "witness_cover=3 complement_witness_cover=4 "
        "slots_blocked=82 graph_slots=25 "
        "joint=12/12:20,11/13:180,10/14:180,9/15:20 "
        "prefix_paths=210 cone=3,6,8,8,6,3,1 "
        "plain_word=%s sharp_word=%s controls=12"
        % (plain_word, sharp_word)
    )


if __name__ == "__main__":
    main()
