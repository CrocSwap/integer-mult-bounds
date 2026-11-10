#!/usr/bin/env python3
"""Joint off-diagonal pairs for the six-source c=7 weight-3 count.

Hypothesis, inherited from the one-index exchange and not re-proved here:
the only failed diagonal index in 4..22 is the centre, so s=4..21 are
free-type weight-3 masks. This program exhausts that finite graph.

It does not decide unrestricted c=7 existence, and it does not inventory
masks of any weight other than 3.
"""

import itertools

K = 6
SOURCES = range(K)
ALLOWED = (0, 1, 7, 8, 14)
MASK_VALUES = (1, 8)
LAYER_SIZES = (
    120, 420, 1120, 2400, 4320, 6720, 9120, 10920, 11600,
    10920, 9120, 6720, 4320, 2400, 1120, 420, 120, 20,
)
# Image of size 1, three masks outside it, and (0, 3) equal to the image.
THREE_WORD = "012001122012345334455345554433543210221100"
# Image of size 6 plus the single complement. Ceiling 7, attained.
SHARP_WORD = "012001122301452554433345334455543210221100"
MASK_M = frozenset((0, 1, 2))
MASK_COMPLEMENT = frozenset((3, 4, 5))
MASK_1014 = frozenset((0, 3, 4))
MASK_1113 = frozenset((0, 1, 3))


def fail(message):
    raise SystemExit("FAIL: " + message)


def weight3_mask(vector):
    """The weight-3 support, or None when the vector is not a realization."""
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
    return tuple(
        7 - 2 * usage[source] - (1 if source in mask else 0) for source in SOURCES
    )


def prefix_of(usage, mask):
    return tuple(usage[source] + (1 if source in mask else 0) for source in SOURCES)


def letter_moves(usage, mask):
    """In-type steps from the letter recurrence.

    A step reads a prefix letter p at position s and a suffix letter x at
    position 44-s. The free-type sum stays a permutation of (8, 8, 8, 7, 7, 7)
    only for a stay p=x, or for a swap that moves the 8 from x onto p.
    Usage records the growing suffix and is already 3 at the terminal layer.
    """
    counts = middle(usage, mask)
    if min(counts) < 0:
        return []
    moves = []
    for source in SOURCES:
        if usage[source] >= 3 or counts[source] < 2:
            continue
        updated = list(usage)
        updated[source] += 1
        moves.append((tuple(updated), mask))
    for removed in mask:
        if usage[removed] >= 3 or counts[removed] < 1:
            continue
        for added in SOURCES:
            if added in mask or counts[added] < 1:
                continue
            updated = list(usage)
            updated[removed] += 1
            moved = frozenset((set(mask) - {removed}) | {added})
            moves.append((tuple(updated), moved))
    return moves


def johnson_moves(usage, mask):
    """The same steps, written as a Johnson swap or a stay on the mask."""
    counts = middle(usage, mask)
    if min(counts) < 0:
        return []
    moves = []
    current = list(usage)
    for removed in mask:
        if usage[removed] >= 3 or counts[removed] < 1:
            continue
        for added in SOURCES:
            if added in mask or counts[added] < 1:
                continue
            current[removed] += 1
            moved = frozenset((set(mask) - {removed}) | {added})
            moves.append((tuple(current), moved))
            current[removed] -= 1
    for source in SOURCES:
        if usage[source] >= 3 or counts[source] < 2:
            continue
        current[source] += 1
        moves.append((tuple(current), mask))
        current[source] -= 1
    return moves


def start_states():
    """Every free-type state at s=4. The partner is one final letter."""
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
                fail("s=4 weight-3 vector is not free type: " + str(summed))
            usage = tuple(1 if source == last else 0 for source in SOURCES)
            if prefix_of(usage, mask) != counts:
                fail("s=4 prefix formula missed " + str(counts))
            state = (usage, mask)
            if state in seen:
                fail("duplicate s=4 state " + str(state))
            seen.add(state)
            found.append(state)
    if len(found) != 120:
        fail("expected 120 states at s=4, found %s" % len(found))
    return found


def build_layers():
    """Forward closure of the free-type steps from s=4 through s=21."""
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
                fail("move generators diverged at usage %s mask %s" % (usage, mask))
            targets = []
            for new_usage, new_mask in letter:
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
    if any(len(targets) != len(set(targets)) for edges in successors for targets in edges):
        fail("a free-type state has a repeated successor")
    return layers, successors


def check_terminal(layers):
    masks = []
    for usage, mask in layers[-1]:
        if usage != (3, 3, 3, 3, 3, 3):
            fail("s=21 usage is not saturated: " + str(usage))
        if letter_moves(usage, mask):
            fail("s=21 still has an in-type step")
        masks.append(mask)
    if len(masks) != 20 or len(set(masks)) != 20:
        fail("s=21 is not one state per mask")


def complement_pairs(layers):
    """Every free-type pair at s=9 and s=15 whose prefixes sum to weight 3.

    Connectivity is not required for this list. A centre-only chain meets
    one of these pairs if its (9, 15) sum is weight 3, because both states
    lie in the forward closure.
    """
    right_by_prefix = {}
    for index, (usage, mask) in enumerate(layers[11]):
        right_by_prefix.setdefault(prefix_of(usage, mask), []).append((index, mask))
    vectors = []
    for mask in itertools.combinations(SOURCES, 3):
        others = [source for source in SOURCES if source not in mask]
        for mask_values in itertools.product(MASK_VALUES, repeat=3):
            for other_values in itertools.product((0, 7, 14), repeat=3):
                vector = [0] * K
                for position, source in enumerate(mask):
                    vector[source] = mask_values[position]
                for position, source in enumerate(others):
                    vector[source] = other_values[position]
                if sum(vector) == 24:
                    vectors.append(tuple(vector))
    if len(vectors) != 700:
        fail("expected 700 sum-24 weight-3 vectors, found %s" % len(vectors))
    found = []
    for left_index, (usage, mask) in enumerate(layers[5]):
        left_prefix = prefix_of(usage, mask)
        for vector in vectors:
            needed = tuple(vector[source] - left_prefix[source] for source in SOURCES)
            if min(needed) < 0 or needed not in right_by_prefix:
                continue
            for right_index, right_mask in right_by_prefix[needed]:
                found.append((left_index, right_index, mask, right_mask, vector))
    if len(found) != 20:
        fail("expected 20 free-type (9, 15) pairs, found %s" % len(found))
    by_mask = {}
    for left_index, right_index, mask, right_mask, vector in found:
        if mask != right_mask:
            fail("(9, 15) endpoints differ: %s %s" % (mask, right_mask))
        realized = weight3_mask(vector)
        complement = frozenset(SOURCES) - mask
        if realized != complement:
            fail("(9, 15) mask is not the complement of " + str(sorted(mask)))
        left_usage = layers[5][left_index][0]
        right_usage = layers[11][right_index][0]
        expect_left = tuple(2 if source in mask else 0 for source in SOURCES)
        expect_right = tuple(3 if source in mask else 1 for source in SOURCES)
        if left_usage != expect_left or right_usage != expect_right:
            fail("complement usage changed for " + str(sorted(mask)))
        if prefix_of(left_usage, mask) != tuple(3 if source in mask else 0 for source in SOURCES):
            fail("q9 is not 3 on the mask and 0 off it")
        by_mask[mask] = (left_index, right_index)
    if len(by_mask) != 20:
        fail("complement pairs are not one per mask")
    return by_mask


def check_forward(layers, successors, pairs):
    """From each complement state at s=15, only stays on the complement remain."""
    for mask, (_, right_index) in pairs.items():
        complement = frozenset(SOURCES) - mask
        seen = {11: {right_index}}
        frontier = [right_index]
        for layer in range(11, 17):
            nxt = []
            for state in frontier:
                usage, state_mask = layers[layer][state]
                if state_mask != mask:
                    fail("forward mask left %s at s=%s" % (sorted(mask), layer + 4))
                for source in mask:
                    if usage[source] != 3:
                        fail("mask source is not saturated on the complement tail")
                moves = letter_moves(usage, state_mask)
                for target in successors[layer][state]:
                    new_usage, new_mask = layers[layer + 1][target]
                    increased = [
                        source for source in SOURCES if new_usage[source] != usage[source]
                    ]
                    if new_mask != mask or len(increased) != 1 or increased[0] not in complement:
                        fail("forward step is not a stay on the complement")
                    nxt.append(target)
                if not moves:
                    fail("complement tail died before s=21")
            frontier = nxt
            seen[layer + 1] = set(frontier)
        if len(seen[17]) != 1:
            fail("complement tail does not end at one s=21 state")
        usage, state_mask = layers[17][next(iter(seen[17]))]
        if usage != (3, 3, 3, 3, 3, 3) or state_mask != mask:
            fail("complement tail does not saturate on the same mask")


def reverse_edges(successors, layer, width):
    reverse = [[] for _ in range(width)]
    for source, targets in enumerate(successors[layer]):
        for target in targets:
            reverse[target].append(source)
    return reverse


def check_ancestors(layers, successors, pairs):
    """Every free-type state from s=4 through s=9 on a complement chain carries M."""
    for mask, (left_index, _) in pairs.items():
        frontier = {left_index}
        for layer in range(5, 0, -1):
            reverse = reverse_edges(successors, layer - 1, len(layers[layer]))
            previous = set()
            for state in frontier:
                previous.update(reverse[state])
            if not previous:
                fail("complement state at s=9 has no ancestor at s=%s" % (layer + 3))
            for state in previous:
                usage, state_mask = layers[layer - 1][state]
                if state_mask != mask:
                    fail("ancestor mask left %s" % sorted(mask))
                prefix = prefix_of(usage, state_mask)
                if any(prefix[source] for source in SOURCES if source not in mask):
                    fail("ancestor prefix uses the complement of %s" % sorted(mask))
            frontier = previous
        if not frontier:
            fail("no s=4 ancestor")


def walk_census(layers, successors, pairs):
    """Every in-type walk from the s=9 complement state to s=15.

    The diagonal image outside s=10..14 is exactly {M}, by the ancestor and
    forward checks. A walk therefore determines the image and the three
    off-diagonal masks.
    """
    mask_bit = {
        frozenset(choice): 1 << position
        for position, choice in enumerate(itertools.combinations(SOURCES, 3))
    }
    summary = []
    for mask, (left_index, right_index) in sorted(pairs.items(), key=lambda item: sorted(item[0])):
        complement = frozenset(SOURCES) - mask
        allowed = [None] * 7
        allowed[6] = {right_index}
        for depth in range(6):
            reverse = reverse_edges(successors, 10 - depth, len(layers[11 - depth]))
            previous = set()
            for state in allowed[6 - depth]:
                previous.update(reverse[state])
            allowed[5 - depth] = previous
        if left_index not in allowed[0]:
            fail("complement endpoints are not joined for " + str(sorted(mask)))
        counts = [0] * len(layers[5])
        counts[left_index] = 1
        for step in range(6):
            layer = 5 + step
            nxt = [0] * len(layers[layer + 1])
            for state, count in enumerate(counts):
                if not count:
                    continue
                for target in successors[layer][state]:
                    if target in allowed[step + 1]:
                        nxt[target] += count
            counts = nxt
        dynamic = counts[right_index]
        stats = {
            "walks": 0,
            "outside33": 0,
            "unclassified": 0,
            "max_cover": 0,
            "max_cover_several": 0,
            "several": 0,
            "three": 0,
            "cover7": 0,
        }

        def visit(step, state, path):
            if step == 6:
                stats["walks"] += 1
                image = mask_bit[mask]
                for offset, layer in ((1, 6), (2, 7), (3, 8), (4, 9), (5, 10)):
                    image |= mask_bit[layers[layer][path[offset]][1]]
                outside = []
                if mask_bit[complement] & image == 0:
                    outside.append(complement)
                for left_layer, left_at, right_layer, right_at in (
                    (6, path[1], 10, path[5]),
                    (7, path[2], 9, path[4]),
                ):
                    left_usage, left_mask = layers[left_layer][left_at]
                    right_usage, right_mask = layers[right_layer][right_at]
                    vector = tuple(
                        prefix_of(left_usage, left_mask)[source]
                        + prefix_of(right_usage, right_mask)[source]
                        for source in SOURCES
                    )
                    realized = weight3_mask(vector)
                    if realized is None:
                        continue
                    if realized == left_mask or realized == right_mask:
                        continue
                    if left_mask != right_mask:
                        stats["unclassified"] += 1
                        continue
                    if mask_bit[realized] & image == 0 and realized not in outside:
                        outside.append(realized)
                usage12 = layers[8][path[3]][0]
                if all(value in (0, 3) for value in usage12):
                    support = frozenset(
                        source for source, value in enumerate(usage12) if value == 3
                    )
                    if len(support) == 3 and mask_bit[support] & image == 0:
                        stats["outside33"] += 1
                        if support not in outside:
                            outside.append(support)
                image_size = image.bit_count()
                cover = image_size + len(outside)
                stats["max_cover"] = max(stats["max_cover"], cover)
                if len(outside) >= 2:
                    stats["several"] += 1
                    stats["max_cover_several"] = max(stats["max_cover_several"], cover)
                if len(outside) == 3:
                    stats["three"] += 1
                if cover == 7:
                    stats["cover7"] += 1
                if image_size > 6:
                    fail("image exceeded the five variable indices")
                return
            layer = 5 + step
            for target in successors[layer][state]:
                if target in allowed[step + 1]:
                    path.append(target)
                    visit(step + 1, target, path)
                    path.pop()

        visit(0, left_index, [left_index])
        if stats["walks"] != dynamic:
            fail(
                "walk count diverged for %s: recursion %s dynamic %s"
                % (sorted(mask), stats["walks"], dynamic)
            )
        if stats["unclassified"] or stats["outside33"]:
            fail("unexpected joint hit for %s: %s" % (sorted(mask), stats))
        if stats["max_cover"] != 7 or stats["max_cover_several"] != 6:
            fail("cover bound changed for %s: %s" % (sorted(mask), stats))
        if stats["three"] != 72 or stats["several"] != 1044 or stats["cover7"] != 3276:
            fail("joint histogram changed for %s: %s" % (sorted(mask), stats))
        if stats["walks"] != 31788:
            fail("walk total changed for %s: %s" % (sorted(mask), stats["walks"]))
        summary.append(stats)
    if len(summary) != 20:
        fail("census did not cover every mask")
    return summary[0]


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
    return found


def pair_mask(found, left, right):
    return weight3_mask(
        tuple(found[left][source] + found[right][source] for source in SOURCES)
    )


def weight3_inventory(found):
    """Every pair whose index sum can be a weight-3 coordinate sum."""
    realized = {}
    for left in range(42):
        for right in range(left, 42):
            if (left + right - 3) % 7:
                continue
            mask = pair_mask(found, left, right)
            if mask is not None:
                realized.setdefault(mask, []).append((left, right))
    return realized


def diagonal_image(found):
    masks = []
    for index in range(4, 23):
        masks.append(pair_mask(found, index, 45 - index))
    return masks


def audit_three(word):
    found = prefixes(word)
    diagonal = diagonal_image(found)
    if diagonal[:18] != [MASK_M] * 18 or diagonal[18] is not None:
        fail("three-new word does not have image {(0,1,2)} and a failed centre")
    if pair_mask(found, 0, 3) != MASK_M:
        fail("three-new word does not realize (0, 3) as (0, 1, 2)")
    inventory = weight3_inventory(found)
    expected = {
        MASK_M: "diagonal and (0, 3) and (33, 33)",
        MASK_COMPLEMENT: (9, 15),
        MASK_1014: (10, 14),
        MASK_1113: (11, 13),
    }
    if set(inventory) != set(expected):
        fail("three-new inventory changed: " + str(sorted(tuple(sorted(m)) for m in inventory)))
    for mask, slot in (
        (MASK_COMPLEMENT, (9, 15)),
        (MASK_1014, (10, 14)),
        (MASK_1113, (11, 13)),
    ):
        if inventory[mask] != [slot]:
            fail("three-new mask %s is not only %s" % (sorted(mask), slot))
    if (33, 33) not in inventory[MASK_M] or (0, 3) not in inventory[MASK_M]:
        fail("three-new word lost (0, 3) or (33, 33) inside the image")
    # The three new masks differ from the mask of (0, 3). The complement is
    # also disjoint from that mask as a 3-subset.
    if MASK_M & MASK_COMPLEMENT:
        fail("complement meets (0, 1, 2)")
    for mask in (MASK_1014, MASK_1113, MASK_COMPLEMENT):
        if mask == MASK_M:
            fail("a new mask equals (0, 3)")


def audit_sharp(word):
    found = prefixes(word)
    diagonal = diagonal_image(found)
    if any(mask is None for mask in diagonal[:18]) or diagonal[18] is not None:
        fail("sharp word is not centre-only")
    image = set(diagonal[:18])
    if len(image) != 6 or MASK_M not in image or MASK_COMPLEMENT in image:
        fail("sharp diagonal image is not six masks excluding the complement")
    if pair_mask(found, 0, 3) != MASK_M:
        fail("sharp word does not realize (0, 3) as (0, 1, 2)")
    if pair_mask(found, 9, 15) != MASK_COMPLEMENT:
        fail("sharp word lost the complement")
    if pair_mask(found, 10, 14) is not None or pair_mask(found, 11, 13) is not None:
        fail("sharp word realized a second named pair")
    if pair_mask(found, 33, 33) != MASK_M:
        fail("sharp (33, 33) is not the diagonal mask")
    inventory = weight3_inventory(found)
    if set(inventory) != image | {MASK_COMPLEMENT}:
        fail("sharp inventory is not the image plus the complement")
    if len(inventory) != 7:
        fail("sharp cover is not 7")


def mutated_three_fails():
    letters = list(THREE_WORD)
    letters[0] = "1" if letters[0] == "0" else "0"
    try:
        audit_three("".join(letters))
    except SystemExit as error:
        if str(error).startswith("FAIL:"):
            return
        raise
    fail("mutated three-new word was accepted")


def main():
    layers, successors = build_layers()
    check_terminal(layers)
    pairs = complement_pairs(layers)
    check_forward(layers, successors, pairs)
    check_ancestors(layers, successors, pairs)
    census = walk_census(layers, successors, pairs)
    audit_three(THREE_WORD)
    audit_sharp(SHARP_WORD)
    mutated_three_fails()
    # Short proof, before the sharp census: image size <= 6, (0, 3) and
    # (33, 33) add nothing, and the three named pairs add at most one mask
    # each. 6 + 3 = 9 < 20. The walk census tightens 9 to 7.
    if 6 + 3 >= 20 or census["max_cover"] >= 20 or census["max_cover_several"] >= 20:
        fail("cover reached 20")
    print(
        "PASS_SIX_SOURCE_C7_TWO_PAIR_COUNT "
        "endpoint_pairs=20/20 walks_per_mask=%s "
        "image_at_most=6 structural_cover_at_most=9 "
        "census_cover_at_most=%s several_walks=%s several_cover_at_most=%s "
        "three_new_walks=%s cover7_walks=%s "
        "three_word_cover=4 sharp_word_cover=7 "
        "block33_outside=0 unclassified=0 controls=12"
        % (
            census["walks"],
            census["max_cover"],
            census["several"],
            census["max_cover_several"],
            census["three"],
            census["cover7"],
        )
    )


if __name__ == "__main__":
    main()
