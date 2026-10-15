#!/usr/bin/env python3
"""Exact finite check for a paired order-four dirty-output frame."""

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path


PKG = Path(__file__).resolve().parent
ROOT = PKG.parent.parent
CERT = PKG / "CERTIFICATE.json"
SEED = 56
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
BLOCKS = (0, 1, 2, 0, 1)
WORK_OCTETS = 3
OUTPUT_WIDTH = 8
WORK_WIDTH = 8 * WORK_OCTETS
LOCAL_WIDTH = OUTPUT_WIDTH + WORK_WIDTH
ECHO_WIDTH = OUTPUT_WIDTH + WORK_WIDTH + WORK_WIDTH


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(target, source, sign=1):
    require(sign in (-1, 1), "ADD sign must be +/-1")
    return ("ADD", target, source, sign)


def neg(target):
    return ("NEG", target, None, 0)


def inverse_word(word):
    inverse = []
    for kind, target, source, sign in reversed(word):
        inverse.append(add(target, source, -sign) if kind == "ADD" else neg(target))
    return inverse


def lift_word(word, indices):
    lifted = []
    for kind, target, source, sign in word:
        lifted.append((kind, indices[target], None if source is None else indices[source], sign))
    return lifted


def swap_word(a, b):
    """Pure swap (a,b)->(b,a), using three ADDs and one NEG."""
    return [add(a, b), add(b, a, -1), add(a, b), neg(b)]


def signed_swap_positive(a, b):
    """Three ADDs map (a,b)->(b,-a)."""
    return [add(a, b), add(b, a, -1), add(a, b)]


def signed_swap_negative(a, b):
    """Three ADDs map (a,b)->(-b,a)."""
    return [add(b, a), add(a, b, -1), add(b, a)]


def one_cycle_word(phase, base=0):
    """Powers of (a,b,c,d)->(d,a,b,c) on one four-register cycle."""
    require(phase in range(4), "invalid phase")
    a, b, c, d = (base + i for i in range(4))
    if phase == 0:
        return []
    if phase == 1:
        # Three signed swaps compose to (d,-a,b,c); one NEG on b gives
        # the requested pure cycle (d,a,b,c).
        return (signed_swap_positive(a, b) + signed_swap_negative(a, c)
                + signed_swap_positive(a, d) + [neg(b)])
    if phase == 2:
        return swap_word(a, c) + swap_word(b, d)
    return inverse_word(one_cycle_word(1, base))


def octet_word(phase, base=0):
    """Apply the same phase to two disjoint four-cycles."""
    return one_cycle_word(phase, base) + one_cycle_word(phase, base + 4)


def workspace_word(phase, base=0):
    """Apply P^phase to three disjoint eight-register blocks."""
    return sum((octet_word(phase, base + 8 * j) for j in range(WORK_OCTETS)), [])


def word_counts(word):
    adds = sum(kind == "ADD" for kind, *_ in word)
    negs = sum(kind == "NEG" for kind, *_ in word)
    return (adds, negs)


def word_sha256(word):
    payload = json.dumps(word, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def vector_add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def vector_scale(a, n):
    return tuple(n * x for x in a)


def vector_total(a):
    return sum(a)


def phase_counts(phase):
    return word_counts(octet_word(phase))


def work_phase_counts(phase):
    return word_counts(workspace_word(phase))


def apply_word_matrix(word, width):
    """Return output rows as exact integer linear forms in the input rows."""
    rows = [[int(i == j) for j in range(width)] for i in range(width)]
    for kind, target, source, sign in word:
        require(0 <= target < width, "gate target outside matrix")
        if kind == "ADD":
            require(source is not None and 0 <= source < width, "gate source outside matrix")
            rows[target] = [a + sign * b for a, b in zip(rows[target], rows[source])]
        else:
            rows[target] = [-x for x in rows[target]]
    return rows


def matmul(a, b):
    require(bool(a) and bool(b) and len(a[0]) == len(b), "bad matrix dimensions")
    bt = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def matrix_power(a, exponent):
    out = identity(len(a))
    for _ in range(exponent):
        out = matmul(out, a)
    return out


def expected_octet_frame():
    rows = [[0] * 8 for _ in range(8)]
    for base in (0, 4):
        # New tuple is (old d, old a, old b, old c).
        for target, source in ((base, base + 3), (base + 1, base),
                               (base + 2, base + 1), (base + 3, base + 2)):
            rows[target][source] = 1
    return rows


def block_diag(blocks):
    widths = [len(block) for block in blocks]
    total = sum(widths)
    out = [[0] * total for _ in range(total)]
    offset = 0
    for block, width in zip(blocks, widths):
        for i in range(width):
            for j in range(width):
                out[offset + i][offset + j] = block[i][j]
        offset += width
    return out


def reader_matrix(block):
    rows = [[0] * WORK_WIDTH for _ in range(OUTPUT_WIDTH)]
    for j in range(OUTPUT_WIDTH):
        rows[j][8 * block + j] = 1
    return rows


def child_word(block):
    word = [add(j, OUTPUT_WIDTH + 8 * block + j) for j in range(OUTPUT_WIDTH)]
    work_indices = [OUTPUT_WIDTH + j for j in range(WORK_WIDTH)]
    return word + lift_word(workspace_word(1), work_indices)


def expected_child(block):
    r = reader_matrix(block)
    p = matrix_power(expected_octet_frame(), 1)
    rows = []
    for i in range(OUTPUT_WIDTH):
        rows.append([int(i == j) for j in range(OUTPUT_WIDTH)] + r[i])
    for i in range(WORK_WIDTH):
        rows.append([0] * OUTPUT_WIDTH + block_diag([p] * WORK_OCTETS)[i])
    return rows


def expected_child_inverse(block):
    r = reader_matrix(block)
    p_inverse = matrix_power(expected_octet_frame(), 3)
    correction = matmul(r, block_diag([p_inverse] * WORK_OCTETS))
    rows = []
    for i in range(OUTPUT_WIDTH):
        rows.append([int(i == j) for j in range(OUTPUT_WIDTH)] + [-x for x in correction[i]])
    for i in range(WORK_WIDTH):
        rows.append([0] * OUTPUT_WIDTH + block_diag([p_inverse] * WORK_OCTETS)[i])
    return rows


def batch_word(states, blocks=BLOCKS, wrong_first_output_phase=False, omit_last_gap=False):
    """Emit a batch; states list aligned phases at entrance/after each child."""
    require(len(states) == len(blocks) + 1, "wrong state path length")
    require(all(p in range(4) for p in states), "phase outside Z/4Z")
    work_indices = [OUTPUT_WIDTH + j for j in range(WORK_WIDTH)]
    word = lift_word(octet_word(states[0]), list(range(OUTPUT_WIDTH)))
    word += lift_word(workspace_word(states[0]), work_indices)
    for i, block in enumerate(blocks):
        word += child_word(block)
        if omit_last_gap and i == len(blocks) - 1:
            continue
        old, new = states[i], states[i + 1]
        u = (new - old - 1) % 4
        v = (new - old) % 4
        if wrong_first_output_phase and i == 0:
            v = (v + 1) % 4
        word += lift_word(workspace_word(u), work_indices)
        word += lift_word(octet_word(v), list(range(OUTPUT_WIDTH)))
    return word


def boundary_components(states):
    total = vector_add(work_phase_counts(states[0]), phase_counts(states[0]))
    for i, (old, new) in enumerate(zip(states, states[1:])):
        u = (new - old - 1) % 4
        v = (new - old) % 4
        total = vector_add(total, work_phase_counts(u))
        total = vector_add(total, phase_counts(v))
    return total


def dynamic_plan(k):
    require(k > 0, "positive child count required")
    wcost = [vector_scale(phase_counts(p), WORK_OCTETS) for p in range(4)]
    ocost = [phase_counts(p) for p in range(4)]
    f = [vector_total(vector_add(wcost[t], ocost[t])) for t in range(4)]
    predecessors = []
    for _ in range(k):
        g = [0] * 4
        pred = [0] * 4
        for s in range(4):
            choices = []
            for t in range(4):
                u, v = (s - t - 1) % 4, (s - t) % 4
                step = vector_add(wcost[u], ocost[v])
                choices.append((f[t] + vector_total(step), t))
            g[s], pred[s] = min(choices)
        f = g
        predecessors.append(pred)
    state = 0  # final arbitrary-output/restoration endpoint is canonical
    reverse_states = [state]
    for pred in reversed(predecessors):
        state = pred[state]
        reverse_states.append(state)
    states = list(reversed(reverse_states))
    return states, f[0], boundary_components(states)


def brute_boundary_min(k):
    best = None
    for prefix in itertools.product(range(4), repeat=k):
        states = list(prefix) + [0]
        cost = vector_total(boundary_components(states))
        best = cost if best is None else min(best, cost)
    return best


def expected_batch(blocks=BLOCKS):
    rsum = [[0] * WORK_WIDTH for _ in range(OUTPUT_WIDTH)]
    for block in blocks:
        r = reader_matrix(block)
        for i in range(OUTPUT_WIDTH):
            rsum[i] = [a + b for a, b in zip(rsum[i], r[i])]
    rows = []
    for i in range(OUTPUT_WIDTH):
        rows.append([int(i == j) for j in range(OUTPUT_WIDTH)] + rsum[i])
    rows.extend([[0] * OUTPUT_WIDTH + row for row in identity(WORK_WIDTH)])
    return rows


def lifted_batch_word(states):
    local = batch_word(states)
    mapping = list(range(OUTPUT_WIDTH)) + [OUTPUT_WIDTH + WORK_WIDTH + i for i in range(WORK_WIDTH)]
    return lift_word(local, mapping)


def echo_word(states):
    word = [add(OUTPUT_WIDTH + WORK_WIDTH + i, OUTPUT_WIDTH + i) for i in range(WORK_WIDTH)]
    body = lifted_batch_word(states)
    word += body
    word += [add(OUTPUT_WIDTH + WORK_WIDTH + i, OUTPUT_WIDTH + i, -1) for i in range(WORK_WIDTH)]
    word += inverse_word(body)
    return word


def expected_echo(blocks=BLOCKS):
    rsum = [[0] * WORK_WIDTH for _ in range(OUTPUT_WIDTH)]
    for block in blocks:
        r = reader_matrix(block)
        for i in range(OUTPUT_WIDTH):
            rsum[i] = [a + b for a, b in zip(rsum[i], r[i])]
    rows = []
    for i in range(OUTPUT_WIDTH):
        rows.append([int(i == j) for j in range(OUTPUT_WIDTH)] + rsum[i] + [0] * WORK_WIDTH)
    rows.extend([[0] * OUTPUT_WIDTH + row + [0] * WORK_WIDTH for row in identity(WORK_WIDTH)])
    rows.extend([[0] * (OUTPUT_WIDTH + WORK_WIDTH) + row for row in identity(WORK_WIDTH)])
    return rows


def internal_c_word(states):
    """Implement one internal C_v using source X and a separate dirty scratch."""
    word = echo_word(states)
    source_indices = [OUTPUT_WIDTH + j for j in range(WORK_WIDTH)]
    return word + lift_word(workspace_word(1), source_indices)


def expected_internal_c():
    echo = expected_echo()
    p = block_diag([expected_octet_frame()] * WORK_OCTETS)
    rows = [row[:] for row in echo[:OUTPUT_WIDTH]]
    rows.extend([[0] * OUTPUT_WIDTH + p[i] + [0] * WORK_WIDTH
                 for i in range(WORK_WIDTH)])
    rows.extend([[0] * (OUTPUT_WIDTH + WORK_WIDTH) + row
                 for row in identity(WORK_WIDTH)])
    return rows


def reject_controls(states, batch_expected):
    controls = 0
    # A sign mutation in the rotation circuit must not pass its frame identity.
    broken = octet_word(1)
    kind, target, source, sign = broken[0]
    broken[0] = (kind, target, source, -sign)
    require(apply_word_matrix(broken, 8) != expected_octet_frame(), "bad rotation control escaped")
    controls += 1

    # An extra output phase at the first gap violates the reader/frame contract.
    misaligned = batch_word(states, wrong_first_output_phase=True)
    require(apply_word_matrix(misaligned, LOCAL_WIDTH) != batch_expected,
            "misaligned phase control escaped")
    controls += 1

    # Omitting the terminal correction must leave a noncanonical dirty workspace.
    unclosed = batch_word(states, omit_last_gap=True)
    require(apply_word_matrix(unclosed, LOCAL_WIDTH) != batch_expected,
            "missing terminal restoration control escaped")
    controls += 1

    # A forward batch followed by itself is not the literal inverse operation.
    forward = batch_word(states)
    doubled = forward + forward
    require(apply_word_matrix(doubled, LOCAL_WIDTH) != identity(LOCAL_WIDTH),
            "forward-for-inverse control escaped")
    controls += 1
    return controls


def permutation_determinant(matrix):
    columns = []
    signs = []
    for row in matrix:
        nonzero = [(j, x) for j, x in enumerate(row) if x]
        require(len(nonzero) == 1 and nonzero[0][1] in (-1, 1),
                "frame is not a signed permutation")
        columns.append(nonzero[0][0])
        signs.append(nonzero[0][1])
    inversions = sum(columns[i] > columns[j]
                     for i in range(len(columns)) for j in range(i + 1, len(columns)))
    return (-1 if inversions % 2 else 1) * math.prod(signs)


def prefix_row_l1_peak(word, width):
    rows = identity(width)
    peak = max(sum(abs(x) for x in row) for row in rows)
    for kind, target, source, sign in word:
        if kind == "ADD":
            rows[target] = [a + sign * b for a, b in zip(rows[target], rows[source])]
        else:
            rows[target] = [-x for x in rows[target]]
        peak = max(peak, *(sum(abs(x) for x in row) for row in rows))
    return peak


def verify_source_pins():
    pins = json.loads((PKG / "SOURCES.json").read_text())
    require(pins["base_commit"] == BASE, "SOURCES base mismatch")
    for entry in pins["files"]:
        path = ROOT / entry["path"]
        require(path.is_file(), "missing pinned input: " + entry["path"])
        got = hashlib.sha256(path.read_bytes()).hexdigest()
        require(got == entry["sha256"], "pinned input bytes changed: " + entry["path"])
    return {entry["path"]: entry["sha256"] for entry in pins["files"]}


def build_certificate():
    source_pins = verify_source_pins()
    p1 = expected_octet_frame()
    phase_vectors = [word_counts(octet_word(p)) for p in range(4)]
    require(phase_vectors == [(0, 0), (18, 2), (12, 4), (18, 2)], "octet gate-cost vector changed")
    for phase in range(4):
        require(apply_word_matrix(octet_word(phase), 8) == matrix_power(p1, phase),
                "octet phase word does not implement P^phase")
        require(apply_word_matrix(workspace_word(phase), WORK_WIDTH)
                == block_diag([matrix_power(p1, phase)] * WORK_OCTETS),
                "workspace phase word does not implement P^phase")
    require(matrix_power(p1, 4) == identity(8) and p1 != identity(8), "frame is not order four")
    require(matrix_power(p1, 2) != identity(8), "frame has order two")
    require(permutation_determinant(p1) == 1, "paired four-cycle frame is not orientation-preserving")

    q = p1
    readers = [reader_matrix(block) for block in BLOCKS]
    for r in readers:
        require(matmul(r, block_diag([p1] * WORK_OCTETS)) == matmul(q, r),
                "reader does not intertwine P and Q")

    child_counts = []
    child_columns = 0
    for block in sorted(set(BLOCKS)):
        word = child_word(block)
        expected = expected_child(block)
        require(apply_word_matrix(word, LOCAL_WIDTH) == expected,
                "child word differs from its declared dirty-state map")
        inv = inverse_word(word)
        require(apply_word_matrix(inv, LOCAL_WIDTH) == expected_child_inverse(block),
                "literal child inverse differs from the block inverse formula")
        require(matmul(apply_word_matrix(inv, LOCAL_WIDTH), expected) == identity(LOCAL_WIDTH),
                "child inverse does not restore arbitrary input")
        require(word_counts(word) == (62, 6), "child invoice changed")
        require(word_counts(inv) == word_counts(word), "literal child inverse count changed")
        child_counts.append({"block": block, "ADD": 62, "NEG": 6,
                             "word_sha256": word_sha256(word),
                             "inverse_word_sha256": word_sha256(inv),
                             "basis_columns": LOCAL_WIDTH})
        child_columns += LOCAL_WIDTH

    states, optimum, chosen_vector = dynamic_plan(5)
    require(states == [0, 1, 2, 3, 0, 0], "unexpected deterministic shortest path")
    require(optimum == 140 and chosen_vector == (126, 14) and vector_total(chosen_vector) == optimum,
            "four-state recurrence returned an unexpected boundary cost")
    require(brute_boundary_min(5) == optimum, "exhaustive 4^5 schedule census disagrees")
    eager_vec = vector_scale(work_phase_counts(3), 5)
    require(eager_vec == (270, 30) and vector_total(eager_vec) == 300,
            "eager per-child restoration invoice changed")

    batch = batch_word(states)
    batch_map = apply_word_matrix(batch, LOCAL_WIDTH)
    expected_h = expected_batch()
    require(batch_map == expected_h, "optimized batch does not implement the full typed map")
    batch_inv = inverse_word(batch)
    require(matmul(apply_word_matrix(batch_inv, LOCAL_WIDTH), batch_map)
            == identity(LOCAL_WIDTH), "literal inverse batch fails on dirty columns")
    eager_states = [0] * (len(BLOCKS) + 1)
    eager_batch = batch_word(eager_states)
    require(apply_word_matrix(eager_batch, LOCAL_WIDTH) == expected_h,
            "eager baseline does not implement the same batch map")
    require(word_counts(batch) == (436, 44), "optimized batch primitive invoice changed")
    require(word_counts(eager_batch) == (580, 60), "eager batch primitive invoice changed")

    echo_opt = echo_word(states)
    echo_eager = echo_word(eager_states)
    echo_expected = expected_echo()
    require(apply_word_matrix(echo_opt, ECHO_WIDTH) == echo_expected,
            "optimized echo fails arbitrary dirty/source inputs")
    require(apply_word_matrix(echo_eager, ECHO_WIDTH) == echo_expected,
            "eager echo is not the same complete map")
    require(word_counts(echo_opt) == (920, 88), "optimized echo primitive invoice changed")
    require(word_counts(echo_eager) == (1208, 120), "eager echo primitive invoice changed")
    require(len(echo_opt) == 1008 and len(echo_eager) == 1328,
            "complete echo totals changed")

    internal_opt = internal_c_word(states)
    internal_eager = internal_c_word(eager_states)
    internal_expected = expected_internal_c()
    require(apply_word_matrix(internal_opt, ECHO_WIDTH) == internal_expected,
            "internal recursive C_v map fails arbitrary input/scratch columns")
    require(apply_word_matrix(internal_eager, ECHO_WIDTH) == internal_expected,
            "eager internal C_v map differs from the optimized interface")
    require(matmul(apply_word_matrix(inverse_word(internal_opt), ECHO_WIDTH), internal_expected)
            == identity(ECHO_WIDTH), "internal C_v literal inverse fails")
    require(word_counts(internal_opt) == (974, 94), "optimized internal C_v invoice changed")
    require(word_counts(internal_eager) == (1262, 126), "eager internal C_v invoice changed")

    control_count = reject_controls(states, expected_h)
    phase_changes = []
    for old, new in zip(states, states[1:]):
        phase_changes.append({"before": old, "after": new,
                              "P_power": (new - old - 1) % 4,
                              "Q_power": (new - old) % 4})
    return {
        "schema_version": 1,
        "task": "z4-paired-frame-restoration-seed56",
        "base_commit": BASE,
        "assignment": {"os_seed": SEED, "track": "recursive interfaces",
                       "cycle_order": 2 + SEED % 3},
        "selected_context": {
            "kappa": "836330098538459/500000000000000000",
            "decimal": "0.001672660197076918",
            "selected_source_pr": 1094,
            "review": "docs/research/community-batch1099-review.md",
        },
        "frame": {
            "per_register": "two disjoint 4-cycles on one octet",
            "determinant": 1,
            "order": 4,
            "phase_costs_per_octet": [
                {"phase": p, "ADD": c[0], "NEG": c[1], "total": sum(c),
                 "word_sha256": word_sha256(octet_word(p))}
                for p, c in enumerate(phase_vectors)
            ],
            "workspace_octets": WORK_OCTETS,
            "output_octets": 1,
            "readers": list(BLOCKS),
            "intertwining_verified": True,
        },
        "boundary": {
            "children": len(BLOCKS),
            "states": states,
            "transitions": phase_changes,
            "dynamic_program_total": optimum,
            "exhaustive_path_count": 4 ** len(BLOCKS),
            "exhaustive_path_minimum": brute_boundary_min(5),
            "optimized_ADD": chosen_vector[0],
            "optimized_NEG": chosen_vector[1],
            "eager_ADD": eager_vec[0],
            "eager_NEG": eager_vec[1],
            "eager_total": vector_total(eager_vec),
            "saved_per_batch": vector_total(eager_vec) - optimum,
            "optimized_word_sha256": word_sha256(batch),
            "eager_word_sha256": word_sha256(eager_batch),
            "macro_alphabet": "canonical powers P^u and Q^v using the listed explicit words",
        },
        "child": {"per_call": {"ADD": 62, "NEG": 6, "total": 68},
                  "selection_blocks": list(BLOCKS), "distinct_block_checks": child_counts,
                  "checked_basis_columns": child_columns},
        "complete_echo": {
            "layout": {"output_D": OUTPUT_WIDTH, "source_X": WORK_WIDTH,
                       "working_W": WORK_WIDTH, "total_data_coordinates": ECHO_WIDTH},
            "map": "(D,X,W)->(D+sum_i R_i X,X,W)",
            "optimized": {"ADD": 920, "NEG": 88, "total": 1008},
            "eager": {"ADD": 1208, "NEG": 120, "total": 1328},
            "saved_total_primitives": 320,
            "dispatches": {"optimized": 1008, "eager": 1328},
            "reads": {"optimized": 1928, "eager": 2536},
            "writes": {"optimized": 1008, "eager": 1328},
            "optimized_word_sha256": word_sha256(echo_opt),
            "eager_word_sha256": word_sha256(echo_eager),
            "all_arbitrary_dirty_basis_columns": ECHO_WIDTH,
            "prefix_row_l1_peak": {"optimized": prefix_row_l1_peak(echo_opt, ECHO_WIDTH),
                                    "eager": prefix_row_l1_peak(echo_eager, ECHO_WIDTH)},
            "internal_C_v_example": {
                "optimized": {"ADD": 974, "NEG": 94, "total": 1068},
                "eager": {"ADD": 1262, "NEG": 126, "total": 1388},
                "optimized_word_sha256": word_sha256(internal_opt),
                "eager_word_sha256": word_sha256(internal_eager),
                "all_arbitrary_input_and_scratch_basis_columns": ECHO_WIDTH,
            },
        },
        "recursive_interface_cost": {
            "leaf_forward": {"ADD": 62, "NEG": 6},
            "internal_C_v": "2*sum(child vectors) + (48,0) + 2*g(k_v) + (54,6)",
            "complete_root_echo": "2*sum(child vectors) + (48,0) + 2*g(k_v)",
            "g(k)": "minimum 4-state recurrence below; vector ADD/NEG invoice retained along chosen path",
            "eager_comparator": "replace g(k_v) by k_v*(54,6)",
            "depth_storage": "56 data coordinates for the root echo plus 24 per active nested internal C_v level",
        },
        "controls": {"count": control_count,
                     "names": ["rotation sign mutation", "wrong output phase", "missing terminal restoration",
                               "forward word substituted for inverse"]},
        "source_pins": source_pins,
        "scope": "Exact finite dirty-state interface construction and macro-alphabet optimum for five children; no actual supplier admission, selected profile change, new kappa, or multiplication theorem.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true", help="write the exact computed certificate")
    args = parser.parse_args()
    certificate = build_certificate()
    encoded = json.dumps(certificate, sort_keys=True, indent=2) + "\n"
    if args.emit:
        CERT.write_text(encoded)
    else:
        require(CERT.is_file(), "missing CERTIFICATE.json; run --emit once while authoring")
        saved = json.loads(CERT.read_text())
        require(saved == certificate, "committed certificate differs from recomputed evidence")
    echo = certificate["complete_echo"]
    print("PASS_Z4_PAIRED_FRAME boundary=140_vs_300 "
          "echo=1008_vs_1328 saved=320 root_cost=ADD920+NEG88 "
          "basis_columns=56 controls=4 no_new_kappa")


if __name__ == "__main__":
    main()
