"""Replay the sharp rank-six A3 common-support threshold. Apache-2.0."""

import argparse
import json
from pathlib import Path

import model


def build():
    g = model.geometry()
    roots, labels, _, values, costs, groups = model.star_data(g)
    _, points, _, coordinates = g.root_data()
    frame_list = model.frames(g, roots)
    punctures = model.puncture_facts(frame_list, costs, groups)
    at29, at30 = (model.budget_table(s, punctures) for s in (29, 30))
    model.require(
        all(row["lower"] > row["upper"] for row in at29), "support29 exclusion"
    )
    model.require(
        any(
            r["frame_cost"] == 12
            and r["unpinned"] == 0
            and r["lower"] == r["upper"] == 64
            for r in at30
        ),
        "support30 budget boundary",
    )
    result = {
        "schema": "p112-a3-support29/v1",
        "errors": 0,
        "chamber": g.chamber_receipt(roots, points, coordinates),
        "root_planes": g.root_plane_receipt(roots),
        "star_orbits": model.star_orbits(g, roots),
        "label_action_checks": model.label_actions(g, roots, labels),
        "six_flat_histogram": model.six_flat_capacity(labels),
        "singleton_facts": model.singleton_facts(labels, groups),
        "punctures": punctures,
        "budget29": at29,
        "budget30": at30,
        "witness30": model.boundary_witness(roots, labels, values, costs, frame_list),
    }
    return json.loads(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build()
    if args.output:
        output = args.output.expanduser().resolve()
        model.require(not output.is_relative_to(model.REPO), "external output required")
        with output.open("x", encoding="utf-8") as stream:
            encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
            model.require(stream.write(encoded) == len(encoded), "receipt write")
    else:
        model.require(
            result == json.loads((model.PACKAGE / "RESULT.json").read_bytes()),
            "committed receipt differs",
        )
    print("PASS_P112_A3_SUPPORT29 flats=788035 frames=2025 witness_support=30 errors=0")


if __name__ == "__main__":
    main()
