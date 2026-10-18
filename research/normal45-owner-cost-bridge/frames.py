# SPDX-License-Identifier: Apache-2.0
"""Independent finite frame invoice using explicit subsets of GF(2)^9.

No supplier, predecessor auditor, frame solver, or owner ledger is imported.
analyze() is a pure, read-only operation on a decoded BORROW-WORD dictionary.
See FRAMES-PROOF.md for the contract, attribution, and excluded claims.
"""

from collections import Counter
from fractions import Fraction
from functools import lru_cache
import gzip
import json
from pathlib import Path


H, V, R = 9, 112, 480
N, FIRST_HELPER = 2 * V + R, 2 * V
FULL = frozenset(range(1 << H))
ZERO = frozenset({0})
FIELDS = {
    "A", "B", "base", "center_frames", "centers", "compensation", "cut",
    "helper_final", "initial_corrections", "kind", "ports", "precondition",
    "prelude_events", "removed", "report", "restore", "start_extra",
    "target_levels", "warps", "cleanup",
}


class FrameError(ValueError):
    """An explicit failed predicate; remains active under Python -O."""

    def __init__(self, predicate, detail):
        self.predicate = predicate
        self.detail = detail
        super().__init__(f"{predicate}: {detail}")


def _need(ok, predicate, detail):
    if not ok:
        raise FrameError(predicate, detail)


def _integer(x, where, low=None, high=None):
    _need(type(x) is int, "primitive_schema", f"{where}: integer required")
    _need(low is None or x >= low, "primitive_schema", f"{where}: below {low}")
    _need(high is None or x <= high, "primitive_schema", f"{where}: above {high}")
    return x


def _list(x, where):
    _need(type(x) is list, "primitive_schema", f"{where}: list required")
    return x


@lru_cache(maxsize=8192)
def _closure(generators):
    points = {0}
    for generator in generators:
        points.update(point ^ generator for point in tuple(points))
    return frozenset(points)


def _span(generators, where):
    _list(generators, where)
    for i, generator in enumerate(generators):
        _integer(generator, f"{where}[{i}]", 0, 511)
    result = _closure(tuple(sorted(set(generators))))
    size = len(result)
    _need(size > 0 and size & (size - 1) == 0,
          "subspace_cardinality", where)
    return result


def _dimension(points):
    return len(points).bit_length() - 1


def _frame_map(mapping, where, low, high):
    _need(type(mapping) is dict, "primitive_schema", f"{where}: dictionary required")
    result = {}
    for key, value in mapping.items():
        _need(type(key) is str and key.isascii() and key.isdigit(),
              "primitive_schema", f"{where}: decimal string key required")
        index = int(key)
        _need(str(index) == key, "primitive_schema", f"{where}: noncanonical key {key}")
        _integer(index, f"{where}.{key}", low, high)
        result[index] = _span(value, f"{where}.{key}")
    return result


def _inventory(mapping, where, minimum):
    _need(type(mapping) is dict, "primitive_schema", f"{where}: dictionary required")
    parsed = {}
    for key, count in mapping.items():
        _need(type(key) is str and key.isascii() and key.isdigit(),
              "primitive_schema", f"{where}: decimal string key required")
        rank = int(key)
        _need(str(rank) == key, "primitive_schema", f"{where}: noncanonical rank")
        _integer(rank, where, minimum, H)
        _integer(count, f"{where}.{key}", 1)
        parsed[rank] = count
    return parsed


def _linear_image(points, columns):
    def image(point):
        result = 0
        for i, column in enumerate(columns):
            if point & (1 << i):
                result ^= column
        return result
    return frozenset(map(image, points))


def _scalar(gate, where, register, mode):
    _list(gate, where)
    _need(bool(gate) and gate[0] in ("add", "scale"),
          "primitive_schema", f"{where}: scalar gate tag")
    expected = 6 if gate[0] == "add" else 5
    _need(len(gate) == expected, "primitive_schema", f"{where}: scalar gate arity")
    register(gate[1], where)
    if gate[0] == "add":
        register(gate[2], where)
        _need(gate[1] != gate[2], "primitive_schema", f"{where}: self-add")
        numerator, denominator = gate[3:5]
    else:
        numerator, denominator = gate[2:4]
    _integer(numerator, where)
    _integer(denominator, where)
    _need(numerator != 0 and denominator != 0 and
          abs(denominator) & (abs(denominator) - 1) == 0,
          "primitive_schema", f"{where}: nonzero dyadic scalar required")
    if mode == "cut":
        _need(gate[-1] is None, "primitive_schema", f"{where}: cut frame must be null")
    else:
        frame = _span(gate[-1], f"{where}.frame")
        if mode == "cleanup":
            _need(frame == FULL, "cleanup_frame", where)
        elif mode == "zero":
            _need(frame == ZERO, "primitive_schema", f"{where}: expected zero frame")


def analyze(word):
    """Validate and reconstruct the fixed h=9, v=112, R=480 frame invoice.

    Returns integer-keyed histograms and widths in sorted live-helper order.
    This does not evaluate the dyadic/free operator or prove buffer zero return.
    """
    _need(type(word) is dict and set(word) == FIELDS, "primitive_schema", "word fields")
    _need(word["kind"] == "BORROW-WORD" and type(word["base"]) is str,
          "primitive_schema", "word kind/base")
    report = word["report"]
    _need(type(report) is dict and set(report) == {
        "R", "h", "v", "local_profile", "width_inventory"},
        "primitive_schema", "report fields")
    for key, expected in (("h", H), ("v", V), ("R", R)):
        _integer(report[key], f"report.{key}")
        _need(report[key] == expected, "covered_domain", f"report.{key} != {expected}")
    declared_profile = _inventory(report["local_profile"], "report.local_profile", 1)
    declared_widths = _inventory(report["width_inventory"], "report.width_inventory", 0)

    ports = _list(word["ports"], "ports")
    for port in ports:
        _integer(port, "ports", 1, 511)
    _need(len(ports) == V and len(set(ports)) == V, "primitive_schema", "112 distinct ports")
    removed_values = _list(word["removed"], "removed")
    for register_id in removed_values:
        _integer(register_id, "removed", FIRST_HELPER, N - 1)
    removed = set(removed_values)
    _need(len(removed) == len(removed_values), "primitive_schema", "duplicate removed register")
    live = set(range(N)) - removed

    def live_register(register_id, where):
        _integer(register_id, where, 0, N - 1)
        _need(register_id in live, "primitive_schema", f"{where}: removed register {register_id}")

    starts = _frame_map(word["start_extra"], "start_extra", FIRST_HELPER, N - 1)
    finals = _frame_map(word["helper_final"], "helper_final", FIRST_HELPER, N - 1)
    targets = _frame_map(word["target_levels"], "target_levels", 0, V - 1)
    _need(set(starts) <= live and set(finals) <= live,
          "primitive_schema", "removed helper has boundary override")
    entrance = [_span([port], "port entrance") for port in ports] + [ZERO] * (V + R)
    terminal = [FULL] * V + [frozenset(
        point for point in range(512) if (point & port).bit_count() % 2 == 0
    ) for port in ports] + [FULL] * R
    for register_id, frame in starts.items():
        entrance[register_id] = frame
    for register_id, frame in finals.items():
        terminal[register_id] = frame

    for section in ("A", "B", "restore", "precondition", "compensation", "cut", "cleanup", "warps"):
        _list(word[section], section)
    _integer(word["prelude_events"], "prelude_events", 0, len(word["A"]))
    warp_maps = []
    for i, warp in enumerate(word["warps"]):
        where = f"warps[{i}]"
        _list(warp, where)
        _need(len(warp) == 5, "primitive_schema", f"{where}: arity")
        _integer(warp[0], where, 0, len(word["B"]))
        live_register(warp[1], where)
        columns = _list(warp[2], where)
        _need(len(columns) == H and _span(columns, where) == FULL,
              "warp_invertibility", where)
        before, after = _span(warp[3], where), _span(warp[4], where)
        _need(_linear_image(before, columns) == after, "warp_map", where)
        warp_maps.append(columns)

    def warp_reference(operator_id, where):
        _integer(operator_id, where)
        _need(0 < abs(operator_id) <= len(warp_maps),
              "primitive_schema", f"{where}: unknown signed warp")

    for section in ("A", "B", "restore", "precondition", "compensation", "cut"):
        mode = "cut" if section == "cut" else "zero" if section in ("precondition", "compensation") else "normal"
        for i, gate in enumerate(word[section]):
            where = f"{section}[{i}]"
            _list(gate, where)
            if gate and gate[0] == "warp":
                _need(section == "A" and len(gate) == 5,
                      "primitive_schema", f"{where}: warp placement/arity")
                live_register(gate[1], where)
                warp_reference(gate[2], where)
                before, after = _span(gate[3], where), _span(gate[4], where)
                left, right = (before, after) if gate[2] > 0 else (after, before)
                _need(_linear_image(left, warp_maps[abs(gate[2]) - 1]) == right,
                      "warp_map", where)
            else:
                _scalar(gate, where, live_register, mode)

    expected_buffers = {N + helper for helper in finals}
    observed_buffers = set()

    def cleanup_register(register_id, where):
        _integer(register_id, where, 0, 2 * N - 1)
        if register_id >= N:
            observed_buffers.add(register_id)
        else:
            live_register(register_id, where)

    for i, gate in enumerate(word["cleanup"]):
        where = f"cleanup[{i}]"
        _list(gate, where)
        if gate and gate[0] == "warp":
            _need(len(gate) == 4, "primitive_schema", f"{where}: warp arity")
            cleanup_register(gate[1], where)
            warp_reference(gate[2], where)
            _need(_span(gate[3], where) == FULL, "cleanup_frame", where)
        else:
            _scalar(gate, where, cleanup_register, "cleanup")
    _need(observed_buffers == expected_buffers, "cleanup_namespace", {
        "missing": sorted(expected_buffers - observed_buffers),
        "unexpected": sorted(observed_buffers - expected_buffers),
    })

    # Reconstruct inverse-reverse syntax independently; the prelude is excluded
    # by this supplier's cleanup convention. This is not a buffer-zero proof.
    forward = list(word["A"][word["prelude_events"]:])
    forward_warps = {}
    for i, warp in enumerate(word["warps"], 1):
        forward_warps.setdefault(warp[0], []).append(["warp", warp[1], i])
    for position in range(len(word["B"]) + 1):
        forward.extend(forward_warps.get(position, ()))
        if position < len(word["B"]):
            forward.append(word["B"][position])
    forward.extend(word["restore"])

    def name(register_id):
        return N + register_id if register_id in finals else register_id

    def normalized(gate):
        if gate[0] == "warp":
            return tuple(gate[:3])
        if gate[0] == "add":
            return ("add", gate[1], gate[2], Fraction(gate[3], gate[4]))
        return ("scale", gate[1], Fraction(gate[2], gate[3]))

    expected_cleanup = []
    for gate in reversed(forward):
        if V <= gate[1] < 2 * V:
            continue
        if gate[0] == "warp":
            expected_cleanup.append(("warp", name(gate[1]), -gate[2]))
        elif gate[0] == "add":
            expected_cleanup.append(("add", name(gate[1]), name(gate[2]),
                                     -Fraction(gate[3], gate[4])))
        else:
            expected_cleanup.append(("scale", name(gate[1]), Fraction(gate[3], gate[2])))
    observed_cleanup = list(map(normalized, word["cleanup"]))

    corrections = _list(word["initial_corrections"], "initial_corrections")
    for i, correction in enumerate(corrections):
        where = f"initial_corrections[{i}]"
        _need(type(correction) is dict and set(correction) == {
            "coefficient", "operator_word", "source", "target"}, "primitive_schema", where)
        live_register(correction["source"], where)
        live_register(correction["target"], where)
        _need(type(correction["coefficient"]) is str, "primitive_schema", where)
        try:
            coefficient = Fraction(correction["coefficient"])
        except (ValueError, ZeroDivisionError) as error:
            raise FrameError("primitive_schema", where) from error
        _need(coefficient != 0 and coefficient.denominator & (coefficient.denominator - 1) == 0,
              "primitive_schema", f"{where}: nonzero dyadic correction")
        for operator_id in _list(correction["operator_word"], where):
            warp_reference(operator_id, where)

    centers = _list(word["centers"], "centers")
    center_frames = _list(word["center_frames"], "center_frames")
    _need(len(centers) == len(center_frames), "primitive_schema", "center/frame lengths")
    for center in centers:
        live_register(center, "centers")
    _need(len(set(centers)) == len(centers), "primitive_schema", "duplicate center")
    for i, gate in enumerate(word["cut"]):
        _need(gate[0] == "add" and V <= gate[1] < 2 * V and gate[2] in centers,
              "primitive_schema", f"cut[{i}]: target/center contract")

    current = entrance.copy()
    paid = Counter()
    stage_profiles = {stage: Counter() for stage in ("A", "centers", "B", "restore", "endpoints")}
    climb_attempts = Counter()
    warp_checks = Counter()
    center_descents = 0

    def charge(rank, stage):
        if rank:
            _need(1 <= rank <= H, "paid_rank", (stage, rank))
            paid[rank] += 1
            stage_profiles[stage][rank] += 1

    def climb(register_id, frame, stage, where):
        climb_attempts[stage] += 1
        _need(current[register_id] <= frame, "frame_containment", {
            "where": where, "register": register_id,
            "old_dimension": _dimension(current[register_id]),
            "new_dimension": _dimension(frame),
        })
        charge(_dimension(frame) - _dimension(current[register_id]), stage)
        current[register_id] = frame

    def step(gate, stage, where):
        if gate[0] == "warp":
            before, after = _span(gate[3], where), _span(gate[4], where)
            _need(current[gate[1]] == before, "warp_frame", where)
            current[gate[1]] = after
            warp_checks[stage] += 1
        else:
            frame = _span(gate[-1], where)
            for register_id in (gate[1:3] if gate[0] == "add" else gate[1:2]):
                climb(register_id, frame, stage, where)

    for i, gate in enumerate(word["A"]):
        step(gate, "A", f"A[{i}]")
    for i, (center, generators) in enumerate(zip(centers, center_frames)):
        frame = _span(generators, f"center_frames[{i}]")
        _need(current[center] == frame, "center_frame", center)
        levels = {targets.get(gate[1] - V, ZERO) for gate in word["cut"] if gate[2] == center}
        for level in sorted(levels, key=lambda value: (-len(value), tuple(sorted(value)))):
            _need(level <= frame, "center_descent", center)
            if frame != level:
                charge(_dimension(frame) - _dimension(level), "centers")
                center_descents += 1
            frame = level
        # These are the cut's separate descent invoice, not the B register frame.
    scheduled = {}
    for i, warp in enumerate(word["warps"]):
        scheduled.setdefault(warp[0], []).append((i, warp))
    for position in range(len(word["B"]) + 1):
        for i, warp in scheduled.get(position, ()):
            _need(current[warp[1]] == _span(warp[3], f"warps[{i}]"),
                  "warp_frame", f"warps[{i}]")
            current[warp[1]] = _span(warp[4], f"warps[{i}]")
            warp_checks["B"] += 1
        if position < len(word["B"]):
            step(word["B"][position], "B", f"B[{position}]")
    for i, gate in enumerate(word["restore"]):
        step(gate, "restore", f"restore[{i}]")
    for register_id in sorted(live):
        climb(register_id, terminal[register_id], "endpoints", f"endpoint[{register_id}]")
    _need(all(current[register_id] == terminal[register_id] for register_id in live),
          "endpoint_coverage", "every live endpoint")
    _need(observed_cleanup == expected_cleanup, "cleanup_inverse_syntax", {
        "expected_length": len(expected_cleanup), "observed_length": len(observed_cleanup),
        "first_mismatch": next((i for i, pair in enumerate(zip(expected_cleanup, observed_cleanup))
                                if pair[0] != pair[1]), None),
    })

    helper_ids = sorted(register_id for register_id in live if register_id >= FIRST_HELPER)
    widths = [_dimension(terminal[helper]) - _dimension(entrance[helper]) for helper in helper_ids]
    _need(all(0 <= width <= H for width in widths), "helper_width", widths)
    width_inventory = dict(sorted(Counter(widths).items()))
    profile = dict(sorted(paid.items()))
    paid_rank_mass = sum(rank * count for rank, count in profile.items())
    center_mass = sum(rank * count for rank, count in stage_profiles["centers"].items())
    boundary_mass = sum(_dimension(terminal[register_id]) - _dimension(entrance[register_id])
                        for register_id in live)
    _need(paid_rank_mass == boundary_mass + center_mass,
          "rank_mass_telescoping", (paid_rank_mass, boundary_mass, center_mass))
    _need(profile == declared_profile, "declared_profile", {"computed": profile, "declared": declared_profile})
    _need(width_inventory == declared_widths, "declared_width_inventory", {
        "computed": width_inventory, "declared": declared_widths})
    return {
        "profile": profile,
        "paid_events": sum(profile.values()),
        "paid_rank_mass": paid_rank_mass,
        "boundary_rank_mass": boundary_mass,
        "center_descent_rank_mass": center_mass,
        "widths": widths,
        "helper_width_sum": sum(widths),
        "helper_ids": helper_ids,
        "buffer_count": len(observed_buffers),
        "buffer_ids": sorted(observed_buffers),
        "buffer_helpers": sorted(finals),
        "width_inventory": width_inventory,
        "live_count": len(live),
        "helper_count": len(helper_ids),
        "removed_count": len(removed),
        "endpoint_count": len(live),
        "endpoint_paid_climbs": sum(stage_profiles["endpoints"].values()),
        "stage_profiles": {stage: dict(sorted(counter.items())) for stage, counter in stage_profiles.items()},
        "climb_attempts": dict(climb_attempts),
        "warp_checks": dict(warp_checks),
        "center_count": len(centers),
        "center_descents": center_descents,
        "cleanup_gates": len(word["cleanup"]),
        "cleanup_inverse_syntax_checked": True,
        "cleanup_warps": sum(gate[0] == "warp" for gate in word["cleanup"]),
        "section_gate_counts": {section: len(word[section]) for section in (
            "A", "B", "restore", "cut", "compensation", "precondition", "cleanup")},
        "section_primitive_counts": {section: dict(sorted(Counter(
            gate[0] for gate in word[section]).items())) for section in (
            "A", "B", "restore", "cut", "compensation", "precondition", "cleanup")},
        "helper_entrance_dimensions": [_dimension(entrance[helper]) for helper in helper_ids],
        "helper_terminal_dimensions": [_dimension(terminal[helper]) for helper in helper_ids],
    }


def main():
    inputs = Path(__file__).resolve().parent / "inputs"
    reports = {}
    for stem in ("WORD-base", "WORD-extra", "PARENT-base", "PARENT-extra"):
        word = json.loads(gzip.decompress((inputs / f"{stem}.json.gz").read_bytes()))
        report = analyze(word)
        reports[stem] = {key: value for key, value in report.items()
                         if key not in {"widths", "helper_ids", "buffer_ids", "buffer_helpers",
                                        "helper_entrance_dimensions", "helper_terminal_dimensions"}}
    print(json.dumps(reports, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
