"""Finite nonlinear-message controls; no code imported from PR785 or PR814.

Only the pinned PR738 Gaussian E8 geometry is reused. These finite controls
test decoder and accounting hypotheses, not the universal entropy theorem.
All new obligations use explicit exceptions, including the negative controls.
"""

from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import random


GEOMETRY_SHA256 = "4a3e2cee2e35ccebde346e63fd9869ed48b2d59de120f570650ecb9c8875f5e4"
GEOMETRY_COMMIT = "9671c5d72f3119ba26f3774f40aa7130c67bcf77"
SEED = 44
INPUT_BITS = 12
INPUT_COUNT = 1 << INPUT_BITS
INPUT_MASK = INPUT_COUNT - 1


def _load_geometry():
    path = Path(__file__).resolve().parent / "vendor" / "pr738" / "geometry.py"
    if hashlib.sha256(path.read_bytes()).hexdigest() != GEOMETRY_SHA256:
        raise ValueError("retained PR738 geometry source hash mismatch")
    specification = importlib.util.spec_from_file_location("pr738_controls_geometry", path)
    if specification is None or specification.loader is None:
        raise ValueError("cannot load retained PR738 geometry")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def _rank(rows):
    """Independent rational Gaussian elimination, avoiding retained rank code."""
    rows = [list(map(Fraction, row)) for row in rows]
    if not rows:
        return 0
    rank = 0
    for column in range(len(rows[0])):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [entry / scale for entry in rows[rank]]
        for i in range(rank + 1, len(rows)):
            scale = rows[i][column]
            rows[i] = [entry - scale * pivot_entry
                       for entry, pivot_entry in zip(rows[i], rows[rank])]
        rank += 1
        if rank == len(rows):
            break
    return rank


def _rows(geometry, lines, ports):
    return tuple(row for port in ports for row in (lines[port], geometry.J(lines[port])))


def _pair_charge(geometry, lines, source_ports, reader_ports):
    source_rows = _rows(geometry, lines, source_ports)
    reader_rows = _rows(geometry, lines, reader_ports)
    source_rank, reader_rank = _rank(source_rows), _rank(reader_rows)
    pairing_rank = _rank(tuple(tuple(geometry.dot(a, b) for b in reader_rows)
                               for a in source_rows))
    if any(rank % 2 for rank in (source_rank, reader_rank, pairing_rank)):
        raise ValueError("Gaussian dimensions must have even real rank")
    return source_rank // 2, reader_rank // 2, pairing_rank // 2


def _select_frames(graph):
    frames = []
    for frame in combinations(range(len(graph)), 4):
        mask = sum(1 << port for port in frame)
        if all(not (graph[port] & mask) for port in frame):
            frames.append(frame)
    if len(frames) != 105:
        raise ValueError("expected exactly 105 orthogonal four-line frames")
    random.Random(SEED).shuffle(frames)
    selected, used = [], set()
    for frame in frames:
        if used.isdisjoint(frame):
            selected.append(frame)
            used.update(frame)
        if len(selected) == 3:
            return tuple(selected), len(frames)
    raise ValueError("cannot select three disjoint orthogonal frames")


def _encode(word):
    z0 = (word & 15).bit_count() % 2
    z1 = ((word >> 4) & 15).bit_count() % 2
    z2 = ((word >> 8) & 15).bit_count() % 2
    return z0 | (z1 << 1) | ((z2 ^ (z0 & z1)) << 2)


def _undo_toffoli(message):
    z0, z1 = message & 1, (message >> 1) & 1
    return message ^ ((z0 & z1) << 2)


def _receiver_failures(transcript, invert=True):
    count, witness = 0, None
    for word, message in enumerate(transcript):
        parities = _undo_toffoli(message) if invert else message
        for receiver in range(INPUT_BITS):
            frame = receiver // 4
            mates = (15 << (4 * frame)) ^ (1 << receiver)
            decoded = ((parities >> frame) & 1) ^ ((word & mates).bit_count() % 2)
            expected = (word >> receiver) & 1
            if decoded != expected:
                count += 1
                if witness is None:
                    witness = {"input_word": word, "receiver_local_index": receiver,
                               "message_word": message, "decoded": decoded,
                               "expected": expected}
    return count, witness


def _conditional_projection(transcript, local_mask):
    """Condition outside a clique; require injectivity of its requested bits."""
    outside_mask = INPUT_MASK ^ local_mask
    seen, fiber_sizes = {}, Counter()
    for word, message in enumerate(transcript):
        outside = word & outside_mask
        key = outside, message
        inside = word & local_mask
        if key in seen and seen[key] != inside:
            raise ValueError("conditional transcript collision: " + json.dumps({
                "local_mask": local_mask, "outside_word": outside,
                "message_word": message, "first_inside_word": seen[key],
                "second_inside_word": inside}, sort_keys=True))
        if key not in seen:
            seen[key] = inside
            fiber_sizes[outside] += 1
    expected_fibers = 1 << (INPUT_BITS - local_mask.bit_count())
    expected_transcripts = 1 << local_mask.bit_count()
    if len(fiber_sizes) != expected_fibers:
        raise ValueError("conditional projection omitted an outside assignment")
    if any(size != expected_transcripts for size in fiber_sizes.values()):
        raise ValueError("conditional transcript has the wrong fiber size")
    return expected_fibers, expected_transcripts


def _side_info_violations(graph, ports, side_information):
    violations = []
    for receiver, known in zip(ports, side_information):
        for source in known:
            if receiver == source or graph[receiver] & (1 << source):
                violations.append((receiver, source))
    return violations


def _require_accounting(charge, floor):
    if charge < floor:
        raise ValueError("charged copied-information cost is below the certified floor")


def calculate(lines=None, graph=None, cliques=None):
    """Return deterministic JSON-compatible evidence for the finite controls.

    Inputs may be supplied by the complete geometry replay. ``cliques`` may
    contain all maximal cliques or just the 640 maximum cliques.
    """
    if not __debug__:
        raise ValueError("optimized Python is unsupported because retained geometry uses assertions")
    geometry = _load_geometry()
    expected_lines = geometry.gaussian_lines()
    lines = expected_lines if lines is None else tuple(lines)
    if lines != expected_lines:
        raise ValueError("controls require the pinned 60-line Gaussian E8 geometry")
    expected_graph = geometry.nonorthogonality(lines)
    graph = expected_graph if graph is None else tuple(graph)
    if graph != expected_graph:
        raise ValueError("nonorthogonality graph does not match retained geometry")
    all_cliques = geometry.maximal_cliques(graph) if cliques is None else tuple(cliques)
    maximum_cliques = tuple(sorted(c for c in all_cliques if c.bit_count() == 12))
    if len(maximum_cliques) != 640 or len(set(maximum_cliques)) != 640:
        raise ValueError("controls require all 640 distinct maximum cliques")
    for clique in maximum_cliques:
        members = tuple(port for port in range(60) if clique & (1 << port))
        if len(members) != 12 or any((clique ^ (1 << port)) & ~graph[port]
                                     for port in members):
            raise ValueError("invalid maximum nonorthogonality clique")

    frames, frame_count = _select_frames(graph)
    ports = tuple(port for frame in frames for port in frame)
    source_rank, reader_rank, pair_charge = _pair_charge(geometry, lines, ports, ports)
    if (source_rank, reader_rank, pair_charge) != (4, 4, 4):
        raise ValueError("nonlinear example does not span a full rank-four source and reader")
    side_information = tuple(tuple(port for port in frames[receiver // 4]
                                  if port != ports[receiver])
                             for receiver in range(INPUT_BITS))
    if _side_info_violations(graph, ports, side_information):
        raise ValueError("nonlinear example uses nonorthogonal side information")
    transcript = tuple(_encode(word) for word in range(INPUT_COUNT))
    failures, witness = _receiver_failures(transcript)
    if failures:
        raise ValueError("nonlinear receiver failed: " + json.dumps(witness, sort_keys=True))
    if len(set(transcript)) != 8:
        raise ValueError("the three-bit message must attain all eight output words")

    dependence_counts = []
    for variable in range(INPUT_BITS):
        count = sum(transcript[word] != transcript[word ^ (1 << variable)]
                    for word in range(INPUT_COUNT))
        if count != INPUT_COUNT:
            raise ValueError("message omitted an advertised source variable")
        dependence_counts.append(count)
    derivative_counts = Counter(transcript[word] ^ transcript[word ^ 1]
                                ^ transcript[word ^ 16] ^ transcript[word ^ 17]
                                for word in range(INPUT_COUNT))
    if derivative_counts != Counter({4: INPUT_COUNT}):
        raise ValueError("nonlinear second-difference witness is missing")

    intersection_counts, conditional_classes = Counter(), 0
    local_masks = []
    for clique in maximum_cliques:
        local_mask = sum(1 << i for i, port in enumerate(ports) if clique & (1 << port))
        local_masks.append(local_mask)
        intersection_counts[local_mask.bit_count()] += 1
        classes, _ = _conditional_projection(transcript, local_mask)
        conditional_classes += classes
    if max(intersection_counts) != 3:
        raise ValueError("expected a three-demand maximum-clique concentration")
    active_floor = (2 * len(ports) + 2) // 3
    correct_charge = 3 * pair_charge
    _require_accounting(correct_charge, active_floor)

    omitted_failures, omitted_witness = _receiver_failures(transcript, invert=False)
    if not omitted_failures:
        raise ValueError("negative control failed to detect omitted nonlinear inversion")
    three_demand_mask = next(mask for mask in local_masks if mask.bit_count() == 3)
    dropped_controls = []
    for bit in range(3):
        dropped = tuple(message & ~(1 << bit) for message in transcript)
        count, witness = _receiver_failures(dropped)
        if not count:
            raise ValueError("negative control failed to detect a dropped output bit")
        try:
            _conditional_projection(dropped, three_demand_mask)
        except ValueError as error:
            projection_error = str(error)
        else:
            raise ValueError("dropped-bit conditional collision was not detected")
        dropped_controls.append({"dropped_output_bit": bit, "detected": True,
                                 "receiver_failure_count": count, "witness": witness,
                                 "projection_rejection": projection_error})
    try:
        _require_accounting(pair_charge, active_floor)
    except ValueError as error:
        undercharge_error = str(error)
    else:
        raise ValueError("negative control failed to reject one charge for three output bits")

    illegal_clique = maximum_cliques[0]
    illegal_ports = tuple(port for port in range(60) if illegal_clique & (1 << port))
    illegal_side_info = tuple(tuple(port for port in illegal_ports if port != receiver)
                              for receiver in illegal_ports)
    illegal_violations = _side_info_violations(graph, illegal_ports, illegal_side_info)
    if len(illegal_violations) != 132:
        raise ValueError("illegal maximum-clique side-information control is incomplete")
    illegal_ranks = _pair_charge(geometry, lines, illegal_ports, illegal_ports)
    if illegal_ranks != (4, 4, 4):
        raise ValueError("illegal maximum-clique example has unexpected geometry")
    illegal_transcript = tuple(word.bit_count() % 2 for word in range(INPUT_COUNT))
    illegal_decodes = 0
    for word, parity in enumerate(illegal_transcript):
        for receiver in range(INPUT_BITS):
            mates = INPUT_MASK ^ (1 << receiver)
            decoded = parity ^ ((word & mates).bit_count() % 2)
            if decoded != (word >> receiver) & 1:
                raise ValueError("illegal-side-information parity decoder failed")
            illegal_decodes += 1
    try:
        _conditional_projection(illegal_transcript, INPUT_MASK)
    except ValueError as error:
        illegal_projection_error = str(error)
    else:
        raise ValueError("illegal-side-information transcript collision was not detected")

    return {
        "geometry_source": {"commit": GEOMETRY_COMMIT, "sha256": GEOMETRY_SHA256},
        "seed": SEED,
        "frame_search": {"orthogonal_frames": frame_count,
                         "selection": "seed44 shuffle of sorted four-line frames; first three disjoint"},
        "nonlinear_example": {
            "frames": [list(frame) for frame in frames], "source_ports": list(ports),
            "reader_ports": list(ports), "side_information": [list(known) for known in side_information],
            "side_information_checks": 36, "source_rank": source_rank, "reader_rank": reader_rank,
            "pairing_rank_charge": pair_charge, "output_bits": 3,
            "encoder": "three frame parities z0,z1,z2, then z2 ^= z0 & z1",
            "input_assignments": INPUT_COUNT, "receiver_decodes": INPUT_COUNT * INPUT_BITS,
            "distinct_message_words": len(set(transcript)), "cost": correct_charge,
            "active_demands": INPUT_BITS, "averaged_demand_floor": active_floor,
            "maximum_clique_demand_floor": max(intersection_counts),
            "source_dependence_counts": dependence_counts,
            "nonlinear_second_difference": {"source_local_indices": [0, 4],
                                            "nonzero_output_word": 4, "checks": INPUT_COUNT},
        },
        "conditional_transcript_projections": {
            "maximum_cliques": len(maximum_cliques),
            "input_assignments_per_clique": INPUT_COUNT,
            "assignment_checks": len(maximum_cliques) * INPUT_COUNT,
            "conditional_classes": conditional_classes,
            "active_intersection_census": {str(k): intersection_counts[k]
                                           for k in sorted(intersection_counts)},
            "injective": True,
        },
        "negative_controls": {
            "per_bit_charging": {"detected": True, "incorrect_one_message_charge": pair_charge,
                                 "correct_three_bit_charge": correct_charge,
                                 "certified_active_floor": active_floor, "rejection": undercharge_error},
            "omitted_nonlinear_inversion": {"detected": True,
                                            "receiver_failure_count": omitted_failures,
                                            "witness": omitted_witness},
            "dropped_output_bits": dropped_controls,
            "illegal_nonorthogonal_side_information": {
                "detected": True, "clique_ports": list(illegal_ports),
                "ordered_side_information_violations": len(illegal_violations),
                "first_violation": list(illegal_violations[0]),
                "output_bits": 1, "pairing_rank_charge": illegal_ranks[2],
                "cost": illegal_ranks[2], "active_demands": INPUT_BITS,
                "averaged_floor_if_orthogonality_held": active_floor,
                "clique_floor_if_orthogonality_held": INPUT_BITS,
                "input_assignments": INPUT_COUNT, "receiver_decodes": illegal_decodes,
                "conditional_projection_rejection": illegal_projection_error,
            },
        },
    }


if __name__ == "__main__":
    print(json.dumps(calculate(), indent=2, sort_keys=True))
