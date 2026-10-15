#!/usr/bin/env python3
"""Code-disjoint event interpreter for the GF(4) dirty-state construction."""
from itertools import product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MULTIPLICATION = (
    (0, 0, 0, 0),
    (0, 1, 2, 3),
    (0, 2, 3, 1),
    (0, 3, 1, 2),
)


def require(ok, label):
    if not ok:
        raise SystemExit("FAIL_GF4_SCALAR_CONNECTOR_INDEPENDENT " + label)


def fmul(a, b):
    return MULTIPLICATION[a][b]


def execute(events, target_id, maps, inputs, connector, output):
    b0, b1, a_map = maps
    x0, x1 = inputs
    sources = (b0, b1)
    xs = (x0, x1)
    start = connector
    value = output
    for event in events:
        if event["kind"] == "source":
            j = event["source"]
            connector ^= fmul(event["alpha"], fmul(sources[j], xs[j]))
        elif event["target"] == target_id:
            value ^= fmul(a_map, connector)
    return connector, value, start


def main():
    cert = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    require(cert["format"] == "gf4-scalar-source-connector-v1", "format")
    events = cert["event_stream"]
    targets = cert["targets"]
    word = cert["source_word"]
    require(len(word) == 6 and len(events) == 36, "event counts")

    # Independently build prefix states from event labels using the two-bit
    # additive representation. Each pair is checked against its target row.
    q = [0, 0]
    states = [tuple(q)]
    for source_event in word:
        q[source_event["source"]] ^= source_event["alpha"]
        states.append(tuple(q))
    require(states[0] == states[-1] == (0, 0), "closed walk")
    require(len(set(states[:-1])) == 6, "distinct prefixes")
    differences = []
    for left in range(6):
        for right in range(left + 1, 6):
            differences.append((states[left][0] ^ states[right][0],
                                states[left][1] ^ states[right][1]))
    require(len(set(differences)) == 15, "difference uniqueness")
    require(set(differences) == {(u, v) for u in range(4) for v in range(4)
                                 if (u, v) != (0, 0)}, "difference coverage")
    for target in targets:
        left, right = target["boundaries"]
        got = (states[left][0] ^ states[right][0],
               states[left][1] ^ states[right][1])
        require(list(got) == target["coefficients"], "pair label")

    # Execute the literal interleaving over every length-one GF(4)-linear map,
    # source, dirty connector, and dirty target scalar. A_r, B0 and B1 are all
    # multiplication maps, which exhaust End_GF(4)(GF(4)).
    checked = 0
    for row in targets:
        u, v = row["coefficients"]
        for b0, b1, a_map, x0, x1, z_dirty, y_dirty in product(range(4), repeat=7):
            connector, output, initial = execute(
                events, row["target"], (b0, b1, a_map), (x0, x1), z_dirty, y_dirty)
            expected = y_dirty ^ fmul(a_map,
                                      fmul(u, fmul(b0, x0)) ^ fmul(v, fmul(b1, x1)))
            require(connector == initial, "arbitrary connector dirt")
            require(output == expected, "target output")
            checked += 1

    # Negative controls use concrete states: deleting the final source event
    # leaves z=w^2; moving row (1,0)'s second read from boundary 1 to 2 adds
    # the unwanted x1 term.
    shortened = [event for event in events
                 if not (event["kind"] == "source" and
                         event.get("after_boundary") == 5)]
    end, _, _ = execute(shortened, 0, (0, 1, 1), (0, 1), 0, 0)
    require(end == 3, "omitted-event control")
    row10 = next(row for row in targets if row["coefficients"] == [1, 0])
    corrupted = [event for event in events
                 if not (event["kind"] == "read" and event["target"] == row10["target"]
                         and event["boundary"] == 1)]
    # The bad second read is inserted at boundary 2, after source event 1.
    insert_at = next(i + 1 for i, event in enumerate(corrupted)
                     if event["kind"] == "source" and event.get("after_boundary") == 1)
    corrupted.insert(insert_at, {"kind": "read", "target": row10["target"],
                                 "boundary": 2})
    _, bad_output, _ = execute(corrupted, row10["target"], (0, 1, 1),
                               (0, 1), 0, 0)
    require(bad_output == 1, "misplaced-readout control")

    print("PASS_GF4_SCALAR_CONNECTOR_INDEPENDENT rows=15 pair_differences=15 "
          "dirty_states=%d omitted_source_and_misplaced_read_controls=2" % checked)


if __name__ == "__main__":
    main()
