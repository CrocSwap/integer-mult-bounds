#!/usr/bin/env python3
"""Check heterogeneous paired-output packetization and its dirty-state contract."""
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "universal-connector-boundary" / "CERTIFICATE.json"
SOURCE_SHA256 = "e733746ba3e5151c829b4e8728bfff5ae3ed24d8d203eb77c735d20758e8266a"
FIVE_WORD = [0, 1, 2, 0, 3, 1, 4, 2, 3, 4]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def prefix_states(word):
    states = [0]
    for label in word:
        states.append(states[-1] ^ (1 << label))
    return states


def endpoints(word, masks):
    states = prefix_states(word)
    result = {}
    for mask in masks:
        found = next(((i, j) for i in range(len(states))
                      for j in range(i + 1, len(states))
                      if states[i] ^ states[j] == mask), None)
        need(found is not None, f"mask {mask} has no paired readout")
        result[mask] = found
    return result


def pair_count(counts):
    total = sum(counts.values())
    return min(total // 2, total - max(counts.values(), default=0))


def maximum_pairs(counts):
    """Return a maximum matching in a complete graph with colored vertices."""
    remaining = Counter(counts)
    pairs = []
    while True:
        live = [label for label, count in remaining.items() if count]
        if len(live) < 2:
            break
        live.sort(key=lambda label: (-remaining[label], label))
        left, right = live[:2]
        pairs.append(tuple(sorted((left, right))))
        remaining[left] -= 1
        remaining[right] -= 1
    need(len(pairs) == pair_count(counts), "pair matching is not maximum")
    return sorted(pairs)


def boundary_targets(readout_slots):
    slots = [Counter() for _ in range(max(max(x) for x in readout_slots) + 1)]
    for target, endpoints_ in enumerate(readout_slots):
        for boundary in endpoints_:
            slots[boundary][target] += 1
    return slots


def make_packets(slots):
    packets = []
    for counts in slots:
        pairs = maximum_pairs(counts)
        used = Counter(label for pair in pairs for label in pair)
        singles = []
        for target, count in sorted(counts.items()):
            singles.extend([target] * (count - used[target]))
        packets.append([("P", left, right) for left, right in pairs]
                       + [("A", target) for target in singles])
    return packets


def validate_packets(packets, slots):
    need(len(packets) == len(slots), "packet boundary count mismatch")
    for boundary, (events, expected) in enumerate(zip(packets, slots)):
        observed = Counter()
        for event in events:
            if event[0] == "A":
                need(len(event) == 2, f"malformed singleton at boundary {boundary}")
                observed[event[1]] += 1
            elif event[0] == "P":
                need(len(event) == 3, f"malformed pair at boundary {boundary}")
                left, right = event[1:]
                need(left != right, "paired targets must be distinct")
                observed[left] += 1
                observed[right] += 1
            else:
                raise ValueError(f"unknown output event {event[0]}")
        need(observed == expected,
             f"boundary {boundary} output inventory mismatch: {observed} != {expected}")


def expand_packets(packets):
    expanded = []
    for events in packets:
        row = []
        for event in events:
            if event[0] == "A":
                row.append(("A", event[1]))
            elif event[0] == "P":
                row.extend(("A", target) for target in event[1:])
            else:
                raise ValueError(f"unknown output event {event[0]}")
        expanded.append(sorted(row, key=lambda event: event[1]))
    return expanded


def scalar_replay(events, source_masks, b_maps, a_maps, sources, connector, targets):
    """One-bit F2 interpreter; event tuples are B, A or P."""
    z = connector
    ys = list(targets)
    for event in events:
        if event[0] == "B":
            j = event[1]
            z ^= b_maps[j] & sources[j]
        elif event[0] == "A":
            i = event[1]
            ys[i] ^= a_maps[i] & z
        elif event[0] == "P":
            i, k = event[1:]
            need(i != k, "paired targets must be distinct")
            ys[i] ^= a_maps[i] & z
            ys[k] ^= a_maps[k] & z
        else:
            raise ValueError(f"unknown scalar event {event[0]}")
    expected = list(targets)
    for i, mask in enumerate(source_masks):
        signal = 0
        for j in range(len(sources)):
            if mask & (1 << j):
                signal ^= b_maps[j] & sources[j]
        expected[i] ^= a_maps[i] & signal
    return z, ys, expected


def flatten_at_boundaries(packets, source_word):
    events = []
    for boundary, outputs in enumerate(packets):
        events.extend(outputs)
        if boundary < len(source_word):
            events.append(("B", source_word[boundary]))
    return events


def build_certificate(certificate):
    item = certificate["schedules"]["five_extra_output"]
    slots = boundary_targets(item["readout_slots"])
    packets = make_packets(slots)
    five_events = []
    for boundary, outputs in enumerate(packets):
        five_events.append({"boundary": boundary,
                            "events": [list(event) for event in outputs]})

    small_word = [0, 1, 0, 1]
    small_masks = [1, 2, 3]
    small_ends = endpoints(small_word, small_masks)
    small_slots = boundary_targets([list(small_ends[m]) for m in small_masks])
    small_packets = make_packets(small_slots)
    small_events = []
    for boundary, outputs in enumerate(small_packets):
        small_events.append({"boundary": boundary,
                             "events": [list(event) for event in outputs]})

    readouts = sum(sum(counts.values()) for counts in slots)
    pair_count_ = sum(event[0] == "P" for events in packets for event in events)
    singleton_count = sum(event[0] == "A" for events in packets for event in events)
    source_events = len(item["source_word"])
    return {
        "schema": "heterogeneous-output-pair-v1",
        "source": {
            "path": "research/universal-connector-boundary/CERTIFICATE.json",
            "sha256": SOURCE_SHA256,
        },
        "operation": "AP(i,k,z): y_i += A_i z; y_k += A_k z",
        "contract": "distinct targets; arbitrary independent binary-linear A maps; arbitrary dirty connector and targets; both A child evaluations and writes are paid",
        "small_fixture": {
            "source_word": small_word,
            "prefix_states": prefix_states(small_word),
            "output_masks": small_masks,
            "readout_slots": [list(small_ends[m]) for m in small_masks],
            "events_by_boundary": small_events,
            "root_events_including_sources": len(small_word) + sum(
                len(events) for events in small_packets),
        },
        "five_source_fixture": {
            "source_word": item["source_word"],
            "prefix_states": prefix_states(item["source_word"]),
            "output_masks": item["rows"],
            "target_id_to_mask": list(range(1, 32)),
            "readout_slots": item["readout_slots"],
            "events_by_boundary": five_events,
            "source_events": source_events,
            "paired_output_events": pair_count_,
            "singleton_output_events": singleton_count,
            "output_map_evaluations_and_target_writes": readouts,
            "root_events": source_events + pair_count_ + singleton_count,
            "complete_map_child_calls": source_events + readouts,
        },
        "descriptor_model": {
            "event_tag_bits": 2,
            "tag_codes": {"B": "00", "A": "01", "AP": "10"},
            "source_id_bits": 3,
            "output_id_bits": 5,
            "unpaired_bits": source_events * 5 + readouts * 7,
            "paired_bits": source_events * 5 + singleton_count * 7 + pair_count_ * 12,
        },
        "complete_cost_delta": "29 * (d_pair - 2*d_A - 2*s)",
        "definitions": {
            "s": "fully charged stored/read descriptor-bit cost",
            "d_A": "ordinary top-level output-event dispatch cost",
            "d_pair": "pair-event dispatch, decode, routing and transitions, excluding its 12 descriptor bits and its two complete A children",
        },
        "break_even": "d_pair < 2*d_A + 2*s",
        "scope": "finite connector interface construction; no selected supplier or kappa claim",
    }


def expect_reject(label, thunk):
    try:
        thunk()
    except (AssertionError, ValueError):
        return
    raise ValueError(f"negative control accepted: {label}")


def main():
    source_bytes = SOURCE.read_bytes()
    need(hashlib.sha256(source_bytes).hexdigest() == SOURCE_SHA256,
         "source certificate hash mismatch")
    certificate = json.loads(source_bytes)
    expected_package_certificate = build_certificate(certificate)
    package_certificate = json.loads((ROOT / "CERTIFICATE.json").read_text())
    need(package_certificate == expected_package_certificate,
         "package certificate differs from the recomputed pinned schedule")
    item = certificate["schedules"]["five_extra_output"]
    need(item["source_word"] == FIVE_WORD, "pinned five-source word changed")
    need(Counter(FIVE_WORD) == Counter({j: 2 for j in range(5)}),
         "each source map must occur exactly twice")
    need(item["queries"] == 74, "pinned source query total changed")
    need(certificate["lowered"]["five_extra_output"]["leaf_calls"] == 182,
         "pinned lowered leaf total changed")

    # Smallest meaningful instance: all three nonzero masks on n=2.
    small_word = [0, 1, 0, 1]
    small_masks = [1, 2, 3]
    small_ends = endpoints(small_word, small_masks)
    need(small_ends == {1: (0, 1), 2: (0, 3), 3: (0, 2)},
         "n=2 endpoint fixture changed")
    small_slots = boundary_targets([list(small_ends[m]) for m in small_masks])
    small_packets = make_packets(small_slots)
    validate_packets(small_packets, small_slots)
    small_events = flatten_at_boundaries(small_packets, small_word)
    need(sum(e[0] == "P" for e in small_events) == 1,
         "n=2 fixture must use one paired output event")
    need(len(small_events) == 9, "n=2 event count mismatch")

    # Exhaust every scalar linear map and every dirty/input bit in n=2.
    scalar_cases = 0
    for b0 in range(2):
        for b1 in range(2):
            for a0 in range(2):
                for a1 in range(2):
                    for a2 in range(2):
                        for x0 in range(2):
                            for x1 in range(2):
                                for z0 in range(2):
                                    for y0 in range(2):
                                        for y1 in range(2):
                                            for y2 in range(2):
                                                z, ys, expected = scalar_replay(
                                                    small_events, small_masks,
                                                    [b0, b1], [a0, a1, a2],
                                                    [x0, x1], z0, [y0, y1, y2])
                                                need(z == z0, "small dirty connector not restored")
                                                need(ys == expected, "small arbitrary-dirty map identity failed")
                                                scalar_cases += 1
    need(scalar_cases == 2048, "scalar exhaustive domain incomplete")

    # Max-cardinality grouping on the pinned 31-output schedule.
    need(item["rows"] == list(range(1, 32)), "output mask set changed")
    need(all(len(slot) in (2, 4) for slot in item["readout_slots"]),
         "base outputs must have paired readouts")
    need(Counter(map(len, item["readout_slots"])) == Counter({2: 30, 4: 1}),
         "expected 30 two-read outputs and one four-read output")
    for row, slot in zip(item["rows"], item["readout_slots"]):
        states = prefix_states(FIVE_WORD)
        value = 0
        for boundary in slot:
            value ^= states[boundary]
        need(value == row, f"row {row} endpoint difference mismatch")
    slots = boundary_targets(item["readout_slots"])
    packets = make_packets(slots)
    validate_packets(packets, slots)
    expanded = expand_packets(packets)
    canonical_original = [sorted(("A", target) for target, ends in enumerate(item["readout_slots"])
                                 if boundary in ends)
                          for boundary in range(len(slots))]
    need(expanded == canonical_original, "paired packets do not expand to the exact readout schedule")
    pairs = sum(event[0] == "P" for events in packets for event in events)
    singles = sum(event[0] == "A" for events in packets for event in events)
    readouts = sum(len(events) for events in canonical_original)
    source_events = len(FIVE_WORD)
    root_events = source_events + pairs + singles
    child_calls = source_events + readouts
    need((pairs, singles, readouts, root_events, child_calls) == (29, 6, 64, 45, 74),
         "five-source packet inventory changed")

    # Meaningful corruptions: omission, moving a pair across a boundary, and aliasing.
    omitted = [list(events) for events in packets]
    omitted[0].pop(0)
    expect_reject("omitted output", lambda: validate_packets(omitted, slots))
    moved = [list(events) for events in packets]
    pair = next(event for event in moved[0] if event[0] == "P")
    moved[0].remove(pair)
    moved[1].append(pair)
    expect_reject("wrong boundary", lambda: validate_packets(moved, slots))
    aliased = [list(events) for events in packets]
    aliased[0][0] = ("P", 0, 0)
    expect_reject("aliased targets", lambda: validate_packets(aliased, slots))

    # Fixed-width instruction invoice: 2-bit event tag, 3-bit B ID, 5-bit A ID.
    unpaired_bits = source_events * (2 + 3) + readouts * (2 + 5)
    paired_bits = source_events * (2 + 3) + singles * (2 + 5) + pairs * (2 + 10)
    need((unpaired_bits, paired_bits, unpaired_bits - paired_bits) == (498, 440, 58),
         "fixed-width descriptor invoice changed")
    print(
        "PASS_HETEROGENEOUS_OUTPUT_PAIR "
        f"n2_scalar_cases={scalar_cases} n2_events={len(small_events)} "
        f"five_source_pairs={pairs} singles={singles} root_events={root_events} "
        f"child_calls={child_calls} descriptor_bits={unpaired_bits}->{paired_bits}"
    )


if __name__ == "__main__":
    main()
