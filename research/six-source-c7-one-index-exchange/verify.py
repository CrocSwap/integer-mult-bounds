#!/usr/bin/env python3
"""One-index off-diagonal exchange for the six-source c=7 weight-3 block.

The diagonal equality case (every s in 4..22 is a weight-3 mask) is the
inherited empty result. This program does not repeat that induction. It
checks the next question: if exactly one index in 4..22 fails, can one
off-diagonal pair restore a complete set of 20 weight-3 masks?

Answer checked here: no. The cover is at most 19, and a concrete word
attains 19. Unrestricted depth-two existence at c=7 stays open.
"""

import itertools

K = 6
SOURCES = range(K)
ALLOWED = (0, 1, 7, 8, 14)
MASK_VALUES = (1, 8)
NONMASK_VALUES = (0, 7, 14)
OFF_SUMS = (10, 17, 24, 31, 38, 52, 59, 66, 73, 80)
WITNESS = "023514103524310254054123145203452034213150"
# The witness misses exactly this triple after the diagonal image and (0, 3).
WITNESS_MISSING = frozenset((1, 3, 5))


def fail(message):
    raise SystemExit("FAIL: " + message)


def masks():
    return [frozenset(choice) for choice in itertools.combinations(SOURCES, 3)]


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


def centre_lemma():
    """Inherited fact: every weight-3 centre freezes a coordinate at 14.

    This is the centre classification used by the diagonal obstruction. The
    equality-case induction down to q_4 is not repeated.
    """
    found = 0
    frozen = 0
    for counts in itertools.product(range(8), repeat=K):
        if sum(counts) != 22:
            continue
        for centre in SOURCES:
            if counts[centre] >= 7:
                continue
            summed = tuple(
                2 * counts[source] + (1 if source == centre else 0) for source in SOURCES
            )
            if weight3_mask(summed) is None:
                continue
            found += 1
            if 14 not in summed:
                fail("weight-3 centre without a 14: " + str(counts))
            frozen += summed.count(14)
    if found != 300 or frozen != 480:
        fail("centre lemma changed: found %s frozen %s" % (found, frozen))
    return found


def free_type_vectors():
    """Sum-45 weight-3 vectors with no coordinate 14."""
    found = []
    for mask in masks():
        vector = tuple(8 if source in mask else 7 for source in SOURCES)
        if sum(vector) != 45 or weight3_mask(vector) != mask:
            fail("free-type vector is not weight 3: " + str(vector))
        found.append(vector)
    # No other 14-free shape has coordinate sum 45.
    seen = set(found)
    for mask_bits in itertools.product((1, 8), repeat=3):
        for other in itertools.product((0, 7), repeat=3):
            if 14 in other:
                continue
            values = list(mask_bits) + list(other)
            if sum(values) != 45:
                continue
            for order in set(itertools.permutations(values)):
                if 14 in order:
                    continue
                if weight3_mask(order) is not None and order not in seen:
                    fail("unexpected 14-free vector " + str(order))
    if len(found) != 20:
        fail("expected 20 free-type vectors, found %s" % len(found))
    return found


def fourteen_is_fixed():
    """Inside {0, 1, 7, 8, 14}, a step cannot change a coordinate equal to 14."""
    grew = {value for value in ALLOWED if value + 1 in ALLOWED}
    shrank = {value for value in ALLOWED if value - 1 in ALLOWED}
    if grew != {0, 7} or shrank != {1, 8} or 14 in grew or 14 in shrank:
        fail("14 is not fixed: +%s -%s" % (sorted(grew), sorted(shrank)))


def two_step_values():
    """Coordinates reachable from {7, 8} by two steps of size at most 1."""
    values = {7, 8}
    for _ in range(2):
        values = {value + delta for value in values for delta in (-1, 0, 1)}
    if 14 in values or max(values) > 10:
        fail("two steps from {7, 8} can reach 14: " + str(sorted(values)))
    return values


def short_prefix_cannot_meet_14():
    """A coordinate 14 in a weight-3 sum is 7+7. A prefix shorter than 7 has no 7."""
    for length in (4, 5, 6):
        if length + 7 >= 14:
            fail("a length-%s prefix can meet a frozen 14" % length)


def start_states():
    """Count states at s=4. Each is a free-type vector, and there are no others."""
    found = []
    for last in SOURCES:
        for counts in itertools.product(range(5), repeat=K):
            if sum(counts) != 4:
                continue
            suffix = tuple(6 if source == last else 7 for source in SOURCES)
            summed = tuple(counts[source] + suffix[source] for source in SOURCES)
            if weight3_mask(summed) is None:
                continue
            if sorted(summed) != [7, 7, 7, 8, 8, 8]:
                fail("s=4 weight-3 vector is not free type: " + str(summed))
            mask = weight3_mask(summed)
            usage = tuple(1 if source == last else 0 for source in SOURCES)
            found.append((usage, mask))
    if len(found) != 120 or len(set(found)) != 120:
        fail("s=4 state count changed: %s" % len(found))
    return found


def middle(usage, mask):
    return tuple(7 - 2 * usage[source] - (1 if source in mask else 0) for source in SOURCES)


def legal_moves(usage, mask):
    """In-type steps: a Johnson swap of the mask, or a stay on one source."""
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
            new_mask = frozenset((set(mask) - {removed}) | {added})
            moves.append((tuple(current), new_mask))
            current[removed] -= 1
    for source in SOURCES:
        if usage[source] >= 3 or counts[source] < 2:
            continue
        current[source] += 1
        moves.append((tuple(current), mask))
        current[source] -= 1
    return moves


def build_layers():
    """Exact free-type chains from s=4 through s=21, stays included."""
    layers = [start_states()]
    successors = []
    for _ in range(17):
        previous = layers[-1]
        index = {}
        states = []
        edges = []
        for usage, mask in previous:
            targets = []
            for new_usage, new_mask in legal_moves(usage, mask):
                key = (new_usage, new_mask)
                if key not in index:
                    index[key] = len(states)
                    states.append(key)
                targets.append(index[key])
            edges.append(targets)
        layers.append(states)
        successors.append(edges)
    if [len(layer) for layer in layers][-1] != 20:
        fail("s=21 should be one state per mask, found %s" % len(layers[-1]))
    for usage, mask in layers[-1]:
        if usage != (3, 3, 3, 3, 3, 3):
            fail("s=21 usage is not saturated: " + str(usage))
        if legal_moves(usage, mask):
            fail("s=21 still has an in-type successor")
    return layers, successors


def prefix_of(usage, mask):
    return tuple(usage[source] + (1 if source in mask else 0) for source in SOURCES)


def marginal_hit(left, right, sigma):
    """True when some independently reachable prefixes sum to a weight-3 vector."""
    shapes = []
    for mask in masks():
        for mask_values in itertools.product(MASK_VALUES, repeat=3):
            for other_values in itertools.product((0, 7), repeat=3):
                vector = [0] * K
                for position, source in enumerate(sorted(mask)):
                    vector[source] = mask_values[position]
                others = [source for source in SOURCES if source not in mask]
                for position, source in enumerate(others):
                    vector[source] = other_values[position]
                if sum(vector) == sigma and weight3_mask(vector) is not None:
                    shapes.append(tuple(vector))
    right_set = set(right)
    for start in left:
        for vector in shapes:
            needed = tuple(vector[source] - start[source] for source in SOURCES)
            if min(needed) < 0:
                continue
            if needed in right_set:
                return True
    return False


def joint_hits(layers, successors, left_index, right_index):
    """Pairs of states on one chain whose prefixes sum to a weight-3 vector."""
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
            vector = tuple(
                left_prefix[source] + right_prefix[source] for source in SOURCES
            )
            realized = weight3_mask(vector)
            if realized is not None:
                hits.append((left_mask, right_mask, realized))
    return hits


def classify_graph(layers, successors):
    """Every jointly realized off-diagonal pair inside s=4..21.

    A hit is internal when its mask is already the mask of one endpoint, and
    novel when the two endpoints carry the same mask and the sum does not.
    Anything else is unclassified and stops the proof.
    """
    prefixes = []
    for layer in layers:
        prefixes.append({prefix_of(usage, mask) for usage, mask in layer})
    census = {}
    slots = 0
    for sigma in OFF_SUMS:
        for left in range(4, 22):
            right = sigma - left
            if right < left or right > 21:
                continue
            slots += 1
            if not marginal_hit(prefixes[left - 4], prefixes[right - 4], sigma):
                continue
            for left_mask, right_mask, realized in joint_hits(
                layers, successors, left - 4, right - 4
            ):
                if realized == left_mask or realized == right_mask:
                    kind = "internal"
                elif left != right and left_mask == right_mask:
                    kind = "novel"
                else:
                    fail(
                        "unclassified joint pair s=%s t=%s masks %s %s realized %s"
                        % (left, right, left_mask, right_mask, realized)
                    )
                census[(left, right, kind)] = census.get((left, right, kind), 0) + 1
    if slots != 25:
        fail("expected 25 diagonal-index off-diagonal slots, found %s" % slots)
    expected = {
        (12, 12, "internal"): 20,
        (11, 13, "novel"): 180,
        (10, 14, "novel"): 180,
        (9, 15, "novel"): 20,
    }
    if census != expected:
        fail("joint census changed: " + str(sorted(census.items())))
    return 20, 380


def block_max_distinct():
    """A (33, 33) block repeats a mask on s=4..12. Maximum distinct count is 8."""
    all_masks = masks()
    numbered = {mask: position for position, mask in enumerate(all_masks)}
    worst = 0
    reachable = 0
    for block in all_masks:
        for last in block:
            usage = tuple(1 if source == last else 0 for source in SOURCES)
            layer = {}
            for mask in all_masks:
                if min(middle(usage, mask)) < 0:
                    continue
                layer[(usage, mask)] = {1 << numbered[mask]}
            for _ in range(8):
                nxt = {}
                for (state_usage, mask), seen in layer.items():
                    for new_usage, new_mask in legal_moves(state_usage, mask):
                        # The outer nine suffix letters use only the block sources.
                        increased = [
                            source
                            for source in SOURCES
                            if new_usage[source] != state_usage[source]
                        ]
                        if len(increased) != 1 or increased[0] not in block:
                            continue
                        bit = 1 << numbered[new_mask]
                        bucket = nxt.setdefault((new_usage, new_mask), set())
                        for previous in seen:
                            bucket.add(previous | bit)
                layer = nxt
            target = tuple(3 if source in block else 0 for source in SOURCES)
            for (state_usage, mask), seen in layer.items():
                if state_usage != target:
                    continue
                reachable += 1
                for bits in seen:
                    worst = max(worst, bits.bit_count())
    if worst != 8 or reachable == 0:
        fail("block distinct bound changed: max %s reachable %s" % (worst, reachable))
    return worst


def q_bounds(index):
    if index <= 3:
        return 0, 2
    if index <= 21:
        return 0, 4
    if index <= 23:
        return 3, 4
    return 4, 7


def bound_reason(left, right, sigma):
    """A uniform count obstruction, or None when the slot needs the graph or the block."""
    if 4 <= left and right <= 21:
        return None
    if (left, right) == (33, 33):
        return None
    low = q_bounds(left)[0] + q_bounds(right)[0]
    high = q_bounds(left)[1] + q_bounds(right)[1]
    possible = {value for value in ALLOWED if low <= value <= high}
    if not possible:
        return "no allowed coordinate in [%s, %s]" % (low, high)
    if possible <= {0, 1} and sigma != 3:
        return "only {0, 1} coordinates would sum to 3, not %s" % sigma
    if possible <= {7, 8} and sigma != 45:
        return "only {7, 8} coordinates would sum to 45, not %s" % sigma
    if possible <= {8, 14} and sigma != 66:
        return "only {8, 14} coordinates would sum to 66, not %s" % sigma
    if left >= 24 and sigma == 66 and left < right:
        return "every source would have to avoid the nonempty middle [%s, %s)" % (left, right)
    return None


def classify_slots():
    graph = 0
    blocked = 0
    block = 0
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
        fail("slot census changed: blocked %s graph %s block %s" % (blocked, graph, block))
    return blocked, graph, block


def vector_at(prefixes, left, right):
    return tuple(prefixes[left][source] + prefixes[right][source] for source in SOURCES)


def audit_witness(word):
    if len(word) != 42 or any(character not in "012345" for character in word):
        fail("witness is not a length-42 word on six sources")
    letters = [int(character) for character in word]
    if any(letters.count(source) != 7 for source in SOURCES):
        fail("witness does not call every source seven times")
    prefixes = []
    running = [0] * K
    prefixes.append(tuple(running))
    for letter in letters:
        running[letter] += 1
        prefixes.append(tuple(running))
    diagonal = {}
    for index in range(4, 23):
        diagonal[index] = weight3_mask(vector_at(prefixes, index, 45 - index))
    if any(diagonal[index] is None for index in range(4, 22)):
        fail("witness drops a diagonal weight-3 mask before the centre")
    if diagonal[22] is not None:
        fail("witness centre is weight 3")
    image = {diagonal[index] for index in range(4, 22)}
    if len(image) != 18:
        fail("witness diagonal image has %s masks, expected 18" % len(image))
    early = weight3_mask(prefixes[3])
    holes = set(masks()) - image
    if early not in holes or len(holes) != 2:
        fail("witness early pair does not fill exactly one of two holes")
    missing = holes - {early}
    if missing != {WITNESS_MISSING}:
        fail("witness missing mask changed: " + str(missing))
    off_masks = set()
    for sigma in OFF_SUMS:
        for left in range(0, sigma // 2 + 1):
            right = sigma - left
            if right > 41:
                continue
            realized = weight3_mask(vector_at(prefixes, left, right))
            if realized is not None:
                off_masks.add(realized)
    if off_masks & missing:
        fail("witness off-diagonal pair fills the missing mask")
    if off_masks - image:
        fail("witness has an off-diagonal mask outside the diagonal image")
    # The same word must be a chain of in-type moves, so the graph applies to it.
    for index in range(4, 22):
        usage = tuple(
            sum(1 for position in range(45 - index, 42) if letters[position] == source)
            for source in SOURCES
        )
        prefix = prefixes[index]
        mask = diagonal[index]
        for source in SOURCES:
            expected = usage[source] + (1 if source in mask else 0)
            if prefix[source] != expected:
                fail("witness s=%s is not free type at source %s" % (index, source))
        if index < 21:
            next_usage = tuple(
                sum(1 for position in range(45 - (index + 1), 42) if letters[position] == source)
                for source in SOURCES
            )
            if (next_usage, diagonal[index + 1]) not in set(legal_moves(usage, mask)):
                fail("witness step s=%s is not an in-type move" % index)
    return 19


def mutated_witness_fails():
    letters = list(WITNESS)
    letters[0] = "0" if letters[0] != "0" else "1"
    mutated = "".join(letters)
    try:
        audit_witness(mutated)
    except SystemExit as error:
        if str(error).startswith("FAIL:"):
            return
        raise
    fail("mutated witness was accepted")


def main():
    centres = centre_lemma()
    free_type_vectors()
    fourteen_is_fixed()
    two_step_values()
    short_prefix_cannot_meet_14()
    blocked, graph_slots, block_slots = classify_slots()
    layers, successors = build_layers()
    internal, novel = classify_graph(layers, successors)
    distinct = block_max_distinct()
    # A new off-diagonal mask is either a (33, 33) block, whose first nine
    # diagonal masks number at most 8, or a pair of diagonal indices carrying
    # the same mask. Either way the diagonal image has size at most 17.
    # The early pair (0, 3) adds at most one mask. One off-diagonal pair adds
    # at most one mask. 17 + 1 + 1 = 19. An off-diagonal mask that is already
    # on the diagonal adds nothing, and 18 + 1 = 19 as well.
    if distinct > 8:
        fail("block no longer forces a repeat in the first nine masks")
    cover = 19
    witness_cover = audit_witness(WITNESS)
    if witness_cover != cover:
        fail("witness cover %s does not meet the proved ceiling" % witness_cover)
    mutated_witness_fails()
    print(
        "PASS_SIX_SOURCE_C7_ONE_INDEX_EXCHANGE "
        "only_failure=22 centres_with_14=%s/300 free_vectors=20 "
        "slots_blocked=%s graph_slots=%s block_slots=%s "
        "graph_internal=%s graph_novel=%s block33_max_distinct=%s "
        "cover_at_most=%s witness_cover=%s missing=(1,3,5) "
        "census=12/12:20,11/13:180,10/14:180,9/15:20 controls=6"
        % (centres, blocked, graph_slots, block_slots, internal, novel, distinct, cover, witness_cover)
    )


if __name__ == "__main__":
    main()
