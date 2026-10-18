#!/usr/bin/env python3
"""Exact two-role word search in F2[GL_3(F2)] for a fixed CNOT target."""

from collections import deque
import hashlib


DIM = 3
ROLES = 2
ID3 = (1, 2, 4)  # rows of the identity, with column j in bit j
ID2 = (1, 2)
TARGET_WORD = ("T12", "T13", "T21")
PREFIX_RADIUS = 2
SUFFIX_RADIUS = 3
SEARCH_LIMIT = PREFIX_RADIUS + SUFFIX_RADIUS


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def matmul(a, b):
    """Multiply binary matrices stored as row bitmasks."""
    out = []
    for row in a:
        value = 0
        for j in range(DIM):
            if (row >> j) & 1:
                value ^= b[j]
        out.append(value)
    return tuple(out)


def rank_binary(rows, columns):
    rows = list(rows)
    rank = 0
    for col in range(columns):
        pivot = next((i for i in range(rank, len(rows))
                      if (rows[i] >> col) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and ((rows[i] >> col) & 1):
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def address_generators():
    names = []
    matrices = []
    for i in range(DIM):
        for j in range(DIM):
            if i == j:
                continue
            rows = list(ID3)
            rows[i] ^= rows[j]  # Tij = I + Eij: row i <- row i + row j
            names.append(f"T{i + 1}{j + 1}")
            matrices.append(tuple(rows))
    return tuple(names), tuple(matrices)


def enumerate_gl3(names, generators):
    distance = {ID3: 0}
    words = {ID3: ()}
    queue = deque([ID3])
    layers = [1]
    while queue:
        current = queue.popleft()
        for name, generator in zip(names, generators):
            nxt = matmul(current, generator)
            if nxt not in distance:
                distance[nxt] = distance[current] + 1
                words[nxt] = words[current] + (name,)
                queue.append(nxt)
                while len(layers) <= distance[nxt]:
                    layers.append(0)
                layers[distance[nxt]] += 1
    return distance, words, tuple(layers)


def scalar_projectors():
    result = []
    for x in range(1, 1 << ROLES):
        for y in range(1, 1 << ROLES):
            if (x & y).bit_count() % 2 != 1:
                continue
            rows = tuple(y if (x >> i) & 1 else 0 for i in range(ROLES))
            result.append((x, y, rows))
    return tuple(result)


def build_group_table(group, group_index):
    table = []
    for a in group:
        row = []
        for b in group:
            row.append(group_index[matmul(a, b)])
        table.append(tuple(row))
    return tuple(table)


def make_engine():
    names, generators = address_generators()
    distances, words, layers = enumerate_gl3(names, generators)
    require(len(distances) == 168, "coordinate CNOTs did not generate GL_3(F2)")
    require(all(rank_binary(g, DIM) == DIM for g in distances),
            "enumerated address group contains a singular matrix")
    group = tuple(sorted(distances))
    index = {g: i for i, g in enumerate(group)}
    table = build_group_table(group, index)
    labels = tuple(index[g] for g in generators)
    return names, generators, distances, words, layers, group, index, table, labels


def right_translate(mask, label, table):
    """Right-translate a formal group-algebra coefficient vector by label."""
    out = 0
    while mask:
        bit = mask & -mask
        old = bit.bit_length() - 1
        out |= 1 << table[old][label]
        mask ^= bit
    return out


def apply_factor(state, factor, projectors, table, labels):
    """Right-multiply a 2x2 formal matrix by I+([g]+1)xy^T."""
    label, projector_index = factor
    group_label = labels[label]
    x, y, _ = projectors[projector_index]
    out = list(state)
    for i in range(ROLES):
        if (x >> i) & 1:
            v = 0
            for k in range(ROLES):
                v ^= state[i * ROLES + k]
            delta = right_translate(v, group_label, table) ^ v
            for j in range(ROLES):
                if (y >> j) & 1:
                    out[i * ROLES + j] ^= delta
    return tuple(out)


def as_sets(state):
    return tuple(frozenset(i for i in range(state_entry.bit_length())
                           if (state_entry >> i) & 1)
                 for state_entry in state)


def from_sets(state, group_size):
    result = []
    for entry in state:
        mask = 0
        for i in entry:
            mask |= 1 << i
        result.append(mask)
    return tuple(result)


def apply_factor_sparse(state, factor, projectors, table, labels):
    """Reference replay by generic 2x2 matrix multiplication over F2[G]."""
    label, projector_index = factor
    group_label = labels[label]
    _x, _y, nrows = projectors[projector_index]
    entries = as_sets(state)
    output = []
    for i in range(ROLES):
        for j in range(ROLES):
            coefficient = set()
            for k in range(ROLES):
                value = entries[i * ROLES + k]
                if k == j:
                    coefficient.symmetric_difference_update(value)
                if (nrows[k] >> j) & 1:
                    shifted = {table[h][group_label] for h in value}
                    coefficient.symmetric_difference_update(shifted)
                    coefficient.symmetric_difference_update(value)
            output.append(frozenset(coefficient))
    return from_sets(tuple(output), len(table))


def identity_state(group_size, identity_index):
    one = 1 << identity_index
    return (one, 0, 0, one)


def target_state(group_size, target_index):
    target = 1 << target_index
    return (target, 0, 0, target)


def enumerate_ball(radius, factors, projectors, table, labels, initial):
    """Exact BFS ball in the Cayley graph of formal 2x2 group-algebra matrices."""
    states = {initial: ()}
    frontier = [(initial, ())]
    layer_sizes = [1]
    for _depth in range(radius):
        following = []
        for state, word in frontier:
            for factor_index, factor in enumerate(factors):
                nxt = apply_factor(state, factor, projectors, table, labels)
                if nxt not in states:
                    next_word = word + (factor_index,)
                    states[nxt] = next_word
                    following.append((nxt, next_word))
        frontier = following
        layer_sizes.append(len(frontier))
    return states, tuple(layer_sizes)


def replay(word, initial, factors, projectors, table, labels):
    state = initial
    for factor_index in word:
        state = apply_factor(state, factors[factor_index], projectors, table, labels)
    return state


def state_digest(states, group_size):
    width = (group_size + 7) // 8
    digest = hashlib.sha256()
    for state in sorted(states):
        for entry in state:
            digest.update(entry.to_bytes(width, "little"))
    return digest.hexdigest()


def factor_description(factor, names, projectors):
    label, pidx = factor
    x, y, _ = projectors[pidx]
    return {"address": names[label], "x": x, "y": y}


def main():
    (names, generators, address_distance, address_words, address_layers,
     group, group_index, table, labels) = make_engine()
    target = ID3
    for name in TARGET_WORD:
        target = matmul(target, generators[names.index(name)])
    target_index = group_index[target]
    rho = rank_binary(tuple(target[i] ^ ID3[i] for i in range(DIM)), DIM)
    require(rho == 2, "target displacement rank is not two")
    require(address_distance[target] == len(TARGET_WORD) == 3,
            "target coordinate-CNOT length is not exactly three")
    require(address_words[target] == TARGET_WORD,
            "Cayley BFS recovered an unexpected target word")

    projectors = scalar_projectors()
    require(len(projectors) == 6, "wrong number of rank-one idempotents on two roles")
    for x, y, _rows in projectors:
        require((x & y).bit_count() % 2 == 1, "projector is not idempotent")
    factors = tuple((label, pidx)
                    for label in range(len(names))
                    for pidx in range(len(projectors)))
    require(len(factors) == 36, "wrong paid factor alphabet size")
    for factor in factors:
        once = apply_factor(identity_state(len(group), group_index[ID3]),
                            factor, projectors, table, labels)
        twice = apply_factor(once, factor, projectors, table, labels)
        require(twice == identity_state(len(group), group_index[ID3]),
                "coordinate-CNOT rank-one factor is not involutive")

    initial = identity_state(len(group), group_index[ID3])
    target_matrix = target_state(len(group), target_index)
    p_by_xy = {(x, y): i for i, (x, y, _rows) in enumerate(projectors)}
    p_e00 = p_by_xy[(1, 1)]
    p_e11 = p_by_xy[(2, 2)]
    label_by_name = {name: i for i, name in enumerate(names)}
    direct_word = tuple(
        next(i for i, f in enumerate(factors) if f == (label_by_name[name], pidx))
        for pidx in (p_e00, p_e11)
        for name in TARGET_WORD
    )
    require(replay(direct_word, initial, factors, projectors, table, labels)
            == target_matrix, "direct six-call word misses the formal endpoint")
    require(len(direct_word) == 2 * address_distance[target],
            "direct call price does not equal twice the target CNOT length")

    one_copy = tuple(next(i for i, f in enumerate(factors)
                          if f == (label_by_name[name], p_e00))
                     for name in TARGET_WORD)
    one_copy_endpoint = replay(one_copy, initial, factors, projectors, table, labels)
    one = 1 << group_index[ID3]
    require(one_copy_endpoint == (1 << target_index, 0, 0, one),
            "single-role positive control failed")

    # Compare the rank-one optimized transition to a separate generic matrix
    # product over sparse formal coefficient sets on every generator and a
    # fixed family of nontrivial prefix states.
    samples = [initial]
    state = initial
    for factor_index in direct_word:
        state = apply_factor(state, factors[factor_index], projectors, table, labels)
        samples.append(state)
    for state in samples:
        for factor in factors:
            fast = apply_factor(state, factor, projectors, table, labels)
            slow = apply_factor_sparse(state, factor, projectors, table, labels)
            require(fast == slow, "bitset transition disagrees with sparse matrix product")

    prefix, prefix_layers = enumerate_ball(
        PREFIX_RADIUS, factors, projectors, table, labels, initial)
    suffix, suffix_layers = enumerate_ball(
        SUFFIX_RADIUS, factors, projectors, table, labels, initial)
    hits = []
    for prefix_state, prefix_word in prefix.items():
        inverse_prefix = replay(tuple(reversed(prefix_word)), initial,
                                factors, projectors, table, labels)
        residual = tuple(right_translate(entry, target_index, table)
                         for entry in inverse_prefix)
        suffix_word = suffix.get(residual)
        if suffix_word is not None:
            candidate = prefix_word + suffix_word
            require(len(candidate) <= SEARCH_LIMIT,
                    "meet-in-the-middle candidate exceeds the declared bound")
            require(replay(candidate, initial, factors, projectors, table, labels)
                    == target_matrix,
                    "meet-in-the-middle candidate fails exact formal replay")
            hits.append(candidate)
    best = min(hits, key=len) if hits else None

    # Deliberate boundary controls: every omitted direct call fails, and admitting
    # the composite target as a paid address label compresses the endpoint to 2.
    omissions = 0
    for pos in range(len(direct_word)):
        mutated = direct_word[:pos] + direct_word[pos + 1:]
        require(replay(mutated, initial, factors, projectors, table, labels)
                != target_matrix, "a one-call omission was accepted")
        omissions += 1
    wrong_first = next(i for i, factor in enumerate(factors)
                       if factor == (label_by_name["T13"], p_e00))
    mutated = (wrong_first,) + direct_word[1:]
    require(replay(mutated, initial, factors, projectors, table, labels)
            != target_matrix, "wrong CNOT label mutation was accepted")
    expanded_word = []
    for pidx in (p_e00, p_e11):
        expanded_word.append((len(names), pidx))
    expanded_names = names + ("A (forbidden composite label)",)
    expanded_labels = labels + (target_index,)
    expanded_state = initial
    for factor in expanded_word:
        expanded_state = apply_factor(expanded_state, factor, projectors,
                                      table, expanded_labels)
    require(expanded_state == target_matrix,
            "expanded-alphabet boundary control failed")

    prefix_hash = state_digest(prefix, len(group))
    suffix_hash = state_digest(suffix, len(group))
    print("PASS_GL3_COORDINATE_CNOT_TWO_ROLE"
          " gl3=168 address_layers=%s target_rank=%d target_length=%d"
          % (list(address_layers), rho, address_distance[target]))
    print("  labels=6 rank_one_idempotents=6 paid_factor_types=36 direct_two_role_calls=6")
    print("  prefix_radius2_layers=%s states=%d sha256=%s"
          % (list(prefix_layers), len(prefix), prefix_hash))
    print("  suffix_radius3_layers=%s states=%d sha256=%s"
          % (list(suffix_layers), len(suffix), suffix_hash))
    print("  meet_in_middle_candidates=%d omissions_rejected=%d wrong_label_rejected=1"
          " sparse_matrix_transition_checks=%d expanded_label_control=2"
          % (len(hits), omissions, len(samples) * len(factors)))
    if best is None:
        print("  exact_two_register_minimum=6 no_word_through=5 selected_kappa_unchanged")
    else:
        print("  witness_calls=%d witness=%s" % (
            len(best), [factor_description(factors[i], names, projectors)
                        for i in best]))
        print("  selected_kappa_unchanged abstract_model_not_supplier")


if __name__ == "__main__":
    main()
