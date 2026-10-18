#!/usr/bin/env python3
"""Exact three-register paid-word census for a cyclic GL3(F2) alphabet."""
from collections import deque
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
BASE = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
SELECTED_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
I3 = (1, 0, 0, 0, 1, 0, 0, 0, 1)
RING_BITS = 168
RING_MASK = (1 << RING_BITS) - 1
STATE_BITS = 9 * RING_BITS
STATE_BYTES = (STATE_BITS + 7) // 8


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def mat3_mul(a, b):
    return tuple((a[3 * i] * b[j] + a[3 * i + 1] * b[3 + j]
                  + a[3 * i + 2] * b[6 + j]) & 1
                 for i in range(3) for j in range(3))


def address_generators():
    rows = []
    names = []
    for i, j, name in ((0, 1, "C01"), (1, 2, "C12"), (2, 0, "C20"),
                       (1, 0, "C10"), (2, 1, "C21"), (0, 2, "C02")):
        a = list(I3)
        a[3 * i + j] = 1
        rows.append(tuple(a))
        names.append(name)
    return tuple(rows), tuple(names)


def enumerate_address_group(generators):
    elements = [I3]
    paths = {I3: ()}
    queue = deque([I3])
    while queue:
        x = queue.popleft()
        for j, g in enumerate(generators):
            y = mat3_mul(x, g)
            if y not in paths:
                paths[y] = paths[x] + (j,)
                elements.append(y)
                queue.append(y)
    need(len(elements) == 168, "cyclic CNOT labels must generate GL3(F2)")
    return elements, paths


def rank_one_idempotents():
    rows = []
    for u in range(1, 8):
        for v in range(1, 8):
            if (u & v).bit_count() & 1:
                rows.append((u, v))
    need(len(rows) == 28, "three-register rank-one idempotent inventory")
    return tuple(rows)


def make_right_translation_tables(multiplication, label_indices):
    """Byte LUTs for right multiplication in the formal group basis."""
    tables = []
    byte_count = (RING_BITS + 7) // 8
    for g in label_indices:
        by_position = []
        for pos in range(byte_count):
            by_value = [0] * 256
            for value in range(1, 256):
                bits = value
                output = 0
                while bits:
                    bit = (bits & -bits).bit_length() - 1
                    source = 8 * pos + bit
                    if source < RING_BITS:
                        output |= 1 << multiplication[source][g]
                    bits &= bits - 1
                by_value[value] = output
            by_position.append(by_value)
        tables.append(tuple(by_position))
    return tuple(tables)


def right_translate(value, table):
    encoded = value.to_bytes((RING_BITS + 7) // 8, "little")
    result = 0
    for pos, byte in enumerate(encoded):
        if byte:
            result ^= table[pos][byte]
    return result


def projectors():
    return tuple((u, v) for u, v in rank_one_idempotents())


def pack_identity():
    result = 0
    for i in range(3):
        result |= 1 << (RING_BITS * (3 * i + i))
    return result


def pack_target(c_index):
    result = 1 << (RING_BITS * 0 + c_index)
    result |= 1 << (RING_BITS * 4 + c_index)
    result |= 1 << (RING_BITS * 8)
    return result


def apply_factor(state, factor, translation_tables):
    """Right multiply a formal 3x3 matrix by I+([g]+1)uv^T."""
    g, u, v = factor
    entries = [(state >> (RING_BITS * k)) & RING_MASK for k in range(9)]
    table = translation_tables[g]
    for i in range(3):
        row = 0
        for k in range(3):
            if (u >> k) & 1:
                row ^= entries[3 * i + k]
        delta = row ^ right_translate(row, table)
        for j in range(3):
            if (v >> j) & 1:
                entries[3 * i + j] ^= delta
    return sum(value << (RING_BITS * k) for k, value in enumerate(entries))


def ball(start, depth, factors, translation_tables):
    seen = {start}
    frontier = {start}
    shells = [1]
    for _ in range(depth):
        following = {apply_factor(state, factor, translation_tables)
                     for state in frontier for factor in factors} - seen
        seen.update(following)
        frontier = following
        shells.append(len(frontier))
    return seen, shells


def target_side_search(target, depth, left_ball, factors, translation_tables):
    """Check every raw target-side word; no deduplication can hide a path."""
    word_counts = [1] + [len(factors) ** d for d in range(1, depth + 1)]
    transitions = 0
    hits = 0

    def visit(state, current_depth):
        nonlocal transitions, hits
        if current_depth == depth:
            return
        for factor in factors:
            following = apply_factor(state, factor, translation_tables)
            transitions += 1
            hits += int(following in left_ball)
            visit(following, current_depth + 1)

    if target in left_ball:
        hits += 1
    visit(target, 0)
    return hits, word_counts, transitions


def state_digest(states):
    digest = hashlib.sha256()
    for state in sorted(states):
        digest.update(state.to_bytes(STATE_BYTES, "little"))
    return digest.hexdigest()


def apply_row_factor(row, factor, translation_tables):
    g, u, v = factor
    source = 0
    for k in range(3):
        if (u >> k) & 1:
            source ^= row[k]
    delta = source ^ right_translate(source, translation_tables[g])
    result = list(row)
    for j in range(3):
        if (v >> j) & 1:
            result[j] ^= delta
    return result


def apply_row_word(row, word, translation_tables):
    result = list(row)
    for factor in word:
        result = apply_row_factor(result, factor, translation_tables)
    return result


def regular_basis_replay(word, c_index, multiplication, translation_tables):
    """Check the direct witness on all 3*168 regular-action basis rows."""
    checked = 0
    for register in range(3):
        for address in range(RING_BITS):
            row = [0, 0, 0]
            row[register] = 1 << address
            got = apply_row_word(row, word, translation_tables)
            expected = [0, 0, 0]
            if register < 2:
                expected[register] = 1 << multiplication[address][c_index]
            else:
                expected[register] = 1 << address
            need(got == expected, "six-call direct witness regular-basis mismatch")
            checked += 1
    return checked


def join_control(target, left_radius, right_radius, factors, translation_tables):
    left, _ = ball(pack_identity(), left_radius, factors, translation_tables)
    right, _ = ball(target, right_radius, factors, translation_tables)
    return len(left & right)


def check_sources():
    source = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    need(source["base_commit"] == BASE, "source base drift")
    import hashlib as _hashlib
    import subprocess
    for row in source["files"]:
        path = row["path"]
        expression = BASE + ":" + path
        blob = subprocess.check_output(["git", "rev-parse", expression], cwd=ROOT, text=True).strip()
        data = subprocess.check_output(["git", "show", expression], cwd=ROOT)
        need(blob == row["git_blob"], "Git blob mismatch: " + path)
        need(_hashlib.sha256(data).hexdigest() == row["sha256"], "source SHA256 mismatch: " + path)
        if row["usage"] == "input":
            need((ROOT / path).read_bytes() == data, "working input drift: " + path)
    selected_bytes = (ROOT / "certificates/selected-result.json").read_bytes()
    need(_hashlib.sha256(selected_bytes).hexdigest() == SELECTED_SHA256,
         "selected record SHA mismatch")


def calculate():
    generators, names = address_generators()
    elements, shortest = enumerate_address_group(generators)
    index = {element: i for i, element in enumerate(elements)}
    need(len(index) == 168, "duplicate address group element")
    multiplication = [[index[mat3_mul(a, b)] for b in elements] for a in elements]
    identity_index = index[I3]
    need(identity_index == 0, "group identity enumeration order")
    for i, g in enumerate(generators):
        gi = index[g]
        need(multiplication[gi][gi] == identity_index, "CNOT label is not involutive")

    x, y, z = (index[g] for g in generators[:3])
    c_matrix = mat3_mul(mat3_mul(generators[0], generators[1]), generators[2])
    c_index = index[c_matrix]
    power = I3
    for _ in range(7):
        power = mat3_mul(power, c_matrix)
    need(power == I3 and mat3_mul(I3, c_matrix) != I3, "target address is not order seven")
    need(len(shortest[c_matrix]) == 3, "target direct word cost")

    projectors_list = projectors()
    factors = tuple((generator_number, u, v)
                    for generator_number in range(len(generators)) for u, v in projectors_list)
    need(len(factors) == 168, "paid-factor inventory")
    tables = make_right_translation_tables(multiplication,
                                          tuple(index[g] for g in generators))
    identity = pack_identity()
    target = pack_target(c_index)

    # Each factor is an involution in characteristic two: g^2=1 and N^2=N.
    for factor in factors:
        need(apply_factor(apply_factor(identity, factor, tables), factor, tables) == identity,
             "paid factor failed its inverse check")

    direct = tuple((generator_number, 1 << register, 1 << register)
                   for register in (0, 1) for generator_number in range(3))
    direct_state = identity
    for factor in direct:
        direct_state = apply_factor(direct_state, factor, tables)
    need(direct_state == target, "six-call direct witness formal endpoint")
    basis_columns = regular_basis_replay(direct, c_index, multiplication, tables)
    need(basis_columns == 504, "regular-action basis coverage")

    # Exhaust every formal word of length <=5 by the 2+3 radius split.
    left, left_shells = ball(identity, 2, factors, tables)
    hit_count, right_word_counts, right_transitions = target_side_search(
        target, 3, left, factors, tables)
    need(hit_count == 0, "a word of at most five paid calls exists")

    # Positive controls establish the join orientation and catch a lost role.
    one_target = pack_target_one(c_index)
    one_target_hits = join_control(one_target, 1, 2, factors, tables)
    need(one_target_hits > 0, "one-target three-call join control failed")
    identity_hits = join_control(identity, 0, 0, factors, tables)
    need(identity_hits == 1, "identity join control failed")

    # Mutating a label order or omitting a call must break the direct endpoint.
    wrong_direct = tuple((generator_number, 1 << register, 1 << register)
                         for register in (0, 1) for generator_number in (0, 2, 1))
    wrong_state = identity
    for factor in wrong_direct:
        wrong_state = apply_factor(wrong_state, factor, tables)
    need(wrong_state != target, "wrong CNOT order escaped the endpoint control")
    omissions = 0
    for omitted in range(len(direct)):
        state = identity
        for j, factor in enumerate(direct):
            if j != omitted:
                state = apply_factor(state, factor, tables)
        need(state != target, "omitted-call control escaped")
        omissions += 1

    return {
        "status": "PASS_GL3_ORDER7_DIRTY_REGISTER_FLOOR",
        "base_commit": BASE,
        "seed": "39ae4eb03387f147b3cd06da8e84b83e",
        "selected_record_sha256": SELECTED_SHA256,
        "model": {
            "address_group_order": len(elements),
            "paid_address_labels": list(names),
            "scalar_registers": 3,
            "free_scalar_mixing": "GL3(F2)",
            "rank_one_idempotents": len(projectors_list),
            "paid_factors": len(factors),
            "target": "diag([C],[C],1)",
            "C_matrix_rows": [list(c_matrix[0:3]), list(c_matrix[3:6]), list(c_matrix[6:9])],
            "C_order": 7,
            "C_direct_word": list(names[:3]),
            "direct_paid_calls": len(direct),
        },
        "exact_search": {
            "maximum_word_length": 5,
            "split": [2, 3],
            "identity_side_shells": left_shells,
            "identity_side_ball_size": len(left),
            "target_side_raw_word_counts": right_word_counts,
            "target_side_transitions": right_transitions,
            "intersection_hits": hit_count,
            "identity_side_sha256": state_digest(left),
        },
        "positive_checks": {
            "factor_inverse_checks": len(factors),
            "direct_regular_basis_columns": basis_columns,
            "one_target_join_hits": one_target_hits,
            "identity_join_hits": identity_hits,
        },
        "negative_controls": {
            "wrong_CNOT_order_rejected": True,
            "omitted_direct_calls_rejected": omissions,
        },
        "conclusion": "The exact minimum is six paid calls in this finite three-register full-coordinate-CNOT model; no scalar-mixing saving is found.",
        "limitations": [
            "This result covers only the full six-coordinate-CNOT alphabet, the stated order-seven target, and exactly three scalar registers.",
            "No selected supplier, physical compilation, recursive moment change, new kappa, or multiplication theorem is established.",
            "No human independent review or proof-assistant formalization is claimed."
        ]
    }


def pack_target_one(c_index):
    result = 1 << c_index
    result |= 1 << (RING_BITS * 4)
    result |= 1 << (RING_BITS * 8)
    return result


if __name__ == "__main__":
    check_sources()
    result = calculate()
    out = PACKAGE / "RESULT.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PASS_GL3_ORDER7_DIRTY_REGISTER registers=3 factors=168 prefix=22051 suffix_words=4770025 hits=0 minimum=6")
