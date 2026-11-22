#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent scalar replay for the 326→531→1 prefix-cut theorem.

The source is the unmodified #8027 graph retained by #8041.  Python 3.10+;
no third-party packages.  An optional argument selects the graph file.
"""

from collections import Counter
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
import sys

PACKED_HASH = "74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326"
EXPANDED_HASH = "b096d6df2a0c4688296b13ab0cfd50fec1c7dec732819c624ddd7a745a144b69"
BASE = Path(__file__).resolve().parent
EXPECTED_RESIDUAL = [3, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71,
                     72, 230, 359, 362, 365, 367, 372, 375, 378, 386, 388,
                     390, 522]
EXPECTED_SIGNATURE = [0, 11, 117, 223, 224, 230, 249, 250, 251]


def require(condition, why):
    if not condition:
        raise AssertionError(why)


def read_graph(path):
    packed = path.read_bytes()
    require(sha256(packed).hexdigest() == PACKED_HASH, "source gzip hash")
    data = decompress(packed)
    require(sha256(data).hexdigest() == EXPANDED_HASH, "source content hash")
    return json.loads(data)


def bit_support(x):
    return [i for i in range(x.bit_length()) if (x >> i) & 1]


def row_rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return len(pivots)


def standard_projector(frame):
    """Recover the axes of these specifically coordinate-aligned frames."""
    basis = frame["B"]
    kernel = frame["A"]
    require(len(basis) == frame["dim"] and len(basis) + len(kernel) == 8,
            "projector dimension")
    def axis(row):
        require(len(row) == 8 and set(row) <= {0, 1} and sum(row) == 1,
                "non-coordinate frame")
        return row.index(1)
    image = [axis(row) for row in basis]
    complement = [axis(row) for row in kernel]
    require(sorted(image + complement) == list(range(8)), "basis coverage")
    return frozenset(image)


def instructions(graph, changed):
    replacements = {
        8073: ["INIT", 2327, 531],
        8074: ["ADD", 2327, 2326, 531],
        8075: ["MOVE", 2327, 531, 1],
    }
    result = []
    for clock, original in enumerate(graph["program"]):
        if changed and clock in (8070, 8071):
            continue
        result.append((clock, replacements.get(clock, original) if changed else original))
    return result


def forward(graph, program, inject_at_reader=0):
    n = graph["public"]
    locations = dict(enumerate(graph["start"]))
    values = {i: 1 << i for i in range(n)}
    clears = []
    pre_reader = None
    residual = None
    received = None
    for clock, event in program:
        if clock == 8068:
            residual = values[1857] ^ values[2224]
        if clock == 10137:
            pre_reader = (locations.copy(), values.copy())
            if inject_at_reader:
                require(locations[2326] == 531, "oracle owner location")
                values[2326] ^= inject_at_reader
        op, dest, *args = event
        if op == "INIT":
            require(dest >= n and dest not in locations, "invalid INIT")
            locations[dest], values[dest] = args[0], 0
        elif op == "ADD":
            source, chart = args
            require(dest != source and locations[dest] == locations[source] == chart,
                    "invalid ADD")
            values[dest] ^= values[source]
        elif op == "MOVE":
            source, target = args
            require(locations[dest] == source, "invalid MOVE")
            locations[dest] = target
            if clock == 8075:
                received = values[dest]
        elif op == "SWAP":
            source, = args
            require(source != dest, "invalid SWAP")
            locations[dest], locations[source] = locations[source], locations[dest]
            values[dest], values[source] = values[source], values[dest]
        elif op == "CLEAR":
            require(dest >= n and locations.pop(dest) == args[0], "invalid CLEAR")
            clears.append((clock, dest, args[0], values.pop(dest)))
        else:
            raise AssertionError("unrecognized opcode")
    require(locations == dict(enumerate(graph["final"])) and len(values) == n,
            "final owner bindings")
    require(residual is not None and pre_reader is not None and received is not None,
            "missing observations")
    return [values[i] for i in range(n)], clears, pre_reader, residual, received


def reverse(graph, program):
    """Independent adjoint pass, with each input row a final-output bitmask."""
    n = graph["public"]
    charts = dict(enumerate(graph["final"]))
    dual = {i: 1 << i for i in range(n)}
    for _, event in reversed(program):
        op, dest, *args = event
        if op == "CLEAR":
            require(dest not in charts, "reverse CLEAR")
            charts[dest], dual[dest] = args[0], 0
        elif op == "INIT":
            require(charts.pop(dest) == args[0], "reverse INIT")
            del dual[dest]
        elif op == "ADD":
            source, chart = args
            require(charts[source] == charts[dest] == chart, "reverse ADD")
            dual[source] ^= dual[dest]
        elif op == "MOVE":
            before, after = args
            require(charts[dest] == after, "reverse MOVE")
            charts[dest] = before
        elif op == "SWAP":
            source, = args
            charts[dest], charts[source] = charts[source], charts[dest]
            dual[dest], dual[source] = dual[source], dual[dest]
        else:
            raise AssertionError("reverse opcode")
    require(charts == dict(enumerate(graph["start"])), "reverse boundary")
    return [dual[i] for i in range(n)]


def main(path):
    g = read_graph(path)
    n = g["public"]
    require(n == 630 and len(g["program"]) == 39600 and len(g["frames"]) == 636,
            "source dimensions")
    require(g["program"][8068:8076] == [
        ["INIT", 2326, 326], ["ADD", 2326, 1855, 326],
        ["ADD", 2326, 1857, 326], ["ADD", 2326, 2224, 326],
        ["MOVE", 2326, 326, 531], ["INIT", 2327, 326],
        ["ADD", 2327, 1855, 326], ["MOVE", 2327, 326, 1]],
        "source relay window")
    p326, p531, p1 = [standard_projector(g["frames"][str(x)]) for x in (326, 531, 1)]
    require(len(p326) == 6 and len(p531) == 7 and len(p1) == 8
            and p326 < p531 < p1, "nested relay projectors")
    require(g["start"].count(1) == g["start"].count(531) == 0, "empty receivers")

    original = instructions(g, False)
    altered = instructions(g, True)
    direct_arrivals = [(t, row[1], row[2]) for t, row in altered
                       if row[0] == "MOVE" and row[3] == 1]
    hub_in = [(t, row[1], row[2]) for t, row in altered
              if row[0] == "MOVE" and row[3] == 531 and t <= 10141]
    hub_to_top = [(t, row[1], row[2]) for t, row in altered
                  if row[0] == "MOVE" and row[2:] == [531, 1] and t <= 10141]
    require(len(direct_arrivals) == 505 and len(direct_arrivals) - len(hub_to_top) == 502,
            "receiver contact count")
    require(hub_in == [(8072, 2326, 326), (8098, 2333, 329)], "hub ingress prefix")
    require(hub_to_top == [(8075, 2327, 531), (10138, 2862, 531),
                           (10141, 2863, 531)], "hub egress prefix")
    require(not any(row[0] == "MOVE" and row[2] == 1 for _, row in altered),
            "unexpected chart-1 output channel")

    old, old_clear, old_pre, residual, old_received = forward(g, original)
    new, new_clear, new_pre, changed_residual, new_received = forward(g, altered)
    require(old_received == new_received and residual == changed_residual,
            "forwarded 2327 receipt")
    require(bit_support(residual) == EXPECTED_RESIDUAL, "residual support")
    require(old == [(1 << i) ^ ((1 << (i - 111)) if 111 <= i < 222 else 0)
                    for i in range(n)], "native operator")
    difference = [a ^ b for a, b in zip(old, new)]
    require(all(d in (0, residual) for d in difference), "not a rank-one error")
    signature = [i for i, d in enumerate(difference) if d]
    require(signature == EXPECTED_SIGNATURE and row_rank(old) == 630 and row_rank(new) == 629,
            "error support or rank")
    for rows, program in ((old, original), (new, altered)):
        dual = reverse(g, program)
        require(all(((rows[o] >> i) & 1) == ((dual[i] >> o) & 1)
                    for i in range(n) for o in range(n)), "transpose mismatch")

    require(old_pre[0] == new_pre[0], "pre-reader locations")
    changed_owners = [i for i in old_pre[1] if old_pre[1][i] != new_pre[1][i]]
    require(changed_owners == [2326]
            and old_pre[1][2326] ^ new_pre[1][2326] == residual, "pre-reader values")
    require(len(old_clear) == len(new_clear) == 3433, "private clear count")
    require(all(a[:3] == b[:3] and (a[3] ^ b[3]) in (0, residual)
                for a, b in zip(old_clear, new_clear)), "private clear discrepancy")
    repaired, repaired_clears, _, _, _ = forward(g, altered, inject_at_reader=residual)
    require(repaired == old and repaired_clears == old_clear, "oracle correction")
    wrong, _, _, _, _ = forward(g, altered, inject_at_reader=1 << 3)
    require(wrong != old, "wrong-side-information control")

    top = [i for i, chart in enumerate(g["final"]) if chart == 1]
    require(len(top) == row_rank(old[i] for i in top) == 505, "native chart-1 rank")
    require(row_rank(new[i] for i in top) == 504, "altered chart-1 rank")
    require(row_rank([old[i] for i in top] + [new[i] for i in top]) == 505,
            "altered target space not contained")
    bad_top = [i for i in signature if i in top]
    require(bad_top == [0, 11, 223, 224, 230, 249, 250, 251], "top error signature")
    unaffected = [i for i in top if i not in bad_top]
    attained = [new[i] for i in unaffected] + [new[i] ^ new[0] for i in bad_top[1:]]
    wanted = [old[i] for i in unaffected] + [old[i] ^ old[0] for i in bad_top[1:]]
    require(attained == wanted and len(attained) == row_rank(attained) == 504,
            "504-function construction")

    dims = {int(c): spec["dim"] for c, spec in g["frames"].items()}
    def paid(program):
        return Counter(abs(dims[row[2]] - dims[row[3]]) for _, row in program
                       if row[0] == "MOVE")
    old_paid, new_paid = paid(original), paid(altered)
    require(old_paid[1] + 1 == new_paid[1] and old_paid[2] - 1 == new_paid[2]
            and all(old_paid[r] == new_paid[r] for r in set(old_paid) | set(new_paid)
                    if r not in (1, 2)), "paid count change")

    # Exercise the attained k-copy side-information construction with every
    # assignment of the k independent residual bits, for k=1..8.  Rank and
    # the cut proof, not this finite control, establish the general theorem.
    vector_controls = []
    for k in range(1, 9):
        for m in range(k + 2):
            fixed = min(k, m)
            successes = sum(1 for bits in range(1 << k) if bits >> fixed == 0)
            require(successes == 1 << fixed, "joint-copy side observation")
            vector_controls.append([k, m, successes, 1 << k])

    print(json.dumps({
        "source_sha256": PACKED_HASH,
        "scope": "fixed-incidence normalized constant binary fields; no physical supplier admission",
        "chart1_target_rank": len(top),
        "other_chart1_arrivals": len(direct_arrivals) - len(hub_to_top),
        "early_hub_ingress": hub_in,
        "early_hub_to_chart1": hub_to_top,
        "native_top_rank": row_rank(old[i] for i in top),
        "changed_top_rank": row_rank(new[i] for i in top),
        "native_full_rank": row_rank(old), "changed_full_rank": row_rank(new),
        "attained_native_target_combinations": len(attained),
        "unaffected_top_outputs": len(unaffected), "paired_top_outputs": len(bad_top) - 1,
        "residual_support": bit_support(residual), "public_error_signature": signature,
        "pre_reader_only_changed_owner": changed_owners,
        "preserved_2327_receipt": True, "original_and_changed_clears": len(old_clear),
        "clear_differences_vanish_on_residual_hyperplane": True,
        "oracle_residual_at_10137_repairs_all_public_and_clear_values": True,
        "wrong_side_information_rejected": True,
        "reverse_transposes_verified": True,
        "paid_histogram_change": {"rank_1": 1, "rank_2": -1},
        "joint_copy_residual_controls": vector_controls,
    }, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else BASE / "strong-bit.json.gz")
