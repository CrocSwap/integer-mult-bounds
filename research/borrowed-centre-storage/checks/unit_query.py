#!/usr/bin/env python3
"""Review the separate unit-query word with the independent interpreter."""

from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json


HERE = Path(__file__).resolve().parents[1] / "sources" / "work/centre-encoding-campaign-20261014" / "lanes/coherent-port/current-query-review-20261015"
spec = importlib.util.spec_from_file_location("independent_query_review", HERE / "review_query.py")
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
review.need(sha256((HERE / "review_query.py").read_bytes()).hexdigest() ==
            "85166891ae71ca6847a778c74e8395ddb70bc3387ef42279f765bf27726e8824", "Independent interpreter pin")
PINS = {
    "UNIT-QUERY.md": "6f53e12ba5144c8eb9df5de7eb3e19e7e0c7c1e1119db3e8116a2e643662f3a7",
    "emit_unit_query.py": "9092389471e70436018a67e29604e1987301ad82ca6b2da63aae4f8117c3eab8",
    "UNIT-QUERY.json": "872c32ff5445a29862f8e5f7102a981948cd70b82f6439df421286dc343bde6b",
}
PAYLOAD = "9cb744034b11ef515a9c429264199a03f02fd9c4cb408e6455021ce9c0802a9c"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    need, plus, mul = review.need, review.plus, review.product
    for name, pin in PINS.items():
        review.read(review.SOURCE / name, pin)
    data = json.loads(review.read(review.SOURCE / "UNIT-QUERY-PROGRAM.json.gz", PAYLOAD, True))
    old = json.loads(review.read(review.SOURCE / "CURRENT-QUERY-PROGRAM.json.gz", review.PAYLOAD, True))
    word = json.loads(gzip.decompress(review.read(review.REPO / "work/five-pr-sprint-20261013/lanes/centre-sharing/CANONICAL-WORD.json.gz", review.WORD)))
    interface = json.loads(review.read(review.LANES / "circuit-interface/INTERFACE.json",
                                      "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"))
    r = review.deserialize(interface["R"])
    eye = [{p: F(1)} for p in range(112)]
    k = [{j: row[p] / 4 for j, row in enumerate(r) if p in row} for p in range(112)]
    ka = [dict(row) if p in review.A else {} for p, row in enumerate(k)]
    ku = [dict(row) if p not in review.A else {} for p, row in enumerate(k)]
    la = [{p: c for p, c in row.items() if p in review.A} for row in r]
    ru = [{p: c for p, c in row.items() if p not in review.A} for row in r]
    j = [dict(row) for row in eye]
    for p, row in enumerate(mul(k, r)):
        plus(j[p], row, -1)
    x, y = mul(ka, ru), mul(ku, la)
    need(not any(mul(x, x)) and not any(mul(y, y)), "Both square-zero factors")
    upper, lower, upper_i, lower_i = [[dict(row) for row in eye] for _ in range(4)]
    for p in range(112):
        plus(upper[p], x[p]); plus(upper_i[p], x[p], -1)
        plus(lower[p], y[p], -1); plus(lower_i[p], y[p])
    target, inverse = mul(lower, upper), mul(upper_i, lower_i)
    need(mul(target, inverse) == mul(inverse, target) == eye, "Both exact dyadic inverse orders")
    need(mul(la, target) == r, "Full current query without odd division")
    correction = [dict(row) for row in target]
    for p, row in enumerate(j):
        plus(correction[p], row, -1)
    expected_correction = mul(ka, [{p: 2 * row.get(p, F(0)) - la[m].get(p, F(0))
                                  for p in row if 2 * row.get(p, F(0)) - la[m].get(p, F(0))}
                                 for m, row in enumerate(r)])
    need(correction == expected_correction, "Selected completion formula")
    need({p for p, row in enumerate(correction) if row} == set(review.A), "Only eight selected output rows")
    need(sum(map(len, correction)) == 424 and {c for row in correction for c in row.values()} == {F(-1), F(1)},
         "Actual signed-unit suffix coefficients")
    for name, value in (("T", target), ("inverse_T", inverse), ("S", correction)):
        need(review.deserialize(data[name]) == value, "Actual matrix: " + name)
    for name in ("retained_core", "native_normalizations", "output_frames", "physical_input", "physical_output"):
        need(data[name] == old[name], "Unchanged native or frame source: " + name)
    need(data["selected_A"] == list(review.A), "Actual selected minor")
    program = data["prefix"] + data["retained_core"] + data["native_normalizations"] + data["suffix"]
    need(data["program"] == program and len(program) == 26531, "Exact emitted chronology")
    expected = [{p: F(1)} for p in range(712)]
    for p, row in enumerate(target):
        expected[112 + p] = dict(row)
        plus(expected[112 + p], {112 + q: c for q, c in row.items()})
    expected[704:] = [{} for _ in range(8)]
    output, frames, scalars, climbs = review.replay(program, word)
    need(output == expected and frames == data["output_frames"], "All 712 columns and mixed output frames")
    half = len(data["prefix"]) // 2
    need(half == 472, "Two complete prefix factors")
    controls = (
        data["prefix"][half:] + data["prefix"][:half] + data["retained_core"] + data["native_normalizations"] + data["suffix"],
        data["prefix"][:half] + data["retained_core"] + data["native_normalizations"] + data["suffix"],
        data["prefix"] + data["retained_core"] + data["native_normalizations"],
    )
    for events in controls:
        actual, _, _, _ = review.replay(events, word)
        need(actual != expected, "Wrong factor or missing correction is rejected")
    costs = {name: sum(review.price(e) for e in events if e[0] == "scalar")
             for name, events in (("first_factor", data["prefix"][:half]), ("second_factor", data["prefix"][half:]),
                                  ("core", data["retained_core"]), ("suffix", data["suffix"]), ("total", program))}
    need(costs == dict(first_factor=3648, second_factor=3648, core=202138, suffix=3392, total=212826),
         "Independent complete scalar count")
    result = dict(status="PASS_UNIT_QUERY_REVIEW", producer_pins=PINS, payload_sha256=PAYLOAD,
                  inherited_PJ_review_sha256="149b4bbedafaca62fe414f2ff22035ece47fa1c203e1bdf0949e6d08045a17d5",
                  all_input_columns=712, exact_scalar_frame_checks=scalars, retained_native_climbs=climbs,
                  helper_rows_restored=480, owned_private_rows_zero=8, output_query="L_A T=R",
                  changed_output_rows=8, correction_coefficients=424, both_dyadic_inverse_orders=True,
                  rejected_controls=3, costs=costs, added_rank_one_children=8, native_mass=5530,
                  scope="Separate unit-query local word; native line and exterior phase evidence inherited byte-for-byte from the independent PJ review.")
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS_UNIT_QUERY_REVIEW: all 712 columns, both inverse orders, and 212826 scalar")


if __name__ == "__main__":
    main()
