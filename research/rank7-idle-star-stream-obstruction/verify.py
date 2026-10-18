"""Reject PR3184's first literal star with a source-bound physical operator check."""

import argparse
import json

from algebra import apply_overlay, host_projection, intervening_events, replay, rotate
from source import FILL_SHA, PACKAGE, TOTAL_ROWS, load_context, read_bytes, require


def check_baseline(context, residual):
    modes = [0] + [1 << i for i in range(73)] + [(1 << 73) - 1]
    modes += [(1 << i) | (1 << (i + 1)) for i in range(72)]
    for character in modes:
        target = [
            [
                rotate((1, 0), character.bit_count()) if i == j else (0, 0)
                for j in range(8)
            ]
            for i in range(8)
        ]
        require(
            replay(context, residual, character) == target, "baseline physical operator"
        )
    return len(modes)


def receipt(context):
    require(
        context["moves"]
        == [[0, 0, 10, 12, [16, 32, 64]], [0, 0, 10, 13, [128, 256, 4096]]],
        "literal current star",
    )
    _, residual = host_projection(context)
    plan = context["plan"]
    require(
        [2 * plan["pairs"][str(c)] + plan["sides"][str(c)] for c in (10, 12, 13)]
        == [7, 0, 1],
        "physical donor and receiver streams",
    )
    changed = apply_overlay(context["recipe"], residual, context["moves"])
    interval = intervening_events(context["template"])
    mode_count = check_baseline(context, residual)
    baseline, overlay = replay(context, residual, 16), replay(context, changed, 16)
    differences = [
        [i, j, list(baseline[i][j]), list(overlay[i][j])]
        for i in range(8)
        for j in range(8)
        if baseline[i][j] != overlay[i][j]
    ]
    require(
        differences
        == [[1, 1, [0, 1], [-1, 0]], [3, 1, [0, 0], [-1, -1]], [7, 7, [0, 1], [1, 0]]],
        "exact current-candidate counterexample",
    )
    return dict(
        status="PASS_PR3184_PHYSICAL_STREAM_COUNTEREXAMPLE",
        admitted=False,
        fill_payload_sha256=FILL_SHA,
        authenticated_fill_rows=TOTAL_ROWS,
        projected_hosted_roles=len(context["rows"]),
        baseline_modes=mode_count,
        projected_hosted_rows=context["rows"],
        replica_call_times=[
            i for i, call in enumerate(context["order"]) if call[1] == 0
        ],
        replica=0,
        port=0,
        cover="identity",
        fourier_character=16,
        stream_order=["X0", "Y0", "X1", "Y1", "X2", "Y2", "X3", "Y3"],
        gaussian_integer_format="[real, imaginary]",
        moves=context["moves"],
        intervening_events=interval,
        baseline=baseline,
        overlay=overlay,
        differences=differences,
        structural_rule_accepts=True,
        selected_frontier_changed=False,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--print-receipt", action="store_true")
    args = parser.parse_args()
    result = receipt(load_context())
    expected = json.loads(read_bytes(PACKAGE / "RESULT.json"))
    require(json.loads(json.dumps(result)) == expected, "stored receipt differs")
    if args.print_receipt:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            result["status"]
            + " rows=2717280 hosts=30 modes=147 differences=3 no_new_kappa"
        )


if __name__ == "__main__":
    main()
