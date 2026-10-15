#!/usr/bin/env python3
"""Verify the exact two-source GF(4) scalar-toggle connector construction."""
from itertools import product
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise SystemExit("FAIL_GF4_SCALAR_CONNECTOR " + message)


def mul(a, b):
    """Multiply codes for a+b*w, with w^2=w+1."""
    product_bits = 0
    for shift in range(2):
        if (b >> shift) & 1:
            product_bits ^= a << shift
    if product_bits & 4:
        product_bits ^= 0b111
    return product_bits


def apply_event(q, event):
    j, alpha = event["source"], event["alpha"]
    out = list(q)
    out[j] ^= alpha
    return tuple(out)


def pair_cover(points):
    cover = {}
    for left in range(len(points)):
        for right in range(left + 1, len(points)):
            diff = (points[left][0] ^ points[right][0],
                    points[left][1] ^ points[right][1])
            need(diff not in cover, "duplicate prefix difference")
            cover[diff] = (left, right)
    return cover


def event_stream(targets, source_word):
    stream = []
    for boundary in range(len(source_word)):
        for target in targets:
            if boundary in target["boundaries"]:
                stream.append({"kind": "read", "target": target["target"],
                               "boundary": boundary})
        event = source_word[boundary]
        stream.append({"kind": "source", "source": event["source"],
                       "alpha": event["alpha"], "after_boundary": boundary})
    return stream


def search_short_words():
    """Exact finite negative control for every closed event word of length < 6."""
    operations = [(j, a) for j in range(2) for a in (1, 2, 3)]
    closed = 0
    maximum = 0
    for k in range(1, 6):
        for word in product(operations, repeat=k):
            q = (0, 0)
            points = [q]
            for j, alpha in word:
                p = list(q)
                p[j] ^= alpha
                q = tuple(p)
                points.append(q)
            if q != (0, 0):
                continue
            closed += 1
            distinct = list(dict.fromkeys(points[:-1]))
            masks = {(p[0] ^ r[0], p[1] ^ r[1])
                     for i, p in enumerate(distinct)
                     for r in distinct[i + 1:]}
            maximum = max(maximum, len(masks))
            need(len(masks) < 15, "unexpected shorter full cover")
    return closed, maximum


def main():
    cert = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    need(cert["format"] == "gf4-scalar-source-connector-v1", "format")
    need(cert["seed"] == "a472dd8c6aee62b83f9dbc2e489790b0", "seed pin")
    need(cert["base_commit"] == "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2", "base pin")
    need(cert["selected_record_sha256"] ==
         "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
         "selected record pin")
    need(cert["field"]["representation"] == "a+b*w encoded by bits (a,b), code=a+2*b",
         "field convention")
    need([[mul(a, b) for b in range(4)] for a in range(4)] ==
         [[0, 0, 0, 0], [0, 1, 2, 3], [0, 2, 3, 1], [0, 3, 1, 2]],
         "GF(4) multiplication table")

    word = cert["source_word"]
    need(len(word) == 6 and all(e["source"] in (0, 1) and e["alpha"] in (1, 2, 3)
                                for e in word), "source word domain")
    q = (0, 0)
    points = [q]
    for event in word:
        q = apply_event(q, event)
        points.append(q)
    need(q == (0, 0), "dirty connector not restored")
    need(points == [tuple(p) for p in cert["prefix_points"]], "prefix certificate")
    core_points = points[:-1]
    need(len(set(core_points)) == 6, "prefixes are not six distinct states")

    rows = [(u, v) for u in range(4) for v in range(4) if (u, v) != (0, 0)]
    targets = cert["targets"]
    need(len(targets) == 15, "target count")
    need([(t["coefficients"][0], t["coefficients"][1]) for t in targets] == rows,
         "target ordering")
    cover = pair_cover(core_points)
    need(set(cover) == set(rows), "prefix differences do not cover GF(4)^2\\{0}")
    for target in targets:
        i, j = target["boundaries"]
        need((i, j) == cover[tuple(target["coefficients"])], "boundary pair")
        need((core_points[i][0] ^ core_points[j][0],
              core_points[i][1] ^ core_points[j][1]) == tuple(target["coefficients"]),
             "target coefficient difference")

    need(cert["event_stream"] == event_stream(targets, word), "literal event stream")
    reads = [e for e in cert["event_stream"] if e["kind"] == "read"]
    need(len(cert["event_stream"]) == 36 and len(reads) == 30, "event count")
    need([sum(e["kind"] == "read" and e["target"] == t for e in cert["event_stream"])
          for t in range(15)] == [2] * 15, "paired target readouts")

    # Any closed k-call path has at most k distinct prefixes. Its unordered
    # pairwise differences number at most binom(k,2), so k<6 cannot cover 15.
    need(all(k * (k - 1) // 2 < 15 for k in range(6)), "minimum-call counting bound")
    closed_short, max_short = search_short_words()
    need(closed_short == 594 and max_short == 7, "short-word census")

    # Every GF(4)-linear scalar map and every dirty scalar state at length 1.
    # Replay the actual source calls, then both A readouts at the certified pair.
    dirty_cases = 0
    for target in targets:
        u, v = target["coefficients"]
        i, j = target["boundaries"]
        for b0, b1, a_map, x0, x1, z0, y0 in product(range(4), repeat=7):
            z = z0
            at = [z]
            for event in word:
                src = (b0, b1)[event["source"]]
                x = (x0, x1)[event["source"]]
                z ^= mul(event["alpha"], mul(src, x))
                at.append(z)
            need(at[-1] == z0, "connector dirt changed in scalar replay")
            got = y0 ^ mul(a_map, at[i]) ^ mul(a_map, at[j])
            expected = y0 ^ mul(a_map, mul(u, mul(b0, x0))) ^ \
                mul(a_map, mul(v, mul(b1, x1)))
            need(got == expected, "dirty scalar target replay")
            dirty_cases += 1

    # Negative controls: deleting the last source event leaves dirty connector
    # state; corrupting a target's boundary pair fails on an explicit input.
    q_bad = (0, 0)
    for event in word[:-1]:
        q_bad = apply_event(q_bad, event)
    need(q_bad == (0, 3), "omission control fixture")
    need(mul(q_bad[1], mul(1, 1)) != 0, "omitted event dirt witness")
    target10 = next(t for t in targets if t["coefficients"] == [1, 0])
    wrong_i, wrong_j = (0, 2)
    wrong_diff = (core_points[wrong_i][0] ^ core_points[wrong_j][0],
                  core_points[wrong_i][1] ^ core_points[wrong_j][1])
    need(wrong_diff != tuple(target10["coefficients"]), "wrong-pair control fixture")
    bad_pair_got = (core_points[wrong_i][1] ^ core_points[wrong_j][1])
    bad_pair_expected = 0  # x0=0, x1=1, B0=0, B1=1 for row (1,0).
    need(bad_pair_got != bad_pair_expected, "wrong-pair control was not detected")
    bad_stream = [e for e in cert["event_stream"]
                  if not (e["kind"] == "read" and e["target"] == target10["target"]
                          and e["boundary"] == 1)]
    need(len(bad_stream) == 35 and
         sum(e["kind"] == "read" and e["target"] == target10["target"]
             for e in bad_stream) == 1, "readout-deletion control")

    row_weight_sum = sum((u != 0) + (v != 0) for u, v in rows)
    need(row_weight_sum == 24, "baseline row weights")
    for source in range(2):
        multiplicities = [2 * sum(row[source] == alpha for row in rows)
                          for alpha in (1, 2, 3)]
        need(multiplicities == [8, 8, 8], "baseline coefficient event multiplicities")
        proposed = [sum(e["source"] == source and e["alpha"] == alpha for e in word)
                    for alpha in (1, 2, 3)]
        need(proposed == [1, 1, 1], "proposed coefficient event multiplicities")
    new_scalars = sum(e["alpha"] != 1 for e in word)
    old_scalars = sum(a != 1 for j in range(2) for a in (1, 2, 3) for _ in range(8))
    need(new_scalars == 4 and old_scalars == 32, "scalar-multiply cost counts")
    desc_new = 6 * 4 + 30 * 5
    desc_old = 48 * 4 + 30 * 5
    cost = cert["cost_model"]
    need(cost["proposed_event_descriptor_bits"] == desc_new == 174, "new descriptor bits")
    need(cost["serial_event_descriptor_bits"] == desc_old == 342, "baseline descriptor bits")
    need(cost["descriptor_saving_bits"] == desc_old - desc_new == 168, "descriptor delta")
    need(cert["lower_bound"]["minimum_source_calls"] == 6, "certified lower bound")
    need(cert["lower_bound"]["minimum_target_readouts"] == 30 and
         cert["lower_bound"]["minimum_total_root_calls"] == 36,
         "full-query lower bound")

    print("PASS_GF4_SCALAR_SOURCE_CONNECTOR targets=15 source_calls=6 minimum=6 readouts=30 "
          "short_closed_words=594 max_short_cover=7 dirty_cases=%d scalar_ops=4_vs_32 "
          "descriptor_bits=174_vs_342 controls=3" % dirty_cases)


if __name__ == "__main__":
    main()
