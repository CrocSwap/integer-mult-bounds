# SPDX-License-Identifier: Apache-2.0
"""Reproduce the finite routing invoice and fresh literal event bindings."""

import argparse
import hashlib
import json
import tempfile
from pathlib import Path

import route
import source_events

HERE = Path(__file__).resolve().parent


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build():
    paired = source_events.load_pairscale()
    census, witnesses = [], {}
    for width in range(4, 257):
        row = {"width": width}
        for control in (False, True):
            label = "control" if control else "paired"
            gates = paired.circuit(width, 1, -1, [("neg", 0)], control=control)
            instructions = route.compile_route(width, gates)
            counts = route.counters(instructions)
            route.require(counts == route.expected_counts(width, control=control),
                          "complete route tariff: " + str((width, label)))
            row[label] = counts
            if width == 84:
                fixtures = []
                limit = 1 << (width - 1)
                for real, imag in ((0, 0), (7, -3), (-limit + 1, limit - 1), (-limit, -limit)):
                    result = route.execute(width, gates, real, imag)
                    route.require(result["components"] == ((-real) % (2 * limit), (-imag) % (2 * limit)),
                                  "complete modular endpoint")
                    route.require(result["counters"] == counts, "payload-independent physical invoice")
                    fixtures.append({"input": [real, imag], "result": result})
                witnesses[label] = {
                    "logical_gates": paired.s.counts(gates),
                    "gates_sha256": digest(gates),
                    "route_sha256": digest(instructions),
                    "route_instructions": len(instructions),
                    "counts": counts,
                    "total": sum(counts.values()),
                    "fixtures": fixtures,
                }
        census.append(row)
    try:
        paired.endpoint(84, 1, -1, -(1 << 83))
    except ValueError:
        pass
    else:
        raise ValueError("most-negative input must fail signed SCALE admission")
    with tempfile.TemporaryDirectory(prefix="paired-scale-routing-") as work:
        events = source_events.event_bindings(work)
    return {
        "status": "PASS_PAIRED_SCALE_LOCAL_TAPE_ROUTE_NO_SUPPLIER_ADMISSION",
        "contract": {
            "data_tapes": 2, "carry_tapes": 1, "clean_carry_bits": 1,
            "temporary_finite_control_bits": 2, "heads_return_to_origin": True,
            "scope": "compiled local split-component layout; one coordinate of native SCALE",
            "entry_acquisition_and_whole_role_cardinality": "not supplied",
        },
        "native_event_bindings": events,
        "width_census": {"minimum": 4, "maximum": 256, "streams": 2 * len(census),
                         "all_counts_sha256": digest(census)},
        "at_width_84": witnesses,
        "saving_at_84": {k: witnesses["control"]["counts"][k] - witnesses["paired"]["counts"][k]
                         for k in ("moves", "reads", "writes")},
        "signed_guard_control": "most-negative input rejected by inherited endpoint guard",
        "unrun": ["full inherited capacity/scalar-layer replay", "selected cold-chain replay",
                  "uniform encoded-width controller", "physical next ADD consumer"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print regenerated receipt without writing package files")
    args = parser.parse_args()
    result = build()
    # Normalize tuples exactly as the retained JSON receipt does.
    result = json.loads(json.dumps(result))
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        route.require(result == json.loads((HERE / "RESULT.json").read_text()), "complete receipt equality")
        print("PASS_PAIRED_SCALE_LOCAL_TAPE_ROUTE 506 routes; W84 paired 14508 vs control 24568")


if __name__ == "__main__":
    main()
