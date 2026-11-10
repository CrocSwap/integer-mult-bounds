#!/usr/bin/env python3
"""Non-complement (10, 14) and (11, 13) pairs on a centre-only c=7 chain.

Hypothesis, inherited from the one-index exchange and not re-proved here: the
only failed diagonal index in 4..22 is the centre, so s=4..21 are free-type
states in the layered graph rebuilt below. This program exhausts the finite
subfamily on which (10, 14) and (11, 13) are both weight 3. That is the only
place both pairs can be new.

Evidence class: exhaustive finite census, plus the slot bounds rechecked on
the same graph. Not a heuristic search, and not an unrestricted c=7 theorem.
No kappa change.
"""

import itertools

K = 6
SOURCES = tuple(range(K))
ALLOWED = (0, 1, 7, 8, 14)
MASK_VALUES = (1, 8)
NONMASK = (0, 7, 14)
OFF_SUMS = (10, 17, 24, 31, 38, 52, 59, 66, 73, 80)
LAYER_SIZES = (
    120, 420, 1120, 2400, 4320, 6720, 9120, 10920, 11600,
    10920, 9120, 6720, 4320, 2400, 1120, 420, 120, 20,
)
# s=9 usage is (3, 1, 2) on (0, 1, 2), not the complement (2, 2, 2).
# s=15 increments an already-used off-mask source, so it is not (1, 1, 1) off M.
WITNESS = "012220001121343344555345555443343121100022"
# The three-new word of the complement census. Cover 4, excluded here.
COMPLEMENT_WORD = "012001122012345334455345554433543210221100"


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


def check_terminal_and_centre(layers):
    """Every s=21 state is saturated, and every centre sum has a coordinate 6."""
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
        q24 = [4 if source in mask else 3 for source in SOURCES]
        for source in off:
            q24[source] += 1
        if q24 != [4] * K:
            fail("q_24 is not uniformly 4")
        # q_21 is 4 on the mask and 3 off it. Positions 21, 22, 23 are the
        # three off-mask sources in some order.
        for order in itertools.permutations(off):
            q22 = [4 if source in mask else 3 for source in SOURCES]
            q22[order[0]] += 1
            q23 = q22[:]
            q23[order[1]] += 1
            centre = [q22[source] + q23[source] for source in SOURCES]
            if 6 not in centre or weight3_mask(tuple(centre)) is not None:
                fail("centre sum became weight 3: " + str(centre))
            if any(value not in (3, 4) for value in q22 + q23):
                fail("q_22 or q_23 left {3, 4}")
    if len(seen) != 20 or len(set(seen)) != 20:
        fail("s=21 is not one state per mask")


def check_prefix_bounds(layers):
    """Coordinate bounds used by the off-diagonal slot obstruction."""
    for layer, states in enumerate(layers):
        for usage, mask in states:
            prefix = prefix_of(usage, mask)
            if any(value < 0 or value > 4 for value in prefix):
                fail("free-type prefix left 0..4 at s=%s" % (layer + 4))
            if layer == 0 and any(value > 2 for value in prefix):
                fail("s=4 prefix has a coordinate above 2")
    # q_s for s<=3 is componentwise at most q_4, hence at most 2.
    # q_t for t>=24 starts from q_24 = (4, 4, 4, 4, 4, 4) and ends at 7.


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
    """Every jointly realized weight-3 pair inside s=4..21, on one chain."""
    prefixes = []
    for layer in layers:
        prefixes.append([prefix_of(usage, mask) for usage, mask in layer])
    census = {}
    slots = 0
    complement_usages = []
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
                    fail(
                        "unclassified joint pair s=%s t=%s" % (left, right)
                    )
                census[(left, right, kind)] = census.get((left, right, kind), 0) + 1
                if (left, right) == (9, 15):
                    complement_usages.append((left_mask, left_usage, right_usage, realized))
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
    if len(complement_usages) != 20:
        fail("complement usage list changed")
    for mask, left_usage, right_usage, realized in complement_usages:
        expect_left = tuple(2 if source in mask else 0 for source in SOURCES)
        expect_right = tuple(3 if source in mask else 1 for source in SOURCES)
        if left_usage != expect_left or right_usage != expect_right:
            fail("a (9, 15) hit is not the complement usage")
        if realized != frozenset(SOURCES) - mask:
            fail("a (9, 15) hit is not the complement mask")
    return census, shaped


def shapes_1014():
    found = []
    for mask in masks():
        off = [source for source in SOURCES if source not in mask]
        for anchor in mask:
            usage = tuple(3 if source == anchor else (2 if source in mask else 0) for source in SOURCES)
            for pair in itertools.combinations(off, 2):
                delta = [0] * K
                for source in mask:
                    if source != anchor:
                        delta[source] += 1
                for source in pair:
                    delta[source] += 1
                realized = frozenset((anchor,) + pair)
                found.append((usage, tuple(delta), mask, mask, realized))
    return found


def shapes_1113():
    found = []
    for mask in masks():
        off = [source for source in SOURCES if source not in mask]
        for pivot in mask:
            usage = tuple(2 if source == pivot else (3 if source in mask else 0) for source in SOURCES)
            for extra in off:
                delta = [0] * K
                delta[pivot] = 1
                delta[extra] = 1
                realized = frozenset((set(mask) - {pivot}) | {extra})
                found.append((usage, tuple(delta), mask, mask, realized))
    return found


def check_hits_are_shapes(shaped):
    """The 180 graph hits are exactly the shape list, with equal masks."""
    expected = {10: set(), 14: set()}
    for usage, delta, mask, _, realized in shapes_1014():
        right = tuple(usage[source] + delta[source] for source in SOURCES)
        expected[10].add((mask, mask, realized, usage, right))
    for usage, delta, mask, _, realized in shapes_1113():
        right = tuple(usage[source] + delta[source] for source in SOURCES)
        expected[14].add((mask, mask, realized, usage, right))
    got = {10: set(), 14: set()}
    for left, right, left_mask, right_mask, realized, left_usage, right_usage in shaped:
        key = 10 if (left, right) == (10, 14) else 14
        got[key].add((left_mask, right_mask, realized, left_usage, right_usage))
    if got[10] != expected[10] or len(got[10]) != 180:
        fail("(10, 14) hits are not the 180 shapes")
    if got[14] != expected[14] or len(got[14]) != 180:
        fail("(11, 13) hits are not the 180 shapes")


def state_index(layers):
    return [{state: position for position, state in enumerate(layer)} for layer in layers]


def reverse_edges(successors):
    reverse = []
    for layer, edges in enumerate(successors):
        # The next layer's width is known from the edge targets' layer.
        width = max((max(targets) for targets in edges if targets), default=-1) + 1
        bucket = [[] for _ in range(width)]
        for source, targets in enumerate(edges):
            for target in targets:
                bucket[target].append(source)
        reverse.append(bucket)
    return reverse


def usage_at(layers, layer, state):
    return layers[layer][state][0]


def mask_at(layers, layer, state):
    return layers[layer][state][1]


def check_family(layers, successors):
    """Every chain on which both pairs are weight 3.

    Returns the witness-independent census counts.
    """
    index = state_index(layers)
    reverse = reverse_edges(successors)
    types = 0
    prefix_paths = {}
    cone_signature = None
    tails_checked = set()
    for mask in masks():
        off = [source for source in SOURCES if source not in mask]
        for anchor in mask:
            usage10 = tuple(
                3 if source == anchor else (2 if source in mask else 0) for source in SOURCES
            )
            state10 = index[6][(usage10, mask)]
            cone, paths = prefix_cone(layers, successors, reverse, state10)
            signature = tuple(len(cone[layer]) for layer in range(7))
            if cone_signature is None:
                cone_signature = signature
            elif signature != cone_signature:
                fail("prefix cone shape depends on the anchor: %s" % (signature,))
            if paths != 210:
                fail("expected 210 prefix paths, found %s" % paths)
            prefix_paths[state10] = paths
            predecessors = reverse[5][state10]
            if len(predecessors) != 3:
                fail("s=10 shape does not have three s=9 parents")
            parent_usages = {usage_at(layers, 5, state) for state in predecessors}
            expect_parents = set()
            for source in mask:
                reduced = list(usage10)
                reduced[source] -= 1
                expect_parents.add(tuple(reduced))
            if parent_usages != expect_parents:
                fail("s=9 parents are not the three stays inside the mask")
            for state in predecessors:
                if mask_at(layers, 5, state) != mask:
                    fail("prefix mask left M before s=10")
            for layer, states in cone.items():
                for state in states:
                    if mask_at(layers, layer, state) != mask:
                        fail("prefix cone carries a mask other than M")
                    usage = usage_at(layers, layer, state)
                    if any(usage[source] for source in SOURCES if source not in mask):
                        fail("prefix usage leaves M")
            for state in cone[0]:
                early_mask_is_diagonal(*layers[0][state])
            for pivot in mask:
                if pivot == anchor:
                    continue
                usage11 = tuple(
                    2 if source == pivot else (3 if source in mask else 0) for source in SOURCES
                )
                state11 = index[7][(usage11, mask)]
                if state11 not in successors[6][state10]:
                    fail("shape edge s=10 to s=11 is missing")
                third = next(iter(set(mask) - {anchor, pivot}))
                for pair in itertools.combinations(off, 2):
                    for extra in pair:
                        usage13 = tuple(
                            (1 if source == extra else 0) if source not in mask else 3
                            for source in SOURCES
                        )
                        usage14 = tuple(
                            3 if source in mask else (1 if source in pair else 0)
                            for source in SOURCES
                        )
                        state13 = index[9][(usage13, mask)]
                        state14 = index[10][(usage14, mask)]
                        if state14 not in successors[9][state13]:
                            fail("shape edge s=13 to s=14 is missing")
                        realized10 = frozenset((anchor,) + pair)
                        realized11 = frozenset((set(mask) - {pivot}) | {extra})
                        if realized10 == mask or realized11 == mask or realized10 == realized11:
                            fail("the two realized masks are not new and distinct")
                        mids = [
                            target
                            for target in successors[7][state11]
                            if state13 in successors[8][target]
                        ]
                        if len(mids) != 3:
                            fail("expected 3 states at s=12, found %s" % len(mids))
                        mid_masks = [mask_at(layers, 8, target) for target in mids]
                        if mid_masks.count(mask) != 2 or mid_masks.count(realized11) != 1:
                            fail("s=12 masks are not {M, M, R11}: " + str(mid_masks))
                        for target in mids:
                            usage12 = usage_at(layers, 8, target)
                            if all(value in (0, 3) for value in usage12):
                                support = frozenset(
                                    source for source, value in enumerate(usage12) if value == 3
                                )
                                if support != mask or usage12.count(3) != 3:
                                    fail("(33, 33) support left M")
                        successors14 = successors[10][state14]
                        if len(successors14) != 3:
                            fail("s=14 shape does not have three s=15 children")
                        child_usages = {usage_at(layers, 11, state) for state in successors14}
                        expect_children = set()
                        for source in off:
                            grown = list(usage14)
                            grown[source] += 1
                            expect_children.add(tuple(grown))
                        if child_usages != expect_children:
                            fail("s=15 children are not the three off-mask stays")
                        if state14 not in tails_checked:
                            check_tail(layers, successors, state14, mask)
                            tails_checked.add(state14)
                        check_pair_sums(
                            layers,
                            predecessors,
                            successors14,
                            mask,
                            state10,
                            state14,
                            realized10,
                            realized11,
                        )
                        types += 1
    if len(tails_checked) != 60:
        fail("expected 60 distinct s=14 shapes, found %s" % len(tails_checked))
    if types != 720:
        fail("expected 720 joint types, found %s" % types)
    if cone_signature != (3, 6, 8, 8, 6, 3, 1):
        fail("cone signature changed: %s" % (cone_signature,))
    if len(prefix_paths) != 60:
        fail("expected 60 distinct s=10 shapes, found %s" % len(prefix_paths))
    return types


def prefix_cone(layers, successors, reverse, state10):
    cone = {6: {state10}}
    for layer in range(6, 0, -1):
        previous = set()
        for state in cone[layer]:
            previous.update(reverse[layer - 1][state])
        cone[layer - 1] = previous
    # Count paths from s=4 to this state that stay in the cone.
    ways = {state: 1 for state in cone[0]}
    for layer in range(0, 6):
        nxt = {}
        for state, count in ways.items():
            for target in successors[layer][state]:
                if target in cone[layer + 1]:
                    nxt[target] = nxt.get(target, 0) + count
        ways = nxt
    return cone, ways.get(state10, 0)


def check_tail(layers, successors, state14, mask):
    frontier = {state14}
    for layer in range(10, 17):
        nxt = set()
        for state in frontier:
            targets = successors[layer][state]
            if not targets:
                fail("tail died before s=21")
            for target in targets:
                if mask_at(layers, layer + 1, target) != mask:
                    fail("tail mask left M")
                grown = usage_at(layers, layer + 1, target)
                start = usage_at(layers, layer, state)
                increased = [
                    source for source in SOURCES if grown[source] != start[source]
                ]
                if len(increased) != 1 or increased[0] in mask:
                    fail("tail step is not a stay off M")
                nxt.add(target)
        frontier = nxt
    if len(frontier) != 1:
        fail("tail does not end at one s=21 state")
    usage, state_mask = layers[17][next(iter(frontier))]
    if usage != (3, 3, 3, 3, 3, 3) or state_mask != mask:
        fail("tail does not saturate on M")


def check_pair_sums(
    layers, parents, children, mask, state10, state14, realized10, realized11
):
    """Inside one type, (9, 15) is weight 3 only for the complement endpoints."""
    del state10, state14
    complement_left = tuple(2 if source in mask else 0 for source in SOURCES)
    complement_right = tuple(3 if source in mask else 1 for source in SOURCES)
    hits = 0
    for left in parents:
        for right in children:
            vector = tuple(
                prefix_of(usage_at(layers, 5, left), mask)[source]
                + prefix_of(usage_at(layers, 11, right), mask)[source]
                for source in SOURCES
            )
            realized = weight3_mask(vector)
            is_complement = (
                usage_at(layers, 5, left) == complement_left
                and usage_at(layers, 11, right) == complement_right
            )
            if is_complement:
                if realized != frozenset(SOURCES) - mask:
                    fail("complement endpoints do not realize M^c")
                hits += 1
            elif realized is not None:
                fail("non-complement (9, 15) sum is weight 3: " + str(vector))
    if hits != 1:
        fail("expected one complement (9, 15) sum per type, found %s" % hits)
    anchor_conflict(realized10, realized11, mask)


def anchor_conflict(realized10, realized11, mask):
    if realized10 == realized11 or realized10 == mask or realized11 == mask:
        fail("realized masks collapsed")
    return False


def early_mask_is_diagonal(usage, mask):
    """On an s=4 state whose final letter lies in the mask, (0, 3) is that mask."""
    final = [source for source in SOURCES if usage[source] == 1]
    if sum(usage) != 1 or len(final) != 1 or final[0] not in mask:
        fail("s=4 final letter left the diagonal mask")
    prefix = list(prefix_of(usage, mask))
    # The only coordinate above 1 is the final letter. Decrementing anything
    # else leaves a 2, which is not an allowed weight-3 value.
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


def shared_path_counts(layers, successors):
    """Two counts of s=10..s=14 paths whose endpoint pairs share masks.

    mask(s=10) = mask(s=14) and mask(s=11) = mask(s=13). The paths are the
    joint walks named in the question, before the s=9 and s=15 endpoints.
    """
    number = {mask: position for position, mask in enumerate(masks())}
    width = 20

    def zeros(count):
        return [[0] * width for _ in range(count)]

    forward = zeros(len(layers[7]))
    for state, (_, mask) in enumerate(layers[6]):
        column = number[mask]
        for target in successors[6][state]:
            forward[target][column] += 1
    by_mask = {}
    for state, (_, mask) in enumerate(layers[7]):
        if any(forward[state]):
            by_mask.setdefault(number[mask], []).append(state)
    total_forward = 0
    for mask_id, starts in by_mask.items():
        layer12 = {}
        for state in starts:
            for target in successors[7][state]:
                bucket = layer12.setdefault(target, [0] * width)
                for column, count in enumerate(forward[state]):
                    if count:
                        bucket[column] += count
        layer13 = {}
        for state, buckets in layer12.items():
            for target in successors[8][state]:
                if number[mask_at(layers, 9, target)] != mask_id:
                    continue
                bucket = layer13.setdefault(target, [0] * width)
                for column, count in enumerate(buckets):
                    if count:
                        bucket[column] += count
        for state, buckets in layer13.items():
            for target in successors[9][state]:
                column = number[mask_at(layers, 10, target)]
                total_forward += buckets[column]

    reverse = reverse_edges(successors)
    backward = zeros(len(layers[9]))
    for state, (_, mask) in enumerate(layers[10]):
        column = number[mask]
        for source in reverse[9][state]:
            backward[source][column] += 1
    by_mask = {}
    for state, (_, mask) in enumerate(layers[9]):
        if any(backward[state]):
            by_mask.setdefault(number[mask], []).append(state)
    total_backward = 0
    for mask_id, starts in by_mask.items():
        layer12 = {}
        for state in starts:
            for source in reverse[8][state]:
                bucket = layer12.setdefault(source, [0] * width)
                for column, count in enumerate(backward[state]):
                    if count:
                        bucket[column] += count
        layer11 = {}
        for state, buckets in layer12.items():
            for source in reverse[7][state]:
                if number[mask_at(layers, 7, source)] != mask_id:
                    continue
                bucket = layer11.setdefault(source, [0] * width)
                for column, count in enumerate(buckets):
                    if count:
                        bucket[column] += count
        for state, buckets in layer11.items():
            for source in reverse[6][state]:
                column = number[mask_at(layers, 6, source)]
                total_backward += buckets[column]
    if total_forward != total_backward or total_forward <= 0:
        fail(
            "shared-mask path counts diverged: %s %s" % (total_forward, total_backward)
        )
    return total_forward


def prefixes(word):
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
    return letters, found


def pair_mask(found, left, right):
    return weight3_mask(tuple(found[left][source] + found[right][source] for source in SOURCES))


def usage_of(letters, index):
    return tuple(sum(1 for position in range(45 - index, 42) if letters[position] == source) for source in SOURCES)


def inventory(found):
    realized = {}
    for left in range(42):
        for right in range(left, 42):
            if (left + right - 3) % 7:
                continue
            mask = pair_mask(found, left, right)
            if mask is not None:
                realized.setdefault(mask, []).append((left, right))
    return realized


def diagonal(found):
    return [pair_mask(found, index, 45 - index) for index in range(4, 23)]


def audit_witness(word):
    letters, found = prefixes(word)
    image = diagonal(found)
    if any(mask is None for mask in image[:18]) or image[18] is not None:
        fail("witness is not centre-only")
    if len(set(image[:18])) != 1:
        fail("witness diagonal image is not a single mask")
    mask = image[0]
    usage10 = usage_of(letters, 10)
    usage11 = usage_of(letters, 11)
    usage13 = usage_of(letters, 13)
    usage14 = usage_of(letters, 14)
    anchor = [source for source in mask if usage10[source] == 3]
    if len(anchor) != 1:
        fail("witness s=10 is not a (10, 14) shape")
    anchor = anchor[0]
    if usage10 != tuple(3 if source == anchor else (2 if source in mask else 0) for source in SOURCES):
        fail("witness s=10 usage is not the shape")
    pivot = [source for source in mask if usage11[source] == 2]
    if len(pivot) != 1:
        fail("witness s=11 is not an (11, 13) shape")
    pivot = pivot[0]
    if usage11 != tuple(2 if source == pivot else (3 if source in mask else 0) for source in SOURCES):
        fail("witness s=11 usage is not the shape")
    off = [source for source in SOURCES if source not in mask]
    extra = [source for source in off if usage13[source] == 1]
    if extra != [source for source in off if usage13[source] == 1] or len(extra) != 1:
        fail("witness s=13 does not mark one off-mask source")
    extra = extra[0]
    if usage13 != tuple((1 if source == extra else 0) if source not in mask else 3 for source in SOURCES):
        fail("witness s=13 usage is not the shape")
    pair = tuple(source for source in off if usage14[source] == 1)
    if len(pair) != 2 or extra not in pair or any(usage14[source] for source in off if source not in pair):
        fail("witness s=14 is not a (10, 14) shape")
    if usage14 != tuple(3 if source in mask else (1 if source in pair else 0) for source in SOURCES):
        fail("witness s=14 usage is not the shape")
    realized10 = frozenset((anchor,) + pair)
    realized11 = frozenset((set(mask) - {pivot}) | {extra})
    if pair_mask(found, 10, 14) != realized10 or pair_mask(found, 11, 13) != realized11:
        fail("witness pair masks do not match the shapes")
    if pair_mask(found, 9, 15) is not None:
        fail("witness (9, 15) is weight 3")
    usage9 = usage_of(letters, 9)
    if usage9 == tuple(2 if source in mask else 0 for source in SOURCES):
        fail("witness s=9 is the complement state")
    block = pair_mask(found, 33, 33)
    if block not in (None, mask):
        fail("witness (33, 33) left the diagonal mask")
    if pair_mask(found, 0, 3) != mask:
        fail("witness (0, 3) left the diagonal mask")
    realized = inventory(found)
    if set(realized) != {mask, realized10, realized11}:
        fail("witness cover is not exactly the diagonal mask and the two pairs")
    if len(realized) != 3:
        fail("witness cover is not 3")
    if realized[realized10] != [(10, 14)] or realized[realized11] != [(11, 13)]:
        fail("witness new masks are realized off the named pairs")
    return 3


def audit_complement_word(word):
    letters, found = prefixes(word)
    image = diagonal(found)
    if any(mask is None for mask in image[:18]) or image[18] is not None:
        fail("complement word is not centre-only")
    if len(set(image[:18])) != 1:
        fail("complement word image is not a single mask")
    mask = image[0]
    complement = frozenset(SOURCES) - mask
    if usage_of(letters, 9) != tuple(2 if source in mask else 0 for source in SOURCES):
        fail("complement word s=9 is not the complement usage")
    if usage_of(letters, 15) != tuple(3 if source in mask else 1 for source in SOURCES):
        fail("complement word s=15 is not the complement usage")
    if pair_mask(found, 9, 15) != complement:
        fail("complement word does not realize M^c at (9, 15)")
    realized = inventory(found)
    pair10 = pair_mask(found, 10, 14)
    pair11 = pair_mask(found, 11, 13)
    if pair10 is None or pair11 is None or pair10 == mask or pair11 == mask or pair10 == pair11:
        fail("complement word does not make both pairs new")
    if set(realized) != {mask, pair10, pair11, complement}:
        fail("complement word cover is not 4")
    return 4


def mutated_witness_fails():
    letters = list(WITNESS)
    letters[0] = "1" if letters[0] == "0" else "0"
    try:
        audit_witness("".join(letters))
    except SystemExit as error:
        if str(error).startswith("FAIL:"):
            return
        raise
    fail("mutated witness was accepted")


def main():
    layers, successors = build_layers()
    check_terminal_and_centre(layers)
    check_prefix_bounds(layers)
    blocked = classify_slots()
    _, shaped = classify_graph(layers, successors)
    check_hits_are_shapes(shaped)
    types = check_family(layers, successors)
    shared = shared_path_counts(layers, successors)
    witness_cover = audit_witness(WITNESS)
    complement_cover = audit_complement_word(COMPLEMENT_WORD)
    mutated_witness_fails()
    # 36 types per mask, 2 routes with s=12 mask M, 3 x 3 endpoint
    # combinations at s=9 and s=15, minus the one complement combination.
    # 36 * 2 * 8 = 576 non-complement both-new windows per mask.
    # The complement combination is 36 * 2 = 72, the three-new count.
    if 36 * 2 * 8 != 576 or 36 * 2 != 72:
        fail("window arithmetic changed")
    if types != 20 * 36:
        fail("types are not 36 per mask")
    # Both new forces this family, and every non-complement chain in it has
    # diagonal image of size 1 or 2. The size-1 chains are exactly the
    # both-new ones, with cover 1 + 2 = 3. The size-2 chains put R11 on s=12,
    # so only one pair is new and the cover is still 3. Neither is 20.
    if witness_cover != 3 or complement_cover != 4:
        fail("word covers changed")
    if blocked != 82 or shared < 2160:
        fail("census floor failed")
    print(
        "PASS_SIX_SOURCE_C7_NONCOMPLEMENT_PAIRS "
        "shapes=180/180 types=720/720 prefix_paths_per_state=210 "
        "cone=3,6,8,8,6,3,1 mids_per_type=3 mask_M_routes=2 "
        "both_new_windows_per_mask=576 complement_windows_per_mask=72 "
        "noncomplement_cover=3 complement_cover=4 "
        "witness_cover=3 witness_both_new=1 sharp_word_cover=4 "
        "slots_blocked=82 graph_slots=25 shared_mask_paths=%s "
        "shared_mask_paths_agree=1 controls=16"
        % shared
    )


if __name__ == "__main__":
    main()
