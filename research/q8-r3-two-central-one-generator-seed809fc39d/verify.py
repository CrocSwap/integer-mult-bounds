#!/usr/bin/env python3
"""Exact depth-four word search for a mixed Q8 three-register target."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
CERTIFICATE = PACKAGE / "CERTIFICATE.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def q8_tables():
    # Hamilton basis order 1, i, j, k; signs occupy the high bit of each index.
    basis = [
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (0, 0, 1, 0),
        (0, 0, 0, 1),
    ]
    elements = basis + [tuple(-x for x in q) for q in basis]
    to_index = {q: i for i, q in enumerate(elements)}

    def hamilton(a, b):
        a0, a1, a2, a3 = a
        b0, b1, b2, b3 = b
        return (
            a0*b0 - a1*b1 - a2*b2 - a3*b3,
            a0*b1 + a1*b0 + a2*b3 - a3*b2,
            a0*b2 - a1*b3 + a2*b0 + a3*b1,
            a0*b3 + a1*b2 - a2*b1 + a3*b0,
        )

    table = [[to_index[hamilton(a, b)] for b in elements] for a in elements]
    require(table[1][1] == 4 and table[2][2] == 4, "i^2 and j^2 must be -1")
    require(table[1][2] == 3 and table[2][1] == 7, "ij=k and ji=-k")
    require(all(table[4][g] == (g ^ 4) and table[g][4] == (g ^ 4) for g in range(8)), "-1 must be central")
    for a, b, c in itertools.product(range(8), repeat=3):
        require(table[table[a][b]][c] == table[a][table[b][c]], "Q8 associativity")
    return elements, table


def mul_mask(left: int, right: int, table) -> int:
    out = 0
    for a in range(8):
        if (left >> a) & 1:
            for b in range(8):
                if (right >> b) & 1:
                    out ^= 1 << table[a][b]
    return out


def right_times_generator_plus_one(mask: int, generator: int, table) -> int:
    out = mask
    for a in range(8):
        if (mask >> a) & 1:
            out ^= 1 << table[a][generator]
    return out


def rankone_idempotents():
    result = []
    for u in range(1, 8):
        for v in range(1, 8):
            if ((u & v).bit_count() & 1) == 1:
                result.append((u, v))
    require(len(result) == 28, "M3(F2) must have 28 rank-one idempotents")
    return result


def mat_mul2(left, right):
    out = []
    for row in left:
        acc = 0
        for k in range(3):
            if (row >> k) & 1:
                acc ^= right[k]
        out.append(acc)
    return tuple(out)


def rank2(rows):
    rows = list(rows)
    r = 0
    for c in range(3):
        pivot = next((i for i in range(r, 3) if (rows[i] >> c) & 1), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        for i in range(3):
            if i != r and ((rows[i] >> c) & 1):
                rows[i] ^= rows[r]
        r += 1
    return r


def inverse2(rows):
    aug = [rows[i] | (1 << (3+i)) for i in range(3)]
    r = 0
    for c in range(3):
        pivot = next((i for i in range(r, 3) if (aug[i] >> c) & 1), None)
        if pivot is None:
            return None
        aug[r], aug[pivot] = aug[pivot], aug[r]
        for i in range(3):
            if i != r and ((aug[i] >> c) & 1):
                aug[i] ^= aug[r]
        r += 1
    return tuple((row >> 3) & 7 for row in aug)


def check_gl3_closure(idempotents):
    ns = {tuple(v if ((u >> i) & 1) else 0 for i in range(3))
          for u, v in idempotents}
    gl = []
    for rows in itertools.product(range(8), repeat=3):
        if rank2(rows) == 3:
            inv = inverse2(rows)
            require(inv is not None, "invertible matrix lacked inverse")
            gl.append((rows, inv))
    require(len(gl) == 168, "GL3(F2) order mismatch")
    for s, sinv in gl:
        for n in ns:
            require(mat_mul2(mat_mul2(s, n), sinv) in ns,
                    "rank-one idempotent alphabet not closed under GL3 conjugation")
    return len(gl)


def pack_matrix(matrix):
    out = 0
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            out |= value << (8 * (3*i+j))
    return out


def unpack_matrix(state):
    return [[(state >> (8*(3*i+j))) & 255 for j in range(3)] for i in range(3)]


def identity_matrix():
    return [[1 if i == j else 0 for j in range(3)] for i in range(3)]


def target_matrix(diagonal):
    out = [[0, 0, 0] for _ in range(3)]
    for i, group_element in enumerate(diagonal):
        out[i][i] = 1 << group_element
    return out


def generic_matrix_product(left, right, table):
    out = [[0, 0, 0] for _ in range(3)]
    for i in range(3):
        for j in range(3):
            for k in range(3):
                out[i][j] ^= mul_mask(left[i][k], right[k][j], table)
    return out


def gate_matrix(descriptor):
    generator, u, v = descriptor
    a = 1 ^ (1 << generator)
    out = identity_matrix()
    for i in range(3):
        if (u >> i) & 1:
            for j in range(3):
                if (v >> j) & 1:
                    out[i][j] ^= a
    return out


def generic_word(word, table):
    result = identity_matrix()
    for descriptor in word:
        result = generic_matrix_product(result, gate_matrix(descriptor), table)
    return result


def fast_step(state, descriptor, shifts):
    generator, u, v = descriptor
    out = state
    rows_u = [k for k in range(3) if (u >> k) & 1]
    cols_v = [j for j in range(3) if (v >> j) & 1]
    for i in range(3):
        coefficient = 0
        for k in rows_u:
            coefficient ^= (state >> (8 * (3*i+k))) & 255
        delta = shifts[generator][coefficient]
        if delta:
            for j in cols_v:
                out ^= delta << (8 * (3*i+j))
    return out


def digest_states(states):
    h = hashlib.sha256()
    for state in sorted(states):
        h.update(state.to_bytes(9, "little"))
    return h.hexdigest()


def path_to(state, depth, parents):
    path = []
    for d in range(depth, 0, -1):
        previous, generator_index = parents[d][state]
        path.append(generator_index)
        state = previous
    return list(reversed(path))


def direct_word(diagonal):
    # Coordinate projectors: two x calls make z=x^2; one produces x or y.
    x = 1
    word = []
    for i, g in enumerate(diagonal):
        if g == 4:
            u = v = 1 << i
            word.extend([(x, u, v), (x, u, v)])
        elif g in (1, 2):
            u = v = 1 << i
            word.append((g, u, v))
        else:
            raise ValueError("direct witness covers only z,z and x/y targets")
    return word


def run_search():
    _elements, table = q8_tables()
    x, y, z = 1, 2, 4
    ns = rankone_idempotents()
    gl3_order = check_gl3_closure(ns)
    abelianization = [(0, 0), (1, 0), (0, 1), (1, 1),
                      (0, 0), (1, 0), (0, 1), (1, 1)]
    require(all(abelianization[table[a][b]] ==
                (abelianization[a][0] ^ abelianization[b][0],
                 abelianization[a][1] ^ abelianization[b][1])
                for a in range(8) for b in range(8)),
            "Q8 abelianization map to C2 x C2 is not a homomorphism")
    generators = [(g, u, v) for g in (x, y) for u, v in ns]
    require(len(generators) == 56, "paid alphabet size mismatch")
    shifts = [[0] * 256 for _ in range(8)]
    for g in range(8):
        for mask in range(256):
            shifts[g][mask] = right_times_generator_plus_one(mask, g, table)

    target_specs = []
    for g in (x, y):
        for diagonal in sorted(set(itertools.permutations((z, z, g)))):
            target_specs.append((g, diagonal, pack_matrix(target_matrix(diagonal))))
    target_specs.append((None, (z, z, z), pack_matrix(target_matrix((z, z, z)))))
    require(len(target_specs) == 7, "expected six mixed maps plus the triple-central pivot")
    target_by_state = {state: (g, diagonal) for g, diagonal, state in target_specs}
    targets = set(target_by_state)

    identity = pack_matrix(identity_matrix())
    known_control = pack_matrix(target_matrix((z, z, 0)))
    seen = {identity}
    frontier = {identity}
    parents = {}
    layer_counts = [1]
    layer_digests = [digest_states(frontier)]
    raw_extensions = [0]
    witnesses = {}
    target_depths = {}
    control_depth = 0 if identity == known_control else None

    for depth in range(1, 5):
        next_layer = set()
        parent_layer = {}
        extensions = len(frontier) * len(generators)
        for state in sorted(frontier):
            for gen_index, descriptor in enumerate(generators):
                candidate = fast_step(state, descriptor, shifts)
                if candidate not in seen:
                    seen.add(candidate)
                    next_layer.add(candidate)
                    if depth < 4:
                        parent_layer[candidate] = (state, gen_index)
                if candidate in targets and candidate not in witnesses:
                    witness_indices = path_to(state, depth-1, parents)
                    witness_indices.append(gen_index)
                    witnesses[candidate] = witness_indices
                    target_depths[candidate] = depth
                if candidate == known_control and control_depth is None:
                    control_depth = depth
        parents[depth] = parent_layer
        frontier = next_layer
        layer_counts.append(len(frontier))
        layer_digests.append(digest_states(frontier))
        raw_extensions.append(extensions)
        print(f"depth={depth} new_states={len(frontier)} raw_extensions={extensions}", file=sys.stderr, flush=True)

    require(layer_counts[:4] == [1, 56, 2324, 89574],
            f"Q8 predecessor layer control mismatch: {layer_counts[:4]}")
    require(control_depth == 4, "known Q8 diag(z,z,e) depth-four control failed")

    # Check fast transitions against generic noncommutative group-algebra matrix products.
    samples = [identity, *sorted(seen)[:8], *sorted(frontier)[:8]]
    transition_checks = 0
    for state in samples:
        matrix = unpack_matrix(state)
        for descriptor in generators:
            expected = pack_matrix(generic_matrix_product(matrix, gate_matrix(descriptor), table))
            require(fast_step(state, descriptor, shifts) == expected,
                    "packed transition differs from generic F2[Q8] multiplication")
            transition_checks += 1

    results = []
    for g, diagonal, target in target_specs:
        word = direct_word(diagonal)
        expected_direct_calls = sum(2 if label == z else 1 for label in diagonal)
        require(len(word) == expected_direct_calls, "coordinate baseline call count mismatch")
        require(pack_matrix(generic_word(word, table)) == target,
                "five-call coordinate positive control failed")
        deletion_controls = 0
        for remove in range(len(word)):
            shortened = word[:remove] + word[remove+1:]
            require(pack_matrix(generic_word(shortened, table)) != target,
                    "a one-call deletion unexpectedly preserved the direct target")
            deletion_controls += 1
        linear_x = sum(abelianization[label][0] for label in diagonal) & 1
        linear_y = sum(abelianization[label][1] for label in diagonal) & 1
        length_parity = linear_x ^ linear_y
        entry = {
            "diagonal": list(diagonal),
            "direct_calls": len(word),
            "direct_word": [list(item) for item in word],
            "minimum_through_four": target not in seen,
            "found_depth": target_depths.get(target),
            "linear_target_trace_x_mod2": linear_x,
            "linear_target_trace_y_mod2": linear_y,
            "realizing_word_length_mod2": length_parity,
            "exact_minimum": None,
            "candidate_word": None,
            "deletion_controls": deletion_controls,
        }
        if target not in seen:
            exact_minimum = 5 if length_parity else 6
            require(len(word) == exact_minimum,
                    "BFS/parity lower bound does not match the coordinate upper bound")
            entry["exact_minimum"] = exact_minimum
        else:
            entry["exact_minimum"] = target_depths[target]
        if target in witnesses:
            ids = witnesses[target]
            candidate_word = [generators[i] for i in ids]
            require(len(candidate_word) == target_depths[target], "witness length mismatch")
            require(pack_matrix(generic_word(candidate_word, table)) == target,
                    "candidate witness fails independent generic product")
            entry["candidate_word"] = [list(item) for item in candidate_word]
        results.append(entry)

    result = {
        "schema_version": 1,
        "status": "PASS_Q8_EXACT_MIXED_TARGET_FLOORS",
        "model": {
            "group": "Q8={+/-1,+/-i,+/-j,+/-k}",
            "x": x,
            "y": y,
            "z": z,
            "registers": 3,
            "dirty_roles": 3,
            "rank_one_idempotents": len(ns),
            "paid_generators": len(generators),
            "paid_labels": [x, y],
            "equality": "coefficientwise in full F2[Q8]",
            "free_scalar_mixing": "normalized; all 168 GL3 conjugations preserve the 28 idempotents",
        },
        "search": {
            "max_depth": 4,
            "raw_words_lengths_0_to_4": sum(56**i for i in range(5)),
            "raw_extensions_by_depth": raw_extensions,
            "new_states_by_depth": layer_counts,
            "layer_sha256_sorted_9_byte_states": layer_digests,
            "known_diag_z_z_e_depth": control_depth,
            "transition_crosschecks": transition_checks,
        },
        "targets": results,
        "parity_obstructions": {
            "diag_z_z_x_or_y": "The x and y coefficient matrices in J/J^2 are E_kk for the one noncentral role and zero for the other label; trace forces odd count of that label and even count of the other, so every realizing word has odd length.",
            "diag_z_z_z": "Both first-order coefficient matrices vanish; trace forces even counts of x and y calls, so every realizing word has even length.",
        },
        "scope": "Six coordinate permutations of diag([z],[z],[x]) or diag([z],[z],[y]), plus diag([z],[z],[z]), in the stated three-register alphabet; no statement for other labels, groups, roles, or longer words.",
        "cost": {
            "direct_calls_mixed": 5,
            "direct_calls_triple_central": 6,
            "candidate_gate_mixed": "at most 4 paid calls, saving at least 1/5 of this local word",
            "candidate_gate_triple_central": "at most 5 paid calls, saving at least 1/6 of this local word; parity makes an odd saving length impossible, so a saving requires at most 4",
            "setup_copy_hosting_precision_restoration_supplier_mapping": "zero in this optimistic formal-model screen; must be separately charged for physical adoption",
            "selected_kappa_change": False,
        },
    }
    return result


def main():
    write = len(sys.argv) == 2 and sys.argv[1] == "--write"
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and not write):
        raise SystemExit("usage: verify.py [--write]")
    result = run_search()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if write:
        CERTIFICATE.write_text(encoded)
    else:
        require(CERTIFICATE.is_file(), "CERTIFICATE.json missing; generate with --write")
        expected = CERTIFICATE.read_text()
        require(expected == encoded, "recomputed result differs from CERTIFICATE.json")
    print(result["status"])
    print("targets=" + ",".join(str(x["diagonal"]) + ":min=" + str(x["exact_minimum"]) for x in result["targets"]))
    print("layers=" + str(result["search"]["new_states_by_depth"]))


if __name__ == "__main__":
    main()
