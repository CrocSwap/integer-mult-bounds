#!/usr/bin/env python3
"""Exact P111 bit-decoder factorization through five rank-two planes."""

from fractions import Fraction
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
WORD_PATH = ROOT / "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
EXPECTED_PATH = ROOT / "research/e8-bit-p111-tuned/tune/EXPECTED.json"
ASSEMBLY_PATH = ROOT / "research/community-frontier1094-audit/ASSEMBLY.json"
CEILING_PATH = ROOT / "research/complex-local-word-ceiling/ceiling.py"

# Columns of a 9-by-10 Parseval frame over F2, in little-endian coordinates.
# The verifier checks sum_j a_j a_j^T = I_9 directly.
FRAME_COLUMNS = (0x003, 0x005, 0x006, 0x007, 0x008,
                 0x010, 0x020, 0x040, 0x080, 0x100)
PLANES = ((0, 1), (2, 3), (4, 5), (6, 7), (8, 9))
NINE = 9
BASE_COMMIT = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pinned_bytes(path):
    return subprocess.run(["git", "show", f"{BASE_COMMIT}:{path}"], cwd=ROOT,
                          check=True, capture_output=True).stdout


def rank_f2(vectors):
    pivots = {}
    for value in vectors:
        value = int(value)
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    return len(pivots)


def frame_identity(columns):
    return all(
        sum(((column >> i) & 1) * ((column >> j) & 1) for column in columns) % 2
        == int(i == j)
        for i in range(NINE) for j in range(NINE)
    )


def load_ceiling():
    spec = importlib.util.spec_from_file_location("pinned_ceiling", CEILING_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rational_basis(rows, ncols=8):
    matrix = [[Fraction(value) for value in row] for row in rows]
    pivots = []
    rank = 0
    for col in range(ncols):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][col]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = matrix[rank][col]
        matrix[rank] = [value / scale for value in matrix[rank]]
        for i in range(len(matrix)):
            if i != rank and matrix[i][col]:
                scale = matrix[i][col]
                matrix[i] = [x - scale * y for x, y in zip(matrix[i], matrix[rank])]
        pivots.append(col)
        rank += 1
    return matrix[:rank]


def rank_fraction(matrix, ncols):
    return len(rational_basis(matrix, ncols))


def pairing_rank(lines, target_mask, source_mask, v):
    targets = [lines[i] for i in range(v) if (target_mask >> i) & 1]
    sources = [lines[i] for i in range(v) if (source_mask >> i) & 1]
    target_basis = rational_basis(targets)
    source_basis = rational_basis(sources)
    pairing = [
        [sum(x * y for x, y in zip(t, s)) / 2 for s in source_basis]
        for t in target_basis
    ]
    return rank_fraction(pairing, len(source_basis))


def decoder_map(left, right, n_targets):
    """Return each target's linear form over every initial word register."""
    result = []
    for target in range(n_targets):
        value = 0
        for lmask, rmask in zip(left, right):
            if (lmask >> target) & 1:
                value ^= rmask
        result.append(value)
    return result


def transformed_factors(old, columns):
    result = []
    for column in columns:
        value = 0
        for i in range(NINE):
            if (column >> i) & 1:
                value ^= old[i]
        result.append(value)
    return result


def plane_map(left, right, n_targets, planes=PLANES):
    output = [0] * n_targets
    for i, j in planes:
        for target in range(n_targets):
            if (left[i] >> target) & 1:
                output[target] ^= right[i]
            if (left[j] >> target) & 1:
                output[target] ^= right[j]
    return output


def serialize_masks(values, nbits):
    size = (nbits + 7) // 8
    return b"".join(value.to_bytes(size, "little") for value in values)


def check():
    expected_bytes = EXPECTED_PATH.read_bytes()
    word_bytes = WORD_PATH.read_bytes()
    require(sha256(EXPECTED_PATH) == "b9f0e5ca038abe837b0007c8fe006f366a6f02009244ac57705a8a200e2301f4",
            "pinned PR589 EXPECTED.json changed")
    require(sha256(WORD_PATH) == "e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f",
            "pinned tuned PR589 word changed")
    expected = json.loads(expected_bytes)
    word = json.loads(gzip.decompress(word_bytes))
    selected = json.loads(pinned_bytes("certificates/selected-result.json"))
    require(selected["source_manifest"] == "research/community-frontier1094-audit/SELECTED-SOURCE.json"
            and selected["certificate"] == "research/community-frontier1094-audit/ASSEMBLY.json"
            and selected["review"] == "docs/research/community-batch1099-review.md",
            "selected-result pointers changed")
    require(selected["certificate_sha256"] == sha256(ASSEMBLY_PATH)
            == "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
            "selected certificate hash mismatch")
    require(hashlib.sha256(pinned_bytes("research/community-frontier1094-audit/SELECTED-SOURCE.json")).hexdigest()
            == "79b3de5db3dbcb9829789ba58e9e45758926031e2a7d80667a08429d369be53b",
            "selected source manifest changed")
    require(hashlib.sha256(pinned_bytes("docs/research/community-batch1099-review.md")).hexdigest()
            == "7e76d2c38e5fce30587835b7251df1430488ae4dd372611ef69a3f03f476b6cb",
            "selected review changed")
    word_record = expected["word"]
    require(word["v"] == 111 and word_record["v"] == 111 and word["R"] == 439,
            "not the selected punctured R439 P111 word")
    require(word["punctured"] == [10, 15, 51, 53, 56, 66, 72, 89, 111],
            "puncture list changed")
    require(word_record["copy_ranks"] == [7] * NINE and word_record["decoder_constant"] == 63,
            "line-port baseline decoder invoice changed")
    require(hashlib.sha256(word_bytes).hexdigest() == word_record["file_sha256"],
            "word archive does not match its receipt")

    assembly = json.loads(ASSEMBLY_PATH.read_text(encoding="utf-8"))
    supplier = assembly["bit_supplier"]
    require(supplier["pr"] == 589 and supplier["word"]["decoder_constant"] == 63,
            "selected assembly no longer cites PR589's P111 word")
    require(supplier["deficit_formula"] == "T(2Kv-L*cst), L=9 T=32 K=4 M=64",
            "selected bit-side mass parameters changed")

    v = word["v"]
    n_registers = 2 * v + word["R"]
    values = [1 << register for register in range(n_registers)]
    for section in ("D", "A"):
        for _frame, destination, sources in word[section]:
            for source in sources:
                values[destination] ^= values[source]

    old_right = [values[register] for register in word["ret"]]
    old_left = [sum(1 << target for target, row in enumerate(word["scatter"]) if k in row)
                for k in range(NINE)]
    require(len(old_left) == NINE and len(old_right) == NINE, "expected nine retained channels")
    old_map = decoder_map(old_left, old_right, v)

    lines = [tuple(int(value) for value in row) for row in word["lines"]]
    b0 = [
        sum((((1 + sum(x * y for x, y in zip(lines[t], lines[s])) // 2) & 1) << s)
            for s in range(v))
        for t in range(v)
    ]
    for target in range(v):
        require((old_map[target] & ((1 << v) - 1)) == b0[target],
                f"source decoder row {target} does not equal B0=(1+G) mod 2")
    old_costs = [pairing_rank(lines, old_left[i],
                              sum(1 << s for s in range(v) if (old_right[i] >> s) & 1), v)
                 for i in range(NINE)]
    require(old_costs == [7] * NINE, f"line-port costs changed: {old_costs}")

    require(frame_identity(FRAME_COLUMNS), "Parseval frame identity failed")
    new_left = transformed_factors(old_left, FRAME_COLUMNS)
    new_right = transformed_factors(old_right, FRAME_COLUMNS)
    new_map = plane_map(new_left, new_right, v)
    require(new_map == old_map, "five-plane decoder differs on a dirty input basis column")
    require(all((new_map[t] & ((1 << v) - 1)) == b0[t] for t in range(v)),
            "five-plane decoder does not reproduce B0")

    plane_costs = []
    plane_ranks = []
    plane_sizes = []
    for i, j in PLANES:
        require(rank_f2((new_left[i], new_left[j])) == 2,
                f"target factors in plane {i // 2} are dependent")
        require(rank_f2((new_right[i], new_right[j])) == 2,
                f"source factors in plane {i // 2} are dependent")
        target_union = new_left[i] | new_left[j]
        source_union = 0
        for source in range(v):
            if ((new_right[i] | new_right[j]) >> source) & 1:
                source_union |= 1 << source
        cost = pairing_rank(lines, target_union, source_union, v)
        plane_costs.append(cost)
        plane_ranks.append((rank_f2((new_left[i], new_left[j])),
                            rank_f2((new_right[i], new_right[j]))))
        plane_sizes.append((target_union.bit_count(), source_union.bit_count()))
    require(plane_costs == [8] * 5, f"unexpected plane copy ranks: {plane_costs}")
    require(sum(plane_costs) == 40 and sum(old_costs) == 63,
            "copy bill does not improve 63 -> 40")

    # The identity holds for every formal input column, including dirty helper
    # coordinates: the nine source channels are multiplied by the same frame
    # as the nine target channels, and A A^T = I exactly over F2.
    full_input_digest = hashlib.sha256(serialize_masks(old_map, n_registers)).hexdigest()
    require(hashlib.sha256(serialize_masks(new_map, n_registers)).hexdigest() == full_input_digest,
            "dirty-input decoder digest differs")

    # Failure controls: a broken frame, omitted plane, switched source channel,
    # and a collapsed rank-two source plane must all be rejected.
    broken_columns = list(FRAME_COLUMNS)
    broken_columns[3] ^= 1 << 8
    require(not frame_identity(broken_columns), "frame mutation was not detected")
    require(plane_map(new_left, new_right, v, PLANES[:-1]) != old_map,
            "omitted-plane control was not detected")
    switched = list(new_right)
    switched[0], switched[1] = switched[1], switched[0]
    require(plane_map(new_left, switched, v) != old_map,
            "switched-source control was not detected")
    require(rank_f2((new_right[0], new_right[0])) != 2,
            "collapsed-plane rank control is invalid")

    profile = {int(rank): int(count) for rank, count in word_record["local_histogram"].items()}
    for rank in word_record["copy_ranks"]:
        profile[rank] -= 1
    profile[8] = profile.get(8, 0) + len(PLANES)
    # Five independent XORs on each side form the ten frame channels.
    profile[1] += 2 * sum(column.bit_count() - 1 for column in FRAME_COLUMNS)
    require(profile[1] == int(word_record["local_histogram"]["1"]) + 10,
            "basis-change ADD invoice changed")
    local_mass = sum(rank * count for rank, count in profile.items())
    require(local_mass == 5116, f"unexpected favorable local mass {local_mass}")

    ceiling = load_ceiling()
    families = 2 * 4 * v
    stages = 9
    m = 64
    max_child = expected["nine"]["bit"]["maxchild"]
    require(families == 888 and max_child == 42, "selected bit coverage/guard inputs changed")
    old_profile = {int(rank): int(count) for rank, count in word_record["local_histogram"].items()}
    baseline_model = ceiling.model(old_profile, m, families, stages, 63,
                                   R=max_child, unpaid=1)
    changed_model = ceiling.model(profile, m, families, stages, 40,
                                  R=max_child, unpaid=2)
    require(baseline_model["total_mass"] == 6279 and baseline_model["idle_mass"] == 1150,
            "baseline bit coverage identity mismatch")
    require(changed_model["total_mass"] == Fraction(18472, 3)
            and changed_model["idle_mass"] == Fraction(3124, 3),
            "replacement bit coverage identity mismatch")
    grid = Fraction(1, 10**12)
    baseline_bracket = ceiling.ceiling(old_profile, m, families, stages, 63,
                                       grid=grid, R=max_child, unpaid=1)
    changed_bracket = ceiling.ceiling(profile, m, families, stages, 40,
                                      grid=grid, R=max_child, unpaid=2)
    target = Fraction(1, 99)
    require(baseline_bracket[1] == Fraction(1947467559, 10**12),
            "baseline ceiling replay differs")
    require(changed_bracket[1] == Fraction(8520849563, 10**12),
            "changed ceiling replay differs")
    require(changed_bracket[1] < target and
            ceiling.relax(profile, m, families, stages, 40, target,
                          R=max_child, unpaid=2)[0] > 1,
            "favorable plane screen unexpectedly reaches a=1/99")

    return {
        "status": "PASS_BIT_P111_PARSEVAL_PLANE_DECODER",
        "seed": "ceccc7658dd89c833863007fb63ad7b2",
        "base_commit": "0b1cccf86e2f5132ed286a26ef0a681a495740ea",
        "selected_record_sha256": "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
        "ports": v,
        "formal_dirty_input_columns": n_registers,
        "parseval_columns_hex": [hex(value) for value in FRAME_COLUMNS],
        "planes_zero_based": [list(pair) for pair in PLANES],
        "plane_factor_ranks": plane_ranks,
        "plane_target_source_support_sizes": plane_sizes,
        "line_copy_costs": old_costs,
        "plane_copy_costs": plane_costs,
        "copy_charge_line": sum(old_costs),
        "copy_charge_planes": sum(plane_costs),
        "basis_adds_charged": 10,
        "full_dirty_decoder_sha256": full_input_digest,
        "baseline_mass": str(baseline_model["total_mass"]),
        "baseline_idle_mass": str(baseline_model["idle_mass"]),
        "replacement_mass": str(changed_model["total_mass"]),
        "replacement_idle_mass": str(changed_model["idle_mass"]),
        "baseline_a_ceiling": [str(x) for x in baseline_bracket],
        "plane_a_ceiling": [str(x) for x in changed_bracket],
        "plane_at_1_over_99_relaxation_lower": str(
            ceiling.relax(profile, m, families, stages, 40, target,
                          R=max_child, unpaid=2)[0]),
        "unpriced_interface_obligations": [
            "physical plane-frame routes and transitions",
            "streaming/register schedule and cleanup",
            "owner hosting and whole-call placement",
            "precision/tape and integration with the selected complex supplier",
        ],
        "controls": 4,
        "kappa_claim": False,
    }


if __name__ == "__main__":
    result = check()
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
