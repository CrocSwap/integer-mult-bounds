"""Exact, source-pinned frame and cost floor for one QQ16 private relay."""

from collections import Counter
from hashlib import sha256
import gzip
import json
from pathlib import Path


BASE = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
CERTIFICATE_SHA256 = "a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7"
PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
CERTIFICATE = ROOT / "research/joint-query/certificate.json.gz"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def bits(value):
    while value:
        bit = value & -value
        yield bit.bit_length() - 1
        value ^= bit


def act(columns, vector):
    result = 0
    for index in bits(vector):
        result ^= columns[index]
    return result


def canonical(entries):
    counts = Counter()
    for axis, coefficient in entries:
        counts[axis] = (counts[axis] + coefficient) % 4
    return tuple(sorted((axis, value) for axis, value in counts.items() if value))


def frame_entries(record):
    return canonical((int(axis), coefficient)
                     for axis, coefficient in record["line_terms_Z4"])


def output_frame(stage, port, label):
    """Y-port boundary frame: completed(stage) minus its port label."""
    entries = [(1 << index, 1) for index in range(9 + 8 * stage)]
    entries.append((label, -1))
    return canonical(entries)


def move_frame(frame, mapping):
    columns = mapping["owner_right_matrix_columns"]
    shift = mapping["payload_translation_at_identity_owner"]
    entries = [(act(columns, axis), coefficient) for axis, coefficient in frame]
    entries.extend((1 << index, 2) for index in bits(shift))
    return canonical(entries)


def unit_line_distance(frame):
    """Minimum +/-1 single-term Z4 edits needed to reach the zero frame."""
    return sum(min(coefficient, 4 - coefficient) for _, coefficient in frame)


def load_certificate(raw, expected_hash=CERTIFICATE_SHA256):
    need(sha256(raw).hexdigest() == expected_hash, "Pinned compressed certificate")
    return json.loads(gzip.decompress(raw))


def calculate(packet):
    need(packet["schema"] == "conserved-qq16-full-cover-native-words-v1",
         "Pinned QQ16 certificate schema")
    ports = packet["A_ports"]
    need(ports == [0, 7, 20, 27, 36, 46, 57, 111], "Exact eight A ports")
    program = packet["programs"]["B_1_2"]
    need(program[-1][:3] == ["retained_core", "backward", 1],
         "The B1_2 word ends at the backward stage-one cut")

    core = packet["core_words"]["backward"]
    for private in range(8):
        token = repr(["C", private])
        accesses = [(index, event) for index, event in enumerate(core)
                    if token in repr(event)]
        need(accesses, f"C{private} has a retained-core access")
        last = accesses[-1][1]
        need(last[0:2] == ["scalar", ["clear", ["C", private]]],
             f"C{private} is last cleared by the core")

    private_frame = frame_entries(packet["native_frame_registry"]["f0"])
    need(private_frame == (), "Private output frame is I")
    frames = packet["native_frame_registry"]
    maps = packet["map_registry"]
    need(len(maps) == 3650, "Complete pinned one-map search domain")

    outputs = []
    total_line_floor = 0
    map_hits = {}
    expected_frame_ids = ["f117", "f124", "f137", "f144",
                          "f153", "f163", "f174", "f228"]
    for port, expected_frame_id in zip(ports, expected_frame_ids):
        label = packet["native_line_recipes"][f"positive_{port}"]["label"]
        target = output_frame(1, port, label)
        need(target != private_frame, f"Y_A port {port} differs from private I")
        frame_ids = [name for name, record in frames.items()
                     if frame_entries(record) == target]
        need(frame_ids == [expected_frame_id],
             f"Exact registered frame for Y_A port {port}")
        need(len(target) == 18, f"Exactly 18 nonzero Z4 terms at Y_A port {port}")
        need(all(value in (1, 3) for _, value in target),
             f"Unit coefficients at Y_A port {port}")

        hits = [name for name, mapping in maps.items()
                if move_frame(target, mapping) == private_frame]
        map_hits[port] = hits
        need(not hits, f"No registered single map normalizes port {port}")
        distance = unit_line_distance(target)
        need(distance == 18, f"18 single-term line operations for port {port}")
        total_line_floor += distance
        outputs.append({"port": port, "frame": frame_ids[0],
                        "terms": len(target), "unit_line_distance": distance,
                        "single_map_hits": hits})

    # Positive controls: a zero frame stays zero under the identity map, and
    # one +/-1 edit cancels one Z4 term exactly.
    identity_hits = [name for name, mapping in maps.items()
                     if move_frame(private_frame, mapping) == private_frame]
    need(identity_hits, "Identity-map positive control")
    need(unit_line_distance(((17, 1),)) == 1, "Single-term line positive control")

    # A wrong stage or a wrong A-port label must not recreate the target frame.
    control_port = ports[0]
    control_label = packet["native_line_recipes"][f"positive_{control_port}"]["label"]
    wrong_stage = output_frame(0, control_port, control_label)
    wrong_port_label = packet["native_line_recipes"][f"positive_{ports[1]}"]["label"]
    wrong_port = output_frame(1, control_port, wrong_port_label)
    target = output_frame(1, control_port, control_label)
    need(wrong_stage != target, "Wrong-stage negative control")
    need(wrong_port != target, "Wrong-port negative control")

    scalar_add_unit_primitive_bound = 4  # 3 + 0 + 1 + 0 in the pinned scalar rule.
    copy_adds = len(ports)
    copy_primitive_bound = copy_adds * scalar_add_unit_primitive_bound
    cleanup_clears_if_terminal = len(ports)
    result = {
        "status": "PASS_QQ16_PRIVATE_DA_FRAME_FLOOR",
        "source_base": BASE,
        "certificate_sha256_compressed": CERTIFICATE_SHA256,
        "a_ports": outputs,
        "private_frame": "f0",
        "registered_maps_checked": len(maps),
        "single_map_hits": sum(len(v) for v in map_hits.values()),
        "rank_one_line_calls_lower_bound": total_line_floor,
        "cover_maps_at_two_per_line": 2 * total_line_floor,
        "copy_adds": copy_adds,
        "copy_add_real_primitive_bound": copy_primitive_bound,
        "terminal_cleanup_clear_macros": cleanup_clears_if_terminal,
        "terminal_cleanup_real_primitive_bound": cleanup_clears_if_terminal,
        "next_core_cleanup_extra_charge": 0,
        "observation_coordinates": len(ports),
        # Live candidate-budget comparator from Discussion #2074; this is not
        # computed from the pinned local QQ16 certificate.
        "favorable_extra_rank_one_credit_from_discussion_2074": 2,
        "comparison": "144 rank-one line calls exceed the two-call favorable slack before global hosting or address costs",
        "scope": "Eight A ports at B_1_2; all registered one-map normalizers and the one-term native-line conversion model only.",
        "controls": ["identity map", "single-term line cancellation",
                     "wrong stage rejected", "wrong port rejected",
                     "mutated source certificate rejected"],
        "no_kappa": True,
    }
    return result


def main():
    need(ROOT.is_dir(), "Repository root found from package path")
    raw = CERTIFICATE.read_bytes()
    packet = load_certificate(raw)
    result = calculate(packet)
    need(result["rank_one_line_calls_lower_bound"] >
         result["favorable_extra_rank_one_credit_from_discussion_2074"],
         "The bounded line mechanism fails the favorable call budget")
    print("PASS_QQ16_PRIVATE_DA_FRAME_FLOOR ports=8 frame_terms=18 "
          "single_map_hits=0 rank1_line_floor=144 cover_maps=288 "
          "scalar_add=32 no_kappa")


if __name__ == "__main__":
    main()
